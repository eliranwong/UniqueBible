import config

if config.pluginContext:
    useFastVerseParsing = config.useFastVerseParsing
    config.useFastVerseParsing = False
    config.mainWindow.textCommandChanged(config.pluginContext, "main")
    config.useFastVerseParsing = useFastVerseParsing
else:
    config.contextSource.messageNoSelection()
