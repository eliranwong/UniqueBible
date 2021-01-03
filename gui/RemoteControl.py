from re import search
import config, re
from functools import partial
from PySide2.QtWidgets import (QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit, QPushButton, QWidget)
from BibleVerseParser import BibleVerseParser
from ToolsSqlite import Commentary, LexiconData
from TextCommandParser import TextCommandParser
from BiblesSqlite import BiblesSqlite

class RemoteControl(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Remote Control")
        self.parent = parent
        # specify window size
        self.resizeWindow(1 / 3, 1 / 3)
        # setup interface
        self.setupUI()

    # window appearance
    def resizeWindow(self, widthFactor, heightFactor):
        availableGeometry = qApp.desktop().availableGeometry()
        self.resize(availableGeometry.width() * widthFactor, availableGeometry.height() * heightFactor)

    # re-implementing close event, when users close this widget
    # avoid closing by mistake
    # this window can be closed via "Remote Control [On / Off]" in menu bar
    def closeEvent(self, event):
        event.ignore()

    # setup ui
    def setupUI(self):
        mainLayout = QVBoxLayout()

        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setToolTip("Enter command here ...")
        self.searchLineEdit.returnPressed.connect(self.searchLineEntered)
        mainLayout.addWidget(self.searchLineEdit)

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

        otBooks = QGroupBox("Old Testament")
        otLayout = QVBoxLayout()
        otLayout.setMargin(0)
        otLayout.setSpacing(0)
        for bookNumGp in bookNumGps[0:4]:
            gp = QWidget()
            layout = self.newRowLayout()
            for bookNum in bookNumGp:
                text = self.bookMap[bookNum]
                button = QPushButton(text)
                button.clicked.connect(partial(self.bibleBookAction, bookNum))
                layout.addWidget(button)
            gp.setLayout(layout)
            otLayout.addWidget(gp)
        otBooks.setLayout(otLayout)
        mainLayout.addWidget(otBooks)

        ntBooks = QGroupBox("New Testament")
        ntLayout = QVBoxLayout()
        ntLayout.setMargin(0)
        ntLayout.setSpacing(0)
        for bookNumGp in bookNumGps[4:7]:
            gp = QWidget()
            layout = self.newRowLayout()
            for bookNum in bookNumGp:
                text = self.bookMap[bookNum]
                button = QPushButton(text)
                button.clicked.connect(partial(self.bibleBookAction, bookNum))
                layout.addWidget(button)
            gp.setLayout(layout)
            ntLayout.addWidget(gp)
        ntBooks.setLayout(ntLayout)
        mainLayout.addWidget(ntBooks)

        bibles_box = QGroupBox("Bibles")
        box_layout = QVBoxLayout()
        box_layout.setMargin(0)
        box_layout.setSpacing(0)
        row_layout = self.newRowLayout()
        bibleSqlite = BiblesSqlite()
        bibles = bibleSqlite.getBibleList()
        count = 0
        for bible in bibles:
            button = QPushButton(bible)
            button.setToolTip(bibleSqlite.bibleInfo(bible))
            button.clicked.connect(partial(self.bibleAction, bible))
            row_layout.addWidget(button)
            count += 1
            if count > 6:
                count = 0
                box_layout.addLayout(row_layout)
                row_layout = self.newRowLayout()
        box_layout.addLayout(row_layout)
        bibles_box.setLayout(box_layout)
        mainLayout.addWidget(bibles_box)

        commentaries_box = QGroupBox("Commentaries")
        box_layout = QVBoxLayout()
        box_layout.setMargin(0)
        box_layout.setSpacing(0)
        row_layout = self.newRowLayout()
        commentaries = Commentary().getCommentaryList()
        count = 0
        for commentary in commentaries:
            button = QPushButton(commentary)
            # button.setToolTip(Commentary(commentary).commentaryInfo())
            button.clicked.connect(partial(self.commentaryAction, commentary))
            row_layout.addWidget(button)
            count += 1
            if count > 6:
                count = 0
                box_layout.addLayout(row_layout)
                row_layout = self.newRowLayout()
        box_layout.addLayout(row_layout)
        commentaries_box.setLayout(box_layout)
        mainLayout.addWidget(commentaries_box)

        lexicons_box = QGroupBox("Lexicon")
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
        lexicons_box.setLayout(box_layout)
        mainLayout.addWidget(lexicons_box)

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
