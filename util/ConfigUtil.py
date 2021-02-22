import os, pprint
from platform import system

import config


class ConfigUtil:

    @staticmethod
    def messageFeatureNotEnabled(feature, module):
        print("Optional feature '{0}'is not enabled.  To enable it, install python package '{1}' first, by running 'pip3 install {1}' with terminal.".format(feature, module))

    @staticmethod
    def setup():

        # Check current version
        with open("UniqueBibleAppVersion.txt", "r", encoding="utf-8") as fileObject:
            text = fileObject.read()
            current_version = float(text)

        # update current version in config
        if not hasattr(config, "version") or current_version > config.version:
            config.version = current_version

        # Default settings for configurations:

        # Developer option
        if not hasattr(config, "developer"):
            config.developer = False
        # Personal google api key for display of google maps
        if not hasattr(config, "myGoogleApiKey"):
            config.myGoogleApiKey = ""
        # Options to always display static maps even "myGoogleApiKey" is not empty: True / False
        if not hasattr(config, "alwaysDisplayStaticMaps"):
            if config.myGoogleApiKey:
                config.alwaysDisplayStaticMaps = False
            else:
                config.alwaysDisplayStaticMaps = True
        # IBM Watson service api key
        if not hasattr(config, "myIBMWatsonApikey"):
            config.myIBMWatsonApikey = ""
        if not hasattr(config, "myIBMWatsonUrl"):
            config.myIBMWatsonUrl = ""
        if not hasattr(config, "myIBMWatsonVersion"):
            config.myIBMWatsonVersion = "2018-05-01"
        # Options to use control panel: True / False
        # This feature is created for use in church settings.
        # If True, users can use an additional command field, in an additional window, to control the content being displayed, even the main window of UniqueBible.app is displayed on extended screen.
        if not hasattr(config, "showControlPanelOnStartup"):
            config.showControlPanelOnStartup = False
        if not hasattr(config, "preferControlPanelForCommandLineEntry"):
            config.preferControlPanelForCommandLineEntry = False
        if not hasattr(config, "closeControlPanelAfterRunningCommand"):
            config.closeControlPanelAfterRunningCommand = True
        if not hasattr(config, "addBreakAfterTheFirstToolBar"):
            config.addBreakAfterTheFirstToolBar = True
        if not hasattr(config, "addBreakBeforeTheLastToolBar"):
            config.addBreakBeforeTheLastToolBar = False
        # Configure verse number single-click & double-click action
        # available options: "_noAction", "_cp0", "_cp1", "_cp2", "_cp3", "_cp4", "COMPARE", "CROSSREFERENCE", "TSKE", "TRANSLATION", "DISCOURSE", "WORDS", "COMBO", "INDEX", "COMMENTARY", "_menu"
        # corresponding translation: "noAction", "cp0", "cp1", "cp2", "cp3", "cp4", "menu4_compareAll", "menu4_crossRef", "menu4_tske", "menu4_traslations", "menu4_discourse", "menu4_words", "menu4_tdw", "menu4_indexes", "menu4_commentary", "classicMenu"
        if not hasattr(config, "verseNoSingleClickAction"):
            config.verseNoSingleClickAction = "INDEX"
        if not hasattr(config, "verseNoDoubleClickAction"):
            config.verseNoDoubleClickAction = "_cp0"
        # Start full-screen on Linux os
        if not hasattr(config, "linuxStartFullScreen"):
            # Check if UniqueBible.app is running on Chrome OS:
            if (os.path.exists("/mnt/chromeos/")):
                config.linuxStartFullScreen = True
            else:
                config.linuxStartFullScreen = False
        # Show text-to-speech feature on Linux os
        if not hasattr(config, "showTtsOnLinux"):
            # Check if UniqueBible.app is running on Chrome OS:
            if (os.path.exists("/mnt/chromeos/")):
                config.showTtsOnLinux = True
            else:
                config.showTtsOnLinux = False
        # Use espeak for text-to-speech feature instead of built-in qt tts engine
        # espeak is a text-to-speech tool that can run offline
        # To check for available langauge codes, run on terminal: espeak --voices
        # Notes on espeak setup is available at: https://github.com/eliranwong/ChromeOSLinux/blob/main/multimedia/espeak.md
        # If you need text-to-speech features to work on Chinese / Russian text, you may read the link above.
        if not hasattr(config, "espeak"):
            # Check if UniqueBible.app is running on Chrome OS:
            if (os.path.exists("/mnt/chromeos/")):
                config.espeak = True
            else:
                config.espeak = False
        # espeak speed
        if not hasattr(config, "espeakSpeed"):
            config.espeakSpeed = 160
        # qtts speed
        if not hasattr(config, "qttsSpeed"):
            config.qttsSpeed = 0.0
        # tts language options
        if not hasattr(config, "ttsDefaultLangauge"):
            config.ttsDefaultLangauge = "en"
        if not hasattr(config, "ttsChineseAlwaysCantonese"):
            config.ttsChineseAlwaysCantonese = False
        if not hasattr(config, "ttsChineseAlwaysMandarin"):
            config.ttsChineseAlwaysMandarin = False
        if not hasattr(config, "ttsEnglishAlwaysUS"):
            config.ttsEnglishAlwaysUS = False
        if not hasattr(config, "ttsEnglishAlwaysUK"):
            config.ttsEnglishAlwaysUK = False
        # Options to use ibus as input method: True / False
        # This option may be useful on some Linux systems, where qt4 and qt5 applications use different input method variables.
        if not hasattr(config, "ibus"):
            config.ibus = False
        # This option may be useful on some Linux systems, where qt4 and qt5 applications use different input method variables.
        if not hasattr(config, "fcitx"):
            config.fcitx = False
        # Options to use built-in virtual keyboards: True / False
        if not hasattr(config, "virtualKeyboard"):
            config.virtualKeyboard = False
        # Specify the "open" command on Windows
        if not hasattr(config, "openWindows"):
            config.openWindows = "start"
        # Specify the "open" command on macOS
        if not hasattr(config, "openMacos"):
            config.openMacos = "open"
        # Specify the "open" command on Linux
        if not hasattr(config, "openLinux"):
            config.openLinux = "xdg-open"
        # Specify the command to open pdf file on Linux
        if not hasattr(config, "openLinuxPdf"):
            config.openLinuxPdf = "xdg-open"
        # Specify the folder path of resources
        if not hasattr(config, "marvelData"):
            config.marvelData = "marvelData"
        # Specify the folder path of music files
        if not hasattr(config, "musicFolder"):
            config.musicFolder = "music"
        # Specify the folder path of video files
        if not hasattr(config, "videoFolder"):
            config.videoFolder = "video"
        # Specify the file path of note file on bible chapters and verses
        if not hasattr(config, "bibleNotes"):
            config.bibleNotes = "note.sqlite"
        # Specify the number of tabs for bible reading and workspace
        if not hasattr(config, "numberOfTab"):
            config.numberOfTab = 5
        # Options to open Bible Window's content in the tab next to the current one: True / False
        if not hasattr(config, "openBibleWindowContentOnNextTab"):
            config.openBibleWindowContentOnNextTab = False
        # Options to open Study Window's content in the tab next to the current one: True / False
        if not hasattr(config, "openStudyWindowContentOnNextTab"):
            config.openStudyWindowContentOnNextTab = True
        # Options to convert all bible book abbreviations to standard ones: YES / NO
        if not hasattr(config, "parserStandarisation"):
            config.parserStandarisation = "NO"
        # Options of language of book abbreviations: ENG / TC / SC
        if not hasattr(config, "standardAbbreviation"):
            config.standardAbbreviation = "ENG"
        # Option to set a customised language for google-translate
        # References: https://cloud.google.com/translate/docs/languages
        # Use gui "Set my Language" dialog, from menu bar, to set "userLanguage".
        if not hasattr(config, "userLanguage"):
            config.userLanguage = ""
        # Option to use interface translated into userLanguage: True / False
        if not hasattr(config, "userLanguageInterface"):
            config.userLanguageInterface = False
        # Option to copy automatically to clipboard the result of accessing Google Translate: True / False
        if not hasattr(config, "autoCopyTranslateResult"):
            config.autoCopyTranslateResult = True
        # Option to copy automatically to clipboard the output of Chinese pinyin conversion: True / False
        if not hasattr(config, "autoCopyChinesePinyinOutput"):
            config.autoCopyChinesePinyinOutput = True
        # Option to display verse number in a range of verses: True / False
        # e.g. Try entering in command field "Ps 23:1; Ps 23:1-3; Ps 23:1-24:3"
        if not hasattr(config, "showVerseNumbersInRange"):
            config.showVerseNumbersInRange = True
        # Options to open chapter / verse note on Study Window after saving: True / False
        if not hasattr(config, "openBibleNoteAfterSave"):
            config.openBibleNoteAfterSave = False
        # Options to export all embedded images displayed on Study Window: True / False
        if not hasattr(config, "exportEmbeddedImages"):
            config.exportEmbeddedImages = True
        # Options to add open image action with a single click: True / False
        if not hasattr(config, "clickToOpenImage"):
            config.clickToOpenImage = True
        # Options to use landscape mode: True / False
        if not hasattr(config, "landscapeMode"):
            config.landscapeMode = True
        # Options for NOT displaying any toolbars on startup: True / False
        if not hasattr(config, "noToolBar"):
            config.noToolBar = False
        # Options to display the top toolbar only, with all other toolbars hidden: True / False
        if not hasattr(config, "topToolBarOnly"):
            config.topToolBarOnly = False
        # Options to use large sets of icons: True / False
        if not hasattr(config, "toolBarIconFullSize"):
            config.toolBarIconFullSize = False
        # Options on parallel mode: 0, 1, 2, 3
        if not hasattr(config, "parallelMode"):
            config.parallelMode = 1
        # Options to display the window showing instant information: 0, 1
        if not hasattr(config, "instantMode"):
            config.instantMode = 1
        # Options to trigger instant information: True / False
        if not hasattr(config, "instantInformationEnabled"):
            config.instantInformationEnabled = True
        # Default font size of content in main window and workspace
        if not hasattr(config, "fontSize"):
            config.fontSize = 17
        # Default font
        if not hasattr(config, "font"):
            config.font = ""
        # Default Chinese font
        if not hasattr(config, "fontChinese"):
            config.fontChinese = ""
        # Default font size of content in note editor
        if not hasattr(config, "noteEditorFontSize"):
            config.noteEditorFontSize = 14
        # Default: False: Open bible note on Study Window afer it is edited with Note Editor.
        # Bible note is opened when Note editor is closed.
        if not hasattr(config, "openBibleNoteAfterEditing"):
            config.openBibleNoteAfterEditing = False
        # Show Note Editor's style toolbar by default
        if not hasattr(config, "hideNoteEditorStyleToolbar"):
            config.hideNoteEditorStyleToolbar = False
        # Hide Note Editor's text utility by default
        if not hasattr(config, "hideNoteEditorTextUtility"):
            config.hideNoteEditorTextUtility = True
        # Options to display bibles in formatted layout or paragraphs: True / False
        # "False" here means displaying bible verse in plain format, with each one on a single line.
        if not hasattr(config, "readFormattedBibles"):
            config.readFormattedBibles = True
        # Options to add sub-headings when "readFormattedBibles" is set to "False": True / False
        if not hasattr(config, "addTitleToPlainChapter"):
            config.addTitleToPlainChapter = True
        # Options to hide lexical entries or Strong's numbers: True / False
        if not hasattr(config, "hideLexicalEntryInBible"):
            config.hideLexicalEntryInBible = False
        # Import setting - add a line break after each verse: True / False
        if not hasattr(config, "importAddVerseLinebreak"):
            config.importAddVerseLinebreak = False
        # Import setting - keep Strong's number for search: True / False
        if not hasattr(config, "importDoNotStripStrongNo"):
            config.importDoNotStripStrongNo = False
        # Import setting - keep morphology codes for search: True / False
        if not hasattr(config, "importDoNotStripMorphCode"):
            config.importDoNotStripMorphCode = False
        # Import setting - import text in right-to-left direction: True / False
        if not hasattr(config, "importRtlOT"):
            config.importRtlOT = False
        # Import setting - import interlinear text: True / False
        if not hasattr(config, "importInterlinear"):
            config.importInterlinear = False
        # List of modules, which contains Hebrew / Greek texts
        if not hasattr(config, "originalTexts"):
            config.originalTexts = ['original', 'MOB', 'MAB', 'MTB', 'MIB', 'MPB', 'OHGB', 'OHGBi', 'LXX', 'LXX1',
                                    'LXX1i',
                                    'LXX2', 'LXX2i']
        # List of modules, which contains right-to-left texts on old testament
        if not hasattr(config, "rtlTexts"):
            config.rtlTexts = ["original", "MOB", "MAB", "MIB", "MPB", "OHGB", "OHGBi"]
        # Open bible references on main window instead of workspace: Ture / False
        if not hasattr(config, "openBibleInMainViewOnly"):
            config.openBibleInMainViewOnly = False
        # Last-opened bible version and passage to be displayed on main window
        if not hasattr(config, "mainText"):
            config.mainText = "KJV"
        if not hasattr(config, "mainB"):
            config.mainB = 1
        if not hasattr(config, "mainC"):
            config.mainC = 1
        if not hasattr(config, "mainV"):
            config.mainV = 1
        # Last-opened bible version and passage to be displayed on workspace
        if not hasattr(config, "studyText"):
            config.studyText = "NET"
        if not hasattr(config, "studyB"):
            config.studyB = 43
        if not hasattr(config, "studyC"):
            config.studyC = 3
        if not hasattr(config, "studyV"):
            config.studyV = 16
        # Search Bible Mode
        # Accept value: 0-4
        # Correspond to ("SEARCH", "SHOWSEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH")
        if not hasattr(config, "bibleSearchMode"):
            config.bibleSearchMode = 0
        # Set your favourite version here
        if not hasattr(config, "favouriteBible"):
            config.favouriteBible = "OHGBi"
        # Options to display "favouriteBible" together with the main version for reading multiple references: True / False
        if not hasattr(config, "addFavouriteToMultiRef"):
            config.addFavouriteToMultiRef = False
        # Options to enforce comparison / parallel: True / False
        # When it is enabled after comparison / parallel feature is loaded once, subsequence entries of bible references will be treated as launching comparison / parallel even COMPARE::: or PARALLEL::: keywords is not used.
        # Please note that change in bible version for chapter reading is ignored when this option is enabled.
        # This feature is accessible via a left toolbar button, located under the "Comparison / Parallel Reading / Difference" button.
        if not hasattr(config, "enforceCompareParallel"):
            config.enforceCompareParallel = False
        # Options to show note indicator on bible chapter: True / False
        if not hasattr(config, "showNoteIndicatorOnBibleChapter"):
            config.showNoteIndicatorOnBibleChapter = True
        # Options sync Study Window's with changes verse references on Main Window: True / False
        if not hasattr(config, "syncStudyWindowBibleWithMainWindow"):
            config.syncStudyWindowBibleWithMainWindow = False
        # Options sync commentary with changes verse references on Main Window: True / False
        if not hasattr(config, "syncCommentaryWithMainWindow"):
            config.syncCommentaryWithMainWindow = False
        # Last-opened commentary text and passage
        if not hasattr(config, "commentaryText"):
            config.commentaryText = "CBSC"
        if not hasattr(config, "commentaryB"):
            config.commentaryB = 43
        if not hasattr(config, "commentaryC"):
            config.commentaryC = 3
        if not hasattr(config, "commentaryV"):
            config.commentaryV = 16
        # Last-opened module for topical studies
        if not hasattr(config, "topic"):
            config.topic = "EXLBT"
        # Last-opened dictionary module
        if not hasattr(config, "dictionary"):
            config.dictionary = "EAS"
        # Last-opened encyclopedia module
        if not hasattr(config, "encyclopedia"):
            config.encyclopedia = "ISB"
        # Last-opened book module
        if not hasattr(config, "book"):
            config.book = "Harmonies_and_Parallels"
        # Last-opened book chapter
        if not hasattr(config, "bookChapter"):
            config.bookChapter = "03 - Gospels I"
        # Option to open book content on a new window
        if not hasattr(config, "bookOnNewWindow"):
            config.bookOnNewWindow = False
        # Option to overwrite font in book modules
        if not hasattr(config, "overwriteBookFont"):
            config.overwriteBookFont = True
        # Option to overwrite font size in book modules
        if not hasattr(config, "overwriteBookFontSize"):
            config.overwriteBookFontSize = True
        # Option to overwrite font in bible notes
        if not hasattr(config, "overwriteNoteFont"):
            config.overwriteNoteFont = True
        # Option to overwrite font size in bible notes
        if not hasattr(config, "overwriteNoteFontSize"):
            config.overwriteNoteFontSize = True
        # List of favourite book modules
        # Only the first 10 books are shown on menu bar
        if not hasattr(config, "favouriteBooks"):
            config.favouriteBooks = ["Harmonies_and_Parallels", "Bible_Promises", "Timelines", "Maps_ABS", "Maps_NET"]
        # Last string entered for searching book
        if not hasattr(config, "bookSearchString"):
            config.bookSearchString = ""
        # Last string entered for searching note
        if not hasattr(config, "noteSearchString"):
            config.noteSearchString = ""
        # Last-opened third-party dictionary
        if not hasattr(config, "thirdDictionary"):
            config.thirdDictionary = "webster"
        # Last-opened lexicon
        if not hasattr(config, "lexicon"):
            config.lexicon = "ConcordanceBook"
        # Default Hebrew lexicon
        if not hasattr(config, "defaultLexiconStrongH"):
            config.defaultLexiconStrongH = "TBESH"
        # Default Greek lexicon
        if not hasattr(config, "defaultLexiconStrongG"):
            config.defaultLexiconStrongG = "TBESG"
        # Default lexicon based on ETCBC data
        if not hasattr(config, "defaultLexiconETCBC"):
            config.defaultLexiconETCBC = "ConcordanceMorphology"
        # Default lexicon on LXX words
        if not hasattr(config, "defaultLexiconLXX"):
            config.defaultLexiconLXX = "LXX"
        # Default lexicon on GK entries
        if not hasattr(config, "defaultLexiconGK"):
            config.defaultLexiconGK = "MCGED"
        # Default lexicon on LN entries
        if not hasattr(config, "defaultLexiconLN"):
            config.defaultLexiconLN = "LN"
        # Maximum number of history records allowed to be stored
        if not hasattr(config, "historyRecordAllowed"):
            config.historyRecordAllowed = 50
        # Indexes of last-opened records
        if not hasattr(config, "currentRecord"):
            config.currentRecord = {"main": 0, "study": 0}
        # History records are kept in config.history
        if not hasattr(config, "history"):
            config.history = {"external": ["note_editor.uba"], "main": ["BIBLE:::KJV:::Genesis 1:1"],
                              "study": ["BIBLE:::NET:::John 3:16"]}
        # Installed Formatted Bibles
        if not hasattr(config, "installHistory"):
            config.installHistory = {}
        # for checking if note editor is currently opened
        config.noteOpened = False
        # set show information to True
        if not hasattr(config, "showInformation"):
            config.showInformation = True
        # Window Style
        # Availability of window styles depends on device
        if not hasattr(config, "windowStyle"):
            config.windowStyle = ""
        # Theme (default, dark)
        if not hasattr(config, "theme"):
            config.theme = "default"
        # qt-material theme
        # qt-material theme is used only qtMaterial is true and qtMaterialTheme is not empty
        if not hasattr(config, "qtMaterial"):
            config.qtMaterial = False
        if not hasattr(config, "qtMaterialTheme"):
            config.qtMaterialTheme = ""
        # Disable modules update check
        if not hasattr(config, "disableModulesUpdateCheck"):
            config.disableModulesUpdateCheck = True
        # Enable Copy HTML in popup menu
        if not hasattr(config, "enableCopyHtmlCommand"):
            config.enableCopyHtmlCommand = False
        # Force generate main.html for all pages
        if not hasattr(config, "forceGenerateHtml"):
            config.forceGenerateHtml = False
        # Enable logging
        if not hasattr(config, "enableLogging"):
            config.enableLogging = False
        # Log commands for debugging
        if not hasattr(config, "logCommands"):
            config.logCommands = False
        # Migrate Bible name from Verses table to Details table
        if not hasattr(config, "migrateDatabaseBibleNameToDetailsTable"):
            config.migrateDatabaseBibleNameToDetailsTable = True
        # Verse highlighting functionality
        if not hasattr(config, "enableVerseHighlighting"):
            config.enableVerseHighlighting = False
        # Show verse highlight markers
        if not hasattr(config, "showHighlightMarkers"):
            config.showHighlightMarkers = True
        # Menu layout
        if not hasattr(config, "menuLayout"):
            config.menuLayout = "focus"
        # Verse parsing method
        if not hasattr(config, "useFastVerseParsing"):
            config.useFastVerseParsing = False
        # Enable macros
        if not hasattr(config, "enableMacros"):
            config.enableMacros = False
        # Startup macro
        if not hasattr(config, "startupMacro"):
            config.startupMacro = ""
        # Gist synching
        if not hasattr(config, "enableGist"):
            config.enableGist = False
        if not hasattr(config, "gistToken"):
            config.gistToken = ''
        # Clear command entry line by default
        if not hasattr(config, "clearCommandEntry"):
            config.clearCommandEntry = False
        # Highlight collections
        if not hasattr(config, "highlightCollections") or len(config.highlightCollections) < 12:
            config.highlightCollections = ["Collection 1", "Collection 2", "Collection 3", "Collection 4", "Collection 5", "Collection 6", "Collection 7", "Collection 8", "Collection 9", "Collection 10", "Collection 11", "Collection 12"]
        if not hasattr(config, "highlightDarkThemeColours") or len(config.highlightDarkThemeColours) < 12:
            config.highlightDarkThemeColours = ["#646400", "#060166", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400"]
        if not hasattr(config, "highlightLightThemeColours") or len(config.highlightLightThemeColours) < 12:
            config.highlightLightThemeColours = ["#e8e809", "#4ff7fa", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#646400", "#646400"]
        # Default menu shortcuts
        if not hasattr(config, "menuShortcuts"):
            config.menuShortcuts = "micron"
        # Option to use flags=re.IGNORECASE with regular expression for searching bible
        # flags=re.IGNORECASE will be applied only if config.regexCaseSensitive is set to False
        if not hasattr(config, "regexCaseSensitive"):
            config.regexCaseSensitive = False
        if not hasattr(config, "displayLanguage"):
            config.displayLanguage = 'en_US'

        # Temporary configurations
        # Their values are not saved on exit.
        if not hasattr(config, "controlPanel"):
            config.controlPanel = False
        if not hasattr(config, "miniControl"):
            config.miniControl = False
        if not hasattr(config, "tempRecord"):
            config.tempRecord = ""
        if not hasattr(config, "isDownloading"):
            config.isDownloading = False
        if not hasattr(config, "noStudyBibleToolbar"):
            config.noStudyBibleToolbar = False

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
        #    ConfigUtil.messageFeatureNotEnabled("Conversion between traditional Chinese and simplified Chinese", "opencc")

        # [Optional] Chinese feature - pypinyin
        # It translates Chinese characters into pinyin.
        # To enable functions working with "pypinyin", install python package "pypinyin" first, e.g. pip3 install pypinyin.
        try:
            from pypinyin import pinyin
            config.pinyinSupport = True
        except:
            config.pinyinSupport = False
            ConfigUtil.messageFeatureNotEnabled("Translate Chinese words into pinyin", "pypinyin")

        # [Optional] Gist-syncing notes
        if config.enableGist:
            try:
                from github import Github, InputFileContent
            except:
                config.enableGist = False
                ConfigUtil.messageFeatureNotEnabled("Gist-synching notes across devices", "pygithub")

        # Import modules for developer
        if config.developer:
            # import exlbl
            pass

    # Save configurations on exit
    @staticmethod
    def save():
        config.bookSearchString = ""
        config.noteSearchString = ""
        configs = (
            # ("version", config.version),
            ("developer", config.developer),
            ("myGoogleApiKey", config.myGoogleApiKey),
            ("alwaysDisplayStaticMaps", config.alwaysDisplayStaticMaps),
            ("myIBMWatsonApikey", config.myIBMWatsonApikey),
            ("myIBMWatsonUrl", config.myIBMWatsonUrl),
            ("myIBMWatsonVersion", config.myIBMWatsonVersion),
            ("openWindows", config.openWindows),
            ("openMacos", config.openMacos),
            ("openLinux", config.openLinux),
            ("openLinuxPdf", config.openLinuxPdf),
            ("linuxStartFullScreen", config.linuxStartFullScreen),
            ("showTtsOnLinux", config.showTtsOnLinux),
            ("espeak", config.espeak),
            ("espeakSpeed", config.espeakSpeed),
            ("qttsSpeed", config.qttsSpeed),
            ("ttsDefaultLangauge", config.ttsDefaultLangauge),
            ("ttsChineseAlwaysCantonese", config.ttsChineseAlwaysCantonese),
            ("ttsChineseAlwaysMandarin", config.ttsChineseAlwaysMandarin),
            ("ttsEnglishAlwaysUS", config.ttsEnglishAlwaysUS),
            ("ttsEnglishAlwaysUK", config.ttsEnglishAlwaysUK),
            ("ibus", config.ibus),
            ("fcitx", config.fcitx),
            ("virtualKeyboard", config.virtualKeyboard),
            ("marvelData", config.marvelData),
            ("musicFolder", config.musicFolder),
            ("videoFolder", config.videoFolder),
            ("bibleNotes", config.bibleNotes),
            ("numberOfTab", config.numberOfTab),
            ("openBibleWindowContentOnNextTab", config.openBibleWindowContentOnNextTab),
            ("openStudyWindowContentOnNextTab", config.openStudyWindowContentOnNextTab),
            ("parserStandarisation", config.parserStandarisation),
            ("standardAbbreviation", config.standardAbbreviation),
            ("userLanguage", config.userLanguage),
            ("userLanguageInterface", config.userLanguageInterface),
            ("autoCopyTranslateResult", config.autoCopyTranslateResult),
            ("autoCopyChinesePinyinOutput", config.autoCopyChinesePinyinOutput),
            ("showVerseNumbersInRange", config.showVerseNumbersInRange),
            ("openBibleNoteAfterSave", config.openBibleNoteAfterSave),
            ("exportEmbeddedImages", config.exportEmbeddedImages),
            ("clickToOpenImage", config.clickToOpenImage),
            ("landscapeMode", config.landscapeMode),
            ("noToolBar", config.noToolBar),
            ("topToolBarOnly", config.topToolBarOnly),
            ("toolBarIconFullSize", config.toolBarIconFullSize),
            ("parallelMode", config.parallelMode),
            ("instantMode", config.instantMode),
            ("instantInformationEnabled", config.instantInformationEnabled),
            ("fontSize", config.fontSize),
            ("font", config.font),
            ("fontChinese", config.fontChinese),
            ("noteEditorFontSize", config.noteEditorFontSize),
            ("hideNoteEditorStyleToolbar", config.hideNoteEditorStyleToolbar),
            ("hideNoteEditorTextUtility", config.hideNoteEditorTextUtility),
            ("readFormattedBibles", config.readFormattedBibles),
            ("addTitleToPlainChapter", config.addTitleToPlainChapter),
            ("hideLexicalEntryInBible", config.hideLexicalEntryInBible),
            ("importDoNotStripStrongNo", config.importDoNotStripStrongNo),
            ("importDoNotStripMorphCode", config.importDoNotStripMorphCode),
            ("importAddVerseLinebreak", config.importAddVerseLinebreak),
            ("importRtlOT", config.importRtlOT),
            ("importInterlinear", config.importInterlinear),
            ("originalTexts", config.originalTexts),
            ("rtlTexts", config.rtlTexts),
            ("openBibleInMainViewOnly", config.openBibleInMainViewOnly),
            ("mainText", config.mainText),
            ("mainB", config.mainB),
            ("mainC", config.mainC),
            ("mainV", config.mainV),
            ("favouriteBible", config.favouriteBible),
            ("addFavouriteToMultiRef", config.addFavouriteToMultiRef),
            ("showNoteIndicatorOnBibleChapter", config.showNoteIndicatorOnBibleChapter),
            ("enforceCompareParallel", config.enforceCompareParallel),
            ("syncStudyWindowBibleWithMainWindow", config.syncStudyWindowBibleWithMainWindow),
            ("syncCommentaryWithMainWindow", config.syncCommentaryWithMainWindow),
            ("studyText", config.studyText),
            ("studyB", config.studyB),
            ("studyC", config.studyC),
            ("studyV", config.studyV),
            ("bibleSearchMode", config.bibleSearchMode),
            ("regexCaseSensitive", config.regexCaseSensitive),
            ("commentaryText", config.commentaryText),
            ("commentaryB", config.commentaryB),
            ("commentaryC", config.commentaryC),
            ("commentaryV", config.commentaryV),
            ("topic", config.topic),
            ("dictionary", config.dictionary),
            ("encyclopedia", config.encyclopedia),
            ("book", config.book),
            ("bookChapter", config.bookChapter),
            ("bookOnNewWindow", config.bookOnNewWindow),
            ("verseNoSingleClickAction", config.verseNoSingleClickAction),
            ("verseNoDoubleClickAction", config.verseNoDoubleClickAction),
            ("overwriteBookFont", config.overwriteBookFont),
            ("overwriteBookFontSize", config.overwriteBookFontSize),
            ("overwriteNoteFont", config.overwriteNoteFont),
            ("overwriteNoteFontSize", config.overwriteNoteFontSize),
            ("favouriteBooks", config.favouriteBooks),
            ("bookSearchString", config.bookSearchString),
            ("noteSearchString", config.noteSearchString),
            ("thirdDictionary", config.thirdDictionary),
            ("lexicon", config.lexicon),
            ("defaultLexiconStrongH", config.defaultLexiconStrongH),
            ("defaultLexiconStrongG", config.defaultLexiconStrongG),
            ("defaultLexiconETCBC", config.defaultLexiconETCBC),
            ("defaultLexiconLXX", config.defaultLexiconLXX),
            ("defaultLexiconGK", config.defaultLexiconGK),
            ("defaultLexiconLN", config.defaultLexiconLN),
            ("showInformation", config.showInformation),
            ("historyRecordAllowed", config.historyRecordAllowed),
            ("currentRecord", {'main': 0, 'study': 0}),
            ("history", config.history),
            ("installHistory", config.installHistory),
            ("windowStyle", config.windowStyle),
            ("theme", config.theme),
            ("qtMaterial", config.qtMaterial),
            ("qtMaterialTheme", config.qtMaterialTheme),
            ("disableModulesUpdateCheck", config.disableModulesUpdateCheck),
            ("enableCopyHtmlCommand", config.enableCopyHtmlCommand),
            ("showControlPanelOnStartup", config.showControlPanelOnStartup),
            ("preferControlPanelForCommandLineEntry", config.preferControlPanelForCommandLineEntry),
            ("closeControlPanelAfterRunningCommand", config.closeControlPanelAfterRunningCommand),
            ("addBreakAfterTheFirstToolBar", config.addBreakAfterTheFirstToolBar),
            ("addBreakBeforeTheLastToolBar", config.addBreakBeforeTheLastToolBar),
            ("forceGenerateHtml", config.forceGenerateHtml),
            ("enableLogging", config.enableLogging),
            ("logCommands", config.logCommands),
            ("enableVerseHighlighting", config.enableVerseHighlighting),
            ("migrateDatabaseBibleNameToDetailsTable", config.migrateDatabaseBibleNameToDetailsTable),
            ("menuLayout", config.menuLayout),
            ("showHighlightMarkers", config.showHighlightMarkers),
            ("useFastVerseParsing", config.useFastVerseParsing),
            ("enableMacros", config.enableMacros),
            ("startupMacro", config.startupMacro),
            ("enableGist", config.enableGist),
            ("gistToken", config.gistToken),
            ("clearCommandEntry", config.clearCommandEntry),
            ("highlightCollections", config.highlightCollections),
            ("highlightLightThemeColours", config.highlightLightThemeColours),
            ("highlightDarkThemeColours", config.highlightDarkThemeColours),
            ("showHighlightMarkers", config.showHighlightMarkers),
            ("menuShortcuts", config.menuShortcuts),
            ("displayLanguage", config.displayLanguage)
        )
        with open("config.py", "w", encoding="utf-8") as fileObj:
            for name, value in configs:
                fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))
            if hasattr(config, "translationLanguage"):
                fileObj.write("{0} = {1}\n".format("translationLanguage", pprint.pformat(config.translationLanguage)))
            if hasattr(config, "iModeSplitterSizes"):
                fileObj.write("{0} = {1}\n".format("iModeSplitterSizes", pprint.pformat(config.iModeSplitterSizes)))
            if hasattr(config, "pModeSplitterSizes"):
                fileObj.write("{0} = {1}\n".format("pModeSplitterSizes", pprint.pformat(config.pModeSplitterSizes)))

