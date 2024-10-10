from uniquebible import config
import os, apsw, re
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
from uniquebible.db.ToolsSqlite import ExlbData
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

class BibleTopics(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["menu5_topics"])
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
        self.modules = config.mainWindow.topicList
        # Connect database
        self.database = os.path.join(config.marvelData, "search.sqlite")
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
            tooltip = "[{0}] {1}".format(config.mainWindow.topicListAbb[index], tooltip)
            self.moduleView.setItemData(index, tooltip, Qt.ToolTipRole)
        initialIndex = config.mainWindow.topicListAbb.index(config.topic) if config.topic in config.mainWindow.topicListAbb else 0
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
        self.contentView = WebEngineViewPopover(config.mainWindow, "main", "main", windowTitle=config.thisTranslation["menu5_topics"], enableCloseAction=False)
        html = config.mainWindow.wrapHtml("<h2>{0}</h2>".format(config.thisTranslation["menu5_topics"]))
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
        moduleIndex = self.moduleView.currentIndex()
        query = "SELECT EntryID, link FROM {0}".format(config.mainWindow.topicListAbb[moduleIndex])
        self.cursor.execute(query)
        self.entries = self.cursor.fetchall()
        for entryID, link in self.entries:
            if searchString.lower() in entryID.lower():
                item = QStandardItem(entryID)
                # link example: <ref onclick="exlbt('HIT52')">Making Wise</ref>
                tooltip = re.sub("""<ref onclick="exlbt\('(.*?)'\)">(.*?)</ref>""", r"[\1] \2", link)
                item.setToolTip(tooltip)
                self.entryViewModel.appendRow(item)

    def entrySelected(self, selection):
        if not self.refreshing:
            # set config
            moduleIndex = self.moduleView.currentIndex()
            config.topic = config.mainWindow.topicListAbb[moduleIndex]
            # get articleEntry
            index = selection[0].indexes()[0].row()
            toolTip = self.entryViewModel.item(index).toolTip()
            config.topicEntry = re.sub("^\[(.*?)\].*?$", r"\1", toolTip)
            # display
            self.displayContent()
    
    def displayContent(self):
        if config.topic and config.topicEntry:
            # fetch entry data
            exlbData = ExlbData()
            content = exlbData.getContent("exlbt", config.topicEntry)
            if config.theme in ("dark", "night"):
                content = config.mainWindow.textCommandParser.adjustDarkThemeColorsForExl(content)
            content = config.mainWindow.wrapHtml(content)
            self.contentView.setHtml(content, config.baseUrl)

    def openOnMainWindow(self):
        # command examples, EXLB:::exlbt:::HIT116
        if config.topic and config.topicEntry:
            command = "EXLB:::exlbt:::{0}".format(config.topicEntry)
            config.mainWindow.runTextCommand(command)


databaseFile = os.path.join(config.marvelData, "search.sqlite")
if os.path.isfile(databaseFile):
    databaseFile = os.path.join(config.marvelData, "data", "exlb3.data")
    if os.path.isfile(databaseFile):
        config.mainWindow.bibleTopics = BibleTopics(config.mainWindow)
        config.mainWindow.bibleTopics.show()
    else:
        databaseInfo = ((config.marvelData, "data", "exlb3.data"), "1gp2Unsab85Se-IB_tmvVZQ3JKGvXLyMP")
        config.mainWindow.downloadHelper(databaseInfo)
else:
    databaseInfo = ((config.marvelData, "search.sqlite"), "1A4s8ewpxayrVXamiva2l1y1AinAcIKAh")
    config.mainWindow.downloadHelper(databaseInfo)
