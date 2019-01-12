import os, sys
from PySide2.QtCore import QUrl
from PySide2.QtGui import QIcon, QGuiApplication
from PySide2.QtWidgets import (QApplication, QDesktopWidget, QGridLayout, QLineEdit, QMainWindow, QPushButton, QToolBar, QWidget)
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from UbCommandParser import UbCommandParser

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Unique Bible App')
        
        appIconFile = os.path.join("htmlResources", "UniqueBible.png")
        appIcon = QIcon(appIconFile)
        QGuiApplication.setWindowIcon(appIcon)
        
        self.setupToolBar()
        self.setupBaseUrl()
        
        self.centralWidget = CentralWidget(self)
        self.webEngineView = self.centralWidget.webEngineView
        self.page = self.webEngineView.page()
        self.page.titleChanged.connect(self.displayUbCommand)
        self.setCentralWidget(self.centralWidget)

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
        self.ubCommandLineEdit.setText("[Enter command here]")
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
        print("Back")

    def forward(self):
        print("Forward")

    def displayUbCommand(self):
        title = self.page.title()
        if not title == "about:blank":
            self.ubCommandLineEdit.setText(title)

    def parallel(self):
        parallelRatio = {
            0: (1, 0),
            1: (2, 1),
            2: (1, 1),
            3: (1, 2),
        }
        if self.parallelMode == 3:
            self.parallelMode = 0
            self.centralWidget.webEngineView2.hide()
        else:
            self.parallelMode += 1
            self.centralWidget.webEngineView2.show()
        ratio = parallelRatio[self.parallelMode]
        self.centralWidget.layout.setColumnStretch(1, ratio[0])
        self.centralWidget.layout.setColumnStretch(2, ratio[1])

    def runUbCommand(self):
        ubCommand = self.ubCommandLineEdit.text()
        commandParser = UbCommandParser()
        html = commandParser.parser(ubCommand)
        del commandParser
        self.webEngineView.setHtml(html)


class CentralWidget(QWidget):

    def __init__(self, parent):        
        super().__init__()
        self.layout = QGridLayout()

        # content in unicode html format - Content larger than 2 MB cannot be displayed
        self.html = "<h1>Heading</h1><p><ref onclick=\"document.title='TESTING IN PROGRESS';\">paragraph</ref></p><p><a href=\"https://UniqueBible.app\"><img src='UniqueBible.png' alt='Marvel.Bible icon'></a></p>"
        self.webEngineView = WebEngineView()
        self.webEngineView.setHtml(self.html, baseUrl)
        self.webEngineView2 = WebEngineView()
        self.webEngineView2.setHtml("Parallel View", baseUrl)
        self.webEngineView2.hide() # hide parallel view by default

        self.layout.addWidget(self.webEngineView, 0, 1)
        self.layout.addWidget(self.webEngineView2, 0, 2)

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

        self.webEngineViewPopover = WebEngineViewPopover()
        self.webEngineViewPopover.setHtml(html, baseUrl)
        self.webEngineViewPopover.show()


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