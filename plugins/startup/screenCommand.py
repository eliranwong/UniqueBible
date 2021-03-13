import config
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite

def presentReferenceOnFullScreen(command, source):
    if ":::" in command:
        screenNo, reference = command.split(":::", 1)
    else:
        screenNo = -1
        reference = command
    verseList = BibleVerseParser(config.parserStandarisation).extractAllReferences(reference, False)
    if not verseList:
        #config.mainWindow.displayMessage(config.thisTranslation["message_noReference"])
        return (source, "INVALID_COMMAND_ENTERED", {})
    else:
        style = "font-size:{0}em;margin-left:{1}px;margin-right:{1}px;color:{2}".format(config.presentationFontSize, config.presentationMargin, config.presentationColorOnDarkTheme if config.theme == "dark" else config.presentationColorOnLightTheme)
        biblesSqlite = BiblesSqlite()
        verses = biblesSqlite.readMultipleVerses(config.mainText, verseList, options={"presentMode": True, "style": style})
        del biblesSqlite
        return ("popover.fullscreen".format(screenNo), verses, {})

config.mainWindow.textCommandParser.interpreters["screen"] = (presentReferenceOnFullScreen, """
# [KEYWORD] SCREEN
# Shows verse(s) in a new window for presentation purposes
# Users can still control the content being displayed through main window / command line interface
# Usage - SCREEN:::[BIBLE_REFERENCE(S)]
# Usage - SCREEN:::[SCREEN_NO]:::[BIBLE_REFERENCE(S)]
# e.g. SCREEN:::John 3:16
# e.g. SCREEN:::John 3:16-18
# SCREEN_NO is optional; users can use it to specify on which screen reference is displayed in case users have multiple screens.
# 0 = 1st screen, 1 = 2nd screen, 3 = 3rd screen, etc.
# e.g. SCREEN:::1:::John 3:16
# e.g. SCREEN:::1:::John 3:16-18
# Customisation: The following values are configuration by editing config.py:
#    presentationFontSize - font size of bible text; 3.0 by default
#    presentationMargin - left and right margins of displayed text; 50 by default
#    presentationColorOnLightTheme - text color applied when light theme is used; 'magenta' by default 
#    presentationColorOnDarkTheme - text color applied when dark theme is used; 'black' by default
#    presentationVerticalTopPosition - the top position where text starts to be displayed; 50 by default
# TODO: test on different platforms
# TODO: add a gui to work with this command keyword""")
