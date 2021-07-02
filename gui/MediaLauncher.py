import glob
import os

import config
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import (QPushButton, QListView, QAbstractItemView, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget)

class MediaLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        # set title
        self.setWindowTitle(config.thisTranslation["mediaPlayer"])
        # set up variables
        self.parent = parent
        self.musicList = [os.path.basename(file) for file in glob.glob(r"music/*.mp3")]
        self.videoList = [os.path.basename(file) for file in glob.glob(r"video/*.mp4")]
        # setup interface
        self.setupUI()

    def setupUI(self):
        mainLayout = QHBoxLayout()

        leftColumnWidget = QGroupBox(config.thisTranslation["menu11_music"])
        musicLayout = QVBoxLayout()
        musicLayout.addWidget(self.musicListView())
        buttons = QHBoxLayout()
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(lambda: self.playMedia("music"))
        buttons.addWidget(button)
        musicLayout.addLayout(buttons)
        leftColumnWidget.setLayout(musicLayout)

        rightColumnWidget = QGroupBox(config.thisTranslation["menu11_video"])
        videoLayout = QVBoxLayout()
        videoLayout.addWidget(self.videoListView())
        buttons = QHBoxLayout()
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(lambda: self.playMedia("video"))
        buttons.addWidget(button)
        videoLayout.addLayout(buttons)
        rightColumnWidget.setLayout(videoLayout)

        mainLayout.addWidget(leftColumnWidget)
        mainLayout.addWidget(rightColumnWidget)
        self.setLayout(mainLayout)

    def musicListView(self):
        list = QListView()
        list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        model = QStandardItemModel(list)
        for file in self.musicList:
            item = QStandardItem(file)
            model.appendRow(item)
        list.setModel(model)
        list.selectionModel().selectionChanged.connect(self.playSelectedMusic)
        return list

    def videoListView(self):
        list = QListView()
        list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        model = QStandardItemModel(list)
        for file in self.videoList:
            item = QStandardItem(file)
            model.appendRow(item)
        list.setModel(model)
        list.selectionModel().selectionChanged.connect(self.playSelectedVideo)
        return list

    def playSelectedMusic(self, selection):
        index = selection[0].indexes()[0].row()
        self.mediaFile = self.musicList[index]
        command = "VLC:::music/{0}".format(self.mediaFile)
        self.parent.runTextCommand(command)

    def playSelectedVideo(self, selection):
        index = selection[0].indexes()[0].row()
        self.mediaFile = self.videoList[index]
        command = "VLC:::video/{0}".format(self.mediaFile)
        self.parent.runTextCommand(command)

    def playMedia(self, directory):
        command = "VLC:::{0}/{1}".format(directory, self.mediaFile)
        self.parent.runTextCommand(command)



## Standalone development code

class DummyParent():
    def runTextCommand(self, command):
        print(command)

    def verseReference(self, command):
        return ['', '']


if __name__ == "__main__":
    from qtpy import QtWidgets
    from qtpy.QtWidgets import QWidget
    import sys

    from util.LanguageUtil import LanguageUtil
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    app = QtWidgets.QApplication(sys.argv)
    window = MediaLauncher(DummyParent())
    window.show()
    sys.exit(app.exec_())

