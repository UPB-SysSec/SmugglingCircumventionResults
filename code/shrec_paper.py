import socket
import queue
import request
import argparse
import logging
from datetime import datetime
from tqdm import tqdm
import concurrent.futures
import pandas as pd
import csv
from time import sleep

TIMEOUT = 10.0
#Control Server Answer
ANSWER = b'AAAAA'

#Configure ports
STARTPORT = 80
PORTS = 1
RETRIES = 10
RES_CENSOR_TIMER = 121.0

#Add IP of control server here
DST_HOST = "control server ip"

DATA_HEADERS = ["tv_id", "smuggle_url", "success", "rst", "blockpage","timeout_afterhs","timeout_beforehs", "other", "timestamp", "request"]

#Add a clean url for the countrycode
CLEAN_URLS = {
    "cn": "www.gov.cn/",
    "ir": "irangov.ir/",
    "ru": "government.ru/"
}

timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M')

sock_q = queue.Queue()

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--country", default="cn")
    parser.add_argument("-t", "--threads", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--residual-timer", type=float, default=121.0)

    args = parser.parse_args()
    return args  

def _trialworker(row):
    if(row.vector_id == "No-Vector"):
        tecl = True
        req = str(request.request(row.url))
    elif(row.vector_id[-5:] == "TE.CL"):
        tecl = True
        req = str(request.request(CLEAN_URL,row.url, row.vector, tecl))
    else:
        tecl = False
        req = str(request.request(CLEAN_URL,row.url, row.vector, tecl))

    success_count = 0
    rst_count = 0
    timeout_beforehs_count = 0
    timeout_afterhs_count = 0
    blockpage_count = 0
    other_count = 0
    ports = []


    for i in range(RETRIES):
        if PORTS > 1:    
            port = sock_q.get()
            ports.append(port)
        else:
            ports.append(STARTPORT)


    for port in ports:
        connection_is_made = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(args.timeout)
            try:
                s.connect((DST_HOST, port))
                connection_is_made = True
                s.send(req.encode())
                res = s.recv(1024)
                if res == b'AAAAA':
                    success_count += 1
                elif "403" in res.decode():
                    blockpage_count += 1
                elif "307" in res.decode():
                    blockpage_count += 1
            except ConnectionResetError as rst_e:
                rst_count += 1
            except TimeoutError as to_e:
                print(str(to_e))
                if connection_is_made:
                    timeout_afterhs_count += 1
                else:
                    timeout_beforehs_count += 1
            except Exception as exc:
                other_count += 1
                logger.info("{} {} {} {} {}".format(row.vector_id, row.url, port,type(exc), exc))
                
    if PORTS > 1:
        sleep(RES_CENSOR_TIMER)
        for port in ports:
            sock_q.put(port)
    return
    return success_count, rst_count, blockpage_count, timeout_afterhs_count, timeout_beforehs_count, other_count, req.encode()
    

if __name__ == "__main__":
    args = parse_args()
    CC = args.country.lower()
    CLEAN_URL = CLEAN_URLS[CC]
    RES_CENSOR_TIMER = args.residual_timer

    logpath = f"data/logs/{CC}-{timestamp}.log"
    logger = logging.getLogger("log")
    logger.setLevel(logging.INFO)
    ch = logging.FileHandler(logpath)
    ch.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(ch)

    for port in range(STARTPORT, STARTPORT+PORTS):
        sock_q.put(port)

    li = []
    for suffix in ["censored", "uncensored"]:
        print(f"Loading URLs: {CC}_{suffix}")
        df = pd.read_csv(f"data/urls/{CC}_{suffix}.csv")
        li.append(df)
    urls = pd.concat(li, axis=0, ignore_index=True)

    viable_vectors = pd.read_csv("data/viable_vectors.csv", keep_default_na=False)
    viable_vectors["vector"] = viable_vectors["vector"].apply(lambda x: bytes.fromhex(x).decode("utf-8"))

    combined_df = urls.merge(viable_vectors, how="cross")
    shuffled_df = combined_df.sample(frac=1)

    results = []
    results_file = f"data/results/{CC}-{timestamp}.csv"

    with tqdm(total=len(shuffled_df), ascii=True, ncols=100, desc="Evasion Scan", leave=None) as pbar:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            future_trial = {executor.submit(_trialworker, row): row for row in shuffled_df.itertuples()}
            for future in concurrent.futures.as_completed(future_trial):
                pbar.update(1)
                row = future_trial[future]
                try:
                    success_count, rst_count, blockpage_count, timeout_afterhs_count, timeout_beforehs_count, other_count, req = future.result()
                except Exception as exc:
                    tqdm.write(str(exc))
                    result = (row.vector_id, row.url, "-", "-", "-","-","-", str(exc), datetime.now().strftime('%Y-%m-%dT%H:%M:%S,%f'), req)
                else:
                    result = (row.vector_id, row.url, success_count, rst_count, blockpage_count, timeout_afterhs_count, timeout_beforehs_count, other_count, datetime.now().strftime('%Y-%m-%dT%H:%M:%S,%f'), req)
                finally:
                    tqdm.write(str(result))
                    results.append(result)
        with open(results_file, 'a') as f:
            csv_out = csv.writer(f)
            csv_out.writerow(DATA_HEADERS)
            for row in results:
                csv_out.writerow(row)


    
