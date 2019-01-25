import os, sys, config
from PySide2.QtCore import QUrl, Qt
from PySide2.QtGui import QIcon, QGuiApplication
from PySide2.QtWidgets import (QAction, QDesktopWidget, QGridLayout, QLineEdit, QMainWindow, QPushButton, QToolBar, QWidget)
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from TextCommandParser import TextCommandParser
from BibleVerseParser import BibleVerseParser

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.textCommandParser = TextCommandParser()

        self.setWindowTitle('THE TEXT APP')
        
        appIconFile = os.path.join("htmlResources", "theText.png")
        appIcon = QIcon(appIconFile)
        QGuiApplication.setWindowIcon(appIcon)
        
        self.create_menu()
        self.setupToolBar()
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

    def __del__(self):
        del self.textCommandParser

    def create_menu(self):
        appIconFile = os.path.join("htmlResources", "theText.png")
        appIcon = QIcon(appIconFile)
        menu1 = self.menuBar().addMenu("&theText.app")
        quit_action = QAction(appIcon, "E&xit",
                             self, shortcut = "Ctrl+Q", triggered=qApp.quit)
        menu1.addAction(quit_action)

    def setupToolBar(self):
        self.toolBar = QToolBar()
        self.addToolBar(self.toolBar)

        self.backButton = QPushButton()
        leftButtonFile = os.path.join("htmlResources", "left.png")
        self.backButton.setIcon(QIcon(leftButtonFile))
        self.backButton.clicked.connect(self.back)
        self.toolBar.addWidget(self.backButton)

        self.forwardButton = QPushButton()
        rightButtonFile = os.path.join("htmlResources", "right.png")
        self.forwardButton.setIcon(QIcon(rightButtonFile))
        self.forwardButton.clicked.connect(self.forward)
        self.toolBar.addWidget(self.forwardButton)

        self.textCommandLineEdit = QLineEdit()
        #self.textCommandLineEdit.setText("[Enter command here]")
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        self.toolBar.addWidget(self.textCommandLineEdit)

        self.studyBackButton = QPushButton()
        leftButtonFile = os.path.join("htmlResources", "left.png")
        self.studyBackButton.setIcon(QIcon(leftButtonFile))
        self.studyBackButton.clicked.connect(self.studyBack)
        self.toolBar.addWidget(self.studyBackButton)

        self.studyForwardButton = QPushButton()
        rightButtonFile = os.path.join("htmlResources", "right.png")
        self.studyForwardButton.setIcon(QIcon(rightButtonFile))
        self.studyForwardButton.clicked.connect(self.studyForward)
        self.toolBar.addWidget(self.studyForwardButton)

        self.parallelMode = 1 # default parallel mode
        self.parallelButton = QPushButton()
        parallelButtonFile = os.path.join("htmlResources", "parallel.png")
        self.parallelButton.setIcon(QIcon(parallelButtonFile))
        self.parallelButton.clicked.connect(self.parallel)
        self.toolBar.addWidget(self.parallelButton)
        
        self.instantMode = 1 # default parallel mode
        self.instantButton = QPushButton()
        instantButtonFile = os.path.join("htmlResources", "lightning.png")
        self.instantButton.setIcon(QIcon(instantButtonFile))
        self.instantButton.clicked.connect(self.instant)
        self.toolBar.addWidget(self.instantButton)

    def setupBaseUrl(self):
        # baseUrl
        # External objects, such as stylesheets or images referenced in the HTML document, are located RELATIVE TO baseUrl .
        # e.g. put all local files linked by html's content in folder "htmlResources"
        global baseUrl
        relativePath = os.path.join("htmlResources", "theText.png")
        absolutePath = os.path.abspath(relativePath)
        baseUrl = QUrl.fromLocalFile(absolutePath)

    def finishMainViewLoading(self):
        # scroll to the main verse
        self.mainPage.runJavaScript("var activeVerse = document.getElementById('v"+str(config.mainB)+"."+str(config.mainC)+"."+str(config.mainV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = 'red'; } else { document.getElementById('v0.0.0').scrollIntoView(); }")

    def finishStudyViewLoading(self):
        # scroll to the study verse
        self.studyPage.runJavaScript("var activeVerse = document.getElementById('v"+str(config.studyB)+"."+str(config.studyC)+"."+str(config.studyV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = 'red'; } else { document.getElementById('v0.0.0').scrollIntoView(); }")

    def back(self):
        mainCurrentRecord = config.currentRecord["main"]
        if not mainCurrentRecord == 0:
            mainCurrentRecord = mainCurrentRecord - 1
            config.currentRecord["main"] = mainCurrentRecord
            textCommand = config.history["main"][mainCurrentRecord]
            self.textCommandLineEdit.setText(textCommand)
            self.runTextCommand(textCommand, False)

    def forward(self):
        mainCurrentRecord = config.currentRecord["main"]
        if not mainCurrentRecord == (len(config.history["main"]) - 1):
            mainCurrentRecord = mainCurrentRecord + 1
            config.currentRecord["main"] = mainCurrentRecord
            textCommand = config.history["main"][mainCurrentRecord]
            self.textCommandLineEdit.setText(textCommand)
            self.runTextCommand(textCommand, False)

    def studyBack(self):
        if self.parallelMode == 0:
            self.parallel()
        studyCurrentRecord = config.currentRecord["study"]
        if not studyCurrentRecord == 0:
            studyCurrentRecord = studyCurrentRecord - 1
            config.currentRecord["study"] = studyCurrentRecord
            textCommand = config.history["study"][studyCurrentRecord]
            #self.textCommandLineEdit.setText(textCommand)
            self.runTextCommand(textCommand, False, "study")

    def studyForward(self):
        if self.parallelMode == 0:
            self.parallel()
        studyCurrentRecord = config.currentRecord["study"]
        if not studyCurrentRecord == (len(config.history["study"]) - 1):
            studyCurrentRecord = studyCurrentRecord + 1
            config.currentRecord["study"] = studyCurrentRecord
            textCommand = config.history["study"][studyCurrentRecord]
            #self.textCommandLineEdit.setText(textCommand)
            self.runTextCommand(textCommand, False, "study")

    def mainTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "main")

    def studyTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "study")

    def instantTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "instant")

    # change of text command detected via change of document.title
    def textCommandChanged(self, newTextCommand, source="main"):
        exceptionTuple = (self.textCommandLineEdit.text(), "theText.app", "about:blank", "study.html")
        if not (newTextCommand.startswith("data:text/html;") or newTextCommand.startswith("file:///") or newTextCommand in exceptionTuple):
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
            self.mainPage.runJavaScript("alert('Invalid command entered.')")
        elif view == "command":
            self.textCommandLineEdit.setText(content)
        else:
            activeBCVsettings = ""
            if view == "main":
                activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.mainText, config.mainB, config.mainC, config.mainV)
            elif view == "study":
                activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.studyText, config.studyB, config.studyC, config.studyV)
            html = "<!DOCTYPE html><html><head><title>theText.app</title><link rel='stylesheet' type='text/css' href='theText.css'><script src='theText.js'></script><script src='w3.js'></script>{0}<script>var versionList = []; var compareList = []; var parallelList = [];</script></head><body style='font-size: {1}%;'><span id='v0.0.0'></span>".format(activeBCVsettings, config.fontSize)
            html += content
            html += "</body></html>"
            views = {
                "main": self.mainView,
                "study": self.studyView,
                "instant": self.instantView,
            }
            if view == "study":
                # save html in a separate file
                outputFile = os.path.join("htmlResources", "study.html")
                f = open(outputFile,'w')
                f.write(html)
                f.close()
                fullOutputPath = os.path.abspath(outputFile)
                self.studyView.load(QUrl.fromLocalFile(fullOutputPath))
            elif view == "popover":
                self.mainView.openPopover(html=html)
            else:
                views[view].setHtml(html, baseUrl)
            if addRecord == True:
                self.addHistoryRecord(view, textCommand)

    def addHistoryRecord(self, view, textCommand):
        if not textCommand.startswith("_"):
            viewhistory = config.history[view]
            if not (viewhistory[len(viewhistory) - 1] == textCommand):
                viewhistory.append(textCommand)
                # set maximum number of history records for each view here
                historyRecordAllowed = config.historyRecordAllowed
                if len(viewhistory) > historyRecordAllowed:
                    viewhistory = viewhistory[-historyRecordAllowed:]
                config.history[view] = viewhistory
                config.currentRecord[view] = len(viewhistory) - 1

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


