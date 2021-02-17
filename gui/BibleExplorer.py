import config, re
from BiblesSqlite import BiblesSqlite
from BibleBooks import BibleBooks
from gui.CheckableComboBox import CheckableComboBox
from BibleVerseParser import BibleVerseParser
from PySide2.QtWidgets import (QBoxLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QLabel, QWidget, QComboBox)

class BibleExplorer(QWidget):

    def __init__(self, parent, bcvTextTuple):
        super().__init__()

        self.parent = parent
        self.b, self.c, self.v, self.text = bcvTextTuple
        self.bcvChain = False
        self.biblesSqlite = BiblesSqlite()
        self.bookNo2Abb = BibleVerseParser(config.parserStandarisation).standardAbbreviation
        self.bookLabel = QLabel("")
        self.chapterLabel = QLabel("")
        self.verseLabel = QLabel("")
        
        # set title
        self.setWindowTitle(config.thisTranslation["menu_bible"])
        # setup interface
        self.setupUI()

    # setup ui
    def setupUI(self):
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.navigationWidget())
        mainLayout.addWidget(self.featuresWidget())
        self.setLayout(mainLayout)

    def navigationWidget(self):
        navigation = QWidget()

        navigationLayouts = QVBoxLayout()
        navigationLayouts.setSpacing(20)

        navigationLayoutsSub1 = QVBoxLayout()
        navigationLayoutsSub1.setSpacing(3)
        navigationLayout1 = self.navigationLayout1()
        navigationLayoutsSub1.addLayout(navigationLayout1)
        navigationLayout2 = self.navigationLayout2()
        navigationLayoutsSub1.addLayout(navigationLayout2)
        navigationLayouts.addLayout(navigationLayoutsSub1)

        navigationLayout3 = self.navigationLayout3()
        navigationLayouts.addLayout(navigationLayout3)

        navigationLayout4 = self.navigationLayout4()
        navigationLayouts.addLayout(navigationLayout4)

        navigationLayout5 = self.navigationLayout5()
        navigationLayouts.addLayout(navigationLayout5)

        navigationLayout6 = self.navigationLayout6()
        navigationLayouts.addWidget(navigationLayout6)

        navigationLayouts.addStretch()

        navigation.setLayout(navigationLayouts)
        return navigation

    def navigationLayout1(self):
        navigationLayout1 = QBoxLayout(QBoxLayout.LeftToRight)
        navigationLayout1.setSpacing(5)
        # Version selection
        self.versionCombo = QComboBox()
        self.textList = self.biblesSqlite.getBibleList()
        self.versionCombo.addItems(self.textList)
        initialIndex = 0
        if self.text in self.textList:
            initialIndex = self.textList.index(self.text)
        self.versionCombo.setCurrentIndex(initialIndex)
        navigationLayout1.addWidget(self.versionCombo)
        # Book / Chapter / Verse selection
        self.bookCombo = QComboBox()
        navigationLayout1.addWidget(self.bookCombo)
        self.chapterCombo = QComboBox()
        navigationLayout1.addWidget(self.chapterCombo)
        self.verseCombo = QComboBox()
        navigationLayout1.addWidget(self.verseCombo)
        # Initial setup
        self.updateBookCombo()
        # Interactive update in response to users selection
        self.versionCombo.currentIndexChanged.connect(self.updateBookCombo)
        self.bookCombo.currentIndexChanged.connect(lambda index: self.updateChapterCombo(self.bookList[index], True))
        self.chapterCombo.currentIndexChanged.connect(lambda index: self.updateVerseCombo(self.chapterList[index], True))
        self.verseCombo.currentIndexChanged.connect(self.updateV)
        return navigationLayout1

    def navigationLayout2(self):
        buttonElementTuple = (
            ("addToCommand", self.addToCommand),
            ("openInMainWindow", lambda: self.openInWindow("BIBLE")),
            ("openInStudyWindow", lambda: self.openInWindow("STUDY")),
        )
        return self.parent.buttonsLayout(buttonElementTuple)

    def navigationLayout3(self):
        feature = "html_showParallel"
        action = lambda: self.versionsAction("PARALLEL")
        items = self.textList
        initialItems = list({config.mainText, config.studyText, config.favouriteBible})
        self.parallelCombo = CheckableComboBox(items, initialItems)
        return self.parent.comboFeatureLayout(feature, self.parallelCombo, action)

    def navigationLayout4(self):
        feature = "html_showCompare"
        action = lambda: self.versionsAction("COMPARE")
        items = self.textList
        initialItems = list({config.mainText, config.studyText, config.favouriteBible})
        self.compareCombo = CheckableComboBox(items, initialItems)
        return self.parent.comboFeatureLayout(feature, self.compareCombo, action)

    def navigationLayout5(self):
        feature = "html_showDifference"
        action = lambda: self.versionsAction("DIFFERENCE")
        items = self.textList
        initialItems = list({config.mainText, config.studyText, config.favouriteBible})
        self.differenceCombo = CheckableComboBox(items, initialItems)
        return self.parent.comboFeatureLayout(feature, self.differenceCombo, action)

    def navigationLayout6(self):
        buttonRow1 = (
            ("MOB", lambda: self.openInWindow("BIBLE", "MOB")),
            ("MIB", lambda: self.openInWindow("BIBLE", "MIB")),
            ("MTB", lambda: self.openInWindow("BIBLE", "MTB")),
            ("MPB", lambda: self.openInWindow("BIBLE", "MPB")),
            ("MAB", lambda: self.openInWindow("BIBLE", "MAB")),
        )
        buttonRow2 = (
            ("LXX1", lambda: self.openInWindow("BIBLE", "LXX1")),
            ("LXX1i", lambda: self.openInWindow("BIBLE", "LXX1i")),
            ("LXX2", lambda: self.openInWindow("BIBLE", "LXX2")),
            ("LXX2i", lambda: self.openInWindow("BIBLE", "LXX2i")),
            ("SBLGNTl", lambda: self.openInWindow("BIBLE", "SBLGNTl")),
        )
        buttonElementTupleTuple = (buttonRow1, buttonRow2)
        return self.parent.buttonsWidget(buttonElementTupleTuple, False, False)

    def updateBCVText(self, b, c, v, text):
        if text in self.textList:
            self.versionCombo.setCurrentIndex(self.textList.index(text))
            self.text = text
        if b in self.bookList:
            self.bookCombo.setCurrentIndex(self.bookList.index(b))
            self.b = b
        if c in self.chapterList:
            self.chapterCombo.setCurrentIndex(self.chapterList.index(c))
            self.c = c
        if v in self.verseList:
            self.verseCombo.setCurrentIndex(self.verseList.index(v))
            self.v = v
        self.updateBcvLabels()

    def updateBookCombo(self, textIndex=None, reset=False):
        if textIndex is None or ((textIndex is not None) and textIndex >= 0):
            self.bcvChain = True
    
            if textIndex is not None:
                self.text = self.textList[textIndex]
            self.bookCombo.clear()
            self.bookList = self.biblesSqlite.getBookList(self.text)
            # Add only those are recognised by UBA parser
            for b in self.bookList:
                strB = str(b)
                if strB in self.bookNo2Abb:
                    self.bookCombo.addItem(self.bookNo2Abb[str(b)])
            index = 0
            if not reset and self.b in self.bookList:
                index = self.bookList.index(self.b)
            else:
                self.b = self.bookList[index]
                reset = True
            self.bookCombo.setCurrentIndex(index)
            # check / update
            self.updateChapterCombo(self.b, reset, False)

    def updateChapterCombo(self, b=None, reset=False, head=True):
        if b is None or ((b is not None) and b >= 0):
            if (head and not self.bcvChain) or (self.bcvChain and not head):
                self.bcvChain = True
    
                if b is not None:
                    self.b = b
                self.chapterCombo.clear()
                self.chapterList = self.biblesSqlite.getChapterList(self.b, self.text)
                self.chapterCombo.addItems([str(c) for c in self.chapterList])
                index = 0
                if not reset and self.c in self.chapterList:
                    index = self.chapterList.index(self.c)
                else:
                    self.c = self.chapterList[index]
                    reset = True
                self.chapterCombo.setCurrentIndex(index)
                # check / update
                self.updateVerseCombo(self.c, reset, False)

    def updateVerseCombo(self, c=None, reset=False, head=True):
        if c is None or ((c is not None) and c >= 0):
            if (head and not self.bcvChain) or (self.bcvChain and not head):
                self.bcvChain = True
    
                if c is not None:
                    self.c = c
                self.verseCombo.clear()
                self.verseList = self.biblesSqlite.getVerseList(self.b, self.c, self.text)
                self.verseCombo.addItems([str(v) for v in self.verseList])
                index = 0
                if not reset and self.v in self.verseList:
                    index = self.verseList.index(self.v)
                else:
                    self.v = self.verseList[index]
                self.verseCombo.setCurrentIndex(index)
                # Complete update
                self.updateBcvLabels()
                self.bcvChain = False

    def updateV(self, index):
        if not self.bcvChain and (index >= 0):
            self.v = self.verseList[index]
            self.verseLabel.setText(self.getSelectedReference())
            self.parent.updateBibleTabText("{0}:::{1}".format(self.text, self.getSelectedReference()))

    def featuresWidget(self):
        features = QWidget()
        featuresLayout = QFormLayout()
        featuresLayout.setSpacing(5)
        featuresLayout.addRow(self.bookLabel, self.bookFeatures())
        featuresLayout.addRow(self.chapterLabel, self.chapterFeatures())
        featuresLayout.addRow(self.verseLabel, self.verseFeatures())
        features.setLayout(featuresLayout)
        return features
    
    def updateBcvLabels(self):
        self.bookLabel.setText(self.getSelectedReferenceBook())
        self.chapterLabel.setText(self.getSelectedReferenceChapter())
        self.verseLabel.setText(self.getSelectedReference())
        self.parent.updateBibleTabText("{0}:::{1}".format(self.text, self.getSelectedReference()))

    def bookFeatures(self):
        buttonRow1 = (
            ("readNotes", lambda: self.openBibleNotes("book")),
            ("editNotes", lambda: self.editBibleNotes("book")),
        )
        buttonRow2 = (
            ("html_introduction", lambda: self.searchBookChapter("Tidwell_The_Bible_Book_by_Book")),
            ("html_timelines", lambda: self.searchBookChapter("Timelines")),
            ("context1_dict", lambda: self.searchBookName(True)),
            ("context1_encyclopedia", lambda: self.searchBookName(False)),
        )
        buttonElementTupleTuple = (buttonRow1, buttonRow2)
        return self.parent.buttonsWidget(buttonElementTupleTuple)

    def chapterFeatures(self):
        buttonRow1 = (
            ("readNotes", lambda: self.openBibleNotes("chapter")),
            ("editNotes", lambda: self.editBibleNotes("chapter")),
        )
        buttonRow2 = (
            ("html_overview", lambda: self.chapterAction("OVERVIEW")),
            ("html_chapterIndex", lambda: self.chapterAction("CHAPTERINDEX")),
            ("html_summary", lambda: self.chapterAction("SUMMARY")),
            ("menu4_commentary", lambda: self.chapterAction("COMMENTARY")),
        )
        buttonElementTupleTuple = (buttonRow1, buttonRow2)
        return self.parent.buttonsWidget(buttonElementTupleTuple)

    def verseFeatures(self):
        buttonRow1 = (
            ("readNotes", lambda: self.openBibleNotes("verse")),
            ("editNotes", lambda: self.editBibleNotes("verse")),
        )
        buttonRow2 = (
            ("menu4_compareAll", lambda: self.verseAction("COMPARE")),
            ("menu4_crossRef", lambda: self.verseAction("CROSSREFERENCE")),
            ("menu4_tske", lambda: self.verseAction("TSKE")),
        )
        buttonRow3 = (
            ("menu4_traslations", lambda: self.verseAction("TRANSLATION")),
            ("menu4_discourse", lambda: self.verseAction("DISCOURSE")),
            ("menu4_words", lambda: self.verseAction("WORDS")),
            ("menu4_tdw", lambda: self.verseAction("COMBO")),
        )
        buttonRow4 = (
            ("menu4_indexes", lambda: self.verseAction("INDEX")),
            ("menu4_commentary", lambda: self.verseAction("COMMENTARY")),
        )
        buttonElementTupleTuple = (buttonRow1, buttonRow2, buttonRow3, buttonRow4)
        return self.parent.buttonsWidget(buttonElementTupleTuple)

    # Selected Reference

    def getSelectedReference(self):
        return "{0} {1}:{2}".format(self.bookNo2Abb[str(self.b)], self.c, self.v)

    def getSelectedReferenceBook(self):
        return self.getSelectedReference().split(" ")[0]

    def getSelectedReferenceChapter(self):
        return self.getSelectedReference().split(":")[0]

    # Button actions

    def addToCommand(self):
        self.parent.commandField.setText("{0} {1}".format(self.parent.commandField.text(), self.getSelectedReference()))

    def openInWindow(self, window, text=""):
        if window == "STUDY" and config.openBibleInMainViewOnly:
            self.parent.parent.enableStudyBibleButtonClicked()
        command = "{0}:::{1}:::{2}".format(window, text if text else self.text, self.getSelectedReference())
        self.parent.runTextCommand(command)

    def openBibleNotes(self, noteType):
        keywords = {
            "book": "_openbooknote",
            "chapter": "_openchapternote",
            "verse": "_openversenote",
        }
        command = "{0}:::{1}.{2}.{3}".format(keywords[noteType], self.b, self.c, self.v)
        self.parent.runTextCommand(command)

    def versionsAction(self, keyword):
        selectedVersionsMap = {
            "PARALLEL": self.parallelCombo.checkItems,
            "COMPARE": self.compareCombo.checkItems,
            "DIFFERENCE": self.differenceCombo.checkItems,
        }
        selectedVersions = "_".join(selectedVersionsMap[keyword])
        command = "{0}:::{1}:::{2}".format(keyword, selectedVersions, self.getSelectedReference())
        self.parent.runTextCommand(command)

    def editBibleNotes(self, noteType):
        keywords = {
            "book": "_editbooknote",
            "chapter": "_editchapternote",
            "verse": "_editversenote",
        }
        command = "{0}:::{1}.{2}.{3}".format(keywords[noteType], self.b, self.c, self.v)
        self.parent.runTextCommand(command)

    def searchBookName(self, dictionary):
        engFullBookName = BibleBooks().eng[str(self.b)][1]
        matches = re.match("^[0-9]+? (.*?)$", engFullBookName)
        if matches:
            engFullBookName = matches.group(1)
        command = "SEARCHTOOL:::{0}:::{1}".format(config.dictionary if dictionary else config.encyclopedia, engFullBookName)
        self.parent.runTextCommand(command)

    def searchBookChapter(self, resource):
        engFullBookName = BibleBooks().eng[str(self.b)][1]
        command = "SEARCHBOOKCHAPTER:::{0}:::{1}".format(resource, engFullBookName)
        self.parent.runTextCommand(command)

    def chapterAction(self, keyword):
        command = "{0}:::{1}".format(keyword, self.getSelectedReferenceChapter())
        self.parent.runTextCommand(command)

    def verseAction(self, keyword):
        command = "{0}:::{1}".format(keyword, self.getSelectedReference())
        self.parent.runTextCommand(command)
