
from uniquebible import config
from uniquebible.gui.SimpleBrowser import SimpleBrowser
from uniquebible.util.TextUtil import TextUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QUrl
else:
    from qtpy.QtCore import QUrl


config.mainWindow.laparola = SimpleBrowser(config.mainWindow, "Louw-Nida Lexicon")
if config.pluginContext:
    content = TextUtil.plainTextToUrl(config.pluginContext)
    config.mainWindow.laparola.setUrl(QUrl(f"http://www.laparola.net/greco/louwnida.php/search?LNGloss={content}"))
else:
    config.mainWindow.laparola.setUrl(QUrl("http://www.laparola.net/greco/louwnida.php"))
config.mainWindow.laparola.show()
