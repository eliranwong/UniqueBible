import config, re
from BiblesSqlite import BiblesSqlite
from BibleBooks import BibleBooks
from gui.BibleExplorer import BibleExplorer
from gui.ToolsLauncher import ToolsLauncher
from gui.CheckableComboBox import CheckableComboBox
from PySide2.QtCore import QStringListModel
from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtWidgets import (QListView, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QPushButton, QWidget, QComboBox, QTabWidget, QLineEdit)
from ThirdParty import ThirdPartyDictionary
from ToolsSqlite import Commentary, LexiconData, BookData, IndexesSqlite
from BibleVerseParser import BibleVerseParser

class LibraryLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        # set title
        self.setWindowTitle(config.thisTranslation["menu_library"])
        # set up variables
        self.parent = parent
        # setup interface
        self.setupUI()

    def setupUI(self):
        mainLayout = QHBoxLayout()

        leftLayout = QVBoxLayout()
        leftLayout.addWidget(QLabel("Commentary"))
        leftLayout.addWidget(self.commentaryListView())
        #leftLayout.addStretch()

        rightLayout = QVBoxLayout()
        rightLayout.addWidget(QLabel("Books"))
        rightLayout.addWidget(self.bookListView())
        #rightLayout.addStretch()

        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(rightLayout)
        self.setLayout(mainLayout)

    def commentaryListView(self):
        # https://doc.qt.io/archives/qtforpython-5.12/PySide2/QtCore/QStringListModel.html
        # https://gist.github.com/minoue/9f384cd36339429eb0bf
        # https://www.pythoncentral.io/pyside-pyqt-tutorial-qlistview-and-qstandarditemmodel/
        list = QListView()
        #model = QStandardItemModel(list)
        #for item in items:
        #    item = QStandardItem(item)
        #    item.setCheckable(True)
        #    model.appendRow(item)
        model = QStringListModel(self.parent.commentaryList)
        list.setModel(model)
        list.selectionModel().selectionChanged.connect(self.commentarySelected)
        return list

    def bookListView(self):
        list = QListView()
        model = QStringListModel(self.parent.referenceBookList)
        list.setModel(model)
        list.selectionModel().selectionChanged.connect(self.bookSelected)
        return list

    def commentarySelected(self, indexes):
        print(indexes[0].indexes()[0].data())

    def bookSelected(self, indexes):
        print(indexes[0].indexes()[0].data())
