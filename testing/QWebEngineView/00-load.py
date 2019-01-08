from PySide2.QtWidgets import QApplication
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtCore import QUrl

app = QApplication([])

view = QWebEngineView()
view.load(QUrl("https://marvel.bible"))
view.show()

app.exec_()