import requests
import urllib.request
import mechanicalsoup 
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import hashlib

def searchPic(term):
    img_list = getPic(term)
    if len(img_list)>0:
        for img in img_list:
            savePic(img)
    print ("done...")     

def getPic (search):
    search = search.replace(" ","%20")
    try:
        browser = mechanicalsoup.StatefulBrowser()
        #browser.set_verbose(2)
        #browser.set_handle_robots(False)
        #browser.addheaders = [('User-agent','Mozilla')]

        htmltext = browser.open("http://www.omgmix.com/2012/07/top-27-sea-animals-wallpapers-in-hd.html")
        #print (htmltext)
        img_urls = []
        formatted_images = []
        soup = BeautifulSoup(htmltext.text)
        results = soup.findAll("img")
        for r in results:
            try:
                if ".jpg" in r['src']:
                    #print (r['src'])
                    img_urls.append(r['src'])
            except:
                a=0

        #for im in img_urls:
            #refer_url = urlparse(str(im))
            #image_f = refer_url.query.split("&")[0].replace("imgurl=","")
            #formatted_images.append(image_f)
        
        #return  formatted_images
        return img_urls
    except:
        return []

def savePic(url):
    hs = hashlib.sha224(str(url).encode()).hexdigest()
    file_extension = url.split(".")[-1]
    uri = ""
    dest = uri+hs+"."+file_extension
    print (dest)
    try:
        urllib.request.urlretrieve(url,dest)
    except:
        print ("save failed") 
searchPic("sea animals") 