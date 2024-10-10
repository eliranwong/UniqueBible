import config
from gui.SimpleBrowser import SimpleBrowser
from util.TextUtil import TextUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QUrl
else:
    from qtpy.QtCore import QUrl


config.mainWindow.googleYoutube = SimpleBrowser(config.mainWindow, "Youtube")
if config.pluginContext:
    content = TextUtil.plainTextToUrl(config.pluginContext)
    config.mainWindow.googleYoutube.setUrl(QUrl(f"https://youtube.com/results?search_query={content}"))
else:
    config.mainWindow.googleYoutube.setUrl(QUrl("https://youtube.com"))
config.mainWindow.googleYoutube.show()
