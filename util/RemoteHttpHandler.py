# https://docs.python.org/3/library/http.server.html
# https://ironpython-test.readthedocs.io/en/latest/library/simplehttpserver.html
import hashlib
import json
import os, re, config, pprint
import subprocess
import urllib

import requests
from http.server import SimpleHTTPRequestHandler
from time import gmtime
from util.BibleBooks import BibleBooks
from util.BibleVerseParser import BibleVerseParser
from db.BiblesSqlite import BiblesSqlite
from util.TextCommandParser import TextCommandParser
from util.RemoteCliMainWindow import RemoteCliMainWindow
from urllib.parse import urlparse
from urllib.parse import parse_qs
from util.FileUtil import FileUtil


class RemoteHttpHandler(SimpleHTTPRequestHandler):

    parser = None
    textCommandParser = None
    bibles = None
    books = None
    bookMap = None
    abbreviations = None
    session = None
    users = []

    def __init__(self, *args, **kwargs):
        if RemoteHttpHandler.textCommandParser is None:
            RemoteHttpHandler.textCommandParser = TextCommandParser(RemoteCliMainWindow())
        self.textCommandParser = RemoteHttpHandler.textCommandParser
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
        self.primaryUser = False
        if config.httpServerViewerGlobalMode:
            try:
                urllib.request.urlopen(config.httpServerViewerBaseUrl)
            except:
                config.httpServerViewerGlobalMode = False
        super().__init__(*args, directory="htmlResources", **kwargs)

    def getCommands(self):
        return {
            ".myqrcode": self.getQrCodeCommand,
            ".bible": self.getCurrentReference,
        }

    def getShortcuts(self):
        return {
            ".biblemenu": "_menu:::",
            ".commentarymenu": "_commentary:::{0}".format(config.commentaryText),
            ".timelinemenu": "BOOK:::Timelines",
            ".maps": "SEARCHTOOL:::EXLBL:::",
            ".characters": "SEARCHTOOL:::EXLBP:::",
            ".names": "SEARCHTOOL:::HBN:::",
            ".promises": "BOOK:::Bible_Promises",
            ".parallels": "BOOK:::Harmonies_and_Parallels",
            ".topics": "SEARCHTOOL:::EXLBT:::",
            ".mob": "TEXT:::MOB",
            ".mib": "TEXT:::MIB",
            ".mtb": "TEXT:::MTB",
            ".mpb": "TEXT:::MPB",
            ".mab": "TEXT:::MAB",
            ".introduction": "SEARCHBOOKCHAPTER:::Tidwell_The_Bible_Book_by_Book:::{0}".format(BibleBooks.eng[str(config.mainB)][-1]),
            ".timeline": "SEARCHBOOKCHAPTER:::Timelines:::{0}".format(BibleBooks.eng[str(config.mainB)][-1]),
            ".timelines": "SEARCHBOOKCHAPTER:::Timelines:::{0}".format(BibleBooks.eng[str(config.mainB)][-1]),
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

    def do_GET(self):
        features = {
            "download": self.downloadContent,
            "config": self.configContent,
            "history": self.historyContent,
            "library": self.libraryContent,
            "search": self.searchContent,
            "import": self.importContent,
            "layout": self.swapLayout,
            "theme": self.swapTheme,
            "globalviewer": self.toggleGlobalViewer,
            "presentationmode": self.togglePresentationMode,
            "increasefontsize": self.increaseFontSize,
            "decreasefontsize": self.decreaseFontSize,
            "compareparallelmode": self.toggleCompareParallel,
            "subheadings": self.toggleSubheadings,
            "plainmode": self.togglePlainMode,
            "regexcasesensitive": self.toggleRegexCaseSensitive,
            "setfavouritebible": self.setFavouriteBibleContent,
            "setfavouritebible2": lambda: self.setFavouriteBibleContent("favouriteBible2"),
            "setfavouritebible3": lambda: self.setFavouriteBibleContent("favouriteBible3"),
            "setstandardabbreviation": self.setStandardAbbreviationContent,
            "setversenosingleclickaction": self.setVerseNoClickActionContent,
            "setversenodoubleclickaction": lambda: self.setVerseNoClickActionContent(True),
        }
        self.session = self.getSession()
        clientIP = self.client_address[0]
        if clientIP not in self.users:
            self.users.append(clientIP)
        if clientIP == self.users[0]:
            self.primaryUser = True
        if self.path == "" or self.path == "/" or self.path.startswith("/index.html"):
            if self.primaryUser or not config.webPresentationMode:
                query_components = parse_qs(urlparse(self.path).query)
                if 'cmd' in query_components:
                    self.command = query_components["cmd"][0].strip()
                    # Convert command shortcut
                    shortcuts = self.getShortcuts()
                    commands = self.getCommands()
                    commandLower = self.command.lower()
                    if not self.command:
                        self.command = config.history["main"][-1]
                    elif commandLower in config.customCommandShortcuts.keys():
                        self.command = config.customCommandShortcuts[commandLower]
                    elif commandLower in shortcuts.keys():
                        self.command = shortcuts[commandLower]
                    elif commandLower in commands.keys():
                        self.command = commands[commandLower]()
                    elif self.command.upper()[1:] in self.getVerseFeatures().keys():
                        self.command = "{0}:::{1}".format(self.command.upper()[1:], self.getCurrentReference())
                    elif self.command.upper()[1:] in self.getChapterFeatures().keys():
                        self.command = "{0}:::{1}".format(self.command.upper()[1:], self.getCurrentReference())
                        self.command = re.sub(":[0-9]+?$", "", self.command)
                    # Parse command
                    if commandLower in (".help", "?"):
                        content = self.helpContent()
                    elif commandLower.startswith(".") and commandLower[1:] in features.keys():
                        content = features[commandLower[1:]]()
                    elif commandLower == ".stop" or self.command == config.httpServerStopCommand:
                        permission, message = self.checkPermission()
                        if permission or (config.httpServerStopCommand and self.command == config.httpServerStopCommand):
                            self.closeWindow()
                            config.enableHttpServer = False
                            return
                        else:
                            content = message
                    elif commandLower == ".restart":
                        permission, message = self.checkPermission()
                        if not permission:
                            content = message
                        else:
                            return self.restartServer()
                    elif commandLower == ".update":
                        permission, message = self.checkPermission()
                        if not permission:
                            content = message
                        else:
                            subprocess.Popen("git pull", shell=True)
                            return self.restartServer("updated and ")
                    else:
                        try:
                            view, content, *_ = self.textCommandParser.parser(self.command, "http")
                        except:
                            content = "Error!"
                        if content == "Downloaded!":
                            content = self.downloadContent()
                        elif not content:
                            content = "Command was processed!"
                        elif not content in ("INVALID_COMMAND_ENTERED", "Error!"):
                            self.textCommandParser.parent.addHistoryRecord(view, self.command)
                else:
                    #self.command = self.abbreviations[str(config.mainB)]
                    self.command = config.history["main"][-1]
                    view, content, dict = self.textCommandParser.parser(self.command, "http")
                content = self.wrapHtml(content)
                if config.bibleWindowContentTransformers:
                    for transformer in config.bibleWindowContentTransformers:
                        content = transformer(content)
                outputFile = os.path.join("htmlResources", "main-{0}.html".format(self.session))
                with open(outputFile, "w", encoding="utf-8") as fileObject:
                    fileObject.write(content)
                if config.httpServerViewerGlobalMode and config.webPresentationMode:
                    url = config.httpServerViewerBaseUrl + "/submit.php"
                    data = {"code": self.session, "content": content}
                    response = requests.post(url, data=json.dumps(data))
                    # print("Submitted data to {0}: {1}".format(url, response))
                self.indexPage()
            else:
                self.mainPage()
        else:
            return super().do_GET()

    def indexPage(self):
        self.commonHeader()
        bcv = (config.mainText, config.mainB, config.mainC, config.mainV)
        activeBCVsettings = """<script>
        var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};
        var tempActiveText = '{0}'; var tempB = {1}; var tempC = {2}; var tempV = {3};
        var toolB = {1}; var toolC = {2}; var toolV = {3};
        var changeVerse = 1;
        var activeBCV = [
        [0], 
        [0, 31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26], 
        [0, 22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38], 
        [0, 17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34], 
        [0, 54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13], 
        [0, 46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12], 
        [0, 18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33], 
        [0, 36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25], 
        [0, 22, 23, 18, 22], 
        [0, 28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13], 
        [0, 27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25], 
        [0, 53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53], 
        [0, 18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30], 
        [0, 54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30], 
        [0, 17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23], 
        [0, 11, 70, 13, 24, 17, 22, 28, 36, 15, 44], 
        [0, 11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31], 
        [0, 22, 23, 15, 17, 14, 14, 10, 17, 32, 3], 
        [0, 22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17], 
        [0, 6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6], 
        [0, 33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31], 
        [0, 18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14], 
        [0, 17, 17, 11, 16, 16, 13, 13, 14], 
        [0, 31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24], 
        [0, 19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34], 
        [0, 22, 22, 66, 22, 22], 
        [0, 28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35], 
        [0, 21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13], 
        [0, 11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9], 
        [0, 20, 32, 21], 
        [0, 15, 16, 15, 13, 27, 14, 17, 14, 15], 
        [0, 21], 
        [0, 17, 10, 10, 11], 
        [0, 16, 13, 12, 13, 15, 16, 20], 
        [0, 15, 13, 19], 
        [0, 17, 20, 19], 
        [0, 18, 15, 20], 
        [0, 15, 23], 
        [0, 21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21], 
        [0, 14, 17, 18, 6], 
        [0, 25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20], 
        [0, 45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20], 
        [0, 80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53], 
        [0, 51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25], 
        [0, 26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 40, 38, 40, 30, 35, 27, 27, 32, 44, 31], 
        [0, 32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27], 
        [0, 31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24], 
        [0, 24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 13], 
        [0, 24, 21, 29, 31, 26, 18], 
        [0, 23, 22, 21, 32, 33, 24], 
        [0, 30, 30, 21, 23], 
        [0, 29, 23, 25, 18], 
        [0, 10, 20, 13, 18, 28], 
        [0, 12, 17, 18], 
        [0, 20, 15, 16, 16, 25, 21], 
        [0, 18, 26, 17, 22], 
        [0, 16, 15, 15], 
        [0, 25], 
        [0, 14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25], 
        [0, 27, 26, 18, 17, 20], 
        [0, 25, 25, 22, 19, 14], 
        [0, 21, 22, 18], 
        [0, 10, 29, 24, 21, 21], 
        [0, 13], 
        [0, 15], 
        [0, 25], 
        [0, 20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 18, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21]
        ];
        </script>""".format(*bcv)
        #fontSize = "{0}px".format(config.fontSize)
        fontFamily = config.font
        collapseFooter = "document.getElementById('bibleFrame').contentWindow.document.getElementById('lastElement').style.height='5px'" if config.webCollapseFooterHeight else ""
        html = """
            <html>
            <head>
                <link rel="icon" href="UniqueBibleApp.png">
                <title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />

                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{9}.css?v=1.020'>
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
                  font-size: 25px;
                {5}

                .sidenav .closebtn {4}
                  position: absolute;
                  top: 0;
                  right: 25px;
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
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/http_server.css?v=1.020'>
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.020'>
                <script src='js/common.js?v=1.020'></script>
                <script src='js/{9}.js?v=1.020'></script>
                <script src='w3.js?v=1.020'></script>
                <script src='js/http_server.js?v=1.020'></script>
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
                      <span id="myMessageHeader"><h2>UniqueBible.app</h2></span>
                    </div>
                    <div class="modal2-body">
                      <span id="myMessage"><p>UniqueBible.app</p></span>
                    </div>
                <!--
                    <div class="modal2-footer">
                      <span id="myMessageFooter"><h3>UniqueBible.app</h3></span>
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

                function openSideNav() {4}
                    document.getElementById("mySidenav").style.width = "250px";
                {5}
                
                function closeSideNav() {4}
                    document.getElementById("mySidenav").style.width = "0";
                {5}

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

    def getSideNavContent(self):
        sideNavItems = (
            (config.thisTranslation["menu5_bible"], ".biblemenu"),
            (config.favouriteBible, "TEXT:::{0}".format(config.favouriteBible)),
            (config.favouriteBible2, "TEXT:::{0}".format(config.favouriteBible2)),
            (config.favouriteBible3, "TEXT:::{0}".format(config.favouriteBible3)),
            (config.thisTranslation["commentaries"], ".commentarymenu"),
            (config.thisTranslation["menu_library"], ".library"),
            (config.thisTranslation["html_timelines"], ".timelineMenu"),
            (config.thisTranslation["menu5_names"], ".names"),
            (config.thisTranslation["menu5_characters"], ".characters"),
            (config.thisTranslation["menu5_locations"], ".maps"),
            (config.thisTranslation["menu5_topics"], ".topics"),
            (config.thisTranslation["bibleHarmonies"], ".parallels"),
            (config.thisTranslation["biblePromises"], ".promises"),
            (config.thisTranslation["menu_search"], ".search"),
            (config.thisTranslation["download"], ".download"),
        )
        html = """<a href="#" onclick="submitCommand('.bible')">{0}</a>""".format(self.parser.bcvToVerseReference(config.mainB, config.mainC, config.mainV))
        for item in sideNavItems:
            html += """<a href="#" onclick="submitCommand('{1}')">{0}</a>""".format(*item)
        html += """<a href="#" onclick="submitCommand('qrcode:::'+window.location.href)">{0}</a>""".format(config.thisTranslation["qrcode"])
        html += """<a href="#">&nbsp;</a>"""
        html += """<a href="#">&nbsp;</a>"""
        return html

    def buildForm(self):
        if self.primaryUser or not config.webPresentationMode:
            if config.webUI == "mini":
                return """
                    <form id="commandForm" action="index.html" action="get">
                    <table class='layout' style='border-collapse: collapse;'><tr>
                    <td class='layout' style='white-space: nowrap;'>{1}&nbsp;</td>
                    <td class='layout' style='width: 100%;'><input type="text" id="commandInput" style="width:100%" name="cmd" value=""/></td>
                    <td class='layout' style='white-space: nowrap;'>&nbsp;{2}&nbsp;{3}&nbsp;{0}</td>
                    </tr></table>
                    </form>
                """.format(
                    self.featureButton(),
                    self.openSideNav(),
                    self.submitButton(),
                    self.helpButton(),
                )
            else:
                return """
                    <form id="commandForm" action="index.html" action="get">
                    {10}&nbsp;&nbsp;{5}&nbsp;&nbsp;{3}&nbsp;&nbsp;{4}&nbsp;&nbsp;{6}&nbsp;&nbsp;{7}&nbsp;&nbsp;
                    {11}&nbsp;&nbsp;{12}{13}{14}{15}&nbsp;&nbsp;{9}&nbsp;&nbsp;{8}&nbsp;&nbsp;{16}
                    <br/><br/>
                    {1}: <input type="text" id="commandInput" style="width:60%" name="cmd" value="{0}"/>
                    <input type="submit" value="{2}"/>
                    </form>
                    """.format(
                    "",
                    config.thisTranslation["menu_command"],
                    config.thisTranslation["run"],
                    self.bibleSelection(),
                    self.bookSelection(),
                    self.previousChapter(),
                    self.currentVerseButton(),
                    self.nextChapter(),
                    self.toggleFullscreen(),
                    self.helpButton(),
                    self.featureButton(),
                    self.libraryButton(),
                    self.searchButton(),
                    "&nbsp;&nbsp;{0}".format(self.favouriteBibleButton(config.favouriteBible)) if config.favouriteBible else "",
                    "&nbsp;&nbsp;{0}".format(self.favouriteBibleButton(config.favouriteBible2)) if config.favouriteBible2 else "",
                    "&nbsp;&nbsp;{0}".format(self.favouriteBibleButton(config.favouriteBible3)) if config.favouriteBible3 else "",
                    self.qrButton(),
                )
        else:
            return ""

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
        html = ("""<!DOCTYPE html><html><head><link rel="icon" href="UniqueBibleApp.png"><title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />"""
                "<style>body {2} font-size: {4}; font-family:'{5}';{3} "
                "zh {2} font-family:'{6}'; {3} "
                "{8} {9}</style>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{7}.css?v=1.020'>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.020'>"
                "<script src='js/common.js?v=1.020'></script>"
                "<script src='js/{7}.js?v=1.020'></script>"
                "<script src='w3.js?v=1.020'></script>"
                "<script src='js/http_server.js?v=1.020'></script>"
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
                "<script src='js/custom.js?v=1.020'></script>"
                "</head><body><span id='v0.0.0'></span>{1}"
                "<p>&nbsp;</p><div id='footer'><span id='lastElement'></span></div><script>loadBible()</script></body></html>"
                ).format(activeBCVsettings,
                         content,
                         "{",
                         "}",
                         fontSize,
                         fontFamily,
                         config.fontChinese,
                         config.theme,
                         self.getHighlightCss(),
                         "")
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

<p><cat>[Book]</cat></p>

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
<p><cat>[Chapter]</cat></p>
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
<p><cat>[Verse]</cat></p>
<navItem class="numPad" onclick="closeNav('navV')">&#8630;</navItem>
<span id="verses"></span>
</div>
  </div>
</div>

<!-- end Verse Selection Interface -->
"""

    def bibleSelection(self):
        return self.formatSelectList("bibleName", "submitTextCommand", self.bibles, config.mainText)

    def bookSelection(self):
        return self.formatSelectList("bookName", "submitBookCommand", self.books, str(config.mainB))

    def formatSelectList(self, id, action, options, selected):
        selectForm = "<select id='{0}' style='width: 100px' onchange='{1}(\"{0}\")'>".format(id, action)
        for value, display in options:
            selectForm += "<option value='{0}' {2}>{1}</option>".format(value, display,
                ("selected='selected'" if value == selected else ""))
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
        html = "<button type='button' onclick='submitCommand(\"{0}\")'>&lt;</button>".format(command)
        return html

    def nextChapter(self):
        newChapter = config.mainC
        if config.mainC < BibleBooks.getLastChapter(config.mainB):
            newChapter += 1
        command = self.parser.bcvToVerseReference(config.mainB, newChapter, 1)
        html = "<button type='button' onclick='submitCommand(\"{0}\")'>&gt;</button>".format(command)
        return html

    def toggleFullscreen(self):
        html = "<button type='button' onclick='fullScreenSwitch()'>+ / -</button>"
        return html

    def openSideNav(self):
        html = "<button type='button' onclick='openSideNav()'>&equiv;</button>"
        return html

    def helpButton(self):
        html = """<button type='button' onclick='submitCommand(".help")'>&quest;</button>"""
        return html

    def submitButton(self):
        html = """<button type='button' onclick='document.getElementById("commandForm").submit();'>&crarr;</button>"""
        return html

    def qrButton(self):
        html = """<button type='button' onclick='submitCommand("qrcode:::"+window.location.href)'>QR</button>"""
        return html

    def featureButton(self):
        #html = """<button type='button' onclick='submitCommand("_menu:::")'>&dagger;</button>"""
        html = """<button type='button' onclick='mod = "KJV"; updateBook("KJV"); openNav("navB");'>&dagger;</button>"""
        return html

    def libraryButton(self):
        html = """<button type='button' onclick='submitCommand(".library")'>{0}</button>""".format(config.thisTranslation["menu_library"])
        return html

    def searchButton(self):
        html = """<button type='button' onclick='submitCommand(".search")'>{0}</button>""".format(config.thisTranslation["menu_search"])
        return html

    def favouriteBibleButton(self, text):
        html = """<button type='button' onclick='submitCommand("TEXT:::{0}")'>{0}</button>""".format(text)
        return html

    def getHighlightCss(self):
        css = ""
        for i in range(len(config.highlightCollections)):
            code = "hl{0}".format(i + 1)
            css += ".{2} {0} background: {3}; {1} ".format("{", "}", code, config.highlightDarkThemeColours[i] if config.theme == "dark" else config.highlightLightThemeColours[i])
        return css

    def checkPermission(self):
        if config.developer or config.webFullAccess:
            return (True, "")
        else:
            return (False, "This feature is available for developers only.  To enable it, set 'developer = True' in file config.py and restart the server.")

    def displayMessage(self, message):
        return """
        <html>
            <head>
                <link rel="icon" href="UniqueBibleApp.png">
                <title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head><body>{0}</body></html>""".format(message)

    def historyContent(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        view, content, *_ = self.textCommandParser.parser("_history:::main", "http")
        return content

    def importContent(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        self.textCommandParser.parser("import:::import", "http")
        return "Processed!"

    def configContent(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
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
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            config.fontSize = config.fontSize + 1
            return self.displayMessage("""<p>Font size changed to {0}!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""".format(config.fontSize))

    def decreaseFontSize(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            if config.fontSize >= 4:
                config.fontSize = config.fontSize - 1
                return self.displayMessage("""<p>Font size changed to {0}!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""".format(config.fontSize))
            else:
                return self.displayMessage("Current font size is already too small!")

    def getBibleChapter(self):
        view, content, *_ = self.textCommandParser.parser(self.getCurrentReference(), "http")
        return content

    def toggleCompareParallel(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            if config.enforceCompareParallel:
                config.enforceCompareParallel = False
                return self.displayMessage("""<p>Compare / parallel mode is turned OFF!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")
            else:
                config.enforceCompareParallel = True
                return self.displayMessage("""<p>Compare / parallel mode is turned ON!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")

    def togglePlainMode(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            config.readFormattedBibles = not config.readFormattedBibles
            return self.getBibleChapter()

    def toggleSubheadings(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            config.addTitleToPlainChapter = not config.addTitleToPlainChapter
            return self.getBibleChapter()

    def toggleRegexCaseSensitive(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            if config.regexCaseSensitive:
                config.regexCaseSensitive = False
                return self.displayMessage("""<p>Option 'case sensitive' is turned off for searching bible with regular expression!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")
            else:
                config.regexCaseSensitive = True
                return self.displayMessage("""<p>Option 'case sensitive' is turned on for searching bible with regular expression!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")

    def togglePresentationMode(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            if config.webPresentationMode:
                config.webPresentationMode = False
                return self.displayMessage("""<p>Option 'presentation mode' is turned off!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")
            else:
                config.webPresentationMode = True
                return self.displayMessage("""<p>Option 'presentation mode' is turned on!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")

    def toggleGlobalViewer(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            if config.httpServerViewerGlobalMode:
                config.httpServerViewerGlobalMode = False
                return self.displayMessage("""<p>Option 'global viewer' is turned off for presentation mode.!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")
            else:
                config.httpServerViewerGlobalMode = True
                return self.displayMessage("""<p>Option 'global viewer' is turned on for presentation mode.!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")

    def swapLayout(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            config.webUI = "" if config.webUI == "mini" else "mini"
            #return self.displayMessage("Layout changed!")
            return self.getBibleChapter()

    def swapTheme(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
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
        dotCommands = """
        <h2>Documentation</h2><p>
        <a target="_blank" href="https://github.com/eliranwong/UniqueBible/wiki">Wiki</a><br>
        <h2>Http-server Commands [case insensitive]</h2>
        <p>
        <ref onclick="displayCommand('.help')">.help</ref> - Display help page with list of available commands.<br>
        <ref onclick="window.parent.submitCommand('.myqrcode')">.myQRcode</ref> - Display a QR code for other users connecting to the same UBA http-server.<br>
        <ref onclick="window.parent.submitCommand('.bible')">.bible</ref> - Open bible chapter.<br>
        <ref onclick="window.parent.submitCommand('.biblemenu')">.bibleMenu</ref> - Open bible menu.<br>
        <ref onclick="window.parent.submitCommand('.commentarymenu')">.commentaryMenu</ref> - Open Commentary menu.<br>
        <ref onclick="window.parent.submitCommand('.timelinemenu')">.timelineMenu</ref> - Open Timeline menu.<br>
        <ref onclick="window.parent.submitCommand('.names')">.names</ref> - Open bible names content page.<br>
        <ref onclick="window.parent.submitCommand('.characters')">.characters</ref> - Open bible characters content page.<br>
        <ref onclick="window.parent.submitCommand('.maps')">.maps</ref> - Open bible maps content page.<br>
        <ref onclick="window.parent.submitCommand('.topics')">.topics</ref> - Open bible topics content page.<br>
        <ref onclick="window.parent.submitCommand('.parallels')">.parallels</ref> - Open bible parallels content page.<br>
        <ref onclick="window.parent.submitCommand('.promises')">.promises</ref> - Open bible promises content page.<br>
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
        dotCommands += """<u>Bible feature shortcut on currently selected book [{0}]</u><br>
        <ref onclick="window.parent.submitCommand('.introduction')">.introduction</ref> - {1}.<br>
        <ref onclick="window.parent.submitCommand('.timelines')">.timelines</ref> - {2}.
        </p><p>""".format(self.abbreviations[str(config.mainB)], config.thisTranslation["html_introduction"], config.thisTranslation["html_timelines"])
        currentChapter = "{0} {1}".format(self.abbreviations[str(config.mainB)], config.mainC)
        dotCommands += "<u>Bible feature shortcut on currently selected chapter [{0}]</u><br>".format(currentChapter)
        dotCommands += "<br>".join(["""<ref onclick="window.parent.submitCommand('.{0}')">.{0}</ref> - {1}.""".format(key.lower(), value) for key, value in self.getChapterFeatures().items()])
        dotCommands += "</p><p>"
        currentVerse = "{0} {1}:{2}".format(self.abbreviations[str(config.mainB)], config.mainC, config.mainV)
        dotCommands += "<u>Bible feature shortcut on currently selected verse [{0}]</u><br>".format(currentVerse)
        dotCommands += "<br>".join(["""<ref onclick="window.parent.submitCommand('.{0}')">.{0}</ref> - {1}.""".format(key.lower(), value) for key, value in self.getVerseFeatures().items()])
        dotCommands += """
        </p><p><b>Developer Options</b></p>
        <p>The following options are enabled only if 'developer' or 'webFullAccess' is set to 'True' in file 'config.py'.  To prevent access to the following features, both configurations need to be set 'False'.  Make sure UBA is not running when 'config.py' is being edited.</p><p>
        <ref onclick="window.parent.submitCommand('.config')">.config</ref> - Display config.py values and their description.<br>
        <ref onclick="window.parent.submitCommand('.history')">.history</ref> - Display history records.<br>
        <ref onclick="window.parent.submitCommand('.import')">.import</ref> - Place third-party resources in directory 'UniqueBible/import/' and run this command to import them into UBA.<br>
        <ref onclick="window.parent.submitCommand('.layout')">.layout</ref> - Swap between available layouts.<br>
        <ref onclick="window.parent.submitCommand('.theme')">.theme</ref> - Swap between available themes.<br>
        <ref onclick="window.parent.submitCommand('.increasefontsize')">.increaseFontSize</ref> - Increase font size.<br>
        <ref onclick="window.parent.submitCommand('.decreasefontsize')">.decreaseFontSize</ref> - Decrease font size.<br>
        <ref onclick="window.parent.submitCommand('.plainmode')">.plainMode</ref> - Toggle 'plain mode' for displaying bible chapters.<br>
        <ref onclick="window.parent.submitCommand('.subheadings')">.subHeadings</ref> - Toggle 'sub-headings' for displaying bible chapters in plain mode.<br>
        <ref onclick="window.parent.submitCommand('.compareparallelmode')">.compareParallelMode</ref> - Toggle 'compare / parallel mode' for bible reading.<br>
        <ref onclick="window.parent.submitCommand('.regexcasesensitive')">.regexCaseSensitive</ref> - Toggle 'case sensitive' for searching bible with regular expression.<br>
        <ref onclick="window.parent.submitCommand('.presentationmode')">.presentationMode</ref> - Toggle 'presentation mode'.<br>
        <ref onclick="window.parent.submitCommand('.globalviewer')">.globalViewer</ref> - Toggle 'global viewer' for presentation mode.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebible')">.setFavouriteBible</ref> - Set configuration 'favouriteBible'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebible2')">.setFavouriteBible2</ref> - Set configuration 'favouriteBible2'.<br>
        <ref onclick="window.parent.submitCommand('.setfavouritebible3')">.setFavouriteBible3</ref> - Set configuration 'favouriteBible3'.<br>
        <ref onclick="window.parent.submitCommand('.setstandardabbreviation')">.setStandardAbbreviation</ref> - Set configuration 'standardAbbreviation'.<br>
        <ref onclick="window.parent.submitCommand('.setversenosingleclickaction')">.setVerseNoSingleClickAction</ref> - Set configuration 'verseNoSingleClickAction'.<br>
        <ref onclick="window.parent.submitCommand('.setversenodoubleclickaction')">.setVerseNoDoubleClickAction</ref> - Set configuration 'verseNoDoubleClickAction'.<br>
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
        from util.DatafileLocation import DatafileLocation
        from util.GithubUtil import GithubUtil
        resources = (
            ("Marvel Datasets", DatafileLocation.marvelData, "marveldata"),
            ("Marvel Bibles", DatafileLocation.marvelBibles, "marvelbible"),
            ("Marvel Commentaries", DatafileLocation.marvelCommentaries, "marvelcommentary"),
            ("Hymn Lyrics", DatafileLocation.hymnLyrics, "hymnlyrics"),
        )
        for collection, data, keyword in resources:
            content += "<h2>{0}</h2>".format(collection)
            for k, v in data.items():
                if os.path.isfile(os.path.join(*v[0])):
                    content += """{0} [{1}]<br>""".format(k, config.thisTranslation["installed"])
                else:
                    content += """<ref onclick="document.title='download:::{1}:::{0}'">{0}</ref><br>""".format(k, keyword)
        resources = (
            ("GitHub Bibles", "GitHubBible", "otseng/UniqueBible_Bibles", (config.marvelData, "bibles"), ".bible"),
            ("GitHub Commentaries", "GitHubCommentary", "darrelwright/UniqueBible_Commentaries", (config.marvelData, "commentaries"), ".commentary"),
            ("GitHub Books", "GitHubBook", "darrelwright/UniqueBible_Books", (config.marvelData, "books"), ".book"),
            ("GitHub Maps", "GitHubMap", "darrelwright/UniqueBible_Maps-Charts", (config.marvelData, "books"), ".book"),
            ("GitHub PDF", "GitHubPdf", "otseng/UniqueBible_PDF", (config.marvelData, "pdf"), ".pdf"),
            ("GitHub EPUB", "GitHubEpub", "otseng/UniqueBible_EPUB", (config.marvelData, "epub"), ".epub"),
        )
        for collection, type, repo, location, extension in resources:
            content += "<h2>{0}</h2>".format(collection)
            for file in GithubUtil(repo).getRepoData():
                if os.path.isfile(os.path.join(*location, file)):
                    content += """{0} [{1}]<br>""".format(file.replace(extension, ""), config.thisTranslation["installed"])
                else:
                    content += """<ref onclick="document.title='download:::{1}:::{0}'">{0}</ref><br>""".format(file.replace(extension, ""), type)
        content += "<h2>Third-party Resources</h2><p><a href='https://github.com/eliranwong/UniqueBible/wiki/Third-party-resources' target='_blank'>Click this link to read our wiki page about third-party resources.</a></p>"
        return content

    def getCurrentReference(self):
        return "{0} {1}:{2}".format(BibleBooks.eng[str(config.mainB)][0], config.mainC, config.mainV)

    def getQrCodeCommand(self):
        if config.httpServerViewerGlobalMode:
            return "QRCODE:::{0}/index.php?code={1}".format(config.httpServerViewerBaseUrl, self.session)
        else:
            return "QRCODE:::server"

    def libraryContent(self):
        content = ""
        reference = self.getCurrentReference()
        content += """<h2><ref onclick="window.parent.submitCommand('.commentarymenu')">Commentary</ref></h2>"""
        content += "<br>".join(["""<ref onclick ="document.title = 'COMMENTARY:::{0}:::{1}'">{2}</ref>""".format(abb, reference, self.textCommandParser.parent.commentaryFullNameList[index]) for index, abb in enumerate(self.textCommandParser.parent.commentaryList)])
        content += "<h2>Reference Book</h2>"
        content += "<br>".join(["""<ref onclick ="document.title = 'BOOK:::{0}'">{0}</ref>""".format(book) for book in self.textCommandParser.parent.referenceBookList])
        return content

    def setVerseNoClickActionContent(self, double=False):
        values = ("_noAction", "COMPARE", "CROSSREFERENCE", "TSKE", "TRANSLATION", "DISCOURSE", "WORDS", "COMBO", "INDEX", "COMMENTARY", "_menu")
        features = ("noAction", "menu4_compareAll", "menu4_crossRef", "menu4_tske", "menu4_traslations", "menu4_discourse", "menu4_words", "menu4_tdw", "menu4_indexes", "menu4_commentary", "classicMenu")
        items = [config.thisTranslation[feature] for feature in features]
        content = "<h2>Select Verse Number Single-click Action:</h2>"
        content += "<br>".join(["""<ref onclick ="document.title = '_setconfig:::{2}:::\\'{0}\\''">{1}</ref>""".format(value, items[index], "verseNoDoubleClickAction" if double else "verseNoSingleClickAction") for index, value in enumerate(values)])
        return content

    def setFavouriteBibleContent(self, favouriteBible="favouriteBible"):
        content = "<h2>Select Faviourite Bible:</h2>"
        content += "<br>".join(["""<ref onclick ="document.title = '_setconfig:::{2}:::\\'{0}\\''">{1}</ref>""".format(abb, self.textCommandParser.parent.textFullNameList[index], favouriteBible) for index, abb in enumerate(self.textCommandParser.parent.textList)])
        return content

    def setStandardAbbreviationContent(self):
        options = (
            ("ENG", "English"),
            ("TC", "Traditional Chinese"),
            ("SC", "Simplified Chinese"),
        )
        content = "<h2>Select Standard Abbreviation:</h2>"
        content += "<br>".join(["""<ref onclick ="document.title = '_setconfig:::standardAbbreviation:::\\'{0}\\''">{1}</ref>""".format(code, language) for code, language in options])
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
        content += """<h2>Bible Versions</h2><p><ref onclick="document.title='_menu:::'">Click HERE to Search Bibles</ref></p>"""
        abbList = ["HBN", "EXLBP", "EXLBL"]
        nameList = ["Bible Names", "Bible Characters", "Bible Locations"]
        content += self.formatSearchSection("Bible Background", "SEARCHTOOL", "SEARCHTOOL", abbList, nameList)
        abbList = ["Bible_Promises", "Harmonies_and_Parallels", "FAV", "ALL"]
        nameList = ["Bible Promises", "Harmonies and Parallels", "Favourite Books", "All Books"]
        content += self.formatSearchSection("Collections", "collection", "SEARCHBOOK", abbList, nameList)
        content += self.formatSearchSection("Topics", "topics", "SEARCHTOOL", self.textCommandParser.parent.topicListAbb, self.textCommandParser.parent.topicList)
        content += self.formatSearchSection("Dictionary", "dictionary", "SEARCHTOOL", self.textCommandParser.parent.dictionaryListAbb, self.textCommandParser.parent.dictionaryList)
        content += self.formatSearchSection("Encyclopedia", "encyclopedia", "SEARCHTOOL", self.textCommandParser.parent.encyclopediaListAbb, self.textCommandParser.parent.encyclopediaList)
        content += self.formatSearchSection("Concordance", "CONCORDANCE", "CONCORDANCE", self.textCommandParser.parent.strongBibles)
        content += self.formatSearchSection("Lexicon", "LEXICON", "LEXICON", self.textCommandParser.parent.lexiconList)
        content += self.formatSearchSection("Books", "SEARCHBOOK", "SEARCHBOOK", self.textCommandParser.parent.referenceBookList)
        content += self.formatSearchSection("Third Party Dictionaries", "SEARCHTHIRDDICTIONARY", "SEARCHTHIRDDICTIONARY", self.textCommandParser.parent.thirdPartyDictionaryList)
        return content

    def getSession(self):
        headers = {x: y for x, y in self.headers._headers}
        ip = self.client_address[0]
        browser = headers['User-Agent']
        session = str(ip + browser).encode('utf-8')
        session = hashlib.sha256(session).hexdigest()[:30]
        return session
