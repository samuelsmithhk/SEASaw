from tornado.ioloop import IOLoop
import tornado.ioloop, tornado.web
from tornado import gen, httpclient

from urllib.parse import urlparse
from optparse import OptionParser
from datetime import datetime, date, time, timedelta
from .. import inventory

import time, hashlib, os, ast, requests, urllib.request, multiprocessing, emoji 

def checkEmoji(filename):
    for character in filename:
        if character in emoji.UNICODE_EMOJI:
            print (filename + " has emoji haence skipping")
            return True
    return False
    

def savePic(url, path, filename):
    file_extension = url.split(".")[-1]
    uri = ""
    dest = path + "/" + filename + "."+file_extension
    try:
        urllib.request.urlretrieve(url,dest)
    except Exception as e:
        print ("save failed" + str(e)) 
    return dest

class ImageDownload:
    def __init__(self, path, opts, videosProcessed):
        self.path = path
        self.videosProcessed = videosProcessed
        self.opts = opts
    
    def getVideos(self, video_ids):
        videos = []
        count = 20
        for id in video_ids:
            if len(videos) <= count:
                videos.append(id)
            else:
                break
        
        #videos.remove(1493312192)
        #videos.remove(1493315890)
        #videos.remove(1493315894)
        #videos.remove(1493325021)
        #videos.remove(1493331679)
        #videos.remove(1493331831)
        #videos.remove(1493341424)
        #videos.remove(1493341605)
        #videos.remove(1493342089)
        return videos
    
    @gen.coroutine
    def main(self):
        #Get video dataset
        video_ids = []
        httpclient.AsyncHTTPClient.configure(None, defaults={'connect_timeout': 300, 'request_timeout': 300})
        http = httpclient.AsyncHTTPClient()
        try: 
            while 1:
                destination = inventory.DATA_SERVERS[0] + "/results" + \
                      "?" + "start=" + str(self.opts["start"]) + \
                            "&end=" + str(self.opts["end"]) + \
                            "&pagination=" + str(self.opts["pagination"]) + \
                            "&page=" + str(self.opts["page"])
                print ("Fetching data: " + str(destination))
                request = tornado.httpclient.HTTPRequest(destination)
                response = yield http.fetch(request)
                results = ast.literal_eval(response.body.decode("utf-8"))
                if len(results["results"]) is 0:
                    break
                video_ids.append(results["results"])
                self.opts["page"] += 1
       
        except Exception as e:
            print (str(e))
            
        video_ids = [int(item) for sublist in video_ids for item in sublist]
        #Limit to 3 videos for processing
        video_ids = self.getVideos(video_ids)
        
        #Video Frame Processing
        tasks = []
        server_id = 0
        for id in video_ids:
            if id not in self.videosProcessed:
                if server_id >= inventory.DATA_PARTITIONS:
                    server_id = 0
                destination = inventory.DATA_SERVERS[server_id] + "/results/" + str(id)
                print ("Fetching video information: " + str(destination))
                tasks.append(http.fetch(destination))
                server_id += 1
                self.videosProcessed.append(id)
        
        if len(tasks) > 0:
            responses = yield tasks
            for response in responses:
                video_information = ast.literal_eval(response.body.decode("utf-8"))
                count = 1
                jobs = []
                for frame in video_information["frames"]:
                    if len(frame["url"]) > 0:
                        frame_url = "http://i.imgur.com/" + str(frame["url"])
                        filename = str(video_information["video_title"]) + "|" + str(video_information["result_id"]) + "|" + str(count)
                        if not checkEmoji(filename):
                            p = multiprocessing.Process(target=savePic, args=(frame_url, self.path, filename))
                            jobs.append(p)
                            p.start()
                            p.join()
                            count = count + 1
    
    def run(self):
        IOLoop.current().run_sync(self.main)
    
if __name__ == '__main__':
    ImageDownload('frames').run()
    
        
