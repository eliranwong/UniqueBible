import os


class MacroParser:

    macros_dir = "macros"

    def parse(main, file):
        filename = os.path.join(MacroParser.macros_dir, file)
        if os.path.isfile(filename):
            file = open(filename, "r")
            lines = file.readlines()
            for line in lines:
                line = line.strip()
                MacroParser.parse_line(main, line)

    def parse_line(main, line):
        try:
            if line.startswith("#") or line.startswith("!") or len(line) == 0:
                pass
            elif line.startswith("."):
                command = line[1:].strip()
                if len(command) > 0:
                    method = command.split(" ")[0]
                    arg_str = command[len(method):]
                    args = arg_str.split(",")
                    if (args[0] == ''):
                        getattr(main, method)()
                    elif (len(args) == 1):
                        getattr(main, method)(args[0].strip())
                    elif (len(args) == 2):
                        getattr(main, method)(args[0].strip(), args[1].strip())
            else:
                main.textCommandLineEdit.setText(line)
                main.runTextCommand(line, forceExecute=True)
        except:
            print("Error running line: {0}".format(line))
