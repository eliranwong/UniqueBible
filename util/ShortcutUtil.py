import glob
import pprint
import sys
from os import path
from qtpy.QtCore import Qt
import config


# Defined sets of shortcuts:
# blank
# brachys
# micron
# syntemno
class ShortcutUtil:

    data = {
        "blank": {
            "back": "",
            "bookFeatures": "",
            "bottomHalfScreenHeight": "",
            "chapterFeatures": "",
            "commentaryRefButtonClicked": "",
            "createNewNoteFile": "",
            "cycleInstant": "",
            "displaySearchAllBookCommand": "",
            "displaySearchBibleCommand": "",
            "displaySearchBibleMenu": "",
            "displaySearchBookCommand": "",
            "displaySearchHighlightCommand": "",
            "displaySearchStudyBibleCommand": "",
            "displayShortcuts": "",
            "editExternalFileButtonClicked": "",
            "enableInstantButtonClicked": "",
            "enableParagraphButtonClicked": "",
            "enableSubheadingButtonClicked": "",
            "toggleShowVerseReference": "",
            "toggleShowWordAudio": "",
            "toggleShowUserNoteIndicator": "",
            "toggleShowBibleNoteIndicator": "",
            "toggleHideLexicalEntryInBible": "",
            "toggleReadTillChapterEnd": "",
            "enforceCompareParallel": "",
            "externalFileButtonClicked": "",
            "forward": "",
            "fullsizeWindow": "",
            "maximizedWindow": "",
            "gotoFirstChapter": "",
            "gotoLastChapter": "",
            "hideShowSideToolBars": "",
            "hideShowAdditionalToolBar": "",
            "hideShowLeftToolBar": "",
            "hideShowMainToolBar": "",
            "hideShowRightToolBar": "",
            "hideShowSecondaryToolBar": "",
            "largerFont": "",
            "leftHalfScreenWidth": "",
            "loadRunMacro": "",
            "mainHistoryButtonClicked": "",
            "mainPageScrollPageDown": "",
            "mainPageScrollPageUp": "",
            "mainPageScrollToTop": "",
            "manageControlPanel": "",
            "manageMiniControl": "",
            "mediaPlayer": "",
            "moreConfigOptionsDialog": "",
            "nextChapterButton": "",
            "nextMainBook": "",
            "nextMainChapter": "",
            "openControlPanelTab0": "",
            "openControlPanelTab1": "",
            "openControlPanelTab2": "",
            "openControlPanelTab3": "",
            "openControlPanelTab4": "",
            "openControlPanelTab5": "",
            "openControlPanelTab6": "",
            "openControlPanelTab7": "",
            "openMainBookNote": "",
            "openMainChapterNote": "",
            "openMainVerseNote": "",
            "openTextFileDialog": "",
            "parallel": "",
            "parseContentOnClipboard": "",
            "previousChapterButton": "",
            "previousMainBook": "",
            "previousMainChapter": "",
            "quitApp": "",
            "reloadCurrentRecord": "",
            "reloadResources": "",
            "rightHalfScreenWidth": "",
            "runCOMBO": "",
            "runCOMMENTARY": "",
            "runCOMPARE": "",
            "runCROSSREFERENCE": "",
            "runDISCOURSE": "",
            "runINDEX": "",
            "runKJV2Bible": "",
            "runMAB": "",
            "runMIB": "",
            "runMOB": "",
            "runMPB": "",
            "runMTB": "",
            "runTSKE": "",
            "runTransliteralBible": "",
            "runWORDS": "",
            "searchCommandBibleCharacter": "",
            "searchCommandBibleDictionary": "",
            "searchCommandBibleEncyclopedia": "",
            "searchCommandBibleLocation": "",
            "searchCommandBibleName": "",
            "searchCommandBibleTopic": "",
            "searchCommandBookNote": "",
            "searchCommandChapterNote": "",
            "searchCommandLexicon": "",
            "searchCommandVerseNote": "",
            "setDefaultFont": "",
            "setNoToolBar": "",
            "showGistWindow": "",
            "smallerFont": "",
            "studyBack": "",
            "studyForward": "",
            "studyHistoryButtonClicked": "",
            "studyPageScrollPageDown": "",
            "studyPageScrollPageUp": "",
            "studyPageScrollToTop": "",
            "switchIconSize": "",
            "switchLandscapeMode": "",
            "syncStudyWindowBible": "",
            "syncStudyWindowCommentary": "",
            "toggleHighlightMarker": '',
            "toggleHighlightMarker": "",
            "topHalfScreenHeight": "",
            "twoThirdWindow": "",
            "ubaWiki": '',
            "ubaDiscussions": '',
            "commandLineInterface": '',
            "liveFilterDialog": '',
            "bibleCollections": "",
            "showLibraryCatalogDialog": "",
            "toggleFavouriteVersionIntoMultiRef": "",
        },
        "brachys": {
            "back": "Ctrl+[",
            "bookFeatures": "Ctrl+R, F",
            "bottomHalfScreenHeight": "Ctrl+S, 2",
            "chapterFeatures": "Ctrl+W, H",
            "commentaryRefButtonClicked": "Ctrl+H, C",
            "createNewNoteFile": "Ctrl+N, N",
            "cycleInstant": "Ctrl+U, 0",
            "displaySearchAllBookCommand": "Ctrl+S, R",
            "displaySearchBibleCommand": "Ctrl+1",
            "displaySearchBibleMenu": "Ctrl+S, M",
            "displaySearchBookCommand": "Ctrl+E, 5",
            "displaySearchHighlightCommand": "Ctrl+S, H",
            "displaySearchStudyBibleCommand": "Ctrl+E, 1",
            "displayShortcuts": 'Ctrl+|',
            "editExternalFileButtonClicked": "Ctrl+N, E",
            "enableInstantButtonClicked": "Ctrl+=",
            "enableParagraphButtonClicked": "Ctrl+P",
            "enableSubheadingButtonClicked": "Ctrl+D, P",
            "toggleShowVerseReference": "",
            "toggleShowWordAudio": "",
            "toggleShowUserNoteIndicator": "",
            "toggleShowBibleNoteIndicator": "",
            "toggleHideLexicalEntryInBible": "",
            "toggleReadTillChapterEnd": "",
            "enforceCompareParallel": '',
            "externalFileButtonClicked": "Ctrl+N, R",
            "forward": "Ctrl+]",
            "fullsizeWindow": "Ctrl+S, F",
            "maximizedWindow": "",
            "gotoFirstChapter": "Ctrl+I, <",
            "gotoLastChapter": "Ctrl+I, >",
            "hideShowSideToolBars": "Ctrl+E, \\",
            "hideShowAdditionalToolBar": "Ctrl+H, 1",
            "hideShowLeftToolBar": "Ctrl+T, L",
            "hideShowMainToolBar": "Ctrl+T, 1",
            "hideShowRightToolBar": "Ctrl+T, R",
            "hideShowSecondaryToolBar": "Ctrl+T, 3",
            "largerFont": "Ctrl++",
            "leftHalfScreenWidth": "Ctrl+S, 3",
            "loadRunMacro": "",
            "mainHistoryButtonClicked": "Ctrl+'",
            "mainPageScrollPageDown": "Ctrl+H, 5",
            "mainPageScrollPageUp": "Ctrl+H, 4",
            "mainPageScrollToTop": "Ctrl+H, 3",
            "manageControlPanel": "Ctrl+M, 0",
            "manageMiniControl": "Ctrl+I, R",
            "mediaPlayer": "Ctrl+Shift+V",
            "moreConfigOptionsDialog": "Ctrl+Shift+C",
            "nextChapterButton": "Ctrl+)",
            "nextMainBook": "Ctrl+}",
            "nextMainChapter": "Ctrl+>",
            "openControlPanelTab0": 'Ctrl+B',
            "openControlPanelTab1": 'Ctrl+L',
            "openControlPanelTab2": 'Ctrl+Shift+L',
            "openControlPanelTab3": 'Ctrl+F',
            "openControlPanelTab4": 'Ctrl+Y',
            "openControlPanelTab5": 'Ctrl+M',
            "openControlPanelTab6": 'Ctrl+Shift+M',
            "openControlPanelTab7": 'Ctrl+Shift+S',
            "openMainBookNote": "Ctrl+N, B",
            "openMainChapterNote": "Ctrl+N, C",
            "openMainVerseNote": "Ctrl+N, V",
            "openTextFileDialog": "Ctrl+O",
            "parallel": "Ctrl+W",
            "parseContentOnClipboard": "Ctrl+^",
            "previousChapterButton": "Ctrl+(",
            "previousMainBook": "Ctrl+{",
            "previousMainChapter": "Ctrl+<",
            "quitApp": "Ctrl+Q",
            "reloadCurrentRecord": "Ctrl+D, R",
            "reloadResources": "Ctrl+R, R",
            "rightHalfScreenWidth": "Ctrl+S, 4",
            "runCOMBO": "Ctrl+K",
            "runCOMMENTARY": "Ctrl+I, C",
            "runCOMPARE": "Ctrl+D, C",
            "runCROSSREFERENCE": "Ctrl+U, C",
            "runDISCOURSE": "Ctrl+R, D",
            "runINDEX": "Ctrl+.",
            "runKJV2Bible": "Ctrl+I, K",
            "runMAB": "Ctrl+M, 1",
            "runMIB": "Ctrl+M, 2",
            "runMOB": "Ctrl+M, 3",
            "runMPB": "Ctrl+M, 4",
            "runMTB": "Ctrl+M, 5",
            "runTSKE": "Ctrl+M, T",
            "runTransliteralBible": "Ctrl+I, T",
            "runWORDS": "Ctrl+R, W",
            "searchCommandBibleCharacter": "Ctrl+E, 7",
            "searchCommandBibleDictionary": "Ctrl+E, 2",
            "searchCommandBibleEncyclopedia": "Ctrl+E, 3",
            "searchCommandBibleLocation": "Ctrl+E, 9",
            "searchCommandBibleName": "Ctrl+E, 8",
            "searchCommandBibleTopic": "Ctrl+E, 6",
            "searchCommandBookNote": "Ctrl+S, 1",
            "searchCommandChapterNote": "Ctrl+S, 2",
            "searchCommandLexicon": "Ctrl+S, 0",
            "searchCommandVerseNote": "Ctrl+S, 3",
            "setDefaultFont": "Ctrl+D, F",
            "setNoToolBar": "Ctrl+J",
            "showGistWindow": "Ctrl+N, G",
            "smallerFont": "Ctrl+-",
            "studyBack": "Ctrl+I, [",
            "studyForward": "Ctrl+I, ]",
            "studyHistoryButtonClicked": 'Ctrl+"',
            "studyPageScrollPageDown": "Ctrl+H, 8",
            "studyPageScrollPageUp": "Ctrl+H, 7",
            "studyPageScrollToTop": "Ctrl+H, 6",
            "switchIconSize": "Ctrl+T, I",
            "switchLandscapeMode": "Ctrl+R, M",
            "syncStudyWindowBible": "",
            "syncStudyWindowCommentary": "",
            "toggleHighlightMarker": "Ctrl+I, I",
            "topHalfScreenHeight": "Ctrl+S, 1",
            "twoThirdWindow": "Ctrl+S, S",
            "ubaWiki": '',
            "ubaDiscussions": '',
            "commandLineInterface": '',
            "liveFilterDialog": '',
            "bibleCollections": "",
            "showLibraryCatalogDialog": "Ctrl+Shift+O",
            "toggleFavouriteVersionIntoMultiRef": "",
        },
        "micron": {
            "back": 'Ctrl+[',
            "bookFeatures": '',
            "bottomHalfScreenHeight": 'Ctrl+S, 2',
            "chapterFeatures": '',
            "commentaryRefButtonClicked": '',
            "createNewNoteFile": 'Ctrl+N',
            "cycleInstant": 'Ctrl+E',
            "displaySearchAllBookCommand": '',
            "displaySearchBibleCommand": '',
            "displaySearchBibleMenu": '',
            "displaySearchBookCommand": '',
            "displaySearchHighlightCommand": '',
            "displaySearchStudyBibleCommand": '',
            "displayShortcuts": 'Ctrl+|',
            "editExternalFileButtonClicked": '',
            "enableInstantButtonClicked": 'Ctrl+=',
            "enableParagraphButtonClicked": 'Ctrl+P',
            "enableSubheadingButtonClicked": 'Ctrl+I',
            "toggleShowVerseReference": "Ctrl+Shift+E",
            "toggleShowWordAudio": "Ctrl+Shift+A",
            "toggleShowUserNoteIndicator": "Ctrl+Shift+N",
            "toggleShowBibleNoteIndicator": "Ctrl+Shift+B",
            "toggleHideLexicalEntryInBible": "Ctrl+Shift+X",
            "toggleReadTillChapterEnd": "Ctrl+Shift+R",
            "enforceCompareParallel": 'Ctrl+*',
            "externalFileButtonClicked": '',
            "forward": 'Ctrl+]',
            "fullsizeWindow": 'Ctrl+Shift+U',
            "maximizedWindow": 'Ctrl+U',
            "gotoFirstChapter": '',
            "gotoLastChapter": '',
            "hideShowSideToolBars": '',
            "hideShowAdditionalToolBar": 'Ctrl+T',
            "hideShowLeftToolBar": 'Ctrl+3',
            "hideShowMainToolBar": 'Ctrl+1',
            "hideShowRightToolBar": 'Ctrl+4',
            "hideShowSecondaryToolBar": 'Ctrl+2',
            "largerFont": 'Ctrl++',
            "leftHalfScreenWidth": 'Ctrl+S, 3',
            "loadRunMacro": '',
            "mainHistoryButtonClicked": '',
            "mainPageScrollPageDown": 'Ctrl+J',
            "mainPageScrollPageUp": 'Ctrl+K',
            "mainPageScrollToTop": 'Ctrl+!',
            "manageControlPanel": '',
            "manageMiniControl": 'Ctrl+G',
            "moreConfigOptionsDialog": "Ctrl+Shift+C",
            "mediaPlayer": "Ctrl+Shift+V",
            "nextChapterButton": '',
            "nextMainBook": 'Ctrl+}',
            "nextMainChapter": 'Ctrl+>',
            "openControlPanelTab0": 'Ctrl+B',
            "openControlPanelTab1": 'Ctrl+L',
            "openControlPanelTab2": 'Ctrl+Shift+L',
            "openControlPanelTab3": 'Ctrl+F',
            "openControlPanelTab4": 'Ctrl+Y',
            "openControlPanelTab5": 'Ctrl+M',
            "openControlPanelTab6": 'Ctrl+Shift+M',
            "openControlPanelTab7": 'Ctrl+Shift+S',
            "openMainBookNote": '',
            "openMainChapterNote": '',
            "openMainVerseNote": '',
            "openTextFileDialog": 'Ctrl+O',
            "parallel": 'Ctrl+W',
            "parseContentOnClipboard": '',
            "previousChapterButton": '',
            "previousMainBook": 'Ctrl+{',
            "previousMainChapter": 'Ctrl+<',
            "quitApp": 'Ctrl+Q',
            "reloadCurrentRecord": 'Ctrl+R',
            "reloadResources": "",
            "rightHalfScreenWidth": 'Ctrl+S, 4',
            "runCOMBO": '',
            "runCOMMENTARY": '',
            "runCOMPARE": '',
            "runCROSSREFERENCE": '',
            "runDISCOURSE": '',
            "runINDEX": '',
            "runKJV2Bible": '',
            "runMAB": '',
            "runMIB": '',
            "runMOB": '',
            "runMPB": '',
            "runMTB": '',
            "runTSKE": '',
            "runTransliteralBible": '',
            "runWORDS": '',
            "searchCommandBibleCharacter": '',
            "searchCommandBibleDictionary": '',
            "searchCommandBibleEncyclopedia": '',
            "searchCommandBibleLocation": '',
            "searchCommandBibleName": '',
            "searchCommandBibleTopic": '',
            "searchCommandBookNote": '',
            "searchCommandChapterNote": '',
            "searchCommandLexicon": '',
            "searchCommandVerseNote": '',
            "setDefaultFont": '',
            "setNoToolBar": '',
            "showGistWindow": '',
            "smallerFont": 'Ctrl+-',
            "studyBack": '',
            "studyForward": '',
            "studyHistoryButtonClicked": '',
            "studyPageScrollPageDown": 'Ctrl+,',
            "studyPageScrollPageUp": 'Ctrl+.',
            "studyPageScrollToTop": 'Ctrl+@',
            "switchIconSize": '',
            "switchLandscapeMode": '',
            "syncStudyWindowBible": 'Ctrl+`',
            "syncStudyWindowCommentary": 'Ctrl+~',
            "toggleHighlightMarker": 'Ctrl+%',
            "topHalfScreenHeight": 'Ctrl+S, 1',
            "twoThirdWindow": 'Ctrl+S, 0',
            "ubaWiki": 'Ctrl+H',
            "ubaDiscussions": 'Ctrl+D',
            "commandLineInterface": 'Ctrl+^',
            "liveFilterDialog": 'Ctrl+Shift+F',
            "bibleCollections": "",
            "showLibraryCatalogDialog": "",
            "toggleFavouriteVersionIntoMultiRef": "Ctrl+Shift+I",
        },
        "syntemno": {
            "back": "Ctrl+Y, 1",
            "bookFeatures": "Ctrl+L, F",
            "bottomHalfScreenHeight": "Ctrl+W, B",
            "chapterFeatures": "Ctrl+L, H",
            "commentaryRefButtonClicked": "",
            "createNewNoteFile": "Ctrl+N, N",
            "cycleInstant": "Ctrl+'",
            "displaySearchAllBookCommand": "Ctrl+S, R",
            "displaySearchBibleCommand": "Ctrl+S, B",
            "displaySearchBibleMenu": "Ctrl+S, M",
            "displaySearchBookCommand": "Ctrl+E, 5",
            "displaySearchHighlightCommand": "Ctrl+S, H",
            "displaySearchStudyBibleCommand": "Ctrl+E, 2",
            "displayShortcuts": 'Ctrl+|',
            "editExternalFileButtonClicked": "Ctrl+N, E",
            "enableInstantButtonClicked": "Ctrl+=",
            "enableParagraphButtonClicked": "Ctrl+D, S",
            "enableSubheadingButtonClicked": "Ctrl+D, P",
            "toggleShowVerseReference": "",
            "toggleShowWordAudio": "",
            "toggleShowUserNoteIndicator": "",
            "toggleShowBibleNoteIndicator": "",
            "toggleHideLexicalEntryInBible": "",
            "toggleReadTillChapterEnd": "",
            "enforceCompareParallel": '',
            "externalFileButtonClicked": "Ctrl+N, R",
            "forward": "Ctrl+Y, 2",
            "fullsizeWindow": "Ctrl+W, F",
            "maximizedWindow": "Ctrl+W, M",
            "gotoFirstChapter": 'Ctrl+<',
            "gotoLastChapter": 'Ctrl+>',
            "hideShowSideToolBars": "Ctrl+\\",
            "hideShowAdditionalToolBar": "Ctrl+T, 2",
            "hideShowLeftToolBar": "Ctrl+T, L",
            "hideShowMainToolBar": "Ctrl+T, 1",
            "hideShowRightToolBar": "Ctrl+T, R",
            "hideShowSecondaryToolBar": "Ctrl+T, 3",
            "largerFont": "Ctrl++",
            "leftHalfScreenWidth": "Ctrl+W, L",
            "loadRunMacro": "Ctrl+M",
            "mainHistoryButtonClicked": "Ctrl+Y, M",
            "mainPageScrollPageDown": 'Ctrl+J',
            "mainPageScrollPageUp": 'Ctrl+K',
            "mainPageScrollToTop": 'Ctrl+7',
            "manageControlPanel": "Ctrl+U",
            "manageMiniControl": "Ctrl+O",
            "mediaPlayer": "Ctrl+Shift+M",
            "moreConfigOptionsDialog": "Ctrl+D, C",
            "nextChapterButton": "Ctrl+)",
            "nextMainBook": 'Ctrl+]',
            "nextMainChapter": 'Ctrl+.',
            "openControlPanelTab0": 'Ctrl+B, B',
            "openControlPanelTab1": 'Ctrl+L, L',
            "openControlPanelTab2": "Ctrl+P, P",
            "openControlPanelTab3": 'Ctrl+S, S',
            "openControlPanelTab4": 'Ctrl+Y, Y',
            "openControlPanelTab5": 'Ctrl+M, N',
            "openControlPanelTab6": 'Ctrl+M, M',
            "openControlPanelTab7": 'Ctrl+Shift+S',
            "openMainBookNote": "Ctrl+N, B",
            "openMainChapterNote": "Ctrl+N, C",
            "openMainVerseNote": "Ctrl+N, V",
            "openTextFileDialog": "Ctrl+N, O",
            "parallel": "Ctrl+;",
            "parseContentOnClipboard": "Ctrl+^",
            "previousChapterButton": "Ctrl+(",
            "previousMainBook": 'Ctrl+[',
            "previousMainChapter": "Ctrl+,",
            "quitApp": "Ctrl+Q",
            "reloadCurrentRecord": "Ctrl+D, R",
            "reloadResources": "Ctrl+R, R",
            "rightHalfScreenWidth": "Ctrl+W, R",
            "runCOMBO": "Ctrl+L, M",
            "runCOMMENTARY": "Ctrl+L, C",
            "runCOMPARE": "Ctrl+S, V",
            "runCROSSREFERENCE": "Ctrl+L, X",
            "runDISCOURSE": "Ctrl+L, D",
            "runINDEX": "Ctrl+L, I",
            "runKJV2Bible": "",
            "runMAB": "Ctrl+B, 5",
            "runMIB": "Ctrl+B, 2",
            "runMOB": "Ctrl+B, 1",
            "runMPB": "Ctrl+B, 4",
            "runMTB": "Ctrl+B, 3",
            "runTSKE": "Ctrl+L, T",
            "runTransliteralBible": "Ctrl+B, T",
            "runWORDS": "Ctrl+L, W",
            "searchCommandBibleCharacter": "Ctrl+S, C",
            "searchCommandBibleDictionary": "Ctrl+E, 3",
            "searchCommandBibleEncyclopedia": "Ctrl+E, 4",
            "searchCommandBibleLocation": "Ctrl+S, O",
            "searchCommandBibleName": "Ctrl+S, N",
            "searchCommandBibleTopic": "Ctrl+E, 6",
            "searchCommandBookNote": "Ctrl+S, 1",
            "searchCommandChapterNote": "Ctrl+S, 2",
            "searchCommandLexicon": "Ctrl+S, L",
            "searchCommandVerseNote": "Ctrl+S, 3",
            "setDefaultFont": "Ctrl+D, F",
            "setNoToolBar": "Ctrl+T, T",
            "showGistWindow": "Ctrl+N, G",
            "smallerFont": "Ctrl+-",
            "studyBack": "Ctrl+Y, 3",
            "studyForward": "Ctrl+Y, 4",
            "studyHistoryButtonClicked": 'Ctrl+Y, S',
            "studyPageScrollPageDown": 'Ctrl+9',
            "studyPageScrollPageUp": 'Ctrl+0',
            "studyPageScrollToTop": "Ctrl+8",
            "switchIconSize": "Ctrl+T, I",
            "switchLandscapeMode": "Ctrl+/",
            "syncStudyWindowBible": "",
            "syncStudyWindowCommentary": "",
            "toggleHighlightMarker": "",
            "topHalfScreenHeight": "Ctrl+W, T",
            "twoThirdWindow": "Ctrl+W, S",
            "ubaWiki": '',
            "ubaDiscussions": '',
            "commandLineInterface": '',
            "liveFilterDialog": 'Ctrl+*',
            "bibleCollections": "Ctrl+D,B",
            "showLibraryCatalogDialog": "Ctrl+I",
            "toggleFavouriteVersionIntoMultiRef": "",
        }
    }

    # For check
    reverseMicron = {
        "Ctrl+A": "",
        "Ctrl+B": "openControlPanelTab0",
        "Ctrl+C": "",
        "Ctrl+D": "ubaDiscussions",
        "Ctrl+E": "cycleInstant",
        "Ctrl+F": "openControlPanelTab3",
        "Ctrl+G": "manageMiniControl",
        "Ctrl+H": "ubaWiki",
        "Ctrl+I": "enableSubheadingButtonClicked",
        "Ctrl+J": "mainPageScrollPageDown",
        "Ctrl+K": "mainPageScrollPageUp",
        "Ctrl+L": "openControlPanelTab1",
        "Ctrl+M": "openControlPanelTab5",
        "Ctrl+N": "createNewNoteFile",
        "Ctrl+O": "openTextFileDialog",
        "Ctrl+P": "enableParagraphButtonClicked",
        "Ctrl+Q": "quitApp",
        "Ctrl+R": "reloadCurrentRecord",
        "Ctrl+S": "",
        "Ctrl+T": "hideShowAdditionalToolBar",
        "Ctrl+U": "maximizedWindow",
        "Ctrl+V": "",
        "Ctrl+W": "parallel",
        "Ctrl+X": "",
        "Ctrl+Y": "openControlPanelTab4",
        "Ctrl+Z": "",
        "Ctrl+Shift+A": "toggleShowWordAudio",
        "Ctrl+Shift+B": "toggleShowBibleNoteIndicator",
        "Ctrl+Shift+C": "moreConfigOptionsDialog",
        "Ctrl+Shift+D": "",
        "Ctrl+Shift+E": "toggleShowVerseReference",
        "Ctrl+Shift+F": "liveFilterDialog",
        "Ctrl+Shift+G": "",
        "Ctrl+Shift+H": "",
        "Ctrl+Shift+I": "toggleFavouriteVersionIntoMultiRef",
        "Ctrl+Shift+J": "",
        "Ctrl+Shift+K": "",
        "Ctrl+Shift+L": "openControlPanelTab2",
        "Ctrl+Shift+M": "openControlPanelTab6",
        "Ctrl+Shift+N": "toggleShowUserNoteIndicator",
        "Ctrl+Shift+O": "",
        "Ctrl+Shift+P": "",
        "Ctrl+Shift+Q": "",
        "Ctrl+Shift+R": "toggleReadTillChapterEnd",
        "Ctrl+Shift+S": "openControlPanelTab7",
        "Ctrl+Shift+T": "",
        "Ctrl+Shift+U": "fullsizeWindow",
        "Ctrl+Shift+V": "mediaPlayer",
        "Ctrl+Shift+W": "",
        "Ctrl+Shift+X": "toggleHideLexicalEntryInBible",
        "Ctrl+Shift+Y": "",
        "Ctrl+Shift+Z": "",
    }

    @staticmethod
    def setup(name):
        try:
            if name not in ShortcutUtil.data.keys():
                filename = "shortcut_" + name + ".py"
                if not path.exists(filename):
                    name = "micron"
                else:
                    from shutil import copyfile
                    ShortcutUtil.checkCustomShortcutFileValid(name)
                    copyfile(filename, "shortcut.py")
        except Exception as e:
            name = "micron"

        if name in ShortcutUtil.data.keys():
            ShortcutUtil.create(ShortcutUtil.data[name])
        config.menuShortcuts = name

    @staticmethod
    def create(data):
        with open("shortcut.py", "w", encoding="utf-8") as fileObj:
            for name in data.keys():
                value = data[name]
                fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
            fileObj.close()

    @staticmethod
    def reset():
        with open("shortcut.py", "w", encoding="utf-8") as fileObj:
            fileObj.write("")
            fileObj.close()

    @staticmethod
    def keyCode(letter):
        if letter is None:
            return None
        else:
            return Qt.Key_A + ord(letter) - ord("A")

    @staticmethod
    def getListCustomShortcuts():
        return [file[9:-3] for file in glob.glob("shortcut_*.py")]

    @staticmethod
    def getAllShortcuts():
        import shortcut as sc

        lines = []
        for action in sc.__dict__.keys():
            if action[:1] != '_':
                key = str(sc.__dict__[action])
                key = key.replace("\\\\", "\\")
                lines.append([action, key])
        lines.sort()
        return lines

    @staticmethod
    def getAllShortcutsAsString():
        str = ""
        for (key, command) in ShortcutUtil.getAllShortcuts():
            str += "{0} : {1}\n".format(key, command)
        return str

    @staticmethod
    def checkCustomShortcutFileValid(name, source="micron"):
        customShortcuts = ShortcutUtil.readShorcutFile(name)
        actions = customShortcuts.keys()
        for action in ShortcutUtil.data[source]:
            if action not in actions:
                ShortcutUtil.addActionToShortcutFile(name, action, ShortcutUtil.data[source][action])

    @staticmethod
    def readShorcutFile(name=None):
        if name is None or name in ShortcutUtil.data.keys():
            filename = "shortcut.py"
        else:
            filename = "shortcut_" + name + ".py"
        file = open(filename, "r")
        lines = file.readlines()
        data = {}
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                values = line.split('=')
                key = values[0].strip()
                action = values[1].strip()
                data[key] = action
        return data

    @staticmethod
    def loadShortcutFile(name=None):
        import shortcut
        customShortcuts = ShortcutUtil.readShorcutFile(name)
        for key in customShortcuts.keys():
            action = customShortcuts[key]
            setattr(shortcut, key, action[1:-1])

    @staticmethod
    def addActionToShortcutFile(name, action, shortcut=""):
        filename = "shortcut_" + name + ".py"
        with open(filename, "a", encoding="utf-8") as fileObj:
            print("Added {0} to {1}".format(action, filename))
            fileObj.write('{0} = "{1}"\n'.format(action, shortcut))
            fileObj.close()

    @staticmethod
    def createShortcutFile(name, shortcuts):
        shortcuts.sort(key=lambda x: x[0])
        with open("shortcut_"+name+".py", "w", encoding="utf-8") as fileObj:
            for action, key in shortcuts:
                key = key.replace("\\\\", "\\")
                fileObj.write("{0} = {1}\n".format(action, pprint.pformat(key)))
            fileObj.close()

