from pathlib import Path

from PyQt5.QtWidgets import QCheckBox

import config, platform, webbrowser, os
from qtpy.QtCore import Qt
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QMessageBox

from util.BibleBooks import BibleBooks
from util.FileUtil import FileUtil


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
        self.catalog = []
        self.catalogData = {}
        self.loadCatalog()

    def setupUI(self):
        mainLayout = QVBoxLayout()

        filterLayout = QHBoxLayout()
        filterLayout.addWidget(QLabel(config.thisTranslation["menu5_search"]))
        self.filterEntry = QLineEdit()
        self.filterEntry.textChanged.connect(self.resetItems)
        filterLayout.addWidget(self.filterEntry)
        mainLayout.addLayout(filterLayout)

        typesLayout = QHBoxLayout()
        self.pdfCheckbox = QCheckBox("PDF")
        self.pdfCheckbox.setChecked(True)
        self.pdfCheckbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.pdfCheckbox)
        self.mp3Checkbox = QCheckBox("MP3")
        self.mp3Checkbox.setChecked(True)
        self.mp3Checkbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.mp3Checkbox)
        self.mp4Checkbox = QCheckBox("MP4")
        self.mp4Checkbox.setChecked(True)
        self.mp4Checkbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.mp4Checkbox)
        self.bookCheckbox = QCheckBox("BOOK")
        self.bookCheckbox.setChecked(True)
        self.bookCheckbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.bookCheckbox)
        self.docxCheckbox = QCheckBox("DOCX")
        self.docxCheckbox.setChecked(True)
        self.docxCheckbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.docxCheckbox)
        self.commCheckbox = QCheckBox("COMM")
        self.commCheckbox.setChecked(True)
        self.commCheckbox.stateChanged.connect(self.resetItems)
        typesLayout.addWidget(self.commCheckbox)
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
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(self.open)
        buttonLayout.addWidget(button)
        # button = QPushButton(config.thisTranslation["download"])
        # button.clicked.connect(self.download)
        # buttonLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["close"])
        button.clicked.connect(self.close)
        buttonLayout.addWidget(button)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def getCatalogItems(self):
        data = {}
        pdfCount = 0
        mp3Count = 0
        mp4Count = 0
        bookCount = 0
        docxCount = 0
        commCount = 0
        lexCount = 0
        for filename, type, directory, file, description, repo, installDirectory in self.catalog:
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
            data[id] = [id, filename, type, directory, file, description, repo, installDirectory]
        return data

    def resetItems(self):
        self.isUpdating = True
        self.dataViewModel.clear()
        self.catalogData = self.getCatalogItems()
        filterEntry = self.filterEntry.text().lower()
        rowCount = 0
        colCount = 0
        for id, value in self.catalogData.items():
            id2, filename, type, directory, file, description, repo, installDirectory = value
            if (filterEntry == "" or filterEntry in filename.lower() or filterEntry in description.lower()):
                if (not self.pdfCheckbox.isChecked() and type == "PDF") or \
                        (not self.mp3Checkbox.isChecked() and type == "MP3") or \
                        (not self.mp4Checkbox.isChecked() and type == "MP4") or \
                        (not self.bookCheckbox.isChecked() and type == "BOOK") or \
                        (not self.docxCheckbox.isChecked() and type == "DOCX") or \
                        (not self.commCheckbox.isChecked() and type == "COMM"):
                    continue
                item = QStandardItem(id)
                self.dataViewModel.setItem(rowCount, colCount, item)
                colCount += 1
                item = QStandardItem(file)
                self.dataViewModel.setItem(rowCount, colCount, item)
                colCount += 1
                item = QStandardItem(directory)
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
             config.thisTranslation["directory"],
             # config.thisTranslation["description"]
             ])
        self.dataView.resizeColumnsToContents()
        self.isUpdating = False

    def itemClicked(self, index):
        selectedRow = index.row()
        self.catalogEntryId = self.dataViewModel.item(selectedRow, 0).text()

    def displayMessage(self, message="", title="UniqueBible"):
        QMessageBox.information(self, title, message)

    def loadCatalog(self):
        self.catalog += self.loadLocalFiles("PDF", config.marvelData + "/pdf", ".pdf", "", "")
        self.catalog += self.loadLocalFiles("MP3", "music", ".mp3", "", "")
        self.catalog += self.loadLocalFiles("MP4", "video", ".mp4", "", "")
        self.catalog += self.loadLocalFiles("BOOK", config.marvelData + "/books", ".book", "", "")
        self.catalog += self.loadLocalFiles("DOCX", config.marvelData + "/docx", ".docx", "", "")
        self.catalog += self.loadLocalFiles("COMM", config.marvelData + "/commentaries", ".commentary", "", "")

    def loadLocalFiles(self, type, folder, extension, repo="", installFolder=""):
        data = []
        files = FileUtil.getAllFilesWithExtension(folder, extension)
        for file in files:
            path = os.path.dirname(file)
            filename = os.path.basename(file)
            data.append((file, type, path, filename, folder, repo, installFolder))
        return data

    def download(self):
        pass

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
        item = self.catalogData[self.catalogEntryId]
        id, filename, type, directory, file, description, repo, installDirectory = item
        directory = self.fixDirectory(directory, type)
        command = ""
        if type == "PDF":
            command = "PDF:::{0}{1}".format(directory, file)
        elif type == "MP3":
            command = "VLC:::{0}{1}".format(directory, file)
        elif type == "MP4":
            command = "VLC:::{0}{1}".format(directory, file)
        elif type == "BOOK":
            if file.endswith(".book"):
                file = file.replace(".book", "")
            config.booksFolder = directory
            command = "BOOK:::{0}".format(file)
        elif type == "COMM":
            file = file.replace(".commentary", "")
            file = file[1:]
            config.commentariesFolder = directory
            command = "COMMENTARY:::{0}:::{1} {2}".format(file, BibleBooks.eng[str(config.mainB)][0], config.mainC)
        print(command)
        self.parent.runTextCommand(command)


## Standalone development code

class DummyParent():
    def runTextCommand(self, command):
        print(command)

    def verseReference(self, command):
        return ['', '']

if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QApplication
    from qtpy.QtCore import QCoreApplication
    from util.ConfigUtil import ConfigUtil
    from util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.noQt = False
    config.bibleCollections["Custom"] = ['ABP', 'ACV']
    config.bibleCollections["King James"] = ['KJV', 'KJVx', 'KJVA', 'KJV1611', 'KJV1769x']
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    dialog = LibraryCatalogDialog(DummyParent())
    dialog.exec_()