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
        mainLayout = QGridLayout()
        self.highLightLauncher = HighlightLauncher(self)
        mainLayout.addWidget(self.highLightLauncher, 0, 0, 1, 2)
        mainLayout.addWidget(QLabel(""), 0, 2, 1, 1)
        #mainLayout.setColumnStretch(2, 1)
        self.setLayout(mainLayout)

    def refresh(self):
        self.highLightLauncher.refresh()
