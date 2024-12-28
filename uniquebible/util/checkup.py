from uniquebible import config, getSitePackagesLocation
import subprocess, os, zipfile, platform, sys, re, shutil
from shutil import copyfile
from uniquebible.util.WebtopUtil import WebtopUtil
from uniquebible.install.module import *


def downloadFileIfNotFound(databaseInfo):
    fileItems, cloudID, *_ = databaseInfo
    targetFile = os.path.join(*fileItems)
    if not os.path.isfile(targetFile):
        cloudFile = "https://drive.google.com/uc?id={0}".format(cloudID)
        localFile = "{0}.zip".format(targetFile)
        # Download from google drive
        import gdown
        try:
            if not config.gdownIsUpdated:
                installmodule("--upgrade gdown")
                config.gdownIsUpdated = True
            print("Downloading initial content '{0}' ...".format(fileItems[-1]))
            #print("from: {0}".format(cloudFile))
            #print("to: {0}".format(localFile))
            try:
                gdown.download(cloudFile, localFile, quiet=True)
                print("Downloaded!")
                connection = True
            except:
                cli = "gdown {0} -O {1}".format(cloudFile, localFile)
                os.system(cli)
                print("Downloaded!")
                connection = True
        except:
            print("Failed to download '{0}'!".format(fileItems[-1]))
            connection = False
        if connection and os.path.isfile(localFile) and localFile.endswith(".zip"):
            print("Unpacking ...")
            zipObject = zipfile.ZipFile(localFile, "r")
            path, *_ = os.path.split(localFile)
            zipObject.extractall(path)
            zipObject.close()
            os.remove(localFile)
            print("'{0}' is installed!".format(fileItems[-1]))
        else:
            print("Failed to download '{0}'!".format(fileItems[-1]))

def fixFcitxOnLinux(module):
    # Fixed fcitx for Linux users
    if platform.system() == "Linux" and not (config.runMode == "docker"):
        #major, minor, micro, *_ = sys.version_info
        #if (config.runMode == "docker"):
        #    fcitxPlugin = "/usr/lib/qt/plugins/platforminputcontexts/libfcitx5platforminputcontextplugin.so"
        ubaInputPluginDir = os.path.join(getSitePackagesLocation(), module, "Qt/plugins/platforminputcontexts")
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

def isConfigInstalled():
    try:
        from uniquebible import config
        return True
    except:
        return False

def isPySide6Installed():
    try:
        from PySide6.QtWidgets import QApplication, QStyleFactory
        fixFcitxOnLinux("PySide2")
        return True
    except:
        return False

def isPySide2Installed():
    try:
        from PySide2.QtWidgets import QApplication, QStyleFactory
        fixFcitxOnLinux("PySide2")
        return True
    except:
        return False

def isPyQt5Installed():
    try:
        from PyQt5 import QtGui
        fixFcitxOnLinux("PyQt5")
        return True
    except:
        return False

def isQtpyInstalled():
    try:
        if not config.qtLibrary == "pyside6":
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

#def isPyPDF2Installed():
#    try:
#        import PyPDF2
#        return True
#    except:
#        return False

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

def isMarkitdownInstalled():
    try:
        from markitdown import MarkItDown
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
    if platform.system() == "Darwin":
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
    elif platform.system() == "Linux":
        if not shutil.which("espeak") and config.espeak:
            config.espeak = False
        if not shutil.which("piper") and config.piper:
            config.piper = False
        return True if shutil.which("piper") or shutil.which("espeak") else False
    else:
        if config.qtLibrary == "pyside6":
            try:
                #QtTextToSpeech is currently not in PySide6 pip3 package
                #ModuleNotFoundError: No module named 'PySide6.QtTextToSpeech'
                from PySide6.QtTextToSpeech import QTextToSpeech
                return True
            except:
                return False
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

def isGoogleSearchPythonInstalled():
    try:
        import googlesearch
        return True
    except:
        return False

def isDuckduckgoSearchInstalled():
    try:
        from duckduckgo_search import ddg
        return True
    except:
        return False

def isGroqInstalled():
    try:
        from groq import Groq
        return True
    except:
        return False

def isMistralInstalled():
    try:
        from mistralai import Mistral
        return True
    except:
        return False


