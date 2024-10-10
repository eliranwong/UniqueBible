import os, platform, sys, subprocess, re, time
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.ConfigUtil import ConfigUtil
from uniquebible.util.LanguageUtil import LanguageUtil
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.startup.share import *
if not platform.system() == "Windows" and not config.enableHttpServer:
    import readline


# Setup menu shortcut configuration file
from uniquebible.util.ShortcutUtil import ShortcutUtil
ShortcutUtil.setup(config.menuShortcuts)
# Import Qt Library
from uniquebible.gui.Styles import *
from uniquebible.gui.MainWindow import MainWindow
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QApplication, QStyleFactory
    from PySide6.QtWidgets import QSystemTrayIcon
    from PySide6.QtGui import QIcon
    from PySide6.QtCore import QEvent
else:
    from qtpy.QtWidgets import QApplication, QStyleFactory
    from qtpy.QtWidgets import QSystemTrayIcon
    from qtpy.QtGui import QIcon
    from qtpy.QtCore import QEvent
from uniquebible.util.themes import Themes
# [Optional] qt-material
# qt-material have to be imported after PySide2
if config.qtMaterial and not ("Qtmaterial" in config.enabled):
    config.qtMaterial = False
if config.qtMaterial:
    from qt_material import apply_stylesheet


# check startup time
testStartupTime = False
if testStartupTime:
    bootStartTime = time.time()

# check initial command
initialCommand = " ".join(sys.argv[2:]).strip() if config.runMode else " ".join(sys.argv[1:]).strip()
initialCommandIsPython = True if initialCommand.endswith(".py") and os.path.isfile(initialCommand) else False

# Set screen size at first launch
def setupMainWindow(availableGeometry):
    config.screenWidth = availableGeometry.width()
    config.screenHeight = availableGeometry.height()
    # Check os with platform.system() or sys.platform
    # Linux / Darwin / Windows
    if (config.runMode == "docker") or config.startFullScreen or (platform.system() == "Linux" and config.linuxStartFullScreen):
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
    from uniquebible.util.NoteService import NoteService

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
    if (config.runMode == "docker") and config.restartUBA:
        os.system("nohup ./UniqueBibleApp.sh > /dev/null 2>&1 &")
    elif config.restartUBA and hasattr(config, "cli"):
        subprocess.Popen("{0} uba.py gui".format(sys.executable), shell=True)

def nameChanged():
    if app.applicationName() == "UniqueBible.app CLI":
        switchToCli()

def getCommandDocumentation():
    print("\nUBA commands:")
    print("\n".join([re.sub("            #", "#", value[-1]) for value in config.mainWindow.textCommandParser.interpreters.values()]))

def startWithCli():
    if not "html-text" in sys.modules:
        import html_text
    config.bibleWindowContentTransformers.append(printContentOnConsole)
    config.studyWindowContentTransformers.append(printContentOnConsole)
    while config.cli:
        print("--------------------")
        print("Enter '.bible' to read bible text, '.study' to read study resource, '.help' to read UBA command reference, '.gui' to launch gui, '.quit' to quit,")
        command = input("or UBA command: ").strip()
        if command == ".gui":
            del config.bibleWindowContentTransformers[-1]
            del config.studyWindowContentTransformers[-1]
            config.cli = False
        elif command == ".bible":
            print(html_text.extract_text(config.bibleWindowContent))
            # The following line does not work on Windows on UBA startup
            #config.mainWindow.mainPage.runJavaScript("document.documentElement.outerHTML", 0, printContentOnConsole)
        elif command == ".study":
            print(html_text.extract_text(config.studyWindowContent))
            # The following line does not work on Windows on UBA startup
            #config.mainWindow.studyPage.runJavaScript("document.documentElement.outerHTML", 0, printContentOnConsole)
        elif command in (".help", ".command"):
            getCommandDocumentation()
        elif command == ".quit":
            ConfigUtil.save()
            exit()
        else:
            config.mainWindow.runTextCommand(command)
    config.mainWindow.show()
    if platform.system() == "Windows":
        config.mainWindow.showMaximized()

def switchToCli():
    if not "html-text" in sys.modules:
        import html_text
    # Print content where is context menu was called from
    if config.pluginContext == "study":
        print(html_text.extract_text(config.studyWindowContent))
    else:
        print(html_text.extract_text(config.bibleWindowContent))
    # Hide gui
    if platform.system() == "Darwin":
        config.mainWindow.showMinimized()
    else:
        config.mainWindow.hide()
    # Cli input
    config.cli = True
    toQuit = False
    #config.printContentOnConsole = printContentOnConsole
    config.bibleWindowContentTransformers.append(printContentOnConsole)
    config.studyWindowContentTransformers.append(printContentOnConsole)
    while config.cli:
        print("--------------------")
        print("Enter '.bible' to read bible text, '.study' to read study resource, '.help' to read UBA command reference, '.gui' to launch gui, '.quit' to quit,")
        command = input("or UBA command: ").strip()
        if command == ".gui":
            del config.bibleWindowContentTransformers[-1]
            del config.studyWindowContentTransformers[-1]
            config.cli = False
        elif command == ".bible":
            print(html_text.extract_text(config.bibleWindowContent))
        elif command == ".study":
            print(html_text.extract_text(config.studyWindowContent))
        elif command in (".help", ".command"):
            getCommandDocumentation()
        elif command == ".quit":
            toQuit = True
            config.cli = False
        else:
            config.mainWindow.runTextCommand(command)
    if toQuit:
        config.mainWindow.quitApp()
    else:
        app.setApplicationName("UniqueBible.app")
        if platform.system() == "Darwin":
            config.mainWindow.showMaximized()
            config.mainWindow.raise_()
        else:
            config.mainWindow.show()

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


