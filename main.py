#!venv/bin/python

# UniqueBible.app
# a cross-platform desktop bible application
# For more information on this application, visit https://BibleTools.app or https://UniqueBible.app.

import os, platform, logging, re, sys, socket
import logging.handlers as handlers
from util.FileUtil import FileUtil

if not platform.system() == "Windows":
    import readline

# Change working directory to UniqueBible directory
thisFile = os.path.realpath(__file__)
wd = thisFile[:-7]
if os.getcwd() != wd:
    os.chdir(wd)

# Create custom files
FileUtil.createCustomFiles()

# Make sure config.py exists before importing config and all other scripts which depends on config
import config
# Setup config values
from util.ConfigUtil import ConfigUtil
ConfigUtil.setup()
# Check for dependencies and other essential elements
#from checkup import *

# Check argument passed to UBA as a parameter
initialCommand = " ".join(sys.argv[1:]).strip()
config.telnet = False
if initialCommand == "cli":
    config.cli = True
elif initialCommand == "gui":
    initialCommand = ""
    config.cli = False
elif initialCommand.startswith("telnet-server"):
    config.telnet = True
initialCommandIsPython = True if initialCommand.endswith(".py") and os.path.isfile(initialCommand) else False

# Check for dependencies and other essential elements
from checkup import *

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

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

# Remote CLI
if (len(sys.argv) > 1) and sys.argv[1] == "telnet-server":
    try:
        import telnetlib3
    except:
        print("Please run 'pip install telnetlib3' to use remote CLI")
        exit(0)

    try:
        import telnetlib3
        import asyncio
        from util.RemoteCliHandler import RemoteCliHandler

        port = 8888
        if (len(sys.argv) > 2):
            port = int(sys.argv[2])
        print("Running in remote CLI Mode on port {0}".format(port))
        print("Access by 'telnet {0} {1}'".format(get_ip(), port))
        print("Press Ctrl-C to stop the server")
        loop = asyncio.get_event_loop()
        coro = telnetlib3.create_server(port=port, shell=RemoteCliHandler.shell)
        server = loop.run_until_complete(coro)
        loop.run_until_complete(server.wait_closed())
        exit(0)
    except KeyboardInterrupt:
        exit(0)
    except Exception as e:
        print(str(e))
        exit(-1)

# HTTP Server
if (len(sys.argv) > 1) and sys.argv[1] == "http-server":
    import socketserver
    from util.RemoteHttpHandler import RemoteHttpHandler

    port = 80
    if (len(sys.argv) > 2):
        port = int(sys.argv[2])
    print("Running in HTTP Server Mode")
    print("Open browser link: 'http://{0}:{1}'".format(get_ip(), port))
    socketserver.TCPServer.allow_reuse_address = True
    config.enableHttpServer = True
    with socketserver.TCPServer(("", port), RemoteHttpHandler) as httpd:
        while config.enableHttpServer:
            httpd.handle_request()
        httpd.shutdown()
        exit(0)

# Setup menu shortcut configuration file
from util.ShortcutUtil import ShortcutUtil
ShortcutUtil.setup(config.menuShortcuts)
# Setup GUI windows
from gui.MainWindow import MainWindow
from qtpy.QtWidgets import QApplication, QStyleFactory
from themes import Themes
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
    if platform.system() == "Linux" and not config.linuxStartFullScreen:
        # Launching the app in full screen in some Linux distributions makes the app too sticky to be resized.
        config.mainWindow.resize(config.screenWidth, config.screenHeight - 60)
        # Below is an alternate workaround, loading the app in 4/5 of the screen size.
        #config.mainWindow.resize(config.screenWidth * 4 / 5, config.screenHeight)
    elif platform.system() == "Windows" and hasattr(config, "cli") and not config.cli:
        config.mainWindow.showMaximized()
    else:
        # macOS or Linux set to fullscreen
        config.mainWindow.resize(config.screenWidth, config.screenHeight)
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
        config.mainWindow.runTextCommand(textCommand, addRecord, source)
    except:
        print("Failed to execute '{0}' on startup.".format(textCommand))

