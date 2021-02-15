import config
from PySide2.QtCore import QStringListModel
#from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtWidgets import (QLabel, QPushButton, QListView, QAbstractItemView, QGroupBox, QGridLayout, QHBoxLayout, QVBoxLayout, QWidget)
from ToolsSqlite import Book
from gui.HighlightLauncher import HighlightLauncher

class MiscellaneousLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        # set title
        self.setWindowTitle(config.thisTranslation["cp4"])
        # set up variables
        self.parent = parent
        # setup interface
        self.setupUI()

    def setupUI(self):
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(HighlightLauncher(self))
        mainLayout.addWidget(QLabel("testing"))
        self.setLayout(mainLayout)


