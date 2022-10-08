import re, config, pprint, os, requests, platform, pydoc, markdown, sys, subprocess, json
from datetime import date
#import urllib.request
from ast import literal_eval
from db.BiblesSqlite import Bible
from db.JournalSqlite import JournalSqlite
from db.ToolsSqlite import Book
from db.NoteSqlite import NoteSqlite
from util.DateUtil import DateUtil
from util.TextUtil import TextUtil
from util.NetworkUtil import NetworkUtil
from util.RemoteCliMainWindow import RemoteCliMainWindow
from util.TextCommandParser import TextCommandParser
from util.BibleVerseParser import BibleVerseParser
from util.CrossPlatform import CrossPlatform
from util.BibleBooks import BibleBooks
from util.GitHubRepoInfo import GitHubRepoInfo
from util.FileUtil import FileUtil
from util.UpdateUtil import UpdateUtil
from util.DateUtil import DateUtil
from util.WebtopUtil import WebtopUtil
#from util.NoteService import NoteService


class LocalCliHandler:

    def __init__(self, command="John 3:16"):
        self.textCommandParser = TextCommandParser(RemoteCliMainWindow())
        self.crossPlatform = CrossPlatform()
        self.crossPlatform.setupResourceLists()
        self.html = "<ref >Unique Bible App</ref>"
        self.plainText = "Unique Bible App"
        self.command = command
        self.dotCommands = self.getDotCommands()
        self.cancelCommand = ".cancel"
        self.initPromptElements()
        self.setOsOpenCmd()
        self.ttsLanguages = self.getTtsLanguages()
        #config.cliTtsProcess = None

    # Set text-to-speech default language
    def getTtsLanguages(self):
        return self.crossPlatform.getTtsLanguages()

    def setOsOpenCmd(self):
        if config.terminalEnableTermuxAPI:
            config.open = "termux-open"
        elif platform.system() == "Linux":
            config.open = config.openLinux
        elif platform.system() == "Darwin":
            config.open = config.openMacos
        elif platform.system() == "Windows":
            config.open = config.openWindows

    def initPromptElements(self):
        self.divider = "--------------------"
        self.inputIndicator = ">>> "
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import FileHistory

            find_history = os.path.join("terminal_history", "find")
            module_history_books = os.path.join("terminal_history", "books")
            module_history_bibles = os.path.join("terminal_history", "bibles")
            module_history_topics = os.path.join("terminal_history", "topics")
            module_history_dictionaries = os.path.join("terminal_history", "dictionaries")
            module_history_encyclopedia = os.path.join("terminal_history", "encyclopedia")
            module_history_lexicons = os.path.join("terminal_history", "lexicons")
            module_history_thirdDict = os.path.join("terminal_history", "thirdPartyDictionaries")
            module_history_commentaries = os.path.join("terminal_history", "commentaries")
            search_bible_history = os.path.join("terminal_history", "search_bible")
            search_strong_bible_history = os.path.join("terminal_history", "search_strong_bible")
            search_bible_book_range_history = os.path.join("terminal_history", "search_bible_book_range")
            config_history = os.path.join("terminal_history", "config")
            tts_language_history = os.path.join("terminal_history", "tts_language")

            self.terminal_books_selection_session = PromptSession(history=FileHistory(module_history_books))
            self.terminal_find_session = PromptSession(history=FileHistory(find_history))
            self.terminal_search_strong_bible_session = PromptSession(history=FileHistory(search_strong_bible_history))
            self.terminal_search_bible_session = PromptSession(history=FileHistory(search_bible_history))
            self.terminal_search_bible_book_range_session = PromptSession(history=FileHistory(search_bible_book_range_history))
            self.terminal_bible_selection_session = PromptSession(history=FileHistory(module_history_bibles))
            self.terminal_topics_selection_session = PromptSession(history=FileHistory(module_history_topics))
            self.terminal_dictionary_selection_session = PromptSession(history=FileHistory(module_history_dictionaries))
            self.terminal_encyclopedia_selection_session = PromptSession(history=FileHistory(module_history_encyclopedia))
            self.terminal_lexicons_selection_session = PromptSession(history=FileHistory(module_history_lexicons))
            self.terminal_thridPartyDictionaries_selection_session = PromptSession(history=FileHistory(module_history_thirdDict))
            self.terminal_commentary_selection_session = PromptSession(history=FileHistory(module_history_commentaries))
            self.terminal_config_selection_session = PromptSession(history=FileHistory(config_history))
            self.terminal_tts_language_session = PromptSession(history=FileHistory(tts_language_history))

        else:

            self.terminal_tts_language_session = None
            self.terminal_search_strong_bible_session = None
            self.terminal_books_selection_session = None
            self.terminal_find_session = None
            self.terminal_search_bible_session = None
            self.terminal_search_bible_book_range_session = None
            self.terminal_bible_selection_session = None
            self.terminal_topics_selection_session = None
            self.terminal_dictionary_selection_session = None
            self.terminal_encyclopedia_selection_session = None
            self.terminal_lexicons_selection_session = None
            self.terminal_thridPartyDictionaries_selection_session = None
            self.terminal_commentary_selection_session = None
            self.terminal_config_selection_session = None

    def getDotCommands(self):
        return {
            ".togglepager": ("toggle paging for text output", self.togglePager),
            ".togglebiblechapterformat": ("toggle between plain and formatted bible chapter", self.toggleBibleChapterFormat),
            ".togglebiblecomparison": ("toggle bible comparison view", self.togglebiblecomparison),
            ".stopaudio": ("stop audio playback", self.stopAudio),
            ".sa": ("an alias to the '.stopaudio' command", self.stopAudio),
            ".read": ("read available audio files", self.read),
            ".readsync": ("read available audio files with synchronised text display", self.readsync),
            ".run": ("run copied text as command", self.runclipboardtext),
            ".r": ("an alias to the '.paste' command", self.runclipboardtext),
            ".forward": ("open one bible chapter forward", self.forward),
            ".backward": ("open one bible chapter backward", self.backward),
            ".f": ("an alias to the '.forward' command", self.forward),
            ".b": ("an alias to the '.backward' command", self.backward),
            ".swap": ("swap to a favourite bible", self.swap),
            ".s": ("an alias to the '.swap' command", self.swap),
            ".web": ("open web version", self.web),
            ".share": ("copy a web link for sharing", self.share),
            ".tts": ("open text-to-speech feature", lambda: self.tts(False)),
            ".ttscopiedtext": ("run text-to-speech on copied text", self.tts),
            ".copy": ("copy the last opened content", self.copy),
            ".copyhtml": ("copy the last opened content in html format", self.copyHtml),
            ".quicksearchcopiedtext": ("run quick search of copied text", self.quickSearch),
            ".qc": ("an alias to the '.quicksearchcopiedtext' command", self.quickSearch),
            ".find": ("find a string in the last opened content", self.find),
            ".history": ("display history records", self.history),
            ".latest": ("display the lastest module selection", self.latest),
            ".latestbible": ("display the lastest bible chapter", self.latestBible),
            ".l": ("an alias to the '.lastestbible' command", self.latestBible),
            ".update": ("update Unique Bible App to the latest version", self.update),
            ".commands": ("display available commands", self.commands),
            ".config": ("display UBA configurations", self.config),
            ".showbibles": ("display installed bibles", self.showbibles),
            ".showstrongbibles": ("display installed bibles with Strong's numbers", self.showstrongbibles),
            ".showbiblebooks": ("display bible book list", self.showbiblebooks),
            ".showbibleabbreviations": ("display bible book name list", self.showbibleabbreviations),
            ".showbiblechapters": ("display bible chapter list", self.showbiblechapters),
            ".showbibleverses": ("display bible verse list", self.showbibleverses),
            ".showcommentaries": ("display installed commentaries", self.showcommentaries),
            ".showtopics": ("display installed bible topic modules", self.showtopics),
            ".showlexicons": ("display installed lexicons", self.showlexicons),
            ".showencyclopedia": ("display installed encyclopedia", self.showencyclopedia),
            ".showdictionaries": ("display installed dictionaries", self.showdictionaries),
            ".showthirdpartydictionary": ("display installed third-party dictionaries", self.showthirdpartydictionary),
            ".showreferencebooks": ("display installed reference books", self.showreferencebooks),
            ".showdata": ("display installed data", self.showdata),
            ".showttslanguages": ("display text-to-speech languages", self.showttslanguages),
            ".showdownloads": ("display available downloads", self.showdownloads),
            ".openbible": ("open bible", self.openbible),
            ".opencommentary": ("open commentary", self.opencommentary),
            ".openreferencebook": ("open reference book", self.openreferencebook),
            ".openbooknote": ("open bible book note", lambda: self.openbookfeature("OPENBOOKNOTE")),
            ".openchapternote": ("open bible chapter note", lambda: self.openchapterfeature("OPENCHAPTERNOTE")),
            ".openversenote": ("open bible verse note", lambda: self.openversefeature("OPENVERSENOTE")),
            ".openjournal": ("open journal", lambda: self.journalFeature("OPENJOURNAL")),
            ".editbooknote": ("edit bible book note", lambda: self.openbookfeature("EDITBOOKNOTE")),
            ".editchapternote": ("edit bible chapter note", lambda: self.openchapterfeature("EDITCHAPTERNOTE")),
            ".editversenote": ("edit bible verse note", lambda: self.openversefeature("EDITVERSENOTE")),
            ".editjournal": ("edit journal", lambda: self.journalFeature("EDITJOURNAL")),
            ".searchbooknote": ("search bible book note", lambda: self.searchNote("SEARCHBOOKNOTE")),
            ".searchchapternote": ("search bible chapter note", lambda: self.searchNote("SEARCHCHAPTERNOTE")),
            ".searchversenote": ("search bible verse note", lambda: self.searchNote("SEARCHVERSENOTE")),
            ".searchjournal": ("search journal", lambda: self.searchNote("SEARCHJOURNAL")),
            ".searchpromises": ("search bible promises", lambda: self.searchTools2("promises")),
            ".searchparallels": ("search bible parallels", lambda: self.searchTools2("parallels")),
            ".searchnames": ("search bible names", lambda: self.searchTools2("names")),
            ".searchcharacters": ("search bible characters", lambda: self.searchTools2("characters")),
            ".searchlocations": ("search bible locations", lambda: self.searchTools2("locations")),
            ".searchdictionaries": ("search dictionaries", lambda: self.searchTools("DICTIONARY", self.showdictionaries)),
            ".searchencyclopedia": ("search encyclopedia", lambda: self.searchTools("ENCYCLOPEDIA", self.showencyclopedia)),
            ".searchlexicons": ("search lexicons", lambda: self.searchTools("LEXICON", self.showlexicons)),
            ".searchlexiconsreversely": ("search lexicons reversely", lambda: self.searchTools("REVERSELEXICON", self.showlexicons)),
            ".searchreferencebooks": ("search reference books", lambda: self.searchTools("BOOK", self.showreferencebooks)),
            ".searchtopics": ("search topics", lambda: self.searchTools("TOPICS", self.showtopics)),
            ".searchthirdpartydictionaries": ("search third-party dictionaries", lambda: self.searchTools("THIRDDICTIONARY", self.showthirdpartydictionary)),
            ".search3dict": ("an alias to the '.searchthirdpartydictionaries' command", lambda: self.searchTools("THIRDDICTIONARY", self.showthirdpartydictionary)),
            ".searchconcordance": ("search for concordance", self.searchconcordance),
            ".quicksearch": ("quick search in default modules", lambda: self.quickSearch(False)),
            ".q": ("an alias to the '.quicksearch' command", lambda: self.quickSearch(False)),
            ".opencrossreference": ("open cross reference", self.openversefeature),
            ".opencomparison": ("open verse comparison", lambda: self.openversefeature("COMPARE")),
            ".opendifference": ("open verse comparison with differences", lambda: self.openversefeature("DIFFERENCE")),
            ".opentske": ("open Treasury of Scripture Knowledge (Enhanced)", lambda: self.openversefeature("TSKE")),
            ".opensmartindex": ("open smart index", lambda: self.openversefeature("INDEX")),
            ".opencombo": ("open combination of translation, discourse and words features", lambda: self.openversefeature("COMBO")),
            ".openwords": ("open original words", lambda: self.openversefeature("WORDS")),
            ".opendiscourse": ("open discourse feature", lambda: self.openversefeature("DISCOURSE")),
            ".opentranslation": ("open original word translation", lambda: self.openversefeature("TRANSLATION")),
            ".openoverview": ("open chapter overview", self.openchapterfeature),
            ".opensummary": ("open chapter summary", lambda: self.openchapterfeature("SUMMARY")),
            ".openchapterindex": ("open chapter index", lambda: self.openchapterfeature("CHAPTERINDEX")),
            ".openintroduction": ("open book introduction", self.openbookfeature),
            ".opendictionarybookentry": ("open bible book entry in dictionary", lambda: self.openbookfeature("dictionary")),
            ".openencyclopediabookentry": ("open bible book entry in encyclopedia", lambda: self.openbookfeature("encyclopedia")),
            #".opentimelines": ("open book timelines", lambda: self.openBookFeature("timelines")),
            ".openbookfeatures": ("open bible book features", self.openbookfeatures),
            ".openchapterfeatures": ("open bible chapter features", self.openchapterfeatures),
            ".openversefeatures": ("open bible verse features", self.openversefeatures),
            ".standardcommands": ("display standard UBA command help menu", self.standardcommands),
            ".terminalcommands": ("display terminal mode commands", self.terminalcommands),
            ".menu": ("display main menu", self.menu),
            ".open": ("display open menu", self.open),
            ".change": ("display change menu", self.change),
            ".search": ("display search menu", self.search),
            ".show": ("display show menu", self.show),
            ".note": ("display note / journal menu", self.accessNoteFeatures),
            ".edit": ("display edit menu", self.edit),
            ".maintain": ("display maintain menu", self.maintain),
            ".control": ("display control menu", self.control),
            ".clipboard": ("display clipboard menu", self.clipboard),
            ".help": ("display help menu", self.help),
            ".w3m": ("open html content in w3m", lambda: self.cliTool("w3m -T text/html", self.html)),
            ".lynx": ("open html content in lynx", lambda: self.cliTool("lynx -stdin", self.html)),
            ".textract": ("open text from document.", self.textract),
            ".nano": ("edit content with text editor 'nano'", lambda: self.texteditor("nano --softwrap --atblanks", self.getPlainText())),
            ".nanonew": ("open new file in text editor 'nano'", lambda: self.texteditor("nano --softwrap --atblanks")),
            ".vi": ("edit content with text editor 'vi'", lambda: self.texteditor("vi", self.getPlainText())),
            ".vinew": ("open new file in text editor 'vi'", lambda: self.texteditor("vi")),
            ".vim": ("edit content with text editor 'vim'", lambda: self.texteditor("vim", self.getPlainText())),
            ".vimnew": ("open new file in text editor 'vim'", lambda: self.texteditor("vim")),
            ".searchbible": ("search bible", self.searchbible),
            ".whatis": ("read description about a command", self.whatis),
            ".nanoconfig": ("edit 'config.py' with nano", lambda: self.editConfig("nano --softwrap --atblanks")),
            ".viconfig": ("edit 'config.py' with vi", lambda: self.editConfig("vi")),
            ".vimconfig": ("edit 'config.py' with vim", lambda: self.editConfig("vim")),
            ".starthttpserver": ("start UBA http-server", self.starthttpserver),
            ".stophttpserver": ("stop UBA http-server", self.stophttpserver),
            ".downloadyoutube": ("download youtube file", self.downloadyoutube),
            ".backupnotes": ("backup note database file", lambda: self.sendFile("marvelData/note.sqlite")),
            ".backupjournals": ("backup journal database file", lambda: self.sendFile("marvelData/journal.sqlite")),
            ".restorenotes": ("restore note database file", lambda: self.restoreFile("marvelData/note.sqlite")),
            ".restorejournals": ("restore journal database file", lambda: self.restoreFile("marvelData/journal.sqlite")),
            ".restorelastnotes": ("restore note database file", lambda: self.restoreLastFile("marvelData/note.sqlite")),
            ".restorelastjournals": ("restore journal database file", lambda: self.restoreLastFile("marvelData/journal.sqlite")),
            ".changenoteeditor": ("change default note editor", self.changenoteeditor),
            ".changebiblesearchmode": ("change default bible search mode", self.changebiblesearchmode),
            ".changecolors": ("change text highlight colors", self.changecolors),
            ".changeconfig": ("change UBA configurations", self.changeconfig),
        }

    #marvelData/note.sqlite
    #marvelData/journal.sqlite
    #marvelData/highlights.bible

    def execPythonFile(self, script):
        self.crossPlatform.execPythonFile(script)

    def getContent(self, command):
        command = command.strip()
        # study window applies to Qt library users only
        if command.lower().startswith("study:::") or command.lower().startswith("studytext:::"):
            config.studyText, config.studyB, config.studyC, config.studyV = config.mainText, config.mainB, config.mainC, config.mainV
        originalCommand = command
        # Shortcuts to change chapter or verse or both chapter and verse for bible reading.
        if command:
            try:
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
                    prefix = f"COMPARE:::{config.compareParallelList}:::" if config.terminalBibleComparison else "BIBLE:::"
                    command = f"{prefix}{command}"
                    self.printRunningCommand(command)
            except:
                pass
        # Redirect heavy html content to web version.
        if re.search('^(map:::|bible:::mab:::|bible:::mib:::|bible:::mob:::|bible:::mpb:::|bible:::mtb:::|text:::mab|text:::mib|text:::mob|text:::mpb|text:::mtb|study:::mab:::|study:::mib:::|study:::mob:::|study:::mpb:::|study:::mtb:::|studytext:::mab|studytext:::mib|studytext:::mob|studytext:::mpb|studytext:::mtb)', command.lower()):
            return self.web(command)
        # Dot commands
        if command.startswith("."):
            return self.getDotCommandContent(command.lower())
        # Non-dot commands
        view, content, dict = self.textCommandParser.parser(command, "cli")
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
        plainText = TextUtil.htmlToPlainText(content).strip()
        self.plainText = "" if content == "Command processed!" else plainText
        # Update main text, b, c, v
        references = self.textCommandParser.extractAllVerses(command)
        if references:
            config.mainB, config.mainC, config.mainV, *_ = references[-1]
        return plainText

    def displayOutputOnTerminal(self, content):
        divider = self.divider
        if config.terminalEnablePager and not content in ("Command processed!", "INVALID_COMMAND_ENTERED") and not content.endswith("not supported in terminal mode.") and not content.startswith("[MESSAGE]"):
            if platform.system() == "Windows":
                try:
                    pydoc.pager(content)
                except:
                    config.terminalEnablePager = False
                    print(divider)
                    print(content)
                # When you use remote powershell and want to pipe a command on the remote windows server through a pager, piping through out-host -paging works as desired. Piping through more when running the remote command is of no use: the entire text is displayed at once.
