import config
import gmplot, os, webbrowser, re
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QWidget
else:
    from qtpy.QtWidgets import QWidget


class BibleLocations(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle("Bible Locations")
        #self.setMinimumSize(830, 500)
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()

    def setupVariables(self):
        from util.exlbl import allLocations
        self.locations = allLocations
        self.locationMap = {exlbl_entry: (name[0].upper(), name, float(latitude), float(longitude)) for exlbl_entry, name, latitude, longitude in self.locations}

    def setupUI(self):
        from gui.CheckableComboBox import CheckableComboBox
        import config

        if config.qtLibrary == "pyside6":
            from PySide6.QtGui import QStandardItemModel
            from PySide6.QtCore import Qt
            from PySide6.QtWidgets import QComboBox, QGroupBox, QPushButton, QLabel, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit
        else:
            from qtpy.QtGui import QStandardItemModel
            from qtpy.QtCore import Qt
            from qtpy.QtWidgets import QComboBox, QGroupBox, QPushButton, QLabel, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit

        self.items = ["{0}. {1}".format(exlbl_entry[2:], name) for exlbl_entry, name, *_ in self.locations]
        itemTooltips = ["{0}. {1} [{2}, {3}]".format(exlbl_entry[2:], name, latitude, longitude) for exlbl_entry, name, latitude, longitude in self.locations]

        layout000 = QVBoxLayout()
        layout001 = QHBoxLayout()
        layout000.addLayout(layout001)
        self.setLayout(layout000)
        
        leftGroupWidget = QGroupBox("Distance")
        layoutLt0 = QVBoxLayout()
        leftGroupWidget.setLayout(layoutLt0)
        layout001.addWidget(leftGroupWidget)

        rightGroupWidget = QGroupBox("Library Links and Google Maps")
        layout0 = QVBoxLayout()
        rightGroupWidget.setLayout(layout0)
        layout001.addWidget(rightGroupWidget)
        lyaout1 = QHBoxLayout()
        layout0.addLayout(lyaout1)
        lyaout2 = QHBoxLayout()
        layout0.addLayout(lyaout2)
        lyaout201 = QHBoxLayout()
        layout0.addLayout(lyaout201)
        layout3 = QHBoxLayout()
        layout0.addLayout(layout3)
        lyaout4 = QHBoxLayout()
        layout0.addLayout(lyaout4)

        wikiButton = QPushButton("Wiki")
        wikiButton.clicked.connect(lambda: webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/Bible-Locations"))
        layout000.addWidget(wikiButton)

        layoutLt0.addWidget(QLabel("between"))
        self.location1 = QComboBox()
        self.location1.addItems(self.items)
        for index, tooltip in enumerate(itemTooltips):
            self.location1.setItemData(index, tooltip, Qt.ToolTipRole)
        self.location1.currentIndexChanged.connect(self.updateLocation)
        layoutLt0.addWidget(self.location1)
        layoutLt0.addWidget(QLabel("and"))
        self.location2 = QComboBox()
        self.location2.addItems(self.items)
        for index, tooltip in enumerate(itemTooltips):
            self.location2.setItemData(index, tooltip, Qt.ToolTipRole)
        self.location2.currentIndexChanged.connect(self.updateLocation)
        layoutLt0.addWidget(self.location2)
        layoutLt0.addWidget(QLabel("is"))
        self.distance = QLabel("0.0 km")
        layoutLt0.addWidget(self.distance)
        layoutLt0.addWidget(QLabel("or"))
        self.distanceInMile = QLabel("0.0 mi")
        layoutLt0.addWidget(self.distanceInMile)

        lyaout1.addWidget(QLabel("Select location(s):"))
        self.locationCombo = CheckableComboBox(self.items, [], itemTooltips)
        lyaout1.addWidget(self.locationCombo)
        clearAllButton = QPushButton("Clear All")
        clearAllButton.clicked.connect(self.locationCombo.clearAll)
        lyaout1.addWidget(clearAllButton)
        selectAllButton = QPushButton("Select All")
        selectAllButton.clicked.connect(self.locationCombo.checkAll)
        lyaout1.addWidget(selectAllButton)

        lyaout2.addWidget(QLabel("Bible Reference:"))
        self.searchEntry = QLineEdit()
        self.searchEntry.setClearButtonEnabled(True)
        self.searchEntry.setText(self.parent.bcvToVerseReference(config.mainB, config.mainC, config.mainV))
        lyaout2.addWidget(self.searchEntry)

        lyaout201.addWidget(QLabel("Added Location(s) in:"))
        bookButton = QPushButton("Book")
        bookButton.clicked.connect(self.addBookLocations)
        lyaout201.addWidget(bookButton)
        chapterButton = QPushButton("Chapter")
        chapterButton.clicked.connect(self.addChapterLocations)
        lyaout201.addWidget(chapterButton)
        verseButton = QPushButton("Verse")
        verseButton.clicked.connect(self.addVerseLocations)
        lyaout201.addWidget(verseButton)
        rangeButton = QPushButton("Range")
        rangeButton.clicked.connect(self.addRangeLocations)
        lyaout201.addWidget(rangeButton)

        layout3.addWidget(QLabel("Search:"))
        self.searchLocationEntry = QLineEdit()
        self.searchLocationEntry.setClearButtonEnabled(True)
        self.searchLocationEntry.textChanged.connect(self.filterLocations)
        layout3.addWidget(self.searchLocationEntry)

        searchLocationsList = QListView()
        searchLocationsList.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.searchLocationsListModel = QStandardItemModel(searchLocationsList)
        searchLocationsList.setModel(self.searchLocationsListModel)
        #self.searchLocationsListModel.itemChanged.connect(self.itemChanged)
        selectedText = config.mainWindow.mainView.currentWidget().selectedText().strip()
        if not selectedText:
            selectedText = config.mainWindow.studyView.currentWidget().selectedText().strip()
        self.searchLocationEntry.setText(selectedText)
        layout3.addWidget(searchLocationsList)

        addSelectedLocationButton = QPushButton("Add Selected Locations")
        addSelectedLocationButton.clicked.connect(self.addSearchedLocations)
        layout3.addWidget(addSelectedLocationButton)

        getLinkButton = QPushButton("Library Links")
        getLinkButton.clicked.connect(self.displayLinks)
        lyaout4.addWidget(getLinkButton)
        lyaout4.addWidget(QLabel("Open Google Map on:"))
        displayMapButton = QPushButton("Study Window")
        displayMapButton.clicked.connect(self.displayMap)
        lyaout4.addWidget(displayMapButton)
        displayMapWebbrowserButton = QPushButton("Web Browser")
        displayMapWebbrowserButton.clicked.connect(lambda: self.displayMap(True))
        lyaout4.addWidget(displayMapWebbrowserButton)

    def updateLocation(self, index):
        from haversine import haversine

        locationIndex1 = self.location1.currentIndex()
        text = self.items[locationIndex1]
        num = int(re.sub("\..*?$", "", text))
        *_, lat, long = self.locationMap["BL{0}".format(num)]
        location1 = (lat, long)

        locationIndex2 = self.location2.currentIndex()
        text = self.items[locationIndex2]
        num = int(re.sub("\..*?$", "", text))
        *_, lat, long = self.locationMap["BL{0}".format(num)]
        location2 = (lat, long)

        self.distance.setText("{0} km".format(haversine(location1, location2)))
        self.distanceInMile.setText("{0} mi".format(haversine(location1, location2, unit='mi')))

    def filterLocations(self):
        if config.qtLibrary == "pyside6":
            from PySide6.QtGui import QStandardItem
        else:
            from qtpy.QtGui import QStandardItem

        self.searchLocationsListModel.clear()
        searchString = self.searchLocationEntry.text().strip()
        if searchString:
            for location in self.items:
                if searchString.lower() in location.lower():
                    item = QStandardItem(location)
                    item.setToolTip(location)
                    item.setCheckable(True)
                    #item.setCheckState(Qt.CheckState.Unchecked)
                    #item.setCheckState(Qt.CheckState.Checked)
                    self.searchLocationsListModel.appendRow(item)

    def addSearchedLocations(self):
        if config.qtLibrary == "pyside6":
            from PySide6.QtCore import Qt
        else:
            from qtpy.QtCore import Qt

        locations = []
        for row in range(0, self.searchLocationsListModel.rowCount()):
            standardItem = self.searchLocationsListModel.item(row)
            if standardItem.checkState() is Qt.CheckState.Checked:
                text = standardItem.text()
                num = int(re.sub("\..*?$", "", text))
                locations.append(("exlbl('BL{0}')".format(num),))
        self.selectLocations(locations)

    def selectLocations(self, locations):
        checkList = []
        for location in locations:
            # e.g. <p><ref onclick="exlbl('BL1163')">Hiddekel</ref> ... <ref onclick="exlbl('BL421')">Euphrates</ref></p>
            searchPattern = "exlbl\('BL([0-9]+?)'\)"
            found = re.findall(searchPattern, location[0])
            if found:
                for entry in found:
                    checkList.append(entry)
        checkList = [int(item) for item in checkList]
        checkList = list(set(checkList))
        #checkList.sort()

        formattedList = []
        for num in checkList:
            exlbl_entry = "BL{0}".format(num)
            if exlbl_entry in self.locationMap:
                formattedList.append("{0}. {1}".format(num, self.locationMap[exlbl_entry][1]))

        # Add the currently selected list
        formattedList += self.locationCombo.checkItems
        formattedList = list(set(formattedList))

        self.locationCombo.checkFromList(formattedList)

    def getReference(self):
        from util.BibleVerseParser import BibleVerseParser
        reference = self.searchEntry.text().strip()
        verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(reference, False)
        return verses[0] if verses else []

    def addBookLocations(self):
        reference = self.getReference()
        if reference:
            from db.ToolsSqlite import IndexesSqlite
            indexesSqlite = IndexesSqlite()
            locations = indexesSqlite.getBookLocations(reference[0])
            self.selectLocations(locations)

    def addChapterLocations(self):
        reference = self.getReference()
        if reference:
            from db.ToolsSqlite import IndexesSqlite
            indexesSqlite = IndexesSqlite()
            b, c, *_ = reference
            locations = indexesSqlite.getChapterLocations(b, c)
            self.selectLocations(locations)

    def addVerseLocations(self):
        reference = self.getReference()
        if reference:
            from db.ToolsSqlite import IndexesSqlite
            indexesSqlite = IndexesSqlite()
            b, c, v, *_ = reference
            locations = indexesSqlite.getVerseLocations(b, c, v)
            self.selectLocations(locations)

    def addRangeLocations(self):
        combinedLocations = []
        reference = self.getReference()
        if reference and len(reference) == 5:
            from db.ToolsSqlite import IndexesSqlite
            indexesSqlite = IndexesSqlite()
            b, c, v, ce, ve = reference
            if c == ce:
                if v == ve:
                    combinedLocations += indexesSqlite.getVerseLocations(b, c, v)
                elif ve > v:
                    combinedLocations += indexesSqlite.getChapterLocations(b, c, startV=v, endV=ve)
            elif ce > c:
                combinedLocations += indexesSqlite.getChapterLocations(b, c, startV=v)
                combinedLocations += indexesSqlite.getChapterLocations(b, ce, endV=ve)
                if (ce - c) > 1:
                    for i in range(c+1, ce):
                        combinedLocations += indexesSqlite.getChapterLocations(b, i)
            self.selectLocations(combinedLocations)

    def displayLinks(self):
        linkList = []
        selectedLocations = self.locationCombo.checkItems
        if selectedLocations:
            for item in selectedLocations:
                try:
                    num = int(re.sub("\..*?$", "", item))
                    exlbl_entry = "BL{0}".format(num)
                    label, name, *_ = self.locationMap[exlbl_entry]
                    link = """<ref onclick="exlbl('{0}')">{1} - {2}</ref>""".format(exlbl_entry, label, name)
                    linkList.append(link)
                except:
                    pass
        else:
            linkList.append("""<ref onclick="exlbl('{0}')">{1} - {2}</ref>""".format("BL636", "J", "Jerusalem"))
        html = "<p>{0}</p>".format("<br>".join(linkList))
        if config.openStudyWindowContentOnNextTab:
            config.mainWindow.nextStudyWindowTab()
        html = config.mainWindow.htmlWrapper(html, False, "study", False, False)
        config.mainWindow.openTextOnStudyView(html, tab_title="Bible Locations", toolTip="Bible Locations")

    def displayMap(self, browser=False):
        if config.qtLibrary == "pyside6":
            from PySide6.QtCore import QUrl
        else:
            from qtpy.QtCore import QUrl

        gmap = gmplot.GoogleMapPlotter(33.877444, 34.234935, 6, map_type='hybrid')
        if config.myGoogleApiKey:
            gmap.apikey = config.myGoogleApiKey

        selectedLocations = self.locationCombo.checkItems
        if selectedLocations:
            for item in selectedLocations:
                try:
                    num = int(re.sub("\..*?$", "", item))
                    exlbl_entry = "BL{0}".format(num)
                    label, name, latitude, longitude = self.locationMap[exlbl_entry]
                    if browser:
                        info = "<a href='https://marvel.bible/tool.php?exlbl={0}' target='_blank'>{1}</a>".format(exlbl_entry, name)
                    else:
                        info = """<ref onclick="document.title = 'EXLB:::exlbl:::{0}';">{1}</ref>""".format(exlbl_entry, name)
                    gmap.marker(latitude, longitude, label=label, title=name, info_window=info)
                except:
                    pass
        else:
            if browser:
                info = "<a href='https://marvel.bible/tool.php?exlbl=BL636' target='_blank'>Jerusalem</a>"
            else:
                info = """<ref onclick="document.title = 'EXLB:::exlbl:::BL636';">Jerusalem</ref>"""
            gmap.marker(31.777444, 35.234935, label="J", title="Jerusalem", info_window=info)

        # HTML file
        mapHtml = os.path.join("htmlResources", "bible_map.html")
        gmap.draw(mapHtml)
        fullFilePath = os.path.abspath(mapHtml)
        if browser:
            webbrowser.open("file://{0}".format(fullFilePath))
        else:
            if config.openStudyWindowContentOnNextTab:
                config.mainWindow.nextStudyWindowTab()
            config.mainWindow.studyView.load(QUrl.fromLocalFile(fullFilePath))

        # HTML text
        #html = gmap.get()
        #config.mainWindow.openTextOnStudyView(html, tab_title="Bible Map", toolTip="Bible Map")
        #config.mainWindow.studyView.setHtml(html, config.baseUrl)

config.mainWindow.bibleLocations = BibleLocations(config.mainWindow)
config.mainWindow.bibleLocations.show()
#config.mainWindow.bibleLocations.locationCombo.clearAll()
#config.mainWindow.bibleLocations.locationCombo.checkAll()
#config.mainWindow.bibleLocations.displayMap()
