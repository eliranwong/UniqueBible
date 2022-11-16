#!venv/bin/python

# UniqueBible.app
# a cross-platform desktop bible application
# For more information on this application, visit https://BibleTools.app or https://UniqueBible.app.
import glob
import os, platform, logging, re, sys, subprocess
import logging.handlers as handlers
from util.FileUtil import FileUtil
from util.NetworkUtil import NetworkUtil
from util.WebtopUtil import WebtopUtil

# Change working directory to UniqueBible directory
thisFile = os.path.realpath(__file__)
wd = thisFile[:-7]
if os.getcwd() != wd:
    os.chdir(wd)

# Create custom files
FileUtil.createCustomFiles()
if not platform.system() == "Windows" and os.path.isfile("config.py"):
    os.system("touch config.py")

# Make sure config.py exists before importing config and all other scripts which depends on config
import config
# Setup config values
from util.ConfigUtil import ConfigUtil
ConfigUtil.setup()
from gui.Styles import *

# Check argument passed to UBA as a parameter
initialCommand = " ".join(sys.argv[1:]).strip()
docker = False
config.noQt = False
config.cli = False
config.enableCli = True if initialCommand.lower() in ("cli", "gui", "docker") else False
if initialCommand == "docker":
    docker = True
    initialCommand = "gui"
    #config.isGTTSInstalled = True
    config.fcitx = True
    config.docker = True
    config.updateWithGitPull = True
    # Force to use PySide2 instead of PyQt5 for general users
    if not config.developer and config.qtLibrary != "pyside2":
        config.qtLibrary = "pyside2"
        os.environ["QT_API"] = config.qtLibrary
    # To deal with "ERROR:command_buffer_proxy_impl.cc(141)] ContextResult::kTransientFailure: Failed to send GpuChannelMsg_CreateCommandBuffer."
    # Reference: https://bugreports.qt.io/browse/QTBUG-82423
    os.environ["QTWEBENGINE_DISABLE_GPU_THREAD"] = "1"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-compositing --num-raster-threads=1 --enable-viewport --main-frame-resizes-are-orientation-changes --disable-composited-antialiasing"
    # Setup yay on first run; latest docker images has /opt/yay in place
    if os.path.isdir("/opt/yay") and not WebtopUtil.isPackageInstalled("yay"):
        print("Installing yay ...")
        os.system("sudo chown -R abc:users /opt/yay && cd /opt/yay && makepkg -si --noconfirm --needed && cd -")
    if WebtopUtil.isPackageInstalled("yay") and not WebtopUtil.isPackageInstalled("wps"):
        print("Installing fonts ...")
        os.system("yay -Syu --noconfirm --needed ttf-wps-fonts ttf-ms-fonts wps-office-fonts")
        print("Installing wps-office ...")
        os.system("yay -Syu --noconfirm --needed wps-office-cn")
else:
    config.docker = False
if initialCommand == "cli":
    config.cli = True
elif initialCommand == "gui":
    initialCommand = ""
elif len(sys.argv) > 1 and sys.argv[1].lower() in ("telnet-server", "http-server", "execute-macro", "terminal"):
    config.noQt = True
initialCommandIsPython = True if initialCommand.endswith(".py") and os.path.isfile(initialCommand) else False

# Check for dependencies and other essential elements
os.environ["PYTHONUNBUFFERED"] = "1"
from util.checkup import *
# The following two imports must not be placed before checkup utilities
import requests
from util.UpdateUtil import UpdateUtil

if initialCommand == "setup-only":
    print("UniqueBibleApp installed!")
    exit()

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

def cleanupTempFiles():
    files = glob.glob(os.path.join("htmlResources", "main-*.html"))
    for file in files:
        os.remove(file)

cleanupTempFiles()

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

# Local CLI - Terminal Mode

# Get terminal mode history records
def getHistoryRecords():
    records = []
    command_history = os.path.join("terminal_history", "commands")
    if os.path.isfile(command_history):
        with open(command_history, "r", encoding="utf-8") as input_file:
            history = input_file.read()
        for item in reversed(history.split("\n")):
            item = item.strip()
            if item and item.startswith("+"):
                item = item[1:]
                if not item.replace(" ", "").lower() in config.mainWindow.startupException1 and not re.search(config.mainWindow.startupException2, item.replace(" ", "").lower()):
                    records.append(item)
    return records

def runTerminalModeCommand(command):
    if command:
        content = config.mainWindow.getContent(command)
        if content:
            if content == ".restart" or content == ".z":
                return ".restart"
            else:
                # display
                config.mainWindow.displayOutputOnTerminal(content)
    return command

def runTerminalModeCommandWrapper(command):
    runTerminalModeCommand(command)
    default = config.terminalCommandDefault
    config.terminalCommandDefault = ""
    config.mainWindow.initialDisplay()
