import os, subprocess, platform, sys
from uniquebible import config
from uniquebible.util.WebtopUtil import WebtopUtil

cwd = os.getcwd()
thisPlatform = platform.system()
currentReference = config.mainWindow.bcvToVerseReference(config.mainB, config.mainC, config.mainV)

if thisPlatform == "Windows":
    shortcut = os.path.join(cwd, "UniqueBibleAppTerminal.bat")
    subprocess.Popen(f"""start {shortcut}""", shell=True)
elif thisPlatform == "Darwin":
    subprocess.Popen(f"""osascript -e 'tell application "Terminal" to do script "{sys.executable} {cwd}/uba.py terminal {currentReference}"' in window 1""", shell=True)
    subprocess.Popen("""osascript -e 'tell application "Terminal" to activate'""", shell=True)
elif thisPlatform == "Linux" and WebtopUtil.isPackageInstalled("konsole"):
    command = f"konsole -e '{sys.executable} {cwd}/uba.py terminal {currentReference}'"
    subprocess.Popen(command, shell=True)
elif thisPlatform == "Linux" and WebtopUtil.isPackageInstalled("gnome-terminal"):
    command = f"gnome-terminal --command '{sys.executable} {cwd}/uba.py terminal {currentReference}'"
    subprocess.Popen(command, shell=True)
else:
    config.mainWindow.displayMessage("No supported terminal application is found!")