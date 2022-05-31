from gui.MenuItems import *
from gui.CheckableComboBox import CheckableComboBox
from db.BiblesSqlite import BiblesSqlite
from util.ShortcutUtil import ShortcutUtil
from util.LanguageUtil import LanguageUtil
from util.Languages import Languages
from util.FileUtil import FileUtil
from util.WebtopUtil import WebtopUtil
import shortcut as sc
import re, os


# Search for material icons at: https://fonts.google.com/icons?selected=Material+Icons

class MaterialMainWindow:

    def create_menu(self):

        config.topToolBarOnly = False
        
        menuBar = self.menuBar()
        # 1st column
        menu = addMenu(menuBar, "menu1_app")
        items = (
            ("note_editor", self.createNewNoteFile, sc.createNewNoteFile),
        )
        for feature, action, shortcut in items:
            addMenuItem(menu, feature, self, action, shortcut)
        menu.addSeparator()
        items = (
            ("menu7_open", self.openTextFileDialog, sc.openTextFileDialog),
        )
        for feature, action, shortcut in items:
            addMenuItem(menu, feature, self, action, shortcut)

        subMenu = addSubMenu(menu, "saveFile")
        subMenu1 = addSubMenu(subMenu, "bibleWindowContent")
        items = [
            ("plainTextFile", self.savePlainText),
            ("htmlFile", self.saveHtml),
            ("pdfFile", self.savePdf),
        ]
        if config.isMarkdownInstalled:
            items.append(("markdownFile", self.saveMarkdown))
        if config.isHtmldocxInstalled:
            items.append(("wordFile", self.saveDocx))
        for feature, action in items:
            addMenuItem(subMenu1, feature, self, action)
        subMenu2 = addSubMenu(subMenu, "studyWindowContent")
        items = [
            ("plainTextFile", lambda: self.savePlainText("study")),
            ("htmlFile", lambda: self.saveHtml("study")),
            ("pdfFile", lambda: self.savePdf("study")),
        ]
        if config.isMarkdownInstalled:
            items.append(("markdownFile", lambda: self.saveMarkdown("study")))
        if config.isHtmldocxInstalled:
            items.append(("wordFile", lambda: self.saveDocx("study")))
        for feature, action in items:
            addMenuItem(subMenu2, feature, self, action)

        menu.addSeparator()

        # Clipboard Content
        subMenu = addSubMenu(menu, "menu1_clipboard")
        items = (
            ("pasteOnStudyWindow", self.pasteFromClipboard, None),
            ("context1_command", self.parseContentOnClipboard, sc.parseContentOnClipboard),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)

        menu.addSeparator()

        # Appearance
        subMenu0 = addSubMenu(menu, "appearance")
        # Window layout

        subMenu01 = addSubMenu(subMenu0, "menu2_view")
        subMenu = addSubMenu(subMenu01, "menu1_screenSize")
        items = (
            ("menu1_fullScreen", self.fullsizeWindow, sc.fullsizeWindow),
            ("menu1_maximized", self.maximizedWindow, sc.maximizedWindow),
            ("menu1_smallSize", self.twoThirdWindow, sc.twoThirdWindow),
            ("menu1_topHalf", self.topHalfScreenHeight, sc.topHalfScreenHeight),
            ("menu1_bottomHalf", self.bottomHalfScreenHeight, sc.bottomHalfScreenHeight),
            ("menu1_leftHalf", self.leftHalfScreenWidth, sc.leftHalfScreenWidth),
            ("menu1_rightHalf", self.rightHalfScreenWidth, sc.rightHalfScreenWidth),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        subMenu = addSubMenu(subMenu01, "menu2_toobars")
        items = (
            ("menu2_all", self.setNoToolBar, sc.setNoToolBar),
            ("menu2_topOnly", self.hideShowAdditionalToolBar, sc.hideShowAdditionalToolBar),
            ("menu2_top", self.hideShowMainToolBar, sc.hideShowMainToolBar),
            ("menu2_second", self.hideShowSecondaryToolBar, sc.hideShowSecondaryToolBar),
            ("menu2_left", self.hideShowLeftToolBar, sc.hideShowLeftToolBar),
            ("menu2_right", self.hideShowRightToolBar, sc.hideShowRightToolBar),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        subMenu01.addSeparator()
        items = (
            ("menu2_study", self.parallel, sc.parallel),
            ("menu2_bottom", self.cycleInstant, sc.cycleInstant),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu01, feature, self, action, shortcut)
        subMenu01.addSeparator()
        addMenuItem(subMenu01, "menu2_landscape", self, self.switchLandscapeMode)

        # Window style
        subMenu = addSubMenu(subMenu0, "menu1_selectWindowStyle")
        for style in QStyleFactory.keys():
            addCheckableMenuItem(subMenu, style, self, partial(self.setAppWindowStyle, style), config.windowStyle, style, None, False)
        # Menu layouts
        subMenu = addSubMenu(subMenu0, "menu1_selectMenuLayout")
        addMenuLayoutItems(self, subMenu)
        # Themes
        subMenu = addSubMenu(subMenu0, "menu1_selectTheme")
        themes = (
            "Light",
            "Dark",
            "Night",
        )
        for theme in themes:
            addCheckableMenuItem(subMenu, theme, self, partial(self.setTheme, theme), config.theme, "default" if theme == "Light" else theme.lower(), None, False)
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
        # Colour Customisation
        items = (
            ("colourCustomisation", self.changeButtonColour),
            #("customiseIconSize", self.setIconButtonSize),
        )
        for feature, action in items:
            addMenuItem(subMenu0, feature, self, action)
        # Icon Size Customisation
        subMenu = addSubMenu(subMenu0, "customiseIconSize")
        sizes = (12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48)
        for size in sizes:
            addCheckableMenuItem(subMenu, str(size), self, partial(self.setIconButtonSize, size), config.iconButtonSize, size, None, False)
        # Fonts
        subMenu = addSubMenu(subMenu0, "menu2_fonts")
        items = (
            ("menu1_setDefaultFont", self.setDefaultFont),
            ("menu1_setChineseFont", self.setChineseFont),
            ("individualBibles", self.selectDatabaseToModify),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        # Font Size
        subMenu = addSubMenu(subMenu0, "menu2_fontSize")
        items = (
            ("menu2_larger", self.largerFont, sc.largerFont),
            ("menu2_smaller", self.smallerFont, sc.smallerFont),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)

        # Other Preferences
        subMenu0 = addSubMenu(menu, "otherPreferences")

        # Control Preference
        subMenu = addSubMenu(subMenu0, "controlPreference")
        options = (
            ("master", "controlPanel"),
            ("mini", "menu1_miniControl"),
        )
        for option, description in options:
            addCheckableMenuItem(subMenu, description, self, partial(self.selectRefButtonSingleClickAction, option), config.refButtonClickAction, option)
        # Others
        items = (
            #("controlPreference", self.selectRefButtonSingleClickActionDialog),
            ("menu1_tabNo", self.setTabNumberDialog),
            #("menu1_setAbbreviations", self.setBibleAbbreviations),
            #("menu1_setMyFavouriteBible", self.openFavouriteBibleDialog),
            #("menu1_setMyFavouriteBible2", self.openFavouriteBibleDialog2),
            #("menu1_setMyFavouriteBible3", self.openFavouriteBibleDialog3),
            #("selectFavouriteHebrewGreekBible", self.openFavouriteMarvelBibleDialog),
            #("selectFavouriteHebrewGreekBible2", self.openFavouriteMarvelBibleDialog2),
            #("menu1_setDefaultStrongsHebrewLexicon", self.openSelectDefaultStrongsHebrewLexiconDialog),
            #("menu1_setDefaultStrongsGreekLexicon", self.openSelectDefaultStrongsGreekLexiconDialog),
        )
        for feature, action in items:
            addMenuItem(subMenu0, feature, self, action)
        # Verse number Action
        subMenu = addSubMenu(subMenu0, "selectVerseNumberAction")
        values = ("_noAction", "_cp0", "_cp1", "_cp2", "_cp3", "_cp4", "_cp5", "_cp6", "STUDY", "COMPARE", "CROSSREFERENCE", "TSKE", "TRANSLATION", "DISCOURSE", "WORDS", "COMBO", "INDEX", "COMMENTARY", "STUDY", "_menu")
        descriptions = ["noAction", "cp0", "cp1", "cp2", "cp3", "cp4", "cp5", "cp6", "openInStudyWindow", "menu4_compareAll", "menu4_crossRef", "menu4_tske", "menu4_traslations", "menu4_discourse", "menu4_words", "menu4_tdw", "menu4_indexes", "menu4_commentary", "menu_syncStudyWindowBible", "classicMenu"]
        options = dict(zip(values, descriptions))
        subMenu1 = addSubMenu(subMenu, "singleClick")
        for option, description in options.items():
            addCheckableMenuItem(subMenu1, description, self, partial(self.singleClickActionSelected, option), config.verseNoSingleClickAction, option)
        subMenu1 = addSubMenu(subMenu, "doubleClick")
        for option, description in options.items():
            addCheckableMenuItem(subMenu1, description, self, partial(self.doubleClickActionSelected, option), config.verseNoDoubleClickAction, option)
        # Abbreviation language
        subMenu = addSubMenu(subMenu0, "menu1_setAbbreviations")
        options = ("ENG", "TC", "SC")
        for option in options:
            addCheckableMenuItem(subMenu, option, self, partial(self.setBibleAbbreviationsSelected, option), config.standardAbbreviation, option, translation=False)
        # My Favourite Bibles
        subMenu = addSubMenu(subMenu0, "menu1_setMyFavouriteBible")
        for option in self.textList:
            addCheckableMenuItem(subMenu, option, self, partial(self.openFavouriteBibleSelected1, option), config.favouriteBible, option, translation=False)
        subMenu = addSubMenu(subMenu0, "menu1_setMyFavouriteBible2")
        for option in self.textList:
            addCheckableMenuItem(subMenu, option, self, partial(self.openFavouriteBibleSelected2, option), config.favouriteBible2, option, translation=False)
        subMenu = addSubMenu(subMenu0, "menu1_setMyFavouriteBible3")
        for option in self.textList:
            addCheckableMenuItem(subMenu, option, self, partial(self.openFavouriteBibleSelected3, option), config.favouriteBible3, option, translation=False)
        # My Favourite Hebrew & Greek Bibles
        subMenu = addSubMenu(subMenu0, "selectFavouriteHebrewGreekBible")
        for option in ("MOB", "MIB", "MTB", "MPB", "MAB"):
            addCheckableMenuItem(subMenu, option, self, partial(self.openFavouriteMarvelBibleSelected1, option), config.favouriteOriginalBible, option, translation=False)
        subMenu = addSubMenu(subMenu0, "selectFavouriteHebrewGreekBible2")
        for option in ("MOB", "MIB", "MTB", "MPB", "MAB"):
            addCheckableMenuItem(subMenu, option, self, partial(self.openFavouriteMarvelBibleSelected2, option), config.favouriteOriginalBible2, option, translation=False)
        # Default Lexicons
        subMenu = addSubMenu(subMenu0, "menu1_setDefaultStrongsHebrewLexicon")
        for option in self.lexiconList:
            addCheckableMenuItem(subMenu, option, self, partial(self.defaultStrongsHebrewLexiconSelected, option), config.defaultLexiconStrongH, option, translation=False)
        subMenu = addSubMenu(subMenu0, "menu1_setDefaultStrongsGreekLexicon")
        for option in self.lexiconList:
            addCheckableMenuItem(subMenu, option, self, partial(self.defaultStrongsGreekLexiconSelected, option), config.defaultLexiconStrongG, option, translation=False)
        # Markdown export heading style
        subMenu = addSubMenu(subMenu0, "markdownExportHeadingStyle")
        options = ("ATX", "ATX_CLOSED", "SETEXT", "UNDERLINED")
        for option in options:
            addCheckableMenuItem(subMenu, option, self, partial(self.setMarkdownExportHeadingStyle, option), config.markdownifyHeadingStyle, option, translation=False)
        # Default TTS voice
        if not config.noTtsFound:
            languages = self.getTtsLanguages()
            languageCodes = list(languages.keys())
            items = [languages[code][1] for code in languageCodes]
            
            subMenu = addSubMenu(subMenu0, "ttsLanguage")
            for index, item in enumerate(items):
                languageCode = languageCodes[index]
                addCheckableMenuItem(subMenu, item, self, partial(self.setDefaultTtsLanguage, languageCode), config.ttsDefaultLangauge, languageCode, translation=False)

        if config.developer:
            items = (
                ("setMaximumHistoryRecord", self.setMaximumHistoryRecordDialog),
                ("selectNoOfLinesPerChunkForParsing", self.setNoOfLinesPerChunkForParsingDialog),
                ("selectMaximumOHGBiVerses", self.setMaximumOHGBiVersesDisplayDialog),
                ("resourceDirectory", self.customMarvelData),
            )
            for feature, action in items:
                addMenuItem(subMenu0, feature, self, action)
        # Shortcuts
        subMenu = addSubMenu(subMenu0, "menu_shortcuts")
        items = (
            ("menu_micron", lambda: self.setShortcuts("micron"), "micron"),
        )
        for feature, action, thisValue in items:
            addCheckableMenuItem(subMenu, feature, self, action, config.menuShortcuts, thisValue)
        subMenu.addSeparator()
        items = (
            ("menu_brachys", lambda: self.setShortcuts("brachys"), "brachys"),
            ("menu_syntemno", lambda: self.setShortcuts("syntemno"), "syntemno"),
            ("menu_blank", lambda: self.setShortcuts("blank"), "blank"),
        )
        for feature, action, thisValue in items:
            addCheckableMenuItem(subMenu, feature, self, action, config.menuShortcuts, thisValue)
        for shortcut in ShortcutUtil.getListCustomShortcuts():
            addMenuItem(subMenu, shortcut, self, partial(self.setShortcuts, shortcut), None, False)
        # Language settings
        subMenu01 = addSubMenu(subMenu0, "languageSettings")
        subMenu = addSubMenu(subMenu01, "menu1_programInterface")
        for language in LanguageUtil.getNamesSupportedLanguages():
            addCheckableMenuItem(subMenu, language, self, partial(self.changeInterfaceLanguage, language), config.displayLanguage, Languages.code[language], translation=False)
        subMenu = addSubMenu(subMenu01, "watsonTranslator")
        items = (
            ("setup", self.setupWatsonTranslator),
            ("enterCredentials", self.showWatsonCredentialWindow),
            ("menu1_setMyLanguage", self.openTranslationLanguageDialog),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        if config.isOfflineTtsInstalled:
            languages = self.getTtsLanguages()
            languageCodes = list(languages.keys())
            items = [languages[code][1] for code in languageCodes]

            subMenu = addSubMenu(subMenu01, "ttsLanguage")
            for index, item in enumerate(items):
                languageCode = languageCodes[index]
                addMenuItem(subMenu, item, self, partial(self.setDefaultTtsLanguage, languageCode), translation=False)

        # Gist
        if config.developer:
            subMenu = addSubMenu(subMenu0, "gistSync")
            items = (
                ("setup", self.setupGist),
                ("menu_gist", self.showGistWindow),
            )
            for feature, action in items:
                addMenuItem(subMenu, feature, self, action)
        # Config Flags
        addMenuItem(menu, "menu_config_flags", self, self.moreConfigOptionsDialog, sc.moreConfigOptionsDialog)
        menu.addSeparator()
        if config.enableMacros:
            addMenuItem(menu, "menu_startup_macro", self, self.setStartupMacro)
            menu.addSeparator()
        addMenuItem(menu, "menu1_update", self, self.showUpdateAppWindow)
        menu.addSeparator()
        if hasattr(config, "cli"):
            addMenuItem(menu, "restart", self, self.restartApp)
        addIconMenuItem("UniqueBibleApp.png", menu, "menu1_exit", self, self.quitApp, sc.quitApp)

        # 2nd column
        menu = addMenu(menuBar, "menu_bible")
        subMenu = addSubMenu(menu, "favourite")
        subMenu1 = addSubMenu(subMenu, config.favouriteBible)
        items = (
            ("openInMainWindow", partial(self.runMainText, config.favouriteBible), sc.openFavouriteBibleOnMain1),
            ("openInStudyWindow", partial(self.runStudyText, config.favouriteBible), sc.openFavouriteBibleOnStudy1),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu1, feature, self, action, shortcut)
        subMenu2 = addSubMenu(subMenu, config.favouriteBible2)
        items = (
            ("openInMainWindow", partial(self.runMainText, config.favouriteBible2), sc.openFavouriteBibleOnMain2),
            ("openInStudyWindow", partial(self.runStudyText, config.favouriteBible2), sc.openFavouriteBibleOnStudy2),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu2, feature, self, action, shortcut)
        subMenu3 = addSubMenu(subMenu, config.favouriteBible3)
        items = (
            ("openInMainWindow", partial(self.runMainText, config.favouriteBible3), sc.openFavouriteBibleOnMain3),
            ("openInStudyWindow", partial(self.runStudyText, config.favouriteBible3), sc.openFavouriteBibleOnStudy3),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu3, feature, self, action, shortcut)
        subMenu3 = addSubMenu(subMenu, config.favouriteOriginalBible)
        items = (
            ("openInMainWindow", partial(self.runMainText, config.favouriteOriginalBible), sc.openFavouriteOriginalBibleOnMain),
            ("openInStudyWindow", partial(self.runStudyText, config.favouriteOriginalBible), sc.openFavouriteOriginalBibleOnStudy),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu3, feature, self, action, shortcut)
        subMenu3 = addSubMenu(subMenu, config.favouriteOriginalBible2)
        items = (
            ("openInMainWindow", partial(self.runMainText, config.favouriteOriginalBible2), sc.openFavouriteOriginalBibleOnMain2),
            ("openInStudyWindow", partial(self.runStudyText, config.favouriteOriginalBible2), sc.openFavouriteOriginalBibleOnStudy2),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu3, feature, self, action, shortcut)

        subMenu = addSubMenu(menu, "menu_navigation")
        items = (
            ("menu_next_book", self.nextMainBook, sc.nextMainBook),
            ("menu_previous_book", self.previousMainBook, sc.previousMainBook),
            ("menu4_next", self.nextMainChapter, sc.nextMainChapter),
            ("menu4_previous", self.previousMainChapter, sc.previousMainChapter),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        subMenu = addSubMenu(menu, "menu_scroll")
        items = (
            ("menu_main_scroll_to_top", self.mainPageScrollToTop, sc.mainPageScrollToTop),
            ("menu_main_page_up", self.mainPageScrollPageUp, sc.mainPageScrollPageUp),
            ("menu_main_page_down", self.mainPageScrollPageDown, sc.mainPageScrollPageDown),
            ("menu_study_scroll_to_top", self.studyPageScrollToTop, sc.studyPageScrollToTop),
            ("menu_study_page_up", self.studyPageScrollPageUp, sc.studyPageScrollPageUp),
            ("menu_study_page_down", self.studyPageScrollPageDown, sc.studyPageScrollPageDown),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        addMenuItem(menu, "swap", self, self.swapBibles, sc.swapBibles)
        
        menu.addSeparator()
        addMenuItem(menu, "liveFilter", self, self.showLiveFilterDialog, sc.liveFilterDialog)

        menu.addSeparator()
        subMenu = addSubMenu(menu, "menu_toggleFeatures")
        items = (
            ("formattedText", self.enableParagraphButtonClicked, sc.enableParagraphButtonClicked, config.readFormattedBibles),
            ("menu2_subHeadings", self.enableSubheadingButtonClicked2, sc.enableSubheadingButtonClicked, config.addTitleToPlainChapter),
            ("toggleFavouriteVersionIntoMultiRef", self.toggleFavouriteVersionIntoMultiRef, sc.toggleFavouriteVersionIntoMultiRef, config.addFavouriteToMultiRef),
            ("displayVerseReference", self.toggleShowVerseReference, sc.toggleShowVerseReference, config.showVerseReference),
            ("displayUserNoteIndicator", self.toggleShowUserNoteIndicator, sc.toggleShowUserNoteIndicator, config.showUserNoteIndicator),
            ("displayBibleNoteIndicator", self.toggleShowBibleNoteIndicator, sc.toggleShowBibleNoteIndicator, config.showBibleNoteIndicator),
            ("displayLexicalEntry", self.toggleHideLexicalEntryInBible, sc.toggleHideLexicalEntryInBible, (not config.hideLexicalEntryInBible)),
            ("displayHebrewGreekWordAudio", self.toggleShowHebrewGreekWordAudioLinks, sc.toggleShowWordAudio, config.showHebrewGreekWordAudioLinks),
            ("readTillChapterEnd", self.toggleReadTillChapterEnd, sc.toggleReadTillChapterEnd, config.readTillChapterEnd),
            ("instantHighlight", self.enableInstantHighlightButtonClicked, sc.toggleInstantHighlight, config.enableInstantHighlight),
            ("menu2_hover", self.enableInstantButtonClicked, sc.enableInstantButtonClicked, config.instantInformationEnabled),
            ("parallelMode", self.enforceCompareParallelButtonClicked, sc.enforceCompareParallel, config.enforceCompareParallel),
            ("studyBibleSyncsWithMainBible", self.enableSyncStudyWindowBibleButtonClicked, sc.syncStudyWindowBible, config.syncStudyWindowBibleWithMainWindow),
            ("commentarySyncsWithMainBible", self.enableSyncCommentaryButtonClicked, sc.syncStudyWindowCommentary, config.syncCommentaryWithMainWindow),
        )
        for feature, action, shortcut, currentValue in items:
            addCheckableMenuItem(subMenu, feature, self, action, currentValue, True, shortcut)
        if config.enableVerseHighlighting:
            addCheckableMenuItem(subMenu, "menu2_toggleHighlightMarkers", self, self.toggleHighlightMarker, config.showHighlightMarkers, True, sc.toggleHighlightMarker)

        # 3rd column
        menu = addMenu(menuBar, "controlPanel")

        # Collections
        subMenu = addSubMenu(menu, "collections")
        items = (
            ("bibleCollections", self.showBibleCollectionDialog, sc.bibleCollections),
            ("libraryCatalog", self.showLibraryCatalogDialog, sc.showLibraryCatalogDialog),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        menu.addSeparator()

        # Cli interface
        if hasattr(config, "cli"):
            addMenuItem(menu, "cli", self, lambda: self.mainView.currentWidget().switchToCli(), sc.commandLineInterface)
            menu.addSeparator()

        # Master Control Tabs
        items = (sc.openControlPanelTab0, sc.openControlPanelTab1, sc.openControlPanelTab2,
                                          sc.openControlPanelTab3, sc.openControlPanelTab4,
                                          sc.openControlPanelTab5, sc.openControlPanelTab6)
        for index, shortcut in enumerate(items):
        # removed sc.openControlPanelTab7 until morophology search tab is fixed.
            addMenuItem(menu, "cp{0}".format(index), self, partial(self.openControlPanelTab, index), shortcut)
        menu.addSeparator()
        # Mini Control Tabs
        addMenuItem(menu, "menu1_miniControl", self, self.manageMiniControl, sc.manageMiniControl)
        tabs = ("bible", "translations", "commentaries", "lexicons", "dictionaries", "bookIntro")
        subMenu = addSubMenu(menu, "miniControlTabs")
        for index, tab in enumerate(tabs):
            addMenuItem(subMenu, tab, self, partial(self.openMiniControlTab, index))
        menu.addSeparator()

        # Media Player
        if WebtopUtil.isPackageInstalled("vlc") or config.isVlcInstalled:
            subMenu = addSubMenu(menu, "mediaPlayer")
            items = (
                ("launch", self.openVlcPlayer, sc.launchMediaPlayer),
                ("stop", self.closeMediaPlayer, sc.stopMediaPlayer),
            )
            for feature, action, shortcut in items:
                addMenuItem(subMenu, feature, self, action, shortcut)
            menu.addSeparator()
        
        # Reload
        subMenu = addSubMenu(menu, "menu_reload")
        items = (
            ("content", lambda: self.reloadCurrentRecord(True), sc.reloadCurrentRecord),
            ("menu8_resources", self.reloadResources, None),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)

        # 4th column
        menu = addMenu(menuBar, "menu8_resources")
        subMenu = addSubMenu(menu, "folders")
        items = (
            ("menu8_marvelData", self.openMarvelDataFolder),
            ("menu11_images", self.openImagesFolder),
            ("menu11_audio", self.openAudioFolder),
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
            ("installBooks", self.installBooks),
            ("menu8_download3rdParty", self.moreBooks),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)

        addGithubDownloadMenuItems(self, subMenu)

        menu.addSeparator()
        subMenu = addSubMenu(menu, "import")
        items = (
            ("menu8_plusDictionaries", self.importBBPlusDictionaryInAFolder),
            ("menu8_plusLexicons", self.importBBPlusLexiconInAFolder),
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
            ("menu10_bookFromPDF", self.createBookModuleFromPDF),
            ("devotionalFromNotes", self.createDevotionalFromNotes),
            ("commentaryFromNotes", self.createCommentaryFromNotes),
            ("lexiconFromNotes", self.createLexiconFromNotes),
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
            macros_menu = self.menuBar().addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation["menu_macros"]))
            run_macros_menu = macros_menu.addMenu(config.thisTranslation["menu_run"])
            self.loadRunMacrosMenu(run_macros_menu)
            build_macros_menu = macros_menu.addMenu(config.thisTranslation["menu_build_macro"])
            addBuildMacroMenuItems(self, build_macros_menu)

        # plugins
        if config.enablePlugins:
            menu = addMenu(menuBar, "menu_plugins")
            for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "menu"), "py"):
                if not plugin in config.excludeMenuPlugins:
                    if "_" in plugin:
                        feature, shortcut = plugin.split("_", 1)
                        # Note the difference between PySide2 & PyQt5
                        # For PySide2
                        #addMenuItem(menu, feature, self, lambda plugin=plugin: self.runPlugin(plugin), shortcut=shortcut, translation=False)
                        # For PyQt5
                        #addMenuItem(menu, feature, self, lambda arg, plugin=plugin: self.runPlugin(plugin), shortcut=shortcut, translation=False)
                        # For both PySide2 and PyQt5
                        addMenuItem(menu, feature, self, partial(self.runPlugin, plugin), shortcut=shortcut, translation=False)
                    else:
                        # For PySide2
                        #addMenuItem(menu, plugin, self, lambda plugin=plugin: self.runPlugin(plugin), translation=False)
                        # For PyQt5
                        #addMenuItem(menu, plugin, self, lambda arg, plugin=plugin: self.runPlugin(plugin), translation=False)
                        # For both PySide2 and PyQt5
                        addMenuItem(menu, plugin, self, partial(self.runPlugin, plugin), translation=False)
            menu.addSeparator()
            addMenuItem(menu, "enableIndividualPlugins", self, self.enableIndividualPluginsWindow)

        # information
        if config.showInformation:
            menu = addMenu(menuBar, "menu9_information")
            addMenuItem(menu, "menu_keyboard_shortcuts", self, self.displayShortcuts, sc.displayShortcuts)
            menu.addSeparator()
            addMenuItem(menu, "latestChanges", self, self.showInfo)
            addMenuItem(menu, "ubaCommands", self, self.showCommandDocumentation)
            addMenuItem(menu, "config.py", self, self.showConfigPyDocumentation, translation=False)
            menu.addSeparator()
            subMenu = addSubMenu(menu, "menu_support")
            items = (
                ("menu1_wikiPages", self.openUbaWiki, sc.ubaWiki),
                ("menu_discussions", self.openUbaDiscussions, sc.ubaDiscussions),
                ("report", self.reportAnIssue, None),
            )
            for feature, action, shortcut in items:
                addMenuItem(subMenu, feature, self, action, shortcut)
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
                ("Unique Bible App", self.openUniqueBibleSource),
                ("Open Hebrew Bible", self.openHebrewBibleSource),
                ("Open Greek New Testament", self.openOpenGNTSource),
            )
            for feature, action in items:
                addMenuItem(subMenu, feature, self, action, None, False)
            menu.addSeparator()
            items = (
                ("menu9_contact", self.contactEliranWong),
            )
            for feature, action in items:
                addMenuItem(menu, feature, self, action)
            menu.addSeparator()
            addMenuItem(menu, "menu9_donate", self, self.donateToUs)

        if config.docker:
            menu = addMenu(menuBar, "menu_apps")
            with open("/defaults/menu.xml", "r") as fileObj:
                for line in fileObj.readlines():
                    if "icon=" in line and not 'label="Unique Bible App"' in line:
                        line = re.sub('^.*?<item label="(.*?)" icon="(.*?)"><action name="Execute"><command>(.*?)</command></action></item>.*?$', r'\1,\2,\3', line)
                        webtopApp, icon, command = line[:-1].split(",", 3)
                        addIconMenuItem(icon, menu, webtopApp, self, partial(WebtopUtil.run, command), "", translation=False)

        if config.developer:
            menu = addMenu(menuBar, "developer")
            #addMenuItem(menu, "Download Google Static Maps", self, self.downloadGoogleStaticMaps, None, False)
            if config.docker:
                icon = "/usr/share/pixmaps/pycharm.png"
                addIconMenuItem(icon, menu, "Pycharm", self, self.pycharm, "", translation=False)
                icon = "/usr/share/pixmaps/vscodium.png"
                addIconMenuItem(icon, menu, "VS Code", self,
                                partial(self.webtopAurApp, "vscodium", "vscodium-bin"),
                                "", translation=False)
                icon = "/usr/share/icons/hicolor/256x256/apps/sqlitebrowser.png"
                addIconMenuItem(icon, menu, "Sqlite Browser", self,
                                partial(self.webtopApp, "sqlitebrowser"),
                                "", translation=False)
                menu.addSeparator()
            addMenuItem(menu, "checkLanguageFiles", self, lambda: LanguageUtil.checkLanguageStringToAllFiles("checked"))
            addMenuItem(menu, "edit_language_file", self, self.selectLanguageFileToEdit)
            addMenuItem(menu, "selectTooltipTranslation", self, self.selectReferenceTranslation)
            addMenuItem(menu, "editWorkingTranslation", self, self.editWorkingTranslation)
            addMenuItem(menu, "addLanguageFiles", self, self.showAddLanguageItemWindow)
            addMenuItem(menu, "updateLanguageFiles", self, self.showUpdateLanguageItemWindow)

    def setupToolBarStandardIconSize(self):
        
        self.firstToolBar = QToolBar()
        self.firstToolBar.setWindowTitle(config.thisTranslation["bar1_title"])
        self.firstToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.firstToolBar)

        # Master Control
        #icon = "material/navigation/unfold_more/materialiconsoutlined/48dp/2x/outline_unfold_more_black_48dp.png"
        icon = "material/image/tune/materialiconsoutlined/48dp/2x/outline_tune_black_48dp.png"
        self.addMaterialIconButton("cp0", icon, self.mainTextMenu, self.firstToolBar)

        #icon = "htmlResources/material/action/settings/materialiconsoutlined/48dp/2x/outline_settings_black_48dp.png"
        #icon = "htmlResources/material/av/playlist_add_circle/materialiconsoutlined/48dp/2x/outline_playlist_add_circle_black_48dp.png"
        #icon = "htmlResources/material/navigation/more_vert/materialiconsoutlined/48dp/2x/outline_more_vert_black_48dp.png"
        icon = "htmlResources/material/content/stacked_bar_chart/materialiconsround/18dp/2x/round_stacked_bar_chart_black_18dp.png"
        iconFile = os.path.join(*icon.split("/"))
        self.firstToolBar.addAction(self.getMaskedQIcon(iconFile, config.maskMaterialIconColor, config.maskMaterialIconBackground), config.thisTranslation["bibleCollections"], self.showBibleCollectionDialog)

        # Version selection

        if config.refButtonClickAction == "mini":
            self.versionCombo = None
            self.bibleSelection = None
            self.versionButton = QPushButton(config.mainText)
            self.addStandardTextButton("bibleVersion", self.versionButtonClicked, self.firstToolBar, self.versionButton)
        else:
            self.versionButton = None
            self.versionCombo = None
            self.bibleSelection = QToolButton()
            #self.bibleSelection.setMinimumWidth(int(config.iconButtonSize * 3))
            self.bibleSelection.setMaximumWidth(int(config.iconButtonSize * 7))
            self.setBibleSelection()
            self.firstToolBar.addWidget(self.bibleSelection)
#            self.versionCombo = QComboBox()
#            self.bibleVersions = BiblesSqlite().getBibleList()
#            self.versionCombo.addItems(self.bibleVersions)
#            initialIndex = 0
#            if config.mainText in self.bibleVersions:
#                initialIndex = self.bibleVersions.index(config.mainText)
#            self.versionCombo.setCurrentIndex(initialIndex)
#            self.versionCombo.currentIndexChanged.connect(self.changeBibleVersion)
#            self.versionCombo.setMaximumWidth(int(config.iconButtonSize * 7))
#            self.firstToolBar.addWidget(self.versionCombo)

        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        # Icon size is now controlled by gui/Styles.py
#        if config.qtMaterial and config.qtMaterialTheme:
#            versionButtonHeight = self.versionButton.height() if config.refButtonClickAction == "mini" else self.versionCombo.height() 
#            config.iconButtonWidth = config.maximumIconButtonWidth if versionButtonHeight > config.maximumIconButtonWidth else versionButtonHeight

#        items = self.textList
#        self.bibleVersionCombo = CheckableComboBox(items, config.compareParallelList, toolTips=self.textFullNameList)
#        self.bibleVersionCombo.setMaximumWidth(int(config.iconButtonSize * 7))
#        self.firstToolBar.addWidget(self.bibleVersionCombo)

        self.bibleSelectionForComparison = QToolButton()
        self.bibleSelectionForComparison.setMinimumWidth(int(config.iconButtonSize * 4))
        self.bibleSelectionForComparison.setMaximumWidth(int(config.iconButtonSize * 7))
        self.setBibleSelectionForComparison()
        self.firstToolBar.addWidget(self.bibleSelectionForComparison)

        #icon = "material/image/navigate_before/materialiconsoutlined/48dp/2x/outline_navigate_before_black_48dp.png"
        #self.addMaterialIconButton("menu_previous_chapter", icon, self.previousMainChapter, self.firstToolBar)
        icon = "htmlResources/material/image/navigate_before/materialiconsoutlined/48dp/2x/outline_navigate_before_black_48dp.png"
        iconFile = os.path.join(*icon.split("/"))
        self.firstToolBar.addAction(self.getMaskedQIcon(iconFile, config.maskMaterialIconColor, config.maskMaterialIconBackground), config.thisTranslation["menu_previous_chapter"], self.previousMainChapter)

        self.mainB = QToolButton()
        self.mainC = QToolButton()
        self.mainV = QToolButton()
        self.setMainRefMenu()
        self.firstToolBar.addWidget(self.mainB)
        self.firstToolBar.addWidget(self.mainC)
        self.firstToolBar.addWidget(QLabel(":"))
        self.firstToolBar.addWidget(self.mainV)

        #icon = "material/image/navigate_next/materialiconsoutlined/48dp/2x/outline_navigate_next_black_48dp.png"
        #self.addMaterialIconButton("menu_next_chapter", icon, self.nextMainChapter, self.firstToolBar)
        icon = "htmlResources/material/image/navigate_next/materialiconsoutlined/48dp/2x/outline_navigate_next_black_48dp.png"
        iconFile = os.path.join(*icon.split("/"))
        self.firstToolBar.addAction(self.getMaskedQIcon(iconFile, config.maskMaterialIconColor, config.maskMaterialIconBackground), config.thisTranslation["menu_next_chapter"], self.nextMainChapter)

        icon = "material/action/ads_click/materialiconsoutlined/48dp/2x/outline_ads_click_black_48dp.png"
        self.addMaterialIconButton("singleVersion", icon, self.openMainChapterMaterial, self.firstToolBar)
        icon = "material/image/auto_awesome_motion/materialiconsoutlined/48dp/2x/outline_auto_awesome_motion_black_48dp.png"
        self.addMaterialIconButton("parallelVersions", icon, lambda: self.runCompareAction("PARALLEL"), self.firstToolBar)
        icon = "material/action/view_column/materialiconsoutlined/48dp/2x/outline_view_column_black_48dp.png"
        self.addMaterialIconButton("sideBySideComparison", icon, lambda: self.runCompareAction("SIDEBYSIDE"), self.firstToolBar)
        icon = "material/editor/table_rows/materialiconsoutlined/48dp/2x/outline_table_rows_black_48dp.png"
        self.addMaterialIconButton("rowByRowComparison", icon, lambda: self.runCompareAction("COMPARE"), self.firstToolBar)

        self.firstToolBar.addSeparator()

        if os.path.isfile(os.path.join("plugins", "menu", "Interlinear Data.py")):
            icon = "material/image/flare/materialiconsoutlined/48dp/2x/outline_flare_black_48dp.png"
            self.addMaterialIconButton("interlinearData", icon, partial(self.runPlugin, "Interlinear Data"), self.firstToolBar)
        if os.path.isfile(os.path.join("plugins", "menu", "Bible Reading Plan.py")):
            icon = "material/action/calendar_month/materialiconsoutlined/48dp/2x/outline_calendar_month_black_48dp.png"
            self.addMaterialIconButton("bibleReadingPlan", icon, partial(self.runPlugin, "Bible Reading Plan"), self.firstToolBar)
            self.firstToolBar.addSeparator()

        icon = "material/action/zoom_in/materialiconsoutlined/48dp/2x/outline_zoom_in_black_48dp.png"
        self.addMaterialIconButton("masterSearch", icon, self.displaySearchBibleMenu, self.firstToolBar)
        icon = "material/action/filter_alt/materialiconsoutlined/48dp/2x/outline_filter_alt_black_48dp.png"
        self.addMaterialIconButton("liveFilter", icon, self.showLiveFilterDialog, self.firstToolBar)

        self.firstToolBar.addSeparator()

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.setClearButtonEnabled(True)
        self.textCommandLineEdit.setToolTip(config.thisTranslation["bar1_command"])
        self.textCommandLineEdit.setMinimumWidth(100)
        self.textCommandLineEdit.textChanged.connect(self.runInstantHighlight)
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        if not config.preferControlPanelForCommandLineEntry:
            self.firstToolBar.addWidget(self.textCommandLineEdit)
            self.firstToolBar.addSeparator()

        self.enableInstantHighlightButton = QPushButton()
        self.addMaterialIconButton(self.getInstantHighlightToolTip(), self.getInstantHighlightDisplay(), self.enableInstantHighlightButtonClicked, self.firstToolBar, self.enableInstantHighlightButton, False)

        #self.firstToolBar.addSeparator()

        icon = "material/action/open_in_new/materialiconsoutlined/48dp/2x/outline_open_in_new_black_48dp.png"
        self.addMaterialIconButton("goOnline", icon, self.goOnline, self.firstToolBar)
        icon = "material/social/share/materialiconsoutlined/48dp/2x/outline_share_black_48dp.png"
        self.addMaterialIconButton("share", icon, self.shareOnline, self.firstToolBar)

        self.firstToolBar.addSeparator()

        self.enableStudyBibleButton = QPushButton()
        self.addMaterialIconButton(self.getStudyBibleDisplayToolTip(), self.getStudyBibleDisplay(), self.enableStudyBibleButtonClicked, self.firstToolBar, self.enableStudyBibleButton, False)

        # Toolbar height here is affected by the actual size of icon file used in a QAction
        # Icon size is now controlled by gui/Styles.py
#        if config.qtMaterial and config.qtMaterialTheme:
#            self.firstToolBar.setFixedHeight(config.iconButtonWidth + 4)
#            self.firstToolBar.setIconSize(QSize(int(config.iconButtonWidth / 2), int(config.iconButtonWidth / 2)))
#        else:
#            self.firstToolBar.setIconSize(QSize(17, 17))

        # QAction can use setVisible whereas QPushButton cannot when it is placed on a toolbar.
        # Old single button
        #self.studyRefButton = self.firstToolBar.addAction(":::".join(self.verseReference("study")), self.studyRefButtonClickedMaterial)

        self.studyBibleSelection = QToolButton()
        self.studyBibleSelection.setMaximumWidth(int(config.iconButtonSize * 7))
        self.setStudyBibleSelection()
        self.firstToolBar.addWidget(self.studyBibleSelection)

        self.studyB = QToolButton()
        self.studyC = QToolButton()
        self.studyRefLabel = QLabel(":")
        self.studyV = QToolButton()
        self.setStudyRefMenu()
        self.firstToolBar.addWidget(self.studyB)
        self.firstToolBar.addWidget(self.studyC)
        self.firstToolBar.addWidget(self.studyRefLabel)
        self.firstToolBar.addWidget(self.studyV)
        
        iconFile = os.path.join("htmlResources", self.getSyncStudyWindowBibleDisplay())
        self.enableSyncStudyWindowBibleButton = self.firstToolBar.addAction(self.getMaskedQIcon(iconFile, config.maskMaterialIconColor, config.maskMaterialIconBackground), self.getSyncStudyWindowBibleDisplayToolTip(), self.enableSyncStudyWindowBibleButtonClicked)
        icon = "htmlResources/material/communication/swap_calls/materialiconsoutlined/48dp/2x/outline_swap_calls_black_48dp.png"
        iconFile = os.path.join(*icon.split("/"))
        self.swapBibleButton = self.firstToolBar.addAction(self.getMaskedQIcon(iconFile, config.maskMaterialIconColor, config.maskMaterialIconBackground), config.thisTranslation["swap"], self.swapBibles)
        if config.openBibleInMainViewOnly:
            #self.studyRefButton.setVisible(False)
            self.studyBibleSelection.setDisabled(True)
            self.studyB.setDisabled(True)
            self.studyC.setDisabled(True)
            self.studyRefLabel.setDisabled(False)
            self.studyV.setDisabled(False)
            self.enableSyncStudyWindowBibleButton.setVisible(False)
            self.swapBibleButton.setVisible(False)
        self.firstToolBar.addSeparator()

        icon = "material/notification/more/materialiconsoutlined/48dp/2x/outline_more_black_48dp.png"
        self.addMaterialIconButton("bar1_toolbars", icon, self.hideShowAdditionalToolBar, self.firstToolBar)

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

        icon = "material/image/auto_stories/materialiconsoutlined/48dp/2x/outline_auto_stories_black_48dp.png"
        self.addMaterialIconButton("libraryCatalog", icon, self.showLibraryCatalogDialog, self.secondToolBar)

        # Commentary selection

        if config.refButtonClickAction == "mini":
            self.commentaryCombo = None
            self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
            self.addStandardTextButton("menu4_commentary", self.commentaryRefButtonClicked, self.secondToolBar, self.commentaryRefButton)
        else:
            self.commentaryRefButton = None
            self.commentaryCombo = QComboBox()
            self.commentaryCombo.addItems(self.commentaryList)
            initialIndex = 0
            if config.commentaryText in self.commentaryList:
                initialIndex = self.commentaryList.index(config.commentaryText)
            self.commentaryCombo.setCurrentIndex(initialIndex)
            self.commentaryCombo.currentIndexChanged.connect(self.changeCommentaryVersion)
            self.commentaryCombo.setMaximumWidth(int(config.iconButtonSize * 7))
            self.secondToolBar.addWidget(self.commentaryCombo)

        self.enableSyncCommentaryButton = QPushButton()
        self.addMaterialIconButton(self.getSyncCommentaryDisplayToolTip(), self.getSyncCommentaryDisplay(), self.enableSyncCommentaryButtonClicked, self.secondToolBar, self.enableSyncCommentaryButton, False)
        self.secondToolBar.addSeparator()

        icon = "material/image/navigate_before/materialiconsoutlined/48dp/2x/outline_navigate_before_black_48dp.png"
        self.addMaterialIconButton("menu_previous_chapter", icon, self.openBookPreviousChapter, self.secondToolBar)
        self.bookButton = QPushButton(config.book[:20])
        self.bookButton.setMaximumWidth(int(config.iconButtonSize * 7))
        self.addStandardTextButton(config.book, self.openBookMenu, self.secondToolBar, self.bookButton, translation=False)
        icon = "material/image/navigate_next/materialiconsoutlined/48dp/2x/outline_navigate_next_black_48dp.png"
        self.addMaterialIconButton("menu_next_chapter", icon, self.openBookNextChapter, self.secondToolBar)

        icon = "material/action/search/materialiconsoutlined/48dp/2x/outline_search_black_48dp.png"
        self.addMaterialIconButton("bar2_searchBooks", icon, self.searchBookCommand, self.secondToolBar)

        self.secondToolBar.addSeparator()

#        icon = "material/maps/rate_review/materialiconsoutlined/48dp/2x/outline_rate_review_black_48dp.png"
#        self.addMaterialIconButton("menu_bookNote", icon, self.openMainBookNote, self.secondToolBar)
#        icon = "material/file/drive_file_rename_outline/materialiconsoutlined/48dp/2x/outline_drive_file_rename_outline_black_48dp.png"
#        self.addMaterialIconButton("menu_chapterNote", icon, self.openMainChapterNote, self.secondToolBar)
#        icon = "material/editor/edit_note/materialiconsoutlined/48dp/2x/outline_edit_note_black_48dp.png"
#        self.addMaterialIconButton("menu_verseNote", icon, self.openMainVerseNote, self.secondToolBar)
#
#        self.secondToolBar.addSeparator()

        icon = "material/action/note_add/materialiconsoutlined/48dp/2x/outline_note_add_black_48dp.png"
        self.addMaterialIconButton("menu7_create", icon, self.createNewNoteFile, self.secondToolBar)
        icon = "material/file/file_open/materialiconsoutlined/48dp/2x/outline_file_open_black_48dp.png"
        self.addMaterialIconButton("menu7_open", icon, self.openTextFileDialog, self.secondToolBar)

        fileName = self.getLastExternalFileName()
        self.externalFileButton = QPushButton(fileName[:20])
        self.externalFileButton.setMaximumWidth(int(config.iconButtonSize * 7))
        self.addStandardTextButton(fileName, self.externalFileButtonClicked, self.secondToolBar, self.externalFileButton, translation=False)

        icon = "material/image/edit/materialiconsoutlined/48dp/2x/outline_edit_black_48dp.png"
        self.addMaterialIconButton("menu7_edit", icon, self.editExternalFileButtonClicked, self.secondToolBar)

        self.secondToolBar.addSeparator()

        if os.path.isfile(os.path.join("plugins", "context", "English Dictionaries_Ctrl+Shift+D.py")):
            icon = "material/action/abc/materialiconsoutlined/48dp/2x/outline_abc_black_48dp.png"
            self.addMaterialIconButton("englishDictionaries", icon, lambda: self.mainView.currentWidget().runPlugin("English Dictionaries_Ctrl+Shift+D"), self.secondToolBar)
        if not config.noTtsFound:
            icon = "material/action/record_voice_over/materialiconsoutlined/48dp/2x/outline_record_voice_over_black_48dp.png"
            triggered = lambda: self.mainView.currentWidget().googleTextToSpeechLanguage("", True) if config.isGoogleCloudTTSAvailable or ((not config.isOfflineTtsInstalled or config.forceOnlineTts) and config.isGTTSInstalled) else lambda: self.mainView.currentWidget().textToSpeech(True)
            self.addMaterialIconButton("context1_speak", icon, triggered, self.secondToolBar)
        self.secondToolBar.addSeparator()


        if os.path.isfile(os.path.join("plugins", "menu", "ePub Viewer.py")):
            icon = "material/action/book/materialiconsoutlined/48dp/2x/outline_book_black_48dp.png"
            self.addMaterialIconButton("epubReader", icon, partial(self.runPlugin, "ePub Viewer"), self.secondToolBar)
        icon = "material/action/description/materialiconsoutlined/48dp/2x/outline_description_black_48dp.png"
        self.addMaterialIconButton("wordDocument", icon, self.openDocxDialog, self.secondToolBar)
        icon = "material/image/picture_as_pdf/materialiconsoutlined/48dp/2x/outline_picture_as_pdf_black_48dp.png"
        self.addMaterialIconButton("pdfDocument", icon, self.openPdfDialog, self.secondToolBar)
        icon = "material/content/save_as/materialiconsoutlined/48dp/2x/outline_save_as_black_48dp.png"
        self.addMaterialIconButton("savePdfCurrentPage", icon, self.invokeSavePdfPage, self.secondToolBar)

        self.secondToolBar.addSeparator()

        icon = "material/editor/text_decrease/materialiconsoutlined/48dp/2x/outline_text_decrease_black_48dp.png"
        self.addMaterialIconButton("menu2_smaller", icon, self.smallerFont, self.secondToolBar)

        #self.defaultFontButton = QPushButton("{0} {1}".format(config.font, config.fontSize))
        self.defaultFontButton = QPushButton(str(config.fontSize))
        self.defaultFontButton.setMaximumWidth(int(config.iconButtonSize * 2))
        self.addStandardTextButton("menu1_setDefaultFont", self.setDefaultFont, self.secondToolBar, self.defaultFontButton)

        icon = "material/editor/text_increase/materialiconsoutlined/48dp/2x/outline_text_increase_black_48dp.png"
        self.addMaterialIconButton("menu2_larger", icon, self.largerFont, self.secondToolBar)
        self.secondToolBar.addSeparator()
        icon = "material/av/play_circle/materialiconsoutlined/48dp/2x/outline_play_circle_black_48dp.png"
        self.addMaterialIconButton("media", icon, partial(self.openControlPanelTab, 6), self.secondToolBar)
        if config.isYoutubeDownloaderInstalled:
            icon = "material/hardware/browser_updated/materialiconsoutlined/48dp/2x/outline_browser_updated_black_48dp.png"
            self.addMaterialIconButton("menu11_youtube", icon, self.openYouTube, self.secondToolBar)
        self.secondToolBar.addSeparator()

        self.enableInstantButton = QPushButton()
        self.addMaterialIconButton(self.getInstantLookupDisplayToolTip(), self.getInstantInformation(), self.enableInstantButtonClicked, self.secondToolBar, self.enableInstantButton, False)
        icon = "material/content/bolt/materialiconsoutlined/48dp/2x/outline_bolt_black_48dp.png"
        self.addMaterialIconButton("menu2_bottom", icon, self.cycleInstant, self.secondToolBar)
        self.secondToolBar.addSeparator()

        icon = "material/navigation/refresh/materialiconsoutlined/48dp/2x/outline_refresh_black_48dp.png"
        self.addMaterialIconButton("menu1_reload", icon, lambda: self.reloadCurrentRecord(True), self.secondToolBar)
        icon = "material/action/fit_screen/materialiconsoutlined/48dp/2x/outline_fit_screen_black_48dp.png"
        self.addMaterialIconButton("menu1_fullScreen", icon, self.fullsizeWindow, self.secondToolBar)
        icon = "material/communication/cancel_presentation/materialiconsoutlined/48dp/2x/outline_cancel_presentation_black_48dp.png"
        self.addMaterialIconButton("clearAll", icon, self.clearAllWindowTabs, self.secondToolBar)
        self.secondToolBar.addSeparator()

        # Left tool bar
        self.leftToolBar = QToolBar()
        self.leftToolBar.setWindowTitle(config.thisTranslation["bar3_title"])
        self.leftToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.LeftToolBarArea, self.leftToolBar)

        icon = "material/image/navigate_before/materialiconsoutlined/48dp/2x/outline_navigate_before_black_48dp.png"
        self.addMaterialIconButton("menu3_mainBack", icon, self.back, self.leftToolBar)
        icon = "material/action/history/materialiconsoutlined/48dp/2x/outline_history_black_48dp.png"
        self.addMaterialIconButton("menu3_main", icon, self.mainHistoryButtonClicked, self.leftToolBar)
        icon = "material/image/navigate_next/materialiconsoutlined/48dp/2x/outline_navigate_next_black_48dp.png"
        self.addMaterialIconButton("menu3_mainForward", icon, self.forward, self.leftToolBar)
        self.leftToolBar.addSeparator()
        if config.isHtmldocxInstalled:
            icon = "material/action/description/materialiconsoutlined/48dp/2x/outline_description_black_48dp.png"
            self.addMaterialIconButton("exportToDocx", icon, self.exportMainPageToDocx, self.leftToolBar)
        icon = "material/image/picture_as_pdf/materialiconsoutlined/48dp/2x/outline_picture_as_pdf_black_48dp.png"
        self.addMaterialIconButton("bar3_pdf", icon, self.printMainPage, self.leftToolBar)
        self.leftToolBar.addSeparator()
        self.enableParagraphButton = QPushButton()
        self.addMaterialIconButton(self.getReadFormattedBiblesToolTip(), self.getReadFormattedBibles(), self.enableParagraphButtonClicked, self.leftToolBar, self.enableParagraphButton, False)
        iconFile = os.path.join("htmlResources", self.getAddSubheading())
        self.enableSubheadingButton = self.leftToolBar.addAction(self.getMaskedQIcon(iconFile, config.maskMaterialIconColor, config.maskMaterialIconBackground), self.enableSubheadingToolTip(), self.enableSubheadingButtonClicked2)
        if config.readFormattedBibles:
            self.enableSubheadingButton.setVisible(False)
        self.leftToolBar.addSeparator()
        icon = "material/action/compare_arrows/materialiconsoutlined/48dp/2x/outline_compare_arrows_black_48dp.png"
        self.addMaterialIconButton("menu4_compareAll", icon, self.runCOMPARE, self.leftToolBar)
        icon = "material/image/compare/materialicons/48dp/2x/baseline_compare_black_48dp.png"
        self.addMaterialIconButton("contrasts", icon, self.runCONTRASTS, self.leftToolBar)
        self.enforceCompareParallelButton = QPushButton()
        self.addMaterialIconButton(self.getEnableCompareParallelDisplayToolTip(), self.getEnableCompareParallelDisplay(), self.enforceCompareParallelButtonClicked, self.leftToolBar, self.enforceCompareParallelButton, False)
        self.leftToolBar.addSeparator()
        icon = "material/image/wb_sunny/materialiconsoutlined/48dp/2x/outline_wb_sunny_black_48dp.png"
        self.addMaterialIconButton("Marvel Original Bible", icon, self.runMOB, self.leftToolBar, None, False)
        icon = "material/maps/layers/materialiconsoutlined/48dp/2x/outline_layers_black_48dp.png"
        self.addMaterialIconButton("Marvel Interlinear Bible", icon, self.runMIB, self.leftToolBar, None, False)
        icon = "material/file/workspaces/materialiconsoutlined/48dp/2x/outline_workspaces_black_48dp.png"
        self.addMaterialIconButton("Marvel Trilingual Bible", icon, self.runMTB, self.leftToolBar, None, False)
        icon = "material/action/horizontal_split/materialiconsoutlined/48dp/2x/outline_horizontal_split_black_48dp.png"
        self.addMaterialIconButton("Marvel Parallel Bible", icon, self.runMPB, self.leftToolBar, None, False)
        icon = "material/editor/schema/materialiconsoutlined/48dp/2x/outline_schema_black_48dp.png"
        self.addMaterialIconButton("Marvel Annotated Bible", icon, self.runMAB, self.leftToolBar, None, False)
        self.leftToolBar.addSeparator()

        icon = "material/image/auto_fix_normal/materialiconsoutlined/48dp/2x/outline_auto_fix_normal_black_48dp.png"
        self.addMaterialIconButton("instantHighlight", icon, lambda: self.mainView.currentWidget().instantHighlight(), self.leftToolBar)
        icon = "material/image/auto_fix_off/materialiconsoutlined/48dp/2x/outline_auto_fix_off_black_48dp.png"
        self.addMaterialIconButton("removeInstantHighlight", icon, lambda: self.mainView.currentWidget().removeInstantHighlight(), self.leftToolBar)
        self.leftToolBar.addSeparator()

        icon = "material/navigation/refresh/materialiconsoutlined/48dp/2x/outline_refresh_black_48dp.png"
        self.addMaterialIconButton("menu1_reload", icon, lambda: self.mainView.currentWidget().page().triggerAction(QWebEnginePage.Reload), self.leftToolBar)
        icon = "material/action/fit_screen/materialiconsoutlined/48dp/2x/outline_fit_screen_black_48dp.png"
        self.addMaterialIconButton("menu1_fullScreen", icon, lambda: self.mainView.currentWidget().openOnFullScreen(), self.leftToolBar)
        icon = "material/communication/cancel_presentation/materialiconsoutlined/48dp/2x/outline_cancel_presentation_black_48dp.png"
        self.addMaterialIconButton("clearAll", icon, self.clearAllMainWindowTabs, self.leftToolBar)
        self.leftToolBar.addSeparator()

        # Right tool bar
        self.rightToolBar = QToolBar()
        self.rightToolBar.setWindowTitle(config.thisTranslation["bar4_title"])
        self.rightToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.RightToolBarArea, self.rightToolBar)

        #icon = "material/navigation/arrow_back_ios/materialiconsoutlined/48dp/2x/outline_arrow_back_ios_black_48dp.png"
        icon = "material/image/navigate_before/materialiconsoutlined/48dp/2x/outline_navigate_before_black_48dp.png"
        self.addMaterialIconButton("menu3_studyBack", icon, self.studyBack, self.rightToolBar)
        icon = "material/action/history/materialiconsoutlined/48dp/2x/outline_history_black_48dp.png"
        self.addMaterialIconButton("menu3_study", icon, self.studyHistoryButtonClicked, self.rightToolBar)
        #icon = "material/navigation/arrow_forward_ios/materialiconsoutlined/48dp/2x/outline_arrow_forward_ios_black_48dp.png"
        icon = "material/image/navigate_next/materialiconsoutlined/48dp/2x/outline_navigate_next_black_48dp.png"
        self.addMaterialIconButton("menu3_studyForward", icon, self.studyForward, self.rightToolBar)
        self.rightToolBar.addSeparator()
        if config.isHtmldocxInstalled:
            icon = "material/action/description/materialiconsoutlined/48dp/2x/outline_description_black_48dp.png"
            self.addMaterialIconButton("exportToDocx", icon, self.exportStudyPageToDocx, self.rightToolBar)
        icon = "material/image/picture_as_pdf/materialiconsoutlined/48dp/2x/outline_picture_as_pdf_black_48dp.png"
        self.addMaterialIconButton("bar3_pdf", icon, self.printStudyPage, self.rightToolBar)
        self.rightToolBar.addSeparator()
        icon = "material/editor/highlight/materialiconsoutlined/48dp/2x/outline_highlight_black_48dp.png"
        self.addMaterialIconButton("menu4_indexes", icon, self.runINDEX, self.rightToolBar)
        icon = "material/maps/local_library/materialiconsoutlined/48dp/2x/outline_local_library_black_48dp.png"
        self.addMaterialIconButton("menu4_commentary", icon, self.runCOMMENTARY, self.rightToolBar)
        self.rightToolBar.addSeparator()
        icon = "material/editor/insert_link/materialiconsoutlined/48dp/2x/outline_insert_link_black_48dp.png"
        self.addMaterialIconButton("menu4_crossRef", icon, self.runCROSSREFERENCE, self.rightToolBar)
        icon = "material/maps/diamond/materialiconsoutlined/48dp/2x/outline_diamond_black_48dp.png"
        self.addMaterialIconButton("menu4_tske", icon, self.runTSKE, self.rightToolBar)
        self.rightToolBar.addSeparator()

        #icon = "material/maps/layers/materialiconsoutlined/48dp/2x/outline_layers_black_48dp.png"
        icon = "material/image/auto_awesome/materialiconsoutlined/48dp/2x/outline_auto_awesome_black_48dp.png"
        self.addMaterialIconButton("openFavouriteHebrewGreekBible", icon, self.runMIBStudy, self.rightToolBar)
        icon = "material/action/translate/materialiconsoutlined/48dp/2x/outline_translate_black_48dp.png"
        self.addMaterialIconButton("menu4_traslations", icon, self.runTRANSLATION, self.rightToolBar)
        icon = "material/editor/align_horizontal_right/materialicons/48dp/2x/baseline_align_horizontal_right_black_48dp.png"
        self.addMaterialIconButton("menu4_discourse", icon, self.runDISCOURSE, self.rightToolBar)
        icon = "material/action/drag_indicator/materialiconsoutlined/48dp/2x/outline_drag_indicator_black_48dp.png"
        self.addMaterialIconButton("menu4_words", icon, self.runWORDS, self.rightToolBar)
        icon = "material/device/widgets/materialiconsoutlined/48dp/2x/outline_widgets_black_48dp.png"
        self.addMaterialIconButton("menu4_tdw", icon, self.runCOMBO, self.rightToolBar)
        self.rightToolBar.addSeparator()
