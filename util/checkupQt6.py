import config, subprocess, os, sys, re
from shutil import copyfile
from util.WebtopUtil import WebtopUtil
from install.module import *


def isConfigInstalled():
    try:
        import config
        return True
    except:
        return False

def isPySide6Installed():
    try:
        from PySide6.QtWidgets import QApplication, QStyleFactory
        return True
    except:
        return False

def isQtpyInstalled():
    try:
        from qtpy import QtGui
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

def isRequestsInstalled():
    try:
        import requests
        return True
    except:
        return False

def isMammothInstalled():
    try:
        import mammoth
        return True
    except:
        return False

def isHtmldocxInstalled():
    try:
        from htmldocx import HtmlToDocx
        return True
    except:
        return False

def isPythonDocxInstalled():
    try:
        from docx import Document
        return True
    except:
        return False

def isDiffMatchPatchInstalled():
    try:
        from diff_match_patch import diff_match_patch
        return True
    except:
        return False

def isLangdetectInstalled():
    try:
        from langdetect import detect, detect_langs, DetectorFactory
        return True
    except:
        return False

def isPygithubInstalled():
    try:
        from github import Github, InputFileContent
        if len(config.githubAccessToken) > 0:
            return True
        else:
            return False
        #return True
    except:
        return False

def isQtMaterialInstalled():
    try:
        from qt_material import apply_stylesheet
        return True
    except:
        return False

def isTelnetlib3Installed():
    try:
        import telnetlib3
        return True
    except:
        return False

def isHtml5libInstalled():
    try:
        import html5lib
        return True
    except:
        return False

def isBeautifulsoup4Installed():
    try:
        from bs4 import BeautifulSoup
        return True
    except:
        return False

def isIbmWatsonInstalled():
    try:
        from ibm_watson import LanguageTranslatorV3
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        return True
    except:
        return False

def isNumpyInstalled():
    try:
        import numpy
        return True
    except:
        return False

def isMatplotlibInstalled():
    try:
        import matplotlib.pyplot
        return True
    except:
        return False

def isTranslateInstalled():
    try:
        from translate import Translator
        return True
    except:
        return False

def isTextractInstalled():
    try:
        import textract
        return True
    except:
        return False

def isHtmlTextInstalled():
    try:
        import html_text
        return True
    except:
        return False

# Check if OFFLINE text-to-speech feature is in place.
def isOfflineTtsInstalled():

    # Check macOS built-in text-to-speech voices
    config.macVoices = {}
    if config.thisOS == "Darwin":
        macVoices = {}
        # reference about say command:
        # https://maithegeek.medium.com/having-fun-in-macos-with-say-command-d4a0d3319668
        os.system('say -v "?" > macOS_voices.txt')
        with open('macOS_voices.txt', 'r') as textFile:
            voices = textFile.read()
        voices = re.sub(" [ ]+?([^ ])", r" \1", voices)
        voices = re.sub(" [ ]*?#.*?$", "", voices, flags=re.M)
        voices = re.sub(" ([A-Za-z_]+?)$", r"＊\1", voices, flags=re.M)
        voices = voices.split("\n")
        for voice in voices:
            if "＊" in voice:
                voice, language = voice.split("＊")
                label = "[{0}] {1}".format(language, voice)
                macVoices[label] = ("", label)
        for key in sorted(macVoices):
            if not key.endswith("(Enhanced)") and not key.endswith("(Premium)"):
                config.macVoices[key] = macVoices[key]
        return True if config.macVoices else False
    elif config.thisOS == "Linux" and config.espeak:
        espeakInstalled, _ = subprocess.Popen("which espeak", shell=True, stdout=subprocess.PIPE).communicate()
        if not espeakInstalled:
            config.espeak = False
            print("'espeak' is not found.  To set up 'espeak', you may read https://github.com/eliranwong/ChromeOSLinux/blob/main/multimedia/espeak.md")
            return False
        else:
            return True
    else:
        try:
            # Note: qtpy.QtTextToSpeech is not found!
            from PySide2.QtTextToSpeech import QTextToSpeech
            return True
        except:
            try:
                from PyQt5.QtTextToSpeech import QTextToSpeech
                return True
            except:
                return False

def isQrCodeInstalled():
    try:
        import qrcode
        return True
    except:
        return False

def isPillowInstalled():
    try:
        import qrcode
        from PIL import Image
        return True
    except:
        return False

def isPurePythonPngInstalled():
    try:
        import qrcode
        from qrcode.image.pure import PymagingImage
        return True
    except:
        return False

