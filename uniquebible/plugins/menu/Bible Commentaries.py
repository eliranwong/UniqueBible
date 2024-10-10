from uniquebible import config
import os, re
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
from uniquebible.db.ToolsSqlite import Commentary
from uniquebible.db.BiblesSqlite import BiblesSqlite
from uniquebible.util.BibleVerseParser import BibleVerseParser
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtWebEngineCore import QWebEnginePage
    from PySide6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication
    from PySide6.QtWidgets import QWidget, QPushButton, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox
else:
    from qtpy.QtCore import Qt
    from qtpy.QtWebEngineWidgets import QWebEnginePage
    from qtpy.QtGui import QStandardItemModel, QStandardItem, QGuiApplication
    from qtpy.QtWidgets import QWidget, QPushButton, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox

class BibleCommentaries(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["menu4_commentary"])
        #self.setMinimumSize(830, 500)
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()
        # set initial window size
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)

    def setupVariables(self):
        bibleVerseParser = BibleVerseParser(config.parserStandarisation)
        self.bookNo2Abb = bibleVerseParser.standardAbbreviation
        self.bookNo2Name = bibleVerseParser.standardFullBookName
        self.books = [self.bookNo2Abb[str(b)] for b in range(1, 67)]
        self.chapters = []
        self.verses = []
        # Commentary reference
        if config.syncAction == "COMMENTARY":
            self.b = config.mainB
            self.c = config.mainC
            self.v = config.mainV
        else:
            self.b = config.commentaryB
            self.c = config.commentaryC
            self.v = config.commentaryV
        # Entries
        self.entries = []
        self.refreshing = False

    def setupUI(self):
        layout000 = QHBoxLayout()
        self.setLayout(layout000)
        widgetLt = QWidget()
        layout000Lt = QVBoxLayout()
        widgetLt.setLayout(layout000Lt)
        widgetRt = QWidget()
        layout000Rt = QVBoxLayout()
        widgetRt.setLayout(layout000Rt)
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.addWidget(widgetLt)
        splitter.addWidget(widgetRt)
        layout000.addWidget(splitter)

        # widgets on the left
        self.bookView = QComboBox()
        self.bookView.addItems(self.books)
        for index, *_ in enumerate(self.books):
            self.bookView.setItemData(index, self.bookNo2Name[str(index + 1)], Qt.ToolTipRole)
        initialIndex = self.b - 1
        if initialIndex < 0 or initialIndex > 65:
            initialIndex = 0
            self.b, self.c, self.v, config.commentaryB, config.commentaryC, config.commentaryV = 1, 1, 1, 1, 1, 1
        self.bookView.setCurrentIndex(initialIndex)
        self.bookView.currentIndexChanged.connect(self.bookSelected)
        self.chapterView = QComboBox()
        self.chapterView.currentIndexChanged.connect(self.chapterSelected)
        self.verseView = QComboBox()
        self.verseView.currentIndexChanged.connect(self.verseSelected)
        ###
        self.searchEntry = QLineEdit()
        self.searchEntry.setClearButtonEnabled(True)
        self.searchEntry.setText(config.commentaryText)
        #self.searchEntry.setText(config.commentaryText)
        self.searchEntry.textChanged.connect(self.filterEntry)
        #self.searchEntry.returnPressed.connect(self.filterEntry)
        entryView = QListView()
        entryView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        entryView.setWordWrap(True)
        self.entryViewModel = QStandardItemModel(entryView)
        entryView.setModel(self.entryViewModel)
        self.filterEntry()
        entryView.selectionModel().selectionChanged.connect(self.entrySelected)
        openButton = QPushButton(config.thisTranslation["html_openStudy"])
        openButton.clicked.connect(self.openOnMainWindow)
        layoutBcv = QHBoxLayout()
        layoutBcv.addWidget(self.bookView)
        layoutBcv.addWidget(self.chapterView)
        layoutBcv.addWidget(self.verseView)
        layout000Lt.addLayout(layoutBcv)
        layout000Lt.addWidget(self.searchEntry)
        layout000Lt.addWidget(entryView)
        layout000Lt.addWidget(openButton)

        #widgets on the right
        self.searchEntryRt = QLineEdit()
        self.searchEntryRt.setClearButtonEnabled(True)
        self.searchEntryRt.textChanged.connect(self.highlightContent)
        self.contentView = WebEngineViewPopover(config.mainWindow, "main", "main", windowTitle=config.thisTranslation["menu4_commentary"], enableCloseAction=False)
        html = config.mainWindow.wrapHtml("<h2>{0}</h2>".format(config.thisTranslation["menu4_commentary"]))
        self.contentView.setHtml(html, config.baseUrl)
        layout000Rt.addWidget(self.searchEntryRt)
        layout000Rt.addWidget(self.contentView)

        self.bookSelected(initialIndex, initialSetup=True)

    def highlightContent(self):
        searchString = self.searchEntryRt.text().strip()
        self.contentView.findText(searchString, QWebEnginePage.FindFlags())

    def bookSelected(self, index, initialSetup=False):
        self.refreshing = True
        if not initialSetup:
            self.b = index + 1
        self.populateChapterView(initialSetup=initialSetup)
        self.populateVerseView(initialSetup=initialSetup)
        self.displayCommentary()
        self.refreshing = False

    def chapterSelected(self, index):
        if not self.refreshing:
            self.c = int(self.chapters[index])
            self.populateVerseView()
            self.displayCommentary()

    def verseSelected(self, index):
        if not self.refreshing:
            self.v = int(self.verses[index])
            self.displayCommentary()

    def populateChapterView(self, initialSetup=False):
        self.refreshing = True
        self.chapterView.clear()
        self.chapters = BiblesSqlite().getKJVchapters(self.b)
        if self.chapters:
            if not initialSetup:
                self.c = self.chapters[0]
                initialIndex = 0
            else:
                try:
                    initialIndex = self.chapters.index(self.c)
                except:
                    self.c = self.chapters[0]
                    initialIndex = 0
            self.chapters = [str(c) for c in self.chapters]
            self.chapterView.addItems(self.chapters)
            self.chapterView.setCurrentIndex(initialIndex)
        self.refreshing = False

    def populateVerseView(self, initialSetup=False):
        self.refreshing = True
        self.verseView.clear()
        self.verses = BiblesSqlite().getKJVverses(self.b, self.c)
        if self.verses:
            if not initialSetup:
                self.v = self.verses[0]
                initialIndex = 0
            else:
                try:
                    initialIndex = self.verses.index(self.v)
                except:
                    self.v = self.verses[0]
                    initialIndex = 0
            self.verses = [str(v) for v in self.verses]
            self.verseView.addItems(self.verses)
            self.verseView.setCurrentIndex(initialIndex)
        self.refreshing = False

    def filterEntry(self):
        # clear entry view
        self.entryViewModel.clear()
        # get search string
        searchString = self.searchEntry.text().strip()
        # get all entries
        self.entries = config.mainWindow.commentaryFullNameList
        for index, entryID in enumerate(self.entries):
            commentaryAbb = config.mainWindow.commentaryList[index]
            if searchString.lower() in entryID.lower() or searchString.lower() == commentaryAbb.lower():
                commentary = "[{0}] {1}".format(commentaryAbb, entryID)
                item = QStandardItem(commentary)
                item.setToolTip(commentary)
                self.entryViewModel.appendRow(item)

    def entrySelected(self, selection):
        if not self.refreshing:
            # get articleEntry
            index = selection[0].indexes()[0].row()
            toolTip = self.entryViewModel.item(index).toolTip()
            config.commentaryText = re.sub("^\[(.*?)\].*?$", r"\1", toolTip)
            self.displayCommentary()
    
    def displayCommentary(self):
        # fetch entry data
        commentary = Commentary(config.commentaryText)
        bcvTuple = (self.b, self.c, self.v)
        content = commentary.getContent(bcvTuple)
        if not content == "INVALID_COMMAND_ENTERED":
            config.mainWindow.textCommandParser.setCommentaryVerse(config.commentaryText, bcvTuple)
        content = config.mainWindow.wrapHtml(content)
        self.contentView.setHtml(content, config.baseUrl)
        config.commentaryB, config.commentaryC, config.commentaryV = self.b, self.c, self.v
        config.mainWindow.updateCommentaryRefButton()

    def openOnMainWindow(self):
        # command examples, COMMENTARY:::CBSC:::Rom 8:33
        if config.commentaryText:
            command = "COMMENTARY:::{0}:::{1}".format(config.commentaryText, config.mainWindow.bcvToVerseReference(self.b, self.c, self.v))
            config.mainWindow.runTextCommand(command)


databaseFile = os.path.join(config.marvelData, "commentaries", "cCBSC.commentary")
if os.path.isfile(databaseFile):
    config.mainWindow.bibleCommentary = BibleCommentaries(config.mainWindow)
    config.mainWindow.bibleCommentary.show()
else:
    databaseInfo = ((config.marvelData, "commentaries", "cCBSC.commentary"), "1IxbscuAMZg6gQIjzMlVkLtJNDQ7IzTh6")
    config.mainWindow.downloadHelper(databaseInfo)
