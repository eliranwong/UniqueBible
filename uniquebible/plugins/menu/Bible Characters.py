from uniquebible import config
import os, apsw, re, webbrowser
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
from uniquebible.db.ToolsSqlite import ExlbData
from uniquebible.db.BiblesSqlite import BiblesSqlite
from uniquebible.util.BibleVerseParser import BibleVerseParser
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import QWidget, QTextEdit, QRadioButton, QPushButton, QLabel, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit
else:
    from qtpy.QtGui import QStandardItemModel, QStandardItem
    from qtpy.QtWidgets import QWidget, QTextEdit, QRadioButton, QPushButton, QLabel, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit


class BiblePeople(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["menu5_characters"])
        #self.setMinimumSize(830, 500)
        # get text selection
        selectedText = config.mainWindow.selectedText(config.pluginContext == "study")
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI(selectedText)

    def setupVariables(self):
        # place holders
        self.selectedPersonID = None
        self.verseReference = None
        self.verseReferenceList = []
        self.verses = None
        self.searchByReference = True
        self.searchMode = 2
        # Connect database
        self.database = os.path.join(config.marvelData, "data", "biblePeople.data")
        self.connection = apsw.Connection(self.database)
        self.cursor = self.connection.cursor()
        # Get all people list
        query = "SELECT PersonID, Name, Sex FROM PEOPLERELATIONSHIP WHERE Relationship=? ORDER BY PersonID"
        self.cursor.execute(query, ("[Reference]",))
        self.people = self.cursor.fetchall()
        # Male icon
        textColor = config.darkThemeTextColor if config.theme in ("dark", "night") else config.lightThemeTextColor
        iconFilePath = os.path.join("htmlResources", "material", "social", "male", "materialiconsoutlined", "48dp", "2x", "outline_male_black_48dp.png")
        self.maleIcon = config.mainWindow.getMaskedQIcon(iconFilePath, textColor, config.maskMaterialIconBackground, True)
        iconFilePath = os.path.join("htmlResources", "material", "social", "female", "materialiconsoutlined", "48dp", "2x", "outline_female_black_48dp.png")
        self.femaleIcon = config.mainWindow.getMaskedQIcon(iconFilePath, textColor, config.maskMaterialIconBackground, True)

    def setupUI(self, selectedText):
        layout000 = QHBoxLayout()
        self.setLayout(layout000)
        layout00h = QHBoxLayout()
        layout00v = QVBoxLayout()
        layout00v.addLayout(layout00h)
        layout0 = QVBoxLayout()
        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QVBoxLayout()
        layout4 = QVBoxLayout()
        layout00h.addLayout(layout0)
        layout00h.addLayout(layout1)
        layout00h.addLayout(layout2)
        layout000.addLayout(layout00v)
        layout000.addLayout(layout3)
        layout000.addLayout(layout4)

        wikiButton = QPushButton("Wiki")
        wikiButton.clicked.connect(lambda: webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/Bible-Characters"))
        layout00v.addWidget(wikiButton)

        label = QLabel("Reference:")
        self.searchEntry0 = QLineEdit()
        self.searchEntry0.setClearButtonEnabled(True)
        self.searchEntry0.textChanged.connect(self.filterPeople0)
        scope = QLabel("Scope:")
        radioButton0 = QRadioButton("Book")
        radioButton0.setToolTip("Search for names contained in the book specified in the entered reference.")
        radioButton0.toggled.connect(lambda checked: self.searchModeChanged(checked, 0))
        radioButton1 = QRadioButton("Chapter")
        radioButton1.setToolTip("Search for names contained in the chapter specified in the entered reference.")
        radioButton1.toggled.connect(lambda checked: self.searchModeChanged(checked, 1))
        radioButton2 = QRadioButton("Verse")
        radioButton2.setToolTip("Search for names contained in the verse specified in the entered reference.")
        radioButton2.setChecked(True)
        radioButton2.toggled.connect(lambda checked: self.searchModeChanged(checked, 2))
        peopleView0 = QListView()
        peopleView0.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.peopleView0Model = QStandardItemModel(peopleView0)
        peopleView0.setModel(self.peopleView0Model)
        self.searchEntry0.setText(self.parent.bcvToVerseReference(config.mainB, config.mainC, config.mainV))
        peopleView0.selectionModel().selectionChanged.connect(self.peopleSelected0)
        layout0.addWidget(label)
        layout0.addWidget(self.searchEntry0)
        layout0.addWidget(scope)
        layout0.addWidget(radioButton0)
        layout0.addWidget(radioButton1)
        layout0.addWidget(radioButton2)
        layout0.addWidget(peopleView0)

        label = QLabel("Name:")
        self.searchEntry = QLineEdit()
        self.searchEntry.setClearButtonEnabled(True)
        self.searchEntry.setText(selectedText)
        self.searchEntry.textChanged.connect(self.filterPeople)
        peopleView = QListView()
        peopleView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.peopleViewModel = QStandardItemModel(peopleView)
        peopleView.setModel(self.peopleViewModel)
        self.filterPeople()
        peopleView.selectionModel().selectionChanged.connect(self.peopleSelected)
        layout1.addWidget(label)
        layout1.addWidget(self.searchEntry)
        layout1.addWidget(peopleView)

        self.reference = QLabel("Relative(s)")
        relatedPeopleView = QListView()
        relatedPeopleView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.relatedPeopleViewModel = QStandardItemModel(relatedPeopleView)
        relatedPeopleView.setModel(self.relatedPeopleViewModel)
        relatedPeopleView.selectionModel().selectionChanged.connect(self.relatedPeopleSelected)
        layout2.addWidget(self.reference)
        layout2.addWidget(relatedPeopleView)

        self.hits = QLabel("Verse(s)")
        scriptureView = QListView()
        #self.scriptureView.setWordWrap(True)
        #self.scriptureView.setWrapping(True)
        scriptureView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.scriptureViewModel = QStandardItemModel(scriptureView)
        scriptureView.setModel(self.scriptureViewModel)
        scriptureView.selectionModel().selectionChanged.connect(self.verseSelected)
        self.verseDisplay = QTextEdit()
        self.verseDisplay.setReadOnly(True)
        openVerseButton = QPushButton("Open")
        openVerseButton.clicked.connect(self.openVerseButtonClicked)
        openAllVerseButton = QPushButton("Open All")
        openAllVerseButton.clicked.connect(self.openAllVerseButtonClicked)
        layout3.addWidget(self.hits)
        layout3.addWidget(scriptureView)
        layout3.addWidget(self.verseDisplay)
        layout3.addWidget(openVerseButton)
        layout3.addWidget(openAllVerseButton)

        self.exlbp = WebEngineViewPopover(config.mainWindow, "main", "main", windowTitle=config.thisTranslation["menu5_characters"], enableCloseAction=False)
        html = config.mainWindow.wrapHtml("<h2>Exhaustive Library</h2>")
        self.exlbp.setHtml(html, config.baseUrl)
        displayOnStudyWindowButton = QPushButton("Display on Study Window")
        displayOnStudyWindowButton.clicked.connect(self.openLibraryContentOnStudyWindow)
        layout4.addWidget(self.exlbp)
        layout4.addWidget(displayOnStudyWindowButton)

    def searchModeChanged(self, checked, mode):
        if checked:
            self.searchMode = mode
        self.filterPeople0()

    def peopleSelected0(self, selection):
        try:
            index = selection[0].indexes()[0].row()
            toolTip = self.peopleView0Model.item(index).toolTip()
            personID = int(re.sub("^.*?\[([0-9]+?)\]", r"\1", toolTip))
            query = "SELECT PersonID, Name, Sex, Relationship FROM PEOPLERELATIONSHIP WHERE RelatedPersonID=? ORDER BY RelationshipOrder"
            self.cursor.execute(query, (personID,))
            self.relatedPeople = self.cursor.fetchall()
            self.relatedPeopleViewModel.clear()
            self.updateSelection(personID)
        except:
            pass

    def peopleSelected(self, selection):
        try:
            index = selection[0].indexes()[0].row()
            toolTip = self.peopleViewModel.item(index).toolTip()
            personID = int(re.sub("^.*?\[([0-9]+?)\]", r"\1", toolTip))
            query = "SELECT PersonID, Name, Sex, Relationship FROM PEOPLERELATIONSHIP WHERE RelatedPersonID=? ORDER BY RelationshipOrder"
            self.cursor.execute(query, (personID,))
            self.relatedPeople = self.cursor.fetchall()
            self.relatedPeopleViewModel.clear()
            self.updateSelection(personID)
        except:
            pass

    def relatedPeopleSelected(self, selection):
        try:
            index = selection[0].indexes()[0].row()
            toolTip = self.relatedPeopleViewModel.item(index).toolTip()
            personID = int(re.sub("^.*?\[([0-9]+?)\]", r"\1", toolTip))
            query = "SELECT PersonID, Name, Sex, Relationship FROM PEOPLERELATIONSHIP WHERE RelatedPersonID=? ORDER BY RelationshipOrder"
            self.cursor.execute(query, (personID,))
            self.relatedPeople = self.cursor.fetchall()
            rowCount = self.relatedPeopleViewModel.rowCount()
            self.relatedPeopleViewModel.removeRows(0, rowCount)
            self.updateSelection(personID)
        except:
            pass

    def openVerseButtonClicked(self):
        if self.verseReference is not None:
            config.mainWindow.textCommandLineEdit.setText(self.verseReference)
            config.mainWindow.runTextCommand(self.verseReference)

    def openAllVerseButtonClicked(self):
        if self.verses:
            cmd = "; ".join(self.verseReferenceList)
            config.mainWindow.textCommandLineEdit.setText(cmd)
            config.mainWindow.runTextCommand(cmd)

    def openLibraryContentOnStudyWindow(self):
        if self.selectedPersonID is not None:
            config.mainWindow.runTextCommand("EXLB:::exlbp:::BP{0}".format(self.selectedPersonID))

    def updateSelection(self, personID):
        for relatedPersonID, name, sex, relationship in self.relatedPeople:
            if relationship == "[Reference]":
                self.reference.setText("{0}'{1} relative(s)".format(name, "" if name[-1] == "s" else "s"))
            else:
                item = QStandardItem("{0} ({1})".format(name, relationship))
                item.setToolTip("{2} - {1} [{0}]".format(relatedPersonID, name, sex))
                item.setIcon(self.femaleIcon if sex == "F" else self.maleIcon)
                self.relatedPeopleViewModel.appendRow(item)
        self.displayVerseList(personID)
        self.openLibraryContent(personID)

    def displayVerseList(self, personID):
        try:
            query = "SELECT Book, Chapter, Verse FROM PEOPLE WHERE PersonID=? ORDER BY Number"
            self.cursor.execute(query, (personID,))
            self.verses = self.cursor.fetchall()
            self.hits.setText("{0} verse(s)".format(len(self.verses)))
            self.scriptureViewModel.clear()
            self.verseReferenceList = []
            parser = BibleVerseParser(config.parserStandarisation)
            for b, c, v in self.verses:
                verseReference = parser.bcvToVerseReference(b, c, v)
                self.verseReferenceList.append(verseReference)
                item = QStandardItem(verseReference)
                item.setToolTip(verseReference)
                self.scriptureViewModel.appendRow(item)
        except:
            pass

    def verseSelected(self, selection):
        try:
            if self.verses is not None:
                index = selection[0].indexes()[0].row()
                self.verseReference = self.scriptureViewModel.item(index).text()
                b, c, v = self.verses[index]
                scripture = BiblesSqlite().readTextVerse(config.mainText, b, c, v)[-1]
                scripture = re.sub("&nbsp;|<br>", " ", scripture)
                scripture = re.sub("<[^<>]*?>|audiotrack", "", scripture)
                self.verseDisplay.setPlainText("[{0}] {1}".format(self.verseReference, scripture))
        except:
            pass

    def openLibraryContent(self, personID):
        exlbData = ExlbData()
        content = exlbData.getContent("exlbp", "BP{0}".format(personID))
        if config.theme in ("dark", "night"):
            content = config.mainWindow.textCommandParser.adjustDarkThemeColorsForExl(content)
        content = config.mainWindow.wrapHtml(content)
        self.exlbp.setHtml(content, config.baseUrl)
        self.selectedPersonID = personID

    def filterPeople0(self):
        self.peopleView0Model.clear()
        searchString = self.searchEntry0.text().strip()
        verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(searchString, False)
        if verses:
            b, c, v, *_ = verses[0]
            if self.searchMode == 0:
                query = "SELECT DISTINCT PersonID, Name, Sex FROM PEOPLE WHERE Book=? ORDER BY Book, Chapter, Verse"
                self.cursor.execute(query, (b,))
            elif self.searchMode == 1:
                query = "SELECT DISTINCT PersonID, Name, Sex FROM PEOPLE WHERE Book=? AND Chapter=? ORDER BY Book, Chapter, Verse"
                self.cursor.execute(query, (b, c))
            elif self.searchMode == 2:
                query = "SELECT DISTINCT PersonID, Name, Sex FROM PEOPLE WHERE Book=? AND Chapter=? AND Verse=? ORDER BY Book, Chapter, Verse"
                self.cursor.execute(query, (b, c, v))
            results = self.cursor.fetchall()
            for personID, name, sex in results:
                item = QStandardItem(name)
                item.setToolTip("{2} - {1} [{0}]".format(personID, name, sex))
                item.setIcon(self.femaleIcon if sex == "F" else self.maleIcon)
                #item.setCheckable(True)
                #item.setCheckState(Qt.CheckState.Unchecked)
                #item.setCheckState(Qt.CheckState.Checked)
                self.peopleView0Model.appendRow(item)

    def filterPeople(self):
        self.peopleViewModel.clear()
        searchString = self.searchEntry.text().strip()
        for personID, name, sex in self.people:
            if searchString.lower() in name.lower():
                item = QStandardItem(name)
                item.setToolTip("{2} - {1} [{0}]".format(personID, name, sex))
                item.setIcon(self.femaleIcon if sex == "F" else self.maleIcon)
                #item.setCheckable(True)
                #item.setCheckState(Qt.CheckState.Unchecked)
                #item.setCheckState(Qt.CheckState.Checked)
                self.peopleViewModel.appendRow(item)


databaseFile = os.path.join(config.marvelData, "data", "exlb3.data")
if os.path.isfile(databaseFile):
    config.mainWindow.biblePeople = BiblePeople(config.mainWindow)
    config.mainWindow.biblePeople.show()
else:
    databaseInfo = ((config.marvelData, "data", "exlb3.data"), "1gp2Unsab85Se-IB_tmvVZQ3JKGvXLyMP")
    config.mainWindow.downloadHelper(databaseInfo)
