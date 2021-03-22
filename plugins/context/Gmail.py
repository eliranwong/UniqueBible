import config, webbrowser
from util.TextUtil import TextUtil

if config.pluginContext:
    content = TextUtil.plainTextToUrl(config.pluginContext)
    webbrowser.open("https://mail.google.com/mail/u/0/?fs=1&tf=cm&su=UniqueBible.app&body={0}".format(content))
else:
    webbrowser.open("https://mail.google.com/mail/u/0/?fs=1&tf=cm")
