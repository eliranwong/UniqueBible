from uniquebible import config
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

config.mainWindow.msonedrive = SimpleBrowser(config.mainWindow, "Microsoft OneDrive")
config.mainWindow.msonedrive.setUrl(QUrl("https://onedrive.live.com/about/en-gb/signin"))
config.mainWindow.msonedrive.show()