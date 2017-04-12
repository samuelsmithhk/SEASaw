from tornado.ioloop import IOLoop
import tornado.ioloop
import tornado.web
from tornado import gen, httpclient
from optparse import OptionParser
from datetime import datetime, date, time, timedelta
import time
from urllib.parse import urlparse
import hashlib
import os
import requests
import urllib.request
from . import inventory

def savePic(url):
    hs = hashlib.sha224(str(url).encode()).hexdigest()
    file_extension = url.split(".")[-1]
    uri = ""
    dest = uri+hs+"."+file_extension
    #print (dest)
    try:
        urllib.request.urlretrieve(url,dest)
    except:
        print ("save failed") 
    
    
class ImageDownload:
    @gen.coroutine
    def __init__(self):
        parser = OptionParser()
        inDate = datetime.now()
        endDate = inDate + timedelta(days=-10)
        parser.add_option("-m", "--start", dest="start" default=inDate.strftime("%y%m%d%H%M%S"))
        parser.add_option("-r", "--end", dest="end" default=endDate.strftime("%y%m%d%H%M%S"))
        parser.add_option("-j", "--pagination", dest="pagination", default=100)
        parser.add_option("-n", "--page", dest="page" default=1)
        (opts, args) = parser.parse_args()
    
        #Get video dataset
        data_output = []
        httpclient.AsyncHTTPClient.configure(None, defaults={'connect_timeout': 300, 'request_timeout': 300})
        http = httpclient.AsyncHTTPClient()
        for i in range(0,inventory.DATA_PARTITIONS):
            destination = DATA_SERVERS[i] + "/results?" + "start=" + opts.start + \
                            "&end=" + opts.end + \
                            "&pagination=" + opts.pagination + \
                            "&page=" + opts.page
            request = tornado.httpclient.HTTPRequest(destination)
            response = yield http.fetch(request)
            results = ast.literal_eval(response.body)
            data_output.append(results)
        
        video_ids = results["results"]
    
        #Video Processing
        tasks = []
        for id in video_ids:
            destination = "http://192.168.33.10:25280/results/" + str(id)
            tasks.append(http.fetch(destination))
        responses = yield tasks
        video_information = ast.literal_eval(responses.body)
        frame_urls = video_information["frames"]
    
        #Frame Processing
        for frame in frame_urls:
            savePic(frame)
        
