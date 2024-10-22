# https://docs.python.org/3/library/http.server.html
# https://ironpython-test.readthedocs.io/en/latest/library/simplehttpserver.html
import hashlib
import json
import logging
import os, re, pprint, glob
from uniquebible import config
import subprocess
import urllib
from http import HTTPStatus

import requests
from http.server import SimpleHTTPRequestHandler
from time import gmtime
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.db.BiblesSqlite import BiblesSqlite, Bible
from uniquebible.util.GitHubRepoInfo import GitHubRepoInfo
from uniquebible.util.TextCommandParser import TextCommandParser
from uniquebible.util.RemoteCliMainWindow import RemoteCliMainWindow
from urllib.parse import urlparse, parse_qs
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.LanguageUtil import LanguageUtil
from pathlib import Path
from uniquebible.util.HtmlGeneratorUtil import HtmlGeneratorUtil


class UBAHTTPRequestHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        self.send_error(
            HTTPStatus.NOT_FOUND,
            "Not found")
        return None

class RemoteHttpHandler(UBAHTTPRequestHandler):

    parser = None
    textCommandParser = None
    bibles = None
    books = None
    bookMap = None
    abbreviations = None
    session = None
    users = []
    adminUsers = []
    whiteListFile = "ip_whitelist.txt"
    whiteListIPs = []
    blackListFile = "ip_blacklist.txt"
    blackListIPs = []

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('uba')
        if RemoteHttpHandler.textCommandParser is None:
            RemoteHttpHandler.textCommandParser = TextCommandParser(RemoteCliMainWindow())
        self.textCommandParser = RemoteHttpHandler.textCommandParser
        config.internet = True
        config.mainWindow = self
        self.runStartupPlugins()
        if RemoteHttpHandler.bibles is None:
            RemoteHttpHandler.bibles = [(bible, bible) for bible in BiblesSqlite().getBibleList()]
        self.bibles = RemoteHttpHandler.bibles
        if RemoteHttpHandler.parser is None:
            RemoteHttpHandler.parser = BibleVerseParser(config.parserStandarisation)
        self.parser = RemoteHttpHandler.parser
        if RemoteHttpHandler.abbreviations is None:
            RemoteHttpHandler.abbreviations = self.parser.standardAbbreviation
        self.abbreviations = RemoteHttpHandler.abbreviations
        if RemoteHttpHandler.books is None:
            RemoteHttpHandler.books = [(k, v) for k, v in self.abbreviations.items() if int(k) <= 69]
            RemoteHttpHandler.bookMap = {k: v for k, v in self.abbreviations.items() if int(k) <= 69}
        self.books = RemoteHttpHandler.books
        self.bookMap = RemoteHttpHandler.bookMap
        self.users = RemoteHttpHandler.users
        self.adminUsers = RemoteHttpHandler.adminUsers
        self.primaryUser = False
        if config.httpServerViewerGlobalMode:
            try:
                urllib.request.urlopen(config.httpServerViewerBaseUrl)
            except:
                config.httpServerViewerGlobalMode = False
        if not hasattr(config, "setMainVerse"):
            config.setMainVerse = False
        try:
            if os.path.exists(self.whiteListFile):
                self.whiteListIPs = [ip.strip() for ip in open(self.whiteListFile, "r").readlines()]
            else:
                Path(self.whiteListFile).touch()
            if os.path.exists(self.blackListFile):
                self.blackListIPs = [ip.strip() for ip in open(self.blackListFile, "r").readlines()]
        except Exception as ex:
            print("Could not read white/blacklists")
            print(ex)
        try:
            super().__init__(*args, directory="htmlResources", **kwargs)
        except Exception as ex:
            print("Could not run init")
            print(ex)

    def getCommands(self):
        return {
            ".myqrcode": self.getQrCodeCommand,
            #".bible": self.getCurrentReference,
        }

    def setMainVerse(self):
        if not hasattr(config, "mainVerseData"):
            config.mainVerseData = {}
        if config.webHomePage == "{0}.html".format(config.webPrivateHomePage):
            privateKey = "{0}_private".format(self.session)
            config.mainVerseData[privateKey] = self.getConfigMainVerse() if privateKey in config.mainVerseData else self.getDefaultMainVerse()
        else:
            config.mainVerseData[self.session] = self.getConfigMainVerse() if self.session in config.mainVerseData else self.getDefaultMainVerse()

    def getConfigMainVerse(self):
        return {
            "text": config.mainText,
            "bAbb": self.abbreviations[str(config.mainB)],
            "bFullEnglishName": BibleBooks.abbrev["eng"][str(config.mainB)][-1],
            "b": config.mainB,
            "c": config.mainC,
            "v": config.mainV,
            "reference": self.getCurrentReference(),
            "commentary": config.commentaryText,
        }

    def getDefaultMainVerse(self):
        return {
            "text": "KJV",
            "bAbb": "John",
            "bFullEnglishName": "John",
            "b": 43,
            "c": 3,
            "v": 16,
            "reference": "John 3:16",
            "commentary": "CBSC",
        }

    def getMainVerse(self):
        if config.webHomePage == "{0}.html".format(config.webPrivateHomePage):
            privateKey = "{0}_private".format(self.session)
            if not hasattr(config, "mainVerseData") or not privateKey in config.mainVerseData:
                self.setMainVerse()
            return config.mainVerseData[privateKey]
        else:
            if not hasattr(config, "mainVerseData") or not self.session in config.mainVerseData:
                self.setMainVerse()
            return config.mainVerseData[self.session]

    def refineCommand(self, command, mainVerse):
        try:
            # match a bible version
            if command in self.textCommandParser.parent.textList:
                command = f"TEXT:::{command}"
            # match a bible reference, started with book number, e.g. 43.3.16
            elif re.search("^[0-9]+?\.[0-9]+?\.[0-9]+?$", command):
                b, c, v = [int(i) for i in command.split(".")]
                command = self.textCommandParser.bcvToVerseReference(b, c, v)
            else:
                # match a bible reference
                bc = command.split(":", 1)
                bci = [int(i) for i in bc if i]
                if len(bc) == 2 and len(bci) == 1:
                    # Users specify a verse number, e.g. :16
                    if command.startswith(":"):
                        command = self.textCommandParser.bcvToVerseReference(mainVerse["b"], mainVerse["c"], bci[0])
                    # Users specify a chapter number, e.g. 3:
                    elif command.endswith(":"):
                        command = self.textCommandParser.bcvToVerseReference(mainVerse["b"], bci[0], 1)
                # Users specify both a chapter number and a verse number, e.g. 3:16
                elif len(bc) == 2 and len(bci) == 2:
                    command = self.textCommandParser.bcvToVerseReference(mainVerse["b"], bci[0], bci[1])
        except:
            pass
        return command

    def getShortcuts(self):
        mainVerse = self.getMainVerse() # e.g. {'text': 'KJV', 'bAbb': 'John', 'bFullEnglishName': 'John', 'b': 43, 'c': 3, 'v': 16, 'reference': 'John 3:16', 'commentary': 'BI'}
        self.command = self.refineCommand(self.command, mainVerse)
        return {
            ".chapters": "_chapters:::{0}".format(mainVerse["text"]),
            ".bible": "BIBLE:::{0}:::{1}".format(mainVerse["text"], mainVerse["reference"]),
            ".mob": "BIBLE:::MOB:::{0}".format(mainVerse["reference"]),
            ".mib": "BIBLE:::MIB:::{0}".format(mainVerse["reference"]),
            ".mtb": "BIBLE:::MTB:::{0}".format(mainVerse["reference"]),
            ".mpb": "BIBLE:::MPB:::{0}".format(mainVerse["reference"]),
            ".mab": "BIBLE:::MAB:::{0}".format(mainVerse["reference"]),
            ".compare": "compare:::{0}".format(mainVerse["reference"]),
            ".crossreference": "crossreference:::{0}".format(mainVerse["reference"]),
            ".tske": "tske:::{0}".format(mainVerse["reference"]),
            ".translation": "translation:::{0}".format(mainVerse["reference"]),
            ".discourse": "discourse:::{0}".format(mainVerse["reference"]),
            ".words": "words:::{0}".format(mainVerse["reference"]),
            ".combo": "combo:::{0}".format(mainVerse["reference"]),
            ".commentary": "commentary:::{0}:::{1}".format(mainVerse["commentary"], mainVerse["reference"]),
            ".index": "index:::{0}".format(mainVerse["reference"]),
            ".commentarymenu": "_commentarychapters:::{0}".format(mainVerse["commentary"]),
            ".introduction": "SEARCHBOOKCHAPTER:::Tidwell_The_Bible_Book_by_Book:::{0}".format(mainVerse["bFullEnglishName"]),
            ".timeline": "SEARCHBOOKCHAPTER:::Timelines:::{0}".format(mainVerse["bFullEnglishName"]),
            ".timelines": "SEARCHBOOKCHAPTER:::Timelines:::{0}".format(mainVerse["bFullEnglishName"]),
            ".overview": "overview:::{0} {1}".format(mainVerse["bAbb"], mainVerse["c"]),
            ".chapterindex": "chapterindex:::{0} {1}".format(mainVerse["bAbb"], mainVerse["c"]),
            ".summary": "summary:::{0} {1}".format(mainVerse["bAbb"], mainVerse["c"]),
            ".biblemenu": "_menu:::",
            ".comparison": "_comparison:::",
            ".timelinemenu": "BOOK:::Timelines",
            ".locations": "SEARCHTOOL:::EXLBL:::",
            ".characters": "SEARCHTOOL:::EXLBP:::",
            ".names": "SEARCHTOOL:::HBN:::",
            ".promises": "BOOK:::Bible_Promises",
            ".parallels": "BOOK:::Harmonies_and_Parallels",
            ".topics": "SEARCHTOOL:::EXLBT:::",
        }

    def getChapterFeatures(self):
        return {
            "OVERVIEW": config.thisTranslation["html_overview"],
            "CHAPTERINDEX": config.thisTranslation["html_chapterIndex"],
            "SUMMARY": config.thisTranslation["html_summary"],
        }

    def getVerseFeatures(self):
        return {
            "COMPARE": config.thisTranslation["menu4_compareAll"],
            "CROSSREFERENCE": config.thisTranslation["menu4_crossRef"],
            "TSKE": config.thisTranslation["menu4_tske"],
            "TRANSLATION": config.thisTranslation["menu4_traslations"],
            "DISCOURSE": config.thisTranslation["menu4_discourse"],
            "WORDS": config.thisTranslation["menu4_words"],
            "COMBO": config.thisTranslation["menu4_tdw"],
            "COMMENTARY": config.thisTranslation["menu4_commentary"],
            "INDEX": config.thisTranslation["menu4_indexes"],
        }

    def runStartupPlugins(self):
        config.bibleWindowContentTransformers = []
        config.customCommandShortcuts = {}
        if config.enablePlugins:
            for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "startup"), "py"):
                if not plugin in config.excludeStartupPlugins:
                    script = os.path.join(os.getcwd(), "plugins", "startup", "{0}.py".format(plugin))
                    config.mainWindow.execPythonFile(script)

    def execPythonFile(self, script):
        self.textCommandParser.parent.execPythonFile(script)

    def updateData(self):
        # Check language
        # Traditional Chinese
        if config.webPrivateHomePage and self.path.startswith("/{0}.html".format(config.webPrivateHomePage)):
            config.displayLanguage = "en_GB"
            config.standardAbbreviation = "ENG"
            config.webHomePage = "{0}.html".format(config.webPrivateHomePage)
            self.path = re.sub("^/{0}.html".format(config.webPrivateHomePage), "/index.html", self.path)
            #self.initialCommand = "BIBLE:::{0}:::John 3:16".format(self.getFavouriteBible())
        elif self.path.startswith("/traditional.html"):
            config.displayLanguage = "zh_HANT"
            config.standardAbbreviation = "TC"
            config.webHomePage = "traditional.html"
            self.path = re.sub("^/traditional.html", "/index.html", self.path)
            #self.initialCommand = "BIBLE:::{0}:::約翰福音 3:16".format(self.getFavouriteBible())
        # Simplified Chinese
        elif self.path.startswith("/simplified.html"):
            config.displayLanguage = "zh_HANS"
            config.standardAbbreviation = "SC"
            config.webHomePage = "simplified.html"
            self.path = re.sub("^/simplified.html", "/index.html", self.path)
            #self.initialCommand = "BIBLE:::{0}:::约翰福音 3:16".format(self.getFavouriteBible())
        # Default English
        else:
            config.displayLanguage = "en_GB"
            config.standardAbbreviation = "ENG"
            config.webHomePage = "index.html"
            #self.initialCommand = "BIBLE:::{0}:::John 3:16".format(self.getFavouriteBible())
        config.marvelData = config.marvelDataPrivate if config.webHomePage == "{0}.html".format(config.webPrivateHomePage) else config.marvelDataPublic
        self.textCommandParser.parent.setupResourceLists()
        config.thisTranslation = LanguageUtil.loadTranslation(config.displayLanguage)
        self.parser = BibleVerseParser(config.parserStandarisation)
        self.abbreviations = self.parser.standardAbbreviation
        if config.webPrivateHomePage:
            self.bibles = [(bible, bible) for bible in BiblesSqlite().getBibleList()]
        if not config.mainText in self.textCommandParser.parent.textList:
            config.mainText = self.getFavouriteBible()

    def ignoreCommand(self, path):
        ignoreCommands = [
            'robots.txt',
            'humans.txt',
            'ads.txt',
            'favicon.ico',
        ]
        for cmd in ignoreCommands:
            if cmd in path:
                return True
        if path.lower().startswith("/index.html?cmd=bible"):
            return False
        if len(path) > 255:
            return True
        return False

    def do_POST(self):
        self.handleBadRequests()

    def do_HEAD(self):
        self.handleBadRequests()

    def handleBadRequests(self):
        if config.enableHttpRemoteErrorRedirection:
            self.clientIP = self.client_address[0]
            if self.checkInWhitelist():
                self.blankPage()
                return
            self.addIpToBlackList(self.clientIP)
            self.redirectHeader()
        else:
            self.blankPage()

    def do_GET(self):
        try:
            self.clientIP = self.client_address[0]
            if config.enableHttpRemoteErrorRedirection and (not self.checkInWhitelist() and self.clientIP in self.blackListIPs):
                self.redirectHeader()
                return
            self.session = self.getSession()
            if self.session is None:
                print("No session")
                self.blankPage()
                return
            if self.clientIP not in self.users:
                self.users.append(self.clientIP)
            if self.clientIP == self.users[0]:
                self.primaryUser = True
            self.updateData()
            if self.ignoreCommand(self.path):
                print(f"Ignoring command: {self.path}")
                self.blankPage()
                return
            elif self.path == "" or self.path == "/" or self.path.startswith("/index.html") or config.displayLanguage != "en_GB":
                if self.primaryUser or not config.webPresentationMode:
                    query_components = parse_qs(urlparse(self.path).query)
                    if 'cmd' in query_components:
                        self.command = query_components["cmd"][0].strip()
                        self.command = self.command.replace("+", " ")
                        if self.command:
                            if self.command.lower().endswith("bible:::") and self.command.count(":::") >= 2:
                                commandSplit = self.command.split(":::")
                                text = commandSplit[1]
                                if not "_" in text and not text in self.textCommandParser.parent.textList:
                                    commandSplit[1] = self.getFavouriteBible()
                                    self.command = ":::".join(commandSplit)
                            self.loadContent()
                        else:
                            self.loadLastVerse()
                    else:
                        self.loadLastVerse()
                else:
                    # Web presentation mode is enabled and user is not the host.
                    self.mainPage()
            else:
                return super().do_GET()
        except Exception as ex:
            print(f"Exception: {ex}")
            if config.enableHttpRemoteErrorRedirection and self.checkAntiSpamBlacklist(self.clientIP):
                self.redirectHeader()
            else:
                self.blankPage()

    # If a 404 request, blacklist the IP
    def send_error(self, code, message=None, explain=None):
        if code == HTTPStatus.NOT_FOUND:
            if not self.checkInWhitelist():
                self.addIpToBlackList(self.clientIP)
        super().send_error(code, message, explain)

    def checkInWhitelist(self):
        for whitelistip in self.whiteListIPs:
            if self.clientIP.startswith(whitelistip):
                return True
        return False

    def checkAntiSpamBlacklist(self, clientIP):
        import pydnsbl
        ip_checker = pydnsbl.DNSBLIpChecker()
        result = ip_checker.check(clientIP)
        if result and result.blacklisted and not self.checkInWhitelist():
            self.addIpToBlackList(clientIP)
            return True
        return False

    def addIpToBlackList(self, clientIP):
        if clientIP not in self.blackListIPs:
            file = open(self.blackListFile, 'a')
            file.write(f"{clientIP}\n")
            file.close()

    def loadLastVerseHtml(self):
        return """<!DOCTYPE html><html><head><link rel="icon" href="icons/{0}"><title>{4}</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{3}.css?v=1.065'>
                <script src='js/http_server.js?v=1.065'></script>
                </head>
                <body>... {1} ...
                <script>
                location.assign("{2}?cmd=.bible");
                </script>
                </body>""".format(config.webUBAIcon, config.thisTranslation["loading"], config.webHomePage, config.theme, config.webSiteTitle)

    def loadLastVerse(self):
        self.commonHeader()
        self.wfile.write(bytes(self.loadLastVerseHtml(), "utf8"))

    def loadContent(self):
        infoDict = {}
        features = {
            "audio": self.audioContent,
            "play": self.playAudio,
            "config": self.configContent,
            "download": self.downloadContent,
            "history": self.historyContent,
            "import": self.importContent,
            "latest": self.latestContent,
            "layout": self.swapLayout,
            "library": self.libraryContent,
            "logout": self.logout,
            "search": self.searchContent,
            "maps": self.mapsContent,
            "days": self.dailyReadingContent,
            "theme": self.swapTheme,
            "globalviewer": self.toggleGlobalViewer,
            "presentationmode": self.togglePresentationMode,
            "increasefontsize": self.increaseFontSize,
            "decreasefontsize": self.decreaseFontSize,
            "caseSensitiveSearch": self.toggleCaseSensitiveSearch,
            "compareparallelmode": self.toggleCompareParallel,
            "subheadings": self.toggleSubheadings,
            "plainmode": self.togglePlainMode,
            "setfavouritebible": self.setFavouriteBibleContent,
            "setfavouritebible2": lambda: self.setFavouriteBibleContent("favouriteBible2"),
            "setfavouritebible3": lambda: self.setFavouriteBibleContent("favouriteBible3"),
            "setfavouritebibletc": lambda: self.setFavouriteBibleContent("favouriteBibleTC"),
            "setfavouritebibletc2": lambda: self.setFavouriteBibleContent("favouriteBibleTC2"),
            "setfavouritebibletc3": lambda: self.setFavouriteBibleContent("favouriteBibleTC3"),
            "setfavouritebiblesc": lambda: self.setFavouriteBibleContent("favouriteBibleSC"),
            "setfavouritebiblesc2": lambda: self.setFavouriteBibleContent("favouriteBibleSC2"),
            "setfavouritebiblesc3": lambda: self.setFavouriteBibleContent("favouriteBibleSC3"),
            "setfavouritebibleprivate": lambda: self.setFavouriteBibleContent("favouriteBiblePrivate"),
            "setfavouritebibleprivate2": lambda: self.setFavouriteBibleContent("favouriteBiblePrivate2"),
            "setfavouritebibleprivate3": lambda: self.setFavouriteBibleContent("favouriteBiblePrivate3"),
            "setversenosingleclickaction": self.setVerseNoClickActionContent,
            "setversenodoubleclickaction": lambda: self.setVerseNoClickActionContent(True),
            "setwebubaicon": self.setWebUBAIconContent,
            "wordaudiolinks": self.toggleWordAudioLinks,
        }
        functions = {
            "login": self.login,
        }
        adminCommands = ('.compareparallelmode',
                         '.config',
                         '.decreasefontsize',
                         '.download',
                         '.globalviewer',
                         '.history',
                         '.import',
                         '.increasefontsize',
                         '.layout',
                         '.logout',
                         '.plainmode',
                         '.presentationmode',
                         '.regexcasesensitive',
                         '.restart',
                         '.stop',
                         '.subheadings',
                         '.theme',
                         '.update',
                         '.setfavouritebible',
                         '.setfavouritebible2',
                         '.setfavouritebible3',
                         '.setfavouritebibletc',
                         '.setfavouritebibletc2',
                         '.setfavouritebibletc3',
                         '.setfavouritebiblesc',
                         '.setfavouritebiblesc2',
                         '.setfavouritebiblesc3',
                         '.setversenosingleclickaction',
                         '.setversenodoubleclickaction',
                         '.setwebubaicon',
                         '.wordaudiolinks',
                         )
        # Convert command shortcut
        commandFunction = ""
        commandParam = ""
        if self.command.startswith(".") and ":::" in self.command:
            commandFunction, commandParam = self.command.split(":::", 1)
            commandFunction = commandFunction.lower()
        shortcuts = self.getShortcuts()
        commands = self.getCommands()
        commandLower = self.command.lower()

        if re.search("^[Bb][Ii][Bb][Ll][Ee]:::[^:]+:::$", self.command):
            self.command = "{0}{1}".format(self.command, self.getMainVerse()["reference"])

        if not self.checkPermission()[0] and config.readFormattedBibles:
            checkOhgb = {
                "text:::ohgb": "TEXT:::MOB",
                "text:::ohgbi": "TEXT:::MIB",
            }
            if commandLower in checkOhgb.keys():
                self.command = checkOhgb[commandLower]
            elif commandLower.startswith("bible:::ohgb:::"):
                self.command = "BIBLE:::MOB:::{0}".format(self.command[15:])
            elif commandLower.startswith("bible:::ohgbi:::"):
                self.command = "BIBLE:::MIB:::{0}".format(self.command[16:])
        
        if commandLower in config.customCommandShortcuts.keys():
            self.command = config.customCommandShortcuts[commandLower]
        elif commandLower in shortcuts.keys():
            self.command = shortcuts[commandLower]
        elif commandLower in commands.keys():
            self.command = commands[commandLower]()
        #elif self.command.upper()[1:] in self.getVerseFeatures().keys():
            #self.command = "{0}:::{1}".format(self.command.upper()[1:], self.getCurrentReference())
        #elif self.command.upper()[1:] in self.getChapterFeatures().keys():
            #self.command = "{0}:::{1}".format(self.command.upper()[1:], self.getCurrentReference())
            #self.command = re.sub(":[0-9]+?$", "", self.command)
        # Parse command
        if commandLower in (".help", "?"):
            content = self.helpContent()
        elif commandLower in adminCommands:
            permission, message = self.checkPermission()
            if not permission:
                content = message
            elif commandLower == ".stop":
                self.closeWindow()
                config.enableHttpServer = False
                return
            elif commandLower == ".restart":
                return self.restartServer()
            elif commandLower == ".update":
                subprocess.Popen("git pull", shell=True)
                return self.restartServer("updated and ")
            else:
                content = features[commandLower[1:]]()
        elif commandLower.startswith(".") and commandLower[1:] in features.keys():
            content = features[commandLower[1:]]()
        elif commandFunction and commandFunction[1:] in functions.keys():
            content = functions[commandFunction[1:]](commandParam)
        else:
            tempDeveloper = False
            if self.clientIP in self.adminUsers and not config.developer:
                config.developer = True
                tempDeveloper = True
            try:
                view, content, infoDict = self.textCommandParser.parser(self.command, "http")
            except Exception as e:
                print(f"Exception: {e}")
                content = "Error!"
            if tempDeveloper:
                config.developer = False
            if content == "Downloaded!":
                content = self.downloadContent()
            elif not content:
                content = "No content for display!"
            elif not content in ("INVALID_COMMAND_ENTERED", "Error!", "No content for display!"):
                self.textCommandParser.parent.addHistoryRecord(view, self.command)

        if ('tab_title' in infoDict.keys() and infoDict['tab_title'] == "Map"):
            content = content.replace("<title>Google Maps - gmplot</title>", """<title>{2}</title>
                <script src='js/http_server.js?v=1.065'></script>
                <script>
                var target = document.querySelector('title');
                var observer = new MutationObserver(function(mutations) {0}
                    mutations.forEach(function(mutation) {0}
                        ubaCommandChanged(document.title);
                    {1});
                {1});
                var config = {0}
                    childList: true,
                {1};
                observer.observe(target, config);
                </script>""".format("{", "}", config.webSiteTitle))
            #print(content)
        else:
            content = self.wrapHtml(content)

        if config.bibleWindowContentTransformers:
            for transformer in config.bibleWindowContentTransformers:
                content = transformer(content)
        outputFile = os.path.join("htmlResources", "main-{0}.html".format(self.session))
        with open(outputFile, "w", encoding="utf-8") as fileObject:
            fileObject.write(content)
        #if config.httpServerViewerGlobalMode and config.webPresentationMode:
            #url = config.httpServerViewerBaseUrl + "/submit.php"
            #data = {"code": self.session, "content": content}
            #response = requests.post(url, data=json.dumps(data))
            # print("Submitted data to {0}: {1}".format(url, response))
        self.indexPage()

    def indexPage(self):
        self.commonHeader()
        bcv = (config.mainText, config.mainB, config.mainC, config.mainV)
        activeBCVsettings = """<script>
        var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};
        var tempActiveText = '{0}'; var tempB = {1}; var tempC = {2}; var tempV = {3};
        var toolB = {1}; var toolC = {2}; var toolV = {3};
        var changeVerse = 1;
        var activeBCV;
        </script>""".format(*bcv)
        #fontSize = "{0}px".format(config.fontSize)
        fontFamily = config.font
        collapseFooter = "document.getElementById('bibleFrame').contentWindow.document.getElementById('lastElement').style.height='5px'" if config.webCollapseFooterHeight else ""
        if config.setMainVerse:
            self.setMainVerse()
        html = """
            <html>
            <head>
                <link rel="icon" href="icons/{20}">
                <title>{21}</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />

                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{9}.css?v=1.065'>
                <style>
                ::-webkit-scrollbar {4}
                  display: none;
                {5}
                ::-webkit-scrollbar-button {4}
                  display: none;
                {5}
                body {4}
                  font-family:'{7}';
                  -ms-overflow-style:none;
                  padding: 0;
                  margin: 0;
                {5}

                .overlay {4}
                    height: 0%;
                    width: 100%;
                    position: fixed;
                    z-index: 1;
                    top: 0;
                    left: 0;
                    background-color: {13};
                    overflow-y: auto;
                    transition: 0.5s;
                {5}
                cat {4}
                    color: {14};
                {5}
                .overlay navItem {4}
                    padding: 8px;
                    text-decoration: none;
                    font-size: 36px;
                    color: {14};
                    transition: 0.3s;
                    display: inline-block;
                {5}
                .overlay navItem:hover, .overlay navItem:focus {4}
                    color: {15};
                    cursor: pointer;
                {5}

                .sidenav {4}
                  height: 100%;
                  width: 0;
                  position: fixed;
                  z-index: 1;
                  top: 0;
                  left: 0;
                  background-color: {13};
                  overflow-x: hidden;
                  transition: 0.5s;
                  padding-top: 60px;
                {5}

                .sidenav a {4}
                  padding: 8px 8px 8px 32px;
                  text-decoration: none;
                  font-size: 25px;
                  color: {14};
                  display: block;
                  transition: 0.3s;
                {5}
                
                .sidenav a:hover {4}
                  color: {15};
                {5}

                .sidenav .fullscreenbtn {4}
                  position: absolute;
                  top: 0;
                  right: 45px;
                  font-size: 30px;
                {5}

                #navBtns {4}
                  position: absolute;
                  top: 20;
                  left: 30px;
                {5}

                .sidenav .closebtn {4}
                  position: absolute;
                  top: 0;
                  right: 5px;
                  font-size: 35px;
                  margin-left: 50px;
                {5}
                
                @media screen and (max-height: 450px) {4}
                  .sidenav {4}padding-top: 15px;{5}
                  .sidenav a {4}font-size: 18px;{5}
                {5}
                table.layout, th.layout, td.layout {4}
                  padding: 0;
                  margin: 0;
                  border: none;
                {5}
                #commandForm {4}
                  margin-left: 5px;
                  margin-right: 5px;
                {5}
                #content {4}
                overflow: hidden;
                display: block;
                {5}
                #bibleDiv, #toolDiv {4}
                -webkit-overflow-scrolling: touch;
                overflow: hidden;
                {5}
                #bibleDiv {4}
                width: 100%;
                float: left;
                display: block;
                {5}
                #toolDiv {4}
                width: 0%;
                height: 0%;
                float: left;
                display: block;
                visibility: hidden;
                {5}
                iframe {4}
                /*height: calc(100% + 1px);*/
                height: {1}%;
                width: 100%;
                {5}
                zh {4} font-family:'{8}'; {5}
                {10}
                </style>
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/http_server.css?v=1.065'>
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.065'>
                <script src='js/common.js?v=1.065'></script>
                <script src='js/{9}.js?v=1.065'></script>
                <script src='w3.js?v=1.065'></script>
                <script src='js/http_server.js?v=1.065'></script>
                <script>
                var queryString = window.location.search;	
                queryString = queryString.substring(1);
                var curPos;
                var para = 2; var annoClause = 1; var annoPhrase = 1; var highlights = 1;
                var paraWin = 1; var syncBible = 1; var paraContent = ''; var triggerPara = 0;
                var currentZone; var currentBookName; var currentB; var currentC; var currentV;
                var fullScreen = 0; var toolDivLoaded = 0; var landscape;
                </script>
                {3}
                <script>
                var versionList = []; var compareList = []; var parallelList = []; 
                var diffList = []; var searchList = [];
                </script>

            </head>
            <body style="padding-top: 10px;" onload="onBodyLoad();{16}" ontouchstart="">
                <span id='v0.0.0'></span>
                <div style="padding-left: {17};">
                <div id="mySidenav" class="sidenav">
                    <a href="javascript:void(0)" class="closebtn" onclick="closeSideNav()">&times;</a>
                    <a href="javascript:void(0)" class="fullscreenbtn" onclick="fullScreenSwitch()">&varr;</a>
                    {12}
                </div>
                {18}
                {0}
                <table class='layout'>
                <tr style='height: 100%;'>
                <div id="content">
                    <div id="bibleDiv" onscroll="scrollBiblesIOS(this.id)">
                        <iframe id="bibleFrame" name="main-{2}" onload="resizeSite();{11}" width="100%" height="{1}%" src="main-{6}.html">Oops!</iframe>
                    </div>
                    <div id="toolDiv" onscroll="scrollBiblesIOS(this.id)">
                        <iframe id="toolFrame" name="tool-{2}" onload="resizeSite()" src="empty.html">Oops!</iframe>
                    </div>
                </div>
                </tr>

                <!-- The Modal - Message -->
                <div id="myModal2" class="modal2">
                  <!-- Modal content -->
                  <div class="modal2-content">
                    <div class="modal2-header">
                      <span class="close2">&times;</span>
                      <span id="myMessageHeader"><h2>{21}</h2></span>
                    </div>
                    <div class="modal2-body">
                      <span id="myMessage"><p>{21}</p></span>
                    </div>
                <!--
                    <div class="modal2-footer">
                      <span id="myMessageFooter"><h3>{21}</h3></span>
                    </div>
                -->
                  </div>
                </div>

                <script>
                if (getMobileOperatingSystem() == 'iOS') {4} 
                    enableIOSScrolling(); 
                {5}

                /* start - modal - message */
                // Get the modal  - message
                var modal2 = document.getElementById('myModal2');
                // Get the <span> element that closes the modal
                var span2 = document.getElementsByClassName("close2")[0];
                // When the user clicks on <span> (x), close the modal
                span2.onclick = function() {4}
                    modal2.style.display = "none";
                {5}
                // When the user clicks anywhere outside of the modal, close it
                window.onclick = function(event) {4}
                    if (event.target == modal2) {4}
                        modal2.style.display = "none";
                    {5}
                {5}
                /* end - modal - message */

                function keepTop() {4}
                    //window.scrollTo(0,0);
                    setTimeout(function(){4}window.scrollTo(0,0);{5}, 250);
                {5}
                window.onscroll = function() {4}keepTop(){5};
                window.onresize = function() {4}resizeSite(){5};

                function getCommandURL() {4}
                    var url;
                    cmd = encodeURI(document.getElementById('commandInput').value);
                    if (cmd == "") {4}
                        url = "{19}";
                    {5} else {4}
                        url = "{19}?cmd="+cmd;
                    {5}
                    url = url.replace(/ /g, "%20");
                    return url;
                {5}

                function openCommandInNewWindow() {4}
                    url = getCommandURL();
                    window.open(url, "_blank");
                {5}

                function shareInfo() {4}
                    document.getElementById('commandInput').value =  "_qrc:::" + document.getElementById('commandInputHolder').title;
                    document.getElementById("commandForm").submit();
                {5}

                // Open and close side navigation bar
                function openSideNav() {4}
                    document.getElementById("mySidenav").style.width = "250px";
                {5}
                function closeSideNav() {4}
                    document.getElementById("mySidenav").style.width = "0";
                {5}
                document.querySelector('#commandInput').addEventListener('click', closeSideNav);
                </script>
                </div>
            </body>
            </html>
        """.format(
            self.buildForm(),
            100,
            gmtime(),
            activeBCVsettings,
            "{",
            "}",
            self.session,
            fontFamily,
            config.fontChinese,
            config.theme,
            self.getHighlightCss(),
            collapseFooter,
            self.getSideNavContent(),
            "rgb(54, 53, 53)" if config.theme == "dark" else "rgb(247, 247, 247)",
            "#b6b4b4" if config.theme == "dark" else "rgb(70, 70, 70)",
            "#f1f1f1" if config.theme == "dark" else "rgb(5, 5, 5)",
            "adjustBibleDivWidth('{0}')".format(config.webDecreaseBibleDivWidth) if config.webDecreaseBibleDivWidth else "",
            config.webPaddingLeft,
            self.getBibleNavigationMenu(),
            config.webHomePage,
            config.webUBAIcon,
            config.webSiteTitle
        )
        self.wfile.write(bytes(html, "utf8"))

    def mainPage(self):
        self.commonHeader()
        html = open(os.path.join("htmlResources", "main-{0}.html".format(self.session)), 'r').read()
        self.wfile.write(bytes(html, "utf8"))

    def commonHeader(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("charset", "UTF-8")
        self.send_header("viewport", "width=device-width, initial-scale=1.0")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate"),
        self.send_header("Pragma", "no-cache"),
        self.send_header("Expires", "0")
        self.end_headers()

    def redirectHeader(self, redirectUrl="http://john316.com"):
        self.send_response(301)
        self.send_header("Expires", "0")
        self.send_header("Location", redirectUrl)
        self.end_headers()

    def blankPage(self):
        self.commonHeader()
        html = ""
        self.wfile.write(bytes(html, "utf8"))

    def getSideNavContent(self):
        mainVerse = self.getMainVerse()
        html = """<div id="navBtns">{0} {1} {2}</div>""".format(self.previousChapter(), self.chapterSelectionButton(), self.nextChapter())
        html += """<a href="#" onclick="submitCommand('.bible')">{0}</a>""".format(mainVerse["reference"])
        html += """<a href="#">{0}</a>""".format(self.verseActiionSelection())
        html += """<a href="#">{0}</a>""".format(self.bibleSelectionSide())
        sideNavItems = (
            (self.getFavouriteBible(), "BIBLE:::{0}:::{1}".format(self.getFavouriteBible(), mainVerse["reference"])),
            (self.getFavouriteBible2(), "BIBLE:::{0}:::{1}".format(self.getFavouriteBible2(), mainVerse["reference"])),
            (self.getFavouriteBible3(), "BIBLE:::{0}:::{1}".format(self.getFavouriteBible3(), mainVerse["reference"])),
        )
        for item in sideNavItems:
            html += """<a href="#" onclick="submitCommand('{1}')">{0}</a>""".format(*item)
        html += "<hr>"
        sideNavItems = (
            ("{0} &#x1F50E;&#xFE0E;".format(config.thisTranslation["menu5_bible"]), ".biblemenu"),
            (config.thisTranslation["html_showCompare"], ".comparison"),
            (config.thisTranslation["commentaries"], ".commentarymenu"),
            (config.thisTranslation["menu_library"], ".library"),
            (config.thisTranslation["html_timelines"], ".timelineMenu"),
            (config.thisTranslation["bibleAudio"], ".audio"),
            (config.thisTranslation["menu5_names"], ".names"),
            (config.thisTranslation["menu5_characters"], ".characters"),
            (config.thisTranslation["bibleMaps"], ".maps"),
            (config.thisTranslation["menu5_locations"], ".locations"),
            (config.thisTranslation["menu5_topics"], ".topics"),
            (config.thisTranslation["bibleHarmonies"], ".parallels"),
            (config.thisTranslation["biblePromises"], ".promises"),
            (config.thisTranslation["readingPlan"], ".days"),
            ("{0} &#x1F50E;&#xFE0E;".format(config.thisTranslation["menu_search"]), ".search"),
            (config.thisTranslation["download"], ".download"),
            (config.thisTranslation["ubaCommands"], ".help"),
        )
        for item in sideNavItems:
            html += """<a href="#" onclick="submitCommand('{1}')">{0}</a>""".format(*item)
        html += """<a href="{1}" target="_blank">{0}</a>""".format(config.thisTranslation["userManual"], self.getUserManual())
        html += "<hr>"
        html += """<a href="traditional.html">繁體中文</a>""" if config.webHomePage != "traditional.html" else ""
        html += """<a href="simplified.html">简体中文</a>""" if config.webHomePage != "simplified.html" else ""
        html += """<a href="index.html">English</a>""" if config.webHomePage != "index.html" else ""
        html += """<hr>{0}""".format(self.getOrganisationIcon())
        html += """<a href="https://github.com/eliranwong/UniqueBible" target="_blank"><img style="width:85px; height:auto;" src="icons/{0}"></a>""".format(config.webUBAIcon)
        html += "<hr>"
        html += """<a href="#" onclick="document.getElementById('bibleFrame').src = '{1}';">{0} <span class="material-icons-outlined">qr_code_scanner</span></a>""".format(config.thisTranslation["qrcodeScanner"], self.getQrScannerPage())
        html += "<hr>"
        html += """<a href="#">&nbsp;</a>"""
        html += """<a href="#">&nbsp;</a>"""
        return html

    def getOrganisationIcon(self):
        if config.webOrganisationIcon and config.webOrganisationLink:
            return """<a href="{0}" target="_blank"><img style="width:85px; height:auto;" src="{1}"></a>""".format(config.webOrganisationLink, config.webOrganisationIcon)
        elif config.webOrganisationLink:
            return """<a href="{0}" target="_blank">{1}</a>""".format(config.webOrganisationLink, config.thisTranslation["homePage"],)
        elif config.webOrganisationIcon:
            return """<a href="#" target="_blank"><img style="width:85px; height:auto;" src="{0}"></a>""".format(config.webOrganisationIcon)
        else:
            return ""

    def buildForm(self):
        if self.primaryUser or not config.webPresentationMode:
            if config.webUI == "mini":
                return """
                    <form id="commandForm" onsubmit="checkCommands()" action="{4}" action="get">
                    <table class='layout' style='border-collapse: collapse;'><tr>
                    <td class='layout' style='white-space: nowrap;'>{1}&nbsp;</td>
                    <td class='layout' style='width: 100%;'><input type="search" autocomplete="on" id="commandInput" style="width:100%" name="cmd" value=""/><span id="commandInputHolder" title=""></span></td>
                    <td class='layout' style='white-space: nowrap;'>&nbsp;{2}&nbsp;{5}&nbsp;{3}&nbsp;{6}&nbsp;{0}</td>
                    </tr></table>
                    </form>
                """.format(
                    self.passageSelectionButton(),
                    self.openSideNav(),
                    self.submitButton(),
                    #self.chapterSelectionButton(),
                    self.qrButton(),
                    config.webHomePage,
                    self.newWindowButton(),
                    #self.qrScannerButton(),
                    self.playAudioButton(),
                )
            else:
                return """
                    <form id="commandForm" action="{0}" action="get">
                    {10}&nbsp;&nbsp;{5}&nbsp;&nbsp;{3}&nbsp;&nbsp;{4}&nbsp;&nbsp;{6}&nbsp;&nbsp;{7}&nbsp;&nbsp;
                    {11}&nbsp;&nbsp;{12}{13}{14}{15}&nbsp;&nbsp;{8}&nbsp;&nbsp;{16}&nbsp;&nbsp;{19}&nbsp;&nbsp;{20}&nbsp;&nbsp;{18}&nbsp;&nbsp;{9}
                    <br/><br/>
                    <span onclick="focusCommandInput()">{1}</span>:
                    <input type="search" autocomplete="on" id="commandInput" style="width:60%" name="cmd" value=""/>
                    <span id="commandInputHolder" title=""></span>
                    {2}&nbsp;&nbsp;{17}
                    </form>
                    """.format(
                    config.webHomePage,
                    config.thisTranslation["menu_command"],
                    self.submitButton(),
                    self.bibleSelection(),
                    self.bookSelection(),
                    self.previousChapter(),
                    self.currentVerseButton(),
                    self.nextChapter(),
                    self.toggleFullscreen(),
                    self.externalHelpButton(),
                    self.openSideNav(),
                    self.libraryButton(),
                    self.searchButton(),
                    "&nbsp;&nbsp;{0}".format(self.favouriteBibleButton(self.getFavouriteBible())),
                    "&nbsp;&nbsp;{0}".format(self.favouriteBibleButton(self.getFavouriteBible2())),
                    "&nbsp;&nbsp;{0}".format(self.favouriteBibleButton(self.getFavouriteBible3())),
                    self.qrButton(),
                    self.newWindowButton(),
                    self.internalHelpButton(),
                    self.qrScannerButton(),
                    self.playAudioButton(),
                )
        else:
            return ""

    def getQrScannerPage(self):
        if config.webHomePage == "traditional.html":
            return "qr_code_scanner_tc.html"
        elif config.webHomePage == "simplified.html":
            return "qr_code_scanner_sc.html"
        else:
            return "qr_code_scanner.html"

    def getFavouriteBible(self):
        if config.webHomePage == "{0}.html".format(config.webPrivateHomePage):
            return config.favouriteBiblePrivate
        elif config.webHomePage == "traditional.html":
            return config.favouriteBibleTC
        elif config.webHomePage == "simplified.html":
            return config.favouriteBibleSC
        else:
            return config.favouriteBible

    def getFavouriteBible2(self):
        if config.webHomePage == "{0}.html".format(config.webPrivateHomePage):
            return config.favouriteBiblePrivate2
        elif config.webHomePage == "traditional.html":
            return config.favouriteBibleTC2
        elif config.webHomePage == "simplified.html":
            return config.favouriteBibleSC2
        else:
            return config.favouriteBible2

    def getFavouriteBible3(self):
        if config.webHomePage == "{0}.html".format(config.webPrivateHomePage):
            return config.favouriteBiblePrivate3
        elif config.webHomePage == "traditional.html":
            return config.favouriteBibleTC3
        elif config.webHomePage == "simplified.html":
            return config.favouriteBibleSC3
        else:
            return config.favouriteBible3

    def wrapHtml(self, content, view="", book=False):
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
        html = ("""<!DOCTYPE html><html><head><link rel="icon" href="icons/{9}"><title>{12}</title>
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
                         config.webSiteTitle
                         )
        return html

    def getBibleNavigationMenu(self):
        return """
<div id="id01" class="modal" onclick="closeMaster()" style="display:none"><div class="modal-content animate" onclick="stopBubbling()"><div class="imgcontainer">
<span id="closeButton" onclick="closeMaster()" class="close" title="Go back!" style="display:none">&#8630;</span>
<span id="goButton" onclick="goBible()" class="go" title="Go to selected verse!" style="display:none"><i class="fa">&#xf04b;&#xf04b;</i></span>
<div id="options"></div></div></div></div>

<!-- start Book Selection Interface -->

<div id="navB" class="overlay">
<div class="overlay-content">
<div class="nav">

<p><cat>{0}</cat></p>

<p>
<navItem class="numPad" onclick="closeNav('navB')">&#8630;</navItem>
</p>

<hr>

<span id="bookMenu"></span>

<hr>

<p>
<navItem class="numPad" onclick="closeNav('navB')">&#8630;</navItem>
</p>

<p>&nbsp;</p>

</div>
</div>
</div>

<!-- end Book Reference Selection Interface -->

<!-- start Chapter Selection Interface -->

<div id="navC" class="overlay">
  <div class="overlay-content">
<div class="nav">
<p><cat>{1}</cat></p>
<navItem class="numPad" onclick="closeNav('navC')">&#8630;</navItem>
<span id="chapters"></span>
</div>
  </div>
</div>

<!-- end Chapter Selection Interface -->

<!-- start Verse Selection Interface -->

<div id="navV" class="overlay">
  <div class="overlay-content">
<div class="nav">
<p><cat>{2}</cat></p>
<navItem class="numPad" onclick="closeNav('navV')">&#8630;</navItem>
<span id="verses"></span>
</div>
  </div>
</div>

<!-- end Verse Selection Interface -->
""".format(self.getBookTitle(), self.getChapterTitle(), self.getVerseTitle())

    def getBookTitle(self):
        if config.webHomePage == "traditional.html":
            return "〔書卷〕"
        elif config.webHomePage == "simplified.html":
            return "〔书卷〕"
        else:
            return "[Book]"

    def getChapterTitle(self):
        if config.webHomePage == "traditional.html":
            return "〔章〕"
        elif config.webHomePage == "simplified.html":
            return "〔章〕"
        else:
            return "[Chapter]"

    def getVerseTitle(self):
        if config.webHomePage == "traditional.html":
            return "〔節〕"
        elif config.webHomePage == "simplified.html":
            return "〔节〕"
        else:
            return "[Verse]"

    def bibleSelection(self):
        return self.formatSelectList("bibleName", "submitTextCommand", self.bibles, config.mainText)

    def bibleSelectionSide(self):
        return self.formatSelectList("bibleNameSide", "submitTextCommand", self.bibles, config.mainText)

    def bookSelection(self):
        books = Bible(config.mainText).getBookList()
        bookList = []
        for book in books:
            bookList.append((str(book), self.bookMap[str(book)]))
        return self.formatSelectList("bookName", "submitBookCommand", bookList, str(config.mainB))

    def verseActiionSelection(self):
        features = [("_noAction", "[{0}]".format(config.thisTranslation["features"])),]
        features += [(".{0}".format(key.lower()), value) for key, value in self.getVerseFeatures().items()]
        return self.formatSelectList("verseAction", "submitVerseActionCommand", features, "_noAction")

    def formatSelectList(self, id, action, options, selected):
        selectForm = "<select id='{0}' style='width: 100px' onchange='{1}(\"{0}\")'>".format(id, action)
        for value, display in options:
            selectForm += "<option value='{0}'{2}>{1}</option>".format(value, display,
                (" selected='selected'" if value == selected else ""))
        selectForm += "</select>"
        return selectForm

    def currentVerseButton(self):
        html = "<button type='button' onclick='submitCommand(\".bible\")'>{0}:{1}</button>"\
            .format(config.mainC, config.mainV)
        return html

    def previousChapter(self):
        newChapter = config.mainC - 1
        if newChapter < 1:
            newChapter = 1
        command = self.parser.bcvToVerseReference(config.mainB, newChapter, 1)
        html = """<button type='button' title='{1}' onclick='submitCommand("{0}")'><span class="material-icons-outlined">navigate_before</span></button>""".format(command, config.thisTranslation["menu4_previous"])
        return html

    def nextChapter(self):
        newChapter = config.mainC
        if config.mainC < BibleBooks.getLastChapter(config.mainB):
            newChapter += 1
        command = self.parser.bcvToVerseReference(config.mainB, newChapter, 1)
        html = """<button type='button' title='{1}' onclick='submitCommand("{0}")'><span class="material-icons-outlined">navigate_next</span></button>""".format(command, config.thisTranslation["menu4_next"])
        return html

    def playAudioButton(self):
        return """<button type='button' title='{0}' onclick='submitCommand(".play")'><span class="material-icons-outlined">audiotrack</span></button>""".format(config.thisTranslation["bibleAudio"])

    def toggleFullscreen(self):
        html = """<button type='button' title='{0}' onclick='fullScreenSwitch()'><span class="material-icons-outlined">fullscreen</span></button>""".format(config.thisTranslation["menu1_fullScreen"])
        return html

    def openSideNav(self):
        #html = "<button type='button' title='{0}' onclick='openSideNav()'>&equiv;</button>".format(config.thisTranslation["menu_bibleMenu"])
        html = """<button type='button' title='{0}' onclick='openSideNav()'><span class="material-icons-outlined">menu</span></button>""".format(config.thisTranslation["menu_bibleMenu"])
        return html

    def getUserManual(self):
        if config.webHomePage in ("traditional.html", "simplified.html"):
            userManual = r"https://www.uniquebible.app/web/%E4%B8%AD%E6%96%87%E8%AA%AA%E6%98%8E"
        else:
            userManual = "https://www.uniquebible.app/web/english-manual"
        return userManual

    def internalHelpButton(self):
        #html = """<button type='button' title='{0}' onclick='submitCommand(".help")'>&quest;</button>""".format(config.thisTranslation["ubaCommands"])
        html = """<button type='button' title='{0}' onclick='submitCommand(".help")'><span class="material-icons-outlined">help_outline</span></button>""".format(config.thisTranslation["ubaCommands"])
        return html

    def externalHelpButton(self):
        #html = """<button type='button' title='{0}' onclick='window.open("{1}", "_blank")'>&quest;&quest;</button>""".format(config.thisTranslation["userManual"], self.getUserManual())
        html = """<button type='button' title='{0}' onclick='window.open("{1}", "_blank")'><span class="material-icons-outlined">menu_book</span></button>""".format(config.thisTranslation["userManual"], self.getUserManual())
        return html

    def submitButton(self):
        #html = """<button type='button' title='{0}' onclick='document.getElementById("commandForm").submit();'>&crarr;</button>""".format(config.thisTranslation["enter"])
        html = """<button type='button' title='{0}' onclick='document.getElementById("commandForm").submit();'><span class="material-icons-outlined">keyboard_return</span></button>""".format(config.thisTranslation["enter"])
        return html

    def qrButton(self):
        #html = """<button type='button' title='{0}' onclick='submitCommand("qrcode:::"+window.location.href)'>&#9641;</button>""".format(config.thisTranslation["qrcode"])
        #html = """<button type='button' title='{0}' onclick='submitCommand("qrcode:::"+window.location.href)'><span class="material-icons-outlined">qr_code</span></button>""".format(config.thisTranslation["qrcode"])
        html = """<button type='button' title='{0}' onclick='shareInfo()'><span class="material-icons-outlined">share</span></button>""".format(config.thisTranslation["share"])
        return html

    def qrScannerButton(self):
        #html = """<button type='button' title='{0}' onclick="document.getElementById('bibleFrame').src = '{1}';">&#9635;</button>""".format(config.thisTranslation["qrcodeScanner"], self.getQrScannerPage())
        html = """<button type='button' title='{0}' onclick="document.getElementById('bibleFrame').src = '{1}';"><span class="material-icons-outlined">qr_code_scanner</span></button>""".format(config.thisTranslation["qrcodeScanner"], self.getQrScannerPage())
        return html

    def passageSelectionButton(self):
        #html = """<button type='button' title='{1}' onclick='mod = "KJV"; updateBook("KJV", "{0}"); openNav("navB");'>&dagger;</button>""".format(config.webHomePage, config.thisTranslation["bibleNavigation"])
        html = """<button type='button' title='{1}' onclick='mod = "KJV"; updateBook("KJV", "{0}"); openNav("navB");'><span class="material-icons-outlined">add</span></button>""".format(config.webHomePage, config.thisTranslation["bibleNavigation"])
        return html

    def chapterSelectionButton(self):
        html = """<button type='button' title='{0}' onclick='submitCommand(".chapters")'><span class="material-icons-outlined">auto_stories</span></button>""".format(config.thisTranslation["bibleNavigation"])
        return html

    def libraryButton(self):
        #html = """<button type='button' onclick='submitCommand(".library")'>{0}</button>""".format(config.thisTranslation["menu_library"])
        html = """<button type='button' onclick='submitCommand(".library")'><span class="material-icons-outlined">local_library</span></button>"""
        return html

    def searchButton(self):
        #html = """<button type='button' onclick='submitCommand(".search")'>{0}</button>""".format(config.thisTranslation["menu_search"])
        html = """<button type='button' onclick='submitCommand(".search")'><span class="material-icons-outlined">search</span></button>"""
        return html

    def newWindowButton(self):
        #html = """<button type='button' title='{0}' onclick='openCommandInNewWindow()'>&#8663;</button>""".format(config.thisTranslation["openOnNewWindow"])
        html = """<button type='button' title='{0}' onclick='openCommandInNewWindow()'><span class="material-icons-outlined">open_in_new</span></button>""".format(config.thisTranslation["openOnNewWindow"])
        return html

    def favouriteBibleButton(self, text):
        html = """<button type='button' onclick='submitCommand("BIBLE:::{0}:::{1}")'>{0}</button>""".format(text, self.getMainVerse()["reference"])
        return html

    def getHighlightCss(self):
        css = ""
        for i in range(len(config.highlightCollections)):
            code = "hl{0}".format(i + 1)
            css += ".{2} {0} background: {3}; {1} ".format("{", "}", code, config.highlightDarkThemeColours[i] if config.theme == "dark" else config.highlightLightThemeColours[i])
        return css

    def checkPermission(self):
        if config.developer or config.webFullAccess or self.clientIP in self.adminUsers:
            return (True, "")
        else:
            return (False, config.thisTranslation["loginAdmin"])

    def displayMessage(self, message):
        return """
        <html>
            <head>
                <link rel="icon" href="icons/{1}">
                <title>{2}</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head><body>{0}</body></html>""".format(message, config.webUBAIcon, config.webSiteTitle)

    def historyContent(self):
        view, content, *_ = self.textCommandParser.parser("_history:::main", "http")
        return content

    def importContent(self):
        self.textCommandParser.parser("import:::import", "http")
        return "Processed!"

    def configContent(self):
        intro = ("File 'config.py' contains essential configurations for running UniqueBible.app.\n(Remarks: Generally speaking, users don't need to edit this file.\nIn case you need to do so, make sure UBA is not running when you manually edit this file.)"
            "\n\nTo telnet-server / http-server users on Android:"
            "\nIf you want to change some configurations but don't see the file config.py, you need to create the file config.py in UniqueBible directory manually and enter in it non-default values ONLY."
            "\nFor example, to change web user interface and theme, create file config.py and enter the following two lines:"
            "\nwebUI = 'mini'"
            "\ntheme = 'dark'"
            "\n\nIndividual items in config.py are briefly described below:")
        content = "{0}\n\n{1}".format(intro, "\n\n".join(["<b>[ITEM] {0}</b>{1}\nCurrent value: <z>{2}</z>".format(key, re.sub("        # ", "", value), eval("pprint.pformat(config."+key+")")) for key, value in config.help.items()]))
        content = re.sub(r"\n", "<br/>", content)
        return content

    def increaseFontSize(self):
        config.fontSize = config.fontSize + 1
        return self.displayMessage("""<p>Font size changed to {0}!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""".format(config.fontSize))

    def decreaseFontSize(self):
        if config.fontSize >= 4:
            config.fontSize = config.fontSize - 1
            return self.displayMessage("""<p>Font size changed to {0}!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""".format(config.fontSize))
        else:
            return self.displayMessage("Current font size is already too small!")

    def getBibleChapter(self):
        #view, content, *_ = self.textCommandParser.parser(self.getCurrentReference(), "http")
        #return content
        return """... {0} ...
                <script>
                window.parent.location.assign("{1}?cmd=.bible");
                </script>""".format(config.thisTranslation["loading"], config.webHomePage)

    def toggleCompareParallel(self):
        if config.enforceCompareParallel:
            config.enforceCompareParallel = False
            return self.displayMessage("""<p>Compare / parallel mode is turned OFF!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")
        else:
            config.enforceCompareParallel = True
            return self.displayMessage("""<p>Compare / parallel mode is turned ON!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")

    def togglePlainMode(self):
        config.readFormattedBibles = not config.readFormattedBibles
        return self.getBibleChapter()

    def toggleWordAudioLinks(self):
        config.showHebrewGreekWordAudioLinks = not config.showHebrewGreekWordAudioLinks
        return self.getBibleChapter()

    def toggleSubheadings(self):
        config.addTitleToPlainChapter = not config.addTitleToPlainChapter
        return self.getBibleChapter()

    def toggleCaseSensitiveSearch(self):
        if config.enableCaseSensitiveSearch:
            config.enableCaseSensitiveSearch = False
            return self.displayMessage("""<p>Case-sensitive search is disabled!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")
        else:
            config.enableCaseSensitiveSearch = True
            return self.displayMessage("""<p>Case-sensitive search is enabled!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")

    def togglePresentationMode(self):
        if config.webPresentationMode:
            config.webPresentationMode = False
            return self.displayMessage("""<p>Option 'presentation mode' is turned off!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")
        else:
            config.webPresentationMode = True
            return self.displayMessage("""<p>Option 'presentation mode' is turned on!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")

    def toggleGlobalViewer(self):
        if config.httpServerViewerGlobalMode:
            config.httpServerViewerGlobalMode = False
            return self.displayMessage("""<p>Option 'global viewer' is turned off for presentation mode.!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")
        else:
            config.httpServerViewerGlobalMode = True
            return self.displayMessage("""<p>Option 'global viewer' is turned on for presentation mode.!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")

    def swapLayout(self):
        config.webUI = "" if config.webUI == "mini" else "mini"
        #return self.displayMessage("Layout changed!")
        return self.getBibleChapter()

    def swapTheme(self):
        config.theme = "default" if config.theme == "dark" else "dark"
        #return self.displayMessage("Theme changed!")
        return self.getBibleChapter()

    def closeWindow(self, message="Server is shut down!"):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = self.displayMessage(message)
        self.wfile.write(bytes(html, "utf8"))

    def restartServer(self, additionalMessage=""):
        config.restartHttpServer = True
        locallink = "http://localhost:{0}".format(config.httpServerPort)
        html = "<h2>Server {1}restarted!</h2><p>To connect again locally, try:<br><a href='{0}'>{0}</a></p>".format(locallink, additionalMessage)
        self.closeWindow(html)
        config.enableHttpServer = False
        return

    def helpContent(self):
        mainVerse = self.getMainVerse()
        dotCommands = """
        <h2>Commands</h2>
        <p>Unique Bible App supports single-line commands to navigate or interact between resources.  This page documents available commands.  Web version commands are supported on UBA web version only.  UBA commands are shared by both desktop and web versions, though some UBA commands apply to desktop version only.</p>
        <h2>Web Version Commands [case insensitive]</h2>
        <p>
        <ref onclick="displayCommand('.help')">.help</ref> - Display help page with list of available commands.<br>
        <ref onclick="window.parent.submitCommand('.myqrcode')">.myQRcode</ref> - Display a QR code for other users connecting to the same UBA http-server.<br>
        <ref onclick="window.parent.submitCommand('.bible')">.bible</ref> - Open bible chapter.<br>
        <ref onclick="window.parent.submitCommand('.biblemenu')">.bibleMenu</ref> - Open bible menu.<br>
        <ref onclick="window.parent.submitCommand('.chapters')">.chapters</ref> - Open a menu of all available chapters.<br>
        <ref onclick="window.parent.submitCommand('.commentarymenu')">.commentaryMenu</ref> - Open Commentary menu.<br>
        <ref onclick="window.parent.submitCommand('.comparison')">.comparison</ref> - Open bible version comparison menu.<br>
        <ref onclick="window.parent.submitCommand('.timelinemenu')">.timelineMenu</ref> - Open Timeline menu.<br>
        <ref onclick="window.parent.submitCommand('.audio')">.audio</ref> - Open audio bible content page.<br>
        <ref onclick="window.parent.submitCommand('.play')">.play</ref> - Play all available bible audio linked with the current content.<br>
        <ref onclick="window.parent.submitCommand('.names')">.names</ref> - Open bible names content page.<br>
        <ref onclick="window.parent.submitCommand('.characters')">.characters</ref> - Open bible characters content page.<br>
        <ref onclick="window.parent.submitCommand('.maps')">.maps</ref> - Open bible map content page.<br>
        <ref onclick="window.parent.submitCommand('.locations')">.locations</ref> - Open bible location content page.<br>
        <ref onclick="window.parent.submitCommand('.topics')">.topics</ref> - Open bible topics content page.<br>
        <ref onclick="window.parent.submitCommand('.parallels')">.parallels</ref> - Open bible parallels content page.<br>
        <ref onclick="window.parent.submitCommand('.promises')">.promises</ref> - Open bible promises content page.<br>
        <ref onclick="window.parent.submitCommand('.days')">.days</ref> - Open bible reading plan page.<br>
        <ref onclick="window.parent.submitCommand('.download')">.download</ref> - Display downloadable resources.<br>
        <ref onclick="window.parent.submitCommand('.library')">.library</ref> - Display installed bible commentaries and references books.<br>
        <ref onclick="window.parent.submitCommand('.search')">.search</ref> - Display search options.
        </p><p>"""
        dotCommands += """<u>Marvel Bibles</u><br>
        <ref onclick="window.parent.submitCommand('.mob')">.mob</ref> - Open Marvel Original Bible.<br>
        <ref onclick="window.parent.submitCommand('.mib')">.mib</ref> - Open Marvel Interlinear Bible.<br>
        <ref onclick="window.parent.submitCommand('.mtb')">.mtb</ref> - Open Marvel Trilingual Bible.<br>
        <ref onclick="window.parent.submitCommand('.mpb')">.mpb</ref> - Open Marvel Parallel Bible.<br>
        <ref onclick="window.parent.submitCommand('.mab')">.mab</ref> - Open Marvel Annotated Bible.<br>
        </p><p>"""
        dotCommands += """<u>Study currently selected book [<span id="libraryBook">{2}</span>]</u><br>
        <ref onclick="window.parent.submitCommand('.introduction')">.introduction</ref> - {0}.<br>
        <ref onclick="window.parent.submitCommand('.timelines')">.timelines</ref> - {1}.
        </p><p>""".format(config.thisTranslation["html_introduction"], config.thisTranslation["html_timelines"], mainVerse["bAbb"])
        dotCommands += """<u>Study currently selected chapter [<span id="libraryChapter">{0} {1}</span>]</u><br>""".format(mainVerse["bAbb"], mainVerse["b"])
        dotCommands += "<br>".join(["""<ref onclick="window.parent.submitCommand('.{0}')">.{0}</ref> - {1}.""".format(key.lower(), value) for key, value in self.getChapterFeatures().items()])
        dotCommands += "</p><p>"
        dotCommands += """<u>Study currently selected verse [<span id="libraryVerse">{0}</span>]</u><br>""".format(mainVerse["reference"])
        dotCommands += "<br>".join(["""<ref onclick="window.parent.submitCommand('.{0}')">.{0}</ref> - {1}.""".format(key.lower(), value) for key, value in self.getVerseFeatures().items()])
        dotCommands += """
        </p><p><b>Admin Options</b></p>
        <p>The following commands are enabled only if either you:
        <br>- log in as an administrator by running '<ref onclick="displayCommand('.login:::')">.login:::</ref>UBA123', where 'UBA123' is the login password by default.
        <br>- set 'developer' to 'True' in file 'config.py'.
        <br>- set 'webFullAccess' to 'True' in file 'config.py'.
        <br>To prevent admin options from public access, administrator should set both config.developer and config.webFullAccess to 'False'. Administrator should also change the default 'webAdminPassword' in config.py.
        <br>Remarks: Make sure UBA is not running when 'config.py' is being edited manually.</p><p>
        <ref onclick="window.parent.submitCommand('.config')">.config</ref> - Display config.py values and their description.<br>
        <ref onclick="window.parent.submitCommand('.latest')">.latest</ref> - Display latest changes.<br>
        <ref onclick="window.parent.submitCommand('.history')">.history</ref> - Display history records.<br>
        <ref onclick="window.parent.submitCommand('.import')">.import</ref> - Place third-party resources in directory 'UniqueBible/import/' and run this command to import them into UBA.<br>
        <ref onclick="window.parent.submitCommand('.layout')">.layout</ref> - Swap between available layouts.<br>
        <ref onclick="window.parent.submitCommand('.logout')">.logout</ref> - Log out as an administrator.<br>
        <ref onclick="window.parent.submitCommand('.theme')">.theme</ref> - Swap between available themes.<br>
        <ref onclick="window.parent.submitCommand('.increasefontsize')">.increaseFontSize</ref> - Increase font size.<br>
        <ref onclick="window.parent.submitCommand('.decreasefontsize')">.decreaseFontSize</ref> - Decrease font size.<br>
        <ref onclick="window.parent.submitCommand('.plainmode')">.plainMode</ref> - Toggle 'plain mode' for displaying bible chapters.<br>
        <ref onclick="window.parent.submitCommand('.wordaudiolinks')">.wordAudioLinks</ref> - Toggle 'Hebrew & Greek word audio links' for displaying bible chapters of marvel bibles.<br>
        <ref onclick="window.parent.submitCommand('.subheadings')">.subHeadings</ref> - Toggle 'sub-headings' for displaying bible chapters in plain mode.<br>
        <ref onclick="window.parent.submitCommand('.compareparallelmode')">.compareParallelMode</ref> - Toggle 'compare / parallel mode' for bible reading.<br>
        <ref onclick="window.parent.submitCommand('.caseSensitiveSearch')">.caseSensitiveSearch</ref> - Toggle case-sensitive search.<br>
        <ref onclick="window.parent.submitCommand('.presentationmode')">.presentationMode</ref> - Toggle 'presentation mode'.<br>
        <ref onclick="window.parent.submitCommand('.globalviewer')">.globalViewer</ref> - Toggle 'global viewer' for presentation mode.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebible')">.setFavouriteBible</ref> - Set configuration 'favouriteBible'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebible2')">.setFavouriteBible2</ref> - Set configuration 'favouriteBible2'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebible3')">.setFavouriteBible3</ref> - Set configuration 'favouriteBible3'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebibletc')">.setFavouriteBibleTC</ref> - Set configuration 'favouriteBible'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebibletc2')">.setFavouriteBibleTC2</ref> - Set configuration 'favouriteBible2'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebibletc3')">.setFavouriteBibleTC3</ref> - Set configuration 'favouriteBible3'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebiblesc')">.setFavouriteBibleSC</ref> - Set configuration 'favouriteBible'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebiblesc2')">.setFavouriteBibleSC2</ref> - Set configuration 'favouriteBible2'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebiblesc3')">.setFavouriteBibleSC3</ref> - Set configuration 'favouriteBible3'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebibleprivate')">.setFavouriteBiblePrivate</ref> - Set configuration 'favouriteBiblePrivate'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebibleprivate2')">.setFavouriteBiblePrivate2</ref> - Set configuration 'favouriteBiblePrivate2'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebibleprivate3')">.setFavouriteBiblePrivate3</ref> - Set configuration 'favouriteBiblePrivate3'.<br>
        <ref onclick="window.parent.submitCommand('.setversenosingleclickaction')">.setVerseNoSingleClickAction</ref> - Set configuration 'verseNoSingleClickAction'.<br>
        <ref onclick="window.parent.submitCommand('.setversenodoubleclickaction')">.setVerseNoDoubleClickAction</ref> - Set configuration 'verseNoDoubleClickAction'.<br>
        <ref onclick="window.parent.submitCommand('.setwebubaicon')">.setWebUBAIcon</ref> - Set configuration 'webUBAIcon'.<br>
        <ref onclick="window.parent.submitCommand('.restart')">.restart</ref> - Re-start http-server.<br>
        <ref onclick="window.parent.submitCommand('.stop')">.stop</ref> - Stop http-server.<br>
        <ref onclick="window.parent.submitCommand('.update')">.update</ref> - Update and re-start http-server.
        </p>
        <h2>UBA Commands</h2>
        <p>"""
        content = "\n".join(
            [re.sub("            #", "#", value[-1]) for value in self.textCommandParser.interpreters.values()])
        content = re.sub("(\[KEYWORD\] )(.*?)$", r"""\1<ref onclick="displayCommand('\2:::')">\2</ref>""", content, flags=re.M)
        content = dotCommands + re.sub(r"\n", "<br/>", content) + "</p>"
        return content

    def downloadContent(self):
        content = ""
        from uniquebible.util.DatafileLocation import DatafileLocation
        try:
            from uniquebible.util.GithubUtil import GithubUtil
            githubutilEnabled = True
        except:
            githubutilEnabled = False
        resources = (
            ("Marvel Datasets", DatafileLocation.marvelData, "marveldata"),
            ("Marvel Bibles", DatafileLocation.marvelBibles, "marvelbible"),
            ("Marvel Commentaries", DatafileLocation.marvelCommentaries, "marvelcommentary"),
        )
        for collection, data, keyword in resources:
            content += "<h2>{0}</h2>".format(collection)
            for k, v in data.items():
                if os.path.isfile(os.path.join(*v[0])):
                    content += """{0} [{1}]<br>""".format(k, config.thisTranslation["installed"])
                else:
                    content += """<ref onclick="document.title='download:::{0}:::{1}'">{2}</ref><br>"""\
                        .format(keyword, k.replace("'", "\\'"), k)
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
                        content += """{0} [{1}]<br>""".format(file.replace(extension, ""), config.thisTranslation["installed"])
                    else:
                        content += """<ref onclick="document.title='download:::{1}:::{0}'">{0}</ref><br>""".format(file.replace(extension, ""), kind)
        content += "<h2>Third-party Resources</h2><p><a href='https://github.com/eliranwong/UniqueBible/wiki/Third-party-resources' target='_blank'>Click this link to read our wiki page about third-party resources.</a></p>"
        return content

    def getCurrentReference(self):
        return "{0} {1}:{2}".format(self.abbreviations[str(config.mainB)], config.mainC, config.mainV)

    def getQrCodeCommand(self):
        if config.httpServerViewerGlobalMode:
            return "QRCODE:::{0}/index.php?code={1}".format(config.httpServerViewerBaseUrl, self.session)
        else:
            return "QRCODE:::server"

    def getPlaylistFromHTML(self, html):
        playlist = []
        #searchPattern = """[Rr][Ee][Aa][Dd][Cc][Hh][Aa][Pp][Tt][Ee][Rr]:::([A-Za-z0-9]+?)\.([0-9]+?)\.([0-9]+?)[\."']"""
        searchPattern = """_[Cc][Hh][Aa][Pp][Tt][Ee][Rr][Ss]:::([^\.>]+?)_([0-9]+?)\.([0-9]+?)["'].*onclick=["']rC\("""
        found = re.search(searchPattern, html)
        if found:
            text, b, c = found[1], found[2], found[3]
            text = FileUtil.getMP3TextFile(text)
            playlist = RemoteCliMainWindow().playAudioBibleChapterVerseByVerse(text, b, c)
        else:
            searchPattern = """[Rr][Ee][Aa][Dd][Vv][Ee][Rr][Ss][Ee]:::([A-Za-z0-9]+?)\.([0-9]+?)\.([0-9]+?)\.([0-9]+?)["']"""
            found = re.findall(searchPattern, html)
            if found:
                for entry in found:
                    text, b, c, v = entry
                    audioFolder = os.path.join("audio", "bibles", text, "default", "{1}_{2}".format(text, b, c))
                    audioFile = "{0}_{1}_{2}_{3}.mp3".format(text, b, c, v)
                    audioFilePath = os.path.join(audioFolder, audioFile)
                    if os.path.isfile(audioFilePath):
                        playlist.append((audioFile, audioFilePath))
            else:
                searchPattern = """[Rr][Ee][Aa][Dd]([Ww][Oo][Rr][Dd]|[Ll][Ee][Xx][Ee][Mm][Ee]):::([A-Za-z0-9]+?)\.([0-9]+?)\.([0-9]+?)\.([0-9]+?)\.([0-9]+?)["']"""
                found = re.findall(searchPattern, html)
                if found:
                    for entry in found:
                        wordType, text, b, c, v, wordID = entry
                        audioFolder = os.path.join("audio", "bibles", text, "default", "{1}_{2}".format(text, b, c))
                        prefix = "lex_" if wordType.lower() == "lexeme" else ""
                        audioFile = "{5}{0}_{1}_{2}_{3}_{4}.mp3".format(text, b, c, v, wordID, prefix)
                        audioFilePath = os.path.join(audioFolder, audioFile)
                        if os.path.isfile(audioFilePath):
                            playlist.append((audioFile, audioFilePath))
        return playlist

    def playAudio(self):
        mainFileHTML = open(os.path.join("htmlResources", "main-{0}.html".format(self.session)), 'r').read()
        playlist = self.getPlaylistFromHTML(mainFileHTML)
        if playlist:
            content = HtmlGeneratorUtil().getAudioPlayer(playlist)
        else:
            #content = config.thisTranslation["noBibleAudioLink"]
            content = self.audioContent()
        return content

    def audioContent(self):
        content = ""
        modules = {
            "ASV": "American Standard Version",
            "BBE": "Bible in Basic English",
            "BSB": "Berean Study Bible",
            "CUV": "中文和合本〔廣東話〕",
            "CUVs": "中文和合本〔普通話〕",
            "ERV": "English Revised Version",
            "ISV": "International Standard Version",
            "KJV": "King James Version",
            "LEB": "Lexham English Bible",
            "NET": "New English Translation",
            "OHGB": "Open Hebrew & Greek Bible",
            "SBLGNT": "SBL Greek New Testament",
            "WEB": "World English Bible",
            "WLC": "Westminster Leningrad Codex",
        }
        for module in modules.keys():
            if os.path.isdir(os.path.join("audio", "bibles", module)):
                try:
                    bible = Bible(module)
                    bookList = bible.getBookList()
                    if bookList:
                        b = bookList[0]
                        chapterList = bible.getChapterList(b)
                        if chapterList:
                            c = chapterList[0]
                            content += "<p>{0}</p>".format(HtmlGeneratorUtil.getChapterAudioButton(module, b, c, modules[module]))
                except:
                    pass
        if not content:
            content = config.thisTranslation["search_notFound"]
        return "<div style='margin: auto; text-align: center;'><h2>{0}</h2><p style='text-align: center;'>{1}</p></div>".format(config.thisTranslation["bibleAudio"], content)

    def libraryContent(self):
        self.textCommandParser.parent.setupResourceLists()
        content = ""
        content += """<h2><ref onclick="window.parent.submitCommand('.commentarymenu')">{0}</ref></h2>""".format(config.thisTranslation["menu4_commentary"])
        #mainVerse = self.getMainVerse()
        content += "<br>".join(["""<ref onclick ="document.title = '_commentarychapters:::{0}'">{1}</ref>""".format(abb, self.textCommandParser.parent.commentaryFullNameList[index]) for index, abb in enumerate(self.textCommandParser.parent.commentaryList)])
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_selectBook"])
        content += "<br>".join(["""<ref onclick ="document.title = 'BOOK:::{0}'">{0}</ref>""".format(book) for book in self.textCommandParser.parent.referenceBookList])
        content += "<h2>PDF {0}</h2>".format(config.thisTranslation["file"])
        content += "<br>".join(["""<ref onclick ="document.title = 'PDF:::{0}'">{0}</ref>""".format(book)
            for book in self.textCommandParser.parent.pdfList])
        content += "<h2>EPUB {0}</h2>".format(config.thisTranslation["file"])
        content += "<br>".join(["""<ref onclick ="document.title = 'EPUB:::{0}'">{0}</ref>""".format(book)
            for book in self.textCommandParser.parent.epubList])
        content += "<h2>{0}</h2>".format(config.thisTranslation["others"])
        dataList = [item for item in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "menu", "Bible_Data"), "txt")]
        content += "<br>".join(["""<ref onclick ="document.title = 'DATA:::{0}'">{0}</ref>""".format(book)
            for book in dataList])
        return content

    def setVerseNoClickActionContent(self, double=False):
        values = ("_noAction", "COMPARE", "CROSSREFERENCE", "TSKE", "TRANSLATION", "DISCOURSE", "WORDS", "COMBO", "INDEX", "COMMENTARY", "_menu")
        features = ("noAction", "menu4_compareAll", "menu4_crossRef", "menu4_tske", "menu4_traslations", "menu4_discourse", "menu4_words", "menu4_tdw", "menu4_indexes", "menu4_commentary", "classicMenu")
        items = [config.thisTranslation[feature] for feature in features]
        content = "<h2>Select Verse Number {0}-click Action:</h2>".format("Double" if double else "Single")
        content += "<br>".join(["""<ref onclick ="document.title = '_setconfig:::{2}:::\\'{0}\\''">{1}</ref>""".format(value, items[index], "verseNoDoubleClickAction" if double else "verseNoSingleClickAction") for index, value in enumerate(values)])
        return content

    def setWebUBAIconContent(self):
        files = glob.glob(os.path.join("htmlResources", "icons", "UniqueBibleApp*.png"))
        files = [file[20:] for file in files]
        content = "<h2>Select {0} Icon:</h2>".format(config.webSiteTitle)
        content += " ".join(["""<ref onclick ="document.title = '_setconfig:::webUBAIcon:::\\'{0}\\''"><img src="icons/{0}"></ref>""".format(file) for file in files])
        return content

    def setFavouriteBibleContent(self, favouriteBible="favouriteBible"):
        content = "<h2>Select Faviourite Bible:</h2>"
        content += "<br>".join(["""<ref onclick ="document.title = '_setconfig:::{2}:::\\'{0}\\''">{1}</ref>""".format(abb, self.textCommandParser.parent.textFullNameList[index], favouriteBible) for index, abb in enumerate(self.textCommandParser.parent.textList)])
        return content

    def dailyReadingContent(self):
        content = "<div style='margin: auto; text-align: center;'><h2>{0}</h2><p style='text-align: center;'>".format(config.thisTranslation["bibleInAYear"])
        for i in range(1, 366):
            day = "第 {0} 日".format(i) if (config.displayLanguage == "zh_HANT" or config.displayLanguage == "zh_HANS") else "Day {0}".format(i)
            readButton = """<button type='button' title='{1}' onclick='document.title="DAY:::{0}"'>{1}</button>""".format(i, config.thisTranslation["menu1_readClipboard"])
            audioButton = """<button type='button' title='{1}' onclick='document.title="DAYAUDIO:::{0}"'>{1}</button>""".format(i, config.thisTranslation["menu11_audio"])
            audioButtonPlus = """<button type='button' title='{1} +' onclick='document.title="DAYAUDIOPLUS:::{0}"'>{1} +</button>""".format(i, config.thisTranslation["menu11_audio"])
            content += "{0} {1} {2} {3}<br>".format(day, readButton, audioButton, audioButtonPlus)
        content += "</p></div>"
        return content

    def mapsContent(self):
        content = "<h2>{0}</h2>".format(config.thisTranslation["bibleMaps"])
        if config.displayLanguage == "zh_HANT":
            content += """<p>如要開啟聖經地圖，請先輸入一個聖經經文章節（例如：啓示錄 1:11、約書亞記 10:1-43、使徒行傳 15:36-18:22 等等），然後按下按鈕「{0}」。</p>""".format(config.thisTranslation["open"])
        elif config.displayLanguage == "zh_HANS":
            content += """<p>如要开启圣经地图，请先输入一个圣经经文章节（例如：启示录 1:11、约书亚记 10:1-43、使徒行传 15:36-18:22 等等），然后按下按钮「{0}」。</p>""".format(config.thisTranslation["open"])
        else:
            content += """<p>To open a bible map, enter a bible reference below (e.g. Rev 1:11, Josh 10:1-43, Act 15:36-18:22, etc.) and click the button '{0}'.</p>""".format(config.thisTranslation["open"])
        content += "<p><input type='text' id='mapReference' style='width:95%' autofocus></p>"
        content += "<p><button id='openMapButton' type='button' onclick='openBibleMap();' class='ubaButton'>{0}</button></p>".format(config.thisTranslation["open"])
        content += """
<script>
var input = document.getElementById('mapReference');
input.addEventListener('keyup', function(event) {0}
  if (event.keyCode === 13) {0}
   event.preventDefault();
   document.getElementById('openMapButton').click();
  {1}
{1});
</script>""".format("{", "}")
        return content

    def formatSearchSection(self, resourceType, inputID, searchCommand, abbreviationList, fullNameList=None):
        content = ""
        content += "<h2>{0}</h2><p>".format(resourceType)
        content += "<input type='text' id='{0}' style='width:95%' autofocus></p><p>".format(inputID)
        if fullNameList is None:
            fullNameList = abbreviationList
        if abbreviationList:
            content += "<br>".join(["""<ref onclick ="searchResourceModule('{0}', '{1}', '{2}')">{3}</ref>""".format(inputID, searchCommand, abb, fullNameList[index]) for index, abb in enumerate(abbreviationList)])
        else:
            content += "[not installed]"
        content += "</p>"
        return content

    def searchContent(self):
        content = ""
        content += """<h2>{0}</h2><p><ref onclick="document.title='_menu:::'">Click HERE to Search Bibles</ref></p>""".format(config.thisTranslation["html_bibles"])
        content += "<hr>"
        abbList = ["HBN", "EXLBP", "EXLBL"]
        nameList = ["Bible Names", "Bible Characters", "Bible Locations"]
        content += self.formatSearchSection(config.thisTranslation["bibleBackground"], "SEARCHTOOL", "SEARCHTOOL", abbList, nameList)
        content += "<hr>"
        abbList = ["Bible_Promises", "Harmonies_and_Parallels", "FAV", "ALL"]
        nameList = ["Bible Promises", "Harmonies and Parallels", "Favourite Books", "All Books"]
        content += self.formatSearchSection(config.thisTranslation["collection"], "collection", "SEARCHBOOK", abbList, nameList)
        content += "<hr>"
        content += self.formatSearchSection(config.thisTranslation["menu5_topics"], "topics", "SEARCHTOOL", self.textCommandParser.parent.topicListAbb, self.textCommandParser.parent.topicList)
        content += "<hr>"
        content += self.formatSearchSection(config.thisTranslation["context1_dict"], "dictionary", "SEARCHTOOL", self.textCommandParser.parent.dictionaryListAbb, self.textCommandParser.parent.dictionaryList)
        content += "<hr>"
        content += self.formatSearchSection(config.thisTranslation["context1_encyclopedia"], "encyclopedia", "SEARCHTOOL", self.textCommandParser.parent.encyclopediaListAbb, self.textCommandParser.parent.encyclopediaList)
        content += "<hr>"
        content += self.formatSearchSection(config.thisTranslation["bibleConcordance"], "CONCORDANCE", "CONCORDANCE", self.textCommandParser.parent.strongBibles)
        content += "<hr>"
        content += self.formatSearchSection(config.thisTranslation["menu5_lexicon"], "LEXICON", "LEXICON", self.textCommandParser.parent.lexiconList)
        content += "<hr>"
        content += self.formatSearchSection(config.thisTranslation["installBooks"], "SEARCHBOOK", "SEARCHBOOK", self.textCommandParser.parent.referenceBookList)
        content += "<hr>"
        content += self.formatSearchSection(config.thisTranslation["menu5_3rdDict"], "SEARCHTHIRDDICTIONARY", "SEARCHTHIRDDICTIONARY", self.textCommandParser.parent.thirdPartyDictionaryList)
        content += "<hr>"
        return content

    def getSession(self):
        headers = {x: y for x, y in self.headers._headers}
        ip = self.client_address[0]
        if 'User-Agent' in headers.keys():
            browser = headers['User-Agent']
        else:
            return None
        session = str(ip + browser).encode('utf-8')
        session = hashlib.sha256(session).hexdigest()[:30]
        return session

    def login(self, password):
        if password == config.webAdminPassword:
            if self.clientIP not in self.adminUsers:
                self.adminUsers.append(self.clientIP)
            return "Administrative rights are enabled!"
        else:
            return "Incorrect password!"

    def logout(self):
        if self.clientIP in self.adminUsers:
            self.adminUsers.remove(self.clientIP)
        return "Administrative rights are disabled!"

    def latestContent(self):
        content = Path('latest_changes.txt').read_text()
        content = content.replace("\n", "<br>")
        return content
