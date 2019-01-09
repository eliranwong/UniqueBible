from PySide2.QtWidgets import QApplication
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl

def finishLoading():
    print("loadFinished")
    print(type(view.page()))
    print("Title: "+view.title())

def printTitle():
    print("Title changed to: "+view.title())

app = QApplication([])

view = QWebEngineView()

view.loadStarted.connect(print("loadStarted"))
view.loadProgress.connect(print("loadProgress"))
view.loadFinished.connect(finishLoading)

view.titleChanged.connect(printTitle)

view.load(QUrl("https://marvel.bible"))
view.show()

app.exec_()