from uniquebible import config
import os, shutil, re, webbrowser
from uniquebible.db.BiblesSqlite import BiblesSqlite
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.util.FileUtil import FileUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QMessageBox, QFileDialog, QWidget, QTextEdit, QPushButton, QLabel, QListView, QAbstractItemView, QGridLayout, QHBoxLayout, QVBoxLayout, QLineEdit, QComboBox
else:
    from qtpy.QtGui import QStandardItemModel, QStandardItem
    from qtpy.QtCore import Qt
    from qtpy.QtWidgets import QMessageBox, QFileDialog, QWidget, QTextEdit, QPushButton, QLabel, QListView, QAbstractItemView, QGridLayout, QHBoxLayout, QVBoxLayout, QLineEdit, QComboBox


class BibleDataEditor(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["dataEditor"])
        self.setMinimumSize(830, 500)
        # set variables
        #self.setupVariables()
        # setup interface
        self.setupUI()

    #def setupVariables(self):
        #pass

    def setupUI(self):
        layout000 = QVBoxLayout()
        self.setLayout(layout000)

        label1 = QLabel(config.thisTranslation["name"])
        self.nameEntry = QLineEdit()
        self.nameEntry.setClearButtonEnabled(True)
        label2 = QLabel(config.thisTranslation["content"])
        self.contentEntry = QTextEdit()
        saveButton = QPushButton(config.thisTranslation["note_save"])
        saveButton.clicked.connect(self.saveAction)

        layout000.addWidget(label1)
        layout000.addWidget(self.nameEntry)
        layout000.addWidget(label2)
        layout000.addWidget(self.contentEntry)
        layout000.addWidget(saveButton)

    def saveAction(self):
        filename = self.nameEntry.text()
        content = self.contentEntry.toPlainText()
        filepath = os.path.join("plugins", "menu", "Bible_Data", "{0}.txt".format(filename))
        with open(filepath, 'w', encoding='utf8') as fileObj:
            fileObj.write(content)
        try:
            self.parent.refreshData()
        except:
            pass


