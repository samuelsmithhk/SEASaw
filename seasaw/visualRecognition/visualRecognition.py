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

class Indexer:
    def __init__(self, picklefilepath):
        #inDate = datetime.now()
        #endDate = inDate + timedelta(days=-1)
        
        #intervedIndexfull = False
        self.INVERTED_INDEX = dict()
        self.postings = defaultdict(dict)
        self.videos = list()
        self.IDF = dict()
        
        for i in range(0,inventory.INDEX_PARTITION):
            self.INVERTED_INDEX[i] = defaultdict(dict)
        #    if os.path.isfile(picklefilepath + '/InvertedIndex' + str(i) +'.pickle'):
        #        self.INVERTED_INDEX[i] = pickle.load(open(picklefilepath + '/InvertedIndex' + str(i) +'.pickle', 'rb'))
        #        intervedIndexfull = True
        #    else:
            
        
        #print ("Printing defaultdict: " + str(self.INVERTED_INDEX))
        self.filenames = [picklefilepath + '/InvertedIndex' + str(i) +'.pickle' for i in range(0,inventory.INDEX_PARTITION)]
        self.IDFfile = picklefilepath + '/IDF.pickle'
        
        #if not intervedIndexfull:
        #    self.postings = defaultdict(dict)
        #    self.videos = list()
        #else:
        #    self.formPostings()
        #    self.formVideos()
            
        #self.IDF = dict()
        
        #self.writeInvertedIndex()
        #self.writeIDF(picklefilepath)
    
    def formIndexer(self, imagepath, opts):
        if opts["start"] is None:
            opts["start"] = inDate.strftime("%y%m%d%H%M%S")
        if opts["end"] is None:
            opts["end"] = endDate.strftime("%y%m%d%H%M%S")
        if opts["pagination"] is None:
            opts["pagination"] = 100
        if opts["page"] is None:
            opts["page"] = 1
        
        self.results = dict()
        ImageDownload(imagepath, opts, self.videos).run()
        
        self.checkZip(imagepath)
        self.formZip(imagepath)
        self.formInvertedIndex()
        self.formIDF()   
        
        print ("Inverted Index: " + str(self.INVERTED_INDEX))
        print ("\nIDF: " + str(self.IDF))
        
        if (len(self.videos) >= 1000):
            self.writeInvertedIndex()
            self.writeIDF(picklefilepath)
    
    def formPostings(self):
        self.postings = self.INVERTED_INDEX[0]
        for i in range(1,inventory.INDEX_PARTITION):
            for term, value in self.INVERTED_INDEX[i].items():
                for video_id, score in value.items():
                    if video_id not in self.postings[term]:
                        self.postings[term][video_id] = score
                    else:
                        self.postings[term][video_id] += score
        
    def formVideos(self):
        self.videos = list()
        for term, value in self.postings.items():
            for video_id, score in value.items():
                if video_id not in self.videos:
                    self.videos.append(video_id)
        
    
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
        with open(self.IDFfile, 'wb') as handle:
            pickle.dump(self.IDF, handle, protocol=pickle.HIGHEST_PROTOCOL)
            handle.close()
    
    def formInvertedIndex(self):
        for key, value in self.results.items():
            images = value["images"]   
            for each in images:
                video_id = int(self.extractVideoInfo(each["image"].split("/"), "id"))
                video_title = self.extractVideoInfo(each["image"].split("/"), "title")
                self.addVideoIds(video_id)
                index_partition = int(hashlib.md5(str(video_id).encode()).hexdigest()[:8], 16) % inventory.INDEX_PARTITION
                classifiers = each['classifiers']
                self.addVideoTitleInvertedIndex(video_title.lower(), index_partition, video_id, 10)
                for classes in classifiers:
                    words = classes['classes'] 
                    for word in words:
                        tag = word['class'].split(" ")
                        for term in tag:
                            term = term.lower()
                            if video_id not in self.INVERTED_INDEX[index_partition][term]:
                                title_bonus = self.checkTitle(video_title, term)
                                self.INVERTED_INDEX[index_partition][term][video_id] = word['score'] + title_bonus
                            else:
                                self.INVERTED_INDEX[index_partition][term][video_id] += word['score']       
                        
                            self.updateTermFrequency(term, video_id, word['score'])
                
    
    def extractVideoInfo(self, data, info):
        for each in data:
            if ".jpg" in each:
                if "id" in info:
                    return each.split("|")[1]
                else:
                    return each.split("|")[0]
         
    def updateTermFrequency(self, tag, video_id, score):
        if video_id not in self.postings[tag]:
            self.postings[tag][video_id] = score
        else:
            self.postings[tag][video_id] += score
    
    def addVideoIds(self, video_id):
        if video_id not in self.videos:
            self.videos.append(video_id)
    
    def addVideoTitleInvertedIndex(self, title, index_partition, video_id, score):
        for word in title.split(" "):
            if video_id not in self.INVERTED_INDEX[index_partition][word]:
                self.INVERTED_INDEX[index_partition][word][video_id] = score
            else:
                self.INVERTED_INDEX[index_partition][word][video_id] += score
            
            self.updateTermFrequency(word, video_id, score)
    
    def checkTitle(self, title, term):
        if term in title.split(" "):
            return 10
        else:
            return 0
    
    
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
                    print ("Processing existing zip file")
                    os.remove(path + "/" + files)
                except Exception as e:
                    print (str(e))

    def formZip(self, path):
        visual_recognition = VisualRecognitionV3('2016-05-20', api_key='2165f1c705d401d4ca563e98dd25d52792d2f2d0')
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
                        taskId = hashlib.sha224(str(time.time()).encode()).hexdigest()
                        self.results[taskId] = visual_recognition.classify(images_file=open(path + '/Images.zip', 'rb'))
                        print ("Processing zip file")
                        os.remove(path + '/Images.zip')
                        zipf = zipfile.ZipFile(path + '/Images.zip', 'w', zipfile.ZIP_DEFLATED)
                        zipf.write(os.path.join(path, files))
                        os.remove(os.path.join(path, files))
                        count = 1
                        processed = False
    
            #If any image is still left to be processes
            if processed:
                zipf.close()
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