import json, os, ast, re, string, pickle, math

from tornado.web import RequestHandler
from seasaw import inventory
from tornado.web import StaticFileHandler
from tornado import web, gen, httpclient
from seasaw.frontend.generateResult import generateResultRows
from seasaw.frontend.generateResult import Result
from collections import defaultdict
import numpy as np
from sklearn.metrics.pairwise import linear_kernel

Line_count = 0


def parseTime(startTime):
    startTime = startTime[:-1]
    st  = startTime.split('m')
    if(len(st) == 1):
        return st[0]
    else:
        return str(int(st[0])*60 + int(st[1]))


#taken from solution code of: Assignment 2
class IndexDotHTMLAwareStaticFileHandler(web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'
        return super(IndexDotHTMLAwareStaticFileHandler, self).parse_url_path(url_path)

class SearchHandler(RequestHandler):
    @gen.coroutine
    def get(self):
        lists = []
        infile0 = open('./pickleFiles/InvertedIndex0.pickle', 'rb')
        while 1:
            try:
                lists.append(pickle.load(infile0))
            except EOFError:
                break
        infile0.close()

        infile1 = open('./pickleFiles/InvertedIndex1.pickle', 'rb')
        while 1:
            try:
                lists.append(pickle.load(infile1))
            except EOFError:
                break
        infile1.close()



        inv = {}

        for i in lists: #each list
            for j in i: # for each term
                if(j not in inv):
                    inv[j] = {}
                for res_id in i[j]:
                    inv[j][res_id] = i[j][res_id]
        # print(inv)
        videos = []
        infile2 = open('./pickleFiles/ProcessedVideos.pickle', 'rb')
        videos = pickle.load(infile2)
        infile2.close()


        idf = {}
        for term in inv:
            idf[term] = math.log10(len(videos)/ float(len(inv[term])))

        query = self.get_argument('query', '')
        searchbar = """<input class="inputbar" type="text" name="query" value="%s" required>""" %query
        query_terms = query.lower().split()
        query_vector = np.array([[idf.get(term,0.0)for term in query_terms]])
        doc_vector_dict = defaultdict(lambda: np.array([0.0] * len(query_terms)))
        for i, term in enumerate(query_terms):
            # print(term)
            ks = inv.get(term,[])
            for doc_id in ks:
                tf = inv[term][doc_id]
                doc_vector_dict[doc_id][i] = tf * idf[term]
        doc_ids = list(doc_vector_dict.keys())
        if len(doc_ids) == 0:
            self.render("template.html", searchbar=searchbar, results="<center><h2> Results not found! Please try another query! <h2></center>")
            return
        doc_matrix = np.zeros((len(doc_vector_dict), len(query_terms)))
        for doc_ix, doc_id in enumerate(doc_ids):
            doc_matrix[doc_ix][:] = doc_vector_dict[doc_id][:]
        sims = linear_kernel(query_vector, doc_matrix).flatten()
        best_doc_ixes = sims.argsort()[::-1]
        best_doc_sims = sims[best_doc_ixes]
        best_doc_ids = [doc_ids[doc_ix] for doc_ix in best_doc_ixes]
        http = httpclient.AsyncHTTPClient()
        postings = list(zip(best_doc_ids, best_doc_sims))

        tasks = []
        server_id = 0
        for id in best_doc_ids:
            if server_id >= inventory.DATA_PARTITIONS:
                server_id = 0
            destination = inventory.DATA_SERVERS[server_id] + "/results/" + str(id)
            tasks.append(httpclient.AsyncHTTPClient().fetch(destination))
            server_id += 1
        
        results = []
        responses = yield tasks
        for response in responses:
            video_information = ast.literal_eval(response.body.decode("utf-8"))
            for i in video_information:
                title = video_information["video_title"]
                url = video_information["video_url"]
                tags = video_information["tags"]
                img_li = []
                st_li = []
                for frame in video_information["frames"]:
                    if len(frame["url"]) > 0:
                        frame_url = frame["url"]
                        start = frame["timestamp"]
                        st = parseTime(start)
                        img_li.append(frame_url)
                        st_li.append(st)
            
            for ind in range(len(tags)):
                for q in query_terms:
                    t = """'%s'""" % q
                    re = """<b>%s</b>""" % q
                    if (tags[ind] == q):
                        tags[ind] = re

            res = Result(title, url, img_li, st_li, tags)
            results.append(res)

        res_row = ""
        res_row = generateResultRows(results)

        self.render("template.html", searchbar=searchbar, results=res_row)

        print(best_doc_ids)

    def post(self):
        query = self.get_argument("query", None)
        self.finish(query)



