import config, webbrowser

if config.pluginContext:
    content = config.pluginContext.replace("\n", "%0D%0A")
    webbrowser.open("https://mail.google.com/mail/u/0/?fs=1&tf=cm&su=UniqueBible.app&body={0}".format(content))
else:
    webbrowser.open("https://mail.google.com/mail/u/0/?fs=1&tf=cm")
