import config

print(config.mainWindow.divider)
print("Enter a search item:")
userInput = config.mainWindow.simplePrompt()
if not userInput or userInput.lower() == config.terminal_cancel_action:
    config.mainWindow.cancelAction()
else:
    command = f"THIRDDICTIONARY:::wordnet:::{userInput}"
    print(config.mainWindow.divider)
    content = config.mainWindow.getContent(command)
    if content == "[MESSAGE][not found]":
        exactMatch = False
        command = f"SEARCHTHIRDDICTIONARY:::wordnet:::{userInput}"
        config.mainWindow.printRunningCommand(command)
        content = config.mainWindow.getContent(command)
    else:
        exactMatch = True
    print(content)
    print(config.mainWindow.divider)
    if not exactMatch:
        print("Enter an entry:")
        userInput = config.mainWindow.simplePrompt()
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            config.mainWindow.cancelAction()
        else:
            command = f"THIRDDICTIONARY:::wordnet:::{userInput}"
            config.mainWindow.printRunningCommand(command)
            print(config.mainWindow.divider)
            print(config.mainWindow.getContent(command))