config.runTerminalModeCommand = runTerminalModeCommandWrapper

def closingTerminalMode():
    config.mainWindow.removeAudioPlayingFile()
    if config.terminalUseMarvelDataPrivate:
        config.marvelData = config.defaultMarvelData
    if config.saveConfigOnExit:
        ConfigUtil.save()
    if config.terminalStopHttpServerOnExit:
        config.mainWindow.stophttpserver()
    if not config.doNotStop3rdPartyMediaPlayerOnExit:
        config.mainWindow.textCommandParser.parent.closeMediaPlayer()
config.closingTerminalMode = closingTerminalMode

def initiateMainPrompt():
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import FileHistory
    command_history = os.path.join("terminal_history", "commands")
    config.main_prompt_session = PromptSession(history=FileHistory(command_history))
config.initiateMainPrompt = initiateMainPrompt

def checkCommand(command):
    if command.lower().startswith("http://") or command.lower().startswith("https://"):
        return f"_website:::{command}"
    elif (command.lower().endswith(".jpg") or command.lower().endswith(".jpeg") or command.lower().endswith(".png")) and os.path.isfile(os.path.join("htmlResources", "images", *command.split("/"))):
        return f"_htmlimage:::{command}"
    else:
        return command

def run_terminal_mode():
    from util.LocalCliHandler import LocalCliHandler
    from util.prompt_shared_key_bindings import prompt_shared_key_bindings
    from util.uba_command_prompt_key_bindings import uba_command_prompt_key_bindings
    from prompt_toolkit.key_binding import merge_key_bindings
    from prompt_toolkit.shortcuts import set_title, clear_title
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.styles import Style
    from prompt_toolkit.filters import Condition


    # startup
    set_title(f"Unique Bible App [{config.version}]")
    config.saveConfigOnExit = True
    print(f"Running Unique Bible App {config.version} in terminal mode ...")
    checkMigration()
    needUpdate = checkApplicationUpdateCli()
    # set up config.mainWindow for terminal mode
    config.mainWindow = LocalCliHandler()
    # command default
    config.terminalCommandDefault = ""
    default = ""
    # make key bindings available in config to allow futher customisation via plugins
    config.key_bindings = uba_command_prompt_key_bindings
    # run plugin where users may add customised key bindings
    runStartupPlugins()
    if config.isPrompt_toolkitInstalled:
        config.key_bindings = merge_key_bindings([
            prompt_shared_key_bindings,
            config.key_bindings,
        ])
    # make sure user-customised menu contains valid item only.
    # validation can only be running after, not before, running startup plugin, as some startup plugin works on command shortcuts.
    config.terminalMyMenu = [i for i in config.terminalMyMenu if i in config.mainWindow.dotCommands]

    # Set initial command
    command = " ".join(sys.argv[2:]).strip()
    if not command:
        records = getHistoryRecords()
        if records:
            command = records[0]
    config.mainWindow.command = command

    if needUpdate and config.terminalAutoUpdate:
        command = ".update"
        print("Updating UBA ...")

    if config.terminalStartHttpServerOnStartup:
        config.mainWindow.starthttpserver()

    # initiate main prompt session
    initiateMainPrompt()
    command_completer = config.mainWindow.getCommandCompleter()
    auto_suggestion=AutoSuggestFromHistory()
    toolbar = " [ctrl+q] .quit [escape+m] .menu [escape+h] .help "
    style = Style.from_dict({
        # User input (default text).
        "": config.terminalCommandEntryColor1,
        # Prompt.
        "indicator": config.terminalPromptIndicatorColor1,
    })
    promptIndicator = ">>> "
    promptIndicator = [
        ("class:indicator", promptIndicator),
    ]
    if command:
        command = checkCommand(command)
        # display
        print(config.mainWindow.divider)
        try:
            config.mainWindow.printRunningCommand(command)
            content = config.mainWindow.getContent(command)
        except:
            # make sure UBA can start up
            print(f"Failed to run '{command}'!")
            command = ".menu"
            config.mainWindow.printRunningCommand(command)
            content = config.mainWindow.getContent(command)
        if content.strip():
            config.mainWindow.displayOutputOnTerminal(content)
        else:
            command = ".latestbible"
    while not command.lower() in (".quit", ".restart", ".q", ".z"):
        default = config.terminalCommandDefault
        config.terminalCommandDefault = ""
        config.mainWindow.initialDisplay()
        # User command input
        command = config.main_prompt_session.prompt(
            promptIndicator,
            style=style,
            completer=command_completer,
            complete_in_thread=None if config.terminalUseLighterCompleter else True,
            auto_suggest=auto_suggestion,
            bottom_toolbar=toolbar,
            default=default,
            key_bindings=config.key_bindings,
            # enable system prompt without auto-completion
            # use escape+!
            enable_system_prompt=True,
            swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")),
            #rprompt="Enter an UBA command",
        ).strip()
        if command:
            command = checkCommand(command)
            # remove spaces before and after ":::"
            command = re.sub("[ ]*?:::[ ]+?([^ ])", r":::\1", command)
            # remove "_" before ":::"
            command = re.sub("_:::", ":::", command)
            # format chapter no. and verse no
            command = re.sub("([0-9]+?)_([0-9]+?)_([0-9])", r"\1.\2.\3", command)
            command = re.sub("_([0-9]+?)_([0-9]+?,)", r" \1:\2", command)
            command = re.sub("_([0-9]+?)_([0-9]+?)$", r" \1:\2", command)
            # change full width characters
            command = re.sub("：：：", r":::", command)
            command = runTerminalModeCommand(command)
        else:
            config.mainWindow.clipboardMonitorFeature()
            command = runTerminalModeCommand(config.terminalDefaultCommand)

    closingTerminalMode()
    if command.lower() in (".restart", ".z"):
        os.system("{0} {1} terminal".format(sys.executable, "uba.py"))
    clear_title()
    sys.exit(0)

