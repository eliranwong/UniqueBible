import config
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QWidget, QVBoxLayout
    from PySide6.QtCharts import QChart, QChartView, QBarSet, QBarSeries, QBarCategoryAxis
    from PySide6.QtGui import QPainter
    from PySide6.QtCore import Qt


# https://doc.qt.io/qtforpython/overviews/qtcharts-barchart-example.html#barchart-example
class BarChart(QWidget):
    def __init__(self, data=[], chartTitle=""):
        super().__init__()
        self.data = data
        self.chartTitle = chartTitle

        self.setWindowTitle("Unique Bible App")
        #self.setGeometry(100,100, 680,500)
        self.create_bar()

        layout = QVBoxLayout()
        layout.addWidget(self.create_bar())
        self.setLayout(layout)


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
