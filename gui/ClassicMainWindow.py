import os, config, myTranslation
from PySide2.QtGui import QIcon, Qt
from PySide2.QtWidgets import (QAction, QToolBar, QPushButton, QLineEdit, QStyleFactory)
from gui.MainWindow import MainWindow
from gui.MasterControl import MasterControl

class ClassicMainWindow(MainWindow):

    def __init__(self):
        super().__init__()

    def create_menu(self):
        menu1 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu1_app"]))

        menu1.addAction(QAction(config.thisTranslation["menu1_remoteControl"], self, shortcut="Ctrl+O", triggered=self.manageRemoteControl))
        menu1.addSeparator()

        clipboardMenu = menu1.addMenu(config.thisTranslation["menu1_clipboard"])
        clipboardMenu.addAction(QAction(config.thisTranslation["menu1_readClipboard"], self, shortcut="Ctrl+^", triggered=self.pasteFromClipboard))
        clipboardMenu.addAction(QAction(config.thisTranslation["menu1_runClipboard"], self, shortcut="Ctrl+M", triggered=self.parseContentOnClipboard))
        menu1.addSeparator()

        generalPreferencesMenu = menu1.addMenu(config.thisTranslation["menu1_generalPreferences"])
        generalPreferencesMenu.addAction(QAction(config.thisTranslation["menu1_tabNo"], self, triggered=self.setTabNumberDialog))
        generalPreferencesMenu.addAction(QAction(config.thisTranslation["menu1_setAbbreviations"], self, triggered=self.setBibleAbbreviations))
        generalPreferencesMenu.addAction(QAction(config.thisTranslation["menu1_setMyFavouriteBible"], self, triggered=self.openFavouriteBibleDialog))
        generalPreferencesMenu.addAction(QAction(config.thisTranslation["menu1_setMyLanguage"], self, triggered=self.openMyLanguageDialog))
        #lexiconMenu = menu1.addMenu(config.thisTranslation["menu1_selectDefaultLexicon"])
        generalPreferencesMenu.addAction(QAction(config.thisTranslation["menu1_setDefaultStrongsHebrewLexicon"], self, triggered=self.openSelectDefaultStrongsHebrewLexiconDialog))
        generalPreferencesMenu.addAction(QAction(config.thisTranslation["menu1_setDefaultStrongsGreekLexicon"], self, triggered=self.openSelectDefaultStrongsGreekLexiconDialog))
        
        windowStyleMenu = menu1.addMenu(config.thisTranslation["menu1_selectWindowStyle"])
        windowStyleMenu.addAction(QAction("default", self, triggered=lambda: self.setAppWindowStyle("default")))
        for style in QStyleFactory.keys():
            windowStyleMenu.addAction(QAction(style, self, triggered=lambda style=style: self.setAppWindowStyle(style)))

        themeMenu = menu1.addMenu(config.thisTranslation["menu1_selectTheme"])
        if config.qtMaterial:
            qtMaterialThemes = ["light_amber.xml",  "light_blue.xml",  "light_cyan.xml",  "light_cyan_500.xml",  "light_lightgreen.xml",  "light_pink.xml",  "light_purple.xml",  "light_red.xml",  "light_teal.xml",  "light_yellow.xml", "dark_amber.xml",  "dark_blue.xml",  "dark_cyan.xml",  "dark_lightgreen.xml",  "dark_pink.xml",  "dark_purple.xml",  "dark_red.xml",  "dark_teal.xml",  "dark_yellow.xml"]
            for theme in qtMaterialThemes:
                themeMenu.addAction(QAction(theme[:-4], self, triggered=lambda theme=theme: self.setQtMaterialTheme(theme)))
        else:
            themeMenu.addAction(QAction(config.thisTranslation["menu_light_theme"], self, triggered=self.setDefaultTheme))
            themeMenu.addAction(QAction(config.thisTranslation["menu1_dark_theme"], self, triggered=self.setDarkTheme))
        
        layoutMenu = menu1.addMenu(config.thisTranslation["menu1_selectMenuLayout"])
        layoutMenu.addAction(
            QAction(config.thisTranslation["menu1_classic_menu_layout"], self, triggered=self.setDefaultMenuLayout))
        layoutMenu.addAction(QAction(config.thisTranslation["menu1_aleph_menu_layout"], self, triggered=self.setAlephMenuLayout))
        if config.enableMacros:
            menu1.addAction(
                QAction(config.thisTranslation["menu_startup_macro"], self, triggered=self.setStartupMacro))
        menu1.addAction(QAction(config.thisTranslation["menu1_moreConfig"], self, triggered=self.moreConfigOptionsDialog))
        menu1.addSeparator()

        userInterfaceMenu = menu1.addMenu(config.thisTranslation["menu1_programInterface"])
        if (not self.isMyTranslationAvailable() and not self.isOfficialTranslationAvailable()) or (self.isMyTranslationAvailable() and not myTranslation.translationLanguage == config.userLanguage) or (self.isOfficialTranslationAvailable() and not config.translationLanguage == config.userLanguage):
            userInterfaceMenu.addAction(QAction(config.thisTranslation["menu1_translateInterface"], self, triggered=self.translateInterface))
        userInterfaceMenu.addAction(QAction(config.thisTranslation["menu1_toogleInterface"], self, triggered=self.toogleInterfaceTranslation))
        menu1.addSeparator()

        exportPdfMenu = menu1.addMenu(config.thisTranslation["bar3_pdf"])
        exportPdfMenu.addAction(QAction(config.thisTranslation["bar1_menu"], self, triggered=self.printMainPage))
        exportPdfMenu.addAction(QAction(config.thisTranslation["bar2_menu"], self, triggered=self.printStudyPage))
        menu1.addSeparator()

        menu1.addAction(QAction(config.thisTranslation["menu1_update"], self, triggered=self.updateUniqueBibleApp))
        menu1.addSeparator()
        appIcon = QIcon(os.path.join("htmlResources", "UniqueBibleApp.png"))
        quit_action = QAction(appIcon, config.thisTranslation["menu1_exit"], self, shortcut="Ctrl+Q", triggered=self.quitApp)
        menu1.addAction(quit_action)

        menu2 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu2_view"]))

        screenSizeMenu = menu2.addMenu(config.thisTranslation["menu1_screenSize"])
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_fullScreen"], self, shortcut="Ctrl+S,F", triggered=self.fullsizeWindow))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_smallSize"], self, shortcut="Ctrl+S,S", triggered=self.twoThirdWindow))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_topHalf"], self, shortcut="Ctrl+S,1", triggered=self.topHalfScreenHeight))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_bottomHalf"], self, shortcut="Ctrl+S,2", triggered=self.bottomHalfScreenHeight))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_leftHalf"], self, shortcut="Ctrl+S,3", triggered=self.leftHalfScreenWidth))
        screenSizeMenu.addAction(QAction(config.thisTranslation["menu1_rightHalf"], self, shortcut="Ctrl+S,4", triggered=self.rightHalfScreenWidth))
        
        menu2.addSeparator()

        toolbarMenu = menu2.addMenu(config.thisTranslation["menu2_toobars"])
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_all"], self, shortcut="Ctrl+J", triggered=self.setNoToolBar))
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_topOnly"], self, shortcut="Ctrl+G", triggered=self.hideShowAdditionalToolBar))
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_top"], self, triggered=self.hideShowMainToolBar))
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_second"], self, triggered=self.hideShowSecondaryToolBar))
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_left"], self, triggered=self.hideShowLeftToolBar))
        toolbarMenu.addAction(QAction(config.thisTranslation["menu2_right"], self, triggered=self.hideShowRightToolBar))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_icons"], self, triggered=self.switchIconSize))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_landscape"], self, shortcut="Ctrl+L", triggered=self.switchLandscapeMode))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_study"], self, shortcut="Ctrl+W", triggered=self.parallel))
        menu2.addAction(QAction(config.thisTranslation["menu2_bottom"], self, shortcut="Ctrl+T", triggered=self.cycleInstant))
        menu2.addSeparator()
        fontsMenu = menu2.addMenu(config.thisTranslation["menu2_fonts"])
        fontsMenu.addAction(QAction(config.thisTranslation["menu1_setDefaultFont"], self, triggered=self.setDefaultFont))
        fontsMenu.addAction(QAction(config.thisTranslation["menu1_setChineseFont"], self, triggered=self.setChineseFont))
        fontSizeMenu = menu2.addMenu(config.thisTranslation["menu2_fontSize"])
        fontSizeMenu.addAction(QAction(config.thisTranslation["menu2_larger"], self, shortcut="Ctrl++", triggered=self.largerFont))
        fontSizeMenu.addAction(QAction(config.thisTranslation["menu2_smaller"], self, shortcut="Ctrl+-", triggered=self.smallerFont))

        menu3 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_bible"]))

        bibleMenuMenu = menu3.addMenu("&{0}".format(config.thisTranslation["menu_bibleMenu"]))
        bibleMenuMenu.addAction(QAction(config.thisTranslation["bar1_menu"], self, triggered=self.mainTextMenu))
        bibleMenuMenu.addAction(QAction(config.thisTranslation["bar2_menu"], self, triggered=self.studyTextMenu))

        bibleNavigationMenu = menu3.addMenu("&{0}".format(config.thisTranslation["menu_navigation"]))
        bibleNavigationMenu.addAction(QAction(config.thisTranslation["menu_next_book"], self, shortcut="Ctrl+H,1", triggered=self.nextMainBook))
        bibleNavigationMenu.addAction(QAction(config.thisTranslation["menu_previous_book"], self, shortcut="Ctrl+H,2", triggered=self.previousMainBook))
        bibleNavigationMenu.addAction(QAction(config.thisTranslation["menu4_next"], self, shortcut="Ctrl+>", triggered=self.nextMainChapter))
        bibleNavigationMenu.addAction(QAction(config.thisTranslation["menu4_previous"], self, shortcut="Ctrl+<", triggered=self.previousMainChapter))

        scrollMenu = menu3.addMenu("&{0}".format(config.thisTranslation["menu_scroll"]))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_main_scroll_to_top"], self, shortcut="Ctrl+H,3",
                                          triggered=self.mainPageScrollToTop))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_main_page_down"], self, self, shortcut="Ctrl+H,4",
                                          triggered=self.mainPageScrollPageDown))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_main_page_up"], self, self, shortcut="Ctrl+H,5",
                                          triggered=self.mainPageScrollPageUp))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_study_scroll_to_top"], self,
                                      self, shortcut="Ctrl+H,6", triggered=self.studyPageScrollToTop))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_study_page_down"], self, self, shortcut="Ctrl+H,7",
                                      triggered=self.studyPageScrollPageDown))
        scrollMenu.addAction(QAction(config.thisTranslation["menu_study_page_up"], self, self, shortcut="Ctrl+H,8",
                                      triggered=self.studyPageScrollPageUp))
        menu3.addSeparator()
        toggleMenu = menu3.addMenu("&{0}".format(config.thisTranslation["menu_toggleFeatures"]))
        toggleMenu.addAction(QAction(config.thisTranslation["menu2_format"], self, shortcut="Ctrl+P", triggered=self.enableParagraphButtonClicked))
        toggleMenu.addAction(QAction(config.thisTranslation["menu2_subHeadings"], self, triggered=self.enableSubheadingButtonClicked))
        toggleMenu.addAction(QAction(config.thisTranslation["menu2_hover"], self, shortcut="Ctrl+=", triggered=self.enableInstantButtonClicked))
        if config.enableVerseHighlighting:
            toggleMenu.addAction(QAction(config.thisTranslation["menu2_toggleHighlightMarkers"], self, triggered=self.toggleHighlightMarker))
        toggleMenu.addAction(QAction(config.thisTranslation["menu_toggleEnforceCompareParallel"], self, triggered=self.enforceCompareParallelButtonClicked))
        toggleMenu.addAction(QAction(config.thisTranslation["menu_syncStudyWindowBible"], self, triggered=self.enableSyncStudyWindowBibleButtonClicked))
        toggleMenu.addAction(QAction(config.thisTranslation["menu_syncBibleCommentary"], self, triggered=self.enableSyncCommentaryButtonClicked))
        menu3.addSeparator()
        searchMenu = menu3.addMenu("&{0}".format(config.thisTranslation["menu5_search"]))
        searchMenu.addAction(QAction(config.thisTranslation["menu5_main"], self, shortcut="Ctrl+1", triggered=self.displaySearchBibleCommand))
        searchMenu.addAction(QAction(config.thisTranslation["menu5_study"], self, shortcut="Ctrl+2", triggered=self.displaySearchStudyBibleCommand))
        searchMenu.addAction(QAction(config.thisTranslation["menu5_bible"], self, triggered=self.displaySearchBibleMenu))
        if config.enableVerseHighlighting:
            searchMenu.addSeparator()
            searchMenu.addAction(QAction(config.thisTranslation["menu_highlight"], self, triggered=self.displaySearchHighlightCommand))

        menu3.addSeparator()

        mainWindowHistoryMenu = menu3.addMenu(config.thisTranslation["menu2_mainWindowHistory"])
        mainWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_main"], self, shortcut="Ctrl+'", triggered=self.mainHistoryButtonClicked))
        mainWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_mainBack"], self, shortcut="Ctrl+[", triggered=self.back))
        mainWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_mainForward"], self, shortcut="Ctrl+]", triggered=self.forward))
        
        studyWindowHistoryMenu = menu3.addMenu(config.thisTranslation["menu2_studyWindowHistory"])
        studyWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_study"], self, shortcut = 'Ctrl+"', triggered=self.studyHistoryButtonClicked))
        studyWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_studyBack"], self, shortcut="Ctrl+{", triggered=self.studyBack))
        studyWindowHistoryMenu.addAction(QAction(config.thisTranslation["menu3_studyForward"], self, shortcut="Ctrl+}", triggered=self.studyForward))
        
        menu3.addSeparator()
        menu3.addAction(QAction(config.thisTranslation["menu1_reload"], self, triggered=self.reloadCurrentRecord))

        menu4 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu4_further"]))

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
        verseFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_indexes"], self, shortcut="Ctrl+.", triggered=self.runINDEX))
        verseFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_crossRef"], self, shortcut="Ctrl+R", triggered=self.runCROSSREFERENCE))
        verseFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_tske"], self, shortcut="Ctrl+E", triggered=self.runTSKE))
        verseFeaturesMenu.addAction(QAction(config.thisTranslation["menu_more"], self, triggered=self.mainRefButtonClicked))

        wordFeaturesMenu = menu4.addMenu(config.thisTranslation["menu4_word"])
        wordFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_traslations"], self, triggered=self.runTRANSLATION))
        wordFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_discourse"], self, triggered=self.runDISCOURSE))
        wordFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_words"], self, triggered=self.runWORDS))
        wordFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_tdw"], self, shortcut="Ctrl+K", triggered=self.runCOMBO))
        menu4.addSeparator()

        compareFeaturesMenu = menu4.addMenu(config.thisTranslation["menu4_compareFeatures"])
        compareFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_compareAll"], self, shortcut="Ctrl+D", triggered=self.runCOMPARE))
        compareFeaturesMenu.addAction(QAction(config.thisTranslation["menu4_moreComparison"], self, triggered=self.mainRefButtonClicked))
        menu4.addSeparator()

        marvelBibleMenu = menu4.addMenu(config.thisTranslation["menu_marvelBibles"])
        marvelBibleMenu.addAction(QAction("Marvel Original Bible", self, shortcut="Ctrl+B, 1", triggered=self.runMOB))
        marvelBibleMenu.addAction(QAction("Marvel Interlinear Bible", self, shortcut="Ctrl+B, 2", triggered=self.runMIB))
        marvelBibleMenu.addAction(QAction("Marvel Trilingual Bible", self, shortcut="Ctrl+B, 3", triggered=self.runMTB))
        marvelBibleMenu.addAction(QAction("Marvel Parallel Bible", self, shortcut="Ctrl+B, 4", triggered=self.runMPB))
        marvelBibleMenu.addAction(QAction("Marvel Annotated Bible", self, shortcut="Ctrl+B, 5", triggered=self.runMAB))
        menu4.addSeparator()

        commentaryMenu = menu4.addMenu(config.thisTranslation["menu4_commentary"])
        commentaryMenu.addAction(QAction(config.thisTranslation["menu4_lastCommentary"], self, shortcut="Ctrl+Y", triggered=self.runCOMMENTARY))
        commentaryMenu.addAction(QAction("{0} {1}".format(config.thisTranslation["menu4_commentary"], config.thisTranslation["menu_bibleMenu"]), self, shortcut="Ctrl+Y", triggered=self.commentaryRefButtonClicked))

        # check if books in favourite list exist
        #for book in config.favouriteBooks:
        #if not os.path.isfile(os.path.join(config.marvelData, "books", "{0}.book".format(book))):
        #config.favouriteBooks.remove(book)

        # remove an old book from favourite list if it is not installed
        book = "Maps_ASB"
        if not os.path.isfile(os.path.join(config.marvelData, "books", "{0}.book".format(book))) and book in config.favouriteBooks:
            config.favouriteBooks.remove(book)

        menu10 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu10_books"]))
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
        menu10.addAction(QAction(config.thisTranslation["menu10_bookFromImages"], self, triggered=self.createBookModuleFromImages))
        menu10.addAction(QAction(config.thisTranslation["menu10_bookFromHtml"], self, triggered=self.createBookModuleFromHTML))
        menu10.addAction(QAction(config.thisTranslation["menu10_bookFromNotes"], self, triggered=self.createBookModuleFromNotes))
        menu10.addSeparator()
        menu10.addAction(QAction(config.thisTranslation["menu10_clearBookHighlights"], self, triggered=self.clearBookHighlights))

        menu5 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu5_lookup"]))
        menu5.addAction(QAction(config.thisTranslation["menu5_dictionary"], self, shortcut="Ctrl+3", triggered=self.searchCommandBibleDictionary))
        menu5.addAction(QAction(config.thisTranslation["context1_dict"], self, triggered=self.searchDictionaryDialog))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_encyclopedia"], self, shortcut="Ctrl+4", triggered=self.searchCommandBibleEncyclopedia))
        menu5.addAction(QAction(config.thisTranslation["context1_encyclopedia"], self, triggered=self.searchEncyclopediaDialog))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_book"], self, shortcut="Ctrl+5", triggered=self.displaySearchBookCommand))
        menu5.addAction(QAction(config.thisTranslation["menu5_selectBook"], self, triggered=self.searchBookDialog))
        menu5.addAction(QAction(config.thisTranslation["menu5_favouriteBook"], self, triggered=self.displaySearchFavBookCommand))
        menu5.addAction(QAction(config.thisTranslation["menu5_allBook"], self, triggered=self.displaySearchAllBookCommand))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_lastTopics"], self, shortcut="Ctrl+6", triggered=self.searchCommandBibleTopic))
        menu5.addAction(QAction(config.thisTranslation["menu5_topics"], self, triggered=self.searchTopicDialog))
        menu5.addAction(QAction(config.thisTranslation["menu5_allTopics"], self, triggered=self.searchCommandAllBibleTopic))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_characters"], self, shortcut="Ctrl+7", triggered=self.searchCommandBibleCharacter))
        menu5.addAction(QAction(config.thisTranslation["menu5_names"], self, shortcut="Ctrl+8", triggered=self.searchCommandBibleName))
        menu5.addAction(QAction(config.thisTranslation["menu5_locations"], self, shortcut="Ctrl+9", triggered=self.searchCommandBibleLocation))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_lexicon"], self, shortcut="Ctrl+0", triggered=self.searchCommandLexicon))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_last3rdDict"], self, triggered=self.searchCommandThirdPartyDictionary))
        menu5.addAction(QAction(config.thisTranslation["menu5_3rdDict"], self, triggered=self.search3rdDictionaryDialog))

        menu6 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_notes"]))

        chapterNotesMenu = menu6.addMenu("&{0}".format(config.thisTranslation["menu_chapterNotes"]))
        chapterNotesMenu.addAction(QAction(config.thisTranslation["bar1_menu"], self, triggered=self.openMainChapterNote))
        chapterNotesMenu.addAction(QAction(config.thisTranslation["bar2_menu"], self, triggered=self.openStudyChapterNote))
        
        verseNotesMenu = menu6.addMenu("&{0}".format(config.thisTranslation["menu_verseNotes"]))
        verseNotesMenu.addAction(QAction(config.thisTranslation["bar1_menu"], self, triggered=self.openMainVerseNote))
        verseNotesMenu.addAction(QAction(config.thisTranslation["bar2_menu"], self, triggered=self.openStudyVerseNote))
        
        searchNotesMenu = menu6.addMenu("&{0}".format(config.thisTranslation["menu_search"]))
        searchNotesMenu.addAction(QAction(config.thisTranslation["menu_bookNotes"], self, triggered=self.searchCommandBookNote))
        searchNotesMenu.addAction(QAction(config.thisTranslation["menu_chapterNotes"], self, triggered=self.searchCommandChapterNote))
        searchNotesMenu.addAction(QAction(config.thisTranslation["menu_verseNotes"], self, triggered=self.searchCommandVerseNote))
        searchNotesMenu.addAction(QAction(config.thisTranslation["menu10_clearBookHighlights"], self, triggered=self.clearNoteHighlights))

        if config.enableGist:
            menu6.addAction(QAction(config.thisTranslation["menu_gist"], self, triggered=self.showGistWindow))

        menu6.addSeparator()

        topicalNotesMenu = menu6.addMenu("&{0}".format(config.thisTranslation["menu7_topics"]))
        topicalNotesMenu.addAction(QAction(config.thisTranslation["menu7_read"], self, triggered=self.externalFileButtonClicked))
        topicalNotesMenu.addAction(QAction(config.thisTranslation["menu7_recent"], self, triggered=self.openExternalFileHistory))
        topicalNotesMenu.addAction(QAction(config.thisTranslation["menu7_open"], self, triggered=self.openTextFileDialog))

        noteEditorMenu = menu6.addMenu("&{0}".format(config.thisTranslation["note_editor"]))
        noteEditorMenu.addAction(QAction(config.thisTranslation["menu7_create"], self, shortcut="Ctrl+N", triggered=self.createNewNoteFile))
        noteEditorMenu.addAction(QAction(config.thisTranslation["menu7_edit"], self, triggered=self.editExternalFileButtonClicked))

        menu11 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu11_multimedia"]))
        menu11.addAction(QAction(config.thisTranslation["menu11_images"], self, triggered=self.openImagesFolder))
        menu11.addAction(QAction(config.thisTranslation["menu11_music"], self, triggered=self.openMusicFolder))
        menu11.addAction(QAction(config.thisTranslation["menu11_video"], self, triggered=self.openVideoFolder))
        menu11.addSeparator()
        menu11.addAction(QAction(config.thisTranslation["menu11_setupDownload"], self, triggered=self.setupYouTube))
        menu11.addAction(QAction(config.thisTranslation["menu11_youtube"], self, triggered=self.openYouTube))
        menu11.addSeparator()
        menu11.addAction(QAction("YouTube -> mp3", self, triggered=self.downloadMp3Dialog))
        menu11.addAction(QAction("YouTube -> mp4", self, triggered=self.downloadMp4Dialog))

        menu8 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu8_resources"]))
        menu8.addAction(QAction(config.thisTranslation["menu8_marvelData"], self, triggered=self.openMarvelDataFolder))
        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["menu8_bibles"], self, triggered=self.installMarvelBibles))
        menu8.addAction(QAction(config.thisTranslation["menu8_commentaries"], self, triggered=self.installMarvelCommentaries))
        menu8.addAction(QAction(config.thisTranslation["menu8_datasets"], self, triggered=self.installMarvelDatasets))
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
        menu8.addAction(QAction(config.thisTranslation["menu8_fixDatabase"], self, triggered=self.selectDatabaseToFix))

        if config.enableMacros:
            macros_menu = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu_macros"]))
            run_macros_menu = macros_menu.addMenu(config.thisTranslation["menu_run"])
            self.loadRunMacrosMenu(run_macros_menu)
            build_macros_menu = macros_menu.addMenu(config.thisTranslation["menu_build_macro"])
            build_macros_menu.addAction(QAction(config.thisTranslation["menu_command"], self, triggered=self.macroSaveCommand))
            build_macros_menu.addAction(QAction(config.thisTranslation["menu_highlight"], self, triggered=self.macroSaveHighlights))

        if config.showInformation:
            menu9 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu9_information"]))
            menu9.addAction(QAction(config.thisTranslation["menu1_wikiPages"], self, triggered=self.openUbaWiki))
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
            menu999 = self.menuBar().addMenu("&Developer")
            #menu999.addAction(QAction("Download Google Static Maps", self, triggered=self.downloadGoogleStaticMaps))
            menu999.addAction(QAction("testing", self, triggered=self.testing))

    def testing(self):
        #pass
        #test = BibleExplorer(self, (config.mainB, config.mainC, config.mainV, config.mainText))
        test = MasterControl(self)
        test.show()

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
            #button.setFixedSize(self.buttonWidth, self.buttonWidth)
            button.setFixedWidth(self.buttonWidth)
            #button.setFixedHeight(self.buttonWidth)
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

        self.mainTextMenuButton = QPushButton(self.verseReference("main")[0])
        toolTip = "{0} {1}".format(config.thisTranslation["bar1_menu"], config.thisTranslation["menu_bibleMenu"])
        self.addStandardTextButton(toolTip, self.mainTextMenu, self.firstToolBar, self.mainTextMenuButton, False)

        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        if config.qtMaterial and config.qtMaterialTheme:
            self.buttonWidth = self.mainTextMenuButton.height()

        self.mainRefButton = QPushButton(self.verseReference("main")[1])
        self.addStandardTextButton("bar1_reference", self.mainRefButtonClicked, self.firstToolBar, self.mainRefButton)

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

        self.studyTextMenuButton = QPushButton(self.verseReference("study")[0])
        toolTip = "{0} {1}".format(config.thisTranslation["bar2_menu"], config.thisTranslation["menu_bibleMenu"])
        self.addStandardTextButton(toolTip, self.studyTextMenu, self.studyBibleToolBar, self.studyTextMenuButton, False)

        self.studyRefButton = QPushButton(self.verseReference("study")[0])
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
        self.addStandardIconButton("menu4_previous", "previousChapter.png", self.previousMainChapter, self.leftToolBar)
        self.addStandardIconButton("menu4_next", "nextChapter.png", self.nextMainChapter, self.leftToolBar)
        self.leftToolBar.addSeparator()
        self.addStandardIconButton("menu4_compareAll", "compare_with.png", self.runCOMPARE, self.leftToolBar)
        self.addStandardIconButton("menu4_moreComparison", "parallel_with.png", self.mainRefButtonClicked, self.leftToolBar)
        self.addStandardIconButton(self.getEnableCompareParallelDisplayToolTip(), self.getEnableCompareParallelDisplay(), self.enforceCompareParallelButtonClicked, self.leftToolBar, None, False)
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

        self.mainTextMenuButton = QPushButton(self.verseReference("main")[0])
        self.mainTextMenuButton.setToolTip("{0} {1}".format(config.thisTranslation["bar1_menu"], config.thisTranslation["menu_bibleMenu"]))
        self.mainTextMenuButton.setStyleSheet(textButtonStyle)
        self.mainTextMenuButton.clicked.connect(self.mainTextMenu)
        self.firstToolBar.addWidget(self.mainTextMenuButton)

        self.mainRefButton = QPushButton(self.verseReference("main")[1])
        self.mainRefButton.setToolTip(config.thisTranslation["bar1_reference"])
        self.mainRefButton.setStyleSheet(textButtonStyle)
        self.mainRefButton.clicked.connect(self.mainRefButtonClicked)
        self.firstToolBar.addWidget(self.mainRefButton)

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

        self.studyTextMenuButton = QPushButton(self.verseReference("study")[0])
        self.studyTextMenuButton.setToolTip("{0} {1}".format(config.thisTranslation["bar2_menu"], config.thisTranslation["menu_bibleMenu"]))
        self.studyTextMenuButton.setStyleSheet(textButtonStyle)
        self.studyTextMenuButton.clicked.connect(self.studyTextMenu)
        self.studyBibleToolBar.addWidget(self.studyTextMenuButton)

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