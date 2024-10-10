from uniquebible import config
import os
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.util.TextUtil import TextUtil
from uniquebible.util.WebtopUtil import WebtopUtil

def generateCharts(text):
    # Extract bible verse references
    useLiteVerseParsing = config.useLiteVerseParsing
    config.useLiteVerseParsing = False
    parser = BibleVerseParser(config.parserStandarisation)
    verses = parser.extractAllReferences(text, False)
    config.useLiteVerseParsing = useLiteVerseParsing
    if verses:
        # Formulate Table Data
        # Sort by Books
        counts = countVersesByBook(verses)
        if not len(counts.keys()) == 1:
            isSortedByChapter = False
            firstColumnTitle = ""
            data = []
            for bookNo in sorted(counts):
                bookName = parser.standardFullBookName[str(bookNo)]
                references = []
                for bcv in sorted(counts[bookNo]):
                    reference = parser.bcvToVerseReference(*bcv)
                    if len(bcv) == 3:
                        references.append('<ref onclick="bcv({0},{1},{2})">{3}</ref>'.format(*bcv, reference))
                    else:
                        references.append('<ref onclick="bcv({0},{1},{2},{3},{4})">{5}</ref>'.format(*bcv, reference))
                data.append("  <tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>".format(bookName, "; ".join(references), len(references)))
        else:
            isSortedByChapter = True
            # Sort by Chapters
            counts = countVersesByChapter(verses)
            data = []
            firstColumnTitle = ""
            for chapterNo in sorted(counts):
                if not firstColumnTitle:
                    bookNo = counts[chapterNo][0][0]
                    firstColumnTitle = parser.standardFullBookName[str(bookNo)]
                references = []
                for bcv in sorted(counts[chapterNo]):
                    reference = parser.bcvToVerseReference(*bcv)
                    if len(bcv) == 3:
                        references.append('<ref onclick="bcv({0},{1},{2})">{3}</ref>'.format(*bcv, reference))
                    else:
                        references.append('<ref onclick="bcv({0},{1},{2},{3},{4})">{5}</ref>'.format(*bcv, reference))
                data.append("  <tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>".format(chapterNo, "; ".join(references), len(references)))

        # table html
        table_html = getTableHtml("\n".join(data), str(len(verses)), firstColumnTitle)
        table_html = config.mainWindow.wrapHtml(table_html)
        config.mainWindow.html = table_html
        config.mainWindow.plainText = TextUtil.htmlToPlainText(table_html)
        displayHtml(table_html)

    else:
        config.mainWindow.displayMessage(config.thisTranslation["message_noReference"])

def displayHtml(html):
    if WebtopUtil.isPackageInstalled("w3m"):
        config.mainWindow.cliTool("w3m -T text/html -o confirm_qq=false", config.mainWindow.html)
    else:
        openHtmlFile(html)

def openHtmlFile(html):
    filepath = os.path.join("terminal_mode", "Unique_Bible_App.html")
    with open(filepath, "w", encoding="utf-8") as fileObj:
        fileObj.write(html)
    command = f"cmd:::{config.open} {filepath}"
    config.mainWindow.printRunningCommand(command)
    config.mainWindow.getContent(command)

def getTableHtml(data, totalVerseCount, firstColumnTitle=""):
    return """
<h2>Unique Bible App</h2>
<h3>{0} x """.format(config.thisTranslation["bibleReferences"])+totalVerseCount+"""</h3>
<table style="width:100%; border: 1px solid black;">
  <tr><th>{0}</th><th>{1}</th><th>{2}&nbsp;</th></tr>
""".format(firstColumnTitle if firstColumnTitle else config.thisTranslation["menu_book"], config.thisTranslation["bibleReferences"], config.thisTranslation["count"])+data+"""
</table>
"""

def countVersesByBook(verses):
    counts = {}
    for verse in verses:
        b = verse[0]
        counts[b] = counts[b] + [verse] if b in counts else [verse]
    return counts

def countVersesByChapter(verses):
    # assume all verses are in the same book
    counts = {}
    for verse in verses:
        c = verse[1]
        counts[c] = counts[c] + [verse] if c in counts else [verse]
    return counts


copiedText = config.mainWindow.getclipboardtext()
generateCharts(copiedText)
