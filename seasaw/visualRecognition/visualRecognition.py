import os
import json
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3
import time
import zipfile
import time
import hashlib
import ast
from seasaw import inventory
from collections import defaultdict
import hashlib
import pickle
import math
from seasaw.visualRecognition.imagedownload import ImageDownload
import os.path
from ..datasource.database import dao
import re


class VisualRecognition:
    def __init__(self, imagepath, opts, processedVideos):
        if opts["start"] is None:
            opts["start"] = inDate.strftime("%y%m%d%H%M%S")
        opts["start"] = ""
        if opts["end"] is None:
            opts["end"] = endDate.strftime("%y%m%d%H%M%S")
        opts["end"] = ""
        if opts["pagination"] is None:
            opts["pagination"] = 1000
        opts["pagination"] = 1000
        if opts["page"] is None:
            opts["page"] = 1
        opts["page"] = 0
            
        self.results = dict()
        ImageDownload(imagepath, opts, processedVideos).run()
        self.apikey = ['2165f1c705d401d4ca563e98dd25d52792d2f2d0', 
                        '25f0a035dea70d2513db56487e5a294201052422', 
                        'f36ee294e6d1f427a0715d5cc90195ef929b259c']
        self.key_pointer = 2
        self.checkPNGImages(imagepath)
        self.checkZip(imagepath)
        self.formZip(imagepath)
    
    def getResults(self):
        return self.results
    
    def checkPNGImages(self, path):
        for files in os.listdir(path):
            if files.endswith('.png'):
                try:
                    visual_recognition = VisualRecognitionV3('2016-05-20', api_key=self.apikey[self.key_pointer % len(self.apikey)])
                    taskId = hashlib.sha224(str(time.time()).encode()).hexdigest()
                    self.results[taskId] = visual_recognition.classify(images_file=open(path + "/" + files, 'rb'))
                    print ("Processing png file: " + str(files))
                    os.remove(os.path.join(path, files))
                    time.sleep(5) #Sleep for 5 seconds so as to avoid connection failure
                    self.key_pointer += 1
                except Exception as e:
                    print (str(e))
    
    
    def checkZip(self, path):
        for files in os.listdir(path):
            if files.endswith('.zip'):
                try:
                    visual_recognition = VisualRecognitionV3('2016-05-20', api_key=self.apikey[ self.key_pointer % len(self.apikey)])
                    taskId = hashlib.sha224(str(time.time()).encode()).hexdigest()
                    self.results[taskId] = visual_recognition.classify(images_file=open(path + "/" + files, 'rb'))
                    print ("Processing existing zip file")
                    os.remove(path + "/" + files)
                    self.key_pointer += 1
                except Exception as e:
                    print (str(e))

    def formZip(self, path):
        count = 0
        try:
            zipf = zipfile.ZipFile(path + '/Images.zip', 'w', zipfile.ZIP_DEFLATED)
            processed = False
            for files in os.listdir(path):
                if files.endswith('.jpg'):
                    if count <= 17:
                        zipf.write(os.path.join(path, files))
                        count = count + 1
                        os.remove(os.path.join(path, files))
                        processed = True
                    else:
                        zipf.close()
                        visual_recognition = VisualRecognitionV3('2016-05-20', api_key=self.apikey[ self.key_pointer % len(self.apikey)])
                        taskId = hashlib.sha224(str(time.time()).encode()).hexdigest()
                        self.results[taskId] = visual_recognition.classify(images_file=open(path + '/Images.zip', 'rb'))
                        print ("Processing zip file")
                        os.remove(path + '/Images.zip')
                        zipf = zipfile.ZipFile(path + '/Images.zip', 'w', zipfile.ZIP_DEFLATED)
                        zipf.write(os.path.join(path, files))
                        os.remove(os.path.join(path, files))
                        count = 1
                        processed = False
                        self.key_pointer += 1

            #If any image is still left to be processes
            if processed:
                zipf.close()
                visual_recognition = VisualRecognitionV3('2016-05-20', api_key=self.apikey[0])
                taskId = hashlib.sha224(str(time.time()).encode()).hexdigest()
                self.results[taskId] = visual_recognition.classify(images_file=open(path + '/Images.zip', 'rb'))
                print ("Processing zip file")
                os.remove(path + '/Images.zip')  
            
            #Remove Images.zip which is empty
            if os.path.isfile(path + '/Images.zip'): 
                os.remove(path + '/Images.zip')
    
        except Exception as e:
            print (str(e))    


if __name__ == '__main__':
    Indexer('frames', 'pickleFiles')   