#!/usr/bin/env python3

import os, sys, subprocess, platform
from shutil import copyfile

thisFile = os.path.realpath(__file__)
wd = thisFile[:-6]
if os.getcwd() != wd:
    os.chdir(wd)

# Required minimum python version: 3.7
if sys.version_info < (3, 7):
    print("UniqueBible.app runs only with Python 3.7 or later")
    exit(1)

# Set environment variable
os.environ["QT_LOGGING_RULES"] = "*=false"

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

def pip3IsInstalled():
    isInstalled, _ = subprocess.Popen("pip3 -V", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    return isInstalled

# A method to install 
def pip3InstallModule(module):
    if not pip3IsInstalled():
        subprocess.Popen([sys.executable, "-m", "pip", "install", "--user", "--upgrade pip"])
    # run pip3IsInstalled again to check if pip3 is installed successfully for users in case they didn't have it.
    if pip3IsInstalled():
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
        import venv
        venv.create(env_dir=venvDir, with_pip=True)

# Run main.py
if platform.system() == "Windows":
    if python.endswith(".exe"):
        python = python[:-4]
    # Create a .bat for application shortcut
    shortcutSh = os.path.join(os.getcwd(), "UniqueBibleApp.bat")
    with open(shortcutSh, "w") as fileObj:
            fileObj.write("{0} {1}".format(python, thisFile))
    # Activate virtual environment
    activator = os.path.join(os.getcwd(), venvDir, binDir, "activate")
    if os.path.exists(activator):
        subprocess.Popen("{0} & {1} main.py".format(activator, python), shell=True)
    else:
        subprocess.Popen("{0} main.py".format(python), shell=True)
else:
    # Create application shortcuts and set file permission
    shortcutSh = os.path.join(os.getcwd(), "UniqueBibleApp.sh")
    if not os.path.exists(shortcutSh):
        # Create .sh shortcut
        with open(shortcutSh, "w") as fileObj:
            fileObj.write("#!{0}\n{1}".format(sys.executable, thisFile))
        # Set permission
        for file in (thisFile, "main.py", "BibleVerseParser.py", "RegexSearch.py", shortcutSh):
            os.chmod(file, 0o755)
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
    try:
        # Automatic setup does not start on some device because pip tool is too old
        # will add control later and update pip tool once
        subprocess.Popen("pip install --upgrade pip", shell=True)
    except:
        pass
    # Fixed fcitx for Linux users
    if platform.system() == "Linux":
        fcitxPlugin = "/usr/lib/x86_64-linux-gnu/qt5/plugins/platforminputcontexts/libfcitxplatforminputcontextplugin.so"
        ubaInputPluginDir = os.path.join(os.getcwd(), venvDir, "lib/python{0}.{1}/site-packages/PySide2/Qt/plugins/platforminputcontexts".format(sys.version_info.major, sys.version_info.minor))
        ubaFcitxPlugin = os.path.join(ubaInputPluginDir, "libfcitxplatforminputcontextplugin.so")
        #print(os.path.exists(fcitxPlugin), os.path.exists(ubaInputPluginDir), os.path.exists(ubaFcitxPlugin))
        if os.path.exists(fcitxPlugin) and os.path.exists(ubaInputPluginDir) and not os.path.exists(ubaFcitxPlugin):
            try:
                copyfile(fcitxPlugin, ubaFcitxPlugin)
                os.chmod(ubaFcitxPlugin, 0o755)
                print("'fcitx' input plugin is installed. This will take effect the next time you relaunch Unique Bible App!")
            except:
                pass
    # Run main file
    subprocess.Popen([python, mainFile])
