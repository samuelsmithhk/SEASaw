import re

class Result:
	def __init__(self, title, url_id, img, sT):
		self.title = title
		self.url_id = url_id
		self.img = img
		self.start = sT


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


def generateResultRows(res):
	output = ""
	# print("there are " + str(len(res)) +"results!!!!!!!!!!!")
	for i in res:
		h = "https://www.youtube.com/watch?v="+i.url_id
		link="https://www.youtube.com/embed/"+i.url_id
		output += result_row.format(h, i.title, h)
		# output += "\n"
		# output += col_seven
		# output += "\n"
		# output += row
		# output += "\n"
		count = 1
		for j in range (len(i.img)):
			media="https://www.youtube.com/embed/"+i.url_id+"?start="+str(i.start[j])
			imgur="http://i.imgur.com/"+i.img[j]
			if count ==1:
				output += first.format(media, imgur)
			else:
				output += others.format(media, imgur)
			count+=1
		# 	media="https://www.youtube.com/embed/"+i.url_id+"?start="+str(i.start[j])
		# 	imgur="http://i.imgur.com/"+i.img[j]
		# 	if j <= 2:
		# 		output += inner.format(media, imgur)
		# output += "\n</div>\n</div>\n"
		# if(len(i.img) > 3):
		# 	output += col_five
		# 	output += "\n"
		# 	output += row
		# 	output += "\n"
		# 	for k in range (len(i.img)):
		# 		if k > 2: 
		# 			media="https://www.youtube.com/embed/"+i.url_id+"?start="+str(i.start[j])
		# 			imgur="http://i.imgur.com/"+i.img[j]
		# 			output += outter.format(media, imgur)
		# 	output += "\n</div>\n</div>\n"
		# #close div for result-row and 1st row
		output += "		</div>\n</div>\n"
	return output




