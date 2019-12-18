#!venv/bin/python

# UniqueBible.app
# a cross-platform desktop bible application
# For more information on this application, visit https://BibleTools.app or https://UniqueBible.app.

import os

# File "config.py" is essential for running module "config"
# Create file "config.py" if it is missing.
if not os.path.isfile("config.py"):
    fileObj = open("config.py", "w")
    fileObj.close()

import config

# Default settings for configurations:

# Set version number on 1st launch / Update version number
current_version = 6.2
if not hasattr(config, "version") or current_version > config.version:
    config.version = current_version
# Personal google api key for display of google maps
if not hasattr(config, "myGoogleApiKey"):
    config.myGoogleApiKey = ""
# Options to use remote commander: True / False
# This feature is created for use in church settings.
# Users can use this additional command field to control the content being displayed, even the main window of UniqueBible.app is displayed on extended screen.
if not hasattr(config, "remoteCommander"):
    config.remoteCommander = False
# Options to use ibus as input method: True / False
# This option may be useful on some Linux systems, where qt4 and qt5 applications use different input method variables.
if not hasattr(config, "ibus"):
    config.ibus = False
# Options to use built-in virtual keyboards: True / False
if not hasattr(config, "virtualKeyboard"):
    config.virtualKeyboard = False
# Specify the folder path of resources
if not hasattr(config, "marvelData"):
    config.marvelData = "marvelData"
# Specify the number of tabs for bible reading and workspace
if not hasattr(config, "numberOfTab"):
    config.numberOfTab = 5
# Options to convert all bible book abbreviations to standard ones: YES / NO
if not hasattr(config, "parserStandarisation"):
    config.parserStandarisation = "NO"
# Options of language of book abbreviations: ENG / TC / SC
if not hasattr(config, "standardAbbreviation"):
    config.standardAbbreviation = "ENG"
# Options to use landscape mode: True / False
if not hasattr(config, "landscapeMode"):
    config.landscapeMode = True
# Options for NOT displaying any toolbars on startup: True / False
if not hasattr(config, "noToolBar"):
    config.noToolBar = False
# Options for displaying a single toolbar only: True / False
if not hasattr(config, "singleToolBar"):
    config.singleToolBar = False
# Options to use large sets of icons: True / False
if not hasattr(config, "toolBarIconFullSize"):
    config.toolBarIconFullSize = False
# Options on parallel mode: 0, 1, 2, 3
if not hasattr(config, "parallelMode"):
    config.parallelMode = 1
# Options to display the window showing instant information: 0, 1
if not hasattr(config, "instantMode"):
    config.instantMode = 1
# Options to trigger instant information: True / False
if not hasattr(config, "instantInformationEnabled"):
    config.instantInformationEnabled = True
# Default font
if not hasattr(config, "font"):
    config.font = ""
# Default font size of content in main window and workspace
if not hasattr(config, "fontSize"):
    config.fontSize = 120
# Default font size of content in note editor
if not hasattr(config, "noteEditorFontSize"):
    config.noteEditorFontSize = 14
# Options to display bibles in formatted layout or paragraphs: True / False
# "False" here means displaying bible verse in plain format, with each one on a single line.
if not hasattr(config, "readFormattedBibles"):
    config.readFormattedBibles = True
# Options to add sub-headings when "readFormattedBibles" is set to "False": True / False
if not hasattr(config, "addTitleToPlainChapter"):
    config.addTitleToPlainChapter = True
# Options to hide lexical entries or Strong's numbers: True / False
if not hasattr(config, "hideLexicalEntryInBible"):
    config.hideLexicalEntryInBible = False
# Import setting - add a line break after each verse: True / False
if not hasattr(config, "importAddVerseLinebreak"):
    config.importAddVerseLinebreak = False
# Import setting - keep Strong's number for search: True / False
if not hasattr(config, "importDoNotStripStrongNo"):
    config.importDoNotStripStrongNo = False
