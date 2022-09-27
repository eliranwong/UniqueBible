from genericpath import isfile
import re, config, pprint, os
import urllib.parse
from util.TextUtil import TextUtil
from util.RemoteCliMainWindow import RemoteCliMainWindow
from util.TextCommandParser import TextCommandParser
from util.CrossPlatform import CrossPlatform
from util.BibleBooks import BibleBooks
from util.GitHubRepoInfo import GitHubRepoInfo
from util.FileUtil import FileUtil
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
            ".commands": ("display available commands", self.commands),
            ".dotcommands": ("display available dot commands", self.dotCommandsHelp),
            ".bible": ("open the last opened bible passage", self.bible),
            ".bibles": ("display installed bibles", self.bibles),
            ".read": ("read available audio files", self.read),
            ".last": ("display last selected items", self.last),
            ".books": ("display bible book list", self.books),
            ".booknames": ("display bible book name list", self.booknames),
            ".chapters": ("display bible chapter list", self.chapters),
            ".verses": ("display bible verse list", self.verses),
            ".download": ("display available downloads", self.download),
            ".data": ("display installed data", self.data),
            ".commentary": ("open the last opened commentary", self.commentary),
            ".commentaries": ("display installed commentaries", self.commentaries),
            ".referencebooks": ("display installed reference books", self.referencebooks),
            ".paste": ("run clipboard text as command", self.paste),
            ".share": ("copy a web link for sharing", self.share),
            ".copy": ("copy the last opened content", self.copy),
            ".copyhtml": ("copy the last opened content in html format", self.copyHtml),
            ".find": ("find a string in the last opened content", self.find),
            #".openbookfeatures": ("open book features", self.openBookFeatures),
            #".openchapterfeatures": ("open chapter features", self.openChapterFeatures),
            #".openversefeatures": ("open verse features", self.openVerseFeatures),
            ".history": ("display history records", self.history),
        }

    def execPythonFile(self, script):
        self.crossPlatform.execPythonFile(script)

    def getContent(self, command):
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
            self.crossPlatform.addHistoryRecord(view, command)
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

    def getDotCommandContent(self, command):
        if command in self.dotCommands:
            return self.dotCommands[command][-1]()
        elif command == ".quit":
            print("Closing ...")
            return ""
        elif command == ".restart":
            print("Restarting ...")
            return ""
        return f"Command not found: {command}"

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
        playlist = self.textCommandParser.parent.getPlaylistFromHTML(self.html)
        self.textCommandParser.parent.playAudioBibleFilePlayList(playlist)
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

    def initialDisplay(self):
        print("--------------------")
        bibleReference = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        print("BIBLE:::{0}:::{1} [{2}.{3}.{4}]".format(config.mainText, bibleReference, config.mainB, config.mainC, config.mainV))
        print("Enter an UBA command ('.help' for help):")
        return ""

    def books(self):
        bible = Bible(config.mainText)
        bibleBooks = BibleBooks()
        print([f"[{b}] {bibleBooks.getStandardBookAbbreviation(b)}" for b in bible.getBookList()])
        return ""

    def booknames(self):
        bible = Bible(config.mainText)
        bibleBooks = BibleBooks()
        print([f"[{b}] {bibleBooks.getStandardBookFullName(b)}" for b in bible.getBookList()])
        return ""

    def chapters(self):
        bible = Bible(config.mainText)
        print(bible.getChapterList(config.mainB))
        return ""

    def verses(self):
        bible = Bible(config.mainText)
        print(bible.getVerseList(config.mainB, config.mainV))
        return ""

    def bibles(self):
        return TextUtil.htmlToPlainText(self.getBiblesContent()).strip()

    def getBiblesContent(self):
        #return pprint.pformat(dict(zip(self.crossPlatform.textList, self.crossPlatform.textFullNameList)))
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_bible"])
        bibleList = []
        for index, bible in enumerate(self.crossPlatform.textList):
            bibleList.append(f"[<ref>TEXT:::{bible}</ref> ] {self.crossPlatform.textFullNameList[index]}")
        content += "<br>".join(bibleList)
        return content

    def commentaries(self):
        return TextUtil.htmlToPlainText(self.getCommentariesContent()).strip()

    def getCommentariesContent(self):
        self.textCommandParser.parent.setupResourceLists()
        content = ""
        content += """<h2><ref onclick="window.parent.submitCommand('.commentarymenu')">{0}</ref></h2>""".format(config.thisTranslation["menu4_commentary"])
        content += "<br>".join(["""[<ref>COMMENTARY:::{0}:::</ref> ] {1}""".format(abb, self.textCommandParser.parent.commentaryFullNameList[index]) for index, abb in enumerate(self.textCommandParser.parent.commentaryList)])
        return content

    def referencebooks(self):
        return TextUtil.htmlToPlainText(self.getReferencebooksContent()).strip()

    def getReferencebooksContent(self):
        self.textCommandParser.parent.setupResourceLists()
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_selectBook"])
        content += "<br>".join(["""[<ref>BOOK:::{0}</ref> ] {0}""".format(book) for book in self.textCommandParser.parent.referenceBookList])
        return content

    def data(self):
        return TextUtil.htmlToPlainText(self.getDataContent()).strip()

    def getDataContent(self):
        self.textCommandParser.parent.setupResourceLists()
        content = ""
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu_data"])
        dataList = [item for item in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "menu", "Bible Data"), "txt")]
        content += "<br>".join(["""[<ref>DATA:::{0}</ref> ] {0}""".format(book)
            for book in dataList])
        return content

    def download(self):
        return TextUtil.htmlToPlainText(self.getDownloadContent()).strip()

    def getDownloadContent(self):
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
        return content

    def paste(self):
        if config.isPyperclipInstalled:
            import pyperclip
            command = pyperclip.paste()
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
