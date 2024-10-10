import os

from uniquebible import config
from uniquebible.gui.CheckableComboBox import CheckableComboBox
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.util.BibleBooks import BibleBooks

if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import QMessageBox
    from PySide6.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
    from PySide6.QtWidgets import QFileDialog
    from PySide6.QtWidgets import QDialogButtonBox
    from PySide6.QtWidgets import QRadioButton
else:
    from qtpy.QtCore import Qt
    from qtpy.QtGui import QStandardItemModel, QStandardItem
    from qtpy.QtWidgets import QMessageBox
    from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
    from qtpy.QtWidgets import QFileDialog
    from qtpy.QtWidgets import QDialogButtonBox
    from qtpy.QtWidgets import QRadioButton
from uniquebible.db.LiveFilterSqlite import LiveFilterSqlite
from uniquebible.gui.MultiLineInputDialog import MultiLineInputDialog


class LiveFilterDialog(QDialog):

    JS_HIDE = """
            count = 0;
            searchResultCount = document.getElementById("searchResultCount");
            divs = document.querySelectorAll("div");
            for (var i = 0, len = divs.length; i < len; i++) {{
                div = divs[i];
                div.hidden = {0};
                count++;
            }};
            if (searchResultCount) {{
                searchResultCount.innerHTML = count;
            }}
            """

    JS_SHOW = """
            wordSets = [{0}];
            count = 0;
            searchResultCount = document.getElementById("searchResultCount");
            divs = document.querySelectorAll("div");
            for (var i=0, len=divs.length; i < len; i++) {{
                div = divs[i];
                var found = true;
                for (var j=0, len2=wordSets.length; j < len2; j++) {{
                    wordSet = wordSets[j];
                    var regex;
                    if (wordSet.startsWith("'")) {{
                        wordSet = wordSet.replace("'", "");
                        wordSet = wordSet.replace("'", "");
                        regex = new RegExp(wordSet);
                    }} else {{
                        regex = new RegExp(wordSet, "i");
                    }}
                    found &= regex.test(div.innerHTML);
                }}
                if (found) {{
                    div.hidden = false;
                    count++;
                }}
            }};
            if (searchResultCount) {{
                searchResultCount.innerHTML = count;
            }}
            """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["liveFilter"])
        self.setMinimumSize(400, 400)
        self.selectedFilter = None
        self.selectedPattern = None
        self.settingBibles = False
        self.db = LiveFilterSqlite()
        self.filters = None
        self.saveReadFormattedBibles = config.readFormattedBibles
        if config.readFormattedBibles:
            self.parent.disableBiblesInParagraphs()
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel(config.thisTranslation["liveFilter"])
        mainLayout.addWidget(title)

        booksLayout = QHBoxLayout()

        bibleVerseParser = BibleVerseParser(config.parserStandarisation)
        bookNo2Abb = bibleVerseParser.standardAbbreviation
        bookNoList = [i + 1 for i in range(66)]
        ontNameList = []
        self.otNameList = []
        self.ntNameList = []
        for b in bookNoList:
            bookNameAbb = bookNo2Abb[str(b)]
            if b < 40:
                self.otNameList.append(bookNameAbb)
            else:
                self.ntNameList.append(bookNameAbb)
            ontNameList.append(bookNameAbb)

        self.bookFilterCombo = CheckableComboBox(ontNameList, config.liveFilterBookFilter)
        self.bookFilterCombo.checkFromList(config.liveFilterBookFilter)
        self.bookFilterCombo.editTextChanged.connect(self.filterSelectionChanged)
        booksLayout.addWidget(self.bookFilterCombo)

        radioButton = QRadioButton(config.thisTranslation["clear"])
        radioButton.setToolTip(config.thisTranslation["noBookFilter"])
        radioButton.toggled.connect(lambda checked: self.filterBookChanged(checked, "clear"))
        #radioButton.setChecked(True)
        booksLayout.addWidget(radioButton)

        radioButton = QRadioButton(config.thisTranslation["ot"])
        radioButton.setToolTip(config.thisTranslation["filterOTBooks"])
        radioButton.toggled.connect(lambda checked: self.filterBookChanged(checked, "ot"))
        booksLayout.addWidget(radioButton)

        radioButton = QRadioButton(config.thisTranslation["nt"])
        radioButton.setToolTip(config.thisTranslation["filterNTBooks"])
        radioButton.toggled.connect(lambda checked: self.filterBookChanged(checked, "nt"))
        booksLayout.addWidget(radioButton)

        mainLayout.addLayout(booksLayout)

        self.filtersTable = QTableView()
        self.filtersTable.setEnabled(True)
        self.filtersTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.filtersTable.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.filtersTable)
        self.filtersTable.setModel(self.dataViewModel)
        self.dataViewModel.itemChanged.connect(self.filterSelectionChanged)
        self.selectionModel = self.filtersTable.selectionModel()
        self.selectionModel.selectionChanged.connect(self.handleSelection)
        mainLayout.addWidget(self.filtersTable)
        self.reloadFilters()

        buttonsLayout = QHBoxLayout()
        clearButton = QPushButton(config.thisTranslation["clear"])
        clearButton.clicked.connect(self.clearFilter)
        buttonsLayout.addWidget(clearButton)
        addButton = QPushButton(config.thisTranslation["add"])
        addButton.clicked.connect(self.addNewFilter)
        buttonsLayout.addWidget(addButton)
        removeButton = QPushButton(config.thisTranslation["remove"])
        removeButton.clicked.connect(self.removeFilter)
        buttonsLayout.addWidget(removeButton)
        editButton = QPushButton(config.thisTranslation["edit"])
        editButton.clicked.connect(self.editFilter)
        buttonsLayout.addWidget(editButton)
        mainLayout.addLayout(buttonsLayout)

        buttonsLayout = QHBoxLayout()
        importButton = QPushButton(config.thisTranslation["import"])
        importButton.clicked.connect(self.importFile)
        buttonsLayout.addWidget(importButton)
        exportButton = QPushButton(config.thisTranslation["export"])
        exportButton.clicked.connect(self.exportFile)
        buttonsLayout.addWidget(exportButton)
        buttonsLayout.addStretch()
        mainLayout.addLayout(buttonsLayout)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.close)
        self.buttonBox.rejected.connect(self.reject)
        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

    def filterBookChanged(self, checked, filter):
        if checked:
            self.bookFilterCombo.clearAll()
            bookMap = {
                "ot": self.otNameList,
                "nt": self.ntNameList,
                "clear": [],
            }
            self.bookFilterCombo.checkFromList(bookMap[filter])
            self.runFilter()

    def close(self):
        pass

    def reloadFilters(self):
        self.filters = self.db.getAll()
        self.dataViewModel.clear()
        rowCount = 0
        for name, description in self.filters:
            item = QStandardItem(name)
            item.setToolTip(name)
            item.setCheckable(True)
            self.dataViewModel.setItem(rowCount, 0, item)
            item = QStandardItem(description)
            self.dataViewModel.setItem(rowCount, 1, item)
            rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels([config.thisTranslation["filter2"],
                                                      config.thisTranslation["pattern"]])
        self.filtersTable.resizeColumnsToContents()

    def handleSelection(self, selected, deselected):
        for item in selected:
            row = item.indexes()[0].row()
            filter = self.dataViewModel.item(row, 0)
            self.selectedFilter = filter.text()
            pattern = self.dataViewModel.item(row, 1)
            self.selectedPattern = pattern.text()

    def filterSelectionChanged(self, item):
        config.liveFilterBookFilter = self.bookFilterCombo.checkItems
        try:
            numChecked = 0
            for index in range(self.dataViewModel.rowCount()):
                item = self.dataViewModel.item(index)
                if item.checkState() == Qt.Checked:
                    numChecked += 1
            if numChecked == 0 and not self.bookFilterCombo.checkItems:
                config.mainWindow.studyPage.runJavaScript(self.JS_HIDE.format("false"))
            else:
                config.mainWindow.studyPage.runJavaScript(self.JS_HIDE.format("true"))
                self.runFilter()
        except Exception as e:
            print(str(e))

    def runFilter(self):
        sets = []
        for index in range(self.dataViewModel.rowCount()):
            item = self.dataViewModel.item(index)
            if item.checkState() == Qt.Checked:
                sets.append('"{0}"'.format(self.filters[index][1]))
        if self.bookFilterCombo.checkItems:
            sets.append(self.getCustomBookListFilter())
        wordSets = ",".join(sets)
        js = self.JS_SHOW.format(wordSets)
        config.mainWindow.studyPage.runJavaScript(js)

    def getCustomBookListFilter(self):
        customList = []
        for bookAbb in self.bookFilterCombo.checkItems:
            pattern = '<ref[^<>]*?>{0} .*</ref>'.format(bookAbb.replace(".", ""))
            customList.append(pattern)
            # Include favourite version in multi-verse fetching feature.
            if not bookAbb in BibleBooks.name2number:
                bookAbb = "{0}.".format(bookAbb)
            pattern = "instantVerse:::[^:]+?:::{0}\\\.".format(BibleBooks.name2number[bookAbb])
            customList.append(pattern)
        return '"{}"'.format("|".join(customList))

    def addNewFilter(self):
        fields = [(config.thisTranslation["filter2"], ""),
                  (config.thisTranslation["pattern"], "")]
        dialog = MultiLineInputDialog("New Filter", fields)
        if dialog.exec():
            data = dialog.getInputs()
            self.db.insert(data[0], data[1])
            self.reloadFilters()

    def removeFilter(self):
        reply = QMessageBox.question(self, "Delete",
                                     'Delete {0} {1}'.format(self.selectedFilter, config.thisTranslation["filter2"]),
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete(self.selectedFilter)
            self.reloadFilters()

    def editFilter(self):
        fields = [(config.thisTranslation["filter2"], self.selectedFilter),
                  (config.thisTranslation["pattern"], self.selectedPattern)]
        dialog = MultiLineInputDialog("Edit Filter", fields)
        if dialog.exec():
            data = dialog.getInputs()
            self.db.delete(self.selectedFilter)
            self.db.insert(data[0], data[1])
            self.reloadFilters()

    def clearFilter(self):
        for index in range(self.dataViewModel.rowCount()):
            item = self.dataViewModel.item(index)
            item.setCheckState(Qt.CheckState.Unchecked)
        self.runFilter()

    def importFile(self):
        options = QFileDialog.Options()
        filename, filtr = QFileDialog.getOpenFileName(self,
                                                      config.thisTranslation["import"],
                                                      config.thisTranslation["liveFilter"],
                                                      "File (*.filter)",
                                                      "", options)
        if filename:
            try:
                with open(filename, errors='ignore') as f:
                    for line in f:
                        data = line.split(":::")
                        filter = data[0].strip()
                        pattern = data[1].strip()
                        if self.db.checkFilterExists(filter):
                            self.db.delete(filter)
                        self.db.insert(filter, pattern)
            except Exception as e:
                print(e)
            self.reloadFilters()

    def exportFile(self):
        options = QFileDialog.Options()
        fileName, *_ = QFileDialog.getSaveFileName(self,
                                           config.thisTranslation["export"],
                                           config.thisTranslation["liveFilter"],
                                           "File (*.filter)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".filter"
            data = ""
            for name, description in self.db.getAll():
                data += f"{name}:::{description}\n"
            f = open(fileName, "w", encoding="utf-8")
            f.write(data)
            f.close()


class Dummy:

    def __init__(self):
        pass

    def disableBiblesInParagraphs(self):
        pass

if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QApplication
    from qtpy.QtCore import QCoreApplication
    from uniquebible.util.ConfigUtil import ConfigUtil
    from uniquebible.util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.noQt = False
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    dialog = LiveFilterDialog(Dummy())
    dialog.exec_()