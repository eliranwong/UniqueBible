import config
from platform import system
from util.ConfigUtil import ConfigUtil

required = ("PySide2", "gdown", "babel")
optional = ("PyPDF2", "python-docx", "diff_match_patch", "langdetect", "pygithub", "qt-material", "telnetlib3", "ibm-watson", "requests", "pypinyin", "opencc")

# Optional Features
# [Optional] Text-to-Speech feature
config.ttsSupport = True
if system() == "Linux":
    if not config.showTtsOnLinux:
        config.ttsSupport = False
    elif config.espeak:
        import subprocess
        espeakInstalled, _ = subprocess.Popen("which espeak", shell=True, stdout=subprocess.PIPE).communicate()
        if not espeakInstalled:
            config.espeak = False
            config.ttsSupport = False
            print(
                "Package 'espeak' is not installed.  To install espeak, read https://github.com/eliranwong/ChromeOSLinux/blob/main/multimedia/espeak.md")
if config.ttsSupport and not config.espeak:
    try:
        from PySide2.QtTextToSpeech import QTextToSpeech, QVoice
    except:
        config.ttsSupport = False
if not config.ttsSupport:
    print("Text-to-speech feature is not enabled or supported on this operating system.")

# [Optional] Chinese feature - opencc
# It converts conversion between Traditional Chinese and Simplified Chinese.
# To enable functions working with "opencc", install python package "opencc" first, e.g. pip3 install OpenCC.
# try:
#    import opencc
#    openccSupport = True
# except:
#    openccSupport = False
#    ConfigUtil.optionalFeatureNotEnabled("Conversion between traditional Chinese and simplified Chinese", "opencc")

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

# [ Required ] babel module
# Internationalization and localization library
# http://babel.pocoo.org/
try:
    from babel import Locale
except:
    ConfigUtil.requiredFeatureNotEnabled("Internationalization and localization library", "babel")
