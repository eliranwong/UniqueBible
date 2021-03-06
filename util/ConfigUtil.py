import codecs
import os, pprint, config
from platform import system
from util.DateUtil import DateUtil


class ConfigUtil:

    @staticmethod
    def setup():

        # Check current version
        with open("UniqueBibleAppVersion.txt", "r", encoding="utf-8") as fileObject:
            text = fileObject.read()
            current_version = float(text)

        # update current version in config"""
        if not hasattr(config, "version") or current_version > config.version:
            config.version = current_version

        # Default settings for configurations:

        # A dictionary entry to hold information about individual attributes
        # It is created to help documentation.
        config.help = {}

        config.help["developer"] = """
        # Option to enable developer menu and options"""
        if not hasattr(config, "developer"):
            config.developer = False
        if not hasattr(config, "referenceTranslation"):
            config.referenceTranslation = "en_US"
        if not hasattr(config, "workingTranslation"):
            config.workingTranslation = "en_US"
        config.help["myGoogleApiKey"] = """
        # Personal google api key for display of google maps"""
        if not hasattr(config, "myGoogleApiKey"):
            config.myGoogleApiKey = ""
        config.help["alwaysDisplayStaticMaps"] = """
        # Options to always display static maps even "myGoogleApiKey" is not empty: True / False"""
        if not hasattr(config, "alwaysDisplayStaticMaps"):
            if config.myGoogleApiKey:
                config.alwaysDisplayStaticMaps = False
            else:
                config.alwaysDisplayStaticMaps = True
        config.help["myIBMWatsonApikey"] = """
        # IBM Watson service api key"""
        if not hasattr(config, "myIBMWatsonApikey"):
            config.myIBMWatsonApikey = ""
        if not hasattr(config, "myIBMWatsonUrl"):
            config.myIBMWatsonUrl = ""
        if not hasattr(config, "myIBMWatsonVersion"):
            config.myIBMWatsonVersion = "2018-05-01"
        config.help["showControlPanelOnStartup"] = """
        # Options to use control panel: True / False
        # This feature is created for use in church settings.
        # If True, users can use an additional command field, in an additional window, to control the content being displayed, even the main window of UniqueBible.app is displayed on extended screen."""
        if not hasattr(config, "showControlPanelOnStartup"):
            config.showControlPanelOnStartup = False
        if not hasattr(config, "preferControlPanelForCommandLineEntry"):
            config.preferControlPanelForCommandLineEntry = False
        if not hasattr(config, "closeControlPanelAfterRunningCommand"):
            config.closeControlPanelAfterRunningCommand = True
        if not hasattr(config, "restrictControlPanelWidth"):
            config.restrictControlPanelWidth = False
        if not hasattr(config, "masterControlWidth"):
            config.masterControlWidth = 1255
        if not hasattr(config, "miniControlInitialTab"):
            config.miniControlInitialTab = 0
        if not hasattr(config, "addBreakAfterTheFirstToolBar"):
            config.addBreakAfterTheFirstToolBar = True
        if not hasattr(config, "addBreakBeforeTheLastToolBar"):
            config.addBreakBeforeTheLastToolBar = False
        config.help["verseNoSingleClickAction"] = """
        # Configure verse number single-click & double-click action
        # available options: "_noAction", "_cp0", "_cp1", "_cp2", "_cp3", "_cp4", "COMPARE", "CROSSREFERENCE", "TSKE", "TRANSLATION", "DISCOURSE", "WORDS", "COMBO", "INDEX", "COMMENTARY", "_menu"
        # corresponding translation: "noAction", "cp0", "cp1", "cp2", "cp3", "cp4", "menu4_compareAll", "menu4_crossRef", "menu4_tske", "menu4_traslations", "menu4_discourse", "menu4_words", "menu4_tdw", "menu4_indexes", "menu4_commentary", "classicMenu" """
        if not hasattr(config, "verseNoSingleClickAction"):
            config.verseNoSingleClickAction = "INDEX"
        if not hasattr(config, "verseNoDoubleClickAction"):
            config.verseNoDoubleClickAction = "_cp0"
        config.help["linuxStartFullScreen"] = """
        # Start full-screen on Linux os"""
        if not hasattr(config, "linuxStartFullScreen"):
            config.linuxStartFullScreen = False
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
        config.help["espeakSpeed"] = """
        # espeak speed"""
        if not hasattr(config, "espeakSpeed"):
            config.espeakSpeed = 160
        config.help["qttsSpeed"] = """
        # qtts speed"""
        if not hasattr(config, "qttsSpeed"):
            config.qttsSpeed = 0.0
        config.help["useLangDetectOnTts"] = """
        # tts language options"""
        if not hasattr(config, "useLangDetectOnTts"):
            config.useLangDetectOnTts = False
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
        config.help["ibus"] = """
        # Options to use ibus as input method: True / False
        # This option may be useful on some Linux systems, where qt4 and qt5 applications use different input method variables."""
        if not hasattr(config, "ibus"):
            config.ibus = False
        config.help["fcitx"] = """
        # This option may be useful on some Linux systems, where qt4 and qt5 applications use different input method variables."""
        if not hasattr(config, "fcitx"):
            config.fcitx = False
        config.help["virtualKeyboard"] = """
        # Options to use built-in virtual keyboards: True / False"""
        if not hasattr(config, "virtualKeyboard"):
            config.virtualKeyboard = False
        config.help["openWindows"] = """
        # Specify the "open" command on Windows"""
        if not hasattr(config, "openWindows"):
            config.openWindows = "start"
        config.help["openMacos"] = """
        # Specify the "open" command on macOS"""
        if not hasattr(config, "openMacos"):
            config.openMacos = "open"
        config.help["openLinux"] = """
        # Specify the "open" command on Linux"""
        if not hasattr(config, "openLinux"):
            config.openLinux = "xdg-open"
        config.help["openLinuxPdf"] = """
        # Specify the command to open pdf file on Linux"""
        if not hasattr(config, "openLinuxPdf"):
            config.openLinuxPdf = "xdg-open"
        config.help["marvelData"] = """
        # Specify the folder path of resources"""
        if not hasattr(config, "marvelData") or not os.path.isdir(config.marvelData):
            config.marvelData = "marvelData"
        config.help["musicFolder"] = """
        # Specify the folder path of music files"""
        if not hasattr(config, "musicFolder"):
            config.musicFolder = "music"
        config.help["videoFolder"] = """
        # Specify the folder path of video files"""
        if not hasattr(config, "videoFolder"):
            config.videoFolder = "video"
        config.help["bibleNotes"] = """
        # Specify the file path of note file on bible chapters and verses"""
        if not hasattr(config, "bibleNotes"):
            config.bibleNotes = "note.sqlite"
        config.help["numberOfTab"] = """
        # Specify the number of tabs for bible reading and workspace"""
        if not hasattr(config, "numberOfTab"):
            config.numberOfTab = 5
        config.help["populateTabsOnStartup"] = """
        # Options to populate tabs with latest history records on start up: True / False"""
        if not hasattr(config, "populateTabsOnStartup"):
            config.populateTabsOnStartup = False
        config.help["openBibleWindowContentOnNextTab"] = """
        # Options to open Bible Window's content in the tab next to the current one: True / False"""
        if not hasattr(config, "openBibleWindowContentOnNextTab"):
            config.openBibleWindowContentOnNextTab = False
        config.help["openStudyWindowContentOnNextTab"] = """
        # Options to open Study Window's content in the tab next to the current one: True / False"""
        if not hasattr(config, "openStudyWindowContentOnNextTab"):
            config.openStudyWindowContentOnNextTab = True
        config.help["preferHtmlMenu"] = """
        # Options to open classic html menu when a bible chapter heading is clicked
        # It is set to False by default that clicking a chapter heading opens Master Control panel."""
        if not hasattr(config, "preferHtmlMenu"):
            config.preferHtmlMenu = False
        config.help["parserStandarisation"] = """
        # Options to convert all bible book abbreviations to standard ones: YES / NO"""
        if not hasattr(config, "parserStandarisation"):
            config.parserStandarisation = "NO"
        config.help["standardAbbreviation"] = """
        # Options of language of book abbreviations: ENG / TC / SC"""
        if not hasattr(config, "standardAbbreviation"):
            config.standardAbbreviation = "ENG"
        config.help["noOfLinesPerChunkForParsing"] = """
        # Large-size text is divided into chunks before parsing, in order to improve performance.  
        # This option specify maximum number of lines included into each chunk.  
        # Too many or too little can affect performance.  
        # Choose a value suitable for your device.  
        # Generally, device with higher memory capacity can handle more numbers of line in each chunk."""
        if not hasattr(config, "noOfLinesPerChunkForParsing"):
            config.noOfLinesPerChunkForParsing = 100
        config.help["convertChapterVerseDotSeparator"] = """
        # Option to convert the dot sign, which separates chapter number and verse number in some bible references, to colon sign so that UBA parser can parse those referencces."""
        if not hasattr(config, "convertChapterVerseDotSeparator"):
            config.convertChapterVerseDotSeparator = True
        config.help["parseBookChapterWithoutSpace"] = """
        # Parse references without space between book name and chapter number."""
        if not hasattr(config, "parseBookChapterWithoutSpace"):
            config.parseBookChapterWithoutSpace = True
        config.help["parseBooklessReferences"] = """
        # Parse bookless references in selected text."""
        if not hasattr(config, "parseBooklessReferences"):
            config.parseBooklessReferences = True
        config.help["userLanguage"] = """
        # Option to set a customised language for google-translate
        # References: https://cloud.google.com/translate/docs/languages
        # Use gui "Set my Language" dialog, from menu bar, to set "userLanguage"."""
        if not hasattr(config, "userLanguage") or not config.userLanguage:
            config.userLanguage = "English"
        config.help["userLanguageInterface"] = """
        # Option to use interface translated into userLanguage: True / False"""
        if not hasattr(config, "userLanguageInterface"):
            config.userLanguageInterface = False
        config.help["autoCopyTranslateResult"] = """
        # Option to copy automatically to clipboard the result of accessing Google Translate: True / False"""
        if not hasattr(config, "autoCopyTranslateResult"):
            config.autoCopyTranslateResult = True
        config.help["showVerseNumbersInRange"] = """
        # Option to display verse number in a range of verses: True / False
        # e.g. Try entering in command field "Ps 23:1; Ps 23:1-3; Ps 23:1-24:3" """
        if not hasattr(config, "showVerseNumbersInRange"):
            config.showVerseNumbersInRange = True
        config.help["openBibleNoteAfterSave"] = """
        # Options to open chapter / verse note on Study Window after saving: True / False"""
        if not hasattr(config, "openBibleNoteAfterSave"):
            config.openBibleNoteAfterSave = False
        config.help["openBibleNoteAfterEditorClosed"] = """
        # Default: False: Open bible note on Study Window afer it is edited with Note Editor.
        # Bible note is opened when Note editor is closed."""
        if not hasattr(config, "openBibleNoteAfterEditorClosed"):
            config.openBibleNoteAfterEditorClosed = False
        config.help["exportEmbeddedImages"] = """
        # Options to export all embedded images displayed on Study Window: True / False"""
        if not hasattr(config, "exportEmbeddedImages"):
            config.exportEmbeddedImages = True
        config.help["clickToOpenImage"] = """
        # Options to add open image action with a single click: True / False"""
        if not hasattr(config, "clickToOpenImage"):
            config.clickToOpenImage = True
        config.help["landscapeMode"] = """
        # Options to use landscape mode: True / False"""
        if not hasattr(config, "landscapeMode"):
            config.landscapeMode = True
        config.help["noToolBar"] = """
        # Options for NOT displaying any toolbars on startup: True / False"""
        if not hasattr(config, "noToolBar"):
            config.noToolBar = False
        config.help["topToolBarOnly"] = """
        # Options to display the top toolbar only, with all other toolbars hidden: True / False"""
        if not hasattr(config, "topToolBarOnly"):
            config.topToolBarOnly = False
        config.help["toolBarIconFullSize"] = """
        # Options to use large sets of icons: True / False"""
        if not hasattr(config, "toolBarIconFullSize"):
            config.toolBarIconFullSize = False
        config.help["parallelMode"] = """
        # Options on parallel mode: 0, 1, 2, 3"""
        if not hasattr(config, "parallelMode"):
            config.parallelMode = 1
        config.help["instantMode"] = """
        # Options to display the window showing instant information: 0, 1"""
        if not hasattr(config, "instantMode"):
            config.instantMode = 1
        config.help["instantInformationEnabled"] = """
        # Options to trigger instant information: True / False"""
        if not hasattr(config, "instantInformationEnabled"):
            config.instantInformationEnabled = True
        config.help["fontSize"] = """
        # Default font size of content in main window and workspace"""
        if not hasattr(config, "fontSize"):
            config.fontSize = 17
        config.help["font"] = """
        # Default font"""
        if not hasattr(config, "font"):
            config.font = ""
        config.help["fontChinese"] = """
        # Default Chinese font"""
        if not hasattr(config, "fontChinese"):
            config.fontChinese = ""
        config.help["noteEditorFontSize"] = """
        # Default font size of content in note editor"""
        if not hasattr(config, "noteEditorFontSize"):
            config.noteEditorFontSize = 14
        config.help["hideNoteEditorStyleToolbar"] = """
        # Show Note Editor's style toolbar by default"""
        if not hasattr(config, "hideNoteEditorStyleToolbar"):
            config.hideNoteEditorStyleToolbar = False
        config.help["hideNoteEditorTextUtility"] = """
        # Hide Note Editor's text utility by default"""
        if not hasattr(config, "hideNoteEditorTextUtility"):
            config.hideNoteEditorTextUtility = True
        config.help["readFormattedBibles"] = """
        # Options to display bibles in formatted layout or paragraphs: True / False
        # "False" here means displaying bible verse in plain format, with each one on a single line."""
        if not hasattr(config, "readFormattedBibles"):
            config.readFormattedBibles = True
        config.help["addTitleToPlainChapter"] = """
        # Options to add sub-headings when "readFormattedBibles" is set to "False": True / False"""
        if not hasattr(config, "addTitleToPlainChapter"):
            config.addTitleToPlainChapter = True
        config.help["hideLexicalEntryInBible"] = """
        # Options to hide lexical entries or Strong's numbers: True / False"""
        if not hasattr(config, "hideLexicalEntryInBible"):
            config.hideLexicalEntryInBible = False
        config.help["importAddVerseLinebreak"] = """
        # Import setting - add a line break after each verse: True / False"""
        if not hasattr(config, "importAddVerseLinebreak"):
            config.importAddVerseLinebreak = False
        config.help["importDoNotStripStrongNo"] = """
        # Import setting - keep Strong's number for search: True / False"""
        if not hasattr(config, "importDoNotStripStrongNo"):
            config.importDoNotStripStrongNo = False
        config.help["importDoNotStripMorphCode"] = """
        # Import setting - keep morphology codes for search: True / False"""
        if not hasattr(config, "importDoNotStripMorphCode"):
            config.importDoNotStripMorphCode = False
        config.help["importRtlOT"] = """
        # Import setting - import text in right-to-left direction: True / False"""
        if not hasattr(config, "importRtlOT"):
            config.importRtlOT = False
        config.help["importInterlinear"] = """
        # Import setting - import interlinear text: True / False"""
        if not hasattr(config, "importInterlinear"):
            config.importInterlinear = False
        config.help["originalTexts"] = """
        # List of modules, which contains Hebrew / Greek texts"""
        if not hasattr(config, "originalTexts"):
            config.originalTexts = ['original', 'MOB', 'MAB', 'MTB', 'MIB', 'MPB', 'OHGB', 'OHGBi', 'LXX', 'LXX1',
                                    'LXX1i',
                                    'LXX2', 'LXX2i']
        config.help["rtlTexts"] = """
        # List of modules, which contains right-to-left texts on old testament"""
        if not hasattr(config, "rtlTexts"):
            config.rtlTexts = ["original", "MOB", "MAB", "MIB", "MPB", "OHGB", "OHGBi"]
        config.help["openBibleInMainViewOnly"] = """
        # Open bible references on main window instead of workspace: Ture / False"""
        if not hasattr(config, "openBibleInMainViewOnly"):
            config.openBibleInMainViewOnly = False
        config.help["mainText"] = """
        # Last-opened bible version and passage to be displayed on main window"""
        if not hasattr(config, "mainText"):
            config.mainText = "KJV"
        if not hasattr(config, "mainB"):
            config.mainB = 1
        if not hasattr(config, "mainC"):
            config.mainC = 1
        if not hasattr(config, "mainV"):
            config.mainV = 1
        config.help["studyText"] = """
        # Last-opened bible version and passage to be displayed on workspace"""
        if not hasattr(config, "studyText"):
            config.studyText = "NET"
        if not hasattr(config, "studyB"):
            config.studyB = 43
        if not hasattr(config, "studyC"):
            config.studyC = 3
        if not hasattr(config, "studyV"):
            config.studyV = 16
        config.help["bibleSearchMode"] = """
        # Search Bible Mode
        # Accept value: 0-4
        # Correspond to ("SEARCH", "SHOWSEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH")"""
        if not hasattr(config, "bibleSearchMode"):
            config.bibleSearchMode = 0
        config.help["favouriteBible"] = """
        # Set your favourite version here"""
        if not hasattr(config, "favouriteBible"):
            config.favouriteBible = "OHGBi"
        config.help["addFavouriteToMultiRef"] = """
        # Options to display "favouriteBible" together with the main version for reading multiple references: True / False"""
        if not hasattr(config, "addFavouriteToMultiRef"):
            config.addFavouriteToMultiRef = False
        config.help["enforceCompareParallel"] = """
        # Options to enforce comparison / parallel: True / False
        # When it is enabled after comparison / parallel feature is loaded once, subsequence entries of bible references will be treated as launching comparison / parallel even COMPARE::: or PARALLEL::: keywords is not used.
        # Please note that change in bible version for chapter reading is ignored when this option is enabled.
        # This feature is accessible via a left toolbar button, located under the "Comparison / Parallel Reading / Difference" button."""
        if not hasattr(config, "enforceCompareParallel"):
            config.enforceCompareParallel = False
        config.help["showNoteIndicatorOnBibleChapter"] = """
        # Options to show note indicator on bible chapter: True / False"""
        if not hasattr(config, "showNoteIndicatorOnBibleChapter"):
            config.showNoteIndicatorOnBibleChapter = True
        config.help["syncStudyWindowBibleWithMainWindow"] = """
        # Options sync Study Window's with changes verse references on Main Window: True / False"""
        if not hasattr(config, "syncStudyWindowBibleWithMainWindow"):
            config.syncStudyWindowBibleWithMainWindow = False
        config.help["syncCommentaryWithMainWindow"] = """
        # Options sync commentary with changes verse references on Main Window: True / False"""
        if not hasattr(config, "syncCommentaryWithMainWindow"):
            config.syncCommentaryWithMainWindow = False
        config.help["commentaryText"] = """
        # Last-opened commentary text and passage"""
        if not hasattr(config, "commentaryText"):
            config.commentaryText = "CBSC"
        if not hasattr(config, "commentaryB"):
            config.commentaryB = 43
        if not hasattr(config, "commentaryC"):
            config.commentaryC = 3
        if not hasattr(config, "commentaryV"):
            config.commentaryV = 16
        config.help["topic"] = """
        # Last-opened module for topical studies"""
        if not hasattr(config, "topic"):
            config.topic = "EXLBT"
        config.help["dictionary"] = """
        # Last-opened dictionary module"""
        if not hasattr(config, "dictionary"):
            config.dictionary = "EAS"
        config.help["encyclopedia"] = """
        # Last-opened encyclopedia module"""
        if not hasattr(config, "encyclopedia"):
            config.encyclopedia = "ISB"
        config.help["docxText"] = """
        # Last-opened docx text"""
        if not hasattr(config, "docxText"):
            config.docxText = ""
        config.help["parseWordDocument"] = """
        # Parse Word Document content"""
        if not hasattr(config, "parseWordDocument"):
            config.parseWordDocument = True
        config.help["pdfText"] = """
        # Last-opened pdf filename"""
        if not hasattr(config, "pdfText"):
            config.pdfText = ""
        config.help["pdfTextPath"] = """
        # Last-opened pdf file path"""
        if not hasattr(config, "pdfTextPath"):
            config.pdfTextPath = ""
        config.help["book"] = """
        # Last-opened book module"""
        if not hasattr(config, "book"):
            config.book = "Harmonies_and_Parallels"
        config.help["bookChapter"] = """
        # Last-opened book chapter"""
        if not hasattr(config, "bookChapter"):
            config.bookChapter = "03 - Gospels I"
        config.help["bookOnNewWindow"] = """
        # Option to open book content on a new window"""
        if not hasattr(config, "bookOnNewWindow"):
            config.bookOnNewWindow = False
        config.help["popoverWindowWidth"] = """
        # Popover Windows width"""
        if not hasattr(config, "popoverWindowWidth"):
            config.popoverWindowWidth = 640
        config.help["popoverWindowHeight"] = """
        # Popover Windows height"""
        if not hasattr(config, "popoverWindowHeight"):
            config.popoverWindowHeight = 480
        config.help["overwriteBookFont"] = """
        # Option to overwrite font in book modules"""
        if not hasattr(config, "overwriteBookFont"):
            config.overwriteBookFont = True
        config.help["overwriteBookFontFamily"] = """
        # Overwrite book font family"""
        if not hasattr(config, "overwriteBookFontFamily"):
            config.overwriteBookFontFamily = ""
        config.help["overwriteBookFontSize"] = """
        # Option to overwrite font size in book modules"""
        if not hasattr(config, "overwriteBookFontSize"):
            config.overwriteBookFontSize = True
        config.help["overwriteNoteFont"] = """
        # Option to overwrite font in bible notes"""
        if not hasattr(config, "overwriteNoteFont"):
            config.overwriteNoteFont = True
        config.help["overwriteNoteFontSize"] = """
        # Option to overwrite font size in bible notes"""
        if not hasattr(config, "overwriteNoteFontSize"):
            config.overwriteNoteFontSize = True
        config.help["favouriteBooks"] = """
        # List of favourite book modules
        # Only the first 10 books are shown on menu bar"""
        if not hasattr(config, "favouriteBooks"):
            config.favouriteBooks = ["Harmonies_and_Parallels", "Bible_Promises", "Timelines", "Maps_ABS", "Maps_NET"]
        config.help["removeHighlightOnExit"] = """
        # Remove book, note and instant highlights on exit."""
        if not hasattr(config, "removeHighlightOnExit"):
            config.removeHighlightOnExit = True
        config.help["bookSearchString"] = """
        # Last string entered for searching book"""
        if not hasattr(config, "bookSearchString"):
            config.bookSearchString = ""
        config.help["instantHighlightString"] = """
        # Instant Highlight: highlighted word in Main Window"""
        if not hasattr(config, "instantHighlightString"):
            config.instantHighlightString = ""
        config.help["noteSearchString"] = """
        # Last string entered for searching note"""
        if not hasattr(config, "noteSearchString"):
            config.noteSearchString = ""
        config.help["thirdDictionary"] = """
        # Last-opened third-party dictionary"""
        if not hasattr(config, "thirdDictionary"):
            config.thirdDictionary = "webster"
        config.help["lexicon"] = """
        # Last-opened lexicon"""
        if not hasattr(config, "lexicon"):
            config.lexicon = "ConcordanceBook"
        config.help["defaultLexiconStrongH"] = """
        # Default Hebrew lexicon"""
        if not hasattr(config, "defaultLexiconStrongH"):
            config.defaultLexiconStrongH = "TBESH"
        config.help["defaultLexiconStrongG"] = """
        # Default Greek lexicon"""
        if not hasattr(config, "defaultLexiconStrongG"):
            config.defaultLexiconStrongG = "TBESG"
        config.help["defaultLexiconETCBC"] = """
        # Default lexicon based on ETCBC data"""
        if not hasattr(config, "defaultLexiconETCBC"):
            config.defaultLexiconETCBC = "ConcordanceMorphology"
        config.help["defaultLexiconLXX"] = """
        # Default lexicon on LXX words"""
        if not hasattr(config, "defaultLexiconLXX"):
            config.defaultLexiconLXX = "LXX"
        config.help["defaultLexiconGK"] = """
        # Default lexicon on GK entries"""
        if not hasattr(config, "defaultLexiconGK"):
            config.defaultLexiconGK = "MCGED"
        config.help["defaultLexiconLN"] = """
        # Default lexicon on LN entries"""
        if not hasattr(config, "defaultLexiconLN"):
            config.defaultLexiconLN = "LN"
        config.help["maximumHistoryRecord"] = """
        # Maximum number of history records allowed to be stored"""
        if not hasattr(config, "maximumHistoryRecord"):
            config.maximumHistoryRecord = 50
        config.help["currentRecord"] = """
        # Indexes of last-opened records"""
        if not hasattr(config, "currentRecord"):
            config.currentRecord = {"main": 0, "study": 0}
        config.help["history"] = """
        # History records are kept in config.history"""
        if not hasattr(config, "history"):
            config.history = {"external": ["note_editor.uba"], "main": ["BIBLE:::KJV:::Genesis 1:1"],
                              "study": ["BIBLE:::NET:::John 3:16"]}
        config.help["installHistory"] = """
        # Installed Formatted Bibles"""
        if not hasattr(config, "installHistory"):
            config.installHistory = {}
        config.help["useWebbrowser"] = """
        # Use webbrowser module to open internal website links instead of opening on Study Window"""
        if not hasattr(config, "useWebbrowser"):
            config.useWebbrowser = True
        config.help["showInformation"] = """
        # set show information to True"""
        if not hasattr(config, "showInformation"):
            config.showInformation = True
        # Window Style
        # Availability of window styles depends on device"""
        if not hasattr(config, "windowStyle") or not config.windowStyle:
            config.windowStyle = "Fusion"
        config.help["theme"] = """
        # Theme (default, dark)"""
        if not hasattr(config, "theme"):
            config.theme = "default"
        config.help["qtMaterial"] = """
        # qt-material theme
        # qt-material theme is used only qtMaterial is true and qtMaterialTheme is not empty"""
        if not hasattr(config, "qtMaterial"):
            config.qtMaterial = False
        if not hasattr(config, "qtMaterialTheme"):
            config.qtMaterialTheme = ""
        config.help["disableModulesUpdateCheck"] = """
        # Disable modules update check"""
        if not hasattr(config, "disableModulesUpdateCheck"):
            config.disableModulesUpdateCheck = True
        config.help["forceGenerateHtml"] = """
        # Force generate main.html for all pages"""
        if not hasattr(config, "forceGenerateHtml"):
            config.forceGenerateHtml = False
        config.help["enableLogging"] = """
        # Enable logging"""
        if not hasattr(config, "enableLogging"):
            config.enableLogging = False
        config.help["logCommands"] = """
        # Log commands for debugging"""
        if not hasattr(config, "logCommands"):
            config.logCommands = False
        config.help["migrateDatabaseBibleNameToDetailsTable"] = """
        # Migrate Bible name from Verses table to Details table"""
        if not hasattr(config, "migrateDatabaseBibleNameToDetailsTable"):
            config.migrateDatabaseBibleNameToDetailsTable = True
        config.help["enableVerseHighlighting"] = """
        # Verse highlighting functionality"""
        if not hasattr(config, "enableVerseHighlighting"):
            config.enableVerseHighlighting = True
        config.help["showHighlightMarkers"] = """
        # Show verse highlight markers"""
        if not hasattr(config, "showHighlightMarkers"):
            config.showHighlightMarkers = False
        config.help["menuLayout"] = """
        # Menu layout"""
        if not hasattr(config, "menuLayout"):
            config.menuLayout = "focus"
        config.help["useFastVerseParsing"] = """
        # Verse parsing method"""
        if not hasattr(config, "useFastVerseParsing"):
            config.useFastVerseParsing = False
        config.help["enablePlugins"] = """
        # Enable plugins"""
        if not hasattr(config, "enablePlugins"):
            config.enablePlugins = True
        config.help["enableMacros"] = """
        # Enable macros"""
        if not hasattr(config, "enableMacros"):
            config.enableMacros = False
        config.help["startupMacro"] = """
        # Startup macro"""
        if not hasattr(config, "startupMacro"):
            config.startupMacro = ""
        config.help["enableGist"] = """
        # Gist synching"""
        if not hasattr(config, "enableGist"):
            config.enableGist = False
        if not hasattr(config, "gistToken"):
            config.gistToken = ''
        config.help["clearCommandEntry"] = """
        # Clear command entry line by default"""
        if not hasattr(config, "clearCommandEntry"):
            config.clearCommandEntry = False
        # Highlight collections"""
        if not hasattr(config, "highlightCollections") or len(config.highlightCollections) < 12:
            config.highlightCollections = ["Collection 1", "Collection 2", "Collection 3", "Collection 4", "Collection 5", "Collection 6", "Collection 7", "Collection 8", "Collection 9", "Collection 10", "Collection 11", "Collection 12"]
        if not hasattr(config, "highlightDarkThemeColours") or len(config.highlightDarkThemeColours) < 12:
            config.highlightDarkThemeColours = ["#646400", "#060166", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400", "#646400"]
        if not hasattr(config, "highlightLightThemeColours") or len(config.highlightLightThemeColours) < 12:
            config.highlightLightThemeColours = ["#e8e809", "#4ff7fa", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#e8e809", "#646400", "#646400"]
        config.help["menuShortcuts"] = """
        # Default menu shortcuts"""
        if not hasattr(config, "menuShortcuts"):
            config.menuShortcuts = "micron"
        config.help["regexCaseSensitive"] = """
        # Option to use flags=re.IGNORECASE with regular expression for searching bible
        # flags=re.IGNORECASE will be applied only if config.regexCaseSensitive is set to False"""
        if not hasattr(config, "regexCaseSensitive"):
            config.regexCaseSensitive = False
        if not hasattr(config, "displayLanguage"):
            config.displayLanguage = 'en_US'
        config.help["lastAppUpdateCheckDate"] = """
        # App update check"""
        if not hasattr(config, "lastAppUpdateCheckDate"):
            config.lastAppUpdateCheckDate = str(DateUtil.localDateNow())
        if not hasattr(config, "daysElapseForNextAppUpdateCheck"):
            config.daysElapseForNextAppUpdateCheck = '14'
        if not hasattr(config, "updateWithGitPull"):
            config.updateWithGitPull = False
        if not hasattr(config, "minicontrolWindowWidth"):
            config.minicontrolWindowWidth = 450
        if not hasattr(config, "minicontrolWindowHeight"):
            config.minicontrolWindowHeight = 400
        if not hasattr(config, "refButtonClickAction"):
            config.refButtonClickAction = "master"
        if not hasattr(config, "presentationScreenNo"):
            config.presentationScreenNo = -1
        if not hasattr(config, "presentationFontSize"):
            config.presentationFontSize = 3.0
        if not hasattr(config, "presentationMargin"):
            config.presentationMargin = 50
        if not hasattr(config, "presentationColorOnLightTheme"):
            config.presentationColorOnLightTheme = "black"
        if not hasattr(config, "presentationColorOnDarkTheme"):
            config.presentationColorOnDarkTheme = "magenta"
        if not hasattr(config, "presentationVerticalPosition"):
            config.presentationVerticalPosition = 50
        if not hasattr(config, "presentationHorizontalPosition"):
            config.presentationHorizontalPosition = 50
        if not hasattr(config, "hideBlankVerseCompare"):
            config.hideBlankVerseCompare = False
        if not hasattr(config, "miniBrowserHome"):
            config.miniBrowserHome = "https://www.youtube.com/"
        if not hasattr(config, "enableMenuUnderline"):
            config.enableMenuUnderline = True
        if not hasattr(config, "addOHGBiToMorphologySearch"):
            config.addOHGBiToMorphologySearch = True
        if not hasattr(config, "activeVerseNoColourLight"):
            config.activeVerseNoColourLight = "#204a87"
        if not hasattr(config, "activeVerseNoColourDark"):
            config.activeVerseNoColourDark = "rgb(197, 197, 56)"
        if not hasattr(config, "maximumOHGBiVersesDisplayedInSearchResult"):
            config.maximumOHGBiVersesDisplayedInSearchResult = 50
        if not hasattr(config, "excludeStartupPlugins"):
            config.excludeStartupPlugins = []
        if not hasattr(config, "excludeMenuPlugins"):
            config.excludeMenuPlugins = []
        if not hasattr(config, "excludeContextPlugins"):
            config.excludeContextPlugins = []
        if not hasattr(config, "excludeShutdownPlugins"):
            config.excludeShutdownPlugins = []
        if not hasattr(config, "toolbarIconSizeFactor"):
            config.toolbarIconSizeFactor = 0.75
        if not hasattr(config, "sidebarIconSizeFactor"):
            config.sidebarIconSizeFactor = 0.6
        if not hasattr(config, "githubAccessToken"):
            token = "{0}_{1}0{2}".format('tuc', 'pOgQGiZ7QLV6N37UN', 'S1ubxgHbiE5Z34mbiZ')
            config.githubAccessToken = codecs.encode(token, 'rot_13')

        # Temporary configurations
        # Their values are not saved on exit.
        config.controlPanel = False
        config.miniControl = False
        config.tempRecord = ""
        config.contextItem = ""
        config.isDownloading = False
        config.noStudyBibleToolbar = False
        config.noteOpened = False
        config.pipIsUpdated = False
        config.bibleWindowContentTransformers = []
        config.studyWindowContentTransformers = []
        config.shortcutList = []
        if config.enableMenuUnderline:
            config.menuUnderline = "&"
        else:
            config.menuUnderline = ""

    # Save configurations on exit
    @staticmethod
    def save():
        if config.removeHighlightOnExit:
            config.bookSearchString = ""
            config.noteSearchString = ""
            config.instantHighlightString = ""
        configs = (
            # ("version", config.version),
            ("developer", config.developer),
            ("referenceTranslation", config.referenceTranslation),
            ("workingTranslation", config.workingTranslation),
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
            #("showTtsOnLinux", config.showTtsOnLinux),
            ("espeak", config.espeak),
            ("espeakSpeed", config.espeakSpeed),
            ("qttsSpeed", config.qttsSpeed),
            ("useLangDetectOnTts", config.useLangDetectOnTts),
            ("ttsDefaultLangauge", config.ttsDefaultLangauge),
            ("ttsEnglishAlwaysUS", config.ttsEnglishAlwaysUS),
            ("ttsEnglishAlwaysUK", config.ttsEnglishAlwaysUK),
            ("ttsChineseAlwaysMandarin", config.ttsChineseAlwaysMandarin),
            ("ttsChineseAlwaysCantonese", config.ttsChineseAlwaysCantonese),
            ("ibus", config.ibus),
            ("fcitx", config.fcitx),
            ("virtualKeyboard", config.virtualKeyboard),
            ("marvelData", config.marvelData),
            ("musicFolder", config.musicFolder),
            ("videoFolder", config.videoFolder),
            ("bibleNotes", config.bibleNotes),
            ("numberOfTab", config.numberOfTab),
            ("populateTabsOnStartup", config.populateTabsOnStartup),
            ("openBibleWindowContentOnNextTab", config.openBibleWindowContentOnNextTab),
            ("openStudyWindowContentOnNextTab", config.openStudyWindowContentOnNextTab),
            ("preferHtmlMenu", config.preferHtmlMenu),
            ("parserStandarisation", config.parserStandarisation),
            ("standardAbbreviation", config.standardAbbreviation),
            ("noOfLinesPerChunkForParsing", config.noOfLinesPerChunkForParsing),
            ("convertChapterVerseDotSeparator", config.convertChapterVerseDotSeparator),
            ("parseBookChapterWithoutSpace", config.parseBookChapterWithoutSpace),
            ("parseBooklessReferences", config.parseBooklessReferences),
            ("userLanguage", config.userLanguage),
            ("userLanguageInterface", config.userLanguageInterface),
            ("autoCopyTranslateResult", config.autoCopyTranslateResult),
            ("showVerseNumbersInRange", config.showVerseNumbersInRange),
            ("openBibleNoteAfterSave", config.openBibleNoteAfterSave),
            ("openBibleNoteAfterEditorClosed", config.openBibleNoteAfterEditorClosed),
            ("exportEmbeddedImages", config.exportEmbeddedImages),
            ("clickToOpenImage", config.clickToOpenImage),
            ("landscapeMode", config.landscapeMode),
            ("noToolBar", config.noToolBar),
            ("topToolBarOnly", config.topToolBarOnly),
            ("toolBarIconFullSize", config.toolBarIconFullSize),
            ("toolbarIconSizeFactor", config.toolbarIconSizeFactor),
            ("sidebarIconSizeFactor", config.sidebarIconSizeFactor),
            ("parallelMode", config.parallelMode),
            ("instantMode", config.instantMode),
            ("instantInformationEnabled", config.instantInformationEnabled),
            ("miniBrowserHome", config.miniBrowserHome),
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
            ("addOHGBiToMorphologySearch", config.addOHGBiToMorphologySearch),
            ("maximumOHGBiVersesDisplayedInSearchResult", config.maximumOHGBiVersesDisplayedInSearchResult),
            ("showNoteIndicatorOnBibleChapter", config.showNoteIndicatorOnBibleChapter),
            ("enforceCompareParallel", config.enforceCompareParallel),
            ("hideBlankVerseCompare", config.hideBlankVerseCompare),
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
            ("pdfText", config.pdfText),
            ("pdfTextPath", config.pdfTextPath),
            ("docxText", config.docxText),
            ("parseWordDocument", config.parseWordDocument),
            ("book", config.book),
            ("bookChapter", config.bookChapter),
            ("bookOnNewWindow", config.bookOnNewWindow),
            ("popoverWindowWidth", config.popoverWindowWidth),
            ("popoverWindowHeight", config.popoverWindowHeight),
            ("verseNoSingleClickAction", config.verseNoSingleClickAction),
            ("verseNoDoubleClickAction", config.verseNoDoubleClickAction),
            ("overwriteBookFont", config.overwriteBookFont),
            ("overwriteBookFontFamily", config.overwriteBookFontFamily),
            ("overwriteBookFontSize", config.overwriteBookFontSize),
            ("overwriteNoteFont", config.overwriteNoteFont),
            ("overwriteNoteFontSize", config.overwriteNoteFontSize),
            ("favouriteBooks", config.favouriteBooks),
            ("removeHighlightOnExit", config.removeHighlightOnExit),
            ("bookSearchString", config.bookSearchString),
            ("noteSearchString", config.noteSearchString),
            ("instantHighlightString", config.instantHighlightString),
            ("thirdDictionary", config.thirdDictionary),
            ("lexicon", config.lexicon),
            ("defaultLexiconStrongH", config.defaultLexiconStrongH),
            ("defaultLexiconStrongG", config.defaultLexiconStrongG),
            ("defaultLexiconETCBC", config.defaultLexiconETCBC),
            ("defaultLexiconLXX", config.defaultLexiconLXX),
            ("defaultLexiconGK", config.defaultLexiconGK),
            ("defaultLexiconLN", config.defaultLexiconLN),
            ("useWebbrowser", config.useWebbrowser),
            ("showInformation", config.showInformation),
            ("windowStyle", config.windowStyle),
            ("theme", config.theme),
            ("qtMaterial", config.qtMaterial),
            ("qtMaterialTheme", config.qtMaterialTheme),
            ("disableModulesUpdateCheck", config.disableModulesUpdateCheck),
            ("showControlPanelOnStartup", config.showControlPanelOnStartup),
            ("preferControlPanelForCommandLineEntry", config.preferControlPanelForCommandLineEntry),
            ("closeControlPanelAfterRunningCommand", config.closeControlPanelAfterRunningCommand),
            ("restrictControlPanelWidth", config.restrictControlPanelWidth),
            ("masterControlWidth", config.masterControlWidth),
            ("miniControlInitialTab", config.miniControlInitialTab),
            ("addBreakAfterTheFirstToolBar", config.addBreakAfterTheFirstToolBar),
            ("addBreakBeforeTheLastToolBar", config.addBreakBeforeTheLastToolBar),
            ("forceGenerateHtml", config.forceGenerateHtml),
            ("enableLogging", config.enableLogging),
            ("logCommands", config.logCommands),
            ("migrateDatabaseBibleNameToDetailsTable", config.migrateDatabaseBibleNameToDetailsTable),
            ("menuLayout", config.menuLayout),
            ("useFastVerseParsing", config.useFastVerseParsing),
            #("customPythonOnStartup", config.customPythonOnStartup),
            ("enablePlugins", config.enablePlugins),
            ("enableMacros", config.enableMacros),
            ("startupMacro", config.startupMacro),
            ("enableGist", config.enableGist),
            ("gistToken", config.gistToken),
            ("clearCommandEntry", config.clearCommandEntry),
            ("activeVerseNoColourLight", config.activeVerseNoColourLight),
            ("activeVerseNoColourDark", config.activeVerseNoColourDark),
            ("highlightCollections", config.highlightCollections),
            ("highlightLightThemeColours", config.highlightLightThemeColours),
            ("highlightDarkThemeColours", config.highlightDarkThemeColours),
            ("enableVerseHighlighting", config.enableVerseHighlighting),
            ("showHighlightMarkers", config.showHighlightMarkers),
            ("menuShortcuts", config.menuShortcuts),
            ("displayLanguage", config.displayLanguage),
            ("lastAppUpdateCheckDate", config.lastAppUpdateCheckDate),
            ("daysElapseForNextAppUpdateCheck", config.daysElapseForNextAppUpdateCheck),
            ("updateWithGitPull", config.updateWithGitPull),
            ("minicontrolWindowWidth", config.minicontrolWindowWidth),
            ("minicontrolWindowHeight", config.minicontrolWindowHeight),
            ("refButtonClickAction", config.refButtonClickAction),
            ("presentationScreenNo", config.presentationScreenNo),
            ("presentationFontSize", config.presentationFontSize),
            ("presentationMargin", config.presentationMargin),
            ("presentationColorOnLightTheme", config.presentationColorOnLightTheme),
            ("presentationColorOnDarkTheme", config.presentationColorOnDarkTheme),
            ("presentationVerticalPosition", config.presentationVerticalPosition),
            ("presentationHorizontalPosition", config.presentationHorizontalPosition),
            ("excludeStartupPlugins", config.excludeStartupPlugins),
            ("excludeMenuPlugins", config.excludeMenuPlugins),
            ("excludeContextPlugins", config.excludeContextPlugins),
            ("excludeShutdownPlugins", config.excludeShutdownPlugins),
            ("maximumHistoryRecord", config.maximumHistoryRecord),
            ("currentRecord", {'main': 0, 'study': 0}),
            ("history", config.history),
            ("installHistory", config.installHistory),
            ("enableMenuUnderline", config.enableMenuUnderline),
            ("githubAccessToken", config.githubAccessToken),
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

