import config, os
from util.BibleVerseParser import BibleVerseParser
from util.TextUtil import TextUtil
from util.WebtopUtil import WebtopUtil

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

        # Display a Table
        # config.mainWindow.studyView.currentWidget().openPopover(html=getTableHtml("\n".join(data), str(len(verses)), firstColumnTitle))

        # table html
        table_html = getTableHtml("\n".join(data), str(len(verses)), firstColumnTitle)
        table_html = config.mainWindow.wrapHtml(table_html)
        config.mainWindow.html = table_html
        config.mainWindow.plainText = TextUtil.htmlToPlainText(table_html)
        displayHtml(table_html)

        # Data for HTML charts
#        if isSortedByChapter:
#            chartTitle = "{0} x {1}".format(firstColumnTitle, len(verses))
#            data = ["  ['{0}', {1}]".format(str(chapterNo), len(counts[chapterNo])) for chapterNo in sorted(counts)]
#        else:
#            chartTitle = "{0} x {1}".format(config.thisTranslation["bibleReferences"], len(verses))
#            data = ["  ['{0}', {1}]".format(parser.standardAbbreviation[str(bookNo)], len(counts[bookNo])) for bookNo in sorted(counts)]

        # pie chart html
        #pie_chart_html = getPieChartHtml(",\n".join(data), chartTitle)
        #pie_chart_html = config.mainWindow.wrapHtml(pie_chart_html)
        #openHtml(pie_chart_html)

        # bar chart html
        #bar_chart_html = getBarChartHtml(",\n".join(data), len(counts.keys()), chartTitle)
        #bar_chart_html = config.mainWindow.wrapHtml(bar_chart_html)
        #openHtml(bar_chart_html)

    else:
        config.mainWindow.displayMessage(config.thisTranslation["message_noReference"])

def displayHtml(html):
    if WebtopUtil.isPackageInstalled("w3m"):
        config.mainWindow.cliTool("w3m -T text/html", config.mainWindow.html)
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
<table style="width:100%">
  <tr><th>{0}</th><th>{1}</th><th>{2}&nbsp;</th></tr>
""".format(firstColumnTitle if firstColumnTitle else config.thisTranslation["menu_book"], config.thisTranslation["bibleReferences"], config.thisTranslation["count"])+data+"""
</table>
"""

def getPieChartHtml(data, chartTitle=""):
    return """
<h2>UniqueBible.app</h2>

<div id="piechart"></div>

<script type="text/javascript" src="js/charts.js"></script>

<script type="text/javascript">
// Load google charts
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

// Draw the chart and set the chart values
function drawChart() {
  var data = google.visualization.arrayToDataTable([
  ['Book', 'Number of Verse(s)'],
"""+data+"""
]);

  // Optional; add a title and set the width and height of the chart
  var options = {'title':'"""+chartTitle+"""', 'width':700, 'height':500};

  // Display the chart inside the <div> element with id="piechart"
  var chart = new google.visualization.PieChart(document.getElementById('piechart'));
  chart.draw(data, options);
}
</script>
"""

def getBarChartHtml(data, noOfBooks, chartTitle=""):
    return """
<h2>UniqueBible.app</h2>

<div id="barchart"></div>

<script type="text/javascript" src="js/charts.js"></script>

<script type="text/javascript">
// Load google charts
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawChart);

// Draw the chart and set the chart values
function drawChart() {
  var data = google.visualization.arrayToDataTable([
  ['Book', 'Number of Verse(s)'],
"""+data+"""
]);

  // Optional; add a title and set the width and height of the chart
  var options = {'title':'"""+chartTitle+"""', 'width':900, 'height':"""+str(noOfBooks * 50 if noOfBooks > 10 else 500)+"""};

  // Display the chart inside the <div> element with id="barchart"
  var chart = new google.visualization.BarChart(document.getElementById('barchart'));
  chart.draw(data, options);
}
</script>
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
