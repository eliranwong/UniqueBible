from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QComboBox
    from PySide6.QtWidgets import QLineEdit, QFormLayout
    from PySide6.QtWidgets import QDialog
    from PySide6.QtWidgets import QDialogButtonBox
else:
    from qtpy.QtWidgets import QComboBox
    from qtpy.QtWidgets import QLineEdit, QFormLayout
    from qtpy.QtWidgets import QDialog
    from qtpy.QtWidgets import QDialogButtonBox


class MultiLineInputDialog(QDialog):
    def __init__(self, title, fields):
        super().__init__()
        self.setWindowTitle(title)
        self.inputs = []
        layout = QFormLayout(self)
        for field in fields:
            value = field[1]
            if type(value) is str:
                entry = QLineEdit(self)
                width = 200
                if len(field[1]) > 50:
                    width = 400
                entry.setMinimumWidth(width)
                entry.setText(value)
            elif isinstance(value, list):
                entry = QComboBox()
                entry.addItems(value)
                if len(field) > 2:
                    index = entry.findText(field[2])
                    if index != -1:
                        entry.setCurrentIndex(index)
            self.inputs.append(entry)
            layout.addRow(field[0], entry)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        values = []
        for input in self.inputs:
            if isinstance(input, QLineEdit):
                values.append(input.text())
            elif isinstance(input, QComboBox):
                values.append(input.currentText())
        return values


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    from uniquebible.util.ConfigUtil import ConfigUtil
    from uniquebible.util.LanguageUtil import LanguageUtil
    import sys
    from uniquebible import config

    ConfigUtil.setup()
    config.noQt = False
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")

    app = QApplication(sys.argv)
    title = "My test input"
    fields = [("Name", ""), ("Bibles", ["KJV", "MIB"]), ("City", "Jerusalem"),
              ("Apostle", ["Matthew", "Peter", "Andrew", "James", "John", "Philip", "Bartholomew", "Thomas", "James", "Judas", "Simon"])]
    dialog = MultiLineInputDialog(title, fields)
    if dialog.exec():
        data = dialog.getInputs()
        print(data)
    exit(0)