def isVlcInstalled():
    try:
        import vlc
        return True
    except:
        return False

def isYoutubeDownloaderInstalled():
    try:
        import yt_dlp
        return True
    except:
        return False

def isGTTSInstalled():
    try:
        from gtts import gTTS
        return True
    except:
        return False

def isMarkdownifyInstalled():
    try:
        from markdownify import markdownify
        return True
    except:
        return False

def isTabulateInstalled():
    try:
        from tabulate import tabulate
        return True
    except:
        return False

def isMarkdownInstalled():
    try:
        import markdown
        return True
    except:
        return False

def isNltkInstalled():
    # Use wordnet https://www.educative.io/edpresso/how-to-use-wordnet-in-python
    config.wordnet = None
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    try:
        from nltk import download
        from nltk.corpus import wordnet
        try:
            wordnet.lemmas("english")
            config.wordnet = wordnet
        except:
            download('wordnet')
            download('omw-1.4')
            config.wordnet = wordnet
        return True
    except:
        return False

def isWordformsInstalled():
    import ssl
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    try:
        # the following line causes the following error on macOS with the codes about ssl above:
        # [nltk_data] Error loading wordnet: <urlopen error [SSL:
        from word_forms.word_forms import get_word_forms
        config.get_word_forms = get_word_forms
        return True
    except:
        return False

def isPaddleocrInstalled():
    try:
        from paddleocr import PaddleOCR,draw_ocr
        return True
    except:
        return False

def isApswInstalled():
    try:
        import apsw
        return True
    except:
        return False

def isPyluachInstalled():
    try:
        from pyluach import dates, hebrewcal, parshios
        return True
    except:
        return False

def isChineseEnglishLookupInstalled():
    try:
        from chinese_english_lookup import Dictionary
        config.cedict = Dictionary()
        return True
    except:
        return False

def isLemmagen3Installed():
    # Note: It looks like that lemmagen3 is a better lemmatizer than using "word_forms.lemmatize" installed with word_forms package
    try:
        from lemmagen3 import Lemmatizer
        config.lemmatizer = Lemmatizer("en")
        return True
    except:
        return False

def isAudioConverterInstalled():
    return True if WebtopUtil.isPackageInstalled("audioconvert") else False

def isPydnsblInstalled():
    try:
        import pydnsbl
        return True
    except:
        return False

def isColoramaInstalled():
    try:
        from colorama import init
        from colorama import Fore, Back, Style
        return True
    except:
        return False

def isArtInstalled():
    try:
        from art import text2art
        return True
    except:
        return False

def isPrompt_toolkitInstalled():
    try:
        from prompt_toolkit import PromptSession
        return True
    except:
        return False

def isPyperclipInstalled():
    try:
        import pyperclip
        return True
    except:
        return False

def isBcryptInstalled():
    try:
        import bcrypt
        return True
    except:
        return False

def isAsyncsshInstalled():
    try:
        import asyncssh
        return True
    except:
        return False

def isPygmentsInstalled():
    try:
        from pygments.lexers.python import PythonLexer
        return True
    except:
        return False

def isPickleyInstalled():
    return True if WebtopUtil.isPackageInstalled("pickley") else False

def isGmplotInstalled():
    try:
        import gmplot
        return True
    except:
        return False

def isHaversineInstalled():
    try:
        from haversine import haversine
        return True
    except:
        return False

def runTerminalMode():
    print("'{0}' is not installed!\nTo run UBA with graphical interface, install 'PySide6', 'PySide2' or 'PyQt5' first!".format(feature))
    if config.enableCli:
        print("attempting to run UBA in terminal mode ...")
        os.system("{0} {1} terminal".format(sys.executable, "uba.py"))
        exit(0)
    else:
        exit(1)

