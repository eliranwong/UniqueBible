import config
import os.path
from PySide2.QtCore import QStringListModel
#from PySide2.QtGui import QStandardItemModel, QStandardItem
from PySide2.QtWidgets import (QPushButton, QListView, QAbstractItemView, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget)

class HistoryLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        # set title
        self.setWindowTitle(config.thisTranslation["menu_history"])
        # set up variables
        self.parent = parent
        self.startup = True
        # setup interface
        self.setupUI()

    def setupUI(self):
        mainLayout = QHBoxLayout()

        leftColumnWidget = QGroupBox(config.thisTranslation["mainWindow"])
        layout = QVBoxLayout()
        layout.addWidget(self.createMainListView())
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(lambda: self.openLastRecord("main"))
        layout.addWidget(button)
        leftColumnWidget.setLayout(layout)

        middleColumnWidget = QGroupBox(config.thisTranslation["studyWindow"])
        layout = QVBoxLayout()
        layout.addWidget(self.createStudyListView())
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(lambda: self.openLastRecord("study"))
        layout.addWidget(button)
        middleColumnWidget.setLayout(layout)

        rightColumnWidget = QGroupBox(config.thisTranslation["menu_external_notes"])
        layout = QVBoxLayout()
        layout.addWidget(self.createExternalListView())
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(lambda: self.openLastRecord("external"))
        layout.addWidget(button)
        rightColumnWidget.setLayout(layout)

        mainLayout.addWidget(leftColumnWidget)
        mainLayout.addWidget(middleColumnWidget)
        mainLayout.addWidget(rightColumnWidget)
        self.setLayout(mainLayout)

    def createMainListView(self):
        mainItems = list(reversed(config.history["main"]))
        # Main and study history records are editable, so users can slightly modify a command and execute a new one.
        self.mainListView = QListView()
        self.mainModel = QStringListModel(mainItems)
        self.mainListView.setModel(self.mainModel)
        self.mainListView.selectionModel().selectionChanged.connect(lambda selection: self.historyAction(selection, "main"))
        if mainItems:
            self.mainListView.setCurrentIndex(self.mainModel.index(0, 0))
        return self.mainListView

    def createStudyListView(self):
        studyItems = list(reversed(config.history["study"]))
        # Main and study history records are editable, so users can slightly modify a command and execute a new one.
        self.studyListView = QListView()
        self.studyModel = QStringListModel(studyItems)
        self.studyListView.setModel(self.studyModel)
        self.studyListView.selectionModel().selectionChanged.connect(lambda selection: self.historyAction(selection, "study"))
        if studyItems:
            self.studyListView.setCurrentIndex(self.studyModel.index(0, 0))
        return self.studyListView

    def createExternalListView(self):
        externalItems = self.filterExternalFileRecords()
        self.externalListView = QListView()
        # Only external file history record is not editable
        self.externalListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.externalModel = QStringListModel(externalItems)
        self.externalListView.setModel(self.externalModel)
        self.externalListView.selectionModel().selectionChanged.connect(lambda selection: self.historyAction(selection, "external"))
        if externalItems:
            self.externalListView.setCurrentIndex(self.externalModel.index(0, 0))
        return self.externalListView

    def filterExternalFileRecords(self):
        # Hide those which do not exist on the current platform
        # This may be useful when users use the same config.py across different platforms
        files = list(reversed(config.history["external"]))
        return [file for file in files if os.path.isfile(file)]

    def refreshHistoryRecords(self):
        if not self.startup:
            mainItems = list(reversed(config.history["main"]))
            studyItems = list(reversed(config.history["study"]))
            externalItems = self.filterExternalFileRecords()
            self.mainModel.setStringList(mainItems)
            self.studyModel.setStringList(studyItems)
            self.externalModel.setStringList(externalItems)
            self.setSelection(mainItems, studyItems, externalItems)
        else:
            self.startup = False

    def setSelection(self, mainItems, studyItems, externalItems):
        print("setselection")
        if mainItems:
            self.mainListView.setCurrentIndex(self.mainModel.index(0, 0))
        if studyItems:
            self.studyListView.setCurrentIndex(self.studyModel.index(0, 0))
        if externalItems:
            self.externalListView.setCurrentIndex(self.externalModel.index(0, 0))

    def openLastRecord(self, key):
        selectedItem = config.history[key][-1]
        self.openSelectedItem(selectedItem, key)

    def historyAction(self, selection, key):
        selectedItem = selection[0].indexes()[0].data()
        self.openSelectedItem(selectedItem, key)

    def openSelectedItem(self, selectedItem, key):
        if key == "external":
            command = "OPENNOTE:::{0}".format(selectedItem)
            self.parent.runTextCommand(command)
        else:
            self.parent.runTextCommand(selectedItem)
