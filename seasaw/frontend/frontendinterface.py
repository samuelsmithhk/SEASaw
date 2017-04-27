import json

from tornado.web import RequestHandler
from seasaw import inventory
from tornado.web import StaticFileHandler
from tornado import web, gen
from seasaw.frontend.generateResult import generateResultRows
from seasaw.frontend.generateResult import Result
import seasaw.scheduler as sc


#taken from solution code of: Assignment 2
class IndexDotHTMLAwareStaticFileHandler(web.StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'
        return super(IndexDotHTMLAwareStaticFileHandler, self).parse_url_path(url_path)

class SearchHandler(RequestHandler):
    def get(self):
        query = self.get_argument("query", None)

        #generate resulit form
        res = Result("First Video", "mRf3-JkwqfU", ["33IGHlg.jpg", "33IGHlg.jpg", "33IGHlg.jpg", "33IGHlg.jpg"], [35, 36, 58, 356])
        res2 = Result("Second Video", "mRf3-JkwqfU", ["33IGHlg.jpg", "33IGHlg.jpg", "33IGHlg.jpg", "33IGHlg.jpg"], [35, 36, 58, 356])
        reslis = []
        reslis.append(res)
        reslis.append(res2)
        res_row = generateResultRows(reslis)
        self.render("template.html", results=res_row)

    def post(self):
        query = self.get_argument("query", None)
        self.finish(query)

#front end search bar query
#taken from solution code of: Assignment 2
class Web(web.RequestHandler):
    def head(self):
        self.finish()

    @gen.coroutine
    def get(self):
        q = self.get_argument('q', None)
        if q is None:
            return

        # Fetch postings from index servers
        http = httpclient.AsyncHTTPClient()
        responses = yield [http.fetch('http://%s/index?%s' % (server, urllib.parse.urlencode({'q': q})))
                           for server in inventory.servers['index']]
        # Flatten postings and sort by score
        postings = sorted(chain(*[json.loads(r.body.decode())['postings'] for r in responses]),
                          key=lambda x: -x[1])[:NUM_RESULTS]

        # Batch requests to doc servers
        server_to_doc_ids = defaultdict(list)
        doc_id_to_result_ix = {}
        for i, (doc_id, _) in enumerate(postings):
            doc_id_to_result_ix[doc_id] = i
            server_to_doc_ids[self._get_server_for_doc_id(doc_id)].append(doc_id)
        responses = yield self._get_doc_server_futures(q, server_to_doc_ids)

        # Parse outputs and insert into sorted result array
        result_list = [None] * len(postings)
        for response in responses:
            for result in json.loads(response.body.decode())['results']:
                result_list[doc_id_to_result_ix[int(result['doc_id'])]] = result

        self.finish(json.dumps({'num_results': len(result_list), 'results': result_list}))

    def _get_doc_server_futures(self, q, server_to_doc_ids):
        http = httpclient.AsyncHTTPClient()
        futures = []
        for server, doc_ids in server_to_doc_ids.items():
            query_string = urllib.parse.urlencode({'ids': ','.join([str(x) for x in doc_ids]), 'q': q})
            futures.append(http.fetch('http://%s/doc?%s' % (server, query_string)))
        return futures

    def _get_server_for_doc_id(self, doc_id):
        servers = inventory.servers['doc']
        return servers[doc_id % len(servers)]


#taken from solution code of: Assignment 2
class Index(web.RequestHandler):
    # def initialize(self):
    #     # self._posting_lists, self._log_idf = data

    def head(self):
        self.finish()





    def get(self):
        query = self.get_argument('q', '')
        query_terms = query.lower().split()
        # query_vector = np.array([[self._log_idf[term] for term in query_terms]])
        # doc_vector_dict = defaultdict(lambda: np.array([0.0] * len(query_terms)))
        # for i, term in enumerate(query_terms):
        #     for doc_id, tf in self._posting_lists[term]:
        #         doc_vector_dict[doc_id][i] = tf * self._log_idf[term]
        # doc_ids = list(doc_vector_dict.keys())
        # if len(doc_ids) == 0:
        #     self.finish(json.dumps({'postings': []}))
        #     return
        # doc_matrix = np.zeros((len(doc_vector_dict), len(query_terms)))
        # for doc_ix, doc_id in enumerate(doc_ids):
        #     doc_matrix[doc_ix][:] = doc_vector_dict[doc_id][:]
        # sims = linear_kernel(query_vector, doc_matrix).flatten()
        # best_doc_ixes = sims.argsort()[::-1]
        # best_doc_sims = sims[best_doc_ixes]
        # best_doc_ids = [doc_ids[doc_ix] for doc_ix in best_doc_ixes]

        # postings = list(zip(best_doc_ids, best_doc_sims))
        self.finish(json.dumps({'postings': query_terms}))


# get query terms
# get results from the database

