# UniqueBible.app
# a cross-platform desktop bible application
# For more information on this application, visit https://BibleTools.app or https://UniqueBible.app.
import os, platform, re, sys, subprocess, config
from util.FileUtil import FileUtil
from util.ConfigUtil import ConfigUtil
# The following two imports must not be placed before checkup utilities
import requests
from util.UpdateUtil import UpdateUtil

# Run startup plugins
def runStartupPlugins():
    if config.enablePlugins:
        for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "startup"), "py"):
            if not plugin in config.excludeStartupPlugins:
                script = os.path.join(os.getcwd(), "plugins", "startup", "{0}.py".format(plugin))
                config.mainWindow.execPythonFile(script)

# Check if database migration is needed
def checkMigration():
    if config.version >= 0.56 and not config.databaseConvertedOnStartup:
        try:
            print("Updating database ... please wait ...")
            biblesSqlite = BiblesSqlite()
            biblesWithBothVersions = biblesSqlite.migratePlainFormattedBibles()
            if biblesWithBothVersions:
                biblesSqlite.proceedMigration(biblesWithBothVersions)
            if config.migrateDatabaseBibleNameToDetailsTable:
                biblesSqlite.migrateDatabaseContent()
            del biblesSqlite
            config.databaseConvertedOnStartup = True
            print("Updated!")
        except:
            pass

# manage latest update
def checkApplicationUpdateCli():
    try:
        print("Checking the latest version ...")
        checkFile = "{0}UniqueBibleAppVersion.txt".format(UpdateUtil.repository)
        # latest version number is indicated in file "UniqueBibleAppVersion.txt"
        request = requests.get(checkFile, timeout=5)
        if request.status_code == 200:
            # tell the rest that internet connection is available
            config.internet = True
            # compare with user's current version
            if not UpdateUtil.currentIsLatest(config.version, request.text):
                print(f"You are runing an older version {config.version}.")
                if not config.terminalAutoUpdate:
                    print(f"Run '.update' to update to the latest version {request.text}.")
                return True
            else:
                print("You are running the latest version.")
        else:
            config.internet = False
            print("Unable to read the latest version.  You may check your internet connection.")
    except Exception as e:
        config.internet = False
        print("Failed to read '{0}'.".format(checkFile))
    return False

# Setup menu shortcut configuration file
from util.ShortcutUtil import ShortcutUtil
ShortcutUtil.setup(config.menuShortcuts)
# Setup GUI windows
from util.LanguageUtil import LanguageUtil
from util.BibleVerseParser import BibleVerseParser
from guiQt6.MainWindow import MainWindow
from PySide6.QtWidgets import QApplication, QStyleFactory
from PySide6.QtWidgets import QSystemTrayIcon
from PySide6.QtGui import QIcon
from PySide6.QtCore import QEvent
from util.themes import Themes
# [Optional] qt-material
# qt-material have to be imported after PySide2
if config.qtMaterial and not config.isQtMaterialInstalled:
    config.qtMaterial = False
if config.qtMaterial:
    from qt_material import apply_stylesheet

# Set screen size at first launch
def setupMainWindow(availableGeometry):
    config.screenWidth = availableGeometry.width()
    config.screenHeight = availableGeometry.height()
    # Check os with platform.system() or sys.platform
    # Linux / Darwin / Windows
    if config.startFullScreen or (platform.system() == "Linux" and config.linuxStartFullScreen):
        config.mainWindow.showFullScreen()
    elif platform.system() == "Linux" and not config.linuxStartFullScreen:
        # Launching the app in full screen in some Linux distributions makes the app too sticky to be resized.
        config.mainWindow.resize(int(config.screenWidth), int(config.screenHeight - 60))
        # Below is an alternate workaround, loading the app in 4/5 of the screen size.
        #config.mainWindow.resize(int(config.screenWidth * 4 / 5), int(config.screenHeight))
    elif platform.system() == "Windows" and hasattr(config, "cli") and not config.cli:
        config.mainWindow.showMaximized()
    else:
        # macOS or Linux set to fullscreen
        config.mainWindow.resize(int(config.screenWidth), int(config.screenHeight))
    # pre-load control panel
    config.mainWindow.manageControlPanel(config.showControlPanelOnStartup)
    if hasattr(config, "cli") and config.cli:
        config.mainWindow.hide()
    else:
        config.mainWindow.show()

    # Check if migration is needed for version >= 0.56
    config.mainWindow.checkMigration()

