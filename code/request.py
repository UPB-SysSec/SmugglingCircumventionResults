import unittest
import random

class request():
    def __init__(self, clean_url="example.com/hello", smuggle_url="flag.com/flag", vector="", tecl=True):
        if "/" in clean_url:
            self.host = clean_url.split("/",1)[0]
            self.endpoint = "/" + clean_url.split("/",1)[1]
        else:
            self.host=clean_url
            self.endpoint = "/"

        if "/" in smuggle_url:
            self.smuggle_host = smuggle_url.split("/",1)[0]
            self.smuggle_endpoint = "/" + smuggle_url.split("/",1)[1]
        else:
            self.smuggle_host = smuggle_url
            self.smuggle_endpoint = "/"
        self.vector = vector
        self.tecl = tecl

    def random_ua_header(self):
        ua_arr = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3.1 Safari/605.1.1",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.3",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.3",
            "Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.3"
            ]
        return ua_arr[random.randint(0, len(ua_arr)-1)]

    def __str__(self):
        smuggled_req = ""
        random_ua = self.random_ua_header()
        uncensored_req = "GET " + self.endpoint + " HTTP/1.1\r\n"
        uncensored_req += "Host: " + self.host + "\r\n"
        uncensored_req += "User-Agent: " + random_ua + "\r\n"


        if not self.vector == "":
            smuggled_req = "GET " + self.smuggle_endpoint + " HTTP/1.1\r\n"
            smuggled_req += "Host: " + self.smuggle_host + "\r\n"
            smuggled_req += "User-Agent: " + random_ua + "\r\n" 
            if "__CL__" in self.vector:
                uncensored_req += self.vector + "\r\n"
                uncensored_req += "Transfer-Encoding: chunked\r\n\r\n"
            else:
                uncensored_req += "Content-Length: __CL__\r\n"
                uncensored_req += self.vector + "\r\n\r\n"
            smuggled_req += "Transfer-Encoding: chunked\r\n" if self.tecl else ""
            smuggled_req += "\r\n"

            if self.tecl: #Smuggle in TE
                smuggled_req_len_as_hex = hex(len(smuggled_req)).replace("0x","")
                #Add offset 0 to terminate TE
                smuggled_req += "0\r\n\r\n"
                smuggled_req_with_offset_length = len(hex(len(smuggled_req)).replace("0x","") + "\r\n")
                uncensored_req += smuggled_req_len_as_hex + "\r\n"
                uncensored_req = uncensored_req.replace("__CL__",str(smuggled_req_with_offset_length))
            else: #Smuggle in CL
                #Terminate TE in Request A
                uncensored_req += "0\r\n\r\n"
                smuggled_req_clte_length_in_bytes = len(smuggled_req.encode("utf-8"))
                smuggled_req_clte_length_in_bytes += 5
                uncensored_req = uncensored_req.replace("__CL__",str(smuggled_req_clte_length_in_bytes))
        else:
            uncensored_req = uncensored_req.replace("__CL__","0") + "\r\n"
        return uncensored_req + smuggled_req

class TestRequests(unittest.TestCase):

    def testNone(self):
        expected_req = "GET /flag HTTP/1.1\r\n"
        expected_req += "Host: flag.com\r\n\r\n"
        none_req = request()

    def testUncensored(self):
        expected_req =  "GET /hello HTTP/1.1\r\n"
        expected_req += "Host: example.com\r\n\r\n"
        uncensored_request = request()
        self.assertEqual(str(uncensored_request), expected_req)
        uncensored_request = request(tecl=False)
        self.assertEqual(str(uncensored_request), expected_req)

    def testCL_TECL(self):
        uncensored_request = request(smuggle_url="censored.com/censored",vector="Content_Length: __CL__", tecl=True)

        expected_req =  "GET /hello HTTP/1.1\r\n"
        expected_req += "Host: example.com\r\n"
        expected_req += "Content_Length: 4\r\n"
        expected_req += "Transfer-Encoding: chunked\r\n\r\n"
        expected_req += "4a\r\n" # 4 Bytes, 24+20+30 = 74, hex(74)=4A
        expected_req += "GET /censored HTTP/1.1\r\n" #24 Bytes
        expected_req += "Host: censored.com\r\n" #20 Bytes
        expected_req += "Transfer-Encoding: chunked\r\n\r\n" #30 Bytes
        expected_req += "0\r\n\r\n" #Terminates both chunked bodies

        self.assertEqual(str(uncensored_request),expected_req)

    def testCL_CLTE(self):
        clte_request = request(smuggle_url="censored.com/censored",vector="Content_Length: __CL__", tecl=False)

        expected_req =  "GET /hello HTTP/1.1\r\n"
        expected_req += "Host: example.com\r\n"
        expected_req += "Content_Length: 51\r\n" #5+24+22 = 51
        expected_req += "Transfer-Encoding: chunked\r\n\r\n"
        expected_req += "0\r\n\r\n" #5 Bytes

        smuggle_req = "GET /censored HTTP/1.1\r\n" # 24 Bytes
        smuggle_req += "Host: censored.com\r\n\r\n" # 22 Bytes

        expected_req += smuggle_req
        self.assertEqual(str(clte_request),expected_req)

    def testTE_TECL(self):
        uncensored_request = request(smuggle_url="example.com/censored",vector="Transfer-Encoding: chunked", tecl=True)

        expected_req =  "GET /hello HTTP/1.1\r\n"
        expected_req += "Host: example.com\r\n"
        expected_req += "Content-Length: 4\r\n"
        expected_req += "Transfer-Encoding: chunked\r\n\r\n"
        expected_req += "49\r\n"
        expected_req += "GET /censored HTTP/1.1\r\n"
        expected_req += "Host: example.com\r\n"
        expected_req += "Transfer-Encoding: chunked\r\n\r\n"
        expected_req += "0\r\n\r\n"

        self.assertEqual(str(uncensored_request),expected_req)

    def testTE_CLTE(self):
        uncensored_request = request(smuggle_url="example.com/censored",vector="Transfer-Encoding: chunked", tecl=False)


        expected_req =  "GET /hello HTTP/1.1\r\n"
        expected_req += "Host: example.com\r\n"
        expected_req += "Content-Length: 50\r\n" #3+24+21 = 48
        expected_req += "Transfer-Encoding: chunked\r\n\r\n"
        expected_req += "0\r\n\r\n" # 3 Bytes
        expected_req += "GET /censored HTTP/1.1\r\n" # 24 Bytes
        expected_req += "Host: example.com\r\n\r\n" # 21 Bytes
        clte_request = request(smuggle_url="example.com/censored", vector="Transfer-Encoding: chunked", tecl=False)
        self.assertEqual(str(uncensored_request),expected_req)

if __name__ == '__main__':
    uncensored_request = request()
    #print(str(uncensored_request))
    tecl_request = request(smuggle_url="example.com/censored",vector="Transfer-Encoding: chunked", tecl=True)
    #print(str(tecl_request))
    clte_request = request(smuggle_url="example.com/censored",vector="Transfer-Encoding: chunked", tecl=False)
    #print(str(clte_request))
    unittest.main()