import config

if config.pluginContext:
    config.mainWindow.runTextCommand("SPEAK:::he:::{0}".format(config.pluginContext))
else:
    config.contextSource.messageNoSelection()
