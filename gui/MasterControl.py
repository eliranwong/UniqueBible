import config
from BiblesSqlite import BiblesSqlite
from gui.BibleExplorer import BibleExplorer
from gui.ToolsLauncher import ToolsLauncher
from gui.LibraryLauncher import LibraryLauncher
from gui.HistoryLauncher import HistoryLauncher
from PySide2.QtWidgets import (QGridLayout, QBoxLayout, QVBoxLayout, QPushButton, QWidget, QTabWidget, QLineEdit)
from ThirdParty import ThirdPartyDictionary
from ToolsSqlite import Commentary, LexiconData, BookData, IndexesSqlite

class MasterControl(QWidget):

    def __init__(self, parent, initialTab=0):
        super().__init__()

        self.parent = parent

        # set title
        self.setWindowTitle(config.thisTranslation["controlPanel"])
        # setup item option lists
        self.setupItemLists()
        # setup interface
        self.setupUI(initialTab)

    def setupItemLists(self):
        # bible versions
        self.textList = BiblesSqlite().getBibleList()
        # commentaries
        self.commentaryList = Commentary().getCommentaryList()
        # reference book
        # menu10_dialog
        bookData = BookData()
        self.referenceBookList = [book for book, *_ in bookData.getBookList()]
        # open database
        indexes = IndexesSqlite()
        # topic
        # menu5_topics
        self.topicDictAbb2Name = {abb: name for abb, name in indexes.topicList}
        self.topicDict = {name: abb for abb, name in indexes.topicList}
        self.topicList = list(self.topicDict.keys())
        # lexicon
        # context1_originalLexicon
        self.lexiconList = LexiconData().lexiconList
        # dictionary
        # context1_dict
        self.dictionaryDictAbb2Name = {abb: name for abb, name in indexes.dictionaryList}
        self.dictionaryDict = {name: abb for abb, name in indexes.dictionaryList}
        self.dictionaryList = list(self.dictionaryDict.keys())
        # encyclopedia
        # context1_encyclopedia
        self.encyclopediaDictAbb2Name = {abb: name for abb, name in indexes.encyclopediaList}
        self.encyclopediaDict = {name: abb for abb, name in indexes.encyclopediaList}
        self.encyclopediaList = list(self.encyclopediaDict.keys())
        # 3rd-party dictionary
        # menu5_3rdDict
        self.thirdPartyDictionaryList = ThirdPartyDictionary(self.parent.textCommandParser.isThridPartyDictionary(config.thirdDictionary)).moduleList

    def setupUI(self, initialTab):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.sharedWidget())
        mainLayout.addWidget(self.tabWidget(initialTab))
        self.setLayout(mainLayout)

    def sharedWidget(self):
        sharedWidget = QWidget()
        sharedWidgetLayout = QVBoxLayout()
        sharedWidgetLayout.addWidget(self.commandFieldWidget())
        sharedWidget.setLayout(sharedWidgetLayout)
        return sharedWidget

    def tabWidget(self, initialTab):
        self.tabs = QTabWidget()
        # 0
        self.bibleTab = BibleExplorer(self, (config.mainB, config.mainC, config.mainV, config.mainText))
        self.tabs.addTab(self.bibleTab, config.thisTranslation["menu_bible"])
        # 1
        libraryTab = LibraryLauncher(self)
        self.tabs.addTab(libraryTab, config.thisTranslation["menu_library"])
        # 2
        self.toolTab = ToolsLauncher(self)
        self.tabs.addTab(self.toolTab, config.thisTranslation["menu5_lookup"])
        # 3
        self.historyTab = HistoryLauncher(self)
        self.tabs.addTab(self.historyTab, config.thisTranslation["menu_history"])
        # set action with changing tabs
        self.tabs.currentChanged.connect(self.tabChanged)
        # set initial tab
        self.tabs.setCurrentIndex(initialTab)
        return self.tabs

    def commandFieldWidget(self):
        self.commandField = QLineEdit()
        self.commandField.setClearButtonEnabled(True)
        self.commandField.setToolTip(config.thisTranslation["enter_command_here"])
        self.commandField.returnPressed.connect(lambda: self.parent.runTextCommand(self.commandField.text()))
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

    def runTextCommand(self, command):
        self.commandField.setText(command)
        self.parent.runTextCommand(command)

    def tabChanged(self, index):
        if index == 2:
            self.toolTab.searchField.setFocus()
        elif index == 3:
            self.historyTab.refreshHistoryRecords()
        else:
            self.commandField.setFocus()
