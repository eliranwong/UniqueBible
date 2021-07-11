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
            entry = QLineEdit(self)
            width = 200
            if len(field[1]) > 50:
                width = 400
            entry.setMinimumWidth(width)
            entry.setText(field[1])
            self.inputs.append(entry)
            layout.addRow(field[0], entry)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);
        layout.addWidget(buttonBox)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        inputs = [i.text() for i in self.inputs]
        return inputs


if __name__ == '__main__':
    from qtpy.QtWidgets import QApplication
    from util.ConfigUtil import ConfigUtil
    from util.LanguageUtil import LanguageUtil
    import sys
    import config

    ConfigUtil.setup()
    config.noQt = False
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")

    app = QApplication(sys.argv)
    title = "My test input"
    fields = [("Name", ""), ("City", "Jerusalem"), ("Apostles", "Matthew|Peter|Andrew|James|John|Philip|Bartholomew|Thomas|James|Judas|Simon")]
    dialog = MultiLineInputDialog(title, fields)
    if dialog.exec():
        data = dialog.getInputs()
        print(len(data))
    exit(0)