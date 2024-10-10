from uniquebible import config
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
if config.qtLibrary == "pyside6":
    #from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QPushButton
    from uniquebible.gui.PieChart import PieChart
    from uniquebible.gui.BarChart import BarChart
else:
    #from qtpy.QtWebEngineWidgets import QWebEngineView
    from qtpy.QtWidgets import QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout, QRadioButton, QPushButton


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

        # Formulate Charts Data
        if isSortedByChapter:
            chartTitle = "{0} x {1}".format(firstColumnTitle, len(verses))
        else:
            chartTitle = "{0} x {1}".format(config.thisTranslation["bibleReferences"], len(verses))

        # Display a Table
        # config.mainWindow.studyView.currentWidget().openPopover(html=getTableHtml("\n".join(data), str(len(verses)), firstColumnTitle))

        tableHtml = getTableHtml("\n".join(data), str(len(verses)), firstColumnTitle)

        if hasattr(config.mainWindow, "charts"):
            config.mainWindow.charts.close()
            config.mainWindow.charts = None
        config.mainWindow.charts = QWidget()
        mainLayout = QVBoxLayout()
        controlLayout = QHBoxLayout()
        mainLayout.addLayout(controlLayout)

        config.stackedCharts = QStackedWidget()
        htmlTable = WebEngineViewPopover(config.mainWindow, "main", "main", windowTitle=config.thisTranslation["table"])
        tableHtml = config.mainWindow.wrapHtml(tableHtml)
        htmlTable.setHtml(tableHtml, config.baseUrl)
        config.stackedCharts.addWidget(htmlTable)

        if config.qtLibrary == "pyside6":

            # Data for feeding QChart
            if isSortedByChapter:
                qtData = [(str(chapterNo), len(counts[chapterNo])) for chapterNo in sorted(counts)]
            else:
                qtData = [(parser.standardAbbreviation[str(bookNo)], len(counts[bookNo])) for bookNo in sorted(counts)]
            # QChart Bar Chart
            #config.mainWindow.barChart = BarChart(qtData, chartTitle)
            #config.mainWindow.barChart.show()
            # QChart Pie Chart
            #config.mainWindow.pieChart = PieChart(qtData, chartTitle)
            #config.mainWindow.pieChart.show()

            config.stackedCharts.addWidget(PieChart(qtData, chartTitle))
            config.stackedCharts.addWidget(BarChart(qtData, chartTitle))
            mainLayout.addWidget(config.stackedCharts)
        else:

            # Data for HTML charts
            if isSortedByChapter:
                data = ["  ['{0}', {1}]".format(str(chapterNo), len(counts[chapterNo])) for chapterNo in sorted(counts)]
            else:
                data = ["  ['{0}', {1}]".format(parser.standardAbbreviation[str(bookNo)], len(counts[bookNo])) for bookNo in sorted(counts)]
            # Display a HTML Bar Chart
            #html = getBarChartHtml(",\n".join(data), len(counts.keys()), chartTitle)
            #html = config.mainWindow.wrapHtml(html)
            #config.mainWindow.barChart = QWebEngineView()
            #config.mainWindow.barChart.setHtml(html, config.baseUrl)
            #config.mainWindow.barChart.setMinimumSize(900, 550)
            #config.mainWindow.barChart.show()
            # Display a HTML Pie Chart
            #html = getPieChartHtml(",\n".join(data), chartTitle)
            #html = config.mainWindow.wrapHtml(html)
            #config.mainWindow.pieChart = QWebEngineView()
            #config.mainWindow.pieChart.setHtml(html, config.baseUrl)
            #config.mainWindow.pieChart.setMinimumSize(700, 380)
            #config.mainWindow.pieChart.show()

            html = getPieChartHtml(",\n".join(data), chartTitle)
            html = config.mainWindow.wrapHtml(html)
            #htmlPieChart = QWebEngineView()
            htmlPieChart = WebEngineViewPopover(None, "main", "main", windowTitle=config.thisTranslation["pieChart"])
            htmlPieChart.setHtml(html, config.baseUrl)
            config.stackedCharts.addWidget(htmlPieChart)
            html = getBarChartHtml(",\n".join(data), len(counts.keys()), chartTitle)
            html = config.mainWindow.wrapHtml(html)
            #htmlBarChart = QWebEngineView()
            htmlBarChart = WebEngineViewPopover(None, "main", "main", windowTitle=config.thisTranslation["barChart"])
            htmlBarChart.setHtml(html, config.baseUrl)
            config.stackedCharts.addWidget(htmlBarChart)
            mainLayout.addWidget(config.stackedCharts)

#        refTable, pieChart, barChart = QRadioButton("Table"), QRadioButton("Pie Chart"), QRadioButton("Bar Chart")
#        refTable.setChecked(True)
#        refTable.toggled.connect(lambda: config.stackedCharts.setCurrentIndex(0))
#        pieChart.toggled.connect(lambda: config.stackedCharts.setCurrentIndex(1))
#        barChart.toggled.connect(lambda: config.stackedCharts.setCurrentIndex(2))
#        for radioButton in (refTable, pieChart, barChart):
#            controlLayout.addWidget(radioButton)

        refTable, pieChart, barChart = QPushButton(config.thisTranslation["table"]), QPushButton(config.thisTranslation["pieChart"]), QPushButton(config.thisTranslation["barChart"])
        refTable.clicked.connect(lambda: config.stackedCharts.setCurrentIndex(0))
        refTable.clicked.connect(lambda: updateButtons(refTable, pieChart, barChart))
        pieChart.clicked.connect(lambda: config.stackedCharts.setCurrentIndex(1))
        pieChart.clicked.connect(lambda: updateButtons(pieChart, refTable, barChart))
        barChart.clicked.connect(lambda: config.stackedCharts.setCurrentIndex(2))
        barChart.clicked.connect(lambda: updateButtons(barChart, refTable, pieChart))
        for pushButton in (refTable, pieChart, barChart):
            pushButton.setCheckable(True)
            controlLayout.addWidget(pushButton)
        refTable.setChecked(True)
        refTable.setDisabled(True)

        config.mainWindow.charts.setLayout(mainLayout)
        config.mainWindow.charts.show()
        config.mainWindow.charts.showMaximized()

    else:
        config.mainWindow.displayMessage(config.thisTranslation["message_noReference"])

def updateButtons(button1, button2, button3):
    button1.setDisabled(True)
    button2.setDisabled(False)
    button2.setChecked(False)
    button3.setDisabled(False)
    button3.setChecked(False)

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

if config.pluginContext:
    generateCharts(config.pluginContext)
else:
    config.contextSource.page().toPlainText(generateCharts)