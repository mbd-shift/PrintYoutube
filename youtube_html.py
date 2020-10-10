#!PYTHON
import os
import time
import re
import webvtt
import sys
import time
import json
import requests

filename="youtube_html.py"


def replace_all(text, dic):#returns str
    for i, j in dic.items():
        text = text.replace(i, j)
    return text
    
def get_meta(youtube_id):#returns meta dict
	os.system('youtube-dl --write-info-json --write-sub --write-auto-sub --write-annotations --skip-download --id '+youtube_id)
	os.system('rm *.??.vtt')
	meta=json.loads(open(youtubeid+".info.json").read())
	return meta
	
def get_lang(meta):#returns str (en)
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
	return lang
 
def find_videofile():#returns str (name of video file)
	formats=("mp4","webm","mkv","flv","vob","avi","m4v","f4v","f4a","3gp","wmv","mov","vob","ogg","gifv")
	for i in os.listdir():
		if(i[i.find(".")+1:] in formats):
			videofile=i
			return videofile
			break
	return 1
	
def download_video(youtube_id,resolution=480,speed="7M",lang="en"):
	fmt='best[height<='+str(resolution)+']'
	os.system('youtube-dl -i --socket-timeout 34 --sub-lang '+lang+' --format "'+fmt+'" --write-sub --write-auto-sub --no-playlist --write-info-json --write-thumbnail --id -r '+speed+' '+youtube_id)
	
def generate_time_data(subfile,videofile,meta,subs,framesdir="frames"):#0 time in s     1 data (image or text)     2 type ("image" or "text")     3 time as timestamped
	maxseconds=int(meta["duration"])
	maxframes=int(os.popen('mediainfo --Output="Video;%FrameCount%" '+videofile).read().replace("\n",""))	
	time_data=[]
	if(subs==1):
		if(subfile[-3:]=="srt"):
			subvtt=webvtt.from_srt(subfile)
		if(subfile[-3:]=="vtt"):
			subvtt=webvtt.read(subfile)
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
		framepos=framenr/maxframes
		framesec=framepos*maxseconds
		hour_=int(framesec/3600)
		minute_=int((framesec/60)-hour_*60)
		second_=int((framesec-(hour_*3600))-(minute_*60))
		tstmp=str(hour_).zfill(2)+":"+str(minute_).zfill(2)+":"+str(second_).zfill(2)
		time_data.append([framesec,framenr,"image", tstmp])
	time_data.sort(key=lambda tup:tup[0])
	return time_data



