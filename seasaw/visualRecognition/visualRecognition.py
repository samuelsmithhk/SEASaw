import os, json, os.path, time, zipfile, hashlib, ast, pickle, math, re

from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3
from collections import defaultdict

from seasaw import inventory
from seasaw.visualRecognition.imagedownload import ImageDownload
from ..datasource.database import dao



class VisualRecognition:
    def __init__(self, imagepath, opts, processedVideos):
        self.results = dict()
        ImageDownload(imagepath, opts, processedVideos).run()
        self.apikey = ['e9903171b11d1258bc872762834252187098d237',
                        'ab6cd6e728330688718e0277dc6401024381afc0',
                        'ff5a62b8cb6c07a58bf6f4022e6da76f1604fd4d',
                        'd06a064171f99e903821cb125039280f81289c94',
                        'b60c1ac7d8bef2b27096a822ffe72b26382f13d7',
                        '89a4bfa35196a41b777570a4e9e79bc70a1cee53',
                        '2165f1c705d401d4ca563e98dd25d52792d2f2d0', 
                        '25f0a035dea70d2513db56487e5a294201052422', 
                        '3d23140b752178eea59539e69cfd72d546a66d66',
                        'f4c65ebd717a4fee92c4a014bdeac3bc066a5324']
        self.key_pointer = 0
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