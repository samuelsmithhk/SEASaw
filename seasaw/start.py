from tornado import process
from tornado.web import Application
from tornado.ioloop import IOLoop

from seasaw import inventory
from seasaw.datasource.datasourceinterface import HealthCheckHandler

def main():
    # spin up component APIs

    process_id = process.fork_processes(len(inventory.ports), max_restarts=0)

    if process_id <= len(inventory.ports) * 0.3:
        # video frame sequence extractor threads

        instance = Application([
            (r"/healthcheck", HealthCheckHandler)
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
