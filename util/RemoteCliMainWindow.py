import os, config, zipfile, gdown, shutil, platform

from util.LanguageUtil import LanguageUtil
from util.TextCommandParser import TextCommandParser
from util.ThirdParty import Converter
from util.CrossPlatform import CrossPlatform
from util.DatafileLocation import DatafileLocation
from util.TextUtil import TextUtil
from db.BiblesSqlite import Bible


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

    def playAudioBibleChapterVerseByVerse(self, text, b, c, startVerse=0):
        playlist = []
        folder = os.path.join(config.audioFolder, "bibles", text, "default", "{0}_{1}".format(b, c))
        if os.path.isdir(folder):
            verses = Bible(text).getVerseList(b, c)
            for verse in verses:
                if verse >= startVerse:
                    audioFile = "{0}_{1}_{2}_{3}.mp3".format(text, b, c, verse)
                    audioFilePath = os.path.join(folder, audioFile)
                    if os.path.isfile(audioFilePath):
                        playlist.append((audioFile, audioFilePath))
        return playlist
        #return [("NET_1_1_3.mp3", "audio/bibles/NET-UK/default/1_1/NET_1_1_3.mp3"), ("NET_1_1_4.mp3", "audio/bibles/NET-UK/default/1_1/NET_1_1_4.mp3")]

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
