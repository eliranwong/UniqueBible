import config

if config.pluginContext:
    config.mainWindow.runTextCommand("SPEAK:::el:::{0}".format(config.pluginContext))
else:
    config.contextSource.messageNoSelection()
