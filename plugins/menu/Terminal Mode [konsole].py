import os, subprocess, config, platform
from util.WebtopUtil import WebtopUtil

if platform.system() == "Windows":
    config.mainWindow.displayMessage("This plugin does not support Windows.")
elif WebtopUtil.isPackageInstalled("konsole"):
    cwd = os.getcwd()
    command = f"konsole -e 'python3 {cwd}/uba.py terminal'"
    subprocess.Popen(command, shell=True)
else:
    config.mainWindow.displayMessage("Install terminal application 'konsole' first!")