if (len(sys.argv) > 1) and sys.argv[1].lower() == "terminal":
    config.runMode = "terminal"
    run_terminal_mode()

# ssh-server
# read setup guide at https://github.com/eliranwong/UniqueBible/wiki/Run-SSH-Server

def run_ssh_server(host="", port=2222, server_host_keys="", passphrase="the_best_bible_app"):
    import os, logging, asyncssh
    from prompt_toolkit.eventloop import get_event_loop
    from prompt_toolkit.contrib.ssh import PromptToolkitSSHServer, PromptToolkitSSHSession
    from prompt_toolkit.shortcuts.prompt import PromptSession
    from util.LocalCliHandler import LocalCliHandler
    from prompt_toolkit.shortcuts import print_formatted_text
    from prompt_toolkit.key_binding import KeyBindings

    # set up config.mainWindow for terminal mode
    config.mainWindow = LocalCliHandler()

    async def ubaCommandPrompt(ssh_session: PromptToolkitSSHSession) -> None:

        prompt_session = PromptSession()
        print = print_formatted_text

        print(f"Running Unique Bible App [{config.version}] in ssh-server mode ...")

        while True:
            try:
                command = await prompt_session.prompt_async("Enter an UBA command: ", bottom_toolbar=" run '.quit' to quit ")
                if command == ".quit":
                    break
                print(config.mainWindow.divider)
                config.mainWindow.printRunningCommand(command)
                print(config.mainWindow.divider)
                print(config.mainWindow.getContent(command))
                print(config.mainWindow.divider)
            except:
                print("Errors!")

    if not server_host_keys:
        home = os.environ["HOME"]
        server_host_keys = f"{home}/.ssh/uba_ssh_server"

    # Set up logging.
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    loop = get_event_loop()
    loop.run_until_complete(
        asyncssh.create_server(
            lambda: PromptToolkitSSHServer(ubaCommandPrompt),
            host=host,
            port=port,
            server_host_keys=server_host_keys,
            options=asyncssh.SSHServerConnectionOptions(passphrase=passphrase),
        )
    )
    loop.run_forever()

if (len(sys.argv) > 1) and sys.argv[1].lower() == "ssh-server":
    config.runMode = "ssh-server"
    run_ssh_server(host=config.sshServerHost, port=config.sshServerPort, server_host_keys=config.sshServerHostKeys, passphrase=config.sshServerPassphrase)

# telnet-server

if (len(sys.argv) > 1) and sys.argv[1] == "telnet-server":
    config.runMode = "telnet-server"
    try:
        import telnetlib3
    except:
        print("Please run 'pip install telnetlib3' to use remote CLI")
        exit(0)

    try:
        import telnetlib3
        import asyncio
        from util.RemoteCliHandler import RemoteCliHandler

        port = config.telnetServerPort
        if (len(sys.argv) > 2):
            port = int(sys.argv[2])
        print("Running in remote CLI Mode on port {0}".format(port))
        print("Access by 'telnet {0} {1}'".format(NetworkUtil.get_ip(), port))
        print("Press Ctrl-C to stop the server")
        loop = asyncio.get_event_loop()
        coro = telnetlib3.create_server(port=port, shell=RemoteCliHandler.shell)
        server = loop.run_until_complete(coro)
        loop.run_until_complete(server.wait_closed())
        ConfigUtil.save()
        exit(0)
    except KeyboardInterrupt:
        ConfigUtil.save()
        exit(0)
    except Exception as e:
        print(str(e))
        exit(-1)

# HTTP Server
from db.BiblesSqlite import BiblesSqlite