#                try:
#                    pydoc.pipepager(content, cmd='out-host -paging')
#                except:
#                    try:
#                        pydoc.pipepager(content, cmd='more')
#                    except:
#                        config.terminalEnablePager = False
#                        print(divider)
#                        print(content)
            else:
                try:
                    # paging without colours
                    #pydoc.pager(content)
                    # paging with colours
                    pydoc.pipepager(content, cmd='less -R')
                except:
                    config.terminalEnablePager = False
                    print(divider)
                    print(content)
        else:
            if content.startswith("[MESSAGE]"):
                content = content[9:]
            print(divider)
            print(content)

    def getDotCommandContent(self, command):
        if command in self.dotCommands:
            return self.dotCommands[command][-1]()
        elif command == ".quit":
            print("Closing ...")
            return ""
        elif command == ".restart":
            print("Restarting ...")
            return ""
        print(f"Command not found: {command}")
        return ""

    def getTextCommandSuggestion(self, addDotCommandWordOnly=True):
        # Text command autocompletion/autosuggest
        textCommands = [key + ":::" for key in self.textCommandParser.interpreters.keys()]
        bibleBooks = BibleBooks().getStandardBookAbbreviations()
        dotCommands = sorted(list(self.dotCommands.keys()))
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        if addDotCommandWordOnly:
            suggestion = ['.quit', '.restart', 'quit', 'restart', bibleReference] + dotCommands + [cmd[1:] for cmd in dotCommands] + sorted(textCommands) + bibleBooks
        else:
            suggestion = ['.quit', '.restart'] + dotCommands + sorted(textCommands) + bibleBooks
            suggestion.sort()
        return suggestion

    def togglePager(self):
        config.terminalEnablePager = not config.terminalEnablePager
        return self.plainText

    def standardcommands(self):
        content = "UBA commands:"
        content += "\n".join([f"{key} - {self.dotCommands[key][0]}" for key in sorted(self.dotCommands.keys())])
        content += "\n".join([re.sub("            #", "#", value[-1]) for value in self.textCommandParser.interpreters.values()])
        return content

    def terminalcommands(self):
        content = "UBA terminal dot commands:"
        content += "\n".join([f"{key} - {self.dotCommands[key][0]}" for key in sorted(self.dotCommands.keys())])
        print(content)
        return ""

    def stopAudio(self):
        self.textCommandParser.parent.closeMediaPlayer()
        return ""

    def commands(self):
        return pprint.pformat(self.getTextCommandSuggestion(False))

    def read(self):
        self.textCommandParser.parent.getPlaylistFromHTML(self.html)
        return ""

    def readsync(self):
        self.textCommandParser.parent.getPlaylistFromHTML(self.html, displayText=True)
        return ""

    def latest(self):
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        print("BIBLE:::{0}:::{1} [{2}.{3}.{4}]".format(config.mainText, bibleReference, config.mainB, config.mainC, config.mainV))
        commentaryReference = self.textCommandParser.bcvToVerseReference(config.commentaryB, config.commentaryC, config.commentaryV)
        print("COMMENTARY:::{0}:::{1} [{2}.{3}.{4}]".format(config.commentaryText, commentaryReference, config.commentaryB, config.commentaryC, config.commentaryV))
        print(f"BOOK:::{config.book}:::{config.bookChapter}")
        print(f"LEXICON:::{config.lexicon}:::{config.lexiconEntry}")
        print(f"DICTIONARY:::{config.dictionaryEntry}")
        print(f"ENCYCLOPEDIA:::{config.encyclopedia}:::{config.encyclopediaEntry}")
        print(f"THIRDDICTIONARY:::{config.thirdDictionary}:::{config.thirdDictionaryEntry}")
        print(f"DATA:::{config.dataset}")
        print(f"EXLB:::exlbt:::{config.topicEntry}")
        print(f"_harmony:::{config.parallels}.{config.parallelsEntry}")
        print(f"_promise:::{config.promises}.{config.promisesEntry}")
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

    def initialDisplay(self):
        print("--------------------")
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        #print("BIBLE:::{0}:::{1} [{2}.{3}.{4}]".format(config.mainText, bibleReference, config.mainB, config.mainC, config.mainV))
        print("{0} [{1}.{2}.{3}] - {4}{5}, {6}".format(bibleReference, config.mainB, config.mainC, config.mainV, config.mainText, self.getPlusBible(), config.commentaryText))
        print("Enter an UBA command ('.menu' for menu):")
        return ""

    def showbibleabbreviations(self, text="", commentary=False):
        bible = Bible(config.mainText if not text else text)
        bibleBooks = BibleBooks()
        bookNumbers = bible.getBookList()
        print([f"[{b}] {bibleBooks.getStandardBookAbbreviation(b)}" for b in bookNumbers])
        self.currentBibleAbbs = [bibleBooks.getStandardBookAbbreviation(b) for b in bookNumbers]
        try:
            if commentary:
                self.currentBibleAbb = bibleBooks.getStandardBookAbbreviation(config.commentaryB)
            else:
                self.currentBibleAbb = bibleBooks.getStandardBookAbbreviation(config.mainB)
        except:
            self.currentBibleAbb = self.currentBibleAbbs[0]
        self.bookNumbers = bookNumbers
        return ""

    def showbiblebooks(self, text=""):
        bible = Bible(config.mainText if not text else text)
        bibleBooks = BibleBooks()
        bookNumbers = bible.getBookList()
        print([f"[{b}] {bibleBooks.getStandardBookFullName(b)}" for b in bookNumbers])
        self.currentBibleBooks = [bibleBooks.getStandardBookFullName(b) for b in bookNumbers]
        try:
            self.currentBibleBook = bibleBooks.getStandardBookFullName(config.mainB)
        except:
            self.currentBibleBook = self.currentBibleBooks[0]
        self.bookNumbers = bookNumbers
        return ""

    def showbiblechapters(self, text="", b=None):
        bible = Bible(config.mainText if not text else text)
        chapterList = bible.getChapterList(config.mainB if b is None else b)
        print(chapterList)
        self.currentBibleChapters = chapterList
        return ""

    def showbibleverses(self, text="", b=None, c=None):
        bible = Bible(config.mainText if not text else text)
        verseList = bible.getVerseList(config.mainB if b is None else b, config.mainC if c is None else c)
        print(verseList)
        self.currentBibleVerses = verseList
        return ""

    def showtopics(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_topics"])
        moduleList = []
        for index, topic in enumerate(self.crossPlatform.topicListAbb):
            moduleList.append(f"[<ref>{topic}</ref> ] {self.crossPlatform.topicList[index]}")
        content += "<br>".join(moduleList)
        return TextUtil.htmlToPlainText(content).strip()

    def showdictionaries(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["context1_dict"])
        moduleList = []
        for index, topic in enumerate(self.crossPlatform.dictionaryListAbb):
            moduleList.append(f"[<ref>{topic}</ref> ] {self.crossPlatform.dictionaryList[index]}")
        content += "<br>".join(moduleList)
        return TextUtil.htmlToPlainText(content).strip()

    def showencyclopedia(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["context1_encyclopedia"])
        moduleList = []
        for index, topic in enumerate(self.crossPlatform.encyclopediaListAbb):
            moduleList.append(f"[<ref>{topic}</ref> ] {self.crossPlatform.encyclopediaList[index]}")
        content += "<br>".join(moduleList)
        return TextUtil.htmlToPlainText(content).strip()

    def showbibles(self):
        #return pprint.pformat(dict(zip(self.crossPlatform.textList, self.crossPlatform.textFullNameList)))
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_bible"])
        bibleList = []
        for index, bible in enumerate(self.crossPlatform.textList):
            bibleList.append(f"[<ref>{bible}</ref> ] {self.crossPlatform.textFullNameList[index]}")
        content += "<br>".join(bibleList)
        return TextUtil.htmlToPlainText(content).strip()

    def showstrongbibles(self):
        strongBiblesFullNameList = [Bible(text).bibleInfo() for text in self.crossPlatform.strongBibles]
        content = ""
        content += "<h2>{0} + {1}</h2>".format(config.thisTranslation["menu5_bible"], config.thisTranslation["bibleStrongNumber"])
        bibleList = []
        for index, bible in enumerate(self.crossPlatform.strongBibles):
            bibleList.append(f"[<ref>{bible}</ref> ] {strongBiblesFullNameList[index]}")
        content += "<br>".join(bibleList)
        return TextUtil.htmlToPlainText(content).strip()

    def showthirdpartydictionary(self):
        modules = []
        for module in self.crossPlatform.thirdPartyDictionaryList:
            modules.append(f"[<ref>{module}</ref> ]")
        content = "<br>".join(modules)
        return TextUtil.htmlToPlainText(content).strip()

    def showlexicons(self):
        modules = []
        for module in self.crossPlatform.lexiconList:
            modules.append(f"[<ref>{module}</ref> ]")
        content = "<br>".join(modules)
        return TextUtil.htmlToPlainText(content).strip()

    def showcommentaries(self):
        self.textCommandParser.parent.setupResourceLists()
        content = ""
        content += """<h2><ref onclick="window.parent.submitCommand('.commentarymenu')">{0}</ref></h2>""".format(config.thisTranslation["menu4_commentary"])
        content += "<br>".join(["""[<ref>{0}</ref> ] {1}""".format(abb, self.textCommandParser.parent.commentaryFullNameList[index]) for index, abb in enumerate(self.textCommandParser.parent.commentaryList)])
        return TextUtil.htmlToPlainText(content).strip()

    def showreferencebooks(self):
        self.textCommandParser.parent.setupResourceLists()
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_selectBook"])
        content += "<br>".join(["""[<ref>{0}</ref> ] {0}""".format(book) for book in self.textCommandParser.parent.referenceBookList])
        return TextUtil.htmlToPlainText(content).strip()

    def showdata(self):
        self.textCommandParser.parent.setupResourceLists()
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu_data"])
        dataList = [item for item in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "menu", "Bible Data"), "txt")]
        content += "<br>".join(["""[<ref>DATA:::{0}</ref> ] {0}""".format(book)
            for book in dataList])
        return TextUtil.htmlToPlainText(content).strip()

    def showdownloads(self):
        content = ""
        from util.DatafileLocation import DatafileLocation
        from util.GithubUtil import GithubUtil
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
                    content += """[<ref>DOWNLOAD:::{0}:::{1}</ref> ]<br>"""\
                        .format(keyword, k)
        resources = (
            ("GitHub Bibles", "GitHubBible", GitHubRepoInfo.bibles[0], (config.marvelData, "bibles"), ".bible"),
            ("GitHub Commentaries", "GitHubCommentary", GitHubRepoInfo.commentaries[0], (config.marvelData, "commentaries"), ".commentary"),
            ("GitHub Books", "GitHubBook", GitHubRepoInfo.books[0], (config.marvelData, "books"), ".book"),
            ("GitHub Maps", "GitHubMap", GitHubRepoInfo.maps[0], (config.marvelData, "books"), ".book"),
            ("GitHub PDF", "GitHubPdf", GitHubRepoInfo.pdf[0], (config.marvelData, "pdf"), ".pdf"),
            ("GitHub EPUB", "GitHubEpub", GitHubRepoInfo.epub[0], (config.marvelData, "epub"), ".epub"),
        )
        for collection, type, repo, location, extension in resources:
            content += "<h2>{0}</h2>".format(collection)
            for file in GithubUtil(repo).getRepoData():
                if os.path.isfile(os.path.join(*location, file)):
                    content += """[ {1} ] {0}<br>""".format(file.replace(extension, ""), config.thisTranslation["installed"])
                else:
                    content += """[<ref>DOWNLOAD:::{1}:::{0}</ref> ]<br>""".format(file.replace(extension, ""), type)
        content += "<h2>Third-party Resources</h2><p>Read <ref>https://github.com/eliranwong/UniqueBible/wiki/Third-party-resources</ref> about third-party resources.</a></p>"
        return TextUtil.htmlToPlainText(content).strip()

    def getCliOutput(self, cli):
        try:
            process = subprocess.Popen(cli, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, *_ = process.communicate()
            return stdout.decode("utf-8")
        except:
            return ""

    def showttslanguages(self):
        codes = list(self.ttsLanguages.keys())

        display = "<h2>Languages</h2>"
        languages = []
        for code in codes:
            language = self.ttsLanguages[code][-1]
            languages.append(language)
            display += f"[<ref>{code}</ref> ] {language}<br>"
        display = display[:-4]
        print(TextUtil.htmlToPlainText(display).strip())
        return ""

    def getDefaultTtsKeyword(self):
        if config.isGoogleCloudTTSAvailable:
            return "GTTS"
        elif (not config.isOfflineTtsInstalled or config.forceOnlineTts) and config.isGTTSInstalled:
            return "GTTS"
        elif config.macVoices:
            return "SPEAK"
        elif config.espeak:
            return "SPEAK"
        else:
            return "SPEAK"

    def tts(self, runOnCopiedText=True):
        codes = list(self.ttsLanguages.keys())
        #display = "<h2>Languages</h2>"
        shortCodes = []
        languages = []
        for code in codes:
            shortCodes.append(re.sub("\-.*?$", "", code))
            languages.append(self.ttsLanguages[code])
            #display += f"[<ref>{codes}</ref> ] {languages}<br>"
        #display = display[:-4]

        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showttslanguages())
            self.printChooseItem()
            print("Enter a language code:")
            if config.isPrompt_toolkitInstalled:
                suggestions = shortCodes + codes
                suggestions = list(set(suggestions))
                completer = WordCompleter(suggestions, ignore_case=True)
                default = config.ttsDefaultLangauge if config.ttsDefaultLangauge in suggestions else ""
                userInput = self.terminal_tts_language_session.prompt(self.inputIndicator, completer=completer, default=default).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if userInput in suggestions:
                config.ttsDefaultLangauge = userInput
                commandPrefix = f"{self.getDefaultTtsKeyword()}:::{userInput}:::"
                if runOnCopiedText:
                    return self.runclipboardtext(commandPrefix)
                else:
                    print(self.divider)
                    print("Enter text to be read:")
                    textToSpeech = self.simplePrompt()
                    command = f"{commandPrefix}{textToSpeech}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def getclipboardtext(self):
        try:
            if config.terminalEnableTermuxAPI:
                clipboardText = self.getCliOutput("termux-clipboard-get")
            elif config.isPyperclipInstalled:
                import pyperclip
                clipboardText = pyperclip.paste()
            if clipboardText:
                print(self.divider)
                print("Clipboard text:")
                print(clipboardText)
                print(self.divider)
                return clipboardText
            else:
                print("No copied text is found!")
                return self.cancelAction()
        except:
            return self.noClipboardUtility()

    def runclipboardtext(self, commandPrefix="", commandSuffix=""):
        clipboardText = self.getclipboardtext()
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

    def toggleBibleChapterFormat(self):
        config.readFormattedBibles = not config.readFormattedBibles
        command = "BIBLE:::"
        self.printRunningCommand(command)
        return self.getContent(command)

    def getCommand(self, command=""):
        if not command:
            command = self.command
        exception = "^(_setconfig:::|mp3:::|mp4:::|cmd:::)"
        if command.startswith(".") or re.search(exception, command.lower()):
            command = ".bible"
        return command

    # open web version
    # use local http-server if it is running
    # otherwise, use public
    def web(self, command=""):
        server = "http://localhost:8080"
        if not self.isUrlAlive(server):
            server = ""
        weblink = TextUtil.getWeblink(self.getCommand(command), server=server)
        return self.getContent(f"_website:::{weblink}")

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
                import pyperclip
                pyperclip.copy(weblink)
            print(f"The following link is copied to clipboard:\n")
            print(weblink)
            print("\nOpen it in a web browser or share with others.")
            return ""
        except:
            return self.noClipboardUtility()

    def copy(self):
        try:
            plainText = self.getPlainText()
            if config.terminalEnableTermuxAPI:
                pydoc.pipepager(plainText, cmd="termux-clipboard-set")
            else:
                import pyperclip
                pyperclip.copy(plainText)
                print("Content is copied to clipboard.")
            return ""
        except:
            return self.noClipboardUtility()

    def copyHtml(self):
        try:
            if config.terminalEnableTermuxAPI:
                pydoc.pipepager(self.html, cmd="termux-clipboard-set")
            else:
                import pyperclip
                pyperclip.copy(self.html)
                print("HTML content is copied to clipboard.")
            return ""
        except:
            return self.noClipboardUtility()

    def noClipboardUtility(self):
        print("Clipboard utility is not found!")
        return ""

    def find(self):
        print("Enter a search pattern: ")
        userInput = self.terminal_find_session.prompt(self.inputIndicator).strip() if config.isPrompt_toolkitInstalled else input(self.inputIndicator).strip()
        if config.isColoramaInstalled:
            from colorama import init
            init()
            from colorama import Fore, Back, Style
            content = re.sub(r"({0})".format(userInput), r"{0}{1}\1{2}".format(Back.RED, Fore.WHITE, Style.RESET_ALL), self.plainText, flags=re.IGNORECASE)
        else:
            content = re.sub(r"({0})".format(userInput), r"[[[ \1 ]]]", self.plainText, flags=re.IGNORECASE)
        return content

    def history(self):
        return self.readPlainTextFile(os.path.join("terminal_history", "commands"))

    def readPlainTextFile(self, filename):
        if os.path.isfile(filename):
            with open(filename, "r", encoding="utf-8") as input_file:
                text = input_file.read()
        return text

    def displayMessage(self, message="", title="UniqueBible"):
        print(title)
        print(message)

    def update(self, debug=False):
        try:
            try:
                os.system("git pull")
                return self.finishUpdate()
            except:
                # Old way to update
                requestObject = requests.get("{0}patches.txt".format(UpdateUtil.repository))
                for line in requestObject.text.split("\n"):
                    if line:
                        try:
                            version, contentType, filePath = literal_eval(line)
                            if version > config.version:
                                localPath = os.path.join(*filePath.split("/"))
                                if debug:
                                    print("{0}:{1}".format(version, localPath))
                                else:
                                    if contentType == "folder":
                                        if not os.path.isdir(localPath):
                                            os.makedirs(localPath, exist_ok=True)
                                    elif contentType == "file":
                                        requestObject2 = requests.get("{0}{1}".format(UpdateUtil.repository, filePath))
                                        with open(localPath, "wb") as fileObject:
                                            fileObject.write(requestObject2.content)
                                    elif contentType == "delete":
                                        try:
                                            if os.path.exists(localPath):
                                                os.remove(localPath)
                                        except:
                                            print("Could not delete {0}".format(localPath))
                        except Exception as e:
                            return self.updateFailed()

                return self.finishUpdate()
        except:
            return self.updateFailed()

    def updateFailed(self):
        print("Failed to update to the latest version.")
        if not config.internet:
            print("You may need to check your internet connection.")
        return ""

    def finishUpdate(self):
        # set executable files on macOS or Linux
        if not platform.system() == "Windows":
            for filename in ("uba.py", "main.py", "BibleVerseParser.py", "RegexSearch.py"):
                if os.path.isfile(filename):
                    os.chmod(filename, 0o755)
                # finish message
        config.lastAppUpdateCheckDate = str(DateUtil.localDateNow())

        print("You have the latest version.")
        return ".restart"

    def config(self):
        intro = "<h2>Unique Bible App Configurations</h2>"
        intro += "<p>Default settings are good for general use.  In case you want to make changes, you may run '<ref>_setconfig:::</ref>' command in terminal mode.  Alternately, you may manually edit the file 'config.py', located in UBA home directory, when UBA is not running.</p>"
        content = "{0}<p>{1}</p>".format(intro, "</p><p>".join(["[ITEM] <ref>{0}</ref>{1}\nCurrent value: <z>{2}</z>".format(key, re.sub("        # ", "", value), eval("pprint.pformat(config."+key+")")) for key, value in config.help.items()]))
        return TextUtil.htmlToPlainText(content).strip()

    def latestBible(self):
        command = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        self.printRunningCommand(command)
        return self.getContent(command)

    def togglebiblecomparison(self):
        config.terminalBibleComparison = not config.terminalBibleComparison
        return self.latestBible()

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
        print("Install package 'prompt_toolkit' first!")
        return ""

    def simplePrompt(self):
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt
            userInput = prompt(self.inputIndicator).strip()
        else:
            userInput = input(self.inputIndicator).strip()
        return userInput

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
            print(f"'{url}' is already alive!")
        else:
            subprocess.Popen([sys.executable, config.httpServerUbaFile, "http-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("UBA hptt-server started!")
        print("To connect, open 'http://{0}:{1}' in a web browser.".format(NetworkUtil.get_ip(), config.httpServerPort))
        return ""

    def stophttpserver(self):
        url = "http://localhost:8080/index.html?cmd=.stop"
        if self.isUrlAlive(url):
            print("http-server stopped!")
        else:
            print("http-server is not running!")
        return ""

    def downloadyoutube(self):
        if config.isYoutubeDownloaderInstalled and self.textCommandParser.isFfmpegInstalled():
            try:
                print(self.divider)
                print("Enter a youtube link:")
                userInput = self.simplePrompt()
                if not userInput or userInput == self.cancelCommand:
                    return self.cancelAction()
                print("Checking connection ...")
                if self.isUrlAlive(userInput):
                    print("Connection is available.")
                    print(self.divider)
                    url = userInput
                    options = {
                        "0": "mp3:::",
                        "1": "mp4:::",
                    }
                    self.printChooseItem()
                    print("[0] Download mp3 audio")
                    print("[1] Download mp4 video")
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

    def textract(self):
        if config.isTextractInstalled:
            print(self.divider)
            print("Enter a file path below:")
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                userInput = prompt(self.inputIndicator).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if os.path.isfile(userInput):
                import textract
                return textract.process(userInput).decode()
            else:
                return self.printInvalidOptionEntered()
        self.printToolNotFound("textract")
        return ""

    def printToolNotFound(self, tool):
        print(f"Tool '{tool}' is not found on your system!")

    def searchTools2(self, moduleType):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
            elements = {
                "parallels": ("SEARCHBOOK:::Harmonies_and_Parallels:::", "SEARCHBOOK:::Harmonies_and_Parallels", "BOOK:::Harmonies_and_Parallels:::"),
                "promises": ("SEARCHBOOK:::Bible_Promises:::", "SEARCHBOOK:::Bible_Promises", "BOOK:::Bible_Promises:::"),
                "names": ("SEARCHTOOL:::HBN:::", "SEARCHTOOL:::HBN:::", ""),
                "characters": ("SEARCHTOOL:::EXLBP:::", "SEARCHTOOL:::EXLBP:::", "EXLB:::exlbp:::"),
                "locations": ("SEARCHTOOL:::EXLBL:::", "SEARCHTOOL:::EXLBL:::", "EXLB:::exlbl:::"),
            }
            searchPrefix, showAll, openPrefix = elements[moduleType]
            print(self.divider)
            self.printSearchEntryPrompt()
            if config.isPrompt_toolkitInstalled:
                userInput = prompt(self.inputIndicator).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if userInput == self.cancelCommand:
                return self.cancelAction()
            elif not userInput:
                command = showAll
            else:
                command = f"{searchPrefix}{userInput}"
            self.printRunningCommand(command)
            print(self.divider)
            content = self.getContent(command)
            if content.startswith("[MESSAGE]"):
                content = content[10:]
            if openPrefix:
                print(content)
                print(self.divider)
                print(f"Enter an item to open:")
                if config.isPrompt_toolkitInstalled:
                    userInput = prompt(self.inputIndicator).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput == self.cancelCommand:
                    return self.cancelAction()
                print(self.divider)
                command = f"{openPrefix}{userInput}"
                self.printRunningCommand(command)
                print(self.divider)
                return self.getContent(command)
            else:
                return content
        except:
            return self.printInvalidOptionEntered()

    def quickSearch(self, runOnCopiedText=True):
        try:
            if runOnCopiedText:
                self.getclipboardtext()
            searchModes = ("SEARCH", "SEARCHALL", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
            options = {
                "0": ("Whole Bible", searchModes[config.bibleSearchMode], "", config.mainText, ""),
                "1": ("Old Testament", searchModes[config.bibleSearchMode], "", config.mainText, ":::OT"),
                "2": ("New Testament", searchModes[config.bibleSearchMode], "", config.mainText, ":::NT"),
                "3": (BibleBooks().getStandardBookFullName(config.mainB), searchModes[config.bibleSearchMode], "", config.mainText, f":::{BibleBooks().getStandardBookAbbreviation(config.mainB)}"),
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
                "20": ("Bible Concordance", "CONCORDANCE", "", "OHGBi", ""),
            }
            display = [f"[<ref>{key}</ref> ] {value[0]} - {value[-2]}" for key, value in options.items()]
            display = "<br>".join(display)
            display = f"<h2>Run Quick Search of Copied Text</h2>{display}" if runOnCopiedText else f"<h2>Quick Search</h2>{display}"
            print(TextUtil.htmlToPlainText(display))
            print(self.divider)
            print("Enter a number:")
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                userInput = prompt(self.inputIndicator).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            # define key
            if -1 < int(userInput) < 21:
                feature, searchKeyword, openKeyword, latestSelection, searchSuffix = options[userInput]
                latestSelection = f"{latestSelection}:::" if latestSelection else ""
                searchPrefix = f"{searchKeyword}:::{latestSelection}"
                if feature == "Dictionary":
                    latestSelection = ""
                if openKeyword == "EXLB":
                    latestSelection = latestSelection.lower()
                config.terminalCommandDefault = f"{openKeyword}:::{latestSelection}" if openKeyword else ""
                if openKeyword:
                    if runOnCopiedText:
                        print(self.runclipboardtext(searchPrefix, searchSuffix))
                        return ""
                    else:
                        print(self.divider)
                        print("Enter a search item:")
                        userInput = self.simplePrompt()
                        command = f"{searchPrefix}{userInput}{searchSuffix}"
                        self.printRunningCommand(command)
                        print(self.getContent(command))
                        return ""
                else:
                    if runOnCopiedText:
                        return self.runclipboardtext(searchPrefix, searchSuffix)
                    else:
                        print(self.divider)
                        print("Enter a search item:")
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
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter
            elements = {
                "BOOK": (config.book, self.crossPlatform.referenceBookList, config.bookChapter, self.terminal_books_selection_session, "SEARCHBOOK"),
                "TOPICS": (config.topic, self.crossPlatform.topicListAbb, config.topicEntry, self.terminal_topics_selection_session, ""),
                "ENCYCLOPEDIA": (config.encyclopedia, self.crossPlatform.encyclopediaListAbb, config.encyclopediaEntry, self.terminal_encyclopedia_selection_session, ""),
                "DICTIONARY": (config.dictionary, self.crossPlatform.dictionaryListAbb, config.dictionaryEntry, self.terminal_dictionary_selection_session, ""),
                "THIRDDICTIONARY": (config.thirdDictionary, self.crossPlatform.thirdPartyDictionaryList, config.thirdDictionaryEntry, self.terminal_thridPartyDictionaries_selection_session, "SEARCHTHIRDDICTIONARY"),
                "LEXICON": (config.lexicon, self.crossPlatform.lexiconList, config.lexiconEntry, self.terminal_lexicons_selection_session, "SEARCHLEXICON"),
                "REVERSELEXICON": (config.lexicon, self.crossPlatform.lexiconList, "", self.terminal_lexicons_selection_session, "REVERSELEXICON"),
            }
            print(self.divider)
            print(showModules())
            default, abbList, latestEntry, historySession, searchKeyword = elements[moduleType]
            if not searchKeyword:
                searchKeyword = "SEARCHTOOL"
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(abbList, ignore_case=True)
                userInput = historySession.prompt(self.inputIndicator, completer=completer, default=default).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if userInput in abbList:
                module = userInput
                print(self.divider)
                self.printSearchEntryPrompt()
                if config.isPrompt_toolkitInstalled:
                    userInput = prompt(self.inputIndicator).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput == self.cancelCommand:
                    return self.cancelAction()
                command = f"{searchKeyword}:::{module}:::{userInput}"
                self.printRunningCommand(command)
                print(self.divider)
                content = self.getContent(command)
                if moduleType == "REVERSELEXICON":
                    return content
                print(content[10:] if content.startswith("[MESSAGE]") else content)
                print(self.divider)
                print(f"To open, enter a module entry (e.g. {latestEntry}):")
                if config.isPrompt_toolkitInstalled:
                    userInput = prompt(self.inputIndicator).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput == self.cancelCommand:
                    return self.cancelAction()
                print(self.divider)

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

    def openreferencebook(self):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showreferencebooks())
            print(self.divider)
            print("Enter a reference book:")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.referenceBookList, ignore_case=True)
                userInput = self.terminal_books_selection_session.prompt(self.inputIndicator, completer=completer, default=config.book).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if userInput in self.crossPlatform.referenceBookList:
                book = userInput
                chapterList = Book(book).getTopicList()
                chapterDisplay = "<h2>Chapters</h2>"
                chapterDisplay += "<br>".join([f"<ref>{chapter}</ref>" for chapter in chapterList])
                print(self.divider)
                print(TextUtil.htmlToPlainText(chapterDisplay).strip())
                print(self.divider)
                print("Enter a chapter title:")
                if config.isPrompt_toolkitInstalled:
                    completer = WordCompleter(chapterList, ignore_case=True)
                    userInput = prompt(self.inputIndicator, completer=completer, default=config.bookChapter if config.bookChapter in chapterList else "").strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput == self.cancelCommand:
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
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
            today = date.today()
            print(self.divider)
            print(f"Enter a year, e.g. {today.year}:")
            if config.isPrompt_toolkitInstalled:
                userInput = prompt(self.inputIndicator, default=str(today.year)).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if int(userInput):
                year = userInput
                print(self.divider)
                print(f"Enter a month, e.g. {today.month}:")
                if config.isPrompt_toolkitInstalled:
                    userInput = prompt(self.inputIndicator, default=str(today.month)).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput == self.cancelCommand:
                    return self.cancelAction()
                if int(userInput):
                    month = userInput
                    print(self.divider)
                    print(f"Enter a day, e.g. {today.day}:")
                    if config.isPrompt_toolkitInstalled:
                        userInput = prompt(self.inputIndicator, default=str(today.day)).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput == self.cancelCommand:
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

    def openversefeature(self, feature="CROSSREFERENCE"):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            firstBible = config.mainText
            print(self.divider)
            print(self.showbibleabbreviations(text=firstBible))
            print(self.divider)
            self.printChooseItem()
            print("(enter a book abbreviation)")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.currentBibleAbbs, ignore_case=True)
                userInput = prompt(self.inputIndicator, completer=completer, default=self.currentBibleAbb).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if userInput in self.currentBibleAbbs:
                abbIndex = self.currentBibleAbbs.index(userInput)
                bibleBookNumber = self.bookNumbers[abbIndex]
                bibleAbb = userInput
                print(self.divider)
                self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                print(self.divider)
                self.printChooseItem()
                print("(enter a chapter number)")
                if config.isPrompt_toolkitInstalled:
                    defaultChapter = str(config.mainC) if config.mainC in self.currentBibleChapters else str(self.currentBibleChapters[0])
                    userInput = prompt(self.inputIndicator, default=defaultChapter).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput == self.cancelCommand:
                    return self.cancelAction()
                if int(userInput) in self.currentBibleChapters:
                    bibleChapter = userInput
                    print(self.divider)
                    self.showbibleverses(text=firstBible, b=bibleBookNumber, c=int(userInput))
                    print(self.divider)
                    self.printChooseItem()
                    print("(enter a verse number)")
                    if config.isPrompt_toolkitInstalled:
                        defaultVerse = str(config.mainV) if config.mainV in self.currentBibleVerses else str(self.currentBibleVerses[0])
                        userInput = prompt(self.inputIndicator, default=defaultVerse).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput == self.cancelCommand:
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
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            firstBible = config.mainText
            print(self.divider)
            print(self.showbibleabbreviations(text=firstBible))
            print(self.divider)
            self.printChooseItem()
            print("(enter a book abbreviation)")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.currentBibleAbbs, ignore_case=True)
                userInput = prompt(self.inputIndicator, completer=completer, default=self.currentBibleAbb).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if userInput in self.currentBibleAbbs:
                abbIndex = self.currentBibleAbbs.index(userInput)
                bibleBookNumber = self.bookNumbers[abbIndex]
                bibleAbb = userInput
                print(self.divider)
                self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                print(self.divider)
                self.printChooseItem()
                print("(enter a chapter number)")
                if config.isPrompt_toolkitInstalled:
                    defaultChapter = str(config.mainC) if config.mainC in self.currentBibleChapters else str(self.currentBibleChapters[0])
                    userInput = prompt(self.inputIndicator, default=defaultChapter).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput == self.cancelCommand:
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
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            firstBible = config.mainText
            print(self.divider)
            print(self.showbiblebooks(text=firstBible))
            print(self.divider)
            self.printChooseItem()
            print("(enter a book abbreviation)")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.currentBibleBooks, ignore_case=True)
                userInput = prompt(self.inputIndicator, completer=completer, default=self.currentBibleBook).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if userInput in self.currentBibleBooks:
                #bookIndex = self.currentBibleBooks.index(userInput)
                #bibleBookNumber = self.bookNumbers[bookIndex]
                bibleBook = userInput
                features = {
                    "introduction": "SEARCHBOOKCHAPTER:::Tidwell_The_Bible_Book_by_Book",
                    "dictionary": f"SEARCHTOOL:::{config.dictionary}",
                    "encyclopedia": f"SEARCHTOOL:::{config.encyclopedia}",
                    "timelines": "SEARCHBOOKCHAPTER:::Timelines",
                }
                feature = features.get(feature, feature)
                command = f"{feature}:::{bibleBook}"
                self.printRunningCommand(command)
                return self.getContent(command)
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def openbible(self):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showbibles())
            print(self.divider)
            self.printChooseItem()
            print("Enter a bible abbreviation to open a single version, e.g. 'KJV'")
            print("To compare multiple versions, use '_' as a delimiter, e.g. 'KJV_NET_OHGBi'")
            # select bible or bibles
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.textList, ignore_case=True)
                defaultText = self.getDefaultText()
                userInput = self.terminal_bible_selection_session.prompt(self.inputIndicator, completer=completer, default=defaultText).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if self.isValidBibles(userInput):
                bible = userInput
                firstBible = bible.split("_")[0]
                print(self.divider)
                print(self.showbibleabbreviations(text=firstBible))
                print(self.divider)
                self.printChooseItem()
                print("(enter a book abbreviation)")
                # select bible book
                if config.isPrompt_toolkitInstalled:
                    completer = WordCompleter(self.currentBibleAbbs, ignore_case=True)
                    userInput = prompt(self.inputIndicator, completer=completer, default=self.currentBibleAbb).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput == self.cancelCommand:
                    return self.cancelAction()
                if userInput in self.currentBibleAbbs:
                    abbIndex = self.currentBibleAbbs.index(userInput)
                    bibleBookNumber = self.bookNumbers[abbIndex]
                    bibleAbb = userInput
                    print(self.divider)
                    self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                    print(self.divider)
                    self.printChooseItem()
                    print("(enter a chapter number)")
                    # select bible chapter
                    if config.isPrompt_toolkitInstalled:
                        defaultChapter = str(config.mainC) if config.mainC in self.currentBibleChapters else str(self.currentBibleChapters[0])
                        userInput = prompt(self.inputIndicator, default=defaultChapter).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput == self.cancelCommand:
                        return self.cancelAction()
                    if int(userInput) in self.currentBibleChapters:
                        bibleChapter = userInput
                        print(self.divider)
                        self.showbibleverses(text=firstBible, b=bibleBookNumber, c=int(userInput))
                        print(self.divider)
                        self.printChooseItem()
                        print("(enter a verse number)")
                        # select verse number
                        if config.isPrompt_toolkitInstalled:
                            defaultVerse = str(config.mainV) if config.mainV in self.currentBibleVerses else str(self.currentBibleVerses[0])
                            userInput = prompt(self.inputIndicator, default=defaultVerse).strip()
                        else:
                            userInput = input(self.inputIndicator).strip()
                        if not userInput or userInput == self.cancelCommand:
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
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.commands())
            print(self.divider)
            self.printChooseItem()
            commands = self.getTextCommandSuggestion(False)
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(commands, ignore_case=True)
                userInput = self.terminal_bible_selection_session.prompt(self.inputIndicator, completer=completer).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if userInput in commands:
                return self.whatiscontent(userInput)
        except:
            return self.printInvalidOptionEntered()

    def whatiscontent(self, command):
        if command in self.dotCommands:
            print(self.dotCommands[command][0])
        else:
            print(self.getContent(f"_whatis:::{command}"))
        return ""

    def searchconcordance(self):
        try:
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showstrongbibles())
            self.printChooseItem()
            print("Enter a bible abbreviation to search a single version, e.g. 'KJVx'")
            print("To search multiple versions, use '_' as a delimiter, e.g. 'KJVx_RWVx_OHGBi'")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.strongBibles, ignore_case=True)
                userInput = self.terminal_search_strong_bible_session.prompt(self.inputIndicator, completer=completer).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if self.isValidBibles(userInput):
                # bible version(s) defined
                bible = userInput
                print(self.divider)
                print("Enter a Strong's number or lexical entry:")
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
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showbibles())
            print(self.divider)
            self.printChooseItem()
            print("Enter a bible abbreviation to open a single version, e.g. 'KJV'")
            print("To compare multiple versions, use '_' as a delimiter, e.g. 'KJV_NET_OHGBi'")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.textList, ignore_case=True)
                defaultText = self.getDefaultText()
                userInput = self.terminal_bible_selection_session.prompt(self.inputIndicator, completer=completer, default=defaultText).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if self.isValidBibles(userInput):
                # bible version(s) defined
                bible = userInput

                firstBible = bible.split("_")[0]
                print(self.divider)
                print(self.showbibleabbreviations(text=firstBible))
                print(self.divider)
                self.printChooseItem()
                print("(enter bible books for search)")
                print("(use ',' as a delimiter between books)")
                print("(use '-' as a range indicator)")
                print("(e.g. 'ALL', 'OT', 'NT', 'Gen, John', 'Matt-John, 1Cor, Rev', etc.)")
                # select bible book range
                if config.isPrompt_toolkitInstalled:
                    completer = WordCompleter(["ALL", "OT", "NT"] + self.currentBibleAbbs, ignore_case=True)
                    userInput = self.terminal_search_bible_book_range_session.prompt(self.inputIndicator, completer=completer, default="ALL").strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput == self.cancelCommand:
                    return self.cancelAction()
                if BibleVerseParser(config.parserStandarisation).extractBookListAsString(userInput):
                    # define book range
                    bookRange = userInput

                    searchOptions = {
                        "SEARCH": ("search for occurrence of a string", "plain text", "Jesus love"),
                        "SEARCHALL": ("search for string", "plain text", "Jesus love"),
                        "ANDSEARCH": ("search for a combination of strings appeared in the same verse", "multiple plain text strings, delimited by '|'", "Jesus|love|disciple"),
                        "ORSEARCH": ("search for either one of the entered strings appeared in a single verse", "multiple plain text strings, delimited by '|'", "Jesus|love|disciple"),
                        "ADVANCEDSEARCH": ("search for a condition or a combination of conditions", "condition statement placed after the keyword 'WHERE' in a SQL query", 'Book = 1 AND Scripture LIKE "%worship%"'),
                        "REGEXSEARCH": ("search for a regular expression", "regular expression", "Jesus.*?love"),
                    }
                    searchOptionsList = list(searchOptions.keys())
                    print(self.divider)
                    display = "<br>".join([f"[<ref>{index}</ref> ] {searchOptions[item][0]}" for index, item in enumerate(searchOptionsList)])
                    display = f"<h2>Search Options</h2>{display}"
                    print(TextUtil.htmlToPlainText(display).strip())
                    print(self.divider)
                    self.printChooseItem()
                    print("(enter a number)")
                    if config.isPrompt_toolkitInstalled:
                        userInput = prompt(self.inputIndicator, default=str(config.bibleSearchMode)).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput == self.cancelCommand:
                        return self.cancelAction()
                    userInput = int(userInput)
                    if -1 < userInput < 6:
                        # define bibleSearchMode
                        config.bibleSearchMode = userInput
                        # define command keyword
                        keyword = searchOptionsList[userInput]
                        print(self.divider)
                        self.printSearchEntryPrompt()
                        *_, stringFormat, example = searchOptions[searchOptionsList[userInput]]
                        print(f"(format: {stringFormat})")
                        print(f"(example: {example})")
                        if config.isPrompt_toolkitInstalled:
                            userInput = self.terminal_search_bible_session.prompt(self.inputIndicator).strip()
                        else:
                            userInput = input(self.inputIndicator).strip()
                        if not userInput or userInput == self.cancelCommand:
                            return self.cancelAction()
                        command = f"{keyword}:::{bible}:::{userInput}:::{bookRange}"

                        # Check if it is a case-sensitive search
                        print(self.divider)
                        print("Is it case sensitive? ([Y]es or [N]o)")
                        if config.isPrompt_toolkitInstalled:
                            userInput = prompt(self.inputIndicator, default="Y" if config.enableCaseSensitiveSearch else "N").strip()
                        else:
                            userInput = input(self.inputIndicator).strip()
                        if not userInput or userInput == self.cancelCommand:
                            return self.cancelAction()
                        if userInput.lower() in ("yes", "y", "no", "n"):
                            config.enableCaseSensitiveSearch = (userInput.lower()[0] == "y")
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
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                from prompt_toolkit.completion import WordCompleter

            print(self.divider)
            print(self.showcommentaries())
            print(self.divider)
            self.printChooseItem()
            print("Enter a commentary abbreviation, e.g. 'CBSC'")
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.commentaryList, ignore_case=True)
                defaultText = config.commentaryText
                userInput = self.terminal_commentary_selection_session.prompt(self.inputIndicator, completer=completer, default=defaultText).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            if userInput in self.crossPlatform.commentaryList:
                module = userInput
                firstBible = "KJV"
                print(self.divider)
                print(self.showbibleabbreviations(text=firstBible, commentary=True))
                print(self.divider)
                self.printChooseItem()
                print("(enter a book abbreviation)")
                if config.isPrompt_toolkitInstalled:
                    completer = WordCompleter(self.currentBibleAbbs, ignore_case=True)
                    userInput = prompt(self.inputIndicator, completer=completer, default=self.currentBibleAbb).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput == self.cancelCommand:
                    return self.cancelAction()
                if userInput in self.currentBibleAbbs:
                    abbIndex = self.currentBibleAbbs.index(userInput)
                    bibleBookNumber = self.bookNumbers[abbIndex]
                    bibleAbb = userInput
                    print(self.divider)
                    self.showbiblechapters(text=firstBible, b=bibleBookNumber)
                    print(self.divider)
                    self.printChooseItem()
                    print("(enter a chapter number)")
                    if config.isPrompt_toolkitInstalled:
                        defaultChapter = str(config.commentaryC) if config.commentaryC in self.currentBibleChapters else str(self.currentBibleChapters[0])
                        userInput = prompt(self.inputIndicator, default=defaultChapter).strip()
                    else:
                        userInput = input(self.inputIndicator).strip()
                    if not userInput or userInput == self.cancelCommand:
                        return self.cancelAction()
                    if int(userInput) in self.currentBibleChapters:
                        bibleChapter = userInput
                        print(self.divider)
                        self.showbibleverses(text=firstBible, b=bibleBookNumber, c=int(userInput))
                        print(self.divider)
                        self.printChooseItem()
                        print("(enter a verse number)")
                        if config.isPrompt_toolkitInstalled:
                            defaultVerse = str(config.commentaryV) if config.commentaryV in self.currentBibleVerses else str(self.currentBibleVerses[0])
                            userInput = prompt(self.inputIndicator, default=defaultVerse).strip()
                        else:
                            userInput = input(self.inputIndicator).strip()
                        if not userInput or userInput == self.cancelCommand:
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
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt
            from prompt_toolkit.completion import WordCompleter

        optionMap = {
            "Terminal Heading Text Color": "terminalHeadingTextColor",
            "Terminal Verse Number Color": "terminalVerseNumberColor",
            "Terminal Resource Link Color": "terminalResourceLinkColor",
            "Terminal Verse Selection Background": "terminalVerseSelectionBackground",
            "Terminal Verse Selection Foreground": "terminalVerseSelectionForeground",
            "Terminal Search Highlight Background": "terminalSearchHighlightBackground",
            "Terminal Search Highlight Foreground": "terminalSearchHighlightForeground",
            "Terminal Find Highlight Background": "terminalFindHighlightBackground",
            "Terminal Find Highlight Foreground": "terminalFindHighlightForeground",
        }
        options = [f"[{i}] {item}" for i, item in enumerate(optionMap.keys())]
        print(self.divider)
        self.printChooseItem()
        print(pprint.pformat(options))
        print(self.divider)
        self.printEnterNumber((len(options) - 1))
        self.printCancelOption()
        if config.isPrompt_toolkitInstalled:
            completer = WordCompleter([str(i) for i in range(len(options))])
            userInput = prompt(self.inputIndicator, completer=completer)
        else:
            userInput = input(self.inputIndicator)
        if userInput == self.cancelCommand:
            return self.cancelAction()
        try:
            optionIndex = int(userInput.strip())
            option = options[optionIndex]
            option = re.sub("^\[[0-9]+?\] ", "", option)
            configitem = optionMap[option]
            options = [f"[{i}] {item}" for i, item in enumerate(config.terminalColors)]
            print(self.divider)
            self.printChooseItem()
            print(pprint.pformat(options))
            print(self.divider)
            self.printEnterNumber((len(options) - 1))
            self.printCancelOption()
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter([str(i) for i in range(len(options))])
                userInput = prompt(self.inputIndicator, completer=completer)
            else:
                userInput = input(self.inputIndicator)
            if userInput == self.cancelCommand:
                return self.cancelAction()
            else:
                color = config.terminalColors[int(userInput)]
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
        if config.terminalEnableTermuxAPI:
            self.getContent(f"cmd:::termux-toast -s {message}")

    def actionDone(self):
        message = "Done!"
        print(message)
        self.toast(message)
        return ""

    def cancelAction(self):
        config.terminalCommandDefault = ""
        message = "Action cancelled!"
        print(message)
        self.toast(message)
        return ""

    def printChooseItem(self):
        print("Choose an item:")

    def printCancelOption(self):
        print(f"(or enter '{self.cancelCommand}' to cancel)")

    def printInvalidOptionEntered(self):
        message = "Invalid option entered!"
        print(message)
        self.toast(message)
        return ""

    def printRunningCommand(self, command):
        self.command = command
        print(f"Running {command} ...")

    def printEnterNumber(self, number):
        print(f"Enter a number [0 ... {number}]:")

    # Get latest content in plain text
    def getPlainText(self, content=None):
        return TextUtil.htmlToPlainText(self.html if content is None else content, False).strip()

    def printSearchEntryPrompt(self):
        print("Enter a search item:")

    def searchNote(self, keyword="SEARCHBOOKNOTE"):
        try:
            print(self.divider)
            self.printSearchEntryPrompt()
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                userInput = prompt(self.inputIndicator).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if userInput == self.cancelCommand:
                return self.cancelAction()
            command = f"{keyword}:::{userInput}"
            self.printRunningCommand(command)
            return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def changebiblesearchmode(self):
        try:
            print(self.divider)
            searchModes = ("SEARCH", "SEARCHALL", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
            searchModesDisplay = [f"[<ref>{i}</ref> ] {mode}" for i, mode in enumerate(searchModes)]
            searchModesDisplay = "<br>".join(searchModesDisplay)
            searchModesDisplay = f"<h2>Change default bible search mode<h2>{searchModesDisplay}"
            print(searchModesDisplay)
            print(self.divider)
            print("Enter a number:")
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit import prompt
                userInput = prompt(self.inputIndicator, default=str(config.bibleSearchMode)).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            # define key
            if userInput in ("0", "1", "2", "3", "4", "5"):
                return self.getContent(f"_setconfig:::bibleSearchMode:::{userInput}")
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def changenoteeditor(self):
        try:
            print(self.divider)
            print("Select default note / journal editor:")
            editors = {
                "nano": "nano --softwrap --atblanks",
                "vi": "vi",
                "vim": "vim",
            }
            configurablesettings = list(editors.keys())
            print(configurablesettings)
            print(self.divider)
            print("Enter your favourite text editor:")
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit.completion import WordCompleter
                from prompt_toolkit import prompt
                completer = WordCompleter(configurablesettings)
                userInput = prompt(self.inputIndicator, completer=completer).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            # define key
            if userInput in configurablesettings:
                #config.terminalNoteEditor = editors[userInput]
                return self.getContent(f"_setconfig:::terminalNoteEditor:::'{editors[userInput]}'")
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def fingerprint(self):
        try:
            output = json.loads(self.getCliOutput("termux-fingerprint"))
            return True if output["auth_result"] == "AUTH_RESULT_SUCCESS" else False
        except:
            return False

    def printTermuxApiDisabled(self):
        print("Termux API is not yet enabled!")
        print("This feature is available on Android ONLY!")
        print("Make sure both Termux:API app and termux-api package are installed first.")
        print("Then, run '.config' and set 'terminalEnableTermuxAPI' to True.")

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
                print(f"Backup file '{filepath}.bak' does not exist!")
                return self.cancelAction()
        else:
            self.printTermuxApiDisabled()
        return ""

    def changeconfig(self):
        if config.terminalEnableTermuxAPI:
            if not self.fingerprint():
                return self.cancelAction()
        try:
            print(self.divider)
            print("Caution! Editing 'config.py' incorrectly may stop UBA from working.")
            print(self.getContent("_setconfig:::"))
            print(self.divider)
            print("Enter the item you want to change:")
            configurablesettings = list(config.help.keys())
            if config.isPrompt_toolkitInstalled:
                from prompt_toolkit.completion import WordCompleter
                completer = WordCompleter(configurablesettings, ignore_case=True)
                userInput = self.terminal_config_selection_session.prompt(self.inputIndicator, completer=completer).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == self.cancelCommand:
                return self.cancelAction()
            # define key
            if userInput in configurablesettings:
                value = userInput
                print(self.divider)
                print(self.getContent(f"_setconfig:::{value}"))
                print(self.divider)
                print("Enter a value:")
                if config.isPrompt_toolkitInstalled:
                    from prompt_toolkit import prompt
                    userInput = prompt(self.inputIndicator).strip()
                else:
                    userInput = input(self.inputIndicator).strip()
                if not userInput or userInput == self.cancelCommand:
                    return self.cancelAction()
                print(self.getContent(f"_setconfig:::{value}:::{userInput}"))
                return ".restart"
            else:
                return self.printInvalidOptionEntered()
        except:
            return self.printInvalidOptionEntered()

    def editConfig(self, editor):
        print(self.divider)
        print("Caution! Editing 'config.py' incorrectly may stop UBA from working.")
        print("Do you want to proceed? [Y]es / [N]o")
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt
            userInput = prompt(self.inputIndicator, default="N").strip()
        else:
            userInput = input(self.inputIndicator).strip()
        userInput = userInput.lower()
        if userInput in ("n", "no"):
            return self.cancelAction()
        elif userInput in ("y", "yes"):
            print("reading config content ...")
            if os.path.isfile("config.py"):
                with open("config.py", "r", encoding="utf-8") as input_file:
                    content = input_file.read()
                print("config is ready for editing ...")
                print("To apply changes, save as 'config.py' and replace the existing 'config.py' when you finish editing.")
            self.texteditor(editor, content)
            config.saveConfigOnExit = False
            print(self.divider)
            print("Restarting ...")
            return ".restart"

    # text editor
    def cliTool(self, tool, content=""):
        if WebtopUtil.isPackageInstalled(tool):
            pydoc.pipepager(content, cmd=tool)
            if WebtopUtil.isPackageInstalled("pkill"):
                tool = tool.strip().split(" ")[0]
                os.system(f"pkill {tool}")
        else:
            self.printToolNotFound(tool)
        return ""

    # text editor
    def texteditor(self, editor, content=""):
        if WebtopUtil.isPackageInstalled(editor):
            pydoc.pipepager(content, cmd=f"{editor} -")
            if WebtopUtil.isPackageInstalled("pkill"):
                editor = editor.strip().split(" ")[0]
                os.system(f"pkill {editor}")
        else:
            self.printToolNotFound(editor)
        return ""

    def openNoteEditor(self, noteType, b=None, c=None, v=None, year=None, month=None, day=None, editor=None):
        if editor is None:
            editor = config.terminalNoteEditor # default: vi
        if WebtopUtil.isPackageInstalled(editor.split(" ")[0]):
            noteDB = JournalSqlite() if noteType == "journal" else NoteSqlite()
            if noteType == "journal":
                note = noteDB.getJournalNote(year, month, day)
            elif noteType == "book":
                note = noteDB.getBookNote(b)[0]
            elif noteType == "chapter":
                note = noteDB.getChapterNote(b, c)[0]
            elif noteType == "verse":
                note = noteDB.getVerseNote(b, c, v)[0]
            if config.isMarkdownifyInstalled:
                # convert html into markdown
                from markdownify import markdownify
                note = markdownify(note, heading_style=config.markdownifyHeadingStyle)
                note = note.replace("\n\np, li { white-space: pre-wrap; }\n", "")
                note = note.replace("hr { height: 1px; border-width: 0; }\n", "")
            else:
                note = self.getPlainText(note)
            # display in editor
            print("Opening text editor ...")
            print("When you finish editing, save content in a file and enter 'note' as its filename.")
            self.texteditor(editor, note)
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
            self.printToolNotFound(editor)
            print("Install it first of run '.changenoteeditor' to change the default note editor.")
            return ""

    def saveNote(self, noteDB, noteType, b=None, c=None, v=None, year=None, month=None, day=None, note=""):
        note = TextUtil.fixNoteFont(note)
        if noteType == "book":
            #NoteService.saveBookNote(b, note)
            #noteDB = NoteSqlite()
            #noteDB.saveBookNote(b, note)
            noteDB.saveBookNote(b, note, DateUtil.epoch())
        elif noteType == "chapter":
            noteDB.saveChapterNote(b, c, note, DateUtil.epoch())
        elif noteType == "verse":
            noteDB.saveVerseNote(b, c, v, note, DateUtil.epoch())
        elif noteType == "journal":
            noteDB.saveJournalNote(year, month, day, note)
        print("Note saved!")

    # organise user interactive menu

    def displayFeatureMenu(self, heading, features):
        featureItems = [f"[<ref>{index}</ref> ] {self.dotCommands[item][0]}" for index, item in enumerate(features)]
        content = f"<h2>{heading}</h2>"
        content += "<br>".join(featureItems)
        print(self.divider)
        print(TextUtil.htmlToPlainText(content).strip())
        print(self.divider)
        self.printChooseItem()
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt
            userInput = prompt(self.inputIndicator).strip()
        else:
            userInput = input(self.inputIndicator).strip()
        if not userInput or userInput == self.cancelCommand:
            return self.cancelAction()
        try:
            command = features[int(userInput)]
            self.printRunningCommand(command)
            return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def menu(self):
        heading = "UBA Terminal Mode Menu"
        features = (".show", ".open", ".search", ".note", ".control", ".edit", ".change", ".maintain", ".help")
        return self.displayFeatureMenu(heading, features)

    def open(self):
        heading = "Open"
        features = (".openbible", ".openbookfeatures", ".openchapterfeatures", ".openversefeatures", ".opencommentary", ".openreferencebook", ".textract", ".w3m", ".lynx", ".web", ".tts")
        return self.displayFeatureMenu(heading, features)

    def control(self):
        heading = "Control"
        features = (".find", ".togglebiblecomparison", ".togglepager", ".togglebiblechapterformat", ".stopaudio", ".read", ".readsync", ".paste", ".forward", ".latestbible", ".backward", ".swap", ".share", ".copy", ".copyhtml")
        return self.displayFeatureMenu(heading, features)

    def clipboard(self):
        heading = "Copy & Copied Text"
        features = (".copy", ".copyhtml", ".run", ".ttscopiedtext", ".quicksearchcopiedtext")
        return self.displayFeatureMenu(heading, features)

    def search(self):
        heading = "Search"
        features = (".searchbible", ".searchpromises", ".searchparallels", ".searchnames", ".searchcharacters", ".searchlocations", ".searchtopics", ".searchreferencebooks", ".searchencyclopedia", ".searchdictionaries", ".searchthirdpartydictionaries", ".searchlexicons", ".searchlexiconsreversely", ".searchconcordance", ".quicksearch")
        return self.displayFeatureMenu(heading, features)

    def show(self):
        heading = "Show"
        features = (".latest", ".history", ".showbibles", ".showstrongbibles", ".showbiblebooks", ".showbibleabbreviations", ".showbiblechapters", ".showbibleverses", ".showcommentaries", ".showtopics", ".showlexicons", ".showencyclopedia", ".showdictionaries", ".showthirdpartydictionary", ".showreferencebooks", ".showdata", ".showttslanguages", ".commands", ".config")
        return self.displayFeatureMenu(heading, features)

    def edit(self):
        heading = "Edit"
        features = (".nano", ".nanonew", ".nanoconfig", ".vi", ".vinew", ".viconfig", ".vim", ".vimnew", ".vimconfig")
        return self.displayFeatureMenu(heading, features)

    def change(self):
        heading = "Change"
        features = (".changebiblesearchmode", ".changenoteeditor", ".changecolors", ".changeconfig")
        return self.displayFeatureMenu(heading, features)

    def help(self):
        heading = "Help"
        features = (".terminalcommands", ".standardcommands", ".whatis")
        return self.displayFeatureMenu(heading, features)

    def maintain(self):
        heading = "Maintain"
        features = [".update", ".showdownloads"]
        if config.terminalEnableTermuxAPI:
            features += [".backupnotes", ".backupjournals", ".restorenotes", ".restorejournals", ".restorelastnotes", ".restorelastjournals"]
        return self.displayFeatureMenu(heading, features)

    def openbookfeatures(self):
        heading = "Bible Book Featues"
        features = (".openintroduction", ".opendictionarybookentry", ".openencyclopediabookentry")
        return self.displayFeatureMenu(heading, features)

    def openchapterfeatures(self):
        heading = "Bible Chapter Featues"
        features = (".openoverview", ".opensummary", ".openchapterindex")
        return self.displayFeatureMenu(heading, features)

    def openversefeatures(self):
        heading = "Bible Verse Featues"
        features = (".opencrossreference", ".opentske", ".opencomparison", ".opendifference", ".opensmartindex", ".openwords", ".opendiscourse", ".opentranslation", ".opencombo")
        return self.displayFeatureMenu(heading, features)

    def accessNoteFeatures(self):
        heading = "Note / Journal Features"
        features = (".openbooknote", ".openchapternote", ".openversenote", ".openjournal", ".searchbooknote", ".searchchapternote", ".searchversenote", ".searchjournal", ".editbooknote", ".editchapternote", ".editversenote", ".editjournal", ".changenoteeditor")
        return self.displayFeatureMenu(heading, features)
