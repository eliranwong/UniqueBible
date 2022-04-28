from qtpy.QtCore import QSize
from gui.MenuItems import *
from db.BiblesSqlite import BiblesSqlite
from util.ShortcutUtil import ShortcutUtil
from util.LanguageUtil import LanguageUtil
from util.FileUtil import FileUtil
from util.WebtopUtil import WebtopUtil
import shortcut as sc
import re, os


class MaterialMainWindow:

    def create_menu(self):

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
            ("activeVerseColour", self.changeActiveVerseColour),
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
#        subMenu = addSubMenu(subMenu0, "toolbarIcon")
#        items = (
#            ("toolbarIconStandard", lambda: self.setFullIconSize(False)),
#            ("toolbarIconFull", lambda: self.setFullIconSize(True)),
#        )
#        for feature, action in items:
#            addMenuItem(subMenu, feature, self, action)
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
        if config.isTtsInstalled:
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
        if config.isHtmldocxInstalled:
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
        menu.addSeparator()
        addMenuItem(menu, "menu1_update", self, self.showUpdateAppWindow)
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
                        addIconMenuItem(icon, menu, webtopApp, self, partial(WebtopUtil.runNohup, command), "", translation=False)

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

        self.defineStyle()
        
        self.firstToolBar = QToolBar()
        self.firstToolBar.setWindowTitle(config.thisTranslation["bar1_title"])
        self.firstToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.firstToolBar)

        # Version selection

        if config.refButtonClickAction == "mini":
            self.versionCombo = None
            self.versionButton = QPushButton(config.mainText)
            self.addStandardTextButton("bibleVersion", self.versionButtonClicked, self.firstToolBar, self.versionButton)
        else:
            self.versionButton = None
            self.versionCombo = QComboBox()
            self.bibleVersions = BiblesSqlite().getBibleList()
            self.versionCombo.addItems(self.bibleVersions)
            initialIndex = 0
            if config.mainText in self.bibleVersions:
                initialIndex = self.bibleVersions.index(config.mainText)
            self.versionCombo.setCurrentIndex(initialIndex)
            self.versionCombo.currentIndexChanged.connect(self.changeBibleVersion)
            self.versionCombo.setStyleSheet(config.comboBoxStyle)
            self.firstToolBar.addWidget(self.versionCombo)

        # The height of the first text button is used to fix icon button width when a qt-material theme is applied.
        if config.qtMaterial and config.qtMaterialTheme:
            versionButtonHeight = self.versionButton.height() if config.refButtonClickAction == "mini" else self.versionCombo.height() 
            config.iconButtonWidth = config.maximumIconButtonWidth if versionButtonHeight > config.maximumIconButtonWidth else versionButtonHeight

        icon = "material/navigation/unfold_more/materialiconsoutlined/18dp/2x/outline_unfold_more_black_18dp.png"
        self.addMaterialIconButton("cp0", icon, self.mainTextMenu, self.firstToolBar)
        icon = "material/action/search/materialiconsoutlined/18dp/2x/outline_search_black_18dp.png"
        self.addMaterialIconButton("cp3", icon, self.displaySearchBibleMenu, self.firstToolBar)

        self.firstToolBar.addSeparator()

        icon = "material/image/navigate_before/materialiconsoutlined/18dp/2x/outline_navigate_before_black_18dp.png"
        self.addMaterialIconButton("menu_previous_chapter", icon, self.previousMainChapter, self.firstToolBar)
        self.mainRefButton = QPushButton(self.verseReference("main")[-1])
        self.addStandardTextButton("bar1_reference", self.mainRefButtonClickedMaterial, self.firstToolBar, self.mainRefButton)
        self.mainRefButton.setVisible(False)
        icon = "material/image/navigate_next/materialiconsoutlined/18dp/2x/outline_navigate_next_black_18dp.png"
        self.addMaterialIconButton("menu_next_chapter", icon, self.nextMainChapter, self.firstToolBar)

        self.firstToolBar.addSeparator()

        icon = "material/maps/rate_review/materialiconsoutlined/18dp/2x/outline_rate_review_black_18dp.png"
        self.addMaterialIconButton("menu_bookNote", icon, self.openMainBookNote, self.firstToolBar)
        icon = "material/file/drive_file_rename_outline/materialiconsoutlined/18dp/2x/outline_drive_file_rename_outline_black_18dp.png"
        self.addMaterialIconButton("menu_chapterNote", icon, self.openMainChapterNote, self.firstToolBar)
        icon = "material/editor/edit_note/materialiconsoutlined/18dp/2x/outline_edit_note_black_18dp.png"
        self.addMaterialIconButton("menu_verseNote", icon, self.openMainVerseNote, self.firstToolBar)

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
        self.addMaterialIconButton(self.getStudyBibleDisplayToolTip(), self.getStudyBibleDisplay(), self.enableStudyBibleButtonClicked, self.firstToolBar, self.enableStudyBibleButton, False)

        # Toolbar height here is affected by the actual size of icon file used in a QAction
        if config.qtMaterial and config.qtMaterialTheme:
            self.firstToolBar.setFixedHeight(config.iconButtonWidth + 4)
            self.firstToolBar.setIconSize(QSize(int(config.iconButtonWidth / 2), int(config.iconButtonWidth / 2)))
        else:
            self.firstToolBar.setIconSize(QSize(17, 17))
        # QAction can use setVisible whereas QPushButton cannot when it is placed on a toolbar.
        self.studyRefButton = self.firstToolBar.addAction(":::".join(self.verseReference("study")), self.showAllChaptersMenuStudy)
        iconFile = os.path.join("htmlResources", self.getSyncStudyWindowBibleDisplay())
        self.enableSyncStudyWindowBibleButton = self.firstToolBar.addAction(self.getMaskedQIcon(iconFile), self.getSyncStudyWindowBibleDisplayToolTip(), self.enableSyncStudyWindowBibleButtonClicked)
        if config.openBibleInMainViewOnly:
            self.studyRefButton.setVisible(False)
            self.enableSyncStudyWindowBibleButton.setVisible(False)
        self.firstToolBar.addSeparator()

        icon = "material/notification/more/materialiconsoutlined/18dp/2x/outline_more_black_18dp.png"
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
            self.commentaryCombo.setStyleSheet(config.comboBoxStyle)
            self.secondToolBar.addWidget(self.commentaryCombo)

        self.enableSyncCommentaryButton = QPushButton()
        self.addMaterialIconButton(self.getSyncCommentaryDisplayToolTip(), self.getSyncCommentaryDisplay(), self.enableSyncCommentaryButtonClicked, self.secondToolBar, self.enableSyncCommentaryButton, False)
        self.secondToolBar.addSeparator()

        icon = "material/image/navigate_before/materialiconsoutlined/18dp/2x/outline_navigate_before_black_18dp.png"
        self.addMaterialIconButton("menu_previous_chapter", icon, self.openBookPreviousChapter, self.secondToolBar)
        self.bookButton = QPushButton(config.book[:20])
        self.addStandardTextButton(config.book, self.openBookMenu, self.secondToolBar, self.bookButton, translation=False)
        icon = "material/image/navigate_next/materialiconsoutlined/18dp/2x/outline_navigate_next_black_18dp.png"
        self.addMaterialIconButton("menu_next_chapter", icon, self.openBookNextChapter, self.secondToolBar)

        icon = "material/action/search/materialiconsoutlined/18dp/2x/outline_search_black_18dp.png"
        self.addMaterialIconButton("bar2_searchBooks", icon, self.displaySearchBookCommand, self.secondToolBar)

        self.secondToolBar.addSeparator()

        icon = "material/action/note_add/materialiconsoutlined/18dp/2x/outline_note_add_black_18dp.png"
        self.addMaterialIconButton("menu7_create", icon, self.createNewNoteFile, self.secondToolBar)
        icon = "material/file/file_open/materialiconsoutlined/18dp/2x/outline_file_open_black_18dp.png"
        self.addMaterialIconButton("menu7_open", icon, self.openTextFileDialog, self.secondToolBar)

        fileName = self.getLastExternalFileName()
        self.externalFileButton = QPushButton(fileName[:20])
        self.addStandardTextButton(fileName, self.externalFileButtonClicked, self.secondToolBar, self.externalFileButton, translation=False)

        icon = "material/image/edit/materialiconsoutlined/18dp/2x/outline_edit_black_18dp.png"
        self.addMaterialIconButton("menu7_edit", icon, self.editExternalFileButtonClicked, self.secondToolBar)

        self.secondToolBar.addSeparator()

        icon = "material/action/description/materialiconsoutlined/18dp/2x/outline_description_black_18dp.png"
        self.addMaterialIconButton("wordDocument", icon, self.openDocxDialog, self.secondToolBar)
        icon = "material/image/picture_as_pdf/materialiconsoutlined/18dp/2x/outline_picture_as_pdf_black_18dp.png"
        self.addMaterialIconButton("pdfDocument", icon, self.openPdfDialog, self.secondToolBar)
        icon = "material/content/save_as/materialiconsoutlined/18dp/2x/outline_save_as_black_18dp.png"
        self.addMaterialIconButton("savePdfCurrentPage", icon, self.invokeSavePdfPage, self.secondToolBar)

        self.secondToolBar.addSeparator()

        icon = "material/editor/text_decrease/materialiconsoutlined/18dp/2x/outline_text_decrease_black_18dp.png"
        self.addMaterialIconButton("menu2_smaller", icon, self.smallerFont, self.secondToolBar)

        self.defaultFontButton = QPushButton("{0} {1}".format(config.font, config.fontSize))
        self.addStandardTextButton("menu1_setDefaultFont", self.setDefaultFont, self.secondToolBar, self.defaultFontButton)

        icon = "material/editor/text_increase/materialiconsoutlined/18dp/2x/outline_text_increase_black_18dp.png"
        self.addMaterialIconButton("menu2_larger", icon, self.largerFont, self.secondToolBar)
        self.secondToolBar.addSeparator()
        if config.isVlcInstalled:
            icon = "material/av/play_circle/materialiconsoutlined/18dp/2x/outline_play_circle_black_18dp.png"
            self.addMaterialIconButton("mediaPlayer", icon, lambda: self.openVlcPlayer(""), self.secondToolBar)
        if config.isYoutubeDownloaderInstalled:
            icon = "material/hardware/browser_updated/materialiconsoutlined/18dp/2x/outline_browser_updated_black_18dp.png"
            self.addMaterialIconButton("menu11_youtube", icon, self.openYouTube, self.secondToolBar)
            self.secondToolBar.addSeparator()
        icon = "material/navigation/refresh/materialiconsoutlined/18dp/2x/outline_refresh_black_18dp.png"
        self.addMaterialIconButton("menu1_reload", icon, lambda: self.reloadCurrentRecord(True), self.secondToolBar)
        icon = "material/action/fit_screen/materialiconsoutlined/18dp/2x/outline_fit_screen_black_18dp.png"
        self.addMaterialIconButton("menu1_fullScreen", icon, self.fullsizeWindow, self.secondToolBar)
        self.secondToolBar.addSeparator()

        # Left tool bar
        self.leftToolBar = QToolBar()
        self.leftToolBar.setWindowTitle(config.thisTranslation["bar3_title"])
        self.leftToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.LeftToolBarArea, self.leftToolBar)

        icon = "material/image/navigate_before/materialiconsoutlined/18dp/2x/outline_navigate_before_black_18dp.png"
        self.addMaterialIconButton("menu3_mainBack", icon, self.back, self.leftToolBar)
        icon = "material/action/history/materialiconsoutlined/18dp/2x/outline_history_black_18dp.png"
        self.addMaterialIconButton("menu3_main", icon, self.mainHistoryButtonClicked, self.leftToolBar)
        icon = "material/image/navigate_next/materialiconsoutlined/18dp/2x/outline_navigate_next_black_18dp.png"
        self.addMaterialIconButton("menu3_mainForward", icon, self.forward, self.leftToolBar)
        self.leftToolBar.addSeparator()
        if config.isHtmldocxInstalled:
            icon = "material/action/description/materialiconsoutlined/18dp/2x/outline_description_black_18dp.png"
            self.addMaterialIconButton("exportToDocx", icon, self.exportMainPageToDocx, self.leftToolBar)
        icon = "material/image/picture_as_pdf/materialiconsoutlined/18dp/2x/outline_picture_as_pdf_black_18dp.png"
        self.addMaterialIconButton("bar3_pdf", icon, self.printMainPage, self.leftToolBar)
        self.leftToolBar.addSeparator()
        self.enableParagraphButton = QPushButton()
        self.addMaterialIconButton("menu2_format", self.getReadFormattedBibles(), self.enableParagraphButtonClicked, self.leftToolBar, self.enableParagraphButton)
        self.enableSubheadingButton = QPushButton()
        self.addMaterialIconButton("menu2_subHeadings", self.getAddSubheading(), self.enableSubheadingButtonClicked, self.leftToolBar, self.enableSubheadingButton)
        self.leftToolBar.addSeparator()
        icon = "material/editor/format_align_justify/materialiconsoutlined/18dp/2x/outline_format_align_justify_black_18dp.png"
        self.addMaterialIconButton("menu4_compareAll", icon, self.runCOMPARE, self.leftToolBar)
        icon = "material/image/compare/materialicons/18dp/2x/baseline_compare_black_18dp.png"
        self.addMaterialIconButton("menu4_moreComparison", icon, lambda: self.openControlPanelTab(0), self.leftToolBar)
        self.enforceCompareParallelButton = QPushButton()
        self.addMaterialIconButton(self.getEnableCompareParallelDisplayToolTip(), self.getEnableCompareParallelDisplay(), self.enforceCompareParallelButtonClicked, self.leftToolBar, self.enforceCompareParallelButton, False)
        self.leftToolBar.addSeparator()
        icon = "material/image/wb_sunny/materialiconsoutlined/18dp/2x/outline_wb_sunny_black_18dp.png"
        self.addMaterialIconButton("Marvel Original Bible", icon, self.runMOB, self.leftToolBar, None, False)
        icon = "material/image/auto_awesome_motion/materialiconsoutlined/18dp/2x/outline_auto_awesome_motion_black_18dp.png"
        self.addMaterialIconButton("Marvel Interlinear Bible", icon, self.runMIB, self.leftToolBar, None, False)
        icon = "material/file/workspaces/materialiconsoutlined/18dp/2x/outline_workspaces_black_18dp.png"
        self.addMaterialIconButton("Marvel Trilingual Bible", icon, self.runMTB, self.leftToolBar, None, False)
        icon = "material/action/horizontal_split/materialiconsoutlined/18dp/2x/outline_horizontal_split_black_18dp.png"
        self.addMaterialIconButton("Marvel Parallel Bible", icon, self.runMPB, self.leftToolBar, None, False)
        icon = "material/editor/schema/materialiconsoutlined/18dp/2x/outline_schema_black_18dp.png"
        self.addMaterialIconButton("Marvel Annotated Bible", icon, self.runMAB, self.leftToolBar, None, False)
        self.leftToolBar.addSeparator()

        # Right tool bar
        self.rightToolBar = QToolBar()
        self.rightToolBar.setWindowTitle(config.thisTranslation["bar4_title"])
        self.rightToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.RightToolBarArea, self.rightToolBar)

        #icon = "material/navigation/arrow_back_ios/materialiconsoutlined/18dp/2x/outline_arrow_back_ios_black_18dp.png"
        icon = "material/image/navigate_before/materialiconsoutlined/18dp/2x/outline_navigate_before_black_18dp.png"
        self.addMaterialIconButton("menu3_studyBack", icon, self.studyBack, self.rightToolBar)
        icon = "material/action/history/materialiconsoutlined/18dp/2x/outline_history_black_18dp.png"
        self.addMaterialIconButton("menu3_study", icon, self.studyHistoryButtonClicked, self.rightToolBar)
        #icon = "material/navigation/arrow_forward_ios/materialiconsoutlined/18dp/2x/outline_arrow_forward_ios_black_18dp.png"
        icon = "material/image/navigate_next/materialiconsoutlined/18dp/2x/outline_navigate_next_black_18dp.png"
        self.addMaterialIconButton("menu3_studyForward", icon, self.studyForward, self.rightToolBar)
        self.rightToolBar.addSeparator()
        if config.isHtmldocxInstalled:
            icon = "material/action/description/materialiconsoutlined/18dp/2x/outline_description_black_18dp.png"
            self.addMaterialIconButton("exportToDocx", icon, self.exportStudyPageToDocx, self.rightToolBar)
        icon = "material/image/picture_as_pdf/materialiconsoutlined/18dp/2x/outline_picture_as_pdf_black_18dp.png"
        self.addMaterialIconButton("bar3_pdf", icon, self.printStudyPage, self.rightToolBar)
        self.rightToolBar.addSeparator()
        icon = "material/image/auto_awesome_motion/materialiconsoutlined/18dp/2x/outline_auto_awesome_motion_black_18dp.png"
        self.addMaterialIconButton("Marvel Interlinear Bible", icon, self.runMIBStudy, self.rightToolBar, None, False)
        self.rightToolBar.addSeparator()
        icon = "material/editor/highlight/materialiconsoutlined/18dp/2x/outline_highlight_black_18dp.png"
        self.addMaterialIconButton("menu4_indexes", icon, self.runINDEX, self.rightToolBar)
        icon = "material/maps/local_library/materialiconsoutlined/18dp/2x/outline_local_library_black_18dp.png"
        self.addMaterialIconButton("menu4_commentary", icon, self.runCOMMENTARY, self.rightToolBar)
        self.rightToolBar.addSeparator()
        icon = "material/editor/insert_link/materialiconsoutlined/18dp/2x/outline_insert_link_black_18dp.png"
        self.addMaterialIconButton("menu4_crossRef", icon, self.runCROSSREFERENCE, self.rightToolBar)
        icon = "material/maps/diamond/materialiconsoutlined/18dp/2x/outline_diamond_black_18dp.png"
        self.addMaterialIconButton("menu4_tske", icon, self.runTSKE, self.rightToolBar)
        self.rightToolBar.addSeparator()
        icon = "material/action/translate/materialiconsoutlined/18dp/2x/outline_translate_black_18dp.png"
        self.addMaterialIconButton("menu4_traslations", icon, self.runTRANSLATION, self.rightToolBar)
        icon = "material/editor/align_horizontal_right/materialicons/18dp/2x/baseline_align_horizontal_right_black_18dp.png"
        self.addMaterialIconButton("menu4_discourse", icon, self.runDISCOURSE, self.rightToolBar)
        icon = "material/action/drag_indicator/materialiconsoutlined/18dp/2x/outline_drag_indicator_black_18dp.png"
        self.addMaterialIconButton("menu4_words", icon, self.runWORDS, self.rightToolBar)
        icon = "material/device/widgets/materialiconsoutlined/18dp/2x/outline_widgets_black_18dp.png"
        self.addMaterialIconButton("menu4_tdw", icon, self.runCOMBO, self.rightToolBar)
        self.rightToolBar.addSeparator()
        self.enableInstantButton = QPushButton()
        self.addMaterialIconButton("menu2_hover", self.getInstantInformation(), self.enableInstantButtonClicked, self.rightToolBar, self.enableInstantButton)
        icon = "material/content/bolt/materialiconsoutlined/18dp/2x/outline_bolt_black_18dp.png"
        self.addMaterialIconButton("menu2_bottom", icon, self.cycleInstant, self.rightToolBar)
        self.rightToolBar.addSeparator()