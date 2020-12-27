import config
from PySide2.QtCore import QUrl, Qt
from PySide2.QtWidgets import (QAction)
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

class YouTubePopover(QWebEngineView):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["menu11_youtube"])
        self.load(QUrl("https://www.youtube.com/"))
        self.urlString = ""
        self.urlChanged.connect(self.videoLinkChanged)
        # add context menu (triggered by right-clicking)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.addMenuActions()

    def videoLinkChanged(self, url):
        self.urlString = url.toString()

    def addMenuActions(self):
        goBack = QAction(self)
        goBack.setText(config.thisTranslation["youtube_back"])
        goBack.triggered.connect(self.back)
        self.addAction(goBack)

        goForward = QAction(self)
        goForward.setText(config.thisTranslation["youtube_forward"])
        goForward.triggered.connect(self.forward)
        self.addAction(goForward)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        copyLink = QAction(self)
        copyLink.setText(config.thisTranslation["youtube_copy"])
        copyLink.triggered.connect(self.copy)
        self.addAction(copyLink)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        mp3 = QAction(self)
        mp3.setText(config.thisTranslation["youtube_mp3"])
        mp3.triggered.connect(self.downloadMp3)
        self.addAction(mp3)

        video = QAction(self)
        video.setText(config.thisTranslation["youtube_mp4"])
        video.triggered.connect(self.downloadVideo)
        self.addAction(video)

    def back(self):
        self.page().triggerAction(QWebEnginePage.Back)

    def forward(self):
        self.page().triggerAction(QWebEnginePage.Forward)

    def copy(self):
        if self.urlString:
            qApp.clipboard().setText(self.urlString)

    def downloadMp3(self):
        if not self.urlString or "/results?search_query=" in self.urlString:
            self.parent.displayMessage(config.thisTranslation["message_invalid"])
        else:
            self.parent.runTextCommand("mp3:::{0}".format(self.urlString))

    def downloadVideo(self):
        if not self.urlString or "/results?search_query=" in self.urlString:
            self.parent.displayMessage(config.thisTranslation["message_invalid"])
        else:
            self.parent.runTextCommand("mp4:::{0}".format(self.urlString))
