from uniquebible import config
import gmplot, os, webbrowser, re
from uniquebible.util.exlbl import allLocations
from uniquebible.gui.CheckableComboBox import CheckableComboBox
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.db.ToolsSqlite import IndexesSqlite
from haversine import haversine

if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtCore import Qt, QUrl
    from PySide6.QtWidgets import QSplitter, QWidget, QComboBox, QGroupBox, QPushButton, QLabel, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit
else:
    from qtpy.QtGui import QStandardItemModel, QStandardItem
    from qtpy.QtCore import Qt, QUrl
    from qtpy.QtWidgets import QSplitter, QWidget, QComboBox, QGroupBox, QPushButton, QLabel, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit


class BibleLocations(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["menu5_locations"])
        #self.setMinimumSize(830, 500)
        # get text selection
        selectedText = config.mainWindow.selectedText(config.pluginContext == "study")
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI(selectedText)

    def setupVariables(self):
        self.locations = allLocations
        self.locationMap = {exlbl_entry: (name[0].upper(), name, float(latitude), float(longitude)) for exlbl_entry, name, latitude, longitude in self.locations}

    def setupUI(self, selectedText):
        self.items = ["{0}. {1}".format(exlbl_entry[2:], name) for exlbl_entry, name, *_ in self.locations]
        itemTooltips = ["{0}. {1} [{2}, {3}]".format(exlbl_entry[2:], name, latitude, longitude) for exlbl_entry, name, latitude, longitude in self.locations]

        widgetTop = QWidget()
        layout001 = QHBoxLayout()
        layout001Lt = QVBoxLayout()
        layout001.addLayout(layout001Lt)
        widgetTop.setLayout(layout001)

        layout0000 = QHBoxLayout()
        splitter = QSplitter(Qt.Vertical, self)
        splitter.addWidget(widgetTop)
        self.contentView = WebEngineViewPopover(config.mainWindow, "main", "main", windowTitle=config.thisTranslation["menu5_locations"], enableCloseAction=False)
        html = config.mainWindow.wrapHtml("<h2>{0}</h2>".format(config.thisTranslation["menu5_locations"]))
        self.contentView.setHtml(html, config.baseUrl)
        splitter.addWidget(self.contentView)
        layout0000.addWidget(splitter)
        self.setLayout(layout0000)

        leftGroupWidget = QGroupBox("Distance")
        layoutLt0 = QVBoxLayout()
        leftGroupWidget.setLayout(layoutLt0)
        layout001Lt.addWidget(leftGroupWidget)

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
        layout001Lt.addWidget(wikiButton)

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
        self.searchLocationEntry.setText(selectedText)
        layout3.addWidget(searchLocationsList)

        addSelectedLocationButton = QPushButton("Add Selected Locations")
        addSelectedLocationButton.clicked.connect(self.addSearchedLocations)
        layout3.addWidget(addSelectedLocationButton)

        getLinkButton = QPushButton("Library Links")
        getLinkButton.clicked.connect(self.displayLinks)
        lyaout4.addWidget(getLinkButton)
        lyaout4.addStretch()
        lyaout4.addWidget(QLabel("Google Map:"))
        displayMapButton = QPushButton("HERE")
        displayMapButton.clicked.connect(self.displayMap)
        lyaout4.addWidget(displayMapButton)
        displayMapOnStudyWindowButton = QPushButton("Study Window")
        displayMapOnStudyWindowButton.clicked.connect(lambda: self.displayMap(displayOnStudyWindow=True))
        lyaout4.addWidget(displayMapOnStudyWindowButton)
        displayMapWebbrowserButton = QPushButton("Web Browser")
        displayMapWebbrowserButton.clicked.connect(lambda: self.displayMap(browser=True))
        lyaout4.addWidget(displayMapWebbrowserButton)

    def updateLocation(self, index):
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
        reference = self.searchEntry.text().strip()
        verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(reference, False)
        return verses[0] if verses else []

    def addBookLocations(self):
        reference = self.getReference()
        if reference:
            indexesSqlite = IndexesSqlite()
            locations = indexesSqlite.getBookLocations(reference[0])
            self.selectLocations(locations)

    def addChapterLocations(self):
        reference = self.getReference()
        if reference:
            indexesSqlite = IndexesSqlite()
            b, c, *_ = reference
            locations = indexesSqlite.getChapterLocations(b, c)
            self.selectLocations(locations)

    def addVerseLocations(self):
        reference = self.getReference()
        if reference:
            indexesSqlite = IndexesSqlite()
            b, c, v, *_ = reference
            locations = indexesSqlite.getVerseLocations(b, c, v)
            self.selectLocations(locations)

    def addRangeLocations(self):
        combinedLocations = []
        reference = self.getReference()
        if reference and len(reference) == 5:
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
        #if config.openStudyWindowContentOnNextTab:
            #config.mainWindow.nextStudyWindowTab()
        html = config.mainWindow.htmlWrapper(html, False, "study", False, False)
        self.contentView.setHtml(html, config.baseUrl)
        #config.mainWindow.openTextOnStudyView(html, tab_title="Bible Locations", toolTip="Bible Locations")

    def displayMap(self, browser=False, displayOnStudyWindow=False):
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
                    googleEarthLink = "https://earth.google.com/web/search/{0},+{1}".format(str(latitude).replace(".", "%2e"), str(longitude).replace(".", "%2e"))
                    if browser:
                        info = "<a href='https://marvel.bible/tool.php?exlbl={0}' target='_blank'>{1}</a> [<a href='{2}' target='_blank'>3D</a>]".format(exlbl_entry, name, googleEarthLink)
                    else:
                        info = """<a href="#" onclick="document.title = 'EXLB:::exlbl:::{0}';">{1}</a> [<a href="#" onclick="document.title = 'online:::{2}';">3D</a>]""".format(exlbl_entry, name, googleEarthLink)
                    gmap.marker(latitude, longitude, label=label, title=name, info_window=info)
                except:
                    pass
        else:
            googleEarthLink = r"https://earth.google.com/web/search/31%2e777444,+35%2e234935"
            if browser:
                info = "<a href='https://marvel.bible/tool.php?exlbl=BL636' target='_blank'>Jerusalem</a> [<a href='{0}' target='_blank'>3D</a>]".format(googleEarthLink)
            else:
                info = """<a href="#" onclick="document.title = 'EXLB:::exlbl:::BL636';">Jerusalem</a> [<a href="#" onclick="document.title = 'online:::{0}';">3D</a>]""".format(googleEarthLink)
            gmap.marker(31.777444, 35.234935, label="J", title="Jerusalem", info_window=info)

        # HTML file
        mapHtml = os.path.join("htmlResources", "bible_map.html")
        gmap.draw(mapHtml)
        fullFilePath = os.path.abspath(mapHtml)
        if browser:
            webbrowser.open("file://{0}".format(fullFilePath))
        elif displayOnStudyWindow:
            if config.openStudyWindowContentOnNextTab:
                config.mainWindow.nextStudyWindowTab()
            config.mainWindow.studyView.load(QUrl.fromLocalFile(fullFilePath))
            config.mainWindow.studyView.setTabText(config.mainWindow.studyView.currentIndex(), "Map")
            config.mainWindow.studyView.setTabToolTip(config.mainWindow.studyView.currentIndex(), "Google Map")
        else:
            self.contentView.load(QUrl.fromLocalFile(fullFilePath))

        # HTML text
        #html = gmap.get()
        #config.mainWindow.openTextOnStudyView(html, tab_title="Bible Map", toolTip="Bible Map")
        #config.mainWindow.studyView.setHtml(html, config.baseUrl)

databaseFile = os.path.join(config.marvelData, "data", "exlb3.data")
if os.path.isfile(databaseFile):
    config.mainWindow.bibleLocations = BibleLocations(config.mainWindow)
    config.mainWindow.bibleLocations.show()
    #config.mainWindow.bibleLocations.locationCombo.clearAll()
    #config.mainWindow.bibleLocations.locationCombo.checkAll()
    #config.mainWindow.bibleLocations.displayMap()
else:
    databaseInfo = ((config.marvelData, "data", "exlb3.data"), "1gp2Unsab85Se-IB_tmvVZQ3JKGvXLyMP")
    config.mainWindow.downloadHelper(databaseInfo)

