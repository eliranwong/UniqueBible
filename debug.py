import locale
import platform
import sys
import time
from os import path, uname

def printValue(object, attribute):
    if hasattr(object, attribute):
        print("{0}.{1}={2}".format(object.__name__, attribute, getattr(object, attribute)))
    else:
        print("{0}.{1} is undefined".format(object.__name__, attribute))

print("==============================================================")
print("Debugging Information")
print("==============================================================")
print("# Platform")
print("Python={0}".format(sys.version.split('\n')))
(sysname, nodename, release, version, machine) = uname()
print("sysname={0}".format(sysname))
print("release={0}".format(release))
print("version={0}".format(version))
print("machine={0}".format(machine))
print("platform={0}".format(platform.platform()))

print("")
print("# Locale")
print("timezone={0}".format(time.strftime('%Z%z')))
print("defaultlocale={0}".format(locale.getdefaultlocale()))
locale.setlocale(locale.LC_ALL, "")
print("getlocale={0}".format(locale.getlocale(locale.LC_MESSAGES)[0]))

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
        import config
        printValue(config, "theme")
        printValue(config, "userLanguage")
        printValue(config, "userLanguageInterface")
        printValue(config, "menuLayout")
        printValue(config, "theme")
        printValue(config, "menuShortcuts")
        printValue(config, "marvelData")
        printValue(config, "qtMaterial")
        printValue(config, "qtMaterialTheme")
        printValue(config, "useFastVerseParsing")
        printValue(config, "menuShortcuts")
        printValue(config, "startupMacro")
        printValue(config, "enableMacros")
        printValue(config, "useFastVerseParsing")
        printValue(config, "disableModulesUpdateCheck")
        printValue(config, "translationLanguage")
    except Exception as e:
        print("Error: {0}".format(e))
else:
    print("config.py does not exist")
