import glob
from pathlib import Path

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
        self.docxList = self.parent.docxList
        self.devotionals = [Path(filename).stem for filename in glob.glob(config.marvelData + "/devotionals/*.devotional")]
        self.selectedDevotional = self.devotionals[0] if len(self.devotionals) > 0 else None

        # setup interface
        self.setupUI()

    def setupUI(self):
        mainLayout = QHBoxLayout()

        leftColumnWidget = QGroupBox(config.thisTranslation["pdfDocument"])
        pdfLayout = QVBoxLayout()
        pdfLayout.addWidget(self.pdfListView())
        buttons = QHBoxLayout()
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(self.openPreviousPdf)
        buttons.addWidget(button)
        button = QPushButton(config.thisTranslation["import"])
        button.clicked.connect(self.parent.parent.importPdfDialog)
        buttons.addWidget(button)
        button = QPushButton(config.thisTranslation["others"])
        button.clicked.connect(self.parent.parent.openPdfDialog)
        buttons.addWidget(button)
        pdfLayout.addLayout(buttons)
        leftColumnWidget.setLayout(pdfLayout)

        centerColumnWidget = QGroupBox(config.thisTranslation["wordDocument"])
        pdfLayout = QVBoxLayout()
        pdfLayout.addWidget(self.docxListView())
        buttons = QHBoxLayout()
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(self.openPreviousDocx)
        buttons.addWidget(button)
        button = QPushButton(config.thisTranslation["import"])
        button.clicked.connect(self.parent.parent.importDocxDialog)
        buttons.addWidget(button)
        button = QPushButton(config.thisTranslation["others"])
        button.clicked.connect(self.parent.parent.openDocxDialog)
        buttons.addWidget(button)
        pdfLayout.addLayout(buttons)
        centerColumnWidget.setLayout(pdfLayout)

        rightColumnWidget = QGroupBox(config.thisTranslation["devotionals"])
        devotionalLayout = QVBoxLayout()
        devotionalLayout.addWidget(self.devotionsListView())
        buttons = QHBoxLayout()
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(self.openDevotional)
        buttons.addWidget(button)
        buttons.addWidget(button)
        devotionalLayout.addLayout(buttons)
        rightColumnWidget.setLayout(devotionalLayout)

        mainLayout.addWidget(leftColumnWidget)
        mainLayout.addWidget(centerColumnWidget)
        mainLayout.addWidget(rightColumnWidget)
        self.setLayout(mainLayout)

    def pdfListView(self):
        list = QListView()
        list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        model = QStandardItemModel(list)
        for pdf in self.pdfList:
            item = QStandardItem(pdf)
            model.appendRow(item)
        list.setModel(model)
        if config.pdfText in self.parent.pdfList:
            list.setCurrentIndex(model.index(self.parent.pdfList.index(config.pdfText), 0))
        list.selectionModel().selectionChanged.connect(self.pdfSelected)
        return list

    def pdfSelected(self, selection):
        index = selection[0].indexes()[0].row()
        config.pdfText = self.pdfList[index]
        command = "PDF:::{0}".format(config.pdfText)
        self.parent.runTextCommand(command)

    def openPreviousPdf(self):
        if config.pdfText in self.parent.pdfList:
            command = "PDF:::{0}".format(config.pdfText)
            self.parent.runTextCommand(command)

    def docxListView(self):
        list = QListView()
        list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        model = QStandardItemModel(list)
        for docx in self.docxList:
            item = QStandardItem(docx)
            model.appendRow(item)
        list.setModel(model)
        if config.docxText in self.parent.docxList:
            list.setCurrentIndex(model.index(self.parent.docxList.index(config.docxText), 0))
        list.selectionModel().selectionChanged.connect(self.docxSelected)
        return list

    def devotionsListView(self):
        list = QListView()
        list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        model = QStandardItemModel(list)
        for devotional in self.devotionals:
            item = QStandardItem(devotional)
            model.appendRow(item)
        list.setModel(model)
        list.selectionModel().selectionChanged.connect(self.devotionalSelected)
        return list

    def docxSelected(self, selection):
        index = selection[0].indexes()[0].row()
        config.docxText = self.docxList[index]
        command = "DOCX:::{0}".format(config.docxText)
        self.parent.runTextCommand(command)

    def openPreviousDocx(self):
        if config.docxText in self.parent.docxList:
            command = "DOCX:::{0}".format(config.docxText)
            self.parent.runTextCommand(command)

    def devotionalSelected(self, selection):
        index = selection[0].indexes()[0].row()
        self.selectedDevotional = self.devotionals[index]

    def openDevotional(self):
        if self.selectedDevotional is not None:
            command = "DEVOTIONAL:::{0}".format(self.selectedDevotional)
            self.parent.runTextCommand(command)
