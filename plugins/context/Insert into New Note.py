import config

if config.pluginContext:
    config.contextItem = config.pluginContext
    config.mainWindow.createNewNoteFile()
else:
    config.contextSource.messageNoSelection()
 