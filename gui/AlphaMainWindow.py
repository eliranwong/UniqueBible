import os, config, myTranslation
from PySide2.QtCore import QSize
from PySide2.QtGui import QIcon, Qt
from PySide2.QtWidgets import (QAction, QToolBar, QPushButton, QLineEdit, QStyleFactory)
from gui.MenuItems import *
from gui.MainWindow import MainWindow

class AlphaMainWindow(MainWindow):

    def __init__(self):
        super().__init__()

    def create_menu(self):
        menuBar = self.menuBar()
        # 1st column
        menu = addMenu(menuBar, "menu1_app")
        items = (
            ("menu7_create", self.createNewNoteFile, "Ctrl+N"),
            ("menu7_open", self.openTextFileDialog, "Ctrl+O"),
        )
        for feature, action, shortcut in items:
            addMenuItem(menu, feature, self, action, shortcut)
        menu.addSeparator()
        subMenu0 = addSubMenu(menu, "menu1_preferences")
        subMenu = addSubMenu(subMenu0, "menu1_generalPreferences")
        items = (
            ("menu1_tabNo", self.setTabNumberDialog),
            ("menu1_setAbbreviations", self.setBibleAbbreviations),
            ("menu1_setMyFavouriteBible", self.openFavouriteBibleDialog),
            ("menu1_setMyLanguage", self.openMyLanguageDialog),
            ("menu1_setDefaultStrongsHebrewLexicon", self.openSelectDefaultStrongsHebrewLexiconDialog),
            ("menu1_setDefaultStrongsGreekLexicon", self.openSelectDefaultStrongsGreekLexiconDialog),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(subMenu0, "menu1_selectWindowStyle")
        addMenuItem(subMenu, "default", self, lambda: self.setAppWindowStyle("default"), None, False)
        for style in QStyleFactory.keys():
            addMenuItem(subMenu, style, self, lambda style=style: self.setAppWindowStyle(style), None, False)
        subMenu = addSubMenu(subMenu0, "menu1_selectTheme")
        if config.qtMaterial:
            qtMaterialThemes = ["light_amber.xml",  "light_blue.xml",  "light_cyan.xml",  "light_cyan_500.xml",  "light_lightgreen.xml",  "light_pink.xml",  "light_purple.xml",  "light_red.xml",  "light_teal.xml",  "light_yellow.xml", "dark_amber.xml",  "dark_blue.xml",  "dark_cyan.xml",  "dark_lightgreen.xml",  "dark_pink.xml",  "dark_purple.xml",  "dark_red.xml",  "dark_teal.xml",  "dark_yellow.xml"]
            for theme in qtMaterialThemes:
                addMenuItem(subMenu, theme[:-4], self, lambda theme=theme: self.setQtMaterialTheme(theme), None, False)
        else:
            items = (
                ("menu_light_theme", self.setDefaultTheme),
                ("menu1_dark_theme", self.setDarkTheme),
            )
            for feature, action in items:
                addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(subMenu0, "menu1_selectMenuLayout")
        items = (
            ("menu1_alpha_menu_layout", lambda: self.setMenuLayout("alpha")),
            ("menu1_aleph_menu_layout", lambda: self.setMenuLayout("aleph")),
            ("menu1_classic_menu_layout", lambda: self.setMenuLayout("classic")),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(subMenu0, "toolbarIcon")
        items = (
            ("toolbarIconStandard", lambda: self.setFullIconSize(False)),
            ("toolbarIconFull", lambda: self.setFullIconSize(True)),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(subMenu0, "menu2_fonts")
        items = (
            ("menu1_setDefaultFont", self.setDefaultFont),
            ("menu1_setChineseFont", self.setChineseFont),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(subMenu0, "menu2_fontSize")
        items = (
            ("menu2_larger", self.largerFont, "Ctrl++"),
            ("menu2_smaller", self.smallerFont, "Ctrl+-"),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        subMenu = addSubMenu(subMenu0, "menu1_programInterface")
        if (not self.isMyTranslationAvailable() and not self.isOfficialTranslationAvailable()) or (self.isMyTranslationAvailable() and not myTranslation.translationLanguage == config.userLanguage) or (self.isOfficialTranslationAvailable() and not config.translationLanguage == config.userLanguage):
            addMenuItem(subMenu, "menu1_translateInterface", self, self.translateInterface)
        addMenuItem(subMenu, "menu1_toogleInterface", self, self.toogleInterfaceTranslation)

        subMenu0 = addSubMenu(menu, "menu2_view")
        subMenu = addSubMenu(subMenu0, "menu1_screenSize")
        items = (
            ("menu1_fullScreen", self.fullsizeWindow, "Ctrl+S,F"),
            ("menu1_topHalf", self.topHalfScreenHeight, "Ctrl+S,1"),
            ("menu1_bottomHalf", self.bottomHalfScreenHeight, "Ctrl+S,2"),
            ("menu1_leftHalf", self.leftHalfScreenWidth, "Ctrl+S,3"),
            ("menu1_rightHalf", self.rightHalfScreenWidth, "Ctrl+S,4"),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        subMenu = addSubMenu(subMenu0, "menu2_toobars")
        items = (
            ("menu2_all", self.setNoToolBar, "Ctrl+J"),
            ("menu2_topOnly", self.hideShowAdditionalToolBar, "Ctrl+G"),
            ("menu2_top", self.hideShowMainToolBar, None),
            ("menu2_second", self.hideShowSecondaryToolBar, None),
            ("menu2_left", self.hideShowLeftToolBar, None),
            ("menu2_right", self.hideShowRightToolBar, None),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        subMenu0.addSeparator()
        items = (
            ("menu2_study", self.parallel, "Ctrl+W"),
            ("menu2_bottom", self.cycleInstant, "Ctrl+T"),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu0, feature, self, action, shortcut)
        subMenu0.addSeparator()
        addMenuItem(subMenu0, "menu2_landscape", self, self.switchLandscapeMode)
        addMenuItem(menu, "menu_config_flags", self, self.moreConfigOptionsDialog)
        menu.addSeparator()
        if config.enableMacros:
            addMenuItem(menu, "menu_startup_macro", self, self.setStartupMacro)
        subMenu = addSubMenu(menu, "menu1_clipboard")
        items = (
            ("menu1_readClipboard", self.pasteFromClipboard, None),
            ("menu1_runClipboard", self.parseContentOnClipboard, "Ctrl+^"),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        subMenu = addSubMenu(menu, "bar3_pdf")
        items = (
            ("bar1_menu", self.printMainPage),
            ("bar2_menu", self.printStudyPage),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        menu.addSeparator()
        #addMenuItem(menu, "menu1_update", self, self.updateUniqueBibleApp)
        #menu.addSeparator()
        addIconMenuItem("UniqueBibleApp.png", menu, "menu1_exit", self, self.quitApp, "Ctrl+Q")

        # 2nd column
        menu = addMenu(menuBar, "menu_bible")
        subMenu = addSubMenu(menu, "menu_navigation")
        items = (
            ("menu_next_book", self.nextMainBook, "Ctrl+H,1"),
            ("menu_previous_book", self.previousMainBook, "Ctrl+H,2"),
            ("menu4_next", self.nextMainChapter, "Ctrl+>"),
            ("menu4_previous", self.previousMainChapter, "Ctrl+<"),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        subMenu = addSubMenu(menu, "menu_scroll")
        items = (
            ("menu_main_scroll_to_top", self.mainPageScrollToTop, "Ctrl+H,3"),
            ("menu_main_page_up", self.mainPageScrollPageUp, "Ctrl+H,4"),
            ("menu_main_page_down", self.mainPageScrollPageDown, "Ctrl+H,5"),
            ("menu_study_scroll_to_top", self.studyPageScrollToTop, "Ctrl+H,6"),
            ("menu_study_page_up", self.studyPageScrollPageUp, "Ctrl+H,7"),
            ("menu_study_page_down", self.studyPageScrollPageDown, "Ctrl+H,8"),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        menu.addSeparator()
        subMenu = addSubMenu(menu, "menu_toggleFeatures")
        items = (
            ("menu2_format", self.enableParagraphButtonClicked, "Ctrl+P"),
            ("menu2_subHeadings", self.enableSubheadingButtonClicked, None),
            ("menu2_hover", self.enableInstantButtonClicked, "Ctrl+="),
            ("menu_toggleEnforceCompareParallel", self.enforceCompareParallelButtonClicked, None),
            ("menu_syncStudyWindowBible", self.enableSyncStudyWindowBibleButtonClicked, None),
            ("menu_syncBibleCommentary", self.enableSyncCommentaryButtonClicked, None),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        if config.enableVerseHighlighting:
            addMenuItem(subMenu, "menu2_toggleHighlightMarkers", self, self.toggleHighlightMarker)

        # 3rd column
        menu = addMenu(menuBar, "controlPanel")
        for index, shortcut in enumerate(("B", "L", "F", "H")):
            addMenuItem(menu, "cp{0}".format(index), self, lambda index=index, shortcut=shortcut: self.openControlPanelTab(index), "Ctrl+{0}".format(shortcut))

        # 4th column
        menu = addMenu(menuBar, "menu8_resources")
        subMenu = addSubMenu(menu, "folders")
        items = (
            ("menu8_marvelData", self.openMarvelDataFolder),
            ("menu11_images", self.openImagesFolder),
            ("menu11_music", self.openMusicFolder),
            ("menu11_video", self.openVideoFolder),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        menu.addSeparator()
        subMenu = addSubMenu(menu, "add")
        items = (
            ("menu8_bibles", self.installMarvelBibles),
            ("menu8_commentaries", self.installMarvelCommentaries),
            ("menu8_datasets", self.installMarvelDatasets),
            ("menu8_plusLexicons", self.importBBPlusLexiconInAFolder),
            ("menu8_plusDictionaries", self.importBBPlusDictionaryInAFolder),
            ("menu8_download3rdParty", self.moreBooks),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        menu.addSeparator()
        subMenu = addSubMenu(menu, "import")
        items = (
            ("menu8_3rdParty", self.importModules),
            ("menu8_3rdPartyInFolder", self.importModulesInFolder),
            ("menu8_settings", self.importSettingsDialog),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(menu, "create")
        items = (
            ("menu10_bookFromImages", self.createBookModuleFromImages),
            ("menu10_bookFromHtml", self.createBookModuleFromHTML),
            ("menu10_bookFromNotes", self.createBookModuleFromNotes),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(menu, "tag")
        items = (
            ("menu8_tagFile", self.tagFile),
            ("menu8_tagFiles", self.tagFiles),
            ("menu8_tagFolder", self.tagFolder),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)

        # macros
        if config.enableMacros:
            macros_menu = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_macros"]))
            run_macros_menu = macros_menu.addMenu(config.thisTranslation["menu_run"])
            self.loadRunMacrosMenu(run_macros_menu)
            build_macros_menu = macros_menu.addMenu(config.thisTranslation["menu_build_macro"])
            build_macros_menu.addAction(QAction(config.thisTranslation["menu_command"], self, triggered=self.macroSaveCommand))
            build_macros_menu.addAction(QAction(config.thisTranslation["menu_highlight"], self, triggered=self.macroSaveHighlights))

        # information
        if config.showInformation:
            menu = addMenu(menuBar, "menu9_information")
            menu.addAction(QAction(config.thisTranslation["menu1_wikiPages"], self, triggered=self.openUbaWiki))
            menu.addSeparator()
            subMenu = addSubMenu(menu, "websites")
            items = (
                ("BibleTools.app", self.openBibleTools),
                ("UniqueBible.app", self.openUniqueBible),
                ("Marvel.bible", self.openMarvelBible),
                ("BibleBento.com", self.openBibleBento),
                ("OpenGNT.com", self.openOpenGNT),
            )
            for feature, action in items:
                addMenuItem(subMenu, feature, self, action, None, False)
            subMenu = addSubMenu(menu, "repositories")
            items = (
                ("GitHub Repositories", self.openSource),
                ("Unique Bible", self.openUniqueBibleSource),
                ("Open Hebrew Bible", self.openHebrewBibleSource),
                ("Open Greek New Testament", self.openOpenGNTSource),
            )
            for feature, action in items:
                addMenuItem(subMenu, feature, self, action, None, False)
            menu.addSeparator()
            items = (
                ("report", self.reportAnIssue),
                ("menu9_contact", self.contactEliranWong),
            )
            for feature, action in items:
                addMenuItem(menu, feature, self, action)
            menu.addSeparator()
            addMenuItem(menu, "menu9_donate", self, self.donateToUs)

        if config.developer:
            menu = addMenu(menuBar, "developer")
            #addMenuItem(menu, "Download Google Static Maps", self, self.downloadGoogleStaticMaps, None, False)
            addMenuItem(menu, "Testing", self, self.testing, None, False)

    def testing(self):
        #pass
        print("testing")

    def addStandardTextButton(self, toolTip, action, toolbar, button=None, translation=True):
        textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"
        if button is None:
            button = QPushButton()
        button.setToolTip(config.thisTranslation[toolTip] if translation else toolTip)
        button.setStyleSheet(textButtonStyle)
        button.clicked.connect(action)
        toolbar.addWidget(button)

    def addStandardIconButton(self, toolTip, icon, action, toolbar, button=None, translation=True):
        if button is None:
            button = QPushButton()
        if config.qtMaterial and config.qtMaterialTheme:
            #button.setFixedSize(config.iconButtonWidth, config.iconButtonWidth)
            button.setFixedWidth(config.iconButtonWidth)
            #button.setFixedHeight(config.iconButtonWidth)
        button.setToolTip(config.thisTranslation[toolTip] if translation else toolTip)
        buttonIconFile = os.path.join("htmlResources", icon)
        button.setIcon(QIcon(buttonIconFile))
        button.clicked.connect(action)
        toolbar.addWidget(button)

    def setupToolBarStandardIconSize(self):
        
        self.firstToolBar = QToolBar()
        self.firstToolBar.setWindowTitle(config.thisTranslation["bar1_title"])
        self.firstToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.firstToolBar)

        self.addStandardTextButton("menu_previous_chapter", self.previousMainChapter, self.firstToolBar, QPushButton("<"))
        self.mainRefButton = QPushButton(":::".join(self.verseReference("main")))
        self.addStandardTextButton("bar1_reference", self.mainRefButtonClicked, self.firstToolBar, self.mainRefButton)
        self.addStandardTextButton("menu_next_chapter", self.nextMainChapter, self.firstToolBar, QPushButton(">"))

        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        if config.qtMaterial and config.qtMaterialTheme:
            config.iconButtonWidth = self.mainRefButton.height()

        self.addStandardIconButton("menu_bookNote", "noteBook.png", self.openMainBookNote, self.firstToolBar)
        self.addStandardIconButton("menu_chapterNote", "noteChapter.png", self.openMainChapterNote, self.firstToolBar)
        self.addStandardIconButton("menu_verseNote", "noteVerse.png", self.openMainVerseNote, self.firstToolBar)
        self.addStandardIconButton("bar1_searchBible", "search.png", self.displaySearchBibleCommand, self.firstToolBar)
        self.addStandardIconButton("bar1_searchBibles", "search_plus.png", self.displaySearchBibleMenu, self.firstToolBar)

        self.firstToolBar.addSeparator()

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.setClearButtonEnabled(True)
        self.textCommandLineEdit.setToolTip(config.thisTranslation["bar1_command"])
        self.textCommandLineEdit.setMinimumWidth(100)
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        if not config.preferControlPanelForCommandLineEntry:
            self.firstToolBar.addWidget(self.textCommandLineEdit)
            self.firstToolBar.addSeparator()

        self.enableStudyBibleButton = QPushButton()
        self.addStandardIconButton(self.getStudyBibleDisplayToolTip(), self.getStudyBibleDisplay(), self.enableStudyBibleButtonClicked, self.firstToolBar, self.enableStudyBibleButton, False)

        #self.studyRefButton = QPushButton(":::".join(self.verseReference("study")))
        #self.addStandardTextButton("bar2_reference", self.studyRefButtonClicked, self.firstToolBar, self.studyRefButton)
        #self.enableSyncStudyWindowBibleButton = QPushButton()
        #self.addStandardIconButton(self.getSyncStudyWindowBibleDisplayToolTip(), self.getSyncStudyWindowBibleDisplay(), self.enableSyncStudyWindowBibleButtonClicked, self.firstToolBar, self.enableSyncStudyWindowBibleButton, False)

        # Toolbar height here is affected by the actual size of icon file used in a QAction
        if config.qtMaterial and config.qtMaterialTheme:
            self.firstToolBar.setFixedHeight(config.iconButtonWidth + 4)
            self.firstToolBar.setIconSize(QSize(config.iconButtonWidth / 2, config.iconButtonWidth / 2))
        # QAction can use setVisible whereas QPushButton cannot when it is placed on a toolbar.
        self.studyRefButton = self.firstToolBar.addAction(":::".join(self.verseReference("study")), self.studyRefButtonClicked)
        iconFile = os.path.join("htmlResources", self.getSyncStudyWindowBibleDisplay())
        self.enableSyncStudyWindowBibleButton = self.firstToolBar.addAction(QIcon(iconFile), self.getSyncStudyWindowBibleDisplayToolTip(), self.enableSyncStudyWindowBibleButtonClicked)
        if config.openBibleInMainViewOnly:
            self.studyRefButton.setVisible(False)
            self.enableSyncStudyWindowBibleButton.setVisible(False)
        self.firstToolBar.addSeparator()

        self.addStandardIconButton("bar1_toolbars", "toolbar.png", self.hideShowAdditionalToolBar, self.firstToolBar)

        if config.addBreakAfterTheFirstToolBar:
            self.addToolBarBreak()

        #self.studyBibleToolBar = QToolBar()
        #self.studyBibleToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        #self.studyBibleToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        #self.addToolBar(self.studyBibleToolBar)

        #if config.addBreakBeforeTheLastToolBar:
        #    self.addToolBarBreak()

        # Second tool bar
        self.secondToolBar = QToolBar()
        self.secondToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.secondToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.secondToolBar)

        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
        self.addStandardTextButton("menu4_commentary", self.commentaryRefButtonClicked, self.secondToolBar, self.commentaryRefButton)

        self.enableSyncCommentaryButton = QPushButton()
        self.addStandardIconButton(self.getSyncCommentaryDisplayToolTip(), self.getSyncCommentaryDisplay(), self.enableSyncCommentaryButtonClicked, self.secondToolBar, self.enableSyncCommentaryButton, False)
        self.secondToolBar.addSeparator()

        self.bookButton = QPushButton(config.book)
        self.addStandardTextButton("menu5_book", self.openBookMenu, self.secondToolBar, self.bookButton)

        self.addStandardIconButton("bar2_searchBooks", "search.png", self.displaySearchBookCommand, self.secondToolBar)

        self.secondToolBar.addSeparator()

        self.addStandardIconButton("menu7_create", "newfile.png", self.createNewNoteFile, self.secondToolBar)
        self.addStandardIconButton("menu7_open", "open.png", self.openTextFileDialog, self.secondToolBar)

        self.externalFileButton = QPushButton(self.getLastExternalFileName())
        self.addStandardTextButton("menu7_read", self.externalFileButtonClicked, self.secondToolBar, self.externalFileButton)

        self.addStandardIconButton("menu7_edit", "edit.png", self.editExternalFileButtonClicked, self.secondToolBar)

        self.secondToolBar.addSeparator()

        self.addStandardIconButton("menu2_smaller", "fontMinus.png", self.smallerFont, self.secondToolBar)

        self.defaultFontButton = QPushButton("{0} {1}".format(config.font, config.fontSize))
        self.addStandardTextButton("menu1_setDefaultFont", self.setDefaultFont, self.secondToolBar, self.defaultFontButton)

        self.addStandardIconButton("menu2_larger", "fontPlus.png", self.largerFont, self.secondToolBar)
        self.secondToolBar.addSeparator()
        self.addStandardIconButton("menu11_youtube", "youtube.png", self.openYouTube, self.secondToolBar)
        self.secondToolBar.addSeparator()
        self.addStandardIconButton("menu1_reload", "reload.png", self.reloadCurrentRecord, self.secondToolBar)
        self.secondToolBar.addSeparator()

        # Left tool bar
        self.leftToolBar = QToolBar()
        self.leftToolBar.setWindowTitle(config.thisTranslation["bar3_title"])
        self.leftToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.LeftToolBarArea, self.leftToolBar)

        self.addStandardIconButton("menu3_mainBack", "left.png", self.back, self.leftToolBar)
        self.addStandardIconButton("menu3_main", "history.png", self.mainHistoryButtonClicked, self.leftToolBar)
        self.addStandardIconButton("menu3_mainForward", "right.png", self.forward, self.leftToolBar)
        self.leftToolBar.addSeparator()
        self.addStandardIconButton("bar3_pdf", "pdf.png", self.printMainPage, self.leftToolBar)
        self.leftToolBar.addSeparator()
        self.enableParagraphButton = QPushButton()
        self.addStandardIconButton("menu2_format", self.getReadFormattedBibles(), self.enableParagraphButtonClicked, self.leftToolBar, self.enableParagraphButton)
        self.enableSubheadingButton = QPushButton()
        self.addStandardIconButton("menu2_subHeadings", self.getAddSubheading(), self.enableSubheadingButtonClicked, self.leftToolBar, self.enableSubheadingButton)
        self.leftToolBar.addSeparator()
        self.addStandardIconButton("menu4_compareAll", "compare_with.png", self.runCOMPARE, self.leftToolBar)
        self.addStandardIconButton("menu4_moreComparison", "parallel_with.png", self.mainRefButtonClicked, self.leftToolBar)
        self.enforceCompareParallelButton = QPushButton()
        self.addStandardIconButton(self.getEnableCompareParallelDisplayToolTip(), self.getEnableCompareParallelDisplay(), self.enforceCompareParallelButtonClicked, self.leftToolBar, self.enforceCompareParallelButton, False)
        self.leftToolBar.addSeparator()
        self.addStandardIconButton("Marvel Original Bible", "original.png", self.runMOB, self.leftToolBar, None, False)
        self.addStandardIconButton("Marvel Interlinear Bible", "interlinear.png", self.runMIB, self.leftToolBar, None, False)
        self.addStandardIconButton("Marvel Trilingual Bible", "trilingual.png", self.runMTB, self.leftToolBar, None, False)
        self.addStandardIconButton("Marvel Parallel Bible", "line.png", self.runMPB, self.leftToolBar, None, False)
        self.addStandardIconButton("Marvel Annotated Bible", "annotated.png", self.runMAB, self.leftToolBar, None, False)
        self.leftToolBar.addSeparator()

        # Right tool bar
        self.rightToolBar = QToolBar()
        self.rightToolBar.setWindowTitle(config.thisTranslation["bar4_title"])
        self.rightToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.RightToolBarArea, self.rightToolBar)

        self.addStandardIconButton("menu3_studyBack", "left.png", self.studyBack, self.rightToolBar)
        self.addStandardIconButton("menu3_study", "history.png", self.studyHistoryButtonClicked, self.rightToolBar)
        self.addStandardIconButton("menu3_studyForward", "right.png", self.studyForward, self.rightToolBar)
        self.rightToolBar.addSeparator()
        self.addStandardIconButton("bar3_pdf", "pdf.png", self.printStudyPage, self.rightToolBar)
        self.rightToolBar.addSeparator()
        self.addStandardIconButton("menu4_indexes", "indexes.png", self.runINDEX, self.rightToolBar)
        self.addStandardIconButton("menu4_commentary", "commentary.png", self.runCOMMENTARY, self.rightToolBar)
        self.rightToolBar.addSeparator()
        self.addStandardIconButton("menu4_crossRef", "cross_reference.png", self.runCROSSREFERENCE, self.rightToolBar)
        self.addStandardIconButton("menu4_tske", "treasure.png", self.runTSKE, self.rightToolBar)
        self.rightToolBar.addSeparator()
        self.addStandardIconButton("menu4_traslations", "translations.png", self.runTRANSLATION, self.rightToolBar)
        self.addStandardIconButton("menu4_discourse", "discourse.png", self.runDISCOURSE, self.rightToolBar)
        self.addStandardIconButton("menu4_words", "words.png", self.runWORDS, self.rightToolBar)
        self.addStandardIconButton("menu4_tdw", "combo.png", self.runCOMBO, self.rightToolBar)
        self.rightToolBar.addSeparator()
        self.addStandardIconButton("menu2_hover", self.getInstantInformation(), self.enableInstantButtonClicked, self.rightToolBar)
        self.addStandardIconButton("menu2_bottom", "lightning.png", self.cycleInstant, self.rightToolBar)
        self.rightToolBar.addSeparator()

    def setupToolBarFullIconSize(self):

        textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"

        self.firstToolBar = QToolBar()
        self.firstToolBar.setWindowTitle(config.thisTranslation["bar1_title"])
        self.firstToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.firstToolBar)

        self.addStandardTextButton("menu_previous_chapter", self.previousMainChapter, self.firstToolBar, QPushButton("<"))
        self.mainRefButton = QPushButton(":::".join(self.verseReference("main")))
        self.mainRefButton.setToolTip(config.thisTranslation["bar1_reference"])
        self.mainRefButton.setStyleSheet(textButtonStyle)
        self.mainRefButton.clicked.connect(self.mainRefButtonClicked)
        self.firstToolBar.addWidget(self.mainRefButton)
        self.addStandardTextButton("menu_next_chapter", self.nextMainChapter, self.firstToolBar, QPushButton(">"))

        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        if config.qtMaterial and config.qtMaterialTheme:
            config.iconButtonWidth = self.mainRefButton.height()

        iconFile = os.path.join("htmlResources", "noteBook.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu_bookNote"], self.openMainBookNote)

        iconFile = os.path.join("htmlResources", "noteChapter.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu_chapterNote"], self.openMainChapterNote)

        iconFile = os.path.join("htmlResources", "noteVerse.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu_verseNote"], self.openMainVerseNote)

        iconFile = os.path.join("htmlResources", "search.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_searchBible"], self.displaySearchBibleCommand)

        iconFile = os.path.join("htmlResources", "search_plus.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_searchBibles"], self.displaySearchBibleMenu)

        self.firstToolBar.addSeparator()

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.setToolTip(config.thisTranslation["bar1_command"])
        self.textCommandLineEdit.setMinimumWidth(100)
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        if not config.preferControlPanelForCommandLineEntry:
            self.firstToolBar.addWidget(self.textCommandLineEdit)
            self.firstToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", self.getStudyBibleDisplay())
        self.enableStudyBibleButton = self.firstToolBar.addAction(QIcon(iconFile), self.getStudyBibleDisplayToolTip(), self.enableStudyBibleButtonClicked)
        
        self.studyRefButton = self.firstToolBar.addAction(":::".join(self.verseReference("study")), self.studyRefButtonClicked)
        iconFile = os.path.join("htmlResources", self.getSyncStudyWindowBibleDisplay())
        self.enableSyncStudyWindowBibleButton = self.firstToolBar.addAction(QIcon(iconFile), self.getSyncStudyWindowBibleDisplayToolTip(), self.enableSyncStudyWindowBibleButtonClicked)
        if config.openBibleInMainViewOnly:
            self.studyRefButton.setVisible(False)
            self.enableSyncStudyWindowBibleButton.setVisible(False)
        self.firstToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "toolbar.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_toolbars"], self.hideShowAdditionalToolBar)

        if config.addBreakAfterTheFirstToolBar:
            self.addToolBarBreak()

        #self.studyBibleToolBar = QToolBar()
        #self.studyBibleToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        #self.studyBibleToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        #self.addToolBar(self.studyBibleToolBar)

        #if config.addBreakBeforeTheLastToolBar:
        #    self.addToolBarBreak()

        self.secondToolBar = QToolBar()
        self.secondToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.secondToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.secondToolBar)

        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
        self.commentaryRefButton.setToolTip(config.thisTranslation["menu4_commentary"])
        self.commentaryRefButton.setStyleSheet(textButtonStyle)
        self.commentaryRefButton.clicked.connect(self.commentaryRefButtonClicked)
        self.secondToolBar.addWidget(self.commentaryRefButton)

        iconFile = os.path.join("htmlResources", self.getSyncCommentaryDisplay())
        self.enableSyncCommentaryButton = self.secondToolBar.addAction(QIcon(iconFile), self.getSyncCommentaryDisplayToolTip(), self.enableSyncCommentaryButtonClicked)

        self.secondToolBar.addSeparator()

        self.bookButton = QPushButton(config.book)
        self.bookButton.setToolTip(config.thisTranslation["menu5_book"])
        self.bookButton.setStyleSheet(textButtonStyle)
        self.bookButton.clicked.connect(self.openBookMenu)
        self.secondToolBar.addWidget(self.bookButton)

        iconFile = os.path.join("htmlResources", "search.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar2_searchBooks"], self.displaySearchBookCommand)

        self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "newfile.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu7_create"], self.createNewNoteFile)

        iconFile = os.path.join("htmlResources", "open.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu7_open"], self.openTextFileDialog)

        self.externalFileButton = QPushButton(self.getLastExternalFileName())
        self.externalFileButton.setToolTip(config.thisTranslation["menu7_read"])
        self.externalFileButton.setStyleSheet(textButtonStyle)
        self.externalFileButton.clicked.connect(self.externalFileButtonClicked)
        self.secondToolBar.addWidget(self.externalFileButton)

        iconFile = os.path.join("htmlResources", "edit.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu7_edit"], self.editExternalFileButtonClicked)

        self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "fontMinus.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_smaller"], self.smallerFont)

        self.defaultFontButton = QPushButton("{0} {1}".format(config.font, config.fontSize))
        self.defaultFontButton.setToolTip(config.thisTranslation["menu1_setDefaultFont"])
        self.defaultFontButton.setStyleSheet(textButtonStyle)
        self.defaultFontButton.clicked.connect(self.setDefaultFont)
        self.secondToolBar.addWidget(self.defaultFontButton)

        iconFile = os.path.join("htmlResources", "fontPlus.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_larger"], self.largerFont)

        self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "youtube.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu11_youtube"], self.openYouTube)

        self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "reload.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu1_reload"], self.reloadCurrentRecord)

        self.secondToolBar.addSeparator()

        self.leftToolBar = QToolBar()
        self.leftToolBar.setWindowTitle(config.thisTranslation["bar3_title"])
        self.leftToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.LeftToolBarArea, self.leftToolBar)

        iconFile = os.path.join("htmlResources", "left.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_mainBack"], self.back)

        iconFile = os.path.join("htmlResources", "history.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_main"], self.mainHistoryButtonClicked)

        iconFile = os.path.join("htmlResources", "right.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_mainForward"], self.forward)

        self.leftToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "pdf.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar3_pdf"], self.printMainPage)

        self.leftToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", self.getReadFormattedBibles())
        self.enableParagraphButton = self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_format"], self.enableParagraphButtonClicked)

        iconFile = os.path.join("htmlResources", self.getAddSubheading())
        self.enableSubheadingButton = self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_subHeadings"], self.enableSubheadingButtonClicked)

        self.leftToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "compare_with.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_compareAll"], self.runCOMPARE)

        iconFile = os.path.join("htmlResources", "parallel_with.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_moreComparison"], self.mainRefButtonClicked)

        iconFile = os.path.join("htmlResources", self.getEnableCompareParallelDisplay())
        self.enforceCompareParallelButton = self.leftToolBar.addAction(QIcon(iconFile), self.getEnableCompareParallelDisplayToolTip(), self.enforceCompareParallelButtonClicked)

        self.leftToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "original.png")
        self.leftToolBar.addAction(QIcon(iconFile), "Marvel Original Bible", self.runMOB)

        iconFile = os.path.join("htmlResources", "interlinear.png")
        self.leftToolBar.addAction(QIcon(iconFile), "Marvel Interlinear Bible", self.runMIB)

        iconFile = os.path.join("htmlResources", "trilingual.png")
        self.leftToolBar.addAction(QIcon(iconFile), "Marvel Trilingual Bible", self.runMTB)

        iconFile = os.path.join("htmlResources", "line.png")
        self.leftToolBar.addAction(QIcon(iconFile), "Marvel Parallel Bible", self.runMPB)

        iconFile = os.path.join("htmlResources", "annotated.png")
        self.leftToolBar.addAction(QIcon(iconFile), "Marvel Annotated Bible", self.runMAB)

        self.leftToolBar.addSeparator()

        self.rightToolBar = QToolBar()
        self.rightToolBar.setWindowTitle(config.thisTranslation["bar4_title"])
        self.rightToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.RightToolBarArea, self.rightToolBar)

        iconFile = os.path.join("htmlResources", "left.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_studyBack"], self.studyBack)

        iconFile = os.path.join("htmlResources", "history.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_study"], self.studyHistoryButtonClicked)

        iconFile = os.path.join("htmlResources", "right.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_studyForward"], self.studyForward)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "pdf.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar3_pdf"], self.printStudyPage)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "indexes.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_indexes"], self.runINDEX)

        iconFile = os.path.join("htmlResources", "commentary.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_commentary"], self.runCOMMENTARY)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "cross_reference.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_crossRef"], self.runCROSSREFERENCE)

        iconFile = os.path.join("htmlResources", "treasure.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_tske"], self.runTSKE)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "translations.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_traslations"], self.runTRANSLATION)

        iconFile = os.path.join("htmlResources", "discourse.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_discourse"], self.runDISCOURSE)

        iconFile = os.path.join("htmlResources", "words.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_words"], self.runWORDS)

        iconFile = os.path.join("htmlResources", "combo.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_tdw"], self.runCOMBO)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", self.getInstantInformation())
        self.enableInstantButton = self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_hover"], self.enableInstantButtonClicked)

        iconFile = os.path.join("htmlResources", "lightning.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_bottom"], self.cycleInstant)

        self.rightToolBar.addSeparator()

        if config.qtMaterial and config.qtMaterialTheme:
            for toolbar in (self.firstToolBar, self.secondToolBar):
                toolbar.setIconSize(QSize(config.iconButtonWidth / 1.33, config.iconButtonWidth / 1.33))
                toolbar.setFixedHeight(config.iconButtonWidth + 4)
            for toolbar in (self.leftToolBar, self.rightToolBar):
                toolbar.setIconSize(QSize(config.iconButtonWidth * 0.6, config.iconButtonWidth * 0.6))
