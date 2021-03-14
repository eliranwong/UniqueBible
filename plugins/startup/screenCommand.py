import config, re
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite

def presentReferenceOnFullScreen(command, source):
    if ":::" in command:
        screenNo, reference, *_ = command.split(":::")
    else:
        screenNo = config.presentationScreenNo
        reference = command
    verseList = BibleVerseParser(config.parserStandarisation).extractAllReferences(reference, False)
    if command.count(":::") == 2:
            style = command.split(":::")[2]
    else:
        style = "font-size:{0}em;margin-left:{1}px;margin-right:{1}px;color:{2}".format(config.presentationFontSize, config.presentationMargin, config.presentationColorOnDarkTheme if config.theme == "dark" else config.presentationColorOnLightTheme)
    if not verseList:
        content = "<div style='display:flex;'><div style='position: absolute;top: {2}%;transform: translateY(-50%);{1}'>{0}</div></div>".format(re.sub("\n", "<br>", command), style, config.presentationVerticalPosition)
        return ("popover.fullscreen".format(screenNo), content, {})
    else:
        verses = BiblesSqlite().readMultipleVerses(config.mainText, verseList, options={"presentMode": True, "style": style})
        return ("popover.fullscreen".format(screenNo), verses, {})

config.mainWindow.textCommandParser.interpreters["screen"] = (presentReferenceOnFullScreen, """
# [KEYWORD] SCREEN
# Shows verse(s) or text in a new window for presentation purposes.
# Users can still update the content being displayed through UBA main window / control panel / command line interface.
# This displays bible verse(s) in presentation mode if command suffix contains bible reference(s).
# If command suffix does not contain a bible reference, command suffix text is displayed in presentation mode.
# Usage - SCREEN:::[BIBLE_REFERENCE(S)]
# Usage - SCREEN:::[TEXT_TO_BE_DISPLAYED]
# Usage - SCREEN:::[SCREEN_NO]:::[BIBLE_REFERENCE(S)]
# Usage - SCREEN:::[SCREEN_NO]:::[TEXT_TO_BE_DISPLAYED]
# e.g. SCREEN:::Jesus is the BEST!
# e.g. SCREEN:::John 3:16
# e.g. SCREEN:::John 3:16-18
# e.g. SCREEN:::John 3:16; Rm 5:8
# SCREEN_NO is optional; users can use it to specify on which screen reference is displayed in case users have multiple screens.
# 0 = 1st screen, 1 = 2nd screen, 3 = 3rd screen, etc.
# e.g. SCREEN:::1:::Jesus is the BEST!
# e.g. SCREEN:::1:::John 3:16
# e.g. SCREEN:::1:::John 3:16-18
# e.g. SCREEN:::1:::John 3:16; Rm 5:8
# Customisation: The following values are configuration by editing config.py:
#    presentationScreenNo - default screen number if users does not specify one; -1 by default; 0 = 1st screen, 1 = 2nd screen, 3 = 3rd screen, etc.
#    presentationFontSize - font size of bible text; 3.0 by default
#    presentationMargin - left and right margins of displayed text; 50 by default
#    presentationColorOnLightTheme - text color applied when light theme is used; 'magenta' by default 
#    presentationColorOnDarkTheme - text color applied when dark theme is used; 'black' by default
#    presentationVerticalPosition - the position where text is displayed vertically; 50 by default placing the text in the centre
# TODO: test on different platforms
# TODO: add a gui to work with this command keyword""")
