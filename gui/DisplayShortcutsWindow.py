import operator
import sys

from PySide2.QtCore import QAbstractTableModel, Qt, SIGNAL

import config

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QTableView, QInputDialog, QLineEdit
from util.ShortcutUtil import ShortcutUtil


class DisplayShortcutsWindow(QDialog):

    def __init__(self, name, shortcuts):
        super(DisplayShortcutsWindow, self).__init__()

        self.name = name
        self.setWindowTitle(name)
        self.setMinimumWidth(360)
        self.setMinimumHeight(500)
        self.layout = QVBoxLayout()

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
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.saveShortcut)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.rejected.connect(self.canceled)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def clickedRow(self, index):
        row = self.model.getRow(index.row())
        (key, action) = row
        newKey, ok = QInputDialog.getText(self, 'Shortcut', action, QLineEdit.Normal, key)
        if ok:
            self.model.list[index.row()] = (newKey, action)

    def saveShortcut(self):
        if self.name not in ShortcutUtil.data.keys():
            ShortcutUtil.createShortcutFile(self.name, self.model.list)

    def canceled(self):
        if self.name not in ShortcutUtil.data.keys():
            ShortcutUtil.loadShortcutFile(self.name)

class DisplayShortcutsModel(QAbstractTableModel):

    def __init__(self, parent, list, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.list = list
        self.header = header = ['Keys', 'Action']

    def rowCount(self, parent):
        return len(self.list)

    def columnCount(self, parent):
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
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.list = sorted(self.list, key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.list.reverse()
        self.emit(SIGNAL("layoutChanged()"))

if __name__ == '__main__':
    from Languages import Languages
    config.thisTranslation = Languages.translation
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    name = "test1"
    ShortcutUtil.setup(name)
    shortcuts = ShortcutUtil.getAllShortcuts()
    window = DisplayShortcutsWindow(name, shortcuts)
    window.exec_()
    window.close()