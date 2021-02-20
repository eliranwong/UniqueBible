from gui.MenuItems import *
from PySide2.QtCore import QSize
import shortcut as sc
from util.ShortcutUtil import ShortcutUtil


class AlephMainWindow:

    def create_menu(self):
        menu1 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu1_app"]))
        menu1_defaults = menu1.addMenu(config.thisTranslation["menu_defaults"])
        menu1_defaults.addAction(QAction(config.thisTranslation["menu_language"], self, triggered=self.openMyLanguageDialog))
        selectTheme = menu1_defaults.addMenu(config.thisTranslation["menu1_selectTheme"])
        if config.qtMaterial:
            qtMaterialThemes = ["light_amber.xml", "light_blue.xml", "light_cyan.xml", "light_cyan_500.xml",
                                "light_lightgreen.xml", "light_pink.xml", "light_purple.xml", "light_red.xml",
                                "light_teal.xml", "light_yellow.xml", "dark_amber.xml", "dark_blue.xml",
                                "dark_cyan.xml", "dark_lightgreen.xml", "dark_pink.xml", "dark_purple.xml",
                                "dark_red.xml", "dark_teal.xml", "dark_yellow.xml"]
            for theme in qtMaterialThemes:
                selectTheme.addAction(
                    QAction(theme[:-4], self, triggered=lambda theme=theme: self.setQtMaterialTheme(theme)))
        else:
            selectTheme.addAction(QAction(config.thisTranslation["menu_light_theme"], self, triggered=self.setDefaultTheme))
            selectTheme.addAction(QAction(config.thisTranslation["menu1_dark_theme"], self, triggered=self.setDarkTheme))
        layoutMenu = menu1_defaults.addMenu(config.thisTranslation["menu1_menuLayout"])
        layoutMenu.addAction(
            QAction(config.thisTranslation["menu1_aleph_menu_layout"], self, triggered=lambda: self.setMenuLayout("aleph")))
        layoutMenu.addAction(
            QAction(config.thisTranslation["menu1_focus_menu_layout"], self, triggered=lambda: self.setMenuLayout("focus")))
        layoutMenu.addAction(
            QAction(config.thisTranslation["menu1_classic_menu_layout"], self, triggered=lambda: self.setMenuLayout("classic")))

        shortcutsMenu = menu1_defaults.addMenu(config.thisTranslation["menu_shortcuts"])
        shortcutsMenu.addAction(
            QAction(config.thisTranslation["menu_blank"], self,
                    triggered=lambda: self.setShortcuts("blank")))
        shortcutsMenu.addAction(
            QAction(config.thisTranslation["menu_brachys"], self,
                    triggered=lambda: self.setShortcuts("brachys")))
        shortcutsMenu.addAction(
            QAction(config.thisTranslation["menu_micron"], self,
                    triggered=lambda: self.setShortcuts("micron")))
        shortcutsMenu.addAction(
            QAction(config.thisTranslation["menu_syntemno"], self,
                    triggered=lambda: self.setShortcuts("syntemno")))
        customShortcuts = ShortcutUtil.getListCustomShortcuts()
        for shortcut in customShortcuts:
            shortcutsMenu.addAction(
                QAction(shortcut, self, triggered=lambda shortcut=shortcut: self.setShortcuts(shortcut)))
        if config.enableMacros:
            menu1_defaults.addAction(
                QAction(config.thisTranslation["menu_startup_macro"], self, triggered=self.setStartupMacro))
        lexiconMenu = menu1_defaults.addMenu(config.thisTranslation["menu_lexicon"])
        lexiconMenu.addAction(QAction(config.thisTranslation["menu1_StrongsHebrew"], self, triggered=self.openSelectDefaultStrongsHebrewLexiconDialog))
        lexiconMenu.addAction(QAction(config.thisTranslation["menu1_StrongsGreek"], self, triggered=self.openSelectDefaultStrongsGreekLexiconDialog))
        menu1_defaults.addAction(
            QAction(config.thisTranslation["menu_favouriteBible"], self, triggered=self.openFavouriteBibleDialog))
        menu1_defaults.addAction(QAction(config.thisTranslation["menu_abbreviations"], self, triggered=self.setBibleAbbreviations))
        menu1_defaults.addAction(QAction(config.thisTranslation["menu_tabs"], self, triggered=self.setTabNumberDialog))
        menu1_defaults.addAction(QAction(config.thisTranslation["menu_font"], self, triggered=self.setDefaultFont))
        menu1_defaults.addAction(QAction(config.thisTranslation["menu_chineseFont"], self, triggered=self.setChineseFont))
        if config.developer:
            menu_developer = menu1.addMenu("&Developer")
        menu1.addAction(
            QAction(config.thisTranslation["menu_config_flags"], self, triggered=self.moreConfigOptionsDialog))

        menu1.addAction(
            QAction(config.thisTranslation["menu_quit"], self, shortcut=sc.quitApp, triggered=self.quitApp))

        navigation_menu = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_navigation"]))
        masterControlMenu = addMenu(navigation_menu, "controlPanel")
        masterControlMenu.addAction(QAction(config.thisTranslation["cp0"], self, shortcut=sc.openControlPanelTab0, triggered=lambda: self.openControlPanelTab(0)))
        masterControlMenu.addAction(QAction(config.thisTranslation["cp1"], self, shortcut=sc.openControlPanelTab1, triggered=lambda: self.openControlPanelTab(1)))
        masterControlMenu.addAction(QAction(config.thisTranslation["cp2"], self, shortcut=sc.openControlPanelTab2, triggered=lambda: self.openControlPanelTab(2)))
        masterControlMenu.addAction(QAction(config.thisTranslation["cp3"], self, shortcut=sc.openControlPanelTab3, triggered=lambda: self.openControlPanelTab(3)))
        masterControlMenu.addAction(QAction(config.thisTranslation["cp4"], self, shortcut=sc.openControlPanelTab4, triggered=lambda: self.openControlPanelTab(4)))
        navigation_menu.addAction(QAction(config.thisTranslation["menu1_miniControl"], self, shortcut=sc.manageMiniControl, triggered=self.manageMiniControl))
        navigation_menu.addSeparator()
        navigation_menu.addAction(
            QAction(config.thisTranslation["menu_first_chapter"], self, shortcut=sc.gotoFirstChapter, triggered=self.gotoFirstChapter))
        prev_chap = QAction(config.thisTranslation["menu4_previous"], self, shortcut=sc.previousMainChapter, triggered=self.previousMainChapter)
        # prev_chap.setShortcuts(["Ctrl+,"])
        navigation_menu.addAction(prev_chap)
        navigation_menu.addAction(QAction(config.thisTranslation["menu4_next"], self, shortcut=sc.nextMainChapter, triggered=self.nextMainChapter))
        navigation_menu.addAction(QAction(config.thisTranslation["menu_last_chapter"], self, shortcut=sc.gotoLastChapter, triggered=self.gotoLastChapter))
        navigation_menu.addAction(QAction(config.thisTranslation["menu_next_book"], self, shortcut=sc.nextMainBook, triggered=self.nextMainBook))
        navigation_menu.addAction(QAction(config.thisTranslation["menu_previous_book"], self, shortcut=sc.previousMainBook, triggered=self.previousMainBook))
        scroll_menu = navigation_menu.addMenu("&{0}".format(config.thisTranslation["menu_scroll"]))
        scroll_menu.addAction(QAction(config.thisTranslation["menu_main_scroll_to_top"], self, shortcut=sc.mainPageScrollToTop,
                                          triggered=self.mainPageScrollToTop))
        scroll_menu.addAction(QAction(config.thisTranslation["menu_main_page_down"], self, shortcut=sc.mainPageScrollPageDown,
                                          triggered=self.mainPageScrollPageDown))
        scroll_menu.addAction(QAction(config.thisTranslation["menu_main_page_up"], self, shortcut=sc.mainPageScrollPageUp,
                                          triggered=self.mainPageScrollPageUp))
        scroll_menu.addAction(QAction(config.thisTranslation["menu_study_scroll_to_top"], self,
                                      shortcut=sc.studyPageScrollToTop,triggered=self.studyPageScrollToTop))
        scroll_menu.addAction(QAction(config.thisTranslation["menu_study_page_down"], self, shortcut=sc.studyPageScrollPageDown,
                                      triggered=self.studyPageScrollPageDown))
        scroll_menu.addAction(QAction(config.thisTranslation["menu_study_page_up"], self, shortcut=sc.studyPageScrollPageUp,
                                      triggered=self.studyPageScrollPageUp))
        navigation_menu.addSeparator()
        marvel_bible_menu = navigation_menu.addMenu(config.thisTranslation["menu_bible"])
        marvel_bible_menu.addAction(QAction("Marvel Original Bible", self, shortcut=sc.runMOB, triggered=self.runMOB))
        marvel_bible_menu.addAction(QAction("Marvel Interlinear Bible", self, shortcut=sc.runMIB, triggered=self.runMIB))
        marvel_bible_menu.addAction(QAction("Marvel Trilingual Bible", self, shortcut=sc.runMTB, triggered=self.runMTB))
        marvel_bible_menu.addAction(
            QAction("Marvel Parallel Bible", self, shortcut=sc.runMPB, triggered=self.runMPB))
        if os.path.isfile(os.path.join(config.marvelData, "bibles/TRLIT.bible")):
            marvel_bible_menu.addAction(
                QAction("Transliteral Bible", self, shortcut=sc.runTransliteralBible, triggered=self.runTransliteralBible))
        if os.path.isfile(os.path.join(config.marvelData, "bibles/KJV*.bible")):
            marvel_bible_menu.addAction(
                QAction("KJV* Bible", self, shortcut=sc.runKJV2Bible, triggered=self.runKJV2Bible))
        history_menu = navigation_menu.addMenu("&{0}".format(config.thisTranslation["menu_history"]))
        history_menu.addAction(QAction(config.thisTranslation["menu3_main"], self, shortcut=sc.mainHistoryButtonClicked, triggered=self.mainHistoryButtonClicked))
        history_menu.addAction(QAction(config.thisTranslation["menu3_mainBack"], self, shortcut=sc.back, triggered=self.back))
        history_menu.addAction(QAction(config.thisTranslation["menu3_mainForward"], self, shortcut=sc.forward, triggered=self.forward))
        history_menu.addAction(QAction(config.thisTranslation["menu3_study"], self, shortcut=sc.studyHistoryButtonClicked, triggered=self.studyHistoryButtonClicked))
        history_menu.addAction(QAction(config.thisTranslation["menu3_studyBack"], self, shortcut=sc.studyBack, triggered=self.studyBack))
        history_menu.addAction(QAction(config.thisTranslation["menu3_studyForward"], self, shortcut=sc.studyForward, triggered=self.studyForward))
        #navigation_menu.addAction(QAction(config.thisTranslation["controlPanel"], self, shortcut=sc.manageControlPanel, triggered=self.manageControlPanel))

        search_menu = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_search"]))
        search_menu.addAction(QAction(config.thisTranslation["menu5_bible"], self, shortcut=sc.displaySearchBibleMenu, triggered=self.displaySearchBibleMenu))
        search_menu.addAction(QAction(config.thisTranslation["menu_verse_all_versions"], self, shortcut=sc.runCOMPARE, triggered=self.runCOMPARE))

        search_resources = search_menu.addMenu("&{0}".format(config.thisTranslation["menu_library"]))
        search_resources.addAction(QAction(config.thisTranslation["menu5_topics"], self, triggered=self.searchTopicDialog))
        search_resources.addAction(QAction(config.thisTranslation["context1_encyclopedia"], self, triggered=self.searchEncyclopediaDialog))
        search_resources.addAction(QAction(config.thisTranslation["menu5_selectBook"], self, triggered=self.searchBookDialog))
        search_resources.addAction(QAction(config.thisTranslation["context1_dict"], self, triggered=self.searchDictionaryDialog))
        search_resources.addAction(QAction(config.thisTranslation["menu5_3rdDict"], self, triggered=self.search3rdDictionaryDialog))

        search_command = search_menu.addMenu(config.thisTranslation["menu_command"])
        search_command.addAction(
            QAction(config.thisTranslation["menu_bible"], self, shortcut=sc.displaySearchBibleCommand, triggered=self.displaySearchBibleCommand))
        if config.enableVerseHighlighting:
            search_command.addAction(QAction(config.thisTranslation["menu_highlight"], self, shortcut=sc.displaySearchHighlightCommand, triggered=self.displaySearchHighlightCommand))
        search_command.addAction(
                QAction(config.thisTranslation["menu_bible_book_notes"], self, shortcut=sc.searchCommandBookNote, triggered=self.searchCommandBookNote))
        search_command.addAction(
            QAction(config.thisTranslation["menu_bible_chapter_notes"], self, shortcut=sc.searchCommandChapterNote, triggered=self.searchCommandChapterNote))
        search_command.addAction(QAction(config.thisTranslation["menu_bible_verse_notes"], self, shortcut=sc.searchCommandVerseNote, triggered=self.searchCommandVerseNote))
        search_command.addAction(QAction(config.thisTranslation["menu_lexicon"], self, shortcut=sc.searchCommandLexicon, triggered=self.searchCommandLexicon))
        search_command.addAction(QAction(config.thisTranslation["menu5_characters"], self, shortcut=sc.searchCommandBibleCharacter, triggered=self.searchCommandBibleCharacter))
        search_command.addAction(QAction(config.thisTranslation["menu5_names"], self, shortcut=sc.searchCommandBibleName,
                                triggered=self.searchCommandBibleName))
        search_command.addAction(QAction(config.thisTranslation["menu5_locations"], self, shortcut=sc.searchCommandBibleLocation, triggered=self.searchCommandBibleLocation))
        search_command.addAction(QAction(config.thisTranslation["menu5_allTopics"], self, triggered=self.searchCommandAllBibleTopic))
        search_command.addAction(
            QAction(config.thisTranslation["menu5_allBook"], self, shortcut=sc.displaySearchAllBookCommand, triggered=self.displaySearchAllBookCommand))

        annotate_menu = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_annotate"]))
        if config.enableVerseHighlighting:
            highlight = annotate_menu.addMenu(config.thisTranslation["menu_highlight"])
            highlight.addAction(
                QAction(config.thisTranslation["menu2_toggleHighlightMarkers"], self, shortcut=sc.toggleHighlightMarker, triggered=self.toggleHighlightMarker))
        bible_notes = annotate_menu.addMenu(config.thisTranslation["menu_bible_notes"])
        bible_notes.addAction(
            QAction(config.thisTranslation["menu_book"], self, shortcut=sc.openMainBookNote, triggered=self.openMainBookNote))
        bible_notes.addAction(
            QAction(config.thisTranslation["menu_chapter"], self, shortcut=sc.openMainChapterNote, triggered=self.openMainChapterNote))
        bible_notes.addAction(QAction(config.thisTranslation["menu_verse"], self, shortcut=sc.openMainVerseNote, triggered=self.openMainVerseNote))
        external_notes = annotate_menu.addMenu(config.thisTranslation["menu_external_notes"])
        external_notes.addAction(QAction(config.thisTranslation["menu_new_note"], self, shortcut=sc.createNewNoteFile, triggered=self.createNewNoteFile))
        external_notes.addAction(QAction(config.thisTranslation["menu_open_note"], self, shortcut=sc.openTextFileDialog, triggered=self.openTextFileDialog))
        external_notes.addAction(QAction(config.thisTranslation["menu_read_note"], self, shortcut=sc.externalFileButtonClicked, triggered=self.externalFileButtonClicked))
        external_notes.addAction(QAction(config.thisTranslation["menu_edit_note"], self, shortcut=sc.editExternalFileButtonClicked, triggered=self.editExternalFileButtonClicked))
        if config.enableGist:
            annotate_menu.addAction(
                QAction(config.thisTranslation["menu_gist"], self, shortcut=sc.showGistWindow, triggered=self.showGistWindow))

        library_menu = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_library"]))
        library_menu.addAction(QAction(config.thisTranslation["menu4_words"], self, shortcut=sc.runWORDS, triggered=self.runWORDS))
        library_menu.addAction(QAction(config.thisTranslation["menu4_commentary"], self, shortcut=sc.runCOMMENTARY, triggered=self.runCOMMENTARY))
        library_menu.addAction(QAction(config.thisTranslation["menu4_crossRef"], self, shortcut=sc.runCROSSREFERENCE, triggered=self.runCROSSREFERENCE))
        library_menu.addAction(QAction(config.thisTranslation["menu4_tske"], self, shortcut=sc.runTSKE, triggered=self.runTSKE))
        library_menu.addAction(QAction(config.thisTranslation["menu4_discourse"], self, shortcut=sc.runDISCOURSE, triggered=self.runDISCOURSE))
        library_menu.addAction(QAction(config.thisTranslation["menu4_tdw"], self, shortcut=sc.runCOMBO, triggered=self.runCOMBO))
        library_menu.addAction(QAction(config.thisTranslation["menu4_book"], self, shortcut=sc.bookFeatures, triggered=self.bookFeatures))
        library_menu.addAction(QAction(config.thisTranslation["menu4_chapter"], self, shortcut=sc.chapterFeatures, triggered=self.chapterFeatures))

        menu_data = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_data"]))
        menu_data.addAction(QAction(config.thisTranslation["menu8_bibles"], self, triggered=self.installMarvelBibles))
        menu_data.addAction(QAction(config.thisTranslation["menu8_commentaries"], self, triggered=self.installMarvelCommentaries))
        menu_data.addAction(QAction(config.thisTranslation["menu8_datasets"], self, triggered=self.installMarvelDatasets))
        menu_data.addAction(QAction(config.thisTranslation["menu8_plusLexicons"], self, triggered=self.importBBPlusLexiconInAFolder))
        menu_data.addAction(QAction(config.thisTranslation["menu8_plusDictionaries"], self, triggered=self.importBBPlusDictionaryInAFolder))
        menu_data.addSeparator()
        menu_data.addAction(QAction(config.thisTranslation["menu8_download3rdParty"], self, triggered=self.moreBooks))
        menu_data.addAction(QAction(config.thisTranslation["menu8_3rdParty"], self, triggered=self.importModules))
        menu_data.addAction(QAction(config.thisTranslation["menu8_3rdPartyInFolder"], self, triggered=self.importModulesInFolder))
        menu_data.addAction(QAction(config.thisTranslation["menu8_settings"], self, triggered=self.importSettingsDialog))
        menu_data.addSeparator()
        menu_data.addAction(QAction(config.thisTranslation["menu8_fixDatabase"], self, triggered=self.selectDatabaseToFix))

        display_menu = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_display"]))
        bible_format_menu = display_menu.addMenu(config.thisTranslation["menu_bible_format"])
        bible_format_menu.addAction(QAction(config.thisTranslation["menu_simple_formatted"], self, shortcut=sc.enableParagraphButtonClicked,
                                         triggered=self.enableParagraphButtonClicked))
        bible_format_menu.addAction(QAction(config.thisTranslation["menu_subheadings"], self, shortcut=sc.enableSubheadingButtonClicked,
                                            triggered=self.enableSubheadingButtonClicked))
        screenSizeMenu = display_menu.addMenu(config.thisTranslation["menu1_screenSize"])
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_fullScreen"], self, shortcut=sc.fullsizeWindow,
                                         triggered=self.fullsizeWindow))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_smallSize"], self, shortcut=sc.twoThirdWindow,
                                         triggered=self.twoThirdWindow))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_topHalf"], self, shortcut=sc.topHalfScreenHeight,
                                         triggered=self.topHalfScreenHeight))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_bottomHalf"], self, shortcut=sc.bottomHalfScreenHeight,
                                         triggered=self.bottomHalfScreenHeight))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_leftHalf"], self, shortcut=sc.leftHalfScreenWidth,
                                         triggered=self.leftHalfScreenWidth))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_rightHalf"], self, shortcut=sc.rightHalfScreenWidth,
                                         triggered=self.rightHalfScreenWidth))
        window_menu = display_menu.addMenu(config.thisTranslation["menu_window"])
        window_menu.addAction(QAction(config.thisTranslation["menu2_study"], self, shortcut=sc.parallel, triggered=self.parallel))
        window_menu.addAction(QAction(config.thisTranslation["menu2_bottom"], self, shortcut=sc.cycleInstant, triggered=self.cycleInstant))
        window_menu.addAction(QAction(config.thisTranslation["menu2_landscape"], self, shortcut=sc.switchLandscapeMode, triggered=self.switchLandscapeMode))
        toolbar_menu = display_menu.addMenu(config.thisTranslation["menu_toolbar"])
        toolbar_menu.addAction(QAction(config.thisTranslation["menu2_all"], self, shortcut=sc.setNoToolBar, triggered=self.setNoToolBar))
        toolbar_menu.addAction(QAction(config.thisTranslation["menu2_top"], self, shortcut=sc.hideShowMainToolBar, triggered=self.hideShowMainToolBar))
        toolbar_menu.addAction(QAction(config.thisTranslation["menu2_topOnly"], self, shortcut=sc.hideShowAdditionalToolBar, triggered=self.hideShowAdditionalToolBar))
        toolbar_menu.addAction(QAction(config.thisTranslation["menu2_second"], self, shortcut=sc.hideShowSecondaryToolBar, triggered=self.hideShowSecondaryToolBar))
        toolbar_menu.addAction(QAction(config.thisTranslation["menu2_sidebars"], self, shortcut=sc.hideShowSideToolBars, triggered=self.hideShowSideToolBars))
        toolbar_menu.addAction(QAction(config.thisTranslation["menu2_left"], self, shortcut=sc.hideShowLeftToolBar, triggered=self.hideShowLeftToolBar))
        toolbar_menu.addAction(QAction(config.thisTranslation["menu2_right"], self, shortcut=sc.hideShowRightToolBar, triggered=self.hideShowRightToolBar))
        toolbar_menu.addAction(QAction(config.thisTranslation["menu2_icons"], self, shortcut=sc.switchIconSize, triggered=self.switchIconSize))
        font_menu = display_menu.addMenu(config.thisTranslation["menu_font"])
        font_menu.addAction(QAction(config.thisTranslation["menu_select_default_font"], self, shortcut=sc.setDefaultFont, triggered=self.setDefaultFont))
        font_menu.addAction(QAction(config.thisTranslation["menu2_larger"], self, shortcut=sc.largerFont, triggered=self.largerFont))
        font_menu.addAction(QAction(config.thisTranslation["menu2_smaller"], self, shortcut=sc.smallerFont, triggered=self.smallerFont))
        display_menu.addAction(
            QAction(config.thisTranslation["menu_display_shortcuts"], self, shortcut=sc.displayShortcuts, triggered=self.displayShortcuts))
        display_menu.addAction(
            QAction(config.thisTranslation["menu_reload"], self, shortcut=sc.reloadCurrentRecord, triggered=self.reloadCurrentRecord))

        if config.enableMacros:
            macros_menu = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_macros"]))
            run_macros_menu = macros_menu.addMenu(config.thisTranslation["menu_run"])
            self.loadRunMacrosMenu(run_macros_menu)
            build_macros_menu = macros_menu.addMenu(config.thisTranslation["menu_build_macro"])
            build_macros_menu.addAction(QAction(config.thisTranslation["menu_command"], self, triggered=self.macroSaveCommand))
            build_macros_menu.addAction(QAction(config.thisTranslation["menu_highlight"], self, triggered=self.macroSaveHighlights))

        about_menu = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_about"]))
        about_menu.addAction(QAction(config.thisTranslation["menu_wiki"], self, triggered=self.openUbaWiki))
        about_menu.addAction(QAction(config.thisTranslation["menu_discussions"], self, triggered=self.openUbaDiscussions))
        apps = about_menu.addMenu(config.thisTranslation["menu_apps"])
        apps.addAction(QAction("BibleTools.app", self, triggered=self.openBibleTools))
        apps.addAction(QAction("UniqueBible.app", self, triggered=self.openUniqueBible))
        apps.addAction(QAction("Marvel.bible", self, triggered=self.openMarvelBible))
        apps.addAction(QAction("BibleBento.com", self, triggered=self.openBibleBento))
        apps.addAction(QAction("OpenGNT.com", self, triggered=self.openOpenGNT))
        apps.addAction(QAction("Unique Bible", self, triggered=self.openUniqueBibleSource))
        apps.addAction(QAction("Open Hebrew Bible", self, triggered=self.openHebrewBibleSource))
        apps.addAction(QAction("Open Greek New Testament", self, triggered=self.openOpenGNTSource))
        apps.addAction(QAction("GitHub Repositories", self, triggered=self.openSource))
        about_menu.addAction(QAction(config.thisTranslation["menu9_contact"], self, triggered=self.contactEliranWong))
        about_menu.addAction(QAction(config.thisTranslation["menu_donate"], self, triggered=self.donateToUs))

    def setupToolBarStandardIconSize(self):

        textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"

        self.firstToolBar = QToolBar()
        self.firstToolBar.setWindowTitle(config.thisTranslation["bar1_title"])
        self.firstToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.firstToolBar)

        self.mainRefButton = QPushButton(self.verseReference("main")[1])
        self.mainRefButton.setToolTip(config.thisTranslation["bar1_reference"])
        self.mainRefButton.setStyleSheet(textButtonStyle)
        self.mainRefButton.clicked.connect(self.mainRefButtonClicked)
        self.firstToolBar.addWidget(self.mainRefButton)

        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        if config.qtMaterial and config.qtMaterialTheme:
            config.iconButtonWidth = self.mainRefButton.height()

        searchBibleButton = QPushButton()
        searchBibleButton.setToolTip(config.thisTranslation["bar1_searchBibles"])
        searchBibleButtonFile = os.path.join("htmlResources", "search_plus.png")
        searchBibleButton.setIcon(QIcon(searchBibleButtonFile))
        searchBibleButton.clicked.connect(self.displaySearchBibleMenu)
        self.firstToolBar.addWidget(searchBibleButton)

        openChapterNoteButton = QPushButton()
        #openChapterNoteButton.setFixedSize(40, 40)
        #openChapterNoteButton.setBaseSize(70, 70)
        openChapterNoteButton.setToolTip(config.thisTranslation["bar1_chapterNotes"])
        openChapterNoteButtonFile = os.path.join("htmlResources", "noteChapter.png")
        openChapterNoteButton.setIcon(QIcon(openChapterNoteButtonFile))
        openChapterNoteButton.clicked.connect(self.openMainChapterNote)
        self.firstToolBar.addWidget(openChapterNoteButton)
        #t = self.firstToolBar.addAction(QIcon(openChapterNoteButtonFile), "Main View Chapter Notes", self.openMainChapterNote)
        #openChapterNoteButtonFile = os.path.join("htmlResources", "search.png")
        #t.setIcon(QIcon(openChapterNoteButtonFile))

        openVerseNoteButton = QPushButton()
        openVerseNoteButton.setToolTip(config.thisTranslation["bar1_verseNotes"])
        openVerseNoteButtonFile = os.path.join("htmlResources", "noteVerse.png")
        openVerseNoteButton.setIcon(QIcon(openVerseNoteButtonFile))
        openVerseNoteButton.clicked.connect(self.openMainVerseNote)
        self.firstToolBar.addWidget(openVerseNoteButton)


        # searchBibleButton = QPushButton()
        # searchBibleButton.setToolTip(config.thisTranslation["bar1_searchBible"])
        # searchBibleButtonFile = os.path.join("htmlResources", "search.png")
        # searchBibleButton.setIcon(QIcon(searchBibleButtonFile))
        # searchBibleButton.clicked.connect(self.displaySearchBibleCommand)
        # self.firstToolBar.addWidget(searchBibleButton)

        previousBookButton = QPushButton()
        previousBookButton.setToolTip(config.thisTranslation["menu_previous_book"])
        previousBookButton.setText("<<")
        previousBookButton.clicked.connect(self.previousMainBook)
        self.firstToolBar.addWidget(previousBookButton)

        previousChapterButton = QPushButton()
        previousChapterButton.setToolTip(config.thisTranslation["menu_previous_chapter"])
        previousChapterButton.setText("<")
        previousChapterButton.clicked.connect(self.previousMainChapter)
        self.firstToolBar.addWidget(previousChapterButton)

        nextChapterButton = QPushButton()
        nextChapterButton.setToolTip(config.thisTranslation["menu_next_chapter"])
        nextChapterButton.setText(">")
        nextChapterButton.clicked.connect(self.nextMainChapter)
        self.firstToolBar.addWidget(nextChapterButton)

        nextBookButton = QPushButton()
        nextBookButton.setToolTip(config.thisTranslation["menu_next_book"])
        nextBookButton.setText(">>")
        nextBookButton.clicked.connect(self.nextMainBook)
        self.firstToolBar.addWidget(nextBookButton)

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.setClearButtonEnabled(True)
        self.textCommandLineEdit.setToolTip(config.thisTranslation["bar1_command"])
        self.textCommandLineEdit.setMinimumWidth(100)
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        if not config.preferControlPanelForCommandLineEntry:
            self.firstToolBar.addWidget(self.textCommandLineEdit)

        self.firstToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["bar1_toolbars"])
        actionButtonFile = os.path.join("htmlResources", "toolbar.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.hideShowAdditionalToolBar)
        self.firstToolBar.addWidget(actionButton)

        if config.addBreakAfterTheFirstToolBar:
            self.addToolBarBreak()

        self.studyBibleToolBar = QToolBar()
        self.studyBibleToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.studyBibleToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.studyBibleToolBar)

        self.studyRefButton = QPushButton(self.verseReference("study")[1])
        self.studyRefButton.setToolTip(config.thisTranslation["bar2_reference"])
        self.studyRefButton.setStyleSheet(textButtonStyle)
        self.studyRefButton.clicked.connect(self.studyRefButtonClicked)
        self.studyBibleToolBar.addWidget(self.studyRefButton)

        # openStudyChapterNoteButton = QPushButton()
        # openStudyChapterNoteButton.setToolTip(config.thisTranslation["bar2_chapterNotes"])
        # openStudyChapterNoteButtonFile = os.path.join("htmlResources", "noteChapter.png")
        # openStudyChapterNoteButton.setIcon(QIcon(openStudyChapterNoteButtonFile))
        # openStudyChapterNoteButton.clicked.connect(self.openStudyChapterNote)
        # self.studyBibleToolBar.addWidget(openStudyChapterNoteButton)

        # openStudyVerseNoteButton = QPushButton()
        # openStudyVerseNoteButton.setToolTip(config.thisTranslation["bar2_verseNotes"])
        # openStudyVerseNoteButtonFile = os.path.join("htmlResources", "noteVerse.png")
        # openStudyVerseNoteButton.setIcon(QIcon(openStudyVerseNoteButtonFile))
        # openStudyVerseNoteButton.clicked.connect(self.openStudyVerseNote)
        # self.studyBibleToolBar.addWidget(openStudyVerseNoteButton)

        # searchStudyBibleButton = QPushButton()
        # searchStudyBibleButton.setToolTip(config.thisTranslation["bar2_searchBible"])
        # searchStudyBibleButtonFile = os.path.join("htmlResources", "search.png")
        # searchStudyBibleButton.setIcon(QIcon(searchStudyBibleButtonFile))
        # searchStudyBibleButton.clicked.connect(self.displaySearchStudyBibleCommand)
        # self.studyBibleToolBar.addWidget(searchStudyBibleButton)

        searchStudyBibleButton = QPushButton()
        searchStudyBibleButton.setToolTip(config.thisTranslation["bar2_searchBibles"])
        searchStudyBibleButtonFile = os.path.join("htmlResources", "search_plus.png")
        searchStudyBibleButton.setIcon(QIcon(searchStudyBibleButtonFile))
        searchStudyBibleButton.clicked.connect(self.displaySearchBibleMenu)
        self.studyBibleToolBar.addWidget(searchStudyBibleButton)

        self.enableSyncStudyWindowBibleButton = QPushButton()
        self.enableSyncStudyWindowBibleButton.setToolTip(self.getSyncStudyWindowBibleDisplayToolTip())
        enableSyncStudyWindowBibleButtonFile = os.path.join("htmlResources", self.getSyncStudyWindowBibleDisplay())
        self.enableSyncStudyWindowBibleButton.setIcon(QIcon(enableSyncStudyWindowBibleButtonFile))
        self.enableSyncStudyWindowBibleButton.clicked.connect(self.enableSyncStudyWindowBibleButtonClicked)
        self.studyBibleToolBar.addWidget(self.enableSyncStudyWindowBibleButton)

        if config.addBreakBeforeTheLastToolBar:
            self.addToolBarBreak()

        self.secondToolBar = QToolBar()
        self.secondToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.secondToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.secondToolBar)

        self.enableStudyBibleButton = QPushButton()
        self.enableStudyBibleButton.setToolTip(self.getStudyBibleDisplayToolTip())
        enableStudyBibleButtonFile = os.path.join("htmlResources", self.getStudyBibleDisplay())
        self.enableStudyBibleButton.setIcon(QIcon(enableStudyBibleButtonFile))
        self.enableStudyBibleButton.clicked.connect(self.enableStudyBibleButtonClicked)
        self.secondToolBar.addWidget(self.enableStudyBibleButton)

        self.secondToolBar.addSeparator()

        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
        self.commentaryRefButton.setToolTip(config.thisTranslation["menu4_commentary"])
        self.commentaryRefButton.setStyleSheet(textButtonStyle)
        self.commentaryRefButton.clicked.connect(self.commentaryRefButtonClicked)
        self.secondToolBar.addWidget(self.commentaryRefButton)

        self.enableSyncCommentaryButton = QPushButton()
        self.enableSyncCommentaryButton.setToolTip(self.getSyncCommentaryDisplayToolTip())
        enableSyncCommentaryButtonFile = os.path.join("htmlResources", self.getSyncCommentaryDisplay())
        self.enableSyncCommentaryButton.setIcon(QIcon(enableSyncCommentaryButtonFile))
        self.enableSyncCommentaryButton.clicked.connect(self.enableSyncCommentaryButtonClicked)
        self.secondToolBar.addWidget(self.enableSyncCommentaryButton)

        self.secondToolBar.addSeparator()

        openFileButton = QPushButton()
        openFileButton.setToolTip(config.thisTranslation["menu10_dialog"])
        openFileButtonFile = os.path.join("htmlResources", "open.png")
        openFileButton.setIcon(QIcon(openFileButtonFile))
        openFileButton.clicked.connect(self.openBookDialog)
        self.secondToolBar.addWidget(openFileButton)

        self.bookButton = QPushButton(config.book)
        self.bookButton.setToolTip(config.thisTranslation["menu5_book"])
        self.bookButton.setStyleSheet(textButtonStyle)
        self.bookButton.clicked.connect(self.openBookMenu)
        self.secondToolBar.addWidget(self.bookButton)

        previousChapterButton = QPushButton()
        previousChapterButton.setToolTip(config.thisTranslation["menu_previous_chapter"])
        previousChapterButton.setText("<")
        previousChapterButton.clicked.connect(self.openBookPreviousChapter)
        previousChapterButton.setShortcut(sc.previousChapterButton)
        self.secondToolBar.addWidget(previousChapterButton)

        nextChapterButton = QPushButton()
        nextChapterButton.setToolTip(config.thisTranslation["menu_next_chapter"])
        nextChapterButton.setText(">")
        nextChapterButton.clicked.connect(self.openBookNextChapter)
        nextChapterButton.setShortcut(sc.nextChapterButton)
        self.secondToolBar.addWidget(nextChapterButton)

        searchBookButton = QPushButton()
        searchBookButton.setToolTip(config.thisTranslation["bar2_searchBooks"])
        searchBookButtonFile = os.path.join("htmlResources", "search.png")
        searchBookButton.setIcon(QIcon(searchBookButtonFile))
        searchBookButton.clicked.connect(self.displaySearchBookCommand)
        self.secondToolBar.addWidget(searchBookButton)

        self.secondToolBar.addSeparator()

        newFileButton = QPushButton()
        newFileButton.setToolTip(config.thisTranslation["menu7_create"])
        newFileButtonFile = os.path.join("htmlResources", "newfile.png")
        newFileButton.setIcon(QIcon(newFileButtonFile))
        newFileButton.clicked.connect(self.createNewNoteFile)
        self.secondToolBar.addWidget(newFileButton)

        openFileButton = QPushButton()
        openFileButton.setToolTip(config.thisTranslation["menu7_open"])
        openFileButtonFile = os.path.join("htmlResources", "open.png")
        openFileButton.setIcon(QIcon(openFileButtonFile))
        openFileButton.clicked.connect(self.openTextFileDialog)
        self.secondToolBar.addWidget(openFileButton)

        self.externalFileButton = QPushButton(self.getLastExternalFileName())
        self.externalFileButton.setToolTip(config.thisTranslation["menu7_read"])
        self.externalFileButton.setStyleSheet(textButtonStyle)
        self.externalFileButton.clicked.connect(self.externalFileButtonClicked)
        self.secondToolBar.addWidget(self.externalFileButton)

        editExternalFileButton = QPushButton()
        editExternalFileButton.setToolTip(config.thisTranslation["menu7_edit"])
        editExternalFileButtonFile = os.path.join("htmlResources", "edit.png")
        editExternalFileButton.setIcon(QIcon(editExternalFileButtonFile))
        editExternalFileButton.clicked.connect(self.editExternalFileButtonClicked)
        self.secondToolBar.addWidget(editExternalFileButton)

        reloadButton = QPushButton()
        reloadButton.setToolTip(config.thisTranslation["menu1_reload"])
        reloadButtonFile = os.path.join("htmlResources", "reload.png")
        reloadButton.setIcon(QIcon(reloadButtonFile))
        reloadButton.clicked.connect(self.reloadCurrentRecord)
        self.secondToolBar.addWidget(reloadButton)

        self.secondToolBar.addSeparator()

        self.leftToolBar = QToolBar()
        self.leftToolBar.setWindowTitle(config.thisTranslation["bar3_title"])
        self.leftToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.LeftToolBarArea, self.leftToolBar)

        backButton = QPushButton()
        backButton.setToolTip(config.thisTranslation["menu3_mainBack"])
        leftButtonFile = os.path.join("htmlResources", "left.png")
        backButton.setIcon(QIcon(leftButtonFile))
        backButton.clicked.connect(self.back)
        self.leftToolBar.addWidget(backButton)

        mainHistoryButton = QPushButton()
        mainHistoryButton.setToolTip(config.thisTranslation["menu3_main"])
        mainHistoryButtonFile = os.path.join("htmlResources", "history.png")
        mainHistoryButton.setIcon(QIcon(mainHistoryButtonFile))
        mainHistoryButton.clicked.connect(self.mainHistoryButtonClicked)
        self.leftToolBar.addWidget(mainHistoryButton)

        forwardButton = QPushButton()
        forwardButton.setToolTip(config.thisTranslation["menu3_mainForward"])
        rightButtonFile = os.path.join("htmlResources", "right.png")
        forwardButton.setIcon(QIcon(rightButtonFile))
        forwardButton.clicked.connect(self.forward)
        self.leftToolBar.addWidget(forwardButton)

        self.leftToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["tab_print"])
        actionButtonFile = os.path.join("htmlResources", "pdf.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.printMainPage)
        self.leftToolBar.addWidget(actionButton)

        self.leftToolBar.addSeparator()

        self.enableParagraphButton = QPushButton()
        self.enableParagraphButton.setToolTip(config.thisTranslation["menu2_format"])
        enableParagraphButtonFile = os.path.join("htmlResources", self.getReadFormattedBibles())
        self.enableParagraphButton.setIcon(QIcon(enableParagraphButtonFile))
        self.enableParagraphButton.clicked.connect(self.enableParagraphButtonClicked)
        self.leftToolBar.addWidget(self.enableParagraphButton)

        self.enableSubheadingButton = QPushButton()
        self.enableSubheadingButton.setToolTip(config.thisTranslation["menu2_subHeadings"])
        enableSubheadingButtonFile = os.path.join("htmlResources", self.getAddSubheading())
        self.enableSubheadingButton.setIcon(QIcon(enableSubheadingButtonFile))
        self.enableSubheadingButton.clicked.connect(self.enableSubheadingButtonClicked)
        self.leftToolBar.addWidget(self.enableSubheadingButton)

        # self.leftToolBar.addSeparator()
        #
        # actionButton = QPushButton()
        # actionButton.setToolTip(config.thisTranslation["menu4_previous"])
        # actionButtonFile = os.path.join("htmlResources", "previousChapter.png")
        # actionButton.setIcon(QIcon(actionButtonFile))
        # actionButton.clicked.connect(self.previousMainChapter)
        # self.leftToolBar.addWidget(actionButton)

        #        actionButton = QPushButton()
        #        actionButton.setToolTip(config.thisTranslation["bar1_reference"])
        #        actionButtonFile = os.path.join("htmlResources", "bible.png")
        #        actionButton.setIcon(QIcon(actionButtonFile))
        #        actionButton.clicked.connect(self.openMainChapter)
        #        self.leftToolBar.addWidget(actionButton)

        # actionButton = QPushButton()
        # actionButton.setToolTip(config.thisTranslation["menu4_next"])
        # actionButtonFile = os.path.join("htmlResources", "nextChapter.png")
        # actionButton.setIcon(QIcon(actionButtonFile))
        # actionButton.clicked.connect(self.nextMainChapter)
        # self.leftToolBar.addWidget(actionButton)

        self.leftToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_compareAll"])
        actionButtonFile = os.path.join("htmlResources", "compare_with.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runCOMPARE)
        self.leftToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_moreComparison"])
        actionButtonFile = os.path.join("htmlResources", "parallel_with.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.mainRefButtonClicked)
        self.leftToolBar.addWidget(actionButton)

        self.enforceCompareParallelButton = QPushButton()
        self.enforceCompareParallelButton.setToolTip(self.getEnableCompareParallelDisplayToolTip())
        enforceCompareParallelButtonFile = os.path.join("htmlResources", self.getEnableCompareParallelDisplay())
        self.enforceCompareParallelButton.setIcon(QIcon(enforceCompareParallelButtonFile))
        self.enforceCompareParallelButton.clicked.connect(self.enforceCompareParallelButtonClicked)
        self.leftToolBar.addWidget(self.enforceCompareParallelButton)

        self.leftToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip("Marvel Original Bible")
        actionButtonFile = os.path.join("htmlResources", "original.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runMOB)
        self.leftToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip("Marvel Interlinear Bible")
        actionButtonFile = os.path.join("htmlResources", "interlinear.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runMIB)
        self.leftToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip("Marvel Trilingual Bible")
        actionButtonFile = os.path.join("htmlResources", "trilingual.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runMTB)
        self.leftToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip("Marvel Parallel Bible")
        actionButtonFile = os.path.join("htmlResources", "line.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runMPB)
        self.leftToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip("Marvel Annotated Bible")
        actionButtonFile = os.path.join("htmlResources", "annotated.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runMAB)
        self.leftToolBar.addWidget(actionButton)

        self.leftToolBar.addSeparator()

        self.rightToolBar = QToolBar()
        self.rightToolBar.setWindowTitle(config.thisTranslation["bar4_title"])
        self.rightToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.RightToolBarArea, self.rightToolBar)

        studyBackButton = QPushButton()
        studyBackButton.setToolTip(config.thisTranslation["menu3_studyBack"])
        leftButtonFile = os.path.join("htmlResources", "left.png")
        studyBackButton.setIcon(QIcon(leftButtonFile))
        studyBackButton.clicked.connect(self.studyBack)
        self.rightToolBar.addWidget(studyBackButton)

        studyHistoryButton = QPushButton()
        studyHistoryButton.setToolTip(config.thisTranslation["menu3_study"])
        studyHistoryButtonFile = os.path.join("htmlResources", "history.png")
        studyHistoryButton.setIcon(QIcon(studyHistoryButtonFile))
        studyHistoryButton.clicked.connect(self.studyHistoryButtonClicked)
        self.rightToolBar.addWidget(studyHistoryButton)

        studyForwardButton = QPushButton()
        studyForwardButton.setToolTip(config.thisTranslation["menu3_studyForward"])
        rightButtonFile = os.path.join("htmlResources", "right.png")
        studyForwardButton.setIcon(QIcon(rightButtonFile))
        studyForwardButton.clicked.connect(self.studyForward)
        self.rightToolBar.addWidget(studyForwardButton)

        self.rightToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["tab_print"])
        actionButtonFile = os.path.join("htmlResources", "pdf.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.printStudyPage)
        self.rightToolBar.addWidget(actionButton)

        self.rightToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_indexes"])
        actionButtonFile = os.path.join("htmlResources", "indexes.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runINDEX)
        self.rightToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_commentary"])
        actionButtonFile = os.path.join("htmlResources", "commentary.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runCOMMENTARY)
        self.rightToolBar.addWidget(actionButton)

        self.rightToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_crossRef"])
        actionButtonFile = os.path.join("htmlResources", "cross_reference.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runCROSSREFERENCE)
        self.rightToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_tske"])
        actionButtonFile = os.path.join("htmlResources", "treasure.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runTSKE)
        self.rightToolBar.addWidget(actionButton)

        self.rightToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_traslations"])
        actionButtonFile = os.path.join("htmlResources", "translations.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runTRANSLATION)
        self.rightToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_discourse"])
        actionButtonFile = os.path.join("htmlResources", "discourse.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runDISCOURSE)
        self.rightToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_words"])
        actionButtonFile = os.path.join("htmlResources", "words.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runWORDS)
        self.rightToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_tdw"])
        actionButtonFile = os.path.join("htmlResources", "combo.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runCOMBO)
        self.rightToolBar.addWidget(actionButton)

        self.rightToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu2_landscape"])
        actionButtonFile = os.path.join("htmlResources", "portrait.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.switchLandscapeMode)
        self.rightToolBar.addWidget(actionButton)

        parallelButton = QPushButton()
        parallelButton.setToolTip(config.thisTranslation["menu2_study"])
        parallelButtonFile = os.path.join("htmlResources", "parallel.png")
        parallelButton.setIcon(QIcon(parallelButtonFile))
        parallelButton.clicked.connect(self.parallel)
        self.rightToolBar.addWidget(parallelButton)

        self.rightToolBar.addSeparator()

        self.enableInstantButton = QPushButton()
        self.enableInstantButton.setToolTip(config.thisTranslation["menu2_hover"])
        enableInstantButtonFile = os.path.join("htmlResources", self.getInstantInformation())
        self.enableInstantButton.setIcon(QIcon(enableInstantButtonFile))
        self.enableInstantButton.clicked.connect(self.enableInstantButtonClicked)
        self.rightToolBar.addWidget(self.enableInstantButton)

        instantButton = QPushButton()
        instantButton.setToolTip(config.thisTranslation["menu2_bottom"])
        instantButtonFile = os.path.join("htmlResources", "lightning.png")
        instantButton.setIcon(QIcon(instantButtonFile))
        instantButton.clicked.connect(self.cycleInstant)
        self.rightToolBar.addWidget(instantButton)

        self.rightToolBar.addSeparator()

    def setupToolBarFullIconSize(self):

        textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"

        self.firstToolBar = QToolBar()
        self.firstToolBar.setWindowTitle(config.thisTranslation["bar1_title"])
        self.firstToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.firstToolBar)

        self.mainRefButton = QPushButton(self.verseReference("main")[1])
        self.mainRefButton.setToolTip(config.thisTranslation["bar1_reference"])
        self.mainRefButton.setStyleSheet(textButtonStyle)
        self.mainRefButton.clicked.connect(self.mainRefButtonClicked)
        self.firstToolBar.addWidget(self.mainRefButton)

        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        if config.qtMaterial and config.qtMaterialTheme:
            config.iconButtonWidth = self.mainRefButton.height()

        iconFile = os.path.join("htmlResources", "noteChapter.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_chapterNotes"], self.openMainChapterNote)

        iconFile = os.path.join("htmlResources", "noteVerse.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_verseNotes"], self.openMainVerseNote)

        previousBookButton = QPushButton()
        previousBookButton.setToolTip(config.thisTranslation["menu_previous_book"])
        previousBookButton.setText("<<")
        previousBookButton.clicked.connect(self.previousMainBook)
        self.firstToolBar.addWidget(previousBookButton)

        previousChapterButton = QPushButton()
        previousChapterButton.setToolTip(config.thisTranslation["menu_previous_chapter"])
        previousChapterButton.setText("<")
        previousChapterButton.clicked.connect(self.previousMainChapter)
        self.firstToolBar.addWidget(previousChapterButton)

        nextChapterButton = QPushButton()
        nextChapterButton.setToolTip(config.thisTranslation["menu_next_chapter"])
        nextChapterButton.setText(">")
        nextChapterButton.clicked.connect(self.nextMainChapter)
        self.firstToolBar.addWidget(nextChapterButton)

        nextBookButton = QPushButton()
        nextBookButton.setToolTip(config.thisTranslation["menu_next_book"])
        nextBookButton.setText(">>")
        nextBookButton.clicked.connect(self.nextMainBook)
        self.firstToolBar.addWidget(nextBookButton)

        self.firstToolBar.addSeparator()

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.setToolTip(config.thisTranslation["bar1_command"])
        self.textCommandLineEdit.setMinimumWidth(100)
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        
        if not config.preferControlPanelForCommandLineEntry:
            self.firstToolBar.addWidget(self.textCommandLineEdit)

        self.firstToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "toolbar.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_toolbars"], self.hideShowAdditionalToolBar)

        if config.addBreakAfterTheFirstToolBar:
            self.addToolBarBreak()

        self.studyBibleToolBar = QToolBar()
        self.studyBibleToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.studyBibleToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.studyBibleToolBar)

        self.studyRefButton = QPushButton(self.verseReference("study")[1])
        self.studyRefButton.setToolTip(config.thisTranslation["bar2_reference"])
        self.studyRefButton.setStyleSheet(textButtonStyle)
        self.studyRefButton.clicked.connect(self.studyRefButtonClicked)
        self.studyBibleToolBar.addWidget(self.studyRefButton)

        iconFile = os.path.join("htmlResources", "noteChapter.png")
        self.studyBibleToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar2_chapterNotes"], self.openStudyChapterNote)

        iconFile = os.path.join("htmlResources", "noteVerse.png")
        self.studyBibleToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar2_verseNotes"], self.openStudyVerseNote)

        iconFile = os.path.join("htmlResources", "search.png")
        self.studyBibleToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar2_searchBible"], self.displaySearchStudyBibleCommand)

        iconFile = os.path.join("htmlResources", "search_plus.png")
        self.studyBibleToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar2_searchBibles"], self.displaySearchBibleMenu)

        iconFile = os.path.join("htmlResources", self.getSyncStudyWindowBibleDisplay())
        self.enableSyncStudyWindowBibleButton = self.studyBibleToolBar.addAction(QIcon(iconFile), self.getSyncStudyWindowBibleDisplayToolTip(), self.enableSyncStudyWindowBibleButtonClicked)

        if config.addBreakBeforeTheLastToolBar:
            self.addToolBarBreak()

        self.secondToolBar = QToolBar()
        self.secondToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.secondToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.secondToolBar)

        iconFile = os.path.join("htmlResources", self.getStudyBibleDisplay())
        self.enableStudyBibleButton = self.secondToolBar.addAction(QIcon(iconFile), self.getStudyBibleDisplayToolTip(), self.enableStudyBibleButtonClicked)

        self.secondToolBar.addSeparator()

        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
        self.commentaryRefButton.setToolTip(config.thisTranslation["menu4_commentary"])
        self.commentaryRefButton.setStyleSheet(textButtonStyle)
        self.commentaryRefButton.clicked.connect(self.commentaryRefButtonClicked)
        self.secondToolBar.addWidget(self.commentaryRefButton)

        iconFile = os.path.join("htmlResources", self.getSyncCommentaryDisplay())
        self.enableSyncCommentaryButton = self.secondToolBar.addAction(QIcon(iconFile), self.getSyncCommentaryDisplayToolTip(), self.enableSyncCommentaryButtonClicked)

        self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "open.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu10_dialog"], self.openBookDialog)

        self.bookButton = QPushButton(config.book)
        self.bookButton.setToolTip(config.thisTranslation["menu5_book"])
        self.bookButton.setStyleSheet(textButtonStyle)
        self.bookButton.clicked.connect(self.openBookMenu)
        self.secondToolBar.addWidget(self.bookButton)

        previousChapterButton = QPushButton()
        previousChapterButton.setToolTip(config.thisTranslation["menu_previous_chapter"])
        previousChapterButton.setText("<")
        previousChapterButton.clicked.connect(self.openBookPreviousChapter)
        previousChapterButton.setShortcut(sc.previousChapterButton)
        self.secondToolBar.addWidget(previousChapterButton)

        nextChapterButton = QPushButton()
        nextChapterButton.setToolTip(config.thisTranslation["menu_next_chapter"])
        nextChapterButton.setText(">")
        nextChapterButton.clicked.connect(self.openBookNextChapter)
        nextChapterButton.setShortcut(sc.nextChapterButton)
        self.secondToolBar.addWidget(nextChapterButton)

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
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["tab_print"], self.printMainPage)

        self.leftToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", self.getReadFormattedBibles())
        self.enableParagraphButton = self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_format"], self.enableParagraphButtonClicked)

        iconFile = os.path.join("htmlResources", self.getAddSubheading())
        self.enableSubheadingButton = self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_subHeadings"], self.enableSubheadingButtonClicked)

        self.leftToolBar.addSeparator()

        # iconFile = os.path.join("htmlResources", "previousChapter.png")
        # self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_previous"], self.previousMainChapter)

        #        actionButton = QPushButton()
        #        actionButton.setToolTip(config.thisTranslation["bar1_reference"])
        #        actionButtonFile = os.path.join("htmlResources", "bible.png")
        #        actionButton.setIcon(QIcon(actionButtonFile))
        #        actionButton.clicked.connect(self.openMainChapter)
        #        self.leftToolBar.addWidget(actionButton)

        # iconFile = os.path.join("htmlResources", "nextChapter.png")
        # self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_next"], self.nextMainChapter)

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
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["tab_print"], self.printStudyPage)

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

        iconFile = os.path.join("htmlResources", "portrait.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_landscape"], self.switchLandscapeMode)

        iconFile = os.path.join("htmlResources", "parallel.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_study"], self.parallel)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", self.getInstantInformation())
        self.enableInstantButton = self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_hover"], self.enableInstantButtonClicked)

        iconFile = os.path.join("htmlResources", "lightning.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_bottom"], self.cycleInstant)

        self.rightToolBar.addSeparator()

        if config.qtMaterial and config.qtMaterialTheme:
            for toolbar in (self.firstToolBar, self.studyBibleToolBar, self.secondToolBar):
                toolbar.setIconSize(QSize(config.iconButtonWidth / 1.33, config.iconButtonWidth / 1.33))
                toolbar.setFixedHeight(config.iconButtonWidth + 4)
            for toolbar in (self.leftToolBar, self.rightToolBar):
                toolbar.setIconSize(QSize(config.iconButtonWidth * 0.6, config.iconButtonWidth * 0.6))
