import config, webbrowser

if config.pluginContext:
    webbrowser.open("https://youtube.com/results?search_query={0}".format(config.pluginContext))
else:
    config.contextSource.messageNoSelection()
