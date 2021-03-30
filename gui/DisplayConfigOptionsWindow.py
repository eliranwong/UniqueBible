import operator
import sys
import webbrowser

import config
import platform

from qtpy.QtCore import QAbstractTableModel, Qt
from qtpy import QtCore, QtWidgets
from qtpy.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QTableView, QInputDialog, QLineEdit, \
    QLabel


class DisplayConfigOptionsWindow(QDialog):

    def __init__(self, parent):
        super(DisplayConfigOptionsWindow, self).__init__()

        self.parent = parent
        self.setWindowTitle(config.thisTranslation["menu_config_flags"])
        self.setMinimumWidth(370)
        self.setMinimumHeight(600)

        options = [
            ["showControlPanelOnStartup", config.showControlPanelOnStartup, self.showControlPanelOnStartupChanged, self.flagToolTip(False, "showControlPanelOnStartup")],
            ["preferControlPanelForCommandLineEntry", config.preferControlPanelForCommandLineEntry, self.preferControlPanelForCommandLineEntryChanged, self.flagToolTip(False, "preferControlPanelForCommandLineEntry")],
            ["closeControlPanelAfterRunningCommand", config.closeControlPanelAfterRunningCommand, self.closeControlPanelAfterRunningCommandChanged, self.flagToolTip(True, "closeControlPanelAfterRunningCommand")],
            ["restrictControlPanelWidth", config.restrictControlPanelWidth, self.restrictControlPanelWidthChanged, self.flagToolTip(False, "restrictControlPanelWidth")],
            ["clearCommandEntry", config.clearCommandEntry, self.clearCommandEntryChanged, self.flagToolTip(False, "clearCommandEntry")],
            ["openBibleWindowContentOnNextTab", config.openBibleWindowContentOnNextTab, self.openBibleWindowContentOnNextTabChanged, self.flagToolTip(False, "openBibleWindowContentOnNextTab")],
            ["openStudyWindowContentOnNextTab", config.openStudyWindowContentOnNextTab, self.openStudyWindowContentOnNextTabChanged, self.flagToolTip(True, "openStudyWindowContentOnNextTab")],
            ["populateTabsOnStartup", config.populateTabsOnStartup, self.populateTabsOnStartupChanged, self.flagToolTip(False, "populateTabsOnStartup")],
            ["qtMaterial", config.qtMaterial, self.qtMaterialChanged, self.flagToolTip(False, "qtMaterial")],
            ["addBreakAfterTheFirstToolBar", config.addBreakAfterTheFirstToolBar, self.addBreakAfterTheFirstToolBarChanged, self.flagToolTip(True, "addBreakAfterTheFirstToolBar")],
            ["addBreakBeforeTheLastToolBar", config.addBreakBeforeTheLastToolBar, self.addBreakBeforeTheLastToolBarChanged, self.flagToolTip(False, "addBreakBeforeTheLastToolBar")],
            ["parserStandarisation", (config.parserStandarisation == "YES"), self.parserStandarisationChanged, self.flagToolTip(False, "parserStandarisation")],
            ["useFastVerseParsing", config.useFastVerseParsing, self.useFastVerseParsingChanged, self.flagToolTip(False, "useFastVerseParsing")],
            ["preferHtmlMenu", config.preferHtmlMenu, self.preferHtmlMenuChanged, self.flagToolTip(False, "preferHtmlMenu")],
            ["showVerseNumbersInRange", config.showVerseNumbersInRange, self.showVerseNumbersInRangeChanged, self.flagToolTip(True, "showVerseNumbersInRange")],
            ["addFavouriteToMultiRef", config.addFavouriteToMultiRef, self.addFavouriteToMultiRefChanged, self.flagToolTip(False, "addFavouriteToMultiRef")],
            ["enableVerseHighlighting", config.enableVerseHighlighting, self.enableVerseHighlightingChanged, self.flagToolTip(False, "enableVerseHighlighting")],
            ["regexCaseSensitive", config.regexCaseSensitive, self.regexCaseSensitiveChanged, self.flagToolTip(False, "regexCaseSensitive")],
            ["alwaysDisplayStaticMaps", config.alwaysDisplayStaticMaps, self.alwaysDisplayStaticMapsChanged, self.flagToolTip(False, "alwaysDisplayStaticMaps")],
            ["exportEmbeddedImages", config.exportEmbeddedImages, self.exportEmbeddedImagesChanged, self.flagToolTip(True, "exportEmbeddedImages")],
            ["clickToOpenImage", config.clickToOpenImage, self.clickToOpenImageChanged, self.flagToolTip(True, "clickToOpenImage")],
            ["showNoteIndicatorOnBibleChapter", config.showNoteIndicatorOnBibleChapter, self.parent.enableNoteIndicatorButtonClicked, self.flagToolTip(True, "showNoteIndicatorOnBibleChapter")],
            ["openBibleNoteAfterSave", config.openBibleNoteAfterSave, self.openBibleNoteAfterSaveChanged, self.flagToolTip(False, "openBibleNoteAfterSave")],
            ["openBibleNoteAfterEditorClosed", config.openBibleNoteAfterEditorClosed, self.openBibleNoteAfterEditorClosedChanged, self.flagToolTip(False, "openBibleNoteAfterEditorClosed")],
            ["hideNoteEditorStyleToolbar", config.hideNoteEditorStyleToolbar, self.hideNoteEditorStyleToolbarChanged, self.flagToolTip(False, "hideNoteEditorStyleToolbar")],
            ["hideNoteEditorTextUtility", config.hideNoteEditorTextUtility, self.hideNoteEditorTextUtilityChanged, self.flagToolTip(True, "hideNoteEditorTextUtility")],
            ["overwriteNoteFont", config.overwriteNoteFont, self.overwriteNoteFontChanged, self.flagToolTip(True, "overwriteNoteFont")],
            ["overwriteNoteFontSize", config.overwriteNoteFontSize, self.overwriteNoteFontSizeChanged, self.flagToolTip(True, "overwriteNoteFontSize")],
            ["overwriteBookFont", config.overwriteBookFont, self.overwriteBookFontChanged, self.flagToolTip(True, "overwriteBookFont")],
            ["overwriteBookFontSize", config.overwriteBookFontSize, self.overwriteBookFontSizeChanged, self.flagToolTip(True, "overwriteBookFontSize")],
            ["bookOnNewWindow", config.bookOnNewWindow, self.bookOnNewWindowChanged, self.flagToolTip(False, "bookOnNewWindow")],
            ["virtualKeyboard", config.virtualKeyboard, self.virtualKeyboardChanged, self.flagToolTip(False, "virtualKeyboard")],
            ["useWebbrowser", config.useWebbrowser, self.useWebbrowserChanged, self.flagToolTip(True, "useWebbrowser")],
            ["removeHighlightOnExit", config.removeHighlightOnExit, self.removeHighlightOnExitChanged, self.flagToolTip(False, "removeHighlightOnExit")],
            ["disableModulesUpdateCheck", config.disableModulesUpdateCheck, self.disableModulesUpdateCheckChanged, self.flagToolTip(True, "disableModulesUpdateCheck")],
            ["enableGist", config.enableGist, self.enableGistChanged, self.flagToolTip(False, "enableGist")],
            ["enableMacros", config.enableMacros, self.enableMacrosChanged, self.flagToolTip(False, "enableMacros")],
            ["enablePlugins", config.enablePlugins, self.enablePluginsChanged, self.flagToolTip(True, "enablePlugins")],
            ["hideBlankVerseCompare", config.hideBlankVerseCompare, self.hideBlankVerseCompareChanged, self.flagToolTip(False, "hideBlankVerseCompare")],
            ["enforceCompareParallel", config.enforceCompareParallel, self.parent.enforceCompareParallelButtonClicked, self.flagToolTip(False, "enforceCompareParallel")],
            ["enableMenuUnderline", config.enableMenuUnderline, self.enableMenuUnderlineChanged, self.flagToolTip(True, "enableMenuUnderline")],
            ["openBibleInMainViewOnly", config.openBibleInMainViewOnly, self.parent.enableStudyBibleButtonClicked, self.flagToolTip(False, "openBibleInMainViewOnly")],
            ["addOHGBiToMorphologySearch", config.addOHGBiToMorphologySearch, self.addOHGBiToMorphologySearchChanged, self.flagToolTip(True, "addOHGBiToMorphologySearch")],
        ]
        if config.isTtsInstalled:
            options += [
                ["useLangDetectOnTts", config.useLangDetectOnTts, self.useLangDetectOnTtsChanged, self.flagToolTip(False, "useLangDetectOnTts")],
                ["ttsEnglishAlwaysUS", config.ttsEnglishAlwaysUS, self.ttsEnglishAlwaysUSChanged, self.flagToolTip(False, "ttsEnglishAlwaysUS")],
                ["ttsEnglishAlwaysUK", config.ttsEnglishAlwaysUK, self.ttsEnglishAlwaysUKChanged, self.flagToolTip(False, "ttsEnglishAlwaysUK")],
                ["ttsChineseAlwaysMandarin", config.ttsChineseAlwaysMandarin, self.ttsChineseAlwaysMandarinChanged, self.flagToolTip(False, "ttsChineseAlwaysMandarin")],
                ["ttsChineseAlwaysCantonese", config.ttsChineseAlwaysCantonese, self.ttsChineseAlwaysCantoneseChanged, self.flagToolTip(False, "ttsChineseAlwaysCantonese")],
            ]

        if platform.system() == "Linux":
            options += [
                ["linuxStartFullScreen", config.linuxStartFullScreen, self.linuxStartFullScreenChanged, self.flagToolTip(False, "linuxStartFullScreen")],
                ["fcitx", config.fcitx, self.fcitxChanged, self.flagToolTip(False, "fcitx")],
                ["ibus", config.ibus, self.ibusChanged, self.flagToolTip(False, "ibus")],
                ["espeak", config.espeak, self.espeakChanged, self.flagToolTip(False, "espeak")],
            ]
        if config.developer:
            options += [
                ["forceGenerateHtml", config.forceGenerateHtml, self.forceGenerateHtmlChanged, self.flagToolTip(False, "forceGenerateHtml")],
                ["enableLogging", config.enableLogging, self.enableLoggingChanged, self.flagToolTip(False, "enableLogging")],
                ["logCommands", config.logCommands, self.logCommandsChanged, self.flagToolTip(False, "logCommands")],
            ]

        self.wikiLink = "https://github.com/eliranwong/UniqueBible/wiki/Config-file-reference"

        self.layout = QVBoxLayout()

        readWiki = QLabel(config.thisTranslation["menu_config_flags"])
        readWiki.mouseReleaseEvent = self.openWiki
        self.layout.addWidget(readWiki)

        self.filterEntry = QLineEdit()
        self.filterEntry.textChanged.connect(self.filterChanged)
        self.layout.addWidget(self.filterEntry)

        self.table = QTableView()
        self.model = DisplayConfigOptionsModel(self, options)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()
        self.table.setSortingEnabled(True)
        checkBoxDelegate = CheckBoxDelegate(self)
        self.table.setItemDelegateForColumn(1, checkBoxDelegate)
        self.layout.addWidget(self.table)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def filterChanged(self, text):
        self.model.filter(text)

    def flagToolTip(self, default, toolTip):
        return "{0} {1}\n{2}".format(config.thisTranslation["default"], default, config.thisTranslation[toolTip])

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

    def restrictControlPanelWidthChanged(self):
        config.restrictControlPanelWidth = not config.restrictControlPanelWidth
        self.parent.reloadControlPanel(False)

    def regexCaseSensitiveChanged(self):
        config.regexCaseSensitive = not config.regexCaseSensitive

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

    def disableModulesUpdateCheckChanged(self):
        config.disableModulesUpdateCheck = not config.disableModulesUpdateCheck

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

    def hideBlankVerseCompareChanged(self):
        config.hideBlankVerseCompare = not config.hideBlankVerseCompare

    def enableMenuUnderlineChanged(self):
        config.enableMenuUnderline = not config.enableMenuUnderline
        if config.enableMenuUnderline:
            config.menuUnderline = "&"
        else:
            config.menuUnderline = ""
        self.parent.setMenuLayout(config.menuLayout)

