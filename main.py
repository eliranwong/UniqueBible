#! /Users/Eliran/Desktop/venv/venv/bin/python
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
latest_version = 0.53
if not hasattr(config, 'version'):
    config.version = latest_version
elif config.version < latest_version:
    config.version = latest_version
if not hasattr(config, 'myGoogleApiKey'):
    config.myGoogleApiKey = ''
if not hasattr(config, 'parserStandarisation'):
    config.parserStandarisation = 'YES'
if not hasattr(config, 'instantInformationEnabled'):
    config.instantInformationEnabled = 1
if not hasattr(config, 'fontSize'):
    config.fontSize = 120
if not hasattr(config, 'noteEditorFontSize'):
    config.noteEditorFontSize = 14
if not hasattr(config, 'readFormattedBibles'):
    config.readFormattedBibles = True
if not hasattr(config, 'importAddVerseLinebreak'):
    config.importAddVerseLinebreak = False
if not hasattr(config, 'importDoNotStripStrongNo'):
    config.importDoNotStripStrongNo = False
if not hasattr(config, 'importDoNotStripMorphCode'):
    config.importDoNotStripMorphCode = False
if not hasattr(config, 'importRtlOT'):
    config.importRtlOT = False
if not hasattr(config, 'rtlTexts'):
    config.rtlTexts = ["original", "MOB", "MAB", "MTB", "MIB", "MPB", "OHGB", "OHGBi"]
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
    config.book = 'Simpson_But_God'
if not hasattr(config, 'bookSearchString'):
    config.bookSearchString = ''
if not hasattr(config, 'noteSearchString'):
    config.noteSearchString = ''
if not hasattr(config, 'thirdDictionary'):
    config.thirdDictionary = 'webster'
if not hasattr(config, 'historyRecordAllowed'):
    config.historyRecordAllowed = 50
if not hasattr(config, 'currentRecord'):
    config.currentRecord = {'main': 0, 'study': 0}
if not hasattr(config, 'history'):
    config.history = {'external': ['Note.docx'], 'main': ['Genesis 1:1'], 'study': ['BIBLE:::NET:::John 3:16']}

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
    fileObj = open("config.py", "w")
    fileObj.write("version = "+pprint.pformat(config.version))
    fileObj.write("\nmyGoogleApiKey = "+pprint.pformat(config.myGoogleApiKey))
    fileObj.write("\nparserStandarisation = "+pprint.pformat(config.parserStandarisation))
    fileObj.write("\ninstantInformationEnabled = "+pprint.pformat(config.instantInformationEnabled))
    fileObj.write("\nfontSize = "+pprint.pformat(config.fontSize))
    fileObj.write("\nnoteEditorFontSize = "+pprint.pformat(config.noteEditorFontSize))
    fileObj.write("\nreadFormattedBibles = "+pprint.pformat(config.readFormattedBibles))
    fileObj.write("\nimportDoNotStripStrongNo = "+pprint.pformat(config.importDoNotStripStrongNo))
    fileObj.write("\nimportDoNotStripMorphCode = "+pprint.pformat(config.importDoNotStripMorphCode))
    fileObj.write("\nimportAddVerseLinebreak = "+pprint.pformat(config.importAddVerseLinebreak))
    fileObj.write("\nimportRtlOT = "+pprint.pformat(config.importRtlOT))
    fileObj.write("\nrtlTexts = "+pprint.pformat(config.rtlTexts))
    fileObj.write("\nmainText = "+pprint.pformat(config.mainText))
    fileObj.write("\nmainB = "+pprint.pformat(config.mainB))
    fileObj.write("\nmainC = "+pprint.pformat(config.mainC))
    fileObj.write("\nmainV = "+pprint.pformat(config.mainV))
    fileObj.write("\nstudyText = "+pprint.pformat(config.studyText))
    fileObj.write("\nstudyB = "+pprint.pformat(config.studyB))
    fileObj.write("\nstudyC = "+pprint.pformat(config.studyC))
    fileObj.write("\nstudyV = "+pprint.pformat(config.studyV))
    fileObj.write("\ncommentaryText = "+pprint.pformat(config.commentaryText))
    fileObj.write("\ncommentaryB = "+pprint.pformat(config.commentaryB))
    fileObj.write("\ncommentaryC = "+pprint.pformat(config.commentaryC))
    fileObj.write("\ncommentaryV = "+pprint.pformat(config.commentaryV))
    fileObj.write("\ntopic = "+pprint.pformat(config.topic))
    fileObj.write("\ndictionary = "+pprint.pformat(config.dictionary))
    fileObj.write("\nencyclopedia = "+pprint.pformat(config.encyclopedia))
    fileObj.write("\nbook = "+pprint.pformat(config.book))
    fileObj.write("\nbookSearchString = "+pprint.pformat(config.bookSearchString))
    fileObj.write("\nnoteSearchString = "+pprint.pformat(config.noteSearchString))
    fileObj.write("\nthirdDictionary = "+pprint.pformat(config.thirdDictionary))
    fileObj.write("\nhistoryRecordAllowed = "+pprint.pformat(config.historyRecordAllowed))
    fileObj.write("\ncurrentRecord = {'main': 0, 'study': 0}")
    fileObj.write("\nhistory = "+pprint.pformat(config.history))
    fileObj.close()

app = QApplication(sys.argv)
app.aboutToQuit.connect(saveDataOnExit)

mainWindow = MainWindow()
setupMainWindow()

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