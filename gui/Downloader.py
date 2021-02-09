import os, config, zipfile, gdown, threading
from PySide2.QtWidgets import (QGridLayout, QPushButton, QDialog, QLabel, QProgressBar)

class Downloader(QDialog):

    def __init__(self, parent, databaseInfo):
        super().__init__()
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["message_downloadHelper"])
        self.setModal(True)

        self.databaseInfo = databaseInfo
        fileItems, cloudID, *_ = databaseInfo
        self.cloudFile = "https://drive.google.com/uc?id={0}".format(cloudID)
        self.localFile = "{0}.zip".format(os.path.join(*fileItems))
        self.filename = fileItems[-1]

        self.setupLayout()

    def setupLayout(self):

        #self.setupProgressBar()

        self.messageLabel = QLabel("{1} '{0}'".format(self.filename, config.thisTranslation["message_missing"]))

        self.downloadButton = QPushButton(config.thisTranslation["message_install"])
        self.downloadButton.clicked.connect(self.startDownloadFile)

        self.cancelButton = QPushButton(config.thisTranslation["message_cancel"])
        self.cancelButton.clicked.connect(self.close)

        self.remarks = QLabel("{0} {1}".format(config.thisTranslation["message_remarks"], config.thisTranslation["message_downloadAllFiles"]))

        self.layout = QGridLayout()
        #self.layout.addWidget(self.progressBar, 0, 0)
        self.layout.addWidget(self.messageLabel, 0, 0)
        self.layout.addWidget(self.downloadButton, 1, 0)
        self.layout.addWidget(self.cancelButton, 2, 0)
        self.layout.addWidget(self.remarks, 3, 0)
        self.setLayout(self.layout)

    def setupProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

    def startDownloadFile(self):
        self.messageLabel.setText(config.thisTranslation["message_installing"])
        self.downloadButton.setText(config.thisTranslation["message_installing"])
        self.downloadButton.setEnabled(False)
        self.cancelButton.setEnabled(False)
        # self.downloadButton.setStyleSheet("background-color: rgb(255,255,102)")
        # self.downloadFile(True)
        # https://www.linuxjournal.com/content/multiprocessing-python
        if config.isDownloading:
            self.parent.displayMessage(config.thisTranslation["previousDownloadIncomplete"])
        else:
            threading.Thread(target=self.downloadFile, args=(True,)).start()
            #self.parent.displayMessage(config.thisTranslation["downloading"])

    def downloadFile(self, notification=True):
        self.hide()
        config.isDownloading = True
        try:
            gdown.download(self.cloudFile, self.localFile, quiet=True)
            connection = True
        except:
            try:
                gdown.download(self.cloudFile, self.localFile, quiet=True, proxy=None)
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
            # Update download history
            # Update install History
            fileItems, cloudID, *_ = self.databaseInfo
            config.installHistory[fileItems[-1]] = cloudID
            if notification:
                self.messageLabel.setText(config.thisTranslation["message_installed"])
                self.remarks.setText("")
                self.downloadButton.setText(config.thisTranslation["message_installed"])
        else:
            if notification:
                self.messageLabel.setText(config.thisTranslation["message_failedToInstall"])
                self.remarks.setText("")
                self.downloadButton.setText(config.thisTranslation["message_failedToInstall"])
        self.show()
        config.isDownloading = False