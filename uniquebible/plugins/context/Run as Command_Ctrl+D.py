from uniquebible import config

if config.pluginContext:
    useLiteVerseParsing = config.useLiteVerseParsing
    config.useLiteVerseParsing = False
    config.mainWindow.textCommandChanged(config.pluginContext, "main")
    config.useLiteVerseParsing = useLiteVerseParsing
else:
    config.contextSource.messageNoSelection()
