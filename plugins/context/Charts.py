import config
from BibleVerseParser import BibleVerseParser
from qtpy.QtWebEngineWidgets import QWebEngineView


def generateCharts(text):
    # Extract bible verse references
    useFastVerseParsing = config.useFastVerseParsing
    config.useFastVerseParsing = False
    parser = BibleVerseParser(config.parserStandarisation)
    verses = parser.extractAllReferences(text, False)
    config.useFastVerseParsing = useFastVerseParsing
    if verses:
        counts = countVersesByBook(verses)
        data = ["  ['{0}', {1}]".format(parser.standardAbbreviation[str(bookNo)], counts[bookNo]) for bookNo in sorted(counts)]
        # Bar Chart
        html = getBarChartHtml(",\n".join(data), str(len(verses)))
        html = config.mainWindow.wrapHtml(html)
        config.mainWindow.barChart = QWebEngineView()
        config.mainWindow.barChart.setHtml(html, config.baseUrl)
        config.mainWindow.barChart.setMinimumSize(900, 550)
        config.mainWindow.barChart.show()
        # Pie Chart
        html = getPieChartHtml(",\n".join(data), str(len(verses)))
        html = config.mainWindow.wrapHtml(html)
        config.mainWindow.pieChart = QWebEngineView()
        config.mainWindow.pieChart.setHtml(html, config.baseUrl)
        config.mainWindow.pieChart.setMinimumSize(700, 380)
        config.mainWindow.pieChart.show()
    else:
        config.mainWindow.displayMessage(config.thisTranslation["message_noReference"])

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

def getBarChartHtml(data, totalVerseCount):
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
  var options = {'title':'"""+totalVerseCount+""" Bible Reference(s)', 'width':900, 'height':700};

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
        bookCount = counts.get(b, 0)
        counts[b] = bookCount + 1
    return counts

if config.pluginContext:
    generateCharts(config.pluginContext)
else:
    config.contextSource.page().toPlainText(generateCharts)