def isTiktokenInstalled():
    try:
        import tiktoken
        return True
    except:
        return False

def isGuidanceInstalled():
    try:
        import guidance
        return True
    except:
        return False

def isMarkdownInstalled():
    try:
        import markdown
        return True
    except:
        return False

def isOpenccInstalled():
    try:
        from opencc import OpenCC
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

def isValidatorsInstalled():
    try:
        import validators
        return True
    except:
        return False

def isOpenaiInstalled():
    try:
        import openai
        return True
    except:
        return False

def isLlamaIndexInstalled():
    try:
        from llama_index import GPTVectorStoreIndex
        return True
    except:
        return False

def isSpeechRecognitionInstalled():
    try:
        import speech_recognition
        return True
    except:
        return False

def isPocketSphinxInstalled():
    try:
        from pocketsphinx import LiveSpeech
        return True
    except:
        return False

def isPydubInstalled():
    try:
        from pydub import AudioSegment
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

# Specify qtLibrary for particular os
if (config.runMode == "docker") and config.usePySide2onWebtop:
    config.qtLibrary = "pyside2"
    os.environ["QT_API"] = config.qtLibrary
elif platform.system() == "Darwin" and config.usePySide6onMacOS:
    config.qtLibrary = "pyside6"
# Check if required modules are installed
required = [
    ("config", "Configurations", isConfigInstalled),
    ("gdown", "Download UBA modules from Google drive", isGdownInstalled),
    ("babel", "Internationalization and localization library", isBabelInstalled),
    ("requests", "Download / Update files", isRequestsInstalled),
    ("apsw", "Another Python SQLite Wrapper", isApswInstalled),
    ("prompt_toolkit", "Command Line Interaction", isPrompt_toolkitInstalled),
]
# Add Qt Library module
if not config.noQt:
    if config.qtLibrary == "pyside6":
        required.append(("PySide6", "Qt Graphical Interface Library", isPySide6Installed))
    else:
        if config.qtLibrary == "pyside2":
            required.append(("PySide2", "Qt Graphical Interface Library", isPySide2Installed))
        else:
            required.append(("PyQt5", "Qt Graphical Interface Library", isPyQt5Installed))
    required.append(("qtpy", "Qt Graphical Interface Layer", isQtpyInstalled))

if not config.enabled:
    for module, feature, isInstalled in required or config.updateDependenciesOnStartup:
        if config.updateDependenciesOnStartup and not (module.startswith("-U ") or module.startswith("--upgrade ")):
                module = "--upgrade {0}".format(module)
        if not isInstalled() or config.updateDependenciesOnStartup:
            installmodule(module)
            if module == "PySide6" and not isInstalled():
                module = "PySide2"
                isInstalled = isPySide2Installed
                print("PySide6 is not found!  Trying to install 'PySide2' instead ...")
                config.qtLibrary == "pyside2"
                os.environ["QT_API"] = config.qtLibrary
                installmodule(module)
                if isInstalled():
                    print("Installed!")
            if module == "PySide2" and not isInstalled():
                module = "PyQt5"
                isInstalled = isPyQt5Installed
                if not isInstalled():
                    print("PySide2 is not found!  Trying to install 'PyQt5' instead ...")
                    if (config.runMode == "docker"):
                        WebtopUtil.installPackage("python-pyqt5 python-pyqt5-sip python-pyqt5-webengine")
                    else:
                        installmodule(module)
                        installmodule("PyQtWebEngine")
                    if isInstalled():
                        config.qtLibrary == "pyqt5"
                        os.environ["QT_API"] = config.qtLibrary
                        print("Installed!")
                    else:
                        #print("Required feature '{0}' is not enabled.\nInstall either 'PySide2' or 'PyQt5' first!".format(feature, module))
                        #exit(1)
                        runTerminalMode()
                else:
                    config.qtLibrary == "pyqt5"
                    os.environ["QT_API"] = config.qtLibrary
            elif module == "PyQt5" and not isInstalled():
                module = "PySide2"
                isInstalled = isPySide2Installed
                if not isInstalled():
                    print("PyQt5 is not found!  Trying to install 'PySide2' instead ...")
                    if (config.runMode == "docker"):
                        WebtopUtil.installPackage("pyside2 pyside2-tools qt5-webengine")
                    else:
                        installmodule(module)
                    if isInstalled():
                        config.qtLibrary == "pyside2"
                        os.environ["QT_API"] = config.qtLibrary
                        print("Installed!")
                    else:
                        #print("Required feature '{0}' is not enabled.\nInstall either 'PySide2' or 'PyQt5' first!".format(feature, module))
                        #exit(1)
                        runTerminalMode()
                else:
                    config.qtLibrary == "pyside2"
                    os.environ["QT_API"] = config.qtLibrary
            if isInstalled():
                if module == "gdown":
                    config.gdownIsUpdated = True
                print("Installed!")
            else:
                if module == "PySide6":
                    runTerminalMode()
                else:
                    print("Required feature '{0}' is not enabled.\nRun 'pip3 install {1}' to install it first!".format(feature, module))
                    exit(1)

