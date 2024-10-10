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
    url = f"https://www.google.com/search?q={content}"
else:
    url = "https://www.google.com"

config.mainWindow.googleSearch = SimpleBrowser(config.mainWindow, "Google")
config.mainWindow.googleSearch.setUrl(QUrl(url))
config.mainWindow.googleSearch.show()
