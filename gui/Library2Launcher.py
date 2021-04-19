import config
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import (QPushButton, QListView, QAbstractItemView, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget)

class Library2Launcher(QWidget):

    def __init__(self, parent):
        super().__init__()
        # set title
        self.setWindowTitle("PDF")
        # set up variables
        self.parent = parent
        self.pdfList = self.parent.pdfList
        # setup interface
        self.setupUI()

    def setupUI(self):
        mainLayout = QHBoxLayout()

        leftColumnWidget = QGroupBox(config.thisTranslation["pdfDocument"])
        pdfLayout = QVBoxLayout()
        pdfLayout.addWidget(self.pdfListView())
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(self.openPreviousPdf)
        pdfLayout.addWidget(button)
        leftColumnWidget.setLayout(pdfLayout)

        mainLayout.addWidget(leftColumnWidget)
        self.setLayout(mainLayout)

    def pdfListView(self):
        list = QListView()
        list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        model = QStandardItemModel(list)
        for index, pdf in enumerate(self.pdfList):
            item = QStandardItem(pdf)
            model.appendRow(item)
        list.setModel(model)
        list.selectionModel().selectionChanged.connect(self.pdfSelected)
        return list

    def pdfSelected(self, selection):
        index = selection[0].indexes()[0].row()
        config.pdfText = self.pdfList[index]
        command = "PDF:::{0}".format(config.pdfText)
        self.parent.runTextCommand(command)

    def openPreviousPdf(self):
        command = "PDF:::{0}".format(config.pdfText)
        self.parent.runTextCommand(command)

