#!PYTHON
import os
import time
import re
import webvtt
import sys
import time
import json
import requests

class YTB:
	def __init__(self,youtube_id,working_dir=os.getcwd()):
		self.id=youtube_id #ID
		#default values
		self.meta=0#meta (from json)
		self.videofile="" #videofile
		self.lang=""#subs language
		self.subs=1 #Subtitles yes /no
		self.res=480 #video resolution
		self.subfile=""	#subtitle file
		self.proxy="" #proxy
		self.out=working_dir+"/out/" #output directory
		self.keylevel=3 #keylevel
		self.pdf=1 #pdf yes / no
		self.speed="7M" #speed limit
		self.retries=9 #how often to try downloads
		self.maxseconds=0
		self.maxframes=0
		self.cooldown=30
		self.title=""
		self.description=""
		self.time_data=[]
		
	def get_meta(yt):#returns meta dict
		os.system('youtube-dl --write-info-json --write-sub --write-auto-sub --write-annotations --skip-download --id '+yt.id)
		os.system('rm *.??.vtt > /dev/null')
		meta=json.loads(open(v.id+".info.json").read())
		yt.meta=meta
		return meta
	def get_lang(yt):#returns str (en)
		meta=yt.meta
		try:
			lang=meta["subtitles"]["en"][0]["url"][meta["subtitles"]["en"][0]["url"].find("lang=")+5:meta["subtitles"]["en"][0]["url"].find("lang=")+7]
		except:
			try:
				lang=meta["automatic_captions"]["en"][0]["url"][meta["automatic_captions"]["en"][0]["url"].find("lang=")+5:meta["automatic_captions"]["en"][0]["url"].find("lang=")+7]
			except:
				print("except in language selection using "+lang)
		try:
			if(lang==""):lang="en"
		except:
			lang="en"
		yt.lang=lang
		return lang
	def download_video(yt):
		fmt='best[height<='+str(yt.res)+']'
		os.system('youtube-dl -i --proxy "'+yt.proxy+'" --socket-timeout 34 --sub-lang '+yt.lang+' --format "'+fmt+'" --write-sub --write-auto-sub --no-playlist --write-info-json --write-thumbnail --id -r '+yt.speed+' '+yt.id)
	def generate_time_data(yt,framesdir="frames"):#0 time in s     1 data (image or text)     2 type ("image" or "text")     3 time as timestamped
		yt.maxseconds=int(yt.meta["duration"])
		yt.maxframes=int(os.popen('mediainfo --Output="Video;%FrameCount%" '+yt.videofile).read().replace("\n",""))	
		time_data=[]
		if(yt.subs==1):
			if(yt.subfile[-3:]=="srt"):
				subvtt=webvtt.from_srt(yt.subfile)
			if(yt.subfile[-3:]=="vtt"):
				subvtt=webvtt.read(yt.subfile)
			 #0 time in s     1 data (image or text)     2 type ("image" or "text")     3 time as timestamped
			for i in subvtt:
				ti_me=sum(x * float(t) for x, t in zip([3600, 60, 1], i.end.split(":")))
				time_data.append([ti_me, i.text, "text", i.start])
			no_duplicates=[]
			buf=[]
			for elements in time_data:
				if(elements[2]=="text"):
					t=elements[0]
					for i in elements[1].split("\n"):
						if(i.replace(" ","")!=""):
							buf.append([t,i,elements[3]])
			lastone=[]
			for i in buf:
				if(i[1]!=lastone):
					no_duplicates.append([i[0],i[1],"text",i[2]])
					lastone=i[1]
			time_data=no_duplicates

		frameslist=os.listdir(framesdir)
		frames=[]
		for i in frameslist:
			framenr=int(i[:i.find(".")])
			framepos=framenr/yt.maxframes
			framesec=framepos*yt.maxseconds
			hour_=int(framesec/3600)
			minute_=int((framesec/60)-hour_*60)
			second_=int((framesec-(hour_*3600))-(minute_*60))
			tstmp=str(hour_).zfill(2)+":"+str(minute_).zfill(2)+":"+str(second_).zfill(2)
			time_data.append([framesec,framenr,"image", tstmp])
		time_data.sort(key=lambda tup:tup[0])
		yt.time_data=time_data
		return time_data

