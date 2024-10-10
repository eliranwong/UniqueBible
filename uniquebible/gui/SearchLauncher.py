from functools import partial
from uniquebible import config
from uniquebible.gui.CheckableComboBox import CheckableComboBox
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QLineEdit, QRadioButton, QCheckBox, QLabel, QButtonGroup
else:
    from qtpy.QtCore import Qt
    from qtpy.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QComboBox, QLineEdit, QRadioButton, QCheckBox, QLabel, QButtonGroup


class SearchLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()

        self.parent = parent

        # set title
        self.setWindowTitle(config.thisTranslation["tools"])
        # set up variables
        self.bibleSearchModeTuple = ("COUNT", "SEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH", "GPTSEARCH", "SEMANTIC")
        #config.bibleSearchRange = "clear"
        # setup interface
        self.setupUI()

    def setupUI(self):
        mainLayout0 = QVBoxLayout()
        mainLayout00 = QHBoxLayout()
        mainLayout00.addWidget(self.searchFieldWidget())
        mainLayout00.addWidget(self.caseSensitiveCheckBox())
        mainLayout0.addLayout(mainLayout00)
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.column1Widget())
        mainLayout.addWidget(self.column2Widget())
        mainLayout0.addLayout(mainLayout)
        self.setLayout(mainLayout0)
        self.searchField.clear()

    def column1Widget(self):
        widget = QWidget()

        widgetLayout0 = QVBoxLayout()

        bibleWidget = QGroupBox(config.thisTranslation["bible"])
        bibleLayout = QVBoxLayout()
        bibleLayout.setSpacing(10)
        self.bibleCombo = CheckableComboBox(self.parent.textList, [config.mainText], toolTips=self.parent.textFullNameList)
        self.bibleCombo.checkFromList([config.mainText])
        bibleLayout.addLayout(self.parent.comboFeatureLayout("html_searchBible2", self.bibleCombo, self.searchBible))

        # Bible Collections
        if len(config.bibleCollections) > 0:
            navigationLayout6 = self.navigationLayout6()
            bibleLayout.addWidget(navigationLayout6)

        subLayout = QHBoxLayout()
        subLayout.setSpacing(5)
        leftGroupLayout = QVBoxLayout()
        centerGroupLayout = QVBoxLayout()
        rightGroupLayout = QVBoxLayout()
        subLayout.addLayout(leftGroupLayout)
        subLayout.addLayout(centerGroupLayout)
        subLayout.addLayout(rightGroupLayout)
        radioButtonGroup1 = QButtonGroup()
        for index, searchMode in enumerate(self.bibleSearchModeTuple):
            radioButton = QRadioButton(searchMode)
            radioButtonGroup1.addButton(radioButton)
            radioButton.setToolTip(config.thisTranslation["searchRB{0}".format(index)])
            radioButton.toggled.connect(lambda checked, mode=index: self.searchModeChanged(checked, mode))
            if index == config.bibleSearchMode:
                radioButton.setChecked(True)
            if index % 3 == 0:
                leftGroupLayout.addWidget(radioButton)
            elif index % 3 == 1:
                centerGroupLayout.addWidget(radioButton)
            else:
                rightGroupLayout.addWidget(radioButton)
        leftGroupLayout.addStretch()
        centerGroupLayout.addStretch()
        rightGroupLayout.addStretch()
        bibleLayout.addLayout(subLayout)

        # Bible Book Filter
        filterWidget = QGroupBox("")
        booksLayout = QHBoxLayout()
        booksLayout.setSpacing(5)
        booksLayout.addWidget(QLabel("{0}:".format(config.thisTranslation["filter2"])))
        radioButtonGroup2 = QButtonGroup()
        for range, tooltip in {"clear": "noBookFilter", "ot": "filterOTBooks", "nt": "filterNTBooks", "custom": "custom"}.items():
            radioButton = QRadioButton(config.thisTranslation[range])
            radioButtonGroup2.addButton(radioButton)
            radioButton.setToolTip(config.thisTranslation[tooltip])
            radioButton.toggled.connect(lambda checked, range=range: self.booksChanged(checked, range))
            if config.bibleSearchRange == range:
                radioButton.setChecked(True)
            booksLayout.addWidget(radioButton)
            if range == "custom":
                self.customRangeRadioButton = radioButton
        self.customBooksRangeSearchField = QLineEdit()
        self.customBooksRangeSearchField.setText(config.customBooksRangeSearch)
        self.customBooksRangeSearchField.setToolTip("{0}: Psa, Matt-John, Rev".format(config.thisTranslation["forExample"]))
        self.customBooksRangeSearchField.textChanged.connect(self.customBooksRangeChanged)
        self.customBooksRangeSearchField.returnPressed.connect(self.searchBible)
        booksLayout.addWidget(self.customBooksRangeSearchField)
        filterWidget.setLayout(booksLayout)
        
        bibleLayout.addWidget(filterWidget)

        bibleWidget.setLayout(bibleLayout)
        widgetLayout0.addWidget(bibleWidget)
        

        # Books range selection

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