def populateTabsOnStartup(source="main"):
    history = config.history[source]
    for i in reversed(range(config.numberOfTab - 1 if initialCommand and not initialCommandIsPython and not (hasattr(config, "cli") and config.cli) and source == "main" else config.numberOfTab)):
        index = i + 1
        if len(history) >= index:
            command = history[0 - index]
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
    config.mainWindow.textCommandParser.stopTtsAudio()
    # Run shutdown plugins
    if config.enablePlugins:
        for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "shutdown"), "py"):
            if not plugin in config.excludeShutdownPlugins:
                script = os.path.join(os.getcwd(), "plugins", "shutdown", "{0}.py".format(plugin))
                config.mainWindow.execPythonFile(script)
    ConfigUtil.save()

def nameChanged():
    if app.applicationName() == "UniqueBible.app CLI":
        switchToCli()

def printContentOnConsole(text):
    if not "html-text" in sys.modules:
        import html_text
    print(html_text.extract_text(text))
    #subprocess.Popen(["echo", html_text.extract_text(text)])
    #sys.stdout.flush()
    return text

def getCommandDocumentation():
    print("\nUBA commands:")
    print("\n".join([re.sub("            #", "#", value[-1]) for value in config.mainWindow.textCommandParser.interpreters.values()]))

def startWithCli():
    if not "html-text" in sys.modules:
        import html_text
    # Cli input
    #config.mainWindow.hide()
    #config.cli = True
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
            # The following line does not work on Windows on UBA startup
            #config.mainWindow.mainPage.runJavaScript("document.documentElement.outerHTML", 0, printContentOnConsole)
        elif command == ".study":
            print(html_text.extract_text(config.studyWindowContent))
            # The following line does not work on Windows on UBA startup
            #config.mainWindow.studyPage.runJavaScript("document.documentElement.outerHTML", 0, printContentOnConsole)
        elif command in (".help", ".command"):
            getCommandDocumentation()
        elif command == ".quit":
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
if config.qtMaterial and config.qtMaterialTheme:
    apply_stylesheet(app, theme=config.qtMaterialTheme)
    config.theme = "dark" if config.qtMaterialTheme.startswith("dark_") else "default"
else:
    app.setPalette(Themes.getPalette())
# Active verse number colour
#config.activeVerseNoColour = config.activeVerseNoColourDark if config.theme == "dark" else config.activeVerseNoColourLight

# Assign mainWindow to config.mainWindow, to make it acessible from user customised user script
config.mainWindow = MainWindow()

# Check screen size
availableGeometry = app.desktop().availableGeometry(config.mainWindow)
setupMainWindow(availableGeometry)

# A container of functions to be run after UBA loaded history records on startup
# This offers a way for startup plugins to run codes after history records being loaded.
config.actionsRightAfterLoadingHistoryRecords = []

# Run startup plugins
if config.enablePlugins:
    for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "startup"), "py"):
        if not plugin in config.excludeStartupPlugins:
            script = os.path.join(os.getcwd(), "plugins", "startup", "{0}.py".format(plugin))
            config.mainWindow.execPythonFile(script)

# Run initial commands
if config.populateTabsOnStartup:
    openBibleWindowContentOnNextTab, openStudyWindowContentOnNextTab = config.openBibleWindowContentOnNextTab, config.openStudyWindowContentOnNextTab
    config.openBibleWindowContentOnNextTab = True
    config.openStudyWindowContentOnNextTab = True
    # Execute initial command on Bible Window
    populateTabsOnStartup("main")
    # Execute initial command on Study Window
    populateTabsOnStartup("study")
    config.openBibleWindowContentOnNextTab, config.openStudyWindowContentOnNextTab = openBibleWindowContentOnNextTab, openStudyWindowContentOnNextTab
else:
    # Execute initial command on Bible Window
    if not initialCommand or initialCommandIsPython or (hasattr(config, "cli") and config.cli):
        runLastHistoryRecord("main")
    # Execute initial command on Study Window
    runLastHistoryRecord("study")

# Run functions placed with startup plugins
if config.actionsRightAfterLoadingHistoryRecords:
    for action in config.actionsRightAfterLoadingHistoryRecords:
        action()

# Startup macro
config.mainWindow.runMacro(config.startupMacro)

if initialCommand == "cli":
    if config.isHtmlTextInstalled:
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

def global_excepthook(type, value, traceback):
    logger.error("Uncaught exception", exc_info=(type, value, traceback))
    print(traceback.format_exc())

sys.excepthook = global_excepthook

sys.exit(app.exec_())