# Set config values for optional features
def setInstallConfig(module, isInstalled):
    #if module == "PyPDF2":
    #    config.isPyPDF2Installed = isInstalled
    if module in ("mammoth", "-U mammoth", "--upgrade mammoth"):
        config.isMammothInstalled = isInstalled
    elif module in ("htmldocx", "-U htmldocx", "--upgrade htmldocx"):
        config.isHtmldocxInstalled = isInstalled
    elif module in ("python-docx", "-U python-docx", "--upgrade python-docx"):
        config.isPythonDocxInstalled = isInstalled
    elif module in ("diff_match_patch", "-U diff_match_patch", "--upgrade diff_match_patch"):
        config.isDiffMatchPatchInstalled = isInstalled
    elif module in ("langdetect", "-U langdetect", "--upgrade langdetect"):
        config.isLangdetectInstalled = isInstalled
    elif module in ("pygithub", "-U pygithub", "--upgrade pygithub"):
        config.isPygithubInstalled = isInstalled
    elif module in ("qt-material", "-U qt-material", "--upgrade qt-material"):
        config.isQtMaterialInstalled = isInstalled
    elif module in ("telnetlib3", "-U telnetlib3", "--upgrade telnetlib3"):
        config.isTelnetlib3Installed = isInstalled
    elif module in ("ibm-watson", "-U ibm-watson", "--upgrade ibm-watson"):
        config.isIbmWatsonInstalled = isInstalled
    elif module in ("numpy", "-U numpy", "--upgrade numpy"):
        config.isNumpyInstalled = isInstalled
    elif module in ("matplotlib", "-U matplotlib", "--upgrade matplotlib"):
        config.isMatplotlibInstalled = isInstalled
    elif module in ("translate", "-U translate", "--upgrade translate"):
        config.isTranslateInstalled = isInstalled
    elif module in ("html-text", "-U html-text", "--upgrade html-text"):
        config.isHtmlTextInstalled = isInstalled
    elif module in ("beautifulsoup4", "-U beautifulsoup4", "--upgrade beautifulsoup4"):
        config.isBeautifulsoup4Installed = isInstalled
    elif module in ("html5lib", "-U html5lib", "--upgrade html5lib"):
        config.isHtml5libInstalled = isInstalled
    elif module in ("qrcode", "-U qrcode", "--upgrade qrcode"):
        config.isQrCodeInstalled = isInstalled
    elif module in ("pillow", "-U pillow", "--upgrade pillow"):
        config.isPillowInstalled = isInstalled
    #elif module in ("git+git://github.com/ojii/pymaging.git#egg=pymaging git+git://github.com/ojii/pymaging-png.git#egg=pymaging-png", "-U git+git://github.com/ojii/pymaging.git#egg=pymaging git+git://github.com/ojii/pymaging-png.git#egg=pymaging-png", "--upgrade git+git://github.com/ojii/pymaging.git#egg=pymaging git+git://github.com/ojii/pymaging-png.git#egg=pymaging-png"):
        #config.isPurePythonPngInstalled = isInstalled
    elif module in ("python-vlc", "-U python-vlc", "--upgrade python-vlc"):
        config.isVlcInstalled = isInstalled
    elif module in ("yt-dlp", "-U yt-dlp", "--upgrade yt-dlp"):
        config.isYoutubeDownloaderInstalled = isInstalled
    elif module in ("gTTS", "-U gTTS", "--upgrade gTTS"):
        config.isGTTSInstalled = isInstalled
    elif module in ("markdownify", "-U markdownify", "--upgrade markdownify"):
        config.isMarkdownifyInstalled = isInstalled
    elif module in ("markdown", "-U markdown", "--upgrade markdown"):
        config.isMarkdownInstalled = isInstalled
    elif module in ("AudioConverter", "-U AudioConverter", "--upgrade AudioConverter"):
        config.isAudioConverterInstalled = isInstalled
    elif module in ("lemmagen3", "-U lemmagen3", "--upgrade lemmagen3"):
        config.isLemmagen3Installed = isInstalled
    elif module in ("word-forms", "-U word-forms", "--upgrade word-forms"):
        config.isWordformsInstalled = isInstalled
    elif module in ("chinese-english-lookup", "-U chinese-english-lookup", "--upgrade chinese-english-lookup"):
        config.isChineseEnglishLookupInstalled = isInstalled
    elif module in ("paddleocr", "-U paddleocr", "--upgrade paddleocr"):
        config.isPaddleocrInstalled = isInstalled
    elif module in ("nltk", "-U nltk", "--upgrade nltk"):
        config.isNltkInstalled = isInstalled
    elif module in ("textract", "-U textract", "--upgrade textract"):
        config.isTextractInstalled = isInstalled
    elif module in ("tabulate", "-U tabulate", "--upgrade tabulate"):
        config.isTabulateInstalled = isInstalled
    elif module in ("apsw", "-U apsw", "--upgrade apsw"):
        config.isApswInstalled = isInstalled
    elif module in ("pyluach", "-U pyluach", "--upgrade pyluach"):
        config.isPyluachInstalled = isInstalled
    elif module in ("pydnsbl", "-U pydnsbl", "--upgrade pydnsbl"):
        config.isPydnsblInstalled = isInstalled
    elif module in ("gmplot", "-U gmplot", "--upgrade gmplot"):
        config.isGmplotInstalled = isInstalled
    elif module in ("haversine", "-U haversine", "--upgrade haversine"):
        config.isHaversineInstalled = isInstalled
    elif module in ("prompt_toolkit", "-U prompt_toolkit", "--upgrade prompt_toolkit"):
        config.isPrompt_toolkitInstalled = isInstalled
    elif module in ("colorama", "-U colorama", "--upgrade colorama"):
        config.isColoramaInstalled = isInstalled
    elif module in ("art", "-U art", "--upgrade art"):
        config.isArtInstalled = isInstalled
    elif module in ("pyperclip", "-U pyperclip", "--upgrade pyperclip"):
        config.isPyperclipInstalled = isInstalled
    elif module in ("pickley", "-U pickley", "--upgrade pickley"):
        config.isPickleyInstalled = isInstalled
    elif module in ("Pygments", "-U Pygments", "--upgrade Pygments"):
        config.isPygmentsInstalled = isInstalled
    elif module in ("asyncssh", "-U asyncssh", "--upgrade asyncssh"):
        config.isAsyncsshInstalled = isInstalled
    elif module in ("bcrypt", "-U bcrypt", "--upgrade bcrypt"):
        config.isBcryptInstalled = isInstalled


