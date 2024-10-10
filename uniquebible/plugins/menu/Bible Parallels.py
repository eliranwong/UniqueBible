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

class BibleParallels(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["bibleHarmonies"])
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
            "History of Israel I",
            "History of Israel II",
            "Gospels I",
            "Gospels II",
            "Book of Moses",
            "Samuel, Kings, Chronicles",
            "Psalms",
            "Gospels - (Mark, Matthew, Luke [ordered] + John) x 54",
            "Gospels - (Mark, Matthew, Luke [unordered]) x 14",
            "Gospels - (Mark & Matthew ONLY) x 11",
            "Gospels - (Mark, Matthew & John ONLY) x 4",
            "Gospels - (Mark & Luke ONLY) x 7",
            "Gospels - (Mathhew & Luke ONLY) x 32",
            "Gospels - (Mark ONLY) x 5",
            "Gospels - (Matthew ONLY) x 30",
            "Gospels - (Luke ONLY) x 39",
            "Gospels - (John ONLY) x 61",
            "摩西五經",
            "撒母耳記，列王紀，歷代志",
            "詩篇",
            "福音書（可，太，路〔順序〕＋ 約） x 54",
            "福音書（可，太，路〔不順序〕） x 14",
            "福音書（可，太） x 11",
            "福音書（可，太，約） x 4",
            "福音書（可，路） x 7",
            "福音書（太，路） x 32",
            "福音書（可〔獨家記載〕） x 5",
            "福音書（太〔獨家記載〕） x 30",
            "福音書（路〔獨家記載〕） x 39",
            "福音書（約〔獨家記載〕） x 61",
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
        initialIndex = config.parallels
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
        openButton = QPushButton(config.thisTranslation["html_openMain"])
        openButton.clicked.connect(self.openOnMainWindow)
        layout000Lt.addWidget(self.moduleView)
        layout000Lt.addWidget(self.searchEntry)
        layout000Lt.addWidget(entryView)
        layout000Lt.addWidget(openButton)

        #widgets on the right
        self.searchEntryRt = QLineEdit()
        self.searchEntryRt.setClearButtonEnabled(True)
        self.searchEntryRt.textChanged.connect(self.highlightContent)
        self.contentView = WebEngineViewPopover(config.mainWindow, "main", "main", windowTitle=config.thisTranslation["bibleHarmonies"], enableCloseAction=False)
        html = config.mainWindow.wrapHtml("<h2>{0}</h2>".format(config.thisTranslation["bibleHarmonies"]))
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
        query = "SELECT Number, Topic FROM PARALLEL WHERE Tool=? ORDER BY Number"
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
            config.parallels = self.moduleView.currentIndex()
            # get tool number
            index = selection[0].indexes()[0].row()
            toolTip = self.entryViewModel.item(index).toolTip()
            toolTip = re.sub("\n", "", toolTip)
            config.parallelsEntry = int(re.sub("^\[([0-9]+?)\].*?$", r"\1", toolTip))
            self.displayContent()
    
    def displayContent(self):
        if config.parallelsEntry:
            # fetch entry data
            query = "SELECT Topic, Passages FROM PARALLEL WHERE Tool=? AND Number=?"
            self.cursor.execute(query, (config.parallels, config.parallelsEntry))
            entry = self.cursor.fetchone()
            if entry:
                topic, passagesString = entry
                bibleVerseParser = BibleVerseParser(config.parserStandarisation)
                biblesSqlite = BiblesSqlite()
                passages = bibleVerseParser.extractAllReferences(passagesString, tagged=True)
                tableList = [("<th><ref onclick='document.title=\"BIBLE:::{0}\"'>{0}</ref></th>".format(bibleVerseParser.bcvToVerseReference(*passage)), "<td style='vertical-align: text-top;'>{0}</td>".format(biblesSqlite.readMultipleVerses(config.mainText, [passage], displayRef=False))) for passage in passages]
                versions, verses = zip(*tableList)
                html = "<h2>{2}</h2><table style='width:100%; table-layout:fixed;'><tr>{0}</tr><tr>{1}</tr></table>".format("".join(versions), "".join(verses), topic)
                html = config.mainWindow.wrapHtml(html)
                self.contentView.setHtml(html, config.baseUrl)

    def openOnMainWindow(self):
        if config.parallelsEntry:
            command = "_harmony:::{0}.{1}".format(config.parallels, config.parallelsEntry)
            config.mainWindow.runTextCommand(command)


databaseFile = os.path.join(config.marvelData, "collections3.sqlite")
if os.path.isfile(databaseFile):
    config.mainWindow.bibleParallels = BibleParallels(config.mainWindow)
    config.mainWindow.bibleParallels.show()
else:
    databaseInfo = ((config.marvelData, "collections3.sqlite"), "18dRwEc3SL2Z6JxD1eI1Jm07oIpt9i205")
    config.mainWindow.downloadHelper(databaseInfo)
