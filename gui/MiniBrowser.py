import config, re, webbrowser
from qtpy.QtWidgets import (QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QListView, QAbstractItemView, QMessageBox, QLabel, QDialog)
from qtpy.QtCore import QUrl, QStringListModel
from gui.YouTubePopover import YouTubePopover


class YouTubeDownloadOptions(QDialog):

    def __init__(self, parent, options):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["downloadOptions"])
        self.parent = parent
        self.options = options
        self.setModal(True)
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()
        # Add a label
        layout.addWidget(QLabel(config.thisTranslation["downloadOptions"]))
        # Add a list view
        list = QListView()
        list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        model = QStringListModel(self.options)
        list.setModel(model)
        list.selectionModel().selectionChanged.connect(self.optionSelected)
        list.setCurrentIndex(model.index(len(self.options) - 1, 0))
        layout.addWidget(list)
        
        subLayout = QHBoxLayout()

        # Add a cancel button
        button = QPushButton(config.thisTranslation["message_cancel"])
        button.clicked.connect(self.close)
        subLayout.addWidget(button)
        # Add a download button
        button = QPushButton(config.thisTranslation["download"])
        button.clicked.connect(lambda: self.parent.downloadSelectedOption(self.selectedOption))
        subLayout.addWidget(button)

        layout.addLayout(subLayout)

        # Set layout
        self.setLayout(layout)
    
    def optionSelected(self, selection):
        index = selection[0].indexes()[0].row()
        self.selectedOption = self.options[index]


class MiniBrowser(QWidget):

    def __init__(self, parent):
        super().__init__()
        # Set title
        self.setWindowTitle(config.thisTranslation["miniBrowser"])
        # Set up variables
        self.parent = parent
        self.isFfmpegInstalled = self.parent.textCommandParser.isFfmpegInstalled()
        # Setup interface
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
        button.clicked.connect(lambda: self.convertToFormat("mp3"))
        layout.addWidget(button)
        if self.isFfmpegInstalled:
            button = QPushButton("mp4")
            button.setToolTip(config.thisTranslation["youtube_mp4"])
            button.clicked.connect(lambda: self.convertToFormat("mp4"))
            layout.addWidget(button)
        else:
            button = QPushButton(config.thisTranslation["menu11_video"])
            button.setToolTip(config.thisTranslation["downloadVideo"])
            button.clicked.connect(self.downloadLastOption)
            layout.addWidget(button)
        button = QPushButton("+")
        button.setToolTip(config.thisTranslation["downloadOptions"])
        button.clicked.connect(self.downloadOptions)
        layout.addWidget(button)
        mainLayout.addLayout(layout)

        self.addressBar.setText("https://www.youtube.com/")
        self.openURL()
        mainLayout.addWidget(self.youTubeView)

        self.setLayout(mainLayout)

    def getYouTubeDownloadOptions(self):
        url = self.addressBar.text()
        return self.parent.textCommandParser.getYouTubeDownloadOptions(url)

    def downloadSelectedOption(self, option):
        self.youTubeDownloadOptions.close()
        option = re.sub("^([0-9]+?) .*?$", r"\1", option)
        downloadCommand = "youtube-dl -f {0}".format(option)
        self.parent.textCommandParser.youtubeDownload(downloadCommand, self.addressBar.text())

    def downloadLastOption(self):
        options = self.getYouTubeDownloadOptions()
        if options:
            self.downloadSelectedOption(options[-1])
        else:
            self.displayMessage(config.thisTranslation["noSupportedUrlFormat"])

    def downloadOptions(self):
        options = self.getYouTubeDownloadOptions()
        if options:
            self.youTubeDownloadOptions = YouTubeDownloadOptions(self, options)
            self.youTubeDownloadOptions.show()
            self.youTubeDownloadOptions.setFixedSize(640, 400)
        else:
            self.displayMessage(config.thisTranslation["noSupportedUrlFormat"])

    def displayMessage(self, message="", title="UniqueBible"):
        if hasattr(config, "cli") and config.cli:
            print(message)
        else:
            reply = QMessageBox.information(self, title, message)

    def openURL(self):
        address = self.addressBar.text()
        if address:
            self.youTubeView.load(QUrl(address))

    def convertToFormat(self, fileType):
        if self.isFfmpegInstalled:
            address = self.addressBar.text()
            self.downloadMpFile(fileType, address)
        else:
            self.displayMessage(config.thisTranslation["ffmpegNotFound"])
            webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/Install-ffmpeg")

    def downloadMpFile(self, fileType, address):
        if not address or not re.search("youtube", address, flags=re.IGNORECASE) or "/results?search_query=" in address:
            self.displayMessage(config.thisTranslation["youTubeLinkNotFound"])
        else:
            self.parent.runTextCommand("{0}:::{1}".format(fileType, address))
