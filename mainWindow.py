import os, sys
from PySide2.QtCore import QUrl
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (QApplication, QDesktopWidget, QLineEdit, QMainWindow, QPushButton, QToolBar)
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Unique Bible')

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

        # content in unicode html format - Content larger than 2 MB cannot be displayed
        html = "<h1>Heading</h1><p><ref onclick=\"document.title='UniqueBible - New Title';window.open('https://UniqueBible.app')\">paragraph</ref></p><p><a href=\"https://UniqueBible.app\"><img src='UniqueBible.png' alt='Marvel.Bible icon'></a></p>"

        # External objects, such as stylesheets or images referenced in the HTML document, are located RELATIVE TO baseUrl .
        # e.g. put all local files linked by html's content in folder "htmlResources"
        relativePath = os.path.join("htmlResources", "UniqueBible.png")
        absolutePath = os.path.abspath(relativePath)
        baseUrl = QUrl.fromLocalFile(absolutePath)

        self.webEngineView = WebEngineView()
        self.setCentralWidget(self.webEngineView)
        self.webEngineView.setHtml(html, baseUrl)

        self.page = self.webEngineView.page()

    def runUbCommand(self):
        ubCommand = self.ubCommandLineEdit.text()
        print("Run command: "+ubCommand)

    def back(self):
        print("Back")

    def forward(self):
        print("Forward")


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
        html = "<h1>Heading</h1><p><ref onclick=\"document.title='UniqueBible - New Title';window.open('https://UniqueBible.app')\">paragraph</ref></p><p><a href=\"https://UniqueBible.app\"><img src='UniqueBible.png' alt='Marvel.Bible icon'></a></p>"

        # External objects, such as stylesheets or images referenced in the HTML document, are located RELATIVE TO baseUrl .
        # e.g. put all local files linked by html's content in folder "htmlResources"
        relativePath = os.path.join("htmlResources", "UniqueBible.png")
        absolutePath = os.path.abspath(relativePath)
        baseUrl = QUrl.fromLocalFile(absolutePath)
        
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