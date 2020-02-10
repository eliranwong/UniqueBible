#!venv/bin/python

# UniqueBible.app
# a cross-platform desktop bible application
# For more information on this application, visit https://BibleTools.app or https://UniqueBible.app.

import os

# File "config.py" is essential for running module "config"
# Create file "config.py" if it is missing.
if not os.path.isfile("config.py"):
    open("config.py", "w", encoding="utf-8").close()

import config

# Check current version
with open("UniqueBibleAppVersion.txt", "r", encoding="utf-8") as fileObject:
    text = fileObject.read()
    current_version = float(text)
# update current version in config
if not hasattr(config, "version") or current_version > config.version:
    config.version = current_version

# Default settings for configurations:

# Personal google api key for display of google maps
if not hasattr(config, "testing"):
    config.testing = False
# Personal google api key for display of google maps
if not hasattr(config, "myGoogleApiKey"):
    config.myGoogleApiKey = ""
# Options to always display static maps even "myGoogleApiKey" is not empty: True / False
if not hasattr(config, "alwaysDisplayStaticMaps"):
    config.alwaysDisplayStaticMaps = False
# Options to use remote control: True / False
# This feature is created for use in church settings.
# If True, users can use an additional command field, in an additional window, to control the content being displayed, even the main window of UniqueBible.app is displayed on extended screen.
if not hasattr(config, "remoteControl"):
    config.remoteControl = False
# Start full-screen on Linux os
if not hasattr(config, "linuxStartFullScreen"):
    config.linuxStartFullScreen = False
# Show text-to-speech feature on Linux os
if not hasattr(config, "showTtsOnLinux"):
    config.showTtsOnLinux = False
# Options to use ibus as input method: True / False
# This option may be useful on some Linux systems, where qt4 and qt5 applications use different input method variables.
if not hasattr(config, "ibus"):
    config.ibus = False
# Options to use built-in virtual keyboards: True / False
if not hasattr(config, "virtualKeyboard"):
    config.virtualKeyboard = False
# Specify the "open" command on Windows
if not hasattr(config, "openWindows"):
    config.openWindows = "start"
# Specify the "open" command on macOS
if not hasattr(config, "openMacos"):
    config.openMacos = "open"
# Specify the "open" command on Linux
if not hasattr(config, "openLinux"):
    config.openLinux = "xdg-open"
# Specify the command to open pdf file on Linux
if not hasattr(config, "openLinuxPdf"):
    config.openLinuxPdf = "xdg-open"
# Specify the folder path of resources
if not hasattr(config, "marvelData"):
    config.marvelData = "marvelData"
# Specify the folder path of music files
if not hasattr(config, "musicFolder"):
    config.musicFolder = "music"
# Specify the folder path of video files
if not hasattr(config, "videoFolder"):
    config.videoFolder = "video"
# Specify the number of tabs for bible reading and workspace
if not hasattr(config, "numberOfTab"):
    config.numberOfTab = 5
# Options to convert all bible book abbreviations to standard ones: YES / NO
if not hasattr(config, "parserStandarisation"):
    config.parserStandarisation = "NO"
# Options of language of book abbreviations: ENG / TC / SC
if not hasattr(config, "standardAbbreviation"):
    config.standardAbbreviation = "ENG"
# Option to set a customised language for google-translate
# References: https://cloud.google.com/translate/docs/languages
# Use gui "Set my Language" dialog, from menu bar, to set "userLanguage".
if not hasattr(config, "userLanguage"):
    config.userLanguage = ""
# Option to use interface translated into userLanguage: True / False
if not hasattr(config, "userLanguageInterface"):
    config.userLanguageInterface = False
# Option to show English options for google translate on right-click context menu: True / False
if not hasattr(config, "showGoogleTranslateEnglishOptions"):
    config.showGoogleTranslateEnglishOptions = False
# Option to show Chinese options for google translate on right-click context menu: True / False
if not hasattr(config, "showGoogleTranslateChineseOptions"):
    config.showGoogleTranslateChineseOptions = False
# Option to copy automatically to clipboard the result of accessing Google Translate: True / False
if not hasattr(config, "autoCopyGoogleTranslateOutput"):
    config.autoCopyGoogleTranslateOutput = True
# Option to copy automatically to clipboard the output of Chinese pinyin conversion: True / False
if not hasattr(config, "autoCopyChinesePinyinOutput"):
    config.autoCopyChinesePinyinOutput = True