def executeInitialTextCommand(textCommand, addRecord=False, source="main"):
    try:
        if source == "main" or (source == "study" and re.match("^online:::", textCommand, flags=re.IGNORECASE)):
            config.mainWindow.textCommandLineEdit.setText(textCommand)
        config.mainWindow.runTextCommand(textCommand, addRecord, source, True)
    except:
        print("Failed to execute '{0}' on startup.".format(textCommand))

def populateTabsOnStartup(source="main"):
    numTabs = config.numberOfTab
    for i in range(numTabs):
        if str(i) in config.tabHistory[source]:
            command = config.tabHistory[source][str(i)]
            if command:
                previous = i - 1
                if previous < 0:
                    previous = config.numberOfTab - 1
                if source == "main":
                    config.mainWindow.mainView.setCurrentIndex(previous)
                elif source == "study":
                    config.mainWindow.studyView.setCurrentIndex(previous)
                executeInitialTextCommand(command, False, source)

def runLastHistoryRecord(source="main"):
    history = config.history[source]
    command = history[-1]
    executeInitialTextCommand(command, False, source)

def setCurrentRecord():
    mainRecordPosition = len(config.history["main"]) - 1
    studyRecordPosition = len(config.history["study"]) - 1
    config.currentRecord = {'main': mainRecordPosition, 'study': studyRecordPosition}

def exitApplication():
    from util.NoteService import NoteService

    app.closeAllWindows()
    if not config.doNotStop3rdPartyMediaPlayerOnExit:
        config.mainWindow.closeMediaPlayer()
    # Run shutdown plugins
    if config.enablePlugins:
        for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "shutdown"), "py"):
            if not plugin in config.excludeShutdownPlugins:
                script = os.path.join(os.getcwd(), "plugins", "shutdown", "{0}.py".format(plugin))
                config.mainWindow.execPythonFile(script)
    ConfigUtil.save()
    NoteService.close()
    if config.docker and config.restartUBA:
        os.system("nohup ./UniqueBibleApp.sh > /dev/null 2>&1 &")
    elif config.restartUBA and hasattr(config, "cli"):
        subprocess.Popen("{0} uba.py gui".format(sys.executable), shell=True)





# Start PySide6 gui
class UBA(QApplication):

    def __init__(self, argv):
        super().__init__(argv)
        config.mainWindowHidden = False

    # Captures the event when qapplication is activated on macOS by clicking the dock icon.
    # On macOS, after main window is closed, clicking the dock icon shows the main window again.
    def event(self, event):
        if event.type() == QEvent.ApplicationActivate and config.mainWindowHidden:
            config.mainWindow.showFromTray()
        return super().event(event)

config.startup = True
config.thisTranslation = LanguageUtil.loadTranslation(config.displayLanguage)
# assign inital command before changes to be made in sys.argv
initialCommand = " ".join(sys.argv[1:]).strip()
# The following line fix loading html with third-party javascript, e.g. Google maps, on QWebengineView.
# This line is required for Google maps to be displayed on Study Window.
sys.argv.append("--disable-web-security")
# Support running without sandbox
sys.argv.append("--no-sandbox")
#sys.argv.append("--user-data-dir")
#sys.argv.append("--allow-file-access-from-files")
#app = QApplication(sys.argv)
app = UBA(sys.argv)

# Set application name
app.setApplicationName("UniqueBible.app")
app.setApplicationDisplayName("UniqueBible.app")
# When application name is changed
#app.applicationNameChanged.connect(nameChanged)
# Assign a function to save configurations when the app is closed.
app.aboutToQuit.connect(exitApplication)
# Apply window style
if config.windowStyle and config.windowStyle in QStyleFactory.keys():
    app.setStyle(config.windowStyle)
# Apply theme style
config.defineStyle()
if config.menuLayout == "material":
    app.setPalette(Themes.getPalette())
    app.setStyleSheet(config.materialStyle)
elif config.qtMaterial and config.qtMaterialTheme:
    apply_stylesheet(app, theme=config.qtMaterialTheme)
    config.theme = "dark" if config.qtMaterialTheme.startswith("dark_") else "default"
else:
    app.setPalette(Themes.getPalette())

# Active verse number colour
#config.activeVerseNoColour = config.darkThemeActiveVerseColor if config.theme == "dark" else config.lightThemeActiveVerseColor

