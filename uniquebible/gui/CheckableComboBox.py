import sys
from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt, QEvent
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QGuiApplication, QStandardItem, QPalette, QFontMetrics, QColor
    from PySide6.QtWidgets import (QStyledItemDelegate, QComboBox)
else:
    from qtpy.QtCore import Qt, QEvent
    from qtpy.QtWidgets import QApplication
    from qtpy.QtGui import QGuiApplication, QStandardItem, QPalette, QFontMetrics, QColor
    from qtpy.QtWidgets import (QStyledItemDelegate, QComboBox)

# We adpat the script shared from the following source.  We modified a bit to work with our application.
# Source: https://gis.stackexchange.com/questions/350148/qcombobox-multiple-selection-pyqt5
# Use QListWidget as an alternative
# https://stackoverflow.com/questions/4008649/qlistwidget-and-multiple-selection

class CheckableComboBox(QComboBox):

    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, items=[], checkedItems=[], toolTips=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up initial checked items
        self.checkItems = checkedItems

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setStyleSheet(config.widgetStyle)
        # Make the lineedit the same color as QPushButton
        palette = QGuiApplication.instance().palette()
        palette.setBrush(QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        # Use custom delegate
        self.setItemDelegate(CheckableComboBox.Delegate())

        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

        # Fill in items
        self.addItems(items, toolTips=toolTips)

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, object, event):

        if object == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if object == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        self.checkItems = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                self.model().item(i).setBackground(QColor(config.widgetBackgroundColorHover))
                self.model().item(i).setForeground(QColor(config.widgetForegroundColor))
                self.checkItems.append(self.model().item(i).text())
            else:
                self.model().item(i).setBackground(QColor(config.widgetBackgroundColor))
                self.model().item(i).setForeground(QColor(config.widgetForegroundColor))
        text = ", ".join(self.checkItems)

        # Compute elided text (with "...")
        # The following three lines does not work on macOS with Apple chip when PySide6 is used.
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

    def addItem(self, text, data=None, toolTip=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        if toolTip is not None:
            item.setToolTip(toolTip)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Checked if text in self.checkItems else Qt.Unchecked, Qt.CheckStateRole)
        item.setBackground(QColor(config.widgetBackgroundColor))
        item.setForeground(QColor(config.widgetForegroundColor))
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None, toolTips=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data, None if toolTips is None else toolTips[i])

    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).data())
        return res

    def clearAll(self):
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            item.setCheckState(Qt.Unchecked)

    def checkAll(self):
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            item.setCheckState(Qt.Checked)

    def checkFromList(self, texts):
        for i in range(self.model().rowCount()):
            item = self.model().item(i)
            if item.text() in texts:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    books = ["Genesis", "Exodus", "Leviticus"]
    combo = CheckableComboBox()
    combo.addItems(books)
    combo.show()
    app.exec_()
