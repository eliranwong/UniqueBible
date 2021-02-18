import config
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (QPushButton, QLineEdit, QComboBox, QGroupBox, QGridLayout, QHBoxLayout, QSlider, QVBoxLayout, QWidget)
from gui.HighlightLauncher import HighlightLauncher
from TtsLanguages import TtsLanguages

class MiscellaneousLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        # set title
        self.setWindowTitle(config.thisTranslation["cp4"])
        # set up variables
        self.parent = parent
        # setup interface
        self.setupUI()

    def setupUI(self):
        mainLayout = QGridLayout()
        leftLayout = QVBoxLayout()
        rightLayout = QVBoxLayout()
        self.highLightLauncher = HighlightLauncher(self)
        leftLayout.addWidget(self.highLightLauncher)
        rightLayout.addWidget(self.noteEditor())
        if config.ttsSupport:
            rightLayout.addWidget(self.textToSpeechUtility())
        rightLayout.addWidget(self.youTubeUtility())
        rightLayout.addStretch()
        mainLayout.addLayout(leftLayout, 0, 0, 1, 2)
        mainLayout.addLayout(rightLayout, 0, 2, 1, 1)
        self.setLayout(mainLayout)


    def noteEditor(self):
        box = QGroupBox(config.thisTranslation["note_editor"])
        subLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["menu7_create"])
        button.setToolTip(config.thisTranslation["menu7_create"])
        button.clicked.connect(self.parent.parent.createNewNoteFile)
        subLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["menu7_open"])
        button.setToolTip(config.thisTranslation["menu7_open"])
        button.clicked.connect(self.parent.parent.openTextFileDialog)
        subLayout.addWidget(button)
        box.setLayout(subLayout)
        return box

    def youTubeUtility(self):
        box = QGroupBox(config.thisTranslation["youtube_utility"])
        subLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["setup"])
        button.setToolTip(config.thisTranslation["menu11_setupDownload"])
        button.clicked.connect(self.parent.parent.setupYouTube)
        subLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["browser"])
        button.setToolTip(config.thisTranslation["builtInBrowser"])
        button.clicked.connect(self.parent.parent.openYouTube)
        subLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["download_mp3"])
        button.setToolTip(config.thisTranslation["youtube_mp3"])
        button.clicked.connect(self.parent.parent.downloadMp3Dialog)
        subLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["download_mp4"])
        button.setToolTip(config.thisTranslation["youtube_mp4"])
        button.clicked.connect(self.parent.parent.downloadMp4Dialog)
        subLayout.addWidget(button)
        box.setLayout(subLayout)
        return box

    def textToSpeechUtility(self):
        box = QGroupBox(config.thisTranslation["tts_utility"])

        layout = QVBoxLayout()

        subLayout = QHBoxLayout()
        self.ttsEdit = QLineEdit()
        self.ttsEdit.setClearButtonEnabled(True)
        self.ttsEdit.setToolTip(config.thisTranslation["enter_text_here"])
        self.ttsEdit.returnPressed.connect(self.speakText)
        subLayout.addWidget(self.ttsEdit)
        layout.addLayout(subLayout)

        self.ttsSlider = QSlider(Qt.Horizontal)
        self.ttsSlider.setMinimum(10)
        self.ttsSlider.setMaximum(310)
        self.ttsSlider.setValue(config.espeakSpeed if config.espeak else (160 + config.qttsSpeed * 150))
        self.ttsSlider.valueChanged.connect(self.changeEspeakSpeed if config.espeak else self.changeQttsSpeed)
        layout.addWidget(self.ttsSlider)

        subLayout = QHBoxLayout()

        self.languageCombo = QComboBox()
        subLayout.addWidget(self.languageCombo)
        if config.espeak:
            languages = TtsLanguages().isoLang2epeakLang
        else:
            languages = TtsLanguages().isoLang2qlocaleLang
        self.languageCodes = list(languages.keys())
        for code in self.languageCodes:
            self.languageCombo.addItem(languages[code][1])
        # Check if selected tts engine has the language user specify.
        if not (config.ttsDefaultLangauge in self.languageCodes):
            config.ttsDefaultLangauge = "en"
        # Set initial item
        initialIndex = self.languageCodes.index(config.ttsDefaultLangauge)
        self.languageCombo.setCurrentIndex(initialIndex)

        button = QPushButton(config.thisTranslation["speak"])
        button.setToolTip(config.thisTranslation["speak"])
        button.clicked.connect(self.speakText)
        subLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["stop"])
        button.setToolTip(config.thisTranslation["stop"])
        button.clicked.connect(self.parent.parent.textCommandParser.stopTtsAudio)
        subLayout.addWidget(button)
        layout.addLayout(subLayout)

        box.setLayout(layout)
        return box

    def speakText(self):
        text = self.ttsEdit.text()
        if ":::" in text:
            text = text.split(":::")[-1]
        command = "SPEAK:::{0}:::{1}".format(self.languageCodes[self.languageCombo.currentIndex()], text)
        self.parent.runTextCommand(command)

    def changeQttsSpeed(self, value):
        config.qttsSpeed = (value - 160) / 150

    def changeEspeakSpeed(self, value):
        config.espeakSpeed = value

    def refresh(self):
        self.highLightLauncher.refresh()
