# development in progress
# visit https://BibleTools.app for more information

import sys, config, pprint
from PySide2.QtWidgets import QApplication
from guiMainWindow import MainWindow

def saveDataOnExit():
    fileObj = open("config.py", "w")
    fileObj.write("mainText = "+pprint.pformat(config.mainText))
    fileObj.close()

app = QApplication(sys.argv)
app.aboutToQuit.connect(saveDataOnExit)

mainWindow = MainWindow()
# set full screen size
availableGeometry = app.desktop().availableGeometry(mainWindow)
mainWindow.resize(availableGeometry.width(), availableGeometry.height())
mainWindow.show()

sys.exit(app.exec_())