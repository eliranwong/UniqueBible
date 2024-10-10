from uniquebible import config
from uniquebible.util.TextUtil import TextUtil
from uniquebible.gui.SimpleBrowser import SimpleBrowser
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QUrl
else:
    from qtpy.QtCore import QUrl


"""
https://office.com
https://teams.microsoft.com
https://outlook.office.com/mail
https://outlook.office.com/calendar
https://www.office.com/launch/onenote
https://www.office.com/launch/word
https://www.office.com/launch/excel
https://www.office.com/launch/powerpoint
https://www.office.com/launch/forms
https://onedrive.live.com/about/en-gb/signin

"""

selectedText = config.mainWindow.selectedText()
if selectedText:
    content = TextUtil.plainTextToUrl(selectedText)
    url = f"https://outlook.office.com/mail/deeplink/compose?subject=UniqueBible.app&body={content}"
else:
    url = "https://outlook.office.com/mail"

config.mainWindow.msoutlook = SimpleBrowser(config.mainWindow, "Microsoft Outlook")
config.mainWindow.msoutlook.setUrl(QUrl(url))
config.mainWindow.msoutlook.show()