# Import setting - keep morphology codes for search: True / False
if not hasattr(config, "importDoNotStripMorphCode"):
    config.importDoNotStripMorphCode = False
# Import setting - import text in right-to-left direction: True / False
if not hasattr(config, "importRtlOT"):
    config.importRtlOT = False
# List of modules, which contains Hebrew / Greek texts
if not hasattr(config, "originalTexts"):
    config.originalTexts = ['original', 'MOB', 'MAB', 'MTB', 'MIB', 'MPB', 'OHGB', 'OHGBi', 'LXX', 'LXX1', 'LXX1i', 'LXX2', 'LXX2i']
# List of modules, which contains right-to-left texts on old testament
if not hasattr(config, "rtlTexts"):
    config.rtlTexts = ["original", "MOB", "MAB", "MIB", "MPB", "OHGB", "OHGBi"]
# Open bible references on main window instead of workspace: Ture / False
if not hasattr(config, "openBibleInMainViewOnly"):
    config.openBibleInMainViewOnly = False
# Last-opened bible version and passage to be displayed on main window
if not hasattr(config, "mainText"):
    config.mainText = "KJV"
if not hasattr(config, "mainB"):
    config.mainB = 1
if not hasattr(config, "mainC"):
    config.mainC = 1
if not hasattr(config, "mainV"):
    config.mainV = 1
# Last-opened bible version and passage to be displayed on workspace
if not hasattr(config, "studyText"):
    config.studyText = "NET"
if not hasattr(config, "studyB"):
    config.studyB = 43
if not hasattr(config, "studyC"):
    config.studyC = 3
if not hasattr(config, "studyV"):
    config.studyV = 16
# Additional version displayed in search results
# This version is displayed in parallel with the version being searched.
if not hasattr(config, "iSearchVersion"):
    config.iSearchVersion = "OHGB"
# Options to display multiple verses using both main text version and "iSearchVersion" in parallel format: True / False
if not hasattr(config, "extractParallel"):
    config.extractParallel = False
# Last-opened commentary text and passage
if not hasattr(config, "commentaryText"):
    config.commentaryText = "CBSC"
if not hasattr(config, "commentaryB"):
    config.commentaryB = 43
if not hasattr(config, "commentaryC"):
    config.commentaryC = 3
if not hasattr(config, "commentaryV"):
    config.commentaryV = 16
# Last-opened module for topical studies
if not hasattr(config, "topic"):
    config.topic = "EXLBT"
# Last-opened dictionary module
if not hasattr(config, "dictionary"):
    config.dictionary = "EAS"
# Last-opened encyclopedia module
if not hasattr(config, "encyclopedia"):
    config.encyclopedia = "ISB"
# Last-opened book module
if not hasattr(config, "book"):
    config.book = "Timelines"
# Last string entered for searching book
if not hasattr(config, "bookSearchString"):
    config.bookSearchString = ""
# Last string entered for searching note
if not hasattr(config, "noteSearchString"):
    config.noteSearchString = ""
# Last-opened third-party dictionary
if not hasattr(config, "thirdDictionary"):
    config.thirdDictionary = "webster"
# Default Hebrew lexicon
if not hasattr(config, "defaultLexiconStrongH"):
    config.defaultLexiconStrongH = "TBESH"
# Default Greek lexicon
if not hasattr(config, "defaultLexiconStrongG"):
    config.defaultLexiconStrongG = "TBESG"
# Default lexicon based on ETCBC data
if not hasattr(config, "defaultLexiconETCBC"):
    config.defaultLexiconETCBC = "ConcordanceMorphology"
# Default lexicon on LXX words
if not hasattr(config, "defaultLexiconLXX"):
    config.defaultLexiconLXX = "LXX"
# Default lexicon on GK entries
if not hasattr(config, "defaultLexiconGK"):
    config.defaultLexiconGK = "MCGED"
# Default lexicon on LN entries
if not hasattr(config, "defaultLexiconLN"):
    config.defaultLexiconLN = "LN"
