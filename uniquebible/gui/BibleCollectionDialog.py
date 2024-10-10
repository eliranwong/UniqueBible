import os
from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
    from PySide6.QtWidgets import QInputDialog
    from PySide6.QtWidgets import QRadioButton
    from PySide6.QtWidgets import QListWidget
    from PySide6.QtWidgets import QFileDialog
else:
    from qtpy.QtCore import Qt
    from qtpy.QtGui import QStandardItemModel, QStandardItem
    from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
    from qtpy.QtWidgets import QInputDialog
    from qtpy.QtWidgets import QRadioButton
    from qtpy.QtWidgets import QListWidget
    from qtpy.QtWidgets import QFileDialog


class BibleCollectionDialog(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["bibleCollections"])
        self.setMinimumSize(680, 500)
        self.setModal(True)
        self.selectedCollection = None
        self.settingBibles = False
        self.bibleNames = []
        self.bibles = self.getBibles()
        self.setupUI()
        self.parent = parent

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel(config.thisTranslation["bibleCollections"])
        mainLayout.addWidget(title)

        self.collectionsLayout = QVBoxLayout()
        self.collectionsList = QListWidget()
        self.collectionsList.setMaximumHeight(90)
        self.collectionsLayout.addWidget(self.collectionsList)
        mainLayout.addLayout(self.collectionsLayout)
        self.showListOfCollections()

        buttonsLayout = QHBoxLayout()
        addButton = QPushButton(config.thisTranslation["add"])
        addButton.clicked.connect(self.addNewCollection)
        buttonsLayout.addWidget(addButton)
        removeButton = QPushButton(config.thisTranslation["remove"])
        removeButton.clicked.connect(self.removeCollection)
        buttonsLayout.addWidget(removeButton)
        renameButton = QPushButton(config.thisTranslation["rename"])
        renameButton.clicked.connect(self.renameCollection)
        buttonsLayout.addWidget(renameButton)
        importButton = QPushButton(config.thisTranslation["import"])
        importButton.clicked.connect(self.importFile)
        buttonsLayout.addWidget(importButton)
        exportButton = QPushButton(config.thisTranslation["export"])
        exportButton.clicked.connect(self.exportFile)
        buttonsLayout.addWidget(exportButton)
        mainLayout.addLayout(buttonsLayout)

        self.biblesTable = QTableView()
        self.biblesTable.setEnabled(False)
        self.biblesTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.biblesTable.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.biblesTable)
        self.biblesTable.setModel(self.dataViewModel)
        self.loadBibleSelection()
        self.dataViewModel.itemChanged.connect(self.bibleSelectionChanged)
        mainLayout.addWidget(self.biblesTable)

        buttonLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["close"])
        button.clicked.connect(self.reloadControlPanel)
        button.clicked.connect(self.close)
        buttonLayout.addWidget(button)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def showListOfCollections(self):
        self.collectionsList.clear()
        if len(config.bibleCollections) > 0:
            for collection in sorted(config.bibleCollections.keys()):
                showBibleSelection = QRadioButton()
                showBibleSelection.setChecked(False)
                self.collectionsList.itemClicked.connect(self.selectCollection)
                self.collectionsList.addItem(collection)
        else:
            self.collectionsList.addItem("[No collection defined]")

    def addNewCollection(self):
        name, ok = QInputDialog.getText(self, 'Collection', 'Collection name:')
        if ok and len(name) > 0 and name != "All":
            config.bibleCollections[name] = {}
            self.showListOfCollections()
            self.biblesTable.setEnabled(False)

    def removeCollection(self):
        config.bibleCollections.pop(self.selectedCollection, None)
        self.showListOfCollections()
        self.biblesTable.setEnabled(False)

    def renameCollection(self):
        name, ok = QInputDialog.getText(self, 'Collection', 'Collection name:', text=self.selectedCollection)
        if ok and len(name) > 0 and name != "All":
            biblesInCollection = config.bibleCollections[self.selectedCollection]
            config.bibleCollections.pop(self.selectedCollection, None)
            self.selectedCollection = name
            config.bibleCollections[name] = biblesInCollection
            self.showListOfCollections()
            self.biblesTable.setEnabled(False)

    def getBibles(self):
        from uniquebible.db.BiblesSqlite import BiblesSqlite
        from uniquebible.db.BiblesSqlite import Bible

        self.bibleNames = BiblesSqlite().getBibleList()
        bibleInfo = []
        for bible in self.bibleNames:
            description = Bible(bible).bibleInfo()
            bibleInfo.append((bible, description))
        return bibleInfo

    def selectCollection(self, item):
        self.selectedCollection = item.text()
        self.biblesTable.setEnabled(True)
        self.loadBibleSelection()

    def bibleSelectionChanged(self, item):
        if not self.settingBibles:
            if self.selectedCollection is not None:
                text = item.text()
                biblesInCollection = config.bibleCollections[self.selectedCollection]
                if len(biblesInCollection) == 0:
                    biblesInCollection = []
                if text in biblesInCollection:
                    biblesInCollection.remove(text)
                else:
                    biblesInCollection.append(text)
                config.bibleCollections[self.selectedCollection] = biblesInCollection

    def loadBibleSelection(self):
        self.settingBibles = True
        self.dataViewModel.clear()
        biblesInCollection = []
        if self.selectedCollection is not None:
            biblesInCollection = config.bibleCollections[self.selectedCollection]
        rowCount = 0
        for bible, description in self.bibles:
            item = QStandardItem(bible)
            item.setToolTip(bible)
            item.setCheckable(True)
            if bible in biblesInCollection:
                item.setCheckState(Qt.Checked)
            self.dataViewModel.setItem(rowCount, 0, item)
            item = QStandardItem(description)
            self.dataViewModel.setItem(rowCount, 1, item)
            rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels([config.thisTranslation["bible"], config.thisTranslation["description"]])
        self.biblesTable.resizeColumnsToContents()
        self.settingBibles = False

    def reloadControlPanel(self):
        self.parent.reloadControlPanel(False)
        if config.menuLayout == "material":
            self.parent.setupMenuLayout("material")

    def importFile(self):
        options = QFileDialog.Options()
        filename, filtr = QFileDialog.getOpenFileName(self,
                                                      config.thisTranslation["import"],
                                                      config.thisTranslation["bibleCollections"],
                                                      "File (*.collection)",
                                                      "", options)
        if filename:
            try:
                with open(filename, errors='ignore') as f:
                    for line in f:
                        data = line.split(":::")
                        name = data[0].strip()
                        bibles = data[1].strip()
                        bibleCollection = []
                        for bible in bibles.split(","):
                            if bible in self.bibleNames:
                                bibleCollection.append(bible)
                        config.bibleCollections[name] = bibleCollection
            except Exception as e:
                print(e)
            self.showListOfCollections()

    def exportFile(self):
        options = QFileDialog.Options()
        fileName, *_ = QFileDialog.getSaveFileName(self,
                                           config.thisTranslation["export"],
                                           config.thisTranslation["bibleCollections"],
                                           "File (*.collection)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".collection"
            data = ""
            for name in config.bibleCollections.keys():
                bibles = ",".join(config.bibleCollections[name])
                data += f"{name}:::{bibles}\n"
            f = open(fileName, "w", encoding="utf-8")
            f.write(data)
            f.close()


class Mock:

    def __init__(self):
        pass

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
    dialog = BibleCollectionDialog(Mock())
    dialog.exec_()