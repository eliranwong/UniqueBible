import operator
import sys

from PySide2.QtCore import QAbstractTableModel, Qt, SIGNAL

import config

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QTableView
from util.ShortcutUtil import ShortcutUtil


class DisplayShortcutsWindow(QDialog):

    def __init__(self, name, shortcuts):
        super(DisplayShortcutsWindow, self).__init__()

        self.setWindowTitle(name)
        self.setMinimumWidth(360)
        self.setMinimumHeight(500)
        self.layout = QVBoxLayout()

        table = QTableView()
        model = DisplayShortcutsModel(self, shortcuts)
        table.setModel(model)
        table.resizeColumnsToContents()
        table.setSortingEnabled(True)
        self.layout.addWidget(table)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

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
    name = "micron"
    ShortcutUtil.setup(name)
    shortcuts = ShortcutUtil.getAllShortcuts()
    window = DisplayShortcutsWindow(name, shortcuts)
    window.exec_()
    window.close()