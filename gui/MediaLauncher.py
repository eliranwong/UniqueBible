import glob
import os
import config
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import QPushButton, QListView, QAbstractItemView, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget
else:
    from qtpy.QtGui import QStandardItemModel, QStandardItem
    from qtpy.QtWidgets import QPushButton, QListView, QAbstractItemView, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget

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
        button = QPushButton(config.thisTranslation["openAll"])
        button.clicked.connect(lambda: self.playAllMedia("music"))
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
        button = QPushButton(config.thisTranslation["openAll"])
        button.clicked.connect(lambda: self.playAllMedia("video"))
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
            item.setToolTip(file)
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
            item.setToolTip(file)
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
        command = "VLC:::{0}".format(os.path.join(directory, self.mediaFile))
        self.parent.runTextCommand(command)

    def playAllMedia(self, directory):
        playlist = self.musicList if directory == "music" else self.videoList
        playlist = [os.path.join(directory, filename) for filename in playlist]
        self.parent.parent.playAudioBibleFilePlayList(playlist)


## Standalone development code

class DummyParent():
    def runTextCommand(self, command):
        print(command)

    def verseReference(self, command):
        return ['', '']


if __name__ == "__main__":
    from PySide6 import QtWidgets
    from PySide6.QtWidgets import QWidget
    import sys

    from util.LanguageUtil import LanguageUtil
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    app = QtWidgets.QApplication(sys.argv)
    window = MediaLauncher(DummyParent())
    window.show()
    sys.exit(app.exec_())

