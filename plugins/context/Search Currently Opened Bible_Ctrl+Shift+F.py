import config

if config.pluginContext:
    config.mainWindow.runTextCommand("SEARCH:::{0}".format(config.pluginContext))
else:
    config.contextSource.messageNoSelection()
