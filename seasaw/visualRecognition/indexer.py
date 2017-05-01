import os, json, time, zipfile, hashlib, ast, pickle, math, os.path, re, string

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3
from collections import defaultdict

from seasaw import inventory
from seasaw.visualRecognition.imagedownload import ImageDownload
from ..datasource.database import dao
from seasaw.visualRecognition.visualRecognition import VisualRecognition

class Indexer:
    def __init__(self, picklefilepath):
        self.INVERTED_INDEX = dict()
        self.postings = defaultdict(dict)
        self.videos = list()
        self.IDF = dict()
        
        for i in range(0,inventory.INDEX_PARTITION):
            self.INVERTED_INDEX[i] = defaultdict(dict)
            
        self.filenames = [picklefilepath + '/InvertedIndex' + str(i) +'.pickle' for i in range(0,inventory.INDEX_PARTITION)]
        self.IDFfile = picklefilepath + '/IDF.pickle'
        self.videosFile = picklefilepath + '/ProcessedVideos.pickle'
        
        self.processedVideos = dao.select_processed_videos()
        print ("processedVideos: " + str(self.processedVideos))
        #self.processedVideos= []
        
    def formIndexer(self, imagepath, opts):     
        self.videoInfo = defaultdict(dict)
        self.results = VisualRecognition(imagepath, opts, self.processedVideos).getResults()
        self.formInvertedIndex()
        self.formIDF() 
        
        #print ("InvertedIndex: " + str(self.INVERTED_INDEX))
        #print ("IDF: " + str(self.IDF))
        
        if (len(self.videos) >= 1):
            #self.downloadPickleFiles('pickleFiles')
            if self.writeProcessedVideos():
                self.writeInvertedIndex()
                self.writeIDF()
            
            self.processedVideos = dao.select_processed_videos()
            print ("processedVideos: " + str(self.processedVideos))
            with open(self.videosFile, 'wb') as handle:
                pickle.dump(self.processedVideos, handle, protocol=pickle.HIGHEST_PROTOCOL)
                print ("Videos processed file write operation complete")
                handle.close()
                
            self.INVERTED_INDEX = dict()
            self.postings = defaultdict(dict)
            self.videos = list()
            self.IDF = dict()
            
            for i in range(0,inventory.INDEX_PARTITION):
                self.INVERTED_INDEX[i] = defaultdict(dict)
            
    def getInvertedIndex(self):
        return self.INVERTED_INDEX
        
    def getIDF(self):
        return self.IDF    
    
    def writeInvertedIndex(self):
        indexpointer = 0
        for filename in self.filenames:
            filename = open(str(filename), 'ab')
            #f = open('temp' + str(indexpointer), 'w')
            #f.write(str(self.INVERTED_INDEX[indexpointer]))
            pickle.dump(self.INVERTED_INDEX[indexpointer], filename, protocol=pickle.HIGHEST_PROTOCOL)
            indexpointer = (indexpointer + 1) % inventory.INDEX_PARTITION
            print ("INVERTED_INDEX" + str(indexpointer) + " Pickle updated")
            filename.close()
            #f.close()
    
    def writeIDF(self):
        with open(self.IDFfile, 'ab') as handle:
            pickle.dump(self.IDF, handle, protocol=pickle.HIGHEST_PROTOCOL)
            print ("IDF Pickle updated")
            handle.close()
    
    def writeProcessedVideos(self):
        processed = True
        for id, videoInfo in self.videoInfo.items():
            print ("Video Info" + str(videoInfo))
            dao.insert_processed_videos(videoInfo)
                
        return processed
            
            
    def formInvertedIndex(self):
        for key, value in self.results.items():
            images = value["images"]   
            for each in images:
                if 'classifiers' in each and len(each["image"]) > 0: 
                    video_id = int(self.extractVideoInfo(each["image"].split("/"), "id"))
                    video_title = self.extractVideoInfo(each["image"].split("/"), "title")
                
                    index_partition = int(hashlib.md5(str(video_id).encode()).hexdigest()[:8], 16) % inventory.INDEX_PARTITION
                    classifiers = each['classifiers']
                    
                    self.videoInfo[video_id]["result_id"] = str(video_id)
                    if video_id not in self.videos:
                        print ("Processing " + str(video_id) + "'s title " + str(video_title))
                        self.videoInfo[video_id]["tags"] = list()
                        self.addVideoTitleInvertedIndex(video_title.lower(), index_partition, video_id, 10)
                    
                    self.addVideoIds(video_id)
                    for classes in classifiers:
                        words = classes['classes'] 
                        for word in words:
                            tag = word['class'].split(" ")
                            for term in tag:
                                term = term.lower()
                                term = re.sub('\W+','', term)
                                if video_id not in self.INVERTED_INDEX[index_partition][term]:
                                    title_bonus = self.checkTitle(video_title, term)
                                    self.INVERTED_INDEX[index_partition][term][video_id] = word['score'] + title_bonus
                                else:
                                    self.INVERTED_INDEX[index_partition][term][video_id] += word['score']       
                        
                                self.updateTermFrequency(term, video_id, word['score'])
                                self.videoInfo[video_id]["tags"].append(term)
            
    
    def extractVideoInfo(self, data, info):
        for each in data:
            if ".jpg" in each:
                temp = each.split("|")
                if "id" in info:
                    return temp[len(temp)-2]
                else:
                    if len(temp) > 3:
                        title = "|".join(temp[i] for i in range(0,len(temp)-2))
                    else:
                        title = temp[len(temp)-3]
                    return title
                
            elif ".png" in each:
                temp = each.split("|")
                if "id" in info:
                    return temp[len(temp)-2]
                else:
                    if len(temp) > 3:
                        title = "|".join(temp[i] for i in range(0,len(temp)-2))
                    else:
                        title = temp[len(temp)-3]    
                    return title
         
    def updateTermFrequency(self, tag, video_id, score):
        if video_id not in self.postings[tag]:
            self.postings[tag][video_id] = score
        else:
            self.postings[tag][video_id] += score
    
    def addVideoIds(self, video_id):
        if video_id not in self.videos:
            self.videos.append(video_id)
            self.processedVideos.append(video_id)
    
    def addVideoTitleInvertedIndex(self, title, index_partition, video_id, score):
        stopWords = set(stopwords.words('english'))
        punctuations = list(string.punctuation)
        casefoldData = title.casefold() 
        tokens = word_tokenize(casefoldData)
        filteredSentence = [w for w in tokens if w not in stopWords]
        filteredSentence = [w for w in filteredSentence if w not in punctuations]
        for word in filteredSentence:
            if word.isalpha():
                if video_id not in self.INVERTED_INDEX[index_partition][word]:
                    self.INVERTED_INDEX[index_partition][word][video_id] = score
                else:
                    self.INVERTED_INDEX[index_partition][word][video_id] += score
            
                self.updateTermFrequency(word, video_id, score)
                self.videoInfo[video_id]["tags"].append(word)
                
    def checkTitle(self, title, term):
        if term in title.split(" "):
            return 10
        else:
            return 0
    
    
    def formIDF(self):
        for term in self.postings:
            self.IDF[term] = math.log10(len(self.videos)/ float(len(self.postings[term])))
        