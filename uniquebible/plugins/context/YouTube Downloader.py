from uniquebible import config
from uniquebible.util.TextUtil import TextUtil

if config.pluginContext:
    content = TextUtil.plainTextToUrl(config.pluginContext)
    config.mainWindow.openMiniBrowser("https://youtube.com/results?search_query={0}".format(content))
else:
    config.mainWindow.openMiniBrowser("https://youtube.com")
