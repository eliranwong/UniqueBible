import config
from qtpy.QtWidgets import QInputDialog, QLineEdit

if config.pluginContext:
    config.mainWindow.mainPage.findText(config.pluginContext)
    config.mainWindow.studyPage.findText(config.pluginContext)
else:
    text, ok = QInputDialog.getText(config.mainWindow, "QInputDialog.getText()",
            "Find in Bible Window:", QLineEdit.Normal,
            "")
    if ok and text != '':
        config.mainWindow.mainPage.findText(text)
        config.mainWindow.studyPage.findText(text)
