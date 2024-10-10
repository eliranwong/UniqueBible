from uniquebible import config
import os.path
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QPushButton, QListView, QAbstractItemView, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget
    from PySide6.QtGui import QStandardItemModel, QStandardItem
else:
    from qtpy.QtWidgets import QPushButton, QListView, QAbstractItemView, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget
    from qtpy.QtGui import QStandardItemModel, QStandardItem


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
        subLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["open"])
        button.clicked.connect(lambda: self.externalFileAction(False))
        subLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["edit"])
        button.clicked.connect(lambda: self.externalFileAction(True))
        subLayout.addWidget(button)
        layout.addLayout(subLayout)
        rightColumnWidget.setLayout(layout)

        mainLayout.addWidget(leftColumnWidget)
        mainLayout.addWidget(middleColumnWidget)
        mainLayout.addWidget(rightColumnWidget)
        self.setLayout(mainLayout)

    def createMainListView(self):
        # Main and study history records are editable, so users can slightly modify a command and execute a new one.
        self.mainListView = QListView()
        #self.mainModel = QStringListModel()
        self.mainModel = QStandardItemModel(self.mainListView)
        self.mainListView.setModel(self.mainModel)
        self.mainListView.selectionModel().selectionChanged.connect(lambda selection: self.historyAction(selection, "main"))
        return self.mainListView

    def createStudyListView(self):
        #studyItems = list(reversed(config.history["study"]))
        # Main and study history records are editable, so users can slightly modify a command and execute a new one.
        self.studyListView = QListView()
        #self.studyModel = QStringListModel()
        self.studyModel = QStandardItemModel(self.studyListView)
        self.studyListView.setModel(self.studyModel)
        self.studyListView.selectionModel().selectionChanged.connect(lambda selection: self.historyAction(selection, "study"))
        return self.studyListView

    def createExternalListView(self):
        self.externalListView = QListView()
        # Only external file history record is not editable
        self.externalListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        #self.externalModel = QStringListModel()
        self.externalModel = QStandardItemModel(self.externalListView)
        self.externalListView.setModel(self.externalModel)
        self.externalListView.selectionModel().selectionChanged.connect(lambda selection: self.historyAction(selection, "external"))
        return self.externalListView

    def filterExternalFileRecords(self):
        # Hide those which do not exist on the current platform
        # This may be useful when users use the same config.py across different platforms
        files = list(reversed(config.history["external"]))
        return [file for file in files if os.path.isfile(file)]

    def refresh(self):
        self.mainModel.clear()
        mainItems = list(reversed(config.history["main"]))
        for mainItem in mainItems:
            item = QStandardItem(mainItem)
            item.setToolTip(mainItem)
            self.mainModel.appendRow(item)
        self.studyModel.clear()
        studyItems = list(reversed(config.history["study"]))
        for studyItem in studyItems:
            item = QStandardItem(studyItem)
            item.setToolTip(studyItem)
            self.studyModel.appendRow(item)
        self.externalModel.clear()
        externalItems = self.filterExternalFileRecords()
        for externalItem in externalItems:
            item = QStandardItem(externalItem)
            item.setToolTip(externalItem)
            self.externalModel.appendRow(item)
        #self.mainModel.setStringList(mainItems)
        #self.studyModel.setStringList(studyItems)
        #self.externalModel.setStringList(externalItems)
        self.setSelection(mainItems, studyItems, externalItems)

    def setSelection(self, mainItems, studyItems, externalItems):
        if mainItems:
            self.mainListView.setCurrentIndex(self.mainModel.index(0, 0))
        if studyItems:
            self.studyListView.setCurrentIndex(self.studyModel.index(0, 0))
        if externalItems:
            self.externalListView.setCurrentIndex(self.externalModel.index(0, 0))

    def openLastRecord(self, key):
        selectedItem = config.history[key][-1]
        self.openSelectedItem(selectedItem, key)

    def externalFileAction(self, edit):
        command = "{0}:::-1".format("_editfile" if edit else "_openfile")
        self.parent.runTextCommand(command)

    def historyAction(self, selection, key):
        if not self.parent.isRefreshing:
            selectedItem = selection[0].indexes()[0].data()
            self.openSelectedItem(selectedItem, key)

    def openSelectedItem(self, selectedItem, key):
        if key == "external":
            command = "OPENNOTE:::{0}".format(selectedItem)
            self.parent.runTextCommand(command)
        else:
            self.parent.runTextCommand(selectedItem)
