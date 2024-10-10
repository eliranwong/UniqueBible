from uniquebible import config
from uniquebible.gui.SimpleBrowser import SimpleBrowser
from uniquebible.util.TextUtil import TextUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QUrl
else:
    from qtpy.QtCore import QUrl

selectedText = config.mainWindow.selectedText()
if selectedText:
    content = TextUtil.plainTextToUrl(selectedText)
    url = f"https://mail.google.com/mail/u/0/?fs=1&tf=cm&su=UniqueBible.app&body={content}"
else:
    url = "https://gmail.com"

config.mainWindow.gmail = SimpleBrowser(config.mainWindow, "Gmail")
config.mainWindow.gmail.setUrl(QUrl(url))
config.mainWindow.gmail.show()