# Check if required modules are installed
required = [
    ("config", "Configurations", isConfigInstalled),
    ("PySide6", "Qt Graphical Interface Library", isPySide6Installed),
    ("qtpy", "Qt Graphical Interface Layer", isQtpyInstalled),
    ("gdown", "Download UBA modules from Google drive", isGdownInstalled),
    ("babel", "Internationalization and localization library", isBabelInstalled),
    ("requests", "Download / Update files", isRequestsInstalled),
    ("apsw", "Another Python SQLite Wrapper", isApswInstalled),
]

for module, feature, isInstalled in required or config.updateDependenciesOnStartup:
    if config.updateDependenciesOnStartup and not (module.startswith("-U ") or module.startswith("--upgrade ")):
            module = "--upgrade {0}".format(module)
    if not isInstalled():
        installmodule(module)

        if isInstalled():
            print("Installed!")
        else:
            print("Required feature '{0}' is not enabled.\nRun 'pip3 install {1}' to install it first!".format(feature, module))
            exit(1)


# Skip disabled optional modules
disabledModules = []
disabledModulesFilePath = os.path.join(config.venvDir, "disabled_modules.txt")
if os.path.exists(disabledModulesFilePath):
    with open(disabledModulesFilePath) as disabledModulesFile:
        disabledModules = [line.strip() for line in disabledModulesFile.readlines()]
# Check if optional modules are installed
optional = [
    ("html-text", "Read html text", isHtmlTextInstalled),
    ("beautifulsoup4", "HTML / XML Parser", isBeautifulsoup4Installed),
    ("html5lib", "HTML Library", isHtml5libInstalled),
    #("PyPDF2", "Open PDF file", isPyPDF2Installed),
    ("mammoth", "Open DOCX file", isMammothInstalled),
    ("htmldocx", "Convert HTML to DOCX", isHtmldocxInstalled),
    ("python-docx", "Handle DOCX file", isPythonDocxInstalled),
    ("diff_match_patch", "Highlight Differences", isDiffMatchPatchInstalled),
    ("langdetect", "Detect Language", isLangdetectInstalled),
    ("pygithub", "Github access", isPygithubInstalled),
    ("qt-material", "Qt Material Themes", isQtMaterialInstalled),
    ("telnetlib3", "Telnet Client and Server library", isTelnetlib3Installed),
    ("ibm-watson", "IBM-Watson Language Translator", isIbmWatsonInstalled),
    ("translate", "Google Translate", isTranslateInstalled),
    ("qrcode", "QR Code", isQrCodeInstalled),
    ("pillow", "QR Code", isPillowInstalled),
    #("git+git://github.com/ojii/pymaging.git#egg=pymaging git+git://github.com/ojii/pymaging-png.git#egg=pymaging-png", "Pure Python PNG", isPurePythonPngInstalled),
    ("python-vlc", "VLC Player", isVlcInstalled),
    ("yt-dlp", "YouTube Downloader", isYoutubeDownloaderInstalled),
    ("gTTS", "Google text-to-speech", isGTTSInstalled),
    ("markdownify", "Convert HTML to Markdown", isMarkdownifyInstalled),
    ("markdown", "Convert Markdown to HTML", isMarkdownInstalled),
    #("paddleocr", "Multilingual OCR", isPaddleocrInstalled),
    ("nltk", "Natural Language Toolkit (NLTK)", isNltkInstalled),
    ("word-forms", "Generate English Word Forms", isWordformsInstalled),
    ("lemmagen3", "Lemmatizer", isLemmagen3Installed),
    ("chinese-english-lookup", "Chinese-to-English word definition", isChineseEnglishLookupInstalled),
    ("textract", "Extract text from document", isTextractInstalled),
    ("tabulate", "Pretty-print tabular data", isTabulateInstalled),
    #("apsw", "Another Python SQLite Wrapper", isApswInstalled),
    ("pyluach", "Hebrew (Jewish) calendar dates", isPyluachInstalled),
    ("gmplot", "Mark locations on Google Maps", isGmplotInstalled),
    ("haversine", "Calculate the distance between two points", isHaversineInstalled),
    ("art", "ASCII Art Library For Python", isArtInstalled),
    ("colorama", "Producing colored terminal text", isColoramaInstalled),
    ("pyperclip", "Cross-platform clipboard utilities", isPyperclipInstalled),
    ("numpy", "Array Computing", isNumpyInstalled),
    ("matplotlib", "Plotting Package", isMatplotlibInstalled),
    ("pickley", "Automate installation of standalone python CLIs", isPickleyInstalled),
    ("Pygments", "Syntax highlighting package", isPygmentsInstalled),
    ("asyncssh", "Asynchronous SSHv2 client and server library", isAsyncsshInstalled),
    ("bcrypt", "Modern password hashing for your software and your servers", isBcryptInstalled),
]
if config.thisOS == "Darwin":
    optional.append(("AudioConverter", "Convert Audio Files to MP3", isAudioConverterInstalled))
