# This class will provide the RESTful interface for the data source
import json

from tornado.web import RequestHandler
from .database import dao


class HealthCheckHandler(RequestHandler):
    def get(self):
        self.write("Healthy")


class ResultQueryHandler(RequestHandler):
    def get(self):
        start = self.get_argument("start", "1460489589")
        end = self.get_argument("end", "1586719989")
        pagination = int(self.get_argument("pagination", "10"))
        page = int(self.get_argument("page", "0"))

        query_results = {}

        results = dao.results_query(start, end, pagination, page)

        query_results["results"] = results
        query_results["pagination"] = pagination
        query_results["page"] = page
        query_results["count"] = len(results)

        self.write(json.dumps(query_results))


class ResultGetterHandler(RequestHandler):
    def get(self, result_id):
        result = dao.result_id_query(result_id)

        if result is None:
            self.write('{"message":"No result found matching id [' + result_id + ']"}')
        else:
            self.write(json.dumps(result))