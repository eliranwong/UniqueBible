import config
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite

def presentReferenceOnFullScreen(command, source):
    verseList = BibleVerseParser(config.parserStandarisation).extractAllReferences(command, False)
    if not verseList:
        #config.mainWindow.displayMessage(config.thisTranslation["message_noReference"])
        return (source, "INVALID_COMMAND_ENTERED", {})
    else:
        style = "font-size:1.5em;margin-left:50px;margin-right:50px;color:magenta"
        biblesSqlite = BiblesSqlite()
        verses = biblesSqlite.readMultipleVerses(config.mainText, verseList, options={"presentMode": True, "style": style})
        del biblesSqlite
        return ("popover.fullscreen", verses, {})

config.mainWindow.textCommandParser.interpreters["screen"] = (presentReferenceOnFullScreen, """
# [KEYWORD] SCREEN
# Shows verse(s) in a new window for presentation purposes
# Users can still control the content being displayed through main window / command line interface
# Usage - SCREEN:::[BIBLE_REFERENCE(S)]
# e.g. SCREEN:::John 3:16
# e.g. SCREEN:::John 3:16-18
# TODO: test on different platforms
# TODO: support multiple, so users can specify on which screen reference is displayed.
# TODO: support multiple verses
# TODO: allow cutomisation of styles
# TODO: add a gui to work with this command keyword""")
