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
        self.dotCommands = {
            ".help": ("display help menu", self.help),
            ".togglepager": ("toggle paging for text output", self.togglePager),
            ".stopaudio": ("stop audio playback", self.stopAudio),
            ".sa": ("an alias to the '.stopaudio' command", self.stopAudio),
            ".commands": ("display available commands", self.commands),
            ".dotcommands": ("display available dot commands", self.dotCommandsHelp),
            ".read": ("read available audio files", self.read),
            ".readsync": ("read available audio files with synchronised text display", self.readsync),
            ".last": ("display last selected items", self.last),
            ".paste": ("run clipboard text as command", self.paste),
            ".p": ("an alias to the '.paste' command", self.paste),
            ".forward": ("open one bible chapter forward", self.forward),
            ".backward": ("open one bible chapter backward", self.backward),
            ".f": ("an alias to the '.forward' command", self.forward),
            ".b": ("an alias to the '.backward' command", self.backward),
            ".share": ("copy a web link for sharing", self.share),
            ".copy": ("copy the last opened content", self.copy),
            ".copyhtml": ("copy the last opened content in html format", self.copyHtml),
            ".find": ("find a string in the last opened content", self.find),
            ".history": ("display history records", self.history),
            ".update": ("update Unique Bible App to the latest version", self.update),
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
            ".changecolors": ("display available downloads", self.changecolors),
            #".openbookfeatures": ("open book features", self.openBookFeatures),
            #".openchapterfeatures": ("open chapter features", self.openChapterFeatures),
            #".openversefeatures": ("open verse features", self.openVerseFeatures),
            #".menu": ("display main menu", self.menu),
            #".open": ("display open menu", self.open),
            #".change": ("display change menu", self.change),
            #".show": ("display show menu", self.show),
            #".download": ("display download menu", self.download),
            #".set": ("display set menu", self.set), # any or particular config
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
                    print(f"Running {command} ...")
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
        divider = "--------------------"
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

    def help(self):
        content = "UBA commands:"
        content += "\n".join([f"{key} - {self.dotCommands[key][0]}" for key in sorted(self.dotCommands.keys())])
        content += "\n".join([re.sub("            #", "#", value[-1]) for value in self.textCommandParser.interpreters.values()])
        return content

    def dotCommandsHelp(self):
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
        print("Enter an UBA command ('.help' for help):")
        return ""

    def showbibleabbreviations(self):
        bible = Bible(config.mainText)
        bibleBooks = BibleBooks()
        print([f"[{b}] {bibleBooks.getStandardBookAbbreviation(b)}" for b in bible.getBookList()])
        return ""

    def showbiblebooks(self):
        bible = Bible(config.mainText)
        bibleBooks = BibleBooks()
        print([f"[{b}] {bibleBooks.getStandardBookFullName(b)}" for b in bible.getBookList()])
        return ""

    def showbiblechapters(self):
        bible = Bible(config.mainText)
        print(bible.getChapterList(config.mainB))
        return ""

    def showbibleverses(self):
        bible = Bible(config.mainText)
        print(bible.getVerseList(config.mainB, config.mainV))
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
            bibleList.append(f"[<ref>TEXT:::{bible}</ref> ] {self.crossPlatform.textFullNameList[index]}")
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
        content += "<br>".join(["""[<ref>COMMENTARY:::{0}:::</ref> ] {1}""".format(abb, self.textCommandParser.parent.commentaryFullNameList[index]) for index, abb in enumerate(self.textCommandParser.parent.commentaryList)])
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
        searchInput = input("Enter a search pattern: ").strip()
        if config.isColoramaInstalled:
            from colorama import init
            init()
            from colorama import Fore, Back, Style
            content = re.sub(r"({0})".format(searchInput), r"{0}{1}\1{2}".format(Back.RED, Fore.WHITE, Style.RESET_ALL), self.plainText)
        else:
            content = re.sub(r"({0})".format(searchInput), r"[[[ \1 ]]]", self.plainText)
        return content

    def history(self):
        if os.path.isfile("myhistory"):
            with open("myhistory", "r", encoding="utf-8") as input_file:
                text = input_file.read()
        print(text)
        return ""

    def openBookFeatures(self):
        pass

    def openChapterFeatures(self):
        pass

    def openVerseFeatures(self):
        pass

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
        print(f"Running {command} ...")
        return self.getContent(command)

    def forward(self):
        newChapter = config.mainC
        if config.mainC < BibleBooks.getLastChapter(config.mainB):
            newChapter += 1
        command = self.textCommandParser.bcvToVerseReference(config.mainB, newChapter, 1)
        print(f"Running {command} ...")
        return self.getContent(command)

    def noPromptToolkit(self):
        print("Install package 'prompt_toolkit' first!")
        return ""

    def changecolors(self):
        if config.isPrompt_toolkitInstalled:
            from prompt_toolkit import prompt

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
            print("Choose an item you want to change:")
            print(pprint.pformat(options))
            text = prompt(f"Enter a number [0 ... {(len(options) - 1)}] or '.c' to cancel: ")
            if text == ".c":
                print("Action cancelled!")
                return ""
            try:
                optionIndex = int(text.strip())
                option = options[optionIndex]
                option = re.sub("^\[[0-9]+?\] ", "", option)
                configitem = optionMap[option]
                options = [f"[{i}] {item}" for i, item in enumerate(config.terminalColors)]
                print("Choose a color:")
                print(options)
                text = prompt(f"Enter a number [0 ... {(len(options) - 1)}] or '.c' to cancel: ")
                if text == ".c":
                    print("Action cancelled!")
                    return ""
                else:
                    color = config.terminalColors[int(text)]
                    command = f"_setconfig:::{configitem}:::'{color}'"
                    print(f"Running {command} ...")
                    return self.getContent(command)
            except:
                print("Invalid option entered!")
                return ""
        else:
            return self.noPromptToolkit()