if(__name__=="__main__"):	
	cleanup=1
	pdf=1
	lang=""
	keylevel=3
	speed="7M"
	ress=480
	#default
	for i in sys.argv:
		if("--no-cleanup" in i):
			cleanup=0
		elif("--no-pdf" in i):
			pdf=0
		elif("--lang=" in i):
			lang=i[i.index("=")+1:]
		elif("--keylevel=" in i):
			keylevel=int(i[i.index("=")+1:])
		elif("--speed=" in i):
			speed=i[i.index("=")+1:]
		elif("--format=" in i):
			ress=i[i.index("=")+1:]
		elif(i==sys.argv[1]):
			None
		elif(i==filename):
			None
		else:
			print("[unrecognized argument] "+str(i))
			
			
	scriptdir=os.getcwd()+"/"
	outdir=scriptdir+"out/"


	if not os.path.isdir(outdir):
		os.system("mkdir "+outdir)
	if not os.path.isfile(outdir+"stylecompact.css"):
		os.system("cp "+scriptdir+"logo_notext.png "+scriptdir+"logo_.png  "+scriptdir+"stylecompact.css "+outdir)
	try:
		youtubeurl=sys.argv[1]
	except:
		print("[ERROR] no Youtube link given")
		exit()
	if("yt" in youtubeurl or "youtube" in youtubeurl):
		youtubeid=youtubeurl[youtubeurl.index("?")+3:(youtubeurl+"&").find("&")]
	else:
		youtubeid=youtubeurl
	youtubeurl="https://www.youtube.com/watch?v="+youtubeid



	os.chdir(outdir)
	if not(youtubeid in os.listdir()):
		os.system('mkdir '+youtubeid)
	os.chdir(youtubeid)#------------------------------------chdir youtubeid
		
	meta=0
	for f in os.listdir():
		if "json" in f:
			meta=json.loads(open(youtubeid+".info.json").read())
			break
	if(meta==0):
		meta=get_meta(youtubeid)
		
	title=meta["title"]
	description=meta["description"]	

	if lang=="":
		lang=get_lang(meta)
		
	print("[Language] for Subtitles: "+lang)
		
	videofile=youtubeid+"."+meta["ext"]


	if not(videofile in os.listdir()):
		videofile=find_videofile()

		
	retrys=0
	max_retrys=4
	while not(videofile in os.listdir()) and retrys < max_retrys:
		retrys +=1
		print("[INFO] Downloading YT video try: "+str(retrys))
		if retrys==max_retrys:
			ress=480
			print("[INFO] Last try reset resolution to 480p")
		download_video(youtubeid,ress,speed,lang)
		if not(videofile in os.listdir()):
			videofile=find_videofile()

	subfile= youtubeid+".vtt"
	os.system('mv '+youtubeid+'*.??.vtt '+subfile)	
	if not(subfile in os.listdir()):
		os.system("rm *.vtt")
		os.system('youtube-dl --write-sub --write-auto-sub --skip-download --id '+youtubeurl)
		os.system('mv '+youtubeid+'*.vtt '+subfile)
	subs=1
	if not(subfile in os.listdir()):
		subs=0
		print("[WARNING] No subtitles")
			   
	if(videofile in os.listdir()):
		maxseconds=int(meta["duration"])
		maxframes=int(os.popen('mediainfo --Output="Video;%FrameCount%" '+videofile).read().replace("\n",""))
	else:
		print("[FATAL] Download Failed, exiting")
		exit()

	print("Video Title    : "+title)
	print("Video ID       : "+youtubeid)
	print("Frames in Video: "+str(maxframes))
	print("Video Duration : "+str(maxseconds))
	print("Directory      : "+outdir+youtubeid+"/")
	print("Language (Subs): "+lang)
	#print("Video Description:\n"+description)


	if not("frames" in os.listdir()):
		os.system("python2 "+scriptdir+"download_and_convert.py "+videofile+" "+str(keylevel))
		
	if not("frames" in os.listdir()):
		os.system("python2 "+scriptdir+"download_and_convert.py "+videofile+" "+str(keylevel))
		
		
	time_data=generate_time_data(subfile,videofile,meta,subs)



	##HTML GENERATOR

	categories=""
	keywords=""
	try:
		for i in meta["categories"]:
			categories=categories+i+" "
	except:
		None
	try:
		for i in meta["tags"]:
			keywords=keywords+i+", "	
	except:
		None


	h_dict={
	"__DESCRIPTION__": description.replace("\n","<br>\n\t\t\t\t\t\t"), #<br>\n
	"__UPLOADER__": meta["uploader"],
	"__YOUTUBEURL__": youtubeurl,
	"__DATE__": str("y:"+meta["upload_date"][:4]+" m:"+meta["upload_date"][4:6]+" d:"+meta["upload_date"][6:8]),
	"__KEYWORDS__": keywords,
	"__CATEGORIES__": categories,
	"__LANG__": lang,
	"__TITLE__": title,
	"__YOUTUBEID__": youtubeid
	}

	if(pdf==1):
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
	for i in time_data:
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
				"__YOUTUBEID__":youtubeid
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
	if pdf==1:
		os.system("wkhtmltopdf --encoding utf-8 --custom-header 'meta' 'charset=utf-8' index.html "+outdir+youtubeid+".pdf")
		if cleanup==1:
			os.chdir(outdir)
			os.system("rm -r "+youtubeid)
			cleanup=0
			os.system("rm logo_.png stylecompact.css")

	if cleanup==1:
		print("[cleanup enabled]")
		os.system('rm -R keyframes')
		os.system('rm "'+videofile+'"')
		os.system('rm "'+youtubeid+'.vtt"')
		os.system('rm "'+youtubeid+'.webp"')
		os.system('rm "'+youtubeid+'.jpg"')
		os.system('rm "'+youtubeid+'.info.json"')
