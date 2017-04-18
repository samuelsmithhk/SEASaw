from apscheduler.schedulers.blocking import BlockingScheduler

from seasaw.visualRecognition.visualRecognition import Indexer

def scheduled_job(): 
    Indexer('frames', 'pickleFiles')

sched = BlockingScheduler()
Indexer('frames', 'pickleFiles')
sched.add_job(scheduled_job, "interval", hours=0.5)
sched.start()