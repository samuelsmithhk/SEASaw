import os
import json
from os.path import join, dirname
from os import environ
from watson_developer_cloud import VisualRecognitionV3

img_files = []
dirname = './Images'
for files in os.listdir(dirname):
    if files.endswith('.jpg'):
        img_files.append(files)
                
visual_recognition = VisualRecognitionV3('2016-05-20', api_key='2165f1c705d401d4ca563e98dd25d52792d2f2d0')

for image in img_files:
    files = open("Images/" + str(image), "rb")
    print(json.dumps(visual_recognition.classify(images_file=files), indent=2))