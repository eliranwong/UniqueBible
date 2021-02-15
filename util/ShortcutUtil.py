import glob
import pprint
import sys

from os import path
from PySide2.QtCore import Qt

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
            "enforceCompareParallel": "",
            "externalFileButtonClicked": "",
            "forward": "",
            "fullsizeWindow": "",
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
            "manageRemoteControl": "",
            "masterCurrentIndex0": "",
            "masterCurrentIndex1": "",
            "masterCurrentIndex2": "",
            "masterCurrentIndex3": "",
            "masterCurrentIndex4": "",
            "nextChapterButton": "",
            "nextMainBook": "",
            "nextMainChapter": "",
            "openControlPanelTab0": "",
            "openControlPanelTab1": "",
            "openControlPanelTab2": "",
            "openControlPanelTab3": "",
            "openControlPanelTab4": "",
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
            "enforceCompareParallel": '',
            "externalFileButtonClicked": "Ctrl+N, R",
            "forward": "Ctrl+]",
            "fullsizeWindow": "Ctrl+S, F",
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
            "manageRemoteControl": "Ctrl+I, R",
            "masterCurrentIndex0": "Ctrl+B",
            "masterCurrentIndex1": "Ctrl+L",
            "masterCurrentIndex2": "Ctrl+F",
            "masterCurrentIndex3": "Ctrl+Y",
            "masterCurrentIndex4": "",
            "nextChapterButton": "Ctrl+)",
            "nextMainBook": "Ctrl+}",
            "nextMainChapter": "Ctrl+>",
            "openControlPanelTab0": 'Ctrl+B',
            "openControlPanelTab1": 'Ctrl+L',
            "openControlPanelTab2": 'Ctrl+F',
            "openControlPanelTab3": 'Ctrl+Y',
            "openControlPanelTab4": 'Ctrl+M',
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
            "enforceCompareParallel": 'Ctrl+*',
            "externalFileButtonClicked": '',
            "forward": 'Ctrl+]',
            "fullsizeWindow": 'Ctrl+U',
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
            "manageRemoteControl": 'Ctrl+G',
            "masterCurrentIndex0": 'Ctrl+B',
            "masterCurrentIndex1": 'Ctrl+L',
            "masterCurrentIndex2": 'Ctrl+F',
            "masterCurrentIndex3": 'Ctrl+Y',
            "masterCurrentIndex4": 'Ctrl+M',
            "nextChapterButton": '',
            "nextMainBook": 'Ctrl+}',
            "nextMainChapter": 'Ctrl+>',
            "openControlPanelTab0": 'Ctrl+B',
            "openControlPanelTab1": 'Ctrl+L',
            "openControlPanelTab2": 'Ctrl+F',
            "openControlPanelTab3": 'Ctrl+Y',
            "openControlPanelTab4": 'Ctrl+M',
            "openMainBookNote": '',
            "openMainChapterNote": '',
            "openMainVerseNote": '',
            "openTextFileDialog": 'Ctrl+O',
            "parallel": 'Ctrl+W',
            "parseContentOnClipboard": 'Ctrl+^',
            "previousChapterButton": '',
            "previousMainBook": 'Ctrl+{',
            "previousMainChapter": 'Ctrl+<',
            "quitApp": 'Ctrl+Q',
            "reloadCurrentRecord": 'Ctrl+R',
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
            "twoThirdWindow": '',
            "ubaWiki": 'Ctrl+H',
            "ubaDiscussions": 'Ctrl+D',
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
            "enforceCompareParallel": '',
            "externalFileButtonClicked": "Ctrl+N, R",
            "forward": "Ctrl+Y, 2",
            "fullsizeWindow": "Ctrl+W, F",
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
            "manageControlPanel": "Ctrl+U, 0",
            "manageRemoteControl": "Ctrl+O",
            "masterCurrentIndex0": "Ctrl+B",
            "masterCurrentIndex1": "Ctrl+L",
            "masterCurrentIndex2": "Ctrl+F",
            "masterCurrentIndex3": "Ctrl+Y",
            "masterCurrentIndex4": '',
            "nextChapterButton": "Ctrl+)",
            "nextMainBook": 'Ctrl+]',
            "nextMainChapter": 'Ctrl+.',
            "openControlPanelTab0": 'Ctrl+U',
            "openControlPanelTab1": '',
            "openControlPanelTab2": '',
            "openControlPanelTab3": '',
            "openControlPanelTab4": '',
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
            "rightHalfScreenWidth": "Ctrl+W, R",
            "runCOMBO": "Ctrl+L, M",
            "runCOMMENTARY": "Ctrl+L, C",
            "runCOMPARE": "Ctrl+S, V",
            "runCROSSREFERENCE": "Ctrl+L, X",
            "runDISCOURSE": "Ctrl+L, D",
            "runINDEX": "Ctrl+.",
            "runKJV2Bible": "Ctrl+B, K",
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
        }
    }

    @staticmethod
    def setup(name):
        try:
            if name not in ShortcutUtil.data.keys():
                filename = "shortcut_" + name + ".py"
                if not path.exists(filename):
                    name = "micron"
                # elif FileUtil.getLineCount("shortcut.py") < 2 \
                #         or FileUtil.getLineCount(filename) != len(ShortcutUtil.data['micron']):
                else:
                    from shutil import copyfile
                    ShortcutUtil.checkCustomShortcutFileValid(filename)
                    copyfile(filename, "shortcut.py")
        except Exception as e:
            name = "micron"

        if name in ShortcutUtil.data.keys():
            ShortcutUtil.create(ShortcutUtil.data[name])
        config.menuShortcuts = name

    @staticmethod
    def create(data):
        # if not path.exists("shortcut.py") or FileUtil.getLineCount("shortcut.py") != len(data):
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
        for key in sc.__dict__.keys():
            if key[:1] != '_':
                lines.append((str(sc.__dict__[key]), (key)))
        lines.sort()
        return lines

    @staticmethod
    def getAllShortcutsAsString():
        str = ""
        for (key, command) in ShortcutUtil.getAllShortcuts():
            str += "{0} : {1}\n".format(key, command)
        return str

    @staticmethod
    def checkCustomShortcutFileValid(filename, source="micron"):
        customShortcuts = ShortcutUtil.readShorcutFile(filename)
        actions = customShortcuts.keys()
        for action in ShortcutUtil.data[source]:
            if action not in actions:
                ShortcutUtil.addActionToShortcutFile(filename, action, ShortcutUtil.data[source][action])

    @staticmethod
    def readShorcutFile(filename):
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
    def addActionToShortcutFile(filename, action, shortcut=""):
        with open(filename, "a", encoding="utf-8") as fileObj:
            print("Added {0} to {1}".format(action, filename))
            fileObj.write('{0} = "{1}"\n'.format(action, shortcut))
            fileObj.close()


