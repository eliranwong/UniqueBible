from uniquebible import config
from uniquebible.gui.SimpleBrowser import SimpleBrowser
from uniquebible.util.TextUtil import TextUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QUrl
else:
    from qtpy.QtCore import QUrl


config.mainWindow.googleSearch = SimpleBrowser(config.mainWindow, "Google")
if config.pluginContext:
    content = TextUtil.plainTextToUrl(config.pluginContext)
    config.mainWindow.googleSearch.setUrl(QUrl(f"https://www.google.com/search?q={content}"))
else:
    config.mainWindow.googleSearch.setUrl(QUrl("https://www.google.com"))
config.mainWindow.googleSearch.show()
