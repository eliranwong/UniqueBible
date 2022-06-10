import config
from util.BibleVerseParser import BibleVerseParser
if config.qtLibrary == "pyside6":
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from gui.PieChart import PieChart
    from gui.BarChart import BarChart
else:
    from qtpy.QtWebEngineWidgets import QWebEngineView


def generateCharts(text):
    # Extract bible verse references
    useLiteVerseParsing = config.useLiteVerseParsing
    config.useLiteVerseParsing = False
    parser = BibleVerseParser(config.parserStandarisation)
    verses = parser.extractAllReferences(text, False)
    config.useLiteVerseParsing = useLiteVerseParsing
    if verses:
        # Sort by Books
        counts = countVersesByBook(verses)
        # Formulate Table Data
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
        # Display a Table
        config.mainWindow.studyView.currentWidget().openPopover(html=getTableHtml("\n".join(data), str(len(verses))))
        # Formulate Charts Data
        if config.qtLibrary == "pyside6":
            # Chart Title
            chartTitle = "{0} x {1}".format(config.thisTranslation["bibleReferences"], len(verses))
            # Data for feeding QChart
            qtData = [(parser.standardAbbreviation[str(bookNo)], len(counts[bookNo])) for bookNo in sorted(counts)]
            # QChart Bar Chart
            config.mainWindow.barChart = BarChart(qtData, chartTitle)
            config.mainWindow.barChart.show()
            # QChart Pie Chart
            config.mainWindow.pieChart = PieChart(qtData, chartTitle)
            config.mainWindow.pieChart.show()
        else:
            # Data for HTML charts
            data = ["  ['{0}', {1}]".format(parser.standardAbbreviation[str(bookNo)], len(counts[bookNo])) for bookNo in sorted(counts)]
            # Display a HTML Bar Chart
            html = getBarChartHtml(",\n".join(data), str(len(verses)), len(counts.keys()))
            html = config.mainWindow.wrapHtml(html)
            config.mainWindow.barChart = QWebEngineView()
            config.mainWindow.barChart.setHtml(html, config.baseUrl)
            config.mainWindow.barChart.setMinimumSize(900, 550)
            config.mainWindow.barChart.show()
            # Display a HTML Pie Chart
            html = getPieChartHtml(",\n".join(data), str(len(verses)))
            html = config.mainWindow.wrapHtml(html)
            config.mainWindow.pieChart = QWebEngineView()
            config.mainWindow.pieChart.setHtml(html, config.baseUrl)
            config.mainWindow.pieChart.setMinimumSize(700, 380)
            config.mainWindow.pieChart.show()
    else:
        config.mainWindow.displayMessage(config.thisTranslation["message_noReference"])

def getTableHtml(data, totalVerseCount):
    return """
<h2>Unique Bible App</h2>
<h3>{0} x """.format(config.thisTranslation["bibleReferences"])+totalVerseCount+"""</h3>
<table style="width:100%">
  <tr><th>Book</th><th>Reference</th><th>Count&nbsp;</th></tr>
"""+data+"""
</table>
"""

def getPieChartHtml(data, totalVerseCount):
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
  var options = {'title':'"""+totalVerseCount+""" Bible Reference(s)', 'width':700, 'height':500};

  // Display the chart inside the <div> element with id="piechart"
  var chart = new google.visualization.PieChart(document.getElementById('piechart'));
  chart.draw(data, options);
}
</script>
"""

def getBarChartHtml(data, totalVerseCount, noOfBooks):
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
  var options = {'title':'"""+totalVerseCount+""" Bible Reference(s)', 'width':900, 'height':"""+str(noOfBooks * 50 if noOfBooks > 10 else 500)+"""};

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

if config.pluginContext:
    generateCharts(config.pluginContext)
else:
    config.contextSource.page().toPlainText(generateCharts)