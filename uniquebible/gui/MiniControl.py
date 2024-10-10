import glob
from uniquebible import config
import os
from pathlib import Path
from uniquebible.util.BibleBooks import BibleBooks

if __name__ == "__main__":
    config.noQt = True

from functools import partial
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QWidget, QTabWidget, QApplication, QBoxLayout, QGridLayout, QComboBox
else:
    from qtpy.QtCore import Qt, QEvent
    from qtpy.QtGui import QGuiApplication
    from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QWidget, QTabWidget, QApplication, QBoxLayout, QGridLayout, QComboBox


from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.db.ToolsSqlite import Commentary, LexiconData, IndexesSqlite
from uniquebible.util.TextCommandParser import TextCommandParser

from uniquebible.db.BiblesSqlite import BiblesSqlite, Bible


class MiniControl(QWidget):

    def __init__(self, parent, selectedTab = 0):
        super().__init__()
        self.textButtonStyleEnabled = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"
        self.textButtonStyleDisabled = "QPushButton {background-color: #323232; color: #323232;} QPushButton:hover {background-color: #323232;} QPushButton:pressed { background-color: #323232;}"
        self.setWindowTitle(config.thisTranslation["remote_control"])
        self.parent = parent
        self.devotionals = sorted(glob.glob(os.path.join(config.marvelData, "devotionals", "*.devotional")))
        # specify window size
        if config.qtMaterial and config.qtMaterialTheme:
            self.resizeWindow(1 / 2, 1 / 3)
        else:
            self.resizeWindow(2 / 5, 1 / 3)
        self.resizeEvent = (lambda old_method: (lambda event: (self.onResized(event), old_method(event))[-1]))(
            self.resizeEvent)
        self.bibleButtons = {}
        self.commentaryButtons = {}
        self.bookIntroButtons = {}
        # setup interface
        self.bible_layout = None
        self.setupUI()
        self.tabs.setCurrentIndex(selectedTab)

    # window appearance
    def resizeWindow(self, widthFactor, heightFactor):
        #availableGeometry = QGuiApplication.instance().desktop().availableGeometry()
        availableGeometry = QGuiApplication.primaryScreen().availableGeometry()
        self.setMinimumWidth(500)
        self.resize(int(availableGeometry.width() * widthFactor), int(availableGeometry.height() * heightFactor))

    def onResized(self, event):
        pass

    def closeEvent(self, event):
        config.miniControl = False

    # manage key capture
    def event(self, event):
        if event.type() == QEvent.KeyRelease:
            if event.modifiers() == Qt.ControlModifier:
                if event.key() == Qt.Key_B:
                    self.tabs.setCurrentIndex(0)
                elif event.key() == Qt.Key_T:
                    self.tabs.setCurrentIndex(1)
                elif event.key() == Qt.Key_C:
                    self.tabs.setCurrentIndex(2)
                elif event.key() == Qt.Key_L:
                    self.tabs.setCurrentIndex(3)
                elif event.key() == Qt.Key_D:
                    self.tabs.setCurrentIndex(4)
                elif event.key() == Qt.Key_O:
                    self.tabs.setCurrentIndex(5)
            elif event.key() == Qt.Key_Escape:
                self.close()
        return QWidget.event(self, event)

    # setup ui
    def setupUI(self):
        textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"

        mainLayout = QGridLayout()

        commandBox = QVBoxLayout()
        commandBox.setSpacing(3)

        commandBar = QWidget()
        commandLayout1 = QBoxLayout(QBoxLayout.LeftToRight)
        commandLayout1.setSpacing(5)

        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setCompleter(self.parent.getTextCommandSuggestion())
        self.searchLineEdit.setClearButtonEnabled(True)
        self.searchLineEdit.setToolTip(config.thisTranslation["enter_command_here"])
        self.searchLineEdit.returnPressed.connect(self.searchLineEntered)
        self.searchLineEdit.setFixedWidth(450)
        commandLayout1.addWidget(self.searchLineEdit)

        enterButton = QPushButton(config.thisTranslation["enter"])
        enterButton.setFixedWidth(100)
        enterButton.clicked.connect(self.searchLineEntered)
        commandLayout1.addWidget(enterButton)

        # commandLayout1.addStretch()
        commandBox.addLayout(commandLayout1)

        if config.showMiniKeyboardInMiniControl:
            commandLayout2 = QBoxLayout(QBoxLayout.LeftToRight)
            commandLayout2.setSpacing(5)

            keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', ':', '-', ',', '.', ' ', '<', 'X']
            for key in keys:
                button = QPushButton(key)
                button.setMaximumWidth(30)
                button.clicked.connect(partial(self.keyEntryAction, key))
                commandLayout2.addWidget(button)

            commandLayout2.addStretch()
            commandBox.addLayout(commandLayout2)

        if config.showMiniKeyboardInMiniControl and not config.noTtsFound:
            ttsLayout = QBoxLayout(QBoxLayout.LeftToRight)
            ttsLayout.setSpacing(5)
    
            self.languageCombo = QComboBox()
            ttsLayout.addWidget(self.languageCombo)
            languages = self.parent.getTtsLanguages()
            self.languageCodes = list(languages.keys())
            for code in self.languageCodes:
                self.languageCombo.addItem(languages[code][1])
            # Check if selected tts engine has the language user specify.
            if not (config.ttsDefaultLangauge in self.languageCodes):
                config.ttsDefaultLangauge = "en-GB" if config.isGoogleCloudTTSAvailable else "en"
            # Set initial item
            initialIndex = self.languageCodes.index(config.ttsDefaultLangauge)
            self.languageCombo.setCurrentIndex(initialIndex)
    
            # setting tts default language here is confusing; better place in menu
            #setDefaultButton = QPushButton(config.thisTranslation["setDefault"])
            #setDefaultButton.setFixedWidth(130)
            #setDefaultButton.clicked.connect(self.setTtsDefaultLanguage)
            #ttsLayout.addWidget(setDefaultButton)
            
            speakButton = QPushButton(config.thisTranslation["speak"])
            speakButton.setFixedWidth(100)
            speakButton.clicked.connect(self.speakCommandFieldText)
            ttsLayout.addWidget(speakButton)
    
            stopButton = QPushButton(config.thisTranslation["stop"])
            stopButton.setFixedWidth(100)
            stopButton.clicked.connect(self.parent.textCommandParser.stopTtsAudio)
            ttsLayout.addWidget(stopButton)
    
            ttsLayout.addStretch()

            commandBox.addLayout(ttsLayout)

        commandBar.setLayout(commandBox)
        mainLayout.addWidget(commandBar, 0, 0, Qt.AlignCenter)

        self.tabs = QTabWidget()
        self.tabs.currentChanged.connect(self.tabChanged)
        mainLayout.addWidget(self.tabs, 1, 0, Qt.AlignCenter)

        parser = BibleVerseParser(config.parserStandarisation)
        self.bookMap = parser.standardAbbreviation
        bookNums = list(self.bookMap.keys())
        self.bookNumGps = [
            bookNums[0:10],
            bookNums[10:20],
            bookNums[20:30],
            bookNums[30:39],
            bookNums[39:49],
            bookNums[49:59],
            bookNums[59:69],
            bookNums[69:79],
            bookNums[79:86],
            bookNums[86:94],
            bookNums[94:99],
            bookNums[99:104],
            bookNums[104:110],
            bookNums[110:119],
            bookNums[119:124],
            bookNums[124:129],
            bookNums[129:139],
            bookNums[139:149],
            bookNums[149:159],
            bookNums[159:169],
            bookNums[169:174],
            bookNums[174:179],
            bookNums[179:189],
            bookNums[189:199],
        ]

        # Bible books tab

        self.bible = QWidget()
        self.populateBooksButtons(config.mainText)
        self.tabs.addTab(self.bible, config.thisTranslation["bible"])

        # Bible translations tab

        self.biblesBox = QWidget()
        self.biblesBoxContainer = QVBoxLayout()
        collectionsLayout = self.newRowLayout()
        if len(config.bibleCollections) > 0:
            button = QPushButton("All")
            button.setStyleSheet(textButtonStyle)
            button.clicked.connect(partial(self.selectCollection, "All"))
            collectionsLayout.addWidget(button)
            count = 0
            for collection in sorted(config.bibleCollections.keys()):
                button = QPushButton(collection)
                button.setStyleSheet(textButtonStyle)
                button.clicked.connect(partial(self.selectCollection, collection))
                collectionsLayout.addWidget(button)
                count += 1
                if count > 5:
                    count = 0
                    self.biblesBoxContainer.addLayout(collectionsLayout)
                    collectionsLayout = self.newRowLayout()

        self.biblesBoxContainer.addLayout(collectionsLayout)
        self.bibleBoxWidget = QWidget()
        self.bibleBoxLayout = QVBoxLayout()
        self.bibleBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.bibleBoxLayout.setSpacing(1)
        row_layout = self.newRowLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(1)
        biblesSqlite = BiblesSqlite()
        bibles = biblesSqlite.getBibleList()
        count = 0
        for bible in bibles:
            button = QPushButton(bible)
            if bible in config.bibleDescription:
                button.setToolTip("{0}".format(config.bibleDescription[bible]))
            button.clicked.connect(partial(self.bibleAction, bible))
            row_layout.addWidget(button)
            count += 1
            if count > 6:
                count = 0
                self.bibleBoxLayout.addLayout(row_layout)
                row_layout = self.newRowLayout()
            self.bibleButtons[bible] = button
        self.bibleBoxLayout.addLayout(row_layout)
        self.bibleBoxLayout.addStretch()
        self.biblesBoxContainer.addLayout(self.bibleBoxLayout)
        self.biblesBoxContainer.addStretch()
        self.biblesBox.setLayout(self.biblesBoxContainer)
        self.tabs.addTab(self.biblesBox, config.thisTranslation["translations"])

        # Commentaries tab

        commentaries_box = QWidget()
        box_layout = QVBoxLayout()
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(1)
        row_layout = self.newRowLayout()
        button = QPushButton(config.thisTranslation["activeOnly"])
        if not config.menuLayout == "material":
            button.setStyleSheet(textButtonStyle)
        button.clicked.connect(self.activeCommentaries)
        row_layout.addWidget(button)
        box_layout.addLayout(row_layout)
        row_layout = self.newRowLayout()
        commentaries = Commentary().getCommentaryList()
        count = 0
        for commentary in commentaries:
            button = QPushButton(commentary)
            button.setToolTip(Commentary.fileLookup[commentary])
            button.clicked.connect(partial(self.commentaryAction, commentary))
            self.commentaryButtons[commentary] = button
            row_layout.addWidget(button)
            count += 1
            if count > 6:
                count = 0
                box_layout.addLayout(row_layout)
                row_layout = self.newRowLayout()
        box_layout.addLayout(row_layout)
        box_layout.addStretch()
        commentaries_box.setLayout(box_layout)

        self.tabs.addTab(commentaries_box, config.thisTranslation["commentaries"])

        # Lexicons tab

        lexicons_box = QWidget()
        box_layout = QVBoxLayout()
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(1)
        row_layout = self.newRowLayout()
        lexicons = LexiconData().lexiconList
        count = 0
        for lexicon in lexicons:
            button = QPushButton(lexicon)
            if lexicon in config.lexiconDescription:
                button.setToolTip("{0}".format(config.lexiconDescription[lexicon]))
            button.clicked.connect(partial(self.lexiconAction, lexicon))
            row_layout.addWidget(button)
            count += 1
            if count > 6:
                count = 0
                box_layout.addLayout(row_layout)
                row_layout = self.newRowLayout()
        box_layout.addLayout(row_layout)
        box_layout.addStretch()
        lexicons_box.setLayout(box_layout)

        self.tabs.addTab(lexicons_box, config.thisTranslation["lexicons"])

        # Dictionaries tab

        dictionaries_box = QWidget()
        box_layout = QVBoxLayout()
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(1)
        row_layout = self.newRowLayout()
        dictionaries = IndexesSqlite().dictionaryList
        count = 0
        for dictionary in dictionaries:
            button = QPushButton(dictionary[0])
            button.setToolTip(dictionary[1])
            button.clicked.connect(partial(self.dictionaryAction, dictionary[0]))
            row_layout.addWidget(button)
            count += 1
            if count > 6:
                count = 0
                box_layout.addLayout(row_layout)
                row_layout = self.newRowLayout()
        box_layout.addLayout(row_layout)
        box_layout.addStretch()
        dictionaries_box.setLayout(box_layout)

        self.tabs.addTab(dictionaries_box, config.thisTranslation["dictionaries"])

        # Book intros tab

        bookIntros_box = QWidget()
        box_layout = QVBoxLayout()
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(1)
        row_layout = self.newRowLayout()
        button = QPushButton(config.thisTranslation["activeOnly"])
        if not config.menuLayout == "material":
            button.setStyleSheet(textButtonStyle)
        button.clicked.connect(self.activeBookIntros)
        row_layout.addWidget(button)
        box_layout.addLayout(row_layout)
        row_layout = self.newRowLayout()
        commentaries = Commentary().getCommentaryList()
        count = 0
        for commentary in commentaries:
            button = QPushButton(commentary)
            button.setToolTip(Commentary.fileLookup[commentary])
            button.clicked.connect(partial(self.bookIntroAction, commentary))
            self.bookIntroButtons[commentary] = button
            row_layout.addWidget(button)
            count += 1
            if count > 6:
                count = 0
                box_layout.addLayout(row_layout)
                row_layout = self.newRowLayout()
        box_layout.addLayout(row_layout)
        box_layout.addStretch()
        bookIntros_box.setLayout(box_layout)

        self.tabs.addTab(bookIntros_box, config.thisTranslation["bookIntro"])

        # Devotionals tab

        if len(self.devotionals) > 0:
            devotionals_box = QWidget()
            box_layout = QVBoxLayout()
            box_layout.setContentsMargins(0, 0, 0, 0)
            box_layout.setSpacing(1)
            row_layout = self.newRowLayout()
            count = 0
            for file in self.devotionals:
                name = Path(file).stem
                button = QPushButton(name)
                # button.setToolTip(dictionary[1])
                button.clicked.connect(partial(self.devotionalAction, name))
                row_layout.addWidget(button)
                count += 1
                if count > 1:
                    count = 0
                    box_layout.addLayout(row_layout)
                    row_layout.addStretch()
                    row_layout = self.newRowLayout()
            for i in range(count, 3):
                button = QPushButton("")
                row_layout.addWidget(button)
            box_layout.addLayout(row_layout)
            box_layout.addStretch()
            devotionals_box.setLayout(box_layout)

            self.tabs.addTab(devotionals_box, config.thisTranslation["devotionals"])

        self.tabs.setCurrentIndex(config.miniControlInitialTab)
        self.setLayout(mainLayout)

    def populateBooksButtons(self, bibleName):
        books = Bible(bibleName).getBookList()
        if self.bible_layout is not None:
            while self.bible_layout.count():
                child = self.bible_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            self.bible_layout = QVBoxLayout()
        self.bible_layout.setContentsMargins(0, 0, 0, 0)
        self.bible_layout.setSpacing(1)
        for bookNumGp in self.bookNumGps:
            gp = QWidget()
            layout = self.newRowLayout()
            for bookNum in bookNumGp:
                if int(bookNum) in books:
                    text = self.bookMap[bookNum]
                    button = QPushButton(text)
                    if config.developer:
                        button.setToolTip("{0} - {1}".format(BibleBooks.abbrev["eng"][bookNum][1], bookNum))
                    else:
                        button.setToolTip("{0}".format(BibleBooks.abbrev["eng"][bookNum][1]))
                    button.clicked.connect(partial(self.bibleBookAction, bookNum))
                    layout.addWidget(button)
            gp.setLayout(layout)
            self.bible_layout.addWidget(gp)
        # for bookNumGp in self.bookNumGps[5:]:
        #     gp = QWidget()
        #     layout = self.newRowLayout()
        #     for bookNum in bookNumGp:
        #         text = self.bookMap[bookNum]
        #         button = QPushButton(text)
        #         button.clicked.connect(partial(self.bibleBookAction, bookNum))
        #         layout.addWidget(button)
        #     gp.setLayout(layout)
        #     bible_layout.addWidget(gp)
        self.bible_layout.addStretch()
        self.bible.setLayout(self.bible_layout)

    def newRowLayout(self):
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(1)
        return row_layout

    def tabChanged(self, index):
        prefix = ""
        if index == 0:
            prefix = "BIBLE:::{0}:::".format(config.mainText)
        elif index == 1:
            prefix = "TEXT:::"
        elif index == 2:
            prefix = "COMMENTARY:::{0}:::".format(config.commentaryText)
        elif index == 3:
            prefix = "LEXICON:::"
        elif index == 4:
            prefix = "SEARCHTOOL:::"
        if not config.clearCommandEntry:
            self.searchLineEdit.setText(prefix)

    def searchLineEntered(self):

        saveOpenBibleWindowContentOnNextTab = config.openBibleWindowContentOnNextTab
        searchString = self.searchLineEdit.text()
        if ":::" not in searchString or ":::{0}:::".format(config.mainText) in searchString:
            config.openBibleWindowContentOnNextTab = False
        self.parent.textCommandLineEdit.setText(searchString)
        self.parent.runTextCommand(searchString)
        self.searchLineEdit.setFocus()
        self.populateBooksButtons(config.mainText)
        config.openBibleWindowContentOnNextTab = saveOpenBibleWindowContentOnNextTab

    #def setTtsDefaultLanguage(self):
        #config.ttsDefaultLangauge = self.languageCodes[self.languageCombo.currentIndex()]

    def speakCommandFieldText(self):
        text = self.searchLineEdit.text()
        if ":::" in text:
            text = text.split(":::")[-1]
        if config.isGoogleCloudTTSAvailable or ((not ("OfflineTts" in config.enabled) or config.forceOnlineTts) and ("Gtts" in config.enabled)):
            command = "GTTS:::{0}:::{1}".format(self.languageCodes[self.languageCombo.currentIndex()], text)
        else:
            command = "SPEAK:::{0}:::{1}".format(self.languageCodes[self.languageCombo.currentIndex()], text)
        self.runCommmand(command)

    def bibleBookAction(self, book):
        command = "{0} ".format(self.bookMap[book])
        self.runCommmand(command)
        self.searchLineEdit.setFocus()

    def keyEntryAction(self, key):
        text = self.searchLineEdit.text()
        if key == "X":
            text = ""
        elif key == "<":
            text = text[:-1]
        else:
            text += key
        self.searchLineEdit.setText(text)

    def bibleAction(self, bible):
        command = "BIBLE:::{0}:::{1}".format(bible, self.parent.verseReference("main")[1])
        self.runCommmand(command)
        command = "_bibleinfo:::{0}".format(bible)
        self.parent.runTextCommand(command)
        self.populateBooksButtons(config.mainText)

    def commentaryAction(self, commentary):
        command = "COMMENTARY:::{0}:::{1}".format(commentary, self.parent.verseReference("main")[1])
        self.runCommmand(command)
        # index = self.parent.commentaryList.index(commentary)
        # self.parent.changeCommentaryVersion(index)
        command = "_commentaryinfo:::{0}".format(commentary)
        self.parent.runTextCommand(command)

    def bookIntroAction(self, commentary):
        command = "COMMENTARY:::{0}:::{1}".format(commentary, BibleBooks().abbrev["eng"][str(config.mainB)][-1])
        self.runCommmand(command)
        command = "_commentaryinfo:::{0}".format(commentary)
        self.parent.runTextCommand(command)

    def devotionalAction(self, devotional):
        command = "DEVOTIONAL:::{0}".format(devotional)
        self.runCommmand(command)

    def lexiconAction(self, lexicon):
        searchString = self.searchLineEdit.text()
        if ":::" not in searchString:
            TextCommandParser.last_lexicon_entry = searchString
        command = "SEARCHLEXICON:::{0}:::{1}".format(lexicon, TextCommandParser.last_lexicon_entry)
        self.runCommmand(command)

    def dictionaryAction(self, dictionary):
        searchString = self.searchLineEdit.text()
        if ":::" not in searchString:
            TextCommandParser.last_text_search = searchString
        command = "SEARCHTOOL:::{0}:::{1}".format(dictionary, TextCommandParser.last_text_search)
        self.runCommmand(command)

    def runCommmand(self, command):
        self.searchLineEdit.setText(command)
        self.parent.runTextCommand(command)
        self.parent.textCommandLineEdit.setText(command)
        self.populateBooksButtons(config.mainText)

    def selectCollection(self, collection):

        if not collection == "All":
            biblesInCollection = config.bibleCollections[collection]
        for bible in self.bibleButtons.keys():
            button = self.bibleButtons[bible]
            if collection == "All":
                button.setEnabled(True)
                button.setStyleSheet("")
            else:
                if bible in biblesInCollection:
                    button.setEnabled(True)
                    button.setStyleSheet("")
                else:
                    button.setEnabled(False)
                    button.setStyleSheet(self.textButtonStyleDisabled)

    def activeCommentaries(self):
        activeCommentaries = [item[0] for item in
                              Commentary().getCommentaryListThatHasBookAndChapter(config.mainB, config.mainC)]
        for commentary in self.commentaryButtons.keys():
            button = self.commentaryButtons[commentary]
            if commentary in activeCommentaries:
                button.setEnabled(True)
                button.setStyleSheet("")
            else:
                button.setEnabled(False)
                button.setStyleSheet(self.textButtonStyleDisabled)

    def activeBookIntros(self):
        activeCommentaries = [item[0] for item in
                              Commentary().getCommentaryListThatHasBookAndChapter(config.mainB, 0)]
        for commentary in self.bookIntroButtons.keys():
            button = self.bookIntroButtons[commentary]
            if commentary in activeCommentaries:
                button.setEnabled(True)
                button.setStyleSheet("")
            else:
                button.setEnabled(False)
                button.setStyleSheet(self.textButtonStyleDisabled)

