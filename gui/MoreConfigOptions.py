import config, platform
from PySide2.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QDialog, QLabel, QCheckBox)

from BibleVerseParser import BibleVerseParser
from themes import Themes

class MoreConfigOptions(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        #self.setModal(True)
        self.setWindowTitle(config.thisTranslation["menu1_moreConfig"])
        self.setupLayout()

    def setupLayout(self):
        layout = QVBoxLayout()

        readWiki = QLabel(config.thisTranslation["message_readWiki"])
        layout.addWidget(readWiki)
        readWiki = QLabel("https://github.com/eliranwong/UniqueBible/wiki/config_file")
        layout.addWidget(readWiki)

        horizontalContainer = QWidget()
        horizontalContainer.setPalette(Themes.getPalette())
        horizontalContainerLayout = QHBoxLayout()

        leftContainer = QWidget()
        leftContainerLayout = QVBoxLayout()
        rightContainer = QWidget()
        rightContainerLayout = QVBoxLayout()

        options = [
            ("openBibleWindowContentOnNextTab", config.openBibleWindowContentOnNextTab, self.openBibleWindowContentOnNextTabChanged),
            ("openStudyWindowContentOnNextTab", config.openStudyWindowContentOnNextTab, self.openStudyWindowContentOnNextTabChanged),
            ("addBreakAfterTheFirstToolBar", config.addBreakAfterTheFirstToolBar, self.addBreakAfterTheFirstToolBarChanged),
            ("addBreakBeforeTheLastToolBar", config.addBreakBeforeTheLastToolBar, self.addBreakBeforeTheLastToolBarChanged),
            ("preferControlPanelForCommandLineEntry", config.preferControlPanelForCommandLineEntry, self.preferControlPanelForCommandLineEntryChanged),
            ("closeControlPanelAfterRunningCommand", config.closeControlPanelAfterRunningCommand, self.closeControlPanelAfterRunningCommandChanged),
            ("showVerseNumbersInRange", config.showVerseNumbersInRange, self.showVerseNumbersInRangeChanged),
            ("addFavouriteToMultiRef", config.addFavouriteToMultiRef, self.addFavouriteToMultiRefChanged),
            ("alwaysDisplayStaticMaps", config.alwaysDisplayStaticMaps, self.alwaysDisplayStaticMapsChanged),
            ("exportEmbeddedImages", config.exportEmbeddedImages, self.exportEmbeddedImagesChanged),
            ("showNoteIndicatorOnBibleChapter", config.showNoteIndicatorOnBibleChapter, self.parent.enableNoteIndicatorButtonClicked),
            ("clickToOpenImage", config.clickToOpenImage, self.clickToOpenImageChanged),
            ("overwriteNoteFont", config.overwriteNoteFont, self.overwriteNoteFontChanged),
            ("overwriteBookFont", config.overwriteBookFont, self.overwriteBookFontChanged),
            ("overwriteNoteFontSize", config.overwriteNoteFontSize, self.overwriteNoteFontSizeChanged),
            ("overwriteBookFontSize", config.overwriteBookFontSize, self.overwriteBookFontSizeChanged),
            ("openBibleNoteAfterSave", config.openBibleNoteAfterSave, self.openBibleNoteAfterSaveChanged),
            ("bookOnNewWindow", config.bookOnNewWindow, self.bookOnNewWindowChanged),
            ("parserStandarisation", (config.parserStandarisation == "YES"), self.parserStandarisationChanged),
            ("virtualKeyboard", config.virtualKeyboard, self.virtualKeyboardChanged),
            ("showGoogleTranslateEnglishOptions", config.showGoogleTranslateEnglishOptions, self.showGoogleTranslateEnglishOptionsChanged),
            ("autoCopyGoogleTranslateOutput", config.autoCopyGoogleTranslateOutput, self.autoCopyGoogleTranslateOutputChanged),
            ("showGoogleTranslateChineseOptions", config.showGoogleTranslateChineseOptions, self.showGoogleTranslateChineseOptionsChanged),
            ("autoCopyChinesePinyinOutput", config.autoCopyChinesePinyinOutput, self.autoCopyChinesePinyinOutputChanged),
            ("disableModulesUpdateCheck", config.disableModulesUpdateCheck, self.disableModulesUpdateCheckChanged),
            ("enableCopyHtmlCommand", config.enableCopyHtmlCommand, self.enableCopyHtmlCommandChanged),
            ("forceGenerateHtml", config.forceGenerateHtml, self.forceGenerateHtmlChanged),
            ("logCommands", config.logCommands, self.logCommandsChanged),
            ("enableVerseHighlighting", config.enableVerseHighlighting, self.enableVerseHighlightingChanged),
            ("useFastVerseParsing", config.useFastVerseParsing, self.useFastVerseParsingChanged),
            ("enableMacros", config.enableMacros, self.enableMacrosChanged)
        ]
        if platform.system() == "Linux":
            options += [
                ("linuxStartFullScreen", config.linuxStartFullScreen, self.linuxStartFullScreenChanged),
                ("showTtsOnLinux", config.showTtsOnLinux, self.showTtsOnLinuxChanged),
                ("espeak", config.espeak, self.espeakChanged),
                ("fcitx", config.fcitx, self.fcitxChanged),
                ("ibus", config.ibus, self.ibusChanged),
            ]
        for counter, content in enumerate(options):
            name, value, function = content
            checkbox = QCheckBox()
            checkbox.setText(name)
            checkbox.setChecked(value)
            checkbox.stateChanged.connect(function)
            if counter % 2 == 0:
                leftContainerLayout.addWidget(checkbox)
            else:
                rightContainerLayout.addWidget(checkbox)

        leftContainer.setLayout(leftContainerLayout)
        rightContainer.setLayout(rightContainerLayout)
        horizontalContainerLayout.addWidget(leftContainer)
        horizontalContainerLayout.addWidget(rightContainer)
        horizontalContainer.setLayout(horizontalContainerLayout)
        layout.addWidget(horizontalContainer)
        self.setLayout(layout)

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

    def showVerseNumbersInRangeChanged(self):
        config.showVerseNumbersInRange = not config.showVerseNumbersInRange

    def openBibleWindowContentOnNextTabChanged(self):
        config.openBibleWindowContentOnNextTab = not config.openBibleWindowContentOnNextTab
        self.newTabException = False

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
