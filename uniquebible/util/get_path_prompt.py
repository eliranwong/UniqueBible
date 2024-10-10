#!/usr/bin/env python
"""
source: https://github.com/eliranwong/get-path-prompt

'get-path-prompt' prompts terminal users for entry of a file or directory path.

Recommended:
You can run 'get-path-prompt' with or without prompt_toolkit.
With prompt_toolkit installed, however, you can use all features we will mention below.
To install prompt_toolkit, run:
> pip install prompt_toolkit

Features:
* prompts for a file or folder path entry
* option to define prompt indicator and text colors
* option to check existence of the entered path
* option to create directories if they do not exist
* auto-history-saving - use up or down keys to get previous entered records
* auto-suggestion from history - use right arrow key to complete a suggestion
* auto-completion of file or directory path
* support command 'cd' to change directories
* support command 'ls' to list directory content
* customise cancel entry or allow empty entry to close the prompt
* built-in key bindings - ctrl+q to quit prompt, ctrl+l to list directory content
* confirm if users want to continue if invalid option is entered
* easily integrated into python project,

For example, we integrate this utility into a text editor we developed:
https://github.com/eliranwong/UniqueBible/blob/main/util/terminal_text_editor.py
"""

import platform, os, subprocess

class GetPath:

    def __init__(self, cancel_entry=".cancel", promptIndicatorColor="ansicyan", promptEntryColor="ansigreen", subHeadingColor="ansigreen", itemColor="ansiyellow", workingDirectory="", ctrl_q_to_exit=False, ctrl_s_to_system=False):
        self.cancel_entry = cancel_entry
        self.promptIndicatorColor = promptIndicatorColor
        self.promptEntryColor = promptEntryColor
        self.subHeadingColor = subHeadingColor
        self.itemColor = itemColor
        self.workingDirectory = workingDirectory
        self.ctrl_q_to_exit = ctrl_q_to_exit
        self.ctrl_s_to_system = ctrl_s_to_system

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

    def getFilePath(self, check_isfile=False, empty_to_cancel=False, list_content_on_directory_change=False, keep_startup_directory=True, message="", bottom_toolbar="", promptIndicator = ""):
        if not message:
            message = "Enter a file path:"
        return self.getPath(check_isfile=check_isfile, empty_to_cancel=empty_to_cancel, list_content_on_directory_change=list_content_on_directory_change, keep_startup_directory=keep_startup_directory, message=message, bottom_toolbar=bottom_toolbar, promptIndicator=promptIndicator)

    def getFolderPath(self, check_isdir=False, display_dir_only=False, create_dirs_if_not_exist=False, empty_to_cancel=False, list_content_on_directory_change=False, keep_startup_directory=True, message="", bottom_toolbar="", promptIndicator = ""):
        if not message:
            message = "Enter a directory path:"
        return self.getPath(check_isdir=check_isdir, display_dir_only=display_dir_only, create_dirs_if_not_exist=create_dirs_if_not_exist, empty_to_cancel=empty_to_cancel, list_content_on_directory_change=list_content_on_directory_change, keep_startup_directory=keep_startup_directory, message=message, bottom_toolbar=bottom_toolbar, promptIndicator=promptIndicator)

    def getPath(self, check_isfile=False, check_isdir=False, display_dir_only=False, create_dirs_if_not_exist=False, empty_to_cancel=False, list_content_on_directory_change=False, keep_startup_directory=True, message="", bottom_toolbar="", promptIndicator = ""):
        if not message:
            message = "Enter a path:"
        thisPath = os.getcwd()

        def returnPath(path="", keep_startup_directory=keep_startup_directory):
            if path:
                fullpath = os.path.join(os.getcwd(), path)
                if os.path.exists(fullpath):
                    path = fullpath
            if keep_startup_directory:
                os.chdir(thisPath)
            return path

        def changeDirectory(path, list_content_on_directory_change=False):
            os.chdir(path)
            if list_content_on_directory_change:
                self.displayDirectoryContent()

        promptEntry = True
        while promptEntry:
            promptEntry = False
            print(message)
            indicator = promptIndicator if promptIndicator else "{0} {1} ".format(os.path.basename(os.getcwd()), "%")
            try:
                # prompt toolkit is installed
                from prompt_toolkit.completion import PathCompleter
                from prompt_toolkit import PromptSession
                from prompt_toolkit.history import FileHistory
                from prompt_toolkit.styles import Style
                from prompt_toolkit.application import run_in_terminal
                from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
                from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
                from uniquebible.util.prompt_shared_key_bindings import prompt_shared_key_bindings

                wd = self.workingDirectory if self.workingDirectory else thisPath
                if os.path.isdir(os.path.join(wd, "terminal_history")):
                    filePathHistory = os.path.join(wd, "terminal_history", "get-path-prompt")
                else:
                    filePathHistory = os.path.join(wd, "get-path-prompt")
                filePathSession = PromptSession(history=FileHistory(filePathHistory))

                # key bindings
                this_key_bindings = KeyBindings()
                if self.ctrl_s_to_system:
                    @this_key_bindings.add("c-s")
                    def _(event):
                        event.app.current_buffer.text = ".system"
                        event.app.current_buffer.validate_and_handle()
                @this_key_bindings.add("c-q")
                def _(event):
                    if self.ctrl_q_to_exit:
                        event.app.current_buffer.text = ".quit"
                    else:
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
                this_key_bindings = merge_key_bindings([
                    this_key_bindings,
                    prompt_shared_key_bindings,
                ])
                if not bottom_toolbar:
                    bottom_toolbar = "[cd [folder]] change dir; [ls]/[ctrl+l] list content; [ctrl+q] quit"
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

            if userInput == ".quit":
                return returnPath(".quit")
            elif userInput == ".system":
                return returnPath(".system")
            elif userInput.startswith("cd ") and os.path.isdir(userInput[3:]):
                changeDirectory(userInput[3:], list_content_on_directory_change)
                userInput = ""
                promptEntry = True
            elif (userInput == "ls" or userInput.startswith("ls ")) and not os.path.exists(userInput):
                try:
                    os.system(userInput)
                except:
                    pass
                userInput = ""
                promptEntry = True
            elif (not userInput and empty_to_cancel) or (userInput == self.cancel_entry and not os.path.isfile(userInput)):
                return returnPath()
            elif not userInput and self.confirm_prompt("Try again?"):
                promptEntry = True
            elif check_isdir and check_isfile:
                if not os.path.isdir(userInput) and not os.path.isfile(userInput) and self.confirm_prompt("No such file or directory! Try again?"):
                    promptEntry = True
                elif os.path.isdir(userInput) and not os.path.isfile(userInput):
                    changeDirectory(userInput, list_content_on_directory_change)
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

if __name__ == '__main__':
    try:
        from prompt_toolkit import prompt
    except:
        try:
            print("Installing prompt_toolkit ...")
            os.system("pip install prompt_toolkit")
        except:
            pass
    try:
        from prompt_toolkit import prompt
    except:
        print("Package 'prompt_toolkit' is not found! Install it to include better display and auto-completion feature.")

    getPath = GetPath()

    filePath = getPath.getFilePath()
    print(f"File path entered: {filePath}")
    print("")
    folderPath = getPath.getFolderPath()
    print(f"Folder path entered: {folderPath}")
