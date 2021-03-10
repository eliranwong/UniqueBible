import config, readline, sys
from qtpy.QtGui import QGuiApplication
from install.module import *
try:
    import html_text
    moduleInstalled = True
except:
    moduleInstalled = False

def printContentOnConsole(text):
    if not "html-text" in sys.modules:
        import html_text
    print(html_text.extract_text(text))
    return text

if not moduleInstalled:
    installmodule("html-text")

config.mainWindow.hide()
#config.cli = True
#config.printContentOnConsole = printContentOnConsole
config.bibleWindowContentTransformers.append(printContentOnConsole)
config.studyWindowContentTransformers.append(printContentOnConsole)
while config.cli:
    print("--------------------")
    print("Enter '.bible' to read bible content, '.study' to read study content, '.gui' to launch gui, '.quit' to quit,")
    command = input("or UBA command: ").strip()
    if command == ".gui":
        del config.bibleWindowContentTransformers[-1]
        del config.studyWindowContentTransformers[-1]
        config.cli = False
    elif command == ".bible":
        config.mainWindow.mainPage.runJavaScript("document.documentElement.outerHTML", 0, printContentOnConsole)
    elif command == ".study":
        config.mainWindow.studyPage.runJavaScript("document.documentElement.outerHTML", 0, printContentOnConsole)
    elif command == ".quit":
        exit()
    else:
        config.mainWindow.runTextCommand(command)
config.mainWindow.show()
