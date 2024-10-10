from uniquebible import config
import subprocess, os, platform, pydoc, re
from uniquebible.util.TextUtil import TextUtil
from uniquebible.util.Languages import Languages
from uniquebible.util.TtsLanguages import TtsLanguages
from uniquebible.util.GoogleCloudTTSVoices import GoogleCloudTTS
from uniquebible.util.get_path_prompt import GetPath
from uniquebible.util.HebrewTransliteration import HebrewTransliteration
from uniquebible.util.WebtopUtil import WebtopUtil
from uniquebible.util.PromptValidator import NumberValidator
from uniquebible.util.VlcUtil import VlcUtil
from uniquebible.install.module import *
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from prompt_toolkit.application import run_in_terminal
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import prompt
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
#from uniquebible.util.terminal_system_command_prompt import SystemCommandPrompt

if config.qtLibrary == "pyside6":
    try:
        #QtTextToSpeech is currently not in PySide6 pip3 package
        #ModuleNotFoundError: No module named 'PySide6.QtTextToSpeech'
        from PySide6.QtTextToSpeech import QTextToSpeech
    except:
        pass
else:
    try:
        # Note: qtpy.QtTextToSpeech is not found!
        from PySide2.QtTextToSpeech import QTextToSpeech
    except:
        try:
            from PyQt5.QtTextToSpeech import QTextToSpeech
        except:
            pass


