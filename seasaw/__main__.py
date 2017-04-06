from tornado import process
from tornado.web import Application
from tornado.ioloop import IOLoop

from seasaw import inventory
from seasaw.datasource.datasourceinterface import HealthCheckHandler

def main():
    # spin up component APIs
    first_tri = inventory.thread_count * 0.3
    second_tri = inventory.thread_count * 0.6

    process_id = process.fork_processes(inventory.thread_count, max_restarts=0)

    if process_id <= first_tri:
        # video frame sequence extractor threads

        instance = Application([
            (r"/healthcheck", HealthCheckHandler)
        ])

        port = inventory.base_port + process_id
        instance.listen(port)

        print("Data Source Interface listening on port " + str(port))

    elif process_id <= second_tri:
        # indexer threads
        print("todo - indexer")
    else:
        # frontend threads
        print("todo - todo frontend")

    IOLoop.current().start()

if __name__ == "__main__":
    main()
