# flake8: noqa
import re, pprint, os, requests, platform, pydoc, markdown, sys, subprocess, json, shutil, webbrowser, traceback, textwrap, wcwidth, unicodedata
from uniquebible import config, extract_text
import threading, time
#from duckduckgo_search import ddg
from functools import partial
from datetime import date
from pathlib import Path
from base64 import b64decode
#import urllib.request
from ast import literal_eval
from haversine import haversine

from uniquebible.db.BiblesSqlite import Bible
from uniquebible.db.JournalSqlite import JournalSqlite
from uniquebible.db.ToolsSqlite import Book
from uniquebible.db.NoteSqlite import NoteSqlite
from uniquebible.util.Languages import Languages
from uniquebible.util.readings import allDays
from uniquebible.util.DateUtil import DateUtil
from uniquebible.util.TextUtil import TextUtil
from uniquebible.util.NetworkUtil import NetworkUtil
from uniquebible.util.RemoteCliMainWindow import RemoteCliMainWindow
from uniquebible.util.TextCommandParser import TextCommandParser
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.util.CrossPlatform import CrossPlatform
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.GitHubRepoInfo import GitHubRepoInfo
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.UpdateUtil import UpdateUtil
from uniquebible.util.DateUtil import DateUtil
from uniquebible.util.WebtopUtil import WebtopUtil
from uniquebible.util.Translator import Translator
from uniquebible.util.HBN import HBN
from uniquebible.util.terminal_text_editor import TextEditor
from uniquebible.util.terminal_system_command_prompt import SystemCommandPrompt
if not config.runMode == "stream":
    from uniquebible.util.terminal_mode_dialogs import TerminalModeDialogs
    from uniquebible.util.get_path_prompt import GetPath
from uniquebible.util.PromptValidator import NumberValidator, NoAlphaValidator
from uniquebible.util.prompt_shared_key_bindings import prompt_shared_key_bindings
from uniquebible.util.prompt_multiline_shared_key_bindings import prompt_multiline_shared_key_bindings
from uniquebible.util.ConfigUtil import ConfigUtil
from uniquebible.util.exlbl import allLocations

if not config.runMode == "stream":
    from prompt_toolkit import PromptSession, prompt, print_formatted_text, HTML
    from prompt_toolkit.shortcuts import clear, confirm
    from prompt_toolkit.filters import Condition
    #from prompt_toolkit.application import run_in_terminal
    from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
    from prompt_toolkit.completion import WordCompleter, NestedCompleter, ThreadedCompleter, FuzzyCompleter
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.styles import Style
    #from prompt_toolkit.auto_suggest import AutoSuggestFromHistory


