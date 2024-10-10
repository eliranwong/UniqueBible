import os
from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QStandardItem, QStandardItemModel
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListView, QFileDialog, QAbstractItemView
else:
    from qtpy.QtGui import QStandardItem, QStandardItemModel
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListView, QFileDialog, QAbstractItemView

class PlaylistUI(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.justLaunched = True
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["media"])

        # Create the model and the view
        self.view = QListView()
        self.view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.model = QStandardItemModel(self.view)
        self.view.setModel(self.model)
        self.populateModel()
        self.view.selectionModel().selectionChanged.connect(self.selectionChanged)

        # Create the user interface widgets
        self.play_button = QPushButton(config.thisTranslation["play"]) #play
        self.pause_button = QPushButton(config.thisTranslation["pause"])#pause
        self.stop_button = QPushButton(config.thisTranslation["stop"]) #stop
        self.add_button = QPushButton(config.thisTranslation["add"]) #add
        self.remove_button = QPushButton(config.thisTranslation["remove"])#remove
        self.clear_all_button = QPushButton(config.thisTranslation["clearAll"]) #clearAll
        self.move_up_button = QPushButton(config.thisTranslation["moveUp"]) #moveUp
        self.move_down_button = QPushButton(config.thisTranslation["moveDown"]) #moveDown

        # Create the layout
        hbox0 = QHBoxLayout()
        hbox0.addWidget(self.play_button)
        hbox0.addWidget(self.pause_button)
        hbox0.addWidget(self.stop_button)
        
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.move_up_button)
        hbox1.addWidget(self.move_down_button)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.add_button)
        hbox2.addWidget(self.remove_button)
        hbox2.addWidget(self.clear_all_button)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox0)
        vbox.addWidget(self.view)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        # Set the layout
        self.setLayout(vbox)

        # Connect the signals and slots
        self.play_button.clicked.connect(self.parent.playAudioPlaying)
        self.pause_button.clicked.connect(self.parent.pauseAudioPlaying)
        self.stop_button.clicked.connect(self.parent.stopAudioPlaying)
        self.add_button.clicked.connect(self.add_item)
        self.remove_button.clicked.connect(self.remove_item)
        self.clear_all_button.clicked.connect(self.clear_all)
        self.move_up_button.clicked.connect(self.move_up)
        self.move_down_button.clicked.connect(self.move_down)

    def populateModel(self):
        # Add items to the model
        for filePath in self.parent.audioPlayList:
            item = QStandardItem(os.path.basename(filePath))
            item.setToolTip(filePath)
            self.model.appendRow(item)

    def selectionChanged(self, selection):
        if selection and selection[0].indexes() and self.model.rowCount():
            row = selection[0].indexes()[0].row()
            if not config.currentAudioFile == os.path.abspath(self.model.item(row).toolTip()):
                self.parent.stopAudioPlaying()
            self.parent.audioPlayListIndex = row
            if self.justLaunched:
                self.justLaunched = False
            elif not config.isVlcPlayingInQThread:
                self.parent.playAudioPlaying()

    def updateMediaList(self):
        fileList = []
        for i in range(self.model.rowCount()):
            fileList.append(self.model.item(i).toolTip())
        self.parent.audioPlayList = fileList

    def add_item(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,
                                                    config.thisTranslation["menu11_audio"], "",
                                                    "MP3 Audio Files (*.mp3);;WAV Audio Files (*.wav);;MP4 Video Files (*.mp4);;AVI Video Files (*.avi)",
                                                    "", options)
        if files:
            for filePath in files:
                item = QStandardItem(os.path.basename(filePath))
                item.setToolTip(filePath)
                self.model.appendRow(item)
            # update media list
            self.updateMediaList()
            if not self.parent.isAudioPlayListPlaying:
                self.parent.playAudioPlayList()

    def remove_item(self):
        # Get the selected index
        current_row = self.view.currentIndex().row()
        if current_row == self.parent.audioPlayListIndex:
            self.parent.stopAudioPlaying()
        # Remove the item from the model
        self.model.removeRow(current_row)
        # update media list
        self.updateMediaList()
    
    def clear_all(self):
        self.parent.stopAudioPlaying()
        self.model.clear()
        # update media list
        self.updateMediaList()
        self.parent.stopAudioPlaying()

    def move_up(self):
        # Get the selected row
        current_row = self.view.currentIndex().row()
        # Move the item up in the model
        if current_row > 0:
            item = self.model.takeItem(current_row)
            self.model.insertRow(current_row - 1, item)
            # remove the empty row
            self.model.removeRow(current_row + 1)
            # update media list
            self.updateMediaList()
            # Select the moved item
            new_index = self.model.indexFromItem(item)
            self.view.setCurrentIndex(new_index)
            self.parent.audioPlayListIndex = new_index.row()

    def move_down(self):
        # Get the selected row
        current_row = self.view.currentIndex().row()
        if current_row < self.model.rowCount() - 1:
            item = self.model.takeItem(current_row)
            self.model.insertRow(current_row + 2, item)
            # remove the empty row
            self.model.removeRow(current_row)
            # update media list
            self.updateMediaList()
            # Select the moved item
            new_index = self.model.indexFromItem(item)
            self.view.setCurrentIndex(new_index)
            self.parent.audioPlayListIndex = new_index.row()


if __name__ == '__main__':
    app = QApplication([])
    ui = PlaylistUI()
    ui.show()
    app.exec()