class BibleData(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["bibleData"])
        self.setMinimumSize(830, 500)
        # get text selection
        selectedText = config.mainWindow.selectedText(config.pluginContext == "study")
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI(selectedText)

    def setupVariables(self):
        self.updatingData = False
        self.verseReferenceList = []
        self.resetFilenameList()
    
    def resetFilenameList(self):
        self.filenameList = [item for item in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "menu", "Bible_Data"), "txt")]

    def setupUI(self, selectedText):
        layout000 = QGridLayout()
        layout000.setColumnStretch(0, 2)
        layout000.setColumnStretch(1, 1)
        self.setLayout(layout000)
        layout001 = QVBoxLayout()
        layout000.addLayout(layout001, 0, 0)
        layout002 = QVBoxLayout()
        layout000.addLayout(layout002, 0, 1)

        #label = QLabel(config.thisTranslation["menu_data"])
        self.datasets = QComboBox()
        self.datasets.addItems(self.filenameList)
        for index, tooltip in enumerate(self.filenameList):
            self.datasets.setItemData(index, tooltip, Qt.ToolTipRole)
        if config.dataset in self.filenameList:
            self.datasets.setCurrentIndex(self.filenameList.index(config.dataset))
        self.datasets.currentIndexChanged.connect(self.filterData)
        editButton = QPushButton(config.thisTranslation["edit2"])
        editButton.clicked.connect(self.editAction)
        deleteButton = QPushButton(config.thisTranslation["remove"])
        deleteButton.clicked.connect(self.deleteAction)
        newButton = QPushButton(config.thisTranslation["new"])
        newButton.clicked.connect(self.newAction)
        importButton = QPushButton(config.thisTranslation["import"])
        importButton.clicked.connect(self.importAction)
        self.searchEntry = QLineEdit()
        self.searchEntry.setClearButtonEnabled(True)
        self.searchEntry.setText(selectedText)
        self.searchEntry.textChanged.connect(self.filterData)
        dataView = QListView()
        dataView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # Enable word wrap
        dataView.setWordWrap(True)
        #dataView.setWrapping(True)
        self.dataViewModel = QStandardItemModel(dataView)
        dataView.setModel(self.dataViewModel)
        self.filterData()
        dataView.selectionModel().selectionChanged.connect(self.dataSelected)
        wikiButton = QPushButton(config.thisTranslation["menu_wiki"])
        wikiButton.clicked.connect(lambda: webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/Bible-Data"))
        #layout001.addWidget(label)
        layout001.addWidget(self.datasets)
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(editButton)
        buttonLayout.addWidget(deleteButton)
        buttonLayout.addWidget(newButton)
        buttonLayout.addWidget(importButton)
        layout001.addLayout(buttonLayout)
        layout001.addWidget(self.searchEntry)
        layout001.addWidget(dataView)
        layout001.addWidget(wikiButton)

        self.hits = QLabel(config.thisTranslation["bibleReferences"])
        scriptureView = QListView()
        #self.scriptureView.setWordWrap(True)
        #self.scriptureView.setWrapping(True)
        scriptureView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scriptureViewModel = QStandardItemModel(scriptureView)
        scriptureView.setModel(self.scriptureViewModel)
        scriptureView.selectionModel().selectionChanged.connect(self.verseSelected)
        self.verseDisplay = QTextEdit()
        self.verseDisplay.setReadOnly(True)
        openVerseButton = QPushButton(config.thisTranslation["openNote"])
        openVerseButton.clicked.connect(self.openVerseButtonClicked)
        openAllVerseButton = QPushButton(config.thisTranslation["openAll"])
        openAllVerseButton.clicked.connect(self.openAllVerseButtonClicked)
        layout002.addWidget(self.hits)
        layout002.addWidget(scriptureView)
        layout002.addWidget(self.verseDisplay)
        layout002.addWidget(openVerseButton)
        layout002.addWidget(openAllVerseButton)

    def refreshData(self):
        self.resetFilenameList()
        self.datasets.clear()
        self.datasets.addItems(self.filenameList)
        #self.filterData()

    def editAction(self):
        filename = self.filenameList[self.datasets.currentIndex()]
        filepath = os.path.join("plugins", "menu", "Bible_Data", "{0}.txt".format(filename))
        with open(filepath, 'r', encoding='utf8') as fileObj:
            content = fileObj.read()

        config.mainWindow.bibleDataEditor = BibleDataEditor(self)
        config.mainWindow.bibleDataEditor.nameEntry.setText(filename)
        config.mainWindow.bibleDataEditor.contentEntry.setPlainText(content)
        config.mainWindow.bibleDataEditor.show()

    def confirmDeleteAction(self):
        filename = self.filenameList[self.datasets.currentIndex()]
        msgBox = QMessageBox(QMessageBox.Warning,
                     config.thisTranslation["attention"],
                     "Do you want to remove data '{0}'?".format(filename),
                     QMessageBox.NoButton, self)
        msgBox.addButton("Yes", QMessageBox.AcceptRole)
        msgBox.addButton("&No", QMessageBox.RejectRole)
        return True if msgBox.exec_() == QMessageBox.AcceptRole else False

    def deleteAction(self):
        confirm = self.confirmDeleteAction()
        if confirm:
            filename = self.filenameList[self.datasets.currentIndex()]
            filepath = os.path.join("plugins", "menu", "Bible_Data", "{0}.txt".format(filename))
            if os.path.exists(filepath):
                os.remove(filepath)
        self.refreshData()

    def newAction(self):
        config.mainWindow.bibleDataEditor = BibleDataEditor(self)
        config.mainWindow.bibleDataEditor.show()

    def importAction(self):
        options = QFileDialog.Options()
        source, *_ = QFileDialog.getOpenFileName(self,
                                                      config.thisTranslation["menu7_open"],
                                                      "",
                                                      "Plain Text Files (*.txt)",
                                                      "", options)
        if source:
            basename = os.path.basename(source)
            destination = os.path.join("plugins", "menu", "Bible_Data", basename)
            shutil.copyfile(source, destination)
            self.refreshData()

    def filterData(self):
        self.updatingData = True
        self.dataViewModel.clear()
        filename = self.filenameList[self.datasets.currentIndex()]
        filepath = os.path.join("plugins", "menu", "Bible_Data", "{0}.txt".format(filename))
        with open(filepath, 'r', encoding='utf8') as fileObj:
            dataList = fileObj.read().split("\n")
        searchString = self.searchEntry.text().strip()
        for datum in dataList:
            # Remove CLRF linebreak
            datum = re.sub("\r", "", datum)
            if datum and searchString.lower() in datum.lower():
                standardItem = QStandardItem(datum)
                standardItem.setToolTip(datum)
                self.dataViewModel.appendRow(standardItem)
        self.updatingData = False

    def dataSelected(self, selection):
        if not self.updatingData:
            try:
                index = selection[0].indexes()[0].row()
                string = self.dataViewModel.item(index).text()
                self.verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(string)

                self.hits.setText("{1} x {0}".format(len(self.verses), config.thisTranslation["bibleReferences"]))
                self.scriptureViewModel.clear()
                self.verseReferenceList = []
                parser = BibleVerseParser(config.parserStandarisation)
                for verse in self.verses:
                    verseReference = parser.bcvToVerseReference(*verse)
                    self.verseReferenceList.append(verseReference)
                    item = QStandardItem(verseReference)
                    item.setToolTip(verseReference)
                    self.scriptureViewModel.appendRow(item)
            except:
                pass

    def openVerseButtonClicked(self):
        if self.verseReference is not None:
            config.mainWindow.textCommandLineEdit.setText(self.verseReference)
            config.mainWindow.runTextCommand(self.verseReference)

    def openAllVerseButtonClicked(self):
        if self.verses:
            cmd = "; ".join(self.verseReferenceList)
            config.mainWindow.textCommandLineEdit.setText(cmd)
            config.mainWindow.runTextCommand(cmd)

    def verseSelected(self, selection):
        try:
            if self.verses is not None:
                index = selection[0].indexes()[0].row()
                self.verseReference = self.scriptureViewModel.item(index).text()
                verse = self.verses[index]
                if len(verse) == 3:
                    scripture = BiblesSqlite().readTextVerse(config.mainText, *verse)[-1]
                    showReference = "({0}) ".format(self.verseReference)
                else:
                    addFavouriteToMultiRef = config.addFavouriteToMultiRef
                    config.addFavouriteToMultiRef = False
                    scripture = BiblesSqlite().readMultipleVerses(config.mainText, [verse])
                    config.addFavouriteToMultiRef = addFavouriteToMultiRef
                    showReference = ""
                scripture = re.sub("&nbsp;|<br>", " ", scripture)
                scripture = re.sub("<[^<>]*?>|audiotrack", "", scripture)
                self.verseDisplay.setPlainText("{0}{1}".format(showReference, scripture))
        except:
            pass

config.mainWindow.bibleData = BibleData(config.mainWindow)
config.mainWindow.bibleData.show()