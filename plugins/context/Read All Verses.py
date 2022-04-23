# This plugin is written for non-Windows device.  This is not tested on Windows platform.

import config, re, os
from util.WebtopUtil import WebtopUtil

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

            if playlist and WebtopUtil.isPackageInstalled("vlc"):
                audioFiles = ' '.join(playlist)
                os.system("pkill vlc")
                WebtopUtil.runNohup(f"vlc {audioFiles}")
            elif playlist and config.isVlcInstalled:
                from gui.VlcPlayer import VlcPlayer
                self = config.mainWindow
                if self.vlcPlayer is not None:
                    self.vlcPlayer.close()
                self.vlcPlayer = VlcPlayer(self)
                for file in playlist:
                    self.vlcPlayer.addToPlaylist(file)
                self.vlcPlayer.show()
                self.vlcPlayer.playNextInPlaylist()

        else:
            config.mainWindow.displayMessage("No single verse audio found!")
    else:
        config.mainWindow.displayMessage("No single verse audio found!")

config.contextSource.page().toHtml(findText)