# Option to display verse number in a range of verses: True / False
# e.g. Try entering in command field "Ps 23:1; Ps 23:1-3; Ps 23:1-24:3"
if not hasattr(config, "showVerseNumbersInRange"):
    config.showVerseNumbersInRange = True
# Options to open chapter / verse note on Study Window after saving: True / False
if not hasattr(config, "openBibleNoteAfterSave"):
    config.openBibleNoteAfterSave = False
# Options to export all embedded images displayed on Study Window: True / False
if not hasattr(config, "exportEmbeddedImages"):
    config.exportEmbeddedImages = True
# Options to add open image action with a single click: True / False
if not hasattr(config, "clickToOpenImage"):
    config.clickToOpenImage = True
# Options to use landscape mode: True / False
if not hasattr(config, "landscapeMode"):
    config.landscapeMode = True
# Options for NOT displaying any toolbars on startup: True / False
if not hasattr(config, "noToolBar"):
    config.noToolBar = False
# Options to display the top toolbar only, with all other toolbars hidden: True / False
if not hasattr(config, "topToolBarOnly"):
    config.topToolBarOnly = False
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
# Default font size of content in main window and workspace
if not hasattr(config, "fontSize"):
    config.fontSize = 17
# Default font
if not hasattr(config, "font"):
    config.font = ""
# Default Chinese font
if not hasattr(config, "fontChinese"):
    config.fontChinese = ""
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
# Set your favourite version here
if not hasattr(config, "favouriteBible"):
    config.favouriteBible = "OHGBi"
# Options to display "favouriteBible" together with the main version for reading multiple references: True / False
if not hasattr(config, "addFavouriteToMultiRef"):
    config.addFavouriteToMultiRef = False
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
    config.book = "Harmonies_and_Parallels"
# Option to open book content on a new window
if not hasattr(config, "bookOnNewWindow"):
    config.bookOnNewWindow = False
# Option to overwrite font in book modules
if not hasattr(config, "overwriteBookFont"):
    config.overwriteBookFont = True
# Option to overwrite font size in book modules
if not hasattr(config, "overwriteBookFontSize"):
    config.overwriteBookFontSize = True
# List of favourite book modules
# Only the first 10 books are shown on menu bar
if not hasattr(config, "favouriteBooks"):
    config.favouriteBooks = ["Harmonies_and_Parallels", "Bible_Promises", "Timelines", "Maps_ASB", "Maps_NET"]
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
# Installed Formatted Bibles
if not hasattr(config, "installHistory"):
    config.installHistory = {}
# for checking if note editor is currently open
config.noteOpened = False
# for checking if external file is repeatedly opened
config.lastOpenedFile = ""
# for checking if an url is repeatedly opened
config.lastOpenedUrl = ""
# for checking if an image is repeatedly opened
config.lastOpenedImage = ""
# set show information to True
if not hasattr(config, "showInformation"):
    config.showInformation = True

import sys, pprint, platform
from PySide2.QtWidgets import QApplication
from gui import MainWindow

