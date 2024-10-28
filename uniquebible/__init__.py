import os, requests, pkg_resources, re
from shutil import copy, copytree
from pathlib import Path
from packaging import version
from uniquebible import config


# go to resource directory
thisFile = os.path.realpath(__file__)
config.packageDir = wd = os.path.dirname(thisFile)
if os.getcwd() != wd:
    os.chdir(wd)

ubahome = os.path.expanduser(os.path.join("~", "UniqueBible"))

# restor previous backup
configFile = os.path.join(wd, "config.py")
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

if not os.path.isdir(ubahome):
    Path(ubahome).mkdir(parents=True, exist_ok=True)
for i in ("audio", "htmlResources", "import", "macros", "marvelData", "music", "notes", "temp", "terminal_history", "terminal_mode", "thirdParty", "video", "webstorage", "workspace"):
    targetFolder = os.path.join(ubahome, i)
    if not os.path.isdir(targetFolder):
        copytree(i, targetFolder, dirs_exist_ok=True)
    #copytree(i, os.path.join(ubahome, i), dirs_exist_ok=True)

# images
import uniquebible.htmlResources.images.exlbl
import uniquebible.htmlResources.images.exlbl_large
import uniquebible.htmlResources.images.exlbl_largeHD_1
import uniquebible.htmlResources.images.exlbl_largeHD_2
import uniquebible.htmlResources.images.exlbl_largeHD_3

# Add folders below for all new folders created after version 0.1.17
# ...

# change directory
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