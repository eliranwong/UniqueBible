import config
from BiblesSqlite import BiblesSqlite, Bible
from gui.BibleExplorer import BibleExplorer
from gui.SearchLauncher import SearchLauncher
from gui.LibraryLauncher import LibraryLauncher
from gui.HistoryLauncher import HistoryLauncher
from gui.MiscellaneousLauncher import MiscellaneousLauncher
from qtpy.QtWidgets import QMessageBox, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QTabWidget, QLineEdit, QCheckBox
from ThirdParty import ThirdPartyDictionary
from ToolsSqlite import Commentary, LexiconData, BookData, IndexesSqlite
from qtpy.QtCore import Qt, QEvent

class MasterControl(QWidget):

    def __init__(self, parent, initialTab=0, b=config.mainB, c=config.mainC, v=config.mainV, text=config.mainText):
        super().__init__()

        self.isRefreshing = True

        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["controlPanel"])
        if config.screenWidth > config.masterControlWidth:
            self.setFixedWidth(config.masterControlWidth)
        # setup item option lists
        self.setupItemLists()
        # setup interface
        self.text = text
        self.setupUI(b, c, v, text, initialTab)
        
        self.isRefreshing = False

    # manage key capture
    def event(self, event):
        if event.type() == QEvent.KeyRelease:
            if event.modifiers() == Qt.ControlModifier:
                if event.key() == Qt.Key_B:
                    self.tabs.setCurrentIndex(0)
                elif event.key() == Qt.Key_L:
                    self.tabs.setCurrentIndex(1)
                elif event.key() == Qt.Key_F:
                    self.tabs.setCurrentIndex(2)
                elif event.key() == Qt.Key_Y:
                    self.tabs.setCurrentIndex(3)
                elif event.key() == Qt.Key_M:
                    self.tabs.setCurrentIndex(4)
            elif event.key() == Qt.Key_Escape:
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
        self.textFullNameList = [Bible(text).bibleInfo() for text in self.textList]
        if self.parent.versionCombo is not None and config.menuLayout in ("focus", "Starter"):
            for index, fullName in enumerate(self.textFullNameList):
                self.parent.versionCombo.setItemData(index, fullName, Qt.ToolTipRole)
        # commentaries
        self.commentaryList = Commentary().getCommentaryList()
        #self.commentaryFullNameList = [Commentary(module).commentaryInfo() for module in self.commentaryList]
        self.commentaryFullNameList = []
        for module in self.commentaryList:
            info = Commentary(module).commentaryInfo()
            if info == "https://Marvel.Bible Commentary" and module in Commentary.marvelCommentaries:
                info = Commentary.marvelCommentaries[module]
            self.commentaryFullNameList.append(info)
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

    def updateBibleTabText(self, reference):
        self.tabs.setTabText(0, reference)

    def tabWidget(self, b, c, v, text, initialTab):
        self.tabs = QTabWidget()
        # 0
        self.bibleTab = BibleExplorer(self, (b, c, v, text))
        self.tabs.addTab(self.bibleTab, config.thisTranslation["cp0"])
        self.tabs.setTabToolTip(0, config.thisTranslation["cp0Tip"])
        # 1
        libraryTab = LibraryLauncher(self)
        self.tabs.addTab(libraryTab, config.thisTranslation["cp1"])
        self.tabs.setTabToolTip(1, config.thisTranslation["cp1Tip"])
        # 2
        self.toolTab = SearchLauncher(self)
        self.tabs.addTab(self.toolTab, config.thisTranslation["cp2"])
        self.tabs.setTabToolTip(2, config.thisTranslation["cp2Tip"])
        # 3
        self.historyTab = HistoryLauncher(self)
        self.tabs.addTab(self.historyTab, config.thisTranslation["cp3"])
        self.tabs.setTabToolTip(3, config.thisTranslation["cp3Tip"])
        # 4
        self.miscellaneousTab = MiscellaneousLauncher(self)
        self.tabs.addTab(self.miscellaneousTab, config.thisTranslation["cp4"])
        self.tabs.setTabToolTip(4, config.thisTranslation["cp4Tip"])
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

    def runTextCommand(self, command, printCommand=True, reloadMainWindow=False):
        if printCommand:
            self.commandField.setText(command)
        self.parent.textCommandLineEdit.setText(command)
        self.parent.runTextCommand(command)
        if reloadMainWindow:
            self.parent.reloadCurrentRecord()
        if config.closeControlPanelAfterRunningCommand and not self.isRefreshing:
            self.hide()

    def tabChanged(self, index):
        self.isRefreshing = True

        # refresh content
        if index == 3:
            self.historyTab.refresh()
        elif index == 4:
            self.miscellaneousTab.refresh()

        # set focus
        if index == 2:
            self.toolTab.searchField.setFocus()
            if config.contextItem:
                self.toolTab.searchField.setText(config.contextItem)
                config.contextItem = ""
            elif self.parent.mainView.currentWidget().selectedText():
                self.toolTab.searchField.setText(self.parent.mainView.currentWidget().selectedText())
            elif self.parent.studyView.currentWidget().selectedText():
                self.toolTab.searchField.setText(self.parent.studyView.currentWidget().selectedText())
        else:
            self.commandField.setFocus()

        self.isRefreshing = False

    def displayMessage(self, message="", title="UniqueBible"):
        reply = QMessageBox.information(self, title, message)
