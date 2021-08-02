import config
from util.BibleBooks import BibleBooks

if __name__ == "__main__":
    config.noQt = False

from qtpy.QtWidgets import QComboBox, QLabel
from qtpy.QtWidgets import QPushButton
from qtpy.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QLineEdit, QRadioButton, QCheckBox

class MorphologyLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["cp7"])
        self.parent = parent
        self.bookList = BibleBooks.getStandardBookAbbreviations()
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()
        subLayout = QHBoxLayout()
        subLayout.addWidget(self.searchFieldWidget())
        button = QPushButton("Search")
        button.clicked.connect(self.searchMorphology)
        subLayout.addWidget(button)
        mainLayout.addLayout(subLayout)

        subLayout = QHBoxLayout()
        subLayout.addWidget(QLabel("Start:"))
        self.startBookCombo = QComboBox()
        subLayout.addWidget(self.startBookCombo)
        self.startBookCombo.addItems(self.bookList)
        self.startBookCombo.setCurrentIndex(0)
        subLayout.addWidget(QLabel("End:"))
        self.endBookCombo = QComboBox()
        subLayout.addWidget(self.endBookCombo)
        self.endBookCombo.addItems(self.bookList)
        self.endBookCombo.setCurrentIndex(65)
        subLayout.addWidget(QLabel(" "))
        button = QPushButton("Entire Bible")
        button.clicked.connect(lambda: self.selectBookCombos(0, 65))
        subLayout.addWidget(button)
        button = QPushButton("OT")
        button.clicked.connect(lambda: self.selectBookCombos(0, 38))
        subLayout.addWidget(button)
        button = QPushButton("NT")
        button.clicked.connect(lambda: self.selectBookCombos(39, 65))
        subLayout.addWidget(button)
        button = QPushButton("Gospels")
        button.clicked.connect(lambda: self.selectBookCombos(39, 42))
        subLayout.addWidget(button)
        subLayout.addStretch()
        mainLayout.addLayout(subLayout)

        subLayout = QHBoxLayout()
        self.searchTypeBox = QGroupBox("Type")
        layout = QVBoxLayout()
        self.strongsRadioButton = QRadioButton("Lexical")
        self.strongsRadioButton.setToolTip("G2424")
        self.strongsRadioButton.toggled.connect(lambda checked, mode="Lexical": self.searchTypeChanged(checked, mode))
        self.strongsRadioButton.setChecked(True)
        layout.addWidget(self.strongsRadioButton)
        radioButton = QRadioButton("Word")
        radioButton.setToolTip("Ἰησοῦς")
        radioButton.toggled.connect(lambda checked, mode="Word": self.searchTypeChanged(checked, mode))
        layout.addWidget(radioButton)
        radioButton = QRadioButton("Gloss")
        radioButton.setToolTip("Jesus")
        radioButton.toggled.connect(lambda checked, mode="Gloss": self.searchTypeChanged(checked, mode))
        layout.addWidget(radioButton)
        # radioButton = QRadioButton("Transliteration")
        # radioButton.setToolTip("Iēsous")
        # radioButton.toggled.connect(lambda checked, mode="Transliteration": self.searchTypeChanged(checked, mode))
        # layout.addWidget(radioButton)
        self.searchTypeBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.searchTypeBox)

        posList = ["Noun", "Pronoun", "Adjective", "Verb", "Article"]
        self.partOfSpeechBox = QGroupBox("Part of speech")
        layout = QVBoxLayout()
        for count, pos in enumerate(posList):
            button = QRadioButton(pos)
            button.toggled.connect(lambda checked, mode=pos: self.searchModeChanged(checked, mode))
            layout.addWidget(button)
            if count == 0:
                self.nounButton = button
        self.partOfSpeechBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.partOfSpeechBox)

        caseList = ["Accusative", "Dative", "Genitive", "Nominative", "Vocative"]
        self.caseCheckBoxes = []
        self.caseBox = QGroupBox("Case")
        self.caseBox.hide()
        layout = QVBoxLayout()
        for case in caseList:
            checkbox = QCheckBox(case)
            layout.addWidget(checkbox)
            self.caseCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, case=case: self.caseCheckBoxChanged(checked, case))
        self.caseBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.caseBox)

        tenseList = ["Aorist", "Future", "Imperfect", "Perfect", "Pluperfect", "Present"]
        self.tenseCheckBoxes = []
        self.tenseBox = QGroupBox("Tense")
        self.tenseBox.hide()
        layout = QVBoxLayout()
        for tense in tenseList:
            checkbox = QCheckBox(tense)
            layout.addWidget(checkbox)
            self.tenseCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, tense=tense: self.tenseCheckBoxChanged(checked, tense))
        self.tenseBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.tenseBox)

        voiceList = ["Active", "Middle", "Passive"]
        self.voiceCheckBoxes = []
        self.voiceBox = QGroupBox("Voice")
        self.voiceBox.hide()
        layout = QVBoxLayout()
        for voice in voiceList:
            checkbox = QCheckBox(voice)
            layout.addWidget(checkbox)
            self.voiceCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, voice=voice: self.voiceCheckBoxChanged(checked, voice))
        self.voiceBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.voiceBox)

        moodList = ["Imperative", "Indicative", "Optative", "Subjunctive"]
        self.moodCheckBoxes = []
        self.moodBox = QGroupBox("Mood")
        self.moodBox.hide()
        layout = QVBoxLayout()
        for mood in moodList:
            checkbox = QCheckBox(mood)
            layout.addWidget(checkbox)
            self.moodCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, mood=mood: self.moodCheckBoxChanged(checked, mood))
        self.moodBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.moodBox)

        personList = ["First", "Second", "Third"]
        self.personCheckBoxes = []
        self.personBox = QGroupBox("Person")
        self.personBox.hide()
        layout = QVBoxLayout()
        for person in personList:
            checkbox = QCheckBox(person)
            layout.addWidget(checkbox)
            self.personCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, person=person: self.personCheckBoxChanged(checked, person))
        self.personBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.personBox)

        numberList = ["Singular", "Plural", "Dual"]
        self.numberCheckBoxes = []
        self.numberBox = QGroupBox("Number")
        self.numberBox.hide()
        layout = QVBoxLayout()
        for number in numberList:
            checkbox = QCheckBox(number)
            layout.addWidget(checkbox)
            self.numberCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, number=number: self.numberCheckBoxChanged(checked, number))
        self.numberBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.numberBox)

        genderList = ["Masculine", "Feminine", "Neuter"]
        self.genderCheckBoxes = []
        self.genderBox = QGroupBox("Gender")
        self.genderBox.hide()
        layout = QVBoxLayout()
        for gender in genderList:
            checkbox = QCheckBox(gender)
            layout.addWidget(checkbox)
            self.genderCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, gender=gender: self.genderCheckBoxChanged(checked, gender))
        self.genderBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.genderBox)

        mainLayout.addLayout(subLayout)

        mainLayout.addStretch()
        self.setLayout(mainLayout)

        self.nounButton.setChecked(True)

    def selectBookCombos(self, start, end):
        self.startBookCombo.setCurrentIndex(start)
        self.endBookCombo.setCurrentIndex(end)

    def searchTypeChanged(self, checked, type):
        self.type = type

    def caseCheckBoxChanged(self, state, case):
        if int(state) > 0:
            for caseCheckbox in self.caseCheckBoxes:
                if caseCheckbox.isChecked() and case != caseCheckbox.text():
                    caseCheckbox.setChecked(False)

    def numberCheckBoxChanged(self, state, number):
        if int(state) > 0:
            for numberCheckbox in self.numberCheckBoxes:
                if numberCheckbox.isChecked() and number != numberCheckbox.text():
                    numberCheckbox.setChecked(False)

    def tenseCheckBoxChanged(self, state, tense):
        if int(state) > 0:
            for tenseCheckbox in self.tenseCheckBoxes:
                if tenseCheckbox.isChecked() and tense != tenseCheckbox.text():
                    tenseCheckbox.setChecked(False)

    def moodCheckBoxChanged(self, state, mood):
        if int(state) > 0:
            for moodCheckbox in self.moodCheckBoxes:
                if moodCheckbox.isChecked() and mood != moodCheckbox.text():
                    moodCheckbox.setChecked(False)

    def voiceCheckBoxChanged(self, state, voice):
        if int(state) > 0:
            for voiceCheckbox in self.voiceCheckBoxes:
                if voiceCheckbox.isChecked() and voice != voiceCheckbox.text():
                    voiceCheckbox.setChecked(False)

    def genderCheckBoxChanged(self, state, gender):
        if int(state) > 0:
            for genderCheckbox in self.genderCheckBoxes:
                if genderCheckbox.isChecked() and gender != genderCheckbox.text():
                    genderCheckbox.setChecked(False)

    def searchFieldWidget(self):
        self.searchField = QLineEdit()
        self.searchField.setClearButtonEnabled(True)
        self.searchField.setToolTip(config.thisTranslation["menu5_searchItems"])
        self.searchField.returnPressed.connect(self.searchMorphology)
        return self.searchField

    def searchModeChanged(self, checked, mode):
        if checked:
            self.mode = mode
            if mode in ("Noun", "Adjective"):
                self.genderBox.show()
                self.numberBox.show()
                self.caseBox.show()
                self.personBox.hide()
                self.tenseBox.hide()
                self.moodBox.hide()
                self.voiceBox.hide()
            elif mode in ("Pronoun", "Article"):
                self.genderBox.hide()
                self.numberBox.show()
                self.caseBox.show()
                self.personBox.show()
                self.tenseBox.hide()
                self.moodBox.hide()
                self.voiceBox.hide()
            elif mode in ("Verb"):
                self.genderBox.hide()
                self.numberBox.show()
                self.personBox.show()
                self.tenseBox.show()
                self.moodBox.show()
                self.voiceBox.show()
                self.caseBox.hide()

    def searchMorphology(self):
        searchTerm = self.searchField.text()
        if len(searchTerm) > 1:
            morphologyList = []
            morphologyList.append(self.mode)
            if self.mode == "Noun":
                for caseCheckbox in self.caseCheckBoxes:
                    if caseCheckbox.isChecked():
                        morphologyList.append(caseCheckbox.text())
            if self.mode == "Verb":
                for tenseCheckbox in self.tenseCheckBoxes:
                    if tenseCheckbox.isChecked():
                        morphologyList.append(tenseCheckbox.text())
                for moodCheckbox in self.moodCheckBoxes:
                    if moodCheckbox.isChecked():
                        morphologyList.append(moodCheckbox.text())
                for voiceCheckbox in self.voiceCheckBoxes:
                    if voiceCheckbox.isChecked():
                        morphologyList.append(voiceCheckbox.text())
                for personCheckbox in self.personCheckBoxes:
                    if personCheckbox.isChecked():
                        morphologyList.append(personCheckbox.text())
            for genderCheckbox in self.genderCheckBoxes:
                if genderCheckbox.isChecked():
                    morphologyList.append(genderCheckbox.text())
            for numberCheckbox in self.numberCheckBoxes:
                if numberCheckbox.isChecked():
                    morphologyList.append(numberCheckbox.text())
            morphology = ",".join(morphologyList)
            startBook = self.startBookCombo.currentIndex() + 1
            endBook = self.endBookCombo.currentIndex() + 1
            if endBook < startBook:
                endBook = startBook
            if self.type == "Lexical":
                command = "SEARCHMORPHOLOGYBYLEX:::{0}:::{1}:::{2}-{3}".format(searchTerm, morphology, startBook, endBook)
            elif self.type == "Word":
                command = "SEARCHMORPHOLOGYBYWORD:::{0}:::{1}:::{2}-{3}".format(searchTerm, morphology, startBook, endBook)
            elif self.type == "Gloss":
                command = "SEARCHMORPHOLOGYBYGLOSS:::{0}:::{1}:::{2}-{3}".format(searchTerm, morphology, startBook, endBook)
            self.parent.runTextCommand(command)


## Standalone development code

class DummyParent():
    def runTextCommand(self, command):
        print(command)

    def verseReference(self, command):
        return ['', '']


if __name__ == "__main__":
    from qtpy import QtWidgets
    from qtpy.QtWidgets import QWidget
    import sys

    from util.LanguageUtil import LanguageUtil
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    app = QtWidgets.QApplication(sys.argv)
    window = MorphologyLauncher(DummyParent())
    window.show()
    sys.exit(app.exec_())