# Check if optional modules are installed
optional = [
    ("html-text", "Read html text", isHtmlTextInstalled),
    ("beautifulsoup4", "HTML / XML Parser", isBeautifulsoup4Installed),
    ("html5lib", "HTML Library", isHtml5libInstalled),
    ("mammoth", "Open DOCX file", isMammothInstalled),
    ("diff_match_patch", "Highlight Differences", isDiffMatchPatchInstalled),
    ("langdetect", "Detect Language", isLangdetectInstalled),
    ("pygithub", "Github access", isPygithubInstalled),
    ("telnetlib3", "Telnet Client and Server library", isTelnetlib3Installed),
    ("translate", "Google Translate", isTranslateInstalled),
    ("qrcode", "QR Code", isQrCodeInstalled),
    ("pillow", "QR Code", isPillowInstalled),
    #("git+git://github.com/ojii/pymaging.git#egg=pymaging git+git://github.com/ojii/pymaging-png.git#egg=pymaging-png", "Pure Python PNG", isPurePythonPngInstalled),
    #("python-vlc", "VLC Player", isVlcInstalled),
    ("yt-dlp", "YouTube Downloader", isYoutubeDownloaderInstalled),
    ("gTTS", "Google text-to-speech", isGTTSInstalled),
    ("markdownify", "Convert HTML to Markdown", isMarkdownifyInstalled),
    ("markdown", "Convert Markdown to HTML", isMarkdownInstalled),
    #("paddleocr", "Multilingual OCR", isPaddleocrInstalled),
    ("nltk", "Natural Language Toolkit (NLTK)", isNltkInstalled),
    ("word-forms", "Generate English Word Forms", isWordformsInstalled),
    ("lemmagen3", "Lemmatizer", isLemmagen3Installed),
    ("chinese-english-lookup", "Chinese-to-English word definition", isChineseEnglishLookupInstalled),
    ("markitdown", "Extract text from document", isMarkitdownInstalled),
    ("tabulate", "Pretty-print tabular data", isTabulateInstalled),
    #("apsw", "Another Python SQLite Wrapper", isApswInstalled),
    ("pyluach", "Hebrew (Jewish) calendar dates", isPyluachInstalled),
    ("pydnsbl", "Checks if ip is listed in anti-spam dns blacklists.", isPydnsblInstalled),
    ("gmplot", "Mark locations on Google Maps", isGmplotInstalled),
    ("haversine", "Calculate the distance between two points", isHaversineInstalled),
    ("art", "ASCII Art Library For Python", isArtInstalled),
    ("colorama", "Producing colored terminal text", isColoramaInstalled),
    ("pyperclip", "Cross-platform clipboard utilities", isPyperclipInstalled),
    ("numpy", "Array Computing", isNumpyInstalled),
    ("matplotlib", "Plotting Package", isMatplotlibInstalled),
    #("pickley", "Automate installation of standalone python CLIs", isPickleyInstalled),
    ("Pygments", "Syntax highlighting package", isPygmentsInstalled),
    ("asyncssh", "Asynchronous SSHv2 client and server library", isAsyncsshInstalled),
    ("bcrypt", "Modern password hashing for your software and your servers", isBcryptInstalled),
    ("validators", "Python Data Validation for Humans", isValidatorsInstalled),
    ("pydub", "Manipulate audio", isPydubInstalled),
    ("openai>=1.45.0", "Python client library for the OpenAI API", isOpenaiInstalled),
    #("llama-index", "Lama Index (GPT Index)", isLlamaIndexInstalled),
    ("SpeechRecognition", "Library for performing speech recognition", isSpeechRecognitionInstalled),
    ("pocketsphinx", "Python bindings for PocketSphinx", isPocketSphinxInstalled),
    #("duckduckgo-search", "DuckDuckGo.com search", isDuckduckgoSearchInstalled),
    ("googlesearch-python", "A Python library for scraping the Google search engine", isGoogleSearchPythonInstalled),
    ("guidance", "A guidance language for controlling large language models", isGuidanceInstalled),
    ("tiktoken", "tokeniser for use with OpenAI's models.", isTiktokenInstalled),
    ("groq", "The official Python library for the groq API", isGroqInstalled),
    ("mistralai", "Python Client SDK for the Mistral AI API", isMistralInstalled),
    ("opencc-python-reimplemented", "OpenCC made with Python", isOpenccInstalled),
] if config.noQt else [
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
    ("translate", "Google Translate", isTranslateInstalled),
    ("qrcode", "QR Code", isQrCodeInstalled),
    ("pillow", "QR Code", isPillowInstalled),
    #("git+git://github.com/ojii/pymaging.git#egg=pymaging git+git://github.com/ojii/pymaging-png.git#egg=pymaging-png", "Pure Python PNG", isPurePythonPngInstalled),
    #("python-vlc", "VLC Player", isVlcInstalled),
    ("yt-dlp", "YouTube Downloader", isYoutubeDownloaderInstalled),
    ("gTTS", "Google text-to-speech", isGTTSInstalled),
    ("markdownify", "Convert HTML to Markdown", isMarkdownifyInstalled),
    ("markdown", "Convert Markdown to HTML", isMarkdownInstalled),
    #("paddleocr", "Multilingual OCR", isPaddleocrInstalled),
    ("nltk", "Natural Language Toolkit (NLTK)", isNltkInstalled),
    ("word-forms", "Generate English Word Forms", isWordformsInstalled),
    ("lemmagen3", "Lemmatizer", isLemmagen3Installed),
    ("chinese-english-lookup", "Chinese-to-English word definition", isChineseEnglishLookupInstalled),
    ("markitdown", "Extract text from document", isMarkitdownInstalled),
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
    #("pickley", "Automate installation of standalone python CLIs", isPickleyInstalled),
    ("Pygments", "Syntax highlighting package", isPygmentsInstalled),
    ("asyncssh", "Asynchronous SSHv2 client and server library", isAsyncsshInstalled),
    ("bcrypt", "Modern password hashing for your software and your servers", isBcryptInstalled),
    ("validators", "Python Data Validation for Humans", isValidatorsInstalled),
    ("pydub", "Manipulate audio", isPydubInstalled),
    ("openai", "Python client library for the OpenAI API", isOpenaiInstalled),
    #("llama-index", "Lama Index (GPT Index)", isLlamaIndexInstalled),
    ("SpeechRecognition", "Library for performing speech recognition", isSpeechRecognitionInstalled),
    ("pocketsphinx", "Python bindings for PocketSphinx", isPocketSphinxInstalled),
    #("duckduckgo-search", "DuckDuckGo.com search", isDuckduckgoSearchInstalled),
    ("googlesearch-python", "A Python library for scraping the Google search engine", isGoogleSearchPythonInstalled),
    ("guidance", "A guidance language for controlling large language models", isGuidanceInstalled),
    ("tiktoken", "tokeniser for use with OpenAI's models", isTiktokenInstalled),
    ("groq", "The official Python library for the groq API", isGroqInstalled),
    ("mistralai", "Python Client SDK for the Mistral AI API", isMistralInstalled),
    ("opencc-python-reimplemented", "OpenCC made with Python", isOpenccInstalled),
]
if platform.system() == "Darwin":
    optional.append(("AudioConverter", "Convert Audio Files to MP3", isAudioConverterInstalled))
