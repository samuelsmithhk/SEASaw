# This class will provide the RESTful interface for the data source
from tornado.web import RequestHandler


class HealthCheckHandler(RequestHandler):
    def get(self):
        self.write("Healthy")


class ResultQueryHandler(RequestHandler):
    def get(self):
        self.write("not implemented")
