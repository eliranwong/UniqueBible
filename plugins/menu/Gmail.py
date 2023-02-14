import config
from gui.SimpleBrowser import SimpleBrowser
from util.TextUtil import TextUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QUrl
else:
    from qtpy.QtCore import QUrl


config.mainWindow.gmail = SimpleBrowser(config.mainWindow, "Gmail", "google")
config.mainWindow.gmail.setUrl(QUrl("https://gmail.com"))
config.mainWindow.gmail.show()
