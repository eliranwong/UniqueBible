import config
from qtpy.QtCore import QUrl, Qt
from qtpy.QtWidgets import QAction, QApplication
from qtpy.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

class YouTubePopover(QWebEngineView):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["menu11_youtube"])
        #self.load(QUrl("https://www.youtube.com/"))
        self.urlString = ""
        self.urlChanged.connect(self.videoLinkChanged)
        # add context menu (triggered by right-clicking)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.addMenuActions()

    def videoLinkChanged(self, url):
        self.urlString = url.toString()
        self.parent.addressBar.setText(self.urlString)

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
        mp3.setText(config.thisTranslation["youtubeMp3"])
        mp3.triggered.connect(lambda: self.downloadMpFile("mp3"))
        self.addAction(mp3)

        video = QAction(self)
        video.setText(config.thisTranslation["youtubeMp4"])
        video.triggered.connect(lambda: self.downloadMpFile("mp4"))
        self.addAction(video)

    def back(self):
        self.page().triggerAction(QWebEnginePage.Back)

    def forward(self):
        self.page().triggerAction(QWebEnginePage.Forward)

    def copy(self):
        if self.urlString:
            QApplication.clipboard().setText(self.urlString)

    def downloadMpFile(self, fileType):
        self.parent.downloadMpFile(fileType, self.urlString)
