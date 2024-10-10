from uniquebible import config
import re, os, sys, subprocess, platform

if config.pluginContext:
    if re.match("^[GH][0-9]+?$", config.pluginContext):
        generate = subprocess.Popen("{0} {1} {2}".format(sys.executable, os.path.join("plugins", "context", "Strongs2csv", "strong2csv.py"), config.pluginContext), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        *_, stderr = generate.communicate()
        outputFile = os.path.join("plugins", "context", "Strongs2csv", "{0}.csv".format(config.pluginContext))
        if not stderr and os.path.isfile(outputFile):
            if platform.system() == "Linux":
                subprocess.Popen([config.open, outputFile])
            else:
                os.system("{0} {1}".format(config.open, outputFile))
    else:
        config.mainWindow.displayMessage("Selected text is not a Strong's number!")
else:
    config.contextSource.messageNoSelection()
