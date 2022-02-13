#!/usr/bin/env python3

import os, sys, subprocess, platform
from shutil import copyfile

thisFile = os.path.realpath(__file__)
wd = thisFile[:-6]
if os.getcwd() != wd:
    os.chdir(wd)

# Required minimum python version: 3.5
if sys.version_info < (3, 5):
    print("UniqueBible.app runs only with Python 3.5 or later")
    exit(1)
# Message for running python version lower than 3.7
if sys.version_info < (3, 7):
    print("You are running a python version lower than 3.7.  Some optional features may not be enabled.  UniqueBible.app requires python version 3.7+ to run all its features.")

# Take arguments
initialCommand = " ".join(sys.argv[1:]).strip()

# Set environment variable
os.environ["QT_API"] = "pyqt5" if initialCommand == "docker" else "pyside2"
os.environ["QT_LOGGING_RULES"] = "*=false"

if initialCommand == "-i":
    initialCommand = input("Enter command: ").strip()
enableCli = True if initialCommand in ("cli", "cli.py", "gui") \
    or len(sys.argv) > 1 and sys.argv[1] in ["telnet-server", "http-server", "execute-macro"] else False

# For ChromeOS Linux (Debian 10) ONLY:
if platform.system() == "Linux" and os.path.exists("/mnt/chromeos/"):
    # On ChromeOS, there are two major options of QT_QPA_PLATFORM: xcb and wayland
    # If QT_QPA_PLATFORM is set to wayland, UBA does not work with touchscreen and its main window closes and opens unexpectedly.
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    # Trouble-shoot an issue: https://github.com/eliranwong/ChromeOSLinux/blob/main/troubleshooting/qt.qpa.plugin_cannot_load_xcb.md
    # The issue causes UBA unable to start up.
    libxcbUtil0 = "/usr/lib/x86_64-linux-gnu/libxcb-util.so.0"
    libxcbUtil1 = "/usr/lib/x86_64-linux-gnu/libxcb-util.so.1"
    if os.path.exists(libxcbUtil0) and not os.path.exists(libxcbUtil1):
        try:
            subprocess.Popen("sudo ln -s /usr/lib/x86_64-linux-gnu/libxcb-util.so.0 /usr/lib/x86_64-linux-gnu/libxcb-util.so.1", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            pass

#python = "py" if platform.system() == "Windows" else "python3"
# Do NOT use sys.executable directly
python = os.path.basename(sys.executable)
mainFile = os.path.join(os.getcwd(), "main.py")
venvDir = "venv"
binDir = "Scripts" if platform.system() == "Windows" else "bin"

def desktopFileContent():
    iconPath = os.path.join(os.getcwd(), "htmlResources", "UniqueBibleApp.png")
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

# A method to install 
def pip3InstallModule(module):
    # update pip tool
    try:
        # Automatic setup does not start on some device because pip tool is too old
        updatePip = subprocess.Popen("pip install --upgrade pip", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        *_, stderr = updatePip.communicate()
        if not stderr:
            print("pip tool updated!")
    except:
        pass
    # Check if pip tool is available
    isInstalled, _ = subprocess.Popen("pip3 -V", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if isInstalled():
        print("Installing missing module '{0}' ...".format(module))
        # implement pip3 as a subprocess:
        install = subprocess.Popen(['pip3', 'install', module], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        *_, stderr = install.communicate()
        return stderr
    else:
        noPip3Message = "pip3 command is not found!"
        print(noPip3Message)
        return noPip3Message

# Check if virtual environment is being used
if sys.prefix == sys.base_prefix:
    # Check if virtual environment is available
    venvPython = os.path.join(os.getcwd(), venvDir, binDir, python)
    if not os.path.exists(venvPython):
        # Installing virtual environment
        # https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
        try:
            import venv
        except:
            pip3InstallModule("virtualenv")
        #subprocess.Popen([python, "-m", "venv", venvDir])
        print("Setting up environment ...")
        try:
            if not "venv" in sys.modules:
                import venv
            venv.create(env_dir=venvDir, with_pip=True)
        except:
            pass

# Run main.py
if platform.system() == "Windows":
    if python.endswith(".exe"):
        python = python[:-4]
    # Create a .bat for application shortcut
    shortcutSh = os.path.join(os.getcwd(), "UniqueBibleApp.bat")
    with open(shortcutSh, "w") as fileObj:
            fileObj.write('{0} "{1}"'.format(python, thisFile))
    # Activate virtual environment
    activator = os.path.join(os.getcwd(), venvDir, binDir, "activate")
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
    # Create application shortcuts and set file permission
    shortcutSh = os.path.join(os.getcwd(), "UniqueBibleApp.sh")
    if not os.path.exists(shortcutSh):
        # Create .sh shortcut
        with open(shortcutSh, "w") as fileObj:
            fileObj.write("#!{0}\n{1} {2}".format("/bin/bash" if initialCommand == "docker" else os.environ["SHELL"], sys.executable, thisFile))
        # Set permission
        for file in (thisFile, "main.py", "util/BibleVerseParser.py", "util/RegexSearch.py", shortcutSh):
            try:
                os.chmod(file, 0o755)
            except:
                pass
    shortcutDesktop = os.path.join(os.getcwd(), "UniqueBibleApp.desktop")
    if not os.path.exists(shortcutDesktop):
        # Create .desktop shortcut
        with open(shortcutDesktop, "w") as fileObj:
            fileObj.write(desktopFileContent())
        # Try to copy the newly created .desktop file to ~/.local/share/applications
        try:
            from pathlib import Path
            userAppDir = os.path.join(str(Path.home()), ".local", "share", "applications")
            # Create directory if it does not exists
            Path(userAppDir).mkdir(parents=True, exist_ok=True)
            # Copy .desktop file
            copyfile(shortcutDesktop, os.path.join(userAppDir, "UniqueBibleApp.desktop"))
        except:
            pass
    # Activate virtual environment
    activator = os.path.join(os.getcwd(), venvDir, binDir, "activate_this.py")
    if not os.path.exists(activator):
        copyfile("activate_this.py", activator)
    with open(activator) as f:
        code = compile(f.read(), activator, 'exec')
        exec(code, dict(__file__=activator))
    # Run main.py
    if enableCli or initialCommand == "docker":
        os.system("{0} {1} {2}".format(python, mainFile, initialCommand))
    else:
        subprocess.Popen([python, mainFile, initialCommand] if initialCommand else [python, mainFile])