for module, feature, isInstalled in optional:
    checkModule = re.sub("-|_", "", module)
    checkModule = re.sub("^(-U |--upgrade )", "", checkModule).capitalize()
    if not checkModule in config.enabled and not checkModule in config.disabled:
        if not isInstalled() or config.updateDependenciesOnStartup:
            if config.updateDependenciesOnStartup and not (module.startswith("-U ") or module.startswith("--upgrade ")):
                module = "--upgrade {0}".format(module)
            installmodule(module)
            available = isInstalled()
            print("Installed!" if available else "Optional feature '{0}' is not enabled.\nRun 'pip3 install {1}' to install it first.".format(feature, module))
        else:
            available = True
        if available:
            config.enabled.append(checkModule)
        else:
            config.disabled.append(checkModule)

# Check if other optional features are installed
# [Optional] Text-to-Speech feature
# Check is OFFLINE tts is in place
if (config.runMode == "docker"):
    config.updateModules("OfflineTts", False)
    config.enableSystemTrayOnLinux = False
    config.macVoices = {}
else:
    config.updateModules("OfflineTts", isOfflineTtsInstalled())
# Check if official Google Cloud text-to-speech service is in place
config.isGoogleCloudTTSAvailable = os.path.isfile(os.path.join(os.getcwd(), "credentials_GoogleCloudTextToSpeech.json"))
if config.isGoogleCloudTTSAvailable and config.ttsDefaultLangauge == "en":
    config.ttsDefaultLangauge = "en-GB"
