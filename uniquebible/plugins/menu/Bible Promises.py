from uniquebible import config
import os, apsw, re
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
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

class BiblePromises(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["biblePromises"])
        #self.setMinimumSize(830, 500)
        # get text selection
        selectedText = config.mainWindow.selectedText(config.pluginContext == "study")
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI(selectedText)
        # set initial window size
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)
        # display initial content
        if not selectedText:
            self.displayContent()

    def setupVariables(self):
        self.modules = (
            "Precious Bible Promises I",
            "Precious Bible Promises II",
            "Precious Bible Promises III",
            "Precious Bible Promises IV",
            "Take Words with You",
            "Index",
            "When you ...",
            "當你 ...",
            "当你 ...",
        )
        # Connect database
        self.database = os.path.join(config.marvelData, "collections3.sqlite")
        self.connection = apsw.Connection(self.database)
        self.cursor = self.connection.cursor()
        # Entries
        self.entries = []
        self.refreshing = False

    def setupUI(self, selectedText):
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
        self.moduleView = QComboBox()
        self.moduleView.addItems(self.modules)
        for index, tooltip in enumerate(self.modules):
            self.moduleView.setItemData(index, tooltip, Qt.ToolTipRole)
        initialIndex = config.promises
        if initialIndex < len(self.modules):
            self.moduleView.setCurrentIndex(initialIndex)
        self.moduleView.currentIndexChanged.connect(self.moduleSelected)
        self.searchEntry = QLineEdit()
        self.searchEntry.setClearButtonEnabled(True)
        self.searchEntry.setText(selectedText)
        self.searchEntry.textChanged.connect(self.filterEntry)
        entryView = QListView()
        entryView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        entryView.setWordWrap(True)
        self.entryViewModel = QStandardItemModel(entryView)
        entryView.setModel(self.entryViewModel)
        self.filterEntry()
        entryView.selectionModel().selectionChanged.connect(self.entrySelected)
        openButton = QPushButton(config.thisTranslation["html_openStudy"])
        openButton.clicked.connect(self.openOnMainWindow)
        layout000Lt.addWidget(self.moduleView)
        layout000Lt.addWidget(self.searchEntry)
        layout000Lt.addWidget(entryView)
        layout000Lt.addWidget(openButton)

        #widgets on the right
        self.searchEntryRt = QLineEdit()
        self.searchEntryRt.setClearButtonEnabled(True)
        self.searchEntryRt.textChanged.connect(self.highlightContent)
        self.contentView = WebEngineViewPopover(config.mainWindow, "main", "main", windowTitle=config.thisTranslation["biblePromises"], enableCloseAction=False)
        html = config.mainWindow.wrapHtml("<h2>{0}</h2>".format(config.thisTranslation["biblePromises"]))
        self.contentView.setHtml(html, config.baseUrl)
        layout000Rt.addWidget(self.searchEntryRt)
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
        query = "SELECT Number, Topic FROM PROMISES WHERE Tool=? ORDER BY Number"
        self.cursor.execute(query, (self.moduleView.currentIndex(),))
        self.entries = self.cursor.fetchall()
        for number, topic in self.entries:
            if searchString.lower() in topic.lower():
                topic = re.sub("<br>", "\n", topic)
                item = QStandardItem(topic)
                item.setToolTip("[{0}] {1}".format(number, topic))
                self.entryViewModel.appendRow(item)

    def entrySelected(self, selection):
        if not self.refreshing:
            # set config
            config.promises = self.moduleView.currentIndex()
            # get tool number
            index = selection[0].indexes()[0].row()
            toolTip = self.entryViewModel.item(index).toolTip()
            toolTip = re.sub("\n", "", toolTip)
            config.promisesEntry = int(re.sub("^\[([0-9]+?)\].*?$", r"\1", toolTip))
            self.displayContent()
    
    def displayContent(self):
        if config.promisesEntry:
            # fetch entry data
            query = "SELECT Topic, Passages FROM PROMISES WHERE Tool=? AND Number=?"
            self.cursor.execute(query, (config.promises, config.promisesEntry))
            entry = self.cursor.fetchone()
            if entry:
                topic, passagesString = entry
                bibleVerseParser = BibleVerseParser(config.parserStandarisation)
                biblesSqlite = BiblesSqlite()
                passages = bibleVerseParser.extractAllReferences(passagesString, tagged=True)
                html = "<h2>{0}</h2>{1}".format(topic, biblesSqlite.readMultipleVerses(config.mainText, passages))
                html = config.mainWindow.wrapHtml(html)
                self.contentView.setHtml(html, config.baseUrl)

    def openOnMainWindow(self):
        if config.promisesEntry:
            command = "_promise:::{0}.{1}".format(config.promises, config.promisesEntry)
            config.mainWindow.runTextCommand(command)


databaseFile = os.path.join(config.marvelData, "collections3.sqlite")
if os.path.isfile(databaseFile):
    config.mainWindow.biblePromises = BiblePromises(config.mainWindow)
    config.mainWindow.biblePromises.show()
else:
    databaseInfo = ((config.marvelData, "collections3.sqlite"), "18dRwEc3SL2Z6JxD1eI1Jm07oIpt9i205")
    config.mainWindow.downloadHelper(databaseInfo)
