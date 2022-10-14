import config

if config.runMode == "terminal":
    # Add new command
    config.mainWindow.dotCommands[".w3m"] = ("open html content in w3m", lambda: config.mainWindow.cliTool("w3m -T text/html", config.mainWindow.html))
    config.mainWindow.dotCommands[".youtube"] = ("open youtube website", lambda: config.mainWindow.getContent("_website:::https://youtube.com"))
    # Add new startup exception
    config.mainWindow.startupException1.append(".w3m")
    # Add aliases
    config.mainWindow.dotCommands[".show"] = ("an alias to the '.info' command", config.mainWindow.info)
    config.mainWindow.dotCommands[".index"] = ("an alias to the '.openverseindex' command", lambda: config.mainWindow.openversefeature("INDEX"))
    config.mainWindow.dotCommands[".cindex"] = ("an alias to the '.openchapterindex' command", lambda: config.mainWindow.openchapterfeature("CHAPTERINDEX"))
