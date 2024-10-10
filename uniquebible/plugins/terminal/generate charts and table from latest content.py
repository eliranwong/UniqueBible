from uniquebible import config
import os
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.util.TextUtil import TextUtil

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
                data.append("""  <tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>""".format(bookName, "; ".join(references), len(references)))
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
                data.append("""  <tr><td>{0}</td><td>{1}</td><td>{2}</td></tr>""".format(chapterNo, "; ".join(references), len(references)))

        # chart data
        import matplotlib.pyplot as plt
        import numpy as np

        totals = []
        labels = []
        if isSortedByChapter:
            chartTitle = "{0} x {1}".format(firstColumnTitle, len(verses))
            for chapterNo in sorted(counts):
                total = len(counts[chapterNo])
                totals.append(total)
                labels.append(f"Ch. {chapterNo} x {total}")
        else:
            chartTitle = "{0} x {1}".format(config.thisTranslation["bibleReferences"], len(verses))
            for bookNo in sorted(counts):
                total = len(counts[bookNo])
                totals.append(total)
                labels.append(f"{parser.standardAbbreviation[str(bookNo)]} x {total}")
        maxTotal = max(totals)
        explode = [0.1 if total == maxTotal else 0 for total in totals]
        x = np.array(labels)
        y = np.array(totals)

        # pie chart
        #plt.pie(y, labels=labels, explode=explode, shadow=True)
        plt.pie(y, labels=labels, explode=explode)
        plt.legend(title=chartTitle)
        imageFile = os.path.join("htmlResources", "pie_chart.png")
        plt.savefig(imageFile, dpi=300)
        plt.close()

        # bar chart
        plt.barh(x, y)
        #plt.legend(title=chartTitle)
        imageFile = os.path.join("htmlResources", "bar_chart.png")
        plt.savefig(imageFile, dpi=300)
        plt.close()

        # generate html
        table_html = getTableHtml("\n".join(data), str(len(verses)), firstColumnTitle)
        table_html = config.mainWindow.wrapHtml(table_html)
        config.mainWindow.html = table_html
        config.mainWindow.plainText = TextUtil.htmlToPlainText(table_html)

        config.mainWindow.saveAndOpenHtmlFile(table_html)
    else:
        config.mainWindow.displayMessage(config.thisTranslation["message_noReference"])

def getTableHtml(data, totalVerseCount, firstColumnTitle=""):
    pieChart = os.path.join(os.getcwd(), "htmlResources", "pie_chart.png")
    pieChartTag = TextUtil.imageToText(pieChart)
    pieChartTag = config.mainWindow.resizeHtmlImage(pieChartTag)
    barChart = os.path.join(os.getcwd(), "htmlResources", "bar_chart.png")
    barChartTag = TextUtil.imageToText(barChart)
    barChartTag = config.mainWindow.resizeHtmlImage(barChartTag)
    return """
<h2>Unique Bible App</h2>
<h3>{0} x """.format(config.thisTranslation["bibleReferences"])+totalVerseCount+"""</h3>
<table style="width:100%;">
  <tr><th>{0}</th><th>{1}</th><th>{2}&nbsp;</th></tr>
""".format(firstColumnTitle if firstColumnTitle else config.thisTranslation["menu_book"], config.thisTranslation["bibleReferences"], config.thisTranslation["count"])+data+"""
</table>
{0}
{1}
""".format(pieChartTag, barChartTag)

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

# run plugin
if ("Numpy" in config.enabled):
    if ("Matplotlib" in config.enabled):
        generateCharts(config.mainWindow.plainText)
    else:
        config.mainWindow.printMissingPackage("matplotlib")
else:
    config.mainWindow.printMissingPackage("numpy")