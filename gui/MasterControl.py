import config
from BiblesSqlite import BiblesSqlite
from gui.BibleExplorer import BibleExplorer
from gui.SearchLauncher import SearchLauncher
from gui.LibraryLauncher import LibraryLauncher
from gui.HistoryLauncher import HistoryLauncher
from PySide2.QtWidgets import QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QTabWidget, QLineEdit, QCheckBox
from ThirdParty import ThirdPartyDictionary
from ToolsSqlite import Commentary, LexiconData, BookData, IndexesSqlite
import shortcut as sc
from util.ShortcutUtil import ShortcutUtil
from PySide2.QtCore import Qt, QEvent

class MasterControl(QWidget):

    def __init__(self, parent, initialTab=0, b=config.mainB, c=config.mainC, v=config.mainV, text=config.mainText):
        super().__init__()

        self.isRefreshing = True

        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["controlPanel"])
        # setup item option lists
        self.setupItemLists()
        # setup interface
        self.setupUI(b, c, v, text, initialTab)
        
        self.isRefreshing = False

    # manage key capture
    def event(self, event):
        if event.type() == QEvent.KeyRelease:
            if event.modifiers() == Qt.ControlModifier:
                if sc.masterHideKeyCode is not None and sc.masterHideKeyCode != '':
                    if event.key() == ShortcutUtil.keyCode(sc.masterHideKeyCode):
                        self.hide()
        return QWidget.event(self, event)

    def closeEvent(self, event):
        # Control panel is designed for frequent use
        # Hiding it instead of closing may save time from reloading
        event.ignore()
        self.hide()

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
        topicDictAbb2Name = {abb: name for abb, name in indexes.topicList}
        self.topicListAbb = list(topicDictAbb2Name.keys())
        topicDict = {name: abb for abb, name in indexes.topicList}
        self.topicList = list(topicDict.keys())
        # lexicon
        # context1_originalLexicon
        self.lexiconList = LexiconData().lexiconList
        # dictionary
        # context1_dict
        dictionaryDictAbb2Name = {abb: name for abb, name in indexes.dictionaryList}
        self.dictionaryListAbb = list(dictionaryDictAbb2Name.keys())
        dictionaryDict = {name: abb for abb, name in indexes.dictionaryList}
        self.dictionaryList = list(dictionaryDict.keys())
        # encyclopedia
        # context1_encyclopedia
        encyclopediaDictAbb2Name = {abb: name for abb, name in indexes.encyclopediaList}
        self.encyclopediaListAbb = list(encyclopediaDictAbb2Name.keys())
        encyclopediaDict = {name: abb for abb, name in indexes.encyclopediaList}
        self.encyclopediaList = list(encyclopediaDict.keys())
        # 3rd-party dictionary
        # menu5_3rdDict
        self.thirdPartyDictionaryList = ThirdPartyDictionary(self.parent.textCommandParser.isThridPartyDictionary(config.thirdDictionary)).moduleList

    def setupUI(self, b, c, v, text, initialTab):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.sharedWidget())
        mainLayout.addWidget(self.tabWidget(b, c, v, text, initialTab))
        self.setLayout(mainLayout)

    def sharedWidget(self):
        sharedWidget = QWidget()
        sharedWidgetLayout = QVBoxLayout()
        subLayout = QHBoxLayout()
        subLayout.addWidget(self.commandFieldWidget())
        subLayout.addWidget(self.autoCloseCheckBox())
        sharedWidgetLayout.addLayout(subLayout)
        sharedWidget.setLayout(sharedWidgetLayout)
        return sharedWidget

    def tabWidget(self, b, c, v, text, initialTab):
        self.tabs = QTabWidget()
        # 0
        self.bibleTab = BibleExplorer(self, (b, c, v, text))
        self.tabs.addTab(self.bibleTab, config.thisTranslation["menu_bible"])
        # 1
        libraryTab = LibraryLauncher(self)
        self.tabs.addTab(libraryTab, config.thisTranslation["menu_library"])
        # 2
        self.toolTab = SearchLauncher(self)
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
        self.commandField.returnPressed.connect(self.commandEntered)
        return self.commandField

    def autoCloseCheckBox(self):
        checkbox = QCheckBox()
        checkbox.setText(config.thisTranslation["autoClose"])
        checkbox.setToolTip(config.thisTranslation["autoCloseToolTip"])
        checkbox.setChecked(config.closeControlPanelAfterRunningCommand)
        checkbox.stateChanged.connect(self.closeControlPanelAfterRunningCommandChanged)
        return checkbox

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

    def closeControlPanelAfterRunningCommandChanged(self):
        config.closeControlPanelAfterRunningCommand = not config.closeControlPanelAfterRunningCommand

    def updateBCVText(self, b, c, v, text):
        self.bibleTab.updateBCVText(b, c, v, text)

    def commandEntered(self):
        command = self.commandField.text()
        self.runTextCommand(command, False)

    def runTextCommand(self, command, printCommand=True):
        if printCommand:
            self.commandField.setText(command)
        self.parent.runTextCommand(command)
        if config.closeControlPanelAfterRunningCommand and not self.isRefreshing:
            self.hide()

    def tabChanged(self, index):
        if index == 2:
            self.toolTab.searchField.setFocus()
        elif index == 3:
            self.isRefreshing = True
            self.historyTab.refreshHistoryRecords()
            self.isRefreshing = False
        else:
            self.commandField.setFocus()
