import config, webbrowser

if config.pluginContext:
    webbrowser.open("https://mail.google.com/mail/u/0/?fs=1&tf=cm&su=UniqueBible.app&body={0}".format(config.pluginContext))
else:
    webbrowser.open("https://mail.google.com/mail/u/0/?fs=1&tf=cm")
