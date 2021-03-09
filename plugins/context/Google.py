import config, webbrowser

if config.pluginContext:
    webbrowser.open("https://www.google.com/search?q={0}".format(config.pluginContext))
else:
    config.contextSource.messageNoSelection()
