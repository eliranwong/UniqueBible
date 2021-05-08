import config
from qtpy.QtCore import QDir
from qtpy.QtWidgets import QInputDialog, QLineEdit
from qtpy.QtWebEngineWidgets import QWebEnginePage

def findText(found):
    if not found:
        config.mainWindow.displayMessage("Not found!")

text, ok = QInputDialog.getText(config.mainWindow, "QInputDialog.getText()",
        "Instant Highlight:", QLineEdit.Normal,
        QDir.home().dirName())
if ok and text != '':
    config.mainWindow.mainPage.findText(text, QWebEnginePage.FindBackward, findText)
