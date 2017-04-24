from datetime import datetime, date, time, timedelta
import os

from apscheduler.schedulers.blocking import BlockingScheduler

from seasaw.visualRecognition.visualRecognition import Indexer

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
    
    start = inDate.strftime("%y%m%d%H%M%S")
    end = endDate.strftime("%y%m%d%H%M%S")
    print ("Start time used: " + start)
    print ("End time used: " + end)
    opts["start"] = start
    opts["end"] = end
    opts["pagination"] = 100
    opts["page"] = 1
    return opts

def index():
    global indexer
    opts = formOptions()
    indexer.formIndexer('frames', opts)
    print (indexer.getInvertedIndex())
    print (indexer.getIDF())


def removeFiles(dir):
    filelist = [ f for f in os.listdir(dir) ]
    for f in filelist:
        os.remove(dir + "/" + f)

times = dict()
indexer = Indexer('pickleFiles')
if __name__ == '__main__':
    scheduler = BlockingScheduler()
    
    #Remove already existing files
    removeFiles('frames')
    removeFiles('pickleFiles')
    
    #Call Indexer
    index()
    
    #schedule index after intervals of 3 minutes
    scheduler.add_job(index, 'interval', minutes=3)
    scheduler.start() 
    
    
    
    
    
    
    
    
    
    
    