# Assign mainWindow to config.mainWindow, to make it acessible from user customised user script
config.studyTextTemp = config.studyText
config.mainWindow = MainWindow()

# Check screen size
try:
    availableGeometry = config.mainWindow.screen().availableGeometry()
    setupMainWindow(availableGeometry)
except:
    pass

# A container of functions to be run after UBA loaded history records on startup
# This offers a way for startup plugins to run codes after history records being loaded.
config.actionsRightAfterLoadingHistoryRecords = []

runStartupPlugins()

# Run initial commands
if config.populateTabsOnStartup:
    openBibleWindowContentOnNextTab, openStudyWindowContentOnNextTab, updateMainReferenceOnChaningTabs = config.openBibleWindowContentOnNextTab, config.openStudyWindowContentOnNextTab, config.updateMainReferenceOnChaningTabs
    config.updateMainReferenceOnChaningTabs = False
    forceGenerateHtml = config.forceGenerateHtml
    syncStudyWindowBibleWithMainWindow = config.syncStudyWindowBibleWithMainWindow
    config.openBibleWindowContentOnNextTab = True
    config.openStudyWindowContentOnNextTab = True
    config.forceGenerateHtml = False
    config.syncStudyWindowBibleWithMainWindow = False
    # Execute initial command on Study Window
    populateTabsOnStartup("study")
    # Execute initial command on Bible Window
    populateTabsOnStartup("main")
    config.openBibleWindowContentOnNextTab, config.openStudyWindowContentOnNextTab = openBibleWindowContentOnNextTab, openStudyWindowContentOnNextTab
    config.forceGenerateHtml = forceGenerateHtml
    config.syncStudyWindowBibleWithMainWindow = syncStudyWindowBibleWithMainWindow
    config.updateMainReferenceOnChaningTabs = updateMainReferenceOnChaningTabs
elif not config.disableLoadLastOpenFilesOnStartup:
    # Execute initial command on Bible Window
    if not initialCommand or (hasattr(config, "cli") and config.cli):
        runLastHistoryRecord("main")
    # Execute initial command on Study Window
    history = config.history["study"]
    command = history[-1] if len(history) > 0 else ""
    if not (config.disableOpenPopupWindowOnStartup and command.lower().startswith("book:::")):
        runLastHistoryRecord("study")

# Run functions placed with startup plugins
if config.actionsRightAfterLoadingHistoryRecords:
    for action in config.actionsRightAfterLoadingHistoryRecords:
        action()

if initialCommand:
    executeInitialTextCommand(initialCommand, True)

# Set indexes of history records
setCurrentRecord()


# Add system tray
if config.enableSystemTray:
    app.setQuitOnLastWindowClosed(False)
    # Set up tray icon
    if not os.path.isfile(config.desktopUBAIcon):
        config.desktopUBAIcon = os.path.join("htmlResources", "UniqueBibleApp.png")
    trayIcon = QIcon(config.desktopUBAIcon)
    tray = QSystemTrayIcon()
    tray.setIcon(trayIcon)
    tray.setToolTip("Unique Bible App")
    tray.setVisible(True)
    # Import system tray menu
    from guiQt6.SystemTrayMenu import *
    # Quit
    quitApp = QAction(config.thisTranslation["menu_quit"])
    #quitApp.triggered.connect(app.quit)
    # The following line instead of the one above is used to check unsaved changes in Note Editor.
    quitApp.triggered.connect(config.mainWindow.quitApp)
    trayMenu.addAction(quitApp)
    tray.setContextMenu(trayMenu)

# Clipboard Monitoring
def clipboardChanged():
    clipboardText = QApplication.clipboard().text().strip()
    config.clipboardText = clipboardText
    if config.enableClipboardMonitoring:
        if clipboardText:
            parser = BibleVerseParser(config.parserStandarisation)
            verseList = parser.extractAllReferences(clipboardText, False)
            if verseList:
                references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verseList])
                config.mainWindow.showFromTray()
                config.mainWindow.runTextCommand(references)
                if config.enableSystemTray:
                    tray.showMessage("Unique Bible App", "{0}: {1}".format(config.thisTranslation["open"], references))
            #elif platform.system() == "Darwin":
            #    config.mainWindow.showFromTray()

# Monitor Clipboard Changed
QApplication.clipboard().dataChanged.connect(clipboardChanged)

# Launch UBA
config.restartUBA = False
sys.exit(app.exec() if config.qtLibrary == "pyside6" else app.exec_())
