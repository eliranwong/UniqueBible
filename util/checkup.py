import config, subprocess, os, zipfile, platform, sys
from shutil import copyfile
from util.WebtopUtil import WebtopUtil


def downloadFileIfNotFound(databaseInfo):
    fileItems, cloudID, *_ = databaseInfo
    targetFile = os.path.join(*fileItems)
    if not os.path.isfile(targetFile):
        cloudFile = "https://drive.google.com/uc?id={0}".format(cloudID)
        localFile = "{0}.zip".format(targetFile)
        # Download from google drive
        import gdown
        try:
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

def pip3InstallModule(module):
    if not config.pipIsUpdated:
        try:
            # Automatic setup does not start on some device because pip tool is too old
            updatePip = subprocess.Popen("pip install --upgrade pip", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            *_, stderr = updatePip.communicate()
            if not stderr:
                print("pip tool updated!")
        except:
            pass
        config.pipIsUpdated = True
    print("Installing missing module '{0}' ...".format(module))
    # implement pip3 as a subprocess:
    #install = subprocess.Popen(['pip3', 'install', module], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    install = subprocess.Popen('pip3 install {0}'.format(module), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    *_, stderr = install.communicate()
    return stderr

def fixFcitxOnLinux(module):
    # Fixed fcitx for Linux users
    if platform.system() == "Linux" and not config.docker:
        #if config.docker:
        #    fcitxPlugin = "/usr/lib/qt/plugins/platforminputcontexts/libfcitx5platforminputcontextplugin.so"
        fcitxPlugin = "/usr/lib/x86_64-linux-gnu/qt5/plugins/platforminputcontexts/libfcitxplatforminputcontextplugin.so"
        ubaInputPluginDir = os.path.join(os.getcwd(), "venv", "lib/python{0}.{1}/site-packages/{2}/Qt/plugins/platforminputcontexts".format(sys.version_info.major, sys.version_info.minor, module))
        ubaFcitxPlugin = os.path.join(ubaInputPluginDir, "libfcitxplatforminputcontextplugin.so")
        #print(os.path.exists(fcitxPlugin), os.path.exists(ubaInputPluginDir), os.path.exists(ubaFcitxPlugin))
        if os.path.exists(fcitxPlugin) and os.path.exists(ubaInputPluginDir) and not os.path.exists(ubaFcitxPlugin):
            try:
                copyfile(fcitxPlugin, ubaFcitxPlugin)
                os.chmod(ubaFcitxPlugin, 0o755)
                print("'fcitx' input plugin is installed. This will take effect the next time you relaunch Unique Bible App!")
            except:
                pass

def isConfigInstalled():
    try:
        import config
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

def isIbmWatsonInstalled():
    try:
        from ibm_watson import LanguageTranslatorV3
        from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
        return True
    except:
        return False

def isHtmlTextInstalled():
    try:
        import html_text
        return True
    except:
        return False

def isTtsInstalled():
    if platform.system() == "Linux" and config.espeak:
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

# Set config values for optional features
def setInstallConfig(module, isInstalled):
    #if module == "PyPDF2":
    #    config.isPyPDF2Installed = isInstalled
    if module == "mammoth":
        config.isMammothInstalled = isInstalled
    elif module == "htmldocx":
        config.isHtmldocxInstalled = isInstalled
    elif module == "python-docx":
        config.isPythonDocxInstalled = isInstalled
    elif module == "diff_match_patch":
        config.isDiffMatchPatchInstalled = isInstalled
    elif module == "langdetect":
        config.isLangdetectInstalled = isInstalled
    elif module == "pygithub":
        config.isPygithubInstalled = isInstalled
    elif module == "qt-material":
        config.isQtMaterialInstalled = isInstalled
    elif module == "telnetlib3":
        config.isTelnetlib3Installed = isInstalled
    elif module == "ibm-watson":
        config.isIbmWatsonInstalled = isInstalled
    elif module == "html-text":
        config.isHtmlTextInstalled = isInstalled
    elif module == "beautifulsoup4":
        config.isBeautifulsoup4Installed = isInstalled
    elif module == "html5lib":
        config.isHtml5libInstalled = isInstalled
    elif module == "qrcode":
        config.isQrCodeInstalled = isInstalled
    elif module == "pillow":
        config.isPillowInstalled = isInstalled
    #elif module == "git+git://github.com/ojii/pymaging.git#egg=pymaging git+git://github.com/ojii/pymaging-png.git#egg=pymaging-png":
        #config.isPurePythonPngInstalled = isInstalled
    elif module == "python-vlc":
        config.isVlcInstalled = isInstalled
    elif module == "yt-dlp":
        config.isYoutubeDownloaderInstalled = isInstalled
    elif module == "gTTS":
        config.isGTTSInstalled = isInstalled

# Check if required modules are installed
required = (
    ("config", "Configurations", isConfigInstalled),
    ("gdown", "Download UBA modules from Google drive", isGdownInstalled),
    ("babel", "Internationalization and localization library", isBabelInstalled),
    ("requests", "Download / Update files", isRequestsInstalled),
) if config.noQt else (
    ("config", "Configurations", isConfigInstalled),
    ("PySide2", "Qt Graphical Interface Library", isPySide2Installed) if config.qtLibrary == "pyside2" else ("PyQt5", "Qt Graphical Interface Library", isPyQt5Installed),
    ("qtpy", "Qt Graphical Interface Layer", isQtpyInstalled),
    ("gdown", "Download UBA modules from Google drive", isGdownInstalled),
    ("babel", "Internationalization and localization library", isBabelInstalled),
    ("requests", "Download / Update files", isRequestsInstalled),
)
for module, feature, isInstalled in required:
    if not isInstalled():
        pip3InstallModule(module)
        if module == "PySide2" and not isInstalled():
            module = "PyQt5"
            isInstalled = isPyQt5Installed
            if not isInstalled():
                print("PySide2 is not found!  Trying to install 'PyQt5' instead ...")
                if config.docker:
                    WebtopUtil.installPackage("python-pyqt5 python-pyqt5-sip python-pyqt5-webengine")
                else:
                    pip3InstallModule(module)
                    pip3InstallModule("PyQtWebEngine")
                if isInstalled():
                    config.qtLibrary == "pyqt5"
                    os.environ["QT_API"] = config.qtLibrary
                    print("Installed!")
                else:
                    print("Required feature '{0}' is not enabled.\nInstall either 'PySide2' or 'PyQt5' first!".format(feature, module))
                    exit(1)
            else:
                config.qtLibrary == "pyqt5"
                os.environ["QT_API"] = config.qtLibrary
        elif module == "PyQt5" and not isInstalled():
            module = "PySide2"
            isInstalled = isPySide2Installed
            if not isInstalled():
                print("PyQt5 is not found!  Trying to install 'PySide2' instead ...")
                if config.docker:
                    WebtopUtil.installPackage("pyside2 pyside2-tools qt5-webengine")
                else:
                    pip3InstallModule(module)
                if isInstalled():
                    config.qtLibrary == "pyside2"
                    os.environ["QT_API"] = config.qtLibrary
                    print("Installed!")
                else:
                    print("Required feature '{0}' is not enabled.\nInstall either 'PySide2' or 'PyQt5' first!".format(feature, module))
                    exit(1)
            else:
                config.qtLibrary == "pyside2"
                os.environ["QT_API"] = config.qtLibrary
        if isInstalled():
            print("Installed!")
        else:
            print("Required feature '{0}' is not enabled.\nRun 'pip3 install {1}' to install it first!".format(feature, module))
            exit(1)

# Check if optional modules are installed
optional = (
    ("beautifulsoup4", "HTML / XML Parser", isBeautifulsoup4Installed),
    ("html5lib", "HTML Library", isHtml5libInstalled),
    ("mammoth", "Open DOCX file", isMammothInstalled),
    ("diff_match_patch", "Highlight Differences", isDiffMatchPatchInstalled),
    ("langdetect", "Detect Language", isLangdetectInstalled),
    ("pygithub", "Github access", isPygithubInstalled),
    ("telnetlib3", "Telnet Client and Server library", isTelnetlib3Installed),
    ("ibm-watson", "IBM-Watson Language Translator", isIbmWatsonInstalled),
    ("qrcode", "QR Code", isQrCodeInstalled),
    ("pillow", "QR Code", isPillowInstalled),
    #("git+git://github.com/ojii/pymaging.git#egg=pymaging git+git://github.com/ojii/pymaging-png.git#egg=pymaging-png", "Pure Python PNG", isPurePythonPngInstalled),
    ("python-vlc", "VLC Player", isVlcInstalled),
    ("yt-dlp", "YouTube Downloader", isYoutubeDownloaderInstalled),
    ("gTTS", "Google text-to-speech", isGTTSInstalled)
) if config.noQt else (
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
    ("qrcode", "QR Code", isQrCodeInstalled),
    ("pillow", "QR Code", isPillowInstalled),
    #("git+git://github.com/ojii/pymaging.git#egg=pymaging git+git://github.com/ojii/pymaging-png.git#egg=pymaging-png", "Pure Python PNG", isPurePythonPngInstalled),
    ("python-vlc", "VLC Player", isVlcInstalled),
    ("yt-dlp", "YouTube Downloader", isYoutubeDownloaderInstalled)
)
for module, feature, isInstalled in optional:
    if not isInstalled():
        pip3InstallModule(module)
        available = isInstalled()
        print("Installed!" if available else "Optional feature '{0}' is not enabled.\nRun 'pip3 install {1}' to install it first.".format(feature, module))
    else:
        available = True
    setInstallConfig(module, available)

# Check if other optional features are installed
# [Optional] Text-to-Speech feature
if config.docker:
    config.isTtsInstalled = False
else:
    config.isTtsInstalled = isTtsInstalled()
if not config.isTtsInstalled and not config.gTTS and not config.isGoogleCloudTTSAvailable:
    print("Text-to-speech feature is not enabled or supported on your device.")

# Import modules for developer
if config.developer:
    # import exlbl
    pass

# Download initial content for fresh installation
files = (
    # Core bible functionality
    ((config.marvelData, "images.sqlite"), "1-aFEfnSiZSIjEPUQ2VIM75I4YRGIcy5-"),
    ((config.marvelData, "commentaries", "cCBSC.commentary"), "1IxbscuAMZg6gQIjzMlVkLtJNDQ7IzTh6"),
)
for file in files:
    downloadFileIfNotFound(file)