# Maximum number of history records allowed to be stored
if not hasattr(config, "historyRecordAllowed"):
    config.historyRecordAllowed = 50
# Indexes of last-opened records
if not hasattr(config, "currentRecord"):
    config.currentRecord = {"main": 0, "study": 0}
# History records are kept in config.history
if not hasattr(config, "history"):
    config.history = {"external": ["note_editor.uba"], "main": ["BIBLE:::KJV:::Genesis 1:1"], "study": ["BIBLE:::NET:::John 3:16"]}

import sys, pprint, platform
from PySide2.QtWidgets import QApplication
from gui import MainWindow

# Set screen size at first launch
def setupMainWindow():
    # check screen size
    availableGeometry = app.desktop().availableGeometry(mainWindow)
    # Check os with platform.system() or sys.platform
    # Linux / Darwin / Windows
    if platform.system() == "Linux":
        # Launching the app in full screen in some Linux distributions makes the app too sticky to be resized.
        # Below is a workaround, loading the app in 4/5 of the screen size.
        mainWindow.resize(availableGeometry.width() * 4/5, availableGeometry.height() * 4/5)
    elif platform.system() == "Windows":
        mainWindow.showMaximized()
    else:
        # macOS
        mainWindow.resize(availableGeometry.width(), availableGeometry.height())
    mainWindow.show()

def executeInitialTextCommand(textCommand, source="main"):
    if source == "main":
        mainWindow.textCommandLineEdit.setText(textCommand)
    mainWindow.runTextCommand(textCommand, True, source)

def setCurrentRecord():
    mainRecordPosition = len(config.history["main"]) - 1
    studyRecordPosition = len(config.history["study"]) - 1
    config.currentRecord = {'main': mainRecordPosition, 'study': studyRecordPosition}

# Save configurations on exit
def saveDataOnExit():
    configs = (
        ("version = ", config.version),
        ("\nmyGoogleApiKey = ", config.myGoogleApiKey),
        ("\nremoteCommander = ", config.remoteCommander),
        ("\nibus = ", config.ibus),
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
        ("\nfont = ", config.font),
        ("\nfontSize = ", config.fontSize),
        ("\nnoteEditorFontSize = ", config.noteEditorFontSize),
        ("\nreadFormattedBibles = ", config.readFormattedBibles),
        ("\naddTitleToPlainChapter = ", config.addTitleToPlainChapter),
        ("\nhideLexicalEntryInBible = ", config.hideLexicalEntryInBible),
        ("\nimportDoNotStripStrongNo = ", config.importDoNotStripStrongNo),
        ("\nimportDoNotStripMorphCode = ", config.importDoNotStripMorphCode),
        ("\nimportAddVerseLinebreak = ", config.importAddVerseLinebreak),
        ("\nimportRtlOT = ", config.importRtlOT),
        ("\noriginalTexts = ", config.originalTexts),
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


# Set Qt input method variable to use ibus if config.ibus is "True"
if config.ibus:
    os.environ["QT_IM_MODULE"] = "ibus"

# Set Qt input method variable to use Qt virtual keyboards if config.virtualKeyboard is "True"
if config.virtualKeyboard:
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

# Start PySide2 gui
app = QApplication(sys.argv)
# Assign a function to save configurations when the app is closed
app.aboutToQuit.connect(saveDataOnExit)

# Class "MainWindow" is located in file "gui.py"
mainWindow = MainWindow()
setupMainWindow()

# Check if migration is needed for version >= 0.56
mainWindow.checkMigration()

# Execute initial command in main view
initial_mainTextCommand = " ".join(sys.argv[1:])
if not initial_mainTextCommand:
    mainHistory = config.history["main"]
    initial_mainTextCommand = mainHistory[-1]
executeInitialTextCommand(initial_mainTextCommand)

# Execute initial command in study view
studyHistory = config.history["study"]
initial_studyTextCommand = studyHistory[-1]
executeInitialTextCommand(initial_studyTextCommand, "study")

# Set indexes of history records
setCurrentRecord()

sys.exit(app.exec_())
