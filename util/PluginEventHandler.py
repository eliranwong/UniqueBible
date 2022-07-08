import glob
import os
import re
import config


class PluginEventHandler:

    eventHandlers = None

    @staticmethod
    def handleEvent(eventType, eventCommand):
        config.eventType = eventType
        config.eventCommand = eventCommand
        if PluginEventHandler.eventHandlers is None:
            filelist = glob.glob(os.path.join("plugins", "event", "*.py"))
            PluginEventHandler.eventHandlers = filelist
        if len(PluginEventHandler.eventHandlers) == 0:
            return
        if eventType == "command":
            commandList = eventCommand.split(":::")
            command = commandList[0].lower()
            try:
                searchfile = re.compile(f".*command_{command}.py")
                filelist = list(filter(searchfile.match, PluginEventHandler.eventHandlers))
                for file in filelist:
                    config.mainWindow.execPythonFile(file)
            except Exception as ex:
                print(ex)
