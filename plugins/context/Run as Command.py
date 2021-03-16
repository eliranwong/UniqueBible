import config

if config.pluginContext:
    config.mainWindow.textCommandChanged(config.pluginContext, "main")
else:
    config.contextSource.messageNoSelection()
