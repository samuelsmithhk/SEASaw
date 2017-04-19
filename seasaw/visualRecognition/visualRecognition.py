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
from seasaw.frames.imagedownload import ImageDownload

class Indexer:
    def __init__(self, path):
        #inDate = datetime.now()
        #endDate = inDate + timedelta(days=-1)
        #if opts["start"] is None:
        #    opts["start"] = inDate.strftime("%y%m%d%H%M%S")
        #if opts["end"] is None:
        #    opts["end"] = endDate.strftime("%y%m%d%H%M%S")
        #if opts["pagination"] is None:
        #    opts["pagination"] = 100
        #if opts["page"] is None:
        #    opts["page"] = 1
        
        ImageDownload().run()
        self.videos = list()
        self.INVERTED_INDEX = dict()
        for i in range(0,inventory.INDEX_PARTITION):
            self.INVERTED_INDEX[i] = defaultdict(dict)
        
        self.filenames = ['InvertedIndex' + str(i) +'.pickle' for i in range(0,inventory.INDEX_PARTITION)]
        
        self.postings = defaultdict(dict)
        self.IDF = dict()
        
        self.results = dict()
        self.checkZip(path)
        self.formZip(path)
        self.formInvertedIndex()
        self.formIDF()
        self.writeInvertedIndex()
        self.writeIDF()
                
    
    def writeInvertedIndex(self):
        indexpointer = 0
        for filename in self.filenames:
            filename = open(str(filename), 'wb')
            #f = open('temp' + str(indexpointer), 'w')
            #f.write(str(self.INVERTED_INDEX[indexpointer]))
            pickle.dump(self.INVERTED_INDEX[indexpointer], filename, protocol=pickle.HIGHEST_PROTOCOL)
            indexpointer = (indexpointer + 1) % inventory.INDEX_PARTITION
            filename.close()
            #f.close()
    
    def writeIDF(self):
        with open('InverseDocumentFrequency.pickle', 'wb') as handle:
            pickle.dump(self.IDF, handle, protocol=pickle.HIGHEST_PROTOCOL)
            handle.close()
    
    def formInvertedIndex(self):
        for key, value in self.results.items():
            images = value["images"]   
            for each in images:
                video_id = self.extractVideoId(each["image"].split("/"))
                self.addVideoIds(video_id)
                index_partition = int(hashlib.md5(str(video_id).encode()).hexdigest()[:8], 16) % inventory.INDEX_PARTITION
                classifiers = each['classifiers']
                for classes in classifiers:
                    words = classes['classes'] 
                    for word in words:
                        tag = word['class']
                        self.updateTermFrequency(tag, video_id)
                        if video_id not in self.INVERTED_INDEX[index_partition][tag]:
                            self.INVERTED_INDEX[index_partition][tag][video_id] = word['score']
                        else:
                            self.INVERTED_INDEX[index_partition][tag][video_id] += word['score']     
                
    
    def extractVideoId(self, data):
        for each in data:
            if ".jpg" in each:
                return each.split("_")[0]
         
    
    def updateTermFrequency(self, tag, video_id):
        if video_id not in self.postings[tag]:
            self.postings[tag][video_id] = 1
        else:
            self.postings[tag][video_id] += 1
    
    def addVideoIds(self, video_id):
        if video_id not in self.videos:
            self.videos.append(video_id)
    
    def formIDF(self):
        for term in self.postings:
            self.IDF[term] = math.log10(len(self.videos)/ float(len(self.postings[term])))
    
    def checkZip(self, path):
        visual_recognition = VisualRecognitionV3('2016-05-20', api_key='2165f1c705d401d4ca563e98dd25d52792d2f2d0')
        #json.dump(visual_recognition.classify(images_file=open(path + '/63db58a5ccc044c20da38c92393008bda55bbf8832970cbe47a8c854.jpg', 'rb')), f, indent=2)
        for files in os.listdir(path):
            if files.endswith('.zip'):
                try:
                    taskId = hashlib.sha224(str(time.time()).encode()).hexdigest()
                    self.results[taskId] = visual_recognition.classify(images_file=open(path + "/" + files, 'rb'))
                    os.remove(path + "/" + files)
                except Exception as e:
                    print (str(e))

    def formZip(self, path):
        visual_recognition = VisualRecognitionV3('2016-05-20', api_key='2165f1c705d401d4ca563e98dd25d52792d2f2d0')
        count = 0
        try:
            zipf = zipfile.ZipFile(path + '/Images.zip', 'w', zipfile.ZIP_DEFLATED)
            for files in os.listdir(path):
                if files.endswith('.jpg'):
                    if count <= 17:
                        zipf.write(os.path.join(path, files))
                        count = count + 1
                        os.remove(os.path.join(path, files))
                    else:
                        zipf.close()
                        taskId = hashlib.sha224(str(time.time()).encode()).hexdigest()
                        self.results[taskId] = visual_recognition.classify(images_file=open(path + '/Images.zip', 'rb'))
                        os.remove(path + '/Images.zip')
                        zipf = zipfile.ZipFile(path + '/Images.zip', 'w', zipfile.ZIP_DEFLATED)
                        zipf.write(os.path.join(path, files))
                        os.remove(os.path.join(path, files))
                        count = 1
    
            #If any image is still left to be processes
            if count <=17:
                zipf.close()
                taskId = hashlib.sha224(str(time.time()).encode()).hexdigest()
                self.results[taskId] = visual_recognition.classify(images_file=open(path + '/Images.zip', 'rb'))
                os.remove(path + '/Images.zip')   
    
        except Exception as e:
            print (str(e))    


if __name__ == '__main__':
    Indexer('seasaw/frames')   