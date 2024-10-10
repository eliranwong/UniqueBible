from uniquebible.gui.MenuItems import *
import shortcut as sc
from uniquebible.db.BiblesSqlite import BiblesSqlite
from uniquebible.util.LanguageUtil import LanguageUtil


class Starter:

    def create_menu(self):

        config.instantMode = 0
        config.parallelMode = 1
        config.syncStudyWindowBibleWithMainWindow = True
        config.syncCommentaryWithMainWindow = False
        config.readFormattedBibles = True
        config.topToolBarOnly = True

        menuBar = self.menuBar()
        menu = addMenu(menuBar, "menu1_app")
        subMenu = addSubMenu(menu, "menu1_selectTheme")
        items = (
            ("menu_light_theme", self.setDefaultTheme),
            ("menu1_dark_theme", self.setDarkTheme),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(menu, "menu1_selectMenuLayout")
        addMenuLayoutItems(self, subMenu)
        subMenu = addSubMenu(menu, "languageSettings")
        for language in LanguageUtil.getNamesSupportedLanguages():
            addMenuItem(subMenu, language, self, lambda language=language: self.changeInterfaceLanguage(language), translation=False)
        addIconMenuItem("UniqueBibleApp.png", menu, "menu1_exit", self, self.quitApp, sc.quitApp)

        menu = addMenu(menuBar, "menu_bible")
        items = (
            ("menu_next_book", self.nextMainBook),
            ("menu_previous_book", self.previousMainBook),
            ("menu4_next", self.nextMainChapter),
            ("menu4_previous", self.previousMainChapter),
            ("menu5_search", self.displaySearchBibleCommand),
        )
        for feature, action in items:
            addMenuItem(menu, feature, self, action)
        menu.addSeparator()
        addMenuItem(menu, "add", self, self.installMarvelBibles)

        menu = addMenu(menuBar, "menu9_information")
        addMenuItem(menu, "latestChanges", self, self.showInfo)
        menu.addSeparator()
        addMenuItem(menu, "menu1_update", self, self.showUpdateAppWindow)
        menu.addSeparator()
        items = (
            ("menu1_wikiPages", self.openUbaWiki),
            ("menu_discussions", self.openUbaDiscussions),
            ("report", self.reportAnIssue),
            ("menu9_contact", self.contactEliranWong),
            ("menu9_donate", self.donateToUs)
        )
        for feature, action in items:
            addMenuItem(menu, feature, self, action)

    def setupToolBarStandardIconSize(self):
        Starter.setupToolBar(self)

    def setupToolBarFullIconSize(self):
        Starter.setupToolBar(self)

    def setupToolBar(self):
        self.firstToolBar = QToolBar()
        self.firstToolBar.setWindowTitle(config.thisTranslation["bar1_title"])
        self.firstToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.firstToolBar)

        self.versionCombo = QComboBox()
        self.bibleVersions = BiblesSqlite().getBibleList()
        self.versionCombo.addItems(self.bibleVersions)
        initialIndex = 0
        if config.mainText in self.bibleVersions:
            initialIndex = self.bibleVersions.index(config.mainText)
        self.versionCombo.setCurrentIndex(initialIndex)
        self.versionCombo.currentIndexChanged.connect(self.changeBibleVersion)
        self.firstToolBar.addWidget(self.versionCombo)

        # books = BibleBooks().getStandardBookAbbreviations()
        # self.bibleBookCombo = QComboBox()
        # self.bibleBookCombo.addItems(books)
        # self.bibleBookCombo.setCurrentIndex(config.mainB-1)
        # self.bibleBookCombo.currentIndexChanged.connect(
        #     lambda: self.runTextCommand("BIBLE:::{0}:::{1}".format(config.mainText, "Matt 1:1")))
        # self.firstToolBar.addWidget(self.bibleBookCombo)

        button = QPushButton("<<")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_previous_book", self.previousMainBook, self.firstToolBar, button)
        button = QPushButton("<")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_previous_chapter", self.previousMainChapter, self.firstToolBar, button)
        self.mainRefButton = QPushButton(self.verseReference("main")[-1])
        self.addStandardTextButton("bar1_reference", lambda: self.runTextCommand("_menu:::{0}.{1}".format(config.mainText, config.mainB)),
                                    self.firstToolBar, self.mainRefButton)
        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        if config.qtMaterial and config.qtMaterialTheme:
            mainRefButtonHeight = self.mainRefButton.height() 
            config.iconButtonWidth = config.maximumIconButtonWidth if mainRefButtonHeight > config.maximumIconButtonWidth else mainRefButtonHeight
        button = QPushButton(">")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_next_chapter", self.nextMainChapter, self.firstToolBar, button)
        button = QPushButton(">>")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_next_book", self.nextMainBook, self.firstToolBar, button)

        self.addStandardIconButton("bar1_searchBible", "search.png", self.displaySearchBibleCommand, self.firstToolBar)

        self.firstToolBar.addSeparator()

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.setClearButtonEnabled(True)
        self.textCommandLineEdit.setToolTip(config.thisTranslation["bar1_command"])
        self.textCommandLineEdit.setMinimumWidth(100)
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        self.firstToolBar.addWidget(self.textCommandLineEdit)

        self.studyBibleToolBar = QToolBar()
        self.studyRefButton, self.enableParagraphButton = QPushButton(), QPushButton()
        self.secondToolBar = QToolBar()
        self.leftToolBar = QToolBar()
        self.rightToolBar = QToolBar()
        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))


