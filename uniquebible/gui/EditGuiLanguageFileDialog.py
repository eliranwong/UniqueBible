import operator, sys
from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QAbstractTableModel, Qt
    from PySide6 import QtCore
    from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QTableView, QInputDialog, QLineEdit, QHBoxLayout
else:
    from qtpy.QtCore import QAbstractTableModel, Qt
    from qtpy import QtCore
    from qtpy.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QTableView, QInputDialog, QLineEdit, QHBoxLayout
from uniquebible.util.Languages import Languages
from uniquebible.util.LanguageUtil import LanguageUtil


class EditGuiLanguageFileDialog(QDialog):

    def __init__(self, parent, language):
        super(EditGuiLanguageFileDialog, self).__init__()

        self.parent = parent
        self.language = language
        self.reference = LanguageUtil.loadTranslation(config.referenceTranslation)
        targetLanguage = LanguageUtil.loadTranslation(language)
        self.languages = []
        self.toolTips = []
        # Cannot use the following two lines directly because target language file and reference file are most likely in different order
        #self.languages = [(key, value.replace("\n", "\\n")) for key, value in targetLanguage.items()]
        #self.toolTips = [(value.replace("\n", "\\n"), value.replace("\n", "\\n")) for value in self.reference.values()]
        for key in self.reference:
            if key in targetLanguage:
                self.languages.append([key, targetLanguage[key].replace("\n", "\\n")])
                self.toolTips.append([self.reference[key].replace("\n", "\\n"), self.reference[key].replace("\n", "\\n")])

        self.setWindowTitle("Edit GUI Language File")
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        self.layout = QVBoxLayout()

        row = QHBoxLayout()
        self.filterEntry1 = QLineEdit()
        self.filterEntry1.textChanged.connect(self.filterChanged1)
        row.addWidget(self.filterEntry1)
        self.filterEntry2 = QLineEdit()
        self.filterEntry2.textChanged.connect(self.filterChanged2)
        row.addWidget(self.filterEntry2)
        self.layout.addLayout(row)

        self.table = QTableView()
        self.model = DisplayLanguagesModel(self, self.languages, self.toolTips)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.clickedRow)
        self.layout.addWidget(self.table)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.save)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def clickedRow(self, index):
        row = self.model.getRow(index.row())
        (key, value) = row
        width = len(value)
        keyDisplay = key + '\n\n' + self.reference[key] + "\n"
        newValue, ok = QInputDialog.getText(self, 'Translation', keyDisplay, QLineEdit.Normal, value)
        if ok:
            self.model.list[index.row()] = (key, newValue)
            for item in self.model.fullList:
                if item[0] == key:
                    item[1] = newValue
                    break

    def save(self):
        LanguageUtil.saveLanguageFile(self.language, self.model.fullList)
        if self.language == config.displayLanguage:
            if self.parent is not None:
                for item in self.model.fullList:
                    key = item[0]
                    newValue = item[1]
                    config.thisTranslation[key] = newValue
                self.parent.setupMenuLayout(config.menuLayout)
                self.parent.reloadControlPanel(False)

    def filterChanged1(self, text):
        self.model.filter(0, text)
        self.filterEntry2.setText("")

    def filterChanged2(self, text):
        self.model.filter(1, text)
        self.filterEntry1.setText("")

class DisplayLanguagesModel(QAbstractTableModel):

    def __init__(self, parent, data, toolTips, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.fullList = data
        self.list = data
        self.fullToolTips = toolTips
        self.toolTips = toolTips
        self.header = ['key', Languages.decode(parent.language)]
        self.col = 0
        self.order = None

    def filter(self, col, text):
        newList = []
        newToolTipList = []
        for itemIndex, item in enumerate(self.fullList):
            if text.lower() in item[col].lower() or text.lower() in self.fullToolTips[itemIndex][col].lower():
                newList.append(item)
                newToolTipList.append(self.fullToolTips[itemIndex])
        self.list = newList
        self.toolTips = newToolTipList
        self.sort(self.col, self.order)

    def rowCount(self, parent):
        return len(self.list)

    def columnCount(self, parent):
        if len(self.list) == 0:
            return 0
        else:
            return len(self.list[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == Qt.ToolTipRole:
            return self.toolTips[index.row()][index.column()]
        elif role != Qt.DisplayRole:
            return None
        return self.list[index.row()][index.column()]

    def getRow(self, row):
        return self.list[row]

    def setRow(self, row, data):
        self.list[row] = data

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        self.layoutAboutToBeChanged.emit()
        self.col = col
        self.order = order
        self.list = sorted(self.list, key=operator.itemgetter(col))
        #self.toolTips = sorted(self.toolTips, key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.list.reverse()
            #self.toolTips.reverse()
        self.toolTips = [self.fullToolTips[self.fullList.index(i)] for i in self.list]
        self.layoutChanged.emit()

if __name__ == '__main__':
    LanguageUtil.loadTranslation("en_US")
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = EditGuiLanguageFileDialog(None, "zh_HANS")
    window.exec_()
    window.close()
