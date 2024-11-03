import os, requests, pkg_resources, re, socket
from shutil import copy, copytree
from pathlib import Path
from packaging import version
from uniquebible import config


# go to resource directory
thisFile = os.path.realpath(__file__)
config.packageDir = os.path.dirname(thisFile)

ubahome = os.path.expanduser(os.path.join("~", "UniqueBible"))

# restor previous backup
configFile = os.path.join(config.packageDir, "config.py")
backupFile = os.path.join(ubahome, "config.py")
if os.path.isfile(backupFile) and not hasattr(config, "mainText"):
    print(f"Configuration backup found: {backupFile}")
    try:
        print("Loading backup ...")
        with open(backupFile, "r", encoding="utf-8") as fileObj:
            configs = fileObj.read()
        # load backup configs
        configs = "from uniquebible import config\n" + re.sub("^([A-Za-z0-9])", r"config.\1", configs, flags=re.M)
        exec(configs, globals())
        # copy backup configs
        copy(backupFile, configFile)
        print("Previous configurations restored!")
    except:
        try:
            os.rename(backupFile, f"{backupFile}_failed")
        except:
            pass
        print("Failed to restore previous configurations!")

# set up folders for storing user content in ~/UniqueBible
if not os.path.isdir(ubahome):
    Path(ubahome).mkdir(parents=True, exist_ok=True)
for i in ("audio", "htmlResources", "import", "macros", "marvelData", "music", "notes", "temp", "terminal_history", "terminal_mode", "thirdParty", "video", "webstorage", "workspace"):
    sourceFolder = os.path.join(config.packageDir, i)
    targetFolder = os.path.join(ubahome, i)
    if not os.path.isdir(targetFolder):
        print(f"Setting up user directory '{i}' ...")
        copytree(sourceFolder, targetFolder, dirs_exist_ok=True)
    #copytree(i, os.path.join(ubahome, i), dirs_exist_ok=True)

# set up map images
import uniquebible.htmlResources.images.exlbl
import uniquebible.htmlResources.images.exlbl_large
import uniquebible.htmlResources.images.exlbl_largeHD_1
import uniquebible.htmlResources.images.exlbl_largeHD_2
import uniquebible.htmlResources.images.exlbl_largeHD_3

# Add folders below for all new folders created after version 0.1.17
# ...

# change directory to user directory
if os.getcwd() != ubahome:
    os.chdir(ubahome)

# user plugins; create folders for users to place their own plugins
# TODO: user plugins not working for now; will implement later
for i in ("chatGPT", "config", "context", "event", "language", "layout", "menu", "shutdown", "startup", "terminal", "text_editor"):
    Path(os.path.join(ubahome, "plugins", i)).mkdir(parents=True, exist_ok=True)


def getPackageInstalledVersion(package):
    try:
        installed_version = pkg_resources.get_distribution(package).version
        return version.parse(installed_version)
    except pkg_resources.DistributionNotFound:
        return None

def getPackageLatestVersion(package):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package}/json", timeout=10)
        latest_version = response.json()['info']['version']
        return version.parse(latest_version)
    except:
        return None

def isServerAlive(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)  # Timeout in case of server not responding
    try:
        sock.connect((ip, port))
        sock.close()
        return True
    except socket.error:
        return False

if isServerAlive("8.8.8.8", 53):

    thisPackage = "uniquebible"

    print(f"Checking '{thisPackage}' version ...")

    config.version = installed_version = getPackageInstalledVersion(thisPackage)
    if installed_version is None:
        print("Installed version information is not accessible!")
    else:
        print(f"Installed version: {installed_version}")
    latest_version = getPackageLatestVersion(thisPackage)
    if latest_version is None:
        print("Latest version information is not accessible at the moment!")
    elif installed_version is not None:
        print(f"Latest version: {latest_version}")
        if latest_version > installed_version:
            print("Run `pip install --upgrade uniquebible` to upgrade!")

    config.internetConnectivity = True
else:
    config.internetConnectivity = False
    config.version = "0.0.0"