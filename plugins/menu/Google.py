import config
from gui.SimpleBrowser import SimpleBrowser
from util.TextUtil import TextUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QUrl
else:
    from qtpy.QtCore import QUrl


config.mainWindow.googleSearch = SimpleBrowser(config.mainWindow, "Google")
config.mainWindow.googleSearch.setUrl(QUrl("https://www.google.com"))
config.mainWindow.googleSearch.show()
