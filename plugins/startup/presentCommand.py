import logging
import config
from TextCommandParser import TextCommandParser


# [KEYWORD] PRESENT
# Shows passage in window for presentation purposes
# Usage - PRESENT:::[BIBLE_VERSION]:::[BIBLE_REFERENCE(S)]
# PRESENT:::KJV:::John 3:16
# Usage - PRESENT:::[BIBLE_VERSION]:::[BIBLE_REFERENCE(S)]:::[STYLE]
# PRESENT:::NET:::John 3:16-17:::font-size:1.5em;margin-left:50px;margin-right:50px;color:magenta
def presentCommand(command, source):
    logger = logging.getLogger('uba')
    msg = "Present passage {0}:{1}".format(command, source)
    logger.info(msg)
    # config.mainWindow.displayMessage(msg)
    parser = TextCommandParser(config.mainWindow)
    style = ""
    if command.count(":::") == 2:
        style = command.split(":::")[2]
        command = ":::".join(command.split(":::", 2)[:2])
    return parser.textAnotherView(command, source, "main", options={"presentMode": True, "style": style})

config.mainWindow.textCommandParser.interpreters["present"] = (presentCommand, "present")
