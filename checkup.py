import config, subprocess
from platform import system
from util.ConfigUtil import ConfigUtil

optional = ("PyPDF2", "python-docx", "diff_match_patch", "langdetect", "pygithub", "qt-material", "telnetlib3", "ibm-watson", "requests", "pypinyin")

def isPySide2Installed():
    try:
        from PySide2.QtWidgets import QWidget
        return True
    except:
        return False

def isTtsInstalled():
    if system() == "Linux" and config.espeak:
        espeakInstalled, _ = subprocess.Popen("which espeak", shell=True, stdout=subprocess.PIPE).communicate()
        if not espeakInstalled:
            config.espeak = False
            print("'espeak' is not found.  To set up 'espeak', you may read https://github.com/eliranwong/ChromeOSLinux/blob/main/multimedia/espeak.md")
            return False
        else:
            return True
    else:
        try:
            from PySide2.QtTextToSpeech import QTextToSpeech, QVoice
            return True
        except:
            return False

def isGdownInstalled():
    try:
        import gdown
        return True
    except:
        return False

# [ Required ] babel module
# Internationalization and localization library
# http://babel.pocoo.org/
def isBabelInstalled():
    try:
        from babel import Locale
        return True
    except:
        return False

def isInstalled():
    try:
        return True
    except:
        return False

required = (
    ("PySide2", "Graphical Interface", isPySide2Installed),
    ("gdown", "Download UBA modules from Google drive", isGdownInstalled),
    ("babel", "Internationalization and localization library", isBabelInstalled),
)
for module, feature, isInstalled in required:
    if not isInstalled:
        ConfigUtil.requiredFeatureNotEnabled(feature, module)

# Optional Features
# [Optional] Text-to-Speech feature
config.isTtsInstalled = isTtsInstalled()
if not config.isTtsInstalled:
    print("Text-to-speech feature is not enabled or supported on your device.")

# [Optional] Chinese feature - pypinyin
# It translates Chinese characters into pinyin.
# To enable functions working with "pypinyin", install python package "pypinyin" first, e.g. pip3 install pypinyin.
try:
    from pypinyin import pinyin
    config.pinyinSupport = True
except:
    config.pinyinSupport = False
    ConfigUtil.optionalFeatureNotEnabled("Translate Chinese words into pinyin", "pypinyin")

# [Optional] Gist-syncing notes
if config.enableGist:
    try:
        from github import Github, InputFileContent
    except:
        config.enableGist = False
        ConfigUtil.optionalFeatureNotEnabled("Gist-synching notes across devices", "pygithub")

# Import modules for developer
if config.developer:
    # import exlbl
    pass