## Standalone development code

class DummyParent():
    def runTextCommand(self, command):
        print(command)

    def verseReference(self, command):
        return ['', '']


if __name__ == "__main__":
   import sys
   from uniquebible import config
   from uniquebible.util.LanguageUtil import LanguageUtil
   from uniquebible.util.ConfigUtil import ConfigUtil
   from PySide6.QtCore import QCoreApplication

   config.mainText = ""
   config.mainB = ""
   config.mainC = ""
   config.mainV = ""
   config.commentaryB = ""
   config.commentaryC = ""
   config.thisTranslation = LanguageUtil.loadTranslation("en_US")
   config.parserStandarisation = 'NO'
   config.standardAbbreviation = 'ENG'
   config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"
   config.updateModules("OfflineTts", False)

   ConfigUtil.setup()
   config.noQt = False
   # config.bibleCollections["Custom"] = ['ABP', 'ACV']
   # config.bibleCollections["King James"] = ['KJV', 'KJVx', 'KJVA', 'KJV1611', 'KJV1769x']
   config.thisTranslation = LanguageUtil.loadTranslation("en_US")
   QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
   app = QApplication(sys.argv)
   ui = MiniControl(DummyParent())
   ui.setMinimumHeight(400)
   ui.setMinimumWidth(450)
   ui.show()
   sys.exit(app.exec_())