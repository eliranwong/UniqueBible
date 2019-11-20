#! venv/bin/python
# visit https://BibleTools.app for more information

import os

# "config.py" is essential for running UniqueBible.app
# check if missing file "config.py"
if not os.path.isfile("config.py"):
    fileObj = open("config.py", "w")
    fileObj.close()

import config

# setup configurations for 1st launch
# or setup configurations if file "config.py" is missing
# or update configurations after codes are updated
latest_version = 5.3
if not hasattr(config, 'version'):
    config.version = latest_version
elif config.version < latest_version:
    config.version = latest_version
if not hasattr(config, 'myGoogleApiKey'):
    config.myGoogleApiKey = ''
if not hasattr(config, 'virtualKeyboard'):
    config.virtualKeyboard = False
if not hasattr(config, 'marvelData'):
    config.marvelData = 'marvelData'
if not hasattr(config, 'numberOfTab'):
    config.numberOfTab = 5
if not hasattr(config, 'parserStandarisation'):
    config.parserStandarisation = 'NO'
if not hasattr(config, 'standardAbbreviation'):
    config.standardAbbreviation = 'ENG'
if not hasattr(config, 'landscapeMode'):
    config.landscapeMode = True
if not hasattr(config, 'noToolBar'):
    config.noToolBar = False
if not hasattr(config, 'singleToolBar'):
    config.singleToolBar = False
if not hasattr(config, 'toolBarIconFullSize'):
    config.toolBarIconFullSize = False
if not hasattr(config, 'parallelMode'):
    config.parallelMode = 1
if not hasattr(config, 'instantMode'):
    config.instantMode = 1
if not hasattr(config, 'instantInformationEnabled'):
    config.instantInformationEnabled = True
if not hasattr(config, 'fontSize'):
    config.fontSize = 120
if not hasattr(config, 'noteEditorFontSize'):
    config.noteEditorFontSize = 14
if not hasattr(config, 'readFormattedBibles'):
    config.readFormattedBibles = True
if not hasattr(config, 'addTitleToPlainChapter'):
    config.addTitleToPlainChapter = True
if not hasattr(config, 'hideLexicalEntryInBible'):
    config.hideLexicalEntryInBible = False
if not hasattr(config, 'importAddVerseLinebreak'):
    config.importAddVerseLinebreak = False
if not hasattr(config, 'importDoNotStripStrongNo'):
    config.importDoNotStripStrongNo = False
if not hasattr(config, 'importDoNotStripMorphCode'):
    config.importDoNotStripMorphCode = False
if not hasattr(config, 'importRtlOT'):
    config.importRtlOT = False
if not hasattr(config, 'rtlTexts'):
    config.rtlTexts = ["original", "MOB", "MAB", "MIB", "MPB", "OHGB", "OHGBi"]
if not hasattr(config, 'openBibleInMainViewOnly'):
    config.openBibleInMainViewOnly = False
if not hasattr(config, 'mainText'):
    config.mainText = 'KJV'
if not hasattr(config, 'mainB'):
    config.mainB = 1
if not hasattr(config, 'mainC'):
    config.mainC = 1
if not hasattr(config, 'mainV'):
    config.mainV = 1
if not hasattr(config, 'studyText'):
    config.studyText = 'NET'
if not hasattr(config, 'studyB'):
    config.studyB = 43
if not hasattr(config, 'studyC'):
    config.studyC = 3
if not hasattr(config, 'studyV'):
    config.studyV = 16
if not hasattr(config, 'iSearchVersion'):
    config.iSearchVersion = "OHGB"
if not hasattr(config, 'extractParallel'):
    config.extractParallel = False
if not hasattr(config, 'commentaryText'):
    config.commentaryText = 'CBSC'
if not hasattr(config, 'commentaryB'):
    config.commentaryB = 43
if not hasattr(config, 'commentaryC'):
    config.commentaryC = 3
if not hasattr(config, 'commentaryV'):
    config.commentaryV = 16
if not hasattr(config, 'topic'):
    config.topic = 'EXLBT'
if not hasattr(config, 'dictionary'):
    config.dictionary = 'EAS'
if not hasattr(config, 'encyclopedia'):
    config.encyclopedia = 'ISB'
if not hasattr(config, 'book'):
    config.book = 'Timelines'
if not hasattr(config, 'bookSearchString'):
    config.bookSearchString = ''
if not hasattr(config, 'noteSearchString'):
    config.noteSearchString = ''
if not hasattr(config, 'thirdDictionary'):
    config.thirdDictionary = 'webster'
if not hasattr(config, 'defaultLexiconStrongH'):
    config.defaultLexiconStrongH = 'TBESH'
if not hasattr(config, 'defaultLexiconStrongG'):
    config.defaultLexiconStrongG = 'TBESG'
if not hasattr(config, 'defaultLexiconETCBC'):
    config.defaultLexiconETCBC = 'ConcordanceMorphology'
if not hasattr(config, 'defaultLexiconLXX'):
    config.defaultLexiconLXX = 'LXX'
if not hasattr(config, 'defaultLexiconGK'):
    config.defaultLexiconGK = 'MCGED'
if not hasattr(config, 'defaultLexiconLN'):
    config.defaultLexiconLN = 'LN'
if not hasattr(config, 'historyRecordAllowed'):
    config.historyRecordAllowed = 50
if not hasattr(config, 'currentRecord'):
    config.currentRecord = {'main': 0, 'study': 0}
if not hasattr(config, 'history'):
    config.history = {'external': ['Note.docx'], 'main': ['BIBLE:::KJV:::Genesis 1:1'], 'study': ['BIBLE:::NET:::John 3:16']}

import sys, pprint, platform
from PySide2.QtWidgets import QApplication
from gui import MainWindow

