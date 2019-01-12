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
    fileObj.write("mainText = "+pprint.pformat(config.mainText))
    fileObj.write("\nhistory = "+pprint.pformat(config.history))
    currentRecord = {'main': 0, 'parallel': 0}
    fileObj.write("\ncurrentRecord = "+pprint.pformat(currentRecord))
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