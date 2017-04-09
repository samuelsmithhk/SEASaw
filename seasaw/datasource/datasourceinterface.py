# This class will provide the RESTful interface for the data source
import string
import random
import json

from tornado.web import RequestHandler


def fake_id_generator():
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(5))

class HealthCheckHandler(RequestHandler):
    def get(self):
        self.write("Healthy")


class ResultQueryHandler(RequestHandler):
    def get(self):
        # TODO: This is mocked data
        start = self.get_argument("start", "000000000000000")
        end = self.get_argument("end", "201231125959999")
        pagination = int(self.get_argument("pagination", "10"))
        page = int(self.get_argument("page", "-1"))

        query_results = {}

        results = []

        for i in range(0, pagination):
            results.append(fake_id_generator())

        query_results["results"] = results
        query_results["pagination"] = pagination
        query_results["page"] = page
        query_results["count"] = random.randint(0, 10000)

        self.write(json.dumps(query_results))


class ResultGetterHandler(RequestHandler):
    def get(self, result_id):
        # TODO:This is mocked data

        result = {}
        result["result_id"] = result_id
        result["video_title"] = "Fake title"
        result["video_url"] = "http://www.thisafakeurl.com/videovideovideo"
        result["frames"] = [
            "frame1",
            "frame2",
            "frame3",
            "frame4",
            "frame5"
        ]

        self.write(json.dumps(result))