class CentralWidget(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.layout = QGridLayout()

        # content in unicode html format - Content larger than 2 MB cannot be displayed
        self.html = "<h1>theText.app</h1><p>theText.app</p>"
        self.mainView = WebEngineView(self, "main")
        self.mainView.setHtml(self.html, baseUrl)
        self.studyView = WebEngineView(self, "study")
        self.studyView.setHtml("Study View", baseUrl)
        self.instantView = WebEngineView(self, "instant")
        self.instantView.setHtml("Instant Information", baseUrl)
        #self.instantView.hide()

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
        parser = BibleVerseParser("YES")
        book = parser.bcvToVerseReference(self.getBook(), 1, 1)[:-4]
        del parser
        self.searchText.setText("Search in {0}".format(text))
        self.searchTextInBook.setText("Search in {0} > {1}".format(text, book))
        self.iSearchText.setText("iSearch in {0}".format(text))
        self.iSearchTextInBook.setText("iSearch in {0} > {1}".format(text, book))

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
        self.searchTextInBook.setText("Search in Book")
        self.searchTextInBook.triggered.connect(self.searchSelectedTextInBook)
        self.addAction(self.searchTextInBook)

        self.iSearchText = QAction(self)
        self.iSearchText.setText("iSearch")
        self.iSearchText.triggered.connect(self.iSearchSelectedText)
        self.addAction(self.iSearchText)

        self.iSearchTextInBook = QAction(self)
        self.iSearchTextInBook.setText("iSearch in Book")
        self.iSearchTextInBook.triggered.connect(self.iSearchSelectedTextInBook)
        self.addAction(self.iSearchTextInBook)

    def messageNoSelection(self):
        self.page().runJavaScript("alert('You have not selected word(s) for this action!')")

    def copySelectedText(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            self.page().triggerAction(self.page().Copy)

    def searchSelectedText(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format(self.getText(), self.selectedText())
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedTextInBook(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            searchCommand = "ADVANCEDSEARCH:::{0}:::Book = {1} AND Scripture LIKE '%{2}%'".format(self.getText(), self.getBook(), self.selectedText())
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def iSearchSelectedText(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            searchCommand = "ISEARCH:::{0}:::{1}".format(self.getText(), self.selectedText())
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def iSearchSelectedTextInBook(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            searchCommand = "ADVANCEDISEARCH:::{0}:::Book = {1} AND Scripture LIKE '%{2}%'".format(self.getText(), self.getBook(), self.selectedText())
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserWindow or windowType == QWebEnginePage.WebBrowserTab:
            self.openPopover()
        return super().createWindow(windowType)

    def openPopover(self, name="popover", html="theText.app"):
        self.popoverView = WebEngineViewPopover(self, name)
        self.popoverView.setHtml(html, baseUrl)
        self.popoverView.show()


class WebEngineViewPopover(QWebEngineView):
    def __init__(self, parent, name):
        super().__init__()
        self.parent = parent
        self.name = name



