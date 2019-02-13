import os, sys, re, config, webbrowser, platform, subprocess, zipfile, gdown
from PySide2.QtCore import QUrl, Qt, QEvent
from PySide2.QtGui import QIcon, QGuiApplication
from PySide2.QtWidgets import (QAction, QGridLayout, QInputDialog, QLineEdit, QMainWindow, QMessageBox, QPushButton, QToolBar, QWidget, QDialog, QFileDialog, QLabel, QFrame, QTextEdit, QProgressBar)
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from TextCommandParser import TextCommandParser
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite
from TextFileReader import TextFileReader
from NoteSqlite import NoteSqlite
from ThirdParty import Converter
from shutil import copyfile

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.textCommandParser = TextCommandParser(self)

        self.setWindowTitle('Unique Bible App')
        
        appIconFile = os.path.join("htmlResources", "theText.png")
        appIcon = QIcon(appIconFile)
        QGuiApplication.setWindowIcon(appIcon)
        
        self.create_menu()
        self.setupToolBar()
        self.setupSecondToolBar()
        self.setupBaseUrl()
        
        self.centralWidget = CentralWidget(self)
        self.mainView = self.centralWidget.mainView
        self.mainPage = self.mainView.page()
        self.mainPage.titleChanged.connect(self.mainTextCommandChanged)
        self.mainPage.loadFinished.connect(self.finishMainViewLoading)
        self.studyView = self.centralWidget.studyView
        self.studyPage = self.studyView.page()
        self.studyPage.titleChanged.connect(self.studyTextCommandChanged)
        self.studyPage.loadFinished.connect(self.finishStudyViewLoading)
        self.instantView = self.centralWidget.instantView
        self.instantPage = self.instantView.page()
        self.instantPage.titleChanged.connect(self.instantTextCommandChanged)
        self.setCentralWidget(self.centralWidget)

        # variable to check if notes in editor been modified
        self.noteSaved = True

        # variables to work with dialog

        frameStyle = QFrame.Sunken | QFrame.Panel

        self.openFileNameLabel = QLabel()
        self.openFileNameLabel.setFrameStyle(frameStyle)
        
        self.openFilesPath = ""
        
        self.directoryLabel = QLabel()
        self.directoryLabel.setFrameStyle(frameStyle)

    def __del__(self):
        del self.textCommandParser

    def event(self, event):
        if event.type() == QEvent.KeyRelease and event.key() == Qt.Key_Tab:
            self.textCommandLineEdit.setFocus()
            return True
        return QWidget.event(self, event)

    def downloadHelper(self, databaseInfo):
        self.downloader = Downloader(self, databaseInfo)
        self.downloader.show()

    def bcvToVerseReference(self, b, c, v):
        parser = BibleVerseParser(config.parserStandarisation)
        verseReference = parser.bcvToVerseReference(b, c, v)
        del parser
        return verseReference

    def create_menu(self):
        
        menu1 = self.menuBar().addMenu("&UniqueBible.app")
        appIcon = QIcon(os.path.join("htmlResources", "theText.png"))
        quit_action = QAction(appIcon, "E&xit", self, shortcut = "Ctrl+Q", triggered=qApp.quit)
        menu1.addAction(quit_action)
        
        menu2 = self.menuBar().addMenu("&View")
        menu2.addAction(QAction("&Full Screen", self, triggered=self.fullsizeWindow))
        menu2.addAction(QAction("&Resize", self, triggered=self.twoThirdWindow))
        menu2.addSeparator()
        menu2.addAction(QAction("&Top Half", self, shortcut = "Ctrl+T", triggered=self.halfScreenHeight))
        menu2.addAction(QAction("&Left Half", self, shortcut = "Ctrl+L", triggered=self.halfScreenWidth))

        menu3 = self.menuBar().addMenu("&Display")
        menu3.addAction(QAction("&Main Toolbar [Hide / Show]", self, triggered=self.hideShowToolBar))
        menu3.addAction(QAction("&Action Toolbar [Hide / Show]", self, triggered=self.hideShowSecondToolBar))
        menu3.addSeparator()
        menu3.addAction(QAction("&Secondary Window [Hide / Resize]", self, shortcut = "Ctrl+P", triggered=self.parallel))
        menu3.addAction(QAction("Li&ghtning Window [Hide / Show]", self, shortcut = "Ctrl+G", triggered=self.instant))
        menu3.addSeparator()
        menu3.addAction(QAction("L&ightning [On / Off]", self, shortcut = "Ctrl+=", triggered=self.enableInstantButtonClicked))
        menu3.addSeparator()
        menu3.addAction(QAction("&Larger Font", self, shortcut = "Ctrl++", triggered=self.largerFont))
        menu3.addAction(QAction("&Smaller Font", self, shortcut = "Ctrl+-", triggered=self.smallerFont))

        menu8 = self.menuBar().addMenu("&History")
        menu8.addAction(QAction("&Main", self, shortcut = "Ctrl+'", triggered=self.mainHistoryButtonClicked))
        menu8.addAction(QAction("&Back", self, shortcut = "Ctrl+[", triggered=self.back))
        menu8.addAction(QAction("&Forward", self, shortcut = "Ctrl+]", triggered=self.forward))
        menu8.addSeparator()
        menu8.addAction(QAction("&Secondary", self, shortcut = 'Ctrl+"', triggered=self.studyHistoryButtonClicked))
        menu8.addAction(QAction("&Back", self, shortcut = "Ctrl+{", triggered=self.studyBack))
        menu8.addAction(QAction("&Forward", self, shortcut = "Ctrl+}", triggered=self.studyForward))

        menu4 = self.menuBar().addMenu("&Study")
        menu4.addAction(QAction("Smart Indexes", self, triggered=self.runINDEX))
        menu4.addAction(QAction("Commentary", self, triggered=self.runCOMMENTARY))
        menu4.addSeparator()
        menu4.addAction(QAction("Translations", self, triggered=self.runTRANSLATION))
        menu4.addAction(QAction("Discourse", self, triggered=self.runDISCOURSE))
        menu4.addAction(QAction("Words", self, triggered=self.runWORDS))
        menu4.addAction(QAction("TDW Combo", self, triggered=self.runCOMBO))
        menu4.addSeparator()
        menu4.addAction(QAction("Scroll Mapper", self, triggered=self.runCROSSREFERENCE))
        menu4.addAction(QAction("TSK (Enhanced)", self, triggered=self.runTSKE))
        menu4.addSeparator()
        menu4.addAction(QAction("Compare All Versions", self, triggered=self.runCOMPARE))
        menu4.addAction(QAction("Compare with ...", self, triggered=self.mainRefButtonClicked))
        menu4.addAction(QAction("Parallel with ...", self, triggered=self.mainRefButtonClicked))
        menu4.addSeparator()

        menu5 = self.menuBar().addMenu("&Search")
        menu5.addAction(QAction("&Last Main Bible", self, shortcut = "Ctrl+1", triggered=self.displaySearchBibleCommand))
        menu5.addAction(QAction("&Last Secondary Bible", self, shortcut = "Ctrl+2", triggered=self.displaySearchStudyBibleCommand))
        menu5.addSeparator()
        menu5.addAction(QAction("&Last Opened Dictionary", self, shortcut = "Ctrl+3", triggered=self.searchCommandBibleDictionary))
        menu5.addAction(QAction("&Last Opened Encyclopedia", self, shortcut = "Ctrl+4", triggered=self.searchCommandBibleEncyclopedia))
        menu5.addAction(QAction("&Last Opened Book", self, shortcut = "Ctrl+5", triggered=self.displaySearchBookCommand))
        menu5.addSeparator()
        menu5.addAction(QAction("&Bible Charcters", self, shortcut = "Ctrl+6", triggered=self.searchCommandBibleCharacter))
        menu5.addAction(QAction("&Bible Names", self, shortcut = "Ctrl+7", triggered=self.searchCommandBibleName))
        menu5.addAction(QAction("&Bible Locations", self, shortcut = "Ctrl+8", triggered=self.searchCommandBibleLocation))
        menu5.addAction(QAction("&Bible Topics", self, shortcut = "Ctrl+9", triggered=self.searchCommandBibleTopic))

        menu6 = self.menuBar().addMenu("&Notes")
        menu6.addAction(QAction("&Note on Main Chapter", self, triggered=self.openMainChapterNote))
        menu6.addAction(QAction("&Note on Secondary Chapter", self, triggered=self.openStudyChapterNote))
        menu6.addAction(QAction("&Search Notes on Chapters", self, triggered=self.searchCommandChapterNote))
        menu6.addSeparator()
        menu6.addAction(QAction("&Note on Main Verse", self, triggered=self.openMainVerseNote))
        menu6.addAction(QAction("&Note on Secondary Verse", self, triggered=self.openStudyVerseNote))
        menu6.addAction(QAction("&Search Notes on Verses", self, triggered=self.searchCommandVerseNote))

        menu7 = self.menuBar().addMenu("&Topics")
        menu7.addAction(QAction("&Create a Topical Note", self, shortcut = "Ctrl+N", triggered=self.createNewNoteFile))
        menu7.addSeparator()
        menu7.addAction(QAction("&Open Note Files", self, shortcut = "Ctrl+F", triggered=self.openTextFileDialog))
        menu7.addAction(QAction("&Recent Files", self, shortcut = "Ctrl+E", triggered=self.openExternalFileHistory))
        menu7.addAction(QAction("&Read Last Opened File", self, triggered=self.externalFileButtonClicked))
        menu7.addAction(QAction("&Edit Last Opened File", self, triggered=self.editExternalFileButtonClicked))
        menu7.addSeparator()
        menu7.addAction(QAction("&Paste from Clipboard", self, shortcut = "Ctrl+^", triggered=self.pasteFromClipboard))

        menu9 = self.menuBar().addMenu("&Resources")
        menu9.addAction(QAction("&Install Formatted Bibles", self, triggered=self.installMarvelBibles))
        menu9.addAction(QAction("&Install Bible Commentaries", self, triggered=self.installMarvelCommentaries))
        menu9.addAction(QAction("&Install Marvel.bible Datasets", self, triggered=self.installMarvelDatasets))
        menu9.addSeparator()
        menu9.addAction(QAction("&Import 3rd Party Modules", self, triggered=self.importModules))
        menu9.addSeparator()
        menu9.addAction(QAction("&Tag References in a File", self, shortcut = "Ctrl+%", triggered=self.tagFile))
        menu9.addAction(QAction("&Tag References in Multiple Files", self, shortcut = "Ctrl+&", triggered=self.tagFiles))
        menu9.addAction(QAction("&Tag References in a Folder", self, shortcut = "Ctrl+*", triggered=self.tagFolder))

        menu10 = self.menuBar().addMenu("&Information")
        menu10.addAction(QAction("&BibleTools.app", self, triggered=self.openBibleTools))
        menu10.addAction(QAction("&UniqueBible.app", self, triggered=self.openUniqueBible))
        menu10.addAction(QAction("&Marvel.bible", self, triggered=self.openMarvelBible))
        menu10.addAction(QAction("&BibleBento.com", self, triggered=self.openBibleBento))
        menu10.addAction(QAction("&OpenGNT.com", self, triggered=self.openOpenGNT))
        menu10.addSeparator()
        menu10.addAction(QAction("&GitHub Repositories", self, triggered=self.openSource))
        menu10.addAction(QAction("&Unique Bible", self, triggered=self.openUniqueBibleSource))
        menu10.addAction(QAction("&Open Hebrew Bible", self, triggered=self.openHebrewBibleSource))
        menu10.addAction(QAction("&Open Greek New Testament", self, triggered=self.openOpenGNTSource))
        menu10.addSeparator()
        menu10.addAction(QAction("&Credits", self, triggered=self.openCredits))
        menu10.addSeparator()
        menu10.addAction(QAction("&Contact Eliran Wong", self, triggered=self.contactEliranWong))

    def setupToolBar(self):
        self.toolBar = QToolBar()
        self.toolBar.setWindowTitle("Text Command")
        self.toolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.toolBar)

        mainHistoryButton = QPushButton()
        mainHistoryButtonFile = os.path.join("htmlResources", "history.png")
        mainHistoryButton.setIcon(QIcon(mainHistoryButtonFile))
        mainHistoryButton.clicked.connect(self.mainHistoryButtonClicked)
        self.toolBar.addWidget(mainHistoryButton)

        backButton = QPushButton()
        leftButtonFile = os.path.join("htmlResources", "left.png")
        backButton.setIcon(QIcon(leftButtonFile))
        backButton.clicked.connect(self.back)
        self.toolBar.addWidget(backButton)

        forwardButton = QPushButton()
        rightButtonFile = os.path.join("htmlResources", "right.png")
        forwardButton.setIcon(QIcon(rightButtonFile))
        forwardButton.clicked.connect(self.forward)
        self.toolBar.addWidget(forwardButton)

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        self.toolBar.addWidget(self.textCommandLineEdit)

        studyBackButton = QPushButton()
        leftButtonFile = os.path.join("htmlResources", "left.png")
        studyBackButton.setIcon(QIcon(leftButtonFile))
        studyBackButton.clicked.connect(self.studyBack)
        self.toolBar.addWidget(studyBackButton)

        studyForwardButton = QPushButton()
        rightButtonFile = os.path.join("htmlResources", "right.png")
        studyForwardButton.setIcon(QIcon(rightButtonFile))
        studyForwardButton.clicked.connect(self.studyForward)
        self.toolBar.addWidget(studyForwardButton)

        studyHistoryButton = QPushButton()
        studyHistoryButtonFile = os.path.join("htmlResources", "history.png")
        studyHistoryButton.setIcon(QIcon(studyHistoryButtonFile))
        studyHistoryButton.clicked.connect(self.studyHistoryButtonClicked)
        self.toolBar.addWidget(studyHistoryButton)

        #self.toolBar.addSeparator()

        self.parallelMode = 1 # default parallel mode
        parallelButton = QPushButton()
        parallelButtonFile = os.path.join("htmlResources", "parallel.png")
        parallelButton.setIcon(QIcon(parallelButtonFile))
        parallelButton.clicked.connect(self.parallel)
        self.toolBar.addWidget(parallelButton)

        # put the secondary toolbar below the main one
        self.addToolBarBreak()

    def setupSecondToolBar(self):
        textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"
        
        self.secondToolBar = QToolBar()
        self.secondToolBar.setWindowTitle("Special Features")
        self.secondToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.secondToolBar)

        searchBibleButton = QPushButton()
        searchBibleButtonFile = os.path.join("htmlResources", "search.png")
        searchBibleButton.setIcon(QIcon(searchBibleButtonFile))
        searchBibleButton.clicked.connect(self.displaySearchBibleCommand)
        self.secondToolBar.addWidget(searchBibleButton)

        self.mainRefButton = QPushButton(self.verseReference("main"))
        self.mainRefButton.setStyleSheet(textButtonStyle)
        self.mainRefButton.clicked.connect(self.mainRefButtonClicked)
        self.secondToolBar.addWidget(self.mainRefButton)

        openChapterNoteButton = QPushButton()
        openChapterNoteButtonFile = os.path.join("htmlResources", "noteChapter.png")
        openChapterNoteButton.setIcon(QIcon(openChapterNoteButtonFile))
        openChapterNoteButton.clicked.connect(self.openMainChapterNote)
        self.secondToolBar.addWidget(openChapterNoteButton)

        openVerseNoteButton = QPushButton()
        openVerseNoteButtonFile = os.path.join("htmlResources", "noteVerse.png")
        openVerseNoteButton.setIcon(QIcon(openVerseNoteButtonFile))
        openVerseNoteButton.clicked.connect(self.openMainVerseNote)
        self.secondToolBar.addWidget(openVerseNoteButton)

        self.secondToolBar.addSeparator()

        searchStudyBibleButton = QPushButton()
        searchStudyBibleButtonFile = os.path.join("htmlResources", "search.png")
        searchStudyBibleButton.setIcon(QIcon(searchStudyBibleButtonFile))
        searchStudyBibleButton.clicked.connect(self.displaySearchStudyBibleCommand)
        self.secondToolBar.addWidget(searchStudyBibleButton)

        self.studyRefButton = QPushButton(self.verseReference("study"))
        self.studyRefButton.setStyleSheet(textButtonStyle)
        self.studyRefButton.clicked.connect(self.studyRefButtonClicked)
        self.secondToolBar.addWidget(self.studyRefButton)

        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
        self.commentaryRefButton.setStyleSheet(textButtonStyle)
        self.commentaryRefButton.clicked.connect(self.commentaryRefButtonClicked)
        self.secondToolBar.addWidget(self.commentaryRefButton)

        self.secondToolBar.addSeparator()

        searchBookButton = QPushButton()
        searchBookButtonFile = os.path.join("htmlResources", "search.png")
        searchBookButton.setIcon(QIcon(searchBookButtonFile))
        searchBookButton.clicked.connect(self.displaySearchBookCommand)
        self.secondToolBar.addWidget(searchBookButton)

        self.bookButton = QPushButton(config.book)
        self.bookButton.setStyleSheet(textButtonStyle)
        self.bookButton.clicked.connect(self.openBookMenu)
        self.secondToolBar.addWidget(self.bookButton)

        #self.secondToolBar.addSeparator()

        #fontMinusButton = QPushButton()
        #fontMinusButtonFile = os.path.join("htmlResources", "fontMinus.png")
        #fontMinusButton.setIcon(QIcon(fontMinusButtonFile))
        #fontMinusButton.clicked.connect(self.smallerFont)
        #self.secondToolBar.addWidget(fontMinusButton)

        #fontPlusButton = QPushButton()
        #fontPlusButtonFile = os.path.join("htmlResources", "fontPlus.png")
        #fontPlusButton.setIcon(QIcon(fontPlusButtonFile))
        #fontPlusButton.clicked.connect(self.largerFont)
        #self.secondToolBar.addWidget(fontPlusButton)

        self.secondToolBar.addSeparator()

        newFileButton = QPushButton()
        newFileButtonFile = os.path.join("htmlResources", "newfile.png")
        newFileButton.setIcon(QIcon(newFileButtonFile))
        newFileButton.clicked.connect(self.createNewNoteFile)
        self.secondToolBar.addWidget(newFileButton)

        openFileButton = QPushButton()
        openFileButtonFile = os.path.join("htmlResources", "open.png")
        openFileButton.setIcon(QIcon(openFileButtonFile))
        openFileButton.clicked.connect(self.openTextFileDialog)
        self.secondToolBar.addWidget(openFileButton)

        self.externalFileButton = QPushButton(self.getLastExternalFileName())
        self.externalFileButton.setStyleSheet(textButtonStyle)
        self.externalFileButton.clicked.connect(self.externalFileButtonClicked)
        self.secondToolBar.addWidget(self.externalFileButton)

        editExternalFileButton = QPushButton()
        editExternalFileButtonFile = os.path.join("htmlResources", "edit.png")
        editExternalFileButton.setIcon(QIcon(editExternalFileButtonFile))
        editExternalFileButton.clicked.connect(self.editExternalFileButtonClicked)
        self.secondToolBar.addWidget(editExternalFileButton)

        self.secondToolBar.addSeparator()

        self.enableInstantButton = QPushButton()
        enableInstantButtonFile = os.path.join("htmlResources", self.getInstantInformation())
        self.enableInstantButton.setIcon(QIcon(enableInstantButtonFile))
        self.enableInstantButton.clicked.connect(self.enableInstantButtonClicked)
        self.secondToolBar.addWidget(self.enableInstantButton)

        self.instantMode = 1 # default parallel mode
        instantButton = QPushButton()
        instantButtonFile = os.path.join("htmlResources", "lightning.png")
        instantButton.setIcon(QIcon(instantButtonFile))
        instantButton.clicked.connect(self.instant)
        self.secondToolBar.addWidget(instantButton)

        self.secondToolBar.addSeparator()

    # install marvel data
    def installMarvelBibles(self):
        bibles = {
            "American Standard Version": (("marvelData", "bibles", "ASV.bible"), "1psDvIqtxjaE0ax0ewyPIF-ueah1I8RG1"),
            "Berean Study Bible": (("marvelData", "bibles", "BSB.bible"), "1dVnS6sFqxVSUAZZXwCUhecK2gy7T5Ung"),
            "Chinese Union Version (Traditional Chinese)": (("marvelData", "bibles", "CUV.bible"), "1m1ml4xt2zjFoY5CQ6rmqXhvLzP6uq-mg"),
            "Chinese Union Version (Simplified Chinese)": (("marvelData", "bibles", "CUVs.bible"), "1feAuYDpbw_wDgFecyfg4lycpiIJhchEE"),
            "International Standard Version": (("marvelData", "bibles", "ISV.bible"), "141o3qUOOeDLh0T5QDTbDynn86CDqkRG3"),
            "King James Version": (("marvelData", "bibles", "KJV.bible"), "1Nd3cPu43tOUzIXgpCG_IrR6spAgt9PIQ"),
            "Lexhame English Bible": (("marvelData", "bibles", "LEB.bible"), "1gN3HOe57EdsSTbZ3qeUlwj9lrMw2ZBy6"),
            "Septuagint / LXX [main]": (("marvelData", "bibles", "LXX1.bible"), "1JFIQ_Ef4sF_VBQJ8PXWLxcjnk8XWgf8x"),
            "Septuagint / LXX [alternate]": (("marvelData", "bibles", "LXX2.bible"), "1FaDp0qdV7Op_XlK_wwB3WyE5dN-_wPED"),
            "Septuagint / LXX interlinear [main]": (("marvelData", "bibles", "LXX1i.bible"), "1BpmD_I2Z_8u-xuRf8DCUYdm2AVC9EXlk"),
            "Septuagint / LXX interlinear [alternate]": (("marvelData", "bibles", "LXX2i.bible"), "19snsLLHK66Ks4tojubkUMG5MfVIv6-g7"),
            "Marvel Original Bible": (("marvelData", "bibles", "MOB.bible"), "1y7Cs5MO4ONQwZOnZC52jKnFFCDk52t_a"),
            "Marvel Annotated Bible": (("marvelData", "bibles", "MAB.bible"), "1QXCwFnHug88wy92pJwFvwZa_M5Gx1ZUX"),
            "Marvel Interlinear Bible": (("marvelData", "bibles", "MIB.bible"), "1W1VuvZMca9ruPBkVKV00F8JI-vPHodwy"),
            "Marvel Parallel Bible": (("marvelData", "bibles", "MPB.bible"), "1co9IO4TRqFqalCTomxT-qpkeTM8hrXnA"),
            "Marvel Trilingual Bible": (("marvelData", "bibles", "MTB.bible"), "1Qp8Z24xrUBPxDZyH9tr7U3d2q4hhW83O"),
            "New English Translation": (("marvelData", "bibles", "NET.bible"), "10FcyT81ZCci7VEB4_ejUn6u2hDkHmfuA"),
            "unfoldingWord Literal Text": (("marvelData", "bibles", "ULT.bible"), "1i6upSEbtskX6P-hplZHa91EW8XU1yFPR"),
            "unfoldingWord Simplified Text": (("marvelData", "bibles", "UST.bible"), "1TPUIiCHefsDO2nuTW_Dr6GeeQbdJQOrJ"),
            "World English Bible": (("marvelData", "bibles", "WEB.bible"), "1QiA9NjTK5TLpbft3zaLnkKHjRHjDFGy5"),
        }
        items = [bible for bible in bibles.keys() if not os.path.isfile(os.path.join(*bibles[bible][0]))]
        if not items:
            items = ["[All Installed]"]
        item, ok = QInputDialog.getItem(self, "Install Formatted Bibles",
                "Available Modules:", items, 0, False)
        if ok and item and not item == "[All Installed]":
            self.downloadHelper(bibles[item])

    def installMarvelCommentaries(self):
        commentaries = {
            "Notes on the Old and New Testaments (Barnes) [26 vol.]": (("marvelData", "commentaries", "cBarnes.commentary"), "13uxButnFH2NRUV-YuyRZYCeh1GzWqO5J"),
            "Commentary on the Old and New Testaments (Benson) [5 vol.]": (("marvelData", "commentaries", "cBenson.commentary"), "1MSRUHGDilogk7_iZHVH5GWkPyf8edgjr"),
            "Biblical Illustrator (Exell) [58 vol.]": (("marvelData", "commentaries", "cBI.commentary"), "1DUATP_0M7SwBqsjf20YvUDblg3_sOt2F"),
            "Complete Summary of the Bible (Brooks) [2 vol.]": (("marvelData", "commentaries", "cBrooks.commentary"), "1pZNRYE6LqnmfjUem4Wb_U9mZ7doREYUm"),
            "John Calvin's Commentaries (Calvin) [22 vol.]": (("marvelData", "commentaries", "cCalvin.commentary"), "1FUZGK9n54aXvqMAi3-2OZDtRSz9iZh-j"),
            "Cambridge Bible for Schools and Colleges (Cambridge) [57 vol.]": (("marvelData", "commentaries", "cCBSC.commentary"), "1IxbscuAMZg6gQIjzMlVkLtJNDQ7IzTh6"),
            "Critical And Exegetical Commentary on the NT (Meyer) [20 vol.]": (("marvelData", "commentaries", "cCECNT.commentary"), "1MpBx7z6xyJYISpW_7Dq-Uwv0rP8_Mi-r"),
            "Cambridge Greek Testament for Schools and Colleges (Cambridge) [21 vol.]": (("marvelData", "commentaries", "cCGrk.commentary"), "1Jf51O0R911Il0V_SlacLQDNPaRjumsbD"),
            "Church Pulpit Commentary (Nisbet) [12 vol.]": (("marvelData", "commentaries", "cCHP.commentary"), "1dygf2mz6KN_ryDziNJEu47-OhH8jK_ff"),
            "Commentary on the Bible (Clarke) [6 vol.]": (("marvelData", "commentaries", "cClarke.commentary"), "1ZVpLAnlSmBaT10e5O7pljfziLUpyU4Dq"),
            "College Press Bible Study Textbook Series (College) [59 vol.]": (("marvelData", "commentaries", "cCPBST.commentary"), "14zueTf0ioI-AKRo_8GK8PDRKael_kB1U"),
            "Expositor's Bible Commentary (Nicoll) [49 vol.]": (("marvelData", "commentaries", "cEBC.commentary"), "1UA3tdZtIKQEx-xmXtM_SO1k8S8DKYm6r"),
            "Commentary for English Readers (Ellicott) [8 vol.]": (("marvelData", "commentaries", "cECER.commentary"), "1sCJc5xuxqDDlmgSn2SFWTRbXnHSKXeh_"),
            "Expositor's Greek New Testament (Nicoll) [5 vol.]": (("marvelData", "commentaries", "cEGNT.commentary"), "1ZvbWnuy2wwllt-s56FUfB2bS2_rZoiPx"),
            "Greek Testament Commentary (Alford) [4 vol.]": (("marvelData", "commentaries", "cGCT.commentary"), "1vK53UO2rggdcfcDjH6mWXAdYti4UbzUt"),
            "Exposition of the Entire Bible (Gill) [9 vol.]": (("marvelData", "commentaries", "cGill.commentary"), "1O5jnHLsmoobkCypy9zJC-Sw_Ob-3pQ2t"),
            "Exposition of the Old and New Testaments (Henry) [6 vol.]": (("marvelData", "commentaries", "cHenry.commentary"), "1m-8cM8uZPN-fLVcC-a9mhL3VXoYJ5Ku9"),
            "Horæ Homileticæ (Simeon) [21 vol.]": (("marvelData", "commentaries", "cHH.commentary"), "1RwKN1igd1RbN7phiJDiLPhqLXdgOR0Ms"),
            "International Critical Commentary, NT (1896-1929) [16 vol.]": (("marvelData", "commentaries", "cICCNT.commentary"), "1QxrzeeZYc0-GNwqwdDe91H4j1hGSOG6t"),
            "Jamieson, Fausset, and Brown Commentary (JFB) [6 vol.]": (("marvelData", "commentaries", "cJFB.commentary"), "1NT02QxoLeY3Cj0uA_5142P5s64RkRlpO"),
            "Commentary on the Old Testament (Keil & Delitzsch) [10 vol.]": (("marvelData", "commentaries", "cKD.commentary"), "1rFFDrdDMjImEwXkHkbh7-vX3g4kKUuGV"),
            "Commentary on the Holy Scriptures: Critical, Doctrinal, and Homiletical (Lange) [25 vol.]": (("marvelData", "commentaries", "cLange.commentary"), "1_PrTT71aQN5LJhbwabx-kjrA0vg-nvYY"),
            "Expositions of Holy Scripture (MacLaren) [32 vol.]": (("marvelData", "commentaries", "cMacL.commentary"), "1p32F9MmQ2wigtUMdCU-biSrRZWrFLWJR"),
            "Preacher's Complete Homiletical Commentary (Exell) [37 vol.]": (("marvelData", "commentaries", "cPHC.commentary"), "1xTkY_YFyasN7Ks9me3uED1HpQnuYI8BW"),
            "Pulpit Commentary (Spence) [23 vol.]": (("marvelData", "commentaries", "cPulpit.commentary"), "1briSh0oDhUX7QnW1g9oM3c4VWiThkWBG"),
            "Word Pictures in the New Testament (Robertson) [6 vol.]": (("marvelData", "commentaries", "cRob.commentary"), "17VfPe4wsnEzSbxL5Madcyi_ubu3iYVkx"),
            "Spurgeon's Expositions on the Bible (Spurgeon) [3 vol.]": (("marvelData", "commentaries", "cSpur.commentary"), "1OVsqgHVAc_9wJBCcz6PjsNK5v9GfeNwp"),
            "Word Studies in the New Testament (Vincent) [4 vol.]": (("marvelData", "commentaries", "cVincent.commentary"), "1ZZNnCo5cSfUzjdEaEvZ8TcbYa4OKUsox"),
            "John Wesley's Notes on the Whole Bible (Wesley) [3 vol.]": (("marvelData", "commentaries", "cWesley.commentary"), "1rerXER1ZDn4e1uuavgFDaPDYus1V-tS5"),
            "Commentary on the Old and New Testaments (Whedon) [14 vol.]": (("marvelData", "commentaries", "cWhedon.commentary"), "1FPJUJOKodFKG8wsNAvcLLc75QbM5WO-9"),
        }
        items = [commentary for commentary in commentaries.keys() if not os.path.isfile(os.path.join(*commentaries[commentary][0]))]
        if not items:
            items = ["[All Installed]"]
        item, ok = QInputDialog.getItem(self, "Install Bible Commentaries",
                "Available Modules:", items, 0, False)
        if ok and item and not item == "[All Installed]":
            self.downloadHelper(commentaries[item])

    def installMarvelDatasets(self):
        datasets = {
            "Core Datasets": (("marvelData", "bibles.sqlite"), "1w5cChadLpfJ51y9BBUdotV31PqVPbkWf"),
            "Search Engine": (("marvelData", "search.sqlite"), "1A4s8ewpxayrVXamiva2l1y1AinAcIKAh"),
            "Smart Indexes": (("marvelData", "indexes.sqlite"), "1Fdq3C9hyoyBX7riniByyZdW9mMoMe6EX"),
            "Chapter & Verse Notes": (("marvelData", "note.sqlite"), "1OcHrAXLS-OLDG5Q7br6mt2WYCedk8lnW"),
            "Bible Background Data": (("marvelData", "data", "exlb.data"), "1kA5appVfyQ1lWF1czEQWtts4idogHIpa"),
            "Bible Topics Data": (("marvelData", "data", "exlb.data"), "1kA5appVfyQ1lWF1czEQWtts4idogHIpa"),
            "Cross-reference Data": (("marvelData", "cross-reference.sqlite"), "1gZNqhwER_-IWYPaMNGZ229teJ5cSA7My"),
            "Dictionaries": (("marvelData", "data", "dictionary.data"), "1NfbkhaR-dtmT1_Aue34KypR3mfPtqCZn"),
            "Encyclopedia": (("marvelData", "data", "encyclopedia.data"), "1OuM6WxKfInDBULkzZDZFryUkU1BFtym8"),
            "Lexicons": (("marvelData", "data", "lexicon.data"), "1GFNnI1PtmPGhoEy6jfBP5U2Gi17Zr6fs"),
            "Book Modules": (("marvelData", "data", "book.data"), "1Oc5kt9V_zq-RgEwY-E_eQVVPoaqJujGm"),
            "Word Data": (("marvelData", "data", "word.data"), "1SN8fr2isJ4FtmvYVvBrO67TB-POmc2ta"),
            "Words Data": (("marvelData", "data", "words.data"), "13d3QeUHhlttgOQ_U7Ag1jgawqrXzOaBq"),
            "Clause Data": (("marvelData", "data", "clause.data"), "19LQlHw9c3V64AWZMr2_70loXfvNNN3JY"),
            "Translation Data": (("marvelData", "data", "translation.data"), "13d3QeUHhlttgOQ_U7Ag1jgawqrXzOaBq"),
            "Discourse Data": (("marvelData", "data", "discourse.data"), "13d3QeUHhlttgOQ_U7Ag1jgawqrXzOaBq"),
            "TDW Combo Data": (("marvelData", "data", "words.data"), "13d3QeUHhlttgOQ_U7Ag1jgawqrXzOaBq"),
        }
        items = [dataset for dataset in datasets.keys() if not os.path.isfile(os.path.join(*datasets[dataset][0]))]
        if not items:
            items = ["[All Installed]"]
        item, ok = QInputDialog.getItem(self, "Install Marvel.bible Datasets",
                "Available Modules:", items, 0, False)
        if ok and item and not item == "[All Installed]":
            self.downloadHelper(datasets[item])

    # Open text on studyView
    def openTextOnStudyView(self, text):
        # write text in a text file
        # reason: setHTML does not work with content larger than 2 MB
        outputFile = os.path.join("htmlResources", "study.html")
        fileObject = open(outputFile,'w')
        fileObject.write(text)
        fileObject.close()
        # open the text file with webview
        fullOutputPath = os.path.abspath(outputFile)
        self.studyView.load(QUrl.fromLocalFile(fullOutputPath))
        if self.parallelMode == 0:
            self.parallel()

    # warning for next action without saving modified notes
    def warningNotSaved(self):
        msgBox = QMessageBox(QMessageBox.Warning,
                "QMessageBox.warning()", "Notes are currently opened and modified.  Do you really want to continue, without saving the changes?",
                QMessageBox.NoButton, self)
        msgBox.addButton("Cancel", QMessageBox.AcceptRole)
        msgBox.addButton("&Continue", QMessageBox.RejectRole)
        if msgBox.exec_() == QMessageBox.AcceptRole:
            # Cancel
            return False
        else:
            # Continue
            return True

    # Actions - chapter / verse / new file note
    def createNewNoteFile(self):
        if self.noteSaved:
            self.noteEditor = NoteEditor(self, "file")
            self.noteEditor.show()
        elif self.warningNotSaved():
            self.noteEditor = NoteEditor(self, "file")
            self.noteEditor.show()
        else:
            self.noteEditor.raise_()

    def openNoteEditor(self, noteType):
        self.noteEditor = NoteEditor(self, noteType)
        self.noteEditor.show()

    def openMainChapterNote(self):
        self.openChapterNote(config.mainB, config.mainC)

    def openMainVerseNote(self):
        self.openVerseNote(config.mainB, config.mainC, config.mainV)

    def openStudyChapterNote(self):
        self.openChapterNote(config.studyB, config.studyC)

    def openStudyVerseNote(self):
        self.openVerseNote(config.studyB, config.studyC, config.studyV)

    def openChapterNote(self, b, c):
        reference = BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, 1)
        config.studyB, config.studyC, config.studyV = b, c, 1
        self.updateStudyRefButton()
        config.commentaryB, config.commentaryC, config.commentaryV = b, c, 1
        self.updateCommentaryRefButton()
        noteSqlite = NoteSqlite()
        note = "<p><b>Note on {0}</b> &ensp;<button class='feature' onclick='document.title=\"_editchapternote:::\"'>edit</button></p>{1}".format(reference[:-2], noteSqlite.displayChapterNote((b, c)))
        del noteSqlite
        note = self.htmlWrapper(note, True, "study", False)
        self.openTextOnStudyView(note)

    def openVerseNote(self, b, c, v):
        reference = BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)
        config.studyB, config.studyC, config.studyV = b, c, v
        self.updateStudyRefButton()
        config.commentaryB, config.commentaryC, config.commentaryV = b, c, v
        self.updateCommentaryRefButton()
        noteSqlite = NoteSqlite()
        note = "<p><b>Note on {0}</b> &ensp;<button class='feature' onclick='document.title=\"_editversenote:::\"'>edit</button></p>{1}".format(reference, noteSqlite.displayVerseNote((b, c, v)))
        del noteSqlite
        note = self.htmlWrapper(note, True, "study", False)
        self.openTextOnStudyView(note)

    # Actions - open text from external sources
    def htmlWrapper(self, text, parsing=False, view="study", linebreak=True):
        searchReplace1 = (
            ("\r\n|\r|\n", "<br>"),
            ("\t", "&emsp;&emsp;"),
        )
        searchReplace2 = (
            ("<br>(<table>|<ol>|<ul>)", r"\1"),
            ("(</table>|</ol>|</ul>)<br>", r"\1"),
            ("<a [^\n<>]*?href=['{0}]([^\n<>]*?)['{0}][^\n<>]*?>".format('"'), r"<a href='javascript:void(0)' onclick='website({0}\1{0})'>".format('"')),
            ("onclick='website\({0}([^\n<>]*?).uba{0}\)'".format('"'), r"onclick='uba({0}\1.uba{0})'".format('"'))
        )
        if linebreak:
            for search, replace in searchReplace1:
                text = re.sub(search, replace, text)        
        for search, replace in searchReplace2:
            text = re.sub(search, replace, text)
        if parsing:
            text = BibleVerseParser(config.parserStandarisation).parseText(text)
        if view == "main":
            activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.mainText, config.mainB, config.mainC, config.mainV)
        elif view == "study":
            activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.studyText, config.studyB, config.studyC, config.studyV)
        text = "<!DOCTYPE html><html><head><title>UniqueBible.app</title><link rel='stylesheet' type='text/css' href='theText.css'><script src='theText.js'></script><script src='w3.js'></script>{0}<script>var versionList = []; var compareList = []; var parallelList = [];</script></head><body style='font-size: {1}%;'><span id='v0.0.0'></span>{2}</body></html>".format(activeBCVsettings, config.fontSize, text)
        return text

    def pasteFromClipboard(self):
        clipboardText = qApp.clipboard().text()
        # note: use qApp.clipboard().setText to set text in clipboard
        self.openTextOnStudyView(self.htmlWrapper(clipboardText, True))

    def openTextFileDialog(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                "QFileDialog.getOpenFileName()",
                self.openFileNameLabel.text(),
                "UniqueBible.app Note Files (*.uba);;HTML Files (*.html);;HTM Files (*.htm);;Word Documents (*.docx);;Plain Text Files (*.txt);;PDF Files (*.pdf);;All Files (*)", "", options)
        if fileName:
            self.openTextFile(fileName)

    def openTextFile(self, fileName):
        functions = {
            "pdf": self.openPdfFile,
            "docx": self.openDocxFile,
            "uba": self.openUbaFile,
            "html": self.openUbaFile,
            "htm": self.openUbaFile,
        }
        function = functions.get(fileName.split(".")[-1].lower(), self.openTxtFile)
        function(fileName)
        self.addExternalFileHistory(fileName)
        self.setExternalFileButton()

    def addExternalFileHistory(self, fileName):
        externalFileHistory = config.history['external']
        if externalFileHistory == [] or externalFileHistory[-1] != fileName:
            if fileName in externalFileHistory:
                externalFileHistory.remove(fileName)
            externalFileHistory.append(fileName)

    def setExternalFileButton(self):
        self.externalFileButton.setText(self.getLastExternalFileName())

    def getLastExternalFileName(self):
        externalFileHistory = config.history["external"]
        if externalFileHistory:
            return os.path.split(externalFileHistory[-1])[-1]
        else:
            return "[open file]"

    def externalFileButtonClicked(self):
        externalFileHistory = config.history["external"]
        if externalFileHistory:
            self.openExternalFileHistoryRecord(-1)
        else:
            self.openTextFileDialog()

    def editExternalFileButtonClicked(self):
        externalFileHistory = config.history["external"]
        if externalFileHistory:
            self.editExternalFileHistoryRecord(-1)
        else:
            self.openTextFileDialog()

    def editExternalFileHistoryRecord(self, record):
        file = config.history["external"][record]
        fileExtension = file.split(".")[-1].lower()
        directEdit = ("uba", "html", "htm")
        if fileExtension in directEdit:
            if self.noteSaved:
                self.noteEditor = NoteEditor(self, "file", file)
                self.noteEditor.show()
            elif self.warningNotSaved():
                self.noteEditor = NoteEditor(self, "file", file)
                self.noteEditor.show()
            else:
                self.noteEditor.raise_()
        else:
            if platform.system() == "Linux":
                subprocess.call(["xdg-open", file])
            elif platform.system() == "Darwin":
                os.system("open {0}".format(file))
            elif platform.system() == "Windows":
                os.system("start {0}".format(file))

    def openExternalFileHistoryRecord(self, record):
        self.openTextFile(config.history["external"][record])

    def openExternalFileHistory(self):
        self.studyView.setHtml(self.getHistory("external"), baseUrl)

    def openTxtFile(self, fileName):
        if fileName:
            text = TextFileReader().readTxtFile(fileName)
            text = self.htmlWrapper(text, True)
            self.openTextOnStudyView(text)

    def openUbaFile(self, fileName):
        if fileName:
            text = TextFileReader().readTxtFile(fileName)
            text = self.htmlWrapper(text, True, "study", False)
            self.openTextOnStudyView(text)

    def openPdfFile(self, fileName):
        if fileName:
            text = TextFileReader().readPdfFile(fileName)
            text = self.htmlWrapper(text, True)
            self.openTextOnStudyView(text)

    def openDocxFile(self, fileName):
        if fileName:
            text = TextFileReader().readDocxFile(fileName)
            text = self.htmlWrapper(text, True)
            self.openTextOnStudyView(text)

    # import 3rd party modules
    def importModules(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                "QFileDialog.getOpenFileName()",
                self.openFileNameLabel.text(),
                "MySword Bibles (*.bbl.mybible);;MySword Dictionaries (*.dct.mybible)", "", options)
        if fileName:
            if fileName.endswith(".dct.mybible"):
                self.importMySwordDictionary(fileName)
            elif fileName.endswith(".bbl.mybible"):
                self.importMySwordBible(fileName)

    def importMySwordDictionary(self, fileName):
        *_, name = os.path.split(fileName)
        destination = os.path.join("thirdParty", "dictionaries", name)
        try:
            copyfile(fileName, destination)
            self.completeImport()
        except:
            print("Failed to copy '{0}'.".format(fileName))

    def importMySwordBible(self, fileName):
        Converter().importMySwordBible(fileName)
        self.completeImport()

    def completeImport(self):
        self.mainPage.runJavaScript("alert('3rd Party Module Installed.')")

    # Actions - tag files with BibleVerseParser
    def onTaggingCompleted(self):
        self.mainPage.runJavaScript("alert('Finished. Tagged file(s) is/are named with a prefix \"tagged_\".')")

    def tagFile(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                "QFileDialog.getOpenFileName()",
                self.openFileNameLabel.text(),
                "All Files (*);;Text Files (*.txt);;CSV Files (*.csv);;TSV Files (*.tsv)", "", options)
        if fileName:
            BibleVerseParser(config.parserStandarisation).startParsing(fileName)
            self.onTaggingCompleted()

    def tagFiles(self):
        options = QFileDialog.Options()
        files, filtr = QFileDialog.getOpenFileNames(self,
                "QFileDialog.getOpenFileNames()", self.openFilesPath,
                "All Files (*);;Text Files (*.txt);;CSV Files (*.csv);;TSV Files (*.tsv)", "", options)
        if files:
            parser = BibleVerseParser(config.parserStandarisation)
            for file in files:
                parser.startParsing(file)
            del parser
            self.onTaggingCompleted()

    def tagFolder(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                "QFileDialog.getExistingDirectory()",
                self.directoryLabel.text(), options)
        if directory:
            path, file = os.path.split(directory)
            outputFile = os.path.join(path, "output_{0}".format(file))
            BibleVerseParser(config.parserStandarisation).startParsing(directory)
            self.onTaggingCompleted()

    # Actions - hide / show tool bars
    def hideShowToolBar(self):
        if self.toolBar.isVisible():
            self.toolBar.hide()
        else:
            self.toolBar.show()

    def hideShowSecondToolBar(self):
        if self.secondToolBar.isVisible():
            self.secondToolBar.hide()
        else:
            self.secondToolBar.show()

    # Actions - book features
    def openBookMenu(self):
        self.runTextCommand("_book:::", False, "main")

    def displaySearchBookCommand(self):
        config.bookSearchString = ""
        self.textCommandLineEdit.setText("SEARCHBOOK:::{0}:::".format(config.book))
        self.textCommandLineEdit.setFocus()

    # Action - bible search commands
    def displaySearchBibleCommand(self):
        self.textCommandLineEdit.setText("SEARCH:::{0}:::".format(config.mainText))
        self.textCommandLineEdit.setFocus()

    def displaySearchStudyBibleCommand(self):
        self.textCommandLineEdit.setText("SEARCH:::{0}:::".format(config.studyText))
        self.textCommandLineEdit.setFocus()

    # Action - other search commands
    def searchCommandChapterNote(self):
        self.textCommandLineEdit.setText("SEARCHCHAPTERNOTE:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandVerseNote(self):
        self.textCommandLineEdit.setText("SEARCHVERSENOTE:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleDictionary(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(config.dictionary))
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleEncyclopedia(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(config.encyclopedia))
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleCharacter(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::EXLBP:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleName(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::HBN:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleLocation(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::EXLBL:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleTopic(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::EXLBT:::")
        self.textCommandLineEdit.setFocus()

    # Actions - open urls
    def openBibleTools(self):
        webbrowser.open("https://bibletools.app")

    def openUniqueBible(self):
        webbrowser.open("https://uniquebible.app")

    def openMarvelBible(self):
        webbrowser.open("https://marvel.bible")

    def openBibleBento(self):
        webbrowser.open("https://biblebento.com")
        
    def openOpenGNT(self):
        webbrowser.open("https://opengnt.com")

    def openSource(self):
        webbrowser.open("https://github.com/eliranwong/")

    def openUniqueBibleSource(self):
        webbrowser.open("https://github.com/eliranwong/UniqueBible")

    def openHebrewBibleSource(self):
        webbrowser.open("https://github.com/eliranwong/OpenHebrewBible")

    def openOpenGNTSource(self):
        webbrowser.open("https://github.com/eliranwong/OpenGNT")

    def openCredits(self):
        webbrowser.open("https://marvel.bible/resource.php")

    def contactEliranWong(self):
        webbrowser.open("https://marvel.bible/contact/contactform.php")

    # Actions - resize the main window
    def fullsizeWindow(self):
        self.resizeWindow(1, 1)

    def twoThirdWindow(self):
        self.resizeWindow(2/3, 2/3)

    def halfScreenHeight(self):
        self.resizeWindow(1, 1/2)

    def halfScreenWidth(self):
        self.resizeWindow(1/2, 1)

    def resizeWindow(self, widthFactor, heightFactor):
        availableGeometry = qApp.desktop().availableGeometry()
        self.resize(availableGeometry.width() * widthFactor, availableGeometry.height() * heightFactor)

    # Actions - hide / show / resize study & lightning views
    def instant(self):
        if self.instantMode == 0:
            self.instantMode = 1
            self.instantView.show()
            self.centralWidget.layout.setRowStretch(0, 10)
            self.centralWidget.layout.setRowStretch(1, 2)
        elif self.instantMode == 1:
            self.instantMode = 0
            self.centralWidget.layout.setRowStretch(0, 10)
            self.centralWidget.layout.setRowStretch(1, 0)
            self.instantView.hide()

    def parallel(self):
        parallelRatio = {
            0: (1, 0),
            1: (2, 1),
            2: (1, 1),
            3: (1, 2),
        }
        if self.parallelMode == 3:
            self.parallelMode = 0
            self.studyView.hide()
        else:
            self.parallelMode += 1
            self.studyView.show()
        ratio = parallelRatio[self.parallelMode]
        self.centralWidget.layout.setColumnStretch(0, ratio[0])
        self.centralWidget.layout.setColumnStretch(1, ratio[1])

    # Actions - enable or disable lightning feature
    def enableLightning(self):
        config.instantInformationEnabled = 1
        #self.enableInstantButton.setText(self.getInstantInformation())
        enableInstantButtonFile = os.path.join("htmlResources", self.getInstantInformation())
        self.enableInstantButton.setIcon(QIcon(enableInstantButtonFile))

    def disableLightning(self):
        config.instantInformationEnabled = 0
        #self.enableInstantButton.setText(self.getInstantInformation())
        enableInstantButtonFile = os.path.join("htmlResources", self.getInstantInformation())
        self.enableInstantButton.setIcon(QIcon(enableInstantButtonFile))

    def getInstantInformation(self):
        if config.instantInformationEnabled == 0:
            return "hide.png"
        elif config.instantInformationEnabled == 1:
            return "show.png"

    def enableInstantButtonClicked(self):
        if config.instantInformationEnabled == 0:
            config.instantInformationEnabled = 1
        elif config.instantInformationEnabled == 1:
            config.instantInformationEnabled = 0
        #self.enableInstantButton.setText(self.getInstantInformation())
        enableInstantButtonFile = os.path.join("htmlResources", self.getInstantInformation())
        self.enableInstantButton.setIcon(QIcon(enableInstantButtonFile))

    # Actions - change font size
    def smallerFont(self):
        if not config.fontSize == 10:
            config.fontSize = config.fontSize - 5
            self.reloadCurrentRecord()

    def largerFont(self):
        config.fontSize = config.fontSize + 5
        self.reloadCurrentRecord()

    def reloadCurrentRecord(self):
        views = {
            "main": self.mainView,
            "study": self.studyView
        }
        for view in views.keys():
            textCommand = config.history[view][config.currentRecord[view]]
            self.runTextCommand(textCommand, False, view)

    # Actions - recently opened bibles & commentary
    def mainRefButtonClicked(self):
        newTextCommand = "_menu:::{0}.{1}.{2}.{3}".format(config.mainText, config.mainB, config.mainC, config.mainV)
        self.runTextCommand(newTextCommand, False, "main")

    def studyRefButtonClicked(self):
        newTextCommand = "_menu:::{0}.{1}.{2}.{3}".format(config.studyText, config.studyB, config.studyC, config.studyV)
        self.runTextCommand(newTextCommand, False, "study")

    def commentaryRefButtonClicked(self):
        newTextCommand = "_commentary:::{0}.{1}.{2}.{3}".format(config.commentaryText, config.commentaryB, config.commentaryC, config.commentaryV)
        self.runTextCommand(newTextCommand, False, "study")

    def updateMainRefButton(self):
        self.mainRefButton.setText(self.verseReference("main"))

    def updateStudyRefButton(self):
        self.studyRefButton.setText(self.verseReference("study"))

    def updateCommentaryRefButton(self):
        self.commentaryRefButton.setText(self.verseReference("commentary"))

    def verseReference(self, view):
        if view == "main":
            return "{0} - {1}".format(config.mainText, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV))
        elif view == "study":
            return "{0} - {1}".format(config.studyText, self.bcvToVerseReference(config.studyB, config.studyC, config.studyV))
        elif view == "commentary":
            return "{0} - {1}".format(config.commentaryText, self.bcvToVerseReference(config.commentaryB, config.commentaryC, config.commentaryV))

    # Actions - access history records
    def mainHistoryButtonClicked(self):
        self.mainView.setHtml(self.getHistory("main"), baseUrl)

    def studyHistoryButtonClicked(self):
        self.studyView.setHtml(self.getHistory("study"), baseUrl)

    def getHistory(self, view):
        historyRecords = [(counter, record) for counter, record in enumerate(config.history[view])]
        if view == "external":
            html = "<br>".join(["<button class='feature' onclick='openExternalRecord({0})'>{1}</button> [<ref onclick='editExternalRecord({0})'>edit</ref>]".format(counter, record) for counter, record in reversed(historyRecords)])
        else:
            html = "<br>".join(["<button class='feature' onclick='openHistoryRecord({0})'>{1}</button>".format(counter, record) for counter, record in reversed(historyRecords)])
        html = self.htmlWrapper(html)
        return html

    # navigation between history records
    def openHistoryRecord(self, view, recordNumber):
        config.currentRecord[view] = recordNumber
        textCommand = config.history[view][recordNumber]
        if view == "main":
            self.textCommandLineEdit.setText(textCommand)
        self.runTextCommand(textCommand, False, view)
    
    def back(self):
        mainCurrentRecord = config.currentRecord["main"]
        if not mainCurrentRecord == 0:
            mainCurrentRecord = mainCurrentRecord - 1
            self.openHistoryRecord("main", mainCurrentRecord)

    def forward(self):
        mainCurrentRecord = config.currentRecord["main"]
        if not mainCurrentRecord == (len(config.history["main"]) - 1):
            mainCurrentRecord = mainCurrentRecord + 1
            self.openHistoryRecord("main", mainCurrentRecord)

    def studyBack(self):
        if self.parallelMode == 0:
            self.parallel()
        studyCurrentRecord = config.currentRecord["study"]
        if not studyCurrentRecord == 0:
            studyCurrentRecord = studyCurrentRecord - 1
            self.openHistoryRecord("study", studyCurrentRecord)

    def studyForward(self):
        if self.parallelMode == 0:
            self.parallel()
        studyCurrentRecord = config.currentRecord["study"]
        if not studyCurrentRecord == (len(config.history["study"]) - 1):
            studyCurrentRecord = studyCurrentRecord + 1
            self.openHistoryRecord("study", studyCurrentRecord)

    # root folder for webViewEngine
    def setupBaseUrl(self):
        # baseUrl
        # External objects, such as stylesheets or images referenced in the HTML document, are located RELATIVE TO baseUrl .
        # e.g. put all local files linked by html's content in folder "htmlResources"
        global baseUrl
        relativePath = os.path.join("htmlResources", "theText.png")
        absolutePath = os.path.abspath(relativePath)
        baseUrl = QUrl.fromLocalFile(absolutePath)

    # finish view loading
    def finishMainViewLoading(self):
        # scroll to the main verse
        self.mainPage.runJavaScript("var activeVerse = document.getElementById('v"+str(config.mainB)+"."+str(config.mainC)+"."+str(config.mainV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = 'red'; } else { document.getElementById('v0.0.0').scrollIntoView(); }")

    def finishStudyViewLoading(self):
        # scroll to the study verse
        self.studyPage.runJavaScript("var activeVerse = document.getElementById('v"+str(config.studyB)+"."+str(config.studyC)+"."+str(config.studyV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = 'red'; } else { document.getElementById('v0.0.0').scrollIntoView(); }")

    # running specific commands
    def runFeature(self, keyword):
        mainVerseReference = self.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        newTextCommand = "{0}:::{1}".format(keyword, mainVerseReference)
        self.textCommandChanged(newTextCommand, "main")

    def runCOMPARE(self):
        self.runFeature("COMPARE")

    def runCROSSREFERENCE(self):
        self.runFeature("CROSSREFERENCE")

    def runTSKE(self):
        self.runFeature("TSKE")

    def runTRANSLATION(self):
        self.runFeature("TRANSLATION")

    def runDISCOURSE(self):
        self.runFeature("DISCOURSE")

    def runWORDS(self):
        self.runFeature("WORDS")

    def runCOMBO(self):
        self.runFeature("COMBO")

    def runCOMMENTARY(self):
        self.runFeature("COMMENTARY")

    def runINDEX(self):
        self.runFeature("INDEX")

    # change of unique bible commands
    def mainTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "main")

    def studyTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "study")

    def instantTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "instant")

    # change of text command detected via change of document.title
    def textCommandChanged(self, newTextCommand, source="main"):
        exceptionTuple = ("UniqueBible.app", "about:blank", "study.html")
        if not (newTextCommand.startswith("data:text/html;") or newTextCommand.startswith("file:///") or newTextCommand[-4:] == ".txt" or newTextCommand in exceptionTuple):
            if source == "main" and not newTextCommand.startswith("_"):
                self.textCommandLineEdit.setText(newTextCommand)
            if newTextCommand.startswith("_"):
                self.runTextCommand(newTextCommand, False, source)
            else:
                self.runTextCommand(newTextCommand, True, source)

    # change of text command detected via user input
    def textCommandEntered(self, source="main"):
        newTextCommand = self.textCommandLineEdit.text()
        self.runTextCommand(newTextCommand, True, source)

    def runTextCommand(self, textCommand, addRecord=True, source="main"):
        view, content = self.textCommandParser.parser(textCommand, source)
        if content == "INVALID_COMMAND_ENTERED":
            self.mainPage.runJavaScript("alert('Invalid command not processed.')")
        elif view == "":
            if source == "main":
                self.mainPage.runJavaScript("document.title = 'UniqueBible.app';")
            elif source == "study":
                self.studyPage.runJavaScript("document.title = 'UniqueBible.app';")
        elif view == "command":
            self.textCommandLineEdit.setText(content)
            self.textCommandLineEdit.setFocus()
        else:
            activeBCVsettings = ""
            if view == "main":
                activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.mainText, config.mainB, config.mainC, config.mainV)
            elif view == "study":
                activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.studyText, config.studyB, config.studyC, config.studyV)
            html = "<!DOCTYPE html><html><head><title>UniqueBible.app</title><link rel='stylesheet' type='text/css' href='theText.css'><script src='theText.js'></script><script src='w3.js'></script>{0}<script>var versionList = []; var compareList = []; var parallelList = [];</script></head><body style='font-size: {1}%;'><span id='v0.0.0'></span>{2}</body></html>".format(activeBCVsettings, config.fontSize, content)
            views = {
                "main": self.mainView,
                "study": self.studyView,
                "instant": self.instantView,
            }
            if view == "study":
                # save html in a separate file
                # reason: setHTML does not work with content larger than 2 MB
                self.openTextOnStudyView(html)
            elif view.startswith("popover"):
                view = view.split(".")[1]
                views[view].openPopover(html=html)
            else:
                views[view].setHtml(html, baseUrl)
            if addRecord == True and view in ("main", "study"):
                self.addHistoryRecord(view, textCommand)

    # add a history record
    def addHistoryRecord(self, view, textCommand):
        if not textCommand.startswith("_"):
            viewhistory = config.history[view]
            if not (viewhistory[-1] == textCommand):
                viewhistory.append(textCommand)
                # set maximum number of history records for each view here
                historyRecordAllowed = config.historyRecordAllowed
                if len(viewhistory) > historyRecordAllowed:
                    viewhistory = viewhistory[-historyRecordAllowed:]
                config.history[view] = viewhistory
                config.currentRecord[view] = len(viewhistory) - 1


class CentralWidget(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QGridLayout()

        self.html = "<h1>UniqueBible.app</h1><p>This is '<b>Main Window</b>'.</p>"
        self.mainView = WebEngineView(self, "main")
        self.mainView.setHtml(self.html, baseUrl)
        self.studyView = WebEngineView(self, "study")
        self.studyView.setHtml("This is '<b>Secondary Window</b>'.", baseUrl)
        self.instantView = WebEngineView(self, "instant")
        self.instantView.setHtml("<u><b>Lightning Window</b></u><br>This small window is designed for viewing instant information, with mouse hovering over verse numbers, special words and links.", baseUrl)

        self.layout.addWidget(self.mainView, 0, 0)
        self.layout.addWidget(self.studyView, 0, 1)
        self.layout.addWidget(self.instantView, 1, 0, 1, 2)

        self.layout.setColumnStretch(0, 2)
        self.layout.setColumnStretch(1, 1)

        self.layout.setRowStretch(0, 10)
        self.layout.setRowStretch(1, 2)

        self.setLayout(self.layout)


class WebEngineView(QWebEngineView):

    def __init__(self, parent, name):
        super().__init__()
        self.parent = parent
        self.name = name
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.selectionChanged.connect(self.updateContextMenu)
        self.addMenuActions();

    def updateContextMenu(self):
        text = self.getText()
        parser = BibleVerseParser(config.parserStandarisation)
        book = parser.bcvToVerseReference(self.getBook(), 1, 1)[:-4]
        del parser
        self.searchText.setText("Search in {0}".format(text))
        self.searchTextInBook.setText("Search in {0} > {1}".format(text, book))
        self.iSearchText.setText("iSearch in {0}".format(text))
        self.iSearchTextInBook.setText("iSearch in {0} > {1}".format(text, book))
        self.searchBibleTopic.setText("Bible Topic > {0}".format(config.topic))
        self.searchBibleDictionary.setText("Bible Dictionary > {0}".format(config.dictionary))
        self.searchBibleEncyclopedia.setText("Bible Encyclopedia > {0}".format(config.encyclopedia))
        self.searchThirdDictionary.setText("3rd Party Dictionary > {0}".format(config.thirdDictionary))

    def getText(self):
        text = {
            "main": config.mainText,
            "study": config.studyText,
            "instant": config.mainText,
        }
        return text[self.name]

    def getBook(self):
        book = {
            "main": config.mainB,
            "study": config.studyB,
            "instant": config.mainB,
        }
        return book[self.name]

    def addMenuActions(self):
        copyText = QAction(self)
        copyText.setText("Copy")
        copyText.triggered.connect(self.copySelectedText)
        self.addAction(copyText)
        
        self.searchText = QAction(self)
        self.searchText.setText("Search")
        self.searchText.triggered.connect(self.searchSelectedText)
        self.addAction(self.searchText)

        self.searchTextInBook = QAction(self)
        self.searchTextInBook.setText("Search in Current Book")
        self.searchTextInBook.triggered.connect(self.searchSelectedTextInBook)
        self.addAction(self.searchTextInBook)

        self.iSearchText = QAction(self)
        self.iSearchText.setText("iSearch")
        self.iSearchText.triggered.connect(self.iSearchSelectedText)
        self.addAction(self.iSearchText)

        self.iSearchTextInBook = QAction(self)
        self.iSearchTextInBook.setText("iSearch in Current Book")
        self.iSearchTextInBook.triggered.connect(self.iSearchSelectedTextInBook)
        self.addAction(self.iSearchTextInBook)

        searchBibleCharacter = QAction(self)
        searchBibleCharacter.setText("Bible Character")
        searchBibleCharacter.triggered.connect(self.searchCharacter)
        self.addAction(searchBibleCharacter)

        searchBibleName = QAction(self)
        searchBibleName.setText("Bible Name")
        searchBibleName.triggered.connect(self.searchName)
        self.addAction(searchBibleName)

        searchBibleLocation = QAction(self)
        searchBibleLocation.setText("Bible Location")
        searchBibleLocation.triggered.connect(self.searchLocation)
        self.addAction(searchBibleLocation)

        self.searchBibleTopic = QAction(self)
        self.searchBibleTopic.setText("Bible Topic")
        self.searchBibleTopic.triggered.connect(self.searchTopic)
        self.addAction(self.searchBibleTopic)

        self.searchBibleDictionary = QAction(self)
        self.searchBibleDictionary.setText("Bible Dictionary")
        self.searchBibleDictionary.triggered.connect(self.searchDictionary)
        self.addAction(self.searchBibleDictionary)

        self.searchBibleEncyclopedia = QAction(self)
        self.searchBibleEncyclopedia.setText("Bible Encyclopedia")
        self.searchBibleEncyclopedia.triggered.connect(self.searchEncyclopedia)
        self.addAction(self.searchBibleEncyclopedia)

        self.searchThirdDictionary = QAction(self)
        self.searchThirdDictionary.setText("3rd Party Dictionary")
        self.searchThirdDictionary.triggered.connect(self.searchThirdPartyDictionary)
        self.addAction(self.searchThirdDictionary)

        searchBibleReferences = QAction(self)
        searchBibleReferences.setText("Extract All Bible References")
        searchBibleReferences.triggered.connect(self.extractAllReferences)
        self.addAction(searchBibleReferences)

    def messageNoSelection(self):
        self.page().runJavaScript("alert('You have not selected word(s) for this action!')")

    def copySelectedText(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            self.page().triggerAction(self.page().Copy)

    def searchSelectedText(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format(self.getText(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedTextInBook(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "ADVANCEDSEARCH:::{0}:::Book = {1} AND Scripture LIKE '%{2}%'".format(self.getText(), self.getBook(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def iSearchSelectedText(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "ISEARCH:::{0}:::{1}".format(self.getText(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def iSearchSelectedTextInBook(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "ADVANCEDISEARCH:::{0}:::Book = {1} AND Scripture LIKE '%{2}%'".format(self.getText(), self.getBook(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchResource(self, module):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTOOL:::{0}:::{1}".format(module, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchCharacter(self):
        self.searchResource("EXLBP")

    def searchName(self):
        self.searchResource("HBN")

    def searchLocation(self):
        self.searchResource("EXLBL")

    def searchTopic(self):
        self.searchResource(config.topic)

    def searchDictionary(self):
        self.searchResource(config.dictionary)

    def searchEncyclopedia(self):
        self.searchResource(config.encyclopedia)

    def searchThirdPartyDictionary(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(config.thirdDictionary, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def extractAllReferences(self):
        selectedText = self.selectedText()
        parser = BibleVerseParser(config.parserStandarisation)
        verseList = parser.extractAllReferences(selectedText, False)
        del parser
        if not verseList:
            self.page().runJavaScript("alert('No bible verse reference is found from the text you selected.')")
        else:
            biblesSqlite = BiblesSqlite()
            verses = biblesSqlite.readMultipleVerses(self.getText(), verseList)
            del biblesSqlite
            self.openPopover(html=verses)

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserWindow or windowType == QWebEnginePage.WebBrowserTab:
            self.openPopover()
        return super().createWindow(windowType)

    def openPopover(self, name="popover", html="UniqueBible.app"):
        html = "<!DOCTYPE html><html><head><title>UniqueBible.app</title><link rel='stylesheet' type='text/css' href='theText.css'><script src='theText.js'></script><script src='w3.js'></script><script>var versionList = []; var compareList = []; var parallelList = [];</script></head><body style='font-size: {0}%;'><span id='v0.0.0'></span>{1}</body></html>".format(config.fontSize, html)
        self.popoverView = WebEngineViewPopover(self, name, self.name)
        self.popoverView.setHtml(html, baseUrl)
        self.popoverView.show()


class WebEngineViewPopover(QWebEngineView):

    def __init__(self, parent, name, source):
        super().__init__()
        self.parent = parent
        self.name = name
        self.source = source
        self.setWindowTitle("Unique Bible App - Popover")
        self.titleChanged.connect(self.popoverTextCommandChanged)

    def popoverTextCommandChanged(self, newTextCommand):
        self.parent.parent.parent.textCommandChanged(newTextCommand, self.source)


class NoteEditor(QWidget):

    def __init__(self, parent, noteType, noteFileName=""):
        super().__init__()
        self.parent, self.noteType = parent, noteType
        self.noteFileName = noteFileName

        # default - "Rich" mode for editing
        self.html = True
        # default - show toolbar with formatting items
        self.showToolBar = True
        # default - text is not modified; no need for saving new content
        self.parent.noteSaved = True

        # specify window size
        self.resizeWindow(2/3, 2/3)

        # setup interface
        self.setupMenuBar()
        self.setupToolBar()
        self.setupLayout()
        
        # display content when first launched
        self.displayInitialContent()

        # specify window title
        self.updateWindowTitle()
        
        #self.close.connect(self.closingEditor)

    # re-implementing close event, when users close this widget
    def closeEvent(self, event):
        if self.parent.noteSaved:
            event.accept()
        else:
            if self.parent.warningNotSaved():
                self.parent.noteSaved = True
                event.accept()
            else:
                event.ignore()

    # re-implement keyPressEvent, control+S for saving file
    def keyPressEvent(self, event):
        keys = {
            Qt.Key_O: self.openFileDialog,
            Qt.Key_S: self.saveNote,
            Qt.Key_B: self.format_bold,
            Qt.Key_I: self.format_italic,
            Qt.Key_U: self.format_underline,
            Qt.Key_M: self.format_custom,
            Qt.Key_R: self.format_clear,
        }
        key = event.key()
        if event.modifiers() == Qt.ControlModifier and key in keys:
            keys[key]()

    # window appearance
    def resizeWindow(self, widthFactor, heightFactor):
        availableGeometry = qApp.desktop().availableGeometry()
        self.resize(availableGeometry.width() * widthFactor, availableGeometry.height() * heightFactor)

    def updateWindowTitle(self):
        if self.noteType == "file":
            if self.noteFileName:
                *_, title = os.path.split(self.noteFileName)
            else:
                title = "NEW"
        else:
            title = self.parent.bcvToVerseReference(self.b, self.c, self.v)
            if self.noteType == "chapter":
                title, *_ = title.split(":")
        mode = {True: "rich", False: "plain"}
        notModified = {True: "", False: " [modified]"}
        self.setWindowTitle("Note Editor ({1} mode) - {0}{2}".format(title, mode[self.html], notModified[self.parent.noteSaved]))

    # switching between "rich" & "plain" mode
    def switchMode(self):
        if self.html:
            note = self.editor.toHtml()
            self.editor.setPlainText(note)
            self.html = False
            self.updateWindowTitle()
        else:
            note = self.editor.toPlainText()
            self.editor.setHtml(note)
            self.html = True
            self.updateWindowTitle()
        # without this hide / show command below, QTextEdit does not update the text in some devices
        self.hide()
        self.show()

    def setupMenuBar(self):

        self.menuBar = QToolBar()
        self.menuBar.setWindowTitle("Menu Bar")
        self.menuBar.setContextMenuPolicy(Qt.PreventContextMenu)

        newButton = QPushButton()
        newButtonFile = os.path.join("htmlResources", "newfile.png")
        newButton.setIcon(QIcon(newButtonFile))
        newButton.clicked.connect(self.newNoteFile)
        self.menuBar.addWidget(newButton)

        openButton = QPushButton()
        openButtonFile = os.path.join("htmlResources", "open.png")
        openButton.setIcon(QIcon(openButtonFile))
        openButton.clicked.connect(self.openFileDialog)
        self.menuBar.addWidget(openButton)

        self.menuBar.addSeparator()

        saveButton = QPushButton()
        saveButtonFile = os.path.join("htmlResources", "save.png")
        saveButton.setIcon(QIcon(saveButtonFile))
        saveButton.clicked.connect(self.saveNote)
        self.menuBar.addWidget(saveButton)

        saveAsButton = QPushButton()
        saveAsButtonFile = os.path.join("htmlResources", "saveas.png")
        saveAsButton.setIcon(QIcon(saveAsButtonFile))
        saveAsButton.clicked.connect(self.openSaveAsDialog)
        self.menuBar.addWidget(saveAsButton)

        self.menuBar.addSeparator()

        toolBarButton = QPushButton()
        toolBarButtonFile = os.path.join("htmlResources", "toolbar.png")
        toolBarButton.setIcon(QIcon(toolBarButtonFile))
        toolBarButton.clicked.connect(self.toogleToolbar)
        self.menuBar.addWidget(toolBarButton)

        self.menuBar.addSeparator()

        switchButton = QPushButton()
        switchButtonFile = os.path.join("htmlResources", "switch.png")
        switchButton.setIcon(QIcon(switchButtonFile))
        switchButton.clicked.connect(self.switchMode)
        self.menuBar.addWidget(switchButton)

        self.menuBar.addSeparator()

        #self.searchLineEdit = QLineEdit()
        #self.searchLineEdit.returnPressed.connect(self.searchLineEntered)
        #self.menuBar.addWidget(self.searchLineEdit)

        #self.menuBar.addSeparator()

    def toogleToolbar(self):
        if self.showToolBar:
            self.toolBar.hide()
            self.showToolBar = False
        else:
            self.toolBar.show()
            self.showToolBar = True

    def setupToolBar(self):

        self.toolBar = QToolBar()
        self.toolBar.setWindowTitle("Tool Bar")
        self.toolBar.setContextMenuPolicy(Qt.PreventContextMenu)

        boldButton = QPushButton()
        boldButtonFile = os.path.join("htmlResources", "bold.png")
        boldButton.setIcon(QIcon(boldButtonFile))
        boldButton.clicked.connect(self.format_bold)
        self.toolBar.addWidget(boldButton)

        italicButton = QPushButton()
        italicButtonFile = os.path.join("htmlResources", "italic.png")
        italicButton.setIcon(QIcon(italicButtonFile))
        italicButton.clicked.connect(self.format_italic)
        self.toolBar.addWidget(italicButton)

        underlineButton = QPushButton()
        underlineButtonFile = os.path.join("htmlResources", "underline.png")
        underlineButton.setIcon(QIcon(underlineButtonFile))
        underlineButton.clicked.connect(self.format_underline)
        self.toolBar.addWidget(underlineButton)

        self.toolBar.addSeparator()

        customButton = QPushButton()
        customButtonFile = os.path.join("htmlResources", "custom.png")
        customButton.setIcon(QIcon(customButtonFile))
        customButton.clicked.connect(self.format_custom)
        self.toolBar.addWidget(customButton)

        self.toolBar.addSeparator()

        leftButton = QPushButton()
        leftButtonFile = os.path.join("htmlResources", "align_left.png")
        leftButton.setIcon(QIcon(leftButtonFile))
        leftButton.clicked.connect(self.format_left)
        self.toolBar.addWidget(leftButton)

        centerButton = QPushButton()
        centerButtonFile = os.path.join("htmlResources", "align_center.png")
        centerButton.setIcon(QIcon(centerButtonFile))
        centerButton.clicked.connect(self.format_center)
        self.toolBar.addWidget(centerButton)

        rightButton = QPushButton()
        rightButtonFile = os.path.join("htmlResources", "align_right.png")
        rightButton.setIcon(QIcon(rightButtonFile))
        rightButton.clicked.connect(self.format_right)
        self.toolBar.addWidget(rightButton)

        justifyButton = QPushButton()
        justifyButtonFile = os.path.join("htmlResources", "align_justify.png")
        justifyButton.setIcon(QIcon(justifyButtonFile))
        justifyButton.clicked.connect(self.format_justify)
        self.toolBar.addWidget(justifyButton)

        self.toolBar.addSeparator()

        clearButton = QPushButton()
        clearButtonFile = os.path.join("htmlResources", "clearFormat.png")
        clearButton.setIcon(QIcon(clearButtonFile))
        clearButton.clicked.connect(self.format_clear)
        self.toolBar.addWidget(clearButton)

        self.toolBar.addSeparator()

        hyperlinkButton = QPushButton()
        hyperlinkButtonFile = os.path.join("htmlResources", "hyperlink.png")
        hyperlinkButton.setIcon(QIcon(hyperlinkButtonFile))
        hyperlinkButton.clicked.connect(self.openHyperlinkDialog)
        self.toolBar.addWidget(hyperlinkButton)

        imageButton = QPushButton()
        imageButtonFile = os.path.join("htmlResources", "gallery.png")
        imageButton.setIcon(QIcon(imageButtonFile))
        imageButton.clicked.connect(self.openImageDialog)
        self.toolBar.addWidget(imageButton)

        self.toolBar.addSeparator()

    def setupLayout(self):

        self.editor = QTextEdit()
        self.editor.textChanged.connect(self.textChanged)

        self.layout = QGridLayout()
        self.layout.setMenuBar(self.menuBar)
        self.layout.addWidget(self.toolBar, 0, 0)
        self.layout.addWidget(self.editor, 1, 0)

        self.setLayout(self.layout)

    # track if the text being modified
    def textChanged(self):
        if self.parent.noteSaved:
            self.parent.noteSaved = False
            self.updateWindowTitle()

    # display content when first launched
    def displayInitialContent(self):
        if self.noteType == "file":
            if self.noteFileName:
                self.openNoteFile(self.noteFileName)
            else:
                self.newNoteFile()
        else:
            self.b, self.c, self.v = config.studyB, config.studyC, config.studyV
            self.openBibleNote()
        self.parent.noteSaved = True

    # load chapter / verse notes from sqlite database
    def openBibleNote(self):
        noteSqlite = NoteSqlite()
        if self.noteType == "chapter":
            note = noteSqlite.getChapterNote((self.b, self.c))
        elif self.noteType == "verse":
            note = noteSqlite.getVerseNote((self.b, self.c, self.v))
        del noteSqlite
        #self.editor.setPlainText(note)
        self.editor.setHtml(note)

    # File I / O
    def newNoteFile(self):
        if self.parent.noteSaved:
            self.newNoteFileAction()
        elif self.parent.warningNotSaved():
            self.newNoteFileAction()

    def newNoteFileAction(self):
        self.noteType = "file"
        self.noteFileName = ""
        self.editor.clear()
        self.parent.noteSaved = True
        self.updateWindowTitle()
        self.hide()
        self.show()

    def openFileDialog(self):
        if self.parent.noteSaved:
            self.openFileDialogAction()
        elif self.parent.warningNotSaved():
            self.openFileDialogAction()

    def openFileDialogAction(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                "QFileDialog.getOpenFileName()",
                self.parent.openFileNameLabel.text(),
                "UniqueBible.app Note Files (*.uba);;HTML Files (*.html);;HTM Files (*.htm);;All Files (*)", "", options)
        if fileName:
            self.openNoteFile(fileName)

    def openNoteFile(self, fileName):
        try:
            f = open(fileName,'r')
        except:
            print("Failed to open '{0}'".format(fileName))
        note = f.read()
        f.close()
        self.noteType = "file"
        self.noteFileName = fileName
        if self.html:
            self.editor.setHtml(note)
        else:
            self.editor.setPlainText(note)
        self.parent.noteSaved = True
        self.updateWindowTitle()
        self.hide()
        self.show()

    def saveNote(self):
        if self.html:
            note = self.editor.toHtml()
        else:
            note = self.editor.toPlainText()
        if self.noteType == "chapter":
            noteSqlite = NoteSqlite()
            noteSqlite.saveChapterNote((self.b, self.c, note))
            del noteSqlite
            self.parent.openChapterNote(self.b, self.c)
            self.parent.noteSaved = True
            self.updateWindowTitle()
        elif self.noteType == "verse":
            noteSqlite = NoteSqlite()
            noteSqlite.saveVerseNote((self.b, self.c, self.v, note))
            del noteSqlite
            self.parent.openVerseNote(self.b, self.c, self.v)
            self.parent.noteSaved = True
            self.updateWindowTitle()
        elif self.noteType == "file":
            if self.noteFileName == "":
                self.openSaveAsDialog()
            else:
                self.saveAsNote(self.noteFileName)

    def openSaveAsDialog(self):
        if self.noteFileName:
            *_, defaultName = os.path.split(self.noteFileName)
        else:
            defaultName = "new.uba"
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getSaveFileName(self,
                "QFileDialog.getSaveFileName()",
                defaultName,
                "UniqueBible.app Note Files (*.uba);;HTML Files (*.html);;HTM Files (*.htm);;All Files (*)", "", options)
        if fileName:
            self.saveAsNote(fileName)

    def saveAsNote(self, fileName):
        if self.html:
            note = self.editor.toHtml()
        else:
            note = self.editor.toPlainText()
        f = open(fileName,'w')
        f.write(note)
        f.close()
        self.noteFileName = fileName
        self.parent.addExternalFileHistory(fileName)
        self.parent.setExternalFileButton()
        self.parent.noteSaved = True
        self.updateWindowTitle()

    # formatting styles
    def format_clear(self):
        selectedText = self.editor.textCursor().selectedText()
        if self.html:
            self.editor.insertHtml(selectedText)
        else:
            selectedText = re.sub("<[^\n<>]*?>", "", selectedText)
            self.editor.insertPlainText(selectedText)
        self.hide()
        self.show()

    def format_bold(self):
        if self.html:
            self.editor.setFontWeight(75)
        else:
            self.editor.insertPlainText("<b>{0}</b>".format(self.editor.textCursor().selectedText()))
        self.hide()
        self.show()

    def format_italic(self):
        if self.html:
            self.editor.setFontItalic(True)
        else:
            self.editor.insertPlainText("<i>{0}</i>".format(self.editor.textCursor().selectedText()))
        self.hide()
        self.show()

    def format_underline(self):
        if self.html:
            self.editor.setFontUnderline(True)
        else:
            self.editor.insertPlainText("<u>{0}</u>".format(self.editor.textCursor().selectedText()))
        self.hide()
        self.show()

    def format_center(self):
        if self.html:
            self.editor.setAlignment(Qt.AlignCenter)
        else:
            self.editor.insertPlainText("<div style='text-align:center;'>{0}</div>".format(self.editor.textCursor().selectedText()))
        self.hide()
        self.show()

    def format_justify(self):
        if self.html:
            self.editor.setAlignment(Qt.AlignJustify)
        else:
            self.editor.insertPlainText("<div style='text-align:justify;'>{0}</div>".format(self.editor.textCursor().selectedText()))
        self.hide()
        self.show()

    def format_left(self):
        if self.html:
            self.editor.setAlignment(Qt.AlignLeft)
        else:
            self.editor.insertPlainText("<div style='text-align:left;'>{0}</div>".format(self.editor.textCursor().selectedText()))
        self.hide()
        self.show()

    def format_right(self):
        if self.html:
            self.editor.setAlignment(Qt.AlignRight)
        else:
            self.editor.insertPlainText("<div style='text-align:right;'>{0}</div>".format(self.editor.textCursor().selectedText()))
        self.hide()
        self.show()

    def format_custom(self):
        selectedText = self.editor.textCursor().selectedText()
        selectedText = self.customFormat(selectedText)
        if self.html:
            self.editor.insertHtml(selectedText)
        else:
            self.editor.insertPlainText(selectedText)
        self.hide()
        self.show()

    def customFormat(self, text):
        # QTextEdit's line break character by pressing ENTER in plain & html mode " "
        # please note that " " is not an empty string
        text = text.replace(" ", "\n")

        text = re.sub("^\*[0-9]+? (.*?)$", r"<ol><li>\1</li></ol>", text, flags=re.M)
        text = text.replace("</ol>\n<ol>", "\n")
        text = re.sub("^\* (.*?)$", r"<ul><li>\1</li></ul>", text, flags=re.M)
        text = text.replace("</ul>\n<ul>", "\n")
        text = re.sub("^{.*?}$", self.formatHTMLTable, text, flags=re.M)
        text = text.replace("</table>\n<table>", "\n")

        # add style to table here
        # please note that QTextEdit supports HTML 4, rather than HTML 5
        # take this old reference: https://www.w3schools.com/tags/tag_table.asp
        text = text.replace('<table>', '<table border="1" cellpadding="5">')

        # convert back to QTextEdit linebreak
        text = text.replace("\n", " ")

        return text

    def formatHTMLTable(self, match):
        row = match.group()[1:-1]
        row = "".join(["<td>{0}</td>".format(cell) for cell in row.split("|")])
        return "<table><tr>{0}</tr></table>".format(row)

    def addImage(self, fileName):
        imageTag = '<img src="{0}" alt="UniqueBible.app">'.format(fileName)
        if self.html:
            self.editor.insertHtml(imageTag)
        else:
            self.editor.insertPlainText(imageTag)
        self.hide()
        self.show()

    def openImageDialog(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                "QFileDialog.getOpenFileName()",
                self.parent.openFileNameLabel.text(),
                "JPG Files (*.jpg);;JPEG Files (*.jpeg);;PNG Files (*.png);;GIF Files (*.gif);;BMP Files (*.bmp);;All Files (*)", "", options)
        if fileName:
            self.addImage(fileName)

    def addHyperlink(self, hyperlink):
        hyperlink = '<a href="{0}">{0}</a>'.format(hyperlink)
        if self.html:
            self.editor.insertHtml(hyperlink)
        else:
            self.editor.insertPlainText(hyperlink)
        self.hide()
        self.show()

    def openHyperlinkDialog(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            hyperlink = selectedText
        else:
            hyperlink = "https://BibleTools.app"
        text, ok = QInputDialog.getText(self, "Add a hyperlink ...",
                "Hyperlink:", QLineEdit.Normal,
                hyperlink)
        if ok and text != '':
            self.addHyperlink(text)


class Downloader(QDialog):

    def __init__(self, parent, databaseInfo):
        super().__init__()
        self.parent = parent
        self.setWindowTitle("Download Helper")
        self.setModal(True)
        
        fileItems, cloudID = databaseInfo
        self.cloudFile = "https://drive.google.com/uc?id={0}".format(cloudID)
        self.localFile = "{0}.zip".format(os.path.join(*fileItems))
        self.filename = fileItems[-1]
        
        self.setupLayout()

    def setupLayout(self):

        #self.setupProgressBar()

        message = QLabel("File '{0}' is required for running the feature you selected.".format(self.filename))

        downloadButton = QPushButton("Download + Install")
        downloadButton.clicked.connect(self.downloadFile)
        
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)

        remarks = QLabel("Remarks: Larger files takes longer time to be downloaded.")

        self.layout = QGridLayout()
        #self.layout.addWidget(self.progressBar, 0, 0)
        self.layout.addWidget(message, 0, 0)
        self.layout.addWidget(downloadButton, 1, 0)
        self.layout.addWidget(cancelButton, 2, 0)
        self.layout.addWidget(remarks, 3, 0)
        self.setLayout(self.layout)

    def setupProgressBar(self):
        self.progressBar = QProgressBar()
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

    def downloadFile(self):
        gdown.download(self.cloudFile, self.localFile, quiet=True)
        if self.localFile.endswith(".zip"):
            zip = zipfile.ZipFile(self.localFile, "r")
            path, *_ = os.path.split(self.localFile)
            zip.extractall(path)
            zip.close()
            os.remove(self.localFile)
        self.close()
