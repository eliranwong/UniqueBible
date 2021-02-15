import config, re
from BiblesSqlite import BiblesSqlite
from BibleBooks import BibleBooks
from gui.CheckableComboBox import CheckableComboBox
from BibleVerseParser import BibleVerseParser
from PySide2.QtWidgets import (QBoxLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QWidget, QComboBox)

class BibleExplorer(QWidget):

    def __init__(self, parent, bcvTextTuple):
        super().__init__()
        # set title
        self.setWindowTitle(config.thisTranslation["highlightEditor"])
        # setup interface
        self.setupUI()

    def setup(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel(config.thisTranslation["highlightEditorLabel"]))
        
