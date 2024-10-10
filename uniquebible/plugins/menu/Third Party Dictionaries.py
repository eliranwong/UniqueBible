from uniquebible import config
import os, apsw, re
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
from uniquebible.util.ThirdParty import ThirdPartyDictionary
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

class ThirdPartyDictionaries(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["menu5_3rdDict"])
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
        self.modules = config.mainWindow.thirdPartyDictionaryList[:-1]
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
        initialIndex = config.mainWindow.thirdPartyDictionaryList.index(config.thirdDictionary) if config.thirdDictionary in config.mainWindow.thirdPartyDictionaryList else 0
        if initialIndex < len(self.modules):
            self.moduleView.setCurrentIndex(initialIndex)
        self.moduleView.currentIndexChanged.connect(self.moduleSelected)
        self.searchEntry = QLineEdit()
        self.searchEntry.setClearButtonEnabled(True)
        self.searchEntry.setText(selectedText)
        # textChanged is slow for fetching third-party dictionary data
        #self.searchEntry.textChanged.connect(self.filterEntry)
        self.searchEntry.returnPressed.connect(self.filterEntry)
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
        self.contentView = WebEngineViewPopover(config.mainWindow, "main", "main", windowTitle=config.thisTranslation["menu5_3rdDict"], enableCloseAction=False)
        html = config.mainWindow.wrapHtml("<h2>{0}</h2>".format(config.thisTranslation["menu5_3rdDict"]))
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
        module = config.mainWindow.thirdPartyDictionaryList[self.moduleView.currentIndex()]
        module = config.mainWindow.isThridPartyDictionary(module)
        thirdPartyDictionary = ThirdPartyDictionary(module)
        self.entries = thirdPartyDictionary.getAllEntries()
        for entryID, *_ in self.entries:
            if searchString.lower() in entryID.lower():
                item = QStandardItem(entryID)
                item.setToolTip(entryID)
                self.entryViewModel.appendRow(item)

    def entrySelected(self, selection):
        if not self.refreshing:
            # set config
            moduleIndex = self.moduleView.currentIndex()
            config.thirdDictionary = config.mainWindow.thirdPartyDictionaryList[moduleIndex]
            # get articleEntry
            index = selection[0].indexes()[0].row()
            config.thirdDictionaryEntry = self.entryViewModel.item(index).toolTip()
            # display
            self.displayContent()
    
    def displayContent(self):
        if config.thirdDictionary and config.thirdDictionaryEntry:
            # fetch entry data
            config.thirdDictionary = config.mainWindow.isThridPartyDictionary(config.thirdDictionary)
            thirdPartyDictionary = ThirdPartyDictionary(config.thirdDictionary)
            content = thirdPartyDictionary.getData(config.thirdDictionaryEntry)
            content = config.mainWindow.wrapHtml(content)
            self.contentView.setHtml(content, config.baseUrl)

    def openOnMainWindow(self):
        # command examples, THIRDDICTIONARY:::wordnet:::love
        if config.thirdDictionary and config.thirdDictionaryEntry:
            command = "THIRDDICTIONARY:::{0}:::{1}".format(config.mainWindow.thirdPartyDictionaryList[self.moduleView.currentIndex()], config.thirdDictionaryEntry)
            config.mainWindow.runTextCommand(command)


config.mainWindow.thirdPartyDictionaries = ThirdPartyDictionaries(config.mainWindow)
config.mainWindow.thirdPartyDictionaries.show()
