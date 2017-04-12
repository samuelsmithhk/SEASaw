import argparse

from tornado import process
from tornado.web import Application
from tornado.web import StaticFileHandler
from tornado.ioloop import IOLoop

from seasaw import inventory
from seasaw.datasource.datasourceinterface import HealthCheckHandler
from seasaw.datasource.datasourceinterface import ResultQueryHandler
from seasaw.datasource.datasourceinterface import ResultGetterHandler
from seasaw.datasource.database import proxy
from seasaw.datasource.database import dao

def main():
    parser = argparse.ArgumentParser('SEASaw - A Search Engine For Video Content')
    parser.add_argument("--gca_credentials_path", action="store", default=None, dest="gca_credentials_path")
    parser.add_argument("--database_password", action="store", default=None, dest="database_password")
    args = parser.parse_args()

    if (args.gca_credentials_path is None) or (args.database_password is None):
        print("Missing credential path or database password, datastore will not be loaded")
    else:
        proxy.start(args.gca_credentials_path)
        dao.init(args.database_password)


    # spin up component APIs

    process_id = process.fork_processes(len(inventory.ports), max_restarts=0)

    if process_id <= len(inventory.ports) * 0.3:
        # video frame sequence extractor threads
        if (args.gca_credentials_path is not None) and (args.database_password is not None):
            instance = Application([
                (r"/healthcheck", HealthCheckHandler),
                (r"/results/(.*)", ResultGetterHandler),
                (r"/results", ResultQueryHandler),
                (r"/(.*)", StaticFileHandler,
                {"path": "static/apidocs/datasource/", "default_filename": "index.html"})
            ])

            port = inventory.ports[process_id]
            instance.listen(port)

            print("Data Source Interface listening on port " + str(port))

    elif process_id <= len(inventory.ports) * 0.6:
        # Indexer threads
        print("todo - todo index server")
    else:
        # frontend threads
        print("todo - todo frontend server")

    IOLoop.current().start()

if __name__ == "__main__":
    main()
