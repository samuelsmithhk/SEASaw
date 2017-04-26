import argparse
import time
import pymysql

from tornado import process
from tornado.web import Application
from tornado.web import StaticFileHandler
from tornado.ioloop import IOLoop
from random import randint

from seasaw import inventory
from seasaw.datasource.datasourceinterface import HealthCheckHandler
from seasaw.datasource.datasourceinterface import ResultQueryHandler
from seasaw.datasource.datasourceinterface import ResultGetterHandler
from seasaw.datasource.database import proxy
from seasaw.datasource.database import dao
from seasaw.datasource import scraper
from seasaw.datasource import imguruploader
from seasaw.datasource import datasourceuploader


def main():
    parser = argparse.ArgumentParser('SEASaw - A Search Engine For Video Content')
    parser.add_argument("--gca_credentials_path", action="store", default=None, dest="gca_credentials_path")
    parser.add_argument("--database_password", action="store", default=None, dest="database_password")
    parser.add_argument("--imgur_password", action="store", default=None, dest="imgur_password")
    args = parser.parse_args()

    if (args.gca_credentials_path is None) or (args.database_password is None):
        print("start - Missing credential path or database password, datastore will not be loaded")
    else:
        proxy.start(args.gca_credentials_path)
        dao.init(args.database_password)

    # spin up component APIs
    process_id = process.fork_processes(len(inventory.ports), max_restarts=1)

    if process_id is 0:
        print("start - initiating scraper")
        # youtube scraper
        for i in range(0, 5):
            term_index = randint(0, len(inventory.search_terms))
            term = inventory.search_terms[term_index]
            print("start - setting scraper to find 10 results for " + term)
            scraper.start(term, 10)

        print("start - scraper finished")
    elif process_id is 1:
        #imgur uploader
        if args.imgur_password is None:
            print("start - imgur password not specified in program args, imgur component will not be launched")
        else:
            print("start - imgur uploader running")
            while True:
                result = imguruploader.start(args.imgur_password)
                if result is 1:
                    print("start - rate limit exceeded, imgur component will pause for a while")
                    time.sleep(120)
                elif result is 2:
                    print("start - nothing for imgur uploader to do, imgur component will pause for a while")
                    time.sleep(120)
    elif process_id is 2:
        # database uploader
        print("start - initiating database uploader")
        while True:
            result = datasourceuploader.start()
            time.sleep(30)
    elif process_id > 2:
        if process_id <= (len(inventory.ports) * 0.3) + 3:
            # datasource api
                instance = Application([
                    (r"/healthcheck", HealthCheckHandler),
                    (r"/results/(.*)", ResultGetterHandler),
                    (r"/results", ResultQueryHandler),
                    (r"/(.*)", StaticFileHandler,
                     {"path": "static/apidocs/datasource/", "default_filename": "index.html"})
                ])

                port = inventory.ports[process_id - 3]
                instance.listen(port)

                print("start - Data Source Interface listening on port " + str(port))

        elif process_id <= (len(inventory.ports) * 0.6) + 3:
            # Index server threads
            print("start - todo - todo index server")
        else:
            # frontend threads
            print("start - todo - todo frontend server")
    
    IOLoop.current().start()

if __name__ == "__main__":
    main()
