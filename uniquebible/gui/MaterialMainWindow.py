from uniquebible import config
import platform
from uniquebible.gui.MenuItems import *
from uniquebible.install.module import *
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.ShortcutUtil import ShortcutUtil
from uniquebible.util.LanguageUtil import LanguageUtil
from uniquebible.util.Languages import Languages
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.WebtopUtil import WebtopUtil
import uniquebible.shortcut as sc
import re, os, webbrowser


# Search for material icons at: https://fonts.google.com/icons?selected=Material+Icons

class MaterialMainWindow:

    def create_menu(self):

        config.topToolBarOnly = False
        
        menuBar = self.menuBar()
        # 1st column
        menu = addMenu(menuBar, "menu1_app")
        # Workspace
        addMenuItem(menu, "workspace", self, self.swapWorkspaceWithMainWindow, sc.swapWorkspaceWithMainWindow)
        menu.addSeparator()
        # Note Editor
        if hasattr(config, "toggleDockWidget"):
            config.toggleDockWidget.setShortcut(sc.createNewNoteFile)
            menu.addAction(config.toggleDockWidget)
        else:
            addMenuItem(menu, "note_editor", self, self.createNewNoteFile, sc.createNewNoteFile)
        subMenu = addSubMenu(menu, "noteFile")
        items = (
            ("openNote", self.openNoteEditorFileViaMenu, sc.openNoteEditorFileViaMenu),
            ("note_save", self.saveNoteEditorFileViaMenu, sc.saveNoteEditorFileViaMenu),
            ("note_saveAs", self.saveAsNoteEditorFileViaMenu, sc.saveAsNoteEditorFileViaMenu),
        )
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)
        menu.addSeparator()
        items = (
            ("menu7_open", self.openTextFileDialog),
        )
        for feature, action in items:
            addMenuItem(menu, feature, self, action)

        subMenu = addSubMenu(menu, "saveFile")
        subMenu1 = addSubMenu(subMenu, "bibleWindowContent")
        items = [
            ("plainTextFile", self.savePlainText),
            ("htmlFile", self.saveHtml),
            ("pdfFile", self.savePdf),
        ]
        if ("Markdown" in config.enabled):
            items.append(("markdownFile", self.saveMarkdown))
        if ("Htmldocx" in config.enabled):
            items.append(("wordFile", self.saveDocx))
        for feature, action in items:
            addMenuItem(subMenu1, feature, self, action)
        subMenu2 = addSubMenu(subMenu, "studyWindowContent")
        items = [
            ("plainTextFile", lambda: self.savePlainText("study")),
            ("htmlFile", lambda: self.saveHtml("study")),
            ("pdfFile", lambda: self.savePdf("study")),
        ]
        if ("Markdown" in config.enabled):
            items.append(("markdownFile", lambda: self.saveMarkdown("study")))
        if ("Htmldocx" in config.enabled):
            items.append(("wordFile", lambda: self.saveDocx("study")))
        for feature, action in items:
            addMenuItem(subMenu2, feature, self, action)

        menu.addSeparator()

        # Clipboard Content
        subMenuClipboardMonitoring = addSubMenu(menu, "clipboardMonitoring")
        def setClipboardMonitoringSubmenu():
            subMenuClipboardMonitoring.clear()
            for option in ("enable", "disable"):
                optionValue = True if option == "enable" else False
                addCheckableMenuItem(subMenuClipboardMonitoring, option, self, partial(self.setClipboardMonitoring, optionValue), config.enableClipboardMonitoring, optionValue)
        self.setClipboardMonitoringSubmenu = setClipboardMonitoringSubmenu
        setClipboardMonitoringSubmenu()
        subMenu.addSeparator()
        clipboardMonitoringWiki = "https://github.com/eliranwong/UniqueBible/wiki/Monitor-Clipboard-Text-Bible-References"
        addMenuItem(subMenu, "menu_about", self, lambda: webbrowser.open(clipboardMonitoringWiki))
        subMenu = addSubMenu(menu, "menu1_clipboard")
        items = [
            ("menu_display", self.pasteFromClipboard, None),
            ("openBibleReferences", self.openReferencesOnClipboard, None),
            ("context1_command", self.parseContentOnClipboard, sc.parseContentOnClipboard),
        ]
        if not config.noTtsFound:
            items.insert(1, ("speak", self.readClipboardContent, None))
        for feature, action, shortcut in items:
            addMenuItem(subMenu, feature, self, action, shortcut)

        menu.addSeparator()

        # Appearance
        subMenu0 = addSubMenu(menu, "appearance")
        # Window layout

        subMenuApplicationIcon = addSubMenu(subMenu0, "applicationIcon")
        def setApplicationIconSubmenu():
            subMenuApplicationIcon.clear()
            for icon in FileUtil.fileNamesWithoutExtension(os.path.join("htmlResources", "icons"), "png"):
                iconFile = os.path.join("htmlResources", "icons", f"{icon}.png")
                currentIconFile = os.path.basename(config.desktopUBAIcon)[:-4]
                addCheckableMenuItem(subMenuApplicationIcon, icon, self, partial(self.setApplicationIcon, iconFile), currentIconFile, icon, translation=False, icon=iconFile)
        self.setApplicationIconSubmenu = setApplicationIconSubmenu
        setApplicationIconSubmenu()

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
            ("menu11_audio", self.toggleAudioPlayer, sc.hideShowAudioToolBar),
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
        subMenuWindowStyle = addSubMenu(subMenu0, "menu1_selectWindowStyle")
        def setAppWindowStyleSubmenu():
            subMenuWindowStyle.clear()
            for style in QStyleFactory.keys():
                addCheckableMenuItem(subMenuWindowStyle, style, self, partial(self.setAppWindowStyle, style), config.windowStyle, style, None, False)
        self.setAppWindowStyleSubmenu = setAppWindowStyleSubmenu
        setAppWindowStyleSubmenu()
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
        
        # Change Qt Library
        def isPySide6Installed():
            try:
                from PySide6.QtWidgets import QApplication, QStyleFactory
                return True
            except:
                return False
        def isPySide2Installed():
            try:
                from PySide2.QtWidgets import QApplication, QStyleFactory
                return True
            except:
                return False
        def isPyQt5Installed():
            try:
                from PyQt5.QtWidgets import QApplication, QStyleFactory
                return True
            except:
                return False
        def isQtpyInstalled():
            try:
                from qtpy import QtGui
                return True
            except:
                return False
        def changeQtLibrary(option):
            if not config.qtLibrary == option.lower():
                if self.warningRestart():
                    notAvailable = "Not available!"
                    # upgrade to the latest version if available
                    installmodule(f"--upgrade {option}")
                    if option in ("PySide2", "PyQt5"):
                        if option == "PyQt5":
                            installmodule("PyQtWebEngine")
                        installmodule("--upgrade qtpy")
                        if not isQtpyInstalled():
                            self.displayMessage(notAvailable)
                            return None
                    isInstalled = {
                        "PySide6": isPySide6Installed,
                        "PySide2": isPySide2Installed,
                        "PyQt5": isPyQt5Installed,
                    }
                    if isInstalled[option]():
                        config.qtLibrary = option.lower()
                        self.restartApp()
                    else:
                        self.displayMessage(notAvailable)
                        if option == "PySide6":
                            self.displayMessage("You may upgrade to the latest python version and try again.")
                else:
                    resetSubMenuChangeQtLibrary()

        subMenuChangeQtLibrary = addSubMenu(subMenu0, "qtLibrary")
        def resetSubMenuChangeQtLibrary():
            subMenuChangeQtLibrary.clear()
            options = (
                ("PySide6", "PySide 6 [recommended]"),
                ("PySide2", "PySide 2"),
                ("PyQt5", "PyQt 5"),
            )
            for option, description in options:
                addCheckableMenuItem(subMenuChangeQtLibrary, description, self, partial(changeQtLibrary, option), config.qtLibrary, option, translation=False)
        resetSubMenuChangeQtLibrary()

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
            ("menu1_tabNo", self.setTabNumberDialog),
        )
        for feature, action in items:
            addMenuItem(subMenu0, feature, self, action)
        # Verse number Action
        subMenu = addSubMenu(subMenu0, "selectVerseNumberAction")
        values = ("_noAction", "_cp0", "_cp1", "_cp2", "_cp3", "_cp4", "_cp5", "_cp6", "STUDY", "COMPARE", "CROSSREFERENCE", "TSKE", "TRANSLATION", "DISCOURSE", "WORDS", "COMBO", "INDEX", "COMMENTARY", "STUDY", "_menu")
        descriptions = ["noAction", "cp0", "cp1", "cp2", "cp3", "cp4", "cp5", "cp6", "openInStudyWindow", "menu4_compareAll", "menu4_crossRef", "menu4_tske", "menu4_traslations", "menu4_discourse", "menu4_words", "menu4_tdw", "menu4_indexes", "menu4_commentary", "menu_syncStudyWindowBible", "classicMenu"]
        clickActionOptions = dict(zip(values, descriptions))
        subMenuSingleClick = addSubMenu(subMenu, "singleClick")
        def singleClickActionSelectedSubmenu():
            subMenuSingleClick.clear()
            for option, description in clickActionOptions.items():
                addCheckableMenuItem(subMenuSingleClick, description, self, partial(self.singleClickActionSelected, option), config.verseNoSingleClickAction, option)
        self.singleClickActionSelectedSubmenu = singleClickActionSelectedSubmenu
        singleClickActionSelectedSubmenu()
        subMenuDoubleClick = addSubMenu(subMenu, "doubleClick")
        def doubleClickActionSelectedSubmenu():
            subMenuDoubleClick.clear()
            for option, description in clickActionOptions.items():
                addCheckableMenuItem(subMenuDoubleClick, description, self, partial(self.doubleClickActionSelected, option), config.verseNoDoubleClickAction, option)
        self.doubleClickActionSelectedSubmenu = doubleClickActionSelectedSubmenu
        doubleClickActionSelectedSubmenu()
        # Abbreviation language
        subMenuSetAbbreviations = addSubMenu(subMenu0, "menu1_setAbbreviations")
        def setBibleAbbreviationsSelectedSubmenu():
            subMenuSetAbbreviations.clear()
            options = BibleBooks().booksMap.keys()
            for option in options:
                addCheckableMenuItem(subMenuSetAbbreviations, option, self, partial(self.setBibleAbbreviationsSelected, option), config.standardAbbreviation, option, translation=False)
        self.setBibleAbbreviationsSelectedSubmenu = setBibleAbbreviationsSelectedSubmenu
        setBibleAbbreviationsSelectedSubmenu()
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
        subMenuStrongsHebrewLexicon = addSubMenu(subMenu0, "menu1_setDefaultStrongsHebrewLexicon")
        def defaultStrongsHebrewLexiconSelectedSubmenu():
            subMenuStrongsHebrewLexicon.clear()
            for option in self.lexiconList:
                addCheckableMenuItem(subMenuStrongsHebrewLexicon, option, self, partial(self.defaultStrongsHebrewLexiconSelected, option), config.defaultLexiconStrongH, option, translation=False)
        self.defaultStrongsHebrewLexiconSelectedSubmenu = defaultStrongsHebrewLexiconSelectedSubmenu
        defaultStrongsHebrewLexiconSelectedSubmenu()
        subMenuStrongsGreekLexicon = addSubMenu(subMenu0, "menu1_setDefaultStrongsGreekLexicon")
        def defaultStrongsGreekLexiconSelectedSubmenu():
            subMenuStrongsGreekLexicon.clear()
            for option in self.lexiconList:
                addCheckableMenuItem(subMenuStrongsGreekLexicon, option, self, partial(self.defaultStrongsGreekLexiconSelected, option), config.defaultLexiconStrongG, option, translation=False)
        self.defaultStrongsGreekLexiconSelectedSubmenu = defaultStrongsGreekLexiconSelectedSubmenu
        defaultStrongsGreekLexiconSelectedSubmenu()
        # Workspace saving order
        subMenuWorkspaceSavingOrder = addSubMenu(subMenu0, "selectWorkspaceSavingOrder")
        def setWorkspaceSavingOrderSubmenu():
            subMenuWorkspaceSavingOrder.clear()
            savingOrderOptions = ("Creation Order", "Stacking Order", "Activation History Order")
            savingOrder = {
                0: "Creation Order",
                1: "Stacking Order",
                2: "Activation History Order",
            }
            for option in savingOrderOptions:
                addCheckableMenuItem(subMenuWorkspaceSavingOrder, option, self, partial(self.setWorkspaceSavingOrder, option), savingOrder[config.workspaceSavingOrder], option, translation=False)
        self.setWorkspaceSavingOrderSubmenu = setWorkspaceSavingOrderSubmenu
        setWorkspaceSavingOrderSubmenu()
        # Markdown export heading style
        subMenuMarkdownExportHeadingStyle = addSubMenu(subMenu0, "markdownExportHeadingStyle")
        def setMarkdownExportHeadingStyleSubmenu():
            subMenuMarkdownExportHeadingStyle.clear()
            options = ("ATX", "ATX_CLOSED", "SETEXT", "UNDERLINED")
            for option in options:
                addCheckableMenuItem(subMenuMarkdownExportHeadingStyle, option, self, partial(self.setMarkdownExportHeadingStyle, option), config.markdownifyHeadingStyle, option, translation=False)
        self.setMarkdownExportHeadingStyleSubmenu = setMarkdownExportHeadingStyleSubmenu
        setMarkdownExportHeadingStyleSubmenu()
        # Default TTS voice
        if not config.noTtsFound:
            # Default tts voice
            languages = self.getTtsLanguages()
            languageCodes = list(languages.keys())
            items = [languages[code][1] for code in languageCodes]
            
            subMenu = addSubMenu(subMenu0, "ttsLanguage")
            for index, item in enumerate(items):
                languageCode = languageCodes[index]
                addCheckableMenuItem(subMenu, item, self, partial(self.setDefaultTtsLanguage, languageCode), config.ttsDefaultLangauge, languageCode, translation=False)
            # Second tts voice
            subMenu = addSubMenu(subMenu0, "ttsLanguage2")
            for index, item in enumerate(items):
                languageCode = languageCodes[index]
                addCheckableMenuItem(subMenu, item, self, partial(self.setDefaultTtsLanguage2, languageCode), config.ttsDefaultLangauge2, languageCode, translation=False)
            # Third tts voice
            subMenu = addSubMenu(subMenu0, "ttsLanguage3")
            for index, item in enumerate(items):
                languageCode = languageCodes[index]
                addCheckableMenuItem(subMenu, item, self, partial(self.setDefaultTtsLanguage3, languageCode), config.ttsDefaultLangauge3, languageCode, translation=False)

        if config.developer:
            items = (
                ("setMaximumHistoryRecord", self.setMaximumHistoryRecordDialog),
                ("selectNoOfLinesPerChunkForParsing", self.setNoOfLinesPerChunkForParsingDialog),
                ("selectMaximumOHGBiVerses", self.setMaximumOHGBiVersesDisplayDialog),
                ("resourceDirectory", self.customMarvelData),
            )
            for feature, action in items:
                addMenuItem(subMenu0, feature, self, action)
        addMenuItem(subMenu0, "setGoogleApiKey", self, self.setMyGoogleApiKey)
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
        if ("OfflineTts" in config.enabled):
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
        #addMenuItem(menu, "menu1_update", self, self.showUpdateAppWindow)
        menu.addSeparator()
        if hasattr(config, "cli"):
            addMenuItem(menu, "restart", self, self.restartApp)
        addIconMenuItem(config.desktopUBAIcon[14:], menu, "menu_quit", self, self.quitApp, sc.quitApp)

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
            ("displayChapterMenuTogetherWithBibleChapter", self.toggleChapterMenuTogetherWithBibleChapter, sc.displayChapterMenuTogetherWithBibleChapter, config.displayChapterMenuTogetherWithBibleChapter),
            ("menu2_subHeadings", self.enableSubheadingButtonClicked2, sc.enableSubheadingButtonClicked, config.addTitleToPlainChapter),
            ("toggleFavouriteVersionIntoMultiRef", self.toggleFavouriteVersionIntoMultiRef, sc.toggleFavouriteVersionIntoMultiRef, config.addFavouriteToMultiRef),
            ("displayVerseReference", self.toggleShowVerseReference, sc.toggleShowVerseReference, config.showVerseReference),
            ("displayChapterVerseAudioIcons", self.toggleDisplayVerseAudioBibleIcon, None, config.displayVerseAudioBibleIcon),
            ("displayVerseAICommentaryIcon", self.toggleDisplayVerseAICommentaryIcon, None, config.displayVerseAICommentaryIcon),
            ("displayUserNoteIndicator", self.toggleShowUserNoteIndicator, sc.toggleShowUserNoteIndicator, config.showUserNoteIndicator),
            ("displayBibleNoteIndicator", self.toggleShowBibleNoteIndicator, sc.toggleShowBibleNoteIndicator, config.showBibleNoteIndicator),
            ("displayLexicalEntry", self.toggleHideLexicalEntryInBible, sc.toggleHideLexicalEntryInBible, (not config.hideLexicalEntryInBible)),
            ("displayHebrewGreekWordAudio", self.toggleShowHebrewGreekWordAudioLinks, sc.toggleShowWordAudio, config.showHebrewGreekWordAudioLinks),
            ("readTillChapterEnd", self.toggleReadTillChapterEnd, sc.toggleReadTillChapterEnd, config.readTillChapterEnd),
            ("instantHighlight", self.enableInstantHighlightButtonClicked, sc.toggleInstantHighlight, config.enableInstantHighlight),
            ("menu2_hover", self.enableInstantButtonClicked, sc.enableInstantButtonClicked, config.instantInformationEnabled),
            ("parallelMode", self.enforceCompareParallelButtonClicked, sc.enforceCompareParallel, config.enforceCompareParallel),
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

        # Cli interface
        if hasattr(config, "cli"):
            addMenuItem(menu, "cli", self, lambda: self.mainView.currentWidget().switchToCli(), sc.commandLineInterface)
            menu.addSeparator()

        # Media Player
        if self.audioPlayer is not None:
            subMenu = addSubMenu(menu, "mediaPlayer")
            items = (
                ("menu11_audio", self.toggleAudioPlayer, sc.launchMediaPlayer),
                ("menu11_video", self.openVideoView, None),
                ("stop", self.closeMediaPlayer, sc.stopMediaPlayer),
            )
            for feature, action, shortcut in items:
                addMenuItem(subMenu, feature, self, action, shortcut)
            menu.addSeparator()
            subMenuMediaSpeed = addSubMenu(subMenu, "adjustSpeed")
            def setSubMenuMediaSpeed():
                subMenuMediaSpeed.clear()
                options = ("0.5", "0.75", "1.0", "1.25", "1.5", "1.75", "2.0")
                for option in options:
                    addCheckableMenuItem(subMenuMediaSpeed, option, self, partial(self.setMediaSpeed, option), str(config.mediaSpeed), option, translation=False)
            self.setSubMenuMediaSpeed = setSubMenuMediaSpeed
            self.setSubMenuMediaSpeed()
        elif config.isVlcAvailable:
            subMenu = addSubMenu(menu, "mediaPlayer")
            items = (
                ("launch", self.openVlcPlayer, sc.launchMediaPlayer),
                ("stop", self.closeMediaPlayer, sc.stopMediaPlayer),
            )
            for feature, action, shortcut in items:
                addMenuItem(subMenu, feature, self, action, shortcut)
            menu.addSeparator()
            subMenuVlcSpeed = addSubMenu(subMenu, "adjustSpeed")
            def setSubMenuVlcSpeed():
                subMenuVlcSpeed.clear()
                options = ("0.5", "0.75", "1.0", "1.25", "1.5", "1.75", "2.0")
                for option in options:
                    addCheckableMenuItem(subMenuVlcSpeed, option, self, partial(self.setVlcSpeed, option), str(config.vlcSpeed), option, translation=False)
            self.setSubMenuVlcSpeed = setSubMenuVlcSpeed
            self.setSubMenuVlcSpeed()
            
        
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
            for plugin in FileUtil.fileNamesWithoutExtension(os.path.join(config.packageDir, "plugins", "menu"), "py"):
                if not plugin in config.excludeMenuPlugins:
                    if "_" in plugin:
                        feature, shortcut = plugin.split("_", 1)
                        feature = "{0} | {1}".format(feature, shortcut)
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
            for plugin in FileUtil.fileNamesWithoutExtension(os.path.join(config.ubaUserDir, "plugins", "menu"), "py"):
                if not plugin in config.excludeMenuPlugins:
                    if "_" in plugin:
                        feature, shortcut = plugin.split("_", 1)
                        feature = "{0} | {1}".format(feature, shortcut)
                        addMenuItem(menu, feature, self, partial(self.runPlugin, plugin), shortcut=shortcut, translation=False)
                    else:
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

        # Master Control
        #icon = "material/navigation/unfold_more/materialiconsoutlined/48dp/2x/outline_unfold_more_black_48dp.png"
        icon = "material/image/tune/materialiconsoutlined/48dp/2x/outline_tune_black_48dp.png"
        self.addMaterialIconButton("cp0", icon, self.mainTextMenu, self.firstToolBar)

        icon = "material/content/stacked_bar_chart/materialiconsround/18dp/2x/round_stacked_bar_chart_black_18dp.png"
        self.addMaterialIconButton("bibleCollections", icon, self.showBibleCollectionDialog, self.firstToolBar, toolButton=True)

        # Version selection

        if config.refButtonClickAction == "mini":
            self.versionCombo = None
            self.bibleSelection = None
            #self.versionButton = QPushButton(config.mainText)
            #self.addStandardTextButton("bibleVersion", self.versionButtonClicked, self.firstToolBar, self.versionButton)
            self.versionButton = self.firstToolBar.addAction(config.mainText, self.versionButtonClicked)
        else:
            self.versionButton = None
            self.versionCombo = None
            self.bibleSelection = QToolButton()
            #self.bibleSelection.setMinimumWidth(int(config.iconButtonSize * 3))
            self.bibleSelection.setMaximumWidth(int(config.iconButtonSize * 7))
            self.setBibleSelection()
            self.firstToolBar.addWidget(self.bibleSelection)

        self.bibleSelectionForComparison = QToolButton()
        self.bibleSelectionForComparison.setMinimumWidth(int(config.iconButtonSize * 4))
        self.bibleSelectionForComparison.setMaximumWidth(int(config.iconButtonSize * 7))
        self.setBibleSelectionForComparison()
        self.firstToolBar.addWidget(self.bibleSelectionForComparison)

        icon = "material/image/navigate_before/materialiconsoutlined/48dp/2x/outline_navigate_before_black_48dp.png"
        self.addMaterialIconButton("menu_previous_chapter", icon, self.previousMainChapter, self.firstToolBar, toolButton=True)

        self.mainB = QToolButton()
        self.mainC = QToolButton()
        self.mainV = QToolButton()
        self.setMainRefMenu()
        self.firstToolBar.addWidget(self.mainB)
        self.firstToolBar.addWidget(self.mainC)
        self.firstToolBar.addWidget(QLabel(":"))
        self.firstToolBar.addWidget(self.mainV)

        icon = "material/image/navigate_next/materialiconsoutlined/48dp/2x/outline_navigate_next_black_48dp.png"
        self.addMaterialIconButton("menu_next_chapter", icon, self.nextMainChapter, self.firstToolBar, toolButton=True)

        self.syncButton = QToolButton()
        self.setSyncButton()
        self.firstToolBar.addWidget(self.syncButton)

        self.firstToolBar.addSeparator()

        if not config.compareOnStudyWindow:
            icon = "material/action/ads_click/materialiconsoutlined/48dp/2x/outline_ads_click_black_48dp.png"
            self.addMaterialIconButton("singleVersion", icon, self.openMainChapterMaterial, self.firstToolBar)
        icon = "material/image/auto_awesome_motion/materialiconsoutlined/48dp/2x/outline_auto_awesome_motion_black_48dp.png"
        self.addMaterialIconButton("parallelVersions", icon, lambda: self.runCompareAction("PARALLEL"), self.firstToolBar)
        icon = "material/action/view_column/materialiconsoutlined/48dp/2x/outline_view_column_black_48dp.png"
        self.addMaterialIconButton("sideBySideComparison", icon, lambda: self.runCompareAction("SIDEBYSIDE"), self.firstToolBar)
        icon = "material/editor/table_rows/materialiconsoutlined/48dp/2x/outline_table_rows_black_48dp.png"
        self.addMaterialIconButton("rowByRowComparison", icon, lambda: self.runCompareAction("COMPARE"), self.firstToolBar)

        self.firstToolBar.addSeparator()

        icon = "material/file/file_open/materialiconsoutlined/48dp/2x/outline_file_open_black_48dp.png"
        self.addMaterialIconButton("menu7_open", icon, lambda: self.openControlPanelTab(2), self.firstToolBar)
        icon = "material/editor/edit_note/materialiconsoutlined/48dp/2x/outline_edit_note_black_48dp.png"
        self.addMaterialIconButton("note_editor", icon, self.toggleNoteEditor, self.firstToolBar)
        icon = "material/action/switch_access_shortcut_add/materialiconssharp/48dp/2x/sharp_switch_access_shortcut_add_black_48dp.png"
        self.addMaterialIconButton("insertBibleReferencesIntoNoteEditor", icon, lambda: self.mainView.currentWidget().runPlugin("Insert References into Note Editor", activeSelection=True), self.firstToolBar)
        icon = "material/av/playlist_add/materialiconsoutlined/48dp/2x/outline_playlist_add_black_48dp.png"
        self.addMaterialIconButton("insertTextIntoNoteEditor", icon, lambda: self.mainView.currentWidget().runPlugin("Insert Text into Note Editor_Ctrl+Shift+J", activeSelection=True), self.firstToolBar)

        self.firstToolBar.addSeparator()

        icon = "material/action/zoom_in/materialiconsoutlined/48dp/2x/outline_zoom_in_black_48dp.png"
        self.addMaterialIconButton("masterSearch", icon, self.displaySearchBibleMenu, self.firstToolBar)
        icon = "material/action/filter_alt/materialiconsoutlined/48dp/2x/outline_filter_alt_black_48dp.png"
        self.addMaterialIconButton("liveFilter", icon, self.showLiveFilterDialog, self.firstToolBar)

        self.firstToolBar.addSeparator()

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.setCompleter(self.getTextCommandSuggestion())
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

        #icon = "material/action/terminal/materialiconsoutlined/48dp/2x/outline_terminal_black_48dp.png"
        #self.addMenuPluginButton("Terminal", "terminal", icon, self.firstToolBar)
        icon = "material/action/terminal/materialiconsoutlined/48dp/2x/outline_terminal_black_48dp.png"
        self.addMenuPluginButton("Terminal Mode", "terminalMode", icon, self.firstToolBar)

        self.firstToolBar.addSeparator()

        self.enableStudyBibleButton = QPushButton()
        self.addMaterialIconButton(self.getStudyBibleDisplayToolTip(), self.getStudyBibleDisplay(), self.enableStudyBibleButtonClicked, self.firstToolBar, self.enableStudyBibleButton, False)

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

        icon = "htmlResources/material/communication/swap_calls/materialiconsoutlined/48dp/2x/outline_swap_calls_black_48dp.png"
        iconFile = os.path.join(*icon.split("/"))
        self.swapBibleButton = self.firstToolBar.addAction(self.getMaskedQIcon(iconFile, config.maskMaterialIconColor, config.maskMaterialIconBackground, True), config.thisTranslation["swap"], self.swapBibles)
        if config.openBibleInMainViewOnly:
            #self.studyRefButton.setVisible(False)
            self.studyBibleSelection.setDisabled(True)
            self.studyB.setDisabled(True)
            self.studyC.setDisabled(True)
            self.studyRefLabel.setDisabled(False)
            self.studyV.setDisabled(False)
            self.swapBibleButton.setVisible(False)
        self.firstToolBar.addSeparator()

        icon = "material/notification/more/materialiconsoutlined/48dp/2x/outline_more_black_48dp.png"
        self.addMaterialIconButton("bar1_toolbars", icon, self.hideShowAdditionalToolBar, self.firstToolBar)

        if config.addBreakAfterTheFirstToolBar:
            self.addToolBarBreak()

        # Second tool bar
        self.secondToolBar = QToolBar()
        self.secondToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.secondToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.secondToolBar)

        icon = "material/maps/local_library/materialiconsoutlined/48dp/2x/outline_local_library_black_48dp.png"
        self.addMaterialIconButton("libraryCatalog", icon, self.showLibraryCatalogDialog, self.secondToolBar)

        if os.path.isfile(os.path.join(config.packageDir, "plugins", "menu", "Bible Commentaries.py")):
            self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
            self.commentaryRefButton = QPushButton(config.commentaryText)
            self.addStandardTextButton("menu4_commentary", partial(self.runPlugin, "Bible Commentaries"), self.secondToolBar, self.commentaryRefButton)
        if os.path.isfile(os.path.join(config.packageDir, "plugins", "menu", "Reference Books.py")):
            icon = "material/image/auto_stories/materialiconsoutlined/48dp/2x/outline_auto_stories_black_48dp.png"
            self.addMaterialIconButton("installBooks", icon, partial(self.runPlugin, "Reference Books"), self.secondToolBar)
        if os.path.isfile(os.path.join(config.packageDir, "plugins", "menu", "ePub Viewer New Window.py")):
            icon = "material/action/book/materialiconsoutlined/48dp/2x/outline_book_black_48dp.png"
            self.addMaterialIconButton("epubReader", icon, partial(self.runPlugin, "ePub Viewer New Window"), self.secondToolBar)
        icon = "material/action/description/materialiconsoutlined/48dp/2x/outline_description_black_48dp.png"
        self.addMaterialIconButton("wordDocument", icon, self.openDocxDialog, self.secondToolBar)
        icon = "material/image/picture_as_pdf/materialiconsoutlined/48dp/2x/outline_picture_as_pdf_black_48dp.png"
        self.addMaterialIconButton("pdfDocument", icon, self.openPdfDialog, self.secondToolBar)
        icon = "material/action/file_present/materialiconsoutlined/48dp/2x/outline_file_present_black_48dp.png"
        self.addMaterialIconButton("savePdfCurrentPage", icon, self.invokeSavePdfPage, self.secondToolBar)

        self.secondToolBar.addSeparator()

        icon = "material/editor/checklist_rtl/materialiconsoutlined/48dp/2x/outline_checklist_rtl_black_48dp.png"
        self.addMenuPluginButton("ToDo", "todo", icon, self.secondToolBar)
        icon = "material/action/calendar_month/materialiconsoutlined/48dp/2x/outline_calendar_month_black_48dp.png"
        self.addMenuPluginButton("Journal and Bible Reading Plan", "journalAndBibleReadingPlan", icon, self.secondToolBar)
        icon = "material/maps/pin_drop/materialiconsoutlined/48dp/2x/outline_pin_drop_black_48dp.png"
        self.addMenuPluginButton("Bible Locations", "menu5_locations", icon, self.secondToolBar)
        icon = "material/social/groups/materialiconsoutlined/48dp/2x/outline_groups_black_48dp.png"
        self.addMenuPluginButton("Bible Characters", "menu5_characters", icon, self.secondToolBar)
        icon = "material/action/view_timeline/materialiconsoutlined/48dp/2x/outline_view_timeline_black_48dp.png"
        self.addMenuPluginButton("Bible Timelines", "bibleTimelines", icon, self.secondToolBar)
        icon = "material/action/token/materialiconsoutlined/48dp/2x/outline_token_black_48dp.png"
        self.addMenuPluginButton("Bible_Data", "bibleData", icon, self.secondToolBar)
        icon = "material/hardware/gamepad/materialiconsoutlined/48dp/2x/outline_gamepad_black_48dp.png"
        self.addMenuPluginButton("Bible Parallels", "bibleHarmonies", icon, self.secondToolBar)
        icon = "material/action/thumb_up_off_alt/materialicons/48dp/2x/baseline_thumb_up_off_alt_black_48dp.png"
        self.addMenuPluginButton("Bible Promises", "biblePromises", icon, self.secondToolBar)
        icon = "material/action/fact_check/materialiconsoutlined/48dp/2x/outline_fact_check_black_48dp.png"
        self.addMenuPluginButton("Bible Topics", "menu5_topics", icon, self.secondToolBar)
        icon = "material/action/language/materialiconsoutlined/48dp/2x/outline_language_black_48dp.png"
        self.addMenuPluginButton("Bible Lexicons", "bibleLexicons", icon, self.secondToolBar)
        icon = "material/action/account_balance/materialiconsoutlined/48dp/2x/outline_account_balance_black_48dp.png"
        self.addMenuPluginButton("Bible Encyclopedia", "context1_encyclopedia", icon, self.secondToolBar)
        icon = "material/content/inventory_2/materialiconsoutlined/48dp/2x/outline_inventory_2_black_48dp.png"
        self.addMenuPluginButton("Bible Dictionaries", "context1_dict", icon, self.secondToolBar)
        icon = "material/image/looks_3/materialiconsoutlined/48dp/2x/outline_looks_3_black_48dp.png"
        self.addMenuPluginButton("Third Party Dictionaries", "menu5_3rdDict", icon, self.secondToolBar)
        icon = "material/action/view_day/materialiconsoutlined/48dp/2x/outline_view_day_black_48dp.png"
        self.addMenuPluginButton("Interlinear Data", "interlinearData", icon, self.secondToolBar)
        if os.path.isfile(os.path.join(config.packageDir, "plugins", "context", "Charts and Table.py")):
            icon = "material/action/addchart/materialiconsoutlined/48dp/2x/outline_addchart_black_48dp.png"
            self.addMaterialIconButton("chartsAndTable", icon, self.generateChartsAndTable, self.secondToolBar)
        icon = "material/action/space_dashboard/materialiconsoutlined/48dp/2x/outline_space_dashboard_black_48dp.png"
        self.addMaterialIconButton("workspace", icon, self.displayWorkspace, self.secondToolBar)
        self.secondToolBar.addSeparator()

        icon = "material/action/highlight_alt/materialiconsoutlined/48dp/2x/outline_highlight_alt_black_48dp.png"
        self.selectionMonitoringButton = QPushButton()
        self.addMaterialIconButton(self.getSelectionMonitoringButtonToolTip(), icon, self.selectionMonitoringButtonClicked, self.secondToolBar, self.selectionMonitoringButton, translation=False)
        self.selectionMonitoringButton.setCheckable(True)
        self.selectionMonitoringButton.setChecked(True if config.enableSelectionMonitoring else False)
        if os.path.isfile(os.path.join(config.packageDir, "plugins", "context", "Search Bible for English Word Forms.py")):
            icon = "material/action/abc/materialiconsoutlined/48dp/2x/outline_abc_black_48dp.png"
            self.addMaterialIconButton("searchEnglishBible", icon, lambda: self.mainView.currentWidget().runPlugin("Search Bible for English Word Forms", activeSelection=True), self.secondToolBar)
        if not config.noTtsFound:
            icon = "material/action/record_voice_over/materialiconsoutlined/48dp/2x/outline_record_voice_over_black_48dp.png"
            self.instantTtsButton = QPushButton()
            self.addMaterialIconButton("{0} - {1}".format(config.thisTranslation["context1_speak"], config.ttsDefaultLangauge), icon, self.instantTTS, self.secondToolBar, self.instantTtsButton, False)
            if config.ttsDefaultLangauge2:
                icon = "material/av/interpreter_mode/materialiconsoutlined/48dp/2x/outline_interpreter_mode_black_48dp.png"
                self.instantTtsButton2 = QPushButton()
                self.addMaterialIconButton("{0} - {1}".format(config.thisTranslation["context1_speak"], config.ttsDefaultLangauge2), icon, self.instantTTS2, self.secondToolBar, self.instantTtsButton2, False)
            if config.ttsDefaultLangauge3:
                icon = "material/av/interpreter_mode/materialiconsoutlined/48dp/2x/outline_interpreter_mode_black_48dp.png"
                self.instantTtsButton3 = QPushButton()
                self.addMaterialIconButton("{0} - {1}".format(config.thisTranslation["context1_speak"], config.ttsDefaultLangauge3), icon, self.instantTTS3, self.secondToolBar, self.instantTtsButton3, False)

        icon = "material/hardware/smart_toy/materialiconsoutlined/48dp/2x/outline_smart_toy_black_48dp.png"
        #if config.openaiApi_key:
            #icon = "material/action/question_answer/materialiconsoutlined/48dp/2x/outline_question_answer_black_48dp.png"
            #self.addMenuPluginButton("Bible Chat", "Bible Chat", icon, self.secondToolBar, translation=False)
        self.bibleChatButton = QToolButton()
        self.setBibleChatButton()
        self.secondToolBar.addWidget(self.bibleChatButton)
        #else:
            #self.addMenuPluginButton("ChatGPT", "ChatGPT", icon, self.secondToolBar, translation=False)
        self.secondToolBar.addSeparator()

        icon = "material/social/travel_explore/materialiconsoutlined/48dp/2x/outline_travel_explore_black_48dp.png"
        self.addMenuPluginButton("Google", "Google", icon, self.secondToolBar, translation=False)
        if ("Ytdlp" in config.enabled):
            icon = "material/hardware/browser_updated/materialiconsoutlined/48dp/2x/outline_browser_updated_black_48dp.png"
            self.addMaterialIconButton("menu11_youtube", icon, self.openMiniBrowser, self.secondToolBar)
        icon = "material/communication/email/materialiconsoutlined/48dp/2x/outline_email_black_48dp.png"
        self.addMenuPluginButton("Gmail", "Gmail", icon, self.secondToolBar, translation=False)

        officeTools = ["Office 365", "Teams", "Outlook", "Calendar", "Word", "Excel", "PowerPoint", "Forms", "OneNote", "OneDrive"]
        enabledOfficeTools = []
        for tool in officeTools:
            toolName = f"Microsoft {tool}"
            if self.isMenuPlugin(toolName) and not toolName in config.excludeMenuPlugins:
                enabledOfficeTools.append(tool)
        if enabledOfficeTools:
            officeButton = QToolButton()
            icon = "material/action/work/materialiconsoutlined/48dp/2x/outline_work_black_48dp.png"
            qIcon = self.getQIcon(self.getCrossplatformPath(icon))
            officeButton.setStyleSheet(qIcon)
            officeButton.setPopupMode(QToolButton.InstantPopup)
            officeButton.setArrowType(Qt.NoArrow)
            officeButton.setCursor(QCursor(Qt.PointingHandCursor))
            officeButton.setToolTip("Microsoft")
            officeButtonMenu = QMenu(officeButton)
            for enabledTool in enabledOfficeTools:
                enabledToolName = f"Microsoft {enabledTool}"
                action = officeButtonMenu.addAction(enabledTool)
                action.triggered.connect(partial(self.runPlugin, enabledToolName))
            officeButton.setMenu(officeButtonMenu)
            self.secondToolBar.addWidget(officeButton)
            #self.secondToolBar.addSeparator()

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

        self.switchOrientationButton = QPushButton()
        self.addMaterialIconButton(self.getOrientationDisplayToolTip(), self.getOrientationDisplay(), self.orientationButtonClicked, self.secondToolBar, self.switchOrientationButton, False)
        icon = "material/action/expand/materialiconsoutlined/48dp/2x/outline_expand_black_48dp.png"
        self.addMaterialIconButton("menu2_study", icon, self.parallel, self.secondToolBar)
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

        if not config.useThirdPartyVLCplayer:

            if config.maximiseMediaPlayerUI:
                self.addToolBarBreak()

            # Third tool bar
            self.thirdToolBar = QToolBar()
            self.thirdToolBar.setWindowTitle(config.thisTranslation["menu11_audio"])
            self.thirdToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
            self.addToolBar(self.thirdToolBar)

            icon = "material/file/folder_open/materialiconsoutlined/48dp/2x/outline_folder_open_black_48dp.png"
            self.addMaterialIconButton("media", icon, partial(self.openControlPanelTab, 6), self.thirdToolBar)
            icon = "material/av/skip_previous/materialiconsoutlined/48dp/2x/outline_skip_previous_black_48dp.png"
            self.addMaterialIconButton("previous", icon, self.previousAudioFile, self.thirdToolBar)
            icon = "material/av/play_circle_outline/materialiconsoutlined/48dp/2x/outline_play_circle_outline_black_48dp.png"
            self.addMaterialIconButton("play", icon, self.playAudioPlaying, self.thirdToolBar)
            icon = "material/av/pause_circle/materialiconsoutlined/48dp/2x/outline_pause_circle_black_48dp.png"
            self.addMaterialIconButton("pause", icon, self.pauseAudioPlaying, self.thirdToolBar)
            icon = "material/av/stop_circle/materialiconsoutlined/48dp/2x/outline_stop_circle_black_48dp.png"
            self.addMaterialIconButton("stop", icon, self.stopAudioPlaying, self.thirdToolBar)
            icon = "material/av/skip_next/materialiconsoutlined/48dp/2x/outline_skip_next_black_48dp.png"
            self.addMaterialIconButton("next", icon, self.nextAudioFile, self.thirdToolBar)

            self.thirdToolBar.addSeparator()

            self.seek_slider = QSlider(Qt.Horizontal, self)
            self.seek_slider.setRange(0, 0)  # Set the range to 0 initially, as we don't know the duration yet
            self.seek_slider.sliderMoved.connect(self.on_slider_moved)  # Connect the sliderMoved signal to our on_slider_moved slot
            self.thirdToolBar.addWidget(self.seek_slider)

            #self.thirdToolBar.addSeparator()

            self.speedButton = QToolButton()
            self.setSpeedButtonButton()
            self.thirdToolBar.addWidget(self.speedButton)

            self.thirdToolBar.addSeparator()

            self.volumeSlider = QSlider()
            self.volumeSlider.setOrientation(Qt.Horizontal)
            self.volumeSlider.setMinimum(0)
            self.volumeSlider.setMaximum(100)
            available_width = self.screen().availableGeometry().width()
            self.volumeSlider.setFixedWidth(int(available_width / 10))
            #self.volumeSlider.setTickInterval(10)
            #self.volumeSlider.setTickPosition(QSlider.TicksBelow)
            self.volumeSlider.setToolTip(config.thisTranslation["volume"])
            self.volumeSlider.valueChanged.connect(self.setAudioVolume)
            self.volumeSlider.setValue(config.audioVolume)
            self.thirdToolBar.addWidget(self.volumeSlider)

            #self.thirdToolBar.addSeparator()

            iconFile = os.path.join("htmlResources", self.getMuteAudioDisplay())
            self.muteAudioButton = self.thirdToolBar.addAction(self.getMaskedQIcon(iconFile, config.maskMaterialIconColor, config.maskMaterialIconBackground, True), self.getMuteAudioToolTip(), self.muteAudioButtonClicked)

            self.thirdToolBar.addSeparator()

            icon = "material/image/video_camera_front/materialiconsoutlined/48dp/2x/outline_video_camera_front_black_48dp.png"
            self.addMaterialIconButton("menu11_video", icon, self.showVideoView, self.thirdToolBar)
            icon = "material/av/queue_music/materialiconsoutlined/48dp/2x/outline_queue_music_black_48dp.png"
            self.addMaterialIconButton("playlist", icon, self.openAudioPlayListUI, self.thirdToolBar)
            self.loopMediaButton = QPushButton()
            self.addMaterialIconButton(self.getLoopMediaButtonToolTip(), self.getLoopMediaButtonDisplay(), self.loopMediaButtonClicked, self.thirdToolBar, self.loopMediaButton, False)
            self.audioTextSyncButton = QPushButton()
            self.addMaterialIconButton(self.getAudioTextSyncToolTip(), self.getAudioTextSyncDisplay(), self.audioTextSyncButtonClicked, self.thirdToolBar, self.audioTextSyncButton, False)
            self.audioTextScrollSyncButton = QPushButton()
            self.addMaterialIconButton(self.getAudioTextScrollSyncToolTip(), self.getAudioTextScrollSyncDisplay(), self.audioTextScrollSyncButtonClicked, self.thirdToolBar, self.audioTextScrollSyncButton, False)
            icon = "material/action/open_in_full/materialiconsoutlined/48dp/2x/outline_open_in_full_black_48dp.png"
            self.addMaterialIconButton("menu1_resize", icon, self.resizeAudioPlayer, self.thirdToolBar)

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
#        if ("Htmldocx" in config.enabled):
#            icon = "material/action/description/materialiconsoutlined/48dp/2x/outline_description_black_48dp.png"
#            self.addMaterialIconButton("exportToDocx", icon, self.exportMainPageToDocx, self.leftToolBar)
#        icon = "material/image/picture_as_pdf/materialiconsoutlined/48dp/2x/outline_picture_as_pdf_black_48dp.png"
#        self.addMaterialIconButton("bar3_pdf", icon, self.printMainPage, self.leftToolBar)
        icon = "material/device/reviews/materialiconsoutlined/48dp/2x/outline_reviews_black_48dp.png"
        tooltip = "{0} [{1}]".format(config.thisTranslation["addToWorkSpace"], config.thisTranslation["readOnly"])
        self.addMaterialIconButton(tooltip, icon, lambda: self.mainView.currentWidget().addToWorkspaceReadOnly(), self.leftToolBar, None, False)
        icon = "material/maps/rate_review/materialiconsoutlined/48dp/2x/outline_rate_review_black_48dp.png"
        tooltip = "{0} [{1}]".format(config.thisTranslation["addToWorkSpace"], config.thisTranslation["editable"])
        self.addMaterialIconButton(tooltip, icon, lambda: self.mainView.currentWidget().addToWorkspaceEditable(), self.leftToolBar, None, False)
        self.leftToolBar.addSeparator()
        self.enableParagraphButton = QPushButton()
        self.addMaterialIconButton(self.getReadFormattedBiblesToolTip(), self.getReadFormattedBibles(), self.enableParagraphButtonClicked, self.leftToolBar, self.enableParagraphButton, False)
        iconFile = os.path.join("htmlResources", self.getAddSubheading())
        self.enableSubheadingButton = self.leftToolBar.addAction(self.getMaskedQIcon(iconFile, config.maskMaterialIconColor, config.maskMaterialIconBackground, True), self.enableSubheadingToolTip(), self.enableSubheadingButtonClicked2)
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
#        if ("Htmldocx" in config.enabled):
#            icon = "material/action/description/materialiconsoutlined/48dp/2x/outline_description_black_48dp.png"
#            self.addMaterialIconButton("exportToDocx", icon, self.exportStudyPageToDocx, self.rightToolBar)
#        icon = "material/image/picture_as_pdf/materialiconsoutlined/48dp/2x/outline_picture_as_pdf_black_48dp.png"
#        self.addMaterialIconButton("bar3_pdf", icon, self.printStudyPage, self.rightToolBar)
        icon = "material/device/reviews/materialiconsoutlined/48dp/2x/outline_reviews_black_48dp.png"
        tooltip = "{0} [{1}]".format(config.thisTranslation["addToWorkSpace"], config.thisTranslation["readOnly"])
        self.addMaterialIconButton(tooltip, icon, lambda: self.studyView.currentWidget().addToWorkspaceReadOnly(), self.rightToolBar, None, False)
        icon = "material/maps/rate_review/materialiconsoutlined/48dp/2x/outline_rate_review_black_48dp.png"
        tooltip = "{0} [{1}]".format(config.thisTranslation["addToWorkSpace"], config.thisTranslation["editable"])
        self.addMaterialIconButton(tooltip, icon, lambda: self.studyView.currentWidget().addToWorkspaceEditable(), self.rightToolBar, None, False)
        self.rightToolBar.addSeparator()
        icon = "material/editor/highlight/materialiconsoutlined/48dp/2x/outline_highlight_black_48dp.png"
        self.addMaterialIconButton("menu4_indexes", icon, self.runINDEX, self.rightToolBar)
        icon = "material/communication/comment/materialiconsoutlined/48dp/2x/outline_comment_black_48dp.png"
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
        #if os.path.isfile(os.path.join(config.packageDir, "plugins", "menu", "Interlinear Data.py")) and os.path.isfile(os.path.join(config.packageDir, "plugins", "context", "Interlinear Data.py")):
        #    icon = "material/image/flare/materialiconsoutlined/48dp/2x/outline_flare_black_48dp.png"
        #    self.addMaterialIconButton("interlinearData", icon, self.openInterlinearData, self.rightToolBar)
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