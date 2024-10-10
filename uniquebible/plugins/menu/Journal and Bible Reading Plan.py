from uniquebible import config
from uniquebible.util.readings import allDays
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QWidget
else:
    from qtpy.QtWidgets import QWidget


class BibleReadingPlan(QWidget):

    template = allDays

    translation = (
        "365-Day Bible Reading Plan",
        "Today is ",
        "Search: ",
        "Open in Tabs",
        "Hide Checked Items",
        "Show Checked Items",
        "Reset All Items",
        "Save Reading Progress",
        "Day ",
        "",
        "Your reading progress is saved in the following location:",
        "Failed to save your progress locally.  You may need to grant write permission to UBA.",
        "Read Journal",
        "Edit Journal",
        "Search Journal",
        "Create Journal",
        "Jewish: ", #16
        "Date: ", #17
        "Jewish Festival: ", #18
        "Jewish Month: ", #19
        "Journal", #20
        "Refresh", #21
        "Journal and Bible Reading Plan", #22
    )

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(self.translation[22])
        self.setMinimumSize(830, 500)
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()

    def setupVariables(self):
        import copy, os
        from datetime import date
        from uniquebible.db.JournalSqlite import JournalSqlite
        self.today = date.today()
        self.todayNo = int(format(self.today, '%j'))
        if self.todayNo > 365:
            self.todayNo = 365
        self.progressFile = os.path.join(os.getcwd(), "plugins", "menu", "{0}.txt".format(self.translation[0]))
        if os.path.isfile(self.progressFile):
            from ast import literal_eval
            with open(self.progressFile, "r") as fileObj:
                self.plan = literal_eval(fileObj.read())
        else:
            self.plan = copy.deepcopy(self.template)
        self.hideCheckedItems = False
        self.journalSqlite = JournalSqlite()

    def setupUI(self):
        from pyluach import dates
        if config.qtLibrary == "pyside6":
            from PySide6.QtGui import QStandardItemModel
            from PySide6.QtWidgets import QPushButton, QLabel, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QCalendarWidget
        else:
            from qtpy.QtGui import QStandardItemModel
            from qtpy.QtWidgets import QPushButton, QLabel, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QCalendarWidget

        mainLayout0 = QHBoxLayout()

        # Layout on the Left
        mainLayoutLeft = QVBoxLayout()

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.selectionChanged.connect(self.selectionChangedAction)
        mainLayoutLeft.addWidget(self.calendar)

        self.selectedDateLabel = QLabel("")
        mainLayoutLeft.addWidget(self.selectedDateLabel)
        self.jewishMonthlLabel = QLabel("")
        mainLayoutLeft.addWidget(self.jewishMonthlLabel)
        self.jewishFestivalLabel = QLabel("")
        mainLayoutLeft.addWidget(self.jewishFestivalLabel)
        self.updateSelectedDate()

        buttonsLayout = QHBoxLayout()
        readJournal = QPushButton(self.translation[12])
        readJournal.clicked.connect(self.readJournal)
        buttonsLayout.addWidget(readJournal)
        editJournal = QPushButton(self.translation[13])
        editJournal.clicked.connect(self.editJournal)
        buttonsLayout.addWidget(editJournal)
        mainLayoutLeft.addLayout(buttonsLayout)

        self.searchJournalEntry = QLineEdit()
        self.searchJournalEntry.returnPressed.connect(self.searchJournal)
        mainLayoutLeft.addWidget(self.searchJournalEntry)
        searchJournal = QPushButton(self.translation[14])
        searchJournal.clicked.connect(self.searchJournal)
        mainLayoutLeft.addWidget(searchJournal)

        mainLayout0.addLayout(mainLayoutLeft)

        # Layout in the middle
        mainLayoutMiddle = QVBoxLayout()

        mainLayoutMiddle.addWidget(QLabel(self.translation[20]))

        self.journalListView = QListView()
        self.journalListViewModel = QStandardItemModel(self.journalListView)
        self.journalListView.setModel(self.journalListViewModel)
        self.journalListView.selectionModel().selectionChanged.connect(self.journalSelectionChanged)
        mainLayoutMiddle.addWidget(self.journalListView)
        self.calendar.currentPageChanged.connect(self.resetJournalSelection)
        self.resetJournalSelection()

        refreshJournal = QPushButton(self.translation[21])
        refreshJournal.clicked.connect(self.refreshJournalSelection)
        mainLayoutMiddle.addWidget(refreshJournal)

        mainLayout0.addLayout(mainLayoutMiddle)

        # Layout on the Right
        mainLayout = QVBoxLayout()

        readingListLayout = QVBoxLayout()

        readingListLayout.addWidget(QLabel(self.translation[0]))
        hebrewToday = dates.HebrewDate.today()
        todayLabel = QLabel("{0}{1} [{2}{3}-{4}-{5}]".format(self.translation[1], self.today, self.translation[16], hebrewToday.year, hebrewToday.month, hebrewToday.day))
        todayLabel.mouseReleaseEvent = self.selectToday
        readingListLayout.addWidget(todayLabel)

        filterLayout = QHBoxLayout()
        filterLayout.addWidget(QLabel(self.translation[2]))
        self.filterEntry = QLineEdit()
        self.filterEntry.textChanged.connect(self.resetItems)
        filterLayout.addWidget(self.filterEntry)
        readingListLayout.addLayout(filterLayout)

        self.readingList = QListView()
        self.readingList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.readingListModel = QStandardItemModel(self.readingList)
        self.readingList.setModel(self.readingListModel)
        self.resetItems()
        self.readingListModel.itemChanged.connect(self.itemChanged)
        #print(self.readingList.currentIndex().row())
        #self.readingList.selectionModel().selectionChanged.connect(self.function)
        readingListLayout.addWidget(self.readingList)

        buttonsLayout = QHBoxLayout()

        button = QPushButton(self.translation[3])
        button.clicked.connect(self.openInTabs)
        buttonsLayout.addWidget(button)

        self.hideShowButton = QPushButton(self.translation[4])
        self.hideShowButton.clicked.connect(self.hideShowCheckedItems)
        buttonsLayout.addWidget(self.hideShowButton)

        button = QPushButton(self.translation[6])
        button.clicked.connect(self.resetAllItems)
        buttonsLayout.addWidget(button)

        button = QPushButton(self.translation[7])
        button.clicked.connect(self.saveProgress)
        buttonsLayout.addWidget(button)

        mainLayout.addLayout(readingListLayout)
        mainLayout.addLayout(buttonsLayout)

        mainLayout0.addLayout(mainLayout)

        self.setLayout(mainLayout0)

    def updateSelectedDate(self):
        from pyluach import dates, hebrewcal
        # documentation: https://pyluach.readthedocs.io/en/latest/index.html

        date = self.calendar.selectedDate()
        year, month, day = date.year(), date.month(), date.day()
        hebrewDate = dates.GregorianDate(year, month, day).to_heb()
        hebYear, hebMonth, hebDay = hebrewDate.year, hebrewDate.month, hebrewDate.day
        dateLabel = "{7}{0}-{1}-{2} [{6}{3}-{4}-{5}]".format(year, month, day, hebYear, hebMonth, hebDay, self.translation[16], self.translation[17])
        self.selectedDateLabel.setText(dateLabel)
        month = hebrewcal.Month(hebYear, hebMonth)
        hebrewMonthInEnglish = month.month_name()
        hebrewMonth = month.month_name(True)
        hebrewMonthLabel = "{0}{1} {2}".format(self.translation[19], hebrewMonthInEnglish, hebrewMonth)
        self.jewishMonthlLabel.setText(hebrewMonthLabel)
        festivalLabel = "{0}{1} {2}".format(self.translation[18], hebrewDate.festival(), hebrewDate.festival(hebrew=True)) if hebrewDate.festival() else ""
        self.jewishFestivalLabel.setText(festivalLabel)

    def scrollBibleReadingPlan(self):
        date = self.calendar.selectedDate()
        scrollIndex = date.dayOfYear() - 1
        if scrollIndex < 0:
            scrollIndex = 0
        elif scrollIndex > 365:
            scrollIndex = 365
        self.readingList.setCurrentIndex(self.readingListModel.index(scrollIndex, 0))

    def selectionChangedAction(self):
        self.updateSelectedDate()
        self.scrollBibleReadingPlan()

    def historyAction(self, selection, key):
        if not self.parent.isRefreshing:
            selectedItem = selection[0].indexes()[0].data()
            self.openSelectedItem(selectedItem, key)

    def refreshJournalSelection(self):
        self.resetJournalSelection(self.calendar.yearShown(), self.calendar.monthShown())

    def resetJournalSelection(self, year=None, month=None):
        if config.qtLibrary == "pyside6":
            from PySide6.QtGui import QStandardItem
        else:
            from qtpy.QtGui import QStandardItem

        if month is None:
            date = self.calendar.selectedDate()
            year, month = date.year(), date.month()

        self.journalListViewModel.clear()
        self.journalList = self.journalSqlite.getMonthJournalList(year, month)
        for journalTitle in self.journalList:
            journalTitle = [str(number) for number in journalTitle]
            journalTitle = "-".join(journalTitle)
            item = QStandardItem(journalTitle)
            item.setToolTip(journalTitle)
            self.journalListViewModel.appendRow(item)

    def journalSelectionChanged(self, selection):
        if config.qtLibrary == "pyside6":
            from PySide6.QtCore import QDate
        else:
            from qtpy.QtCore import QDate
        
        journalTitle = selection[0].indexes()[0].data()
        year, month, day = journalTitle.split("-")
        year, month, day = int(year), int(month), int(day)
        qDate = QDate(year, month, day)
        self.calendar.setSelectedDate(qDate)

    def selectToday(self, event):
        if config.qtLibrary == "pyside6":
            from PySide6.QtCore import QDate
        else:
            from qtpy.QtCore import QDate

        year, month, day = self.today.year, self.today.month, self.today.day
        qDate = QDate(year, month, day)
        self.calendar.setSelectedDate(qDate)

    def searchJournal(self):
        if config.qtLibrary == "pyside6":
            from PySide6.QtGui import QStandardItem
        else:
            from qtpy.QtGui import QStandardItem

        searchString = self.searchJournalEntry.text().strip()
        self.journalListViewModel.clear()
        self.journalList = self.journalSqlite.getSearchJournalList(searchString)
        for journalTitle in self.journalList:
            journalTitle = [str(number) for number in journalTitle]
            journalTitle = "-".join(journalTitle)
            item = QStandardItem(journalTitle)
            item.setToolTip(journalTitle)
            self.journalListViewModel.appendRow(item)

    def readJournal(self):
        config.mainWindow.textCommandParser.lastKeyword = "journal"
        date = self.calendar.selectedDate()
        year, month, day = date.year(), date.month(), date.day()
        note = self.journalSqlite.getJournalNote(year, month, day)
        note = config.mainWindow.fixNoteFontDisplay(note)
        note = config.mainWindow.htmlWrapper(note, True, "study", False)
        config.mainWindow.openTextOnStudyView(note, tab_title="Jou:{0}-{1}-{2}".format(year, month, day), toolTip="Journal: {0}-{1}-{2}".format(month, year, day))

    def editJournal(self):
        date = self.calendar.selectedDate()
        year, month, day = date.year(), date.month(), date.day()
        config.mainWindow.openNoteEditor("journal", year=year, month=month, day=day)

    def itemChanged(self, standardItem):
        if config.qtLibrary == "pyside6":
            from PySide6.QtCore import Qt
        else:
            from qtpy.QtCore import Qt
        key = int(standardItem.text().split(".")[0])
        if standardItem.checkState() is Qt.CheckState.Checked:
            self.plan[key][0] = True
        elif standardItem.checkState() is Qt.CheckState.Unchecked:
            self.plan[key][0] = False
        if self.hideCheckedItems:
            self.resetItems()

    def resetItems(self):
        if config.qtLibrary == "pyside6":
            from PySide6.QtGui import QStandardItem
            from PySide6.QtCore import Qt
        else:
            from qtpy.QtGui import QStandardItem
            from qtpy.QtCore import Qt
        # Empty the model before reset
        self.readingListModel.clear()
        # Reset
        index = 0
        todayIndex = None
        filterEntry = self.filterEntry.text()
        for key, value in self.plan.items():
            checked, passages = value
            if not (self.hideCheckedItems and checked) and (filterEntry == "" or (filterEntry != "" and filterEntry.lower() in passages.lower())):
                item = QStandardItem("{0}. {1}".format(key, passages))
                item.setToolTip("{0}{1} - {2}".format(self.translation[8], key, passages))
                if key == self.todayNo:
                    todayIndex = index
                item.setCheckable(True)
                item.setCheckState(Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
                self.readingListModel.appendRow(item)
                index += 1
        if todayIndex is not None:
            self.readingList.setCurrentIndex(self.readingListModel.index(todayIndex, 0))

    def hideShowCheckedItems(self):
        self.hideCheckedItems = not self.hideCheckedItems
        self.resetItems()
        self.hideShowButton.setText(self.translation[5] if self.hideCheckedItems else self.translation[4])

    def resetAllItems(self):
        import copy
        self.plan = copy.deepcopy(self.template)
        self.resetItems()

    def translateIntoChinese(self):
        import copy, pprint
        from uniquebible.util.BibleBooks import BibleBooks
        plan = copy.deepcopy(self.template)
        filePath = "{0}_zh".format(self.progressFile)
        with open(filePath, "w", encoding="utf-8") as fileObj:
            fileObj.write(pprint.pformat(plan))
        with open(filePath, "r") as fileObj:
            text = fileObj.read()
        translateDict = {}
        bookNames = []
        for key, value in BibleBooks.abbrev["eng"].items():
            bookName = value[-1]
            bookNames.append(bookName)
            translateDict[bookName] = BibleBooks.abbrev["sc"][key][-1]
        bookNames = sorted(bookNames, key=len, reverse=True)
        #print(bookNames)
        for name in bookNames:
            text = text.replace(name, translateDict[name])
        text = text.replace("Psalm", "诗篇")
        with open(filePath, "w", encoding="utf-8") as fileObj:
            fileObj.write(text)

    def saveProgress(self):
        import pprint
        if config.qtLibrary == "pyside6":
            from PySide6.QtWidgets import QMessageBox
        else:
            from qtpy.QtWidgets import QMessageBox
        try:
            with open(self.progressFile, "w", encoding="utf-8") as fileObj:
                fileObj.write(pprint.pformat(self.plan))
            message = "{0}\n'{1}'".format(self.translation[10], self.progressFile)
        except:
            message = self.translation[11]
        QMessageBox.information(self, self.translation[0], message)

    def openInTabs(self):
        dayNo = self.readingList.currentIndex().row() + 1
        todayReading = self.plan[dayNo][-1].split(", ")
        openBibleWindowContentOnNextTab = config.openBibleWindowContentOnNextTab
        config.openBibleWindowContentOnNextTab = True
        for reading in todayReading:
            command = "MAIN:::{0}".format(reading)
            self.parent.runTextCommand(command)
        config.openBibleWindowContentOnNextTab = openBibleWindowContentOnNextTab
        self.close()

config.mainWindow.bibleReadingPlan = BibleReadingPlan(config.mainWindow)
config.mainWindow.bibleReadingPlan.show()
