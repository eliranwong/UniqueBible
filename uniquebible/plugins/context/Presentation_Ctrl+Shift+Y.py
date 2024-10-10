from uniquebible import config

presentationParser = config.presentationParser

config.presentationParser = True

if config.pluginContext:
    config.mainWindow.runTextCommand("SCREEN:::{0}".format(config.pluginContext))
else:
    config.contextSource.messageNoSelection()

config.presentationParser = presentationParser
