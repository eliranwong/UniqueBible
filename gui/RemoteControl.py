from re import search
import config, re
from functools import partial
from PySide2.QtWidgets import (QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit, QPushButton, QWidget, QTabWidget)
from BibleVerseParser import BibleVerseParser
from ToolsSqlite import Commentary, LexiconData, Lexicon
from TextCommandParser import TextCommandParser
from BiblesSqlite import BiblesSqlite

class RemoteControl(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["remote_control"])
        self.parent = parent
        # specify window size
        self.resizeWindow(1 / 3, 1 / 3)
        # setup interface
        self.setupUI()

    # window appearance
    def resizeWindow(self, widthFactor, heightFactor):
        availableGeometry = qApp.desktop().availableGeometry()
        self.resize(availableGeometry.width() * widthFactor, availableGeometry.height() * heightFactor)

    def closeEvent(self, event):
        config.remoteControl = False

    # setup ui
    def setupUI(self):
        mainLayout = QVBoxLayout()

        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setToolTip(config.thisTranslation["enter_command_here"])
        self.searchLineEdit.returnPressed.connect(self.searchLineEntered)
        mainLayout.addWidget(self.searchLineEdit)

        tabs = QTabWidget()
        mainLayout.addWidget(tabs)

        parser = BibleVerseParser(config.parserStandarisation)
        self.bookMap = parser.standardAbbreviation
        bookNums = list(self.bookMap.keys())
        bookNumGps = [
            bookNums[0:10],
            bookNums[10:20],
            bookNums[20:30],
            bookNums[30:39],
            bookNums[39:49],
            bookNums[49:59],
            bookNums[59:66],
        ]

        bible = QWidget()
        bible_layout = QVBoxLayout()
        bible_layout.setMargin(0)
        bible_layout.setSpacing(0)
        for bookNumGp in bookNumGps[0:4]:
            gp = QWidget()
            layout = self.newRowLayout()
            for bookNum in bookNumGp:
                text = self.bookMap[bookNum]
                button = QPushButton(text)
                button.clicked.connect(partial(self.bibleBookAction, bookNum))
                layout.addWidget(button)
            gp.setLayout(layout)
            bible_layout.addWidget(gp)

        for bookNumGp in bookNumGps[4:7]:
            gp = QWidget()
            layout = self.newRowLayout()
            for bookNum in bookNumGp:
                text = self.bookMap[bookNum]
                button = QPushButton(text)
                button.clicked.connect(partial(self.bibleBookAction, bookNum))
                layout.addWidget(button)
            gp.setLayout(layout)
            bible_layout.addWidget(gp)

        bible_layout.addStretch()
        bible.setLayout(bible_layout)
        tabs.addTab(bible, config.thisTranslation["bible"])

        bibles_box = QWidget()
        box_layout = QVBoxLayout()
        box_layout.setMargin(0)
        box_layout.setSpacing(0)
        row_layout = self.newRowLayout()
        bibleSqlite = BiblesSqlite()
        bibles = bibleSqlite.getBibleList()
        count = 0
        for bible in bibles:
            button = QPushButton(bible)
            button.clicked.connect(partial(self.bibleAction, bible))
            row_layout.addWidget(button)
            count += 1
            if count > 6:
                count = 0
                box_layout.addLayout(row_layout)
                row_layout = self.newRowLayout()
        box_layout.addLayout(row_layout)
        box_layout.addStretch()
        bibles_box.setLayout(box_layout)

        tabs.addTab(bibles_box, config.thisTranslation["translations"])

        commentaries_box = QWidget()
        box_layout = QVBoxLayout()
        box_layout.setMargin(0)
        box_layout.setSpacing(0)
        row_layout = self.newRowLayout()
        commentaries = Commentary().getCommentaryList()
        count = 0
        for commentary in commentaries:
            button = QPushButton(commentary)
            button.clicked.connect(partial(self.commentaryAction, commentary))
            row_layout.addWidget(button)
            count += 1
            if count > 6:
                count = 0
                box_layout.addLayout(row_layout)
                row_layout = self.newRowLayout()
        box_layout.addLayout(row_layout)
        box_layout.addStretch()
        commentaries_box.setLayout(box_layout)

        tabs.addTab(commentaries_box, config.thisTranslation["commentaries"])

        lexicons_box = QWidget()
        box_layout = QVBoxLayout()
        box_layout.setMargin(0)
        box_layout.setSpacing(0)
        row_layout = self.newRowLayout()
        lexicons = LexiconData().lexiconList
        count = 0
        for lexicon in lexicons:
            button = QPushButton(lexicon)
            button.clicked.connect(partial(self.lexiconAction, lexicon))
            row_layout.addWidget(button)
            count += 1
            if count > 6:
                count = 0
                box_layout.addLayout(row_layout)
                row_layout = self.newRowLayout()
        box_layout.addLayout(row_layout)
        box_layout.addStretch()
        lexicons_box.setLayout(box_layout)

        tabs.addTab(lexicons_box, config.thisTranslation["lexicons"])

        self.setLayout(mainLayout)

    def newRowLayout(self):
        row_layout = QHBoxLayout()
        row_layout.setSpacing(0)
        row_layout.setMargin(0)
        return row_layout

    # search field entered
    def searchLineEntered(self):
        searchString = self.searchLineEdit.text()
        self.parent.runTextCommand(searchString)

    def bibleBookAction(self, book):
        self.searchLineEdit.setText("{0} ".format(self.bookMap[book]))
        self.searchLineEdit.setFocus()

    def bibleAction(self, bible):
        command = "BIBLE:::{0}:::{1} ".format(bible, self.parent.verseReference("main")[1])
        self.parent.runTextCommand(command)
        command = "_bibleinfo:::{0}".format(bible)
        self.parent.runTextCommand(command)

    def commentaryAction(self, commentary):
        command = "COMMENTARY:::{0}:::{1}".format(commentary, self.parent.verseReference("main")[1])
        self.parent.runTextCommand(command)
        command = "_commentaryinfo:::{0}".format(commentary)
        self.parent.runTextCommand(command)

    def lexiconAction(self, lexicon):
        command = "LEXICON:::{0}:::{1} ".format(lexicon, TextCommandParser.last_lexicon_entry)
        self.parent.runTextCommand(command)
