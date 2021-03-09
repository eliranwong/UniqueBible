import config
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite


def wrapHtml(content):
    activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.mainText, config.mainB, config.mainC, config.mainV)
    fontFamily = config.font
    fontSize = "{0}px".format(config.fontSize)
    html = ("<!DOCTYPE html><html><head><title>UniqueBible.app</title>"
            "<style>body {2} font-size: {4}; font-family:'{5}';{3} "
            "zh {2} font-family:'{6}'; {3} "
            "{8} {9}</style>"
            "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{7}.css'>"
            "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css'>"
            "<script src='js/common.js'></script>"
            "<script src='js/{7}.js'></script>"
            "<script src='w3.js'></script>"
            "<script src='js/custom.js'></script>"
            "{0}"
            "<script>var versionList = []; var compareList = []; var parallelList = []; "
            "var diffList = []; var searchList = [];</script></head>"
            "<body><span id='v0.0.0'></span>{1}</body></html>"
            ).format(activeBCVsettings,
                     content,
                     "{",
                     "}",
                     fontSize,
                     fontFamily,
                     config.fontChinese,
                     config.theme,
                     config.mainWindow.getHighlightCss(),
                     "")
    return html

def extractAllReferences():
    selectedText = config.contextSource.selectedText()
    parser = BibleVerseParser(config.parserStandarisation)
    verseList = parser.extractAllReferences(selectedText, False)
    del parser
    if not verseList:
        return ""
    else:
        biblesSqlite = BiblesSqlite()
        verses = biblesSqlite.readMultipleVerses(config.contextSource.getText(), verseList)
        del biblesSqlite
        return verses

html = extractAllReferences()
if html:
    config.mainWindow.instantView.setHtml(wrapHtml(html), config.baseUrl)
else:
    config.contextSource.displayMessage(config.thisTranslation["message_noReference"])
