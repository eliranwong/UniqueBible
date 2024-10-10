from uniquebible.gui.MenuItems import *
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QSize
else:
    from qtpy.QtCore import QSize
from uniquebible.util.ShortcutUtil import ShortcutUtil
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.WebtopUtil import WebtopUtil
import re, os
import shortcut as sc


class ClassicMainWindow:

    def create_menu(self):

        config.topToolBarOnly = False
        config.syncStudyWindowBibleWithMainWindow = False
        config.syncCommentaryWithMainWindow = False

        menuBar = self.menuBar()
        # 1st column
        menu = addMenu(menuBar, "menu1_app")
        if hasattr(config, "cli"):
            addMenuItem(menu, "cli", self, lambda: self.mainView.currentWidget().switchToCli(), sc.commandLineInterface)
            menu.addSeparator()
        items = (
            ("controlPanel", self.manageControlPanel, sc.manageControlPanel),
            ("menu1_miniControl", self.manageMiniControl, sc.manageMiniControl),
            ("libraryCatalog", self.showLibraryCatalogDialog, sc.showLibraryCatalogDialog),
        )
        for feature, action, shortcut in items:
            addMenuItem(menu, feature, self, action, shortcut)
        menu.addSeparator()
        subMenu = addSubMenu(menu, "controlPanel")
        for index, shortcut in enumerate((sc.openControlPanelTab0, sc.openControlPanelTab1, sc.openControlPanelTab2,
                                          sc.openControlPanelTab3, sc.openControlPanelTab4, sc.openControlPanelTab5,
                                          sc.openControlPanelTab6, sc.openControlPanelTab7)):
            addMenuItem(subMenu, "cp{0}".format(index), self, partial(self.openControlPanelTab, index), shortcut)
        menu.addSeparator()
        subMenu = addSubMenu(menu, "menu1_clipboard")
        items = (
            ("menu1_readClipboard", self.pasteFromClipboard, None),
            ("menu1_runClipboard", self.parseContentOnClipboard, sc.parseContentOnClipboard),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        menu.addSeparator()
        subMenu = addSubMenu(menu, "menu1_generalPreferences")
        items = (
            ("colourCustomisation", self.changeButtonColour, None),
            ("menu1_tabNo", self.setTabNumberDialog, None),
            ("setMaximumHistoryRecord", self.setMaximumHistoryRecordDialog, None),
            ("selectNoOfLinesPerChunkForParsing", self.setNoOfLinesPerChunkForParsingDialog, None),
            ("menu1_setAbbreviations", self.setBibleAbbreviations, None),
            ("resourceDirectory", self.customMarvelData, None),
            ("bibleCollections", self.showBibleCollectionDialog, sc.bibleCollections),
            ("menu1_setMyFavouriteBible", self.openFavouriteBibleDialog, None),
            ("menu1_setMyLanguage", self.openTranslationLanguageDialog, None),
            ("menu1_setDefaultStrongsHebrewLexicon", self.openSelectDefaultStrongsHebrewLexiconDialog, None),
            ("menu1_setDefaultStrongsGreekLexicon", self.openSelectDefaultStrongsGreekLexiconDialog, None),
            ("selectMaximumOHGBiVerses", self.setMaximumOHGBiVersesDisplayDialog, None),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        subMenu = addSubMenu(menu, "menu1_selectWindowStyle")
        for style in QStyleFactory.keys():
            addMenuItem(subMenu, style, self, lambda style=style: self.setAppWindowStyle(style), None, False)

        subMenu = addSubMenu(menu, "menu1_selectTheme")
        if config.qtMaterial:
            qtMaterialThemes = ["light_amber.xml",  "light_blue.xml",  "light_cyan.xml",  "light_cyan_500.xml",  "light_lightgreen.xml",  "light_pink.xml",  "light_purple.xml",  "light_red.xml",  "light_teal.xml",  "light_yellow.xml", "dark_amber.xml",  "dark_blue.xml",  "dark_cyan.xml",  "dark_lightgreen.xml",  "dark_pink.xml",  "dark_purple.xml",  "dark_red.xml",  "dark_teal.xml",  "dark_yellow.xml"]
            for theme in qtMaterialThemes:
                addMenuItem(subMenu, theme[:-4], self, lambda theme=theme: self.setQtMaterialTheme(theme), None, False)
        else:
            items = (
                ("menu_light_theme", lambda: self.setTheme("default")),
                ("menu1_dark_theme", lambda: self.setTheme("dark")),
                ("night_theme", lambda: self.setTheme("night")),
            )
            for feature, action in items:
                addMenuItem(subMenu, feature, self, action, shortcut)

            subMenu.addSeparator()
            themes = (
                "Light MediumVioletRed",
                "Light Tomato",
                "Light DarkOrange",
                "Light DarkRed",
                "Light Indigo",
                "Light DarkSlateBlue",
                "Light DarkGreen",
                "Light DarkOliveGreen",
                "Light Teal",
                "Light DarkBlue",
                "Light MidnightBlue",
                "Light DarkGoldenrod",
                "Light SaddleBrown",
                "Light Maroon",
                "Light DarkSlateGray",
            )
            for theme in themes:
                color = theme.split(" ")[-1]
                addColorIconMenuItem(color, subMenu, theme, self, partial(self.setTheme, theme), None, False)
            subSubMenu = addSubMenu(subMenu, "menu_more")
            addAllThemeColorMenuItem("Light", subSubMenu, self, self.setTheme)
            subMenu.addSeparator()
            themes = (
                "Dark Pink",
                "Dark LightYellow",
                "Dark LightGoldenrodYellow",
                "Dark Lavender",
                "Dark Fuchsia",
                "Dark GreenYellow",
                "Dark SpringGreen",
                "Dark Aqua",
                "Dark Cyan",
                "Dark LightCyan",
                "Dark Aquamarine",
                "Dark Turquoise",
                "Dark LightBlue",
                "Dark DeepSkyBlue",
                "Dark Azure",
            )
            for theme in themes:
                color = theme.split(" ")[-1]
                addColorIconMenuItem(color, subMenu, theme, self, partial(self.setTheme, theme), None, False)
            subSubMenu = addSubMenu(subMenu, "menu_more")
            addAllThemeColorMenuItem("Dark", subSubMenu, self, self.setTheme)
            subMenu.addSeparator()
            themes = (
                "Night Pink",
                "Night LightYellow",
                "Night LightGoldenrodYellow",
                "Night Lavender",
                "Night Fuchsia",
                "Night GreenYellow",
                "Night SpringGreen",
                "Night Aqua",
                "Night Cyan",
                "Night LightCyan",
                "Night Aquamarine",
                "Night Turquoise",
                "Night LightBlue",
                "Night DeepSkyBlue",
                "Night Azure",
            )
            for theme in themes:
                color = theme.split(" ")[-1]
                addColorIconMenuItem(color, subMenu, theme, self, partial(self.setTheme, theme), None, False)
            subSubMenu = addSubMenu(subMenu, "menu_more")
            addAllThemeColorMenuItem("Night", subSubMenu, self, self.setTheme)
        subMenu = addSubMenu(menu, "menu1_selectMenuLayout")
        addMenuLayoutItems(self, subMenu)
        subMenu.addSeparator()
        addMenuItem(subMenu, "refButtonAction", self, self.selectRefButtonSingleClickActionDialog)
        subMenu = addSubMenu(menu, "menu_shortcuts")
        items = (
            ("menu_blank", lambda: self.setShortcuts("blank")),
            ("menu_brachys", lambda: self.setShortcuts("brachys")),
            ("menu_micron", lambda: self.setShortcuts("micron")),
            ("menu_syntemno", lambda: self.setShortcuts("syntemno")),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        for shortcut in ShortcutUtil.getListCustomShortcuts():
            addMenuItem(subMenu, shortcut, self, lambda shortcut=shortcut: self.setShortcuts(shortcut), None, False)
        addMenuItem(menu, "menu_display_shortcuts", self, self.displayShortcuts, sc.displayShortcuts)
        if config.enableMacros:
            addMenuItem(menu, "menu_startup_macro", self, self.setStartupMacro, None)
        addMenuItem(menu, "menu1_moreConfig", self, self.moreConfigOptionsDialog, sc.moreConfigOptionsDialog)
        menu.addSeparator()
        subMenu = addSubMenu(menu, "menu1_programInterface")
        addMenuItem(subMenu, "menu_language", self, self.openInterfaceLanguageDialog)
        menu.addSeparator()
        subMenu = addSubMenu(menu, "bar3_pdf")
        items = (
            ("bar1_menu", self.printMainPage, None),
            ("bar2_menu", self.printStudyPage, None),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        menu.addSeparator()
        addMenuItem(menu, "menu1_update", self, self.showUpdateAppWindow, None)
        menu.addSeparator()

        appIcon = QIcon(os.path.join("htmlResources", "UniqueBibleApp.png"))
        quit_action = QAction(appIcon, config.thisTranslation["menu1_exit"], self, shortcut=sc.quitApp, triggered=self.quitApp)
        menu.addAction(quit_action)

        menu2 = self.menuBar().addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu2_view"]))

        screenSizeMenu = menu2.addMenu(config.thisTranslation["menu1_screenSize"])
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_fullScreen"], self, shortcut=sc.fullsizeWindow, triggered=self.fullsizeWindow))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_maximized"], self, shortcut=sc.maximizedWindow, triggered=self.maximizedWindow))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_smallSize"], self, shortcut=sc.twoThirdWindow, triggered=self.twoThirdWindow))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_topHalf"], self, shortcut=sc.topHalfScreenHeight, triggered=self.topHalfScreenHeight))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_bottomHalf"], self, shortcut=sc.bottomHalfScreenHeight, triggered=self.bottomHalfScreenHeight))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_leftHalf"], self, shortcut=sc.leftHalfScreenWidth, triggered=self.leftHalfScreenWidth))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_rightHalf"], self, shortcut=sc.rightHalfScreenWidth, triggered=self.rightHalfScreenWidth))
        
        menu2.addSeparator()

        toolbarMenu = menu2.addMenu(config.thisTranslation["menu2_toobars"])
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_all"], self, shortcut=sc.setNoToolBar, triggered=self.setNoToolBar))
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_topOnly"], self, shortcut=sc.hideShowAdditionalToolBar, triggered=self.hideShowAdditionalToolBar))
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_top"], self, triggered=self.hideShowMainToolBar))
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_second"], self, triggered=self.hideShowSecondaryToolBar))
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_left"], self, triggered=self.hideShowLeftToolBar))
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_right"], self, triggered=self.hideShowRightToolBar))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_icons"], self, triggered=self.switchIconSize))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_landscape"], self, shortcut=sc.switchLandscapeMode, triggered=self.switchLandscapeMode))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_study"], self, shortcut=sc.parallel, triggered=self.parallel))
        menu2.addAction(QAction(config.thisTranslation["menu2_bottom"], self, shortcut=sc.cycleInstant, triggered=self.cycleInstant))
        menu2.addSeparator()
        fontsMenu = menu2.addMenu(config.thisTranslation["menu2_fonts"])
        fontsMenu.addAction(QAction(config.thisTranslation["menu1_setDefaultFont"], self, triggered=self.setDefaultFont))
        fontsMenu.addAction(QAction(config.thisTranslation["menu1_setChineseFont"], self, triggered=self.setChineseFont))
        fontSizeMenu = menu2.addMenu(config.thisTranslation["menu2_fontSize"])
        fontSizeMenu.addAction(QAction(config.thisTranslation["menu2_larger"], self, shortcut=sc.largerFont, triggered=self.largerFont))
        fontSizeMenu.addAction(QAction(config.thisTranslation["menu2_smaller"], self, shortcut=sc.smallerFont, triggered=self.smallerFont))

        menu3 = self.menuBar().addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu_bible"]))

        bibleMenuMenu = menu3.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu_bibleMenu"]))
        bibleMenuMenu.addAction(QAction(config.thisTranslation["bar1_menu"], self, triggered=self.mainTextMenu))
        bibleMenuMenu.addAction(QAction(config.thisTranslation["bar2_menu"], self, triggered=self.studyTextMenu))

        bibleNavigationMenu = menu3.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu_navigation"]))
        bibleNavigationMenu.addAction(QAction(config.thisTranslation["menu_next_book"], self, shortcut=sc.nextMainBook, triggered=self.nextMainBook))
        bibleNavigationMenu.addAction(QAction(config.thisTranslation["menu_previous_book"], self, shortcut=sc.previousMainBook, triggered=self.previousMainBook))
        bibleNavigationMenu.addAction(QAction(config.thisTranslation["menu4_next"], self, shortcut=sc.nextMainChapter, triggered=self.nextMainChapter))
        bibleNavigationMenu.addAction(QAction(config.thisTranslation["menu4_previous"], self, shortcut=sc.previousMainChapter, triggered=self.previousMainChapter))

        scrollMenu = menu3.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu_scroll"]))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_main_scroll_to_top"], self, shortcut=sc.mainPageScrollToTop,
                                          triggered=self.mainPageScrollToTop))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_main_page_down"], self, shortcut=sc.mainPageScrollPageDown,
                                          triggered=self.mainPageScrollPageDown))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_main_page_up"], self, shortcut=sc.mainPageScrollPageUp,
                                          triggered=self.mainPageScrollPageUp))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_study_scroll_to_top"], self, shortcut=sc.studyPageScrollToTop, triggered=self.studyPageScrollToTop))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_study_page_down"], self, shortcut=sc.studyPageScrollPageDown,
                                      triggered=self.studyPageScrollPageDown))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_study_page_up"], self, shortcut=sc.studyPageScrollPageUp,
                                      triggered=self.studyPageScrollPageUp))
        menu3.addSeparator()
        subMenu = addSubMenu(menu3, "verseNoAction")
        items = (
            ("singleClick", self.selectSingleClickActionDialog),
            ("doubleClick", self.selectDoubleClickActionDialog),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        menu3.addSeparator()
        toggleMenu = menu3.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu_toggleFeatures"]))
        toggleMenu.addAction(QAction(config.thisTranslation["menu2_format"], self, shortcut=sc.enableParagraphButtonClicked, triggered=self.enableParagraphButtonClicked))
        toggleMenu.addAction(QAction(config.thisTranslation["menu2_subHeadings"], self, triggered=self.enableSubheadingButtonClicked))
        toggleMenu.addAction(QAction(config.thisTranslation["menu2_hover"], self, shortcut=sc.enableInstantButtonClicked, triggered=self.enableInstantButtonClicked))
        if config.enableVerseHighlighting:
            toggleMenu.addAction(QAction(config.thisTranslation["menu2_toggleHighlightMarkers"], self, triggered=self.toggleHighlightMarker))
        toggleMenu.addAction(QAction(config.thisTranslation["menu_toggleEnforceCompareParallel"], self, triggered=self.enforceCompareParallelButtonClicked))
        toggleMenu.addAction(QAction(config.thisTranslation["menu_syncStudyWindowBible"], self, triggered=self.enableSyncStudyWindowBibleButtonClicked))
        toggleMenu.addAction(QAction(config.thisTranslation["menu_syncBibleCommentary"], self, triggered=self.enableSyncCommentaryButtonClicked))
        menu3.addSeparator()
        searchMenu = menu3.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu5_search"]))
        searchMenu.addAction(QAction(config.thisTranslation["menu5_main"], self, shortcut=sc.displaySearchBibleCommand, triggered=self.displaySearchBibleCommand))
        searchMenu.addAction(QAction(config.thisTranslation["menu5_study"], self, shortcut=sc.displaySearchStudyBibleCommand, triggered=self.displaySearchStudyBibleCommand))
        searchMenu.addAction(QAction(config.thisTranslation["menu5_bible"], self, triggered=self.displaySearchBibleMenu))
        if config.enableVerseHighlighting:
            searchMenu.addSeparator()
            searchMenu.addAction(QAction(config.thisTranslation["menu_highlight"], self, triggered=self.displaySearchHighlightCommand))

        menu3.addSeparator()

        mainWindowHistoryMenu = menu3.addMenu(config.thisTranslation["menu2_mainWindowHistory"])
        mainWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_main"], self, shortcut=sc.mainHistoryButtonClicked, triggered=self.mainHistoryButtonClicked))
        mainWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_mainBack"], self, shortcut=sc.back, triggered=self.back))
        mainWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_mainForward"], self, shortcut=sc.forward, triggered=self.forward))
        
        studyWindowHistoryMenu = menu3.addMenu(config.thisTranslation["menu2_studyWindowHistory"])
        studyWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_study"], self, shortcut=sc.studyHistoryButtonClicked, triggered=self.studyHistoryButtonClicked))
        studyWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_studyBack"], self, shortcut=sc.studyBack, triggered=self.studyBack))
        studyWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_studyForward"], self, shortcut=sc.studyForward, triggered=self.studyForward))
        menu3.addSeparator()
        menu3.addAction(QAction(config.thisTranslation["liveFilter"], self, triggered=self.showLiveFilterDialog))
        menu3.addSeparator()
        menu3.addAction(QAction(config.thisTranslation["menu1_reload"], self, triggered=self.reloadCurrentRecord))

        menu4 = self.menuBar().addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu4_further"]))

        bookFeaturesMenu = menu4.addMenu(config.thisTranslation["menu4_book"])
        bookFeaturesMenu.addAction(QAction(config.thisTranslation["html_introduction"], self, triggered=self.runBookFeatureIntroduction))
        bookFeaturesMenu.addAction(QAction(config.thisTranslation["html_timelines"], self, triggered=self.runBookFeatureTimelines))
        bookFeaturesMenu.addAction(QAction(config.thisTranslation["context1_dict"], self, triggered=self.runBookFeatureDictionary))
        bookFeaturesMenu.addAction(QAction(config.thisTranslation["context1_encyclopedia"], self, triggered=self.runBookFeatureEncyclopedia))
        
        chapterFeaturesMenu = menu4.addMenu(config.thisTranslation["menu4_chapter"])
        chapterFeaturesMenu.addAction(QAction(config.thisTranslation["html_overview"], self, triggered=self.runChapterFeatureOverview))
        chapterFeaturesMenu.addAction(QAction(config.thisTranslation["html_chapterIndex"], self, triggered=self.runChapterFeatureChapterIndex))
        chapterFeaturesMenu.addAction(QAction(config.thisTranslation["html_summary"], self, triggered=self.runChapterFeatureSummary))
        chapterFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_commentary"], self, triggered=self.runChapterFeatureCommentary))

        verseFeaturesMenu = menu4.addMenu(config.thisTranslation["menu4_verse"])
        verseFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_indexes"], self, shortcut=sc.runINDEX, triggered=self.runINDEX))
        verseFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_crossRef"], self, shortcut=sc.runCROSSREFERENCE, triggered=self.runCROSSREFERENCE))
        verseFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_tske"], self, shortcut=sc.runTSKE, triggered=self.runTSKE))
        verseFeaturesMenu.addAction(QAction(config.thisTranslation["menu_more"], self, triggered=self.mainRefButtonClicked))

        wordFeaturesMenu = menu4.addMenu(config.thisTranslation["menu4_word"])
        wordFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_traslations"], self, triggered=self.runTRANSLATION))
        wordFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_discourse"], self, triggered=self.runDISCOURSE))
        wordFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_words"], self, triggered=self.runWORDS))
        wordFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_tdw"], self, shortcut=sc.runCOMBO, triggered=self.runCOMBO))
        menu4.addSeparator()

        compareFeaturesMenu = menu4.addMenu(config.thisTranslation["menu4_compareFeatures"])
        compareFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_compareAll"], self, shortcut=sc.runCOMPARE, triggered=self.runCOMPARE))
        compareFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_moreComparison"], self, triggered=lambda: self.openControlPanelTab(0)))


        marvelBibleMenu = menu4.addMenu(config.thisTranslation["menu_marvelBibles"])
        marvelBibleMenu.addAction(QAction("Marvel Original Bible", self, shortcut=sc.runMOB, triggered=self.runMOB))
        marvelBibleMenu.addAction(QAction("Marvel Interlinear Bible", self, shortcut=sc.runMIB, triggered=self.runMIB))
        marvelBibleMenu.addAction(QAction("Marvel Trilingual Bible", self, shortcut=sc.runMTB, triggered=self.runMTB))
        marvelBibleMenu.addAction(QAction("Marvel Parallel Bible", self, shortcut=sc.runMPB, triggered=self.runMPB))
        marvelBibleMenu.addAction(QAction("Marvel Annotated Bible", self, shortcut=sc.runMAB, triggered=self.runMAB))
        menu4.addSeparator()

        commentaryMenu = menu4.addMenu(config.thisTranslation["menu4_commentary"])
        commentaryMenu.addAction(QAction(config.thisTranslation["menu4_lastCommentary"], self, shortcut=sc.runCOMMENTARY, triggered=self.runCOMMENTARY))
        commentaryMenu.addAction(QAction("{0} {1}".format(config.thisTranslation["menu4_commentary"], config.thisTranslation["menu_bibleMenu"]), self, shortcut=sc.commentaryRefButtonClicked, triggered=self.commentaryRefButtonClicked))

        # check if books in favourite list exist
        #for book in config.favouriteBooks:
        #if not os.path.isfile(os.path.join(config.marvelData, "books", "{0}.book".format(book))):
        #config.favouriteBooks.remove(book)

        # remove an old book from favourite list if it is not installed
        book = "Maps_ASB"
        if not os.path.isfile(os.path.join(config.marvelData, "books", "{0}.book".format(book))) and book in config.favouriteBooks:
            config.favouriteBooks.remove(book)

        menu10 = self.menuBar().addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu10_books"]))
        if config.favouriteBooks:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[0]), self, triggered=self.openFavouriteBook0))
        if len(config.favouriteBooks) > 1:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[1]), self, triggered=self.openFavouriteBook1))
        if len(config.favouriteBooks) > 2:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[2]), self, triggered=self.openFavouriteBook2))
        if len(config.favouriteBooks) > 3:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[3]), self, triggered=self.openFavouriteBook3))
        if len(config.favouriteBooks) > 4:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[4]), self, triggered=self.openFavouriteBook4))
        if len(config.favouriteBooks) > 5:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[5]), self, triggered=self.openFavouriteBook5))
        if len(config.favouriteBooks) > 6:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[6]), self, triggered=self.openFavouriteBook6))
        if len(config.favouriteBooks) > 7:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[7]), self, triggered=self.openFavouriteBook7))
        if len(config.favouriteBooks) > 8:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[8]), self, triggered=self.openFavouriteBook8))
        if len(config.favouriteBooks) > 9:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[9]), self, triggered=self.openFavouriteBook9))
        menu10.addSeparator()
        menu10.addAction(QAction(config.thisTranslation["menu5_book"], self, triggered=self.openBookMenu))
        menu10.addAction(QAction(config.thisTranslation["menu10_dialog"], self, triggered=self.openBookDialog))
        menu10.addSeparator()
        menu10.addAction(QAction(config.thisTranslation["menu10_addFavourite"], self, triggered=self.addFavouriteBookDialog))
        menu10.addSeparator()
        items = (
            ("menu10_bookFromImages", self.createBookModuleFromImages),
            ("menu10_bookFromHtml", self.createBookModuleFromHTML),
            ("menu10_bookFromNotes", self.createBookModuleFromNotes),
            ("menu10_bookFromPDF", self.createBookModuleFromPDF),
            ("devotionalFromNotes", self.createDevotionalFromNotes),
            ("commentaryFromNotes", self.createCommentaryFromNotes),
            ("lexiconFromNotes", self.createLexiconFromNotes),
        )
        for feature, action in items:
            addMenuItem(menu10, feature, self, action)
        menu10.addSeparator()
        menu10.addAction(QAction(config.thisTranslation["menu10_clearBookHighlights"], self, triggered=self.clearBookHighlights))

        menu5 = self.menuBar().addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu5_lookup"]))
        menu5.addAction(QAction(config.thisTranslation["menu5_dictionary"], self, shortcut=sc.searchCommandBibleDictionary, triggered=self.searchCommandBibleDictionary))
        menu5.addAction(QAction(config.thisTranslation["context1_dict"], self, triggered=self.searchDictionaryDialog))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_encyclopedia"], self, shortcut=sc.searchCommandBibleEncyclopedia, triggered=self.searchCommandBibleEncyclopedia))
        menu5.addAction(QAction(config.thisTranslation["context1_encyclopedia"], self, triggered=self.searchEncyclopediaDialog))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_book"], self, shortcut=sc.displaySearchBookCommand, triggered=self.displaySearchBookCommand))
        menu5.addAction(QAction(config.thisTranslation["menu5_selectBook"], self, triggered=self.searchBookDialog))
        menu5.addAction(QAction(config.thisTranslation["menu5_favouriteBook"], self, triggered=self.displaySearchFavBookCommand))
        menu5.addAction(QAction(config.thisTranslation["menu5_allBook"], self, triggered=self.displaySearchAllBookCommand))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_lastTopics"], self, shortcut=sc.searchCommandBibleTopic, triggered=self.searchCommandBibleTopic))
        menu5.addAction(QAction(config.thisTranslation["menu5_topics"], self, triggered=self.searchTopicDialog))
        menu5.addAction(QAction(config.thisTranslation["menu5_allTopics"], self, triggered=self.searchCommandAllBibleTopic))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_characters"], self, shortcut=sc.searchCommandBibleCharacter, triggered=self.searchCommandBibleCharacter))
        menu5.addAction(QAction(config.thisTranslation["menu5_names"], self, shortcut=sc.searchCommandBibleName, triggered=self.searchCommandBibleName))
        menu5.addAction(QAction(config.thisTranslation["menu5_locations"], self, shortcut=sc.searchCommandBibleLocation, triggered=self.searchCommandBibleLocation))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_lexicon"], self, shortcut=sc.searchCommandLexicon, triggered=self.searchCommandLexicon))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_last3rdDict"], self, triggered=self.searchCommandThirdPartyDictionary))
        menu5.addAction(QAction(config.thisTranslation["menu5_3rdDict"], self, triggered=self.search3rdDictionaryDialog))

        menu6 = self.menuBar().addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu_notes"]))

        chapterNotesMenu = menu6.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu_chapterNotes"]))
        chapterNotesMenu.addAction(QAction(config.thisTranslation["bar1_menu"], self, triggered=self.openMainChapterNote))
        chapterNotesMenu.addAction(QAction(config.thisTranslation["bar2_menu"], self, triggered=self.openStudyChapterNote))
        
        verseNotesMenu = menu6.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu_verseNotes"]))
        verseNotesMenu.addAction(QAction(config.thisTranslation["bar1_menu"], self, triggered=self.openMainVerseNote))
        verseNotesMenu.addAction(QAction(config.thisTranslation["bar2_menu"], self, triggered=self.openStudyVerseNote))
        
        searchNotesMenu = menu6.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu_search"]))
        searchNotesMenu.addAction(QAction(config.thisTranslation["menu_bookNotes"], self, triggered=self.searchCommandBookNote))
        searchNotesMenu.addAction(QAction(config.thisTranslation["menu_chapterNotes"], self, triggered=self.searchCommandChapterNote))
        searchNotesMenu.addAction(QAction(config.thisTranslation["menu_verseNotes"], self, triggered=self.searchCommandVerseNote))
        searchNotesMenu.addAction(QAction(config.thisTranslation["menu10_clearBookHighlights"], self, triggered=self.clearNoteHighlights))

        if config.enableGist:
            menu6.addAction(QAction(config.thisTranslation["menu_gist"], self, triggered=self.showGistWindow))

        menu6.addSeparator()

        topicalNotesMenu = menu6.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu7_topics"]))
        topicalNotesMenu.addAction(QAction(config.thisTranslation["menu7_read"], self, triggered=self.externalFileButtonClicked))
        topicalNotesMenu.addAction(QAction(config.thisTranslation["menu7_recent"], self, triggered=self.openExternalFileHistory))
        topicalNotesMenu.addAction(QAction(config.thisTranslation["menu7_open"], self, triggered=self.openTextFileDialog))

        noteEditorMenu = menu6.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["note_editor"]))
        noteEditorMenu.addAction(QAction(config.thisTranslation["menu7_create"], self, shortcut=sc.createNewNoteFile, triggered=self.createNewNoteFile))
        noteEditorMenu.addAction(QAction(config.thisTranslation["menu7_edit"], self, triggered=self.editExternalFileButtonClicked))

        menu11 = self.menuBar().addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu11_multimedia"]))
        menu11.addAction(QAction(config.thisTranslation["menu11_images"], self, triggered=self.openImagesFolder))
        menu11.addAction(QAction(config.thisTranslation["menu11_audio"], self, triggered=self.openAudioFolder))
        menu11.addAction(QAction(config.thisTranslation["menu11_music"], self, triggered=self.openMusicFolder))
        menu11.addAction(QAction(config.thisTranslation["menu11_video"], self, triggered=self.openVideoFolder))
        menu11.addSeparator()
        if ("Ytdlp" in config.enabled):
            menu11.addAction(QAction(config.thisTranslation["menu11_setupDownload"], self, triggered=self.setupYouTube))
            menu11.addAction(QAction(config.thisTranslation["menu11_youtube"], self, triggered=self.openMiniBrowser))
            menu11.addSeparator()
        menu11.addAction(QAction("YouTube -> mp3", self, triggered=self.downloadMp3Dialog))
        menu11.addAction(QAction("YouTube -> mp4", self, triggered=self.downloadMp4Dialog))
        menu11.addSeparator()

        menu8 = self.menuBar().addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu8_resources"]))
        menu8.addAction(QAction(config.thisTranslation["menu8_marvelData"], self, triggered=self.openMarvelDataFolder))
        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["menu8_bibles"], self, triggered=self.installMarvelBibles))
        menu8.addAction(QAction(config.thisTranslation["menu8_commentaries"], self, triggered=self.installMarvelCommentaries))
        menu8.addAction(QAction(config.thisTranslation["menu8_datasets"], self, triggered=self.installMarvelDatasets))
        menu8.addSeparator()

        addGithubDownloadMenuItems(self, menu8)

        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["menu8_plusLexicons"], self, triggered=self.importBBPlusLexiconInAFolder))
        menu8.addAction(QAction(config.thisTranslation["menu8_plusDictionaries"], self, triggered=self.importBBPlusDictionaryInAFolder))
        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["menu8_download3rdParty"], self, triggered=self.moreBooks))
        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["menu8_3rdParty"], self, triggered=self.importModules))
        menu8.addAction(QAction(config.thisTranslation["menu8_3rdPartyInFolder"], self, triggered=self.importModulesInFolder))
        menu8.addAction(QAction(config.thisTranslation["menu8_settings"], self, triggered=self.importSettingsDialog))
        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["menu8_tagFile"], self, triggered=self.tagFile))
        menu8.addAction(QAction(config.thisTranslation["menu8_tagFiles"], self, triggered=self.tagFiles))
        menu8.addAction(QAction(config.thisTranslation["menu8_tagFolder"], self, triggered=self.tagFolder))
        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["modify_database"], self, triggered=self.selectDatabaseToModify))
        menu8.addSeparator()
        addMenuItem(menu8, "reloadResources", self, self.reloadResources)

        if config.enableMacros:
            macros_menu = self.menuBar().addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu_macros"]))
            run_macros_menu = macros_menu.addMenu(config.thisTranslation["menu_run"])
            self.loadRunMacrosMenu(run_macros_menu)
            build_macros_menu = macros_menu.addMenu(config.thisTranslation["menu_build_macro"])
            addBuildMacroMenuItems(self, build_macros_menu)

        # plugins
        if config.enablePlugins:
            menu = addMenu(self.menuBar(), "menu_plugins")
            for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "menu"), "py"):
                if not plugin in config.excludeMenuPlugins:
                    if "_" in plugin:
                        feature, shortcut = plugin.split("_", 1)
                        addMenuItem(menu, feature, self, lambda plugin=plugin: self.runPlugin(plugin), shortcut=shortcut, translation=False)
                    else:
                        addMenuItem(menu, plugin, self, lambda plugin=plugin: self.runPlugin(plugin), translation=False)
            menu.addSeparator()
            addMenuItem(menu, "enableIndividualPlugins", self, self.enableIndividualPluginsWindow)

        if config.showInformation:
            menu9 = self.menuBar().addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu9_information"]))
            addMenuItem(menu9, "latestChanges", self, self.showInfo)
            addMenuItem(menu9, "ubaCommands", self, self.showCommandDocumentation)
            addMenuItem(menu, "config.py", self, self.showConfigPyDocumentation, translation=False)
            menu9.addSeparator()
            menu9.addAction(QAction(config.thisTranslation["menu1_wikiPages"], self, triggered=self.openUbaWiki))
            menu9.addAction(QAction(config.thisTranslation["menu_discussions"], self, triggered=self.openUbaDiscussions))
            menu9.addSeparator()
            menu9.addAction(QAction("BibleTools.app", self, triggered=self.openBibleTools))
            menu9.addAction(QAction("UniqueBible.app", self, triggered=self.openUniqueBible))
            menu9.addAction(QAction("Marvel.bible", self, triggered=self.openMarvelBible))
            menu9.addAction(QAction("BibleBento.com", self, triggered=self.openBibleBento))
            menu9.addAction(QAction("OpenGNT.com", self, triggered=self.openOpenGNT))
            menu9.addSeparator()
            menu9.addAction(QAction("GitHub Repositories", self, triggered=self.openSource))
            menu9.addAction(QAction("Unique Bible", self, triggered=self.openUniqueBibleSource))
            menu9.addAction(QAction("Open Hebrew Bible", self, triggered=self.openHebrewBibleSource))
            menu9.addAction(QAction("Open Greek New Testament", self, triggered=self.openOpenGNTSource))
            menu9.addSeparator()
            menu9.addAction(QAction(config.thisTranslation["menu9_contact"], self, triggered=self.contactEliranWong))
            menu9.addSeparator()
            menu9.addAction(QAction(config.thisTranslation["menu9_donate"], self, triggered=self.donateToUs))

        if config.developer:
            menu999 = self.menuBar().addMenu("{0}Developer".format(config.menuUnderline))
            #menu999.addAction(QAction("Download Google Static Maps", self, triggered=self.downloadGoogleStaticMaps))
            menu999.addAction(QAction("testing", self, triggered=self.testing))
            addMenuItem(menu999, "edit_language_file", self, self.selectLanguageFileToEdit)

        if (config.runMode == "docker"):
            menu = addMenu(self.menuBar(), "menu_apps")
            with open("/defaults/menu.xml", "r") as fileObj:
                for line in fileObj.readlines():
                    if "icon=" in line and not 'label="Unique Bible App"' in line:
                        line = re.sub('^.*?<item label="(.*?)" icon="(.*?)"><action name="Execute"><command>(.*?)</command></action></item>.*?$', r'\1,\2,\3', line)
                        webtopApp, icon, command = line[:-1].split(",", 3)
                        addIconMenuItem(icon, menu, webtopApp, self, partial(WebtopUtil.run, command), "", translation=False)

    def testing(self):
        pass
        #test = BibleExplorer(self, (config.mainB, config.mainC, config.mainV, config.mainText))
        #test = MasterControl(self)
        #test.show()

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

        self.mainRefButton = QPushButton(self.verseReference("main")[1])
        self.addStandardTextButton("bar1_reference", self.mainRefButtonClicked, self.firstToolBar, self.mainRefButton)

        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        if config.qtMaterial and config.qtMaterialTheme:
            mainRefButtonHeight = self.mainRefButton.height() 
            config.iconButtonWidth = config.maximumIconButtonWidth if mainRefButtonHeight > config.maximumIconButtonWidth else mainRefButtonHeight

        self.addStandardIconButton("bar1_chapterNotes", "noteChapter.png", self.openMainChapterNote, self.firstToolBar)
        self.addStandardIconButton("bar1_verseNotes", "noteVerse.png", self.openMainVerseNote, self.firstToolBar)
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

        self.addStandardIconButton("bar1_toolbars", "toolbar.png", self.hideShowAdditionalToolBar, self.firstToolBar)

        if config.addBreakAfterTheFirstToolBar:
            self.addToolBarBreak()

        self.studyBibleToolBar = QToolBar()
        self.studyBibleToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.studyBibleToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.studyBibleToolBar)

        self.studyRefButton = QPushButton(":::".join(self.verseReference("study")))
        self.addStandardTextButton("bar2_reference", self.studyRefButtonClicked, self.studyBibleToolBar, self.studyRefButton)

        self.addStandardIconButton("bar2_chapterNotes", "noteChapter.png", self.openStudyChapterNote, self.studyBibleToolBar)
        self.addStandardIconButton("bar2_verseNotes", "noteVerse.png", self.openStudyVerseNote, self.studyBibleToolBar)
        self.addStandardIconButton("bar2_searchBible", "search.png", self.displaySearchStudyBibleCommand, self.studyBibleToolBar)
        self.addStandardIconButton("bar2_searchBibles", "search_plus.png", self.displaySearchBibleMenu, self.studyBibleToolBar)

        self.enableSyncStudyWindowBibleButton = QPushButton()
        self.addStandardIconButton(self.getSyncStudyWindowBibleDisplayToolTip(), self.getSyncStudyWindowBibleDisplay(), self.enableSyncStudyWindowBibleButtonClicked, self.studyBibleToolBar, self.enableSyncStudyWindowBibleButton, False)

        if config.addBreakBeforeTheLastToolBar:
            self.addToolBarBreak()

        # Second tool bar
        self.secondToolBar = QToolBar()
        self.secondToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.secondToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.secondToolBar)

        self.enableStudyBibleButton = QPushButton()
        self.addStandardIconButton(self.getStudyBibleDisplayToolTip(), self.getStudyBibleDisplay(), self.enableStudyBibleButtonClicked, self.secondToolBar, self.enableStudyBibleButton, False)

        self.secondToolBar.addSeparator()

        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
        self.addStandardTextButton("menu4_commentary", self.commentaryRefButtonClicked, self.secondToolBar, self.commentaryRefButton)

        self.enableSyncCommentaryButton = QPushButton()
        self.addStandardIconButton(self.getSyncCommentaryDisplayToolTip(), self.getSyncCommentaryDisplay(), self.enableSyncCommentaryButtonClicked, self.secondToolBar, self.enableSyncCommentaryButton, False)
        self.secondToolBar.addSeparator()

        self.addStandardIconButton("menu10_dialog", "open.png", self.openBookDialog, self.secondToolBar)

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
        if ("Ytdlp" in config.enabled):
            self.addStandardIconButton("menu11_youtube", "youtube.png", self.openMiniBrowser, self.secondToolBar)
            self.secondToolBar.addSeparator()
        if ("Pythonvlc" in config.enabled):
            self.addStandardIconButton("mediaPlayer", "buttons/media_player.png", self.openVlcPlayer, self.secondToolBar)
            self.secondToolBar.addSeparator()
        self.addStandardIconButton("menu1_reload", "reload.png", self.reloadCurrentRecord, self.secondToolBar)
        self.addStandardIconButton("menu1_fullScreen", "expand.png", self.fullsizeWindow, self.secondToolBar)
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
        self.addStandardIconButton("menu4_previous", "previousChapter.png", self.previousMainChapter, self.leftToolBar)
        self.addStandardIconButton("menu4_next", "nextChapter.png", self.nextMainChapter, self.leftToolBar)
        self.leftToolBar.addSeparator()
        self.addStandardIconButton("menu4_compareAll", "compare_with.png", self.runCOMPARE, self.leftToolBar)
        self.addStandardIconButton("menu4_moreComparison", "parallel_with.png", lambda: self.openControlPanelTab(0), self.leftToolBar)
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
        self.addStandardIconButton("menu2_landscape", "portrait.png", self.switchLandscapeMode, self.rightToolBar)
        self.addStandardIconButton("menu2_study", "parallel.png", self.parallel, self.rightToolBar)
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

        self.mainRefButton = QPushButton(self.verseReference("main")[1])
        self.mainRefButton.setToolTip(config.thisTranslation["bar1_reference"])
        self.mainRefButton.setStyleSheet(textButtonStyle)
        self.mainRefButton.clicked.connect(self.mainRefButtonClicked)
        self.firstToolBar.addWidget(self.mainRefButton)

        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        if config.qtMaterial and config.qtMaterialTheme:
            mainRefButtonHeight = self.mainRefButton.height() 
            config.iconButtonWidth = config.maximumIconButtonWidth if mainRefButtonHeight > config.maximumIconButtonWidth else mainRefButtonHeight

        iconFile = os.path.join("htmlResources", "noteChapter.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_chapterNotes"], self.openMainChapterNote)

        iconFile = os.path.join("htmlResources", "noteVerse.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_verseNotes"], self.openMainVerseNote)

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

        if ("Ytdlp" in config.enabled):
            iconFile = os.path.join("htmlResources", "youtube.png")
            self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu11_youtube"], self.openMiniBrowser)
            self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "reload.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu1_reload"], self.reloadCurrentRecord)
        iconFile = os.path.join("htmlResources", "expand.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu1_fullScreen"], self.fullsizeWindow)

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

        iconFile = os.path.join("htmlResources", "previousChapter.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_previous"], self.previousMainChapter)

        #        actionButton = QPushButton()
        #        actionButton.setToolTip(config.thisTranslation["bar1_reference"])
        #        actionButtonFile = os.path.join("htmlResources", "bible.png")
        #        actionButton.setIcon(QIcon(actionButtonFile))
        #        actionButton.clicked.connect(self.openMainChapter)
        #        self.leftToolBar.addWidget(actionButton)

        iconFile = os.path.join("htmlResources", "nextChapter.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_next"], self.nextMainChapter)

        self.leftToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "compare_with.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_compareAll"], self.runCOMPARE)

        iconFile = os.path.join("htmlResources", "parallel_with.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_moreComparison"], lambda: self.openControlPanelTab(0))

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
                toolbar.setIconSize(QSize(config.iconButtonWidth * config.toolbarIconSizeFactor, config.iconButtonWidth * config.toolbarIconSizeFactor))
                toolbar.setFixedHeight(config.iconButtonWidth + 4)
            for toolbar in (self.leftToolBar, self.rightToolBar):
                toolbar.setIconSize(QSize(config.iconButtonWidth * config.sidebarIconSizeFactor, config.iconButtonWidth * config.sidebarIconSizeFactor))
