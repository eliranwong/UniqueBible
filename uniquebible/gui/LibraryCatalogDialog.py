import pprint
import zipfile
from uniquebible import config
import os
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QRadioButton
    from PySide6.QtWidgets import QCheckBox
    from PySide6.QtWidgets import QGroupBox
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
else:
    from qtpy.QtCore import Qt
    from qtpy.QtWidgets import QRadioButton
    from qtpy.QtWidgets import QCheckBox
    from qtpy.QtWidgets import QGroupBox
    from qtpy.QtGui import QStandardItemModel, QStandardItem
    from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.CatalogUtil import CatalogUtil
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.GithubUtil import GithubUtil
from uniquebible.util.GitHubRepoCache import gitHubRepoCacheData


class LibraryCatalogDialog(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["libraryCatalog"])
        self.setMinimumSize(700, 500)
        self.setupVariables()
        self.setupUI()

    def setupVariables(self):
        self.isUpdating = False
        self.catalogEntryId = None
        self.localCatalog = CatalogUtil.loadLocalCatalog()
        self.remoteCatalog = self.getCacheData()
        self.localCatalogData = self.getLocalCatalogItems()
        self.remoteCatalogData = self.getRemoteCatalogItems()
        self.location = "local"
        self.textButtonStyle = "QPushButton {background-color: #333972; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"


    def setupUI(self):
        mainLayout = QVBoxLayout()

        filterLayout = QHBoxLayout()
        filterLayout.addWidget(QLabel(config.thisTranslation["menu5_search"]))
        self.filterEntry = QLineEdit()
        self.filterEntry.setClearButtonEnabled(True)
        self.filterEntry.textChanged.connect(self.resetItems)
        filterLayout.addWidget(self.filterEntry)
        mainLayout.addLayout(filterLayout)

        self.searchTypeBox = QGroupBox("")
        locationLayout = QHBoxLayout()
        self.localRadioButton = QRadioButton("Local")
        self.localRadioButton.setChecked(True)
        self.localRadioButton.toggled.connect(lambda: self.setLocation("local"))
        locationLayout.addWidget(self.localRadioButton)
        self.remoteRadioButton = QRadioButton("Remote")
        self.remoteRadioButton.toggled.connect(lambda: self.setLocation("remote"))
        locationLayout.addWidget( self.remoteRadioButton)
        self.searchTypeBox.setLayout(locationLayout)
        mainLayout.addWidget(self.searchTypeBox)

        typesLayout = QHBoxLayout()
        button = QPushButton("All")
        if not config.menuLayout == "material":
            button.setStyleSheet(self.textButtonStyle)
        button.clicked.connect(lambda: self.selectAllTypes(True))
        typesLayout.addWidget(button)
        button = QPushButton("None")
        if not config.menuLayout == "material":
            button.setStyleSheet(self.textButtonStyle)
        button.clicked.connect(lambda: self.selectAllTypes(False))
        typesLayout.addWidget(button)
        self.bookCheckbox = QCheckBox("BOOK")
        self.bookCheckbox.setChecked(True)
        self.bookCheckbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.bookCheckbox)
        self.pdfCheckbox = QCheckBox("PDF")
        self.pdfCheckbox.setChecked(True)
        self.pdfCheckbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.pdfCheckbox)
        self.docxCheckbox = QCheckBox("DOCX")
        self.docxCheckbox.setChecked(True)
        self.docxCheckbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.docxCheckbox)
        self.devotionalCheckbox = QCheckBox("DEVOTIONAL")
        self.devotionalCheckbox.setChecked(True)
        self.devotionalCheckbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.devotionalCheckbox)
        self.commCheckbox = QCheckBox("COMM")
        self.commCheckbox.setChecked(True)
        self.commCheckbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.commCheckbox)
        self.mp3Checkbox = QCheckBox("MP3")
        self.mp3Checkbox.setChecked(True)
        self.mp3Checkbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.mp3Checkbox)
        self.mp4Checkbox = QCheckBox("MP4")
        self.mp4Checkbox.setChecked(True)
        self.mp4Checkbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.mp4Checkbox)
        mainLayout.addLayout(typesLayout)

        self.dataView = QTableView()
        self.dataView.clicked.connect(self.itemClicked)
        self.dataView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dataView.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.dataView)
        self.dataView.setModel(self.dataViewModel)
        self.resetItems()
        mainLayout.addWidget(self.dataView)

        buttonLayout = QHBoxLayout()
        self.openButton = QPushButton(config.thisTranslation["open"])
        self.openButton.setEnabled(True)
        if not config.menuLayout == "material":
            self.openButton.setStyleSheet(self.textButtonStyle)
        self.openButton.clicked.connect(self.open)
        buttonLayout.addWidget(self.openButton)
        self.downloadButton = QPushButton(config.thisTranslation["download"])
        self.downloadButton.setEnabled(False)
        self.downloadButton.clicked.connect(self.download)
        buttonLayout.addWidget(self.downloadButton)
        button = QPushButton(config.thisTranslation["close"])
        if not config.menuLayout == "material":
            button.setStyleSheet(self.textButtonStyle)
        button.clicked.connect(self.close)
        buttonLayout.addWidget(button)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def getCacheData(self):
        cacheData = gitHubRepoCacheData
        if os.path.exists("util/GitHubCustomRepoCache.py"):
            from uniquebible.util.GitHubCustomRepoCache import gitHubCustomRepoCacheData
            cacheData += gitHubCustomRepoCacheData
        return cacheData

    def setLocation(self, location):
        self.location = location
        self.resetItems()
        if location == "local":
            self.openButton.setEnabled(True)
            if not config.menuLayout == "material":
                self.openButton.setStyleSheet(self.textButtonStyle)
            self.downloadButton.setEnabled(False)
        else:
            self.openButton.setEnabled(False)
            if not config.menuLayout == "material":
                self.openButton.setStyleSheet("")
            self.downloadButton.setEnabled(True)

    def selectAllTypes(self, value):
        self.pdfCheckbox.setChecked(value)
        self.mp3Checkbox.setChecked(value)
        self.mp4Checkbox.setChecked(value)
        self.bookCheckbox.setChecked(value)
        self.docxCheckbox.setChecked(value)
        self.devotionalCheckbox.setChecked(value)
        self.commCheckbox.setChecked(value)

    def getLocalCatalogItems(self):
        return self.getCatalogItems(self.localCatalog)

    def getRemoteCatalogItems(self):
        return self.getCatalogItems(self.remoteCatalog)

    def getCatalogItems(self, catalog):
        data = {}
        pdfCount = 0
        mp3Count = 0
        mp4Count = 0
        bookCount = 0
        docxCount = 0
        commCount = 0
        lexCount = 0
        devotionalCount = 0
        for filename, type, directory, file, description, repo, installDirectory, sha in catalog:
            id = "UNKNOWN"
            if type == "PDF":
                pdfCount += 1
                id = "{0}-{1}".format(type, pdfCount)
            elif type == "MP3":
                mp3Count += 1
                id = "{0}-{1}".format(type, mp3Count)
            elif type == "MP4":
                mp4Count += 1
                id = "{0}-{1}".format(type, mp4Count)
            elif type == "BOOK":
                bookCount += 1
                id = "{0}-{1}".format(type, bookCount)
            elif type == "DOCX":
                docxCount += 1
                id = "{0}-{1}".format(type, docxCount)
            elif type == "COMM":
                commCount += 1
                id = "{0}-{1}".format(type, commCount)
            elif type == "LEX":
                lexCount += 1
                id = "{0}-{1}".format(type, lexCount)
            elif type == "DEVOTIONAL":
                devotionalCount += 1
                id = "{0}-{1}".format(type, devotionalCount)
            data[id] = [id, filename, type, directory, file, description, repo, installDirectory, sha]
        return data

    def resetItems(self):
        self.isUpdating = True
        self.dataViewModel.clear()
        filterEntry = self.filterEntry.text().lower()
        rowCount = 0
        colCount = 0
        catalogData = self.localCatalogData
        if self.location == "remote":
            catalogData = self.remoteCatalogData
        for id, value in catalogData.items():
            id2, filename, type, directory, file, description, repo, installDirectory, sha = value
            if (filterEntry == "" or filterEntry in filename.lower() or filterEntry in description.lower()):
                if (not self.pdfCheckbox.isChecked() and type == "PDF") or \
                        (not self.mp3Checkbox.isChecked() and type == "MP3") or \
                        (not self.mp4Checkbox.isChecked() and type == "MP4") or \
                        (not self.bookCheckbox.isChecked() and type == "BOOK") or \
                        (not self.docxCheckbox.isChecked() and type == "DOCX") or \
                        (not self.devotionalCheckbox.isChecked() and type == "DEVOTIONAL") or \
                        (not self.commCheckbox.isChecked() and type == "COMM"):
                    continue
                enable = True
                if self.location == "remote":
                    installDirectory = os.path.join(config.marvelData, installDirectory)
                    if FileUtil.regexFileExists("{0}.*".format(GithubUtil.getShortname(filename)), installDirectory):
                        enable = False
                item = QStandardItem(id)
                item.setEnabled(enable)
                self.dataViewModel.setItem(rowCount, colCount, item)
                colCount += 1
                item = QStandardItem(file)
                item.setEnabled(enable)
                self.dataViewModel.setItem(rowCount, colCount, item)
                colCount += 1
                item = QStandardItem(directory)
                item.setEnabled(enable)
                self.dataViewModel.setItem(rowCount, colCount, item)
                colCount += 1
                # item = QStandardItem(description)
                # self.dataViewModel.setItem(rowCount, colCount, item)
                # colCount += 1
                # add row count
                rowCount += 1
                colCount = 0
        self.dataViewModel.setHorizontalHeaderLabels(
            ["#", config.thisTranslation["file"],
             f"{config.thisTranslation['directory']}/{config.thisTranslation['repository']}",
             # config.thisTranslation["description"]
             ])
        self.dataView.resizeColumnsToContents()
        self.isUpdating = False

    def itemClicked(self, index):
        selectedRow = index.row()
        self.catalogEntryId = self.dataViewModel.item(selectedRow, 0).text()
        if self.location == "remote":
            item = self.remoteCatalogData[self.catalogEntryId]
            id, filename, type, directory, file, description, repo, installDirectory, sha = item
            installDirectory = os.path.join(config.marvelData, installDirectory)
            if FileUtil.regexFileExists("{0}.*".format(GithubUtil.getShortname(filename)), installDirectory):
                self.downloadButton.setEnabled(False)
                if not config.menuLayout == "material":
                    self.downloadButton.setStyleSheet("")
            else:
                self.downloadButton.setEnabled(True)
                if not config.menuLayout == "material":
                    self.downloadButton.setStyleSheet(self.textButtonStyle)

    def displayMessage(self, message="", title="UniqueBible"):
        QMessageBox.information(self, title, message)

    def saveRemoteCatalogToCache(self):
        data = CatalogUtil.loadRemoteCatalog()
        with open("util/GitHubRepoCache.py", "w", encoding="utf-8") as fileObj:
            fileObj.write("gitHubRepoCacheData = {0}\n".format(pprint.pformat(data)))

    def fixDirectory(self, directory, type):
        if type == "PDF":
            directory = directory.replace(config.marvelData, "")
            directory = directory.replace("/pdf", "")
        if len(directory) > 0 and not directory.endswith("/"):
            directory += "/"
        if len(directory) > 0 and directory.startswith("/"):
            directory = directory[1:]
        return directory

    def open(self):
        item = self.localCatalogData[self.catalogEntryId]
        id, filename, type, directory, file, description, repo, installDirectory, sha = item
        directory = self.fixDirectory(directory, type)
        command = ""
        if type == "PDF":
            command = f"PDF:::{file}"
        elif type == "MP3":
            command = "MEDIA:::{0}{1}".format(directory, file)
        elif type == "MP4":
            command = "MEDIA:::{0}{1}".format(directory, file)
        elif type == "BOOK":
            if file.endswith(".book"):
                file = file.replace(".book", "")
            if not file == config.book:
                config.bookChapter = ""
                config.book = file
            config.booksFolder = directory
            self.parent.runPlugin("Reference Books")
            #command = "BOOK:::{0}".format(file)
        elif type == "COMM":
            file = file.replace(".commentary", "")
            file = file[1:]
            if not file == config.commentaryText:
                config.commentaryText = file
            config.commentariesFolder = directory
            self.parent.runPlugin("Bible Commentaries")
            #command = "COMMENTARY:::{0}:::{1} {2}".format(file, BibleBooks.abbrev["eng"][str(config.mainB)][0], config.mainC)
        elif type == "DOCX":
            command = "DOCX:::{0}".format(file)
        elif type == "DEVOTIONAL":
            file = file.replace(".devotional", "")
            command = "DEVOTIONAL:::{0}".format(file)
        if not type in ("BOOK", "COMM"):
            self.parent.runTextCommand(command)

    def download(self):
        self.downloadButton.setEnabled(False)
        if not config.menuLayout == "material":
            self.downloadButton.setStyleSheet("")
        item = self.remoteCatalogData[self.catalogEntryId]
        id, filename, type, directory, file, description, repo, installDirectory, sha = item
        github = GithubUtil(repo)
        installDirectory = os.path.join(config.marvelData, installDirectory)
        file = os.path.join(installDirectory, filename + ".zip")
        github.downloadFile(file, sha)
        with zipfile.ZipFile(file, 'r') as zipped:
            zipped.extractall(installDirectory)
        os.remove(file)
        self.displayMessage(filename + " " + config.thisTranslation["message_installed"])
        self.localCatalog = CatalogUtil.reloadLocalCatalog()
        self.localCatalogData = self.getLocalCatalogItems()
        self.resetItems()


## Standalone development code

class DummyParent():
    def runTextCommand(self, command):
        print(command)

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QCoreApplication
    from uniquebible.util.ConfigUtil import ConfigUtil
    from uniquebible.util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.noQt = False
    config.bibleCollections["Custom"] = ['ABP', 'ACV']
    config.bibleCollections["King James"] = ['KJV', 'KJVx', 'KJVA', 'KJV1611', 'KJV1769x']
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication(sys.argv)
    dialog = LibraryCatalogDialog(DummyParent())
    dialog.saveRemoteCatalogToCache()
    dialog.exec_()