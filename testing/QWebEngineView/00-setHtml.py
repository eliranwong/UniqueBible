# documentation: https://doc.qt.io/qtforpython/PySide2/QtWebEngineWidgets/QWebEngineView.html#PySide2.QtWebEngineWidgets.PySide2.QtWebEngineWidgets.QWebEngineView.setHtml

import os
from PySide2.QtWidgets import QApplication
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl, Slot

def finishLoading():
    print("loadFinished")
    print("View Title: "+view.title())
    print("Page Title: "+page.title())

def titleChanged():
    print("Title changed to: "+view.title())
    print("Page changed to: "+page.title())

def selectionChanged():
    #print(page.action(page.Copy))
    page.triggerAction(page.Copy)
    print("Selected Text Copied: "+page.selectedText())

@Slot(str)
def linkHovered(hoveredLink):
    print(hoveredLink)
    # alternatively, run an alert box
    # page.runJavaScript("alert(\""+hoveredLink+"\")")

def urlChanged(qulr):
    print("url changed to: ")
    print(qulr)

app = QApplication([])

view = QWebEngineView()
page = view.page()

view.loadStarted.connect(print("loadStarted"))
view.loadProgress.connect(print("loadProgress"))
view.loadFinished.connect(finishLoading)
view.titleChanged.connect(titleChanged)

page.selectionChanged.connect(selectionChanged)
page.linkHovered.connect(linkHovered)
page.urlChanged.connect(urlChanged)

# content in unicode html format - Content larger than 2 MB cannot be displayed
html = "<h1>Heading</h1><p>paragraph</p><p><a href=\"https://marvel.bible\"><img src='marvel.png' alt='Marvel.Bible icon'></a></p>"

# External objects, such as stylesheets or images referenced in the HTML document, are located RELATIVE TO baseUrl .
# e.g. put all local files linked by html's content in folder "htmlResources"
relativePath = os.path.join("htmlResources", "marvel.png")
absolutePath = os.path.abspath(relativePath)
baseUrl = QUrl.fromLocalFile(absolutePath)

view.setHtml(html, baseUrl)
view.show()

app.exec_()