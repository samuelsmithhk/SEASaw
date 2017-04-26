from tornado.ioloop import IOLoop
import tornado.ioloop
import tornado.web
from tornado import gen, httpclient
from optparse import OptionParser
from datetime import datetime, date, time, timedelta
import time
from urllib.parse import urlparse
#from urlparse import urlparse
import hashlib
import os
import ast
import requests
import urllib.request
from .. import inventory
import multiprocessing

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
    
    @gen.coroutine
    def main(self):
        #Get video dataset
        video_ids = []
        httpclient.AsyncHTTPClient.configure(None, defaults={'connect_timeout': 300, 'request_timeout': 300})
        http = httpclient.AsyncHTTPClient()
        try: 
            destination = inventory.DATA_SERVERS[0] + "/results" #+ \
            #          "?" + "start=" + self.opts["start"] + \
            #                "&end=" + self.opts["end"] + \
            #                "&pagination=" + str(self.opts["pagination"]) + \
            #                "&page=" + str(self.opts["page"])
            print ("Fetching data: " + str(destination))
            request = tornado.httpclient.HTTPRequest(destination)
            response = yield http.fetch(request)
            results = ast.literal_eval(response.body.decode("utf-8"))
            video_ids.append(results["results"])
        except:
            pass
            
        video_ids = [int(item) for sublist in video_ids for item in sublist]
        
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
                        p = multiprocessing.Process(target=savePic, args=(frame_url, self.path, filename))
                        #savePic(frame_url, self.path, filename)
                        jobs.append(p)
                        p.start()
                        p.join()
                        count = count + 1
    
    def run(self):
        IOLoop.current().run_sync(self.main)
    
if __name__ == '__main__':
    ImageDownload('frames').run()
    
        
