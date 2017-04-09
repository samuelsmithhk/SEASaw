import os

from tornado import process
from tornado.web import Application
from tornado.web import StaticFileHandler
from tornado.ioloop import IOLoop

from seasaw import inventory
from seasaw.datasource.datasourceinterface import HealthCheckHandler
from seasaw.datasource.datasourceinterface import ResultQueryHandler
from seasaw.datasource.datasourceinterface import ResultGetterHandler

root = os.path.dirname(__file__)
print(root)

def main():
    # spin up component APIs

    process_id = process.fork_processes(len(inventory.ports), max_restarts=0)

    if process_id <= len(inventory.ports) * 0.3:
        # video frame sequence extractor threads

        instance = Application([
            (r"/healthcheck", HealthCheckHandler),
            (r"/results/(.*)", ResultGetterHandler),
            (r"/results", ResultQueryHandler),
            (r"/(.*)", StaticFileHandler, {"path": "static/apidocs/datasource/", "default_filename": "index.html"})
        ])

        port = inventory.ports[process_id]
        instance.listen(port)

        print("Data Source Interface listening on port " + str(port))

    elif process_id <= len(inventory.ports) * 0.6:
        # indexer threads
        print("todo - indexer")
    else:
        # frontend threads
        print("todo - todo frontend")

    IOLoop.current().start()

if __name__ == "__main__":
    main()