for module, feature, isInstalled in optional:
    if module in disabledModules:
        print(f"{module} has been manually disabled")
        available = False
    elif not isInstalled() or config.updateDependenciesOnStartup:
        if config.updateDependenciesOnStartup and not (module.startswith("-U ") or module.startswith("--upgrade ")):
            module = "--upgrade {0}".format(module)
        installmodule(module)
        available = isInstalled()
        print("Installed!" if available else "Optional feature '{0}' is not enabled.\nRun 'pip3 install {1}' to install it first.".format(feature, module))
    else:
        available = True
    setInstallConfig(module, available)

# Check if other optional features are installed
# [Optional] Text-to-Speech feature
# Check is OFFLINE tts is in place
config.isOfflineTtsInstalled = isOfflineTtsInstalled()
# Check if official Google Cloud text-to-speech service is in place
config.isGoogleCloudTTSAvailable = os.path.isfile(os.path.join(os.getcwd(), "credentials_GoogleCloudTextToSpeech.json"))
if config.isGoogleCloudTTSAvailable and config.ttsDefaultLangauge == "en":
    config.ttsDefaultLangauge = "en-GB"
elif not config.isGoogleCloudTTSAvailable and config.ttsDefaultLangauge == "en-GB":
    config.ttsDefaultLangauge = "en"
# Check if ONLINE tts is in place
config.isOnlineTtsInstalled = True if config.isGTTSInstalled or config.isGoogleCloudTTSAvailable else False
# Check if any tts is in place
if not config.isOfflineTtsInstalled and not config.isOnlineTtsInstalled:
    config.noTtsFound = True
    print("Text-to-speech feature is not enabled or supported on your device.")
else:
    config.noTtsFound = False
# Check TTS configs
if config.forceOnlineTts and not config.isOnlineTtsInstalled:
    config.forceOnlineTts = False
config.noTtsSpeedAdjustment = (config.isGTTSInstalled and not config.isGoogleCloudTTSAvailable and ((not config.isOfflineTtsInstalled) or (config.isOfflineTtsInstalled and config.forceOnlineTts)))
# Check if builtin media player is in place:
if config.forceUseBuiltinMediaPlayer and not config.isVlcInstalled:
    config.forceUseBuiltinMediaPlayer = False
# Check if 3rd-party VLC player is installed on macOS
macVlc = "/Applications/VLC.app/Contents/MacOS/VLC"
config.macVlc = macVlc if config.thisOS == "Darwin" and os.path.isfile(macVlc) else ""
# Check if 3rd-party VLC player is installed on Windows
windowsVlc = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
config.windowsVlc = windowsVlc if config.thisOS == "Windows" and os.path.isfile(windowsVlc) else ""

# Other tweaks
config.fixLoadingContent = True if config.thisOS == "Darwin" else False
config.enableSystemTray = True if config.enableSystemTrayOnLinux or not config.thisOS == "Linux" else False
