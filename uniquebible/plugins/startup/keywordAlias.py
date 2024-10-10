from uniquebible import config

shortcuts = (
    ("diff", "DIFFERENCE", config.mainWindow.textCommandParser.textDiff),
    ("s3dict", "SEARCHTHIRDDICTIONARY", config.mainWindow.textCommandParser.thirdDictionarySearch),
    ("3dict", "THIRDDICTIONARY", config.mainWindow.textCommandParser.thirdDictionaryOpen),
    ("_mc", "_mastercontrol", config.mainWindow.textCommandParser.openMasterControl),
)

for alias, keyword, function in shortcuts:
    config.mainWindow.textCommandParser.interpreters[alias] = (function, "\n# [KEYWORD] {0}\n# An alias to command keyword '{1}'".format(alias, keyword))
