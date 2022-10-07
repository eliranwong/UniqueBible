import os, config, zipfile, gdown, shutil, re, signal

from util.LanguageUtil import LanguageUtil
from util.TextCommandParser import TextCommandParser
from util.ThirdParty import Converter
from util.CrossPlatform import CrossPlatform
from util.DatafileLocation import DatafileLocation
from util.TextUtil import TextUtil
from util.WebtopUtil import WebtopUtil
from util.FileUtil import FileUtil
from db.BiblesSqlite import Bible, MorphologySqlite
from util.BibleBooks import BibleBooks


class RemoteCliMainWindow(CrossPlatform):

    def __init__(self):
        self.bibleInfo = DatafileLocation.marvelBibles
        if not config.enableHttpServer:
            self.setupResourceLists()
            config.thisTranslation = LanguageUtil.loadTranslation(config.displayLanguage)

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
                    self.playAudioBibleFilePlayListPlusDisplayText(playlist, textList) if displayText else self.playAudioBibleFilePlayList(playlist)
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
            self.playAudioBibleFilePlayListPlusDisplayText(playlist, textList) if displayText else self.playAudioBibleFilePlayList(playlist)
            return []
        return playlist
        #return [("NET_1_1_3.mp3", "audio/bibles/NET-UK/default/1_1/NET_1_1_3.mp3"), ("NET_1_1_4.mp3", "audio/bibles/NET-UK/default/1_1/NET_1_1_4.mp3")]

    def playAudioBibleFilePlayList(self, playlist, gui=False):
        # do not remove the dummy gui argument for this method
        self.closeMediaPlayer()
        if playlist:
            # vlc on macOS
            if config.macVlc or config.windowsVlc:
                audioFiles = '" "'.join(playlist)
                audioFiles = '"{0}"'.format(audioFiles)
                WebtopUtil.run(f"{config.macVlc} --rate {config.vlcSpeed} {audioFiles}")
            # vlc on Windows
            if config.macVlc or config.windowsVlc:
                audioFiles = '" "'.join(playlist)
                audioFiles = '"{0}"'.format(audioFiles)
                WebtopUtil.run(f"'{config.windowsVlc}' --rate {config.vlcSpeed} {audioFiles}")
            # vlc on other platforms
            elif WebtopUtil.isPackageInstalled("vlc"):
                audioFiles = '" "'.join(playlist)
                audioFiles = '"{0}"'.format(audioFiles)
                #vlcCmd = "vlc" if gui else "cvlc"
                # always use cvlc
                vlcCmd = "cvlc"
                #os.system("pkill vlc")
                WebtopUtil.run(f"{vlcCmd} --rate {config.vlcSpeed} {audioFiles}")

    def playAudioBibleFilePlayListPlusDisplayText(self, playlist, textList, gui=False):
        # do not remove the dummy gui argument for this method
        self.closeMediaPlayer()
        if playlist:
            for index, audioFile in enumerate(playlist):
                try:
                    # display text
                    print(textList[index])
                    # vlc on macOS
                    if config.macVlc:
                        os.system(f"{config.macVlc} --intf rc --play-and-exit --rate {config.vlcSpeed} {audioFile} &> /dev/null")
                    # vlc on windows
                    elif config.windowsVlc:
                        os.system(f"'{config.windowsVlc}' --play-and-exit --rate {config.vlcSpeed} {audioFile}")
                    # vlc on other platforms
                    elif WebtopUtil.isPackageInstalled("vlc"):
                        vlcCmd = "cvlc"
                        os.system(f"{vlcCmd} --intf rc --play-and-exit --rate {config.vlcSpeed} {audioFile} &> /dev/null")
                except:
                    pass
                self.closeMediaPlayer()

    def closeMediaPlayer(self):
        if WebtopUtil.isPackageInstalled("pkill"):

            if config.cliTtsProcess is not None:
                try:
                    config.cliTtsProcess.kill()
                    config.cliTtsProcess.terminate()
                    os.killpg(os.getpgid(config.cliTtsProcess.pid), signal.SIGTERM)
                    config.cliTtsProcess = None
                except:
                    pass
                print(config.cliTtsProcess)

            # close Android media player
            #try:
                #if WebtopUtil.isPackageInstalled("termux-media-player"):
                    #config.mainWindow.getCliOutput("termux-media-player stop")
                    #os.system("pkill termux-media-player")
            #except:
                #pass

            # close vlc on macOS
            if config.macVlc:
                os.system("pkill VLC")
            # close vlc on other platforms
            if WebtopUtil.isPackageInstalled("vlc"):
                os.system("pkill vlc")
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

    def downloadHelper(self, v):
        pass

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
