import config, re, subprocess
from qtpy.QtWidgets import (QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, QWidget, QListView, QAbstractItemView, QMessageBox, QLabel)
from qtpy.QtCore import QUrl, QStringListModel
from gui.YouTubePopover import YouTubePopover


class YouTubeDownloadOptions(QWidget):

    def __init__(self, parent, options):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["menu_more"])
        self.parent = parent
        self.options = options
        self.setupUI()

    def setupUI(self):
        layout = QVBoxLayout()
        # Add a label
        layout.addWidget(QLabel(config.thisTranslation["menu_more"]))
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
        button = QPushButton("+")
        button.setToolTip(config.thisTranslation["menu_more"])
        button.clicked.connect(self.downloadOptions)
        layout.addWidget(button)
        mainLayout.addLayout(layout)

        self.addressBar.setText("https://www.youtube.com/")
        self.openURL()
        mainLayout.addWidget(self.youTubeView)

        self.setLayout(mainLayout)

    def downloadSelectedOption(self, option):
        self.youTubeDownloadOptions.close()
        option = re.sub("^([0-9]+?) .*?$", r"\1", option)
        downloadCommand = "youtube-dl -f {0}".format(option)
        self.parent.textCommandParser.youtubeDownload(downloadCommand, self.addressBar.text())

    def downloadOptions(self):
        address = self.addressBar.text()
        options = subprocess.Popen("youtube-dl -F {0}".format(address), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, *_ = options.communicate()
        options = stdout.decode("utf-8").split("\n")
        options = [option for option in options if re.search(r"^[0-9]+? ", option)]
        
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

    def downloadMpFromURL(self, fileType):
        address = self.addressBar.text()
        self.downloadMpFile(fileType, address)

    def downloadMpFile(self, fileType, address):
        if not address or not re.search("youtube", address, flags=re.IGNORECASE) or "/results?search_query=" in address:
            self.parent.displayMessage(config.thisTranslation["youTubeLinkNotFound"])
        else:
            self.parent.runTextCommand("{0}:::{1}".format(fileType, address))
