import glob
import pandas as pd
import argparse
import csv

def get_domains(cc):
    censored_domains = []
    uncensored_domains = []
    with open(f"data/urls/{cc}_censored.csv", 'r') as censored_f:
        csv_reader = csv.DictReader(censored_f)
        for row in csv_reader:
            censored_domains.append(row["url"])

    with open(f"data/urls/{cc}_uncensored.csv", 'r') as uncensored_f:
        csv_reader = csv.DictReader(uncensored_f)
        for row in csv_reader:
            uncensored_domains.append(row["url"])

    return censored_domains, uncensored_domains

def init_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("filename")
    parser.add_argument("--country", default="cn")

    return parser.parse_args()

def get_vector_successrates(df):
    df = df.drop(["timestamp",'request'], axis=1)
    #df["cn_success_rate"] = df["success"]/(df["success"]+df["rst"]+df["timeout"]+df["other"])
    df["ir_success_rate"] = df["success"]/(df["success"]+df["rst"]+df["timeout_afterhs"]+df["timeout_beforehs"]+df["blockpage"]+df["other"])
    df = df.sort_values(by="ir_success_rate", ascending=False)
    return df

def all_vector_rates():
    df_censored_cn = pd.read_csv("data/evaluation/cn_censored_rates.csv", keep_default_na=False)
    df_censored_ir = pd.read_csv("data/evaluation/ir_censored_rates.csv", keep_default_na=False)
    df_censored_ru = pd.read_csv("data/evaluation/ru_censored_rates.csv", keep_default_na=False)

    df_censored_cn = df_censored_cn[["tv_id","cn_success_rate"]].groupby("tv_id").mean()
    df_censored_ir = df_censored_ir[["tv_id","ir_success_rate"]].groupby("tv_id").mean()
    df_censored_ru = df_censored_ru[["tv_id","ru_success_rate"]].groupby("tv_id").mean()

    df_censored_ru.to_csv("ru.csv")

    df_all = df_censored_cn.join(df_censored_ir, on="tv_id")
    df_all = df_all.join(df_censored_ru,on="tv_id")
    df_all["overall_success_without_ru"] = (df_all["cn_success_rate"]+df_all["ir_success_rate"])/2
    df_all["overall_success_with_ru"] = (df_all["cn_success_rate"]+df_all["ir_success_rate"]+df_all["ru_success_rate"])/3
    df_all = df_all.sort_values("overall_success_without_ru", ascending=False)
    df_all = df_all.round(3)
    df_all.to_csv("summary.csv")
    print(df_all)

if __name__ == "__main__":
    all_vector_rates()
    quit()
    args = init_parser()
    df = pd.read_csv(args.filename, keep_default_na=False)

    censored_domains, uncensored_domains = get_domains(args.country.lower())
    # Analyse uncensored domains
    print("Uncensored Domain Results:\n")
    df_uncensored = df[df["smuggle_url"].isin(uncensored_domains)]
    df_uncensored_success_rates = get_vector_successrates(df_uncensored)
    df_uncensored_success_rates.to_csv(f"data/evaluation/{args.country.lower()}_uncensored_rates.csv", index=False)
    # Analyse censored domains
    print("Censored Domain Results:\n")
    df_censored = df[df["smuggle_url"].isin(censored_domains)]
    df_censored_success_rates = get_vector_successrates(df_censored)
    df_censored_success_rates.to_csv(f"data/evaluation/{args.country.lower()}_censored_rates.csv", index=False)