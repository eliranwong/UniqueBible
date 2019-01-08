# documentation: https://doc.qt.io/qtforpython/PySide2/QtWebEngineWidgets/QWebEngineView.html#PySide2.QtWebEngineWidgets.PySide2.QtWebEngineWidgets.QWebEngineView.setHtml

import os
from PySide2.QtWidgets import QApplication
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl

app = QApplication([])

view = QWebEngineView()

# content in unicode html format - Content larger than 2 MB cannot be displayed
html = "<h1>Heading</h1><p>paragraph</p><p><img src='marvel.png' alt='Marvel.Bible icon'></p>"

# External objects, such as stylesheets or images referenced in the HTML document, are located RELATIVE TO baseUrl .
# e.g. put all local files linked by html's content in folder "htmlResources"
relativePath = os.path.join("htmlResources", "marvel.png")
absolutePath = os.path.abspath(relativePath)
baseUrl = QUrl.fromLocalFile(absolutePath)

view.setHtml(html, baseUrl)
view.show()

app.exec_()