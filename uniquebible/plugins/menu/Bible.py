from uniquebible import config
import os, re
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
from uniquebible.db.BiblesSqlite import BiblesSqlite, Bible
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.BibleVerseParser import BibleVerseParser
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtWebEngineCore import QWebEnginePage
    from PySide6.QtGui import QStandardItemModel, QStandardItem, QGuiApplication
    from PySide6.QtWidgets import QWidget, QPushButton, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox, QCompleter
else:
    from qtpy.QtCore import Qt
    from qtpy.QtWebEngineWidgets import QWebEnginePage
    from qtpy.QtGui import QStandardItemModel, QStandardItem, QGuiApplication
    from qtpy.QtWidgets import QWidget, QPushButton, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QSplitter, QComboBox, QCompleter

class Bibles(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["menu5_bible"])
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
        # Bible reference
        self.b = config.mainB
        self.c = config.mainC
        self.v = config.mainV
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
            self.b, self.c, self.v, config.mainB, config.mainC, config.mainV = 1, 1, 1, 1, 1, 1
        self.bookView.setCurrentIndex(initialIndex)
        self.bookView.currentIndexChanged.connect(self.bookSelected)
        self.chapterView = QComboBox()
        self.chapterView.currentIndexChanged.connect(self.chapterSelected)
        self.verseView = QComboBox()
        self.verseView.currentIndexChanged.connect(self.verseSelected)
        ###
        self.previousButton = QPushButton()
        self.previousButton.setToolTip(config.thisTranslation["menu_previous_chapter"])
        icon = "material/image/navigate_before/materialiconsoutlined/48dp/2x/outline_navigate_before_black_48dp.png"
        style = self.parent.getQIcon(icon)
        self.previousButton.setStyleSheet(style)
        self.previousButton.clicked.connect(self.previousChapter)

        self.nextButton = QPushButton()
        self.nextButton.setToolTip(config.thisTranslation["menu_next_chapter"])
        icon = "material/image/navigate_next/materialiconsoutlined/48dp/2x/outline_navigate_next_black_48dp.png"
        style = self.parent.getQIcon(icon)
        self.nextButton.setStyleSheet(style)
        self.nextButton.clicked.connect(self.nextChapter)

        self.referenceEntry = QLineEdit()
        self.referenceEntry.mousePressEvent = lambda _ : self.referenceEntry.selectAll()
        referenceAutosuggestion = QCompleter(BibleBooks().getAllKJVreferences()[0])
        referenceAutosuggestion.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.referenceEntry.setCompleter(referenceAutosuggestion)
        self.referenceEntry.setClearButtonEnabled(True)
        reference = config.mainWindow.bcvToVerseReference(self.b, self.c, self.v)
        self.referenceEntry.setText(reference)
        self.referenceEntry.returnPressed.connect(self.referenceEntered)
        ###
        self.searchEntry = QLineEdit()
        self.searchEntry.mousePressEvent = lambda _ : self.searchEntry.selectAll()
        self.searchEntry.setClearButtonEnabled(True)
        self.searchEntry.setText(config.mainText)
        self.searchEntry.textChanged.connect(self.filterEntry)
        entryView = QListView()
        entryView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        entryView.setWordWrap(True)
        self.entryViewModel = QStandardItemModel(entryView)
        entryView.setModel(self.entryViewModel)
        self.filterEntry()
        entryView.selectionModel().selectionChanged.connect(self.entrySelected)
        openButton = QPushButton(config.thisTranslation["html_openMain"])
        openButton.clicked.connect(self.openOnMainWindow)
        layoutBcv = QHBoxLayout()
        layoutBcv.addWidget(self.bookView)
        layoutBcv.addWidget(self.chapterView)
        layoutBcv.addWidget(self.verseView)
        layout000Lt.addLayout(layoutBcv)
        layoutReference = QHBoxLayout()
        layoutReference.addWidget(self.referenceEntry)
        layoutReference.addWidget(self.previousButton)
        layoutReference.addWidget(self.nextButton)
        layout000Lt.addLayout(layoutReference)
        layout000Lt.addWidget(self.searchEntry)
        layout000Lt.addWidget(entryView)
        layout000Lt.addWidget(openButton)

        #widgets on the right
        self.searchEntryRt = QLineEdit()
        self.searchEntryRt.mousePressEvent = lambda _ : self.searchEntryRt.selectAll()
        self.searchEntryRt.setClearButtonEnabled(True)
        self.searchEntryRt.textChanged.connect(self.highlightContent)
        self.contentView = WebEngineViewPopover(config.mainWindow, "main", "main", windowTitle=config.thisTranslation["menu5_bible"], enableCloseAction=False)
        html = config.mainWindow.wrapHtml("<h2>{0}</h2>".format(config.thisTranslation["menu5_bible"]))
        self.contentView.setHtml(html, config.baseUrl)
        layout000Rt.addWidget(self.searchEntryRt)
        layout000Rt.addWidget(self.contentView)

        self.bookSelected(initialIndex, initialSetup=True)

    def highlightContent(self):
        searchString = self.searchEntryRt.text().strip()
        self.contentView.findText(searchString, QWebEnginePage.FindFlags())

    def previousChapter(self):
        newChapter = config.mainC - 1
        if newChapter == 0:
            prevBook = Bible(config.mainText).getPreviousBook(config.mainB)
            newChapter = BibleBooks.getLastChapter(prevBook)
            config.mainB = prevBook
        mainChapterList = BiblesSqlite().getChapterList(config.mainB)
        if newChapter in mainChapterList:
            newReference = config.mainWindow.bcvToVerseReference(config.mainB, newChapter, 1)
            self.runNewReference(newReference)

    def nextChapter(self):
        if config.mainC < BibleBooks.getLastChapter(config.mainB):
            newChapter = config.mainC + 1
            mainChapterList = BiblesSqlite().getChapterList(config.mainB)
            if newChapter in mainChapterList:
                newReference = config.mainWindow.bcvToVerseReference(config.mainB, newChapter, 1)
                self.runNewReference(newReference)
        else:
            self.nextMainBook()

    def nextMainBook(self):
        nextBook = Bible(config.mainText).getNextBook(config.mainB)
        if nextBook:
            newReference = config.mainWindow.bcvToVerseReference(nextBook, 1, 1)
            if newReference:
                self.runNewReference(newReference)

    def runNewReference(self, reference):
        self.referenceEntry.setText(reference)
        self.referenceEntered()

    def referenceEntered(self):
        reference = self.referenceEntry.text().strip()
        if reference:
            verseList = BibleVerseParser(config.parserStandarisation).extractAllReferences(reference)
            if verseList:
                verse = verseList[0]
                self.b, self.c, self.v, *_ = verse
                if 66 >= self.b >=1:
                    self.bookSelected(self.b - 1, True)

    def bookSelected(self, index, initialSetup=False):
        if self.refreshing == False:
            self.refreshing = True
            if initialSetup:
                self.bookView.setCurrentIndex(index)
            else:
                self.b = index + 1
            self.populateChapterView(initialSetup=initialSetup)
            self.populateVerseView(initialSetup=initialSetup)
            self.displayBible()
            self.refreshing = False

    def chapterSelected(self, index):
        if not self.refreshing:
            self.c = int(self.chapters[index])
            self.populateVerseView()
            self.displayBible()

    def verseSelected(self, index):
        if not self.refreshing:
            self.v = int(self.verses[index])
            self.displayBible()

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
        self.entries = config.mainWindow.textFullNameList
        for index, entryID in enumerate(self.entries):
            bibleAbb = config.mainWindow.textList[index]
            if searchString.lower() in entryID.lower() or searchString.lower() == bibleAbb.lower():
                bible = "[{0}] {1}".format(bibleAbb, entryID)
                item = QStandardItem(bible)
                item.setToolTip(bible)
                self.entryViewModel.appendRow(item)

    def entrySelected(self, selection):
        if not self.refreshing:
            # get articleEntry
            index = selection[0].indexes()[0].row()
            toolTip = self.entryViewModel.item(index).toolTip()
            config.mainText = re.sub("^\[(.*?)\].*?$", r"\1", toolTip)
            self.displayBible()
    
    def displayBible(self):
        # fetch entry data
        bcvTuple = (self.b, self.c, self.v)
        reference = config.mainWindow.bcvToVerseReference(*bcvTuple)
        self.referenceEntry.setText(reference)
        content = config.mainWindow.textCommandParser.textBibleVerseParser(reference, config.mainText, "main")[1]
        if not content == "INVALID_COMMAND_ENTERED":
            config.mainWindow.textCommandParser.setMainVerse(config.mainText, bcvTuple)
        content = config.mainWindow.wrapHtml(content)
        self.contentView.setHtml(content, config.baseUrl)
        config.mainB, config.mainC, config.mainV = self.b, self.c, self.v
        # enable auto-scrolling
        config.studyB, config.studyC, config.studyV = self.b, self.c, self.v

    def openOnMainWindow(self):
        # command examples, BIBLE:::KJV:::John 3:16
        if config.mainText:
            command = "BIBLE:::{0}:::{1}".format(config.mainText, config.mainWindow.bcvToVerseReference(self.b, self.c, self.v))
            config.mainWindow.runTextCommand(command)


databaseFile = os.path.join(config.marvelData, "images.sqlite")
if os.path.isfile(databaseFile):
    config.mainWindow.pluginBible = Bibles(config.mainWindow)
    config.mainWindow.pluginBible.show()
else:
    databaseInfo = ((config.marvelData, "images.sqlite"), "1-aFEfnSiZSIjEPUQ2VIM75I4YRGIcy5-")
    config.mainWindow.downloadHelper(databaseInfo)
