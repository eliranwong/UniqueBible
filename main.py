#!venv/bin/python

# UniqueBible.app
# a cross-platform desktop bible application
# For more information on this application, visit https://BibleTools.app or https://UniqueBible.app.
import os, platform, logging
import logging.handlers as handlers
import sys

# Create files for user customisation
# "config.py" is essential for running module "config".
# "custom.css" is essential for custom css feature.
from gui.MainWindow import MainWindow

customCssFile = os.path.join("htmlResources", "css", "custom.css")
userFiles = ("config.py", customCssFile)
for userFile in userFiles:
    if not os.path.isfile(userFile):
        open(userFile, "w", encoding="utf-8").close()

import config

# Setup config values
from util.ConfigUtil import ConfigUtil
ConfigUtil.setup()

# Setup logging
logger = logging.getLogger('uba')
if config.enableLogging:
    logger.setLevel(logging.DEBUG)
    logHandler = handlers.TimedRotatingFileHandler('uba.log', when='D', interval=1, backupCount=0)
    logHandler.setLevel(logging.DEBUG)
    logger.addHandler(logHandler)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
else:
    logger.addHandler(logging.NullHandler())

# Setup menu shortcut configuration file
from util.ShortcutUtil import ShortcutUtil
ShortcutUtil.setup(config.menuShortcuts)

# Setup GUI windows
from PySide2.QtWidgets import QApplication, QStyleFactory
from themes import Themes

# [Optional] qt-material
# qt-material have to be imported after PySide2
if config.qtMaterial:
    try:
        from qt_material import apply_stylesheet
    except:
        config.qtMaterial = False
        ConfigUtil.messageFeatureNotEnabled("Qt Materials Themes", "qt-material")

# Set screen size at first launch
def setupMainWindow(availableGeometry):
    # Check os with platform.system() or sys.platform
    # Linux / Darwin / Windows
    if platform.system() == "Linux" and not config.linuxStartFullScreen:
        # Launching the app in full screen in some Linux distributions makes the app too sticky to be resized.
        # Below is a workaround, loading the app in 4/5 of the screen size.
        mainWindow.resize(availableGeometry.width() * 4 / 5, availableGeometry.height() * 4 / 5)
    elif platform.system() == "Windows":
        mainWindow.showMaximized()
    else:
        # macOS or Linux set to fullscreen
        mainWindow.resize(availableGeometry.width(), availableGeometry.height())
    mainWindow.show()

    # Check if migration is needed for version >= 0.56
    mainWindow.checkMigration()

def executeInitialTextCommand(textCommand, source="main"):
    if source == "main":
        mainWindow.textCommandLineEdit.setText(textCommand)
    mainWindow.runTextCommand(textCommand, True, source)

def setCurrentRecord():
    mainRecordPosition = len(config.history["main"]) - 1
    studyRecordPosition = len(config.history["study"]) - 1
    config.currentRecord = {'main': mainRecordPosition, 'study': studyRecordPosition}

def exitApplication():
    mainWindow.textCommandParser.stopTtsAudio()
    ConfigUtil.save()

# Set Qt input method variable to use fcitx / ibus if config.fcitx / config.ibus is "True"
if config.fcitx:
    os.environ["QT_IM_MODULE"] = "fcitx"
elif config.ibus:
    os.environ["QT_IM_MODULE"] = "ibus"

# Set Qt input method variable to use Qt virtual keyboards if config.virtualKeyboard is "True"
if config.virtualKeyboard:
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

# Start PySide2 gui
app = QApplication(sys.argv)
# Assign a function to save configurations when the app is closed.
app.aboutToQuit.connect(exitApplication)
# Apply window style
if config.windowStyle and config.windowStyle in QStyleFactory.keys():
    app.setStyle(config.windowStyle)
# Apply theme style
if config.qtMaterial and config.qtMaterialTheme:
    apply_stylesheet(app, theme=config.qtMaterialTheme)
    config.theme = "dark" if config.qtMaterialTheme.startswith("dark_") else "default"
else:
    app.setPalette(Themes.getPalette())

# Setup main window
mainWindow = MainWindow()

# Check screen size
availableGeometry = app.desktop().availableGeometry(mainWindow)
setupMainWindow(availableGeometry)

# Execute initial command on Bible Window
initial_mainTextCommand = " ".join(sys.argv[1:])
if not initial_mainTextCommand:
    mainHistory = config.history["main"]
    initial_mainTextCommand = mainHistory[-1]
try:
    executeInitialTextCommand(initial_mainTextCommand)
except:
    print("Failed to execute '{0}' on startup.".format(initial_mainTextCommand))

# Execute initial command on Study Window
studyHistory = config.history["study"]
initial_studyTextCommand = studyHistory[-1]
try:
    executeInitialTextCommand(initial_studyTextCommand, "study")
except:
    print("Failed to execute '{0}' on startup.".format(initial_studyTextCommand))

# Set indexes of history records
setCurrentRecord()

# Startup macro
mainWindow.runMacro(config.startupMacro)

def global_excepthook(type, value, traceback):
    logger.error("Uncaught exception", exc_info=(type, value, traceback))
    print(traceback.format_exc())

sys.excepthook = global_excepthook

sys.exit(app.exec_())
