import platform, subprocess
from uniquebible import config

thisPlatform = platform.system()
commands = {
    "Darwin": "open -b com.apple.terminal",
    "Windows": "start powershell.exe",
    "Linux": config.openLinuxTerminal,
}

subprocess.Popen(commands[thisPlatform], shell=True)