# Test code

def print_info():
    for name in ShortcutUtil.data.keys():
        print("{0}: {1}".format(name, len(ShortcutUtil.data[name])))
    for name in ShortcutUtil.getListCustomShortcuts():
        print("{0}: {1}".format(name, len(ShortcutUtil.readShorcutFile(name).keys())))

def print_compare(set1, set2):
    if set1 in ShortcutUtil.data.keys():
        keys1 = ShortcutUtil.data[set1].keys()
    else:
        keys1 = ShortcutUtil.readShorcutFile(set1).keys()
    if set2 in ShortcutUtil.data.keys():
        keys2 = ShortcutUtil.data[set2].keys()
    else:
        keys2 = ShortcutUtil.readShorcutFile(set2).keys()
    for key in keys1:
        if key not in keys2:
            print(key + " not in " + set2)
    for key in keys2:
        if key not in keys1:
            print(key + " not in " + set1)

def print_shortcuts(name):
    print(name)
    lines = []
    if name in ShortcutUtil.data.keys():
        data = ShortcutUtil.data[name]
    else:
        data = ShortcutUtil.readShorcutFile(name)
    for key in data.keys():
        lines.append(str(data[key]) + " : " + key)
    lines.sort()
    print("\n".join(lines))

def fix_custom(name):
    ShortcutUtil.checkCustomShortcutFileValid(name)

# To use:
# python -m util.ShortcutUtil <command> <shortcut1> <shortcut2>
#
# Examples:
#   python -m util.ShortcutUtil print_info
#   python -m util.ShortcutUtil print_shortcuts micron
#   python -m util.ShortcutUtil fix_custom myshortcut

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            method = sys.argv[1].strip()
            if len(sys.argv) == 2:
                globals()[method]()
            else:
                name1 = sys.argv[2].strip()
                if len(sys.argv) == 3:
                    globals()[method](name1)
                else:
                    name2 = sys.argv[3].strip()
                    globals()[method](name1, name2)
            print("Done")
        except Exception as e:
            print("Error: " + str(e))
    else:
        pass
        # print_info()
        # print_compare("brachys", "test1")
        # print_shortcuts("blank")
        # print_shortcuts("brachys")
        # print_shortcuts("micron")
        # print_shortcuts("syntemno")
        # print_shortcuts("test1")
        # fix_custom("test1")

    ShortcutUtil.loadShortcutFile("test1")