def startHttpServer():
    import socketserver
    from util.RemoteHttpHandler import RemoteHttpHandler

    config.restartHttpServer = False
    port = config.httpServerPort
    if (len(sys.argv) > 2):
        port = int(sys.argv[2])
    config.thisHttpServerPort = port
    print("Running in HTTP Server Mode")
    print("Open browser link: 'http://{0}:{1}'".format(NetworkUtil.get_ip(), port))
    socketserver.TCPServer.allow_reuse_address = True
    config.enableHttpServer = True
    with socketserver.TCPServer(("", port), RemoteHttpHandler) as httpd:
        while config.enableHttpServer:
            httpd.handle_request()
        httpd.server_close()
        cleanupTempFiles()
        print("Server is stopped!")

config.enableHttpServer = False
if (len(sys.argv) > 1) and sys.argv[1] == "http-server":
    config.runMode = "http-server"
    checkMigration()
    startHttpServer()
    ConfigUtil.save()
    if config.restartHttpServer:
        subprocess.Popen("{0} {1} http-server".format(sys.executable, config.httpServerUbaFile), shell=True)
    exit(0)

def startApiServer():
    import socketserver
    from util.RemoteApiHandler import RemoteApiHandler

    config.restartApiServer = False
    port = config.httpServerPort
    if (len(sys.argv) > 2):
        port = int(sys.argv[2])
    config.thisHttpServerPort = port
    print("Running in API Server Mode")
    print("API URL: 'http://{0}:{1}'".format(NetworkUtil.get_ip(), port))
    socketserver.TCPServer.allow_reuse_address = True
    config.enableApiServer = True
    with socketserver.TCPServer(("", port), RemoteApiHandler) as httpd:
        while config.enableApiServer:
            httpd.handle_request()
        httpd.server_close()
        cleanupTempFiles()
        print("Server is stopped!")

config.enableApiServer = False
if (len(sys.argv) > 1) and sys.argv[1] == "api-server":
    config.runMode = "api-server"
    checkMigration()
    startApiServer()
    ConfigUtil.save()
    if config.restartApiServer:
        subprocess.Popen("{0} {1} api-server".format(sys.executable, config.httpServerUbaFile), shell=True)
    exit(0)

def printContentOnConsole(text):
    if not "html-text" in sys.modules:
        import html_text
    print(html_text.extract_text(text))
    #subprocess.Popen(["echo", html_text.extract_text(text)])
    #sys.stdout.flush()
    return text

# Execute macro
if (len(sys.argv) > 1) and sys.argv[1] == "execute-macro":
    config.runMode = "execute-macro"
    if config.enableMacros:
        from util.MacroParser import MacroParser
        if len(sys.argv) < 3:
            print("Please specify macro file to run")
            exit(-1)
        file = sys.argv[2]
        if os.path.isfile(os.path.join(MacroParser.macros_dir, file)):
            from util.RemoteCliMainWindow import RemoteCliMainWindow
            config.bibleWindowContentTransformers.append(printContentOnConsole)
            config.studyWindowContentTransformers.append(printContentOnConsole)
            MacroParser(RemoteCliMainWindow()).parse(file)
            ConfigUtil.save()
            print("Macro {0} executed".format(file))
        else:
            print("Macro {0} does not exist".format(file))
    else:
        print("Macros are not enabled")
    exit(0)

# Setup menu shortcut configuration file
if not platform.system() == "Windows" and not config.enableHttpServer:
    import readline
from util.ShortcutUtil import ShortcutUtil
ShortcutUtil.setup(config.menuShortcuts)
# Setup GUI windows
from util.LanguageUtil import LanguageUtil
from util.BibleVerseParser import BibleVerseParser
from gui.MainWindow import MainWindow
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
    if docker or config.startFullScreen or (platform.system() == "Linux" and config.linuxStartFullScreen):
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
    # numTabs = config.numberOfTab-1 if initialCommand and not initialCommandIsPython and not (hasattr(config, "cli") and config.cli) and source == "main" else config.numberOfTab
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

def nameChanged():
    if app.applicationName() == "UniqueBible.app CLI":
        switchToCli()

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


# Set Qt input method variable to use fcitx / ibus if config.fcitx / config.ibus is "True"
if config.fcitx:
    os.environ["QT_IM_MODULE"] = "fcitx"
elif config.ibus:
    os.environ["QT_IM_MODULE"] = "ibus"

# Set Qt input method variable to use Qt virtual keyboards if config.virtualKeyboard is "True"
if config.virtualKeyboard:
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

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

config.startup = True
config.thisTranslation = LanguageUtil.loadTranslation(config.displayLanguage)
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
    if not initialCommand or initialCommandIsPython or (hasattr(config, "cli") and config.cli):
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
    from gui.SystemTrayMenu import *
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
