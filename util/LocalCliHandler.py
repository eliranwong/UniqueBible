from util.TextUtil import TextUtil
from util.RemoteCliMainWindow import RemoteCliMainWindow
from util.TextCommandParser import TextCommandParser

class LocalCliHandler:

    def __init__(self):
        self.textCommandParser = TextCommandParser(RemoteCliMainWindow())

    def getContent(self, command):
        *_, content, dict = self.textCommandParser.parser(command, "cli")
        if not content:
            content = "Command was processed!"
        return TextUtil.htmlToPlainText(content).strip()
