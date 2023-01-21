#!/usr/bin/env python3

# Set up configurations
# create config.py if it do not exist
import os
from util.FileUtil import FileUtil
FileUtil.createCustomFiles()
# run initial values
import config
from util.ConfigUtil import ConfigUtil
ConfigUtil.setup()
config.qtLibrary = "pyside6"
config.noQt = False
config.cli = False
config.enableCli = False
config.docker = False
#config.fixLoadingContent = True
#config.fixLoadingContentDelayTime = 1
config.isChromeOS = False

import sys, subprocess, platform, shutil
from shutil import copyfile
from guiQt6.Styles import *

# Requires python 3.7+
if sys.version_info < (3, 7):
    print("Required python version [3.7 or above] is not found!")
    print("Closing ...")
    exit(1)

# set enviornment variables
env = (
    ("PYTHONUNBUFFERED", "1"),
    ("QT_API", "pyside6"),
    ("QT_LOGGING_RULES", "*=false"),
)
for key, value in env:
    os.environ[key] = value
# input environment variables
# Set Qt input method variable to use fcitx5 / fcitx / ibus
if config.fcitx5:
    os.environ["QT_IM_MODULE"] = "fcitx5"
elif config.fcitx:
    os.environ["QT_IM_MODULE"] = "fcitx"
elif config.ibus:
    os.environ["QT_IM_MODULE"] = "ibus"
# Set Qt input method variable to use Qt virtual keyboards if config.virtualKeyboard is "True"
if config.virtualKeyboard:
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

# set current directory
thisFile = os.path.realpath(__file__)
config.ubaDir = os.path.dirname(thisFile)
if os.getcwd() != config.ubaDir:
    os.chdir(config.ubaDir)

# Do NOT use sys.executable directly
python = os.path.basename(sys.executable)
mainFile = os.path.join(config.ubaDir, "mainQt6.py")
major, minor, micro, *_ = sys.version_info
config.thisOS = platform.system()
cpu = ""
if config.thisOS == "Darwin":
    *_, cpu = platform.mac_ver()
    cpu = f"_{cpu}"
config.venvDir = venvDir = "venv_{0}{4}_{1}.{2}.{3}".format("macOS" if config.thisOS == "Darwin" else config.thisOS, major, minor, micro, cpu)
binDir = "Scripts" if config.thisOS == "Windows" else "bin"

# Set up virtual environment directory
if sys.prefix == sys.base_prefix:
    # Check if virtual environment is available
    venvPython = os.path.join(config.ubaDir, venvDir, binDir, python)
    if not os.path.exists(venvPython):
        try:
            import venv
            print("Setting up virtual environment ...")
            venv.create(env_dir=venvDir, with_pip=True, system_site_packages=True) if os.path.isfile("use_system_site_packages") else venv.create(env_dir=venvDir, with_pip=True)
        except:
            pass

# copy essential data to virtual environment directory
nltk_data1 = os.path.join("nltk_data", "corpora", "omw-1.4.zip")
nltk_data1_destination_folder = os.path.join(venvDir, nltk_data1[:-4])
nltk_data2 = os.path.join("nltk_data", "corpora", "wordnet.zip")
nltk_data2_destination_folder = os.path.join(venvDir, nltk_data2[:-4])
corpora_folder = os.path.join(venvDir, "nltk_data", "corpora")
os.makedirs(corpora_folder, exist_ok=True)
if os.path.isfile(nltk_data1) and not os.path.isdir(nltk_data1_destination_folder):
    shutil.unpack_archive(nltk_data1, corpora_folder)
if os.path.isfile(nltk_data2) and not os.path.isdir(nltk_data2_destination_folder):
    shutil.unpack_archive(nltk_data2, corpora_folder)

# Create script shortcuts
# On Windows
if config.thisOS == "Windows":
    if python.endswith(".exe"):
        python = python[:-4]
    # Create a .bat for application shortcut
    shortcutBat = os.path.join(config.ubaDir, "UniqueBibleApp.bat")
    if not os.path.exists(shortcutBat):
        with open(shortcutBat, "w") as fileObj:
            #fileObj.write('{0} "{1}"'.format(python, thisFile))
            fileObj.write('{0} "{1}"'.format(sys.executable, thisFile))
