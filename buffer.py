from PySide2.QtWidgets import QMainWindow
from gui.AlephMainWindow import AlephMainWindow
from gui.ClassicMainWindow import ClassicMainWindow
import sys, platform, config

class BufferWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        if config.menuLayout == "aleph":
            self.mainWindow = AlephMainWindow()
        else:
            self.mainWindow = ClassicMainWindow()

#    def create_menu(self):
#        print("menu")

    # Set screen size at first launch
    def setupMainWindow(self, availableGeometry):
        # Check os with platform.system() or sys.platform
        # Linux / Darwin / Windows
        if platform.system() == "Linux" and not config.linuxStartFullScreen:
            # Launching the app in full screen in some Linux distributions makes the app too sticky to be resized.
            # Below is a workaround, loading the app in 4/5 of the screen size.
            self.mainWindow.resize(availableGeometry.width() * 4 / 5, availableGeometry.height() * 4 / 5)
        elif platform.system() == "Windows":
            self.mainWindow.showMaximized()
        else:
            # macOS or Linux set to fullscreen
            self.mainWindow.resize(availableGeometry.width(), availableGeometry.height())
        self.mainWindow.show()

        # Check if migration is needed for version >= 0.56
        self.mainWindow.checkMigration()

    def executeInitialTextCommand(self, textCommand, source="main"):
        if source == "main":
            self.mainWindow.textCommandLineEdit.setText(textCommand)
        self.mainWindow.runTextCommand(textCommand, True, source)

    def setCurrentRecord(self):
        mainRecordPosition = len(config.history["main"]) - 1
        studyRecordPosition = len(config.history["study"]) - 1
        config.currentRecord = {'main': mainRecordPosition, 'study': studyRecordPosition}
