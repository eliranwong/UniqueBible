from uniquebible import config
import os, apsw, re
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
from uniquebible.util.ThirdParty import ThirdPartyDictionary
from uniquebible.db.ToolsSqlite import Book, BookData
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

class ReferenceBooks(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["installBooks"])
        #self.setMinimumSize(830, 500)
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()
        # set initial window size
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)
        # display initial content
        self.displayBookContent()

    def setupVariables(self):
        self.modules = config.mainWindow.referenceBookList
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
        maxWidth = 350
        self.moduleView = QComboBox()
        self.moduleView.setMaximumWidth(maxWidth)
        self.moduleView.addItems(self.modules)
        for index, tooltip in enumerate(self.modules):
            self.moduleView.setItemData(index, tooltip, Qt.ToolTipRole)
        initialIndex = config.mainWindow.referenceBookList.index(config.book) if config.book in config.mainWindow.referenceBookList else 0
        if initialIndex < len(self.modules):
            self.moduleView.setCurrentIndex(initialIndex)
        self.moduleView.currentIndexChanged.connect(self.moduleSelected)
        self.searchEntry = QLineEdit()
        self.searchEntry.setMaximumWidth(maxWidth)
        self.searchEntry.setClearButtonEnabled(True)
        self.searchEntry.setText(config.mainWindow.selectedText())
        self.searchEntry.textChanged.connect(self.filterEntry)
        #self.searchEntry.returnPressed.connect(self.filterEntry)
        entryView = QListView()
        entryView.setMaximumWidth(maxWidth)
        entryView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        entryView.setWordWrap(True)
        self.entryViewModel = QStandardItemModel(entryView)
        entryView.setModel(self.entryViewModel)
        self.filterEntry()
        entryView.selectionModel().selectionChanged.connect(self.entrySelected)
        openButton = QPushButton(config.thisTranslation["html_openStudy"])
        openButton.setMaximumWidth(maxWidth)
        openButton.clicked.connect(self.openOnMainWindow)
        layout000Lt.addWidget(self.moduleView)
        layout000Lt.addWidget(self.searchEntry)
        layout000Lt.addWidget(entryView)
        layout000Lt.addWidget(openButton)

        #widgets on the right
        self.searchEntryRt = QLineEdit()
        self.searchEntryRt.setClearButtonEnabled(True)
        self.searchEntryRt.textChanged.connect(self.highlightContent)
        openPrevButton = QPushButton("＜")
        openPrevButton.setToolTip(config.thisTranslation["menu_previous_chapter"])
        openPrevButton.clicked.connect(self.openBookPreviousChapter)
        openNextButton = QPushButton("＞")
        openNextButton.setToolTip(config.thisTranslation["menu_next_chapter"])
        openNextButton.clicked.connect(self.openBookNextChapter)
        self.contentView = WebEngineViewPopover(config.mainWindow, "main", "main", windowTitle=config.thisTranslation["installBooks"], enableCloseAction=False)
        html = config.mainWindow.wrapHtml("<h2>{0}</h2>".format(config.thisTranslation["installBooks"]))
        self.contentView.setHtml(html, config.baseUrl)
        layoutRtTop = QHBoxLayout()
        layoutRtTop.addWidget(self.searchEntryRt)
        layoutRtTop.addWidget(openPrevButton)
        layoutRtTop.addWidget(openNextButton)
        layout000Rt.addLayout(layoutRtTop)
        layout000Rt.addWidget(self.contentView)

    def highlightContent(self):
        searchString = self.searchEntryRt.text().strip()
        self.contentView.findText(searchString, QWebEnginePage.FindFlags())

    def moduleSelected(self, index):
        self.refreshing = True
        self.filterEntry()
        self.refreshing = False

    def filterEntry(self):
        # clear entry view
        self.entryViewModel.clear()
        # get search string
        searchString = self.searchEntry.text().strip()
        # get all entries
        module = self.modules[self.moduleView.currentIndex()]
        self.entries = Book(module).getTopicList()
        for entryID in self.entries:
            if searchString.lower() in entryID.lower():
                item = QStandardItem(re.sub("<.*?>", "", entryID))
                item.setToolTip(entryID)
                self.entryViewModel.appendRow(item)

    def entrySelected(self, selection):
        if not self.refreshing:
            # set config
            self.setBookConfig()
            # get articleEntry
            index = selection[0].indexes()[0].row()
            config.bookChapter = self.entryViewModel.item(index).toolTip()
            # fetch entry data
            self.displayBookContent()

    def setBookConfig(self):
        moduleIndex = self.moduleView.currentIndex()
        config.book = self.modules[moduleIndex]
        config.mainWindow.updateBookButton()

    def displayBookContent(self):
        if config.book and config.bookChapter:
            content = BookData().getContent(config.book, config.bookChapter)
            content = config.mainWindow.wrapHtml(content)
            self.contentView.setHtml(content, config.baseUrl)

    def openBookPreviousChapter(self):
        if hasattr(config, "bookChapNum"):
            self.setBookConfig()
            config.bookChapNum -= 1
            if config.bookChapNum < 1:
                book = Book(config.book)
                config.bookChapNum = book.getChapterCount()
            config.bookChapter = str(config.bookChapNum)
            self.displayBookContent()

    def openBookNextChapter(self):
        if hasattr(config, "bookChapNum"):
            self.setBookConfig()
            book = Book(config.book)
            if config.bookChapNum < book.getChapterCount():
                config.bookChapNum += 1
            else:
                config.bookChapNum = 1
            config.bookChapter = str(config.bookChapNum)
            self.displayBookContent()

    def openOnMainWindow(self):
        # command examples, BOOK:::Graphics_Barry7_Doctrinal:::5. The Process of Theology
        if config.book and config.bookChapter:
            command = "BOOK:::{0}:::{1}".format(config.book, config.bookChapter)
            config.mainWindow.runTextCommand(command)


databaseFile = os.path.join(config.marvelData, "books", "Maps_ABS.book")
if os.path.isfile(databaseFile):
    config.mainWindow.referenceBooks = ReferenceBooks(config.mainWindow)
    config.mainWindow.referenceBooks.show()
else:
    databaseInfo = ((config.marvelData, "books", "Maps_ABS.book"), "13hf1NvhAjNXmRQn-Cpq4hY0E2XbEfmEd")
    config.mainWindow.downloadHelper(databaseInfo)
