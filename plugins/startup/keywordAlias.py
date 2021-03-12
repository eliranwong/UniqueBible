import config

shortcuts = (
    ("diff", "DIFFERENCE", config.mainWindow.textCommandParser.textDiff),
    ("s3dict", "SEARCHTHIRDDICTIONARY", config.mainWindow.textCommandParser.thirdDictionarySearch),
    ("3dict", "THIRDDICTIONARY", config.mainWindow.textCommandParser.thirdDictionaryOpen),
    ("_mc", "_mastercontrol", config.mainWindow.textCommandParser.openMasterControl),
)

for alias, keyword, function in shortcuts:
    config.mainWindow.textCommandParser.interpreters[alias] = (function, "An alias to command keyword '{0}'".format(keyword))
