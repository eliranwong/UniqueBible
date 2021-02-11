import config
from gui.CheckableComboBox import CheckableComboBox
from PySide2.QtWidgets import (QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QLineEdit, QRadioButton)

class ToolsLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        # set title
        self.setWindowTitle(config.thisTranslation["tools"])
        # set up variables
        self.setupVariables()
        # setup interface
        self.setupUI()

    def setupVariables(self):
        # Bible Search Mode
        self.bibleSearchModeTuple = ("SEARCH", "SHOWSEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH")
        self.bibleSearchMode = 0

    def setupUI(self):
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.column1Widget())
        mainLayout.addWidget(self.column2Widget())
        self.setLayout(mainLayout)

    def column1Widget(self):
        widget = QWidget()

        widgetLayout0 = QVBoxLayout()
        widgetLayout0.setSpacing(10)

        widgetLayout = QVBoxLayout()
        widgetLayout.setSpacing(40)

        widgetLayout.addWidget(self.searchFieldWidget())

        bibleLayout = QVBoxLayout()
        bibleLayout.setSpacing(10)
        bibleLayout.addLayout(self.multipleSelectionLayout("html_searchBible2", lambda: self.dummyAction(), self.parent.textList, [config.mainText]))
        subLayout = QHBoxLayout()
        subLayout.setSpacing(10)
        leftGroupLayout = QVBoxLayout()
        rightGroupLayout = QVBoxLayout()
        subLayout.addLayout(leftGroupLayout)
        subLayout.addLayout(rightGroupLayout)
        for index, searchMode in enumerate(self.bibleSearchModeTuple):
            radioButton = QRadioButton(searchMode)
            radioButton.toggled.connect(lambda checked, mode=index: self.searchModeChanged(checked, mode))
            if index == self.bibleSearchMode:
                radioButton.setChecked(True)
            leftGroupLayout.addWidget(radioButton) if (index % 2 == 0) else rightGroupLayout.addWidget(radioButton)
        leftGroupLayout.addStretch()
        rightGroupLayout.addStretch()
        bibleLayout.addLayout(subLayout)
        widgetLayout.addLayout(bibleLayout)

        widgetLayout0.addLayout(widgetLayout)
        buttonRow1 = (
            ("menu5_names", lambda: self.dummyAction()),
            ("menu5_characters", lambda: self.dummyAction()),
            ("menu5_locations", lambda: self.dummyAction()),
        )
        buttonRow2 = (
            ("biblePromises", lambda: self.dummyAction()),
            ("bibleHarmonies", lambda: self.dummyAction()),
        )
        widgetLayout0.addWidget(self.parent.buttonsWidget((buttonRow1, buttonRow2)))

        widgetLayout0.addStretch()
        widget.setLayout(widgetLayout0)
        return widget

    def column2Widget(self):
        widget = QWidget()

        widgetLayout = QVBoxLayout()
        widgetLayout.setSpacing(10)

        widgetLayout.addLayout(self.multipleSelectionLayout("menu5_selectBook", lambda: self.dummyAction(), self.parent.referenceBookList, config.favouriteBooks))
        features = (
            ("menu5_topics", lambda: self.dummyAction(), self.parent.topicList, 0),
            ("menu5_lexicon", lambda: self.dummyAction(), self.parent.lexiconList, 0),
            ("context1_encyclopedia", lambda: self.dummyAction(), self.parent.encyclopediaList, 0),
            ("context1_dict", lambda: self.dummyAction(), self.parent.dictionaryList, 0),
            ("menu5_3rdDict", lambda: self.dummyAction(), self.parent.thirdPartyDictionaryList, 0),
        )
        for feature, action, items, initialIndex in features:
            widgetLayout.addLayout(self.singleSelectionLayout(feature, action, items, initialIndex))

        widget.setLayout(widgetLayout)
        return widget

    def searchFieldWidget(self):
        self.searchField = QLineEdit()
        self.searchField.setClearButtonEnabled(True)
        self.searchField.setToolTip(config.thisTranslation["menu5_searchItems"])
        self.searchField.returnPressed.connect(self.dummyAction())
        return self.searchField

    def singleSelectionLayout(self, feature, action, items, initialIndex=0):
        combo = QComboBox()
        combo.addItems(items)
        combo.setCurrentIndex(initialIndex)
        return self.parent.comboFeatureLayout(feature, combo, action)

    def multipleSelectionLayout(self, feature, action, items, initialItems=[]):
        combo = CheckableComboBox(items, initialItems)
        return self.parent.comboFeatureLayout(feature, combo, action)

    # Button actions

    def searchModeChanged(self, checked, mode):
        if checked:
            self.bibleSearchMode = mode

    def searchBible(self):
        pass

    def dummyAction(self):
        print("testing")
