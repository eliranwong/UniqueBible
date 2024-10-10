from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QWidget, QVBoxLayout, QMenu
    from PySide6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis
    from PySide6.QtGui import QPainter
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QAction


# https://doc.qt.io/qtforpython/overviews/qtcharts-barchart-example.html#barchart-example
class BarChart(QWidget):
    def __init__(self, data=[], chartTitle=""):
        super().__init__()
        self.data = data
        self.chartTitle = chartTitle

        self.setWindowTitle(config.thisTranslation["barChart"])
        #self.setGeometry(100,100, 680,500)

        layout = QVBoxLayout()
        layout.addWidget(self.create_bar())
        self.setLayout(layout)

    def contextMenuEvent(self, event):     
        menu = QMenu(self)
        addToWorkSpace = menu.addAction(config.thisTranslation["addToWorkSpace"])
        selectedAction = menu.exec_(self.mapToGlobal(event.pos()))
        if selectedAction == addToWorkSpace:
            config.mainWindow.ws.addWidgetAsSubWindow(self.create_bar(), config.thisTranslation["barChart"])

    def create_bar(self):
        series = QBarSeries()
        countSet = QBarSet(config.thisTranslation["count"])
        categories = []
        for book, count in self.data:
            countSet.append(count)
            categories.append(book)
        series.append(countSet)


        chart = QChart()
        chart.addSeries(series)
        chart.setTitle(self.chartTitle)
        chart.setAnimationOptions(QChart.SeriesAnimations)

        axis = QBarCategoryAxis()
        axis.append(categories)
        chart.createDefaultAxes()
        chart.setAxisX(axis, series)

        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)

        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)

        return chartView
