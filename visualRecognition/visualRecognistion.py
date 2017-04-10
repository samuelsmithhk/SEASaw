import os
import json
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3
import time

img_files = []
dirname = '../seasaw/frames'
for files in os.listdir(dirname):
    if files.endswith('.zip'):
        img_files.append(files)
                
visual_recognition = VisualRecognitionV3('2016-05-20', api_key='2165f1c705d401d4ca563e98dd25d52792d2f2d0')

f = open('classifier.txt', 'a')
for images in img_files:
    files = open(dirname + "/" + str(images), "rb")
    f.write(json.dumps(visual_recognition.classify(images_file=files), indent=2))
    time.sleep(30) # delays for 60 seconds