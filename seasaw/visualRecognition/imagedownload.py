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

def savePic(url, path, filename):
    file_extension = url.split(".")[-1]
    uri = ""
    dest = path + "/" + filename + "."+file_extension
    try:
        urllib.request.urlretrieve(url,dest)
    except:
        print ("save failed") 
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
                destination = inventory.DATA_SERVERS[(server_id) % len(inventory.DATA_SERVERS)] + "/results/" + str(id)
                print ("Fetching video information: " + str(destination))
                tasks.append(http.fetch(destination))
                server_id += 1
                self.videosProcessed.append(id)
        
        if len(tasks) > 0:
            responses = yield tasks
            for response in responses:
                video_information = ast.literal_eval(response.body.decode("utf-8"))
                count = 1
                for frame in video_information["frames"]:
                    frame_url = "http://i.imgur.com/" + str(frame["url"])
                    savePic(frame_url, self.path, str(video_information["video_title"]) + "|" + str(video_information["result_id"]) + "|" + str(count))
                    count = count + 1
    
    def run(self):
        IOLoop.current().run_sync(self.main)
    
if __name__ == '__main__':
    ImageDownload('frames').run()
    
        
