# flake8: noqa
import codecs
import logging
import os, pprint, platform, sys
from shutil import copy
from uniquebible import config
from uniquebible.util.DateUtil import DateUtil
from uniquebible.util.WebtopUtil import WebtopUtil
from uniquebible.lang import language_en_GB

class ConfigUtil:

    @staticmethod
    def swapTerminalColors():
        if config.terminalPromptIndicatorColor1 in config.terminalColors:
            config.terminalPromptIndicatorColor1 = config.terminalColors[config.terminalPromptIndicatorColor1]
        if config.terminalCommandEntryColor1 in config.terminalColors:
            config.terminalCommandEntryColor1 = config.terminalColors[config.terminalCommandEntryColor1]
        if config.terminalPromptIndicatorColor2 in config.terminalColors:
            config.terminalPromptIndicatorColor2 = config.terminalColors[config.terminalPromptIndicatorColor2]
        if config.terminalCommandEntryColor2 in config.terminalColors:
            config.terminalCommandEntryColor2 = config.terminalColors[config.terminalCommandEntryColor2]
        if config.terminalHeadingTextColor in config.terminalColors:
            config.terminalHeadingTextColor = config.terminalColors[config.terminalHeadingTextColor]
        if config.terminalVerseNumberColor in config.terminalColors:
            config.terminalVerseNumberColor = config.terminalColors[config.terminalVerseNumberColor]
        if config.terminalResourceLinkColor in config.terminalColors:
            config.terminalResourceLinkColor = config.terminalColors[config.terminalResourceLinkColor]
        if config.terminalVerseSelectionBackground in config.terminalColors:
            config.terminalVerseSelectionBackground = config.terminalColors[config.terminalVerseSelectionBackground]
        if config.terminalVerseSelectionForeground in config.terminalColors:
            config.terminalVerseSelectionForeground = config.terminalColors[config.terminalVerseSelectionForeground]
        if config.terminalSearchHighlightBackground in config.terminalColors:
            config.terminalSearchHighlightBackground = config.terminalColors[config.terminalSearchHighlightBackground]
        if config.terminalSearchHighlightForeground in config.terminalColors:
            config.terminalSearchHighlightForeground = config.terminalColors[config.terminalSearchHighlightForeground]
        if config.terminalFindHighlightBackground in config.terminalColors:
            config.terminalFindHighlightBackground = config.terminalColors[config.terminalFindHighlightBackground]
        if config.terminalFindHighlightForeground in config.terminalColors:
            config.terminalFindHighlightForeground = config.terminalColors[config.terminalFindHighlightForeground]
        #config.terminalSwapColors = (config.terminalResourceLinkColor.startswith("ansibright"))

    @staticmethod
    def setup(noQt=None, cli=None, enableCli=None, enableApiServer=None, enableHttpServer=None, runMode=None):
        if not hasattr(config, "packageDir"):
            config.packageDir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        if runMode is not None:
            config.runMode = runMode
        if noQt is not None:
            config.noQt = noQt
        if cli is not None:
            config.cli = cli
        if enableCli is not None:
            config.enableCli = enableCli
        if enableApiServer is not None:
            config.enableApiServer = enableApiServer
        if enableHttpServer is not None:
            config.enableHttpServer = enableHttpServer

        # check os
        config.thisOS = platform.system()
        config.isChromeOS = True if config.thisOS == "Linux" and os.path.exists("/mnt/chromeos/") else False

        # check current directory
        ubaUserDir = os.path.join(os.path.expanduser("~"), "UniqueBible")
        config.ubaUserDir = ubaUserDir if os.path.isdir(ubaUserDir) else os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        # check running mode
        config.runMode = sys.argv[1].lower() if len(sys.argv) > 1 else ""
        if config.runMode and not config.runMode in ("stream", "setup-only", "cli", "gui", "terminal", "docker", "telnet-server", "http-server", "execute-macro", "api-server", "api-client", "api-client-localhost"):
            config.runMode = ""

        # Temporary configurations
        # Their values are not saved on exit.
        config.rawOutput = True if config.runMode == "stream" else False
        config.chatMessages = []
        config.controlPanel = False
        config.miniControl = False
        config.tempRecord = ""
        config.contextItem = ""
        config.pluginContext = ""
        config.isDownloading = False
        config.noStudyBibleToolbar = False
        #config.noteOpened = False
        config.pipIsUpdated = False
        config.bibleWindowContentTransformers = []
        config.studyWindowContentTransformers = []
        config.shortcutList = []
        config.enableHttpServer = False
        config.enableApiServer = False
        #config.customBooksRangeSearch = ""
        config.mainCssBibleFontStyle = ""
        if not hasattr(config, "databaseConvertedOnStartup"):
            config.databaseConvertedOnStartup = True


        # Default settings for configurations:

        # A dictionary entry to hold information about individual attributes
        # It is created to help documentation.
        config.help = {}

        def setConfig(name, info, default):
            config.help[name] = info
            if not hasattr(config, name):
                # pprint default in case default is a string
                default = pprint.pformat(default)
                exec(f"""config.{name} = {default} """)

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

        '''def getCurrentVenvDir():
            major, minor, micro, *_ = sys.version_info
            cpu = ""
            if config.thisOS == "Darwin":
                *_, cpu = platform.mac_ver()
                cpu = f"_{cpu}"
            return "venv_{0}{4}_{1}.{2}.{3}".format("macOS" if config.thisOS == "Darwin" else config.thisOS, major, minor, micro, cpu)'''

        config.updateModules = updateModules
        setConfig("enabled", """
        # Enabled modules""",
        [])
        setConfig("disabled", """
        # Disabled modules""",
        ['Pygithub', 'Textract', 'Pydnsbl', 'Pocketsphinx'] if os.path.isdir("/data/data/com.termux/files/home") else [])
        setConfig("desktopUBAIcon", """
        # Desktop version UBA icon filename.  UniqueBible.app provides official icons in different colours.  We ask our users to use one of our official icons to acknowledge our development.""",
        os.path.join("htmlResources", "UniqueBibleApp.png"))
        setConfig("webUBAIcon", """
        # Web version UBA icon filename.  UniqueBible.app provides official icons in different colours.  We ask our users to use one of our official icons to acknowledge our development.""",
        "UniqueBibleApp.png")
        setConfig("developer", """
        # Option to enable developer menu and options""",
        False)
        setConfig("enableCmd", """
        # Option to enable command keyword cmd:::""",
        False)
        config.help["qtLibrary"] = """
        # Specify a Qt library module for GUI.  By default UBA uses PySide2."""
        if not hasattr(config, "qtLibrary"):
            try:
                config.qtLibrary = os.environ["QT_API"]
            except:
                config.qtLibrary = "pyside6"
                os.environ["QT_API"] = config.qtLibrary
        else:
            os.environ["QT_API"] = config.qtLibrary
        setConfig("usePySide2onWebtop", """
        # Use PySide2 as Qt Library, even config.qtLibrary is set to a value other than 'pyside2'.""",
        True)
        setConfig("usePySide6onMacOS", """
        # Use PySide6 as Qt Library, even config.qtLibrary is set to a value other than 'pyside6'.""",
        False)

        setConfig("checkVersionOnStartup", """
        # Check installed and latest versions on startup.""",
        True)

        # UBA Web API (work with GUI)
        setConfig("uniquebible_api_endpoint", """
        # UBA Web API server API endpoint""",
        "https://bible.gospelchurch.uk/html")
        setConfig("uniquebible_api_timeout", """
        # UBA Web API server API timeout""",
        10)
        setConfig("uniquebible_api_private", """
        # UBA Web API server API key to access private data""",
        "")

        # UBA Web API (work with API client mode on console)
        # Start of api-client mode setting
        setConfig("web_api_endpoint", """
        # UniqueBible App web API endpoint.""",
        "https://bible.gospelchurch.uk/plain")
        setConfig("web_api_timeout", """
        # UniqueBible App web API timeout.""",
        10)
        setConfig("web_api_private", """
        # UniqueBible App web API private key.""",
        "")

        # start of groq chat setting
        # config.llm_backend
        # config.addBibleQnA
        # config.answer_systemMessage_general
        # config.answer_systemMessage_youth
        # config.answer_systemMessage_kid
        # config.answer_systemMessage_kid
        # config.groqApi_key
        # config.groqApi_llmTemperature
        # config.groqApi_chat_model
        # config.groqApi_chat_model_max_tokens
        # config.mistralApi_key
        # config.mistralApi_llmTemperature
        # config.mistralApi_chat_model
        # config.mistralApi_chat_model_max_tokens
        # config.grokApi_key
        # config.grokApi_llmTemperature
        # config.grokApi_chat_model
        # config.grokApi_chat_model_max_tokens
        # config.openaiApi_key
        # config.openaiApi_llmTemperature
        # config.openaiApi_chat_model
        # config.openaiApi_chat_model_max_tokens
        # config.googleaiApi_key
        # config.googleaiApi_llmTemperature
        # config.googleaiApi_chat_model
        # config.googleaiApi_chat_model_max_tokens
        setConfig("llm_backend", """
        # Default LLM Backend.""",
        "groq")
        setConfig("enableAICommentary", """
        # Enable AI Commentary.""",
        True)
        setConfig("aiCommentaryIcon", """
        # Specify the icon used for opening AI commentary""",
        '<span class="material-icons-outlined">electric_bolt</span>&nbsp;')
        if not config.aiCommentaryIcon.endswith("&nbsp;"):
            config.aiCommentaryIcon = f"{config.aiCommentaryIcon.strip()}&nbsp;"
        setConfig("displayVerseAICommentaryIcon", """
        # Display indicator for AI commentary""",
        False)
        setConfig("bibleChat_systemMessage", """
        # Default LLM Backend.""",
        "You are a biblical scholar.")
        setConfig("addBibleQnA", """
        # Add Bible Q and A Features to web mode navigation menu.""",
        False)
        setConfig("addBibleChat", """
        # Add Bible Chat to web mode navigation menu.""",
        False)
        setConfig("answer_systemMessage_general", """
        # System Message - General Inquiry""",
        "I would like you to speak like a compassionate church pastor who upholds the truths of the Bible.")
        setConfig("answer_systemMessage_youth", """
        # System Message - Youth""",
        "I would like you to respond as an experienced church youth pastor who is passionate about their faith and dedicated to guiding young people. Speak like you are speaking to a teen.")
        setConfig("answer_systemMessage_kid", """
        # System Message - Kid""",
        "Please speak like a kind Children's Sunday School pastor who loves the Bible and wants to share its wonderful stories with a five-year-old. Use simple words and a gentle, loving tone.")
        setConfig("answer_systemMessage_pray", """
        # System Message - Pray""",
        "I would like you to pray like a compassionate church pastor. Please ensure that your responses to all my requests for prayer are always in the first person, so I can pray them directly.")
        setConfig("answer_systemMessage_quote", """
        # System Message - Quote""",
        "You always quote multiple Bible verses in response to all my requests.")
        setConfig("answer_systemMessage_encourage", """
        # System Message - Encourage""",
        "You always encourage me with Bible promises in a caring and supportive tone..")
        setConfig("answer_systemMessage_interpretot", """
        # System Message - Interpret Old Testament""",
        """# I would like you to interpret the Bible like a biblical scholar.
* Interpret the given bible verses in the light of its context, together with the insights of historical and cultural studies.
* Highlight important key words and explain their original meanings according to Biblical Hebrew studies.
* Quote other related verses in the Bible, if any.
* Elaborate their themes, theological and spiritual meaning of the verses.
* Guide me how to apply in daily life.""")
        setConfig("answer_systemMessage_interpretnt", """
        # System Message - Interpret Old Testament""",
        """# I would like you to interpret the Bible like a biblical scholar.
* Interpret the given bible verses in the light of its context, together with the insights of historical and cultural studies.
* Highlight important key words and explain their original meanings according to Biblical Greek studies.
* Quote other related verses in the Bible, if any.
* Elaborate their themes, theological and spiritual meaning of the verses.
* Guide me how to apply in daily life.""")
        setConfig("groqApi_key", """
        # Groq Cloud API Keys""",
        "")
        setConfig("groqApi_chat_model", """
        # Groq Chat Model""",
        "llama-3.3-70b-versatile")
        setConfig("groqApi_chat_model_max_tokens", """
        # Groq Chat Maximum Output Tokens""",
        8000)
        setConfig("groqApi_llmTemperature", """
        # Groq Chat Temperature""",
        0.3) # 0.2-0.8 is good to use
        setConfig("grokApi_key", """
        # Grok X AI API Keys""",
        "")
        setConfig("grokApi_chat_model", """
        # Grok X AI Chat Model""",
        "grok-beta")
        setConfig("grokApi_chat_model_max_tokens", """
        # Grok X AI Chat Maximum Output Tokens""",
        127999) # maximum 127999, greater than this value causes errors
        setConfig("grokApi_llmTemperature", """
        # Grok X AI Chat Temperature""",
        0.3)
        # mistral
        setConfig("mistralApi_key", """
        # Mistral AI API Keys""",
        "")
        setConfig("mistralApi_chat_model", """
        # Mistral AI Chat Model""",
        "mistral-large-latest")
        setConfig("mistralApi_chat_model_max_tokens", """
        # Mistral AI Chat Maximum Output Tokens""",
        8000)
        setConfig("mistralApi_llmTemperature", """
        # Mistral AI Chat Temperature""",
        0.3) # 0.2-0.7 is good to use
        setConfig("googleaiApi_key", """
        # Google Generative AI API Keys""",
        "")
        setConfig("googleaiApi_chat_model", """
        # Google Generative AI Chat Model""",
        "gemini-1.5-pro")
        setConfig("googleaiApi_chat_model_max_tokens", """
        # Google Generative AI Chat Maximum Output Tokens""",
        8000)
        setConfig("googleaiApi_llmTemperature", """
        # Google Generative AI Chat Temperature""",
        0.3)
        setConfig("openaiApi_key", """
        # OpenAI API Keys""",
        "")
        setConfig("githubApi_key", """
        # Github API Keys""", # either a string or a list of strings
        "")
        setConfig("azureApi_key", """
        # Azure API Key""",
        "")
        setConfig("azureOpenAIModels", """
        # users can manually change config.azureOpenAIModels to match custom model names deployed via Azure service""",
        ["gpt-4o", "gpt-4o-mini"])
        setConfig("azureBaseUrl", """
        # Github API inference endpoint""",
        "")
        setConfig("openaiApi_chat_model", """
        # OpenAI Chat Model""",
        "gpt-4o")
        setConfig("openaiApi_chat_model_max_tokens", """
        # OpenAI Chat Maximum Output Tokens""",
        8000)
        setConfig("openaiApi_llmTemperature", """
        # OpenAI Chat Temperature""",
        0.3) # 0.2-0.8 is good to use

        # 2nd default command
        setConfig("secondDefaultCommand", """
        # `BIBLE:::` is always the default command when no command keyword is specified.
        # When there is no bible reference found in the entry, after trying with the default command, the original command will be prefixed with the value of `config.secondDefaultCommand` and executed with it.""",
        "REGEXSEARCH:::")

        # Start of terminal mode setting
        setConfig("terminalWrapWords", """
        # Wrap words in terminal mode.""",
        True)
        setConfig("terminalEnableTermuxAPI", """
        # Option to enable use of Termux:API tools in UBA.
        # Make sure you have both Termux:API app and termux-api package installed if you want to enable it.
        # Read https://github.com/eliranwong/UniqueBible/wiki/Install-Termux-on-Android#install-termuxapi--termux-api-optional""",
        False)
        setConfig("terminalEnableTermuxAPIToast", """
        # Enable toast message on Android.""",
        False)
        setConfig("terminalTermuxttsSpeed", """
        # Termux text-to-speech speed""",
        1.0)
        setConfig("terminalEnablePager", """
        # To enable paging of terminal output when UBA runs in terminal mode.""",
        False)
        setConfig("terminalEnableClipboardMonitor", """
        # To enable clipboard monitor when users press Enter key in command prompt without text entry.""",
        False)
        setConfig("terminalUseLighterCompleter", """
        # To enable lighter completer to make command completion quicker on slow devices.""",
        True if os.path.isdir("/data/data/com.termux/files/home") else False)
        setConfig("terminalAutoUpdate", """
        # Option to update UBA automatically on startup if newer version is found.""",
        False)
        setConfig("terminalUpdateInOldWay", """
        # Option to update in traditional way of downloading files.""",
        False)
        setConfig("terminalMyMenu", """
        # Customise 'my menu' in terminal mode.
        # UBA does not show 'my menu' if this value is empty""",
        [])
        setConfig("terminalUseMarvelDataPrivate", """
        # Option to use config.marvelDataPrivate in terminal mode.""",
        False)
        setConfig("terminalDefaultCommand", """
        # Define a default command for terminal mode to run when users press Enter key in command prompt without text entry.
        # It is the quickest way to run a favourite command.""",
        ".menu")
        setConfig("terminalDisplayCommandOnMenu", """
        # Option to display command on user-interactive menu.""",
        False)
        setConfig("terminalNoteEditor", """
        # Default note editor used in terminal mode.
        # Suggested options: '', 'micro -softwrap true -wordwrap true', 'nano --softwrap --atblanks -', 'vi -' and 'vim -'.
        # If empty string is given, UBA uses built-in text editor.""",
        "")
        if config.terminalNoteEditor in ("nano --softwrap --atblanks", "vi", "vim"):
            config.terminalNoteEditor = f"{config.terminalNoteEditor} -"
        setConfig("terminalEditorScrollLineCount", """
        # The number of lines terminal text editor scroll with pageup or pagedown keys.""",
        10)
        setConfig("terminalEditorTabText", """
        # The text users insert in text editor when users press the TAB key or 'Ctrl+I'.""",
        "    ")
        setConfig("terminalEditorMaxTextChangeRecords", """
        # Terminal built-in text editor offers 'undo' or 'redo' of text changes.
        # This config value define the maximum number of text change records, which UBA keeps to allow for possible changes via 'undo' or 'redo' features.""",
        10)
        # minimum of 2 records is required
        if config.terminalEditorMaxTextChangeRecords < 2:
            config.terminalEditorMaxTextChangeRecords = 2
        setConfig("terminalForceVlc", """
        # To use third-party VLC media player on terminal mode even config.useThirdPartyVLCplayer is set to False for general cases.""",
        True)
        setConfig("terminalBibleComparison", """
        # To display bible chapter in comparison mode when users enter a reference in terminal mode.""",
        False)
        setConfig("terminalBibleParallels", """
        # To display bible chapter in side-by-side parallel layout.""",
        False)
        setConfig("terminalStartHttpServerOnStartup", """
        # To start http-server on UBA terminal mode startup.""",
        False)
        setConfig("terminalStopHttpServerOnExit", """
        # To stop http-server, if it is running, when users quit UBA terminal mode.""",
        True)
        setConfig("terminalVerseSelectionStart", """
        # Characters displayed at the start of verse selection.""",
        "^⋯")
        setConfig("terminalVerseSelectionEnd", """
        # Characters displayed at the end of verse selection.""",
        "⋯^")
        # support swap between light and dark themes
        #config.help["terminalSwapColors"] = """
        # Swap between light and dark colors in terminal mode."""
        #if not hasattr(config, "terminalSwapColors"):
        #    config.terminalSwapColors = True
        config.terminalColors = {
            "ansidefault": "ansidefault",
            "ansiblack": "ansiwhite",
            "ansired": "ansibrightred",
            "ansigreen": "ansibrightgreen",
            "ansiyellow": "ansibrightyellow",
            "ansiblue": "ansibrightblue",
            "ansimagenta": "ansibrightmagenta",
            "ansicyan": "ansibrightcyan",
            "ansigray": "ansibrightblack",
            "ansiwhite": "ansiblack",
            "ansibrightred": "ansired",
            "ansibrightgreen": "ansigreen",
            "ansibrightyellow": "ansiyellow",
            "ansibrightblue": "ansiblue",
            "ansibrightmagenta": "ansimagenta",
            "ansibrightcyan": "ansicyan",
            "ansibrightblack": "ansigray",
        }
        # old options
        #config.terminalColors = ("RESET", "BLACK", "WHITE", "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "LIGHTBLACK_EX", "LIGHTRED_EX", "LIGHTGREEN_EX", "LIGHTYELLOW_EX", "LIGHTBLUE_EX", "LIGHTMAGENTA_EX", "LIGHTCYAN_EX", "LIGHTWHITE_EX")
        # Colours related configurations in terminal mode
        config.help["terminalPromptIndicatorColor1"] = """
        # Terminal prompt indicator color I.
        # Format: html color code string."""
        if not hasattr(config, "terminalPromptIndicatorColor1") or not config.terminalPromptIndicatorColor1 in config.terminalColors:
            config.terminalPromptIndicatorColor1 = "ansimagenta"
        config.help["terminalCommandEntryColor1"] = """
        # Terminal command entry color I.
        # Format: html color code string."""
        if not hasattr(config, "terminalCommandEntryColor1") or not config.terminalCommandEntryColor1 in config.terminalColors:
            config.terminalCommandEntryColor1 = "ansiyellow"
        config.help["terminalPromptIndicatorColor2"] = """
        # Terminal prompt indicator color II.
        # Format: html color code string."""
        if not hasattr(config, "terminalPromptIndicatorColor2") or not config.terminalPromptIndicatorColor2 in config.terminalColors:
            config.terminalPromptIndicatorColor2 = "ansicyan"
        config.help["terminalCommandEntryColor2"] = """
        # Terminal command entry color II.
        # Format: html color code string."""
        if not hasattr(config, "terminalCommandEntryColor2") or not config.terminalCommandEntryColor2 in config.terminalColors:
            config.terminalCommandEntryColor2 = "ansigreen"
        config.help["terminalHeadingTextColor"] = """
        # Terminal mode heading text color."""
        if not hasattr(config, "terminalHeadingTextColor") or not config.terminalHeadingTextColor in config.terminalColors:
            config.terminalHeadingTextColor = "ansigreen"
        config.help["terminalVerseNumberColor"] = """
        # Terminal mode verse number color."""
        if not hasattr(config, "terminalVerseNumberColor") or not config.terminalVerseNumberColor in config.terminalColors:
            config.terminalVerseNumberColor = "ansicyan"
        config.help["terminalResourceLinkColor"] = """
        # Terminal mode resource link color."""
        if not hasattr(config, "terminalResourceLinkColor") or not config.terminalResourceLinkColor in config.terminalColors:
            config.terminalResourceLinkColor = "ansiyellow"
        config.help["terminalVerseSelectionBackground"] = """
        # Terminal mode verse selection background color."""
        if not hasattr(config, "terminalVerseSelectionBackground") or not config.terminalVerseSelectionBackground in config.terminalColors:
            config.terminalVerseSelectionBackground = "ansimagenta"
        config.help["terminalVerseSelectionForeground"] = """
        # Terminal mode verse selection foreground color."""
        if not hasattr(config, "terminalVerseSelectionForeground") or not config.terminalVerseSelectionForeground in config.terminalColors:
            config.terminalVerseSelectionForeground = "ansidefault"
        config.help["terminalSearchHighlightBackground"] = """
        # Terminal mode search highlight background color."""
        if not hasattr(config, "terminalSearchHighlightBackground") or not config.terminalSearchHighlightBackground in config.terminalColors:
            config.terminalSearchHighlightBackground = "ansiblue"
        config.help["terminalSearchHighlightForeground"] = """
        # Terminal mode search highlight foreground color."""
        if not hasattr(config, "terminalSearchHighlightForeground") or not config.terminalSearchHighlightForeground in config.terminalColors:
            config.terminalSearchHighlightForeground = "ansidefault"
        config.help["terminalFindHighlightBackground"] = """
        # Terminal mode find highlight background color."""
        if not hasattr(config, "terminalFindHighlightBackground") or not config.terminalFindHighlightBackground in config.terminalColors:
            config.terminalFindHighlightBackground = "ansired"
        config.help["terminalFindHighlightForeground"] = """
        # Terminal mode find highlight foreground color."""
        if not hasattr(config, "terminalFindHighlightForeground") or not config.terminalFindHighlightForeground in config.terminalColors:
            config.terminalFindHighlightForeground = "ansidefault"

        # End of terminal mode settings

        # Start of terminal mode customised input settings

        setConfig("terminal_cancel_action", """
        # Customise the entry to cancel action in current prompt.
        # Attention! This value must be in lower cases.""",
        ".cancel")

        setConfig("terminal_dot_a", """
        # Customise the command to be run with shortcut entry '.a'.""",
        ".aliases")
        setConfig("terminal_dot_b", """
        # Customise the command to be run with shortcut entry '.b'.""",
        ".backward")
        setConfig("terminal_dot_c", """
        # Customise the command to be run with shortcut entry '.c'.""",
        ".togglecomparison")
        setConfig("terminal_dot_d", """
        # Customise the command to be run with shortcut entry '.d'.""",
        ".data")
        setConfig("terminal_dot_e", """
        # Customise the command to be run with shortcut entry '.e'.""",
        ".editor")
        setConfig("terminal_dot_f", """
        # Customise the command to be run with shortcut entry '.f'.""",
        ".forward")
        setConfig("terminal_dot_g", """
        # Customise the command to be run with shortcut entry '.g'.""",
        ".togglepager")
        setConfig("terminal_dot_h", """
        # Customise the command to be run with shortcut entry '.h'.""",
        ".help")
        setConfig("terminal_dot_i", """
        # Customise the command to be run with shortcut entry '.i'.""",
        "index:::")
        setConfig("terminal_dot_j", """
        # Customise the command to be run with shortcut entry '.j'.""",
        ".editjournal")
        setConfig("terminal_dot_k", """
        # Customise the command to be run with shortcut entry '.k'.""",
        "tske:::")
        setConfig("terminal_dot_l", """
        # Customise the command to be run with shortcut entry '.l'.""",
        ".latestbible")
        setConfig("terminal_dot_m", """
        # Customise the command to be run with shortcut entry '.m'.""",
        ".maps")
        setConfig("terminal_dot_n", """
        # Customise the command to be run with shortcut entry '.n'.""",
        ".note")
        setConfig("terminal_dot_o", """
        # Customise the command to be run with shortcut entry '.o'.""",
        ".open")
        setConfig("terminal_dot_p", """
        # Customise the command to be run with shortcut entry '.p'.""",
        ".toggleparallels")
        setConfig("terminal_dot_r", """
        # Customise the command to be run with shortcut entry '.r'.""",
        ".run")
        setConfig("terminal_dot_s", """
        # Customise the command to be run with shortcut entry '.s'.""",
        ".swap")
        setConfig("terminal_dot_t", """
        # Customise the command to be run with shortcut entry '.t'.""",
        ".tts")
        setConfig("terminal_dot_u", """
        # Customise the command to be run with shortcut entry '.u'.""",
        ".downloadyoutube")
        setConfig("terminal_dot_v", """
        # Customise the command to be run with shortcut entry '.v'.""",
        ".versefeatures")
        setConfig("terminal_dot_w", """
        # Customise the command to be run with shortcut entry '.w'.""",
        ".web")
        setConfig("terminal_dot_x", """
        # Customise the command to be run with shortcut entry '.x'.""",
        "crossreference:::")
        setConfig("terminal_dot_y", """
        # Customise the command to be run with shortcut entry '.y'.""",
        ".whatis")
        setConfig("terminal_ctrl_b", """
        # Customise the command to be run with key combination 'ctrl + b'.""",
        ".backward")
        setConfig("terminal_ctrl_f", """
        # Customise the command to be run with key combination 'ctrl + f'.""",
        ".forward")
        setConfig("terminal_ctrl_g", """
        # Customise the command to be run with key combination 'ctrl + g'.""",
        ".togglepager")
        setConfig("terminal_ctrl_k", """
        # Customise the command to be run with key combination 'ctrl + k'.""",
        "tske:::")
        setConfig("terminal_ctrl_l", """
        # Customise the command to be run with key combination 'ctrl + l'.""",
        ".latestbible")
        setConfig("terminal_ctrl_r", """
        # Customise the command to be run with key combination 'ctrl + r'.""",
        ".run")
        setConfig("terminal_ctrl_s", """
        # Customise the command to be run with key combination 'ctrl + s'.""",
        ".swap")
        setConfig("terminal_ctrl_u", """
        # Customise the command to be run with key combination 'ctrl + u'.""",
        ".stopaudio")
        setConfig("terminal_ctrl_w", """
        # Customise the command to be run with key combination 'ctrl + w'.""",
        ".web")
        setConfig("terminal_ctrl_y", """
        # Customise the command to be run with key combination 'ctrl + y'.""",
        ".whatis")

        # End of terminal mode customised input settings

        # ssh server
        setConfig("sshServerHost", """
        # To specify ssh server host.""",
        "")
        setConfig("sshServerPort", """
        # To specify ssh server port.""",
        2222)
        setConfig("sshServerHostKeys", """
        # To specify ssh server host keys, either a string or a list of strings.""",
        "")
        setConfig("sshServerPassphrase", """
        # To specify ssh server passphrase.""",
        "the_best_bible_app")
        # telnet-server
        setConfig("telnetServerPort", """
        # To specify the port used by telnet-server.""",
        8888)
        # http-server
        setConfig("httpServerPort", """
        # To specify the port used by http-server.""",
        8080)
        setConfig("httpServerViewerGlobalMode", """
        # Set to true to enable global mode for http-server viewer.  If false, only viewers on same wifi can access the link""",
        False)
        setConfig("webUBAServer", """
        # Specify a web server to work with the share links.
        # Default is 'https://bible.gospelchurch.uk'
        # Users can specify a private page, e.g. 'https://ubaserver.com/private.html'""",
        "https://bible.gospelchurch.uk")
        setConfig("httpServerViewerBaseUrl", """
        # Base URL for http-server viewer""",
        "https://marvelbible.com/uba_viewer")
        setConfig("webOrganisationIcon", """
        # Customise an organisation icon filename.  The filename given should be a path relative to directory 'htmlResouces/'.""",
        "")
        setConfig("webOrganisationLink", """
        # Customise an organisation link.""",
        "")
        setConfig("webFullAccess", """
        # Full server to web http-server from browser, including shutdown or restart server.""",
        True)
        setConfig("webPrivateHomePage", """
        # Specify a homepage, to which only developers can access.""",
        "")
        setConfig("httpServerUbaFile", """
        # Specify a python file to start http-server mode.""",
        "uba.py")
        setConfig("webUI", """
        # To specify web user interface.""",
        "mini")
        setConfig("webPresentationMode", """
        # Http-server presentation mode - only the primary user have full control and ability to share content to other users.""",
        False)
        setConfig("webCollapseFooterHeight", """
        # Collapse footer height for http-server.""",
        False)
        setConfig("webDecreaseBibleDivWidth", """
        # Adjust bibleDiv width to be narrower.""",
        "")
        setConfig("webPaddingLeft", """
         # Add padding-left size to body.""",
        "0px")
        setConfig("webAdminPassword", """
         # Web admin password.""",
        "UBA123")
        setConfig("webSiteTitle", """
        # Site title for remote http server.""",
        "UniqueBible.app")
        setConfig("referenceTranslation", """
        # Specify a translation as a reference for making other translations.  This option is created for development purpose.""",
        "en_US")
        setConfig("workingTranslation", """
        # Specify the translation which is actively being edited.  This option is created for development purpose.""",
        "en_US")
        setConfig("myGoogleApiKey", """
        # Personal google api key for display of google maps inside UBA window.""",
        "")
        config.help["alwaysDisplayStaticMaps"] = """
        # Options to always display static maps even "myGoogleApiKey" is not empty: True / False"""
        if not hasattr(config, "alwaysDisplayStaticMaps"):
            if config.myGoogleApiKey:
                config.alwaysDisplayStaticMaps = False
            else:
                config.alwaysDisplayStaticMaps = True
        setConfig("chatApiNoOfChoices", """
        # ChatGPT API number of choices in response
        # How many chat completion choices to generate for each input message.""",
        1)
        setConfig("chatApiFunctionCall", """
        # Enable / Disable ChatGPT function calling
        # Select 'auto' to enable; 'none' to disable""",
        "none")
        setConfig("chatGPTApiLastChatDatabase", """
        # The latest chat database file that was opened.""",
        "")
        setConfig("chatGPTApiPredefinedContext", """
        # Set a predefined context""",
        "[none]")
        setConfig("chatGPTApiContext", """
        # Set a context for chatGPT conversations""",
        "# Study the Bible")
        setConfig("chatGPTApiContextInAllInputs", """
        # ChatGP API - predefined context in all inputs.""",
        False)
        setConfig("chatApiLoadingInternetSearches", """
        # ChatGPT API - always loading internet searches.
        # options - 'always', 'auto', 'none'.""",
        "none")
        setConfig("chatGPTApiMaximumInternetSearchResults", """
        # ChatGPT API - maximum number of internet search results to be integrated.""",
        5)
        setConfig("chatGPTApiAutoScrolling", """
        # Auto-scroll display as response is received""",
        True)
        setConfig("chatGPTFontSize", """
        # Set chatGPT conversation font size""",
        14)
        setConfig("chatGPTApiAudio", """
        # ChatGPT API Response Audio Playback.""",
        False)
        setConfig("chatGPTApiAudioLanguage", """
        # Language for ChatGPT API Response Audio Playback.""",
        "en")
        setConfig("chatGPTApiSearchRegexp", """
        # Option to search chat content or database with regular expression.""",
        True)
        setConfig("chatGPTPluginExcludeList", """
        # Option to exclude ChatGPT plugins from running.""",
        [])
        setConfig("chatAfterFunctionCalled", """
        # Option to automatically generate next chat response after a function is called.""",
        True)
        setConfig("runPythonScriptGlobally", """
        # Option to execute Python Script Globally via plugin Bible Chat.""",
        False)
        setConfig("pocketsphinxModelPath", """
        # Model path of pocketsphinx""",
        "")
        setConfig("pocketsphinxModelPathBin", """
        # Model path of pocketsphinx bin""",
        "")
        setConfig("pocketsphinxModelPathDict", """
        # Model path of pocketsphinx dict""",
        "")
        setConfig("updateDependenciesOnStartup", """
        # Update Dependencies on Startup: True / False""",
        False)
        if config.updateDependenciesOnStartup:
            config.enabled = []
            config.disabled = []
        if "Nltk" in config.enabled:
            try:
                from nltk.corpus import wordnet
                wordnet.lemmas("english")
                config.wordnet = wordnet
            except:
                pass
        if "Lemmagen3" in config.enabled:
            try:
                from lemmagen3 import Lemmatizer
                config.lemmatizer = Lemmatizer("en")
            except:
                pass
        if "Chineseenglishlookup" in config.enabled:
            try:
                from chinese_english_lookup import Dictionary
                config.cedict = Dictionary()
            except:
                pass
        setConfig("showControlPanelOnStartup", """
        # Options to use control panel: True / False
        # This feature is created for use in church settings.
        # If True, users can use an additional command field, in an additional window, to control the content being displayed, even the main window of UniqueBible.app is displayed on extended screen.""",
        False)
        config.help["preferControlPanelForCommandLineEntry"] = """
        # {0}""".format(language_en_GB.translation["preferControlPanelForCommandLineEntry"])
        if not hasattr(config, "preferControlPanelForCommandLineEntry"):
            config.preferControlPanelForCommandLineEntry = False
        config.help["closeControlPanelAfterRunningCommand"] = """
        # {0}""".format(language_en_GB.translation["closeControlPanelAfterRunningCommand"])
        if not hasattr(config, "closeControlPanelAfterRunningCommand"):
            config.closeControlPanelAfterRunningCommand = True
        config.help["restrictControlPanelWidth"] = """
        # {0}""".format(language_en_GB.translation["restrictControlPanelWidth"])
        if not hasattr(config, "restrictControlPanelWidth"):
            config.restrictControlPanelWidth = False
        setConfig("masterControlWidth", """
        # Specify the width of Master Control panel.""",
        1255)
        setConfig("miniControlInitialTab", """
        # Specify the initial tab index of Mini Control panel.""",
        0)
        setConfig("addBreakAfterTheFirstToolBar", """
        # Add a line break after the first toolbar.""",
        True)
        setConfig("addBreakBeforeTheLastToolBar", """
        # Add a line break before the last toolbar.""",
        False)
        setConfig("verseNoSingleClickAction", """
        # Configure verse number single-click action
        # available options: "_noAction", "_cp0", "_cp1", "_cp2", "_cp3", "_cp4", "COMPARE", "CROSSREFERENCE", "TSKE", "TRANSLATION", "DISCOURSE", "WORDS", "COMBO", "INDEX", "COMMENTARY", "_menu"
        # corresponding translation: "noAction", "cp0", "cp1", "cp2", "cp3", "cp4", "menu4_compareAll", "menu4_crossRef", "menu4_tske", "menu4_traslations", "menu4_discourse", "menu4_words", "menu4_tdw", "menu4_indexes", "menu4_commentary", "classicMenu" """,
        "_menu" if config.enableHttpServer else "INDEX")
        setConfig("verseNoDoubleClickAction", """
        # Configure verse number double-click action
        # available options: "_noAction", "_cp0", "_cp1", "_cp2", "_cp3", "_cp4", "COMPARE", "CROSSREFERENCE", "TSKE", "TRANSLATION", "DISCOURSE", "WORDS", "COMBO", "INDEX", "COMMENTARY", "_menu"
        # corresponding translation: "noAction", "cp0", "cp1", "cp2", "cp3", "cp4", "menu4_compareAll", "menu4_crossRef", "menu4_tske", "menu4_traslations", "menu4_discourse", "menu4_words", "menu4_tdw", "menu4_indexes", "menu4_commentary", "classicMenu" """,
        "CROSSREFERENCE" if config.enableHttpServer else "_cp0")
        setConfig("startFullScreen", """
        # Start UBA with full-screen""",
        False)
        setConfig("linuxStartFullScreen", """
        # Start UBA with full-screen on Linux os""",
        False)
        setConfig("enableClipboardMonitoring", """
        # Enable Clipboard Monitoring""",
        False)
        setConfig("enableSystemTrayOnLinux", """
        # Enable UBA system tray on Linux os""",
        False)
        setConfig("piper", """
        # Piper text-to-speech feature on Linux""",
        False)
        setConfig("piperVoice", """
        # Piper text-to-speech voice""",
        "en_US-lessac-medium")
        setConfig("forceOnlineTts", """
        # This forces default text-to-speech feature uses online service, even if offline tts engine is installed.""",
        False)
        config.help["espeak"] = """
        # Use espeak for text-to-speech feature instead of built-in qt tts engine
        # espeak is a text-to-speech tool that can run offline
        # To check for available langauge codes, run on terminal: espeak --voices
        # Notes on espeak setup is available at: https://github.com/eliranwong/ChromeOSLinux/blob/main/multimedia/espeak.md
        # If you need text-to-speech features to work on Chinese / Russian text, you may read the link above."""
        if not hasattr(config, "espeak"):
            # Check if UniqueBible.app is running on Chrome OS:
            if (os.path.exists("/mnt/chromeos/")):
                config.espeak = True
            else:
                config.espeak = False
        setConfig("espeakSpeed", """
        # espeak speed""",
        160)
        setConfig("gcttsSpeed", """
        # Google Cloud text-to-speech speed""",
        1.0)
        setConfig("mediaSpeed", """
        # Built-in media player playback speed""",
        1.0)
        setConfig("audioVolume", """
        # Built-in media player playback audio volume""",
        100)
        setConfig("speedUpFilterFrequency", """
        # Cutoff frequency used for low_pass_filter and high_pass_filter when audio file speed is increased with pydub.
        # Changing this value may change the quality of audio with increased speed.
        # Read low_pass_filter and high_pass_filter at:
        # https://github.com/jiaaro/pydub/blob/master/pydub/effects.py#L221""",
        500)
        setConfig("vlcSpeed", """
        # VLC player playback speed""",
        1.0)
        setConfig("macOSttsSpeed", """
        # Apple macOS text-to-speech speaking rate""",
        200)
        setConfig("qttsSpeed", """
        # Qt text-to-speech speed""",
        0.0)
        setConfig("useLangDetectOnTts", """
        # Apply language detect package to text-to-speech feature.""",
        False)
        setConfig("ttsDefaultLangauge", """
        # Default text-to-speech language""",
        "en")
        setConfig("ttsDefaultLangauge2", """
        # Second text-to-speech language""",
        "")
        setConfig("ttsDefaultLangauge3", """
        # Third text-to-speech language""",
        "")
        setConfig("ttsDefaultLangauge4", """
        # Fourth text-to-speech language""",
        "")
        setConfig("ttsChineseAlwaysCantonese", """
        # Force text-to-speech feature to use Cantonese for all Chinese text.""",
        False)
        setConfig("ttsChineseAlwaysMandarin", """
        # Force text-to-speech feature to use Mandarin for all Chinese text.""",
        False)
        setConfig("ttsEnglishAlwaysUS", """
        # Force text-to-speech feature to use English (US) for all Chinese text.""",
        False)
        setConfig("ttsEnglishAlwaysUK", """
        # Force text-to-speech feature to use English (UK) for all Chinese text.""",
        False)
        setConfig("ibus", """
        # Use ibus, if installed, as input method.""",
        False)
        setConfig("fcitx", """
        # Use fcitx, if installed, as input method.""",
        False)
        setConfig("fcitx5", """
        # Use fcitx5, if installed, as input method.""",
        False)
        setConfig("virtualKeyboard", """
        # Options to use built-in virtual keyboards: True / False""",
        False)
        setConfig("openWindows", """
        # Specify the "open" command on Windows""",
        "start")
        setConfig("openMacos", """
        # Specify the "open" command on macOS""",
        "open")
        setConfig("openLinux", """
        # Specify the "open" command on Linux""",
        "xdg-open")
        setConfig("openLinuxPdf", """
        # Specify the command to open pdf file on Linux""",
        "xdg-open")
        setConfig("openLinuxDirectory", """
        # Specify the command to open a directory on Linux""",
        "xdg-open")
        setConfig("openLinuxTerminal", """
        # Specify the command to launch a terminal app on Linux""",
        "x-terminal-emulator")
        config.help["marvelData"] = """
        # Specify the folder path of resources"""
        if not hasattr(config, "marvelData") or not os.path.isdir(config.marvelData):
            userMarvelData = os.path.join(config.ubaUserDir, "marvelData")
            if os.path.isdir(userMarvelData):
                config.marvelData = userMarvelData
            else:
                config.marvelData = "marvelData"
        config.help["marvelDataPublic"] = """
        # Public marvelData Directory."""
        if not hasattr(config, "marvelDataPublic") or not os.path.isdir(config.marvelData):
            config.marvelDataPublic = "marvelData"
        config.help["marvelDataPrivate"] = """
        # Private marvelData Directory."""
        if not hasattr(config, "marvelDataPrivate") or not os.path.isdir(config.marvelData):
            config.marvelDataPrivate = "marvelData"
        setConfig("musicFolder", """
        # Specify the folder path of music files""",
        "music")
        setConfig("audioFolder", """
        # Specify the folder path of audio bible files""",
        "audio")
        setConfig("audioBibleIcon", """
        # Specify the icon used for playing audio bible features""",
        '<span class="material-icons-outlined">audiotrack</span>&nbsp;')
        if not config.audioBibleIcon.endswith("&nbsp;"):
            config.audioBibleIcon = f"{config.audioBibleIcon.strip()}&nbsp;"
        setConfig("audioBibleIcon2", """
        # Specify the icon used for playing audio bible features, which work with config.readTillChapterEnd.""",
        '<span class="material-icons">audiotrack</span>&nbsp;')
        if not config.audioBibleIcon2.endswith("&nbsp;"):
            config.audioBibleIcon2 = f"{config.audioBibleIcon2.strip()}&nbsp;"
        setConfig("displayVerseAudioBibleIcon", """
        # Display verse audio bible icon""",
        True)
        setConfig("videoFolder", """
        # Specify the folder path of video files""",
        "video")
        setConfig("bibleNotes", """
        # Specify the file path of note file on bible chapters and verses""",
        "note.sqlite")
        setConfig("numberOfTab", """
        # Specify the number of tabs for bible reading and workspace""",
        5)
        setConfig("populateTabsOnStartup", """
        # Options to populate tabs with latest history records on start up: True / False""",
        False)
        setConfig("displayLoadingTime", """
        # Time, in millisecond, to display Main/Study Window loading time""",
        1 if config.qtLibrary == "pyside6" else 500)
        setConfig("openBibleWindowContentOnNextTab", """
        # Options to open Bible Window's content in the tab next to the current one: True / False""",
        False)
        setConfig("openStudyWindowContentOnNextTab", """
        # Options to open Study Window's content in the tab next to the current one: True / False""",
        True)
        setConfig("updateMainReferenceOnChangingTabs", """
        # Options to update main reference buttons when Bible Window tabs are changed: True / False""",
        False)
        setConfig("preferHtmlMenu", """
        # Options to open classic html menu when a bible chapter heading is clicked
        # It is set to False by default that clicking a chapter heading opens Master Control panel.""",
        False)
        setConfig("parserStandarisation", """
        # Options to convert all bible book abbreviations to standard ones: YES / NO""",
        "NO")
        setConfig("standardAbbreviation", """
        # Options of language of book abbreviations: ENG / TC / SC""",
        "ENG")
        setConfig("noOfLinesPerChunkForParsing", """
        # Large-size text is divided into chunks before parsing, in order to improve performance.  
        # This option specify maximum number of lines included into each chunk.  
        # Too many or too little can affect performance.  
        # Choose a value suitable for your device.  
        # Generally, device with higher memory capacity can handle more numbers of line in each chunk.""",
        100)
        setConfig("convertChapterVerseDotSeparator", """
        # Option to convert the dot sign, which separates chapter number and verse number in some bible references, to colon sign so that UBA parser can parse those referencces.""",
        True)
        setConfig("parseBookChapterWithoutSpace", """
        # Parse references without space between book name and chapter number.""",
        True)
        setConfig("parseBooklessReferences", """
        # Parse bookless references in selected text.""",
        True)
        setConfig("parseEnglishBooksOnly", """
        # Parse bible verse references with English books only.""",
        False)
        config.help["userLanguage"] = """
        # Option to set a customised language for google-translate
        # References: https://cloud.google.com/translate/docs/languages
        # Use gui "Set my Language" dialog, from menu bar, to set "userLanguage"."""
        if not hasattr(config, "userLanguage") or not config.userLanguage:
            config.userLanguage = "English"
        setConfig("userLanguageInterface", """
        # Option to use interface translated into userLanguage: True / False""",
        False)
        setConfig("autoCopyTranslateResult", """
        # Option to copy automatically to clipboard the result of accessing Google Translate: True / False""",
        True)
        setConfig("showVerseNumbersInRange", """
        # Option to display verse number in a range of verses: True / False
        # e.g. Try entering in command field "Ps 23:1; Ps 23:1-3; Ps 23:1-24:3" """,
        True)
        setConfig("openBibleNoteAfterSave", """
        # Options to open chapter / verse note on Study Window after saving: True / False""",
        False)
        setConfig("openBibleNoteAfterEditorClosed", """
        # Default: False: Open bible note on Study Window afer it is edited with Note Editor.
        # Bible note is opened when Note editor is closed.""",
        False)
        setConfig("exportEmbeddedImages", """
        # Options to export all embedded images displayed on Study Window: True / False""",
        True)
        setConfig("clickToOpenImage", """
        # Options to add open image action with a single click: True / False""",
        True)
        setConfig("landscapeMode", """
        # Options to use landscape mode: True / False""",
        True)
        setConfig("noToolBar", """
        # Options for NOT displaying any toolbars on startup: True / False""",
        False)
        setConfig("topToolBarOnly", """
        # Options to display the top toolbar only, with all other toolbars hidden: True / False""",
        False)
        setConfig("toolBarIconFullSize", """
        # Options to use large sets of icons: True / False""",
        False)
        setConfig("iconButtonSize", """
        # Options to set icon button size.  This value applies to icon width and height.
        # Ideally, the value is a multiple of 3, within a range from 12 to 48.
        # This value is used as a reference point to scale all other widgets when you use Material menu layout.""",
        18)
        setConfig("maximumIconButtonWidth", """
        # Options to set maximum icon button width""",
        48)
        setConfig("toolbarIconSizeFactor", """
        # Toolbar icon size factor""",
        0.75)
        setConfig("sidebarIconSizeFactor", """
        # Sidebar icon size factor""",
        0.6)
        setConfig("parallelMode", """
        # Options on parallel mode: 0, 1, 2, 3""",
        1)
        setConfig("instantMode", """
        # Options to display the window showing instant information: 0, 1""",
        1)
        setConfig("enableInstantHighlight", """
        # Options to implement instant highlight feature: True / False""",
        False)
        setConfig("enableSelectionMonitoring", """
        # Options to enable selection monitoring: True / False""",
        False)
        setConfig("instantInformationEnabled", """
        # Options to trigger instant information: True / False""",
        True)
        setConfig("floatableInstantViewWidth", """
        # Specify the width of extra instant view""",
        400)
        setConfig("floatableInstantViewHeight", """
        # Specify the height of extra instant view""",
        250)
        setConfig("audioTextSync", """
        # Options to enable text synchronisation with audio playing: True / False""",
        True)
        setConfig("scrollBibleTextWithAudioPlayback", """
        # Options to scroll bible text with audio synchronisation: True / False""",
        False)
        setConfig("loopMediaPlaylist", """
        # Options to loop media player playlist: True / False""",
        False)
        setConfig("maximiseMediaPlayerUI", """
        # Options to maximise media player graphical user interface: True / False""",
        True)
        setConfig("fontSize", """
        # Default font size of content in main window and workspace""",
        18)
        setConfig("font", """
        # Default font""",
        "")
        setConfig("fontChinese", """
        # Default Chinese font""",
        "")
        setConfig("noteEditorFontSize", """
        # Default font size of content in note editor""",
        14)
        setConfig("dockNoteEditorOnStartup", """
        # Dock Note Editor when it is launched.""",
        True)
        setConfig("doNotDockNoteEditorByDragging", """
        # Do not dock Note Editor by dragging.""",
        False)
        setConfig("hideNoteEditorStyleToolbar", """
        # Show Note Editor's style toolbar by default""",
        False)
        setConfig("hideNoteEditorTextUtility", """
        # Hide Note Editor's text utility by default""",
        True)
        setConfig("readFormattedBibles", """
        # Options to display bibles in formatted layout or paragraphs: True / False
        # "False" here means displaying bible verse in plain format, with each one on a single line.""",
        True)
        setConfig("addTitleToPlainChapter", """
        # Options to add sub-headings when "readFormattedBibles" is set to "False": True / False""",
        True)
        setConfig("displayChapterMenuTogetherWithBibleChapter", """
        # Display chapter menu together with bible chapter: True / False""",
        False)
        setConfig("showVerseReference", """
        # Options to display verse reference: True / False""",
        True)
        setConfig("useFfmpegToChangeAudioSpeed", """
        # Options to use ffmpeg library to change audio speed: True / False
        # This applies only to mp3 and wav audio files playing with built-in media player.""",
        False)
        setConfig("usePydubToChangeAudioSpeed", """
        # Options to use pydub library to change audio speed: True / False
        # This applies only to mp3 and wav audio files playing with built-in media player.""",
        False)
        setConfig("useThirdPartyVLCplayer", """
        # Options to use third-party VLC player: True / False""",
        False)
        setConfig("useThirdPartyVLCplayerForVideoOnly", """
        # Options to use third-party VLC player for video playback only: True / False""",
        False)
        setConfig("doNotStop3rdPartyMediaPlayerOnExit", """
        # Options to not stop 3rd-party media player on exit: True / False""",
        False)
        setConfig("hideVlcInterfaceReadingSingleVerse", """
        # Options to hide VLC graphical interface on supported operating systems: True / False""",
        True)
        setConfig("showHebrewGreekWordAudioLinks", """
        # Options to display word-by-word Hebrew & Greek audio links: True / False""",
        False)
        setConfig("showHebrewGreekWordAudioLinksInMIB", """
        # Options to display word-by-word Hebrew & Greek audio links in bible module, MIB: True / False""",
        False)
        setConfig("hideLexicalEntryInBible", """
        # Options to hide lexical entries or Strong's numbers: True / False""",
        False)
        setConfig("readTillChapterEnd", """
        # Options to read, with audio bible, through the rest of a chapter from a verse: True / False""",
        True)
        setConfig("importAddVerseLinebreak", """
        # Import setting - add a line break after each verse: True / False""",
        False)
        setConfig("importDoNotStripStrongNo", """
        # Import setting - keep Strong's number for search: True / False""",
        False)
        setConfig("importDoNotStripMorphCode", """
        # Import setting - keep morphology codes for search: True / False""",
        False)
        setConfig("importRtlOT", """
        # Import setting - import text in right-to-left direction: True / False""",
        False)
        setConfig("importInterlinear", """
        # Import setting - import interlinear text: True / False""",
        False)
        config.help["originalTexts"] = """
        # List of modules, which contains Hebrew / Greek texts"""
        if not hasattr(config, "originalTexts"):
            config.originalTexts = ['original', 'MOB', 'MAB', 'MTB', 'MIB', 'MPB', 'OHGB', 'OHGBi', 'LXX', 'LXX1',
                                    'LXX1i',
                                    'LXX2', 'LXX2i']
        config.help["rtlTexts"] = """
        # List of modules, which contains right-to-left texts on old testament"""
        rtlTexts = ["original", "MOB", "MAB", "MIB", "MPB", "OHGB", "OHGBi", "WLC", "WLCx"]
        if not hasattr(config, "rtlTexts"):
            config.rtlTexts = rtlTexts
        else:
            for text in rtlTexts:
                if not text in config.rtlTexts:
                    config.rtlTexts.append(text)
        setConfig("openBibleInMainViewOnly", """
        # Open bible references on main window instead of workspace: Ture / False""",
        False)
        setConfig("mainText", """
        # Last-opened bible text on Main Window""",
        "KJV")
        setConfig("mainB", """
        # Last-opened bible book number on Main Window""",
        1)
        setConfig("mainC", """
        # Last-opened bible chapter number on Main Window""",
        1)
        setConfig("mainV", """
        # Last-opened bible verse number on Main Window""",
        1)
        setConfig("studyText", """
        # Last-opened bible module on Study Window""",
        "NET")
        setConfig("studyB", """
        # Last-opened bible book number on Study Window""",
        43)
        setConfig("studyC", """
        # Last-opened bible chapter number on Study Window""",
        3)
        setConfig("studyV", """
        # Last-opened bible verse number on Study Window""",
        16)
        setConfig("liveFilterBookFilter", """
        # Book Filter for Live Filter""",
        [])
        setConfig("bibleSearchRange", """
        # Pre-defined Book Range for Bible Search""",
        "clear")
        setConfig("customBooksRangeSearch", """
        # Custom Book Range for Bible Search""",
        "")
        setConfig("bibleSearchMode", """
        # Search Bible Mode
        # Accept value: 0-5
        # Correspond to ("COUNT", "SEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")""",
        0)
        config.help["workspaceDirectory"] = """
        # Set the directory for storing workspace files."""
        if not hasattr(config, "workspaceDirectory") or not os.path.isdir(config.workspaceDirectory):
            config.workspaceDirectory = "workspace"
        config.help["workspaceSavingOrder"] = """
        # Set the order for saving workspace files.
        # 0 - CreationOrder
        # 1 - StackingOrder
        # 2 - ActivationHistoryOrder
        # Read more at https://github.com/eliranwong/UniqueBible/wiki/Workspace#auto-save"""
        if not hasattr(config, "workspaceSavingOrder") or not config.workspaceSavingOrder in (0, 1, 2):
            config.workspaceSavingOrder = 0
        setConfig("favouriteOriginalBible", """
        # Set your favourite marvel bible version here
        # MOB, MIB, MTB, MPB, MAB""",
        "MIB")
        setConfig("favouriteOriginalBible2", """
        # Set your second favourite marvel bible version here
        # MOB, MIB, MTB, MPB, MAB""",
        "MPB")
        setConfig("favouriteBible", """
        # Set your favourite bible version here""",
        "OHGBi")
        setConfig("favouriteBible2", """
        # Set your second favourite bible version here""",
        "KJV")
        setConfig("favouriteBible3", """
        # Set your third favourite bible version here""",
        "NET")
        setConfig("favouriteBiblePrivate", """
        # Set your favourite bible version here""",
        "OHGBi")
        setConfig("favouriteBiblePrivate2", """
        # Set your second favourite bible version here""",
        "KJV")
        setConfig("favouriteBiblePrivate3", """
        # Set your third favourite bible version here""",
        "NET")
        setConfig("favouriteBibleTC", """
        # Set your favourite bible version here for traditional Chinese interface.""",
        "CUV")
        setConfig("favouriteBibleTC2", """
        # Set your second favourite bible version here for traditional Chinese interface.""",
        "KJV")
        setConfig("favouriteBibleTC3", """
        # Set your third favourite bible version here for traditional Chinese interface.""",
        "NET")
        setConfig("favouriteBibleSC", """
        # Set your favourite bible version here for simplified Chinese interface.""",
        "CUVs")
        setConfig("favouriteBibleSC2", """
        # Set your second favourite bible version here for simplified Chinese interface.""",
        "KJV")
        setConfig("favouriteBibleSC3", """
        # Set your third favourite bible version here for simplified Chinese interface.""",
        "NET"        )
        setConfig("addFavouriteToMultiRef", """
        # Options to display "favouriteBible" together with the main version for reading multiple references: True / False""",
        True)
        setConfig("compareParallelList", """
        # Specify bible versions to work with parallel:::, compare:::, and sidebyside::: commands in material menu layout.""",
        list({config.favouriteBible, config.favouriteBible2, config.favouriteBible3}))
        config.compareParallelList.sort()
        setConfig("enforceCompareParallel", """
        # Options to enforce comparison / parallel: True / False
        # When it is enabled after comparison / parallel feature is loaded once, subsequence entries of bible references will be treated as launching comparison / parallel even COMPARE::: or PARALLEL::: keywords is not used.
        # Please note that change in bible version for chapter reading is ignored when this option is enabled.
        # This feature is accessible via a left toolbar button, located under the "Comparison / Parallel Reading / Difference" button.""",
        False)
        setConfig("compareOnStudyWindow", """
        # Options to display comparison on Study Window: True / False""",
        False)
        setConfig("showUserNoteIndicator", """
        # Options to show user note indicator on bible chapter: True / False""",
        True)
        setConfig("showBibleNoteIndicator", """
        # Options to show bible module note indicator on bible chapter: True / False""",
        True)
        setConfig("syncAction", """
        # Command keyword, in upper case, for sync option.  Set empty string to disable sync action.""",
        "")
        if not config.compareOnStudyWindow and config.syncAction in ("PARALLEL", "SIDEBYSIDE", "COMPARE"):
            config.syncAction = ""
        setConfig("commentaryText", """
        # Last-opened commentary module""",
        "CBSC")
        setConfig("commentaryB", """
        # Last-opened commentary book number""",
        43)
        setConfig("commentaryC", """
        # Last-opened commentary chapter number""",
        3)
        setConfig("commentaryV", """
        # Last-opened commentary verse number""",
        16)
        setConfig("concordance", """
        # Last-opened module for concordance""",
        "OHGBi")
        setConfig("concordanceEntry", """
        # Last-opened entry for concordance""",
        "")
        setConfig("topic", """
        # Last-opened module for topical studies""",
        "EXLBT")
        setConfig("topicEntry", """
        # Last-opened entry for topical studies""",
        "")
        setConfig("locationEntry", """
        # Last-opened entry for bible location""",
        "")
        setConfig("characterEntry", """
        # Last-opened entry for bible character""",
        "")
        setConfig("dictionary", """
        # Last-opened dictionary module""",
        "EAS")
        setConfig("dictionaryEntry", """
        # Last-opened dictionary entry""",
        "")
        setConfig("encyclopedia", """
        # Last-opened encyclopedia module""",
        "ISB")
        setConfig("encyclopediaEntry", """
        # Last-opened encyclopedia entry""",
        "")
        setConfig("docxText", """
        # Last-opened docx text""",
        "")
        setConfig("parseWordDocument", """
        # Parse Word Document content""",
        True)
        setConfig("pdfText", """
        # Last-opened pdf filename""",
        "")
        setConfig("pdfTextPath", """
        # Last-opened pdf file path""",
        "")
        setConfig("dataset", """
        # Last-opened dataset module""",
        "Bible Chronology")
        setConfig("book", """
        # Last-opened book module""",
        "Harmonies_and_Parallels")
        config.help["parallels"] = """
        # Last-opened parallels module"""
        if not hasattr(config, "parallels") or not isinstance(config.parallels, int):
            config.parallels = 2
        config.help["parallelsEntry"] = """
        # Last-opened parallels entry"""
        if not hasattr(config, "parallelsEntry") or not isinstance(config.parallelsEntry, int):
            config.parallelsEntry = 1
        config.help["promises"] = """
        # Last-opened promises module"""
        if not hasattr(config, "promises") or not isinstance(config.promises, int):
            config.promises = 4
        config.help["promisesEntry"] = """
        # Last-opened promises entry"""
        if not hasattr(config, "promisesEntry") or not isinstance(config.promisesEntry, int):
            config.promisesEntry = 1
        setConfig("bookChapter", """
        # Last-opened book chapter""",
        "")
        setConfig("openBookInNewWindow", """
        # Option to open book content on a new window""",
        False)
        setConfig("openPdfViewerInNewWindow", """
        # Option to open PDF viewer on a new window""",
        False)
        setConfig("popoverWindowWidth", """
        # Popover Windows width""",
        640)
        setConfig("popoverWindowHeight", """
        # Popover Windows height""",
        480)
        setConfig("overwriteBookFont", """
        # Option to overwrite font in book modules""",
        True)
        setConfig("overwriteBookFontFamily", """
        # Overwrite book font family""",
        "")
        setConfig("overwriteBookFontSize", """
        # Option to overwrite font size in book modules""",
        True)
        setConfig("overwriteNoteFont", """
        # Option to overwrite font in bible notes""",
        True)
        setConfig("overwriteNoteFontSize", """
        # Option to overwrite font size in bible notes""",
        True)
        setConfig("favouriteBooks", """
        # List of favourite book modules
        # Only the first 10 books are shown on menu bar""",
        ["Harmonies_and_Parallels", "Bible_Promises", "Timelines", "Maps_ABS", "Maps_NET"])
        setConfig("removeHighlightOnExit", """
        # Remove book, note and instant highlights on exit.""",
        True)
        setConfig("bookSearchString", """
        # Last string entered for searching book""",
        "")
        setConfig("noteSearchString", """
        # Last string entered for searching note""",
        "")
        setConfig("thirdDictionary", """
        # Last-opened third-party dictionary""",
        "webster")
        setConfig("thirdDictionaryEntry", """
        # Last-opened third-party dictionary entry""",
        "")
        setConfig("lexicon", """
        # Last-opened lexicon""",
        "ConcordanceBook")
        setConfig("lexiconEntry", """
        # Last-opened lexicon entry""",
        "")
        setConfig("defaultLexiconStrongH", """
        # Default Hebrew lexicon""",
        "TBESH")
        setConfig("defaultLexiconStrongG", """
        # Default Greek lexicon""",
        "TBESG")
        setConfig("defaultLexiconETCBC", """
        # Default lexicon based on ETCBC data""",
        "ConcordanceMorphology")
        setConfig("defaultLexiconLXX", """
        # Default lexicon on LXX words""",
        "LXX")
        setConfig("defaultLexiconGK", """
        # Default lexicon on GK entries""",
        "MCGED")
        setConfig("defaultLexiconLN", """
        # Default lexicon on LN entries""",
        "LN")
        setConfig("maximumHistoryRecord", """
        # Maximum number of history records allowed to be stored""",
        50)
        setConfig("currentRecord", """
        # Indexes of last-opened records""",
        {"main": 0, "study": 0})
        setConfig("history", """
        # History records are kept in config.history""",
        {"external": ["note_editor.uba"], "main": ["BIBLE:::KJV:::Genesis 1:1"], "study": ["BIBLE:::NET:::John 3:16"]})
        setConfig("tabHistory", """
        # Tab history records for startup""",
        {"main": {"0": config.history["main"][-1]}, "study": {"0": config.history["study"][-1]}})
        setConfig("installHistory", """
        # Installed Formatted Bibles""",
        {})
        setConfig("useWebbrowser", """
        # Use webbrowser module to open internal website links instead of opening on Study Window""",
        True)
        setConfig("showInformation", """
        # set show information to True""",
        True)
        config.help["windowStyle"] = """
        # Window Style
        # Availability of window styles depends on the device running UBA."""
        if not hasattr(config, "windowStyle") or not config.windowStyle:
            config.windowStyle = "Fusion"
        setConfig("theme", """
        # Theme (default, dark)""",
        "default")
        setConfig("widgetBackgroundColor", """
        # Widget background color in 'material' menu layout.""",
        "#e7e7e7" if config.theme == "default" else "#2f2f2f")
        setConfig("widgetForegroundColor", """
        # Widget foreground color in 'material' menu layout.""",
        "#483D8B" if config.theme == "default" else "#FFFFE0")
        setConfig("widgetBackgroundColorHover", """
        # Widget background color when a widget is hovered in 'material' menu layout.""",
        "#f8f8a0" if config.theme == "default" else "#545454")
        setConfig("widgetForegroundColorHover", """
        # Widget foreground color when a widget is hovered in 'material' menu layout.""",
        "#483D8B" if config.theme == "default" else "#FFFFE0")
        setConfig("widgetBackgroundColorPressed", """
        # Widget background color when a widget is pressed in 'material' menu layout.""",
        "#d9d9d9" if config.theme == "default" else "#232323")
        setConfig("widgetForegroundColorPressed", """
        # Widget foreground color when a widget is pressed in 'material' menu layout.""",
        "#483D8B" if config.theme == "default" else "#FFFFE0")
        setConfig("maskMaterialIconBackground", """
        # config.maskMaterialIconColor applies to either background or foreground of material icons. 
        # Set True to apply the mask to background. 
        # Set False to apply the mask to foreground.""",
        False)
        config.help["maskMaterialIconColor"] = """
        # Use this color for masking material icons."""
        if not config.maskMaterialIconBackground:
            config.maskMaterialIconColor = config.widgetForegroundColor
        elif not hasattr(config, "maskMaterialIconColor"):
            config.maskMaterialIconColor = "#483D8B" if config.theme == "default" else "#FFFFE0"
        setConfig("lightThemeTextColor", """
        # Text colour displayed on light theme.""",
        "#000000")
        setConfig("darkThemeTextColor", """
        # Text colour displayed on dark theme.""",
        "#ffffff")
        setConfig("lightThemeActiveVerseColor", """
        # Active verse colour displayed on light theme.""",
        "#483D8B")
        setConfig("darkThemeActiveVerseColor", """
        # Active verse colour displayed on dark theme.""",
        "#aaff7f")
        setConfig("qtMaterial", """
        # Apply qt-material theme.""",
        False)
        setConfig("qtMaterialTheme", """
        # qt-material theme
        # qt-material theme is used only qtMaterial is true and qtMaterialTheme is not empty""",
        "")
        setConfig("disableModulesUpdateCheck", """
        # Disable modules update check""",
        True)
        setConfig("markdownifyHeadingStyle", """
        # Specify heading style to work with markdownify
        # Options: ATX, ATX_CLOSED, SETEXT, and UNDERLINED
        # Read more at https://pypi.org/project/markdownify/""",
        "UNDERLINED")
        setConfig("forceGenerateHtml", """
        # Force generate main.html for all pages""",
        False)
        setConfig("enableLogging", """
        # Enable logging""",
        False)
        setConfig("logCommands", """
        # Log commands for debugging""",
        False)
        setConfig("migrateDatabaseBibleNameToDetailsTable", """
        # Migrate Bible name from Verses table to Details table""",
        True)
        setConfig("enableVerseHighlighting", """
        # Verse highlighting functionality""",
        True)
        setConfig("showHighlightMarkers", """
        # Show verse highlight markers""",
        False)
        setConfig("menuLayout", """
        # Menu layout""",
        "material")
        setConfig("useLiteVerseParsing", """
        # Verse parsing method""",
        False)
        setConfig("enablePlugins", """
        # Enable plugins""",
        True)
        setConfig("enableMacros", """
        # Enable macros""",
        False)
        setConfig("startupMacro", """
        # Startup macro""",
        "")
        setConfig("enableGist", """
        # Gist synching""",
        False)
        setConfig("gistToken", """
        # Gist token""",
        '')
        setConfig("clearCommandEntry", """
        # Clear command entry line by default""",
        False)
        setConfig("mutualHighlightMultipleStrongNumber", """
        # This value controls how UBA handles mutual highlighting of single string tagged with multiple Strong's numbers.
        # This value applies when Strong's number bibles are opened with Lexical entries not being displayed.
        # 0 - String is highlighted when one of the Strong's numbers tagged for the string is triggered.
        # 1 - String is highlighted only when the first Strong's number tagged for the string is triggered
        # 2 - String is highlighted only when the last Strong's number tagged for the string is triggered""",
        0)
        # Highlight collections"""
        config.help["highlightCollections"] = """
        # Highlight collection names."""
        if not hasattr(config, "highlightCollections") or len(config.highlightCollections) < 12:
            config.highlightCollections = ["Collection 1", "Collection 2", "Collection 3", "Collection 4", "Collection 5", "Collection 6", "Collection 7", "Collection 8", "Collection 9", "Collection 10", "Collection 11", "Collection 12"]
        config.help["highlightDarkThemeColours"] = """
        # Highlight collection colours displayed on dart theme."""
        if not hasattr(config, "highlightDarkThemeColours") or len(config.highlightDarkThemeColours) < 12:
            config.highlightDarkThemeColours = ["#646400", "#060166", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400"]
        config.help["highlightLightThemeColours"] = """
        # Highlight collection colours displayed on light theme."""
        if not hasattr(config, "highlightLightThemeColours") or len(config.highlightLightThemeColours) < 12:
            config.highlightLightThemeColours = ["#e8e809", "#4ff7fa", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#646400", "#646400"]
        setConfig("menuShortcuts", """
        # Default menu shortcuts""",
        "micron")
        setConfig("enableCaseSensitiveSearch", """
        # Option to enable case-sensitive search.""",
        False)
        setConfig("displayLanguage", """
        # Specify translation language for user interface.""",
        'en_US')
        setConfig("lastAppUpdateCheckDate", """
        # App update check""",
        str(DateUtil.localDateNow()))
        setConfig("daysElapseForNextAppUpdateCheck", """
        # Days elapse for next app update check""",
        '14')
        setConfig("updateWithGitPull", """
        # Update with git pull command""",
        False)
        setConfig("minicontrolWindowWidth", """
        # Specify the width of mini Control panel""",
        450)
        setConfig("minicontrolWindowHeight", """
        # Mini Control window height""",
        400)
        setConfig("refButtonClickAction", """
        # Action of reference button when it is clicked.""",
        "master")
        setConfig("presentationScreenNo", """
        # Specify screen number for presentation features.""",
        -1)
        setConfig("presentationFontSize", """
        # Specify font size for display in presentation.""",
        3.0)
        setConfig("presentationMargin", """
        # Specify margin for display in presentation.""",
        50)
        setConfig("presentationColorOnLightTheme", """
        # Specify background colour for display in presentation with light theme.""",
        "black")
        setConfig("presentationColorOnDarkTheme", """
        # Specify background colour for display in presentation with dark theme.""",
        "magenta")
        setConfig("presentationVerticalPosition", """
        # Presentation vertical position""",
        50)
        setConfig("presentationHorizontalPosition", """
        # Presentation horizontal position""",
        50)
        config.help["hideBlankVerseCompare"] = """
        # {0}""".format(language_en_GB.translation["hideBlankVerseCompare"])
        if not hasattr(config, "hideBlankVerseCompare"):
            config.hideBlankVerseCompare = False
        setConfig("miniBrowserHome", """
        # Home page of mini web browser.""",
        "https://www.youtube.com/")
        config.help["enableMenuUnderline"] = """
        # {0}""".format(language_en_GB.translation["enableMenuUnderline"])
        if not hasattr(config, "enableMenuUnderline"):
            config.enableMenuUnderline = True
        config.help["addOHGBiToMorphologySearch"] = """
        # {0}""".format(language_en_GB.translation["addOHGBiToMorphologySearch"])
        if not hasattr(config, "addOHGBiToMorphologySearch"):
            config.addOHGBiToMorphologySearch = True
        setConfig("maximumOHGBiVersesDisplayedInSearchResult", """
        # Maximum number of OHGBi verses displayed in each search result.""",
        50)
        setConfig("excludeStartupPlugins", """
        # List of disabled startup plugins""",
        [])
        setConfig("excludeMenuPlugins", """
        # List of disabled menu plugins""",
        [])
        setConfig("excludeContextPlugins", """
        # List of disabled context plugins""",
        [])
        setConfig("excludeShutdownPlugins", """
        # List of disabled shutdown plugins""",
        [])
        setConfig("commandTextIfNoSelection", """
        # Context menu features run on command field text if no text is selected.""",
        False)
        config.help["githubAccessToken"] = """
        # Github access token"""
        token = "{0}_{1}_{2}".format('tvguho_cng', '11NNTRMXN0v3X2sTuLF0Yg', 'TNK81tX21MzjexjP4pnqTbV9l1tVADsn54ybj4s6PzKLRQ2IRKMa1whP3O2')
        githubAccessToken = codecs.encode(token, 'rot_13')
        setConfig("githubAccessToken", "githubAccessToken", githubAccessToken)
        setConfig("includeStrictDocTypeInNote", """
        # Include the strict doc type in first line of notes""",
        True)
        setConfig("bibleCollections", """
        # Custom Bible Collections""",
        {})
        setConfig("parseTextConvertNotesToBook", """
        # Parse the text when converting notes to book""",
        True)
        setConfig("parseTextConvertHTMLToBook", """
        # Parse the text when converting HTML to book""",
        False)
        setConfig("displayCmdOutput", """
        # Display output of CMD command""",
        False)
        setConfig("defaultMP3BibleFolder", """
        # Default MP3 Bible folder
        """,
        "default")
        setConfig("disableLoadLastOpenFilesOnStartup", """
        # Disable load last open files on startup
        """,
        False)
        setConfig("disableOpenPopupWindowOnStartup", """
        # Disable open popup windows on startup
        """,
        True)
        setConfig("showMiniKeyboardInMiniControl", """
        # Show mini keyboard in miniControl
        """,
        False)
        setConfig("parseClearSpecialCharacters", """
        # Clear special characters when parsing
        # When set to True, will make parsing take a long time
        """,
        False)

        # Additional configurations
        config.booksFolder = os.path.join(config.marvelData, "books")
        config.commentariesFolder = os.path.join(config.marvelData, "commentaries")
        if config.enableMenuUnderline:
            config.menuUnderline = "&"
        else:
            config.menuUnderline = ""

        setConfig("refreshWindowsAfterSavingNote", """
        # Refresh the windows after saving a note
        """,
        True)

        setConfig("limitWorkspaceFilenameLength", """
        # Limit the workspace filename length to 20 characters
        """,
        True)

        setConfig("enableHttpRemoteErrorRedirection", """
        # Go to redirection page if error in http-server
        """,
        False)

        setConfig("overrideCompareToUseAllTexts", """
        # Override verse comparison to compare all Bible texts instead of favourite texts
        """,
        False)

        setConfig("translate_api_url", """
        # Translation service API URL
        """,
        "https://translate.otweb.com")

        setConfig("translate_api_key", """
        # Translation service API key
        """,
          "")

        patFile = os.path.join("secrets", "github", "pat.txt")
        if os.path.exists(patFile):
            with open(patFile) as file:
                pat = file.readline().strip()
                if pat:
                    config.githubAccessToken = pat
                    logger = logging.getLogger('uba')
                    logger.info(f"Using {patFile}")

        setConfig("apiServerClientId", """
        # API Server Client ID
        """,
        '')

        setConfig("apiServerClientSecret", """
        # API Server Client Secret
        """,
        '')

        ConfigUtil.loadColorConfig()

    # Save configurations on exit
    @staticmethod
    def save():
        if config.openBibleInMainViewOnly == True and not config.noQt:
            config.studyText = config.studyTextTemp
        if config.removeHighlightOnExit:
            config.bookSearchString = ""
            config.noteSearchString = ""
            #config.instantHighlightString = ""
        configFile = os.path.join(config.packageDir, "config.py")
        with open(configFile, "w", encoding="utf-8") as fileObj:
            for name in config.help.keys():
                try:
                    value = eval(f"config.{name}")
                    fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
                except:
                    print(name)
            if hasattr(config, "translationLanguage"):
                fileObj.write("{0} = {1}\n".format("translationLanguage", pprint.pformat(config.translationLanguage)))
            if hasattr(config, "iModeSplitterSizes"):
                fileObj.write("{0} = {1}\n".format("iModeSplitterSizes", pprint.pformat(config.iModeSplitterSizes)))
            if hasattr(config, "pModeSplitterSizes"):
                fileObj.write("{0} = {1}\n".format("pModeSplitterSizes", pprint.pformat(config.pModeSplitterSizes)))
            # print("A copy of configurations is saved in file 'config.py'!")
        # backup
        try:
            backupFile = os.path.join(config.ubaUserDir, "config.py.bk")
            copy(configFile, backupFile)
        except:
            pass

    @staticmethod
    def getColorConfigFilename():
        fileName = os.path.join(config.packageDir, "plugins", "config", f"{config.menuLayout}_{config.theme}.color")
        return fileName

    @staticmethod
    def loadColorConfig(fileName=None):
        if not fileName:
            fileName = ConfigUtil.getColorConfigFilename()
        if os.path.exists(fileName):
            with open(fileName, "r") as f:
                settings = f.read()
                exec(settings)