elif not config.isGoogleCloudTTSAvailable and config.ttsDefaultLangauge == "en-GB":
    config.ttsDefaultLangauge = "en"
# Check if ONLINE tts is in place
config.updateModules("OnlineTts", True if ("Gtts" in config.enabled) or config.isGoogleCloudTTSAvailable else False)
# Check if any tts is in place
if not ("OfflineTts" in config.enabled) and not ("OnlineTts" in config.enabled):
    config.noTtsFound = True
    print("Text-to-speech feature is not enabled or supported on your device.")
else:
    config.noTtsFound = False
# Check if TTS speed adjustment is supported
if config.forceOnlineTts and not ("OnlineTts" in config.enabled):
    config.forceOnlineTts = False
config.noTtsSpeedAdjustment = (("Gtts" in config.enabled) and not config.isGoogleCloudTTSAvailable and ((not ("isOfflineTts" in config.enabled)) or (("OfflineTts" in config.enabled) and config.forceOnlineTts)))
# Check if builtin media player is in place:
#if config.forceUseBuiltinMediaPlayer and not ("Pythonvlc" in config.enabled):
#    config.forceUseBuiltinMediaPlayer = False
# Check if 3rd-party VLC player is installed on macOS
# on macOS
macVlc = "/Applications/VLC.app/Contents/MacOS/VLC"
config.macVlc = macVlc if platform.system() == "Darwin" and os.path.isfile(macVlc) else ""
# on Windows
windowsVlc = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
config.windowsVlc = windowsVlc if platform.system() == "Windows" and os.path.isfile(windowsVlc) else ""
# set useThirdPartyVLCplayer to False if there is no VLC player installed
config.isVlcAvailable = False if not macVlc and not windowsVlc and (not platform.system() == "Windows" and not WebtopUtil.isPackageInstalled("vlc")) else True
if config.useThirdPartyVLCplayer and not config.isVlcAvailable:
    config.useThirdPartyVLCplayer = False
if config.terminalForceVlc and not config.isVlcAvailable:
            config.terminalForceVlc = False

# Check if system tray is enabled
config.enableSystemTray = True if config.enableSystemTrayOnLinux or not platform.system() == "Linux" else False

# Import modules for developer
if config.developer:
    # import exlbl
    pass

# turn OFF config.updateDependenciesOnStartup after update
if config.updateDependenciesOnStartup:
    config.updateDependenciesOnStartup = False

# Download initial content for fresh installation
if not hasattr(config, "gdownIsUpdated"):
    config.gdownIsUpdated = False
files = (
    # Core bible functionality
    ((config.marvelData, "images.sqlite"), "1-aFEfnSiZSIjEPUQ2VIM75I4YRGIcy5-"),
    ((config.marvelData, "commentaries", "cCBSC.commentary"), "1IxbscuAMZg6gQIjzMlVkLtJNDQ7IzTh6"),
)
for file in files:
    downloadFileIfNotFound(file)