def replace_all(text, dic):#returns str
    for i, j in dic.items():
        text = text.replace(i, j)
    return text
   
def find_videofile():#returns str (name of video file)
	formats=("mp4","webm","mkv","flv","vob","avi","m4v","f4v","f4a","3gp","wmv","mov","vob","ogg","gifv")
	for i in os.listdir():
		if(i[i.find(".")+1:] in formats):
			videofile=i
			return videofile
			break
	return 1


if(__name__=="__main__"):	
	filename="youtube_html.py"
	try:
		youtubeurl=sys.argv[1]
	except:
		print("[ERROR] no Youtube link given")
		exit()
					
	scriptdir=os.getcwd()+"/"

	if("yt" in youtubeurl or "youtube" in youtubeurl):
		v=YTB(youtubeurl[youtubeurl.index("?")+3:(youtubeurl+"&").find("&")])
	else:
		v=YTB(youtubeurl)
	youtubeurl="https://www.youtube.com/watch?v="+v.id
	
	if not os.path.isdir(v.out):
		os.system("mkdir "+v.out)
	if not os.path.isfile(v.out+"stylecompact.css"):
		os.system("cp "+scriptdir+"logo_notext.png "+scriptdir+"logo_.png "+scriptdir+"stylecompact.css "+v.out+" >> /dev/null")
		
	for i in sys.argv:
		if("--no-cleanup" in i):
			cleanup=0
		elif("--no-pdf" in i):
			v.pdf=0
		elif("--lang=" in i):
			v.lang=i[i.index("=")+1:]
		elif("--proxy=" in i):
			v.proxy=i[i.index("=")+1:]
		elif("--keylevel=" in i):
			v.keylevel=int(i[i.index("=")+1:])
		elif("--speed=" in i):
			v.speed=i[i.index("=")+1:]
		elif("--format=" in i):
			v.res=i[i.index("=")+1:]
		elif(i==sys.argv[1]):
			None
		elif(i==filename):
			None
		else:
			print("[unrecognized argument] "+str(i))
	
	if v.proxy != "":
		print("[INFO] Using Proxy: "+v.proxy)
	else:
		print("[INFO] Not using Proxy")

	os.chdir(v.out)
	if not(v.id in os.listdir()):
		os.system('mkdir '+v.id)
	os.chdir(v.id)#------------------------------------chdir youtubeid
	
	v.subfile= v.id+".vtt"
		
	for f in os.listdir():
		if "json" in f:
			meta=json.loads(open(v.id+".info.json").read())
			break
	if(v.meta==0):
		v.get_meta()	
	if v.lang=="":
		v.get_lang()	
	v.videofile=v.id+"."+v.meta["ext"]
	if not(v.videofile in os.listdir()):
		v.videofile=find_videofile()	
		
	retrys=0
	while not(v.videofile in os.listdir()) and retrys < v.retries:
		if(retrys >=1): time.sleep(v.cooldown)
		retrys +=1
		print("[INFO] Downloading YT video try: "+str(retrys))
		if retrys==v.retries:
			ress=480
			print("[INFO] Last try reset resolution to 480p")
		v.download_video()
		os.system('mv '+v.id+'*.vtt '+v.subfile)
		if not(v.videofile in os.listdir()):
			v.videofile=find_videofile()
			
	if not(v.subfile in os.listdir()):
		os.system("rm *.vtt")
		os.system('youtube-dl --proxy "'+v.proxy+'" --write-sub --lang '+v.lang+' --write-auto-sub --skip-download --id '+v.id)
		os.system('mv '+v.id+'*.vtt '+v.subfile)
	v.subs=1
	if not(v.subfile in os.listdir()):
		v.subs=0
		print("[WARNING] No subtitles")
			   
	if(v.videofile in os.listdir()):
		v.maxseconds=int(v.meta["duration"])
		v.maxframes=int(os.popen('mediainfo --Output="Video;%FrameCount%" '+v.videofile).read().replace("\n",""))
	else:
		print("[FATAL] Download Failed, exiting")
		exit()
		
	v.title=v.meta["title"]
	v.description=v.meta["description"]	
	
	print("Video Title       : "+v.title)
	print("Video ID          : "+v.id)
	print("Frames in Video   : "+str(v.maxframes))
	print("Video Duration    : "+str(v.maxseconds))
	print("Directory         : "+v.out+v.id+"/")
	print("Language (Subs)   : "+v.lang)
	#print("Video Description:\n"+description)

	if not("frames" in os.listdir()):
		os.system("python2 "+scriptdir+"download_and_convert.py "+v.videofile+" "+str(v.keylevel))		
	if not("frames" in os.listdir()):
		os.system("python2 "+scriptdir+"download_and_convert.py "+v.videofile+" "+str(v.keylevel))
		
		

	v.generate_time_data()
	
	##HTML GENERATOR
	categories=""
	keywords=""
	try:
		for i in v.meta["categories"]:
			categories=categories+i+" "
	except:
		None
	try:
		for i in v.meta["tags"]:
			keywords=keywords+i+", "	
	except:
		None
		
	h_dict={
	"__DESCRIPTION__": v.description.replace("\n","<br>\n\t\t\t\t\t\t"), #<br>\n
	"__UPLOADER__": v.meta["uploader"],
	"__YOUTUBEURL__": youtubeurl,
	"__DATE__": str("y:"+v.meta["upload_date"][:4]+" m:"+v.meta["upload_date"][4:6]+" d:"+v.meta["upload_date"][6:8]),
	"__KEYWORDS__": keywords,
	"__CATEGORIES__": categories,
	"__LANG__": v.lang,
	"__TITLE__": v.title,
	"__YOUTUBEID__": v.id
	}
	
	if(v.pdf==1):
		h_dict["<details>"]="<details open>"   
	 
	with open(scriptdir+"h.html","r") as f:
		html=replace_all(f.read(),h_dict)

	'''
	#0 time in s     
	#1 data (image or text)     
	#2 type ("image" or "text")
	#3 timestampstring
	'''
	im1=[]
	tx1=""
	for i in v.time_data:
		if(i[2]=="image"):
			if(im1==[]):
				im1=i
			else:
				i_dict={
				"__ID1__":str(im1[1]),
				"__TIME1__":str(int(im1[0])),
				"__TIMESTAMP1__":str(im1[3]),
				"__ID2__":str(i[1]),
				"__TIME2__":str(int(i[0])),
				"__TIMESTAMP2__":str(i[3]),
				"__YOUTUBEID__":v.id
					}
				with open(scriptdir+"i.html") as f:			
					html=html+replace_all(f.read(),i_dict)
				im1=[]
				tx1=""#buffer previous text to join blocs together in one <p></p>
		if(i[2]=="text"):
			if(tx1==""):
				html=html+'\t\t\t\t<p>'+i[1]+'</p>\n'
				tx1=i[1]
			else:
				html=html[:-5]+' '+i[1]+'</p>\n'
				tx1=i[1]

	with open(scriptdir+"f.html","r") as f:
		html=html+f.read()
	with open("index.html","w") as f:
		f.write(html)
	if v.pdf==1:
		os.system("wkhtmltopdf --encoding utf-8 --custom-header 'meta' 'charset=utf-8' index.html "+v.out+v.id+".pdf")
		if cleanup==1:
			os.chdir(v.out)
			os.system("rm -r "+v.id)
			cleanup=0
			os.system("rm logo_.png stylecompact.css")
	if cleanup==1:
		print("[cleanup enabled]")
		os.system('rm -R keyframes')
		os.system('rm "'+v.videofile+'"')
		os.system('rm "'+v.id+'.vtt"')
		os.system('rm "'+v.id+'.webp"')
		os.system('rm "'+v.id+'.jpg"')
		os.system('rm "'+v.id+'.info.json"')
