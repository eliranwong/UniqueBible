import config, platform, webbrowser
from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QDialog, QLabel, QCheckBox

class MoreConfigOptions(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        #self.setModal(True)
        self.setWindowTitle(config.thisTranslation["menu_config_flags"])
        self.wikiLink = "https://github.com/eliranwong/UniqueBible/wiki/Config-file-reference"
        self.setupLayout()

    def flagToolTip(self, default, toolTip):
        return "{0} {1}\n{2}".format(config.thisTranslation["default"], default, config.thisTranslation[toolTip])

    def setupLayout(self):
        layout = QVBoxLayout()

        readWiki = QLabel(self.wikiLink)
        readWiki.mouseReleaseEvent = self.openWiki
        layout.addWidget(readWiki)

        horizontalContainer = QWidget()
        #horizontalContainer.setPalette(Themes.getPalette())
        horizontalContainerLayout = QHBoxLayout()

        options = [
            ("showControlPanelOnStartup", config.showControlPanelOnStartup, self.showControlPanelOnStartupChanged, self.flagToolTip(False, "showControlPanelOnStartup")),
            ("preferControlPanelForCommandLineEntry", config.preferControlPanelForCommandLineEntry, self.preferControlPanelForCommandLineEntryChanged, self.flagToolTip(False, "preferControlPanelForCommandLineEntry")),
            ("closeControlPanelAfterRunningCommand", config.closeControlPanelAfterRunningCommand, self.closeControlPanelAfterRunningCommandChanged, self.flagToolTip(True, "closeControlPanelAfterRunningCommand")),
            ("clearCommandEntry", config.clearCommandEntry, self.clearCommandEntryChanged, self.flagToolTip(False, "clearCommandEntry")),
            ("openBibleWindowContentOnNextTab", config.openBibleWindowContentOnNextTab, self.openBibleWindowContentOnNextTabChanged, self.flagToolTip(False, "openBibleWindowContentOnNextTab")),
            ("openStudyWindowContentOnNextTab", config.openStudyWindowContentOnNextTab, self.openStudyWindowContentOnNextTabChanged, self.flagToolTip(True, "openStudyWindowContentOnNextTab")),
            ("populateTabsOnStartup", config.populateTabsOnStartup, self.populateTabsOnStartupChanged, self.flagToolTip(False, "populateTabsOnStartup")), 
            ("qtMaterial", config.qtMaterial, self.qtMaterialChanged, self.flagToolTip(False, "qtMaterial")),
            ("addBreakAfterTheFirstToolBar", config.addBreakAfterTheFirstToolBar, self.addBreakAfterTheFirstToolBarChanged, self.flagToolTip(True, "addBreakAfterTheFirstToolBar")),
            ("addBreakBeforeTheLastToolBar", config.addBreakBeforeTheLastToolBar, self.addBreakBeforeTheLastToolBarChanged, self.flagToolTip(False, "addBreakBeforeTheLastToolBar")),
            ("parserStandarisation", (config.parserStandarisation == "YES"), self.parserStandarisationChanged, self.flagToolTip(False, "parserStandarisation")),
            ("useFastVerseParsing", config.useFastVerseParsing, self.useFastVerseParsingChanged, self.flagToolTip(False, "useFastVerseParsing")),
            ("preferHtmlMenu", config.preferHtmlMenu, self.preferHtmlMenuChanged, self.flagToolTip(False, "preferHtmlMenu")),
            ("showVerseNumbersInRange", config.showVerseNumbersInRange, self.showVerseNumbersInRangeChanged, self.flagToolTip(True, "showVerseNumbersInRange")),
            ("addFavouriteToMultiRef", config.addFavouriteToMultiRef, self.addFavouriteToMultiRefChanged, self.flagToolTip(False, "addFavouriteToMultiRef")),
            ("enableVerseHighlighting", config.enableVerseHighlighting, self.enableVerseHighlightingChanged, self.flagToolTip(False, "enableVerseHighlighting")),
            ("regexCaseSensitive", config.regexCaseSensitive, self.regexCaseSensitiveChanged, self.flagToolTip(False, "regexCaseSensitive")),
            ("alwaysDisplayStaticMaps", config.alwaysDisplayStaticMaps, self.alwaysDisplayStaticMapsChanged, self.flagToolTip(False, "alwaysDisplayStaticMaps")),
            ("exportEmbeddedImages", config.exportEmbeddedImages, self.exportEmbeddedImagesChanged, self.flagToolTip(True, "exportEmbeddedImages")),
            ("clickToOpenImage", config.clickToOpenImage, self.clickToOpenImageChanged, self.flagToolTip(True, "clickToOpenImage")),
            ("showNoteIndicatorOnBibleChapter", config.showNoteIndicatorOnBibleChapter, self.parent.enableNoteIndicatorButtonClicked, self.flagToolTip(True, "showNoteIndicatorOnBibleChapter")),
            ("openBibleNoteAfterSave", config.openBibleNoteAfterSave, self.openBibleNoteAfterSaveChanged, self.flagToolTip(False, "openBibleNoteAfterSave")),
            ("openBibleNoteAfterEditorClosed", config.openBibleNoteAfterEditorClosed, self.openBibleNoteAfterEditorClosedChanged, self.flagToolTip(False, "openBibleNoteAfterEditorClosed")),
            ("hideNoteEditorStyleToolbar", config.hideNoteEditorStyleToolbar, self.hideNoteEditorStyleToolbarChanged, self.flagToolTip(False, "hideNoteEditorStyleToolbar")),
            ("hideNoteEditorTextUtility", config.hideNoteEditorTextUtility, self.hideNoteEditorTextUtilityChanged, self.flagToolTip(True, "hideNoteEditorTextUtility")),
            ("overwriteNoteFont", config.overwriteNoteFont, self.overwriteNoteFontChanged, self.flagToolTip(True, "overwriteNoteFont")),
            ("overwriteNoteFontSize", config.overwriteNoteFontSize, self.overwriteNoteFontSizeChanged, self.flagToolTip(True, "overwriteNoteFontSize")),
            ("overwriteBookFont", config.overwriteBookFont, self.overwriteBookFontChanged, self.flagToolTip(True, "overwriteBookFont")),
            ("overwriteBookFontSize", config.overwriteBookFontSize, self.overwriteBookFontSizeChanged, self.flagToolTip(True, "overwriteBookFontSize")),
            ("bookOnNewWindow", config.bookOnNewWindow, self.bookOnNewWindowChanged, self.flagToolTip(False, "bookOnNewWindow")),
            ("virtualKeyboard", config.virtualKeyboard, self.virtualKeyboardChanged, self.flagToolTip(False, "virtualKeyboard")),
            ("autoCopyTranslateResult", config.autoCopyTranslateResult, self.autoCopyTranslateResultChanged, self.flagToolTip(True, "autoCopyTranslateResult")),
            ("autoCopyChinesePinyinOutput", config.autoCopyChinesePinyinOutput, self.autoCopyChinesePinyinOutputChanged, self.flagToolTip(True, "autoCopyChinesePinyinOutput")),
            ("useWebbrowser", config.useWebbrowser, self.useWebbrowserChanged, self.flagToolTip(True, "useWebbrowser")),
            ("removeHighlightOnExit", config.removeHighlightOnExit, self.removeHighlightOnExitChanged, self.flagToolTip(False, "removeHighlightOnExit")),
            ("disableModulesUpdateCheck", config.disableModulesUpdateCheck, self.disableModulesUpdateCheckChanged, self.flagToolTip(True, "disableModulesUpdateCheck")),
            ("enableGist", config.enableGist, self.enableGistChanged, self.flagToolTip(False, "enableGist")),
            ("enableMacros", config.enableMacros, self.enableMacrosChanged, self.flagToolTip(False, "enableMacros")),
            ("enablePlugins", config.enablePlugins, self.enablePluginsChanged, self.flagToolTip(True, "enablePlugins")),
            #("customPythonOnStartup", config.customPythonOnStartup, self.customPythonOnStartupChanged, self.flagToolTip(False, "customPythonOnStartup")),
        ]
        if config.isTtsInstalled:
            options += [
                ("useLangDetectOnTts", config.useLangDetectOnTts, self.useLangDetectOnTtsChanged, self.flagToolTip(False, "useLangDetectOnTts")),
                ("ttsEnglishAlwaysUS", config.ttsEnglishAlwaysUS, self.ttsEnglishAlwaysUSChanged, self.flagToolTip(False, "ttsEnglishAlwaysUS")),
                ("ttsEnglishAlwaysUK", config.ttsEnglishAlwaysUK, self.ttsEnglishAlwaysUKChanged, self.flagToolTip(False, "ttsEnglishAlwaysUK")),
                ("ttsChineseAlwaysMandarin", config.ttsChineseAlwaysMandarin, self.ttsChineseAlwaysMandarinChanged, self.flagToolTip(False, "ttsChineseAlwaysMandarin")),
                ("ttsChineseAlwaysCantonese", config.ttsChineseAlwaysCantonese, self.ttsChineseAlwaysCantoneseChanged, self.flagToolTip(False, "ttsChineseAlwaysCantonese")),
            ]
        if platform.system() == "Linux":
            options += [
                ("linuxStartFullScreen", config.linuxStartFullScreen, self.linuxStartFullScreenChanged, self.flagToolTip(False, "linuxStartFullScreen")),
                ("fcitx", config.fcitx, self.fcitxChanged, self.flagToolTip(False, "fcitx")),
                ("ibus", config.ibus, self.ibusChanged, self.flagToolTip(False, "ibus")),
                ("espeak", config.espeak, self.espeakChanged, self.flagToolTip(False, "espeak")),
            ]
        if config.developer:
            options += [
                ("enableCopyHtmlCommand", config.enableCopyHtmlCommand, self.enableCopyHtmlCommandChanged, self.flagToolTip(False, "enableCopyHtmlCommand")),
                ("forceGenerateHtml", config.forceGenerateHtml, self.forceGenerateHtmlChanged, self.flagToolTip(False, "forceGenerateHtml")),
                ("enableLogging", config.enableLogging, self.enableLoggingChanged, self.flagToolTip(False, "enableLogging")),
                ("logCommands", config.logCommands, self.logCommandsChanged, self.flagToolTip(False, "logCommands")),
            ]

        columns = (QVBoxLayout(), QVBoxLayout(), QVBoxLayout(), QVBoxLayout())

        counter = 0
        for content in options:
            name, value, function, toolTip = content
            checkbox = QCheckBox()
            checkbox.setText(name)
            checkbox.setChecked(value)
            checkbox.stateChanged.connect(function)
            checkbox.setToolTip(toolTip)

            columns[counter].addWidget(checkbox)
            if counter == len(columns) - 1:
                counter = 0
            else:
                counter += 1

        for column in columns:
            column.addStretch()
            horizontalContainerLayout.addLayout(column)
        horizontalContainer.setLayout(horizontalContainerLayout)
        layout.addWidget(horizontalContainer)
        self.setLayout(layout)

    def openWiki(self, event):
        webbrowser.open(self.wikiLink)

    def ibusChanged(self):
        config.ibus = not config.ibus
        if config.fcitx and config.ibus:
            config.fcitx = not config.fcitx
        if config.virtualKeyboard and config.ibus:
            config.virtualKeyboard = not config.virtualKeyboard
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def fcitxChanged(self):
        config.fcitx = not config.fcitx
        if config.fcitx and config.ibus:
            config.ibus = not config.ibus
        if config.fcitx and config.virtualKeyboard:
            config.virtualKeyboard = not config.virtualKeyboard
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def virtualKeyboardChanged(self):
        config.virtualKeyboard = not config.virtualKeyboard
        if config.fcitx and config.virtualKeyboard:
            config.fcitx = not config.fcitx
        if config.virtualKeyboard and config.ibus:
            config.ibus = not config.ibus
        self.parent.displayMessage(config.thisTranslation["message_restart"])

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

    def ttsChineseAlwaysCantoneseChanged(self):
        config.ttsChineseAlwaysCantonese = not config.ttsChineseAlwaysCantonese
        if config.ttsChineseAlwaysMandarin and config.ttsChineseAlwaysCantonese:
            config.ttsChineseAlwaysMandarin = not config.ttsChineseAlwaysMandarin

    def showVerseNumbersInRangeChanged(self):
        config.showVerseNumbersInRange = not config.showVerseNumbersInRange

    #def customPythonOnStartupChanged(self):
    #    config.customPythonOnStartup = not config.customPythonOnStartup

    def openBibleWindowContentOnNextTabChanged(self):
        config.openBibleWindowContentOnNextTab = not config.openBibleWindowContentOnNextTab
        self.newTabException = False

    def showControlPanelOnStartupChanged(self):
        config.showControlPanelOnStartup = not config.showControlPanelOnStartup
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def preferControlPanelForCommandLineEntryChanged(self):
        config.preferControlPanelForCommandLineEntry = not config.preferControlPanelForCommandLineEntry
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def closeControlPanelAfterRunningCommandChanged(self):
        config.closeControlPanelAfterRunningCommand = not config.closeControlPanelAfterRunningCommand

    def regexCaseSensitiveChanged(self):
        config.regexCaseSensitive = not config.regexCaseSensitive

    def openStudyWindowContentOnNextTabChanged(self):
        config.openStudyWindowContentOnNextTab = not config.openStudyWindowContentOnNextTab
        self.newTabException = False

    def addFavouriteToMultiRefChanged(self):
        config.addFavouriteToMultiRef = not config.addFavouriteToMultiRef

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

    def bookOnNewWindowChanged(self):
        config.bookOnNewWindow = not config.bookOnNewWindow

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
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def addBreakBeforeTheLastToolBarChanged(self):
        config.addBreakBeforeTheLastToolBar = not config.addBreakBeforeTheLastToolBar
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def autoCopyTranslateResultChanged(self):
        config.autoCopyTranslateResult = not config.autoCopyTranslateResult

    def autoCopyChinesePinyinOutputChanged(self):
        config.autoCopyChinesePinyinOutput = not config.autoCopyChinesePinyinOutput

    def disableModulesUpdateCheckChanged(self):
        config.disableModulesUpdateCheck = not config.disableModulesUpdateCheck

    def enableCopyHtmlCommandChanged(self):
        config.enableCopyHtmlCommand = not config.enableCopyHtmlCommand
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def forceGenerateHtmlChanged(self):
        config.forceGenerateHtml = not config.forceGenerateHtml

    def parserStandarisationChanged(self):
        if config.parserStandarisation == "YES":
            config.parserStandarisation = "NO"
        else:
            config.parserStandarisation = "YES"

    def linuxStartFullScreenChanged(self):
        config.linuxStartFullScreen = not config.linuxStartFullScreen
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def espeakChanged(self):
        config.espeak = not config.espeak

    def enableLoggingChanged(self):
        config.enableLogging = not config.enableLogging
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def logCommandsChanged(self):
        config.logCommands = not config.logCommands

    def enableVerseHighlightingChanged(self):
        config.enableVerseHighlighting = not config.enableVerseHighlighting
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def useFastVerseParsingChanged(self):
        config.useFastVerseParsing = not config.useFastVerseParsing

    def enableMacrosChanged(self):
        config.enableMacros = not config.enableMacros
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def enablePluginsChanged(self):
        config.enablePlugins = not config.enablePlugins
        self.parent.setMenuLayout(config.menuLayout)

    def clearCommandEntryChanged(self):
        config.clearCommandEntry = not config.clearCommandEntry

    def qtMaterialChanged(self):
        if not config.qtMaterial:
            self.parent.enableQtMaterial(True)
        else:
            self.parent.enableQtMaterial(False)

    def enableGistChanged(self):
        if not config.enableGist and config.isPygithubInstalled:
            config.enableGist = True
            self.parent.displayMessage(config.thisTranslation["message_restart"])            
        elif config.enableGist:
            config.enableGist = not config.enableGist
            self.parent.displayMessage(config.thisTranslation["message_restart"])
        else:
            self.parent.displayMessage(config.thisTranslation["message_noSupport"])
