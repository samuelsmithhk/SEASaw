from datetime import datetime, date, time, timedelta
import os

from apscheduler.schedulers.blocking import BlockingScheduler

from seasaw.visualRecognition.visualRecognition import Indexer

def formOptions():
    global times
    opts = dict()
    if not times: #empty start and end
        print ("Times are empty")
        inDate = datetime.now()
        endDate = inDate + timedelta(days=-1)
        times["start"] = list()
        times["start"].append(inDate)
        times["end"] = list()
        times["end"].append(endDate)
    else:
        print (str(times["end"]))
        inDate = times["end"][len(times["end"]) - 1]
        endDate = datetime.now()
        times["start"].append(inDate)
        times["end"].append(endDate)
    
    start = inDate.strftime("%y%m%d%H%M%S")
    end = endDate.strftime("%y%m%d%H%M%S")
    opts["start"] = start
    opts["end"] = end
    opts["pagination"] = 100
    opts["page"] = 1
    return opts

def index():
    opts = formOptions()
    Indexer('frames', 'pickleFiles', opts)


def removeFiles(dir):
    filelist = [ f for f in os.listdir(dir) ]
    for f in filelist:
        os.remove(dir + "/" + f)

times = dict()
if __name__ == '__main__':
    scheduler = BlockingScheduler()
    removeFiles('frames')
    removeFiles('pickleFiles')
    index()
    scheduler.add_job(index, 'interval', minutes=3)
    scheduler.start() 