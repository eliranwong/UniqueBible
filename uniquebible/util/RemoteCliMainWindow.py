import os, zipfile, gdown, shutil, re, platform, subprocess, sys, signal, threading
from uniquebible import config

from uniquebible.util.LanguageUtil import LanguageUtil
from uniquebible.util.TextCommandParser import TextCommandParser
from uniquebible.util.ThirdParty import Converter
from uniquebible.util.CrossPlatform import CrossPlatform
from uniquebible.util.DatafileLocation import DatafileLocation
from uniquebible.util.TextUtil import TextUtil
from uniquebible.util.WebtopUtil import WebtopUtil
from uniquebible.util.FileUtil import FileUtil
from uniquebible.db.BiblesSqlite import Bible, MorphologySqlite
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.PydubUtil import PydubUtil
from uniquebible.util.VlcUtil import VlcUtil
from pydub.playback import play
from uniquebible.install.module import *


class RemoteCliMainWindow(CrossPlatform):

    def __init__(self):
        self.bibleInfo = DatafileLocation.marvelBibles
        if not config.enableHttpServer:
            self.setupResourceLists()
            try:
                config.thisTranslation = LanguageUtil.loadTranslation(config.displayLanguage)
            except:
                pass

    def importModulesInFolder(self, directory="import"):
        if os.path.isdir(directory):
            if Converter().importAllFilesInAFolder(directory):
                self.completeImport()
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def completeImport(self):
        self.reloadControlPanel(False)
        self.displayMessage(config.thisTranslation["message_done"])

    def downloadFile(self, databaseInfo, notification=True):
        config.isDownloading = True
        # Retrieve file information
        fileItems, cloudID, *_ = databaseInfo
        cloudFile = "https://drive.google.com/uc?id={0}".format(cloudID)
        localFile = "{0}.zip".format(os.path.join(*fileItems))
        try:
            if not config.gdownIsUpdated:
                installmodule("--upgrade gdown")
                config.gdownIsUpdated = True
            try:
                gdown.download(cloudFile, localFile, quiet=True)
                print("Downloaded!")
                connection = True
            except:
                cli = "gdown {0} -O {1}".format(cloudFile, localFile)
                os.system(cli)
                print("Downloaded!")
                connection = True
        except:
            print("Failed to download '{0}'!".format(fileItems[-1]))
            connection = False
        if connection and os.path.isfile(localFile) and localFile.endswith(".zip"):
            zipObject = zipfile.ZipFile(localFile, "r")
            path, *_ = os.path.split(localFile)
            zipObject.extractall(path)
            zipObject.close()
            os.remove(localFile)
        self.moduleInstalled(fileItems, cloudID, notification)

    def moduleInstalled(self, fileItems, cloudID, notification=True):
        if hasattr(self, "downloader") and self.downloader.isVisible():
            self.downloader.close()
        # Check if file is y installed
        localFile = os.path.join(*fileItems)
        if os.path.isfile(localFile):
            # Reload Master Control
            self.reloadControlPanel(False)
            # Update install history
            config.installHistory[fileItems[-1]] = cloudID
            # Notify users
            if notification:
                self.displayMessage(config.thisTranslation["message_installed"])
        elif notification:
            self.displayMessage(config.thisTranslation["message_failedToInstall"])
        config.isDownloading = False

    def openPdfReader(self, file, page=1, fullPath=False, fullScreen=False):
        if file:
            try:
                libPdfDir = "lib/pdfjs-2.7.570-dist/web"
                marvelDataPath = os.path.join(os.getcwd(), "marvelData") if config.marvelData == "marvelData" else config.marvelData
                fileFrom = os.path.join(marvelDataPath, "pdf", file)
                fileFrom = fileFrom.replace("+", " ")
                fileTo = os.path.join(os.getcwd(), "htmlResources", libPdfDir, "temp.pdf")
                shutil.copyfile(fileFrom, fileTo)
                pdfViewer = "{0}/viewer.html".format(libPdfDir)
                url = "{0}?file=temp.pdf&theme={1}#page={2}".format(pdfViewer, config.theme, page)
                content = "<script>window.location.href = '{0}'</script>".format(url)
                return("main", content, {})
            except Exception as e:
                return ("main", "Could not load {0}".format(file), {})
        else:
            return("main", "No file specified", {})

    def openEpubReader(self, file, page=1, fullPath=False, fullScreen=False):
        if file:
            try:
                libEpubDir = "lib/bibi-v1.2.0"
                marvelDataPath = os.path.join(os.getcwd(), "marvelData") if config.marvelData == "marvelData" else config.marvelData
                fileFrom = os.path.join(marvelDataPath, "epub", file)
                fileFrom = fileFrom.replace("+", " ")
                fileTo = os.path.join(os.getcwd(), "htmlResources", libEpubDir, "bibi-bookshelf", file)
                shutil.copyfile(fileFrom, fileTo)
                viewer = "{0}/bibi/index.html".format(libEpubDir)
                url = "{0}?book={1}".format(viewer, file)
                content = "<script>window.location.href = '{0}'</script>".format(url)
                return("main", content, {})
            except Exception as e:
                return ("main", "Could not load {0}".format(file), {})
        else:
            return("main", "No file specified", {})

    def getPlaylistFromHTML(self, html, displayText=False):
        playlist = []
        textList = []
        #searchPattern = """[Rr][Ee][Aa][Dd][Cc][Hh][Aa][Pp][Tt][Ee][Rr]:::([A-Za-z0-9]+?)\.([0-9]+?)\.([0-9]+?)[\."']"""
        searchPattern = """_[Cc][Hh][Aa][Pp][Tt][Ee][Rr][Ss]:::([^\.>]+?)_([0-9]+?)\.([0-9]+?)["'].*onclick=["']rC\("""
        found = re.search(searchPattern, html)
        if found:
            text, b, c = found[1], found[2], found[3]
            text = FileUtil.getMP3TextFile(text)
            return RemoteCliMainWindow().playAudioBibleChapterVerseByVerse(text, b, c, displayText=displayText)
        else:
            searchPattern = """[Rr][Ee][Aa][Dd][Vv][Ee][Rr][Ss][Ee]:::([A-Za-z0-9]+?)\.([0-9]+?)\.([0-9]+?)\.([0-9]+?)["']"""
            found = re.findall(searchPattern, html)
            if found:
                for entry in found:
                    text, b, c, v = entry
                    if displayText:
                        try:
                            *_, verseText = Bible(text).readTextVerse(b, c, v)
                            verseText = TextUtil.htmlToPlainText(f"[<ref>{config.mainWindow.textCommandParser.bcvToVerseReference(b, c, v)}</ref> ]{verseText}").strip()
                            verseText = verseText.replace("audiotrack ", "")
                            textList.append(verseText)
                        except:
                            textList.append("")
                    audioFolder = os.path.join("audio", "bibles", text, "default", "{1}_{2}".format(text, b, c))
                    audioFile = "{0}_{1}_{2}_{3}.mp3".format(text, b, c, v)
                    audioFilePath = os.path.join(audioFolder, audioFile)
                    if os.path.isfile(audioFilePath):
                        playlist.append(audioFilePath)
                if config.runMode == "terminal":
                    # Create a new thread for the streaming task
                    config.playback_finished = False
                    playback_event = threading.Event()
                    if displayText:
                        self.playback_thread = threading.Thread(target=self.playAudioBibleFilePlayListPlusDisplayText, args=(playlist, textList, False, playback_event))
                    else:
                        self.playback_thread = threading.Thread(target=self.playAudioBibleFilePlayList, args=(playlist,))
                    # Start the streaming thread
                    self.playback_thread.start()

                    # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
                    config.mainWindow.textCommandParser.keyToStopStreaming(playback_event)

                    # when streaming is done or when user press "ctrl+q"
                    self.playback_thread.join()

                    # old way
                    #self.playAudioBibleFilePlayListPlusDisplayText(playlist, textList) if displayText else self.playAudioBibleFilePlayList(playlist)
                    return []
            else:
                searchPattern = """[Rr][Ee][Aa][Dd]([Ww][Oo][Rr][Dd]|[Ll][Ee][Xx][Ee][Mm][Ee]):::([A-Za-z0-9]+?)\.([0-9]+?)\.([0-9]+?)\.([0-9]+?)\.([0-9]+?)["']"""
                found = re.findall(searchPattern, html)
                if found:
                    for entry in found:
                        wordType, text, b, c, v, wordID = entry
                        audioFolder = os.path.join("audio", "bibles", text, "default", "{1}_{2}".format(text, b, c))
                        #prefix = "lex_" if wordType.lower() == "lexeme" else ""
                        if wordType.lower() == "lexeme":
                            prefix = "lex_"
                            if displayText:
                                try:
                                    textList.append(self.getOriginalWord(("lex", text, b, c, v, wordID)))
                                except:
                                    textList.append("")
                        else:
                            prefix = ""
                            if displayText:
                                try:
                                    textList.append(self.getOriginalWord((text, b, c, v, wordID)))
                                except:
                                    textList.append("")
                        audioFile = "{5}{0}_{1}_{2}_{3}_{4}.mp3".format(text, b, c, v, wordID, prefix)
                        audioFilePath = os.path.join(audioFolder, audioFile)
                        if os.path.isfile(audioFilePath):
                            playlist.append(audioFilePath)
                if config.runMode == "terminal":
                    self.playAudioBibleFilePlayListPlusDisplayText(playlist, textList) if displayText else self.playAudioBibleFilePlayList(playlist)
                    return []
        return playlist

    def getOriginalWord(self, elements):

        books = BibleBooks().booksMap.get(config.standardAbbreviation, BibleBooks.abbrev["eng"])
        morphology = MorphologySqlite()

        if len(elements) == 5:
            text, b, c, v, wordID = elements
            #wordID = wordID[:-4]
            if b in books:
                word = morphology.getWord(b, wordID)
                if not word:
                    word = wordID
                #title = "{1} {2}:{3} - {4} ({0})".format(text, books[b][0], c, v, word)
                title = "[<ref>READWORD:::{0}.{5}.{2}.{3}.{6}</ref> ] {4}".format(text, books[b][0], c, v, word, b, wordID)
        elif len(elements) == 6:
            *_, text, b, c, v, wordID = elements
            #wordID = wordID[:-4]
            if b in books:
                lexeme = morphology.getLexeme(int(b), int(wordID))
                if not lexeme:
                    lexeme = wordID
                #title = "{1} {2}:{3} - {4} [{5}] ({0})".format(text, books[b][0], c, v, lexeme, lex)
                title = "[<ref>READLEXEME:::{0}.{5}.{2}.{3}.{6}</ref> ] {4}".format(text, books[b][0], c, v, lexeme, b, wordID)
        title = TextUtil.htmlToPlainText(title).strip()
        return title

    def playAudioBibleChapterVerseByVerse(self, text, b, c, startVerse=0, displayText=False):
        playlist = []
        textList = []
        folder = os.path.join(config.audioFolder, "bibles", text, "default", "{0}_{1}".format(b, c))
        if os.path.isdir(folder):
            bible = Bible(text)
            verses = bible.getVerseList(b, c)
            for verse in verses:
                if verse >= startVerse:
                    # add audio file
                    audioFile = "{0}_{1}_{2}_{3}.mp3".format(text, b, c, verse)
                    audioFilePath = os.path.join(folder, audioFile)
                    if os.path.isfile(audioFilePath):
                        playlist.append((audioFile, audioFilePath))
                    # add text
                    if displayText:
                        try:
                            *_, verseText = bible.readTextVerse(b, c, verse)
                            verseText = TextUtil.htmlToPlainText(f"[<ref>{config.mainWindow.textCommandParser.bcvToVerseReference(b, c, verse)}</ref> ]{verseText}").strip()
                            verseText = verseText.replace("audiotrack ", "")
                            textList.append(verseText)
                        except:
                            textList.append("")
        if config.runMode == "terminal":
            playlist = [filepath for *_, filepath in playlist]

            # Create a new thread for the streaming task
            config.playback_finished = False
            playback_event = threading.Event()
            if displayText:
                self.playback_thread = threading.Thread(target=self.playAudioBibleFilePlayListPlusDisplayText, args=(playlist, textList, False, playback_event))
            else:
                self.playback_thread = threading.Thread(target=self.playAudioBibleFilePlayList, args=(playlist,))
            # Start the streaming thread
            self.playback_thread.start()

            # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
            config.mainWindow.textCommandParser.keyToStopStreaming(playback_event)

            # when streaming is done or when user press "ctrl+q"
            self.playback_thread.join()

            # old way
            #self.playAudioBibleFilePlayListPlusDisplayText(playlist, textList) if displayText else self.playAudioBibleFilePlayList(playlist)
            return []
        return playlist
        #return [("NET_1_1_3.mp3", "audio/bibles/NET-UK/default/1_1/NET_1_1_3.mp3"), ("NET_1_1_4.mp3", "audio/bibles/NET-UK/default/1_1/NET_1_1_4.mp3")]

    def notifyAudioPlayback(self):
        print("--------------------")
        print("Playing audio ...")
        print("To stop audio playback, press 'ctrl+q' or 'ctrl+z'.")
        print("--------------------")

    def playAudioBibleFilePlayList(self, playlist, gui=False, playback_event=None):
        # do not remove the dummy gui argument for this method
        self.closeMediaPlayer()
        if playlist:
            if config.isVlcAvailable:
                self.notifyAudioPlayback()
                VlcUtil.playMediaFile(playlist, config.vlcSpeed, gui)
            else:
                print("No VLC player is found!")
        config.playback_finished = True

    def playAudioBibleFilePlayListPlusDisplayText(self, playlist, textList, gui=False, playback_event=None):
        # do not remove the dummy gui argument for this method
        self.closeMediaPlayer()
        if playlist:
            self.notifyAudioPlayback()
            #if config.runMode == "terminal":
            #    config.mainWindow.createAudioPlayingFile()
            for index, audioFile in enumerate(playlist):
                #if not os.path.isfile(config.audio_playing_file):
                if playback_event is not None and playback_event.is_set():
                    break
                try:
                    # display text
                    if config.runMode == "terminal":
                        config.mainWindow.print(textList[index])
                    else:
                        print(textList[index])
                    # play audio with user customised speed
                    if config.useThirdPartyVLCplayer or (config.terminalForceVlc and config.isVlcAvailable):
                        VlcUtil.playMediaFile(audioFile, config.vlcSpeed)
                    else:
                        if not platform.system() == "Darwin":
                            # use subprocess to hide pydub output
                            isPydubPlaying = os.path.join("temp", "isPydubPlaying")
                            FileUtil.touchFile(isPydubPlaying)
                            subprocess.Popen(f"""{sys.executable} util/PydubUtil.py {config.mediaSpeed} {config.speedUpFilterFrequency} {audioFile}""", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                            while os.path.isfile(isPydubPlaying):
                                pass
                        else:
                            # on macOS, pydub does not print output on terminal while playing, so we play the audio directly
                            play(PydubUtil.audioChangeSpeed(audioFile, config.mediaSpeed, config.speedUpFilterFrequency))
                except:
                    pass
                self.closeMediaPlayer()
            if config.runMode == "terminal":
                config.mainWindow.removeAudioPlayingFile()
        config.playback_finished = True

    def closeMediaPlayer(self):
        if os.path.isfile(config.audio_playing_file):
            os.remove(config.audio_playing_file)
        if WebtopUtil.isPackageInstalled("pkill"):
            # close Android media player
            try:
                if WebtopUtil.isPackageInstalled("termux-media-player"):
                    config.mainWindow.getCliOutput("termux-media-player stop")
            except:
                pass

            # close macOS text-to-speak voice
            if shutil.which("say"):
                os.system("pkill say")
            VlcUtil.closeVlcPlayer()
            # close espeak on Linux
            if WebtopUtil.isPackageInstalled("espeak"):
                os.system("pkill espeak")

    def enforceCompareParallelButtonClicked(self):
        config.enforceCompareParallel = not config.enforceCompareParallel

    def reloadControlPanel(self, show=True):
        pass

    def openControlPanelTab(self, index=None, b=None, c=None, v=None, text=None):
        pass

    def displayMessage(self, message):
        print(message)

    def updateMainRefButton(self):
        pass

    def enableParagraphButtonAction(self, v):
        pass

    #def downloadHelper(self, v):
    #    pass

    # manage download helper
    def downloadHelper(self, databaseInfo):
        if config.runMode == "terminal":
            config.mainWindow.downloadHelper(databaseInfo)

    def updateStudyRefButton(self):
        pass

    def updateCommentaryRefButton(self):
        pass

    def updateBookButton(self):
        pass

    def closePopover(self):
        pass

    def runTextCommand(self, textCommand, addRecord=False, source="cli", forceExecute=False):
        view, content, dict = TextCommandParser(self).parser(textCommand, source)
        print(TextUtil.htmlToPlainText(content))
