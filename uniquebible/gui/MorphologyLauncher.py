from uniquebible import config
from uniquebible.util.BibleBooks import BibleBooks

if __name__ == "__main__":
    config.noQt = False
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QComboBox, QLabel
    from PySide6.QtWidgets import QPushButton
    from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QLineEdit, QRadioButton, QCheckBox
else:
    from qtpy.QtWidgets import QComboBox, QLabel
    from qtpy.QtWidgets import QPushButton
    from qtpy.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QLineEdit, QRadioButton, QCheckBox

# Hebrew:
# https://uhg.readthedocs.io/en/latest/
# https://blakleycreative.com/jtb/HebrewGrammar.htm
# Greek:
# https://ugg.readthedocs.io/en/latest/
class MorphologyLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["cp7"])
        self.parent = parent
        self.bookList = BibleBooks().getStandardBookAbbreviations()
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
        button = QPushButton("Current Book")
        button.clicked.connect(lambda: self.selectBookCombos(config.mainB-1, config.mainB-1))
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

        languageList = ["Greek", "Hebrew"]
        self.languageBox = QGroupBox("Language")
        layout = QVBoxLayout()
        for count, lang in enumerate(languageList):
            button = QRadioButton(lang)
            button.toggled.connect(lambda checked, mode=lang: self.languageChanged(checked, mode))
            layout.addWidget(button)
            if count == 0:
                self.greekButton = button
        self.languageBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.languageBox)

        posList = ["Adjective", "Adverb", "Article", "Conjunction", "Interjection", "Noun", "Participle", "Preposition", "Pronoun", "Verb", ""]
        self.posCheckBoxes = []
        self.partOfSpeechBox = QGroupBox("Part of speech")
        layout = QVBoxLayout()
        for count, pos in enumerate(posList):
            button = QRadioButton(pos)
            button.toggled.connect(lambda checked, mode=pos: self.partOfSpeechChanged(checked, mode))
            layout.addWidget(button)
            if count == 0:
                self.nounButton = button
        self.partOfSpeechBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.partOfSpeechBox)

        greekCaseList = ["Accusative", "Dative", "Genitive", "Nominative", "Vocative"]
        self.greekCaseCheckBoxes = []
        self.greekCaseBox = QGroupBox("Case")
        self.greekCaseBox.hide()
        layout = QVBoxLayout()
        for case in greekCaseList:
            checkbox = QCheckBox(case)
            layout.addWidget(checkbox)
            self.greekCaseCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, case=case: self.checkBoxChanged(checked, case, self.greekCaseCheckBoxes))
        self.greekCaseBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.greekCaseBox)

        greekTenseList = ["Aorist", "Future", "Imperfect", "Perfect", "Pluperfect", "Present"]
        self.greekTenseCheckBoxes = []
        self.greekTenseBox = QGroupBox("Tense")
        self.greekTenseBox.hide()
        layout = QVBoxLayout()
        for tense in greekTenseList:
            checkbox = QCheckBox(tense)
            layout.addWidget(checkbox)
            self.greekTenseCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, tense=tense: self.checkBoxChanged(checked, tense, self.greekTenseCheckBoxes))
        self.greekTenseBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.greekTenseBox)

        voiceList = ["Active", "Middle", "Passive"]
        self.voiceCheckBoxes = []
        self.voiceBox = QGroupBox("Voice")
        self.voiceBox.hide()
        layout = QVBoxLayout()
        for voice in voiceList:
            checkbox = QCheckBox(voice)
            layout.addWidget(checkbox)
            self.voiceCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, voice=voice: self.checkBoxChanged(checked, voice, self.voiceCheckBoxes))
        self.voiceBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.voiceBox)

        greekMoodList = ["Imperative", "Indicative", "Optative", "Subjunctive"]
        self.greekMoodCheckBoxes = []
        self.greekMoodBox = QGroupBox("Mood")
        self.greekMoodBox.hide()
        layout = QVBoxLayout()
        for mood in greekMoodList:
            checkbox = QCheckBox(mood)
            layout.addWidget(checkbox)
            self.greekMoodCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, mood=mood: self.checkBoxChanged(checked, mood, self.greekMoodCheckBoxes))
        self.greekMoodBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.greekMoodBox)

        hebrewStateList = ["Construct", "Absolute"]
        self.hebrewStateCheckBoxes = []
        self.hebrewStateBox = QGroupBox("State")
        self.hebrewStateBox.hide()
        layout = QVBoxLayout()
        for state in hebrewStateList:
            checkbox = QCheckBox(state)
            layout.addWidget(checkbox)
            self.hebrewStateCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, state=state: self.checkBoxChanged(checked, state, self.hebrewStateCheckBoxes))
        self.hebrewStateBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.hebrewStateBox)

        hebrewStateList = ["Construct", "Absolute"]
        self.hebrewStateCheckBoxes = []
        self.hebrewStateBox = QGroupBox("State")
        self.hebrewStateBox.hide()
        layout = QVBoxLayout()
        for stem in hebrewStateList:
            checkbox = QCheckBox(stem)
            layout.addWidget(checkbox)
            self.hebrewStateCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, stem=stem: self.checkBoxChanged(checked, stem, self.hebrewStateCheckBoxes))
        self.hebrewStateBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.hebrewStateBox)

        hebrewPatternList = ["Hif‘il", "Hitpa“el", "Nif‘al", "Pi“el", "Pu“al", "Qal", "Wayyiqtol"]
        self.hebrewPatternCheckBoxes = []
        self.hebrewPatternBox = QGroupBox("State")
        self.hebrewPatternBox.hide()
        layout = QVBoxLayout()
        for stem in hebrewPatternList:
            checkbox = QCheckBox(stem)
            layout.addWidget(checkbox)
            self.hebrewPatternCheckBoxes.append(checkbox)
            # checkbox.stateChanged.connect(lambda checked, stem=stem: self.checkBoxChanged(checked, stem, self.hebrewPatternCheckBoxes))
        self.hebrewPatternBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.hebrewPatternBox)

        personList = ["First", "Second", "Third"]
        self.personCheckBoxes = []
        self.personBox = QGroupBox("Person")
        self.personBox.hide()
        layout = QVBoxLayout()
        for person in personList:
            checkbox = QCheckBox(person)
            layout.addWidget(checkbox)
            self.personCheckBoxes.append(checkbox)
            checkbox.stateChanged.connect(lambda checked, person=person: self.checkBoxChanged(checked, person, self.personCheckBoxes))
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
            checkbox.stateChanged.connect(lambda checked, number=number: self.checkBoxChanged(checked, number, self.numberCheckBoxes))
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
            checkbox.stateChanged.connect(lambda checked, gender=gender: self.checkBoxChanged(checked, gender, self.genderCheckBoxes))
        self.genderBox.setLayout(layout)
        layout.addStretch()
        subLayout.addWidget(self.genderBox)

        # TODO:
        hebrewList = ["Absolute", "",  "Infinitive", "Pronominal", ""]

        self.spacerBox1 = QGroupBox(" ")
        layout = QVBoxLayout()
        layout.addStretch()
        self.spacerBox1.setLayout(layout)
        subLayout.addWidget(self.spacerBox1)

        self.spacerBox2 = QGroupBox(" ")
        layout = QVBoxLayout()
        layout.addStretch()
        self.spacerBox2.setLayout(layout)
        subLayout.addWidget(self.spacerBox2)

        self.spacerBox3 = QGroupBox(" ")
        layout = QVBoxLayout()
        layout.addStretch()
        self.spacerBox3.setLayout(layout)
        subLayout.addWidget(self.spacerBox3)

        self.spacerBox4 = QGroupBox(" ")
        layout = QVBoxLayout()
        layout.addStretch()
        self.spacerBox4.setLayout(layout)
        subLayout.addWidget(self.spacerBox4)

        self.spacerBox5 = QGroupBox(" ")
        layout = QVBoxLayout()
        layout.addStretch()
        self.spacerBox5.setLayout(layout)
        subLayout.addWidget(self.spacerBox5)

        mainLayout.addLayout(subLayout)

        mainLayout.addStretch()
        self.setLayout(mainLayout)

        self.greekButton.setChecked(True)
        self.nounButton.setChecked(True)

    def selectBookCombos(self, start, end):
        self.startBookCombo.setCurrentIndex(start)
        self.endBookCombo.setCurrentIndex(end)

    def searchTypeChanged(self, checked, type):
        self.type = type

    def searchFieldWidget(self):
        self.searchField = QLineEdit()
        self.searchField.setClearButtonEnabled(True)
        self.searchField.setToolTip(config.thisTranslation["menu5_searchItems"])
        self.searchField.returnPressed.connect(self.searchMorphology)
        return self.searchField

    def checkBoxChanged(self, state, value, checkboxes):
        if int(state) > 0:
            for checkbox in checkboxes:
                if checkbox.isChecked() and value != checkbox.text():
                    checkbox.setChecked(False)

    def languageChanged(self, checked, language):
        if checked:
            self.language = language
        self.updateAllCheckboxes()

    def partOfSpeechChanged(self, checked, pos):
        if checked:
            self.pos = pos
        self.updateAllCheckboxes()

    def updateAllCheckboxes(self):
        self.genderBox.hide()
        self.numberBox.hide()
        self.greekCaseBox.hide()
        self.personBox.hide()
        self.greekTenseBox.hide()
        self.greekMoodBox.hide()
        self.voiceBox.hide()
        self.hebrewStateBox.hide()
        self.hebrewPatternBox.hide()
        self.spacerBox1.hide()
        self.spacerBox2.hide()
        self.spacerBox3.hide()
        self.spacerBox4.hide()
        self.spacerBox5.hide()
        if self.language == "Greek":
            if self.pos in ("Noun", "Adjective"):
                self.greekCaseBox.show()
                self.numberBox.show()
                self.genderBox.show()
                self.spacerBox4.show()
                self.spacerBox5.show()
            elif self.pos in ("Pronoun", "Article"):
                self.greekCaseBox.show()
                self.numberBox.show()
                self.genderBox.show()
                self.personBox.show()
                self.spacerBox5.show()
            elif self.pos == "Verb":
                self.greekTenseBox.show()
                self.voiceBox.show()
                self.greekMoodBox.show()
                self.personBox.show()
                self.numberBox.show()
            elif self.pos == "Adverb":
                self.greekCaseBox.show()
                self.numberBox.show()
                self.genderBox.show()
                self.spacerBox4.show()
                self.spacerBox5.show()
            else:
                self.spacerBox1.show()
                self.spacerBox2.show()
                self.spacerBox3.show()
                self.spacerBox4.show()
                self.spacerBox5.show()
        else:
            if self.pos in ("Noun", "Adjective", "Preposition", "Pronoun"):
                self.numberBox.show()
                self.genderBox.show()
                self.hebrewStateBox.show()
                self.spacerBox4.show()
                self.spacerBox5.show()
            elif self.pos in ("Verb", "Adverb"):
                self.personBox.show()
                self.genderBox.show()
                self.numberBox.show()
                self.hebrewStateBox.show()
                self.hebrewPatternBox.show()
            else:
                self.spacerBox1.show()
                self.spacerBox2.show()
                self.spacerBox3.show()
                self.spacerBox4.show()
                self.spacerBox5.show()

    def searchMorphology(self):
        searchTerm = self.searchField.text()
        if len(searchTerm) > 1:
            morphologyList = []
            morphologyList.append(self.pos)
            if self.language == "Greek":
                if self.pos in ("Noun", "Adjective"):
                    checkBoxList = [self.greekCaseCheckBoxes, self.numberCheckBoxes, self.genderCheckBoxes]
                elif self.pos == ("Pronoun", "Article"):
                    checkBoxList = [self.greekCaseCheckBoxes, self.numberCheckBoxes, self.genderCheckBoxes, self.personCheckBoxes]
                elif self.pos == "Verb":
                    checkBoxList = [self.greekTenseCheckBoxes, self.voiceCheckBoxes, self.greekMoodCheckBoxes, self.personCheckBoxes, self.numberCheckBoxes]
                elif self.pos == "Adverb":
                    checkBoxList = [self.greekCaseCheckBoxes, self.numberCheckBoxes, self.genderCheckBoxes]
                else:
                    checkBoxList = []
            else:
                if self.pos in ("Noun", "Adjective", "Preposition", "Pronoun"):
                    checkBoxList = [self.numberCheckBoxes, self.genderCheckBoxes, self.hebrewStateCheckBoxes]
                elif self.pos in ("Verb", "Adverb"):
                    checkBoxList = [self.personCheckBoxes, self.genderCheckBoxes, self.numberCheckBoxes, self.hebrewStateCheckBoxes, self.hebrewPatternCheckBoxes]
                else:
                    checkBoxList = []
            for checkBoxes in checkBoxList:
                for checkbox in checkBoxes:
                    if checkbox.isChecked():
                        morphologyList.append(checkbox.text())
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
    from PySide6 import QtWidgets
    from PySide6.QtWidgets import QWidget
    import sys

    from uniquebible.util.LanguageUtil import LanguageUtil
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    app = QtWidgets.QApplication(sys.argv)
    window = MorphologyLauncher(DummyParent())
    window.show()
    sys.exit(app.exec_())

