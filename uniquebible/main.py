# UniqueBible.app
# a cross-platform desktop bible application
# For more information on this application, visit https://BibleTools.app or https://UniqueBible.app.
import os, platform, sys, subprocess, shutil, ctypes
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.WebtopUtil import WebtopUtil

thisOS = platform.system()
if thisOS == "Windows":
    myappid = "uniquebible.app"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    icon_path = os.path.abspath(os.path.join(sys.path[0], "htmlResources", "UniqueBibleApp.ico"))
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(icon_path)

# Make sure config.py exists before importing config and all other scripts which depends on config
from uniquebible import config
# Setup config values
from uniquebible.util.ConfigUtil import ConfigUtil
ConfigUtil.setup()

# set enviornment variables
env = (
    ("PYTHONUNBUFFERED", "1"),
    ("QT_API", "pyside2"),
    ("QT_LOGGING_RULES", "*=false"),
)
for key, value in env:
    os.environ[key] = value

# check runmode and initial command
config.noQt = True if config.runMode in ("stream", "terminal", "ssh-server", "telnet-server", "http-server", "api-server", "api-client", "execute-macro") or os.path.isdir("/data/data/com.termux/files/home") else False
config.cli = True if config.runMode == "cli" else False
config.enableCli = True if config.runMode in ("cli", "gui", "docker") else False
config.enableApiServer = True if config.runMode == "api-server" else False
config.enableHttpServer = False

# Tweaks for ChromeOS Linux (Debian 11) ONLY:
if config.isChromeOS:
    # On ChromeOS, there are two major options of QT_QPA_PLATFORM: xcb and wayland
    # If QT_QPA_PLATFORM is set to wayland, UBA does not work with touchscreen and its main window closes and opens unexpectedly.
    os.environ["QT_QPA_PLATFORM"] = "xcb"
    # Trouble-shoot an issue: https://github.com/eliranwong/ChromeOSLinux/blob/main/troubleshooting/qt.qpa.plugin_cannot_load_xcb.md
    # The issue causes UBA unable to start up.
    libxcbUtil0 = "/usr/lib/x86_64-linux-gnu/libxcb-util.so.0"
    libxcbUtil1 = "/usr/lib/x86_64-linux-gnu/libxcb-util.so.1"
    if os.path.exists(libxcbUtil0) and not os.path.exists(libxcbUtil1):
        try:
            subprocess.Popen(f"sudo ln -s {libxcbUtil0} {libxcbUtil1}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

# Tweaks for docker version
if config.runMode == "docker":
    config.runMode = "gui"
    config.fcitx = True
    config.updateWithGitPull = True
    # Force to use PySide2 instead of PyQt5 for general users
    if not config.developer and config.qtLibrary != "pyside2":
        config.qtLibrary = "pyside2"
        os.environ["QT_API"] = config.qtLibrary
    # To deal with "ERROR:command_buffer_proxy_impl.cc(141)] ContextResult::kTransientFailure: Failed to send GpuChannelMsg_CreateCommandBuffer."
    # Reference: https://bugreports.qt.io/browse/QTBUG-82423
    os.environ["QTWEBENGINE_DISABLE_GPU_THREAD"] = "1"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-compositing --num-raster-threads=1 --enable-viewport --main-frame-resizes-are-orientation-changes --disable-composited-antialiasing"
    # Setup yay on first run; latest docker images has /opt/yay in place
    if os.path.isdir("/opt/yay") and not WebtopUtil.isPackageInstalled("yay"):
        print("Installing yay ...")
        os.system("sudo chown -R abc:users /opt/yay && cd /opt/yay && makepkg -si --noconfirm --needed && cd -")
    if WebtopUtil.isPackageInstalled("yay") and not WebtopUtil.isPackageInstalled("wps"):
        print("Installing fonts ...")
        os.system("yay -Syu --noconfirm --needed ttf-wps-fonts ttf-ms-fonts wps-office-fonts")
        print("Installing wps-office ...")
        os.system("yay -Syu --noconfirm --needed wps-office-cn")

# Check for dependencies and other essential elements
from uniquebible.util.checkup import *

# make sure nltk data are installed
if "Nltk" in config.enabled:
    # copy nltk data to virtual environment directory
    nltk_data1 = os.path.join("nltk_data", "corpora", "omw-1.4.zip")
    nltk_data1_destination_folder = os.path.join(config.venvDir, nltk_data1[:-4])
    nltk_data2 = os.path.join("nltk_data", "corpora", "wordnet.zip")
    nltk_data2_destination_folder = os.path.join(config.venvDir, nltk_data2[:-4])
    corpora_folder = os.path.join(config.venvDir, "nltk_data", "corpora")
    os.makedirs(corpora_folder, exist_ok=True)
    if os.path.isfile(nltk_data1) and not os.path.isdir(nltk_data1_destination_folder):
        shutil.unpack_archive(nltk_data1, corpora_folder)
    if os.path.isfile(nltk_data2) and not os.path.isdir(nltk_data2_destination_folder):
        shutil.unpack_archive(nltk_data2, corpora_folder)

# exit application if it is run for setup only
if config.runMode == "setup-only":
    print("UniqueBibleApp installed!")
    exit()

# Running non-gui modes
# ("terminal", "ssh-server", "telnet-server", "http-server", "api-server", "execute-macro")
if config.noQt:
    from uniquebible.startup.nonGui import *
    if config.runMode == "stream":
        run_stream_mode()
    elif config.runMode == "api-client":
        run_api_client_mode()
    elif config.runMode == "terminal":
        run_terminal_mode()
    elif config.runMode == "ssh-server":
        run_ssh_server(host=config.sshServerHost, port=config.sshServerPort, server_host_keys=config.sshServerHostKeys, passphrase=config.sshServerPassphrase)
    elif config.runMode == "telnet-server":
        startTelnetServer()
    elif config.runMode == "http-server":
        startHttpServer()
        ConfigUtil.save()
        if config.restartHttpServer:
            subprocess.Popen("{0} {1} http-server".format(sys.executable, config.httpServerUbaFile), shell=True)
        exit(0)
    elif config.runMode == "api-server":
        startApiServer()
        ConfigUtil.save()
        if config.restartApiServer:
            subprocess.Popen("{0} {1} api-server".format(sys.executable, config.httpServerUbaFile), shell=True)
        exit(0)
    elif config.runMode == "execute-macro":
        startMacro()
else:
    from uniquebible.startup.guiQt import *
