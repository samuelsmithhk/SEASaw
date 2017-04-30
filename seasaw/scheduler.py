from datetime import datetime, date, time, timedelta
import os, argparse

from apscheduler.schedulers.blocking import BlockingScheduler
from seasaw.datasource.database import proxy
from seasaw.datasource.database import dao
from seasaw.visualRecognition.indexer import Indexer

def formOptions():
    global times
    opts = dict()
    if not times: #empty start and end
        endDate = datetime.now()
        inDate = endDate + timedelta(days=-100)
        times["start"] = list()
        times["start"].append(inDate)
        times["end"] = list()
        times["end"].append(endDate)
    else:
        inDate = times["end"][len(times["end"]) - 1]
        endDate = datetime.now()
        times["start"].append(inDate)
        times["end"].append(endDate)
    
    start = inDate.strftime("%y%m%d%H%M%S")
    end = endDate.strftime("%y%m%d%H%M%S")
    opts["start"] = start
    opts["end"] = end
    opts["pagination"] = 10000
    opts["page"] = 0
    return opts

def index():
    global indexer
    opts = formOptions()
    indexer.formIndexer('frames', opts)
    #print (indexer.getInvertedIndex())
    #print (indexer.getIDF())


def removeFiles(dir):
    filelist = [ f for f in os.listdir(dir) ]
    for f in filelist:
        os.remove(dir + "/" + f)

times = dict()

if __name__ == "__main__":
    parser = argparse.ArgumentParser('SEASaw - A Search Engine For Video Content')
    parser.add_argument("--gca_credentials_path", action="store", default=None, dest="gca_credentials_path")
    parser.add_argument("--database_password", action="store", default=None, dest="database_password")
    args = parser.parse_args()
    
    if (args.gca_credentials_path is None) or (args.database_password is None):
        print("start - Missing credential path or database password, datastore will not be loaded")
    else:
        proxy.start(args.gca_credentials_path)
        dao.init(args.database_password)
    
    try:
        scheduler = BlockingScheduler()
        indexer = Indexer('pickleFiles')
        
        #Remove already existing files
        removeFiles('frames')
        
        #Call Indexer
        index()
    
        #schedule index after intervals of 3 minutes
        scheduler.add_job(index, 'interval', minutes=10)
        scheduler.start() 
        
    except Exception as e:
        print (str(e))
    
    