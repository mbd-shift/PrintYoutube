![LOGO](logo_.png)


# PrintYoutube


this is intended for saving time, as you can have an overview on a video relatively quickly.

I use this for lectures, guides, and tutorials.

It may also be used to allow citation of youtube videos in academic papers
as each page and picture can uniquely be identified with Timestamps.


report any bug please. 


### dependencies:
```bash
sudo apt install youtube-dl
sudo apt install mediainfo
sudo apt install ffmpeg
sudo apt install wkhtmltopdf
sudo apt install python3-pip python3 setuptools
sudo apt install python-pip
sudo apt install python-opencv
sudo python3 -m pip install webvtt-py
sudo python2 -m pip install scipy numpy
```

### usage:
`python3 youtube_html.py LINK/ID [--lang=XY] [--no-pdf] [--no-cleanup] [--speed=10M] [--keylevel=3] [--format=480]`

yotube-html downloads the Video, uses ffmpeg to extract i-frames, then another python script to select "worthy" frames from those. 


for __example__:

`python3 youtube_html.py "https://www.youtube.com/watch?v=Lu56xVlZ40M" --lang=en --keylevel=1`

**--no-pdf** outputs html and a folder of frames. If the file contains unicode, this can be neccessary

**--no-cleanup** outputs all files (vtt subs, meta json, video file, I-frames folder)

**--speed** download speed limit default is 10M

**--keylevel** default is 3... HIGHER means Less pictures (therefore bigger blocks of text)

**--lang** can be used with a 2-letter-lowercase string to set language (e.g. en, de, cz,...) not specifying --lang downloads vtt files in the Video language.

**--format** can specify video resolution, e.g. 720, 1080, 480, 360. Default is 480. For printing recommended is 360, for digital 720 (so you can zoom in the PDF)

if you plan to experiment with a video, be sure to enable --no-cleanup, as you will save time because it is not downloaded again and again

### html

feel free to edit stylecompact.css and the files h,f,i __[.html]__. 
h is the header part, f the footer, and i the intermediate which contains a set of 2 images and text

`__KEY__` will be replaced with the appropriate value by the main script 


_sorry for using adf.ly .. maybe it's not good practice. If you think so, just edit the html files and remove it. It's easy_