def setupMainWindow():
    # set screen size when first opened
    # launching with full screen size in some Linux distributions makes the app too sticky to be resized.
    # check os with platform.system() or sys.platform
    # Linux / Darwin / Windows
    availableGeometry = app.desktop().availableGeometry(mainWindow)
    if platform.system() == "Linux":
        mainWindow.resize(availableGeometry.width() * 4/5, availableGeometry.height() * 4/5)
    elif platform.system() == "Windows":
        mainWindow.showMaximized()
    else:
        mainWindow.resize(availableGeometry.width(), availableGeometry.height())
    mainWindow.show()

def executeInitialTextCommand(textCommand, source="main"):
    if source == "main":
        mainWindow.textCommandLineEdit.setText(textCommand)
    mainWindow.runTextCommand(textCommand, True, source)

def setCurrentRecord():
    mainRecordPosition = len(config.history["main"]) - 1
    studyRecordPosition = len(config.history["study"]) - 1
    currentRecord = {'main': mainRecordPosition, 'study': studyRecordPosition}
    config.currentRecord = currentRecord

def saveDataOnExit():
    #os.environ["QT_IM_MODULE"] = config.im
    configs = (
        ("version = ", config.version),
        ("\nmyGoogleApiKey = ", config.myGoogleApiKey),
        ("\nvirtualKeyboard = ", config.virtualKeyboard),
        ("\nmarvelData = ", config.marvelData),
        ("\nnumberOfTab = ", config.numberOfTab),
        ("\nparserStandarisation = ", config.parserStandarisation),
        ("\nstandardAbbreviation = ", config.standardAbbreviation),
        ("\nlandscapeMode = ", config.landscapeMode),
        ("\nnoToolBar = ", config.noToolBar),
        ("\nsingleToolBar = ", config.singleToolBar),
        ("\ntoolBarIconFullSize = ", config.toolBarIconFullSize),
        ("\nparallelMode = ", config.parallelMode),
        ("\ninstantMode = ", config.instantMode),
        ("\ninstantInformationEnabled = ", config.instantInformationEnabled),
        ("\nfontSize = ", config.fontSize),
        ("\nnoteEditorFontSize = ", config.noteEditorFontSize),
        ("\nreadFormattedBibles = ", config.readFormattedBibles),
        ("\naddTitleToPlainChapter = ", config.addTitleToPlainChapter),
        ("\nhideLexicalEntryInBible = ", config.hideLexicalEntryInBible),
        ("\nimportDoNotStripStrongNo = ", config.importDoNotStripStrongNo),
        ("\nimportDoNotStripMorphCode = ", config.importDoNotStripMorphCode),
        ("\nimportAddVerseLinebreak = ", config.importAddVerseLinebreak),
        ("\nimportRtlOT = ", config.importRtlOT),
        ("\nrtlTexts = ", config.rtlTexts),
        ("\nopenBibleInMainViewOnly = ", config.openBibleInMainViewOnly),
        ("\nmainText = ", config.mainText),
        ("\nmainB = ", config.mainB),
        ("\nmainC = ", config.mainC),
        ("\nmainV = ", config.mainV),
        ("\niSearchVersion = ", config.iSearchVersion),
        ("\nextractParallel = ", config.extractParallel),
        ("\nstudyText = ", config.studyText),
        ("\nstudyB = ", config.studyB),
        ("\nstudyC = ", config.studyC),
        ("\nstudyV = ", config.studyV),
        ("\ncommentaryText = ", config.commentaryText),
        ("\ncommentaryB = ", config.commentaryB),
        ("\ncommentaryC = ", config.commentaryC),
        ("\ncommentaryV = ", config.commentaryV),
        ("\ntopic = ", config.topic),
        ("\ndictionary = ", config.dictionary),
        ("\nencyclopedia = ", config.encyclopedia),
        ("\nbook = ", config.book),
        ("\nbookSearchString = ", config.bookSearchString),
        ("\nnoteSearchString = ", config.noteSearchString),
        ("\nthirdDictionary = ", config.thirdDictionary),
        ("\ndefaultLexiconStrongH = ", config.defaultLexiconStrongH),
        ("\ndefaultLexiconStrongG = ", config.defaultLexiconStrongG),
        ("\ndefaultLexiconETCBC = ", config.defaultLexiconETCBC),
        ("\ndefaultLexiconLXX = ", config.defaultLexiconLXX),
        ("\ndefaultLexiconGK = ", config.defaultLexiconGK),
        ("\ndefaultLexiconLN = ", config.defaultLexiconLN),
        ("\nhistoryRecordAllowed = ", config.historyRecordAllowed),
        ("\ncurrentRecord = ", {'main': 0, 'study': 0}),
        ("\nhistory = ", config.history),
    )
    fileObj = open("config.py", "w")
    for name, value in configs:
        fileObj.write(name+pprint.pformat(value))
    fileObj.close()

#config.im = os.environ["QT_IM_MODULE"]
if config.virtualKeyboard:
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

app = QApplication(sys.argv)
app.aboutToQuit.connect(saveDataOnExit)

mainWindow = MainWindow()
setupMainWindow()

# check if migration is needed for version >= 0.56
mainWindow.checkMigration()

# execute initial command in main view
initial_mainTextCommand = " ".join(sys.argv[1:])
if not initial_mainTextCommand:
    mainHistory = config.history["main"]
    initial_mainTextCommand = mainHistory[-1]
executeInitialTextCommand(initial_mainTextCommand)

# execute initial command in study view
studyHistory = config.history["study"]
initial_studyTextCommand = studyHistory[-1]
executeInitialTextCommand(initial_studyTextCommand, "study")

setCurrentRecord()

sys.exit(app.exec_())
