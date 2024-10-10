# This plugin is written for non-Windows device.  This is not tested on Windows platform.

from uniquebible import config
import re, os, platform
from uniquebible.util.WebtopUtil import WebtopUtil

def findText(html):
    searchPattern = """[Rr][Ee][Aa][Dd][Vv][Ee][Rr][Ss][Ee]:::([A-Za-z0-9]+?)\.([0-9]+?)\.([0-9]+?)\.([0-9]+?)["']"""
    found = re.findall(searchPattern, html)
    if found:
        playlist = []
        for entry in found:
            text, b, c, v = entry
            moduleFolder = os.path.join(os.getcwd(), config.audioFolder, "bibles", text, "default")
            audioFile = os.path.join(moduleFolder, "{0}_{1}".format(b, c), "{0}_{1}_{2}_{3}.mp3".format(text, b, c, v))
            if os.path.isfile(audioFile):
                playlist.append(audioFile)
        if playlist:
            config.mainWindow.playAudioBibleFilePlayList(playlist)
        else:
            config.mainWindow.displayMessage("No single verse audio found!")
    else:
        config.mainWindow.displayMessage("No single verse audio found!")

config.contextSource.page().toHtml(findText)

