# UniqueBible
A cross-platform & offline bible application, integrated with high-quality resources and unique features.

<b>Tested in:</b> Windows, macOS and Linux (Ubuntu & Mint)

(developed with Python [version: 3.7.2])

Our Wiki Pages: https://github.com/eliranwong/UniqueBible/wiki

Visit <a href="https://BibleTools.app" target="_blank">https://BibleTools.app</a> for further information.

# Screenshot:

<img src="screenshots/screenshot.png">

# Pre-requisite

Install a Pyhton Distribution First!

The "desktop" version of "UniqueBible.app" is programmed with python library.  Users have to install python library first in order to run "UniqueBible.app" on your desktop OS.

Go to <a href="https://www.python.org">https://www.python.org</a> for instructions on installation of python for FREE.

We also recommend <a href='https://www.anaconda.com/'>Anaconda python distribution</a>.  It may be easier to be installed.

# Install Dependencies

<b>[ESSENTIAL]</b>

> pip3 install PySide2
<br>(PySide2 is required for graphical user interface, used by UniqueBible.app.)

> pip3 install PyPDF2
<br>(PyPDF2 is required for reading text from *.pdf documents.)

> pip3 install python-docx
<br>(python-docx is required for reading text from *.docx documents.)

> pip3 install gdown
<br>(gdown is required for downloading database files from google drive.)

<b>[OPTIONAL]</b>

> pip3 install diff-match-patch<br>
or [on some Linux distro]:<br>
> sudo apt install python3-diff-match-patch
<br>(it is an essential component for advanced verse comparison developed <b>from version 5.7 onwards</b>.)

> pip3 install googletrans<br>
(Install it to enable google-translate of any texts displayed on UniqueBible.app.)<br>
(It is also essentail for translating program interface into user's language.)

> pip3 install OpenCC<br>
(Install it to enable conversion of Chinese texts in command field between traditional and simplified characters.)

> pip3 install pypinyin<br>
(Install it to enable translating Chinese characters into Mandarin pinyin.)

If you use use <a href='https://www.anaconda.com/'>Anaconda python distribution</a>, use the following commands instead to install dependencies [<a href="https://github.com/eliranwong/UniqueBible/blob/master/installation/mac.md">Click here for an example of installation using Anaconda</a>]:

conda install -c conda-forge pyside2<br>
conda install -c vladsaveliev gdown<br>
conda install -c conda-forge pypdf2<br>
conda install -c conda-forge python-docx<br>
conda install -c conda-forge diff-match-patch<br>
conda install -c conda-forge googletrans<br>

# Dependency to Run YouTube Downloader

Read <a href="https://github.com/eliranwong/UniqueBible/wiki/download_youtube_audio_video">https://github.com/eliranwong/UniqueBible/wiki/download_youtube_audio_video</a>

# Instructions on Installation

There are different ways to setup and run our app.  We have some examples in the following link:

https://github.com/eliranwong/UniqueBible/blob/master/installation/Readme.md

# Technical Support / Join our Development

You are welcome to join our channel:

https://join.slack.com/t/marvelbible/shared_invite/enQtNDYyMTAxNTMwNTY2LWU4YzUyMzUxYWQxNDNiNDhjMmYwMjdjZTQ0ZWQyODg3NTA1MWZmZmM1ZThmOWFlMGUzZWUxNTllNmMxNTgzYTU

# Donations:

Please consider a donation via our PayPal account:
<a href="https://www.paypal.me/MarvelBible">https://www.paypal.me/MarvelBible</a>

