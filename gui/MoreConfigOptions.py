import webbrowser

import config, platform
from PySide2.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QDialog, QLabel, QCheckBox)

class MoreConfigOptions(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        #self.setModal(True)
        self.setWindowTitle(config.thisTranslation["menu_config_flags"])
        self.wikiLink = "https://github.com/eliranwong/UniqueBible/wiki/Config-file-reference"
        self.setupLayout()

    def setupLayout(self):
        layout = QVBoxLayout()

        readWiki = QLabel(config.thisTranslation["message_readWiki"])
        layout.addWidget(readWiki)
        readWiki = QLabel(self.wikiLink)
        readWiki.mouseReleaseEvent = self.openWiki
        layout.addWidget(readWiki)

        horizontalContainer = QWidget()
        #horizontalContainer.setPalette(Themes.getPalette())
        horizontalContainerLayout = QHBoxLayout()

        leftContainer = QWidget()
        leftContainerLayout = QVBoxLayout()
        middleContainer = QWidget()
        middleContainerLayout = QVBoxLayout()
        rightContainer = QWidget()
        rightContainerLayout = QVBoxLayout()

        options = [
            ("openBibleWindowContentOnNextTab", config.openBibleWindowContentOnNextTab, self.openBibleWindowContentOnNextTabChanged, ""),
            ("openStudyWindowContentOnNextTab", config.openStudyWindowContentOnNextTab, self.openStudyWindowContentOnNextTabChanged, ""),
            ("addBreakAfterTheFirstToolBar", config.addBreakAfterTheFirstToolBar, self.addBreakAfterTheFirstToolBarChanged, ""),
            ("addBreakBeforeTheLastToolBar", config.addBreakBeforeTheLastToolBar, self.addBreakBeforeTheLastToolBarChanged, ""),
            ("showControlPanelOnStartup", config.showControlPanelOnStartup, self.showControlPanelOnStartupChanged, ""),
            ("preferControlPanelForCommandLineEntry", config.preferControlPanelForCommandLineEntry, self.preferControlPanelForCommandLineEntryChanged, "Default: False \nTurn it on to hide the toolbar command field on the main window. \nWhen a command prefix is prompted to add to the command field, control panel is opned with command prefix in its command field."),
            ("closeControlPanelAfterRunningCommand", config.closeControlPanelAfterRunningCommand, self.closeControlPanelAfterRunningCommandChanged, "Default: True \nTurn it on to hide Master Control panel each time when a command is executed from it. \nIt is designed to save time from manually closing control panel and go straight to the selected resource. \nUsers can easily call the Control Panel back to screen with shortcuts, like 'Ctrl+B', 'Ctrl+L', 'Ctrl+F' and 'Ctrl+H'."),
            ("qtMaterial", config.qtMaterial, self.qtMaterialChanged, ""),
            ("showVerseNumbersInRange", config.showVerseNumbersInRange, self.showVerseNumbersInRangeChanged, ""),
            ("addFavouriteToMultiRef", config.addFavouriteToMultiRef, self.addFavouriteToMultiRefChanged, ""),
            ("alwaysDisplayStaticMaps", config.alwaysDisplayStaticMaps, self.alwaysDisplayStaticMapsChanged, ""),
            ("exportEmbeddedImages", config.exportEmbeddedImages, self.exportEmbeddedImagesChanged, ""),
            ("showNoteIndicatorOnBibleChapter", config.showNoteIndicatorOnBibleChapter, self.parent.enableNoteIndicatorButtonClicked, ""),
            ("clickToOpenImage", config.clickToOpenImage, self.clickToOpenImageChanged, ""),
            ("overwriteNoteFont", config.overwriteNoteFont, self.overwriteNoteFontChanged, ""),
            ("overwriteBookFont", config.overwriteBookFont, self.overwriteBookFontChanged, ""),
            ("overwriteNoteFontSize", config.overwriteNoteFontSize, self.overwriteNoteFontSizeChanged, ""),
            ("overwriteBookFontSize", config.overwriteBookFontSize, self.overwriteBookFontSizeChanged, ""),
            ("openBibleNoteAfterSave", config.openBibleNoteAfterSave, self.openBibleNoteAfterSaveChanged, ""),
            ("bookOnNewWindow", config.bookOnNewWindow, self.bookOnNewWindowChanged, ""),
            ("parserStandarisation", (config.parserStandarisation == "YES"), self.parserStandarisationChanged, ""),
            ("virtualKeyboard", config.virtualKeyboard, self.virtualKeyboardChanged, ""),
            ("showGoogleTranslateEnglishOptions", config.showGoogleTranslateEnglishOptions, self.showGoogleTranslateEnglishOptionsChanged, ""),
            ("autoCopyGoogleTranslateOutput", config.autoCopyGoogleTranslateOutput, self.autoCopyGoogleTranslateOutputChanged, ""),
            ("showGoogleTranslateChineseOptions", config.showGoogleTranslateChineseOptions, self.showGoogleTranslateChineseOptionsChanged, ""),
            ("autoCopyChinesePinyinOutput", config.autoCopyChinesePinyinOutput, self.autoCopyChinesePinyinOutputChanged, ""),
            ("disableModulesUpdateCheck", config.disableModulesUpdateCheck, self.disableModulesUpdateCheckChanged, ""),
            ("enableCopyHtmlCommand", config.enableCopyHtmlCommand, self.enableCopyHtmlCommandChanged, ""),
            ("forceGenerateHtml", config.forceGenerateHtml, self.forceGenerateHtmlChanged, ""),
            ("enableLogging", config.enableLogging, self.enableLoggingChanged, ""),
            ("logCommands", config.logCommands, self.logCommandsChanged, ""),
            ("enableVerseHighlighting", config.enableVerseHighlighting, self.enableVerseHighlightingChanged, ""),
            ("useFastVerseParsing", config.useFastVerseParsing, self.useFastVerseParsingChanged, ""),
            ("enableMacros", config.enableMacros, self.enableMacrosChanged, ""),
            ("enableGist", config.enableGist, self.enableGistChanged, ""),
            ("clearCommandEntry", config.clearCommandEntry, self.clearCommandEntryChanged, "")
        ]
        if platform.system() == "Linux":
            options += [
                ("linuxStartFullScreen", config.linuxStartFullScreen, self.linuxStartFullScreenChanged, ""),
                ("fcitx", config.fcitx, self.fcitxChanged, ""),
                ("ibus", config.ibus, self.ibusChanged, ""),
                ("showTtsOnLinux", config.showTtsOnLinux, self.showTtsOnLinuxChanged, ""),
                ("espeak", config.espeak, self.espeakChanged, ""),
            ]
        if config.ttsSupport:
            options += [
                ("ttsEnglishAlwaysUS", config.ttsEnglishAlwaysUS, self.ttsEnglishAlwaysUSChanged, ""),
                ("ttsEnglishAlwaysUK", config.ttsEnglishAlwaysUK, self.ttsEnglishAlwaysUKChanged, ""),
                ("ttsChineseAlwaysMandarin", config.ttsChineseAlwaysMandarin, self.ttsChineseAlwaysMandarinChanged, ""),
                ("ttsChineseAlwaysCantonese", config.ttsChineseAlwaysCantonese, self.ttsChineseAlwaysCantoneseChanged, ""),
            ]

        counter = 0
        for content in options:
            name, value, function, toolTip = content
            checkbox = QCheckBox()
            checkbox.setText(name)
            checkbox.setChecked(value)
            checkbox.stateChanged.connect(function)
            checkbox.setToolTip(toolTip)
            if (counter == 0):
                leftContainerLayout.addWidget(checkbox)
                counter += 1
            elif (counter == 1):
                middleContainerLayout.addWidget(checkbox)
                counter += 1
            elif (counter == 2):
                rightContainerLayout.addWidget(checkbox)
                counter = 0

        leftContainerLayout.addStretch()
        middleContainerLayout.addStretch()
        rightContainerLayout.addStretch()

        leftContainer.setLayout(leftContainerLayout)
        middleContainer.setLayout(middleContainerLayout)
        rightContainer.setLayout(rightContainerLayout)
        horizontalContainerLayout.addWidget(leftContainer)
        horizontalContainerLayout.addWidget(middleContainer)
        horizontalContainerLayout.addWidget(rightContainer)
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

    def openStudyWindowContentOnNextTabChanged(self):
        config.openStudyWindowContentOnNextTab = not config.openStudyWindowContentOnNextTab
        self.newTabException = False

    def addFavouriteToMultiRefChanged(self):
        config.addFavouriteToMultiRef = not config.addFavouriteToMultiRef

    def exportEmbeddedImagesChanged(self):
        config.exportEmbeddedImages = not config.exportEmbeddedImages

    def clickToOpenImageChanged(self):
        config.clickToOpenImage = not config.clickToOpenImage

    def bookOnNewWindowChanged(self):
        config.bookOnNewWindow = not config.bookOnNewWindow

    def overwriteNoteFontChanged(self):
        config.overwriteNoteFont = not config.overwriteNoteFont

    def overwriteNoteFontSizeChanged(self):
        config.overwriteNoteFontSize = not config.overwriteNoteFontSize

    def overwriteBookFontChanged(self):
        config.overwriteBookFont = not config.overwriteBookFont

    def overwriteBookFontSizeChanged(self):
        config.overwriteBookFontSize = not config.overwriteBookFontSize

    def alwaysDisplayStaticMapsChanged(self):
        config.alwaysDisplayStaticMaps = not config.alwaysDisplayStaticMaps

    def openBibleNoteAfterSaveChanged(self):
        config.openBibleNoteAfterSave = not config.openBibleNoteAfterSave

    def showGoogleTranslateEnglishOptionsChanged(self):
        config.showGoogleTranslateEnglishOptions = not config.showGoogleTranslateEnglishOptions
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def addBreakAfterTheFirstToolBarChanged(self):
        config.addBreakAfterTheFirstToolBar = not config.addBreakAfterTheFirstToolBar
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def addBreakBeforeTheLastToolBarChanged(self):
        config.addBreakBeforeTheLastToolBar = not config.addBreakBeforeTheLastToolBar
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def showGoogleTranslateChineseOptionsChanged(self):
        config.showGoogleTranslateChineseOptions = not config.showGoogleTranslateChineseOptions
        self.parent.displayMessage(config.thisTranslation["message_restart"])

    def autoCopyGoogleTranslateOutputChanged(self):
        config.autoCopyGoogleTranslateOutput = not config.autoCopyGoogleTranslateOutput

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

    def showTtsOnLinuxChanged(self):
        config.showTtsOnLinux = not config.showTtsOnLinux
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

    def clearCommandEntryChanged(self):
        config.clearCommandEntry = not config.clearCommandEntry

    def qtMaterialChanged(self):
        if not config.qtMaterial:
            self.parent.enableQtMaterial(True)
        else:
            self.parent.enableQtMaterial(False)

    def enableGistChanged(self):
        if not config.enableGist:
            try:
                from github import Github, InputFileContent
                config.enableGist = True
                self.parent.displayMessage(config.thisTranslation["message_restart"])
            except:
                self.parent.displayMessage(config.thisTranslation["installPygithub"])
        else:
            config.enableGist = not config.enableGist
            self.parent.displayMessage(config.thisTranslation["message_restart"])
