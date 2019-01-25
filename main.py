#! /Users/eliranwong/Desktop/venv/venv/bin/python
# development in progress
# visit https://BibleTools.app for more information

import sys, config, pprint
from PySide2.QtWidgets import QApplication
from gui import MainWindow

def setupMainWindow():
    # set full screen size
    availableGeometry = app.desktop().availableGeometry(mainWindow)
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
    fileObj.write("myGoogleApiKey = "+pprint.pformat(config.myGoogleApiKey))
    fileObj.write("\nfontSize = "+pprint.pformat(config.fontSize))
    fileObj.write("\nmainText = "+pprint.pformat(config.mainText))
    fileObj.write("\nmainB = "+pprint.pformat(config.mainB))
    fileObj.write("\nmainC = "+pprint.pformat(config.mainC))
    fileObj.write("\nmainV = "+pprint.pformat(config.mainV))
    fileObj.write("\nstudyText = "+pprint.pformat(config.studyText))
    fileObj.write("\nstudyB = "+pprint.pformat(config.studyB))
    fileObj.write("\nstudyC = "+pprint.pformat(config.studyC))
    fileObj.write("\nstudyV = "+pprint.pformat(config.studyV))
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
    initial_mainTextCommand = mainHistory[len(mainHistory) - 1]
executeInitialTextCommand(initial_mainTextCommand)

# execute initial command in study view
studyHistory = config.history["study"]
initial_studyTextCommand = studyHistory[len(studyHistory) - 1]
executeInitialTextCommand(initial_studyTextCommand, "study")

setCurrentRecord()

sys.exit(app.exec_())