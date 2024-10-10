from uniquebible import config
import platform, webbrowser, os
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
else:
    from qtpy.QtCore import Qt
    from qtpy.QtGui import QStandardItemModel, QStandardItem
    from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QMessageBox
from uniquebible.util.WebtopUtil import WebtopUtil


class ConfigFlagsWindow(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(config.thisTranslation["menu_config_flags"])
        self.setMinimumSize(830, 500)
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()

    def setupVariables(self):
        self.isUpdating = False

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel(config.thisTranslation["menu_config_flags"])
        title.mouseReleaseEvent = self.openWiki
        mainLayout.addWidget(title)

        filterLayout = QHBoxLayout()
        filterLayout.addWidget(QLabel(config.thisTranslation["menu5_search"]))
        self.filterEntry = QLineEdit()
        self.filterEntry.textChanged.connect(self.resetItems)
        filterLayout.addWidget(self.filterEntry)
        mainLayout.addLayout(filterLayout)

        self.dataView = QTableView()
        self.dataView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dataView.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.dataView)
        self.dataView.setModel(self.dataViewModel)
        self.resetItems()
        self.dataViewModel.itemChanged.connect(self.itemChanged)
        mainLayout.addWidget(self.dataView)

        buttonLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["close"])
        button.clicked.connect(self.close)
        buttonLayout.addWidget(button)
        button = QPushButton(config.thisTranslation["restoreAllDefaults"])
        button.clicked.connect(self.restoreAllDefaults)
        buttonLayout.addWidget(button)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def getOptions(self):
        options = [
            ("updateDependenciesOnStartup", config.updateDependenciesOnStartup, self.updateDependenciesOnStartupChanged, False, config.thisTranslation["updateDependenciesOnStartup"]),
            ("showControlPanelOnStartup", config.showControlPanelOnStartup, self.showControlPanelOnStartupChanged, False, config.thisTranslation["showControlPanelOnStartup"]),
            ("preferControlPanelForCommandLineEntry", config.preferControlPanelForCommandLineEntry, self.preferControlPanelForCommandLineEntryChanged, False, config.thisTranslation["preferControlPanelForCommandLineEntry"]),
            ("closeControlPanelAfterRunningCommand", config.closeControlPanelAfterRunningCommand, self.closeControlPanelAfterRunningCommandChanged, True, config.thisTranslation["closeControlPanelAfterRunningCommand"]),
            ("restrictControlPanelWidth", config.restrictControlPanelWidth, self.restrictControlPanelWidthChanged, False, config.thisTranslation["restrictControlPanelWidth"]),
            ("clearCommandEntry", config.clearCommandEntry, self.clearCommandEntryChanged, False, config.thisTranslation["clearCommandEntry"]),
            ("openBibleWindowContentOnNextTab", config.openBibleWindowContentOnNextTab, self.openBibleWindowContentOnNextTabChanged, False, config.thisTranslation["openBibleWindowContentOnNextTab"]),
            ("openStudyWindowContentOnNextTab", config.openStudyWindowContentOnNextTab, self.openStudyWindowContentOnNextTabChanged, True, config.thisTranslation["openStudyWindowContentOnNextTab"]),
            ("updateMainReferenceOnChangingTabs", config.updateMainReferenceOnChangingTabs, self.updateMainReferenceOnChangingTabsChanged, False, config.thisTranslation["updateMainReferenceOnChangingTabs"]),
            ("usePySide2onWebtop", config.usePySide2onWebtop, self.usePySide2onWebtopChanged, True, config.thisTranslation["usePySide2onWebtop"]),
            ("usePySide6onMacOS", config.usePySide6onMacOS, self.usePySide6onMacOSChanged, True, config.thisTranslation["usePySide6onMacOS"]),
            ("populateTabsOnStartup", config.populateTabsOnStartup, self.populateTabsOnStartupChanged, False, config.thisTranslation["populateTabsOnStartup"]),
            ("qtMaterial", config.qtMaterial, self.qtMaterialChanged, False, config.thisTranslation["qtMaterial"]),
            ("startFullScreen", config.startFullScreen, self.startFullScreenChanged, False, "Option to launch UBA in fullscreen."),
            ("addBreakAfterTheFirstToolBar", config.addBreakAfterTheFirstToolBar, self.addBreakAfterTheFirstToolBarChanged, True, config.thisTranslation["addBreakAfterTheFirstToolBar"]),
            ("addBreakBeforeTheLastToolBar", config.addBreakBeforeTheLastToolBar, self.addBreakBeforeTheLastToolBarChanged, False, config.thisTranslation["addBreakBeforeTheLastToolBar"]),
            ("parserStandarisation", (config.parserStandarisation == "YES"), self.parserStandarisationChanged, False, config.thisTranslation["parserStandarisation"]),
            ("useLiteVerseParsing", config.useLiteVerseParsing, self.useLiteVerseParsingChanged, False, config.thisTranslation["useLiteVerseParsing"]),
            ("parseEnglishBooksOnly", config.parseEnglishBooksOnly, self.parseEnglishBooksOnlyChanged, False, config.thisTranslation["parseEnglishBooksOnly"]),
            ("parseWordDocument", config.parseWordDocument, self.parseWordDocumentChanged, True, config.thisTranslation["parseWordDocument"]),
            ("convertChapterVerseDotSeparator", config.convertChapterVerseDotSeparator, self.convertChapterVerseDotSeparatorChanged, True, config.thisTranslation["convertChapterVerseDotSeparator"]),
            ("parseBookChapterWithoutSpace", config.parseBookChapterWithoutSpace, self.parseBookChapterWithoutSpaceChanged, True, config.thisTranslation["parseBookChapterWithoutSpace"]),
            ("parseBooklessReferences", config.parseBooklessReferences, self.parseBooklessReferencesChanged, True, config.thisTranslation["parseBooklessReferences"]),
            ("enableCaseSensitiveSearch", config.enableCaseSensitiveSearch, self.enableCaseSensitiveSearchChanged, False, config.thisTranslation["enableCaseSensitiveSearch"]),
            #("searchBibleIfCommandNotFound", config.searchBibleIfCommandNotFound, self.searchBibleIfCommandNotFoundChanged, True, config.thisTranslation["searchBibleIfCommandNotFound"]),
            #("regexSearchBibleIfCommandNotFound", config.regexSearchBibleIfCommandNotFound, self.regexSearchBibleIfCommandNotFoundChanged, False, config.thisTranslation["regexSearchBibleIfCommandNotFound"]),
            ("preferHtmlMenu", config.preferHtmlMenu, self.preferHtmlMenuChanged, False, config.thisTranslation["preferHtmlMenu"]),
            ("showVerseNumbersInRange", config.showVerseNumbersInRange, self.showVerseNumbersInRangeChanged, True, config.thisTranslation["showVerseNumbersInRange"]),
            ("addFavouriteToMultiRef", config.addFavouriteToMultiRef, self.addFavouriteToMultiRefChanged, True, config.thisTranslation["addFavouriteToMultiRef"]),
            ("enableVerseHighlighting", config.enableVerseHighlighting, self.enableVerseHighlightingChanged, True, config.thisTranslation["enableVerseHighlighting"]),
            ("alwaysDisplayStaticMaps", config.alwaysDisplayStaticMaps, self.alwaysDisplayStaticMapsChanged, False, config.thisTranslation["alwaysDisplayStaticMaps"]),
            ("exportEmbeddedImages", config.exportEmbeddedImages, self.exportEmbeddedImagesChanged, True, config.thisTranslation["exportEmbeddedImages"]),
            ("clickToOpenImage", config.clickToOpenImage, self.clickToOpenImageChanged, True, config.thisTranslation["clickToOpenImage"]),
            ("showUserNoteIndicator", config.showUserNoteIndicator, self.parent.toggleShowUserNoteIndicator, True, config.thisTranslation["displayUserNoteIndicator"]),
            ("showBibleNoteIndicator", config.showBibleNoteIndicator, self.parent.toggleShowBibleNoteIndicator, True, config.thisTranslation["displayBibleNoteIndicator"]),
            ("showVerseReference", config.showVerseReference, self.parent.toggleShowVerseReference, True, config.thisTranslation["displayVerseReference"]),
            ("showHebrewGreekWordAudioLinks", config.showHebrewGreekWordAudioLinks, self.parent.toggleShowHebrewGreekWordAudioLinks, False, config.thisTranslation["showHebrewGreekWordAudioLinks"]),
            ("showHebrewGreekWordAudioLinksInMIB", config.showHebrewGreekWordAudioLinksInMIB, self.parent.toggleShowHebrewGreekWordAudioLinksInMIB, False, config.thisTranslation["showHebrewGreekWordAudioLinksInMIB"]),
            ("hideLexicalEntryInBible", config.hideLexicalEntryInBible, self.parent.toggleHideLexicalEntryInBible, False, config.thisTranslation["displayLexicalEntry"]),
            ("openBibleNoteAfterSave", config.openBibleNoteAfterSave, self.openBibleNoteAfterSaveChanged, False, config.thisTranslation["openBibleNoteAfterSave"]),
            ("openBibleNoteAfterEditorClosed", config.openBibleNoteAfterEditorClosed, self.openBibleNoteAfterEditorClosedChanged, False, config.thisTranslation["openBibleNoteAfterEditorClosed"]),
            ("dockNoteEditorOnStartup", config.dockNoteEditorOnStartup, self.dockNoteEditorChanged, True, config.thisTranslation["dockNoteEditorOnStartup"]),
            ("doNotDockNoteEditorByDragging", config.doNotDockNoteEditorByDragging, self.doNotDockNoteEditorByDraggingChanged, False, config.thisTranslation["doNotDockNoteEditorByDragging"]),
            ("hideNoteEditorStyleToolbar", config.hideNoteEditorStyleToolbar, self.hideNoteEditorStyleToolbarChanged, False, config.thisTranslation["hideNoteEditorStyleToolbar"]),
            ("hideNoteEditorTextUtility", config.hideNoteEditorTextUtility, self.hideNoteEditorTextUtilityChanged, True, config.thisTranslation["hideNoteEditorTextUtility"]),
            ("overwriteNoteFont", config.overwriteNoteFont, self.overwriteNoteFontChanged, True, config.thisTranslation["overwriteNoteFont"]),
            ("overwriteNoteFontSize", config.overwriteNoteFontSize, self.overwriteNoteFontSizeChanged, True, config.thisTranslation["overwriteNoteFontSize"]),
            ("overwriteBookFont", config.overwriteBookFont, self.overwriteBookFontChanged, True, config.thisTranslation["overwriteBookFont"]),
            ("overwriteBookFontSize", config.overwriteBookFontSize, self.overwriteBookFontSizeChanged, True, config.thisTranslation["overwriteBookFontSize"]),
            ("openBookInNewWindow", config.openBookInNewWindow, self.openBookInNewWindowChanged, False, config.thisTranslation["openBookInNewWindow"]),
            ("openPdfViewerInNewWindow", config.openPdfViewerInNewWindow, self.openPdfViewerInNewWindowChanged, False, config.thisTranslation["openPdfViewerInNewWindow"]),
            ("virtualKeyboard", config.virtualKeyboard, self.virtualKeyboardChanged, False, config.thisTranslation["virtualKeyboard"]),
            ("useWebbrowser", config.useWebbrowser, self.useWebbrowserChanged, True, config.thisTranslation["useWebbrowser"]),
            ("removeHighlightOnExit", config.removeHighlightOnExit, self.removeHighlightOnExitChanged, False, config.thisTranslation["removeHighlightOnExit"]),
            ("disableModulesUpdateCheck", config.disableModulesUpdateCheck, self.disableModulesUpdateCheckChanged, True, config.thisTranslation["disableModulesUpdateCheck"]),
            ("updateWithGitPull", config.updateWithGitPull, self.updateWithGitPullChanged, False, config.thisTranslation["updateWithGitPull"]),
            ("enableGist", config.enableGist, self.enableGistChanged, False, config.thisTranslation["enableGist"]),
            ("enableMacros", config.enableMacros, self.enableMacrosChanged, False, config.thisTranslation["enableMacros"]),
            ("enablePlugins", config.enablePlugins, self.enablePluginsChanged, True, config.thisTranslation["enablePlugins"]),
            ("hideBlankVerseCompare", config.hideBlankVerseCompare, self.hideBlankVerseCompareChanged, False, config.thisTranslation["hideBlankVerseCompare"]),
            ("enforceCompareParallel", config.enforceCompareParallel, self.parent.enforceCompareParallelButtonClicked, False, config.thisTranslation["enforceCompareParallel"]),
            ("compareOnStudyWindow", config.compareOnStudyWindow, self.compareOnStudyWindowChanged, False, config.help["compareOnStudyWindow"][11:]),
            ("enableMenuUnderline", config.enableMenuUnderline, self.enableMenuUnderlineChanged, True, config.thisTranslation["enableMenuUnderline"]),
            ("openBibleInMainViewOnly", config.openBibleInMainViewOnly, self.parent.enableStudyBibleButtonClicked, False, config.thisTranslation["openBibleInMainViewOnly"]),
            ("addOHGBiToMorphologySearch", config.addOHGBiToMorphologySearch, self.addOHGBiToMorphologySearchChanged, True, config.thisTranslation["addOHGBiToMorphologySearch"]),
            ("includeStrictDocTypeInNote", config.includeStrictDocTypeInNote, self.includeStrictDocTypeInNoteChanged, False, config.thisTranslation["includeStrictDocTypeInNote"]),
            ("parseTextConvertNotesToBook", config.parseTextConvertNotesToBook, self.parseTextConvertNotesToBookChanged, False, config.thisTranslation["parseTextConvertNotesToBook"]),
            ("parseTextConvertHTMLToBook", config.parseTextConvertHTMLToBook, self.parseTextConvertHTMLToBookChanged, False, config.thisTranslation["parseTextConvertHTMLToBook"]),
            ("commandTextIfNoSelection", config.commandTextIfNoSelection, self.commandTextIfNoSelectionChanged, False, config.thisTranslation["commandTextIfNoSelection"]),
            ("displayCmdOutput", config.displayCmdOutput, self.displayCmdOutputChanged, False, config.thisTranslation["displayCmdOutput"]),
            ("disableLoadLastOpenFilesOnStartup", config.disableLoadLastOpenFilesOnStartup, self.disableLoadLastOpenFilesOnStartupChanged, False, config.thisTranslation["disableLoadLastOpenFilesOnStartup"]),
            ("disableOpenPopupWindowOnStartup", config.disableOpenPopupWindowOnStartup, self.disableOpenPopupWindowOnStartupChanged, True, config.thisTranslation["disableOpenPopupWindowOnStartup"]),
            ("showMiniKeyboardInMiniControl", config.showMiniKeyboardInMiniControl, self.showMiniKeyboardInMiniControlChanged, False, config.thisTranslation["showMiniKeyboardInMiniControl"]),
            ("useFfmpegToChangeAudioSpeed", config.useFfmpegToChangeAudioSpeed, self.useFfmpegToChangeAudioSpeedChanged, False, config.thisTranslation["useFfmpegToChangeAudioSpeed"]),
            ("usePydubToChangeAudioSpeed", config.usePydubToChangeAudioSpeed, self.usePydubToChangeAudioSpeedChanged, False, config.thisTranslation["usePydubToChangeAudioSpeed"]),
            ("useThirdPartyVLCplayerForVideoOnly", config.useThirdPartyVLCplayerForVideoOnly, self.useThirdPartyVLCplayerForVideoOnlyChanged, False, config.thisTranslation["useThirdPartyVLCplayerForVideoOnly"]),
            ("useThirdPartyVLCplayer", config.useThirdPartyVLCplayer, self.useThirdPartyVLCplayerChanged, False, config.thisTranslation["useThirdPartyVLCplayer"]),
            ("terminalForceVlc", config.terminalForceVlc, self.terminalForceVlcChanged, True, config.thisTranslation["terminalForceVlc"]),
            ("hideVlcInterfaceReadingSingleVerse", config.hideVlcInterfaceReadingSingleVerse, self.hideVlcInterfaceReadingSingleVerseChanged, True, config.thisTranslation["hideVlcInterfaceReadingSingleVerse"]),
            ("doNotStop3rdPartyMediaPlayerOnExit", config.doNotStop3rdPartyMediaPlayerOnExit, self.doNotStop3rdPartyMediaPlayerOnExitChanged, False, config.thisTranslation["doNotStop3rdPartyMediaPlayerOnExit"]),
            ("refreshWindowsAfterSavingNote", config.refreshWindowsAfterSavingNote, self.refreshWindowsAfterSavingNoteChanged, True, config.thisTranslation["refreshWindowsAfterSavingNote"]),
            ("limitWorkspaceFilenameLength", config.limitWorkspaceFilenameLength, self.limitWorkspaceFilenameLengthChanged, True, config.thisTranslation["limitWorkspaceFilenameLength"]),
            ("enableHttpRemoteErrorRedirection", config.enableHttpRemoteErrorRedirection, self.enableHttpRemoteErrorRedirection, False, config.thisTranslation["enableHttpRemoteErrorRedirection"]),
        ]
        if ("OfflineTts" in config.enabled):
            options += [
                ("useLangDetectOnTts", config.useLangDetectOnTts, self.useLangDetectOnTtsChanged, False, config.thisTranslation["useLangDetectOnTts"]),
                ("ttsEnglishAlwaysUS", config.ttsEnglishAlwaysUS, self.ttsEnglishAlwaysUSChanged, False, config.thisTranslation["ttsEnglishAlwaysUS"]),
                ("ttsEnglishAlwaysUK", config.ttsEnglishAlwaysUK, self.ttsEnglishAlwaysUKChanged, False, config.thisTranslation["ttsEnglishAlwaysUK"]),
                ("ttsChineseAlwaysMandarin", config.ttsChineseAlwaysMandarin, self.ttsChineseAlwaysMandarinChanged, False, config.thisTranslation["ttsChineseAlwaysMandarin"]),
                ("ttsChineseAlwaysCantonese", config.ttsChineseAlwaysCantonese, self.ttsChineseAlwaysCantoneseChanged, False, config.thisTranslation["ttsChineseAlwaysCantonese"]),
            ]
        if ("OnlineTts" in config.enabled):
            options += [
                ("forceOnlineTts", config.forceOnlineTts, self.forceOnlineTtsChanged, False, config.thisTranslation["forceOnlineTts"]),
            ]
        if platform.system() == "Linux":
            options += [
                ("enableSystemTrayOnLinux", config.enableSystemTrayOnLinux, self.enableSystemTrayOnLinuxChanged, False, config.thisTranslation["enableSystemTrayOnLinux"]),
                ("linuxStartFullScreen", config.linuxStartFullScreen, self.linuxStartFullScreenChanged, False, config.thisTranslation["linuxStartFullScreen"]),
                ("fcitx5", config.fcitx5, self.fcitx5Changed, False, f'[fcitx5] {config.thisTranslation["fcitx"]}'),
                ("fcitx", config.fcitx, self.fcitxChanged, False, config.thisTranslation["fcitx"]),
                ("ibus", config.ibus, self.ibusChanged, False, config.thisTranslation["ibus"]),
                ("espeak", config.espeak, self.espeakChanged, False, config.thisTranslation["espeak"]),
                ("piper", config.piper, self.piperChanged, False, "piper text-to-speech feature"),
            ]
        if config.developer:
            options += [
                ("forceGenerateHtml", config.forceGenerateHtml, self.forceGenerateHtmlChanged, False, config.thisTranslation["forceGenerateHtml"]),
                ("enableLogging", config.enableLogging, self.enableLoggingChanged, False, config.thisTranslation["enableLogging"]),
                ("logCommands", config.logCommands, self.logCommandsChanged, False, config.thisTranslation["logCommands"]),
            ]
        data = {}
        for flag, configValue, action, default, tooltip in options:
            data[flag] = [configValue, default, tooltip, action]
        return data

    def restoreAllDefaults(self):
        for key, value in self.data.items():
            code = "config.{0} = {1}".format(key, value[1])
            exec(code)
        self.resetItems()
        self.parent.handleRestart()

    def itemChanged(self, standardItem):
        flag = standardItem.text()
        if flag in self.data and not self.isUpdating:
            self.data[flag][-1]()

    def resetItems(self):
        self.isUpdating = True
        # Empty the model before reset
        self.dataViewModel.clear()
        # Reset
        self.data = self.getOptions()
        filterEntry = self.filterEntry.text().lower()
        rowCount = 0
        for flag, value in self.data.items():
            configValue, default, tooltip, *_ = value
            if filterEntry == "" or (filterEntry != "" and (filterEntry in flag.lower() or filterEntry in tooltip.lower())):
                # 1st column
                item = QStandardItem(flag)
                item.setToolTip(tooltip)
                item.setCheckable(True)
                item.setCheckState(Qt.CheckState.Checked if configValue else Qt.CheckState.Unchecked)
                self.dataViewModel.setItem(rowCount, 0, item)
                # 2nd column
                item = QStandardItem(str(default))
                self.dataViewModel.setItem(rowCount, 1, item)
                # 3rd column
                tooltip = tooltip.replace("\n", " ")
                item = QStandardItem(tooltip)
                item.setToolTip(tooltip)
                self.dataViewModel.setItem(rowCount, 2, item)
                # add row count
                rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels([config.thisTranslation["flag"], config.thisTranslation["default"], config.thisTranslation["description"]])
        self.dataView.resizeColumnsToContents()
        self.isUpdating = False

    def displayMessage(self, message="", title="UniqueBible"):
        QMessageBox.information(self, title, message)

    def openWiki(self, event):
        wikiLink = "https://github.com/eliranwong/UniqueBible/wiki/Config-file-reference"
        webbrowser.open(wikiLink)

    def ibusChanged(self):
        config.ibus = not config.ibus
        if config.fcitx5 and config.ibus:
            config.fcitx5 = not config.fcitx5
        if config.fcitx and config.ibus:
            config.fcitx = not config.fcitx
        if config.virtualKeyboard and config.ibus:
            config.virtualKeyboard = not config.virtualKeyboard
        self.parent.handleRestart()

    def fcitxChanged(self):
        config.fcitx = not config.fcitx
        if config.fcitx and config.fcitx5:
            config.fcitx5 = not config.fcitx5
        if config.fcitx and config.ibus:
            config.ibus = not config.ibus
        if config.fcitx and config.virtualKeyboard:
            config.virtualKeyboard = not config.virtualKeyboard
        self.parent.handleRestart()

    def fcitx5Changed(self):
        config.fcitx5 = not config.fcitx5
        if config.fcitx5 and config.fcitx:
            config.fcitx = not config.fcitx
        if config.fcitx5 and config.ibus:
            config.ibus = not config.ibus
        if config.fcitx5 and config.virtualKeyboard:
            config.virtualKeyboard = not config.virtualKeyboard
        self.parent.handleRestart()

    def virtualKeyboardChanged(self):
        config.virtualKeyboard = not config.virtualKeyboard
        if config.fcitx and config.virtualKeyboard:
            config.fcitx = not config.fcitx
        if config.virtualKeyboard and config.ibus:
            config.ibus = not config.ibus
        self.parent.handleRestart()

    def parseWordDocumentChanged(self):
        config.parseWordDocument = not config.parseWordDocument

    def useLangDetectOnTtsChanged(self):
        config.useLangDetectOnTts = not config.useLangDetectOnTts

    def ttsEnglishAlwaysUSChanged(self):
        config.ttsEnglishAlwaysUS = not config.ttsEnglishAlwaysUS
        if config.ttsEnglishAlwaysUK and config.ttsEnglishAlwaysUS:
            config.ttsEnglishAlwaysUK = not config.ttsEnglishAlwaysUK

    def ttsEnglishAlwaysUKChanged(self):
        config.ttsEnglishAlwaysUK = not config.ttsEnglishAlwaysUK
        if config.ttsEnglishAlwaysUK and config.ttsEnglishAlwaysUS:
            config.ttsEnglishAlwaysUS = not config.ttsEnglishAlwaysUS

    def ttsChineseAlwaysMandarinChanged(self):
        config.ttsChineseAlwaysMandarin = not config.ttsChineseAlwaysMandarin
        if config.ttsChineseAlwaysMandarin and config.ttsChineseAlwaysCantonese:
            config.ttsChineseAlwaysCantonese = not config.ttsChineseAlwaysCantonese

    def useFfmpegToChangeAudioSpeedChanged(self):
        config.useFfmpegToChangeAudioSpeed = not config.useFfmpegToChangeAudioSpeed
        if config.useFfmpegToChangeAudioSpeed and not WebtopUtil.isPackageInstalled("ffmpeg"):
            config.useFfmpegToChangeAudioSpeed = False
        if config.usePydubToChangeAudioSpeed and config.useFfmpegToChangeAudioSpeed:
            config.usePydubToChangeAudioSpeed = False

    def usePydubToChangeAudioSpeedChanged(self):
        config.usePydubToChangeAudioSpeed = not config.usePydubToChangeAudioSpeed
        if config.usePydubToChangeAudioSpeed and not WebtopUtil.isPackageInstalled("ffmpeg"):
            config.usePydubToChangeAudioSpeed = False
        if config.usePydubToChangeAudioSpeed and config.useFfmpegToChangeAudioSpeed:
            config.useFfmpegToChangeAudioSpeed = False

    def terminalForceVlcChanged(self):
        config.terminalForceVlc = not config.terminalForceVlc
        if config.terminalForceVlc and not config.isVlcAvailable:
            config.terminalForceVlc = False

    def useThirdPartyVLCplayerForVideoOnlyChanged(self):
        config.useThirdPartyVLCplayerForVideoOnly = not config.useThirdPartyVLCplayerForVideoOnly
        if config.useThirdPartyVLCplayerForVideoOnly and not config.isVlcAvailable:
            config.useThirdPartyVLCplayerForVideoOnly = False

    def useThirdPartyVLCplayerChanged(self):
        config.useThirdPartyVLCplayer = not config.useThirdPartyVLCplayer
        if config.useThirdPartyVLCplayer and not config.isVlcAvailable:
            config.useThirdPartyVLCplayer = False
        self.parent.handleRestart()

    def doNotStop3rdPartyMediaPlayerOnExitChanged(self):
        config.doNotStop3rdPartyMediaPlayerOnExit = not config.doNotStop3rdPartyMediaPlayerOnExit
        self.parent.handleRestart()

    def enableSystemTrayOnLinuxChanged(self):
        config.enableSystemTrayOnLinux = not config.enableSystemTrayOnLinux
        self.parent.handleRestart()

    def dockNoteEditorChanged(self):
        config.dockNoteEditorOnStartup = not config.dockNoteEditorOnStartup
        self.parent.handleRestart()

    def ttsChineseAlwaysCantoneseChanged(self):
        config.ttsChineseAlwaysCantonese = not config.ttsChineseAlwaysCantonese
        if config.ttsChineseAlwaysMandarin and config.ttsChineseAlwaysCantonese:
            config.ttsChineseAlwaysMandarin = not config.ttsChineseAlwaysMandarin

    def showVerseNumbersInRangeChanged(self):
        config.showVerseNumbersInRange = not config.showVerseNumbersInRange

    def updateMainReferenceOnChangingTabsChanged(self):
        config.updateMainReferenceOnChangingTabs = not config.updateMainReferenceOnChangingTabs

    #def customPythonOnStartupChanged(self):
    #    config.customPythonOnStartup = not config.customPythonOnStartup

    def openBibleWindowContentOnNextTabChanged(self):
        config.openBibleWindowContentOnNextTab = not config.openBibleWindowContentOnNextTab
        self.newTabException = False

    def commandTextIfNoSelectionChanged(self):
        config.commandTextIfNoSelection = not config.commandTextIfNoSelection

    def showControlPanelOnStartupChanged(self):
        config.showControlPanelOnStartup = not config.showControlPanelOnStartup
        self.parent.handleRestart()

    def updateDependenciesOnStartupChanged(self):
        config.updateDependenciesOnStartup = not config.updateDependenciesOnStartup
        self.parent.handleRestart()

    def doNotDockNoteEditorByDraggingChanged(self):
        config.doNotDockNoteEditorByDragging = not config.doNotDockNoteEditorByDragging
        self.parent.handleRestart()

    def preferControlPanelForCommandLineEntryChanged(self):
        config.preferControlPanelForCommandLineEntry = not config.preferControlPanelForCommandLineEntry
        self.parent.handleRestart()

    def closeControlPanelAfterRunningCommandChanged(self):
        config.closeControlPanelAfterRunningCommand = not config.closeControlPanelAfterRunningCommand

    def restrictControlPanelWidthChanged(self):
        config.restrictControlPanelWidth = not config.restrictControlPanelWidth
        self.parent.reloadControlPanel(False)

    def enableCaseSensitiveSearchChanged(self):
        config.enableCaseSensitiveSearch = not config.enableCaseSensitiveSearch

    def openStudyWindowContentOnNextTabChanged(self):
        config.openStudyWindowContentOnNextTab = not config.openStudyWindowContentOnNextTab
        self.newTabException = False

    def addFavouriteToMultiRefChanged(self):
        config.addFavouriteToMultiRef = not config.addFavouriteToMultiRef

    def addOHGBiToMorphologySearchChanged(self):
        config.addOHGBiToMorphologySearch = not config.addOHGBiToMorphologySearch

    def exportEmbeddedImagesChanged(self):
        config.exportEmbeddedImages = not config.exportEmbeddedImages

    def clickToOpenImageChanged(self):
        config.clickToOpenImage = not config.clickToOpenImage

    def openBibleNoteAfterEditorClosedChanged(self):
        config.openBibleNoteAfterEditorClosed = not config.openBibleNoteAfterEditorClosed

    def preferHtmlMenuChanged(self):
        config.preferHtmlMenu = not config.preferHtmlMenu

    def hideNoteEditorStyleToolbarChanged(self):
        config.hideNoteEditorStyleToolbar = not config.hideNoteEditorStyleToolbar

    def hideNoteEditorTextUtilityChanged(self):
        config.hideNoteEditorTextUtility = not config.hideNoteEditorTextUtility

    def populateTabsOnStartupChanged(self):
        config.populateTabsOnStartup = not config.populateTabsOnStartup
        self.parent.handleRestart()

    def openBookInNewWindowChanged(self):
        config.openBookInNewWindow = not config.openBookInNewWindow

    def convertChapterVerseDotSeparatorChanged(self):
        config.convertChapterVerseDotSeparator = not config.convertChapterVerseDotSeparator

    def updateWithGitPullChanged(self):
        config.updateWithGitPull = not config.updateWithGitPull
        if config.updateWithGitPull and not os.path.isdir(".git"):
            config.updateWithGitPull = False

    def parseBookChapterWithoutSpaceChanged(self):
        config.parseBookChapterWithoutSpace = not config.parseBookChapterWithoutSpace

    def parseBooklessReferencesChanged(self):
        config.parseBooklessReferences = not config.parseBooklessReferences

    def openPdfViewerInNewWindowChanged(self):
        config.openPdfViewerInNewWindow = not config.openPdfViewerInNewWindow

