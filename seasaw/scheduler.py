from datetime import datetime, date, time, timedelta
import os, argparse, shutil, time
from time import mktime

from apscheduler.schedulers.blocking import BlockingScheduler
from seasaw.datasource.database import proxy
from seasaw.datasource.database import dao
from seasaw.visualRecognition.indexer import Indexer
from . import inventory

def formOptions():
    global times
    opts = dict()
    if not times: #empty start and end
        endDate = datetime.now()
        inDate = endDate + timedelta(days=-1)
        times["start"] = list()
        times["start"].append(inDate)
        times["end"] = list()
        times["end"].append(endDate)
    else:
        inDate = times["end"][len(times["end"]) - 1]
        endDate = datetime.now()
        times["start"].append(inDate)
        times["end"].append(endDate)
    
    start = time.strptime(inDate.strftime("%y%m%d%H%M%S"), "%y%m%d%H%M%S")
    end = time.strptime(endDate.strftime("%y%m%d%H%M%S"), "%y%m%d%H%M%S")
    opts["start"] = int(mktime(start))
    opts["end"] = int(mktime(end))
    opts["pagination"] = 100
    opts["page"] = 0
    return opts

def index():
    global indexer
    global filename
    opts = formOptions()
    print ("Options: " + str(opts))
    indexer.formIndexer(filename, opts)
    #print (indexer.getInvertedIndex())
    #print (indexer.getIDF())


times = dict()

if __name__ == "__main__":
    parser = argparse.ArgumentParser('SEASaw - A Search Engine For Video Content')
    parser.add_argument("--gca_credentials_path", action="store", default=None, dest="gca_credentials_path")
    parser.add_argument("--database_password", action="store", default=None, dest="database_password")
    parser.add_argument("-l", action="store_true", dest="local")
    args = parser.parse_args()

    if args.local:
        inventory.set_local()
    else:
        inventory.set_linserv()

    while True:
        try:
            filename = 'frames' + datetime.now().strftime("%y%m%d%H%M%S")
            if (args.gca_credentials_path is None) or (args.database_password is None):
                print("start - Missing credential path or database password, datastore will not be loaded")
            else:
                proxy.start(args.gca_credentials_path)
                dao.init(args.database_password)

            scheduler = BlockingScheduler()
            indexer = Indexer('pickleFiles')
            
            #Remove already existing files
            if not os.path.exists(filename):
                os.makedirs(filename)

            #Call Indexer
            index()
    
            #schedule index after intervals of 3 minutes
            scheduler.add_job(index, 'interval', minutes=10)
            scheduler.start() 
        
        except Exception as e:
            print (str(e))
            if os.path.exists(filename):
                shutil.rmtree(filename)
            time.sleep(20)
            continue
    
    