from uniquebible import config
import re
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.db.BiblesSqlite import BiblesSqlite
from uniquebible.db.ToolsSqlite import Book

config.presentationParser = True

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
    content = command if not verseList or not config.presentationParser else BiblesSqlite().readMultipleVerses(config.mainText, verseList, presentMode=True)
    content = "<div style='display:flex;'><div style='position: absolute;top: {2}%;transform: translateY(-{3}%);{1}'>{0}</div></div>".format(re.sub("\n", "<br>", content), style, config.presentationVerticalPosition, config.presentationHorizontalPosition)
    return ("popover.fullscreen".format(screenNo), content, {})

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
# Usage - SCREEN:::[SCREEN_NO]:::[BIBLE_REFERENCE(S)]:::[CUSTOM_STYLE]
# Usage - SCREEN:::[SCREEN_NO]:::[TEXT_TO_BE_DISPLAYED]:::[CUSTOM_STYLE]
# SCREEN_NO is optional if custom style is not given
# If SCREEN_NO is not given, SCREEN_NO is determined by config.presentationScreenNo
# e.g. SCREEN:::Jesus is the BEST!
# e.g. SCREEN:::John 3:16
# e.g. SCREEN:::John 3:16-18
# e.g. SCREEN:::John 3:16; Rm 5:8
# SCREEN_NO is optional if custom style is not given; users can use it to specify on which screen reference is displayed in case users have multiple screens.
# 0 = 1st screen, 1 = 2nd screen, 3 = 3rd screen, etc.
# e.g. SCREEN:::1:::Jesus is the BEST!
# e.g. SCREEN:::1:::John 3:16
# e.g. SCREEN:::1:::John 3:16-18
# e.g. SCREEN:::1:::John 3:16; Rm 5:8
# SCREEN_NO must be given if CUSTOM_STYLE is given
# When CUSTOM_STYLE is specified
# e.g. SCREEN:::1:::Rom 5:8, Rom 5:12:::font-size:1.5em;margin-left:50px;margin-right:50px;color:red
# Customisation: The following values are configuration by editing config.py:
# When CUSTOM_STYLE is given, the following values are ignored.
#    presentationScreenNo - default screen number if users does not specify one; -1 by default; 0 = 1st screen, 1 = 2nd screen, 3 = 3rd screen, etc.
#    presentationFontSize - font size of bible text; 3.0 by default
#    presentationMargin - left and right margins of displayed text; 50 by default
#    presentationColorOnLightTheme - text color applied when light theme is used; 'magenta' by default 
#    presentationColorOnDarkTheme - text color applied when dark theme is used; 'black' by default
#    presentationVerticalPosition - the position where text is displayed vertically; 50 by default placing the text in the centre
#    presentationHorizontalPosition - the position where text is displayed horizontally; 50 by default placing the text in the centre""")

def presentBookOnFullScreen(command, source):
    bookName, chapter, paragraph = command.split(":::")
    book = Book(bookName)
    sections = book.getParagraphSectionsByChapter(chapter)
    para = int(paragraph)
    if para >= len(sections):
        para = 0
    content = sections[para]
    screenNo = 0
    marginTop = config.presentationVerticalPosition
    titleFontSize = config.presentationFontSize
    titleStyle = "font-size:{0}em;margin-left:{1}px;margin-right:{1}px;color:{2}".format(titleFontSize, config.presentationMargin, config.presentationColorOnDarkTheme if config.theme == "dark" else config.presentationColorOnLightTheme)
    textFontSize = config.presentationFontSize * .9
    textStyle = "font-size:{0}em;margin-left:{1}px;margin-right:{1}px;color:{2}".format(textFontSize, config.presentationMargin, config.presentationColorOnDarkTheme if config.theme == "dark" else config.presentationColorOnLightTheme)
    content = "<div style='margin-top: {4}px'><div style='{2}'>{0}</div><div style='{3}'>{1}</div></div>".format(chapter, content, titleStyle, textStyle, marginTop)
    return ("popover.fullscreen".format(screenNo), content, {})

config.mainWindow.textCommandParser.interpreters["screenbook"] = (presentBookOnFullScreen, """
# [KEYWORD] SCREENBOOK
# Shows book chapter in a new window for presentation purposes.  
# Typically used for Hymn Lyrics.
# Usage - SCREENBOOK:::[BOOK]:::[CHAPTER]:::[PARAGRAPH]
# e.g. SCREENBOOK:::Hymn Lyrics - English:::Amazing Grace:::0
""")
