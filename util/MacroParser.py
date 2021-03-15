import os
import config


class MacroParser:

    macros_dir = "macros"

    def __init__(self, parent):
        self.lines = None
        self.parent = parent
        self.ifState = IF.na

    def parse(self, file):
        filename = os.path.join(MacroParser.macros_dir, file)
        if os.path.isfile(filename):
            config.macroIsRunning = True
            file = open(filename, "r")
            self.lines = file.readlines()
            currentLine = 0
            config.quitMacro = False
            while(currentLine < len(self.lines)) and not config.quitMacro:
                currentLine = self.parseLine(currentLine)
            self.parent.closePopover()
            config.macroIsRunning = False

    def parseLine(self, currentLine):
        try:
            line = self.lines[currentLine].strip()
            if line.startswith("#") or line.startswith("!") or len(line) == 0:
                pass
            elif line.lower().startswith("if "):
                if eval(line[3:]):
                    self.ifState = IF.match
                else:
                    self.ifState = IF.nomatch
            elif line.lower().startswith("elif "):
                if self.ifState == IF.match:
                    return self.goto("fi", currentLine)
                elif eval(line[4:]):
                    self.ifState = IF.match
                else:
                    self.ifState = IF.nomatch
            elif line.lower().startswith("else"):
                if self.ifState == IF.match:
                    return self.goto("fi", currentLine)
                else:
                    self.ifState = IF.match
            elif line.lower().strip() == "fi":
                self.ifState = IF.na
            elif self.ifState == IF.nomatch:
                pass
            elif line.lower().startswith("goto "):
                num = self.findLabel(line[5:])
                if num >= 0:
                    return num
            elif line.startswith("config."):
                exec(line)
            elif line.startswith("."):
                command = line[1:].strip()
                if len(command) > 0:
                    method = command.split(" ")[0]
                    arg_str = command[len(method):]
                    args = arg_str.split(",")
                    if (args[0] == ''):
                        getattr(self.parent, method)()
                    elif (len(args) == 1):
                        getattr(self.parent, method)(args[0].strip())
                    elif (len(args) == 2):
                        getattr(self.parent, method)(args[0].strip(), args[1].strip())
            else:
                self.parent.textCommandLineEdit.setText(line)
                self.parent.runTextCommand(line, forceExecute=True)
        except Exception as e:
            print("Error running line: {0}".format(line))
            print("{0}".format(e))
        currentLine += 1
        return currentLine

    def findLabel(self, label):
        index = 0
        for line in self.lines:
            if line.startswith(":"+label):
                return index
            index += 1
        print("Could not find label {0}".format(label))
        return -1

    def goto(self, label, startFrom):
        index = startFrom
        while index < len(self.lines):
            line = self.lines[index]
            if line.strip() == label:
                return index
            index += 1
        print("Could not go to {0}".format(label))
        return -1

class IF:
    na = 0
    match = 1
    nomatch = 2
