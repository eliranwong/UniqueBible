import os, sys, config
from PySide2.QtCore import QUrl
from PySide2.QtGui import QIcon, QGuiApplication
from PySide2.QtWidgets import (QApplication, QDesktopWidget, QGridLayout, QLineEdit, QMainWindow, QPushButton, QToolBar, QWidget)
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from UbCommandParser import UbCommandParser

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ubCommandParser = UbCommandParser()

        self.setWindowTitle('Unique Bible App')
        
        appIconFile = os.path.join("htmlResources", "UniqueBible.png")
        appIcon = QIcon(appIconFile)
        QGuiApplication.setWindowIcon(appIcon)
        
        self.setupToolBar()
        self.setupBaseUrl()
        
        self.centralWidget = CentralWidget(self)
        self.mainView = self.centralWidget.mainView
        self.parallelView = self.centralWidget.parallelView
        self.page = self.mainView.page()
        self.page.titleChanged.connect(self.displayUbCommand)
        self.setCentralWidget(self.centralWidget)

    def __del__(self):
        del self.ubCommandParser

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

        self.ubCommandLineEdit = QLineEdit()
        #self.ubCommandLineEdit.setText("[Enter command here]")
        self.ubCommandLineEdit.returnPressed.connect(self.runUbCommand)
        self.toolBar.addWidget(self.ubCommandLineEdit)

        self.parallelMode = 0 # hide parallel view by default
        self.parallelButton = QPushButton()
        parallelButtonFile = os.path.join("htmlResources", "parallel.png")
        self.parallelButton.setIcon(QIcon(parallelButtonFile))
        self.parallelButton.clicked.connect(self.parallel)
        self.toolBar.addWidget(self.parallelButton)

    def setupBaseUrl(self):
        # baseUrl
        # External objects, such as stylesheets or images referenced in the HTML document, are located RELATIVE TO baseUrl .
        # e.g. put all local files linked by html's content in folder "htmlResources"
        global baseUrl
        relativePath = os.path.join("htmlResources", "UniqueBible.png")
        absolutePath = os.path.abspath(relativePath)
        baseUrl = QUrl.fromLocalFile(absolutePath)

    def back(self):
        mainCurrentRecord = config.currentRecord["main"]
        if not mainCurrentRecord == 0:
            mainCurrentRecord = mainCurrentRecord - 1
            config.currentRecord["main"] = mainCurrentRecord
            ubCommand = config.history["main"][mainCurrentRecord]
            self.ubCommandLineEdit.setText(ubCommand)
            self.runUbCommand(False)

    def forward(self):
        mainCurrentRecord = config.currentRecord["main"]
        if not mainCurrentRecord == (len(config.history["main"]) - 1):
            mainCurrentRecord = mainCurrentRecord + 1
            config.currentRecord["main"] = mainCurrentRecord
            ubCommand = config.history["main"][mainCurrentRecord]
            self.ubCommandLineEdit.setText(ubCommand)
            self.runUbCommand(False)

    def displayUbCommand(self):
        title = self.page.title()
        exceptionTuple = (self.ubCommandLineEdit.text(), "UniqueBible.app", "about:blank")
        if not (title.startswith("data:text/html;") or title.startswith("file:///") or title in exceptionTuple):
            self.ubCommandLineEdit.setText(title)
            self.runUbCommand()

    def parallel(self):
        parallelRatio = {
            0: (1, 0),
            1: (2, 1),
            2: (1, 1),
            3: (1, 2),
        }
        if self.parallelMode == 3:
            self.parallelMode = 0
            self.centralWidget.parallelView.hide()
        else:
            self.parallelMode += 1
            self.centralWidget.parallelView.show()
        ratio = parallelRatio[self.parallelMode]
        self.centralWidget.layout.setColumnStretch(1, ratio[0])
        self.centralWidget.layout.setColumnStretch(2, ratio[1])

    def runUbCommand(self, addRecord=True):
        ubCommand = self.ubCommandLineEdit.text()
        result = self.ubCommandParser.parser(ubCommand)
        view = result[0]
        content = result[1]
        if content == "INVALID_COMMAND_ENTERED":
            pass
        else:
            html = "<!DOCTYPE html><html><head><title>UniqueBible.app</title><link rel='stylesheet' type='text/css' href='bible.css'></head><body style='font-size: "+str(config.fontSize)+"%;'>"
            html += content
            html += "<script>activeVerse = document.getElementById('v"+str(config.mainB)+"."+str(config.mainC)+"."+str(config.mainV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = 'red'; }</script>"
            html += "</body></html>"
            views = {
                "main": self.mainView,
                "parallel": self.parallelView,
            }
            views[view].setHtml(html, baseUrl)
            if addRecord == True:
                self.addHistoryRecord(view, ubCommand)

    def addHistoryRecord(self, view, ubCommand):
        viewhistory = config.history[view]
        if not viewhistory[len(viewhistory) - 1] == ubCommand:
            viewhistory.append(ubCommand)
            # set maximum number of history records for each view here
            historyRecordAllowed = config.historyRecordAllowed
            if len(viewhistory) > historyRecordAllowed:
                viewhistory = viewhistory[-historyRecordAllowed:]
            config.history[view] = viewhistory
            config.currentRecord[view] = len(viewhistory) - 1


class CentralWidget(QWidget):

    def __init__(self, parent):        
        super().__init__()
        self.layout = QGridLayout()

        # content in unicode html format - Content larger than 2 MB cannot be displayed
        self.html = "<h1>UniqueBible.app</h1><p><ref onclick=\"document.title='TESTING IN PROGRESS';\">development in progress</ref></p><p><a href=\"https://UniqueBible.app\"><img src='UniqueBible.png' alt='Marvel.Bible icon'></a></p>"
        self.mainView = WebEngineView()
        self.mainView.setHtml(self.html, baseUrl)
        self.parallelView = WebEngineView()
        self.parallelView.setHtml("Parallel View", baseUrl)
        self.parallelView.hide() # hide parallel view by default

        self.layout.addWidget(self.mainView, 0, 1)
        self.layout.addWidget(self.parallelView, 0, 2)

        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 0)

        self.setLayout(self.layout)


class WebEngineView(QWebEngineView):
    def __init__(self):
        super().__init__()

    def createWindow(self, windowType):
        # an example: https://stackoverflow.com/questions/47897467/qwebengine-open-createwindow-if-target-blank
        if windowType == QWebEnginePage.WebBrowserWindow or windowType == QWebEnginePage.WebBrowserTab:
            print("testing open new window1")
            # read ubCommand, placed in document.title with javascript
            ubCommand = self.title()
            self.runUbCommand(ubCommand)
        return super().createWindow(windowType)

    def runUbCommand(self, ubCommand):

        # content in unicode html format - Content larger than 2 MB cannot be displayed
        print("Unique Bible Command: "+ubCommand) # develop further from here to handle Unique Bible Command
        html = ubCommand # develop further from here to handle Unique Bible Command

        self.popoverView = WebEngineViewPopover()
        self.popoverView.setHtml(html, baseUrl)
        self.popoverView.show()


class WebEngineViewPopover(QWebEngineView):
    def __init__(self):
        super().__init__()

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserTab:
            print("testing open new window2")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    
    # set full screen size
    availableGeometry = app.desktop().availableGeometry(mainWindow)
    mainWindow.resize(availableGeometry.width(), availableGeometry.height())
    
    mainWindow.show()

    sys.exit(app.exec_())
