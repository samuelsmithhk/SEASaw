import re

class Result:
	def __init__(self, title, url_id, img, sT, tag):
		self.title = title
		self.url_id = url_id
		self.img = img
		self.start = sT
		self.tag = tag


result_row = """\t<div class="result-row">
    		<p class="result-title col-sm-offset-1" ><a href='{}'>{}</a></p>
       		<p class="result-url col-sm-offset-1" >{}</p>
       		<div class="row">"""

first = """\t<div class="col-sm-2 col-sm-offset-1">
             <p><a href="#media-popup" data-media="{}">
             <img border="0" alt="dog" src="{}" ></a></p>
             </div>\n"""
others = """\t<div class="col-sm-2">
             <p><a href="#media-popup" data-media="{}">
             <img border="0" alt="dog" src="{}" ></a></p>
             </div>\n"""
tags = """<div class="tags" style="margin-left: 10%; margin-right: 10%;"><p>{}</p></div>"""

def generateResultRows(res):
	output = ""
	
	for i in res:
		h = "https://www.youtube.com/watch?v="+i.url_id
		link="https://www.youtube.com/embed/"+i.url_id
		output += result_row.format(h, i.title, h)
		count = 1
		for j in range (len(i.img)):
			media="https://www.youtube.com/embed/"+i.url_id+"?start="+str(i.start[j])
			imgur="http://i.imgur.com/"+i.img[j]
			if count ==1:
				output += first.format(media, imgur)
			else:
				output += others.format(media, imgur)
			count+=1
		output += "		</div>\n"
		output += tags.format(i.tag)
		output += "		</div>\n"
	return output




