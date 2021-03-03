from qtpy.QtWidgets import QApplication
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtCore import QUrl

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