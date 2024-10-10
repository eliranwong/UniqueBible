# This plugin search currently opened bible for all forms of selected English word.

from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QWidget
else:
    from qtpy.QtWidgets import QWidget


class BibleSearchForEnglishForms(QWidget):

    def __init__(self, parent, wordEntry):
        super().__init__()
        self.parent = parent
        self.wordEntry = wordEntry.split(" ", 1)[0] if wordEntry else ""
        # set title
        self.setWindowTitle("English Word Forms")
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()
    
    def setupVariables(self):
        pass

    def setupUI(self):
        self.setupLayouts()
        self.setupWidgets()

    def setupLayouts(self):
        if config.qtLibrary == "pyside6":
            from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout
        else:
            from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout
        self.mainLayout = QVBoxLayout()
        self.searchItemsLayout = QFormLayout()
        self.searchItemsLayout.setSpacing(5)
        self.mainLayout.addLayout(self.searchItemsLayout)
        self.bottomLayout = QHBoxLayout()
        self.mainLayout.addLayout(self.bottomLayout)
        self.setLayout(self.mainLayout)

    def setupWidgets(self):
        self.setupSearchItemsLayoutWidgets()
        self.setupBottomLayoutWidgets()

    def setupSearchItemsLayoutWidgets(self):
        if config.qtLibrary == "pyside6":
            from PySide6.QtWidgets import QPushButton, QHBoxLayout, QLabel
        else:
            from qtpy.QtWidgets import QPushButton, QHBoxLayout, QLabel
        from uniquebible.gui.CheckableComboBox import CheckableComboBox

        layout = QHBoxLayout()
        wordAudioButton = QPushButton("Audio")
        wordAudioButton.clicked.connect(lambda: self.parent.runTextCommand("GTTS:::{0}".format(self.wordEntry)))
        searchWordButton = QPushButton("Search")
        searchWordButton.clicked.connect(lambda: self.parent.runTextCommand("SEARCH:::{0}".format(self.wordEntry)))
        for item in (QLabel(self.wordEntry), wordAudioButton, searchWordButton):
            layout.addWidget(item)
        self.searchItemsLayout.addRow("Word:", layout)
        layout = QHBoxLayout()
        lemmaAudioButton = QPushButton("Audio")
        lemmaAudioButton.clicked.connect(lambda: self.parent.runTextCommand("GTTS:::{0}".format(self.lemma)))
        searchLemmaButton = QPushButton("Search")
        searchLemmaButton.clicked.connect(lambda: self.parent.runTextCommand("SEARCH:::{0}".format(self.lemma)))
        self.lemma = config.lemmatizer.lemmatize(self.wordEntry)
        for item in (QLabel(self.lemma), lemmaAudioButton, searchLemmaButton):
            layout.addWidget(item)
        self.searchItemsLayout.addRow("Lemma:", layout)
        synsets = config.wordnet.synsets(self.lemma)
        websterButton, wordnetButton = QPushButton("Webster"), QPushButton("WordNet")
        websterButton.clicked.connect(lambda: self.parent.runTextCommand("SEARCHTHIRDDICTIONARY:::webster:::{0}".format(self.lemma)))
        wordnetButton.clicked.connect(lambda: self.parent.runTextCommand("SEARCHTHIRDDICTIONARY:::wordnet:::{0}".format(self.lemma)))
        layout = QHBoxLayout()
        for item in (QLabel(synsets[0].definition() if synsets else ""), websterButton, wordnetButton):
            layout.addWidget(item)
        self.searchItemsLayout.addRow("Definition:", layout)
        comboWidth = 300
        self.formDict = config.get_word_forms(self.wordEntry)
        if self.formDict["n"]:
            self.nouns = self.formDict["n"]
            self.nounCombo = CheckableComboBox(self.nouns, self.nouns)
            self.nounCombo.setFixedWidth(comboWidth)
            self.nounCombo.checkFromList(self.nouns)
            self.clearNounButton, self.allNounButton, self.searchNounButton = QPushButton("None"), QPushButton("All"), QPushButton("Search")
            self.searchNounButton.clicked.connect(self.searchNounButtonClicked)
            self.clearNounButton.clicked.connect(lambda: self.nounCombo.checkFromList([]))
            self.allNounButton.clicked.connect(lambda: self.nounCombo.checkFromList(self.nouns))
            layout = QHBoxLayout()
            for item in (self.nounCombo, self.clearNounButton, self.allNounButton, self.searchNounButton):
                layout.addWidget(item)
            self.searchItemsLayout.addRow("Noun:", layout)
        if self.formDict["a"]:
            self.adjectives = self.formDict["a"]
            self.adjectiveCombo = CheckableComboBox(self.adjectives, self.adjectives)
            self.adjectiveCombo.setFixedWidth(comboWidth)
            self.adjectiveCombo.checkFromList(self.adjectives)
            self.clearAdjectiveButton, self.allAdjectiveButton, self.searchAdjectiveButton = QPushButton("None"), QPushButton("All"), QPushButton("Search")
            self.searchAdjectiveButton.clicked.connect(self.searchAdjectiveButtonClicked)
            self.clearAdjectiveButton.clicked.connect(lambda: self.adjectiveCombo.checkFromList([]))
            self.allAdjectiveButton.clicked.connect(lambda: self.adjectiveCombo.checkFromList(self.adjectives))
            layout = QHBoxLayout()
            for item in (self.adjectiveCombo, self.clearAdjectiveButton, self.allAdjectiveButton, self.searchAdjectiveButton):
                layout.addWidget(item)
            self.searchItemsLayout.addRow("Adjective:", layout)
        if self.formDict["v"]:
            self.verbs = self.formDict["v"]
            self.verbCombo = CheckableComboBox(self.verbs, self.verbs)
            self.verbCombo.setFixedWidth(comboWidth)
            self.verbCombo.checkFromList(self.verbs)
            self.clearVerbButton, self.allVerbButton, self.searchVerbButton = QPushButton("None"), QPushButton("All"), QPushButton("Search")
            self.searchVerbButton.clicked.connect(self.searchVerbButtonClicked)
            self.clearVerbButton.clicked.connect(lambda: self.verbCombo.checkFromList([]))
            self.allVerbButton.clicked.connect(lambda: self.verbCombo.checkFromList(self.verbs))
            layout = QHBoxLayout()
            for item in (self.verbCombo, self.clearVerbButton, self.allVerbButton, self.searchVerbButton):
                layout.addWidget(item)
            self.searchItemsLayout.addRow("Verb:", layout)
        if self.formDict["r"]:
            self.adverbs = self.formDict["r"]
            self.adverbCombo = CheckableComboBox(self.adverbs, self.adverbs)
            self.adverbCombo.setFixedWidth(comboWidth)
            self.adverbCombo.checkFromList(self.adverbs)
            self.clearAdverbButton, self.allAdverbButton, self.searchAdverbButton = QPushButton("None"), QPushButton("All"), QPushButton("Search")
            self.searchAdverbButton.clicked.connect(self.searchAdverbButtonClicked)
            self.clearAdverbButton.clicked.connect(lambda: self.adverbCombo.checkFromList([]))
            self.allAdverbButton.clicked.connect(lambda: self.adverbCombo.checkFromList(self.adverbs))
            layout = QHBoxLayout()
            for item in (self.adverbCombo, self.clearAdverbButton, self.allAdverbButton, self.searchAdverbButton):
                layout.addWidget(item)
            self.searchItemsLayout.addRow("Adverb:", layout)

    def setupBottomLayoutWidgets(self):
        if config.qtLibrary == "pyside6":
            from PySide6.QtWidgets import QPushButton
        else:
            from qtpy.QtWidgets import QPushButton
        noneButton = QPushButton("Clear All")
        noneButton.clicked.connect(self.clearAllCombo)
        allButton = QPushButton("Select All")
        allButton.clicked.connect(self.selectAllCombo)
        copyButton = QPushButton("Copy")
        copyButton.clicked.connect(self.copyAllSelectedItems)
        searchButton = QPushButton("Search")
        searchButton.clicked.connect(self.searchAllSelectedItems)
        for button in (noneButton, allButton, copyButton, searchButton):
            self.bottomLayout.addWidget(button)

    def clearAllCombo(self):
        self.nounCombo.checkFromList([])
        self.adjectiveCombo.checkFromList([])
        self.verbCombo.checkFromList([])
        self.adverbCombo.checkFromList([])

    def selectAllCombo(self):
        self.nounCombo.checkFromList(self.nouns)
        self.adjectiveCombo.checkFromList(self.adjectives)
        self.verbCombo.checkFromList(self.verbs)
        self.adverbCombo.checkFromList(self.adverbs)

    def searchNounButtonClicked(self):
        items = self.nounCombo.checkItems
        self.searchSelectedItems(items)

    def searchAdjectiveButtonClicked(self):
        items = self.adjectiveCombo.checkItems
        self.searchSelectedItems(items)

    def searchVerbButtonClicked(self):
        items = self.verbCombo.checkItems
        self.searchSelectedItems(items)

    def searchAdverbButtonClicked(self):
        items = self.adverbCombo.checkItems
        self.searchSelectedItems(items)

    def getAllSelectedItems(self):
        items = []
        if hasattr(self, "nounCombo"):
            items += self.nounCombo.checkItems
        if hasattr(self, "adjectiveCombo"):
            items += self.adjectiveCombo.checkItems
        if hasattr(self, "verbCombo"):
            items += self.verbCombo.checkItems
        if hasattr(self, "adverbCombo"):
            items += self.adverbCombo.checkItems
        return items

    def copyAllSelectedItems(self):
        items = self.getAllSelectedItems()
        if items:
            if config.qtLibrary == "pyside6":
                from PySide6.QtWidgets import QApplication
            else:
                from qtpy.QtWidgets import QApplication
            print(", ".join(set(items)))
            QApplication.clipboard().setText("|".join(set(items)))

    def searchAllSelectedItems(self):
        items = self.getAllSelectedItems()
        self.searchSelectedItems(items)

    def searchSelectedItems(self, items):
        if items:
            self.parent.runTextCommand("ORSEARCH:::{0}".format("|".join(set(items))))
        else:
            self.parent.runTextCommand("SEARCH:::{0}".format(self.wordEntry))

if config.pluginContext:
    config.mainWindow.bibleSearchForEnglishForms = BibleSearchForEnglishForms(config.mainWindow, config.pluginContext)
    config.mainWindow.bibleSearchForEnglishForms.show()