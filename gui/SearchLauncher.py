import config
from gui.CheckableComboBox import CheckableComboBox
from PySide2.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QLineEdit, QRadioButton, QCheckBox

class SearchLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        # set title
        self.setWindowTitle(config.thisTranslation["tools"])
        # set up variables
        self.bibleSearchModeTuple = ("SEARCH", "SHOWSEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
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
        self.searchField.clear()

    def column1Widget(self):
        widget = QWidget()

        widgetLayout0 = QVBoxLayout()
        #widgetLayout0.setSpacing(5)

        bibleWidget = QGroupBox(config.thisTranslation["bible"])
        bibleLayout = QVBoxLayout()
        bibleLayout.setSpacing(10)
        self.bibleCombo = CheckableComboBox(self.parent.textList, [config.mainText])
        bibleLayout.addLayout(self.parent.comboFeatureLayout("html_searchBible2", self.bibleCombo, self.searchBible))
        subLayout = QHBoxLayout()
        subLayout.setSpacing(5)
        leftGroupLayout = QVBoxLayout()
        rightGroupLayout = QVBoxLayout()
        subLayout.addLayout(leftGroupLayout)
        subLayout.addLayout(rightGroupLayout)
        for index, searchMode in enumerate(self.bibleSearchModeTuple):
            radioButton = QRadioButton(searchMode)
            radioButton.setToolTip(config.thisTranslation["searchRB{0}".format(index)])
            radioButton.toggled.connect(lambda checked, mode=index: self.searchModeChanged(checked, mode))
            if index == config.bibleSearchMode:
                radioButton.setChecked(True)
            leftGroupLayout.addWidget(radioButton) if (index % 2 == 0) else rightGroupLayout.addWidget(radioButton)
        leftGroupLayout.addStretch()
        rightGroupLayout.addStretch()
        bibleLayout.addLayout(subLayout)
        bibleWidget.setLayout(bibleLayout)
        
        widgetLayout0.addWidget(bibleWidget)

        subLayout = QHBoxLayout()
        buttonRow = (
            ("menu_bookNotes", lambda: self.runSearchCommand("SEARCHBOOKNOTE")),
            ("menu_chapterNotes", lambda: self.runSearchCommand("SEARCHCHAPTERNOTE")),
            ("menu_verseNotes", lambda: self.runSearchCommand("SEARCHVERSENOTE")),
        )
        subLayout.addLayout(self.parent.buttonsLayout(buttonRow))
        #subLayout.addWidget(self.highlightNoteSearchResultCheckBox())
        #subLayout.addStretch()
        widgetLayout0.addLayout(subLayout)

        buttonRow1 = (
            ("menu5_names", lambda: self.runSearchCommand("SEARCHTOOL:::HBN")),
            ("menu5_characters", lambda: self.runSearchCommand("SEARCHTOOL:::EXLBP")),
            ("menu5_locations", lambda: self.runSearchCommand("SEARCHTOOL:::EXLBL")),
        )
        buttonRow2 = (
            ("biblePromises", lambda: self.runSearchCommand("SEARCHBOOK:::Bible_Promises")),
            ("bibleHarmonies", lambda: self.runSearchCommand("SEARCHBOOK:::Harmonies_and_Parallels")),
            ("menu5_allBook", lambda: self.runSearchCommand("SEARCHBOOK:::ALL")),
            ("favouriteBooks", lambda: self.runSearchCommand("SEARCHBOOK:::FAV")),
        )
        widgetLayout0.addWidget(self.parent.buttonsWidget((buttonRow1, buttonRow2)))

        widgetLayout0.addStretch()
        widget.setLayout(widgetLayout0)
        return widget

    def column2Widget(self):
        widget = QWidget()

        widgetLayout = QVBoxLayout()
        widgetLayout.setSpacing(10)

        subLayout = QHBoxLayout()
        self.bookCombo = CheckableComboBox(self.parent.referenceBookList, [config.book])
        subLayout.addLayout(self.parent.comboFeatureLayout("menu5_selectBook", self.bookCombo, self.searchBook))
        #checkbox = self.highlightBookSearchResultCheckBox()
        #subLayout.addWidget(checkbox)
        widgetLayout.addLayout(subLayout)

        self.topicCombo = QComboBox()
        initialTopicIndex = self.parent.topicListAbb.index(config.topic) if config.topic in self.parent.topicListAbb else 0
        self.lexiconCombo = QComboBox()
        initialLexiconIndex = self.parent.lexiconList.index(config.lexicon) if config.lexicon in self.parent.lexiconList else 0
        self.encyclopediaCombo = QComboBox()
        initialEncyclopediaIndex = self.parent.encyclopediaListAbb.index(config.encyclopedia) if config.encyclopedia in self.parent.encyclopediaListAbb else 0
        self.dictionaryCombo = QComboBox()
        initialDictionaryIndex = self.parent.dictionaryListAbb.index(config.dictionary) if config.dictionary in self.parent.dictionaryListAbb else 0
        self.thirdPartyDictionaryCombo = QComboBox()
        initialThridPartyDictionaryIndex = self.parent.thirdPartyDictionaryList.index(config.thirdDictionary) if config.thirdDictionary in self.parent.thirdPartyDictionaryList else 0
        features = (
            (self.topicCombo, "menu5_topics", lambda: self.runSearchSelection("topic"), self.parent.topicList, initialTopicIndex),
            (self.lexiconCombo, "menu5_lexicon", lambda: self.runSearchSelection("lexicon"), self.parent.lexiconList, initialLexiconIndex),
            (self.encyclopediaCombo, "context1_encyclopedia", lambda: self.runSearchSelection("encyclopedia"), self.parent.encyclopediaList, initialEncyclopediaIndex),
            (self.dictionaryCombo, "context1_dict", lambda: self.runSearchSelection("dictionary"), self.parent.dictionaryList, initialDictionaryIndex),
            (self.thirdPartyDictionaryCombo, "menu5_3rdDict", lambda: self.runSearchSelection("thirdPartyDictionary"), self.parent.thirdPartyDictionaryList, initialThridPartyDictionaryIndex),
        )
        for combo, feature, action, items, initialIndex in features:
            widgetLayout.addLayout(self.singleSelectionLayout(combo, feature, action, items, initialIndex))

        widget.setLayout(widgetLayout)
        return widget

    def searchFieldWidget(self):
        self.searchField = QLineEdit()
        self.searchField.setClearButtonEnabled(True)
        self.searchField.setToolTip(config.thisTranslation["menu5_searchItems"])
        self.searchField.returnPressed.connect(self.searchBible)
        return self.searchField

    def singleSelectionLayout(self, combo, feature, action, items, initialIndex=0):
        combo.addItems(items)
        combo.setCurrentIndex(initialIndex)
        return self.parent.comboFeatureLayout(feature, combo, action)

    def highlightNoteSearchResultCheckBox(self):
        self.searchNoteCheckbox = QCheckBox()
        self.searchNoteCheckbox.setMaximumWidth(30)
        self.searchNoteCheckbox.setToolTip(config.thisTranslation["highlightNoteSearchResult"])
        self.searchNoteCheckbox.setChecked(True if config.noteSearchString else False)
        self.searchNoteCheckbox.stateChanged.connect(self.searchNoteCheckboxChanged)
        return self.searchNoteCheckbox

    def highlightBookSearchResultCheckBox(self):
        self.searchBookCheckbox = QCheckBox()
        self.searchBookCheckbox.setMaximumWidth(30)
        self.searchBookCheckbox.setToolTip(config.thisTranslation["highlightBookSearchResult"])
        self.searchBookCheckbox.setChecked(True if config.bookSearchString else False)
        self.searchBookCheckbox.stateChanged.connect(self.searchBookCheckboxChanged)
        return self.searchBookCheckbox

    # Button actions

    def searchModeChanged(self, checked, mode):
        if checked:
            config.bibleSearchMode = mode

    def getSearchItem(self):
        searchItem = self.searchField.text()
        noItemMessage = config.thisTranslation["menu5_searchItems"]
        if not searchItem:
            self.searchField.setText(noItemMessage)
            return ""
        elif searchItem == noItemMessage:
            return ""
        else:
            return searchItem

    def searchHighlight(self, index):
        command = "SEARCHHIGHLIGHT:::hl{0}".format(index + 1)
        self.parent.runTextCommand(command)

    def searchBible(self):
        searchItem = self.getSearchItem()
        if searchItem:
            command = "{0}:::{1}:::{2}".format(self.bibleSearchModeTuple[config.bibleSearchMode], "_".join(self.bibleCombo.checkItems), self.searchField.text())
            self.parent.runTextCommand(command)

    def searchBook(self):
        searchItem = self.getSearchItem()
        if searchItem:
            self.searchBookCheckbox.setChecked(True)
            command = "{0}:::{1}:::{2}".format("SEARCHBOOK", ",".join(self.bookCombo.checkItems), self.searchField.text())
            self.parent.runTextCommand(command)

    def searchBookCheckboxChanged(self, state):
        if not state:
            config.bookSearchString = ""
            self.parent.parent.reloadCurrentRecord()
            if config.closeControlPanelAfterRunningCommand and not self.isRefreshing:
                self.parent.hide()

    def searchNoteCheckboxChanged(self, state):
        if not state:
            config.noteSearchString = ""
            self.parent.parent.reloadCurrentRecord()
            if config.closeControlPanelAfterRunningCommand and not self.parent.isRefreshing:
                self.parent.hide()

    def runSearchCommand(self, prefix):
        searchItem = self.getSearchItem()
        if searchItem:
            if prefix.endswith("NOTE"):
                self.searchNoteCheckbox.setChecked(True)
            command = "{0}:::{1}".format(prefix, self.searchField.text())
            self.parent.runTextCommand(command)

    def runSearchSelection(self, resource):
        searchItem = self.getSearchItem()
        if searchItem:
            comboDict = {
                "topic": (self.topicCombo, self.parent.topicListAbb),
                "lexicon": (self.lexiconCombo, self.parent.lexiconList),
                "encyclopedia": (self.encyclopediaCombo, self.parent.encyclopediaListAbb),
                "dictionary": (self.dictionaryCombo, self.parent.dictionaryListAbb),
                "thirdPartyDictionary": (self.thirdPartyDictionaryCombo, self.parent.thirdPartyDictionaryList),
            }
            combo, resourceList = comboDict[resource]
            selectedItem = resourceList[combo.currentIndex()]
            if resource == "lexicon":
                keyword = "LEXICON"
            elif resource == "thirdPartyDictionary":
                keyword = "SEARCHTHIRDDICTIONARY"
            else:
                keyword = "SEARCHTOOL"
            prefix = "{0}:::{1}".format(keyword, selectedItem)
            self.runSearchCommand(prefix)
