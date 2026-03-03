import os, zipfile, gdown, platform
from uniquebible import config
# import threading
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QGridLayout, QPushButton, QDialog, QLabel
    from PySide6.QtCore import QObject, Signal
else:
    from qtpy.QtWidgets import QGridLayout, QPushButton, QDialog, QLabel
    from qtpy.QtCore import QObject, Signal
from uniquebible.install.module import *


class DownloadProcess(QObject):

    finished = Signal()

    def __init__(self, cloudFile, localFile):
        super().__init__()
        self.cloudFile, self.localFile = cloudFile, localFile

    def downloadFile(self):
        try:
            connection = False
            try:
                if not config.gdownIsUpdated:
                    installmodule("--upgrade gdown")
                    config.gdownIsUpdated = True
                try:
                    gdown.download(self.cloudFile, self.localFile, quiet=True)
                    print("Downloaded " + self.localFile)
                    connection = True
                except Exception as ex:
                    cli = "gdown {0} -O {1}".format(self.cloudFile, self.localFile)
                    os.system(cli)
                    print("Downloaded " + self.localFile)
                    connection = True
            except Exception as ex:
                print("Failed to download '{0}'!".format(self.cloudFile))
                print(ex)
            if connection and os.path.isfile(self.localFile) and self.localFile.endswith(".zip"):
                try:
                    zipObject = zipfile.ZipFile(self.localFile, "r")
                    path, *_ = os.path.split(self.localFile)
                    zipObject.extractall(path)
                    zipObject.close()
                    os.remove(self.localFile)
                except Exception as ex:
                    print("Failed to extract '{0}'!".format(self.localFile))
                    print(ex)
        except Exception as ex:
            print(ex)
        self.finished.emit()


class GitHubRepoFetchProcess(QObject):

    finished = Signal(bool, object, str)

    def __init__(self, repo):
        super().__init__()
        self.repo = repo

    def run(self):
        try:
            from uniquebible.util.GithubUtil import GithubUtil
            github = GithubUtil(self.repo)
            repoData = github.getRepoData()
            self.finished.emit(True, repoData, "")
        except Exception as ex:
            print("Failed to fetch repo data: {0}".format(ex))
            self.finished.emit(False, {}, str(ex))


class GitHubDownloadProcess(QObject):

    finished = Signal(bool, str)

    def __init__(self, repo, repoData, items, folder):
        super().__init__()
        self.repo = repo
        self.repoData = repoData
        self.items = items
        self.folder = folder

    def run(self):
        try:
            from uniquebible.util.GithubUtil import GithubUtil
            github = GithubUtil(self.repo)
            for item in self.items:
                file = os.path.join(self.folder, item + ".zip")
                print("Downloading {0}".format(file))
                github.downloadFile(file, self.repoData[item])
                with zipfile.ZipFile(file, 'r') as zipped:
                    zipped.extractall(self.folder)
                os.remove(file)
            print("Downloading complete")
            self.finished.emit(True, "")
        except Exception as ex:
            print("Failed to download from GitHub: {0}".format(ex))
            self.finished.emit(False, str(ex))


class LibraryCatalogDownloadProcess(QObject):

    finished = Signal(bool, str)

    def __init__(self, repo, filename, sha, installDirectory):
        super().__init__()
        self.repo = repo
        self.filename = filename
        self.sha = sha
        self.installDirectory = installDirectory

    def run(self):
        try:
            from uniquebible.util.GithubUtil import GithubUtil
            github = GithubUtil(self.repo)
            file = os.path.join(self.installDirectory, self.filename + ".zip")
            github.downloadFile(file, self.sha)
            with zipfile.ZipFile(file, 'r') as zipped:
                zipped.extractall(self.installDirectory)
            os.remove(file)
            self.finished.emit(True, self.filename)
        except Exception as ex:
            print("Failed to download '{0}': {1}".format(self.filename, ex))
            self.finished.emit(False, str(ex))


class Downloader(QDialog):

    def __init__(self, parent, databaseInfo):
        super().__init__()
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["message_downloadHelper"])
        self.setModal(True)

        self.databaseInfo = databaseInfo
        fileItems, *_ = databaseInfo
        self.filename = fileItems[-1]

        self.setupLayout()

    def setupLayout(self):

        self.messageLabel = QLabel("{1} '{0}'".format(self.filename, config.thisTranslation["message_missing"]))

        self.downloadButton = QPushButton(config.thisTranslation["message_install"])
        self.downloadButton.clicked.connect(self.startDownloadFile)

        self.cancelButton = QPushButton(config.thisTranslation["message_cancel"])
        self.cancelButton.clicked.connect(self.close)

        self.remarks = QLabel("{0} {1}".format(config.thisTranslation["message_remarks"], config.thisTranslation["message_downloadAllFiles"]))

        self.layout = QGridLayout()
        self.layout.addWidget(self.messageLabel, 0, 0)
        self.layout.addWidget(self.downloadButton, 1, 0)
        if config.downloadGCloudModulesInSeparateThread:
            self.layout.addWidget(self.cancelButton, 2, 0)
        self.layout.addWidget(self.remarks, 3, 0)
        self.setLayout(self.layout)

    def startDownloadFile(self):
        self.hide()
        self.setWindowTitle(config.thisTranslation["message_installing"])
        self.messageLabel.setText(config.thisTranslation["message_installing"])
        self.downloadButton.setText(config.thisTranslation["message_installing"])
        self.downloadButton.setEnabled(False)
        self.cancelButton.setText(config.thisTranslation["runInBackground"])
        self.show()
        self.downloadFile(True)

    # Put in a separate funtion to allow downloading file without gui
    def downloadFile(self, notification=True):
        self.parent.downloadFile(self.databaseInfo, notification)
