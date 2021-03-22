import config, webbrowser
from util.TextUtil import TextUtil

if config.pluginContext:
    content = TextUtil.plainTextToUrl(config.pluginContext)
    webbrowser.open("https://www.google.com/search?q={0}".format(content))
else:
    config.contextSource.messageNoSelection()
