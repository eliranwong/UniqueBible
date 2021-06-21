import config, webbrowser
from util.TextUtil import TextUtil

if config.pluginContext:
    content = TextUtil.plainTextToUrl(config.pluginContext)
    webbrowser.open("http://www.laparola.net/greco/louwnida.php/search?LNGloss={0}".format(content))
else:
    config.contextSource.messageNoSelection()
