from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu
    from PySide6.QtCharts import QChart, QChartView, QPieSeries
    from PySide6.QtGui import QPainter, QPen
    from PySide6.QtCore import Qt
from uniquebible.util.BibleVerseParser import BibleVerseParser


class PieChart(QWidget):

    def __init__(self, data=[], chartTitle="", showFigure=True):
        super().__init__()
        self.data = data
        self.chartTitle, self.showFigure = chartTitle, showFigure

        self.setWindowTitle(config.thisTranslation["pieChart"])
        #self.setGeometry(100,100, 1280,600)

        layout = QVBoxLayout()
        layout.addWidget(self.create_piechart())
        self.setLayout(layout)

    def contextMenuEvent(self, event):     
        menu = QMenu(self)
        addToWorkSpace = menu.addAction(config.thisTranslation["addToWorkSpace"])
        selectedAction = menu.exec_(self.mapToGlobal(event.pos()))
        if selectedAction == addToWorkSpace:
            config.mainWindow.ws.addWidgetAsSubWindow(self.create_piechart(), config.thisTranslation["pieChart"])

    def create_piechart(self):

        series = QPieSeries()
        for book, count in self.data:
            series.append("{0} x {1}".format(book, count) if self.showFigure else book, count)
        for slice in series.slices():
            slice.setLabelVisible(True)

        # Highlight the currently opened book
        bookNameList = [book for book, *_ in self.data]
        bookNumberList = BibleVerseParser(config.parserStandarisation).extractBookList(",".join(bookNameList))
        try:
            highlightBookIndex = bookNumberList.index(config.mainB)
        except:
            highlightBookIndex = None
        if highlightBookIndex is not None:
            slice = series.slices()[highlightBookIndex]
            slice.setExploded(True)
            slice.setPen(QPen(Qt.darkGreen, highlightBookIndex))
            slice.setBrush(Qt.green)

        chart = QChart()
        chart.legend().hide()
        chart.addSeries(series)
        chart.createDefaultAxes()
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.setTitle(self.chartTitle)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chartview = QChartView(chart)
        chartview.setRenderHint(QPainter.Antialiasing)

        return chartview
