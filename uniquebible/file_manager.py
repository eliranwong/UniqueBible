from uniquebible import config
import os, platform, subprocess
from uniquebible.util.get_path_prompt import GetPath
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style


class FileManager:
    def __init__(self, workingDirectory=""):
        self.getPath = GetPath(
            cancel_entry=config.terminal_cancel_action,
            promptIndicatorColor=config.terminalPromptIndicatorColor2,
            promptEntryColor=config.terminalCommandEntryColor2,
            subHeadingColor=config.terminalHeadingTextColor,
            itemColor=config.terminalResourceLinkColor,
            workingDirectory=workingDirectory,
            ctrl_q_to_exit=True,
            ctrl_s_to_system=True,
        )
        self.setOsOpenCmd()
        self.startup()

    def setOsOpenCmd(self):
        if config.terminalEnableTermuxAPI:
            self.openCommand = "termux-share"
        elif platform.system() == "Linux":
            self.openCommand = config.openLinux
        elif platform.system() == "Darwin":
            self.openCommand = config.openMacos
        elif platform.system() == "Windows":
            self.openCommand = config.openWindows

    def startup(self):
        print("Mini File Manager")
        while True:
            userInput = self.getPath.getPath(
                check_isfile=True,
                check_isdir=True,
                display_dir_only=False,
                create_dirs_if_not_exist=False,
                empty_to_cancel=True,
                list_content_on_directory_change=True,
                keep_startup_directory=False,
                message="Enter a directory or file:",
                bottom_toolbar="[ctrl+q] quit [ctrl+s] system commands",
            )
            if userInput == ".system":
                self.system()
            elif userInput == ".quit":
                break
            elif not userInput:
                self.getPath.displayDirectoryContent()
            else:
                userInput = f'"{userInput}"'
                os.system(f"""{self.openCommand} {userInput}""")

    def getSystemCommands(self):
        try:
            options = subprocess.Popen("bash -c 'compgen -ac | sort'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = options.communicate()
            options = stdout.decode("utf-8").split("\n")
            options = [option for option in options if option and not option in ("{", "}", ".", "!", ":")]
            return options
        except:
            return []

    def system(self):
        self.divider = "--------------------"
        system_command_history = os.path.join(os.getcwd(), "system_command")
        self.terminal_system_command_session = PromptSession(history=FileHistory(system_command_history))
        self.promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        self.runSystemCommandPrompt = True
        # initial message
        print("You are now using system command prompt!")
        print(f"To go back, either press 'ctrl+q' or run '{config.terminal_cancel_action}'.")
        # keep current path in case users change directory
        ubaPath = os.getcwd()

        this_key_bindings = KeyBindings()
        @this_key_bindings.add("c-q")
        def _(event):
            event.app.current_buffer.text = config.terminal_cancel_action
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-l")
        def _(_):
            print("")
            print(self.divider)
            run_in_terminal(lambda: self.getPath.displayDirectoryContent())

        userInput = ""
        systemCommands = self.getSystemCommands()
        while self.runSystemCommandPrompt and not userInput == config.terminal_cancel_action:
            try:
                indicator = "{0} {1} ".format(os.path.basename(os.getcwd()), "%")
                inputIndicator = [("class:indicator", indicator)]
                dirIndicator = "\\" if platform.system() == "Windows" else "/"
                completer = FuzzyCompleter(WordCompleter(sorted(set(systemCommands + [f"{i}{dirIndicator}" if os.path.isdir(i) else i for i in os.listdir()]))))
                auto_suggestion=AutoSuggestFromHistory()
                userInput = self.terminal_system_command_session.prompt(inputIndicator, style=self.promptStyle, key_bindings=this_key_bindings, auto_suggest=auto_suggestion, completer=completer).strip()
                #userInput = self.simplePrompt(inputIndicator=inputIndicator).strip()
                if userInput and not userInput == config.terminal_cancel_action:
                    userInput = userInput.replace("~", os.path.expanduser("~"))
                    os.system(userInput)
                    # check if directory is changed
                    #userInput = re.sub("^.*?[ ;&]*(cd .+?)[;&]*$", r"\1", userInput)
                    cmdList = []
                    userInput = userInput.split(";")
                    for i in userInput:
                        subList = i.split("&")
                        cmdList += subList
                    cmdList = [i.strip() for i in cmdList if i and i.strip().startswith("cd ")]
                    if cmdList:
                        lastDir = cmdList[-1][3:]
                        if os.path.isdir(lastDir):
                            os.chdir(lastDir)
            except:
                pass
        os.chdir(ubaPath)

if __name__ == "__main__":
    workingDirectory = os.path.dirname(os.path.realpath(__file__))
    fileManager = FileManager(workingDirectory)

    # TODO add filter, copy/paste/move multple files, create folders, integrate text editor
