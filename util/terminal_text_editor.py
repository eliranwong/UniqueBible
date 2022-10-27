import config, re, os
from util.TextUtil import TextUtil
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit import PromptSession
from prompt_toolkit import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import clear, set_title
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding import merge_key_bindings
from util.prompt_shared_key_bindings import *
from util.PromptValidator import NumberValidator
from util.get_path import GetPath
from prompt_toolkit import print_formatted_text, HTML
#from prompt_toolkit.application.current import get_app
#get_app().current_buffer.text = ""

class TextEditor:

    def __init__(self, parent=None, custom_save_file_method=None):
        self.parent = parent
        self.filepath = ""
        self.custom_save_file_method = custom_save_file_method
        self.divider = "--------------------"
        self.promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        self.inputIndicator = [
            ("class:indicator", ">>> "),
        ]
        self.getPath = GetPath(
            cancel_entry=config.terminal_cancel_action,
            promptIndicatorColor=config.terminalPromptIndicatorColor2,
            promptEntryColor=config.terminalCommandEntryColor2,
            subHeadingColor=config.terminalHeadingTextColor,
            itemColor=config.terminalResourceLinkColor,
        )

    def prompt_continuation(self, width, line_number, wrap_count):
        if wrap_count > 0:
            return " " * (width - 3) + "-> "
        else:
            text = ("%i " % (line_number + 1)).rjust(width)
            return HTML("<skyblue>%s</skyblue>") % text

    def resetEditor(self):
        self.filepath = ""
        self.custom_save_file_method = None
        self.oldChanges = []
        self.editorCursorPosition = 0
        #self.editor.app.current_buffer.text = ""
        self.textSelection = ""
        self.savedText = ""
        self.textModified = False

    def multilineEditor(self, text="", placeholder=""):
        def goBackEditor():
            answer = False
            while not answer:
                answer = confirm("Go back to editor?")

        editorStartupLine = 1
        initiateEditor = True
        self.savedText = text
        self.textModified = False
        self.editorReload = ""
        self.editorCursorPosition = 0
        self.oldChanges = []
        self.textSelection = ""
        while initiateEditor or self.editorReload:
            initiateEditor = False
            self.editorReload = ""
            text = self.startMultilineEditor(text, placeholder, editorStartupLine)
            if self.editorReload == "e-t" and self.textSelection:
                print(self.divider)
                print(self.parent.googleTranslate(True, self.textSelection))
                print(self.divider)
                self.textSelection = ""
                goBackEditor()
            elif self.editorReload == "e-o" and self.textSelection:
                print(self.divider)
                print(self.parent.quickopen(True, self.textSelection))
                print(self.divider)
                self.textSelection = ""
                goBackEditor()
            elif self.editorReload == "e-f" and self.textSelection:
                print(self.divider)
                print(self.parent.quickSearch(True, self.textSelection))
                print(self.divider)
                self.textSelection = ""
                goBackEditor()
            elif self.editorReload == "e-r":
                print(self.divider)
                print("Enter an UBA command:")
                ubaCommand = self.simplePrompt()
                if ubaCommand and not ubaCommand == config.terminal_cancel_action:
                    print(config.mainWindow.getContent(ubaCommand))
                print(self.divider)
                goBackEditor()
            elif self.editorReload == "e-c":
                print(self.divider)
                try:
                    config.mainWindow.getContent(".system")
                except:
                    pass
                print(self.divider)
                goBackEditor()
            elif self.editorReload == "e-d":
                print(self.divider)
                print(config.mainWindow.getContent(config.terminalDefaultCommand))
                print(self.divider)
                goBackEditor()
            elif self.editorReload == "e-m":
                print(self.divider)
                print(config.mainWindow.getContent(".menu"))
                print(self.divider)
                goBackEditor()
            elif self.editorReload == "e-s" and self.textSelection:
                print(self.divider)
                print(self.parent.tts(True, self.textSelection))
                print(self.divider)
                self.textSelection = ""
            elif self.editorReload == "c-n":
                if self.textModified and confirm("Save changes first?"):
                    self.saveFile()
                self.resetEditor()
                editorStartupLine = 1
                text = ""
            elif self.editorReload == "c-w":
                pass
            elif self.editorReload == "c-p":
                try:
                    exec(self.editor.app.current_buffer.text, globals())
                except:
                    print("Errors!")
                goBackEditor()
            elif self.editorReload == "c-o":
                if self.textModified and confirm("Save changes first?"):
                    self.saveFile()
                self.resetEditor()
                editorStartupLine = 1
                text = self.openFile(getTextOnly=True)
                self.savedText = text
            elif self.editorReload == "c-w":
                self.saveFile()
            elif self.editorReload == "e-w":
                self.saveFile(True)
            elif self.editorReload == "c-g":
                print("Go to line number:")
                lineNumber = self.simplePrompt(True)
                if lineNumber:
                    try:
                        editorStartupLine = int(lineNumber)
                    except:
                        pass
            elif self.editorReload == "c-t":
                print_formatted_text(HTML(self.getEditorHelp()))
                goBackEditor()
            elif self.editorReload == "c-f":
                print("Enter a search pattern:")
                print("(regular expression is supported)")
                searchPattern = self.simplePrompt()
                if searchPattern:
                    try:
                        # line-by-line search results
                        matchedLines = []
                        #buffer = self.editor.app.current_buffer
                        for index, line in enumerate(text.split("\n")):
                            regexp = re.compile(r"({0})".format(searchPattern), flags=re.IGNORECASE)
                            if regexp.search(line) is not None:
                                line = regexp.sub(r"<z>\1</z>", line)
                                matchedLines.append(f"[<ref>line {index + 1}</ref> ]<br>{line}")
                        lineByLineSearchResult = ""
                        if matchedLines:
                            lineByLineSearchResult = f"{self.divider}<h2>Matched lines:</h2>{'<br>'.join(matchedLines)}"
                        # multiline search results
                        allMatches = re.findall(pattern=searchPattern, string=text, flags=re.I | re.M)
                        # we do not use list(set(uniqueMatches)) here, in order to reserve first match order
                        uniqueMatches = []
                        for match in allMatches:
                            if not match in uniqueMatches:
                                uniqueMatches.append(match)
                        multilineSearchResult = ""
                        if uniqueMatches:
                            multilineSearchResultDivider = f"<br>{self.divider}<br>"
                            multilineSearchResult = f"{self.divider}<h2>Multiline matches:</h2>{multilineSearchResultDivider.join(uniqueMatches)}<br>{self.divider}"
                        # display on terminal
                        if lineByLineSearchResult:
                            print(TextUtil.htmlToPlainText(lineByLineSearchResult))
                        if multilineSearchResult:
                            print(TextUtil.htmlToPlainText(multilineSearchResult))
                        if lineByLineSearchResult or multilineSearchResult:
                            replaceAll = confirm("Replace all?")
                            if replaceAll:
                                print(f"""Replace "{searchPattern}" with:""")
                                print("back reference [e.g. \\1, \\2, etc.] is supported")
                                replaceWith = self.simplePrompt()
                                try:
                                    text = re.sub(searchPattern, r"{0}".format(replaceWith), text)
                                except:
                                    print("Invalid entry!")
                        else:
                            print("No match is found!")
                    except:
                        print("Search pattern is invalid!")
                    goBackEditor()
            if not self.editorReload and self.textModified and confirm("Save changes?"):
                # notify if file content is changed
                return self.saveFile()
        return False

    def getKeyBindings(self):
        # work out key bindings
        this_key_bindings = KeyBindings()

        # find and replace
        @this_key_bindings.add("c-f")
        def _(event):
            buffer = event.app.current_buffer
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "c-f"
            buffer.validate_and_handle()
        # go to a specific line
        @this_key_bindings.add("c-g")
        def _(event):
            buffer = event.app.current_buffer
            self.oldChanges = self.editorTextChanges
            self.editorReload = "c-g"
            buffer.validate_and_handle()
        # display tips
        @this_key_bindings.add("c-t")
        def _(event):
            buffer = event.app.current_buffer
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "c-t"
            buffer.validate_and_handle()
        # undo text change
        @this_key_bindings.add("c-z")
        def _(event):
            nextUndoTextIndex = self.undoTextIndex + 1
            if nextUndoTextIndex < len(self.editorTextChanges):
                self.undoTextIndex = nextUndoTextIndex
                self.undoChanging = True
                buffer = event.app.current_buffer
                cursor_position = buffer.cursor_position
                buffer.text = self.editorTextChanges[self.undoTextIndex]
                buffer.cursor_position = cursor_position
        # new file
        @this_key_bindings.add("c-n")
        def _(event):
            buffer = event.app.current_buffer
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "c-n"
            buffer.validate_and_handle()
        # open file
        @this_key_bindings.add("c-o")
        def _(event):
            buffer = event.app.current_buffer
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "c-o"
            buffer.validate_and_handle()
        # run as python script
        @this_key_bindings.add("c-p")
        def _(event):
            buffer = event.app.current_buffer
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "c-p"
            buffer.validate_and_handle()
        # quit editor
        @this_key_bindings.add("c-q")
        def _(event):
            buffer = event.app.current_buffer
            buffer.validate_and_handle()
        # save file
        @this_key_bindings.add("c-w")
        def _(event):
            buffer = event.app.current_buffer
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "c-w"
            buffer.validate_and_handle()
        # save file as ...
        @this_key_bindings.add("escape", "w")
        def _(event):
            buffer = event.app.current_buffer
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "e-w"
            buffer.validate_and_handle()
        # redo text change
        @this_key_bindings.add("escape", "z")
        def _(event):
            nextUndoTextIndex = self.undoTextIndex - 1
            if nextUndoTextIndex >= 0:
                self.undoTextIndex = nextUndoTextIndex
                self.undoChanging = True
                buffer = event.app.current_buffer
                cursor_position = buffer.cursor_position
                buffer.text = self.editorTextChanges[self.undoTextIndex]
                buffer.cursor_position = cursor_position
        # run UBA commands
        @this_key_bindings.add("escape", "r")
        def _(event):
            buffer = event.app.current_buffer
            data = buffer.copy_selection()
            self.textSelection = data.text
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "e-r"
            buffer.validate_and_handle()
        # run system console commands
        @this_key_bindings.add("escape", "c")
        def _(event):
            buffer = event.app.current_buffer
            data = buffer.copy_selection()
            self.textSelection = data.text
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "e-c"
            buffer.validate_and_handle()
        # run quick search on selected text
        @this_key_bindings.add("escape", "f")
        def _(event):
            buffer = event.app.current_buffer
            data = buffer.copy_selection()
            self.textSelection = data.text
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "e-f"
            buffer.validate_and_handle()
        # run quick open on selected text
        @this_key_bindings.add("escape", "o")
        def _(event):
            buffer = event.app.current_buffer
            data = buffer.copy_selection()
            self.textSelection = data.text
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "e-o"
            buffer.validate_and_handle()
        # translate text
        @this_key_bindings.add("escape", "t")
        def _(event):
            buffer = event.app.current_buffer
            data = buffer.copy_selection()
            self.textSelection = data.text
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "e-t"
            buffer.validate_and_handle()
        # open UBA main menu
        @this_key_bindings.add("escape", "m")
        def _(event):
            buffer = event.app.current_buffer
            data = buffer.copy_selection()
            self.textSelection = data.text
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "e-m"
            buffer.validate_and_handle()
        # run UBA default command
        @this_key_bindings.add("escape", "d")
        def _(event):
            buffer = event.app.current_buffer
            data = buffer.copy_selection()
            self.textSelection = data.text
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "e-d"
            buffer.validate_and_handle()
        # text-to-speech
        @this_key_bindings.add("escape", "s")
        def _(event):
            buffer = event.app.current_buffer
            data = buffer.copy_selection()
            self.textSelection = data.text
            self.editorCursorPosition = buffer.cursor_position
            self.oldChanges = self.editorTextChanges
            self.editorReload = "e-s"
            buffer.validate_and_handle()

        # return key_bindings
        return this_key_bindings

    def startMultilineEditor(self, initialText="", placeholder="", editorStartupLine=1):
        
        # define self.editor
        self.editor = PromptSession()
        # keep changed text for undo or redo features
        self.undoTextIndex = 0
        self.undoChanging = False
        if not self.oldChanges:
            self.editorTextChanges = [initialText]
        elif self.oldChanges[0] == initialText:
            self.editorTextChanges = self.oldChanges
        else:
            self.editorTextChanges = [initialText] + self.oldChanges
        self.oldChanges = []
        def trimEditorTextChanges():
            if len(self.editorTextChanges) > config.terminalEditorMaxTextChangeRecords:
                self.editorTextChanges = self.editorTextChanges[0:config.terminalEditorMaxTextChangeRecords]
        trimEditorTextChanges()
        def editor_buffer_changed(buffer):
            if self.undoChanging:
                self.undoChanging = False
            else:
                self.undoTextIndex = 0
                self.editorTextChanges.insert(0, buffer.text)
                trimEditorTextChanges()
                if not buffer.text == self.savedText:
                    self.textModified = True
        # editor startup script
        def pre_run(line=1):
            buffer = self.editor.app.current_buffer
            buffer.on_text_changed += editor_buffer_changed
            buffer.cursor_position = self.editorCursorPosition
            self.editorCursorPosition = 0
            if line > 1:
                buffer.cursor_down(line - 1)
        # work out key bindings
        # this_key_bindings = self.getKeyBindings()
        this_key_bindings = merge_key_bindings([
            prompt_shared_key_bindings,
            self.getKeyBindings(),
        ])
        # set title
        set_title("Editor")
        # clear current screen first to allow more space
        clear()
        #print("Press 'Escape+Enter' when you finish editing!")
        # define style
        promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        inputIndicator = [
            ("class:indicator", "   1 "),
        ]
        bottom_toolbar = "[ctrl+q] quit [ctrl+t] tips"
        # multiline prompt
        userInput = self.editor.prompt(
            inputIndicator,
            style=promptStyle,
            multiline=True,
            default=initialText,
            prompt_continuation=self.prompt_continuation,
            placeholder=placeholder,
            key_bindings=this_key_bindings,
            pre_run=lambda: pre_run(editorStartupLine),
            mouse_support=True,
            bottom_toolbar=bottom_toolbar,
        )
        set_title("")
        return userInput

    def simplePrompt(self, numberOnly=False, multiline=False, inputIndicator=""):
        if not inputIndicator:
            inputIndicator = self.inputIndicator
        if numberOnly:
            if multiline:
                self.printMultineNote()
            userInput = prompt(inputIndicator, style=self.promptStyle, validator=NumberValidator(), multiline=multiline).strip()
        else:
            userInput = prompt(inputIndicator, style=self.promptStyle, multiline=multiline).strip()
        return userInput

    def newFile(self):
        return self.multilineEditor("", "[type here ...]")

    def openFile(self, filepath="", getTextOnly=False):
        if not filepath:
            filepath = self.getPath.getFilePath(True)
        if os.path.isfile(filepath):
            text = self.getFileText(filepath)
            if getTextOnly:
                return text
            else:
                # return True if file content is changed
                return self.multilineEditor(text)
        else:
            return "" if getTextOnly else False

    def getFileText(self, filepath):
        if os.path.isfile(filepath):
            with open(filepath, "r", encoding="utf-8") as fileObj:
                text = fileObj.read()
            self.filepath = filepath
            self.savedText = text
            return text
        return ""

    def saveFile(self, saveAs=False):
        def failSavingFile():
            print("Failed to save file!")
            print("Make sure you have permission to write the given filepath!")
            return False
        text = self.editor.app.current_buffer.text
        if self.custom_save_file_method is not None and not self.filepath and not saveAs:
            self.custom_save_file_method(text)
        else:
            if not self.filepath or saveAs:
                filepath = self.getPath.getFilePath()
                if not filepath:
                    return False
                else:
                    if os.path.isfile(filepath) and not confirm("Overwrite existing file?"):
                        return False
                    try:
                        with open(filepath, "w", encoding="utf-8") as fileObj:
                            fileObj.write(text)
                        self.filepath = filepath
                    except:
                        return failSavingFile()
            else:
                try:
                    with open(self.filepath, "w", encoding="utf-8") as fileObj:
                        fileObj.write(text)
                except:
                    return failSavingFile()
        self.savedText = text
        return True

    def getEditorHelp(self):
        # keep original key bindings here for reference
        # some of the key bindings are overwritten by UBA
        """
        # Multiline input built-in key bindings:
        Ctrl+W remove non-numerical words before cursor
        Ctrl+U delete all words before cursor
        Ctrl+K delete all words under and after cursor

        Ctrl+O complete prompt open

        Ctrl+A go to current line starting position
        Ctrl+E go to current line ending position

        Ctrl+P one line up
        Ctrl+N one line down

        Ctrl+S I-search
        Ctrl+R reverse I-search

        Ctrl+C Keyboard Interrupt

        Ctrl+D delete the char under cursor
        Ctrl+H delete the char before cursor

        Ctrl+J enter one new line
        Ctrl+M enter one new line

        Ctrl+F one character forward
        Ctrl+B one character backward

        Ctrl+T swap with previous char"""

        return """{0}
<b># Key bindings:</b>

<b># Essential</b>
<{1}>ctrl+q</{1}> quit
<{1}>ctrl+t</{1}> show tips

<b># Editing</b>
<{1}>ctrl+c</{1}> copy selected text
<{1}>ctrl+x</{1}> copy selected text
<{1}>ctrl+v</{1}> paste clipboard text

<{1}>ctrl+z</{1}> undo
<{1}>escape+z</{1}> redo

<{1}>ctrl+i</{1}> insert TAB text, defined by config.terminalEditorTabText
<{1}>ctrl+u</{1}> delete characters before cursor in the current line
<{1}>ctrl+k</{1}> delete characters after cursor in the current line
<{1}>ctrl+h</{1}> delete one character before cursor or selected text 
<{1}>ctrl+d</{1}> delete one character after cursor

<b># Searching</b>
<{1}>ctrl+s</{1}> I-search
<{1}>ctrl+r</{1}> reverse I-search
<{1}>ctrl+f</{1}> find and replace with regular expression

<b># Text Selection</b>
<{1}>ctrl+a</{1}> select all
<{1}>escape+t</{1}> translate selected text
<{1}>escape+s</{1}> say selected text
<{1}>escape+f</{1}> quick search UBA resources for selected text
<{1}>escape+o</{1}> quick open UBA resources with selected text

<b># File I/O</b>
<{1}>ctrl+n</{1}> new file
<{1}>ctrl+o</{1}> open file
<{1}>ctrl+w</{1}> write file [save]
<{1}>escape+w</{1}> write file as [save as]

<b># Commands</b>
<{1}>ctrl+p</{1}> run as python script
<{1}>escape+m</{1}> open UBA main menu
<{1}>escape+d</{1}> run UBA default command
<{1}>escape+r</{1}> run UBA commands
<{1}>escape+c</{1}> run system concole commands

<b># Navigation</b>
<{1}>home</{1}> go to current line starting position
<{1}>end</{1}> go to current line ending position
<{1}>ctrl+j</{1}> go to current line starting position
<{1}>ctrl+e</{1}> go to current line ending position
<{1}>escape+j</{1}> go to document starting position
<{1}>escape+e</{1}> go to document line ending position
<{1}>ctrl+g</{1}> go to a spcific line
<{1}>pageup</{1}> go up number of lines, defined by config.terminalEditorScrollLineCount
<{1}>pagedown</{1}> go down number of lines, defined by config.terminalEditorScrollLineCount
<{1}>ctrl+y</{1}> same as pageup
<{1}>ctrl+b</{1}> same as pagedown

<{1}>escape+1</{1}> go up line 10 lines
<{1}>escape+2</{1}> go up line 20 lines
<{1}>escape+3</{1}> go up line 30 lines
<{1}>escape+4</{1}> go up line 40 lines
<{1}>escape+5</{1}> go up line 50 lines
<{1}>escape+6</{1}> go up line 60 lines
<{1}>escape+7</{1}> go up line 70 lines
<{1}>escape+8</{1}> go up line 80 lines
<{1}>escape+9</{1}> go up line 90 lines
<{1}>escape+0</{1}> go up line 100 lines

<{1}>f1</{1}> go down line 10 lines
<{1}>f2</{1}> go down line 20 lines
<{1}>f3</{1}> go down line 30 lines
<{1}>f4</{1}> go down line 40 lines
<{1}>f5</{1}> go down line 50 lines
<{1}>f6</{1}> go down line 60 lines
<{1}>f7</{1}> go down line 70 lines
<{1}>f8</{1}> go down line 80 lines
<{1}>f9</{1}> go down line 90 lines
<{1}>f10</{1}> go down line 100 lines

{0}""".format(self.divider, config.terminalResourceLinkColor)
