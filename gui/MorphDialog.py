import config
from ast import literal_eval
from PySide2.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QDialog, QLabel, QCheckBox)

class MorphDialog(QDialog):

    def __init__(self, parent, items):
        super().__init__()
        self.parent = parent
        lexeme, self.lexicalEntry, morphologyString = items

        # morphology items
        morphology = QWidget()
        morphologyLayout = QVBoxLayout()
        morphologyLayout.setContentsMargins(0, 0, 0, 0)

        lexemeLabel = QLabel(lexeme)
        morphologyLayout.addWidget(lexemeLabel)

        self.checkBoxes = []
        self.morphologyList = morphologyString.split(",")
        for counter, value in enumerate(self.morphologyList[:-1]):
            self.checkBoxes.append(QCheckBox(value))
            morphologyLayout.addWidget(self.checkBoxes[counter])
        morphology.setLayout(morphologyLayout)

        # Two buttons
        buttons = QWidget()
        buttonsLayout = QHBoxLayout()
        self.searchButton = QPushButton("&{0}".format(config.thisTranslation["menu5_search"]))
        self.searchButton.clicked.connect(self.searchMorphology)
        buttonsLayout.addWidget(self.searchButton)
        self.cancelButton = QPushButton("&{0}".format(config.thisTranslation["message_cancel"]))
        self.cancelButton.clicked.connect(self.close)
        buttonsLayout.addWidget(self.cancelButton)
        buttons.setLayout(buttonsLayout)

        # set main layout & title
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(morphology)
        mainLayout.addWidget(buttons)

        self.setLayout(mainLayout)
        self.setWindowTitle(config.thisTranslation["message_searchMorphology"])

    def searchMorphology(self):
        command = "MORPHOLOGY:::LexicalEntry LIKE '%{0},%'".format(self.lexicalEntry.split(",")[0])
        selectedItems = [self.morphologyList[counter] for counter, value in enumerate(self.checkBoxes) if value.isChecked()]
        if selectedItems:
            joinedItems = ",%".join(selectedItems)
            command += " AND Morphology LIKE '%{0}%'".format(joinedItems)
        self.parent.runTextCommand(command)
        self.close()
