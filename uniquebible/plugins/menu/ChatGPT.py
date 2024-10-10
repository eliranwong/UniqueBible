from uniquebible import config
from uniquebible.gui.SimpleBrowser import SimpleBrowser
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QUrl
else:
    from qtpy.QtCore import QUrl


config.mainWindow.chatGPT = SimpleBrowser(config.mainWindow, "OpenAI ChatGPT")
config.mainWindow.chatGPT.setUrl(QUrl("https://chat.openai.com/chat"))
config.mainWindow.chatGPT.show()