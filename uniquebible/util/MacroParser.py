import os
from uniquebible import config


class MacroParser:

    macros_dir = "macros"

    def __init__(self, parent):
        self.lines = None
        self.parent = parent
        self.ifStack = {0: IF.na}
        self.ifDepth = 0
        self.mapping = {}

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
            for key, value in vars(config).items():
                self.mapping[key] = value
            line = line.format(**self.mapping)
            if len(line) == 0 or line[0] in ['#', "!", ":"]:
                pass
            elif line.lower().startswith("if "):
                self.ifDepth += 1
                if eval(line[3:]):
                    self.ifStack[self.ifDepth] = IF.match
                else:
                    self.ifStack[self.ifDepth] = IF.nomatch
            elif line.lower().startswith("elif "):
                if self.ifStack[self.ifDepth] == IF.match:
                    return self.gotoMatchingEndIf(currentLine)
                elif eval(line[4:]):
                    self.ifStack[self.ifDepth] = IF.match
                else:
                    self.ifStack[self.ifDepth] = IF.nomatch
            elif line.lower().startswith("else"):
                if self.ifStack[self.ifDepth] == IF.match:
                    return self.gotoMatchingEndIf(currentLine)
                else:
                    self.ifStack[self.ifDepth] = IF.match
            elif line.lower().strip() == "fi":
                self.ifDepth -= 1
                self.ifStack[self.ifDepth] = IF.na
            elif self.ifStack[self.ifDepth] == IF.nomatch:
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
                if hasattr(self.parent, "textCommandLineEdit"):
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

    def gotoMatchingEndIf(self, startFrom):
        index = startFrom
        count = 0
        while index < len(self.lines):
            line = self.lines[index]
            if line.strip() == "fi":
                if count == 0:
                    return index
                else:
                    count -= 1
            elif line.strip().startswith("if "):
                count += 1
            index += 1
        print("Could not find matching fi")
        return -1

class IF:
    na = 0
    match = 1
    nomatch = 2

class Dummy:
    def closePopover(self):
        pass

    def runTextCommand(self, command):
        print(command)

    def displayMessage(self, command):
        print(command)


if __name__ == "__main__":

    parser = MacroParser(Dummy())
    parser.parse("/home/oliver/dev/UniqueBible/macros/save/TestNestedIf.ubam")
