import config, webbrowser
from util.TextUtil import TextUtil

if config.pluginContext:
    content = TextUtil.plainTextToUrl(config.pluginContext)
    webbrowser.open("https://youtube.com/results?search_query={0}".format(content))
else:
    config.contextSource.messageNoSelection()