#        buttonRow1 = (
#            (config.favouriteBible, lambda: self.searchBible(config.favouriteBible)),
#            (config.favouriteBible2, lambda: self.searchBible(config.favouriteBible2)),
#            (config.favouriteBible3, lambda: self.searchBible(config.favouriteBible3)),
#        )
        buttonRow2 = (
            ("menu5_names", lambda: self.runSearchCommand("SEARCHTOOL:::HBN")),
            ("menu5_characters", lambda: self.runSearchCommand("SEARCHTOOL:::EXLBP")),
            ("menu5_locations", lambda: self.runSearchCommand("SEARCHTOOL:::EXLBL")),
            ("biblePromises", lambda: self.runSearchCommand("SEARCHBOOK:::Bible_Promises")),
            ("bibleHarmonies", lambda: self.runSearchCommand("SEARCHBOOK:::Harmonies_and_Parallels")),
        )
        buttonRow3 = (
            ("favouriteBooks", lambda: self.runSearchCommand("SEARCHBOOK:::FAV")),
            ("menu5_allBook", lambda: self.runSearchCommand("SEARCHBOOK:::ALL")),
            ("pdfFiles", lambda: self.runSearchCommand("SEARCHPDF")),
            ("allBooksPDF", lambda: self.runSearchCommand("SEARCHALLBOOKSPDF")),
        )
        #widgetLayout0.addWidget(self.parent.buttonsWidget((buttonRow1,), translation=False))
        widgetLayout0.addWidget(self.parent.buttonsWidget((buttonRow2, buttonRow3), translation=True))

        widgetLayout0.addStretch()
        widget.setLayout(widgetLayout0)
        return widget

    def navigationLayout6(self):
        rows = []
        row = [
            ("All", lambda: self.selectCollection("All")),
            ("None", lambda: self.selectCollection("None")),
        ]
        count = len(row)
        for collection in sorted(config.bibleCollections.keys()):
            row.append((collection, partial(self.selectCollection, collection)))
            count += 1
            if count % 6 == 0:
                rows.append(row)
                row = []
        if len(row) > 0:
            rows.append(row)
        return self.parent.buttonsWidget(rows, False, False)

    def column2Widget(self):
        maximumComboWidth = 350

        widget = QWidget()

        widgetLayout = QVBoxLayout()
        widgetLayout.setSpacing(10)

        subLayout = QHBoxLayout()
        self.bookCombo = CheckableComboBox(self.parent.referenceBookList, [config.book], toolTips=self.parent.referenceBookList)
        # Workaround display issues on macOS with PySide6
        self.bookCombo.checkFromList([config.book])
        self.bookCombo.setMaximumWidth(maximumComboWidth)
        subLayout.addLayout(self.parent.comboFeatureLayout("menu5_selectBook", self.bookCombo, self.searchBook))
        #checkbox = self.highlightBookSearchResultCheckBox()
        #subLayout.addWidget(checkbox)
        widgetLayout.addLayout(subLayout)

        self.topicCombo = QComboBox()
        self.topicCombo.setMaximumWidth(maximumComboWidth)
        initialTopicIndex = self.parent.topicListAbb.index(config.topic) if config.topic in self.parent.topicListAbb else 0
        self.lexiconCombo = QComboBox()
        self.lexiconCombo.setMaximumWidth(maximumComboWidth)
        initialLexiconIndex = self.parent.lexiconList.index(config.lexicon) if config.lexicon in self.parent.lexiconList else 0
        self.reverseLexiconCombo = QComboBox()
        self.reverseLexiconCombo.setMaximumWidth(maximumComboWidth)
        initialReverseLexiconIndex = self.parent.lexiconList.index(config.lexicon) if config.lexicon in self.parent.lexiconList else 0
        self.encyclopediaCombo = QComboBox()
        self.encyclopediaCombo.setMaximumWidth(maximumComboWidth)
        initialEncyclopediaIndex = self.parent.encyclopediaListAbb.index(config.encyclopedia) if config.encyclopedia in self.parent.encyclopediaListAbb else 0
        self.dictionaryCombo = QComboBox()
        self.dictionaryCombo.setMaximumWidth(maximumComboWidth)
        initialDictionaryIndex = self.parent.dictionaryListAbb.index(config.dictionary) if config.dictionary in self.parent.dictionaryListAbb else 0
        self.thirdPartyDictionaryCombo = QComboBox()
        self.thirdPartyDictionaryCombo.setMaximumWidth(maximumComboWidth)
        initialThridPartyDictionaryIndex = self.parent.thirdPartyDictionaryList.index(config.thirdDictionary) if config.thirdDictionary in self.parent.thirdPartyDictionaryList else 0
        self.lexiconList = self.parent.lexiconList
        self.lexiconList.append(config.thisTranslation['searchAllLexicons'])
        self.dictionaryList = self.parent.dictionaryList
        self.dictionaryList.append(config.thisTranslation['searchAllDictionaries'])
        self.dictionaryListAbb = self.parent.dictionaryListAbb
        self.dictionaryListAbb.append(config.thisTranslation['searchAllDictionaries'])
        self.thirdPartyDictionaryList = self.parent.thirdPartyDictionaryList
        self.thirdPartyDictionaryList.append(config.thisTranslation['searchAllDictionaries'])

        features = (
            (self.topicCombo, "menu5_topics", lambda: self.runSearchSelection("topic"), self.parent.topicList, initialTopicIndex),
            (self.lexiconCombo, "menu5_lexicon", lambda: self.runSearchSelection("lexicon"), self.lexiconList, initialLexiconIndex),
            (self.reverseLexiconCombo, "menu5_reverseLexicon", lambda: self.runSearchSelection("reverselexicon"), self.lexiconList, initialReverseLexiconIndex),
            (self.encyclopediaCombo, "context1_encyclopedia", lambda: self.runSearchSelection("encyclopedia"), self.parent.encyclopediaList, initialEncyclopediaIndex),
            (self.dictionaryCombo, "context1_dict", lambda: self.runSearchSelection("dictionary"), self.dictionaryList, initialDictionaryIndex),
            (self.thirdPartyDictionaryCombo, "menu5_3rdDict", lambda: self.runSearchSelection("thirdPartyDictionary"), self.thirdPartyDictionaryList, initialThridPartyDictionaryIndex),
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
        for i, item in enumerate(items):
            combo.setItemData(i, item, Qt.ToolTipRole)
        combo.setCurrentIndex(initialIndex)
        return self.parent.comboFeatureLayout(feature, combo, action)

    def caseSensitiveCheckBox(self):
        checkbox = QCheckBox()
        checkbox.setText(config.thisTranslation["caseSensitive"])
        checkbox.setToolTip(config.thisTranslation["caseSensitiveSearch"])
        checkbox.setChecked(config.enableCaseSensitiveSearch)
        checkbox.stateChanged.connect(self.caseSensitiveCheckBoxChanged)
        return checkbox

    def caseSensitiveCheckBoxChanged(self):
        config.enableCaseSensitiveSearch = not config.enableCaseSensitiveSearch

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

    def booksChanged(self, checked, range):
        if checked:
            config.bibleSearchRange = range

    def customBooksRangeChanged(self, text):
        config.customBooksRangeSearch = text
        if text:
            self.customRangeRadioButton.setChecked(True)

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

    def searchBible(self, text=""):
        searchItem = self.getSearchItem()
        if searchItem:
            text = text if text else "_".join(self.bibleCombo.checkItems)
            command = "{0}:::{1}:::{2}".format(self.bibleSearchModeTuple[config.bibleSearchMode], text, self.searchField.text())
            if config.bibleSearchRange == "custom" and config.customBooksRangeSearch:
                command += ":::{0}".format(config.customBooksRangeSearch)
            elif not config.bibleSearchRange in ("clear", "custom"):
                command += ":::{0}".format(config.bibleSearchRange)
            self.parent.runTextCommand(command)

    def searchBook(self):
        searchItem = self.getSearchItem()
        if searchItem:
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
            command = "{0}:::{1}".format(prefix, self.searchField.text())
            self.parent.runTextCommand(command)

    def runSearchSelection(self, resource):
        searchItem = self.getSearchItem()
        if searchItem:
            comboDict = {
                "topic": (self.topicCombo, self.parent.topicListAbb),
                "lexicon": (self.lexiconCombo, self.lexiconList),
                "reverselexicon": (self.reverseLexiconCombo, self.lexiconList),
                "encyclopedia": (self.encyclopediaCombo, self.parent.encyclopediaListAbb),
                "dictionary": (self.dictionaryCombo, self.dictionaryListAbb),
                "thirdPartyDictionary": (self.thirdPartyDictionaryCombo, self.thirdPartyDictionaryList),
            }
            combo, resourceList = comboDict[resource]
            selectedItem = resourceList[combo.currentIndex()]
            if resource == "lexicon":
                keyword = "LEXICON"
            elif resource == "reverselexicon":
                keyword = "REVERSELEXICON"
            elif resource == "thirdPartyDictionary":
                keyword = "SEARCHTHIRDDICTIONARY"
            else:
                keyword = "SEARCHTOOL"
            prefix = "{0}:::{1}".format(keyword, selectedItem)
            self.runSearchCommand(prefix)

    def blankOperation(self):
        return

    def selectCollection(self, collection):
        if collection == "All":
            self.bibleCombo.checkAll()
        elif collection == "None":
            self.bibleCombo.clearAll()
        else:
            self.bibleCombo.checkFromList(config.bibleCollections[collection])
