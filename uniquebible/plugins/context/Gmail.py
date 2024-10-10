from uniquebible import config
from uniquebible.gui.SimpleBrowser import SimpleBrowser
from uniquebible.util.TextUtil import TextUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QUrl
else:
    from qtpy.QtCore import QUrl


config.mainWindow.gmail = SimpleBrowser(config.mainWindow, "Gmail")
if config.pluginContext:
    content = TextUtil.plainTextToUrl(config.pluginContext)
    #webbrowser.open("https://mail.google.com/mail/u/0/?fs=1&tf=cm&su=UniqueBible.app&body={0}".format(content))
    config.mainWindow.gmail.setUrl(QUrl(f"https://mail.google.com/mail/u/0/?fs=1&tf=cm&su=UniqueBible.app&body={content}"))
else:
    #webbrowser.open("https://mail.google.com/mail/u/0/?fs=1&tf=cm")
    config.mainWindow.gmail.setUrl(QUrl("https://mail.google.com/mail/u/0/?fs=1&tf=cm"))
config.mainWindow.gmail.show()