class LocalCliHandler:

    def __init__(self, command="John 3:16", allowPrivateData=True):
        if config.terminalUseMarvelDataPrivate and allowPrivateData:
            config.defaultMarvelData = config.marvelData
            config.marvelData = config.marvelDataPrivate
        try:
            self.textCommandParser = TextCommandParser(RemoteCliMainWindow())
        except:
            self.textCommandParser = TextCommandParser(None)
        self.crossPlatform = CrossPlatform()
        self.crossPlatform.setupResourceLists()
        self.html = "<ref >Unique Bible App</ref>"
        self.plainText = "Unique Bible App"
        if not config.runMode == "stream":
            self.setupDialogs()
        self.audioPlayer = None
        self.command = command
        self.dotCommands = {} if config.runMode == "stream" else self.getDotCommands()
        self.addShortcuts()
        if not config.runMode == "stream":
            self.initPromptElements()
        self.setOsOpenCmd()
        try:
            self.ttsLanguages = self.getTtsLanguages()
            self.ttsLanguageCodes = list(self.ttsLanguages.keys())
        except:
            pass
        self.bibleBooks = BibleBooks()
        abbReferences, bcvReferences = self.bibleBooks.getAllKJVreferences()
        self.allKJVreferences = self.getDummyDict(abbReferences, ",")
        self.allKJVreferencesBcv1 = self.getDummyDict(bcvReferences)
        self.allKJVreferencesBcv2 = self.getDummyDict(bcvReferences, ":::")
        self.unsupportedCommands = ["_mc", "_mastercontrol", "epub", "anypdf", "searchpdf", "pdffind", "pdf", "docx", "_savepdfcurrentpage", "searchallbookspdf", "readbible", "searchhighlight", "parallel", "_editfile", "_openfile", "_uba", "opennote", "_history", "_historyrecord", "_highlight"]
        if not WebtopUtil.isPackageInstalled("w3m"):
            config.terminalBibleParallels = False
            self.unsupportedCommands.append("sidebyside")
        try:
            self.ttsCommandKeyword = self.getDefaultTtsKeyword().lower()
            self.unsupportedCommands.append("gtts" if self.ttsCommandKeyword == "speak" else "speak")
        except:
            pass
        self.startupException1 = [config.terminal_cancel_action, ".", ".ed", ".sys", ".system", ".quit", ".q", ".restart", ".z", ".togglepager", ".filters", ".toggleclipboardmonitor", ".history", ".update", ".find", ".sa", ".sas", ".read", ".readsync", ".download", ".paste", ".share", ".copy", ".copyhtml", ".nano", ".vi", ".vim", ".searchbible", ".starthttpserver", ".downloadyoutube", ".web", ".gtts", ".portablepython", ".textfile"]
        self.startupException2 = "^(_setconfig:::|\.edit|\.change|\.toggle|\.stop|\.exec|mp3:::|mp4:::|cmd:::|\.backup|\.restore|gtts:::|speak:::|download:::|read:::|readsync:::|semantic:::)"
        #config.cliTtsProcess = None
        config.audio_playing_file = os.path.join("temp", "000_audio_playing.txt")
        if not config.runMode == "stream":
            self.getPath = GetPath(
                cancel_entry=config.terminal_cancel_action,
                promptIndicatorColor=config.terminalPromptIndicatorColor2,
                promptEntryColor=config.terminalCommandEntryColor2,
                subHeadingColor=config.terminalHeadingTextColor,
                itemColor=config.terminalResourceLinkColor,
            )
            self.shareKeyBindings()

    def setupDialogs(self):
        self.dialogs = TerminalModeDialogs(self)
        self.changebible = self.dialogs.changebible
        self.changebibles = self.dialogs.changebibles
        self.changefavouritebible1 = self.dialogs.changefavouritebible1
        self.changefavouritebible2 = self.dialogs.changefavouritebible2
        self.changefavouritebible3 = self.dialogs.changefavouritebible3
        self.changefavouriteoriginalbible = self.dialogs.changefavouriteoriginalbible
        self.changecommentary = self.dialogs.changecommentary
        self.changelexicon = self.dialogs.changelexicon
        self.changedictionary = self.dialogs.changedictionary
        self.changethirdpartydictionary = self.dialogs.changethirdpartydictionary
        self.changeencyclopedia = self.dialogs.changeencyclopedia
        self.changeconcordance = self.dialogs.changeconcordance
        self.changereferencebook = self.dialogs.changereferencebook
        self.changereferencebookchapter = self.dialogs.changereferencebookchapter
        self.changenoteeditor = self.dialogs.changenoteeditor
        self.changebiblesearchmode = self.dialogs.changebiblesearchmode
        self.displayFeatureMenu = self.dialogs.displayFeatureMenu
        self.changettslanguage1 = self.dialogs.changettslanguage1
        self.changettslanguage2 = self.dialogs.changettslanguage2
        self.changettslanguage3 = self.dialogs.changettslanguage3
        self.changettslanguage4 = self.dialogs.changettslanguage4

    def shareKeyBindings(self):
        this_key_bindings = KeyBindings()
        @this_key_bindings.add("c-q")
        def _(event):
            event.app.current_buffer.text = config.terminal_cancel_action
            event.app.current_buffer.validate_and_handle()

        self.prompt_shared_key_bindings = merge_key_bindings([
            prompt_shared_key_bindings,
            this_key_bindings,
        ])
        self.prompt_multiline_shared_key_bindings = merge_key_bindings([
            prompt_shared_key_bindings,
            prompt_multiline_shared_key_bindings,
            this_key_bindings,
        ])

    def getToolBar(self, multiline=False):
        if multiline:
            return f" [ctrl+q] {config.terminal_cancel_action}; 'escape+enter' to complete entry "
        return f" [ctrl+q] {config.terminal_cancel_action} "

    # Set text-to-speech default language
    def getTtsLanguages(self):
        # Support Android Google TTS if available
        if config.runMode == "terminal" and config.terminalEnableTermuxAPI:
            config.isGoogleCloudTTSAvailable = True
        if config.isGoogleCloudTTSAvailable and config.ttsDefaultLangauge == "en":
            config.ttsDefaultLangauge = "en-GB"
        return self.crossPlatform.getTtsLanguages()

    def setOsOpenCmd(self):
        if config.terminalEnableTermuxAPI:
            config.open = "termux-share"
        elif platform.system() == "Linux":
            config.open = config.openLinux
        elif platform.system() == "Darwin":
            config.open = config.openMacos
        elif platform.system() == "Windows":
            config.open = config.openWindows

    def is_CJK(self, text):
        for char in text:
            if 'CJK' in unicodedata.name(char):
                return True
        return False

    # wrap html text at spaces
    def getWrappedHTMLText(self, text, terminal_width=None):
        if not " " in text:
            return text
        if terminal_width is None:
            terminal_width = shutil.get_terminal_size().columns
        self.wrappedText = ""
        self.lineWidth = 0

        def addWords(words):
            words = words.split(" ")
            for index, item in enumerate(words):
                isLastItem = (len(words) - index == 1)

                if self.is_CJK(item):
                    for iIndex, i in enumerate(item):
                        isSpaceItem = (not isLastItem and (len(item) - iIndex == 1))
                        iWidth = self.getStringWidth(i)
                        if isSpaceItem:
                            newLineWidth = self.lineWidth + iWidth + 1
                        else:
                            newLineWidth = self.lineWidth + iWidth
                        if newLineWidth > terminal_width:
                            self.wrappedText += f"\n{i} " if isSpaceItem else f"\n{i}"
                            self.lineWidth = iWidth + 1 if isSpaceItem else iWidth
                        else:
                            self.wrappedText += f"{i} " if isSpaceItem else i
                            self.lineWidth += iWidth + 1 if isSpaceItem else iWidth
                else:
                    itemWidth = self.getStringWidth(item)
                    if isLastItem:
                        newLineWidth = self.lineWidth + itemWidth
                    else:
                        newLineWidth = self.lineWidth + itemWidth + 1
                    if newLineWidth > terminal_width:
                        self.wrappedText += f"\n{item}" if isLastItem else f"\n{item} "
                        self.lineWidth = itemWidth if isLastItem else itemWidth + 1
                    else:
                        self.wrappedText += item if isLastItem else f"{item} "
                        self.lineWidth += itemWidth if isLastItem else itemWidth + 1
        
        def processLine(lineText):
            if re.search("<[^<>]+?>", lineText):
                # handle html/xml tags
                chunks = lineText.split(">")
                totalChunks = len(chunks)
                for index, chunk in enumerate(chunks):
                    isLastChunk = (totalChunks - index == 1)
                    if isLastChunk:
                        addWords(chunk)
                    else:
                        tag = True if "<" in chunk else False
                        if tag:
                            nonTag, tagContent = chunk.rsplit("<", 1)
                            addWords(nonTag)
                            self.wrappedText += f"<{tagContent}>"
                        else:
                            addWords(f"{chunk}>")
            else:
                addWords(lineText)

        lines = text.split("\n")
        totalLines = len(lines)
        for index, line in enumerate(lines):
            isLastLine = (totalLines - index == 1)
            processLine(line)
            if not isLastLine:
                self.wrappedText += "\n"
                self.lineWidth = 0
        
        return self.wrappedText

    def getStringWidth(self, text): 
        width = 0 
        for character in text: 
            width += wcwidth.wcwidth(character) 
        return width

    def print(self, content):
        if isinstance(content, str) and content.startswith("[MESSAGE]"):
            content = content[9:]
        if config.terminalWrapWords:
            content = self.getWrappedHTMLText(content)
        try:
            print_formatted_text(HTML(content))
        except:
            print(TextUtil.convertHtmlTagToColorama(content))

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

        bible_chat_history = os.path.join(os.getcwd(), "terminal_history", "bible_chat")
        find_history = os.path.join(os.getcwd(), "terminal_history", "find")
        module_history_concordance = os.path.join(os.getcwd(), "terminal_history", "concordance")
        module_history_books = os.path.join(os.getcwd(), "terminal_history", "books")
        module_history_bibles = os.path.join(os.getcwd(), "terminal_history", "bibles")
        module_history_multiple_bibles = os.path.join(os.getcwd(), "terminal_history", "muliple_bibles")
        module_history_topics = os.path.join(os.getcwd(), "terminal_history", "topics")
        module_history_dictionaries = os.path.join(os.getcwd(), "terminal_history", "dictionaries")
        module_history_encyclopedia = os.path.join(os.getcwd(), "terminal_history", "encyclopedia")
        module_history_lexicons = os.path.join(os.getcwd(), "terminal_history", "lexicons")
        module_history_thirdDict = os.path.join(os.getcwd(), "terminal_history", "thirdPartyDictionaries")
        module_history_commentaries = os.path.join(os.getcwd(), "terminal_history", "commentaries")
        search_bible_history = os.path.join(os.getcwd(), "terminal_history", "search_bible")
        search_strong_bible_history = os.path.join(os.getcwd(), "terminal_history", "search_strong_bible")
        search_bible_book_range_history = os.path.join(os.getcwd(), "terminal_history", "search_bible_book_range")
        config_history = os.path.join(os.getcwd(), "terminal_history", "config")
        live_filter = os.path.join(os.getcwd(), "terminal_history", "live_filter")
        tts_language_history = os.path.join(os.getcwd(), "terminal_history", "tts_language")
        watson_translate_from_language_history = os.path.join(os.getcwd(), "terminal_history", "watson_translate_from_language")
        watson_translate_to_language_history = os.path.join(os.getcwd(), "terminal_history", "watson_translate_to_language")
        google_translate_from_language_history = os.path.join(os.getcwd(), "terminal_history", "google_translate_from_language")
        google_translate_to_language_history = os.path.join(os.getcwd(), "terminal_history", "google_translate_to_language")
        python_string_history = os.path.join(os.getcwd(), "terminal_history", "python_string")
        python_file_history = os.path.join(os.getcwd(), "terminal_history", "python_file")
        #system_command_history = os.path.join(os.getcwd(), "terminal_history", "system_command")

        self.terminal_bible_chat_session = PromptSession(history=FileHistory(bible_chat_history))
        self.terminal_live_filter_session = PromptSession(history=FileHistory(live_filter))
        self.terminal_concordance_selection_session = PromptSession(history=FileHistory(module_history_concordance))
        self.terminal_books_selection_session = PromptSession(history=FileHistory(module_history_books))
        self.terminal_find_session = PromptSession(history=FileHistory(find_history))
        self.terminal_search_strong_bible_session = PromptSession(history=FileHistory(search_strong_bible_history))
        self.terminal_search_bible_session = PromptSession(history=FileHistory(search_bible_history))
        self.terminal_search_bible_book_range_session = PromptSession(history=FileHistory(search_bible_book_range_history))
        self.terminal_bible_selection_session = PromptSession(history=FileHistory(module_history_bibles))
        self.terminal_multiple_bible_selection_session = PromptSession(history=FileHistory(module_history_multiple_bibles))
        self.terminal_topics_selection_session = PromptSession(history=FileHistory(module_history_topics))
        self.terminal_dictionary_selection_session = PromptSession(history=FileHistory(module_history_dictionaries))
        self.terminal_encyclopedia_selection_session = PromptSession(history=FileHistory(module_history_encyclopedia))
        self.terminal_lexicons_selection_session = PromptSession(history=FileHistory(module_history_lexicons))
        self.terminal_thridPartyDictionaries_selection_session = PromptSession(history=FileHistory(module_history_thirdDict))
        self.terminal_commentary_selection_session = PromptSession(history=FileHistory(module_history_commentaries))
        self.terminal_config_selection_session = PromptSession(history=FileHistory(config_history))
        self.terminal_tts_language_session = PromptSession(history=FileHistory(tts_language_history))
        self.terminal_google_translate_from_language_session = PromptSession(history=FileHistory(google_translate_from_language_history))
        self.terminal_google_translate_to_language_session = PromptSession(history=FileHistory(google_translate_to_language_history))
        self.terminal_python_string_session = PromptSession(history=FileHistory(python_string_history))
        self.terminal_python_file_session = PromptSession(history=FileHistory(python_file_history))
        self.terminal_watson_translate_from_language_session = PromptSession(history=FileHistory(watson_translate_from_language_history))
        self.terminal_watson_translate_to_language_session = PromptSession(history=FileHistory(watson_translate_to_language_history))
        #self.terminal_system_command_session = PromptSession(history=FileHistory(system_command_history))

    def getShortcuts(self):
        return {
            ".a": config.terminal_dot_a,
            ".b": config.terminal_dot_b,
            ".c": config.terminal_dot_c,
            ".d": config.terminal_dot_d,
            ".e": config.terminal_dot_e,
            ".f": config.terminal_dot_f,
            ".g": config.terminal_dot_g,
            ".h": config.terminal_dot_h,
            ".i": config.terminal_dot_i,
            ".j": config.terminal_dot_j,
            ".k": config.terminal_dot_k,
            ".l": config.terminal_dot_l,
            ".m": config.terminal_dot_m,
            ".n": config.terminal_dot_n,
            ".o": config.terminal_dot_o,
            ".p": config.terminal_dot_p,
            #".q": config.terminal_dot_q,
            ".r": config.terminal_dot_r,
            ".s": config.terminal_dot_s,
            ".t": config.terminal_dot_t,
            ".u": config.terminal_dot_u,
            ".v": config.terminal_dot_v,
            ".w": config.terminal_dot_w,
            ".x": config.terminal_dot_x,
            ".y": config.terminal_dot_y,
            #".z": config.terminal_dot_z,
        }

    def addShortcuts(self):
        for key, value in self.getShortcuts().items():
            value = value.strip()
            if value:
                self.dotCommands[key] = (f"an alias to '{value}'", partial(self.getContent, value))

    def getDotCommands(self):
        if config.runMode == "stream":
            return {}
        dotCommands = {
            config.terminal_cancel_action: ("cancel action in current prompt", self.cancelAction),
            ".togglecolorbrightness": ("toggle color brightness", self.togglecolorbrightness),
            ".togglecolourbrightness": ("an alias to '.togglecolorbrightness'", self.togglecolorbrightness),
            ".togglepager": ("toggle paging for text output", self.togglePager),
            ".toggleclipboardmonitor": ("toggle paging for text output", self.toggleClipboardMonitor),
            ".togglecomparison": ("toggle bible comparison view", self.togglebiblecomparison),
            ".toggleparallels": ("toggle bible parallel view", self.togglebibleparallels),
            ".togglechapterlayout": ("toggle bible chapter plain layout", self.toggleBibleChapterFormat),
            ".toggleplainbiblechaptersubheadings": ("toggle bible chapter subheadings in plain layout", self.toggleaddTitleToPlainChapter),
            ".togglefavouriteverses": ("toggle favourite bible verses in displaying multiple verses", self.toggleaddFavouriteToMultiRef),
            ".togglefavoriteverses": ("an alias to '.togglefavouriteverses'", self.toggleaddFavouriteToMultiRef),
            ".toggleversenumber": ("toggle verse number display", self.toggleshowVerseReference),
            ".toggleusernoteindicator": ("toggle user note indicator display", self.toggleshowUserNoteIndicator),
            ".togglenoteindicator": ("toggle bible note indicator display", self.toggleshowBibleNoteIndicator),
            ".togglelexicalentries": ("toggle lexical entry display", self.togglehideLexicalEntryInBible),
            ".stopaudio": ("stop audio", self.stopAudio),
            ".sa": ("an alias to '.stopaudio'", self.stopAudio),
            ".stopaudiosync": ("stop audio with text synchronisation", self.removeAudioPlayingFile),
            ".sas": ("an alias to '.stopaudiosync'", self.removeAudioPlayingFile),
            ".read": ("play audio", self.read),
            ".readsync": ("play audio with text synchronisation", self.readsync),
            ".customisefilters": ("customise filters", self.customisefilters),
            ".customizefilters": ("an alias to '.customisefilters'", self.customisefilters),
            ".run": ("run copied text as command", self.runclipboardtext),
            ".forward": ("one bible chapter forward", self.forward),
            ".backward": ("one bible chapter backward", self.backward),
            ".swap": ("swap to a favourite bible", self.swap),
            ".web": ("web version", self.web),
            ".share": ("copy a web link for sharing", self.share),
            ".tts": ("text to speech ANY", lambda: self.tts(False)),
            ".tts1": ("text to speech 1", lambda: self.tts(False, defaultLanguage=config.ttsDefaultLangauge)),
            ".tts2": ("text to speech 2", lambda: self.tts(False, defaultLanguage=config.ttsDefaultLangauge2)),
            ".tts3": ("text to speech 3", lambda: self.tts(False, defaultLanguage=config.ttsDefaultLangauge3)),
            ".tts4": ("text to speech 4", lambda: self.tts(False, defaultLanguage=config.ttsDefaultLangauge4)),
            ".ttscopiedtext": ("copied text to speech ANY", self.tts),
            ".ttscopiedtext1": ("copied text to speech 1", lambda: self.tts(True, defaultLanguage=config.ttsDefaultLangauge)),
            ".ttscopiedtext2": ("copied text to speech 2", lambda: self.tts(True, defaultLanguage=config.ttsDefaultLangauge2)),
            ".ttscopiedtext3": ("copied text to speech 3", lambda: self.tts(True, defaultLanguage=config.ttsDefaultLangauge3)),
            ".ttscopiedtext4": ("copied text to speech 4", lambda: self.tts(True, defaultLanguage=config.ttsDefaultLangauge4)),
            ".ttsc": ("an alias to '.ttscopiedtext'", self.tts),
            ".paste": ("copied text", self.getclipboardtext),
            ".copy": ("copy the last opened content", self.copy),
            ".copyhtml": ("copy the last opened content in html format", self.copyHtml),
            ".quicksearchcopiedtext": ("run quick search on copied text", self.quickSearch),
            ".qsc": ("an alias to '.quicksearchcopiedtext'", self.quickSearch),
            ".quickopencopiedtext": ("run quick open on copied text", self.quickopen),
            ".qoc": ("an alias to '.quickopencopiedtext'", self.quickopen),
            ".quickeditcopiedtext": ("run quick edit on copied text", self.quickedit),
            ".qec": ("an alias to '.quickeditcopiedtext'", self.quickedit),
            ".find": ("search the lastest content", self.find),
            ".findcopiedtext": ("search the copied text", self.findCopiedText),
            ".findc": ("an alias to '.findcopiedtext'", self.findCopiedText),
            ".history": ("history records", self.history),
            ".latestchanges": ("latest changes", self.latestchanges),
            ".latest": ("the lastest selection", self.latest),
            ".latestbible": ("the lastest bible chapter", self.latestBible),
            ".update": ("update Unique Bible App to the latest version", self.update),
            ".commands": ("available commands", self.commands),
            ".config": ("UBA configurations", self.config),
            ".showbibles": ("installed bibles", self.showbibles),
            ".showstrongbibles": ("installed bibles with Strong's numbers", self.showstrongbibles),
            ".showbiblebooks": ("bible book list", self.showbiblebooks),
            ".showbibleabbreviations": ("bible book name list", self.showbibleabbreviations),
            ".showbiblechapters": ("bible chapter list", self.showbiblechapters),
            ".showbibleverses": ("bible verse list", self.showbibleverses),
            ".showcommentaries": ("installed commentaries", self.showcommentaries),
            ".showtopics": ("installed bible topic modules", self.showtopics),
            ".showlexicons": ("installed lexicons", self.showlexicons),
            ".showencyclopedia": ("installed encyclopedia", self.showencyclopedia),
            ".showdictionaries": ("installed dictionaries", self.showdictionaries),
            ".showthirdpartydictionary": ("installed third-party dictionaries", self.showthirdpartydictionary),
            ".showreferencebooks": ("installed reference books", self.showreferencebooks),
            ".showdata": ("installed data", self.showdata),
            ".showttslanguages": ("text-to-speech languages", self.showttslanguages),
            ".showdownloads": ("available downloads", self.showdownloads),
            ".downloadyoutube": ("download youtube file", self.downloadyoutube),
            ".downloadbibleaudio": ("download bible audio", self.downloadbibleaudio),
            ".bible": ("bible", self.openbible),
            ".biblenote": ("bible module note", self.openbiblemodulenote),
            ".original": ("Hebrew & Greek bibles", self.original),
            ".ohgb": ("hebrew & Greek bible", lambda: self.getContent("TEXT:::OHGB")),
            ".ohgbi": ("hebrew & Greek bible [interlinear]", lambda: self.getContent("TEXT:::OHGBi")),
            ".mob": ("hebrew & Greek original bible", lambda: self.web(".mob", False)),
            ".mib": ("hebrew & Greek interlinear bible", lambda: self.web(".mib", False)),
            ".mtb": ("hebrew & Greek trilingual bible", lambda: self.web(".mtb", False)),
            ".mpb": ("hebrew & Greek parallel bible", lambda: self.web(".mpb", False)),
            ".mab": ("hebrew & Greek annotated bible", lambda: self.web(".mab", False)),
            ".lxx1i": ("Septuagint interlinear I", lambda: self.web("TEXT:::LXX1i", False)),
            ".lxx2i": ("Septuagint interlinear II", lambda: self.web("TEXT:::LXX2i", False)),
            ".365": ("365-day bible reading plan", self.open365readingplan),
            ".commentary": ("commentary", self.opencommentary),
            ".referencebook": ("reference book", self.openreferencebook),
            ".audio": ("bible audio", self.openbibleaudio),
            ".booknote": ("bible book note", lambda: self.openbookfeature("OPENBOOKNOTE")),
            ".chapternote": ("bible chapter note", lambda: self.openchapterfeature("OPENCHAPTERNOTE")),
            ".versenote": ("bible verse note", lambda: self.openversefeature("OPENVERSENOTE")),
            ".journal": ("journal", lambda: self.journalFeature("OPENJOURNAL")),
            ".promises": ("bible promises", lambda: self.openTools2("promises")),
            ".parallels": ("bible parallels", lambda: self.openTools2("parallels")),
            #".names": ("bible names", lambda: self.openTools2("names")),
            ".names": ("bible names", self.names),
            ".characters": ("bible characters", self.characters),
            ".locations": ("bible locations", self.locations),
            ".exlbp": ("exhaustive library of bible people", lambda: self.openTools2("characters")),
            ".exlbl": ("exhaustive library of bible locations", lambda: self.openTools2("locations")),
            ".maps": ("bible maps", self.openmaps),
            ".customisemaps": ("customise bible maps", self.customisemaps),
            ".customizemaps": ("an alias to '.customisemap'", self.customisemaps),
            ".distance": ("distance between two locations", self.distance),
            ".data": ("bible data", self.opendata),
            ".timelines": ("bible timelines", lambda: self.web(".timelineMenu", False)),
            ".topics": ("bible topics", lambda: self.openTools("TOPICS", self.showtopics)),
            ".dictionaries": ("dictionaries", lambda: self.openTools("DICTIONARY", self.showdictionaries)),
            ".encyclopedia": ("encyclopedia", lambda: self.openTools("ENCYCLOPEDIA", self.showencyclopedia)),
            ".lexicons": ("lexicons", lambda: self.openTools("LEXICON", self.showlexicons)),
            ".concordancebybook": ("Hebrew / Greek concordance sorted by books", lambda: self.openTools("LEXICON", self.showlexicons, "ConcordanceBook")),
            ".concordancebymorphology": ("Hebrew / Greek concordance sorted by morphology", lambda: self.openTools("LEXICON", self.showlexicons, "ConcordanceMorphology")),
            ".thirdpartydictionaries": ("third-party dictionaries", lambda: self.openTools("THIRDDICTIONARY", self.showthirdpartydictionary)),
            ".3dict": ("an alias to '.thirdpartydictionaries'", lambda: self.openTools("THIRDDICTIONARY", self.showthirdpartydictionary)),
            ".editbooknote": ("edit bible book note", lambda: self.openbookfeature("EDITBOOKNOTE")),
            ".editchapternote": ("edit bible chapter note", lambda: self.openchapterfeature("EDITCHAPTERNOTE")),
            ".editversenote": ("edit bible verse note", lambda: self.openversefeature("EDITVERSENOTE")),
            ".editjournal": ("edit journal", lambda: self.journalFeature("EDITJOURNAL")),
            ".quickedit": ("quick edit", lambda: self.quickedit(False)),
            ".qe": ("an alias to '.quickedit'", lambda: self.quickedit(False)),
            ".searchbooknote": ("search bible book note", lambda: self.searchNote("SEARCHBOOKNOTE")),
            ".searchchapternote": ("search bible chapter note", lambda: self.searchNote("SEARCHCHAPTERNOTE")),
            ".searchversenote": ("search bible verse note", lambda: self.searchNote("SEARCHVERSENOTE")),
            ".searchjournal": ("search journal", lambda: self.searchNote("SEARCHJOURNAL")),
            #".searchpromises": ("search bible promises", lambda: self.searchTools2("promises")),
            #".searchparallels": ("search bible parallels", lambda: self.searchTools2("parallels")),
            #".searchnames": ("search bible names", lambda: self.searchTools2("names")),
            #".searchcharacters": ("search bible characters", lambda: self.searchTools2("characters")),
            #".searchlocations": ("search bible locations", lambda: self.searchTools2("locations")),
            #".searchdictionaries": ("search dictionaries", lambda: self.searchTools("DICTIONARY", self.showdictionaries)),
            #".searchencyclopedia": ("search encyclopedia", lambda: self.searchTools("ENCYCLOPEDIA", self.showencyclopedia)),
            #".searchlexicons": ("search lexicons", lambda: self.searchTools("LEXICON", self.showlexicons)),
            ".searchlexiconcontent": ("search lexicons reversely", lambda: self.searchTools("REVERSELEXICON", self.showlexicons)),
            ".searchreferencebooks": ("search reference books", lambda: self.searchTools("BOOK", self.showreferencebooks)),
            #".searchtopics": ("search topics", lambda: self.searchTools("TOPICS", self.showtopics)),
            #".searchthirdpartydictionaries": ("search third-party dictionaries", lambda: self.searchTools("THIRDDICTIONARY", self.showthirdpartydictionary)),
            #".search3dict": ("an alias to '.searchthirdpartydictionaries'", lambda: self.searchTools("THIRDDICTIONARY", self.showthirdpartydictionary)),
            ".searchconcordance": ("search concordance", self.searchconcordance),
            ".quicksearch": ("quick search", lambda: self.quickSearch(False)),
            ".qs": ("an alias to '.quicksearch'", lambda: self.quickSearch(False)),
            ".crossreference": ("cross reference", self.openversefeature),
            ".comparison": ("verse comparison", lambda: self.openversefeature("COMPARE")),
            ".difference": ("verse comparison with differences", lambda: self.openversefeature("DIFFERENCE")),
            ".tske": ("Treasury of Scripture Knowledge (Enhanced)", lambda: self.openversefeature("TSKE")),
            ".verseindex": ("verse index", lambda: self.openversefeature("INDEX")),
            ".combo": ("combination of translation, discourse and words features", lambda: self.openversefeature("COMBO")),
            ".words": ("all word data in a single verse", lambda: self.openversefeature("WORDS")),
            ".word": ("Hebrew / Greek word data", lambda: self.readword(dataOnly=True)),
            ".discourse": ("discourse features", lambda: self.openversefeature("DISCOURSE")),
            ".translation": ("original word translation", lambda: self.openversefeature("TRANSLATION")),
            ".overview": ("chapter overview", self.openchapterfeature),
            ".summary": ("chapter summary", lambda: self.openchapterfeature("SUMMARY")),
            ".chapterindex": ("chapter index", lambda: self.openchapterfeature("CHAPTERINDEX")),
            ".introduction": ("book introduction", self.openbookfeature),
            ".dictionarybookentry": ("bible book entry in dictionary", lambda: self.openbookfeature("dictionary")),
            ".encyclopediabookentry": ("bible book entry in encyclopedia", lambda: self.openbookfeature("encyclopedia")),
            ".bookfeatures": ("bible book features", self.openbookfeatures),
            ".chapterfeatures": ("bible chapter features", self.openchapterfeatures),
            ".versefeatures": ("bible verse features", self.openversefeatures),
            ".wordfeatures": ("Hebrew / Greek word features", self.openwordfeatures),
            ".quickopen": ("quick open", lambda: self.quickopen(False)),
            ".readword": ("read Hebrew or Greek word", self.readword),
            ".readlexeme": ("read Hebrew or Greek lexeme", lambda: self.readword(True)),
            ".qo": ("an alias to '.quickopen'", lambda: self.quickopen(False)),
            ".standardcommands": ("standard UBA command", self.standardcommands),
            ".terminalcommands": ("terminal mode commands", self.terminalcommands),
            ".aliases": ("terminal mode command shortcuts", self.commandAliases),
            ".keys": ("keyboard shortcuts", self.keys),
            ".menu": ("master menu", self.menu),
            ".my": ("my menu", self.my),
            ".info": ("information", self.info),
            ".speak": ("speak ...", self.speak),
            ".translate": ("translate ...", self.translate),
            ".open": ("open ...", self.open),
            ".search": ("search ...", self.search),
            ".note": ("note / journal", self.accessNoteFeatures),
            ".edit": ("edit ...", self.edit),
            ".quick": ("quick features", self.quick),
            ".control": ("control", self.control),
            ".toggle": ("toggle ...", self.toggle),
            ".clipboard": ("copy / paste ...", self.clipboard),
            ".clip": ("an alias to '.clipboard'", self.clipboard),
            ".change": ("change ...", self.change),
            ".tools": ("tools", self.tools),
            ".python": ("python tools", self.python),
            ".plugins": ("plugins", self.plugins),
            ".howto": ("how-to", self.howto),
            ".maintain": ("maintain ...", self.maintain),
            ".download": ("download ...", self.download),
            ".backup": ("backup ...", self.backup),
            ".restore": ("restore ...", self.restore),
            ".help": ("help", self.help),
            ".filters": ("filters", self.filters),
            ".wiki": ("online wiki page", self.wiki),
            ".quickstart": ("how to quick start", lambda: self.readHowTo("quick start")),
            ".helpinstallmicro": ("how to install micro", lambda: self.readHowTo("install micro")),
            #".w3m": ("html content in w3m", lambda: self.cliTool("w3m -T text/html", self.html)),
            #".lynx": ("html content in lynx", lambda: self.cliTool("lynx -stdin", self.html)),
            ".textfile": ("read text file", self.opentext),
            ".edittextfile": ("edit text file", lambda: self.opentext(True)),
            ".extract": ("extract bible references from the latest content", self.extract),
            ".extractcopiedtext": ("extract bible references from copied text", self.extractcopiedtext),
            ".editor": ("built-in text editor", self.cliTool),
            ".ed": ("an alias to '.editor'", self.cliTool),
            ".editnewfile": ("edit a new file", lambda: self.cliTool(config.terminalNoteEditor)),
            ".editcontent": ("edit the latest content", lambda: self.cliTool(config.terminalNoteEditor, self.getPlainText())),
            ".editconfig": ("edit 'config.py'", lambda: self.editConfig(config.terminalNoteEditor)),
            ".editfilters": ("edit saved filters", self.editfilters),
            ".applyfilters": ("apply saved filters", self.applyfilters),
            ".searchbible": ("search bible", self.searchbible),
            ".whatis": ("command description", self.whatis),
            ".starthttpserver": ("start UBA http-server", self.starthttpserver),
            ".stophttpserver": ("stop UBA http-server", self.stophttpserver),
            ".backupnotes": ("backup note database file", lambda: self.sendFile("marvelData/note.sqlite")),
            ".backupjournals": ("backup journal database file", lambda: self.sendFile("marvelData/journal.sqlite")),
            ".restorenotes": ("restore note database file", lambda: self.restoreFile("marvelData/note.sqlite")),
            ".restorejournals": ("restore journal database file", lambda: self.restoreFile("marvelData/journal.sqlite")),
            ".restorelastnotes": ("restore note database file", lambda: self.restoreLastFile("marvelData/note.sqlite")),
            ".restorelastjournals": ("restore journal database file", lambda: self.restoreLastFile("marvelData/journal.sqlite")),
            ".changemymenu": ("change my menu", self.changemymenu),
            #".changebible": ("change current bible version", lambda: self.changeDefaultModule("mainText", self.crossPlatform.textList, config.mainText, self.showbibles)),
            ".changebible": ("change current bible version", self.changebible),
            ".changebibles": ("change bible versions for comparison", self.changebibles),
            ".changefavouritebible1": ("change favourite bible version 1", self.changefavouritebible1),
            ".changefavouritebible2": ("change favourite bible version 2", self.changefavouritebible2),
            ".changefavouritebible3": ("change favourite bible version 3", self.changefavouritebible3),
            ".changefavouriteoriginalbible": ("change favourite Hebrew & Greek bible", self.changefavouriteoriginalbible),
            ".changecommentary": ("change default commentary module", self.changecommentary),
            ".changelexicon": ("change default lexicon", self.changelexicon),
            ".changedictionary": ("change default dictionary", self.changedictionary),
            ".changethirdpartydictionary": ("change default third-party dictionary", self.changethirdpartydictionary),
            ".changeencyclopedia": ("change default encyclopedia", self.changeencyclopedia),
            ".changeconcordance": ("change default concordance", self.changeconcordance),
            ".changereferencebook": ("change default reference book", self.changereferencebook),
            ".changereferencebookchapter": ("change default reference book chapter", self.changereferencebookchapter),
            ".changettslanguage1": ("change default text-to-speech language 1", self.changettslanguage1),
            ".changettslanguage2": ("change default text-to-speech language 2", self.changettslanguage2),
            ".changettslanguage3": ("change default text-to-speech language 3", self.changettslanguage3),
            ".changettslanguage4": ("change default text-to-speech language 4", self.changettslanguage4),
            ".changedefaultcommand": ("change default command", self.changeDefaultCommand),
            ".changebiblesearchmode": ("change default bible search mode", self.changebiblesearchmode),
            ".changenoteeditor": ("change default note editor", self.changenoteeditor),
            ".changecolors": ("change colors", self.changecolors),
            ".changecolours": ("an alias to '.changecolors'", self.changecolors),
            ".changeconfig": ("change UBA configurations", self.changeconfig),
            ".changeterminalmodeconfig": ("change UBA terminal mode configurations", lambda: self.changeconfig(True)),
            ".gitstatus": ("git status", self.gitstatus),
            ".calculate": ("calculator", self.calculate),
            ".exec": ("execute a python string", self.execPythonString),
            ".execfile": ("execute a python file", self.execFile),
            ".reload": ("reload the latest content", self.reload),
            ".restart": ("restart UBA", self.restartUBA),
            ".z": ("an alias to '.restart'", self.restartUBA),
            ".quit": ("quit UBA", self.quitUBA),
            ".q": ("an alias to '.quit'", self.quitUBA),
            ".googletranslate": ("run Google Translate", lambda: self.googleTranslate(False)),
            ".googletranslatecopiedtext": ("run Google Translate on copied text", self.googleTranslate),
            ".gt": ("an alias to '.googletranslate'", lambda: self.googleTranslate(False)),
            ".gtc": ("an alias to '.googletranslatecopiedtext'", self.googleTranslate),
            ".watsontranslate": ("run IBM Watson Translator", lambda: self.watsonTranslate(False)),
            ".watsontranslatecopiedtext": ("run IBM Watson Translator on copied text", self.watsonTranslate),
            ".wt": ("an alias to '.watsontranslate'", lambda: self.watsonTranslate(False)),
            ".wtc": ("an alias to '.watsontranslatecopiedtext'", self.watsonTranslate),
            #".portablepython": ("build portable python", self.buildPortablePython),
            ".system": ("system command prompt", SystemCommandPrompt().run),
            ".sys": ("an alias to '.system'", SystemCommandPrompt().run),
            ".clear": ("clear screen", self.clear_screen),
            ".wordnet": ("wordnet dictionary", self.wordnet),
            ".customize": ("an alias to '.customise'", self.customise),
            ".mp3": ("play mp3 files in music folder", self.mp3),
            ".allmp3": ("play all mp3 files in music folder", lambda: self.mp3(default="[ALL]")),
            ".mp4": ("play mp4 files in video folder", self.mp4),
            ".allmp4": ("play all mp4 files in video folder", lambda: self.mp4(default="[ALL]")),
            # dummy 
            ".all": ("all ...", self.all),
            ".apply": ("apply ...", self.apply),
            ".customise": ("customise ...", self.customise),
            ".google": ("google ...", self.google),
            ".watson": ("watson ...", self.watson),
        }
        if shutil.which("groqchat"):
            dotCommands[".chat"] = ("bible chat", self.bibleChat)
        return dotCommands

    def clear_screen(self):
        clear()

    def calculate(self):
        userInput = ""
        self.print("Calculate:")
        while not userInput == config.terminal_cancel_action:
            userInput = self.simplePrompt(validator=NoAlphaValidator())
            try:
                self.print(eval(userInput))
            except:
                pass
        return ""

    def editfilters(self):
        savedFiltersFile = os.path.join("terminal_mode", "filters.txt")
        changesMade = self.multilineEditor(filepath=savedFiltersFile)
        if changesMade:
            self.print("Filters updated!")

    def applyfilters(self):
        savedFiltersFile = os.path.join("terminal_mode", "filters.txt")
        if not os.path.isfile(savedFiltersFile):
            with open(savedFiltersFile, "w", encoding="utf-8") as fileObj:
                fileObj.write("jesus|christ\nGen \nJohn ")
        with open(savedFiltersFile, "r", encoding="utf-8") as input_file:
            savedFiltersFileContent = input_file.read()
        savedFilters = [i for i in savedFiltersFileContent.split("\n") if i.strip()]
        filters = self.dialogs.getMultipleSelection(options=savedFilters, descriptions=[], default_values=[savedFilters[0]], title="Apply Saved Filters", text="Select filters:")
        return self.customisefilters(filters) if filters else ""

    def customisefilters(self, defaultFilters=[]):
        try:
        #if True:
            savedFiltersFile = os.path.join("terminal_mode", "filters.txt")
            if not os.path.isfile(savedFiltersFile):
                with open(savedFiltersFile, "w", encoding="utf-8") as fileObj:
                    fileObj.write("jesus|christ\nGen \nJohn ")
            with open(savedFiltersFile, "r", encoding="utf-8") as input_file:
                savedFiltersFileContent = input_file.read()
            savedFilters = [i for i in savedFiltersFileContent.split("\n") if i.strip()]

            if defaultFilters:
                currentFilters = defaultFilters
            else:
                self.print(self.divider)
                self.print(TextUtil.htmlToPlainText("<h2>Saved Filters are:</h2>"))
                self.print(pprint.pformat(savedFilters))
                self.print(self.divider)
                self.print("Enter mulitple filters:")
                self.print("(enter each on a single line)")
                self.print("(newly added filters will be automatically saved)")
                userInput = self.terminal_live_filter_session.prompt(self.inputIndicator, key_bindings=self.prompt_multiline_shared_key_bindings, bottom_toolbar=self.getToolBar(True), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle, multiline=True).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                currentFilters = []
                for i in userInput.split("\n"):
                    if i.strip():
                        if not i in savedFilters:
                            savedFilters.append(i)
                        currentFilters.append(i)
            if not currentFilters:
                return self.reload()
            filteredText = []
            for line in self.plainText.split("\n"):
                match = True
                for f in currentFilters:
                    # check if any one of the filters is not matched
                    if not TextUtil.regexp(f, line):
                        match = False
                        break
                # display when a line matches all filters
                if match:
                    filteredText.append(line)
            # update saved filters
            with open(savedFiltersFile, "w", encoding="utf-8") as fileObj:
                fileObj.write("\n".join(sorted(savedFilters)))
            # display filtered text
            return self.displayOutputOnTerminal("\n".join(filteredText))
        except:
            self.print("Errors!")
        return ""

    def execPythonString(self):
        if config.terminalEnableTermuxAPI:
            if not self.fingerprint():
                return self.cancelAction()
        try:
            self.print(self.divider)
            self.print("Enter a python script:")
            userInput = self.terminal_python_string_session.prompt(self.inputIndicator, key_bindings=self.prompt_multiline_shared_key_bindings, bottom_toolbar=self.getToolBar(True), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle, multiline=True).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            exec(userInput, globals())
        except:
            self.print("Errors!")
        return ""

    def execFile(self):
        if config.terminalEnableTermuxAPI:
            if not self.fingerprint():
                return self.cancelAction()
        try:
            self.print(self.divider)
            userInput = self.getPath.getFilePath(check_isfile=True, empty_to_cancel=True)
            if userInput:
                self.execPythonFile(userInput)
            else:
                return self.cancelAction()
        except:
            self.print("Errors!")
        return ""

    def plugins(self, default="", accept_default=False):
        availablePlugins = FileUtil.fileNamesWithoutExtension(os.path.join(config.packageDir, "plugins", "terminal"), "py") + FileUtil.fileNamesWithoutExtension(os.path.join(config.ubaUserDir, "plugins", "terminal"), "py")
        if default and accept_default:
            userInput = self.simplePrompt(default=default, accept_default=accept_default)
        else:
            userInput = self.dialogs.getValidOptions(options=availablePlugins, title="Plugins", default=default)
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        try:
            filepath1 = os.path.join(config.packageDir, "plugins", "terminal", f"{userInput}.py")
            filepath2 = os.path.join(config.ubaUserDir, "plugins", "terminal", f"{userInput}.py")
            if os.path.isfile(filepath1):
                self.execPythonFile(filepath1)
            elif os.path.isfile(filepath2):
                self.execPythonFile(filepath2)
            else:
                return self.printInvalidOptionEntered()
            return ""
        except:
            return self.printInvalidOptionEntered()

    def mp3(self, default="", accept_default=False):
        vlcSpeed = config.vlcSpeed
        config.vlcSpeed = 1.0
        options = FileUtil.fileNamesWithoutExtension(config.musicFolder, "mp3")
        if default and accept_default:
            userInput = self.simplePrompt(default=default, accept_default=accept_default)
            userInput = [userInput]
        else:
            userInput = self.dialogs.getMultipleSelection(options=options, descriptions=[], title="Music", text="Select file(s):", default_values=options if default == "[ALL]" else [default])
        if not userInput:
            return self.cancelAction()
        try:
            playlist = [os.path.join(os.getcwd(), config.musicFolder, f"{i}.mp3") for i in userInput]
            self.textCommandParser.parent.playAudioBibleFilePlayList(playlist)
            config.vlcSpeed = vlcSpeed
            return ""
        except:
            config.vlcSpeed = vlcSpeed
            return self.printInvalidOptionEntered()

    def mp4(self, default="", accept_default=False):
        vlcSpeed = config.vlcSpeed
        config.vlcSpeed = 1.0
        options = FileUtil.fileNamesWithoutExtension(config.videoFolder, "mp4")
        if default and accept_default:
            userInput = self.simplePrompt(default=default, accept_default=accept_default)
            userInput = [userInput]
        else:
            userInput = self.dialogs.getMultipleSelection(options=options, descriptions=[], title="Video", text="Select file(s):", default_values=options if default == "[ALL]" else [default])
        if not userInput:
            return self.cancelAction()
        try:
            playlist = [os.path.join(os.getcwd(), config.videoFolder, f"{i}.mp4") for i in userInput]
            self.textCommandParser.parent.playAudioBibleFilePlayList(playlist)
            config.vlcSpeed = vlcSpeed
            return ""
        except:
            config.vlcSpeed = vlcSpeed
            return self.printInvalidOptionEntered()

    def wordnet(self):
        filepath = os.path.join(config.packageDir, "plugins", "terminal", "look up in wordnet.py")
        self.execPythonFile(filepath)
        return ""

    def howto(self):
        availableHowto = FileUtil.fileNamesWithoutExtension(os.path.join("terminal_mode", "how_to"), "md")
        userInput = self.dialogs.getValidOptions(options=availableHowto, title="How-to")
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        try:
            filepath = os.path.join("terminal_mode", "how_to", f"{userInput}.md")
            return self.readPlainTextFile(filepath)
        except:
            return self.printInvalidOptionEntered()

    def execPythonFile(self, script):
        self.crossPlatform.execPythonFile(script)

    # a dummy method to work with config.mainWindow.runTextCommand in some codes
    def runTextCommand(self, command):
        return self.getContent(command)

    # the method that runs UBA command
    def getContent(self, command, checkDotCommand=True):
        try:
        #if True:
            command = command.strip()
            # allow use of tts::: no matter which tts engine is in place
            if command.lower().startswith("tts:::"):
                command = f"{self.ttsCommandKeyword}{command[3:]}"
            # study window applies to Qt library users only
            if command.lower().startswith("study:::") or command.lower().startswith("studytext:::"):
                config.studyText, config.studyB, config.studyC, config.studyV = config.mainText, config.mainB, config.mainC, config.mainV
            originalCommand = command
            # Shortcuts to change chapter or verse or both chapter and verse for bible reading.
            if command:
                try:
                    # match a bible version
                    if command in self.crossPlatform.textList:
                        command = f"TEXT:::{command}"
                    # match a bible reference
                    bc = command.split(":", 1)
                    bci = [int(i) for i in bc if i]
                    if len(bc) == 2 and len(bci) == 1:
                        # Users specify a verse number, e.g. :16
                        if command.startswith(":"):
                            command = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, bci[0])
                        # Users specify a chapter number, e.g. 3:
                        elif command.endswith(":"):
                            command = self.textCommandParser.bcvToVerseReference(config.mainB, bci[0], 1)
                    # Users specify both a chapter number and a verse number, e.g. 3:16
                    elif len(bc) == 2 and len(bci) == 2:
                        command = self.textCommandParser.bcvToVerseReference(config.mainB, bci[0], bci[1])
                    if not originalCommand == command:
                        bibles = "_".join(config.compareParallelList)
                        prefix = f"COMPARE:::{bibles}:::" if config.terminalBibleComparison else "BIBLE:::"
                        command = f"{prefix}{command}"
                        self.printRunningCommand(command)
                except:
                    pass
            # Redirect heavy html content to web version.
            if not command.lower().startswith(".") and re.search('^(map:::|locations:::|qrcode:::|bible:::mab:::|bible:::mib:::|bible:::mob:::|bible:::mpb:::|bible:::mtb:::|text:::mab|text:::mib|text:::mob|text:::mpb|text:::mtb|study:::mab:::|study:::mib:::|study:::mob:::|study:::mpb:::|study:::mtb:::|studytext:::mab|studytext:::mib|studytext:::mob|studytext:::mpb|studytext:::mtb)', command.lower()):
                return self.web(command)
            # Dot commands
            if command == ".":
                return ""
            elif checkDotCommand and command.startswith("."):
                return self.getDotCommandContent(command.lower())
            # Non-dot commands
            _, content, _ = self.textCommandParser.parser(command, "cli")
            # keep record of last command
            self.command = command
            if config.bibleWindowContentTransformers:
                for transformer in config.bibleWindowContentTransformers:
                    content = transformer(content)
            if content:
                #self.crossPlatform.addHistoryRecord(view, command)
                self.html = content
            else:
                content = "Command processed!"
            # Convert html to plain text
            content = content.replace("<u><b>", "<u><b># ")
            plainText = TextUtil.htmlToPlainText(content).strip()
            self.plainText = "" if content == "Command processed!" else plainText
            # Update main text, b, c, v
            references = self.textCommandParser.extractAllVerses(command)
            if references:
                config.mainB, config.mainC, config.mainV, *_ = references[-1]
            return plainText
        except:
            #print(traceback.format_exc())
            return self.printInvalidOptionEntered()

    def fineTuneTextForWebBrowserDisplay(self, text=""):
        if not text:
            text = self.html
        if text.startswith("[BROWSER]"):
            text = text[9:]
        text = re.sub("「(Back|Fore|Style)\.[^「」]+?」|audiotrack|「tmvs [^「」]+?」|「/tmvs」", "", text)
        return text

    def displayOutputOnTerminal(self, content):
        if content.startswith("[BROWSER]"):
            html = self.fineTuneTextForWebBrowserDisplay()
            self.cliTool("w3m -T text/html -o confirm_qq=false", html)
        else:
            divider = self.divider
            if config.terminalEnablePager and not content in ("Command processed!", "INVALID_COMMAND_ENTERED") and not content.endswith("not supported in terminal mode.") and not content.startswith("[MESSAGE]"):
                try:
                    if config.terminalWrapWords:
                        content = self.getWrappedHTMLText(content)
                    pagerContent = TextUtil.convertHtmlTagToColorama(content)
                    pydoc.pipepager(pagerContent, cmd='less -R') if WebtopUtil.isPackageInstalled("less") else pydoc.pager(pagerContent)
                    # Windows users can install less command with scoop
                    # read: https://github.com/ScoopInstaller/Scoop
                    # instll scoop
                    # > iwr -useb get.scoop.sh | iex
                    # > scoop install aria2
                    # instll less
                    # > scoop install less
                except:
                    config.terminalEnablePager = False
                    self.print(divider)
                    self.print(content)
            else:
                if content.startswith("[MESSAGE]"):
                    content = content[9:]
                self.print(divider)
                self.print(content)
        self.checkAudioContent()

    def quitUBA(self):
        self.print("Closing ...")
        return ""

    def restartUBA(self):
        self.print("Restarting ...")
        return ""

    def getDotCommandContent(self, command):
        enteredCommand = command
        command = command.replace(" ", "")
        if command in self.dotCommands:
            return self.dotCommands[command][-1]()
        else:
            options = []
            descriptions = []
            for key, value in self.dotCommands.items():
                options.append(key)
                descriptions.append(value[0])
            # allow users to search for commands
            userInput = self.dialogs.getValidOptions(options=options, descriptions=descriptions, filter=command[1:])
            if userInput:
                return self.dotCommands[userInput][-1]()
            else:
                return self.getContent(enteredCommand, False)

    def getDummyDict(self, data, suffix="", furtherOptions=None):
        # set is supported in NestedCompleter but not preferred as set is unordered
        return {f"{i}{suffix}": furtherOptions for i in data} if furtherOptions is not None else {f"{i}{suffix}": None for i in data}

    def getCommandCompleterSuggestions(self, textCommandSuggestion=None):
        if textCommandSuggestion is None:
            textCommandSuggestion = self.getTextCommandSuggestion()
        suggestions = {}
        days365 = self.getDummyDict([(i + 1) for i in range(365)])
        for i in textCommandSuggestion:
            if re.sub(":::.*?$", "", i) in self.unsupportedCommands:
                pass
            elif i == ".backup":
                suggestions[i] = self.getDummyDict(["journals", "notes",])
            elif i == ".copy":
                suggestions[i] = self.getDummyDict(["html",])
            elif i == ".google":
                suggestions[i] = self.getDummyDict(["translate", "translatecopiedtext"])
            elif i == ".watson":
                suggestions[i] = self.getDummyDict(["translate", "translatecopiedtext"])
            elif i == ".all":
                suggestions[i] = self.getDummyDict(["mp3", "mp4"])
            elif i == ".apply":
                suggestions[i] = self.getDummyDict(["filters",])
            elif i == ".customise":
                suggestions[i] = self.getDummyDict(["maps", "filters",])
            elif i == ".customize":
                suggestions[i] = self.getDummyDict(["maps", "filters",])
            elif i == ".download":
                suggestions[i] = self.getDummyDict(["bibleaudio", "youtube",])
            elif i == ".extract":
                suggestions[i] = self.getDummyDict(["copiedtext",])
            elif i == ".find":
                suggestions[i] = self.getDummyDict(["copiedtext",])
            elif i == ".help":
                suggestions[i] = self.getDummyDict(["installmicro",])
            elif i == ".latest":
                suggestions[i] = self.getDummyDict(["bible", "changes",])
            elif i == ".read":
                suggestions[i] = self.getDummyDict(["lexeme", "sync", "word"])
            elif i == ".restore":
                suggestions[i] = self.getDummyDict(["journals", "lastjournals", "lastnotes", "notes",])
            elif i == ".tts":
                suggestions[i] = self.getDummyDict(["1", "2", "3", "4", "copiedtext", "copiedtext1", "copiedtext2", "copiedtext3", "copiedtext4",])
            elif i == ".change":
                suggestions[i] = self.getDummyDict(["bible", "bibles", "biblesearchmode", "colors", "colours", "commentary", "concordance", "config", "defaultcommand", "dictionary", "encyclopedia", "favouritebible1", "favouritebible2", "favouritebible3", "favouriteoriginalbible", "lexicon", "mymenu", "noteeditor", "referencebook", "referencebookchapter", "terminalmodeconfig", "thirdpartydictionary", "ttslanguage1", "ttslanguage2", "ttslanguage3", "ttslanguage4"])
            elif i == ".exec":
                suggestions[i] = self.getDummyDict(["file",])
            elif i == ".edit":
                suggestions[i] = self.getDummyDict(["booknote", "chapternote", "config", "content", "filters", "journal", "newfile", "textfile", "versenote"])
            elif i == ".quick":
                suggestions[i] = self.getDummyDict(["edit", "editcopiedtext", "open", "opencopiedtext", "search", "searchcopiedtext", "start"])
            elif i == ".search":
                suggestions[i] = self.getDummyDict(["bible", "booknote", "chapternote", "concordance", "journal", "lexiconcontent", "referencebooks", "versenote"])
            elif i == ".show":
                suggestions[i] = self.getDummyDict(["bibleabbreviations", "biblebooks", "biblechapters", "bibles", "bibleverses", "commentaries", "data", "dictionaries", "downloads", "encyclopedia", "lexicons", "referencebooks", "strongbibles", "thirdpartydictionary", "topics", "ttslanguages"])
            elif i == ".toggle":
                suggestions[i] = self.getDummyDict(["chapterlayout", "comparison", "lexicalentries", "noteindicator", "parallels", "clipboardmonitor", "colorbrightness", "colourbrightness", "favoriteverses", "favouriteverses", "pager", "plainbiblechaptersubheadings", "usernoteindicator", "versenumber"])
            elif i in ("text:::", "studytext:::", "_chapters", "_bibleinfo:::"):
                suggestions[i] = self.getDummyDict(self.crossPlatform.textList)
            elif i in ("_vnsc:::", "_vndc:::", "readchapter:::", "readverse:::", "readword:::", "readlexeme:::",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.textList, ".")
            elif i in ("compare:::", "comparechapter:::"):
                suggestions[i] = self.getDummyDict(self.crossPlatform.textList, "_")
            elif i in ("count:::", "search:::", "andsearch:::", "orsearch:::", "advancedsearch:::", "regexsearch:::",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.textList, ":::")
            elif i in ("bible:::", "chapter:::", "main:::", "study:::", "read:::", "readsync:::", "_verses:::"):
                suggestions[i] = self.getDummyDict(self.crossPlatform.textList, ":::", None if config.terminalUseLighterCompleter else self.allKJVreferences)
            elif i in ("_biblenote:::",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.textList, ":::", None if config.terminalUseLighterCompleter else self.allKJVreferencesBcv1)
            elif i in ("concordance:::",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.strongBibles, ":::")
            elif i in ("lexicon:::", "searchlexicon:::", "reverselexicon",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.lexiconList, ":::")
            elif i in ("data:::",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.dataList)
            elif i in ("translate:::",):
                suggestions[i] = self.getDummyDict(Translator.fromLanguageCodes, "-")
            elif i in ("download:::",):
                downloadTypes = ["MarvelData", "MarvelBible", "MarvelCommentary", "GitHubBible", "GitHubCommentary", "GitHubBook", "GitHubMap", "GitHubPdf", "GitHubEpub"]
                suggestions[i] = self.getDummyDict(downloadTypes, ":::")
            elif i in ("_commentarychapters:::", "_commentaryinfo:::"):
                suggestions[i] = self.getDummyDict(self.crossPlatform.commentaryList)
            elif i in ("commentary:::", "_commentaryverses:::"):
                suggestions[i] = self.getDummyDict(self.crossPlatform.commentaryList, ":::", None if config.terminalUseLighterCompleter else self.allKJVreferences)
            elif i in ("_commentary:::",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.commentaryList, ".")
            elif i in ("crossreference:::", "difference:::", "diff:::", "passages:::", "overview:::", "summary:::", "index:::", "chapterindex:::", "map:::", "tske:::", "combo:::", "translation:::", "discourse:::", "words:::", "openbooknote:::", "openchapternote:::", "openversenote:::", "editbooknote:::", "editchapternote:::", "editversenote:::", "_imvr:::"):
                suggestions[i] = None if config.terminalUseLighterCompleter else self.allKJVreferences
            elif i in ("_imv:::", "_instantverse:::", "_menu:::", "_openbooknote:::", "_openchapternote:::", "_openversenote:::", "_editbooknote:::", "_editchapternote:::", "_editversenote:::"):
                suggestions[i] = None if config.terminalUseLighterCompleter else self.allKJVreferencesBcv1
            elif i in ("clause:::",):
                suggestions[i] = None if config.terminalUseLighterCompleter else self.allKJVreferencesBcv2
            elif i in ("dictionary:::",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.dictionaryListAbb, ":::")
            elif i in ("encyclopedia:::",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.encyclopediaListAbb, ":::")
            elif i in ("_book:::",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.referenceBookList)
            elif i in ("book:::", "searchbook:::", "searchbookchapter:::",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.referenceBookList, ":::")
            elif i in ("thirddictionary:::", "searchthirddictionary:::", "s3dict:::", "3dict:::"):
                suggestions[i] = self.getDummyDict(self.crossPlatform.thirdPartyDictionaryList, ":::")
            elif i in ("searchtool:::",):
                suggestions[i] = self.getDummyDict(self.crossPlatform.searchToolList, ":::")
            elif self.textCommandParser.parent is not None:
                try:
                    # self.textCommandParser.parent is None when uba is not running as a full app
                    if i in (f"{self.ttsCommandKeyword}:::",):
                        suggestions[i] = self.getDummyDict(self.ttsLanguageCodes, ":::")
                except:
                    pass
            elif i in ("exlb:::",):
                suggestions[i] = self.getDummyDict(["exlbt", "exlbp", "exlbl"], ":::")
            elif i in ("day:::", "dayaudio:::", "dayaudioplus:::"):
                suggestions[i] = days365
            elif i in ("_whatis:::",):
                options = sorted(list(self.dotCommands.keys())) + list(self.textCommandParser.interpreters.keys())
                suggestions[i] = self.getDummyDict(options)
            else:
                suggestions[i] = None
        # Added all KJV verse references
        suggestions = {**suggestions, **self.allKJVreferences}
        # Remove unexpected item
        suggestions.pop(":::", None)
        return suggestions

    def getCommandCompleter(self):
        suggestions = self.getCommandCompleterSuggestions()
        return FuzzyCompleter(ThreadedCompleter(NestedCompleter.from_nested_dict(suggestions)))

    def getTextCommandSuggestion(self, addDotCommandWordOnly=True):
        # Text command autocompletion/autosuggest
        textCommands = [key + ":::" for key in self.textCommandParser.interpreters.keys()]
        bibleBooks = self.bibleBooks.getStandardBookAbbreviations()
        dotCommands = sorted(list(self.dotCommands.keys()))
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        if addDotCommandWordOnly:
            #suggestion = ['.quit', '.restart', 'quit', 'restart', bibleReference] + dotCommands + [cmd[1:] for cmd in dotCommands] + sorted(textCommands) + bibleBooks
            #suggestion = ['.quit', '.restart', 'quit', 'restart', bibleReference] + dotCommands + [cmd[1:] for cmd in dotCommands] + sorted(textCommands)
            suggestion = [bibleReference] + dotCommands + sorted(textCommands)
        else:
            suggestion = dotCommands + sorted(textCommands) + bibleBooks
            suggestion.sort()
        return suggestion

    def togglePager(self):
        config.terminalEnablePager = not config.terminalEnablePager
        return self.plainText

    def showClipboardMonitorStatus(self):
        self.print(self.divider)
        self.print("Clipboard Monitor: {0}".format("ON" if config.terminalEnableClipboardMonitor else "OFF"))

    def toggleClipboardMonitor(self):
        config.terminalEnableClipboardMonitor = not config.terminalEnableClipboardMonitor
        self.showClipboardMonitorStatus()
        return ""

    def standardcommands(self):
        content = "UBA commands:"
        content += "\n".join([re.sub("            #", "#", value[-1]) for value in self.textCommandParser.interpreters.values()])
        return self.keepContent(content)

    def terminalcommands(self):
        content = "UBA terminal mode commands:"
        content += "\n".join([f"{key} - {self.dotCommands[key][0]}" for key in sorted(self.dotCommands.keys())])
        self.print(self.keepContent(content))
        return ""

    def commandAliases(self):
        content = "UBA terminal mode command aliases:\n"
        content += "\n".join([f"{key} - {value[0]}" for key, value in sorted(self.dotCommands.items()) if value[0].startswith("an alias to ")])
        self.print(self.keepContent(content))
        return ""

    def keys(self):
        bulitinKeyBindings = """Built-in keyboard shortcuts:
Ctrl+Q quit UBA
Ctrl+Z restart UBA
Escape+1 change bible
Escape+2 change bibles for comparison
Escape+3 change commentary
Escape+C open system command prompt
Escape+D run default command
Escape+H launch help menu
Escape+M launch master menu
Escape+O launch open menu
Escape+P launch plugins menu
Escape+S swap colour brightness
Escape+T launch text-to-speech menu
Escape+W open wordnet"""
        content = "Customised keyboard shortcuts:\n"
        keyCombo = ["ctrl+b", "ctrl+f", "ctrl+g", "ctrl+k", "ctrl+l", "ctrl+r", "ctrl+s", "ctrl+u", "ctrl+w", "ctrl+y"]
        configEntry = [config.terminal_ctrl_b, config.terminal_ctrl_f, config.terminal_ctrl_g, config.terminal_ctrl_k, config.terminal_ctrl_l, config.terminal_ctrl_r, config.terminal_ctrl_s, config.terminal_ctrl_u, config.terminal_ctrl_w, config.terminal_ctrl_y]
        content += pprint.pformat(dict(zip(keyCombo, configEntry)))
        self.print(self.keepContent(f"{self.divider}\n{bulitinKeyBindings}\n{self.divider}\n{content}"))
        return ""

    def open365readingplan(self):
        days = "<br>".join([f"[<ref>{i}</ref> ] <ref>{text[-1]}</ref>" for i, text in allDays.items()])
        days = f"<h2>365 Day Reading Plan</h2>{days}"
        self.print(self.divider)
        content = TextUtil.htmlToPlainText(days).strip()
        self.print(content)
        self.print(self.divider)
        self.print("Enter a day number")
        userInput = self.promptSelectionFromContent(content)
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        try:
            if int(userInput) and int(userInput) in range(366):
                command = f"DAY:::{userInput}"
                self.printRunningCommand(command)
                return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def stopAudio(self):
        self.textCommandParser.parent.closeMediaPlayer()
        return ""

    def reload(self):
        return self.plainText

    def keepContent(self, content):
        self.html = re.sub("\n", "<br>", content)
        self.plainText = content
        return content

    def commands(self):
        content = pprint.pformat(self.getTextCommandSuggestion(False))
        return self.keepContent(content)

    def read(self):
        self.textCommandParser.parent.getPlaylistFromHTML(self.html)
        return ""

    def readsync(self):
        self.textCommandParser.parent.getPlaylistFromHTML(self.html, displayText=True)
        return ""

    def latest(self):
        self.print(self.divider)
        server = "http://localhost:8080"
        serverAlive = "ON" if self.isUrlAlive(server) else "OFF"
        self.print(f"{server} [{serverAlive}]")
        searchModes = ("COUNT", "SEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
        self.print(f"Current search mode: {searchModes[config.bibleSearchMode]}")
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        self.print("BIBLE:::{0}:::{1} [{2}.{3}.{4}]".format(config.mainText, bibleReference, config.mainB, config.mainC, config.mainV))
        commentaryReference = self.textCommandParser.bcvToVerseReference(config.commentaryB, config.commentaryC, config.commentaryV)
        self.print("COMMENTARY:::{0}:::{1} [{2}.{3}.{4}]".format(config.commentaryText, commentaryReference, config.commentaryB, config.commentaryC, config.commentaryV))
        self.print(f"BOOK:::{config.book}:::{config.bookChapter}")
        self.print(f"LEXICON:::{config.lexicon}:::{config.lexiconEntry}")
        self.print(f"CONCORDANCE:::{config.concordance}:::{config.concordanceEntry}")
        self.print(f"DICTIONARY:::{config.dictionaryEntry}")
        self.print(f"ENCYCLOPEDIA:::{config.encyclopedia}:::{config.encyclopediaEntry}")
        self.print(f"THIRDDICTIONARY:::{config.thirdDictionary}:::{config.thirdDictionaryEntry}")
        self.print(f"DATA:::{config.dataset}")
        self.print(f"EXLB:::exlbt:::{config.topicEntry}")
        self.print(f"EXLB:::exlbp:::{config.characterEntry}")
        self.print(f"EXLB:::exlbl:::{config.locationEntry}")
        self.print(f"_harmony:::{config.parallels}.{config.parallelsEntry}")
        self.print(f"_promise:::{config.promises}.{config.promisesEntry}")
        return ""

    def getPlusBible(self):
        plusBible = ""
        if not config.mainText == config.favouriteBible:
            plusBible = config.favouriteBible
        elif not config.mainText == config.favouriteBible2:
            plusBible = config.favouriteBible2
        elif not config.mainText == config.favouriteBible3:
            plusBible = config.favouriteBible3
        if plusBible:
            return f", {plusBible}"
        return plusBible

    def checkAudioContent(self):
        if config.audioBibleIcon in self.html or config.audioBibleIcon2 in self.html:
            self.print(self.divider)
            self.print("Audio content is available!")
            self.print("To listen, run '.read' or '.readsync'")

    def initialDisplay(self):
        self.print(self.divider)
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        self.print("{0} [{1}.{2}.{3}] - {4}{5}, {6}".format(bibleReference, config.mainB, config.mainC, config.mainV, config.mainText, self.getPlusBible(), config.commentaryText))
        self.print("Enter an UBA command:")
        #if config.terminalDisplayBeginnerMessage:
        #    self.print("(run '.menu' to begin ...)")
        return ""

    def showbibleabbreviations(self, text="", commentary=False):
        bible = Bible(config.mainText if not text else text)
        bibleBooks = self.bibleBooks
        bookNumbers = bible.getBookList()
        display = [f"[<ref>{b}</ref>] {bibleBooks.getStandardBookAbbreviation(b)}" for b in bookNumbers]
        self.print(TextUtil.htmlToPlainText(" ".join(display)))
        self.currentBibleAbbs = [bibleBooks.getStandardBookAbbreviation(b) for b in bookNumbers]
        try:
            if commentary:
                self.currentBibleAbb = bibleBooks.getStandardBookAbbreviation(config.commentaryB)
                self.currentBibleBookNo = config.commentaryB
            else:
                self.currentBibleAbb = bibleBooks.getStandardBookAbbreviation(config.mainB)
                self.currentBibleBookNo = config.mainB
        except:
            self.currentBibleAbb = self.currentBibleAbbs[0]
            self.currentBibleBookNo = bookNumbers[0]
        if not self.currentBibleBookNo in bookNumbers:
            self.currentBibleBookNo = bookNumbers[0]
        self.bookNumbers = bookNumbers
        return ""

    def showbiblebooks(self, text=""):
        bible = Bible(config.mainText if not text else text)
        bibleBooks = self.bibleBooks
        bookNumbers = bible.getBookList()
        display = [f"[<ref>{b}</ref>] {bibleBooks.getStandardBookFullName(b)}" for b in bookNumbers]
        self.print(TextUtil.htmlToPlainText(" ".join(display)))
        self.currentBibleBooks = [bibleBooks.getStandardBookFullName(b) for b in bookNumbers]
        try:
            self.currentBibleBook = bibleBooks.getStandardBookFullName(config.mainB)
            self.currentBibleBookNo = config.mainB
        except:
            self.currentBibleBook = self.currentBibleBooks[0]
            self.currentBibleBookNo = bookNumbers[0]
        if not self.currentBibleBookNo in bookNumbers:
            self.currentBibleBookNo = bookNumbers[0]
        self.bookNumbers = bookNumbers
        return ""

    def wiki(self):
        url = "https://github.com/eliranwong/UniqueBible/wiki/Terminal-Mode"
        command = f"_website:::{url}"
        self.printRunningCommand(command)
        return self.getContent(command)

    def showbiblechapters(self, text="", b=None):
        bible = Bible(config.mainText if not text else text)
        chapterList = bible.getChapterList(config.mainB if b is None else b)
        chapterListDisplay = " | ".join([f"<ref>{c}</ref>" for c in chapterList])
        self.print(TextUtil.htmlToPlainText(f"<h2>Chapters:</h2><br>| {chapterListDisplay} |"))
        self.currentBibleChapters = chapterList
        return ""

    def showbibleverses(self, text="", b=None, c=None):
        bible = Bible(config.mainText if not text else text)
        verseList = bible.getVerseList(config.mainB if b is None else b, config.mainC if c is None else c)
        verseListDisplay = " | ".join([f"<ref>{v}</ref>" for v in verseList])
        self.print(TextUtil.htmlToPlainText(f"<h2>Verses:</h2><br>| {verseListDisplay} |"))
        self.currentBibleVerses = verseList
        return ""

    def showtopics(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_topics"])
        moduleList = []
        for index, topic in enumerate(self.crossPlatform.topicListAbb):
            moduleList.append(f"[<ref>{topic}</ref> ] {self.crossPlatform.topicList[index]}")
        content += "<br>".join(moduleList)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showdictionaries(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["context1_dict"])
        moduleList = []
        for index, topic in enumerate(self.crossPlatform.dictionaryListAbb):
            moduleList.append(f"[<ref>{topic}</ref> ] {self.crossPlatform.dictionaryList[index]}")
        content += "<br>".join(moduleList)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showencyclopedia(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["context1_encyclopedia"])
        moduleList = []
        for index, topic in enumerate(self.crossPlatform.encyclopediaListAbb):
            moduleList.append(f"[<ref>{topic}</ref> ] {self.crossPlatform.encyclopediaList[index]}")
        content += "<br>".join(moduleList)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showbibles(self):
        #return pprint.pformat(dict(zip(self.crossPlatform.textList, self.crossPlatform.textFullNameList)))
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_bible"])
        bibleList = []
        for index, bible in enumerate(self.crossPlatform.textList):
            bibleList.append(f"[<ref>{bible}</ref> ] {self.crossPlatform.textFullNameList[index]}")
        content += "<br>".join(bibleList)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showstrongbibles(self):
        strongBiblesFullNameList = [Bible(text).bibleInfo() for text in self.crossPlatform.strongBibles]
        content = ""
        content += "<h2>{0} + {1}</h2>".format(config.thisTranslation["menu5_bible"], config.thisTranslation["bibleStrongNumber"])
        bibleList = []
        for index, bible in enumerate(self.crossPlatform.strongBibles):
            bibleList.append(f"[<ref>{bible}</ref> ] {strongBiblesFullNameList[index]}")
        content += "<br>".join(bibleList)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showthirdpartydictionary(self):
        modules = []
        for module in self.crossPlatform.thirdPartyDictionaryList:
            modules.append(f"[<ref>{module}</ref> ]")
        content = "<br>".join(modules)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showlexicons(self):
        modules = []
        for module in self.crossPlatform.lexiconList:
            modules.append(f"[<ref>{module}</ref> ]")
        content = "<br>".join(modules)
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showcommentaries(self):
        content = ""
        content += """<h2><ref onclick="window.parent.submitCommand('.commentarymenu')">{0}</ref></h2>""".format(config.thisTranslation["menu4_commentary"])
        content += "<br>".join(["""[<ref>{0}</ref> ] {1}""".format(abb, self.crossPlatform.commentaryFullNameList[index]) for index, abb in enumerate(self.crossPlatform.commentaryList)])
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showreferencebooks(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_selectBook"])
        content += "<br>".join(["""[<ref>{0}</ref> ] {0}""".format(book) for book in self.crossPlatform.referenceBookList])
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showdata(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu_data"])
        content += "<br>".join(["[<ref>{0}</ref> ]".format(book) for book in self.crossPlatform.dataList])
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def showdownloads(self):
        content = ""
        from uniquebible.util.DatafileLocation import DatafileLocation
        try:
            from uniquebible.util.GithubUtil import GithubUtil
            githubutilEnabled = True
        except:
            githubutilEnabled = False
        # ["marveldata", "marvelbible", "marvelcommentary", "GitHubBible", "GitHubCommentary", "GitHubBook", "GitHubMap", "GitHubPdf", "GitHubEpub"]
        resources = (
            ("Marvel Datasets", DatafileLocation.marvelData, "marveldata"),
            ("Marvel Bibles", DatafileLocation.marvelBibles, "marvelbible"),
            ("Marvel Commentaries", DatafileLocation.marvelCommentaries, "marvelcommentary"),
        )
        for collection, data, keyword in resources:
            content += "<h2>{0}</h2>".format(collection)
            for k, v in data.items():
                if os.path.isfile(os.path.join(*v[0])):
                    content += """[ {1} ] {0}<br>""".format(k, config.thisTranslation["installed"])
                else:
                    content += """[<ref>DOWNLOAD:::{0}:::{1}</ref> ]<br>""".format(keyword, k)
        if githubutilEnabled:
            resources = (
                ("GitHub Bibles", "GitHubBible", GitHubRepoInfo.bibles[0], (config.marvelData, "bibles"), ".bible"),
                ("GitHub Commentaries", "GitHubCommentary", GitHubRepoInfo.commentaries[0], (config.marvelData, "commentaries"), ".commentary"),
                ("GitHub Books", "GitHubBook", GitHubRepoInfo.books[0], (config.marvelData, "books"), ".book"),
                ("GitHub Maps", "GitHubMap", GitHubRepoInfo.maps[0], (config.marvelData, "books"), ".book"),
                ("GitHub PDF", "GitHubPdf", GitHubRepoInfo.pdf[0], (config.marvelData, "pdf"), ".pdf"),
                ("GitHub EPUB", "GitHubEpub", GitHubRepoInfo.epub[0], (config.marvelData, "epub"), ".epub"),
            )
            for collection, kind, repo, location, extension in resources:
                content += "<h2>{0}</h2>".format(collection)
                for file in GithubUtil(repo).getRepoData():
                    if os.path.isfile(os.path.join(*location, file)):
                        content += """[ {1} ] {0}<br>""".format(file.replace(extension, ""), config.thisTranslation["installed"])
                    else:
                        content += """[<ref>DOWNLOAD:::{1}:::{0}</ref> ]<br>""".format(file.replace(extension, ""), kind)
        content += "<h2>Third-party Resources</h2><p>Read <ref>https://github.com/eliranwong/UniqueBible/wiki/Third-party-resources</ref> about third-party resources.</a></p>"
        self.html = content
        self.plainText = TextUtil.htmlToPlainText(content).strip()
        return self.plainText

    def getCliOutput(self, cli):
        try:
            process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = process.communicate()
            return stdout.decode("utf-8")
        except:
            return ""

    def gitstatus(self):
        return self.getCliOutput("git status")

    def showttslanguages(self):
        codes = self.ttsLanguageCodes
        #languages = [self.ttsLanguages[code][-1] for code in codes]

        display = "<h2>Languages</h2>"
        for code in codes:
            language = self.ttsLanguages[code][-1]
            display += f"[<ref>{code}</ref> ] {language}<br>"
        display = display[:-4]
        self.html = display
        self.plainText = TextUtil.htmlToPlainText(display).strip()
        self.print(self.plainText)
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

    def extract(self, text=""):
        if not text:
            text = self.plainText
        parser = BibleVerseParser(config.parserStandarisation)
        verseList = parser.extractAllReferences(text, False)
        #print(self.divider)
        if not verseList:
            self.print("No bible reference is found!")
        else:
            self.print("Bible reference(s):")
            references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verseList])
            self.print(references)
        return ""

    def extractcopiedtext(self):
        clipboardText = self.getclipboardtext()
        self.html = clipboardText
        self.plainText = clipboardText
        return self.extract()

    def findCopiedText(self):
        clipboardText = self.getclipboardtext()
        self.html = clipboardText
        self.plainText = clipboardText
        return self.find()

    def tts(self, runOnSelectedText=True, defaultText="", defaultLanguage=""):
        if runOnSelectedText:
            clipboardText = defaultText if defaultText else self.getclipboardtext()
        try:
        #if True:
            suggestions = self.ttsLanguageCodes
            languages = [self.ttsLanguages[code][-1] for code in suggestions]
            #shortCodes = []
            #languages = []
            #for code in codes:
            #    shortCodes.append(re.sub("\-.*?$", "", code))
            #    languages.append(self.ttsLanguages[code][-1])
            # suggestions
            #suggestions = codes + shortCodes
            #suggestions = list(set(suggestions))
            self.print(self.divider)
            default = config.ttsDefaultLangauge if config.ttsDefaultLangauge in suggestions else ""
            if defaultLanguage and defaultLanguage in suggestions:
                userInput = defaultLanguage
            else:
                # display available languages
                self.print(self.showttslanguages())
                self.printChooseItem()
                self.print("Enter a language:")
                userInput = self.searchablePrompt(self.inputIndicator, default=default, options=suggestions, descriptions=languages, promptSession=self.terminal_tts_language_session)
            # alternative: use input dialog
            #if defaultLanguage and defaultLanguage in suggestions:
            #    userInput = defaultLanguage
            #else:
            #    userInput = self.dialogs.searchableInput(title="Text-to-speech", text="Enter or search for a language code:", options=suggestions)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in suggestions:
                #config.ttsDefaultLangauge = userInput
                commandPrefix = f"{self.getDefaultTtsKeyword()}:::{userInput}:::"
                if runOnSelectedText:
                    userInput = clipboardText
                else:
                    self.print(self.divider)
                    self.print("Enter text:")
                    userInput = self.simplePrompt(multiline=True)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()

                command = f"{commandPrefix}{userInput}"
                self.printRunningCommand(command)
                return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def watsonTranslate(self, runOnSelectedText=True, defaultText=""):
        if ("Ibmwatson" in config.enabled):
            if runOnSelectedText:
                clipboardText = defaultText if defaultText else self.getclipboardtext()
            try:
                codes = []
                display = []
                descriptions = []
                for index, item in enumerate(Translator.fromLanguageCodes):
                    display.append(f"[<ref>{item}</ref> ] {Translator.fromLanguageNames[index]}")
                    codes.append(item)
                    descriptions.append(Translator.fromLanguageNames[index])
                display = "<br>".join(display)
                display = TextUtil.htmlToPlainText(f"<h2>Languages</h2>{display}")

                self.print(self.divider)
                self.print(display)
                self.print("Translate from:")
                self.print("(enter a language code)")
                suggestions = codes
                userInput = self.searchablePrompt(self.inputIndicator, options=suggestions, descriptions=descriptions, promptSession=self.terminal_watson_translate_from_language_session)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput in suggestions:
                    fromLanguage = userInput

                    codes = []
                    display = []
                    for index, item in enumerate(Translator.toLanguageCodes):
                        display.append(f"[<ref>{item}</ref> ] {Translator.toLanguageNames[index]}")
                        codes.append(item)
                    display = "<br>".join(display)
                    display = TextUtil.htmlToPlainText(f"<h2>Languages</h2>{display}")

                    self.print(self.divider)
                    self.print(display)
                    self.print("Translate to:")
                    self.print("(enter a language code)")
                    suggestions = codes
                    userInput = self.searchablePrompt(self.inputIndicator, options=suggestions, descriptions=descriptions, promptSession=self.terminal_watson_translate_to_language_session)
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()

                    if userInput in suggestions:
                        toLanguage = userInput

                    if runOnSelectedText:
                        userInput = clipboardText
                    else:
                        self.print(self.divider)
                        self.print("Enter the text you want to translate:")
                        userInput = self.simplePrompt(multiline=True)

                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    # translate if all input are invalid
                    command = f"TRANSLATE:::{fromLanguage}-{toLanguage}:::{userInput}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
                else:
                    return self.printInvalidOptionEntered()
            except:
                return self.printInvalidOptionEntered()
        else:
            self.print("Package 'ibm-watson' is not found on your system!")
            return ""

    def googleTranslate(self, runOnSelectedText=True, defaultText=""):
        if ("Translate" in config.enabled):
            if runOnSelectedText:
                clipboardText = defaultText if defaultText else self.getclipboardtext()
            try:
                codes = []
                display = []
                descriptions = []
                for key, value in Languages.googleTranslateCodes.items():
                    display.append(f"[<ref>{value}</ref> ] {key}")
                    codes.append(value)
                    descriptions.append(key)
                display = "<br>".join(display)
                display = TextUtil.htmlToPlainText(f"<h2>Languages</h2>{display}")

                self.print(self.divider)
                self.print(display)
                self.print("Translate from:")
                self.print("(enter a language code)")
                suggestions = codes
                userInput = self.searchablePrompt(self.inputIndicator, options=suggestions, descriptions=descriptions, promptSession=self.terminal_google_translate_from_language_session)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput in suggestions:
                    fromLanguage = userInput

                    self.print(self.divider)
                    self.print(display)
                    self.print("Translate to:")
                    self.print("(enter a language code)")
                    suggestions = codes
                    userInput = self.searchablePrompt(self.inputIndicator, options=suggestions, descriptions=descriptions, promptSession=self.terminal_google_translate_to_language_session)
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()

                    if userInput in suggestions:
                        toLanguage = userInput

                    if runOnSelectedText:
                        userInput = clipboardText
                    else:
                        self.print(self.divider)
                        self.print("Enter the text you want to translate:")
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
            self.print("Package 'translate' is not found on your system!")
            return ""

    def printMultilineNote(self):
        self.print("[Attention! Multiline input is enabled. Press Escape+Enter when you finish text entry.]")

    def getclipboardtext(self, confirmMessage=True):
        try:
            if shutil.which("termux-clipboard-get"):
                clipboardText = subprocess.run("termux-clipboard-get", shell=True, capture_output=True, text=True).stdout
            elif ("Pyperclip" in config.enabled):
                import pyperclip
                clipboardText = pyperclip.paste()
            if clipboardText:
                if confirmMessage:
                    self.print(self.divider)
                    self.print("Clipboard text:")
                    self.print(clipboardText)
                    self.print(self.divider)
                return clipboardText
            elif confirmMessage:
                self.print("No copied text is found!")
                #return self.cancelAction()
            return ""
        except:
            return self.noClipboardUtility()

    def runclipboardtext(self, commandPrefix="", commandSuffix="", defaultText=""):
        clipboardText = defaultText if defaultText else self.getclipboardtext()
        if clipboardText:
            command = f"{commandPrefix}{clipboardText}{commandSuffix}"
            self.printRunningCommand(command)
            return self.getContent(command)
        else:
            return ""

    def bible(self):
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        return self.getContent(f"BIBLE:::{config.mainText}:::{bibleReference}")

    def commentary(self):
        bibleReference = self.textCommandParser.bcvToVerseReference(config.commentaryB, config.commentaryC, config.commentaryV)
        return self.getContent(f"COMMENTARY:::{config.commentaryText}:::{bibleReference}")

    def getCommand(self, command=""):
        if not command:
            command = self.command
        exception = "^(_setconfig:::|mp3:::|mp4:::|cmd:::|read:::|readsync:::)"
        if command.startswith(".") or re.search(exception, command.lower()):
            command = ".bible"
        return command

    # open web version
    # use local http-server if it is running
    # otherwise, use public
    def web(self, command="", filterCommand=True):
        weblink = self.textCommandParser.getWeblink(command, filterCommand)
        return self.getContent(f"_website:::{weblink}")

    def isBibleReference(self, text):
        references = self.textCommandParser.extractAllVerses(text)
        return True if references else False

    def openbibleaudio(self):
        try:
            default = config.mainText if config.mainText in self.crossPlatform.bibleAudioModules else ""
            userInput = self.dialogs.getValidOptions(options=self.crossPlatform.bibleAudioModules, title="Downlaod Bible Audio", default=default)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            module = userInput
            self.print(f"You selected '{module}'.")
            self.print("Enter bible reference(s) below:")
            userInput = self.simplePrompt()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if self.isBibleReference(userInput):
                command = f"READ:::{module}:::{userInput}"
                return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openmaps(self):
        self.print(self.divider)
        self.print("Enter bible reference(s) below:")
        self.print("(e.g. Rev 1:11, Josh 10:1-43, Act 15:36-18:22, etc.)")
        userInput = self.simplePrompt()
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        if self.isBibleReference(userInput):
            return self.web(f"MAP:::{userInput}", False)
        else:
            self.printInvalidOptionEntered()

    def share(self, command=""):
        try:
            weblink = TextUtil.getWeblink(self.getCommand(command))
            if config.terminalEnableTermuxAPI:
                plainText = self.getPlainText()
                plainText += f"\n\n{weblink}"
                plainText += "\n\n[Unique Bible App]"
                pydoc.pipepager(plainText, cmd="termux-share -a send")
                return ""
            else:
                if shutil.which("termux-clipboard-set"):
                    pydoc.pipepager(weblink, cmd="termux-clipboard-set")
                else:
                    import pyperclip
                    pyperclip.copy(weblink)
            self.print(f"The following link is copied to clipboard:\n")
            self.print(weblink)
            self.print("\nOpen it in a web browser or share with others.")
            return ""
        except:
            return self.noClipboardUtility()

    def copy(self, content="", confirmMessage=True):
        try:
            if not content:
                content = self.getPlainText()
            if config.terminalEnableTermuxAPI:
                pydoc.pipepager(content, cmd="termux-clipboard-set")
            else:
                if shutil.which("termux-clipboard-set"):
                    pydoc.pipepager(weblink, cmd="termux-clipboard-set")
                else:
                    import pyperclip
                    pyperclip.copy(content)
            if confirmMessage:
                self.print("Content is copied to clipboard.")
            return ""
        except:
            return self.noClipboardUtility()

    def copyHtml(self, content="", confirmMessage=True):
        try:
            if not content:
                content = self.html
            if config.terminalEnableTermuxAPI:
                pydoc.pipepager(content, cmd="termux-clipboard-set")
            else:
                if shutil.which("termux-clipboard-set"):
                    pydoc.pipepager(weblink, cmd="termux-clipboard-set")
                else:
                    import pyperclip
                    pyperclip.copy(content)
            if confirmMessage:
                self.print("HTML content is copied to clipboard.")
            return ""
        except:
            return self.noClipboardUtility()

    def noClipboardUtility(self):
        self.print("Clipboard utility is not found!")
        return ""

    def find(self):
        self.print("Enter a search pattern: ")
        userInput = self.terminal_find_session.prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle).strip()
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        if ("Colorama" in config.enabled):
            from colorama import init
            init()
            from colorama import Fore, Back, Style
            content = re.sub(r"({0})".format(userInput), r"{0}{1}\1{2}".format(Back.RED, Fore.WHITE, Style.RESET_ALL), self.plainText, flags=re.IGNORECASE)
        else:
            content = re.sub(r"({0})".format(userInput), r"[[[ \1 ]]]", self.plainText, flags=re.IGNORECASE)
        return content

    def history(self):
        return self.readPlainTextFile(os.path.join("terminal_history", "commands"))

    def latestchanges(self):
        return self.readPlainTextFile("latest_changes.txt")

    def readPlainTextFile(self, filename):
        if os.path.isfile(filename):
            with open(filename, "r", encoding="utf-8") as input_file:
                text = input_file.read()
        return self.keepContent(text)

    def displayMessage(self, message="", title="UniqueBible"):
        self.print(title)
        self.print(message)

    def printNoSupportMessage(self):
        self.print("This feature is not supported on your system!")
        return ""

    def buildPortablePython(self):
        if ("Pickley" in config.enabled):
            if not WebtopUtil.isPackageInstalled("portable-python"):
                os.system("pickley install portable-python")
            try:
                if WebtopUtil.isPackageInstalled("portable-python") and WebtopUtil.isPackageInstalled("tar"):
                    major, minor, micro, *_ = sys.version_info
                    thisOS = platform.system()
                    cpu = ""
                    if thisOS == "Darwin":
                        thisOS = "macOS"
                        *_, cpu = platform.mac_ver()
                        cpu = f"_{cpu}"
                    thisdir = os.path.join("portable_python", "{0}{4}_{1}.{2}.{3}".format(thisOS, major, minor, micro, cpu))
                    if not os.path.isdir(thisdir):
                        os.makedirs(thisdir, exist_ok=True)
                    # build
                    os.system(f"cd {thisdir}; portable-python build {major}.{minor}.{micro}")
                    # unpack
                    self.print("Unpacking ...")
                    os.system(f"cd {thisdir}; tar -xf dist/*.tar.gz")
                    self.print("Done!")
                    portablePythonPath = os.path.join(thisdir, f"{major}.{minor}.{micro}", "bin", f"python{major}.{minor}")
                    if os.path.isfile(portablePythonPath):
                        self.print(f"The path of the newly built portable-python path is:")
                        self.print(portablePythonPath)
                        self.print(self.divider)
                        self.saveBashScript("gui")
                        self.print(self.divider)
                        self.saveBashScript("terminal")
                else:
                    self.print("Install both 'portable-python' and 'tar' first!")
            except:
                self.printNoSupportMessage()
        else:
            self.print("Install 'pickley' first!")
        return ""

    def saveBashScript(self, mode):
        major, minor, micro, *_ = sys.version_info
        thisOS = platform.system()
        cpu = ""
        if thisOS == "Darwin":
            thisOS = "macOS"
            *_, cpu = platform.mac_ver()
            cpu = f"_{cpu}"
        script = """#!/usr/bin/env bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${0}BASH_SOURCE[0]{1}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
$SCRIPT_DIR/portable_python/{2}{7}_{3}.{4}.{5}/{3}.{4}.{5}/bin/python{3}.{4} uba.py {6}
""".format("{", "}", thisOS, major, minor, micro, mode, cpu)
        filepath = f"uba_{mode}_{thisOS}{cpu}_{major}.{minor}.{micro}.sh"
        with open(filepath, "w", encoding="utf-8") as fileObj:
            fileObj.write(script)
        # add executable permissions
        try:
            os.chmod(filepath, 0o755)
        except:
            pass
        self.print(f"Created '{filepath}' for running UBA in {mode} mode.")

    def update(self, debug=False):
        try:
            try:
                if WebtopUtil.isPackageInstalled("git") and not config.terminalUpdateInOldWay:
                    os.system("git pull")
                    return self.finishUpdate()
                else:
                    return self.oldWayUpdate(debug)
            except:
                return self.oldWayUpdate(debug)
        except:
            return self.updateFailed()

    def updateFailed(self):
        self.print("Failed to update to the latest version.")
        if not config.internet:
            self.print("You may need to check your internet connection.")
        return ""

    def finishUpdate(self):
        # set executable files on macOS or Linux
        if not platform.system() == "Windows":
            for filename in ("uba.py", "main.py", "BibleVerseParser.py", "RegexSearch.py"):
                if os.path.isfile(filename):
                    os.chmod(filename, 0o755)
                # finish message
        config.lastAppUpdateCheckDate = str(DateUtil.localDateNow())

        self.print("You have the latest version.")
        return ".restart"

    def config(self):
        intro = "<h2>Unique Bible App Configurations</h2>"
        intro += "<p>Default settings are good for general use.  In case you want to make changes, you may run '<ref>_setconfig:::</ref>' command in terminal mode.  Alternately, you may manually edit the file 'config.py', located in UBA home directory, when UBA is not running.</p>"
        self.html = "{0}<p>{1}</p>".format(intro, "</p><p>".join(["[ITEM] <ref>{0}</ref>{1}\nCurrent value: <z>{2}</z>".format(key, re.sub("        # ", "", value), eval("pprint.pformat(config."+key+")")) for key, value in config.help.items()]))
        self.plainText = TextUtil.htmlToPlainText(self.html).strip()
        return self.plainText

    def latestBible(self):
        command = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        self.printRunningCommand(command)
        return self.getContent(command)

    def backward(self):
        newChapter = config.mainC - 1
        if newChapter < 1:
            newChapter = 1
        command = self.textCommandParser.bcvToVerseReference(config.mainB, newChapter, 1)
        self.printRunningCommand(command)
        return self.getContent(command)

    def forward(self):
        newChapter = config.mainC
        if config.mainC < BibleBooks.getLastChapter(config.mainB):
            newChapter += 1
        command = self.textCommandParser.bcvToVerseReference(config.mainB, newChapter, 1)
        self.printRunningCommand(command)
        return self.getContent(command)

    def noPromptToolkit(self):
        self.print("Install package 'prompt_toolkit' first!")
        return ""

    def multilineEditor(self, text="", placeholder="", custom_save_file_method=None, filepath="", newFile=False):
        config.ubaIsRunning = True
        config.textEditor = TextEditor(self, custom_save_file_method=custom_save_file_method)
        if newFile:
            return config.textEditor.newFile()
        elif filepath:
            return config.textEditor.openFile(filepath)
        return config.textEditor.multilineEditor(text, placeholder)

    def simplePrompt(self, numberOnly=False, validator=None, multiline=False, inputIndicator="", default="", accept_default=False, completer=None, promptSession=None):
        inputPrompt = promptSession.prompt if promptSession is not None else prompt
        if not inputIndicator:
            inputIndicator = self.inputIndicator
        if numberOnly:
            validator = NumberValidator()
        userInput = inputPrompt(
            inputIndicator,
            key_bindings=self.prompt_multiline_shared_key_bindings if multiline else self.prompt_shared_key_bindings,
            bottom_toolbar=self.getToolBar(multiline),
            enable_system_prompt=True,
            swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")),
            style=self.promptStyle,
            validator=validator,
            multiline=multiline,
            default=default,
            accept_default=accept_default,
            completer=completer,
        ).strip()
        return userInput

    # a wrapper to standard prompt; open radiolist_dialog showing available options when user input is not a valid option.
    def searchablePrompt(self, inputIndicator="", multiline=False, default="", accept_default=False, completer=None, options=[], descriptions=[], bold_descriptions=False, validator=None, numberOnly=False, promptSession=None, placeholder=None):
        self.print("(or search here)")
        inputPrompt = promptSession.prompt if promptSession is not None else prompt
        if not inputIndicator:
            inputIndicator = self.inputIndicator
        if completer is None and options:
            completer = FuzzyCompleter(WordCompleter(options, ignore_case=True))
        if validator is None and numberOnly:
            validator=NumberValidator()
        result = inputPrompt(
            message=inputIndicator,
            key_bindings=self.prompt_multiline_shared_key_bindings if multiline else self.prompt_shared_key_bindings,
            bottom_toolbar=self.getToolBar(multiline),
            enable_system_prompt=True,
            swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")),
            style=self.promptStyle,
            completer=completer,
            validator=NumberValidator() if numberOnly else None,
            multiline=multiline,
            default=default,
            accept_default=accept_default,
            placeholder=placeholder,
        ).strip()
        if result.lower() == config.terminal_cancel_action:
            return result
        if options:
            if result and result in options:
                return result
            else:
                return self.dialogs.getValidOptions(options=options, descriptions=descriptions, bold_descriptions=bold_descriptions, filter=result, default=default)
        else:
            if result:
                return result
            else:
                return ""

    def getBibleVersion(self, defaultText=""):
        return self.searchablePrompt(self.inputIndicator, options=self.crossPlatform.textList, descriptions=self.crossPlatform.textFullNameList, default=defaultText if defaultText else config.mainText, promptSession=self.terminal_bible_selection_session)

    def getBibleVersions(self):
        self.print("(empty entry to select from a list)")
        completer = FuzzyCompleter(WordCompleter(self.crossPlatform.textList, ignore_case=True))
        userInput = self.simplePrompt(default="_".join(config.compareParallelList), completer=completer, promptSession=self.terminal_multiple_bible_selection_session).strip()
        userInput = userInput.replace(" ", "")
        if not userInput:
            userInput = self.dialogs.getBibles(title="Search Multiple Bibles")
            if userInput:
                userInput = "_".join(userInput)
                self.print(userInput)
        return userInput

    def getStrongBibleVersions(self):
        self.print("(empty entry to select from a list)")
        completer = FuzzyCompleter(WordCompleter(self.crossPlatform.strongBibles, ignore_case=True))
        userInput = self.simplePrompt(default=config.concordance, completer=completer, promptSession=self.terminal_concordance_selection_session).strip()
        userInput = userInput.replace(" ", "")
        if not userInput:
            userInput = self.dialogs.getMultipleSelection(options=self.crossPlatform.strongBibles, default_values=["OHGBi"])
            if userInput:
                userInput = "_".join(userInput)
                self.print(userInput)
        return userInput

    def getBibleBookRange(self, options=["ALL"], default_values=["ALL"]):
        self.print("(empty entry to select from a list)")
        completer = FuzzyCompleter(WordCompleter(options, ignore_case=True))
        userInput = self.simplePrompt(default="ALL", completer=completer, promptSession=self.terminal_search_bible_book_range_session).strip()
        userInput = userInput.replace(" ", "")
        if not userInput:
            userInput = self.dialogs.getMultipleSelection(options=options, default_values=default_values)
            if userInput:
                userInput = ",".join(userInput)
                self.print(userInput)
        return userInput

    def getBibleBookNumber(self, defaultBookNo=None):
        return self.searchablePrompt(self.inputIndicator, options=[str(i) for i in self.bookNumbers], descriptions=[self.bibleBooks.getStandardBookFullName(i) for i in self.bookNumbers], default=str(defaultBookNo) if defaultBookNo is not None else str(config.mainB), validator=NumberValidator())

    def getBibleBookAbb(self, defaultBookNo=None):
        return self.searchablePrompt(self.inputIndicator, options=[self.bibleBooks.getStandardBookAbbreviation(i) for i in self.bookNumbers], descriptions=[self.bibleBooks.getStandardBookFullName(i) for i in self.bookNumbers], default=self.bibleBooks.getStandardBookAbbreviation(defaultBookNo) if defaultBookNo is not None else self.bibleBooks.getStandardBookAbbreviation(config.mainB))

    def getBibleBookName(self, defaultBookNo=None):
        return self.searchablePrompt(self.inputIndicator, options=[self.bibleBooks.getStandardBookFullName(i) for i in self.bookNumbers], descriptions=[self.bibleBooks.getStandardBookFullName(i) for i in self.bookNumbers], default=self.bibleBooks.getStandardBookFullName(defaultBookNo) if defaultBookNo is not None else self.bibleBooks.getStandardBookFullName(config.mainB))

    def getBibleChapterNumber(self, defaultChapterNo=None):
        return self.searchablePrompt(self.inputIndicator, options=[str(i) for i in self.currentBibleChapters], default=str(defaultChapterNo) if defaultChapterNo is not None else str(config.mainC), validator=NumberValidator())

    def getBibleVerseNumber(self, defaultVerseNo=None):
        return self.searchablePrompt(self.inputIndicator, options=[str(i) for i in self.currentBibleVerses], default=str(defaultVerseNo) if defaultVerseNo is not None else str(config.mainV), validator=NumberValidator())

    def isUrlAlive(self, url):
        #print(urllib.request.urlopen("https://www.stackoverflow.com").getcode())
        try:
            request = requests.get(url, timeout=5)
        except:
            return False
        return True if request.status_code == 200 else False

    def starthttpserver(self):
        url = "http://localhost:8080"
        if self.isUrlAlive(url):
            self.print(f"'{url}' is already alive!")
        else:
            subprocess.Popen([sys.executable, config.httpServerUbaFile, "http-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.print("UBA hptt-server started!")
        self.print("To connect, open 'http://{0}:{1}' in a web browser.".format(NetworkUtil.get_ip(), config.httpServerPort))
        return ""

    def stophttpserver(self):
        url = "http://localhost:8080/index.html?cmd=.stop"
        if self.isUrlAlive(url):
            self.print("http-server stopped!")
        else:
            self.print("http-server is not running!")
        return ""

    def downloadyoutube(self):
        if ("Ytdlp" in config.enabled) and self.textCommandParser.isFfmpegInstalled():
            try:
                self.print(self.divider)
                self.print("Enter a youtube link:")
                userInput = self.simplePrompt()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                self.print("Checking connection ...")
                if self.isUrlAlive(userInput):
                    self.print("Connection is available.")
                    self.print(self.divider)
                    url = userInput
                    options = {
                        "0": "mp3:::",
                        "1": "mp4:::",
                    }
                    self.printChooseItem()
                    self.print("[0] Download mp3 audio")
                    self.print("[1] Download mp4 video")
                    userInput = self.simplePrompt()
                    if userInput in options:
                        command = f"{options[userInput]}{url}"
                        self.printRunningCommand(command)
                        return self.getContent(command)
                    else:
                        return self.printInvalidOptionEntered()
                else:
                    return self.printInvalidOptionEntered()
            except:
                return self.printInvalidOptionEntered()
        self.printToolNotFound("yt-dlp' or 'ffmpeg")
        return ""

    def opentext(self, editMode=False):
        if ("Markitdown" in config.enabled):
            self.print(self.divider)
            userInput = self.getPath.getFilePath(check_isfile=True, empty_to_cancel=True)
            if userInput:
                content = extract_text(userInput)
                if editMode:
                    self.multilineEditor(content)
                    return ""
                else:
                    return content
            else:
                return self.cancelAction()
        self.printToolNotFound("markitdown")
        return ""

    def printToolNotFound(self, tool):
        self.print(f"Tool '{tool}' is not found on your system!")

    def spinning_animation(self, stop_event):
        while not stop_event.is_set():
            for symbol in '|/-\\':
                print(symbol, end='\r')
                time.sleep(0.1)

    def fineTunePythonCode(self, code):
        insert_string = "from uniquebible import config\nconfig.pythonFunctionResponse = "
        code = re.sub("^!(.*?)$", r"import os\nos.system(\1)", code, flags=re.M)
        if "\n" in code:
            substrings = code.rsplit("\n", 1)
            lastLine = re.sub("print\((.*)\)", r"\1", substrings[-1])
            code = code if lastLine.startswith(" ") else f"{substrings[0]}\n{insert_string}{lastLine}"
        else:
            code = f"{insert_string}{code}"
        return code

    def getFunctionResponse(self, response_message, function_name):
        if function_name == "python":
            config.pythonFunctionResponse = ""
            python_code = textwrap.dedent(response_message["function_call"]["arguments"])
            refinedCode = self.fineTunePythonCode(python_code)

            print("--------------------")
            print(f"running python code ...")
            if config.developer or config.codeDisplay:
                print("```")
                print(python_code)
                print("```")
            print("--------------------")

            try:
                exec(refinedCode, globals())
                function_response = str(config.pythonFunctionResponse)
            except:
                function_response = python_code
            info = {"information": function_response}
            function_response = json.dumps(info)
        else:
            fuction_to_call = config.chatGPTApiAvailableFunctions[function_name]
            function_args = json.loads(response_message["function_call"]["arguments"])
            function_response = fuction_to_call(function_args)
        return function_response

    def getStreamFunctionResponseMessage(self, completion, function_name):
        function_arguments = ""
        for event in completion:
            delta = event["choices"][0]["delta"]
            if delta and delta.get("function_call"):
                function_arguments += delta["function_call"]["arguments"]
        return {
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": function_name,
                "arguments": function_arguments,
            }
        }

    def showErrors(self):
        if config.developer:
            print(traceback.format_exc())

    def bibleChat(self):
        os.system('''groqchat -n "Bible Chat" -s "You are an expert on the bible" Hi!''')

    def names(self):
        with open(os.path.join(config.packageDir, "plugins", "menu", "Bible_Data", "Bible Names.txt"), "r", encoding="utf-8") as input_file:
            names = input_file.read().split("\n")
        self.print("Search for a name:")
        userInput = self.simplePrompt()
        names = [i for i in names if userInput.lower() in i.lower()]
        if names:
            self.print("\n".join(names))
        else:
            self.print("[not found]")
        return ""

    def opendata(self):
        try:
            default = config.dataset if config.dataset in self.crossPlatform.dataList else ""
            userInput = self.dialogs.getValidOptions(options=self.crossPlatform.dataList, title="Bible_Data", default=default)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            command = f"DATA:::{userInput}"
            self.printRunningCommand(command)
            return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def promptSelectionFromContent(self, content):
        entries = re.compile("<{0}>(.*?)</{0}> .*?\] (.*?)$".format(config.terminalResourceLinkColor), flags=re.M).findall(content)
        options = []
        descriptions = []
        if entries:
            for option, description in entries:
                options.append(option)
                description = re.sub("<.*?>", "", description.strip())
                descriptions.append(description)
        else:
            options = re.compile("<{0}>(.*?)</{0}>".format(config.terminalResourceLinkColor)).findall(content)

        return self.searchablePrompt(self.inputIndicator, options=options, descriptions=descriptions)

    def filterMultipleOptions(self, content, filters=[]):
        if not content or not filters:
            return ([], [])
        entries = re.compile("<{0}>(.*?)</{0}> .*?\] (.*?)$".format(config.terminalResourceLinkColor), flags=re.M).findall(content)
        options = []
        descriptions = []
        if entries:
            for option, description in entries:
                if option in filters:
                    options.append(option)
                    description = re.sub("<.*?>", "", description.strip())
                    descriptions.append(description)
        else:
            options = re.compile("<{0}>(.*?)</{0}>".format(config.terminalResourceLinkColor)).findall(content)
            options = [i for i in options if i in filters]
            descriptions = options
        return (options, descriptions)

    def distance(self):
        locationMap = {exlbl_entry: (name[0].upper(), name, float(latitude), float(longitude)) for exlbl_entry, name, latitude, longitude in allLocations}

        content = self.getContent("SEARCHTOOL:::EXLBL:::")
        self.print(self.divider)
        self.print(content)
        self.print(self.divider)

        self.print("Enter a location:")
        userInput = self.promptSelectionFromContent(content)
        *_, lat, long = locationMap[userInput]
        location1 = (lat, long)
        
        self.print("Enter another location:")
        userInput = self.promptSelectionFromContent(content)
        *_, lat, long = locationMap[userInput]
        location2 = (lat, long)

        self.print(self.divider)
        self.print("Distance between the locations:")
        self.print("{0} km".format(haversine(location1, location2)))
        self.print("{0} mi".format(haversine(location1, location2, unit='mi')))

    def customisemaps(self):
        content = self.getContent("SEARCHTOOL:::EXLBL:::")
        self.print(self.divider)
        self.print(content)
        self.print(self.divider)

        locations = []
        userInput = ""
        while not userInput == config.terminal_cancel_action:
            if userInput:
                locations.append(userInput)
            userInput = self.dialogs.getValidOptions(options=["add a location", "add a reference", "done"])
            if userInput == "add a location":
                #self.print("Add a location:")
                userInput = self.promptSelectionFromContent(content)
            elif userInput == "add a reference":
                #self.print("Add a reference:")
                userInput = self.simplePrompt()
                verseList = self.textCommandParser.extractAllVerses(userInput)
                if verseList:
                    referenceLocations = self.textCommandParser.getLocationsFromReference(verseList[0])
                    for referenceLocation in referenceLocations:
                        searchPattern = "exlbl\('(BL[0-9]+?)'\)"
                        found = re.findall(searchPattern, referenceLocation[0])
                        locations += found
                userInput = ""
            elif userInput == "done":
                userInput = config.terminal_cancel_action
        if not locations:
            locations = ["BL636"]
        options, descriptions = self.filterMultipleOptions(content, locations)
        # final confirmation of multiple selection; users may remove some
        locations = self.dialogs.getMultipleSelection(options=options, descriptions=descriptions, default_values=options, title="Customise Bible Map", text="Confirm locations below:")
        locations = list(set(locations))
        locations = self.textCommandParser.selectLocations(defaultChecklist=[i[2:] for i in locations])
        html = self.textCommandParser.displayMap(locations, browser=True)
        filePath = os.path.join("htmlResources", "bible_map.html")
        fullFilePath = os.path.abspath(filePath)
        with open(fullFilePath, "w", encoding="utf-8") as fileObj:
            fileObj.write(html)
        if config.terminalEnableTermuxAPI:
            self.openLocalHtmlWithAndroidApps(fullFilePath)
        else:
            webbrowser.open("file://{0}".format(fullFilePath))
        return ""
        
        #locations = "|".join(locations)
        #return self.web(f"LOCATIONS:::{locations}", False)
        #return self.web(f"LOCATIONS:::", False)

    def openTools2(self, moduleType):
        try:
            elements = {
                "parallels": ("SEARCHBOOK:::Harmonies_and_Parallels:::", "BOOK:::Harmonies_and_Parallels", "BOOK:::Harmonies_and_Parallels:::"),
                "promises": ("SEARCHBOOK:::Bible_Promises:::", "BOOK:::Bible_Promises", "BOOK:::Bible_Promises:::"),
                "names": ("SEARCHTOOL:::HBN:::", "SEARCHTOOL:::HBN:::", ""),
                "characters": ("SEARCHTOOL:::EXLBP:::", "SEARCHTOOL:::EXLBP:::", "EXLB:::exlbp:::"),
                "locations": ("SEARCHTOOL:::EXLBL:::", "SEARCHTOOL:::EXLBL:::", "EXLB:::exlbl:::"),
            }
            *_, showAll, openPrefix = elements[moduleType]
            self.print(self.divider)
            command = showAll
            self.printRunningCommand(command)
            self.print(self.divider)
            content = self.getContent(command)
            if content.startswith("[MESSAGE]"):
                content = content[10:]
            if openPrefix:
                self.print(content)
                self.print(self.divider)
                self.print(f"Enter an item to be opened:")

                userInput = self.promptSelectionFromContent(content)

                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                self.print(self.divider)
                command = f"{openPrefix}{userInput}"
                self.printRunningCommand(command)
                self.print(self.divider)
                if openPrefix in ("BOOK:::Harmonies_and_Parallels:::", "BOOK:::Bible_Promises:::"):
                    content = self.getContent(command)
                    self.print(content)
                    self.print(self.divider)
                    self.print(f"Enter an item to be opened:")

                    userInput = self.promptSelectionFromContent(content)

                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    return self.getContent(userInput)

                else:
                    return self.getContent(command)
            else:
                return content
        except:
            return self.printInvalidOptionEntered()

    def searchTools2(self, moduleType):
        try:
            elements = {
                "parallels": ("SEARCHBOOK:::Harmonies_and_Parallels:::", "BOOK:::Harmonies_and_Parallels", "BOOK:::Harmonies_and_Parallels:::"),
                "promises": ("SEARCHBOOK:::Bible_Promises:::", "BOOK:::Bible_Promises", "BOOK:::Bible_Promises:::"),
                "names": ("SEARCHTOOL:::HBN:::", "SEARCHTOOL:::HBN:::", ""),
                "characters": ("SEARCHTOOL:::EXLBP:::", "SEARCHTOOL:::EXLBP:::", "EXLB:::exlbp:::"),
                "locations": ("SEARCHTOOL:::EXLBL:::", "SEARCHTOOL:::EXLBL:::", "EXLB:::exlbl:::"),
            }
            searchPrefix, showAll, openPrefix = elements[moduleType]
            self.print(self.divider)
            self.printSearchEntryPrompt()
            userInput = prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle).strip()
            if userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            elif not userInput:
                command = showAll
            else:
                command = f"{searchPrefix}{userInput}"
            self.printRunningCommand(command)
            self.print(self.divider)
            content = self.getContent(command)
            if content.startswith("[MESSAGE]"):
                content = content[10:]
            if openPrefix:
                self.print(content)
                self.print(self.divider)
                self.print(f"Enter an item to be opened:")
                userInput = prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                self.print(self.divider)
                command = f"{openPrefix}{userInput}"
                self.printRunningCommand(command)
                self.print(self.divider)
                return self.getContent(command)
            else:
                return content
        except:
            return self.printInvalidOptionEntered()

    def quickedit(self, runOnSelectedText=True, defaultText=""):
        try:
            if runOnSelectedText:
                if defaultText:
                    self.print(self.divider)
                    self.print(defaultText)
                    self.print(self.divider)
                else:
                    self.getclipboardtext()
            options = {
                "0": ("Bible Book Notes", "EDITBOOKNOTE", ""),
                "1": ("Bible Chapter Notes", "EDITCHAPTERNOTE", ""),
                "2": ("Bible Verse Notes", "EDITVERSENOTE", ""),
                "3": ("Journals", "EDITJOURNAL", ""),
            }
            descriptions = [i[0] for i in options.values()]
            userInput = self.dialogs.getValidOptions(options=list(options.keys()), descriptions=descriptions, title="Quick Open")
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if -1 < int(userInput) < 4:
                *_, openKeyword, latestSelection = options[userInput]
                latestSelection = f"{latestSelection}:::" if latestSelection else ""
                openPrefix = f"{openKeyword}:::{latestSelection}"
                if runOnSelectedText:
                    self.print(self.runclipboardtext(openPrefix, defaultText=defaultText))
                    return ""
                else:
                    self.print(self.divider)
                    #print("Type in an entry:")
                    self.print("Enter a day in yyyy-mm-dd format:" if openKeyword == "EDITJOURNAL" else "Enter a bible reference:")
                    userInput = self.simplePrompt()
                    command = f"{openPrefix}{userInput}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def quickopen(self, runOnSelectedText=True, defaultText=""):
        try:
            if runOnSelectedText:
                if defaultText:
                    self.print(self.divider)
                    self.print(defaultText)
                    self.print(self.divider)
                else:
                    self.getclipboardtext()
            options = {
                "0": ("Bible Version", "TEXT", ""),
                "1": ("Reference in Selected Bible", "BIBLE", config.mainText),
                "2": ("Reference in Favourite Bible", "BIBLE", self.getPlusBible()[2:]),
                "3": ("Reference in Hebrew & Green Bible", "BIBLE", config.favouriteOriginalBible),
                "4": ("Commentary Module", "COMMENTARY", ""),
                "5": ("Reference in Commentary", "COMMENTARY", config.commentaryText),
                "6": ("Bible Book Notes", "OPENBOOKNOTE", ""),
                "7": ("Bible Chapter Notes", "OPENCHAPTERNOTE", ""),
                "8": ("Bible Verse Notes", "OPENVERSENOTE", ""),
                "9": ("Journals", "OPENJOURNAL", ""),
                "10": ("Bible Audio", "READ", ""),
                "11": ("Bible Maps", "MAP", ""),
                "12": ("Chapter Overview", "OVERVIEW", ""),
                "13": ("Chapter Summary", "SUMMARY", ""),
                "14": ("Chapter Index", "CHAPTERINDEX", ""),
                "15": ("Verse Index", "INDEX", ""),
                "16": ("Cross-reference", "CROSSREFERENCE", ""),
                "17": ("Bible Version Comparison", "COMPARE", ""),
                "18": ("Bible Version Differences", "DIFFERENCE", ""),
                "19": ("Treasury of Scripture Knowledge (Enhanced)", "TSKE", ""),
                "20": ("Original Words", "WORDS", ""),
                "21": ("Original Word Translation", "TRANSLATION", ""),
                "22": ("Discourse Features", "DISCOURSE", ""),
                "23": ("Words, Translation & Discourse Combo", "COMBO", ""),
                "24": ("Bible Topics", "EXLB", "exlbt"),
                "25": ("Bible Encyclopedia", "ENCYCLOPEDIA", config.encyclopedia),
                "26": ("Bible Dictionary", "DICTIONARY", ""),
                "27": ("Third-party dictionary", "THIRDDICTIONARY", config.thirdDictionary),
                "28": ("Bible Parallels", "BOOK", "Harmonies_and_Parallels"),
                "29": ("Bible Promises", "BOOK", "Bible_Promises"),
                "30": ("Bible Characters", "EXLB", "exlbp"),
                "31": ("Bible Locations", "EXLB", "exlbl"),
                "32": ("Reference Book", "BOOK", config.book),
                "33": ("Bible Lexicon Entries", "LEXICON", config.lexicon),
                "34": ("Bible Lexicon Content", "REVERSELEXICON", config.lexicon),
                "35": ("Bible Concordance", "CONCORDANCE", config.concordance),
            }
            descriptions = [i[0] for i in options.values()]
            userInput = self.dialogs.getValidOptions(options=list(options.keys()), descriptions=descriptions, title="Quick Open")
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if userInput in options:
                *_, openKeyword, latestSelection = options[userInput]
                latestSelection = f"{latestSelection}:::" if latestSelection else ""
                if openKeyword == "COMMENTARY":
                    latestSelection = ":::"
                openPrefix = f"{openKeyword}:::{latestSelection}"
                if runOnSelectedText:
                    self.print(self.runclipboardtext(openPrefix, defaultText=defaultText))
                    return ""
                else:
                    self.print(self.divider)
                    self.print("Type in an entry:")
                    userInput = self.simplePrompt()
                    command = f"{openPrefix}{userInput}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def quickSearch(self, runOnSelectedText=True, defaultText=""):
        try:
            if runOnSelectedText:
                if defaultText:
                    self.print(self.divider)
                    self.print(defaultText)
                    self.print(self.divider)
                else:
                    self.getclipboardtext()
            searchModes = ("COUNT", "SEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
            options = {
                "0": ("Whole Bible", searchModes[config.bibleSearchMode], "", config.mainText, ""),
                "1": ("Old Testament", searchModes[config.bibleSearchMode], "", config.mainText, ":::OT"),
                "2": ("New Testament", searchModes[config.bibleSearchMode], "", config.mainText, ":::NT"),
                "3": (self.bibleBooks.getStandardBookFullName(config.mainB), searchModes[config.bibleSearchMode], "", config.mainText, f":::{self.bibleBooks.getStandardBookAbbreviation(config.mainB)}"),
                "4": ("Bible Book Notes", "SEARCHBOOKNOTE", "OPENBOOKNOTE", "", ""),
                "5": ("Bible Chapter Notes", "SEARCHCHAPTERNOTE", "OPENCHAPTERNOTE", "", ""),
                "6": ("Bible Verse Notes", "SEARCHVERSENOTE", "OPENVERSENOTE", "", ""),
                "7": ("Journals", "SEARCHJOURNAL", "OPENJOURNAL", "", ""),
                "8": ("Bible Topics", "SEARCHTOOL", "EXLB", "EXLBT", ""),
                "9": ("Bible Encyclopedia", "SEARCHTOOL", "ENCYCLOPEDIA", config.encyclopedia, ""),
                "10": ("Bible Dictionary", "SEARCHTOOL", "DICTIONARY", config.dictionary, ""),
                "11": ("Third-party dictionary", "SEARCHTHIRDDICTIONARY", "THIRDDICTIONARY", config.thirdDictionary, ""),
                "12": ("Bible Parallels", "SEARCHBOOK", "BOOK", "Harmonies_and_Parallels", ""),
                "13": ("Bible Promises", "SEARCHBOOK", "BOOK", "Bible_Promises", ""),
                "14": ("Bible Names", "SEARCHTOOL", "", "HBN", ""),
                "15": ("Bible Characters", "SEARCHTOOL", "EXLB", "EXLBP", ""),
                "16": ("Bible Locations", "SEARCHTOOL", "EXLB", "EXLBL", ""),
                "17": ("Reference Book", "SEARCHBOOK", "BOOK", config.book, ""),
                "18": ("Bible Lexicon Entries", "SEARCHLEXICON", "LEXICON", config.lexicon, ""),
                "19": ("Bible Lexicon Content", "REVERSELEXICON", "", config.lexicon, ""),
                "20": ("Bible Concordance", "CONCORDANCE", "", config.concordance, ""),
            }
            descriptions = [i[0] for i in options.values()]
            userInput = self.dialogs.getValidOptions(options=list(options.keys()), descriptions=descriptions, title="Quick Open")
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if -1 < int(userInput) < 21:
                feature, searchKeyword, openKeyword, latestSelection, searchSuffix = options[userInput]
                latestSelection = f"{latestSelection}:::" if latestSelection else ""
                searchPrefix = f"{searchKeyword}:::{latestSelection}"
                if feature == "Bible Dictionary":
                    latestSelection = ""
                if openKeyword == "EXLB":
                    latestSelection = latestSelection.lower()
                config.terminalCommandDefault = f"{openKeyword}:::{latestSelection}" if openKeyword else ""
                if openKeyword:
                    if runOnSelectedText:
                        self.print(self.runclipboardtext(searchPrefix, searchSuffix, defaultText=defaultText))
                        return ""
                    else:
                        self.print(self.divider)
                        self.print("Enter a search item:")
                        userInput = self.simplePrompt()
                        command = f"{searchPrefix}{userInput}{searchSuffix}"
                        self.printRunningCommand(command)
                        self.print(self.getContent(command))
                        return ""
                else:
                    if runOnSelectedText:
                        return self.runclipboardtext(searchPrefix, searchSuffix, defaultText=defaultText)
                    else:
                        self.print(self.divider)
                        self.print("Enter a search item:")
                        userInput = self.simplePrompt()
                        command = f"{searchPrefix}{userInput}{searchSuffix}"
                        self.printRunningCommand(command)
                        return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def searchTools(self, moduleType, showModules):
        try:
            elements = {
                "BOOK": (config.book, self.crossPlatform.referenceBookList, config.bookChapter, self.terminal_books_selection_session, "SEARCHBOOK"),
                "TOPICS": (config.topic, self.crossPlatform.topicListAbb, config.topicEntry, self.terminal_topics_selection_session, ""),
                "ENCYCLOPEDIA": (config.encyclopedia, self.crossPlatform.encyclopediaListAbb, config.encyclopediaEntry, self.terminal_encyclopedia_selection_session, ""),
                "DICTIONARY": (config.dictionary, self.crossPlatform.dictionaryListAbb, config.dictionaryEntry, self.terminal_dictionary_selection_session, ""),
                "THIRDDICTIONARY": (config.thirdDictionary, self.crossPlatform.thirdPartyDictionaryList, config.thirdDictionaryEntry, self.terminal_thridPartyDictionaries_selection_session, "SEARCHTHIRDDICTIONARY"),
                "LEXICON": (config.lexicon, self.crossPlatform.lexiconList, config.lexiconEntry, self.terminal_lexicons_selection_session, "SEARCHLEXICON"),
                "REVERSELEXICON": (config.lexicon, self.crossPlatform.lexiconList, "", self.terminal_lexicons_selection_session, "REVERSELEXICON"),
            }
            self.print(self.divider)
            self.print(showModules())
            default, abbList, latestEntry, historySession, searchKeyword = elements[moduleType]
            if not searchKeyword:
                searchKeyword = "SEARCHTOOL"
            userInput = self.searchablePrompt(self.inputIndicator, options=abbList, promptSession=historySession, default=default)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in abbList:
                module = userInput
                self.print(self.divider)
                self.printSearchEntryPrompt()
                userInput = prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                command = f"{searchKeyword}:::{module}:::{userInput}"
                self.printRunningCommand(command)
                self.print(self.divider)
                content = self.getContent(command)
                if moduleType == "REVERSELEXICON":
                    return content
                self.print(content[10:] if content.startswith("[MESSAGE]") else content)
                self.print(self.divider)
                self.print(f"To open, enter a module entry (e.g. {latestEntry}):")
                userInput = prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                self.print(self.divider)

                if moduleType == "TOPICS":
                    command = f"EXLB:::exlbt:::{userInput}"
                elif moduleType == "DICTIONARY":
                    command = f"{moduleType}:::{userInput}"
                else:
                    command = f"{moduleType}:::{module}:::{userInput}"
                self.printRunningCommand(command)
                return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def openTools(self, moduleType, showModules, defaultModule=""):
        try:
            elements = {
                "TOPICS": (config.topic, self.crossPlatform.topicListAbb, self.crossPlatform.topicList, config.topicEntry, self.terminal_topics_selection_session, ""),
                "ENCYCLOPEDIA": (config.encyclopedia, self.crossPlatform.encyclopediaListAbb, self.crossPlatform.encyclopediaList, config.encyclopediaEntry, self.terminal_encyclopedia_selection_session, ""),
                "DICTIONARY": (config.dictionary, self.crossPlatform.dictionaryListAbb, self.crossPlatform.dictionaryList, config.dictionaryEntry, self.terminal_dictionary_selection_session, ""),
                "THIRDDICTIONARY": (config.thirdDictionary, self.crossPlatform.thirdPartyDictionaryList, self.crossPlatform.thirdPartyDictionaryList, config.thirdDictionaryEntry, self.terminal_thridPartyDictionaries_selection_session, "SEARCHTHIRDDICTIONARY"),
                "LEXICON": (config.lexicon, self.crossPlatform.lexiconList, self.crossPlatform.lexiconList, config.lexiconEntry, self.terminal_lexicons_selection_session, "SEARCHLEXICON"),
            }
            if not defaultModule:
                self.print(self.divider)
                self.print(showModules())
            default, abbList, nameList, latestEntry, historySession, searchKeyword = elements[moduleType]
            if defaultModule:
                default = defaultModule
            if not searchKeyword:
                searchKeyword = "SEARCHTOOL"
            userInput = self.searchablePrompt(self.inputIndicator, options=abbList, descriptions=nameList, promptSession=historySession, default=default, accept_default=True if defaultModule else False)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in abbList:
                module = userInput
                self.print(self.divider)
                command = f"{searchKeyword}:::{module}:::"
                self.printRunningCommand(command)
                self.print(self.divider)
                content = self.getContent(command)
                content = re.sub(f"<{config.terminalResourceLinkColor}>[^<>]+?','", f"<{config.terminalResourceLinkColor}>", content)
                if moduleType == "REVERSELEXICON":
                    return content
                self.print(content[10:] if content.startswith("[MESSAGE]") else content)
                self.print(self.divider)
                self.print(f"Enter a module entry (e.g. {latestEntry}):")
                userInput = self.promptSelectionFromContent(content)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                self.print(self.divider)

                if moduleType == "TOPICS":
                    command = f"EXLB:::exlbt:::{userInput}"
                elif moduleType == "DICTIONARY":
                    command = f"{moduleType}:::{userInput}"
                else:
                    command = f"{moduleType}:::{module}:::{userInput}"
                self.printRunningCommand(command)
                return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def openreferencebook(self, default="", accept_default=False):
        try:
            self.print(self.divider)
            self.print(self.showreferencebooks())
            self.print(self.divider)
            self.print("Enter a book name:")
            userInput = self.searchablePrompt(self.inputIndicator, options=self.crossPlatform.referenceBookList, promptSession=self.terminal_books_selection_session, default=default if default else config.book, accept_default=accept_default)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.crossPlatform.referenceBookList:
                book = userInput
                chapterList = Book(book).getTopicList()
                chapterDisplay = "<h2>Chapters</h2>"
                chapterDisplay += "<br>".join([f"<ref>{chapter}</ref>" for chapter in chapterList])
                self.print(self.divider)
                self.print(TextUtil.htmlToPlainText(chapterDisplay).strip())
                self.print(self.divider)
                self.print("Enter a chapter title:")
                userInput = self.searchablePrompt(self.inputIndicator, options=chapterList, default=config.bookChapter if config.bookChapter in chapterList else "")
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput in chapterList:
                    command = f"BOOK:::{book}:::{userInput}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
                else:
                    return self.printInvalidOptionEntered()
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def journalFeature(self, feature="OPENJOURNAL"):
        try:
            today = date.today()
            self.print(self.divider)
            self.print(f"Enter a year, e.g. {today.year}:")
            userInput = prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle, default=str(today.year)).strip()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if int(userInput):
                year = userInput
                self.print(self.divider)
                self.print(f"Enter a month, e.g. {today.month}:")
                userInput = prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle, default=str(today.month)).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if int(userInput):
                    month = userInput
                    self.print(self.divider)
                    self.print(f"Enter a day, e.g. {today.day}:")
                    userInput = prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle, default=str(today.day)).strip()
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    if int(userInput):
                        day = userInput
                        command = f"{feature}:::{year}-{month}-{day}"
                        self.printRunningCommand(command)
                        return self.getContent(command)
                    else:
                        return self.printInvalidOptionEntered()
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openbiblemodulenote(self):
        try:
            self.print(self.divider)
            self.print(self.showbibles())
            self.print(self.divider)
            self.print("Enter a bible abbreviation:")
            self.print("(choose a bible module that contains notes)")
            # select bible or bibles
            defaultText = self.getDefaultText()
            userInput = self.getBibleVersion(defaultText)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.crossPlatform.textList:
                bible = userInput
                self.print(self.divider)
                self.print(self.showbibleabbreviations(text=bible))
                self.print(self.divider)
                self.printChooseItem()
                self.print("(enter a book number)")
                # select bible book
                defaultBook = config.mainB if config.mainB in self.bookNumbers else self.bookNumbers[0]
                userInput = self.getBibleBookNumber(defaultBook)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if int(userInput) in self.bookNumbers:
                    bibleBookNumber = userInput
                    self.print(self.divider)
                    self.showbiblechapters(text=bible, b=bibleBookNumber)
                    self.print(self.divider)
                    self.printChooseItem()
                    self.print("(enter a chapter number)")
                    # select bible chapter
                    defaultChapter = config.mainC if config.mainC in self.currentBibleChapters else self.currentBibleChapters[0]
                    userInput = self.getBibleChapterNumber(defaultChapter)
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    if int(userInput) in self.currentBibleChapters:
                        bibleChapter = userInput
                        self.print(self.divider)
                        self.showbibleverses(text=bible, b=bibleBookNumber, c=int(userInput))
                        self.print(self.divider)
                        self.printChooseItem()
                        self.print("(enter a verse number)")
                        # select verse number
                        defaultVerse = config.mainV if config.mainV in self.currentBibleVerses else self.currentBibleVerses[0]
                        userInput = self.getBibleVerseNumber(defaultVerse)
                        if not userInput or userInput.lower() == config.terminal_cancel_action:
                            return self.cancelAction()
                        if int(userInput) in self.currentBibleVerses:
                            bibleVerse = userInput
                            command = f"_biblenote:::{bible}:::{bibleBookNumber}.{bibleChapter}.{bibleVerse}"
                            self.printRunningCommand(command)
                            return self.getContent(command)
                        else:
                            return self.printInvalidOptionEntered()
                else:
                    return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def readword(self, lexeme=False, dataOnly=False):
        try:
            self.print(self.divider)
            self.print(self.showbibleabbreviations(text="KJV"))
            self.print(self.divider)
            self.print("Enter a book number:")
            bookNo = self.getBibleBookNumber()
            if not bookNo or bookNo.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if 66 >= int(bookNo) > 0:
                self.print(self.divider)
                self.showbiblechapters(text="KJV", b=int(bookNo))
                self.print(self.divider)
                self.print("Enter a chapter number:")
                chapterNo = self.getBibleChapterNumber()
                if not chapterNo or chapterNo.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if int(chapterNo) in self.currentBibleChapters:
                    self.print(self.divider)
                    self.showbibleverses(text="KJV", b=int(bookNo), c=int(chapterNo))
                    self.print(self.divider)
                    self.print("Enter a verse number:")
                    verseNo = self.getBibleVerseNumber()
                    if not verseNo or verseNo.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    if int(verseNo) in self.currentBibleVerses:
                        self.print(self.divider)
                        reference = self.textCommandParser.bcvToVerseReference(int(bookNo), int(chapterNo), int(verseNo))
                        translations = self.getContent(f"TRANSLATION:::{reference}")
                        self.print(translations)
                        entries = re.compile("<{0}>([0-9]+?)</{0}>.*?\][^\[\]]*?<{0}>(.*?)</{0}>".format(config.terminalResourceLinkColor)).findall(translations)
                        options = []
                        descriptions = []
                        if entries:
                            for option, description in entries:
                                options.append(option)
                                descriptions.append(description)
                        self.print(self.divider)
                        self.print("Enter a word number:")
                        wordNo = self.searchablePrompt(options=options, descriptions=descriptions, bold_descriptions=(int(bookNo) < 40), numberOnly=True)
                        if not wordNo or wordNo.lower() == config.terminal_cancel_action:
                            return self.cancelAction()
                        if dataOnly:
                            command = f"WORD:::{bookNo}:::{wordNo}"
                        else:
                            command = f"{'READLEXEME' if lexeme else 'READWORD'}:::{'BHS5' if int(bookNo) < 40 else 'OGNT'}.{bookNo}.{chapterNo}.{verseNo}.{int(wordNo)}"
                        self.print(self.divider)
                        self.printRunningCommand(command)
                        content = self.getContent(command)
                        return content
                    else:
                        return self.printInvalidOptionEntered()
                else:
                    return self.printInvalidOptionEntered()
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openversefeature(self, feature="CROSSREFERENCE"):
        try:
            firstBible = config.mainText
            self.print(self.divider)
            self.print(self.showbibleabbreviations(text=firstBible))
            self.print(self.divider)
            self.printChooseItem()
            self.print("(enter a book abbreviation)")
            userInput = self.getBibleBookAbb(self.currentBibleBookNo)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.currentBibleAbbs:
                abbIndex = self.currentBibleAbbs.index(userInput)
                bibleBookNumber = self.bookNumbers[abbIndex]
                bibleAbb = userInput
                self.print(self.divider)
                self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                self.print(self.divider)
                self.printChooseItem()
                self.print("(enter a chapter number)")
                defaultChapter = config.mainC if config.mainC in self.currentBibleChapters else self.currentBibleChapters[0]
                userInput = self.getBibleChapterNumber(defaultChapter)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if int(userInput) in self.currentBibleChapters:
                    bibleChapter = userInput
                    self.print(self.divider)
                    self.showbibleverses(text=firstBible, b=bibleBookNumber, c=int(userInput))
                    self.print(self.divider)
                    self.printChooseItem()
                    self.print("(enter a verse number)")
                    defaultVerse = config.mainV if config.mainV in self.currentBibleVerses else self.currentBibleVerses[0]
                    userInput = self.getBibleVerseNumber(defaultVerse)
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    if int(userInput) in self.currentBibleVerses:
                        bibleVerse = userInput
                        command = f"{feature}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                        self.printRunningCommand(command)
                        return self.getContent(command)
                    else:
                        return self.printInvalidOptionEntered()
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openchapterfeature(self, feature="OVERVIEW"):
        try:
            firstBible = config.mainText
            self.print(self.divider)
            self.print(self.showbibleabbreviations(text=firstBible))
            self.print(self.divider)
            self.printChooseItem()
            self.print("(enter a book abbreviation)")
            userInput = self.getBibleBookAbb(self.currentBibleBookNo)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.currentBibleAbbs:
                abbIndex = self.currentBibleAbbs.index(userInput)
                bibleBookNumber = self.bookNumbers[abbIndex]
                bibleAbb = userInput
                self.print(self.divider)
                self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                self.print(self.divider)
                self.printChooseItem()
                self.print("(enter a chapter number)")
                defaultChapter = config.mainC if config.mainC in self.currentBibleChapters else self.currentBibleChapters[0]
                userInput = self.getBibleChapterNumber(defaultChapter)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if int(userInput) in self.currentBibleChapters:
                    bibleChapter = userInput
                    command = f"{feature}:::{bibleAbb} {bibleChapter}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
                else:
                    return self.printInvalidOptionEntered()
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openbookfeature(self, feature="introduction"):
        try:
            firstBible = config.mainText
            self.print(self.divider)
            self.print(self.showbiblebooks(text=firstBible))
            self.print(self.divider)
            self.printChooseItem()
            self.print("(enter a book name)")
            userInput = self.getBibleBookName(self.currentBibleBookNo)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.currentBibleBooks:
                bibleBook = userInput
                features = {
                    "introduction": ("SEARCHBOOKCHAPTER:::Tidwell_The_Bible_Book_by_Book", "BOOK:::Tidwell_The_Bible_Book_by_Book"),
                    "dictionary": (f"SEARCHTOOL:::{config.dictionary}", "DICTIONARY"),
                    "encyclopedia": (f"SEARCHTOOL:::{config.encyclopedia}", f"ENCYCLOPEDIA:::{config.encyclopedia}"),
                    "timelines": "SEARCHBOOKCHAPTER:::Timelines",
                }
                searchPrefix, openPrefix = features.get(feature, (feature, ""))
                command = f"{searchPrefix}:::{bibleBook}"
                self.printRunningCommand(command)
                content = self.getContent(command)
                if not openPrefix:
                    return content
                content = re.sub("(<{0}>)[^<>]*?','".format(config.terminalResourceLinkColor), r"\1", content)
                self.print(self.divider)
                self.print(content)
                userInput = self.promptSelectionFromContent(content)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                command = f"{openPrefix}:::{userInput}"
                self.printRunningCommand(command)
                self.print(self.divider)
                return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openbible(self):
        try:
            self.print(self.divider)
            self.print(self.showbibles())
            self.print(self.divider)
            self.printChooseItem()
            self.print("Enter a bible abbreviation to open a single version, e.g. 'KJV'")
            self.print("To compare multiple versions, use '_' as a separator, e.g. 'KJV_NET_OHGBi'")
            # select bible or bibles
            if config.terminalBibleComparison:
                userInput = self.getBibleVersions()
            else:
                defaultText = self.getDefaultText()
                userInput = self.getBibleVersion(defaultText)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if self.isValidBibles(userInput):
                bible = userInput
                firstBible = bible.split("_")[0]
                self.print(self.divider)
                self.print(self.showbibleabbreviations(text=firstBible))
                self.print(self.divider)
                self.printChooseItem()
                self.print("(enter a book abbreviation)")
                # select bible book
                userInput = self.getBibleBookAbb(self.currentBibleBookNo)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput in self.currentBibleAbbs:
                    abbIndex = self.currentBibleAbbs.index(userInput)
                    bibleBookNumber = self.bookNumbers[abbIndex]
                    bibleAbb = userInput
                    self.print(self.divider)
                    self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                    self.print(self.divider)
                    self.printChooseItem()
                    self.print("(enter a chapter number)")
                    # select bible chapter
                    defaultChapter = config.mainC if config.mainC in self.currentBibleChapters else self.currentBibleChapters[0]
                    userInput = self.getBibleChapterNumber(defaultChapter)
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    if int(userInput) in self.currentBibleChapters:
                        bibleChapter = userInput
                        self.print(self.divider)
                        self.showbibleverses(text=firstBible, b=bibleBookNumber, c=int(userInput))
                        self.print(self.divider)
                        self.printChooseItem()
                        self.print("(enter a verse number)")
                        # select verse number
                        defaultVerse = config.mainV if config.mainV in self.currentBibleVerses else self.currentBibleVerses[0]
                        userInput = self.getBibleVerseNumber(defaultVerse)
                        if not userInput or userInput.lower() == config.terminal_cancel_action:
                            return self.cancelAction()
                        if int(userInput) in self.currentBibleVerses:
                            bibleVerse = userInput
                            # formulate UBA command
                            if "_" in bible:
                                command = f"COMPARE:::{bible}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                            else:
                                command = f"BIBLE:::{bible}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                            self.printRunningCommand(command)
                            return self.getContent(command)
                        else:
                            return self.printInvalidOptionEntered()
                else:
                    return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def whatis(self):
        try:
            self.print(self.divider)
            self.print(self.commands())
            self.print(self.divider)
            self.printChooseItem()
            commands = self.getTextCommandSuggestion(False)
            userInput = self.searchablePrompt(self.inputIndicator, options=commands)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in commands:
                return self.whatiscontent(userInput)
        except:
            return self.printInvalidOptionEntered()

    def whatiscontent(self, command):
        if command in self.dotCommands:
            self.print(self.dotCommands[command][0])
        else:
            self.print(self.getContent(f"_whatis:::{command}"))
        return ""

    def searchconcordance(self):
        try:
            self.print(self.divider)
            self.print(self.showstrongbibles())
            self.printChooseItem()
            self.print("Enter a bible abbreviation to search a single version, e.g. 'KJVx'")
            self.print("To search multiple versions, use '_' as a separator, e.g. 'KJVx_RWVx_OHGBi'")
            userInput = self.getStrongBibleVersions()
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if self.isValidBibles(userInput):
                # bible version(s) defined
                bible = userInput
                self.print(self.divider)
                self.print("Enter a Strong's number or lexical entry:")
                userInput = self.simplePrompt()
                command = f"CONCORDANCE:::{bible}:::{userInput}"
                self.printRunningCommand(command)
                return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def searchbible(self):
        try:
            self.print(self.divider)
            self.print(self.showbibles())
            self.print(self.divider)
            self.printChooseItem()
            self.print("Enter a bible abbreviation to search a single version, e.g. 'KJV'")
            self.print("To search multiple versions, use '_' as a separator, e.g. 'KJV_NET_WEB'")
            if config.terminalBibleComparison:
                userInput = self.getBibleVersions()
            else:
                defaultText = self.getDefaultText()
                userInput = self.getBibleVersion(defaultText)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if self.isValidBibles(userInput):
                # bible version(s) defined
                bible = userInput

                firstBible = bible.split("_")[0]
                self.print(self.divider)
                self.print(self.showbibleabbreviations(text=firstBible))
                self.print(self.divider)
                self.printChooseItem()
                self.print("(enter bible books for search)")
                self.print("(use ',' as a separator between books)")
                self.print("(use '-' as a range indicator)")
                self.print("(e.g. 'ALL', 'OT', 'NT', 'Gen, John', 'Matt-John, 1Cor, Rev', etc.)")
                # select bible book range
                completion = ["ALL", "OT", "NT"] + self.currentBibleAbbs
                userInput = self.getBibleBookRange(options=completion)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if BibleVerseParser(config.parserStandarisation).extractBookListAsString(userInput):
                    # define book range
                    bookRange = userInput

                    searchOptions = {
                        "COUNT": ("count occurrence of a string", "plain text", r"Jesus%love"),
                        "SEARCH": ("search for string", "plain text", r"Jesus%love"),
                        "ANDSEARCH": ("search for a combination of strings appeared in the same verse", "multiple plain text strings, delimited by '|'", "Jesus|love|disciple"),
                        "ORSEARCH": ("search for either one of the entered strings appeared in a single verse", "multiple plain text strings, delimited by '|'", "Jesus|love|disciple"),
                        "ADVANCEDSEARCH": ("search for a condition or a combination of conditions", "condition statement placed after the keyword 'WHERE' in a SQL query", 'Book = 1 AND Scripture LIKE "%worship%"'),
                        "REGEXSEARCH": ("search for a regular expression", "regular expression", "Jesus.*?love"),
                    }
                    searchOptionsList = list(searchOptions.keys())
                    userInput = self.dialogs.getValidOptions(options=["0", "1", "2", "3", "4", "5"], descriptions=["count occurrence", "search text", "'and' combination", "'or' combination", "query condition", "regular expression"], default=str(config.bibleSearchMode), title="Bible Search Mode", text="Select a mode:")
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    userInput = int(userInput)
                    if -1 < userInput < 6:
                        # define bibleSearchMode
                        config.bibleSearchMode = userInput
                        # define command keyword
                        keyword = searchOptionsList[userInput]
                        self.print(self.divider)
                        self.printSearchEntryPrompt()
                        description, stringFormat, example = searchOptions[keyword]
                        self.print(f"{keyword} - {description}")
                        self.print(f"(format: {stringFormat})")
                        self.print(f"(example: {example})")
                        userInput = self.terminal_search_bible_session.prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle).strip()
                        if not userInput or userInput.lower() == config.terminal_cancel_action:
                            return self.cancelAction()
                        searchString = userInput
                        command = f"{keyword}:::{bible}:::{searchString}:::{bookRange}"

                        # Check if it is a case-sensitive search
                        self.print(self.divider)
                        self.print("Case sensitive? ([y]es or [n]o)")
                        userInput = prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle, default="Y" if config.enableCaseSensitiveSearch else "N").strip()
                        if not userInput or userInput.lower() == config.terminal_cancel_action:
                            return self.cancelAction()
                        if userInput.lower() in ("yes", "y", "no", "n"):
                            config.enableCaseSensitiveSearch = (userInput.lower()[0] == "y")
                            if config.bibleSearchMode == 0:
                                content = self.getContent(command)
                                # selection of search result in a book
                                entries = re.compile("<{0}>(.*?)</{0}>.*?<{0}>([1-9][0-9]*?)</{0}>.*?$".format(config.terminalResourceLinkColor), flags=re.M).findall(content)
                                options = []
                                descriptions = []
                                if entries:
                                    for book, hit in entries:
                                        options.append(book)
                                        descriptions.append(f"{book} x {hit}")
                                    currentAbb = self.bibleBooks.getStandardBookAbbreviation(config.mainB)
                                    default = currentAbb if currentAbb in options else options[0]
                                    bookAbb = self.dialogs.getValidOptions(options=options, descriptions=descriptions, default=default)
                                    if not bookAbb in self.bibleBooks.name2number and not f"{bookAbb}." in self.bibleBooks.name2number:
                                        return self.printInvalidOptionEntered()
                                    if not bookAbb in self.bibleBooks.name2number:
                                        bookAbb = f"{bookAbb}."
                                    command = f"""ADVANCEDSEARCH:::{bible}:::Book = {self.bibleBooks.name2number[bookAbb]} AND Scripture LIKE '%{searchString}%'"""
                                    self.printRunningCommand(command)
                                    return self.getContent(command)
                                else:
                                    self.print("[not found]")
                                    return ""

                            else:
                                self.printRunningCommand(command)
                                return self.getContent(command)
                        else:
                            return self.printInvalidOptionEntered()
                    else:
                        return self.printInvalidOptionEntered()
                else:
                    return self.printInvalidOptionEntered()
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def opencommentary(self):
        try:
            self.print(self.divider)
            self.print(self.showcommentaries())
            self.print(self.divider)
            self.printChooseItem()
            self.print("Enter a commentary abbreviation, e.g. 'CBSC'")
            defaultText = config.commentaryText
            userInput = self.searchablePrompt(self.inputIndicator, options=self.crossPlatform.commentaryList, descriptions=self.crossPlatform.commentaryFullNameList, promptSession=self.terminal_commentary_selection_session, default=defaultText)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            if userInput in self.crossPlatform.commentaryList:
                module = userInput
                firstBible = "KJV"
                self.print(self.divider)
                self.print(self.showbibleabbreviations(text=firstBible, commentary=True))
                self.print(self.divider)
                self.printChooseItem()
                self.print("(enter a book abbreviation)")
                userInput = self.getBibleBookAbb(self.currentBibleBookNo)
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput in self.currentBibleAbbs:
                    abbIndex = self.currentBibleAbbs.index(userInput)
                    bibleBookNumber = self.bookNumbers[abbIndex]
                    bibleAbb = userInput
                    self.print(self.divider)
                    self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                    self.print(self.divider)
                    self.printChooseItem()
                    self.print("(enter a chapter number)")
                    defaultChapter = config.commentaryC if config.commentaryC in self.currentBibleChapters else self.currentBibleChapters[0]
                    userInput = self.getBibleChapterNumber(defaultChapter)
                    if not userInput or userInput.lower() == config.terminal_cancel_action:
                        return self.cancelAction()
                    if int(userInput) in self.currentBibleChapters:
                        bibleChapter = userInput
                        self.print(self.divider)
                        self.showbibleverses(text=firstBible, b=bibleBookNumber, c=int(userInput))
                        self.print(self.divider)
                        self.printChooseItem()
                        self.print("(enter a verse number)")
                        defaultVerse = config.commentaryV if config.commentaryV in self.currentBibleVerses else self.currentBibleVerses[0]
                        userInput = self.getBibleVerseNumber(defaultVerse)
                        if not userInput or userInput.lower() == config.terminal_cancel_action:
                            return self.cancelAction()
                        if int(userInput) in self.currentBibleVerses:
                            bibleVerse = userInput
                            command = f"COMMENTARY:::{module}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                            self.printRunningCommand(command)
                            return self.getContent(command)
                        else:
                            return self.printInvalidOptionEntered()
                else:
                    return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def getDefaultText(self):
        if config.mainText in self.crossPlatform.textList:
            defaultText = config.mainText
        elif config.favouriteBible in self.crossPlatform.textList:
            defaultText = config.favouriteBible
        elif config.favouriteBible2 in self.crossPlatform.textList:
            defaultText = config.favouriteBible2
        elif config.favouriteBible3 in self.crossPlatform.textList:
            defaultText = config.favouriteBible3
        else:
            defaultText = self.crossPlatform.textList[0]
        return defaultText

    def isValidBibles(self, userInput):
        if userInput:
            for bible in userInput.split("_"):
                if not bible in self.crossPlatform.textList:
                    return False
            return True
        return False

    def changecolors(self):
        optionMap = {
            "terminalPromptIndicatorColor1": "Prompt Indicator Color 1",
            "terminalCommandEntryColor1": "Prompt Entry Color 1",
            "terminalPromptIndicatorColor2": "Prompt Indicator Color 2",
            "terminalCommandEntryColor2": "Prompt Entry Color 2",
            "terminalHeadingTextColor": "Terminal Heading Text Color",
            "terminalVerseNumberColor": "Terminal Verse Number Color",
            "terminalResourceLinkColor": "Terminal Resource Link Color",
            "terminalVerseSelectionBackground": "Terminal Verse Selection Background",
            "terminalVerseSelectionForeground": "Terminal Verse Selection Foreground",
            "terminalSearchHighlightBackground": "Terminal Search Highlight Background",
            "terminalSearchHighlightForeground": "Terminal Search Highlight Foreground",
            "terminalFindHighlightBackground": "Terminal Find Highlight Background",
            "terminalFindHighlightForeground": "Terminal Find Highlight Foreground",
        }
        options = []
        descriptions = []
        for key, value in optionMap.items():
            options.append(key)
            descriptions.append(value)
        userInput = self.dialogs.getValidOptions(options=options, descriptions=descriptions, title="Change Colours", text="Select an item:")
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        try:
            configitem = userInput
            options = []
            descriptions = []
            for i in config.terminalColors.keys():
                options.append(i)
                descriptions.append(i[4:])
            userInput = self.dialogs.getValidOptions(options=options, descriptions=descriptions, title=configitem, text="Select a colour:", default=eval(f"config.{configitem}"))
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            else:
                color = userInput
                command = f"_setconfig:::{configitem}:::'{color}'"
                self.printRunningCommand(command)
                return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def swap(self):
        command = f"TEXT:::{(self.getPlusBible()[2:])}"
        self.printRunningCommand(command)
        return self.getContent(command)

    # Shared prompt message

    def toast(self, message):
        if config.terminalEnableTermuxAPI and config.terminalEnableTermuxAPIToast:
            self.getContent(f"cmd:::termux-toast -s {message}")

    def actionDone(self):
        message = "Done!"
        self.print(message)
        self.toast(message)
        return ""

    def downloadbibleaudio(self, default=""):
        options = list(self.crossPlatform.verseByVerseAudio.keys())
        userInput = self.dialogs.getValidOptions(options=options, title="Downlaod Bible Audio", default=default)
        if not userInput or userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        self.print(f"You selected '{userInput}'.")
        module, repo, *_ = self.crossPlatform.verseByVerseAudio[userInput]
        self.downloadbibleaudioaction(module, repo)

    def downloadbibleaudioaction(self, module, repo):
        try:
            self.print(self.divider)
            audioDir = os.path.join(config.audioFolder, "bibles", module, "default")
            Path(audioDir).mkdir(parents=True, exist_ok=True)
            # remove old files
            if os.path.isdir(audioDir):
                # os.rmdir does not work with sub directories
                # os.rmdir(audioDir)
                # use shutil.rmtree instead
                shutil.rmtree(audioDir)
            os.system(f"git clone https://github.com/{repo} {audioDir}")
            self.print("Downloaded!")
            self.print("unpacking files ...")
            for item in os.listdir(audioDir):
                zipFile = os.path.join(audioDir, item)
                if os.path.isfile(zipFile) and item.endswith(".zip"):
                    #os.system(f"unzip {zipFile}")
                    # Unzip file
                    shutil.unpack_archive(zipFile, audioDir)
                    # Delete zip file
                    os.remove(zipFile)
            self.print("Installed!")
        except:
            self.print("Errors!")

    def cancelAction(self):
        config.terminalCommandDefault = ""
        message = "Action cancelled!"
        self.print(self.divider)
        self.print(message)
        self.toast(message)
        self.clipboardMonitorFeature()
        return ""

    def printChooseItem(self):
        self.print("Choose an item:")

    def printCancelOption(self):
        self.print(f"(or enter '{config.terminal_cancel_action}' to cancel)")

    def printInvalidOptionEntered(self):
        if config.developer:
            print(traceback.format_exc())
        message = "Invalid option entered!"
        self.print(message)
        self.toast(message)
        return ""

    def printRunningCommand(self, command):
        self.command = command
        self.print(f"Running {command} ...")

    def printEnterNumber(self, number):
        self.print(f"Enter a number [0 ... {number}]:")

    # Get the latest content in plain text
    def getPlainText(self, content=None):
        return TextUtil.htmlToPlainText(self.html if content is None else content, False).strip()

    def printSearchEntryPrompt(self):
        self.print("Enter a search item:")

    def searchNote(self, keyword="SEARCHBOOKNOTE"):
        try:
            self.print(self.divider)
            self.printSearchEntryPrompt()
            userInput = prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle).strip()
            if userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            command = f"{keyword}:::{userInput}"
            self.printRunningCommand(command)
            return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def clipboardMonitorFeature(self):
        try:
            self.showClipboardMonitorStatus()
            if config.terminalEnableClipboardMonitor:
                # check English definition of selected word
                selectedText = self.getclipboardtext()
                if selectedText:
                    if selectedText in HBN.entries:
                        definition = HBN.entries[selectedText]
                    else:
                        definition = self.getDefinition(selectedText)
                        if not definition:
                            lemma = config.lemmatizer.lemmatize(selectedText)
                            if lemma == selectedText:
                                lemma = ""
                            else:
                                lemma = f"{lemma} -"
                            definition = self.getDefinition(lemma)
                            if definition:
                                definition = "{0}{1}".format(lemma, definition)
                            elif ("Chineseenglishlookup" in config.enabled):
                                definition = "{0}{1}".format(lemma, config.cedict.lookup(lemma))
                    self.print("Definition:")
                    self.print(definition)
                    self.print(self.divider)
                    self.extract(selectedText)
        except:
            pass

    def getDefinition(self, entry):
        definition = ""
        synsets = config.wordnet.synsets(entry)
        if synsets:
            definition = synsets[0].definition()
        return definition

    def changeDefaultCommand(self):
        try:
            options = (".my", ".menu", ".search", ".quicksearch", ".quicksearchcopiedtext", "[CUSTOMISE]")
            default = config.terminalDefaultCommand if config.terminalDefaultCommand in options else ""
            userInput = self.dialogs.getValidOptions(options=options, default=default, title="Change default command", text="UBA runs default command when users enter an emptry string.")
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if not userInput == "[CUSTOMISE]":
                return self.getContent(f"_setconfig:::terminalDefaultCommand:::'{userInput}'")
            self.print(self.divider)
            self.print("Enter an UBA command:")
            userInput = self.simplePrompt(default=config.terminalDefaultCommand)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            return self.getContent(f"_setconfig:::terminalDefaultCommand:::'{userInput}'")
        except:
            return self.printInvalidOptionEntered()

    def changemymenu(self):
        self.print("Change My Menu")
        self.print("Enter a terminal command on each line:")
        self.print(self.divider)
        default = "\n".join(config.terminalMyMenu)
        userInput = prompt(self.inputIndicator, key_bindings=self.prompt_multiline_shared_key_bindings, bottom_toolbar=self.getToolBar(True), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle, multiline=True, default=default).strip()
        if userInput.lower() == config.terminal_cancel_action:
            return self.cancelAction()
        config.terminalMyMenu = [i.lower().strip() for i in userInput.split("\n") if i.lower().strip() in self.dotCommands]
        self.print("config.terminalMyMenu is changed to:")
        self.print(config.terminalMyMenu)

    def readHowTo(self, filename):
        filepath = os.path.join("terminal_mode", "how_to", f"{filename}.md")
        return self.readPlainTextFile(filepath)

    def fingerprint(self):
        try:
            output = json.loads(self.getCliOutput("termux-fingerprint"))
            return True if output["auth_result"] == "AUTH_RESULT_SUCCESS" else False
        except:
            return False

    def printTermuxApiDisabled(self):
        self.print("Termux API is not yet enabled!")
        self.print("This feature is available on Android ONLY!")
        self.print("Make sure both Termux:API app and termux-api package are installed first.")
        self.print("Then, run '.config' and set 'terminalEnableTermuxAPI' to True.")

    def sendFile(self, filepath):
        if config.terminalEnableTermuxAPI:
            if not self.fingerprint():
                return self.cancelAction()
            self.getCliOutput(f"termux-share -a send {filepath}")
            self.actionDone()
        else:
            self.printTermuxApiDisabled()
        return ""

    def restoreFile(self, filepath):
        if config.terminalEnableTermuxAPI:
            if not self.fingerprint():
                return self.cancelAction()
            self.getCliOutput(f"mv {filepath} {filepath}.bak")
            self.getCliOutput(f"termux-storage-get {filepath}")
            self.actionDone()
        else:
            self.printTermuxApiDisabled()
        return ""

    def restoreLastFile(self, filepath):
        if config.terminalEnableTermuxAPI:
            if os.path.isfile(f"{filepath}.bak"):
                if not self.fingerprint():
                    return self.cancelAction()
                self.getCliOutput(f"cp {filepath}.bak {filepath}")
                self.actionDone()
            else:
                self.print(f"Backup file '{filepath}.bak' does not exist!")
                return self.cancelAction()
        else:
            self.printTermuxApiDisabled()
        return ""

    def togglecolorbrightness(self):
        ConfigUtil.swapTerminalColors()
        return "[MESSAGE]Changed!"

    def changeconfig(self, terminalCommandOnly=False):
        if config.terminalEnableTermuxAPI:
            if not self.fingerprint():
                return self.cancelAction()
        try:
            self.print(self.divider)
            self.print("Configurable Settings:")
            self.print("(Caution! UBA may stop from working if you make invalid changes.)\n")
            # display configurable settings
            configurablesettings = [i for i in config.help.keys() if i.startswith("terminal")] if terminalCommandOnly else list(config.help.keys())
            displayContent = pprint.pformat(configurablesettings)
            self.print(displayContent)
            self.print(self.divider)
            self.print("Enter the item to be change:")
            userInput = self.searchablePrompt(self.inputIndicator, options=configurablesettings, promptSession=self.terminal_config_selection_session)
            if not userInput or userInput.lower() == config.terminal_cancel_action:
                return self.cancelAction()
            # define key
            if userInput in configurablesettings:
                value = userInput
                self.print(self.divider)
                self.print(self.getContent(f"_setconfig:::{value}"))
                self.print(self.divider)
                self.print("Enter a value:")
                userInput = prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle).strip()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                self.print(self.getContent(f"_setconfig:::{value}:::{userInput}"))
                return ".restart"
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def editConfig(self, editor):
        configFile = os.path.join(config.packageDir, "config.py")
        if not os.path.isfile(configFile):
            return ""
        self.print(self.divider)
        self.print("Caution! Editing 'config.py' incorrectly may stop UBA from working.")
        if not editor:
            changesMade = self.multilineEditor(filepath=configFile)
            if changesMade:
                config.saveConfigOnExit = False
                self.print(self.divider)
                self.print("Restarting ...")
                return ".restart"
        else:
            self.print("Do you want to proceed? [y]es / [N]o")
            userInput = prompt(self.inputIndicator, key_bindings=self.prompt_shared_key_bindings, bottom_toolbar=self.getToolBar(), enable_system_prompt=True, swap_light_and_dark_colors=Condition(lambda: not config.terminalResourceLinkColor.startswith("ansibright")), style=self.promptStyle, default="N").strip()
            userInput = userInput.lower()
            if userInput in ("y", "yes"):
                self.print("reading config content ...")
                if os.path.isfile(configFile):
                    with open(configFile, "r", encoding="utf-8") as input_file:
                        content = input_file.read()
                    self.print("config is ready for editing ...")
                    self.print("To apply changes, save as 'config.py' and replace the existing 'config.py' when you finish editing.")
                self.cliTool(editor, content)
                config.saveConfigOnExit = False
                self.print(self.divider)
                self.print("Restarting ...")
                return ".restart"
            #if userInput in ("n", "no"):
            else:
                return self.cancelAction()

    def confirmSaveTextFile(self, text):
        answer = confirm("Save changes?")
        if answer:
            promptFilenameEntry = True
            while promptFilenameEntry:
                self.print("Enter a file name:")
                filepath = self.simplePrompt().strip()
                if filepath.lower() == config.terminal_cancel_action:
                    promptFilenameEntry = False
                elif filepath:
                    try:
                        with open(filepath, "w", encoding="utf-8") as fileObj:
                            fileObj.write(text)
                        promptFilenameEntry = False
                    except:
                        self.print(f"Failed to save text in '{filepath}'!")

    # pipe text content into a cli tool
    def cliTool(self, tool="", content=""):
        command = re.sub(" .*?$", "", tool.strip())
        if not command:
            self.multilineEditor(content)
        elif command and WebtopUtil.isPackageInstalled(command):
            pydoc.pipepager(content, cmd=tool)
            if WebtopUtil.isPackageInstalled("pkill"):
                os.system(f"pkill {command}")
        return ""

    def openNoteEditor(self, noteType, b=None, c=None, v=None, year=None, month=None, day=None, editor=""):
        if not editor:
            editor = config.terminalNoteEditor
        if not editor or not WebtopUtil.isPackageInstalled(editor.split(" ")[0]):
            editor = ""
        noteDB = JournalSqlite() if noteType == "journal" else NoteSqlite()
        if noteType == "journal":
            note = noteDB.getJournalNote(year, month, day)
        elif noteType == "book":
            note = noteDB.getBookNote(b)[0]
        elif noteType == "chapter":
            note = noteDB.getChapterNote(b, c)[0]
        elif noteType == "verse":
            note = noteDB.getVerseNote(b, c, v)[0]
        if ("Markdownify" in config.enabled):
            # convert html into markdown
            from markdownify import markdownify
            note = markdownify(note, heading_style=config.markdownifyHeadingStyle)
            note = note.replace("\n\np, li { white-space: pre-wrap; }\n", "")
            note = note.replace("hr { height: 1px; border-width: 0; }\n", "")
        else:
            note = self.getPlainText(note)
        # display in editor
        self.print("Opening text editor ...")
        self.print("When you finish editing, save content in a file and enter 'note' as its filename.")

        if editor:
            self.cliTool(editor, note)
            # check if file is saved
            notePath = "note"
            if os.path.isfile(notePath):
                with open(notePath, "r", encoding="utf-8") as input_file:
                    text = input_file.read()
                # convert markdown into html
                text = markdown.markdown(text)
                text = TextUtil.fixNoteFontDisplay(text)
                #text = TextUtil.htmlWrapper(text, True, "study", False)
                # save into note databse
                self.saveNote(noteDB, noteType, b, c, v, year, month, day, text)
                # remove file after saving
                os.remove(notePath)
        else:
            placeholder = ""
            if note == "[empty]":
                note = ""
                placeholder = "[empty]"
            custom_save_file_method = partial(self.custom_save_note, noteDB, noteType, b, c, v, year, month, day)
            self.multilineEditor(note, placeholder, custom_save_file_method=custom_save_file_method)
        return ""

    def custom_save_note(self, noteDB, noteType, b=None, c=None, v=None, year=None, month=None, day=None, text=""):
        text = markdown.markdown(text)
        text = TextUtil.fixNoteFontDisplay(text)
        self.saveNote(noteDB, noteType, b, c, v, year, month, day, text)

    def saveNote(self, noteDB, noteType, b=None, c=None, v=None, year=None, month=None, day=None, note=""):
        note = TextUtil.fixNoteFont(note)
        if noteType == "book":
            noteDB.saveBookNote(b, note, DateUtil.epoch())
        elif noteType == "chapter":
            noteDB.saveChapterNote(b, c, note, DateUtil.epoch())
        elif noteType == "verse":
            noteDB.saveVerseNote(b, c, v, note, DateUtil.epoch())
        elif noteType == "journal":
            noteDB.saveJournalNote(year, month, day, note)
        self.print("Note saved!")

    # Toggle bible display

    def toggleBibleChapterFormat(self):
        config.readFormattedBibles = not config.readFormattedBibles
        self.print("Reloading bible chapter ...")
        return self.getContent(".l")

    def togglebiblecomparison(self):
        config.terminalBibleComparison = not config.terminalBibleComparison
        self.print("Reloading bible chapter ...")
        return self.getContent(".l")

    def togglebibleparallels(self):
        if not WebtopUtil.isPackageInstalled("w3m"):
            config.terminalBibleParallels = False
            self.printToolNotFound("w3m")
            return ""
        config.terminalBibleParallels = not config.terminalBibleParallels
        self.print("Reloading bible chapter ...")
        return self.getContent(".l")
        #reference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        #return self.getContent(f"SIDEBYSIDE:::{reference}") if config.terminalBibleParallels else self.getContent(reference)

    def toggleaddTitleToPlainChapter(self):
        config.addTitleToPlainChapter = not config.addTitleToPlainChapter
        self.print("Reloading bible chapter ...")
        return self.getContent(".l")

    def toggleaddFavouriteToMultiRef(self):
        config.addFavouriteToMultiRef = not config.addFavouriteToMultiRef
        self.print("Reloading bible chapter ...")
        return self.getContent(".l")

    def toggleshowVerseReference(self):
        config.showVerseReference = not config.showVerseReference
        self.print("Reloading bible chapter ...")
        return self.getContent(".l")

    def toggleshowUserNoteIndicator(self):
        config.showUserNoteIndicator = not config.showUserNoteIndicator
        self.print("Reloading bible chapter ...")
        return self.getContent(".l")

    def toggleshowBibleNoteIndicator(self):
        config.showBibleNoteIndicator = not config.showBibleNoteIndicator
        self.print("Reloading bible chapter ...")
        return self.getContent(".l")

    def togglehideLexicalEntryInBible(self):
        config.hideLexicalEntryInBible = not config.hideLexicalEntryInBible
        self.print("Reloading bible chapter ...")
        return self.getContent(".l")

    # organise user interactive menu
    def menu(self):
        heading = "Master Menu"
        features = [".open", ".search", ".note", ".edit", ".speak", ".translate", ".clipboard", ".quick", ".control", ".tools", ".plugins", ".change", ".download", ".maintain", ".help", ".restart", ".quit"]
        if config.terminalMyMenu:
            features.insert(0, ".my")
        return self.displayFeatureMenu(heading, features)

    def my(self):
        if config.terminalMyMenu:
            heading = "My Menu"
            return self.displayFeatureMenu(heading, config.terminalMyMenu)
        else:
            return "Configure config.terminalMyMenu first!"

    def open(self):
        heading = "Open"
        features = (".bible", ".biblenote", ".original", ".365", ".bookfeatures", ".chapterfeatures", ".versefeatures", ".wordfeatures", ".commentary", ".referencebook", ".audio", ".data", ".topics", ".promises", ".parallels", ".characters", ".locations", ".timelines", ".dictionaries", ".encyclopedia", ".thirdpartydictionaries", ".wordnet", ".textfile")
        return self.displayFeatureMenu(heading, features)

    def characters(self):
        heading = "Bible Characters"
        features = (".names", ".exlbp")
        return self.displayFeatureMenu(heading, features)

    def locations(self):
        heading = "Bible Locations"
        features = (".exlbl", ".maps", ".customisemaps", ".distance")
        return self.displayFeatureMenu(heading, features)

    def all(self):
        heading = "All"
        features = (".allmp3", ".allmp4",)
        return self.displayFeatureMenu(heading, features)

    def apply(self):
        heading = "Apply"
        features = (".applyfilters",)
        return self.displayFeatureMenu(heading, features)

    def google(self):
        heading = "Google"
        features = (".googletranslate", ".googletranslatecopiedtext")
        return self.displayFeatureMenu(heading, features)

    def watson(self):
        heading = "Watson"
        features = (".watsontranslate", ".watsontranslatecopiedtext")
        return self.displayFeatureMenu(heading, features)

    def customise(self):
        heading = "Customise"
        features = (".customisemaps", ".customisefilters")
        return self.displayFeatureMenu(heading, features)

    def quick(self):
        heading = "Quick"
        features = (".quickopen", ".quickopencopiedtext", ".quickedit", ".quickeditcopiedtext", ".quicksearch", ".quicksearchcopiedtext")
        return self.displayFeatureMenu(heading, features)

    def original(self):
        heading = "Hebrew & Greek Bibles"
        features = (".ohgb", ".ohgbi", ".mob", ".mib", ".mtb", ".mpb", ".mab", ".lxx1i", ".lxx2i")
        return self.displayFeatureMenu(heading, features)

    def tools(self):
        heading = "Tools"
        features = (".web", ".share", ".extract", ".filters", ".chat", ".image", ".read", ".readsync", ".system", ".python")
        return self.displayFeatureMenu(heading, features)

    def speak(self):
        heading = "Speak"
        features = (".tts", ".tts1", ".tts2", ".tts3", ".tts4", ".ttscopiedtext", ".ttscopiedtext1", ".ttscopiedtext2", ".ttscopiedtext3", ".ttscopiedtext4")
        return self.displayFeatureMenu(heading, features)

    def translate(self):
        heading = "Translate"
        features = (".googletranslate", ".googletranslatecopiedtext", ".watsontranslate", ".watsontranslatecopiedtext")
        return self.displayFeatureMenu(heading, features)

    def control(self):
        heading = "Control"
        features = (".clear", ".reload", ".latestbible", ".forward", ".backward", ".swap", ".starthttpserver", ".stophttpserver", ".stopaudio", ".stopaudiosync", ".toggle")
        return self.displayFeatureMenu(heading, features)

    def toggle(self):
        heading = "Toggle"
        features = (".togglepager", ".toggleclipboardmonitor", ".togglecomparison", ".togglechapterlayout", ".toggleplainbiblechaptersubheadings", ".togglefavouriteverses", ".toggleversenumber", ".toggleusernoteindicator", ".togglenoteindicator", ".togglelexicalentries")
        return self.displayFeatureMenu(heading, features)

    def clipboard(self):
        heading = "Copy & Copied Text"
        features = (".copy", ".copyhtml", ".paste", ".run", ".findcopiedtext", ".extractcopiedtext")
        return self.displayFeatureMenu(heading, features)

    def search(self):
        heading = "Search"
        features = (".find", ".searchbible", ".searchreferencebooks", ".searchlexiconcontent", ".searchconcordance")
        return self.displayFeatureMenu(heading, features)

    def info(self):
        heading = "Information"
        features = (".latest", ".history", ".showbibles", ".showstrongbibles", ".showbiblebooks", ".showbibleabbreviations", ".showbiblechapters", ".showbibleverses", ".showcommentaries", ".showtopics", ".showlexicons", ".showencyclopedia", ".showdictionaries", ".showthirdpartydictionary", ".showreferencebooks", ".showdata", ".showttslanguages", ".gitstatus", ".commands", ".config")
        return self.displayFeatureMenu(heading, features)

    def filters(self):
        heading = "Filters"
        features = (".customisefilters", ".applyfilters", ".editfilters")
        return self.displayFeatureMenu(heading, features)

    def edit(self):
        heading = "Edit"
        features = (".editor", ".editnewfile", ".edittextfile", ".editcontent", ".editconfig", ".editfilters", ".changenoteeditor", ".helpinstallmicro")
        return self.displayFeatureMenu(heading, features)

    def change(self):
        heading = "Change"
        features = (".changebible", ".changebibles", ".changefavouritebible1", ".changefavouritebible2", ".changefavouritebible3", ".changefavouriteoriginalbible", ".changecommentary", ".changelexicon", ".changedictionary", ".changethirdpartydictionary", ".changeencyclopedia", ".changeconcordance", ".changereferencebook", ".changereferencebookchapter", ".changettslanguage1", ".changettslanguage2", ".changettslanguage3", ".changedefaultcommand", ".changebiblesearchmode", ".changenoteeditor", ".changecolors", ".changeterminalmodeconfig", ".changeconfig")
        return self.displayFeatureMenu(heading, features)

    def help(self):
        heading = "Help"
        features = (".wiki", ".quickstart", ".howto", ".info", ".terminalcommands", ".standardcommands", ".aliases", ".keys", ".whatis")
        return self.displayFeatureMenu(heading, features)

    def maintain(self):
        heading = "Maintenance"
        features = [".latestchanges", ".update"]
        if config.terminalEnableTermuxAPI:
            features += [".backup", ".restore"]
        return self.displayFeatureMenu(heading, features)

    def backup(self):
        heading = "Backup"
        features = (".backupnotes", ".backupjournals")
        return self.displayFeatureMenu(heading, features)

    def restore(self):
        heading = "Restore"
        features = (".restorenotes", ".restorelastnotes", ".restorejournals", ".restorelastjournals")
        return self.displayFeatureMenu(heading, features)

    def download(self):
        heading = "Download"
        features = (".showdownloads", ".downloadbibleaudio", ".downloadyoutube")
        return self.displayFeatureMenu(heading, features)

    def python(self):
        heading = "Python Tools"
        features = (".exec", ".execfile", ".portablepython",)
        return self.displayFeatureMenu(heading, features)

    def openbookfeatures(self):
        heading = "Bible Book Featues"
        features = (".introduction", ".dictionarybookentry", ".encyclopediabookentry")
        return self.displayFeatureMenu(heading, features)

    def openchapterfeatures(self):
        heading = "Bible Chapter Featues"
        features = (".overview", ".summary", ".chapterindex")
        return self.displayFeatureMenu(heading, features)

    def openversefeatures(self):
        heading = "Bible Verse Featues"
        features = (".crossreference", ".tske", ".comparison", ".difference", ".verseindex", ".words", ".discourse", ".translation", ".combo")
        return self.displayFeatureMenu(heading, features)

    def openwordfeatures(self):
        heading = "Original Word Featues"
        features = (".word", ".concordancebybook", ".concordancebymorphology", ".lexicons", ".readword", ".readlexeme")
        return self.displayFeatureMenu(heading, features)

    def accessNoteFeatures(self):
        heading = "Note / Journal Features"
        features = (".booknote", ".chapternote", ".versenote", ".journal", ".searchbooknote", ".searchchapternote", ".searchversenote", ".searchjournal", ".editbooknote", ".editchapternote", ".editversenote", ".editjournal", ".changenoteeditor")
        return self.displayFeatureMenu(heading, features)

    # Download Helper
    def downloadHelper(self, databaseInfo):
        if config.runMode == "terminal":
            if config.isDownloading:
                self.displayMessage(config.thisTranslation["previousDownloadIncomplete"])
            else:
                self.print(self.divider)
                self.print(f"Essential data '{databaseInfo[0][-1]}' is missing!")
                self.print("Do you want to download it now? [y]es / [N]o")
                userInput = self.simplePrompt()
                if not userInput or userInput.lower() == config.terminal_cancel_action:
                    return self.cancelAction()
                if userInput.lower() in ("y", "yes"):
                    self.textCommandParser.parent.downloadFile(databaseInfo)
                    return ""
                elif userInput.lower() in ("n", "no"):
                    return self.cancelAction()
                else:
                    self.printInvalidOptionEntered()

    def resizeHtmlImage(self, imageTag):
        return re.sub("^<img ", """<img style="max-width: 100%; height: auto;" """, imageTag)

    def saveAndOpenHtmlFile(self, html, filepath=""):
        if not filepath:
            filepath = os.path.join(os.getcwd(), "terminal_mode", "Unique_Bible_App.html")
        # write an html file
        with open(filepath, "w", encoding="utf-8") as fileObj:
            fileObj.write(html)
        # open the html file
        if config.terminalEnableTermuxAPI:
            self.print(f"Opening {filepath} ...")
            self.openLocalHtmlWithAndroidApps(filepath)
        else:
            command = f"cmd:::{config.open} {filepath}"
            self.printRunningCommand(command)
            self.getContent(command)

    def openLocalHtmlWithAndroidApps(self, filepath):
        if config.terminalEnableTermuxAPI:
            filepath = re.sub("/", r"%2F", filepath)
            filepath = re.sub(r"%2Fdata%2Fdata%2Fcom.termux%2Ffiles%2Fhome%2F", r"content://com.termux.documents/document/%2Fdata%2Fdata%2Fcom.termux%2Ffiles%2Fhome%2F", filepath)
            cmd = f"termux-open {filepath}"
            self.cliTool(cmd)

    def wrapHtml(self, content):
        return """
                <!DOCTYPE html><html><head><link rel="icon" href="icons/{2}"><title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />
                <style>
                table, th, td {0}
                border: 1px solid black;
                {1}
                </style>
                </head><body>
                {3}
                </body></html>
                """.format("{", "}", config.webUBAIcon, content)

    def wrapHtmlFull(self, content, view="", book=False):
        fontFamily = config.font
        fontSize = "{0}px".format(config.fontSize)
        if book:
            if config.overwriteBookFontFamily:
                fontFamily = config.overwriteBookFontFamily
            if config.overwriteBookFontSize:
                if type(config.overwriteBookFontSize) == str:
                    fontSize = config.overwriteBookFontSize
                elif type(config.overwriteBookFontSize) == int:
                    fontSize = "{0}px".format(config.overwriteBookFontSize)
        bcv = (config.studyText, config.studyB, config.studyC, config.studyV) if view == "study" else (config.mainText, config.mainB, config.mainC, config.mainV)
        activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(*bcv)
        html = ("""<!DOCTYPE html><html><head><link rel="icon" href="icons/{9}"><title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />"""
                "<style>body {2} font-size: {4}; font-family:'{5}';{3} "
                "zh {2} font-family:'{6}'; {3} "
                ".ubaButton {2} background-color: {10}; color: {11}; border: none; padding: 2px 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 17px; margin: 2px 2px; cursor: pointer; {3}"
                "{8}</style>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{7}.css?v=1.065'>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.065'>"
                "<script src='js/common.js?v=1.065'></script>"
                "<script src='js/{7}.js?v=1.065'></script>"
                "<script src='w3.js?v=1.065'></script>"
                "<script src='js/http_server.js?v=1.065'></script>"
                """<script>
                var target = document.querySelector('title');
                var observer = new MutationObserver(function(mutations) {2}
                    mutations.forEach(function(mutation) {2}
                        ubaCommandChanged(document.title);
                    {3});
                {3});
                var config = {2}
                    childList: true,
                {3};
                observer.observe(target, config);
                </script>"""
                "{0}"
                """<script>var versionList = []; var compareList = []; var parallelList = [];
                var diffList = []; var searchList = [];</script>"""
                "<script src='js/custom.js?v=1.065'></script>"
                "</head><body><span id='v0.0.0'></span>{1}"
                "<p>&nbsp;</p><div id='footer'><span id='lastElement'></span></div><script>loadBible();document.querySelector('body').addEventListener('click', window.parent.closeSideNav);</script></body></html>"
                ).format(activeBCVsettings,
                         content,
                         "{",
                         "}",
                         fontSize,
                         fontFamily,
                         config.fontChinese,
                         config.theme,
                         self.getHighlightCss(),
                         config.webUBAIcon,
                         config.widgetBackgroundColor,
                         config.widgetForegroundColor,
                         )
        return html

    def getHighlightCss(self):
        css = ""
        for i in range(len(config.highlightCollections)):
            code = "hl{0}".format(i + 1)
            css += ".{2} {0} background: {3}; {1} ".format("{", "}", code, config.highlightDarkThemeColours[i] if config.theme == "dark" else config.highlightLightThemeColours[i])
        return css

    # Workaround stoping audio playing in some cases
    def createAudioPlayingFile(self):
        # To break the audio playing loop running with readsync or Android tts, manually delete the file "temp/000_audio_playing.txt"
        if not os.path.isfile(config.audio_playing_file):
            open(config.audio_playing_file, "a", encoding="utf-8").close()

    def removeAudioPlayingFile(self):
        if os.path.isfile(config.audio_playing_file):
            os.remove(config.audio_playing_file)

    # Missing package
    def printMissingPackage(self, package):
        self.print(f"Essentail package '{package}' is not found!")
