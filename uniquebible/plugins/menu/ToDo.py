from uniquebible import config
import os, shutil
from datetime import date
from uniquebible.db.JournalSqlite import JournalSqlite
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QStandardItem, QStandardItemModel, QGuiApplication
    from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListView, QSplitter, QAbstractItemView, QMessageBox
else:
    from qtpy.QtCore import Qt
    from qtpy.QtGui import QStandardItem, QStandardItemModel, QGuiApplication
    from qtpy.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QListView, QSplitter, QAbstractItemView, QMessageBox

class ToDo(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("To-Do")
        self.dataFile = os.path.join(config.packageDir, "plugins", "menu", "ToDo", "ToDo.txt")
        if not os.path.isfile(self.dataFile):
            open(self.dataFile, "a", encoding="utf-8").close()

        # Create the model and the view
        self.view = QListView()
        self.model = QStandardItemModel(self.view)
        self.view.setModel(self.model)

        self.searchView = QListView()
        self.searchView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.searchModel = QStandardItemModel(self.searchView)
        self.searchView.setModel(self.searchModel)
        self.searchView.selectionModel().selectionChanged.connect(self.search_result_selected)

        self.resetModel()

        # Create the user interface widgets
        self.filter = QLineEdit()
        self.filter.setToolTip("Search [regular expression enabled]")
        self.filter.setClearButtonEnabled(True)
        self.filter.textChanged.connect(self.filter_item)
        self.label = QLabel('New')
        self.line_edit = QLineEdit()
        self.line_edit.setToolTip("Enter new item here ...")
        self.line_edit.setClearButtonEnabled(True)
        self.line_edit.returnPressed.connect(self.add_item)
        self.add_button = QPushButton('Add')
        self.remove_button = QPushButton('Remove')
        self.move_up_button = QPushButton('Move up')
        self.move_down_button = QPushButton('Move down')
        self.copy_all_button = QPushButton('Copy All')
        self.clear_all_button = QPushButton('Clear All')
        self.undo_button = QPushButton('Undo')
        self.save_button = QPushButton('Save Changes')
        self.done_button = QPushButton("Done and Keep in Today's Journal")

        # Create the layout
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.label)
        hbox1.addWidget(self.line_edit)
        hbox1.addWidget(self.add_button)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.remove_button)
        hbox2.addWidget(self.move_up_button)
        hbox2.addWidget(self.move_down_button)

        hbox3 = QHBoxLayout()
        hbox3.addWidget(self.clear_all_button)
        hbox3.addWidget(self.undo_button)
        hbox3.addWidget(self.save_button)

        hbox4 = QHBoxLayout()
        hbox4.addWidget(self.done_button)
        hbox4.addWidget(self.copy_all_button)

        leftBox = QVBoxLayout()
        leftBox.addWidget(self.filter)
        leftBox.addWidget(self.searchView)
        widgetLt = QWidget()
        widgetLt.setLayout(leftBox)

        rightBox = QVBoxLayout()
        rightBox.addWidget(self.view)
        rightBox.addLayout(hbox1)
        rightBox.addLayout(hbox2)
        rightBox.addLayout(hbox4)
        rightBox.addLayout(hbox3)
        widgetRt = QWidget()
        widgetRt.setLayout(rightBox)

        # Set the layout
        splitter = QSplitter(Qt.Horizontal, self)
        splitter.addWidget(widgetLt)
        splitter.addWidget(widgetRt)
        mainBox = QVBoxLayout()
        mainBox.addWidget(splitter)
        self.setLayout(mainBox)
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)

        # Connect the signals and slots
        self.add_button.clicked.connect(self.add_item)
        self.remove_button.clicked.connect(self.remove_item)
        self.move_up_button.clicked.connect(self.move_up)
        self.move_down_button.clicked.connect(self.move_down)
        self.clear_all_button.clicked.connect(self.model.clear)
        self.copy_all_button.clicked.connect(lambda: QApplication.clipboard().setText("\n".join(self.dataList)))
        self.undo_button.clicked.connect(self.resetModel)
        self.save_button.clicked.connect(self.saveChanges)
        self.done_button.clicked.connect(self.done_and_keep_journal_record)

    def resetModel(self):
        with open(self.dataFile, 'r', encoding='utf8') as fileObj:
            self.dataList = fileObj.read().split("\n")
        self.dataList = [i.strip() for i in self.dataList if i.strip()]
        self.displayData()
    
    def displayData(self):
        self.model.clear()
        for text in self.dataList:
            item = QStandardItem(text)
            self.model.appendRow(item)
        if self.dataList:
            self.view.setCurrentIndex(self.model.index(0, 0))

    def filter_item(self):
        self.searchModel.clear()
        filter = self.filter.text().strip()
        if filter:
            items = self.model.findItems(filter, flags=Qt.MatchRegularExpression)
            for item in items:
                self.searchModel.appendRow(QStandardItem(item.text()))

    def search_result_selected(self, selection):
        if selection and selection[0].indexes():
            row = selection[0].indexes()[0].row()
            text = self.searchModel.item(row).text()
            self.select_todo_item(text)

    def select_todo_item(self, text):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            if text == item.text():
                self.view.setCurrentIndex(self.model.indexFromItem(item))
                break

    def getDataContent(self):
        items = []
        for i in range(self.model.rowCount()):
            text = self.model.item(i).text().strip()
            if text:
                items.append(text)
        return "\n".join(items)
    
    def closeEvent(self, event):
        dataContent = self.getDataContent()
        if not dataContent == "\n".join(self.dataList):
            # Prompt the user for confirmation
            msg_box = QMessageBox(
                QMessageBox.Question, 
                'Confirmation', 
                f'Do you want to save changes?'
            )
            msg_box.addButton(QMessageBox.Yes)
            msg_box.addButton(QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            button_clicked = msg_box.exec()
            # Check the user's response
            if button_clicked == QMessageBox.Yes or True or 1:
                self.saveChanges()
            event.accept()

    def saveChanges(self):
        dataContent = self.getDataContent()
        if dataContent == "\n".join(self.dataList):
            config.mainWindow.displayMessage("No changes!")
        else:
            # backup first
            shutil.copyfile(self.dataFile, f"{self.dataFile}.bk")
            with open(self.dataFile, 'w', encoding='utf8') as fileObj:
                fileObj.write(dataContent)
            config.mainWindow.displayMessage("Changes saved!")

    def add_item(self):
        # Get the text from the line edit
        text = self.line_edit.text().strip()

        if text:
            # Add the item to the model
            item = QStandardItem(text)
            self.model.appendRow(item)

            # Clear the line edit
            self.line_edit.clear()

    def done_and_keep_journal_record(self):
        # Get the selected row
        text = self.model.itemFromIndex(self.view.currentIndex()).text().strip()
        if text:
            today = date.today()
            JournalSqlite().appendJournalNote(today.year, today.month, today.day, f"<p><b>DONE:</b><br>{text}</p>")
            self.remove_item()
            self.saveChanges()

    def remove_item(self):
        # Get the selected index
        index = self.view.currentIndex()

        # Remove the item from the model
        self.model.removeRow(index.row())

    def move_up(self):
        # Get the selected row
        current_row = self.view.currentIndex().row()
        # Move the item up in the model
        if current_row > 0:
            item = self.model.takeItem(current_row)
            self.model.insertRow(current_row - 1, item)
            # remove the empty row
            self.model.removeRow(current_row + 1)
            # Select the moved item
            new_index = self.model.indexFromItem(item)
            self.view.setCurrentIndex(new_index)

    def move_down(self):
        # Get the selected row
        current_row = self.view.currentIndex().row()
        if current_row < self.model.rowCount() - 1:
            item = self.model.takeItem(current_row)
            self.model.insertRow(current_row + 2, item)
            # remove the empty row
            self.model.removeRow(current_row)
            # Select the moved item
            new_index = self.model.indexFromItem(item)
            self.view.setCurrentIndex(new_index)


config.mainWindow.toDo = ToDo()
config.mainWindow.toDo.show()
config.mainWindow.bringToForeground(config.mainWindow.toDo)