import re

class Result:
	def __init__(self, title, url_id, img, sT):
		self.title = title
		self.url_id = url_id
		self.img = img
		self.start = sT




result_row = """\t<div class="col-sm-12 result-row">
    		<p class="result-title" >{}</p>
       		<p class="result-url" >https://www.youtube.com/embed/{}</p>
       		<div class="row">"""

inner = """\t<div class="col-sm-4 inner">
		<p><a href="#media-popup" data-media="{}">
		<img border="0" alt="dog" src="{}" ></a></p>
		</div>\n"""
outter = """\t<div class="col-sm-6 outter">
		<p><a href="#media-popup" data-media="{}">
		<img border="0" alt="bear" src="{}" >
		</a></p>
		</div>\n"""
row = "\t<div class=\"row\">"
col_seven = "\t<div class=\"col-sm-7\">"
col_five = "\t<div class=\"col-sm-5\">"

def generateResultRows(results):
	output = ""
	for i in results:
		link="https://www.youtube.com/embed/"+i.url_id
		output += result_row.format(i.title, link)
		output += "\n"
		output += col_seven
		output += "\n"
		output += row
		output += "\n"
		for j in range (len(i.img)):
			media="https://www.youtube.com/embed/"+i.url_id+"?start="+str(i.start[j])
			imgur="http://i.imgur.com/"+i.img[j]
			if j <= 2:
				output += inner.format(media, imgur)
		output += "\n</div>\n</div>\n"
		if(len(i.img) > 3):
			output += col_five
			output += "\n"
			output += row
			output += "\n"
			for k in range (len(i.img)):
				if k > 2: 
					media="https://www.youtube.com/embed/"+i.url_id+"?start="+str(i.start[j])
					imgur="http://i.imgur.com/"+i.img[j]
					output += outter.format(media, imgur)
			output += "\n</div>\n</div>\n"
		#close div for result-row and 1st row
		output += "		</div>\n</div>\n"
	return output




