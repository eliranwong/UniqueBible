import re, config, pprint, os, requests, platform
from ast import literal_eval
from util.TextUtil import TextUtil
from util.RemoteCliMainWindow import RemoteCliMainWindow
from util.TextCommandParser import TextCommandParser
from util.CrossPlatform import CrossPlatform
from util.BibleBooks import BibleBooks
from util.GitHubRepoInfo import GitHubRepoInfo
from util.FileUtil import FileUtil
from util.UpdateUtil import UpdateUtil
from util.DateUtil import DateUtil
from db.BiblesSqlite import Bible


class LocalCliHandler:

    def __init__(self, command="John 3:16"):
        self.textCommandParser = TextCommandParser(RemoteCliMainWindow())
        self.crossPlatform = CrossPlatform()
        self.crossPlatform.setupResourceLists()
        self.html = "<ref >Unique Bible App</ref>"
        self.plainText = "Unique Bible App"
        self.command = command
        self.dotCommands = self.getDotCommands()
        self.initPromptElements()

    def initPromptElements(self):
        self.divider = "--------------------"
        self.inputIndicator = ">>> "
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import PromptSession
            from prompt_toolkit.history import FileHistory

            find_history = os.path.join("terminal_history", "find")
            module_history_bibles = os.path.join("terminal_history", "bibles")
            module_history_commentaries = os.path.join("terminal_history", "commentaries")
            search_bible_history = os.path.join("terminal_history", "search_bible")

            self.terminal_find_session = PromptSession(history=FileHistory(find_history))
            self.terminal_search_bible_session = PromptSession(history=FileHistory(search_bible_history))
            self.terminal_bible_selection_session = PromptSession(history=FileHistory(module_history_bibles))
            self.terminal_commentary_selection_session = PromptSession(history=FileHistory(module_history_commentaries))

    def getDotCommands(self):
        return {
            ".togglepager": ("toggle paging for text output", self.togglePager),
            ".stopaudio": ("stop audio playback", self.stopAudio),
            ".sa": ("an alias to the '.stopaudio' command", self.stopAudio),
            ".read": ("read available audio files", self.read),
            ".readsync": ("read available audio files with synchronised text display", self.readsync),
            ".paste": ("run clipboard text as command", self.paste),
            ".p": ("an alias to the '.paste' command", self.paste),
            ".forward": ("open one bible chapter forward", self.forward),
            ".backward": ("open one bible chapter backward", self.backward),
            ".f": ("an alias to the '.forward' command", self.forward),
            ".b": ("an alias to the '.backward' command", self.backward),
            ".swap": ("swap to a favourite bible", self.swap),
            ".s": ("an alias to the '.swap' command", self.swap),
            ".share": ("copy a web link for sharing", self.share),
            ".copy": ("copy the last opened content", self.copy),
            ".copyhtml": ("copy the last opened content in html format", self.copyHtml),
            ".find": ("find a string in the last opened content", self.find),
            ".history": ("display history records", self.history),
            ".last": ("display last selected items", self.last),
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
            ".showdownloads": ("display available downloads", self.showdownloads),
            ".changecolors": ("change text highlight colors", self.changecolors),
            ".openbible": ("open bible", self.openbible),
            ".opencommentary": ("open commentary", self.opencommentary),
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
            ".helpubacommands": ("display standard UBA command help menu", self.helpubacommands),
            ".helpterminalcommands": ("display terminal mode commands", self.helpterminalcommands),
            ".menu": ("display main menu", self.menu),
            ".open": ("display open menu", self.open),
            ".change": ("display change menu", self.change),
            ".search": ("display search menu", self.search),
            ".show": ("display show menu", self.show),
            ".maintain": ("display maintain menu", self.maintain),
            ".control": ("display control menu", self.control),
            ".help": ("display help menu", self.help),
            #".download": ("display download menu", self.download),
        }

    def execPythonFile(self, script):
        self.crossPlatform.execPythonFile(script)

    def getContent(self, command):
        command = command.strip()
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
                    self.printRunningCommand(command)
            except:
                pass
        # Redirection when certain commands are used.
        if re.search('^(map:::|bible:::mab:::|bible:::mib:::|bible:::mob:::|bible:::mpb:::|bible:::mtb:::)', command.lower()):
            return self.share(command)
        # Dot commands
        if command.startswith("."):
            return self.getDotCommandContent(command.lower())
        # Non-dot commands
        view, content, dict = self.textCommandParser.parser(command, "cli")
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
            if command.lower().startswith("study:::") or command.lower().startswith("studytext:::"):
                config.mainText = config.studyText
            config.mainB, config.mainC, config.mainV, *_ = references[-1]
        return plainText

    def displayOutputOnTerminal(self, content):
        divider = self.divider
        if config.enableTerminalPager and not content in ("Command processed!", "INVALID_COMMAND_ENTERED") and not content.endswith("not supported in terminal mode."):
            import pydoc
            if platform.system() == "Windows":
                # When you use remote powershell and want to pipe a command on the remote windows server through a pager, piping through  out-host -paging works as desired. Piping through more when running the remote command is of no use: the entire text is displayed at once.
                try:
                    pydoc.pipepager(content, cmd='out-host -paging')
                except:
                    try:
                        pydoc.pipepager(content, cmd='more')
                    except:
                        config.enableTerminalPager = False
                        print(divider)
                        print(content)
            else:
                try:
                    # paging without colours
                    #pydoc.pager(content)
                    # paging with colours
                    pydoc.pipepager(content, cmd='less -R')
                except:
                    config.enableTerminalPager = False
                    print(divider)
                    print(content)
        else:
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

    def getTextCommandSuggestion(self):
        # Text command autocompletion/autosuggest
        textCommands = [key + ":::" for key in self.textCommandParser.interpreters.keys()]
        bibleBooks = BibleBooks().getStandardBookAbbreviations()
        dotCommands = sorted(list(self.dotCommands.keys()))
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        return ['.quit', '.restart', 'quit', 'restart', bibleReference] + dotCommands + [cmd[1:] for cmd in dotCommands] + sorted(textCommands) + bibleBooks

    def togglePager(self):
        config.enableTerminalPager = not config.enableTerminalPager
        return self.plainText

    def helpubacommands(self):
        content = "UBA commands:"
        content += "\n".join([f"{key} - {self.dotCommands[key][0]}" for key in sorted(self.dotCommands.keys())])
        content += "\n".join([re.sub("            #", "#", value[-1]) for value in self.textCommandParser.interpreters.values()])
        return content

    def helpterminalcommands(self):
        content = "UBA terminal dot commands:"
        content += "\n".join([f"{key} - {self.dotCommands[key][0]}" for key in sorted(self.dotCommands.keys())])
        print(content)
        return ""

    def stopAudio(self):
        self.textCommandParser.parent.closeMediaPlayer()
        return ""

    def commands(self):
        #pprint.pprint(self.getTextCommandSuggestion())
        return pprint.pformat(self.getTextCommandSuggestion())

    def read(self):
        self.textCommandParser.parent.getPlaylistFromHTML(self.html)
        return ""

    def readsync(self):
        self.textCommandParser.parent.getPlaylistFromHTML(self.html, displayText=True)
        return ""

    def last(self):
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
            moduleList.append(f"[<ref>SEARCHTOOL:::{topic}:::</ref> ] {self.crossPlatform.topicList[index]}")
        content += "<br>".join(moduleList)
        return TextUtil.htmlToPlainText(content).strip()

    def showdictionaries(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["context1_dict"])
        moduleList = []
        for index, topic in enumerate(self.crossPlatform.dictionaryListAbb):
            moduleList.append(f"[<ref>SEARCHTOOL:::{topic}:::</ref> ] {self.crossPlatform.dictionaryList[index]}")
        content += "<br>".join(moduleList)
        return TextUtil.htmlToPlainText(content).strip()

    def showencyclopedia(self):
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["context1_encyclopedia"])
        moduleList = []
        for index, topic in enumerate(self.crossPlatform.encyclopediaListAbb):
            moduleList.append(f"[<ref>SEARCHTOOL:::{topic}:::</ref> ] {self.crossPlatform.encyclopediaList[index]}")
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
            bibleList.append(f"[<ref>TEXT:::{bible}</ref> ] {strongBiblesFullNameList[index]}")
        content += "<br>".join(bibleList)
        return TextUtil.htmlToPlainText(content).strip()

    def showthirdpartydictionary(self):
        modules = []
        for module in self.crossPlatform.thirdPartyDictionaryList:
            modules.append(f"[<ref>SEARCHTHIRDDICTIONARY:::{module}:::</ref> ]")
        content = "<br>".join(modules)
        return TextUtil.htmlToPlainText(content).strip()

    def showlexicons(self):
        modules = []
        for module in self.crossPlatform.lexiconList:
            modules.append(f"[<ref>SEARCHLEXICON:::{module}:::</ref> ]")
        content = "<br>".join(modules)
        return TextUtil.htmlToPlainText(content).strip()

    def showcommentaries(self):
        self.textCommandParser.parent.setupResourceLists()
        content = ""
        content += """<h2><ref onclick="window.parent.submitCommand('.commentarymenu')">{0}</ref></h2>""".format(config.thisTranslation["menu4_commentary"])
        content += "<br>".join(["""[<ref>{0}:::</ref> ] {1}""".format(abb, self.textCommandParser.parent.commentaryFullNameList[index]) for index, abb in enumerate(self.textCommandParser.parent.commentaryList)])
        return TextUtil.htmlToPlainText(content).strip()

    def showreferencebooks(self):
        self.textCommandParser.parent.setupResourceLists()
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_selectBook"])
        content += "<br>".join(["""[<ref>BOOK:::{0}</ref> ] {0}""".format(book) for book in self.textCommandParser.parent.referenceBookList])
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

    def paste(self):
        if config.isPyperclipInstalled:
            import pyperclip
            command = pyperclip.paste()
            print("Running clipboard text:")
            print(command)
            return self.getContent(command)
        return self.noClipboardUtility()

    def bible(self):
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        return self.getContent(f"BIBLE:::{config.mainText}:::{bibleReference}")

    def commentary(self):
        bibleReference = self.textCommandParser.bcvToVerseReference(config.commentaryB, config.commentaryC, config.commentaryV)
        return self.getContent(f"COMMENTARY:::{config.commentaryText}:::{bibleReference}")

    def share(self, command=""):
        if config.isPyperclipInstalled:
            import pyperclip
            weblink = TextUtil.getWeblink(command if command else self.command)
            pyperclip.copy(weblink)
            print(f"The following link is copied to clipboard:\n")
            print(weblink)
            print("\nPaste and open it in a web browser or share with others.")
            return ""
        return self.noClipboardUtility()

    def copy(self):
        if config.isPyperclipInstalled:
            import pyperclip
            plainText = TextUtil.htmlToPlainText(self.html, False).strip()
            pyperclip.copy(plainText)
            print("Content is copied to clipboard.")
            return ""
        return self.noClipboardUtility()

    def copyHtml(self):
        if config.isPyperclipInstalled:
            import pyperclip
            pyperclip.copy(self.html)
            print("HTML content is copied to clipboard.")
            return ""
        return self.noClipboardUtility()

    def noClipboardUtility(self):
        print("Clipboard utility 'pyperclip' is not installed.")
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
        if os.path.isfile("myhistory"):
            with open("myhistory", "r", encoding="utf-8") as input_file:
                text = input_file.read()
        print(text)
        return ""

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
            if not userInput or userInput == ".c":
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
                if not userInput or userInput == ".c":
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
                    if not userInput or userInput == ".c":
                        return self.cancelAction()
                    if int(userInput) in self.currentBibleVerses:
                        bibleVerse = userInput
                        command = f"{feature}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                        self.printRunningCommand(command)
                        return self.getContent(command)
                    else:
                        self.printInvalidOptionEntered()
            else:
                self.printInvalidOptionEntered()
        except:
            self.printInvalidOptionEntered()

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
            if not userInput or userInput == ".c":
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
                if not userInput or userInput == ".c":
                    return self.cancelAction()
                if int(userInput) in self.currentBibleChapters:
                    bibleChapter = userInput
                    command = f"{feature}:::{bibleAbb} {bibleChapter}"
                    self.printRunningCommand(command)
                    return self.getContent(command)
                else:
                    self.printInvalidOptionEntered()
            else:
                self.printInvalidOptionEntered()
        except:
            self.printInvalidOptionEntered()

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
            if not userInput or userInput == ".c":
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
                feature = features[feature]
                command = f"{feature}:::{bibleBook}"
                self.printRunningCommand(command)
                return self.getContent(command)
            else:
                self.printInvalidOptionEntered()
        except:
            self.printInvalidOptionEntered()

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
            if config.isPrompt_toolkitInstalled:
                completer = WordCompleter(self.crossPlatform.textList, ignore_case=True)
                defaultText = self.getDefaultText()
                userInput = self.terminal_bible_selection_session.prompt(self.inputIndicator, completer=completer, default=defaultText).strip()
            else:
                userInput = input(self.inputIndicator).strip()
            if not userInput or userInput == ".c":
                return self.cancelAction()
            if self.isValidBibles(userInput):
                bible = userInput
                firstBible = bible.split("_")[0]
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
                if not userInput or userInput == ".c":
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
                    if not userInput or userInput == ".c":
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
                        if not userInput or userInput == ".c":
                            return self.cancelAction()
                        if int(userInput) in self.currentBibleVerses:
                            bibleVerse = userInput
                            if "_" in bible:
                                command = f"COMPARE:::{bible}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                            else:
                                command = f"BIBLE:::{bible}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                            self.printRunningCommand(command)
                            return self.getContent(command)
                        else:
                            self.printInvalidOptionEntered()
                else:
                    self.printInvalidOptionEntered()
        except:
            self.printInvalidOptionEntered()

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
            if not userInput or userInput == ".c":
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
                if not userInput or userInput == ".c":
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
                    if not userInput or userInput == ".c":
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
                        if not userInput or userInput == ".c":
                            return self.cancelAction()
                        if int(userInput) in self.currentBibleVerses:
                            bibleVerse = userInput
                            command = f"COMMENTARY:::{module}:::{bibleAbb} {bibleChapter}:{bibleVerse}"
                            self.printRunningCommand(command)
                            return self.getContent(command)
                        else:
                            self.printInvalidOptionEntered()
                else:
                    self.printInvalidOptionEntered()
        except:
            self.printInvalidOptionEntered()

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
        if userInput == ".c":
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
            if userInput == ".c":
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

    # Shared prompt message

    def cancelAction(self):
        print("Action cancelled!")
        return ""

    def printChooseItem(self):
        print("Choose an item:")

    def printCancelOption(self):
        print("(Or enter '.c' to cancel)")

    def printInvalidOptionEntered(self):
        print("Invalid option entered!")
        return ""

    def printRunningCommand(self, command):
        print(f"Running {command} ...")

    def printEnterNumber(self, number):
        print(f"Enter a number [0 ... {number}]:")

    # organise use interactive menu

    def displayFeatureMenu(self, heading, features):
        featureItems = [f"[<ref>{index}</ref> ] {self.dotCommands[item][0]}" for index, item in enumerate(features)]
        content = f"<h2>{heading}</h2><p>"
        content += "<br>".join(featureItems)
        content += "</p>"
        print(self.divider)
        print(TextUtil.htmlToPlainText(content).strip())
        print(self.divider)
        self.printChooseItem()
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt
            userInput = prompt(self.inputIndicator).strip()
        else:
            userInput = input(self.inputIndicator).strip()
        if not userInput or userInput == ".c":
            return self.cancelAction()
        try:
            command = features[int(userInput)]
            self.printRunningCommand(command)
            return self.getContent(command)
        except:
            return self.printInvalidOptionEntered()

    def menu(self):
        heading = "UBA Terminal Mode Menu"
        features = (".open", ".show", ".search", ".control", ".change", ".maintain", ".help")
        return self.displayFeatureMenu(heading, features)

    def open(self):
        heading = "Open"
        features = (".openbible", ".opencommentary", ".openbookfeatures", ".openchapterfeatures", ".openversefeatures")
        return self.displayFeatureMenu(heading, features)

    def control(self):
        heading = "Control"
        features = (".find", ".togglepager", ".stopaudio", ".read", ".readsync", ".paste", ".forward", ".backward", ".swap", ".share", ".copy", ".copyhtml")
        return self.displayFeatureMenu(heading, features)

    def search(self):
        print("user interactive search menu is in progress ...")
        return ""
        #heading = "Search"
        #features = ("",)
        #return self.displayFeatureMenu(heading, features)

    def show(self):
        heading = "Show"
        features = (".last", ".history", ".showbibles", ".showstrongbibles", ".showbiblebooks", ".showbibleabbreviations", ".showbiblechapters", ".showbibleverses", ".showcommentaries", ".showtopics", ".showlexicons", ".showencyclopedia", ".showdictionaries", ".showthirdpartydictionary", ".showreferencebooks", ".showdata", ".commands", ".config")
        return self.displayFeatureMenu(heading, features)

    def change(self):
        heading = "Change"
        features = (".changecolors",)
        return self.displayFeatureMenu(heading, features)

    def help(self):
        heading = "Help"
        features = (".helpterminalcommands", ".helpubacommands",)
        return self.displayFeatureMenu(heading, features)

    def maintain(self):
        heading = "Maintain"
        features = (".update", ".showdownloads",)
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
