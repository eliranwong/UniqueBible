from uniquebible import config
import subprocess, os, platform, sys, re, platform, shutil


config.pipIsUpdated = False
config.runMode = "terminal"
config.ubaIsRunning = False
config.noQt = True


def pip3InstallModule(module):
    #executablePath = os.path.dirname(sys.executable)
    #pippath = os.path.join(executablePath, "pip")
    #pip = pippath if os.path.isfile(pippath) else "pip"
    #pip3path = os.path.join(executablePath, "pip3")
    #pip3 = pip3path if os.path.isfile(pip3path) else "pip3"
    if not config.pipIsUpdated:
        try:
            # Automatic setup does not start on some device because pip tool is too old
            updatePip = subprocess.Popen("python -m pip install --upgrade pip" if platform.system() == "Windows" else "pip3 install --upgrade pip", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            *_, stderr = updatePip.communicate()
            if not stderr:
                print("pip tool updated!")
        except:
            pass
        config.pipIsUpdated = True
    print("Installing missing module '{0}' ...".format(module))
    # implement pip3 as a subprocess:
    #install = subprocess.Popen(['pip3', 'install', module], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    install = subprocess.Popen(f"pip3 install {module}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    *_, stderr = install.communicate()
    return stderr

# required
def isConfigInstalled():
    try:
        from uniquebible import config
        return True
    except:
        return False

# required
def isPrompt_toolkitInstalled():
    try:
        from prompt_toolkit import PromptSession
        return True
    except:
        return False

# optional
def isHtml5libInstalled():
    try:
        import html5lib
        return True
    except:
        return False

# optional
def isBeautifulsoup4Installed():
    try:
        from bs4 import BeautifulSoup
        return True
    except:
        return False

# optional
def isTranslateInstalled():
    try:
        from translate import Translator
        return True
    except:
        return False

# optional
def isTextractInstalled():
    try:
        import textract
        return True
    except:
        return False

# optional
def isHtmlTextInstalled():
    try:
        import html_text
        return True
    except:
        return False

# optional
def isGTTSInstalled():
    try:
        from gtts import gTTS
        return True
    except:
        return False

# optional
def isColoramaInstalled():
    try:
        from colorama import init
        from colorama import Fore, Back, Style
        return True
    except:
        return False

# optional
def isPyperclipInstalled():
    try:
        import pyperclip
        return True
    except:
        return False

# optional
def isPygmentsInstalled():
    try:
        from pygments.lexers.python import PythonLexer
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

def runTerminalMode():
    print("'{0}' is not installed!\nTo run UBA with graphical interface, install 'PySide6', 'PySide2' or 'PyQt5' first!".format(feature))
    if config.enableCli:
        print("attempting to run UBA in terminal mode ...")
        os.system("{0} {1} terminal".format(sys.executable, "uba.py"))
        exit(0)
    else:
        exit(1)

def updateModules(module, isInstalled):
    if isInstalled:
        if not module in config.enabled:
            config.enabled.append(module)
        if module in config.disabled:
            config.disabled.remove(module)
    else:
        if not module in config.disabled:
            config.disabled.append(module)
        if module in config.enabled:
            config.enabled.remove(module)

# Specify qtLibrary for particular os
if (config.runMode == "docker") and config.usePySide2onWebtop:
    config.qtLibrary = "pyside2"
    os.environ["QT_API"] = config.qtLibrary
elif platform.system() == "Darwin" and config.usePySide6onMacOS:
    config.qtLibrary = "pyside6"
# Check if required modules are installed
required = [
    ("config", "Configurations", isConfigInstalled),
    ("prompt_toolkit", "Command Line Interaction", isPrompt_toolkitInstalled),
]

for module, feature, isInstalled in required or config.updateDependenciesOnStartup:
    if config.updateDependenciesOnStartup and not (module.startswith("-U ") or module.startswith("--upgrade ")):
            module = "--upgrade {0}".format(module)
    if not isInstalled():
        pip3InstallModule(module)
        if isInstalled():
            print("Installed!")
        else:
            print("Required feature '{0}' is not enabled.\nRun 'pip3 install {1}' to install it first!".format(feature, module))
            exit(1)

major, minor, micro, *_ = sys.version_info
thisOS = platform.system()
cpu = ""
if thisOS == "Darwin":
    thisOS = "macOS"
    *_, cpu = platform.mac_ver()
    cpu = f"_{cpu}"
venvDir = "venv_{0}{4}_{1}.{2}.{3}".format(thisOS, major, minor, micro, cpu)

disabledModules = []
disabledModulesFilePath = os.path.join(venvDir, "disabled_modules.txt")
if os.path.exists(disabledModulesFilePath):
    with open(disabledModulesFilePath) as disabledModulesFile:
        disabledModules = [line.strip() for line in disabledModulesFile.readlines()]
# Check if optional modules are installed
optional = [
    ("html-text", "Read html text", isHtmlTextInstalled),
    ("beautifulsoup4", "HTML / XML Parser", isBeautifulsoup4Installed),
    ("html5lib", "HTML Library", isHtml5libInstalled),
    ("colorama", "Producing colored terminal text", isColoramaInstalled),
    ("gTTS", "Google text-to-speech", isGTTSInstalled),
    ("pyperclip", "Cross-platform clipboard utilities", isPyperclipInstalled),
    ("Pygments", "Syntax highlighting package", isPygmentsInstalled),
    ("translate", "Google Translate", isTranslateInstalled),
    #("textract", "Extract text from document", isTextractInstalled),
]
for module, feature, isInstalled in optional:
    checkModule = re.sub("-|_", "", module)
    checkModule = re.sub("^(-U |--upgrade )", "", checkModule).capitalize()
    if not checkModule in config.enabled and not checkModule in config.disabled:
        if module in disabledModules:
            print(f"{module} has been manually disabled")
            available = False
        elif not isInstalled() or config.updateDependenciesOnStartup:
            if config.updateDependenciesOnStartup and not (module.startswith("-U ") or module.startswith("--upgrade ")):
                module = "--upgrade {0}".format(module)
            pip3InstallModule(module)
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
updateModules("OfflineTts", isOfflineTtsInstalled())
# Check if official Google Cloud text-to-speech service is in place
config.isGoogleCloudTTSAvailable = os.path.isfile(os.path.join(os.getcwd(), "credentials_GoogleCloudTextToSpeech.json"))
if config.isGoogleCloudTTSAvailable and config.ttsDefaultLangauge == "en":
    config.ttsDefaultLangauge = "en-GB"
elif not config.isGoogleCloudTTSAvailable and config.ttsDefaultLangauge == "en-GB":
    config.ttsDefaultLangauge = "en"
# Check if ONLINE tts is in place
updateModules("OnlineTts", True if ("Gtts" in config.enabled) or config.isGoogleCloudTTSAvailable else False)
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
macVlc = "/Applications/VLC.app/Contents/MacOS/VLC"
config.macVlc = macVlc if platform.system() == "Darwin" and os.path.isfile(macVlc) else ""

windowsVlc = r'C:\Program Files\VideoLAN\VLC\vlc.exe'
config.windowsVlc = windowsVlc if platform.system() == "Windows" and os.path.isfile(windowsVlc) else ""

