# development in progress
# visit https://BibleTools.app for more information

import sys
from PySide2.QtWidgets import QApplication
from guiMainWindow import MainWindow

app = QApplication(sys.argv)
mainWindow = MainWindow()

# set full screen size
availableGeometry = app.desktop().availableGeometry(mainWindow)
mainWindow.resize(availableGeometry.width(), availableGeometry.height())

mainWindow.show()

sys.exit(app.exec_())