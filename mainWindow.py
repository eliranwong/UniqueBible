import os, sys
from PySide2.QtCore import QUrl
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (QApplication, QDesktopWidget, QHBoxLayout, QLineEdit, QMainWindow, QPushButton, QToolBar, QWidget)
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle('Unique Bible App')
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
        self.ubCommandLineEdit.setText(self.page.title())

    def runUbCommand(self):
        ubCommand = self.ubCommandLineEdit.text()
        print("Unique Bible Command: "+ubCommand) # develop further from here to handle Unique Bible Command
        html = ubCommand # develop further from here to handle Unique Bible Command
        self.webEngineView.setHtml(html)


class CentralWidget(QWidget):

    def __init__(self, parent):        
        super().__init__()
        self.layout = QHBoxLayout(self)

        # content in unicode html format - Content larger than 2 MB cannot be displayed
        self.html = "<h1>Heading</h1><p><ref onclick=\"document.title='TESTING IN PROGRESS';window.open('https://UniqueBible.app')\">paragraph</ref></p><p><a href=\"https://UniqueBible.app\"><img src='UniqueBible.png' alt='Marvel.Bible icon'></a></p>"
        self.webEngineView = WebEngineView()
        self.webEngineView.setHtml(self.html, baseUrl)
        self.webEngineView2 = WebEngineView()
        self.webEngineView2.setHtml("Parallel Window", baseUrl)

        self.layout.addWidget(self.webEngineView)
        self.layout.addWidget(self.webEngineView2)
        #self.setLayout(layout)

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