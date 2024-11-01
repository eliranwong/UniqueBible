from uniquebible.gui.MenuItems import *
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QSize
else:
    from qtpy.QtCore import QSize
from uniquebible.util.ShortcutUtil import ShortcutUtil
from uniquebible.util.LanguageUtil import LanguageUtil
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.WebtopUtil import WebtopUtil
import uniquebible.shortcut as sc
import re, os


class FocusMainWindow:

    def create_menu(self):

        config.syncStudyWindowBibleWithMainWindow = False
        config.syncCommentaryWithMainWindow = False
        config.topToolBarOnly = False
        
        menuBar = self.menuBar()
        # 1st column
        menu = addMenu(menuBar, "menu1_app")
        items = (
            ("menu7_create", self.createNewNoteFile, sc.createNewNoteFile),
            ("menu7_open", self.openTextFileDialog, sc.openTextFileDialog),
        )
        for feature, action, shortcut in items:
            addMenuItem(menu, feature, self, action, shortcut)
        menu.addSeparator()
        subMenu0 = addSubMenu(menu, "menu1_preferences")
        subMenu = addSubMenu(subMenu0, "menu1_generalPreferences")
        items = (
            ("bibleCollections", self.showBibleCollectionDialog),
            ("refButtonAction", self.selectRefButtonSingleClickActionDialog),
            ("colourCustomisation", self.changeButtonColour),
            ("menu1_tabNo", self.setTabNumberDialog),
            ("menu1_setAbbreviations", self.setBibleAbbreviations),
            ("menu1_setMyFavouriteBible", self.openFavouriteBibleDialog),
            ("menu1_setDefaultStrongsHebrewLexicon", self.openSelectDefaultStrongsHebrewLexiconDialog),
            ("menu1_setDefaultStrongsGreekLexicon", self.openSelectDefaultStrongsGreekLexiconDialog),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        if config.developer:
            items = (
                ("setMaximumHistoryRecord", self.setMaximumHistoryRecordDialog),
                ("selectNoOfLinesPerChunkForParsing", self.setNoOfLinesPerChunkForParsingDialog),
                ("selectMaximumOHGBiVerses", self.setMaximumOHGBiVersesDisplayDialog),
                ("resourceDirectory", self.customMarvelData),
            )
            for feature, action in items:
                addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(subMenu0, "menu1_selectWindowStyle")
        for style in QStyleFactory.keys():
            addMenuItem(subMenu, style, self, partial(self.setAppWindowStyle, style), None, False)
        subMenu = addSubMenu(subMenu0, "menu1_selectTheme")
        if config.qtMaterial:
            qtMaterialThemes = ("light_amber.xml",  "light_blue.xml",  "light_cyan.xml",  "light_cyan_500.xml",  "light_lightgreen.xml",  "light_pink.xml",  "light_purple.xml",  "light_red.xml",  "light_teal.xml",  "light_yellow.xml", "dark_amber.xml",  "dark_blue.xml",  "dark_cyan.xml",  "dark_lightgreen.xml",  "dark_pink.xml",  "dark_purple.xml",  "dark_red.xml",  "dark_teal.xml",  "dark_yellow.xml")
            for theme in qtMaterialThemes:
                addMenuItem(subMenu, theme[:-4], self, partial(self.setQtMaterialTheme, theme), None, False)
            subMenu.addSeparator()
            addMenuItem(subMenu, "disableQtMaterial", self, lambda: self.enableQtMaterial(False))
        else:
            items = (
                ("menu_light_theme", lambda: self.setTheme("default")),
                ("menu1_dark_theme", lambda: self.setTheme("dark")),
                ("night_theme", lambda: self.setTheme("night")),
            )
            for feature, action in items:
                addMenuItem(subMenu, feature, self, action)

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
            subMenu.addSeparator()
            addMenuItem(subMenu, "enableQtMaterial", self, lambda: self.enableQtMaterial(True))
        subMenu = addSubMenu(subMenu0, "menu1_selectMenuLayout")
        addMenuLayoutItems(self, subMenu)

        subMenu = addSubMenu(subMenu0, "menu_shortcuts")
        items = (
            ("menu_brachys", lambda: self.setShortcuts("brachys")),
            ("menu_micron", lambda: self.setShortcuts("micron")),
            ("menu_syntemno", lambda: self.setShortcuts("syntemno")),
            ("menu_blank", lambda: self.setShortcuts("blank")),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        for shortcut in ShortcutUtil.getListCustomShortcuts():
            addMenuItem(subMenu, shortcut, self, partial(self.setShortcuts, shortcut), None, False)
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
            ("individualBibles", self.selectDatabaseToModify),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(subMenu0, "menu2_fontSize")
        items = (
            ("menu2_larger", self.largerFont, sc.largerFont),
            ("menu2_smaller", self.smallerFont, sc.smallerFont),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        if config.developer:
            subMenu = addSubMenu(subMenu0, "gistSync")
            items = (
                ("setup", self.setupGist),
                ("menu_gist", self.showGistWindow),
            )
            for feature, action in items:
                addMenuItem(subMenu, feature, self, action)
        items = (
            ("menu_config_flags", self.moreConfigOptionsDialog),
        )
        for feature, action in items:
            addMenuItem(subMenu0, feature, self, action)

        subMenu0 = addSubMenu(menu, "menu2_view")
        subMenu = addSubMenu(subMenu0, "menu1_screenSize")
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
        subMenu = addSubMenu(subMenu0, "menu2_toobars")
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
        subMenu0.addSeparator()
        items = (
            ("menu2_study", self.parallel, sc.parallel),
            ("menu2_bottom", self.cycleInstant, sc.cycleInstant),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu0, feature, self, action, shortcut)
        subMenu0.addSeparator()
        addMenuItem(subMenu0, "menu2_landscape", self, self.switchLandscapeMode)

        subMenu0 = addSubMenu(menu, "languageSettings")
        subMenu = addSubMenu(subMenu0, "menu1_programInterface")
        for language in LanguageUtil.getNamesSupportedLanguages():
            addMenuItem(subMenu, language, self, partial(self.changeInterfaceLanguage, language), translation=False)
        subMenu = addSubMenu(subMenu0, "watsonTranslator")
        items = (
            ("setup", self.setupWatsonTranslator),
            ("enterCredentials", self.showWatsonCredentialWindow),
            ("menu1_setMyLanguage", self.openTranslationLanguageDialog),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        if ("OfflineTts" in config.enabled):
            languages = self.getTtsLanguages()
            languageCodes = list(languages.keys())
            items = [languages[code][1] for code in languageCodes]
            
            subMenu = addSubMenu(subMenu0, "ttsLanguage")
            for index, item in enumerate(items):
                languageCode = languageCodes[index]
                addMenuItem(subMenu, item, self, partial(self.setDefaultTtsLanguage, languageCode), translation=False)
            #addMenuItem(subMenu0, "ttsLanguage", self, self.setDefaultTtsLanguageDialog)

        addMenuItem(menu, "configFlags", self, self.moreConfigOptionsDialog, sc.moreConfigOptionsDialog)
        menu.addSeparator()
        if config.enableMacros:
            addMenuItem(menu, "menu_startup_macro", self, self.setStartupMacro)
        subMenu = addSubMenu(menu, "menu1_clipboard")
        items = (
            ("menu1_readClipboard", self.pasteFromClipboard, None),
            ("menu1_runClipboard", self.parseContentOnClipboard, sc.parseContentOnClipboard),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        menu.addSeparator()
        if ("Htmldocx" in config.enabled):
            subMenu = addSubMenu(menu, "exportToDocx")
            items = (
                ("bar1_menu", self.exportMainPageToDocx),
                ("bar2_menu", self.exportStudyPageToDocx),
            )
            for feature, action in items:
                addMenuItem(subMenu, feature, self, action)
        subMenu = addSubMenu(menu, "bar3_pdf")
        items = (
            ("bar1_menu", self.printMainPage),
            ("bar2_menu", self.printStudyPage),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        #menu.addSeparator()
        #addMenuItem(menu, "menu1_update", self, self.showUpdateAppWindow)
        menu.addSeparator()
        if hasattr(config, "cli"):
            addMenuItem(menu, "restart", self, self.restartApp)
        addIconMenuItem("UniqueBibleApp.png", menu, "menu1_exit", self, self.quitApp, sc.quitApp)

        # 2nd column
        menu = addMenu(menuBar, "menu_bible")
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
        menu.addSeparator()
        subMenu = addSubMenu(menu, "verseNoAction")
        items = (
            ("singleClick", self.selectSingleClickActionDialog),
            ("doubleClick", self.selectDoubleClickActionDialog),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        menu.addSeparator()
        subMenu = addSubMenu(menu, "menu_toggleFeatures")
        items = (
            ("menu2_format", self.enableParagraphButtonClicked, sc.enableParagraphButtonClicked),
            ("menu2_subHeadings", self.enableSubheadingButtonClicked, sc.enableSubheadingButtonClicked),
            ("displayVerseReference", self.toggleShowVerseReference, sc.toggleShowVerseReference),
            ("displayUserNoteIndicator", self.toggleShowUserNoteIndicator, sc.toggleShowUserNoteIndicator),
            ("displayBibleNoteIndicator", self.toggleShowBibleNoteIndicator, sc.toggleShowBibleNoteIndicator),
            ("displayLexicalEntry", self.toggleHideLexicalEntryInBible, sc.toggleHideLexicalEntryInBible),
            ("displayHebrewGreekWordAudio", self.toggleShowHebrewGreekWordAudioLinks, sc.toggleShowWordAudio),
            ("readTillChapterEnd", self.toggleReadTillChapterEnd, sc.toggleReadTillChapterEnd),
            ("menu2_hover", self.enableInstantButtonClicked, sc.enableInstantButtonClicked),
            ("menu_toggleEnforceCompareParallel", self.enforceCompareParallelButtonClicked, sc.enforceCompareParallel),
            ("menu_syncStudyWindowBible", self.enableSyncStudyWindowBibleButtonClicked, sc.syncStudyWindowBible),
            ("menu_syncBibleCommentary", self.enableSyncCommentaryButtonClicked, sc.syncStudyWindowCommentary),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        if config.enableVerseHighlighting:
            addMenuItem(subMenu, "menu2_toggleHighlightMarkers", self, self.toggleHighlightMarker, sc.toggleHighlightMarker)

        # 3rd column
        menu = addMenu(menuBar, "controlPanel")
        if hasattr(config, "cli"):
            addMenuItem(menu, "cli", self, lambda: self.mainView.currentWidget().switchToCli(), sc.commandLineInterface)
            menu.addSeparator()
        for index, shortcut in enumerate((sc.openControlPanelTab0, sc.openControlPanelTab1, sc.openControlPanelTab2,
                                          sc.openControlPanelTab3, sc.openControlPanelTab4, sc.openControlPanelTab5,
                                          sc.openControlPanelTab6, sc.openControlPanelTab7)):
            addMenuItem(menu, "cp{0}".format(index), self, partial(self.openControlPanelTab, index), shortcut)
        menu.addSeparator()
        addMenuItem(menu, "menu1_miniControl", self, self.manageMiniControl, sc.manageMiniControl)
        tabs = ("bible", "translations", "commentaries", "lexicons", "dictionaries", "bookIntro")
        subMenu = addSubMenu(menu, "miniControlTabs")
        for index, tab in enumerate(tabs):
            addMenuItem(subMenu, tab, self, partial(self.openMiniControlTab, index))
        menu.addSeparator()
        addMenuItem(menu, "libraryCatalog", self, self.showLibraryCatalogDialog, sc.showLibraryCatalogDialog)
        menu.addSeparator()
        addMenuItem(menu, "liveFilter", self, self.showLiveFilterDialog, sc.liveFilterDialog)
        menu.addSeparator()
        addMenuItem(menu, "reloadResources", self, self.reloadResources)
        addMenuItem(menu, "menu1_reload", self, lambda: self.reloadCurrentRecord(True), sc.reloadCurrentRecord)

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
            for plugin in FileUtil.fileNamesWithoutExtension(os.path.join(config.packageDir, "plugins", "menu"), "py"):
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

        if (config.runMode == "docker"):
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
            if (config.runMode == "docker"):
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

        button = QPushButton("<")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_previous_chapter", self.previousMainChapter, self.firstToolBar, button)
        self.mainRefButton = QPushButton(self.verseReference("main")[-1])
        self.addStandardTextButton("bar1_reference", self.mainRefButtonClicked, self.firstToolBar, self.mainRefButton)
        button = QPushButton(">")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_next_chapter", self.nextMainChapter, self.firstToolBar, button)

        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        if config.qtMaterial and config.qtMaterialTheme:
            mainRefButtonHeight = self.mainRefButton.height() 
            config.iconButtonWidth = config.maximumIconButtonWidth if mainRefButtonHeight > config.maximumIconButtonWidth else mainRefButtonHeight

        self.addStandardIconButton("menu_bookNote", "noteBook.png", self.openMainBookNote, self.firstToolBar)
        self.addStandardIconButton("menu_chapterNote", "noteChapter.png", self.openMainChapterNote, self.firstToolBar)
        self.addStandardIconButton("menu_verseNote", "noteVerse.png", self.openMainVerseNote, self.firstToolBar)

        # Version selection
        self.addBibleVersionButton()

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

        # Toolbar height here is affected by the actual size of icon file used in a QAction
        if config.qtMaterial and config.qtMaterialTheme:
            self.firstToolBar.setFixedHeight(config.iconButtonWidth + 4)
            self.firstToolBar.setIconSize(QSize(int(config.iconButtonWidth / 2), int(config.iconButtonWidth / 2)))
        else:
            self.firstToolBar.setIconSize(QSize(17, 17))
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

        button = QPushButton("<")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_previous_chapter", self.openBookPreviousChapter, self.secondToolBar, button)
        self.bookButton = QPushButton(config.book[:20])
        self.addStandardTextButton(config.book, self.openBookMenu, self.secondToolBar, self.bookButton, translation=False)
        button = QPushButton(">")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_next_chapter", self.openBookNextChapter, self.secondToolBar, button)

        self.addStandardIconButton("bar2_searchBooks", "search.png", self.displaySearchBookCommand, self.secondToolBar)

        self.secondToolBar.addSeparator()

        self.addStandardIconButton("menu7_create", "newfile.png", self.createNewNoteFile, self.secondToolBar)
        self.addStandardIconButton("menu7_open", "open.png", self.openTextFileDialog, self.secondToolBar)

        fileName = self.getLastExternalFileName()
        self.externalFileButton = QPushButton(fileName[:20])
        self.addStandardTextButton(fileName, self.externalFileButtonClicked, self.secondToolBar, self.externalFileButton, translation=False)

        self.addStandardIconButton("wordDocument", "docx.png", self.openDocxDialog, self.secondToolBar)
        self.addStandardIconButton("pdfDocument", "pdfOpen.png", self.openPdfDialog, self.secondToolBar)
        self.addStandardIconButton("savePdfCurrentPage", "save.png", self.invokeSavePdfPage, self.secondToolBar)
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
        self.addStandardIconButton("menu1_reload", "reload.png", lambda: self.reloadCurrentRecord(True), self.secondToolBar)
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
        if ("Htmldocx" in config.enabled):
            self.addStandardIconButton("exportToDocx", "docx.png", self.exportMainPageToDocx, self.leftToolBar)
        self.addStandardIconButton("bar3_pdf", "pdf.png", self.printMainPage, self.leftToolBar)
        self.leftToolBar.addSeparator()
        self.enableParagraphButton = QPushButton()
        self.addStandardIconButton("menu2_format", self.getReadFormattedBibles(), self.enableParagraphButtonClicked, self.leftToolBar, self.enableParagraphButton)
        self.enableSubheadingButton = QPushButton()
        self.addStandardIconButton("menu2_subHeadings", self.getAddSubheading(), self.enableSubheadingButtonClicked, self.leftToolBar, self.enableSubheadingButton)
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
        if ("Htmldocx" in config.enabled):
            self.addStandardIconButton("exportToDocx", "docx.png", self.exportStudyPageToDocx, self.rightToolBar)
        self.addStandardIconButton("bar3_pdf", "pdf.png", self.printStudyPage, self.rightToolBar)
        self.rightToolBar.addSeparator()
        self.addStandardIconButton("Marvel Interlinear Bible", "interlinear.png", self.runMIBStudy, self.rightToolBar, None, False)
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
        self.enableInstantButton = QPushButton()
        self.addStandardIconButton("menu2_hover", self.getInstantInformation(), self.enableInstantButtonClicked, self.rightToolBar, self.enableInstantButton)
        self.addStandardIconButton("menu2_bottom", "lightning.png", self.cycleInstant, self.rightToolBar)
        self.rightToolBar.addSeparator()

    def setupToolBarFullIconSize(self):

        textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"

        self.firstToolBar = QToolBar()
        self.firstToolBar.setWindowTitle(config.thisTranslation["bar1_title"])
        self.firstToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.firstToolBar)

        button = QPushButton("<")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_previous_chapter", self.previousMainChapter, self.firstToolBar, button)
        self.mainRefButton = QPushButton(":::".join(self.verseReference("main")))
        self.mainRefButton.setToolTip(config.thisTranslation["bar1_reference"])
        self.mainRefButton.setStyleSheet(textButtonStyle)
        self.mainRefButton.clicked.connect(self.mainRefButtonClicked)
        self.firstToolBar.addWidget(self.mainRefButton)
        button = QPushButton(">")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_next_chapter", self.nextMainChapter, self.firstToolBar, button)

        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        if config.qtMaterial and config.qtMaterialTheme:
            mainRefButtonHeight = self.mainRefButton.height() 
            config.iconButtonWidth = config.maximumIconButtonWidth if mainRefButtonHeight > config.maximumIconButtonWidth else mainRefButtonHeight

        iconFile = os.path.join("htmlResources", "noteBook.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu_bookNote"], self.openMainBookNote)

        iconFile = os.path.join("htmlResources", "noteChapter.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu_chapterNote"], self.openMainChapterNote)

        iconFile = os.path.join("htmlResources", "noteVerse.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu_verseNote"], self.openMainVerseNote)

        # Version selection
        self.addBibleVersionButton()

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

        button = QPushButton("<")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_previous_chapter", self.openBookPreviousChapter, self.secondToolBar, button)
        self.bookButton = QPushButton(config.book)
        self.bookButton.setToolTip(config.thisTranslation["menu5_book"])
        self.bookButton.setStyleSheet(textButtonStyle)
        self.bookButton.clicked.connect(self.openBookMenu)
        self.secondToolBar.addWidget(self.bookButton)
        button = QPushButton(">")
        button.setFixedWidth(40)
        self.addStandardTextButton("menu_next_chapter", self.openBookNextChapter, self.secondToolBar, button)

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

        iconFile = os.path.join("htmlResources", "docx.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["wordDocument"], self.openDocxDialog)
        iconFile = os.path.join("htmlResources", "pdfOpen.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["pdfDocument"], self.openPdfDialog)
        iconFile = os.path.join("htmlResources", "save.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["savePdfCurrentPage"], self.invokeSavePdfPage)
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

        if ("Pythonvlc" in config.enabled):
            iconFile = os.path.join("htmlResources", "buttons", "media_player.png")
            self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["mediaPlayer"], self.openVlcPlayer)
            self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "reload.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu1_reload"], lambda: self.reloadCurrentRecord(True))
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

        if ("Htmldocx" in config.enabled):
            iconFile = os.path.join("htmlResources", "docx.png")
            self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["exportToDocx"], self.exportMainPageToDocx)
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

        if ("Htmldocx" in config.enabled):
            iconFile = os.path.join("htmlResources", "docx.png")
            self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["exportToDocx"], self.exportStudyPageToDocx)

        iconFile = os.path.join("htmlResources", "pdf.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar3_pdf"], self.printStudyPage)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "interlinear.png")
        self.rightToolBar.addAction(QIcon(iconFile), "Marvel Interlinear Bible", self.runMIBStudy)

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
                toolbar.setIconSize(QSize(int(config.iconButtonWidth * config.toolbarIconSizeFactor), int(config.iconButtonWidth * config.sidebarIconSizeFactor)))
                toolbar.setFixedHeight(config.iconButtonWidth + 4)
            for toolbar in (self.leftToolBar, self.rightToolBar):
                toolbar.setIconSize(QSize(int(config.iconButtonWidth * config.sidebarIconSizeFactor), int(config.iconButtonWidth * config.sidebarIconSizeFactor)))
