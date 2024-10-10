from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QLabel, QCheckBox
else:
    from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QDialog, QLabel, QCheckBox
from uniquebible.gui.CheckableComboBox import CheckableComboBox

class MorphDialog(QDialog):

    def __init__(self, parent, items):
        super().__init__()
        self.parent = parent
        lexeme, lexicalEntry, morphologyString, translations = items

        # morphology items
        morphologyLayout = QVBoxLayout()
        morphologyLayout.setContentsMargins(0, 0, 0, 0)

        lexemeLabel = QLabel(lexeme)
        morphologyLayout.addWidget(lexemeLabel)

        self.checkBoxes = []
        self.morphologyList = morphologyString.split(",")
        for counter, value in enumerate(self.morphologyList[:-1]):
            self.checkBoxes.append(QCheckBox(value))
            morphologyLayout.addWidget(self.checkBoxes[counter])

        # Two buttons
        buttonsLayout = QHBoxLayout()
        self.searchButton = QPushButton("&{0}".format(config.thisTranslation["menu5_search"]))
        self.searchButton.clicked.connect(lambda: self.searchMorphology(lexicalEntry))
        buttonsLayout.addWidget(self.searchButton)
        self.cancelButton = QPushButton("&{0}".format(config.thisTranslation["message_cancel"]))
        self.cancelButton.clicked.connect(self.close)
        buttonsLayout.addWidget(self.cancelButton)

        # options to search morphology in combination with interlinear translations
        self.interlinearCombo = CheckableComboBox(translations, [])

        # set main layout & title
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(morphologyLayout)
        mainLayout.addWidget(self.interlinearCombo)
        mainLayout.addLayout(buttonsLayout)
        self.setLayout(mainLayout)
        self.setWindowTitle(config.thisTranslation["message_searchMorphology"])

    def searchMorphology(self, lexicalEntry):
        command = "MORPHOLOGY:::LexicalEntry LIKE '%{0},%'".format(lexicalEntry)
        selectedItems = [self.morphologyList[counter] for counter, value in enumerate(self.checkBoxes) if value.isChecked()]
        # add selected morphology
        if selectedItems:
            joinedItems = ",%".join(selectedItems)
            command += " AND Morphology LIKE '%{0}%'".format(joinedItems)
        # add selected translation
        if self.interlinearCombo.checkItems:
            translations = ["Interlinear LIKE '%{0}%'".format(i) for i in self.interlinearCombo.checkItems]
            command += " AND ({0})".format(" OR ".join(translations))
        self.parent.runTextCommand(command)
        self.close()
