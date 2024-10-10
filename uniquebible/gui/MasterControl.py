from uniquebible import config
import shortcut as sc
from uniquebible.gui.BibleExplorer import BibleExplorer
from uniquebible.gui.Library2Launcher import Library2Launcher
from uniquebible.gui.MediaLauncher import MediaLauncher
#from uniquebible.gui.MorphologyLauncher import MorphologyLauncher
from uniquebible.gui.SearchLauncher import SearchLauncher
from uniquebible.gui.LibraryLauncher import LibraryLauncher
from uniquebible.gui.HistoryLauncher import HistoryLauncher
from uniquebible.gui.MiscellaneousLauncher import MiscellaneousLauncher
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QMessageBox, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QTabWidget, QLineEdit, QCheckBox
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QKeySequence, QShortcut
else:
    from qtpy.QtWidgets import QMessageBox, QGridLayout, QBoxLayout, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QTabWidget, QLineEdit, QCheckBox, QShortcut
    from qtpy.QtCore import Qt, QEvent
    from qtpy.QtGui import QKeySequence


class MasterControl(QWidget):

    def __init__(self, parent, initialTab=0, b=config.mainB, c=config.mainC, v=config.mainV, text=config.mainText):
        super().__init__()

        self.isRefreshing = True

        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["controlPanel"])
        if config.restrictControlPanelWidth and config.screenWidth > config.masterControlWidth:
            self.setFixedWidth(config.masterControlWidth)
        # setup item option lists
        self.setupResourceLists()
        # setup interface
        self.text = text
        self.setupUI(b, c, v, text, initialTab)
        # setup keyboard shortcuts
        self.setupKeyboardShortcuts()
        
        self.isRefreshing = False

    def setupKeyboardShortcuts(self):
        for index, shortcut in enumerate((sc.openControlPanelTab0, sc.openControlPanelTab1, sc.openControlPanelTab2, sc.openControlPanelTab3, sc.openControlPanelTab4, sc.openControlPanelTab5, sc.openControlPanelTab6)):
            shortcut = QShortcut(QKeySequence(shortcut), self)
            shortcut.activated.connect(lambda index=index: self.tabs.setCurrentIndex(index))

    # manage key capture
    def event(self, event):
        if event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Escape:
                self.hide()
        if isinstance(event, QEvent):
            return QWidget.event(self, event)

    def closeEvent(self, event):
        # Control panel is designed for frequent use
        # Hiding it instead of closing may save time from reloading
        event.ignore()
        self.hide()

    def setupResourceLists(self):
        self.parent.setupResourceLists()
        # bible versions
        self.textList = self.parent.textList
        self.textFullNameList = self.parent.textFullNameList
        self.strongBibles =  self.parent.strongBibles
        if self.parent.versionCombo is not None and config.menuLayout in ("classic", "focus", "aleph", "material"):
            for index, fullName in enumerate(self.textFullNameList):
                self.parent.versionCombo.setItemData(index, fullName, Qt.ToolTipRole)
        # commentaries
        self.commentaryList = self.parent.commentaryList
        #self.commentaryFullNameList = [Commentary(module).commentaryInfo() for module in self.commentaryList]
        self.commentaryFullNameList = self.parent.commentaryFullNameList
        # reference book
        # menu10_dialog
        self.referenceBookList = self.parent.referenceBookList
        # topic
        # menu5_topics
        self.topicListAbb = self.parent.topicListAbb
        self.topicList = self.parent.topicList
        # lexicon
        # context1_originalLexicon
        self.lexiconList = self.parent.lexiconList
        # dictionary
        # context1_dict
        self.dictionaryListAbb = self.parent.dictionaryListAbb
        self.dictionaryList = self.parent.dictionaryList
        # encyclopedia
        # context1_encyclopedia
        self.encyclopediaListAbb = self.parent.encyclopediaListAbb
        self.encyclopediaList = self.parent.encyclopediaList
        # 3rd-party dictionary
        # menu5_3rdDict
        self.thirdPartyDictionaryList = self.parent.thirdPartyDictionaryList
        # pdf list
        self.pdfList = self.parent.pdfList
        # docx list
        self.docxList = self.parent.docxList

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
        subLayout.addWidget(self.refreshButton())
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
        self.tabs.setTabToolTip(0, sc.openControlPanelTab0)
        # 1
        libraryTab1 = LibraryLauncher(self)
        self.tabs.addTab(libraryTab1, config.thisTranslation["cp1"])
        self.tabs.setTabToolTip(1, sc.openControlPanelTab1)
        # 2
        libraryTab2 = Library2Launcher(self)
        self.tabs.addTab(libraryTab2, config.thisTranslation["cp2"])
        self.tabs.setTabToolTip(2, sc.openControlPanelTab2)
        # 3
        self.toolTab = SearchLauncher(self)
        self.tabs.addTab(self.toolTab, config.thisTranslation["cp3"])
        self.tabs.setTabToolTip(3, sc.openControlPanelTab3)
        # 4
        self.historyTab = HistoryLauncher(self)
        self.tabs.addTab(self.historyTab, config.thisTranslation["cp4"])
        self.tabs.setTabToolTip(4, sc.openControlPanelTab4)
        # 5
        self.miscellaneousTab = MiscellaneousLauncher(self)
        self.tabs.addTab(self.miscellaneousTab, config.thisTranslation["cp5"])
        self.tabs.setTabToolTip(5, sc.openControlPanelTab5)
        # 6
        mediaTab = MediaLauncher(self)
        self.tabs.addTab(mediaTab, config.thisTranslation["media"])
        self.tabs.setTabToolTip(6, sc.openControlPanelTab6)
        #7
        # Removed morphology tab temporarily until a fix
        #self.morphologyTab = MorphologyLauncher(self)
        #self.tabs.addTab(self.morphologyTab, config.thisTranslation["cp7"])
        #self.tabs.setTabToolTip(7, sc.openControlPanelTab7)

        # set action with changing tabs
        self.tabs.currentChanged.connect(self.tabChanged)
        # set initial tab
        self.tabs.setCurrentIndex(initialTab)
        return self.tabs

    def commandFieldWidget(self):
        self.commandField = QLineEdit()
        self.commandField.setCompleter(self.parent.getTextCommandSuggestion())
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

    def refreshButton(self):
        button = QPushButton()
        button.setToolTip(config.thisTranslation["reloadResources"])
        file = "material/navigation/refresh/materialiconsoutlined/48dp/2x/outline_refresh_black_48dp.png"
        icon = self.parent.getQIcon(file)
        if config.menuLayout == "material":
            button.setStyleSheet(icon)
        else:
            button.setIcon(icon)
        button.clicked.connect(lambda: self.parent.reloadResources(True))
        return button

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
            buttonLabel = config.thisTranslation.get(label, label) if translation else label
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
        if index == 4:
            self.historyTab.refresh()
        elif index == 5:
            self.miscellaneousTab.refresh()

        # set focus
        if index == 3:
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
