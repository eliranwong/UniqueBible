import config, sys
from install.module import *
try:
    import html_text
    moduleInstalled = True
except:
    moduleInstalled = False

def printContentOnConsole(html):
    if not "html-text" in sys.modules:
        import html_text
    print(html_text.extract_text(html))

if not moduleInstalled:
    installmodule("html-text")
config.printContentOnConsole = printContentOnConsole
config.contextSource.page().runJavaScript("document.documentElement.outerHTML", 0, printContentOnConsole)
