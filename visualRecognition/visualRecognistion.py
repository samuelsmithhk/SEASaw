import os
import json
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3
import time
import zipfile

def checkZip(path):
    f = open('classifier.txt', 'a')
    visual_recognition = VisualRecognitionV3('2016-05-20', api_key='2165f1c705d401d4ca563e98dd25d52792d2f2d0')
    for files in os.listdir(path):
        if os.path.exists(path + '/Images.zip'):
            try:
                f.write(json.dumps(visual_recognition.classify(images_file=open(path + '/Images.zip', 'rb')), indent=2))
                os.remove(path + '/Images.zip')
            except Exception as e:
                print (str(e))

def formZip(path):
    f = open('classifier.txt', 'a')
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
                    f.write(json.dumps(visual_recognition.classify(images_file=open(path + '/Images.zip', 'rb')), indent=2))
                    os.remove(path + '/Images.zip')
                    zipf = zipfile.ZipFile(path + '/Images.zip', 'w', zipfile.ZIP_DEFLATED)
                    zipf.write(os.path.join(path, files))
                    os.remove(os.path.join(path, files))
                    count = 1
    
        #If any image is still left to be processes
        if count <=18:
            zipf.close()
            f.write(json.dumps(visual_recognition.classify(images_file=open(path + '/Images.zip', 'rb')), indent=2))
            os.remove(path + '/Images.zip')   
    except Exception as e:
        print (str(e))    

if __name__ == '__main__':
    checkZip('../seasaw/frames')
    formZip('../seasaw/frames')
                
    
        
    