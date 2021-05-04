import os, config, zipfile, gdown
# import threading
from qtpy.QtWidgets import (QGridLayout, QPushButton, QDialog, QLabel, QApplication)
from qtpy.QtCore import QObject, Signal


class DownloadProcess(QObject):

    finished = Signal()

    def __init__(self, cloudFile, localFile):
        super().__init__()
        self.cloudFile, self.localFile = cloudFile, localFile

    def downloadFile(self):
        try:
            gdown.download(self.cloudFile, self.localFile, quiet=True)
            connection = True
        except:
            connection = False
        if connection:
            if self.localFile.endswith(".zip"):
                zipObject = zipfile.ZipFile(self.localFile, "r")
                path, *_ = os.path.split(self.localFile)
                zipObject.extractall(path)
                zipObject.close()
                os.remove(self.localFile)
        # Emit a signal to notify that download process is finished
        self.finished.emit()


class Downloader(QDialog):

    def __init__(self, parent, databaseInfo, autoStart=False):
        super().__init__()
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["message_downloadHelper"])
        self.setModal(True)

        self.databaseInfo = databaseInfo
        fileItems, *_ = databaseInfo
        self.filename = fileItems[-1]

        self.setupLayout(autoStart)

        if autoStart:
            self.hide()
            QApplication.processEvents()
            self.downloadButton.click()

    def setupLayout(self, autoStart):

        self.messageLabel = QLabel("{1} '{0}'".format(self.filename, config.thisTranslation["message_missing"]))

        self.downloadButton = QPushButton(config.thisTranslation["message_install"])
        self.downloadButton.clicked.connect(self.startDownloadFile)

        self.cancelButton = QPushButton(config.thisTranslation["message_cancel"])
        self.cancelButton.clicked.connect(self.close)

        self.remarks = QLabel("{0} {1}".format(config.thisTranslation["message_remarks"], config.thisTranslation["message_downloadAllFiles"]))

        self.layout = QGridLayout()
        self.layout.addWidget(self.messageLabel, 0, 0)
        self.layout.addWidget(self.downloadButton, 1, 0)
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
