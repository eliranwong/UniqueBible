from uniquebible import config
import os
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QWidget, QLabel, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QStandardItemModel, QStandardItem
else:
    from qtpy.QtWidgets import QWidget, QLabel, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout
    from qtpy.QtCore import Qt
    from qtpy.QtGui import QStandardItemModel, QStandardItem
from uniquebible.util.FileUtil import FileUtil

class EnableIndividualPlugins(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set variables
        self.setupVariables()
        # set title
        self.setWindowTitle(self.translation[0])
        self.setMinimumSize(830, 500)
        # setup interface
        self.setupUI()

    def setupVariables(self):
        self.translation = (
            config.thisTranslation["enableIndividualPlugins"],
            config.thisTranslation["startup"],
            config.thisTranslation["menu"],
            config.thisTranslation["context"],
            config.thisTranslation["shutdown"],
        )
        self.changed = False

    def closeEvent(self, event):
        if self.changed:
            if config.menuLayout == "material":
                self.parent.setupMenuLayout("material")
            self.parent.displayMessage(config.thisTranslation["message_restart"])

    def setupUI(self):
        mainLayout = QVBoxLayout()

        mainLayout.addWidget(QLabel(self.translation[0]))

        subLayout = QHBoxLayout()

        layout = QVBoxLayout()
        layout.addWidget(QLabel(self.translation[1]))
        dataView1 = QListView()
        dataView1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        dataViewModel1 = QStandardItemModel(dataView1)
        dataView1.setModel(dataViewModel1)
        for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "startup"), "py"):
            item = QStandardItem(plugin)
            item.setToolTip(plugin)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked if plugin in config.excludeStartupPlugins else Qt.CheckState.Checked)
            dataViewModel1.appendRow(item)
        dataViewModel1.itemChanged.connect(self.itemChanged1)
        layout.addWidget(dataView1)
        subLayout.addLayout(layout)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(self.translation[2]))
        dataView2 = QListView()
        dataView2.setEditTriggers(QAbstractItemView.NoEditTriggers)
        dataViewModel2 = QStandardItemModel(dataView2)
        dataView2.setModel(dataViewModel2)
        for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "menu"), "py"):
            item = QStandardItem(plugin)
            item.setToolTip(plugin)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked if plugin in config.excludeMenuPlugins else Qt.CheckState.Checked)
            dataViewModel2.appendRow(item)
        dataViewModel2.itemChanged.connect(self.itemChanged2)
        layout.addWidget(dataView2)
        subLayout.addLayout(layout)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(self.translation[3]))
        dataView3 = QListView()
        dataView3.setEditTriggers(QAbstractItemView.NoEditTriggers)
        dataViewModel3 = QStandardItemModel(dataView3)
        dataView3.setModel(dataViewModel3)
        for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "context"), "py"):
            item = QStandardItem(plugin)
            item.setToolTip(plugin)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked if plugin in config.excludeContextPlugins else Qt.CheckState.Checked)
            dataViewModel3.appendRow(item)
        dataViewModel3.itemChanged.connect(self.itemChanged3)
        layout.addWidget(dataView3)
        subLayout.addLayout(layout)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(self.translation[4]))
        dataView4 = QListView()
        dataView4.setEditTriggers(QAbstractItemView.NoEditTriggers)
        dataViewModel4 = QStandardItemModel(dataView4)
        dataView4.setModel(dataViewModel4)
        for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "shutdown"), "py"):
            item = QStandardItem(plugin)
            item.setToolTip(plugin)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked if plugin in config.excludeShutdownPlugins else Qt.CheckState.Checked)
            dataViewModel4.appendRow(item)
        dataViewModel4.itemChanged.connect(self.itemChanged4)
        layout.addWidget(dataView4)
        subLayout.addLayout(layout)

        mainLayout.addLayout(subLayout)

        self.setLayout(mainLayout)

    def itemChanged1(self, standardItem):
        plugin = standardItem.text()
        if standardItem.checkState() is Qt.CheckState.Checked and plugin in config.excludeStartupPlugins:
            config.excludeStartupPlugins.remove(plugin)
            self.changed = True
        elif standardItem.checkState() is Qt.CheckState.Unchecked and not plugin in config.excludeStartupPlugins:
            config.excludeStartupPlugins.append(plugin)
            self.changed = True

    def itemChanged2(self, standardItem):
        plugin = standardItem.text()
        if standardItem.checkState() is Qt.CheckState.Checked and plugin in config.excludeMenuPlugins:
            config.excludeMenuPlugins.remove(plugin)
            self.changed = True
        elif standardItem.checkState() is Qt.CheckState.Unchecked and not plugin in config.excludeMenuPlugins:
            config.excludeMenuPlugins.append(plugin)
            self.changed = True

    def itemChanged3(self, standardItem):
        plugin = standardItem.text()
        if standardItem.checkState() is Qt.CheckState.Checked and plugin in config.excludeContextPlugins:
            config.excludeContextPlugins.remove(plugin)
            self.changed = True
        elif standardItem.checkState() is Qt.CheckState.Unchecked and not plugin in config.excludeContextPlugins:
            config.excludeContextPlugins.append(plugin)
            self.changed = True

    def itemChanged4(self, standardItem):
        plugin = standardItem.text()
        if standardItem.checkState() is Qt.CheckState.Checked and plugin in config.excludeShutdownPlugins:
            config.excludeShutdownPlugins.remove(plugin)
            self.changed = True
        elif standardItem.checkState() is Qt.CheckState.Unchecked and not plugin in config.excludeShutdownPlugins:
            config.excludeShutdownPlugins.append(plugin)
            self.changed = True

