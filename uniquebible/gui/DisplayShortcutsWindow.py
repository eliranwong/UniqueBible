import operator
import sys
from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QAbstractTableModel, Qt
    from PySide6 import QtCore
    from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QTableView, QInputDialog, QLineEdit
else:
    from qtpy.QtCore import QAbstractTableModel, Qt
    from qtpy import QtCore
    from qtpy.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QTableView, QInputDialog, QLineEdit
from uniquebible.util.ShortcutUtil import ShortcutUtil


class DisplayShortcutsWindow(QDialog):

    def __init__(self, name, shortcuts):
        super(DisplayShortcutsWindow, self).__init__()

        self.name = name
        self.setWindowTitle(name)
        self.setMinimumWidth(360)
        self.setMinimumHeight(500)
        self.layout = QVBoxLayout()

        self.filterEntry = QLineEdit()
        self.filterEntry.textChanged.connect(self.filterChanged)
        self.layout.addWidget(self.filterEntry)

        self.table = QTableView()
        self.model = DisplayShortcutsModel(self, shortcuts)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)
        if self.name not in ShortcutUtil.data.keys():
            self.table.doubleClicked.connect(self.clickedRow)
        self.layout.addWidget(self.table)

        if name in ShortcutUtil.data.keys():
            buttons = QDialogButtonBox.Ok
        else:
            buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.saveShortcut)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.rejected.connect(self.canceled)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def clickedRow(self, index):
        row = self.model.getRow(index.row())
        (action, key) = row
        newKey, ok = QInputDialog.getText(self, 'Shortcut', action, QLineEdit.Normal, key)
        if ok:
            self.model.list[index.row()] = (action, newKey)
            for item in self.model.fullList:
                if item[0] == action:
                    item[1] = newKey

    def saveShortcut(self):
        if self.name not in ShortcutUtil.data.keys():
            ShortcutUtil.createShortcutFile(self.name, self.model.fullList)

    def canceled(self):
        if self.name not in ShortcutUtil.data.keys():
            ShortcutUtil.loadShortcutFile(self.name)

    def filterChanged(self, text):
        self.model.filter(text)


class DisplayShortcutsModel(QAbstractTableModel):

    def __init__(self, parent, data, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.fullList = data
        self.list = data
        self.header = header = ['Action', 'Keys']
        self.col = 0
        self.order = None

    def filter(self, text):
        newList = []
        for item in self.fullList:
            if text.lower() in item[0].lower():
                newList.append(item)
        self.list = newList
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
        if order == Qt.DescendingOrder:
            self.list.reverse()
        self.layoutChanged.emit()

if __name__ == '__main__':
    from uniquebible.util.LanguageUtil import LanguageUtil

    LanguageUtil.loadTranslation("en_US")
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    shortcuts = ShortcutUtil.getAllShortcuts()
    window = DisplayShortcutsWindow("test1", shortcuts)
    window.exec_()
    window.close()