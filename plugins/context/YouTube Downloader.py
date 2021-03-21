import config

if config.pluginContext:
    config.mainWindow.openMiniBrowser("https://youtube.com/results?search_query={0}".format(config.pluginContext))
else:
    config.contextSource.messageNoSelection()
