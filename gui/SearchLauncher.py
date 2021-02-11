import config
from gui.CheckableComboBox import CheckableComboBox
from PySide2.QtWidgets import (QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QLineEdit, QRadioButton)

class SearchLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        # set title
        self.setWindowTitle(config.thisTranslation["tools"])
        # set up variables
        self.bibleSearchModeTuple = ("SEARCH", "SHOWSEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH")
        # setup interface
        self.setupUI()

    def setupUI(self):
        mainLayout0 = QVBoxLayout()
        #mainLayout0.setSpacing(5)
        mainLayout0.addWidget(self.searchFieldWidget())
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.column1Widget())
        mainLayout.addWidget(self.column2Widget())
        mainLayout0.addLayout(mainLayout)
        self.setLayout(mainLayout0)

    def column1Widget(self):
        widget = QWidget()

        widgetLayout0 = QVBoxLayout()
        #widgetLayout0.setSpacing(5)

        bibleWidget = QGroupBox(config.thisTranslation["bible"])
        bibleLayout = QVBoxLayout()
        bibleLayout.setSpacing(10)
        self.bibleCombo = CheckableComboBox(self.parent.textList, [config.mainText])
        bibleLayout.addLayout(self.parent.comboFeatureLayout("html_searchBible2", self.bibleCombo, lambda: self.dummyAction()))
        subLayout = QHBoxLayout()
        subLayout.setSpacing(5)
        leftGroupLayout = QVBoxLayout()
        rightGroupLayout = QVBoxLayout()
        subLayout.addLayout(leftGroupLayout)
        subLayout.addLayout(rightGroupLayout)
        for index, searchMode in enumerate(self.bibleSearchModeTuple):
            radioButton = QRadioButton(searchMode)
            radioButton.toggled.connect(lambda checked, mode=index: self.searchModeChanged(checked, mode))
            if index == config.bibleSearchMode:
                radioButton.setChecked(True)
            leftGroupLayout.addWidget(radioButton) if (index % 2 == 0) else rightGroupLayout.addWidget(radioButton)
        leftGroupLayout.addStretch()
        rightGroupLayout.addStretch()
        bibleLayout.addLayout(subLayout)
        bibleWidget.setLayout(bibleLayout)
        
        widgetLayout0.addWidget(bibleWidget)

        buttonRow1 = (
            ("menu_bookNotes", lambda: self.dummyAction()),
            ("menu_chapterNotes", lambda: self.dummyAction()),
            ("menu_verseNotes", lambda: self.dummyAction()),
        )
        buttonRow2 = (
            ("menu5_names", lambda: self.dummyAction()),
            ("menu5_characters", lambda: self.dummyAction()),
            ("menu5_locations", lambda: self.dummyAction()),
        )
        buttonRow3 = (
            ("biblePromises", lambda: self.dummyAction()),
            ("bibleHarmonies", lambda: self.dummyAction()),
        )
        widgetLayout0.addWidget(self.parent.buttonsWidget((buttonRow1, buttonRow2, buttonRow3)))

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
            config.bibleSearchMode = mode

    def searchBible(self):
        command = "{0}:::{1}:::{2}".format(self.bibleSearchModeTuple[config.bibleSearchMode], self.bibleCombo.checkItems, self.searchField.text())

    def dummyAction(self):
        print("testing")