# Start PySide2 gui
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


# Set Qt input method variable to use Qt virtual keyboards if config.virtualKeyboard is "True"
if config.virtualKeyboard:
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"
# Set Qt input method variable to use fcitx / ibus if config.fcitx / config.ibus is "True"
elif config.fcitx5:
    os.environ["QT_IM_MODULE"] = "fcitx5"
elif config.fcitx:
    os.environ["QT_IM_MODULE"] = "fcitx"
elif config.ibus:
    os.environ["QT_IM_MODULE"] = "ibus"

config.startup = True
config.thisTranslation = LanguageUtil.loadTranslation(config.displayLanguage)
# The following line fix loading html with third-party javascript, e.g. Google maps, on QWebengineView.
# This line is required for Google maps to be displayed on Study Window.
sys.argv.append("--disable-web-security")
# Support running without sandbox
sys.argv.append("--no-sandbox")
sys.argv.append("--user-data-dir")
sys.argv.append("--allow-file-access-from-files")
#app = QApplication(sys.argv)
app = UBA(sys.argv)

# Set application name
app.setApplicationName("UniqueBible.app")
app.setApplicationDisplayName("UniqueBible.app")
# When application name is changed
app.applicationNameChanged.connect(nameChanged)
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

# Check if migration is needed for version >= 0.56
config.mainWindow.checkMigration()

# A container of functions to be run after UBA loaded history records on startup
# This offers a way for startup plugins to run codes after history records being loaded.
config.actionsRightAfterLoadingHistoryRecords = []

runStartupPlugins()

# Run initial commands
if config.populateTabsOnStartup:
    openBibleWindowContentOnNextTab, openStudyWindowContentOnNextTab, updateMainReferenceOnChangingTabs = config.openBibleWindowContentOnNextTab, config.openStudyWindowContentOnNextTab, config.updateMainReferenceOnChangingTabs
    config.updateMainReferenceOnChangingTabs = False
    forceGenerateHtml = config.forceGenerateHtml
    syncAction = config.syncAction
    config.openBibleWindowContentOnNextTab = True
    config.openStudyWindowContentOnNextTab = True
    config.forceGenerateHtml = False
    config.syncAction = ""
    # Execute initial command on Study Window
    populateTabsOnStartup("study")
    # Execute initial command on Bible Window
    populateTabsOnStartup("main")
    config.openBibleWindowContentOnNextTab, config.openStudyWindowContentOnNextTab = openBibleWindowContentOnNextTab, openStudyWindowContentOnNextTab
    config.forceGenerateHtml = forceGenerateHtml
    config.syncAction = syncAction
    config.updateMainReferenceOnChangingTabs = updateMainReferenceOnChangingTabs
elif not config.disableLoadLastOpenFilesOnStartup:
    # Execute initial command on Bible Window
    if not initialCommand or initialCommandIsPython:
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

# Startup macro
config.mainWindow.runMacro(config.startupMacro)
if config.runMode == "cli":
    if ("Htmltext" in config.enabled):
        startWithCli()
    else:
        config.cli = False
        print("CLI feature is not enabled!  Install module 'html-text' first, by running 'pip3 install html-text'!")
elif initialCommand and initialCommandIsPython:
    config.mainWindow.execPythonFile(initialCommand)
elif initialCommand:
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
    from uniquebible.gui.SystemTrayMenu import *
    # Quit
    quitApp = QAction(config.thisTranslation["menu_quit"])
    #quitApp.triggered.connect(app.quit)
    # The following line instead of the one above is used to check unsaved changes in Note Editor.
    quitApp.triggered.connect(config.mainWindow.quitApp)
    trayMenu.addAction(quitApp)
    tray.setContextMenu(trayMenu)

# Monitor Clipboard Changed
QApplication.clipboard().dataChanged.connect(clipboardChanged)

# Check screen size
try:
    availableGeometry = config.mainWindow.screen().availableGeometry()
    setupMainWindow(availableGeometry)
except:
    pass

# show start up time in status bar
if testStartupTime:
    timeDifference = time.time() - bootStartTime
    print(f"Unique Bible App launches in {timeDifference}s.")

# Launch UBA
config.restartUBA = False
sys.exit(app.exec() if config.qtLibrary == "pyside6" else app.exec_())
