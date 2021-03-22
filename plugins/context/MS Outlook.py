import config, webbrowser
from util.TextUtil import TextUtil

if config.pluginContext:
    content = TextUtil.plainTextToUrl(config.pluginContext)
    webbrowser.open("https://outlook.office.com/mail/deeplink/compose?subject=UniqueBible.app&body={0}".format(content))
else:
    webbrowser.open("https://outlook.office.com/mail/deeplink/compose")
