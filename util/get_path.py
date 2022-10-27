import platform, os, subprocess

class GetPath:

    def __init__(self, cancel_entry=".cancel", promptIndicatorColor="yellow", promptEntryColor="skyblue", subHeadingColor="cyan", itemColor="skyblue"):
        self.cancel_entry = cancel_entry
        self.promptIndicatorColor = promptIndicatorColor
        self.promptEntryColor = promptEntryColor
        self.subHeadingColor = subHeadingColor
        self.itemColor = itemColor

    def listDirectoryContent(self):
        dirs = []
        files = []
        for i in os.listdir():
            if os.path.isdir(i):
                dirs.append(i)
            elif os.path.isfile(i):
                files.append(i)
        return(dirs, files)

    def displayDirectoryContent(self, display_dir_only=False):

        def printDirsFiles(display_dir_only=display_dir_only):
            dirs, files = self.listDirectoryContent()
            print("Directories:")
            print(" | ".join(sorted(dirs)))
            if not display_dir_only:
                print("Files:")
                print(" | ".join(sorted(files)))

        def printFormattedDirsFiles(display_dir_only=display_dir_only):
            # require prompt-toolkit
            from prompt_toolkit import print_formatted_text, HTML

            # read more color codes at https://github.com/prompt-toolkit/python-prompt-toolkit/blob/65c3d0607c69c19d80abb052a18569a2546280e5/src/prompt_toolkit/styles/named_colors.py
            dirs, files = self.listDirectoryContent()
            separator = '</{0}> | <{0}>'.format(self.itemColor)
            dirs = "<{0}>{1}</{0}>".format(self.itemColor, separator.join(dirs))
            print_formatted_text(HTML("<b><{0}>Directories</{0}></b>".format(self.subHeadingColor)))
            print_formatted_text(HTML(dirs))
            if not display_dir_only:
                files = "<{0}>{1}</{0}>".format(self.itemColor, separator.join(files))
                print_formatted_text(HTML("<b><{0}>Files</{0}></b>".format(self.subHeadingColor)))
                print_formatted_text(HTML(files))
        
        try:
            # when prompt-toolkit is installed
            printFormattedDirsFiles(display_dir_only=display_dir_only)
        except:
            printDirsFiles(display_dir_only=display_dir_only)

    def confirm_prompt(self, message):
        try:
            from prompt_toolkit.shortcuts import confirm
            return confirm(message)
        except:
            userInput = input(f"{message} (y/n)").strip()
            return True if userInput.lower() in ("y", "yes") else False

    def getFilePath(self, check_isfile=False, empty_to_cancel=False, message=""):
        if not message:
            message = "Enter a file path:"
        return self.getPath(check_isfile=check_isfile, empty_to_cancel=empty_to_cancel, message=message)

    def getFolderPath(self, check_isdir=False, display_dir_only=False, create_dirs_if_not_exist=False, empty_to_cancel=False, message=""):
        if not message:
            message = "Enter a directory path:"
        return self.getPath(check_isdir=check_isdir, display_dir_only=display_dir_only, create_dirs_if_not_exist=create_dirs_if_not_exist, empty_to_cancel=empty_to_cancel, message=message)

    def getPath(self, check_isfile=False, check_isdir=False, display_dir_only=False, create_dirs_if_not_exist=False, empty_to_cancel=False, message=""):
        if not message:
            message = "Enter a path:"
        thisPath = os.getcwd()

        def returnPath(path=""):
            os.chdir(thisPath)
            return path

        promptEntry = True
        while promptEntry:
            promptEntry = False
            print(message)
            indicator = "{0} {1} ".format(os.path.basename(os.getcwd()), "%")
            try:
                # prompt toolkit is installed
                from prompt_toolkit.completion import PathCompleter
                from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
                from prompt_toolkit.key_binding import KeyBindings
                from prompt_toolkit import PromptSession
                from prompt_toolkit.history import FileHistory
                from prompt_toolkit.styles import Style
                from prompt_toolkit.application import run_in_terminal

                filePathHistory = os.path.join(thisPath, "terminal_history", "file_path")
                filePathSession = PromptSession(history=FileHistory(filePathHistory))

                # key bindings
                this_key_bindings = KeyBindings()
                @this_key_bindings.add("c-q")
                def _(event):
                    event.app.current_buffer.text = self.cancel_entry
                    event.app.current_buffer.validate_and_handle()
                @this_key_bindings.add("c-l")
                def _(_):
                    # list directories and files
                    run_in_terminal(lambda: self.displayDirectoryContent(display_dir_only=display_dir_only))

                inputIndicator = [("class:indicator", indicator)]
                completer = PathCompleter()
                auto_suggestion=AutoSuggestFromHistory()
                promptStyle = Style.from_dict({
                    # User input (default text).
                    "": self.promptEntryColor,
                    # Prompt.
                    "indicator": self.promptIndicatorColor,
                })
                bottom_toolbar = "cd [folder]: change dir; ctrl+l: list content; ctrl+q: quit"
                userInput = filePathSession.prompt(
                    inputIndicator,
                    style=promptStyle,
                    key_bindings=this_key_bindings,
                    auto_suggest=auto_suggestion,
                    completer=completer,
                    bottom_toolbar=bottom_toolbar,
                    #mouse_support=True,
                ).strip()
            except:
                self.displayDirectoryContent(display_dir_only=display_dir_only)
                if platform.system() == "Windows":
                    userInput = input(indicator).strip()
                else:
                    # use read command for auto-suggestion of filepath
                    # –e: use the Bash built-in Readline library to read the input line
                    # –p: prompt: print the prompt text before requesting the input from the standard input stream without a <newline> character
                    userInput = subprocess.check_output(f'read -e -p "{indicator}" var ; echo $var', shell=True).strip()
                    userInput = userInput.decode("utf-8")

            if not userInput.startswith("cd ") and create_dirs_if_not_exist and not os.path.isdir(userInput):
                os.makedirs(userInput, exist_ok=True)

            if userInput.startswith("cd ") and os.path.isdir(userInput[3:]):
                os.chdir(userInput[3:])
                userInput = ""
                promptEntry = True
            elif (not userInput and empty_to_cancel) or (userInput == self.cancel_entry and not os.path.isfile(userInput)):
                return returnPath()
            elif not userInput and self.confirm_prompt("Try again?"):
                promptEntry = True
            elif userInput and check_isdir and not os.path.isdir(userInput):
                if self.confirm_prompt("No such directory! Try again?"):
                    promptEntry = True
                else:
                    return returnPath()
            elif userInput and check_isfile and not os.path.isfile(userInput):
                if self.confirm_prompt("No such file! Try again?"):
                    promptEntry = True
                else:
                    return returnPath()
        return returnPath(userInput)