# Set screen size at first launch
def setupMainWindow():
    # check screen size
    availableGeometry = app.desktop().availableGeometry(mainWindow)
    # Check os with platform.system() or sys.platform
    # Linux / Darwin / Windows
    if platform.system() == "Linux" and not config.linuxStartFullScreen:
        # Launching the app in full screen in some Linux distributions makes the app too sticky to be resized.
        # Below is a workaround, loading the app in 4/5 of the screen size.
        mainWindow.resize(availableGeometry.width() * 4/5, availableGeometry.height() * 4/5)
    elif platform.system() == "Windows":
        mainWindow.showMaximized()
    else:
        # macOS or Linux set to fullscreen
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
    config.bookSearchString = ""
    config.noteSearchString = ""
    configs = (
        #("version", config.version),
        ("testing", config.testing),
        ("myGoogleApiKey", config.myGoogleApiKey),
        ("alwaysDisplayStaticMaps", config.alwaysDisplayStaticMaps),
        ("remoteControl", config.remoteControl),
        ("openWindows", config.openWindows),
        ("openMacos", config.openMacos),
        ("openLinux", config.openLinux),
        ("openLinuxPdf", config.openLinuxPdf),
        ("linuxStartFullScreen", config.linuxStartFullScreen),
        ("showTtsOnLinux", config.showTtsOnLinux),
        ("ibus", config.ibus),
        ("virtualKeyboard", config.virtualKeyboard),
        ("marvelData", config.marvelData),
        ("musicFolder", config.musicFolder),
        ("videoFolder", config.videoFolder),
        ("numberOfTab", config.numberOfTab),
        ("parserStandarisation", config.parserStandarisation),
        ("standardAbbreviation", config.standardAbbreviation),
        ("userLanguage", config.userLanguage),
        ("userLanguageInterface", config.userLanguageInterface),
        ("showGoogleTranslateEnglishOptions", config.showGoogleTranslateEnglishOptions),
        ("showGoogleTranslateChineseOptions", config.showGoogleTranslateChineseOptions),
        ("autoCopyGoogleTranslateOutput", config.autoCopyGoogleTranslateOutput),
        ("autoCopyChinesePinyinOutput", config.autoCopyChinesePinyinOutput),
        ("showVerseNumbersInRange", config.showVerseNumbersInRange),
        ("openBibleNoteAfterSave", config.openBibleNoteAfterSave),
        ("exportEmbeddedImages", config.exportEmbeddedImages),
        ("clickToOpenImage", config.clickToOpenImage),
        ("landscapeMode", config.landscapeMode),
        ("noToolBar", config.noToolBar),
        ("topToolBarOnly", config.topToolBarOnly),
        ("toolBarIconFullSize", config.toolBarIconFullSize),
        ("parallelMode", config.parallelMode),
        ("instantMode", config.instantMode),
        ("instantInformationEnabled", config.instantInformationEnabled),
        ("fontSize", config.fontSize),
        ("font", config.font),
        ("fontChinese", config.fontChinese),
        ("noteEditorFontSize", config.noteEditorFontSize),
        ("readFormattedBibles", config.readFormattedBibles),
        ("addTitleToPlainChapter", config.addTitleToPlainChapter),
        ("hideLexicalEntryInBible", config.hideLexicalEntryInBible),
        ("importDoNotStripStrongNo", config.importDoNotStripStrongNo),
        ("importDoNotStripMorphCode", config.importDoNotStripMorphCode),
        ("importAddVerseLinebreak", config.importAddVerseLinebreak),
        ("importRtlOT", config.importRtlOT),
        ("originalTexts", config.originalTexts),
        ("rtlTexts", config.rtlTexts),
        ("openBibleInMainViewOnly", config.openBibleInMainViewOnly),
        ("mainText", config.mainText),
        ("mainB", config.mainB),
        ("mainC", config.mainC),
        ("mainV", config.mainV),
        ("favouriteBible", config.favouriteBible),
        ("addFavouriteToMultiRef", config.addFavouriteToMultiRef),
        ("studyText", config.studyText),
        ("studyB", config.studyB),
        ("studyC", config.studyC),
        ("studyV", config.studyV),
        ("commentaryText", config.commentaryText),
        ("commentaryB", config.commentaryB),
        ("commentaryC", config.commentaryC),
        ("commentaryV", config.commentaryV),
        ("topic", config.topic),
        ("dictionary", config.dictionary),
        ("encyclopedia", config.encyclopedia),
        ("book", config.book),
        ("bookOnNewWindow", config.bookOnNewWindow),
        ("overwriteBookFont", config.overwriteBookFont),
        ("overwriteBookFontSize", config.overwriteBookFontSize),
        ("favouriteBooks", config.favouriteBooks),
        ("bookSearchString", config.bookSearchString),
        ("noteSearchString", config.noteSearchString),
        ("thirdDictionary", config.thirdDictionary),
        ("defaultLexiconStrongH", config.defaultLexiconStrongH),
        ("defaultLexiconStrongG", config.defaultLexiconStrongG),
        ("defaultLexiconETCBC", config.defaultLexiconETCBC),
        ("defaultLexiconLXX", config.defaultLexiconLXX),
        ("defaultLexiconGK", config.defaultLexiconGK),
        ("defaultLexiconLN", config.defaultLexiconLN),
        ("historyRecordAllowed", config.historyRecordAllowed),
        ("currentRecord", {'main': 0, 'study': 0}),
        ("history", config.history),
        ("installHistory", config.installHistory),
    )
    with open("config.py", "w", encoding="utf-8") as fileObj:
        for name, value in configs:
            fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
        if hasattr(config, "translationLanguage"):
            fileObj.write("{0} = {1}\n".format("translationLanguage", pprint.pformat(config.translationLanguage)))
#        if hasattr(config, "translation"):
#            fileObj.write("{0} = {1}\n".format("translation", pprint.pformat(config.translation)))

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
