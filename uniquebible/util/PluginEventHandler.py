import glob
import os
import re
from uniquebible import config


class PluginEventHandler:

    eventHandlers = None

    # Supported eventTypes
    #
    # eventType: command
    # runs a script when a particular command is executed
    #
    # eventType: post_parse_bible
    # called at the end of textBibleVerseParser to be able to modify the output content
    # content is in config.eventContent
    #
    # eventType: lexicon_entry
    # called to manipulate the lexicon entry word
    # word is in config.eventEntry
    #
    # eventType: post_theme_change
    # called after a theme is changed
    #
    @staticmethod
    def handleEvent(eventType, eventCommand=''):
        config.eventType = eventType
        config.eventCommand = eventCommand
        if PluginEventHandler.eventHandlers is None:
            filelist = glob.glob(os.path.join(config.packageDir, "plugins", "event", "*.py"))
            PluginEventHandler.eventHandlers = filelist
        if len(PluginEventHandler.eventHandlers) == 0:
            return
        try:
            commandList = eventCommand.split(":::")
            command = commandList[0].lower()
            if eventType in ["command"]:
                searchfile = re.compile(f".*{eventType}_{command}.*.py")
            else:
                searchfile = re.compile(f".*{eventType}.*.py")
            filelist = list(filter(searchfile.match, PluginEventHandler.eventHandlers))
            for file in filelist:
                config.mainWindow.execPythonFile(file)
        except Exception as ex:
            print(ex)