#        self.enableInstantButton = QPushButton()
#        self.addMaterialIconButton(self.getInstantLookupDisplayToolTip(), self.getInstantInformation(), self.enableInstantButtonClicked, self.rightToolBar, self.enableInstantButton, False)
#        icon = "material/content/bolt/materialiconsoutlined/48dp/2x/outline_bolt_black_48dp.png"
#        self.addMaterialIconButton("menu2_bottom", icon, self.cycleInstant, self.rightToolBar)
#        self.rightToolBar.addSeparator()

        icon = "material/image/auto_fix_normal/materialiconsoutlined/48dp/2x/outline_auto_fix_normal_black_48dp.png"
        self.addMaterialIconButton("instantHighlight", icon, lambda: self.studyView.currentWidget().instantHighlight(), self.rightToolBar)
        icon = "material/image/auto_fix_off/materialiconsoutlined/48dp/2x/outline_auto_fix_off_black_48dp.png"
        self.addMaterialIconButton("removeInstantHighlight", icon, lambda: self.studyView.currentWidget().removeInstantHighlight(), self.rightToolBar)
        self.rightToolBar.addSeparator()

        icon = "material/navigation/refresh/materialiconsoutlined/48dp/2x/outline_refresh_black_48dp.png"
        self.addMaterialIconButton("menu1_reload", icon, lambda: self.studyView.currentWidget().page().triggerAction(QWebEnginePage.Reload), self.rightToolBar)
        icon = "material/action/fit_screen/materialiconsoutlined/48dp/2x/outline_fit_screen_black_48dp.png"
        self.addMaterialIconButton("menu1_fullScreen", icon, lambda: self.studyView.currentWidget().openOnFullScreen(), self.rightToolBar)
        icon = "material/communication/cancel_presentation/materialiconsoutlined/48dp/2x/outline_cancel_presentation_black_48dp.png"
        self.addMaterialIconButton("clearAll", icon, self.clearAllStudyWindowTabs, self.rightToolBar)
        self.rightToolBar.addSeparator()