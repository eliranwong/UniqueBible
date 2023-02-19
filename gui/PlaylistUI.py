import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListView

class PlaylistUI(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # Create the model and the view
        self.model = QStandardItemModel()
        self.view = QListView()
        self.view.setModel(self.model)

        # Add items to the model
        for filePath in self.parent.audioPlayList:
            item = QStandardItem(os.path.basename(filePath))
            item.setToolTip(filePath)
            self.model.appendRow(item)

        # Create the user interface widgets
        self.label = QLabel('Add song:')
        self.line_edit = QLineEdit()
        self.add_button = QPushButton('Add')
        self.remove_button = QPushButton('Remove')
        self.move_up_button = QPushButton('Move up')
        self.move_down_button = QPushButton('Move down')

        # Create the layout
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.label)
        hbox1.addWidget(self.line_edit)
        hbox1.addWidget(self.add_button)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.remove_button)
        hbox2.addWidget(self.move_up_button)
        hbox2.addWidget(self.move_down_button)

        vbox = QVBoxLayout()
        vbox.addWidget(self.view)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)

        # Set the layout
        self.setLayout(vbox)

        # Connect the signals and slots
        self.add_button.clicked.connect(self.add_item)
        self.remove_button.clicked.connect(self.remove_item)
        self.move_up_button.clicked.connect(self.move_up)
        self.move_down_button.clicked.connect(self.move_down)

    def add_item(self):
        # Get the text from the line edit
        text = self.line_edit.text()

        # Add the item to the model
        item = QStandardItem(text)
        self.model.appendRow(item)

        # Clear the line edit
        self.line_edit.clear()

    def remove_item(self):
        # Get the selected index
        index = self.view.currentIndex()

        # Remove the item from the model
        self.model.removeRow(index.row())

    def move_up(self):
        # Get the selected index
        index = self.view.currentIndex()

        # Move the item up in the model
        if index.row() > 0:
            item = self.model.takeItem(index.row())
            self.model.insertRow(index.row() - 1, item)

            # Select the moved item
            new_index = self.model.indexFromItem(item)
            self.view.setCurrentIndex(new_index)

    def move_down(self):
        # Get the selected index
        index = self.view.currentIndex()

        # Move the item down in the model
        if index.row() < self.model.rowCount() - 1:
            item = self.model.takeItem(index.row())
            self.model.insertRow(index.row() + 1, item)

            # Select the moved item
            new_index = self.model.indexFromItem(item)
            self.view.setCurrentIndex(new_index)

if __name__ == '__main__':
    app = QApplication([])
    ui = PlaylistUI()
    ui.show()
    app.exec()