# Test code

def print_info():
    for name in ShortcutUtil.data.keys():
        print("{0}: {1}".format(name, len(ShortcutUtil.data[name])))
    for name in ShortcutUtil.getListCustomShortcuts():
        print("{0}: {1}".format(name, len(ShortcutUtil.readShorcutFile("shortcut_"+name+".py").keys())))

def print_compare(set1, set2):
    if set1 in ShortcutUtil.data.keys():
        keys1 = ShortcutUtil.data[set1].keys()
    else:
        keys1 = ShortcutUtil.readShorcutFile("shortcut_"+set1+".py").keys()
    if set2 in ShortcutUtil.data.keys():
        keys2 = ShortcutUtil.data[set2].keys()
    else:
        keys2 = ShortcutUtil.readShorcutFile("shortcut_"+set2+".py").keys()
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
        data = ShortcutUtil.readShorcutFile("shortcut_"+name+".py")
    for key in data.keys():
        lines.append(str(data[key]) + " : " + key)
    lines.sort()
    print("\n".join(lines))

def fix_custom(name):
    ShortcutUtil.checkCustomShortcutFileValid("shortcut_"+name+".py")

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
        # print_compare("brachys", "syntemno")
        # print_shortcuts("blank")
        # print_shortcuts("brachys")
        # print_shortcuts("micron")
        # print_shortcuts("syntemno")
        print_shortcuts("test1")
        # fix_custom("test1")
