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

from seasaw.frontend.frontendinterface import IndexDotHTMLAwareStaticFileHandler
from seasaw.frontend.frontendinterface import SearchHandler
from seasaw.frontend.frontendinterface import IndexDotHTMLAwareStaticFileHandlerL
from seasaw.frontend.frontendinterface import SearchHandlerL

#import seasaw.scheduler 

SETTINGS = {'static_path': inventory.WEBAPP_PATH,
            'template_path':inventory.WEBAPP_PATH }

def main():
    parser = argparse.ArgumentParser('SEASaw - A Search Engine For Video Content')
    parser.add_argument("--gca_credentials_path", action="store", default=None, dest="gca_credentials_path")
    parser.add_argument("--database_password", action="store", default=None, dest="database_password")
    parser.add_argument("--imgur_password", action="store", default=None, dest="imgur_password")
    parser.add_argument("-s", action="store_true", dest="run_scraper") # will not run on linux box, due to dependencies
    parser.add_argument("-l", action="store_true", dest="local") # local env and linserv have differences
    args = parser.parse_args()

    if (args.gca_credentials_path is None) or (args.database_password is None):
        print("start - Missing credential path or database password, datastore will not be loaded")
    else:
        proxy.start(args.gca_credentials_path)
        dao.init(args.database_password)

    # spin up component APIs
    process_id = process.fork_processes(len(inventory.ports), max_restarts=100)

    if process_id is 0:
        if args.run_scraper:
            print("start - initiating scraper")
            # youtube scraper
            for i in range(0, 5):
                term_index = randint(0, len(inventory.search_terms) - 1)
                term = inventory.search_terms[term_index]
                print("start - setting scraper to find 10 results for " + term)
                scraper.start(term, 10)
                print("start - resting scraper")
                time.sleep(3600)
            print("start - scraper finished")
    elif process_id is 1:
        # imgur uploader
        if args.imgur_password is None or args.run_scraper is False:
            print("start - imgur uploader not running")
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
        if args.run_scraper:
            print("start - initiating database uploader")
            while True:
                datasourceuploader.start()
                time.sleep(30)
    elif process_id is 3 or process_id is 4:
        # datasource api

        if args.local:
            instance = Application([
                (r"/healthcheck", HealthCheckHandler),
                (r"/results/(.*)", ResultGetterHandler),
                (r"/results", ResultQueryHandler),
                (r"/(.*)", StaticFileHandler,
                 {"path": "static/apidocs/datasource_local/", "default_filename": "index.html"})
            ])
        else:
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

    else:
        # Index server threads
        port = inventory.ports[process_id]
        if( port == 25285):
            if(args.local): #vagrant
                instance = Application([
                    (r'/search', SearchHandler),
                    (r'/(.*)', IndexDotHTMLAwareStaticFileHandler, dict(path=SETTINGS['static_path']))
                    ], **SETTINGS)
                print("start - Frontend Interface listening on port " + str(port))
                instance.listen(port)
            else:#linserv
                instance = Application([
                    (r'/search', SearchHandlerL),
                    (r'/(.*)', IndexDotHTMLAwareStaticFileHandlerL, dict(path=SETTINGS['static_path']))
                    ], **SETTINGS)
                print("start - Frontend Interface listening on port " + str(port))
                instance.listen(port)
    
    IOLoop.current().start()

if __name__ == "__main__":
    main()
