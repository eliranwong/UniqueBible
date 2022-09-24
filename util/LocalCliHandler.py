import re
from util.TextUtil import TextUtil
from util.RemoteCliMainWindow import RemoteCliMainWindow
from util.TextCommandParser import TextCommandParser
from util.CrossPlatform import CrossPlatform

class LocalCliHandler:

    def __init__(self):
        self.textCommandParser = TextCommandParser(RemoteCliMainWindow())
        self.crossPlatform = CrossPlatform()

    def getContent(self, command):
        if command.lower() == ".help":
            return self.getCommandDocumentation()
        view, content, dict = self.textCommandParser.parser(command, "cli")
        if content:
            self.crossPlatform.addHistoryRecord(view, command)
        else:
            content = "Command was processed!"
        return TextUtil.htmlToPlainText(content).strip()

    def getCommandDocumentation(self):
        print("\nUBA commands:")
        print("\n".join([re.sub("            #", "#", value[-1]) for value in self.textCommandParser.interpreters.values()]))
        return ""
