import config

config.shortcutGotoPresentation = "G"

if config.pluginContext:
    config.mainWindow.runTextCommand("SCREEN:::{0}".format(config.pluginContext))
else:
    config.contextSource.messageNoSelection()