# Created for running text editor without UBA
class TextEditorUtility:

    def __init__(self, working_directory=""):
        self.ttsLanguages = self.getTtsLanguages()
        self.ttsLanguageCodes = list(self.ttsLanguages.keys())
        self.setOsOpenCmd()
        self.initPromptElements()
        self.getPath = GetPath(
            cancel_entry=config.terminal_cancel_action,
            promptIndicatorColor=config.terminalPromptIndicatorColor2,
            promptEntryColor=config.terminalCommandEntryColor2,
            subHeadingColor=config.terminalHeadingTextColor,
            itemColor=config.terminalResourceLinkColor,
            workingDirectory=working_directory,
        )

    def simplePrompt(self, numberOnly=False, multiline=False, inputIndicator=""):
        if not inputIndicator:
            inputIndicator = self.inputIndicator
        if numberOnly:
            if multiline:
                self.printMultilineNote()
            userInput = prompt(inputIndicator, style=self.promptStyle, validator=NumberValidator(), multiline=multiline).strip()
        else:
            userInput = prompt(inputIndicator, style=self.promptStyle, multiline=multiline).strip()
        return userInput

    def printInvalidOptionEntered(self):
        message = "Invalid option entered!"
        print(message)
        return ""

    def printMultilineNote(self):
        print("[Attention! Multiline input is enabled. Press Escape+Enter when you finish text entry.]")

    def setOsOpenCmd(self):
        if config.terminalEnableTermuxAPI:
            config.open = "termux-share"
        elif platform.system() == "Linux":
            config.open = config.openLinux
        elif platform.system() == "Darwin":
            config.open = config.openMacos
        elif platform.system() == "Windows":
            config.open = config.openWindows

    def initPromptElements(self):
        self.divider = "--------------------"
        self.inputIndicator = ">>> "
        self.promptStyle = Style.from_dict({
            # User input (default text).
            "": config.terminalCommandEntryColor2,
            # Prompt.
            "indicator": config.terminalPromptIndicatorColor2,
        })
        self.inputIndicator = [
            ("class:indicator", self.inputIndicator),
        ]

        tts_language_history = os.path.join(os.getcwd(), "terminal_history", "tts_language")
        google_translate_from_language_history = os.path.join(os.getcwd(), "terminal_history", "google_translate_from_language")
        google_translate_to_language_history = os.path.join(os.getcwd(), "terminal_history", "google_translate_to_language")
        system_command_history = os.path.join(os.getcwd(), "terminal_history", "system_command")

        self.terminal_system_command_session = PromptSession(history=FileHistory(system_command_history))
        self.terminal_tts_language_session = PromptSession(history=FileHistory(tts_language_history))
        self.terminal_google_translate_from_language_session = PromptSession(history=FileHistory(google_translate_from_language_history))
        self.terminal_google_translate_to_language_session = PromptSession(history=FileHistory(google_translate_to_language_history))

    def getCliOutput(self, cli):
        try:
            process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = process.communicate()
            return stdout.decode("utf-8")
        except:
            return ""

    def getclipboardtext(self, confirmMessage=True):
        try:
            if config.terminalEnableTermuxAPI:
                clipboardText = self.getCliOutput("termux-clipboard-get")
            elif ("Pyperclip" in config.enabled):
                import pyperclip
                clipboardText = pyperclip.paste()
            if clipboardText:
                if confirmMessage:
                    print(self.divider)
                    print("Clipboard text:")
                    print(clipboardText)
                    print(self.divider)
                return clipboardText
            elif confirmMessage:
                print("No copied text is found!")
                return self.cancelAction()
            else:
                return ""
        except:
            return self.noClipboardUtility()

    def cancelAction(self):
        message = "Action cancelled!"
        print(self.divider)
        print(message)
        return ""

    def noClipboardUtility(self):
        print("Clipboard utility is not found!")
        return ""

    def crossPlatformGetTtsLanguages(self):
        if config.isGoogleCloudTTSAvailable:
            languages = {}
            for language, languageCode in GoogleCloudTTS.getLanguages().items():
                languages[languageCode] = ("", language)
        elif (not ("OfflineTts" in config.enabled) or config.forceOnlineTts) and ("Gtts" in config.enabled):
            languages = {}
            for language, languageCode in Languages.gTTSLanguageCodes.items():
                languages[languageCode] = ("", language)
        elif config.macVoices:
            languages = config.macVoices
        elif config.espeak:
            languages = TtsLanguages().isoLang2epeakLang
        else:
            languages = TtsLanguages().isoLang2qlocaleLang
        # Check default TTS language
        if not config.ttsDefaultLangauge in languages:
            for key in languages.keys():
                if key.startswith("en") or key.startswith("[en"):
                    config.ttsDefaultLangauge = key
                    break
        # return languages
        return languages

    # Set text-to-speech default language
    def getTtsLanguages(self):
        # Support Android Google TTS if available
        if config.terminalEnableTermuxAPI:
            config.isGoogleCloudTTSAvailable = True
        if config.isGoogleCloudTTSAvailable and config.ttsDefaultLangauge == "en":
            config.ttsDefaultLangauge = "en-GB"
        return self.crossPlatformGetTtsLanguages()

    def fineTuneGtts(self, text, language):
        text = re.sub("[\[\]\(\)'\"]", "", text)
        if not config.isGoogleCloudTTSAvailable:
            language = re.sub("\-.*?$", "", language)
        if language in ("iw", "he"):
            text = HebrewTransliteration().transliterateHebrew(text)
            language = "el-GR" if config.isGoogleCloudTTSAvailable else "el"
        elif language == "el" or language.startswith("el-"):
            text = TextUtil.removeVowelAccent(text)
        return (text, language)

    # gtts:::
    # run google text to speech feature
    # internet is required
    def googleTextToSpeech(self, command):
        # Stop current playing first if any:
        self.stopTtsAudio()

        # Language codes: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        if command.count(":::") != 0:
            language, text = self.splitCommand(command)
        else:
            language = "en-GB" if config.isGoogleCloudTTSAvailable else "en"
            text = command
        # fine-tune
        text, language = self.fineTuneGtts(text, language)

        try:
            if config.runMode == "terminal" and config.terminalEnableTermuxAPI:
                # Option 1
                config.mainWindow.createAudioPlayingFile()
                text = re.sub("(\. |。)", r"\1＊", text)
                for i in text.split("＊"):
                    if not os.path.isfile(config.audio_playing_file):
                        break
                    print(i)
                    pydoc.pipepager(i, cmd=f"termux-tts-speak -l {language} -r {config.terminalTermuxttsSpeed}")
                config.mainWindow.removeAudioPlayingFile()
                # Output file shared by option 2 and option 3
                #outputFile = os.path.join("terminal_history", "gtts")
                #with open(outputFile, "w", encoding="utf-8") as f:
                #    f.write(text)
                #command = f"cat {outputFile} | termux-tts-speak -l {language} -r {config.terminalTermuxttsSpeed}"
                # Option 2
                #WebtopUtil.run(command)
                # Option 3
                #config.cliTtsProcess = subprocess.Popen([command], shell=True, preexec_fn=os.setpgrp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Define default tts language
                config.ttsDefaultLangauge = language
                return ("", "", {})
            else:
                if config.isGoogleCloudTTSAvailable:
                    self.saveCloudTTSAudio(text, language)
                else:
                    self.saveGTTSAudio(text, language)
                audioFile = self.getGttsFilename()
                if os.path.isfile(audioFile):
                    self.openMediaPlayer(audioFile, "main", gui=False)
        except:
            self.displayMessage(config.thisTranslation["message_fail"])

        return ("", "", {})

    def openMediaPlayer(self, command, source, gui=True):
        self.closeMediaPlayer()
        try:
            if config.mainWindow.audioPlayer is not None:
                config.mainWindow.addToAudioPlayList(command, True)
            elif config.isVlcAvailable:
                VlcUtil.playMediaFile(command, config.vlcSpeed, (gui and not (config.runMode == "terminal")))
            else:
                self.displayMessage(config.thisTranslation["noMediaPlayer"])
        except:
            WebtopUtil.openFile(command)
        return ("", "", {})

    # Temporary filepath for tts export
    def getGttsFilename(self):
        folder = os.path.join(config.musicFolder, "tmp")
        if not os.path.isdir(folder):
            os.makedirs(folder, exist_ok=True)
        return os.path.abspath(os.path.join(folder, "gtts.mp3"))

    # Python package gTTS, not created by Google
    def saveGTTSAudio(self, inputText, languageCode, filename=""):
        try:
            from gtts import gTTS
            moduleInstalled = True
        except:
            moduleInstalled = False
        if not moduleInstalled:
            installmodule("--upgrade gTTS")

        from gtts import gTTS
        tts = gTTS(inputText, lang=languageCode)
        if not filename:
            filename = os.path.abspath(self.getGttsFilename())
        if os.path.isfile(filename):
            os.remove(filename)
        tts.save(filename)

    # Official Google Cloud Text-to-speech Service
    def saveCloudTTSAudio(self, inputText, languageCode, filename=""):
        try:
            from google.cloud import texttospeech
            moduleInstalled = True
        except:
            moduleInstalled = False
        if not moduleInstalled:
            installmodule("--upgrade google-cloud-texttospeech")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), "credentials_GoogleCloudTextToSpeech.json")
        # Modified from ource: https://cloud.google.com/text-to-speech/docs/create-audio-text-client-libraries#client-libraries-install-python
        """Synthesizes speech from the input string of text or ssml.
        Make sure to be working in a virtual environment.

        Note: ssml must be well-formed according to:
            https://www.w3.org/TR/speech-synthesis/
        """
        from google.cloud import texttospeech
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=inputText)

        # Build the voice request, select the language code (e.g. "yue-HK") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            language_code=languageCode, ssml_gender=texttospeech.SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            # For more config, read https://cloud.google.com/text-to-speech/docs/reference/rest/v1/text/synthesize#audioconfig
            speaking_rate=config.gcttsSpeed,
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        # Save into mp3
        if not filename:
            filename = os.path.abspath(self.getGttsFilename())
        if os.path.isfile(filename):
            os.remove(filename)
        with open(filename, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            #print('Audio content written to file "{0}"'.format(outputFile))

    def googleTranslate(self, runOnSelectedText=True, defaultText=""):
        if ("Translate" in config.enabled):
            if runOnSelectedText:
                clipboardText = defaultText if defaultText else self.getclipboardtext()
            try:
                codes = []
                display = []
                for key, value in Languages.googleTranslateCodes.items():
                    display.append(f"[<ref>{value}</ref> ] {key}")
                    codes.append(value)
                display = "<br>".join(display)
                display = TextUtil.htmlToPlainText(f"<h2>Languages</h2>{display}")

                print(self.divider)
                print(display)
                print("Translate from:")
                print("(enter a language code)")
                suggestions = codes
                completer = FuzzyCompleter(WordCompleter(suggestions, ignore_case=True))
                userInput = self.terminal_google_translate_from_language_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput in suggestions:
                    fromLanguage = userInput

                    print(self.divider)
                    print(display)
                    print("Translate to:")
                    print("(enter a language code)")
                    suggestions = codes
                    completer = FuzzyCompleter(WordCompleter(suggestions, ignore_case=True))
                    userInput = self.terminal_google_translate_to_language_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer).strip()
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()

                    if userInput in suggestions:
                        toLanguage = userInput

                    if runOnSelectedText:
                        userInput = clipboardText
                    else:
                        print(self.divider)
                        print("Enter the text you want to translate:")
                        userInput = self.simplePrompt(multiline=True)

                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    # translate if all input are invalid
                    from translate import Translator
                    translator= Translator(from_lang=fromLanguage, to_lang=toLanguage)
                    return translator.translate(userInput)
                else:
                    return self.printInvalidOptionEntered()
            except:
                return self.printInvalidOptionEntered()
        else:
            print("Package 'translate' is not found on your system!")
            return ""

    def getDefaultTtsKeyword(self):
        if config.isGoogleCloudTTSAvailable:
            return "GTTS"
        elif (not ("OfflineTts" in config.enabled) or config.forceOnlineTts) and ("Gtts" in config.enabled):
            return "GTTS"
        elif config.macVoices:
            return "SPEAK"
        elif config.espeak:
            return "SPEAK"
        else:
            return "SPEAK"

    def showttslanguages(self):
        codes = self.ttsLanguageCodes

        display = "<h2>Languages</h2>"
        languages = []
        for code in codes:
            language = self.ttsLanguages[code][-1]
            languages.append(language)
            display += f"[<ref>{code}</ref> ] {language}<br>"
        display = display[:-4]
        self.html = display
        self.plainText = TextUtil.htmlToPlainText(display).strip()
        print(self.plainText)
        return ""

    def printChooseItem(self):
        print("Choose an item:")

    def tts(self, runOnSelectedText=True, defaultText=""):
        if runOnSelectedText:
            clipboardText = defaultText if defaultText else self.getclipboardtext()
        codes = self.ttsLanguageCodes
        #display = "<h2>Languages</h2>"
        shortCodes = []
        languages = []
        for code in codes:
            shortCodes.append(re.sub("\-.*?$", "", code))
            languages.append(self.ttsLanguages[code])
            #display += f"[<ref>{codes}</ref> ] {languages}<br>"
        #display = display[:-4]

        try:
            print(self.divider)
            print(self.showttslanguages())
            self.printChooseItem()
            print("Enter a language code:")
            suggestions = shortCodes + codes
            suggestions = list(set(suggestions))
            completer = FuzzyCompleter(WordCompleter(suggestions, ignore_case=True))
            default = config.ttsDefaultLangauge if config.ttsDefaultLangauge in suggestions else ""
            userInput = self.terminal_tts_language_session.prompt(self.inputIndicator, style=self.promptStyle, completer=completer, default=default).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in suggestions:
                config.ttsDefaultLangauge = userInput
                commandPrefix = f"{self.getDefaultTtsKeyword()}:::{userInput}:::"
                if runOnSelectedText:
                    userInput = clipboardText
                else:
                    print(self.divider)
                    print("Enter text to be read:")
                    userInput = self.simplePrompt(multiline=True)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()

                command = f"{commandPrefix}{userInput}"
                self.printRunningCommand(command)
                keyword, command = self.splitCommand(command)
                if keyword == "SPEAK":
                    return self.textToSpeech(command)
                else:
                    return self.googleTextToSpeech(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    # sort out keywords from a single line command
    def splitCommand(self, command):
        commandList = re.split('[ ]*?:::[ ]*?', command, 1)
        return commandList

    def closeMediaPlayer(self):
        self.stopTtsAudio()

    def stopTtsAudio(self):
        #if removeAudio_playing_file and os.path.isfile(config.audio_playing_file):
        #    os.remove(config.audio_playing_file)

        if WebtopUtil.isPackageInstalled("pkill"):

            # close Android media player
            try:
                if WebtopUtil.isPackageInstalled("termux-media-player"):
                    config.mainWindow.getCliOutput("termux-media-player stop")
            except:
                pass

            # close macOS text-to-speak voice
            if WebtopUtil.isPackageInstalled("say"):
                os.system("pkill say")
            # close vlc
            VlcUtil.closeVlcPlayer()
            # close espeak on Linux
            if WebtopUtil.isPackageInstalled("espeak"):
                os.system("pkill espeak")

    def displayMessage(self, message="", title="UniqueBible"):
        print(title)
        print(message)

    # speak:::
    # run text to speech feature
    def textToSpeech(self, command):
        # Stop current playing first if any:
        self.stopTtsAudio()

        # Language codes: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        language = config.ttsDefaultLangauge
        text = command
        if command.count(":::") != 0:
            language, text = self.splitCommand(command)

        if language.startswith("["):
            if language in config.macVoices:
                # save a text file first to avoid quotation marks in the text
                if language.startswith("[el_GR]"):
                    text = TextUtil.removeVowelAccent(text)
                with open('temp/temp.txt', 'w') as file:
                    file.write(text)
                voice = re.sub("^\[.*?\] ", "", language)
                # The following does not support "stop" feature
                #WebtopUtil.run(f"say -v {voice} -f temp/temp.txt")
                command = f"say -r {config.macOSttsSpeed} -v {voice} -f temp/temp.txt"
                self.cliTtsProcess = subprocess.Popen([command], shell=True, preexec_fn=os.setpgrp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                self.displayMessage(config.thisTranslation["message_noTtsVoice"])
        else:
            # espeak has no support of "ko", "ko" here is used to correct detection of traditional chinese
            # It is not recommended to use "ko" to correct language detection for "zh-tw", if qt built-in tts engine is used.
            # Different from espeak, Qt text-to-speech has a qlocale on Korean.
            # If the following two lines are uncommented, Korean text cannot be read.
            # In case the language is wrongly detected, users can still use command line to specify a correct language.
            if (config.espeak) and (language == "ko"):
                language = "zh-tw"
            if (language == "zh-cn") or (language == "zh-tw"):
                if config.ttsChineseAlwaysCantonese:
                    language = "zh-tw"
                elif config.ttsChineseAlwaysMandarin:
                    language = "zh-cn"
            elif (language == "en") or (language == "en-gb"):
                if config.ttsEnglishAlwaysUS:
                    language = "en"
                elif config.ttsEnglishAlwaysUK:
                    language = "en-gb"
            elif (language == "el"):
                # Modern Greek
                #language = "el"
                # Ancient Greek
                # To read accented Greek text, language have to be "grc" instead of "el" for espeak
                # In dictionary mapping language to qlocale, we use "grc" for Greek language too.
                language = "grc"
            elif (config.espeak) and (language == "he"):
                # espeak itself does not support Hebrew language
                # Below workaround on Hebrew text-to-speech feature for espeak
                # Please note this workaround is not a perfect solution, but something workable.
                text = HebrewTransliteration().transliterateHebrew(text)
                # Use "grc" to read, becuase it sounds closer to "he" than "en" does.
                language = "grc"

            if platform.system() == "Linux" and config.espeak:
                if WebtopUtil.isPackageInstalled("espeak"):
                    isoLang2epeakLang = TtsLanguages().isoLang2epeakLang
                    languages = isoLang2epeakLang.keys()
                    if not (config.ttsDefaultLangauge in languages):
                        config.ttsDefaultLangauge = "en"
                    if not (language in languages):
                        if config.runMode == "terminal":
                            print(f"'{language}' is not found!")
                            print("Available languages:", languages)
                        else:
                            self.displayMessage(config.thisTranslation["message_noTtsVoice"])
                        language = config.ttsDefaultLangauge
                        print(f"Language changed to '{language}'")
                    language = isoLang2epeakLang[language][0]
                    # subprocess is used
                    WebtopUtil.run("espeak -s {0} -v {1} '{2}'".format(config.espeakSpeed, language, text))
                else:
                    self.displayMessage(config.thisTranslation["message_noEspeak"])
            else:
                # use qt built-in tts engine
                engineNames = QTextToSpeech.availableEngines()
                if engineNames:
                    self.qtTtsEngine = QTextToSpeech(engineNames[0])
                    #locales = self.qtTtsEngine.availableLocales()
                    #print(locales)

                    isoLang2qlocaleLang = TtsLanguages().isoLang2qlocaleLang
                    languages = TtsLanguages().isoLang2qlocaleLang.keys()
                    if not (config.ttsDefaultLangauge in languages):
                        config.ttsDefaultLangauge = "en"
                    if not (language in languages):
                        self.displayMessage(config.thisTranslation["message_noTtsVoice"])
                        language = config.ttsDefaultLangauge
                    self.qtTtsEngine.setLocale(isoLang2qlocaleLang[language][0])

                    self.qtTtsEngine.setVolume(1.0)
                    engineVoices = self.qtTtsEngine.availableVoices()
                    if engineVoices:
                        self.qtTtsEngine.setVoice(engineVoices[0])

                        # Control speed here
                        self.qtTtsEngine.setRate(config.qttsSpeed)

                        self.qtTtsEngine.say(text)
                    else:
                        self.displayMessage(config.thisTranslation["message_noTtsVoice"])
        return ("", "", {})

    def printRunningCommand(self, command):
        self.command = command
        print(f"Running {command} ...")

    def execPythonFile(self, script):
        if config.developer:
            with open(script, 'r', encoding='utf8') as f:
                code = compile(f.read(), script, 'exec')
                exec(code, globals())
        else:
            try:
                with open(script, 'r', encoding='utf8') as f:
                    code = compile(f.read(), script, 'exec')
                    exec(code, globals())
            except:
                print("Failed to run '{0}'!".format(os.path.basename(script)))

    def copy(self, content="", confirmMessage=True):
        try:
            if not content:
                content = self.getPlainText()
            if config.terminalEnableTermuxAPI:
                pydoc.pipepager(content, cmd="termux-clipboard-set")
            else:
                import pyperclip
                pyperclip.copy(content)
            if confirmMessage:
                print("Content is copied to clipboard.")
            return ""
        except:
            return self.noClipboardUtility()

    def getSystemCommands(self):
        try:
            options = subprocess.Popen("bash -c 'compgen -ac | sort'", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = options.communicate()
            options = stdout.decode("utf-8").split("\n")
            options = [option for option in options if option and not option in ("{", "}", ".", "!", ":")]
            return options
        except:
            return []

    def system(self):
        self.runSystemCommandPrompt = True
        # initial message
        print("You are now using system command prompt!")
        print(f"To go back, either press 'ctrl+q' or run '{config.terminal_cancel_action}'.")
        # keep current path in case users change directory
        ubaPath = os.getcwd()
            
        this_key_bindings = KeyBindings()
        @this_key_bindings.add("c-q")
        def _(event):
            event.app.current_buffer.text = config.terminal_cancel_action
            event.app.current_buffer.validate_and_handle()
        @this_key_bindings.add("c-l")
        def _(_):
            print("")
            print(self.divider)
            run_in_terminal(lambda: self.getPath.displayDirectoryContent())

        userInput = ""
        systemCommands = self.getSystemCommands()
        while self.runSystemCommandPrompt and not userInput == config.terminal_cancel_action:
            try:
                indicator = "{0} {1} ".format(os.path.basename(os.getcwd()), "%")
                inputIndicator = [("class:indicator", indicator)]
                dirIndicator = "\\" if platform.system() == "Windows" else "/"
                completer = FuzzyCompleter(WordCompleter(sorted(set(systemCommands + [f"{i}{dirIndicator}" if os.path.isdir(i) else i for i in os.listdir()]))))
                auto_suggestion=AutoSuggestFromHistory()
                userInput = self.terminal_system_command_session.prompt(inputIndicator, style=self.promptStyle, key_bindings=this_key_bindings, auto_suggest=auto_suggestion, completer=completer).strip()
                if userInput and not userInput == config.terminal_cancel_action:
                    userInput = userInput.replace("~", os.path.expanduser("~"))
                    os.system(userInput)
                    # check if directory is changed
                    #userInput = re.sub("^.*?[ ;&]*(cd .+?)[;&]*$", r"\1", userInput)
                    cmdList = []
                    userInput = userInput.split(";")
                    for i in userInput:
                        subList = i.split("&")
                        cmdList += subList
                    cmdList = [i.strip() for i in cmdList if i and i.strip().startswith("cd ")]
                    if cmdList:
                        lastDir = cmdList[-1][3:]
                        if os.path.isdir(lastDir):
                            os.chdir(lastDir)
            except:
                pass
        os.chdir(ubaPath)