#    def searchBibleIfCommandNotFoundChanged(self):
#        config.searchBibleIfCommandNotFound = not config.searchBibleIfCommandNotFound
#
#    def regexSearchBibleIfCommandNotFoundChanged(self):
#        config.regexSearchBibleIfCommandNotFound = not config.regexSearchBibleIfCommandNotFound
#        if config.regexSearchBibleIfCommandNotFound and not config.searchBibleIfCommandNotFound:
#            config.searchBibleIfCommandNotFound = True

    def overwriteNoteFontChanged(self):
        config.overwriteNoteFont = not config.overwriteNoteFont

    def overwriteNoteFontSizeChanged(self):
        config.overwriteNoteFontSize = not config.overwriteNoteFontSize

    def overwriteBookFontChanged(self):
        config.overwriteBookFont = not config.overwriteBookFont

    def useWebbrowserChanged(self):
        config.useWebbrowser = not config.useWebbrowser

    def removeHighlightOnExitChanged(self):
        config.removeHighlightOnExit = not config.removeHighlightOnExit

    def overwriteBookFontSizeChanged(self):
        config.overwriteBookFontSize = not config.overwriteBookFontSize

    def alwaysDisplayStaticMapsChanged(self):
        config.alwaysDisplayStaticMaps = not config.alwaysDisplayStaticMaps

    def openBibleNoteAfterSaveChanged(self):
        config.openBibleNoteAfterSave = not config.openBibleNoteAfterSave

    def addBreakAfterTheFirstToolBarChanged(self):
        config.addBreakAfterTheFirstToolBar = not config.addBreakAfterTheFirstToolBar
        self.parent.handleRestart()

    def addBreakBeforeTheLastToolBarChanged(self):
        config.addBreakBeforeTheLastToolBar = not config.addBreakBeforeTheLastToolBar
        self.parent.handleRestart()

    def disableModulesUpdateCheckChanged(self):
        config.disableModulesUpdateCheck = not config.disableModulesUpdateCheck

    def forceGenerateHtmlChanged(self):
        config.forceGenerateHtml = not config.forceGenerateHtml

    def parserStandarisationChanged(self):
        if config.parserStandarisation == "YES":
            config.parserStandarisation = "NO"
        else:
            config.parserStandarisation = "YES"

    def hideVlcInterfaceReadingSingleVerseChanged(self):
        config.hideVlcInterfaceReadingSingleVerse = not config.hideVlcInterfaceReadingSingleVerse

    def startFullScreenChanged(self):
        config.startFullScreen = not config.startFullScreen
        self.parent.handleRestart()

    def linuxStartFullScreenChanged(self):
        config.linuxStartFullScreen = not config.linuxStartFullScreen
        self.parent.handleRestart()

    def espeakChanged(self):
        config.espeak = not config.espeak
        self.parent.handleRestart()

    def piperChanged(self):
        config.piper = not config.piper
        self.parent.handleRestart()

    def forceOnlineTtsChanged(self):
        config.forceOnlineTts = not config.forceOnlineTts
        self.parent.handleRestart()

    def enableLoggingChanged(self):
        config.enableLogging = not config.enableLogging
        self.parent.handleRestart()

    def logCommandsChanged(self):
        config.logCommands = not config.logCommands

    def enableVerseHighlightingChanged(self):
        config.enableVerseHighlighting = not config.enableVerseHighlighting
        self.parent.handleRestart()

    def useLiteVerseParsingChanged(self):
        config.useLiteVerseParsing = not config.useLiteVerseParsing
    
    def parseEnglishBooksOnlyChanged(self):
        config.parseEnglishBooksOnly = not config.parseEnglishBooksOnly

    def enableMacrosChanged(self):
        config.enableMacros = not config.enableMacros
        self.parent.handleRestart()

    def enablePluginsChanged(self):
        config.enablePlugins = not config.enablePlugins
        self.parent.setupMenuLayout(config.menuLayout)

    def compareOnStudyWindowChanged(self):
        config.compareOnStudyWindow = not config.compareOnStudyWindow
        if not config.compareOnStudyWindow and config.syncAction in ("PARALLEL", "SIDEBYSIDE", "COMPARE"):
            config.syncAction = ""
        if config.menuLayout == "material":
            self.parent.setupMenuLayout("material")

    def usePySide2onWebtopChanged(self):
        config.usePySide2onWebtop = not config.usePySide2onWebtop
        self.parent.handleRestart()

    def usePySide6onMacOSChanged(self):
        config.usePySide6onMacOS = not config.usePySide6onMacOS
        self.parent.handleRestart()

    def clearCommandEntryChanged(self):
        config.clearCommandEntry = not config.clearCommandEntry

    def qtMaterialChanged(self):
        if not config.qtMaterial:
            self.parent.enableQtMaterial(True)
        else:
            self.parent.enableQtMaterial(False)

    def enableGistChanged(self):
        if not config.enableGist and ("Pygithub" in config.enabled):
            config.enableGist = True
            self.parent.handleRestart()
        elif config.enableGist:
            config.enableGist = not config.enableGist
            self.parent.handleRestart()
        else:
            self.displayMessage(config.thisTranslation["message_noSupport"])

    def hideBlankVerseCompareChanged(self):
        config.hideBlankVerseCompare = not config.hideBlankVerseCompare

    def enableMenuUnderlineChanged(self):
        config.enableMenuUnderline = not config.enableMenuUnderline
        if config.enableMenuUnderline:
            config.menuUnderline = "&"
        else:
            config.menuUnderline = ""
        self.parent.setupMenuLayout(config.menuLayout)

    def includeStrictDocTypeInNoteChanged(self):
        config.includeStrictDocTypeInNote = not config.includeStrictDocTypeInNote

    def parseTextConvertNotesToBookChanged(self):
        config.parseTextConvertNotesToBook = not config.parseTextConvertNotesToBook

    def parseTextConvertHTMLToBookChanged(self):
        config.parseTextConvertHTMLToBook = not config.parseTextConvertHTMLToBook

    def displayCmdOutputChanged(self):
        config.displayCmdOutput = not config.displayCmdOutput

    def disableLoadLastOpenFilesOnStartupChanged(self):
        config.disableLoadLastOpenFilesOnStartup = not config.disableLoadLastOpenFilesOnStartup

    def disableOpenPopupWindowOnStartupChanged(self):
        config.disableOpenPopupWindowOnStartup = not config.disableOpenPopupWindowOnStartup

    def showMiniKeyboardInMiniControlChanged(self):
        config.showMiniKeyboardInMiniControl = not config.showMiniKeyboardInMiniControl

    def refreshWindowsAfterSavingNoteChanged(self):
        config.refreshWindowsAfterSavingNote = not config.refreshWindowsAfterSavingNote

    def limitWorkspaceFilenameLengthChanged(self):
        config.limitWorkspaceFilenameLength = not config.limitWorkspaceFilenameLength

    def enableHttpRemoteErrorRedirection(self):
        config.enableHttpRemoteErrorRedirection = not config.enableHttpRemoteErrorRedirection
