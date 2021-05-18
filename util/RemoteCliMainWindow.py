import os, config, zipfile, gdown
from util.LanguageUtil import LanguageUtil
from ThirdParty import Converter

class RemoteCliMainWindow:

    def __init__(self):
        from util.DatafileLocation import DatafileLocation
        import config

        self.bibleInfo = DatafileLocation.marvelBibles
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
            gdown.download(cloudFile, localFile, quiet=True)
            connection = True
        except:
            connection = False
        if connection:
            if localFile.endswith(".zip"):
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

    # add a history record
    def addHistoryRecord(self, view, textCommand):
        if view == "http":
            view = "main"
        if not textCommand.startswith("_") and not textCommand.startswith("download:::"):
            viewhistory = config.history[view]
            if not (viewhistory[-1] == textCommand):
                viewhistory.append(textCommand)
                # set maximum number of history records for each view here
                maximumHistoryRecord = config.maximumHistoryRecord
                if len(viewhistory) > maximumHistoryRecord:
                    viewhistory = viewhistory[-maximumHistoryRecord:]
                config.history[view] = viewhistory
                config.currentRecord[view] = len(viewhistory) - 1

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
