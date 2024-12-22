import os, re, sys
from uniquebible.util.ConfigUtil import ConfigUtil
# The following two imports must not be placed before checkup utilities
import requests
from uniquebible.util.UpdateUtil import UpdateUtil
from uniquebible.util.NetworkUtil import NetworkUtil
from uniquebible.startup.share import *


# manage latest update
def checkApplicationUpdateCli():
    # TODO disable for now; update later
    return False
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
    if hasattr(config, "defaultMarvelData"):
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
    from uniquebible.util.LocalCliHandler import LocalCliHandler
    from uniquebible.util.prompt_shared_key_bindings import prompt_shared_key_bindings
    from uniquebible.util.uba_command_prompt_key_bindings import uba_command_prompt_key_bindings
    from prompt_toolkit.key_binding import merge_key_bindings
    from prompt_toolkit.shortcuts import set_title, clear_title
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.styles import Style
    from prompt_toolkit.filters import Condition


    # startup
    set_title("Unique Bible App")
    config.saveConfigOnExit = True
    print("Running Unique Bible App in terminal mode ...")
    if ("Art" in config.enabled):
        from art import text2art
        print(text2art("UBA")[:-1])

    #needUpdate = checkApplicationUpdateCli()
    # set up config.mainWindow for terminal mode
    config.mainWindow = LocalCliHandler()
    # command default
    config.terminalCommandDefault = ""
    default = ""
    # make key bindings available in config to allow futher customisation via plugins
    config.key_bindings = uba_command_prompt_key_bindings
    # run plugin where users may add customised key bindings
    runStartupPlugins()
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

    #if needUpdate and config.terminalAutoUpdate:
    #    command = ".update"
    #    print("Updating UBA ...")

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
        if content is not None and content.strip():
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

# api-client mode

def run_api_client_mode(localhost: bool =False):
    cwd = os.getcwd()

    def getApiOutput(command: str, localhost: bool =False):
        endpoint = f"http://{NetworkUtil.get_ip()}:{config.httpServerPort}/plain" if localhost else config.web_api_endpoint
        private = f"private={config.web_api_private}&" if config.web_api_private else ""
        url = f"""{endpoint}?{private}cmd={command}"""
        try:
            response = requests.get(url, timeout=config.web_api_timeout)
            response.encoding = "utf-8"
            print(response.text.strip())
        except Exception as err:
            print(f"An error occurred: {err}")

    def multiturn_api_output(apiCommandSuggestions=None, localhost=False):
        from uniquebible.util.prompt_shared_key_bindings import prompt_shared_key_bindings
        from uniquebible.util.uba_command_prompt_key_bindings import api_command_prompt_key_bindings
        from uniquebible.util.PromptValidator import NumberValidator
        from prompt_toolkit import prompt
        from prompt_toolkit.key_binding import merge_key_bindings
        from prompt_toolkit.shortcuts import set_title, clear_title
        from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
        from prompt_toolkit.styles import Style
        from prompt_toolkit.filters import Condition
        from prompt_toolkit.completion import WordCompleter, NestedCompleter, ThreadedCompleter, FuzzyCompleter
        import webbrowser

        def simplePrompt(default="", numberOnly=False, inputIndicator=">>> "):
            promptStyle = Style.from_dict({
                "": config.terminalCommandEntryColor2,
                "indicator": config.terminalPromptIndicatorColor2,
            })
            inputIndicator = [
                ("class:indicator", inputIndicator),
            ]
            if numberOnly:
                userInput = prompt(inputIndicator, style=promptStyle, default=default, validator=NumberValidator()).strip()
            else:
                userInput = prompt(inputIndicator, style=promptStyle, default=default).strip()
            return userInput

        def changeSettings():
            print("# Chaning web API endpoint ...") # config.web_api_endpoint
            if configuration := simplePrompt(config.web_api_endpoint):
                config.web_api_endpoint = configuration
                ConfigUtil.save()
            print("# Chaning web API timeout ...") # config.web_api_timeout
            if configuration := simplePrompt(str(config.web_api_timeout), True):
                config.web_api_timeout = int(configuration)
                ConfigUtil.save()
            print("# Chaning web API private key ...") # config.web_api_private
            if configuration := simplePrompt(config.web_api_private):
                config.web_api_private = configuration
                ConfigUtil.save()

        # startup
        set_title("Unique Bible App API-Client")
        print("Running Unique Bible App api-client ...")
        print("Enter an Unique Bible App command:")
        print("For API documentation, visit https://github.com/eliranwong/UniqueBibleAPI")

        # make key bindings available in config to allow futher customisation via plugins
        config.key_bindings = merge_key_bindings([
            prompt_shared_key_bindings,
            api_command_prompt_key_bindings,
        ])

        # initiate main prompt session
        initiateMainPrompt()
        if apiCommandSuggestions is None:
            apiCommandSuggestions = {}
        for i in (".quit", ".help", ".settings"):
            apiCommandSuggestions[i] = None
        command_completer = FuzzyCompleter(ThreadedCompleter(NestedCompleter.from_nested_dict(apiCommandSuggestions)))
        auto_suggestion=AutoSuggestFromHistory()
        toolbar = " [ctrl+q] .quit [escape+h] .help "
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

        command = ""
        while True:
            # User command input
            command = config.main_prompt_session.prompt(
                promptIndicator,
                style=style,
                completer=command_completer,
                complete_in_thread=None,
                auto_suggest=auto_suggestion,
                bottom_toolbar=toolbar,
                #default=default,
                key_bindings=config.key_bindings,
                # enable system prompt without auto-completion
                # use escape+!
                enable_system_prompt=True,
                swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")),
                #rprompt="Enter an UBA command",
            ).strip()
            if command:
                if command.lower() == ".quit":
                    break
                #elif command.lower() == ".settings":
                elif not localhost and command.lower() == ".settings":
                    changeSettings()
                    continue
                elif command.lower() == ".help":
                    webbrowser.open("https://github.com/eliranwong/UniqueBibleAPI")
                    continue
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
                
                getApiOutput(command, localhost=localhost)

        clear_title()

    try:
        stdin_text = sys.stdin.read() if not sys.stdin.isatty() else ""
        command = " ".join(sys.argv[2:]).strip()
        if stdin_text:
            command = f"{command} {stdin_text}"

        if command:
            # stream output directly
            getApiOutput(command, localhost=localhost)
        else:
            # interactive mode
            private = f"private={config.web_api_private}&" if config.web_api_private else ""
            r = requests.get(f"{config.web_api_endpoint}?{private}cmd=.suggestions", timeout=config.web_api_timeout)
            r.encoding = "utf-8"
            apiCommandSuggestions = r.json()

            multiturn_api_output(apiCommandSuggestions=apiCommandSuggestions, localhost=localhost)
    
    except:
        #import traceback
        #print(traceback.format_exc())
        print(f"Failed to connect '{config.web_api_endpoint}' at the moment!")
    os.chdir(cwd)

