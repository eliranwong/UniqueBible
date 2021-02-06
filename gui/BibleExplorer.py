import config
from functools import partial
from BiblesSqlite import BiblesSqlite
from BibleVerseParser import BibleVerseParser
from PySide2.QtCore import Qt
from PySide2.QtGui import QGuiApplication
from PySide2.QtWidgets import (QVBoxLayout, QFormLayout, QHBoxLayout, QLineEdit, QPushButton, QWidget, QTabWidget,
                               QApplication, QBoxLayout, QGridLayout, QComboBox)

class BibleExplorer(QWidget):

    def __init__(self, parent, bcvTextTuple):
        super().__init__()

        self.parent = parent
        self.b, self.c, self.v, self.text = bcvTextTuple
        self.bcvChain = False
        self.biblesSqlite = BiblesSqlite()
        self.bookNo2Abb = BibleVerseParser(config.parserStandarisation).standardAbbreviation
        
        # set title
        self.setWindowTitle(config.thisTranslation["menu_bible"])
        # setup interface
        self.setupUI()

    # setup ui
    def setupUI(self):
        mainLayout = QGridLayout()
        mainLayout.addWidget(self.navigationWidget())
        mainLayout.addWidget(self.featuresWidget())
        self.setLayout(mainLayout)

    def navigationWidget(self):
        navigation = QWidget()

        navigationLayouts = QVBoxLayout()
        navigationLayouts.setSpacing(3)

        navigationLayout1 = self.navigationLayout1()
        navigationLayout1.addStretch()
        navigationLayouts.addLayout(navigationLayout1)

        navigationLayout2 = self.navigationLayout2()
        navigationLayout2.addStretch()
        navigationLayouts.addLayout(navigationLayout2)

        navigation.setLayout(navigationLayouts)
        return navigation

    def navigationLayout1(self):
        navigationLayout1 = QBoxLayout(QBoxLayout.LeftToRight)
        navigationLayout1.setSpacing(5)
        # Version selection
        versionCombo = QComboBox()
        self.textList = self.biblesSqlite.getBibleList()
        versionCombo.addItems(self.textList)
        initialIndex = 0
        if self.text in self.textList:
            initialIndex = self.textList.index(self.text)
        versionCombo.setCurrentIndex(initialIndex)
        navigationLayout1.addWidget(versionCombo)
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
        versionCombo.currentIndexChanged.connect(self.updateBookCombo)
        self.bookCombo.currentIndexChanged.connect(lambda index: self.updateChapterCombo(index, True))
        self.chapterCombo.currentIndexChanged.connect(lambda index: self.updateVerseCombo(index, True))
        self.verseCombo.currentIndexChanged.connect(self.updateV)
        return navigationLayout1

    def navigationLayout2(self):
        buttonElementTuple = (
            ("openInStudyWindow", self.openInStudyWindow),
            ("openInMainWindow", self.openInMainWindow),
        )
        return self.buttonsLayout(buttonElementTuple, True)

    def updateBookCombo(self, textIndex=None, reset=False):
        if textIndex is None or ((textIndex is not None) and textIndex >= 0):
            self.bcvChain = True
    
            if textIndex is not None:
                self.text = self.textList[textIndex]
            self.bookCombo.clear()
            bookList = self.biblesSqlite.getBookList(self.text)
            # Add only those are recognised by UBA parser
            for b in bookList:
                strB = str(b)
                if strB in self.bookNo2Abb:
                    self.bookCombo.addItem(self.bookNo2Abb[str(b)])
            index = 0
            if not reset and self.b in bookList:
                index = bookList.index(self.b)
            else:
                self.b = bookList[index]
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
                    self.c = self.chapterList[c]
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
                self.bcvChain = False

    def updateV(self, index):
        if not self.bcvChain and (index >= 0):
            self.v = self.verseList[index]

    def featuresWidget(self):
        features = QWidget()
        featuresLayout = QFormLayout()
        featuresLayout.setSpacing(5)
        featuresLayout.addRow(self.getSelectedReferenceBook(), self.bookFeatures())
        featuresLayout.addRow(self.getSelectedReferenceChapter(), self.chapterFeatures())
        featuresLayout.addRow(self.getSelectedReference(), self.verseFeatures())
        features.setLayout(featuresLayout)
        return features
    
    def bookFeatures(self):
        buttonRow1 = (
            ("dummy", self.dummyAction),
        )
        buttonElementTupleTuple = (buttonRow1,)
        return self.buttonsWidget(buttonElementTupleTuple)

    def chapterFeatures(self):
        buttonRow1 = (
            ("dummy", self.dummyAction),
        )
        buttonElementTupleTuple = (buttonRow1,)
        return self.buttonsWidget(buttonElementTupleTuple)

    def verseFeatures(self):
        buttonRow1 = (
            ("menu6_notes", self.openVerseNotes)
            ("menu4_compareAll", partial(self.verseAction, "COMPARE")),
            ("menu4_crossRef", partial(self.verseAction, "CROSSREFERENCE")),
            ("menu4_tske", partial(self.verseAction, "TSKE")),
        )
        buttonRow2 = (
            ("menu4_traslations", partial(self.verseAction, "TRANSLATION")),
            ("menu4_discourse", partial(self.verseAction, "DISCOURSE")),
            ("menu4_words", partial(self.verseAction, "WORDS")),
            ("menu4_tdw", partial(self.verseAction, "COMBO")),
        )
        buttonRow3 = (
            ("menu4_commentary", partial(self.verseAction, "COMMENTARY")),
            ("menu4_indexes", partial(self.verseAction, "INDEX")),
        )
        buttonElementTupleTuple = (buttonRow1, buttonRow2, buttonRow3)
        return self.buttonsWidget(buttonElementTupleTuple)

    def buttonsWidget(self, buttonElementTupleTuple):
        buttons = QWidget()
        buttonsLayouts = QVBoxLayout()
        buttonsLayouts.setSpacing(3)
        for buttonElementTuple in buttonElementTupleTuple:
            buttonsLayouts.addLayout(self.buttonsLayout(buttonElementTuple))
        buttons.setLayout(buttonsLayouts)
        return buttons

    def buttonsLayout(self, buttonElementTuple, r2l=False):
        buttonsLayout = QBoxLayout(QBoxLayout.RightToLeft)
        buttonsLayout.setSpacing(5)
        for buttonElements in buttonElementTuple:
            button = QPushButton(config.thisTranslation[buttonElements[0]])
            button.clicked.connect(buttonElements[1])
            buttonsLayout.addWidget(button)
        return buttonsLayout

    # Selected Reference

    def getSelectedReference(self):
        return "{0} {1}:{2}".format(self.bookNo2Abb[str(self.b)], self.c, self.v)

    def getSelectedReferenceBook(self):
        return self.getSelectedReference().split(" ")[0]

    def getSelectedReferenceChapter(self):
        return self.getSelectedReference().split(":")[0]

    # Button actions

    def dummyAction(self):
        print("testing")

    def openInMainWindow(self):
        command = "BIBLE:::{0}:::{1}".format(self.text, self.getSelectedReference())
        self.parent.runTextCommand(command)

    def openInStudyWindow(self):
        command = "STUDY:::{0}:::{1}".format(self.text, self.getSelectedReference())
        self.parent.runTextCommand(command)

    def openVerseNotes(self):
        command = "_openversenote:::{0}.{1}.{2}".format(self.b, self.c, self.v)
        self.parent.runTextCommand(command)

    def verseAction(self, keyword):
        command = "{0}:::{1}".format(keyword, self.getSelectedReference())
        self.parent.runTextCommand(command)

if __name__ == "__main__":
   import sys

   app = QApplication(sys.argv)
   ui = BibleFeatures()
   ui.show()
   sys.exit(app.exec_())