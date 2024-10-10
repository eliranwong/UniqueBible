import glob
import locale
import os
import platform
import sys
import time
from datetime import datetime
try:
    from os import path
except:
    pass
try:
    from os import uname
except:
    pass

def printValue(object, attribute):
    if hasattr(object, attribute):
        print("{0}.{1}={2}".format(object.__name__, attribute, getattr(object, attribute)))
    else:
        print("{0}.{1} is undefined".format(object.__name__, attribute))


print("==============================================================")
print("Debugging Information")
print("==============================================================")
try:
    print(datetime.now())
except:
    pass

print("")
print("# Platform")
try:
    print("Python={0}".format(sys.version.split('\n')))
    (sysname, nodename, release, version, machine) = uname()
    print("sysname={0}".format(sysname))
    print("release={0}".format(release))
    print("version={0}".format(version))
    print("machine={0}".format(machine))
except:
    print("Could not get uname")
try:
    print("platform={0}".format(platform.platform()))
    print("platform={0}".format(os.name))
    print("platform={0}".format(platform.release()))
except:
    print("Could not get platform")

print("")
print("# Locale")
try:
    print("timezone={0}".format(time.strftime('%Z%z')))
    print("defaultlocale={0}".format(locale.getdefaultlocale()))
    locale.setlocale(locale.LC_ALL, "")
    print("getlocale={0}".format(locale.getlocale(locale.LC_MESSAGES)[0]))
except:
    print("Could not get locale")

print("")
print("# Version")
if path.exists("UniqueBibleAppVersion.txt"):
    with open("UniqueBibleAppVersion.txt") as f:
        print("UBA Version: {}".format(f.read().strip()))
else:
    print("UniqueBibleAppVersion.txt does not exist")

print("")
print("# Config")
if path.exists("config.py"):
    try:
        from uniquebible import config
        printValue(config, "developer")
        printValue(config, "enableCmd")
        printValue(config, "theme")
        printValue(config, "userLanguage")
        printValue(config, "userLanguageInterface")
        printValue(config, "menuLayout")
        printValue(config, "theme")
        printValue(config, "menuShortcuts")
        printValue(config, "marvelData")
        printValue(config, "qtMaterial")
        printValue(config, "qtMaterialTheme")
        printValue(config, "useLiteVerseParsing")
        printValue(config, "startupMacro")
        printValue(config, "enableMacros")
        printValue(config, "useLiteVerseParsing")
        printValue(config, "disableModulesUpdateCheck")
    except Exception as e:
        print("Error: {0}".format(e))
else:
    print("config.py does not exist")

print("")
print("# Marvel data")
try:
    print("Bibles: {0}".format(len(glob.glob(config.marvelData+"/bibles/*.bible"))))
    print("Books: {0}".format(len(glob.glob(config.marvelData+"/books/*.book"))))
    print("Data: {0}".format(len(glob.glob(config.marvelData+"/data/*.data"))))
    print("Commentaries: {0}".format(len(glob.glob(config.marvelData+"/commentaries/*.commentary"))))
    print("Lexicons: {0}".format(len(glob.glob(config.marvelData+"/lexicons/*.lexicon"))))
except:
    print("Could not get marvel data")
