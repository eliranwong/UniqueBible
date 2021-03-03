import config, re
from qtpy.QtWidgets import (QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget)
from qtpy.QtCore import QUrl
from gui.YouTubePopover import YouTubePopover


class MiniBrowser(QWidget):

    def __init__(self, parent):
        super().__init__()
        # set title
        self.setWindowTitle(config.thisTranslation["miniBrowser"])
        # set up variables
        self.parent = parent
        # setup interface
        self.setupUI()

    def setupUI(self):
        self.youTubeView = YouTubePopover(self)
        
        mainLayout = QVBoxLayout()

        layout = QHBoxLayout()
        button = QPushButton("<")
        button.setToolTip(config.thisTranslation["youtube_back"])
        button.clicked.connect(self.youTubeView.back)
        layout.addWidget(button)
        button = QPushButton(">")
        button.setToolTip(config.thisTranslation["youtube_forward"])
        button.clicked.connect(self.youTubeView.forward)
        layout.addWidget(button)
        self.addressBar = QLineEdit()
        self.addressBar.setClearButtonEnabled(True)
        self.addressBar.setToolTip(config.thisTranslation["enter_fullURL"])
        self.addressBar.returnPressed.connect(self.openURL)
        layout.addWidget(self.addressBar)
        button = QPushButton("mp3")
        button.setToolTip(config.thisTranslation["youtube_mp3"])
        button.clicked.connect(lambda: self.downloadMpFromURL("mp3"))
        layout.addWidget(button)
        button = QPushButton("mp4")
        button.setToolTip(config.thisTranslation["youtube_mp4"])
        button.clicked.connect(lambda: self.downloadMpFromURL("mp4"))
        layout.addWidget(button)
        mainLayout.addLayout(layout)

        self.addressBar.setText("https://www.youtube.com/")
        self.openURL()
        mainLayout.addWidget(self.youTubeView)

        self.setLayout(mainLayout)

    def openURL(self):
        address = self.addressBar.text()
        if address:
            self.youTubeView.load(QUrl(address))

    def downloadMpFromURL(self, fileType):
        address = self.addressBar.text()
        self.downloadMpFile(fileType, address)

    def downloadMpFile(self, fileType, address):
        if not address or not re.search("youtube", address, flags=re.IGNORECASE) or "/results?search_query=" in address:
            self.parent.displayMessage(config.thisTranslation["youTubeLinkNotFound"])
        else:
            self.parent.runTextCommand("{0}:::{1}".format(fileType, address))
