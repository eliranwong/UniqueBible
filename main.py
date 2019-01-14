# development in progress
# visit https://BibleTools.app for more information

import sys, config, pprint
from PySide2.QtWidgets import QApplication
from guiMainWindow import MainWindow

def setupMainWindow():
    # set full screen size
    availableGeometry = app.desktop().availableGeometry(mainWindow)
    mainWindow.resize(availableGeometry.width(), availableGeometry.height())
    mainWindow.show()

def executeInitialUbCommand(ubCommand):
    mainWindow.ubCommandLineEdit.setText(ubCommand)
    mainWindow.runUbCommand()

def setCurrentRecord():
    mainRecordPosition = len(config.history["main"]) - 1
    parallelRecordPosition = len(config.history["parallel"]) - 1
    currentRecord = {'main': mainRecordPosition, 'parallel': parallelRecordPosition}
    config.currentRecord = currentRecord

def saveDataOnExit():
    fileObj = open("config.py", "w")
    fileObj.write("fontSize = "+pprint.pformat(config.fontSize))
    fileObj.write("\nmainText = "+pprint.pformat(config.mainText))
    fileObj.write("\nmainB = "+pprint.pformat(config.mainB))
    fileObj.write("\nmainC = "+pprint.pformat(config.mainC))
    fileObj.write("\nmainV = "+pprint.pformat(config.mainV))
    fileObj.write("\nhistoryRecordAllowed = "+pprint.pformat(config.historyRecordAllowed))
    fileObj.write("\ncurrentRecord = {'main': 0, 'parallel': 0}")
    fileObj.write("\nhistory = "+pprint.pformat(config.history))
    fileObj.close()

app = QApplication(sys.argv)
app.aboutToQuit.connect(saveDataOnExit)

mainWindow = MainWindow()
setupMainWindow()

initial_ubCommand = " ".join(sys.argv[1:])
if not initial_ubCommand:
    historyMain = config.history["main"]
    initial_ubCommand = historyMain[len(historyMain) - 1]
executeInitialUbCommand(initial_ubCommand)

setCurrentRecord()

sys.exit(app.exec_())