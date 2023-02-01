#!/usr/bin/env python3

import os, sys, subprocess, platform
from shutil import copyfile
from install.module import *

# requires python 3.7+
if sys.version_info < (3, 7):
    print("Required python version [3.7 or above] is not found!")
    print("Closing ...")
    exit(1)

# set enviornment variables
os.environ["PYTHONUNBUFFERED"] = "1"

# check running mode and initial command
runMode = sys.argv[1] if len(sys.argv) > 1 else ""
enableCli = True if runMode.lower() in ("cli", "cli.py", "gui", "terminal", "docker", "telnet-server", "http-server", "execute-macro", "api-server") else False
initialCommand = input("Enter command: ").strip() if runMode == "-i" else " ".join(sys.argv[1:]).strip()
initialCommand = initialCommand.strip()

# define directories
# set working directory
thisFile = os.path.realpath(__file__)
wd = os.path.dirname(thisFile)
if os.getcwd() != wd:
    os.chdir(wd)
# Do NOT use sys.executable directly
python = os.path.basename(sys.executable)
mainFile = os.path.join(wd, "main.py")
major, minor, micro, *_ = sys.version_info
thisOS = platform.system()
cpu = ""
if thisOS == "Darwin":
    thisOS = "macOS"
    *_, cpu = platform.mac_ver()
    cpu = f"_{cpu}"
venvDir = "venv_{0}{4}_{1}.{2}.{3}".format(thisOS, major, minor, micro, cpu)
binDir = "Scripts" if thisOS == "Windows" else "bin"

# Check if virtual environment is being used
if sys.prefix == sys.base_prefix:
    # Check if virtual environment is available
    venvPython = os.path.join(wd, venvDir, binDir, python)
    if not os.path.exists(venvPython):
        # Installing virtual environment
        # https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
        try:
            import venv
        except:
            installmodule("virtualenv", False)
        #subprocess.Popen([python, "-m", "venv", venvDir])
        print("Setting up environment ...")
        # optional: add file "use_system_site_packages" in UBA direcyory to use packages installed on system
        try:
            if not "venv" in sys.modules:
                import venv
            venv.create(env_dir=venvDir, with_pip=True, system_site_packages=True) if runMode == "docker" or os.path.isfile("use_system_site_packages") else venv.create(env_dir=venvDir, with_pip=True)
        except:
            pass

# create shortcut files
# On Windows
if thisOS == "Windows":
    # Create a .bat for application shortcut
    shortcutBat = os.path.join(wd, "UniqueBibleApp.bat")
    if not os.path.exists(shortcutBat):
        with open(shortcutBat, "w") as fileObj:
            fileObj.write('{0} "{1}"'.format(sys.executable, thisFile))
# On non-Windows platforms
else:
    # Create application shortcuts and set file permission
    shortcutSh = os.path.join(wd, "uba.sh")
    if not os.path.exists(shortcutSh):
        # Create .sh shortcut
        with open(shortcutSh, "w") as fileObj:
            fileObj.write("#!{0}\n{1} {2}".format(os.environ["SHELL"], sys.executable, thisFile))
        # Set permission
        for file in (thisFile, "main.py", "util/BibleVerseParser.py", "util/RegexSearch.py", shortcutSh):
            try:
                os.chmod(file, 0o755)
            except:
                pass
# Additional shortcuts on Linux
if thisOS == "Linux":
    def desktopFileContent():
        iconPath = os.path.join(wd, "htmlResources", "UniqueBibleApp.png")
        return """#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Path={0}
Exec={1} {2}
Icon={3}
Name=Unique Bible App
""".format(wd, sys.executable, thisFile, iconPath)

    ubaLinuxDesktopFile = os.path.join(wd, "UniqueBibleApp.desktop")
    if not os.path.exists(ubaLinuxDesktopFile):
        # Create .desktop shortcut
        with open(ubaLinuxDesktopFile, "w") as fileObj:
            fileObj.write(desktopFileContent())
        try:
            # Try to copy the newly created .desktop file to:
            from pathlib import Path
            # ~/.local/share/applications
            userAppDir = os.path.join(str(Path.home()), ".local", "share", "applications")
            userAppDirShortcut = os.path.join(userAppDir, "UniqueBibleApp.desktop")
            if not os.path.exists(userAppDirShortcut):
                Path(userAppDir).mkdir(parents=True, exist_ok=True)
                copyfile(ubaLinuxDesktopFile, userAppDirShortcut)
            # ~/Desktop
            homeDir = os.environ["HOME"]
            desktopPath = f"{homeDir}/Desktop"
            desktopPathShortcut = os.path.join(desktopPath, "UniqueBibleApp.desktop")
            if os.path.exists(desktopPath) and not os.path.exists(desktopPathShortcut):
                copyfile(ubaLinuxDesktopFile, desktopPathShortcut)
        except:
            pass

# Run main.py
if thisOS == "Windows":
    if python.endswith(".exe"):
        python = python[:-4]
    # Activate virtual environment
    activator = os.path.join(wd, venvDir, binDir, "activate")
    # Run main.py
    mainPy = "main.py {0}".format(initialCommand) if initialCommand else "main.py"
    if enableCli:
        if os.path.exists(activator):
            os.system("{0} & {1} {2}".format(activator, python, mainPy))
        else:
            os.system("{0} {1}".format(python, mainPy))
    else:
        if os.path.exists(activator):
            subprocess.Popen("{0} & {1} {2}".format(activator, python, mainPy), shell=True)
        else:
            subprocess.Popen("{0} {1}".format(python, mainPy), shell=True)
else:
    # Activate virtual environment
    activator = os.path.join(wd, venvDir, binDir, "activate_this.py")
    if not os.path.exists(activator):
        copyfile("activate_this.py", activator)
    with open(activator) as f:
        code = compile(f.read(), activator, 'exec')
        exec(code, dict(__file__=activator))
    # Run main.py
    if enableCli:
        os.system("{0} {1}{2}".format(python, mainFile, f" {initialCommand}" if initialCommand else ""))
    else:
        subprocess.Popen([python, mainFile, initialCommand] if initialCommand else [python, mainFile])