# stream mode
def run_stream_mode():
    cwd = os.getcwd()
    # standard input
    stdin_text = sys.stdin.read() if not sys.stdin.isatty() else ""

    # Set initial command
    command = " ".join(sys.argv[2:]).strip()
    if stdin_text:
        command = f"{command} {stdin_text}"
    if command.strip():
        from uniquebible.util.LocalCliHandler import LocalCliHandler
        config.mainWindow = LocalCliHandler()
        output_text = config.mainWindow.getContent(command, False)
        output_text = re.sub("\n[-]+?$", "", output_text)
        print(output_text, file=sys.stdout)
    else:
        # run terminal mode if no command is given
        config.runMode = "terminal"
        run_terminal_mode()
    os.chdir(cwd)

# ssh-server
# read setup guide at https://github.com/eliranwong/UniqueBible/wiki/Run-SSH-Server
def run_ssh_server(host="", port=2222, server_host_keys="", passphrase="the_best_bible_app"):
    import os, logging, asyncssh
    from prompt_toolkit.eventloop import get_event_loop
    from prompt_toolkit.contrib.ssh import PromptToolkitSSHServer, PromptToolkitSSHSession
    from prompt_toolkit.shortcuts.prompt import PromptSession
    from uniquebible.util.LocalCliHandler import LocalCliHandler
    from prompt_toolkit.shortcuts import print_formatted_text
    from prompt_toolkit.key_binding import KeyBindings

    # set up config.mainWindow for terminal mode
    config.mainWindow = LocalCliHandler()

    async def ubaCommandPrompt(ssh_session: PromptToolkitSSHSession) -> None:

        prompt_session = PromptSession()
        print = print_formatted_text

        print("Running Unique Bible App in ssh-server mode ...")

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
        home = os.path.expanduser("~")
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

# telnet-server
def startTelnetServer():
    try:
        import telnetlib3
    except:
        print("Please run 'pip install telnetlib3' to use remote CLI")
        exit(0)

    try:
        import telnetlib3
        import asyncio
        from uniquebible.util.RemoteCliHandler import RemoteCliHandler

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
def startHttpServer():
    import socketserver
    from uniquebible.util.RemoteHttpHandler import RemoteHttpHandler

    config.restartHttpServer = False
    port = config.httpServerPort
    if (len(sys.argv) > 2):
        port = int(sys.argv[2])
    config.thisHttpServerPort = port
    #ConfigUtil.save()
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

def startApiServer():
    import socketserver
    from uniquebible.util.RemoteApiHandler import RemoteApiHandler

    config.restartApiServer = False
    port = config.httpServerPort
    try:
        if (len(sys.argv) > 2):
            port = int(sys.argv[2])
    except:
        pass
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

# Execute macro
def startMacro():
    if config.enableMacros:
        from uniquebible.util.MacroParser import MacroParser
        if len(sys.argv) < 3:
            print("Please specify macro file to run")
            exit(-1)
        file = sys.argv[2]
        if os.path.isfile(os.path.join(MacroParser.macros_dir, file)):
            from uniquebible.util.RemoteCliMainWindow import RemoteCliMainWindow
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