# On non-Windows platforms
else:
    # Create application shortcuts and set file permission
    shortcutSh = os.path.join(config.ubaDir, "ubaQt6.sh")
    if not os.path.exists(shortcutSh):
        # Create .sh shortcut
        with open(shortcutSh, "w") as fileObj:
            fileObj.write("#!{0}\n{1} {2}".format(os.environ["SHELL"], sys.executable, thisFile))
        # Set permission
        for file in (thisFile, "mainQt6.py", "util/BibleVerseParser.py", "util/RegexSearch.py", shortcutSh):
            try:
                os.chmod(file, 0o755)
            except:
                pass

# Tweaks on Linux
if config.thisOS == "Linux":
    # Create Linux .desktop shortcut file if it does not exist
    shortcutDesktop = os.path.join(config.ubaDir, "UniqueBibleApp.desktop")
    if not os.path.exists(shortcutDesktop):
        iconPath = os.path.join(config.ubaDir, "htmlResources", "UniqueBibleApp.png")
        desktopFileContent =  """#!/usr/bin/env xdg-open

[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Path={0}
Exec={1} {2}
Icon={3}
Name=Unique Bible App
""".format(config.ubaDir, sys.executable, thisFile, iconPath)
        # Create file
        with open(shortcutDesktop, "w") as fileObj:
            fileObj.write(desktopFileContent)
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

    # support fcitx / fcitx5
    ubaInputPluginDir = os.path.join(os.getcwd(), venvDir, f"lib/python{major}.{minor}/site-packages/PySide6/Qt/plugins/platforminputcontexts")
    # plugin file 1
    fcitxPlugin = "/usr/lib/x86_64-linux-gnu/qt5/plugins/platforminputcontexts/libfcitxplatforminputcontextplugin.so"
    ubaFcitxPlugin = os.path.join(ubaInputPluginDir, "libfcitxplatforminputcontextplugin.so")
    #print(os.path.exists(fcitxPlugin), os.path.exists(ubaInputPluginDir), os.path.exists(ubaFcitxPlugin))
    if os.path.exists(fcitxPlugin) and os.path.exists(ubaInputPluginDir) and not os.path.exists(ubaFcitxPlugin):
        try:
            copyfile(fcitxPlugin, ubaFcitxPlugin)
            os.chmod(ubaFcitxPlugin, 0o755)
            print("'fcitx' input plugin is installed. This will take effect the next time you relaunch Unique Bible App!")
        except:
            pass
    # plugin file 2
    fcitxPlugin = "/usr/lib/x86_64-linux-gnu/qt5/plugins/platforminputcontexts/libfcitx5platforminputcontextplugin.so"
    ubaFcitxPlugin = os.path.join(ubaInputPluginDir, "libfcitx5platforminputcontextplugin.so")
    #print(os.path.exists(fcitxPlugin), os.path.exists(ubaInputPluginDir), os.path.exists(ubaFcitxPlugin))
    if os.path.exists(fcitxPlugin) and os.path.exists(ubaInputPluginDir) and not os.path.exists(ubaFcitxPlugin):
        try:
            copyfile(fcitxPlugin, ubaFcitxPlugin)
            os.chmod(ubaFcitxPlugin, 0o755)
            print("'fcitx5' input plugin is installed. This will take effect the next time you relaunch Unique Bible App!")
        except:
            pass

# Tweaks on Chrome OS
# For ChromeOS Linux (Debian 11) ONLY:
if config.thisOS == "Linux" and os.path.exists("/mnt/chromeos/"):
    config.isChromeOS = True
    # disable system tray
    config.enableSystemTrayOnLinux = False
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

# Options to override "QT_QPA_PLATFORM"
# use vnc for qpa platform
if os.path.isfile("use_vnc"):
    os.environ["QT_QPA_PLATFORM"] = "vnc"
# use waland for qpa platform
# https://wiki.archlinux.org/title/wayland
elif os.path.isfile("use_wayland"):
    os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"
# use xcb for qpa platform
elif os.path.isfile("use_xcb"):
    os.environ["QT_QPA_PLATFORM"] = "xcb"

"""
# Activate virtual environment
if config.thisOS == "Windows":
    # Activate virtual environment
    activator = os.path.join(config.ubaDir, venvDir, binDir, "activate")
    if os.path.isfile(activator):
        os.system(activator)
else:
    # Activate virtual environment
    activator = os.path.join(config.ubaDir, venvDir, binDir, "activate_this.py")
    if os.path.isdir(binDir) and not os.path.isfile(activator):
        copyfile("activate_this.py", activator)
    if os.path.isfile(activator):
        with open(activator) as f:
            code = compile(f.read(), activator, 'exec')
            exec(code, dict(__file__=activator))
"""

# Run checkup
from util.checkupQt6 import *

# Run GUI
from mainQt6 import *