class DisplayConfigOptionsModel(QAbstractTableModel):

    def __init__(self, parent, data, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.fullList = data
        self.list = data
        self.header = header = ['Config', 'Value']
        self.col = 0
        self.order = None

    def filter(self, text):
        newList = []
        for item in self.fullList:
            if text.lower() in item[0].lower() or text.lower() in item[3].lower():
                newList.append(item)
        self.list = newList
        self.sort(self.col, self.order)

    def rowCount(self, parent):
        return len(self.list)

    def columnCount(self, parent):
        if len(self.list) == 0:
            return 0
        else:
            return 2

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role == Qt.ToolTipRole:
            return self.list[index.row()][3]
        elif role != Qt.DisplayRole:
            return None
        return self.list[index.row()][index.column()]

    def getRow(self, row):
        return self.list[row]

    def setRow(self, row, data):
        self.list[row] = data

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        self.layoutAboutToBeChanged.emit()
        self.col = col
        self.order = order
        self.list = sorted(self.list, key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.list.reverse()
        self.layoutChanged.emit()

# https://stackoverflow.com/questions/17748546/pyqt-column-of-checkboxes-in-a-qtableview/17788371
class CheckBoxDelegate(QtWidgets.QItemDelegate):
    def __init__(self, parent):
        QtWidgets.QItemDelegate.__init__(self, parent)
        self.parent = parent

    def createEditor(self, parent, option, index):
        return None

    def paint(self, painter, option, index):
        self.drawCheck(painter, option, option.rect, QtCore.Qt.Unchecked if int(index.data()) == 0 else QtCore.Qt.Checked)

    def editorEvent(self, event, model, option, index):
        if event.type() == QtCore.QEvent.MouseButtonRelease:
            self.setModelData(None, model, index)
            return True
        return False

    def setModelData (self, editor, model, index):
        rowIndex = index.row()
        rowData = model.list[rowIndex]
        rowData[2]()
        for item in model.fullList:
            if item[0] == rowData[0]:
               item[1] = getattr(config, rowData[0])

class DummyParent:

    def enableNoteIndicatorButtonClicked(self):
        pass

if __name__ == '__main__':
    from util.LanguageUtil import LanguageUtil
    from util.ConfigUtil import ConfigUtil

    ConfigUtil.setup()
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    config.isTtsInstalled = True

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = DisplayConfigOptionsWindow(DummyParent())
    window.exec_()
    window.close()