import config, re
from BiblesSqlite import BiblesSqlite
from BibleBooks import BibleBooks
from gui.BibleExplorer import BibleExplorer
from gui.ToolsLauncher import ToolsLauncher
from gui.CheckableComboBox import CheckableComboBox
from PySide2.QtWidgets import (QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QPushButton, QWidget, QComboBox, QTabWidget, QLineEdit)
from ThirdParty import ThirdPartyDictionary
from ToolsSqlite import LexiconData, BookData, IndexesSqlite
from BibleVerseParser import BibleVerseParser

class MasterControl(QWidget):

    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        # set title
        self.setWindowTitle(config.thisTranslation["remote_control"])
        # setup item option lists
        self.setupItemLists()
        # setup interface
        self.setupUI()

    def setupItemLists(self):
        # bible versions
        self.textList = BiblesSqlite().getBibleList()
        # reference book
        # menu10_dialog
        bookData = BookData()
        self.referenceBookList = [book for book, *_ in bookData.getBookList()]
        # open database
        indexes = IndexesSqlite()
        # topic
        # menu5_topics
        self.topicDict = {name: abb for abb, name in indexes.topicList}
        self.topicList = list(self.topicDict.keys())
        # lexicon
        # context1_originalLexicon
        self.lexiconList = LexiconData().lexiconList
        # dictionary
        # context1_dict
        self.dictionaryDict = {name: abb for abb, name in indexes.dictionaryList}
        self.dictionaryList = list(self.dictionaryDict.keys())
        # encyclopedia
        # context1_encyclopedia
        self.encyclopediaDict = {name: abb for abb, name in indexes.encyclopediaList}
        self.encyclopediaList = list(self.encyclopediaDict.keys())
        # 3rd-party dictionary
        # menu5_3rdDict
        self.thirdPartyDictionaryList = ThirdPartyDictionary(self.parent.textCommandParser.isThridPartyDictionary(config.thirdDictionary)).moduleList

    def setupUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.sharedWidget())
        mainLayout.addWidget(self.tabWidget())
        self.setLayout(mainLayout)

    def sharedWidget(self):
        sharedWidget = QWidget()
        sharedWidgetLayout = QVBoxLayout()
        sharedWidgetLayout.addWidget(self.commandFieldWidget())
        sharedWidget.setLayout(sharedWidgetLayout)
        return sharedWidget

    def tabWidget(self):
        self.tabs = QTabWidget()
        bibleTab = BibleExplorer(self, (config.mainB, config.mainC, config.mainV, config.mainText))
        self.tabs.addTab(bibleTab, config.thisTranslation["menu_bible"])
        toolTab = ToolsLauncher(self)
        self.tabs.addTab(toolTab, config.thisTranslation["menu5_lookup"])
        self.tabs.currentChanged.connect(self.tabChanged)
        return self.tabs

    def commandFieldWidget(self):
        self.commandField = QLineEdit()
        self.commandField.setClearButtonEnabled(True)
        self.commandField.setToolTip(config.thisTranslation["enter_command_here"])
        self.commandField.returnPressed.connect(self.dummyAction)
        return self.commandField

    # Common layout

    def buttonsWidget(self, buttonElementTupleTuple, r2l=False, translation=True):
        buttons = QWidget()
        buttonsLayouts = QVBoxLayout()
        buttonsLayouts.setSpacing(3)
        for buttonElementTuple in buttonElementTupleTuple:
            buttonsLayouts.addLayout(self.buttonsLayout(buttonElementTuple, r2l, translation))
        buttons.setLayout(buttonsLayouts)
        return buttons

    def buttonsLayout(self, buttonElementTuple, r2l=False, translation=True):
        buttonsLayout = QBoxLayout(QBoxLayout.RightToLeft if r2l else QBoxLayout.LeftToRight)
        buttonsLayout.setSpacing(5)
        for label, action in buttonElementTuple:
            buttonLabel = config.thisTranslation[label] if translation else label
            button = QPushButton(buttonLabel)
            button.clicked.connect(action)
            buttonsLayout.addWidget(button)
        return buttonsLayout

    def comboFeatureLayout(self, feature, combo, action):
        # QGridLayout: https://stackoverflow.com/questions/61451279/how-does-setcolumnstretch-and-setrowstretch-works
        layout = QGridLayout()
        layout.setSpacing(5)
        # combo
        layout.addWidget(combo, 0, 0, 1, 3)
        # button
        button = QPushButton(config.thisTranslation[feature])
        button.clicked.connect(action)
        layout.addWidget(button, 0, 3, 1, 1)
        return layout

    # Actions

    def dummyAction(self):
        print("testing")

    def runTextCommand(self, command):
        self.commandField.setText(command)
        self.parent.runTextCommand(command)

    def tabChanged(self, index):
        print(index)
