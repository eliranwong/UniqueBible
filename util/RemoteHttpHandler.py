# https://docs.python.org/3/library/http.server.html
# https://ironpython-test.readthedocs.io/en/latest/library/simplehttpserver.html
import hashlib
import json
import os, re, config, pprint, glob
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
from urllib.parse import urlparse, parse_qs
from util.FileUtil import FileUtil
from util.LanguageUtil import LanguageUtil
from pathlib import Path


class RemoteHttpHandler(SimpleHTTPRequestHandler):

    parser = None
    textCommandParser = None
    bibles = None
    books = None
    bookMap = None
    abbreviations = None
    session = None
    users = []
    adminUsers = []

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
        self.adminUsers = RemoteHttpHandler.adminUsers
        self.primaryUser = False
        if config.httpServerViewerGlobalMode:
            try:
                urllib.request.urlopen(config.httpServerViewerBaseUrl)
            except:
                config.httpServerViewerGlobalMode = False
        if not hasattr(config, "setMainVerse"):
            config.setMainVerse = False
        super().__init__(*args, directory="htmlResources", **kwargs)

    def getCommands(self):
        return {
            ".myqrcode": self.getQrCodeCommand,
            #".bible": self.getCurrentReference,
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

    def updateData(self):
        # Check language
        # Traditional Chinese
        if config.webPrivateHomePage and self.path.startswith("/{0}.html".format(config.webPrivateHomePage)):
            config.displayLanguage = "en_GB"
            config.standardAbbreviation = "ENG"
            config.webHomePage = "{0}.html".format(config.webPrivateHomePage)
            self.path = re.sub("^/{0}.html".format(config.webPrivateHomePage), "/index.html", self.path)
            self.initialCommand = "BIBLE:::{0}:::John 3:16".format(self.getFavouriteBible())
        elif self.path.startswith("/traditional.html"):
            config.displayLanguage = "zh_HANT"
            config.standardAbbreviation = "TC"
            config.webHomePage = "traditional.html"
            self.path = re.sub("^/traditional.html", "/index.html", self.path)
            self.initialCommand = "BIBLE:::{0}:::約翰福音 3:16".format(self.getFavouriteBible())
        # Simplified Chinese
        elif self.path.startswith("/simplified.html"):
            config.displayLanguage = "zh_HANS"
            config.standardAbbreviation = "SC"
            config.webHomePage = "simplified.html"
            self.path = re.sub("^/simplified.html", "/index.html", self.path)
            self.initialCommand = "BIBLE:::{0}:::约翰福音 3:16".format(self.getFavouriteBible())
        # Default English
        else:
            config.displayLanguage = "en_GB"
            config.standardAbbreviation = "ENG"
            config.webHomePage = "index.html"
            self.initialCommand = "BIBLE:::{0}:::John 3:16".format(self.getFavouriteBible())
        config.marvelData = config.marvelDataPrivate if config.webHomePage == "{0}.html".format(config.webPrivateHomePage) else config.marvelDataPublic
        self.textCommandParser.parent.setupResourceLists()
        config.thisTranslation = LanguageUtil.loadTranslation(config.displayLanguage)
        self.parser = BibleVerseParser(config.parserStandarisation)
        self.abbreviations = self.parser.standardAbbreviation
        if config.webPrivateHomePage:
            self.bibles = [(bible, bible) for bible in BiblesSqlite().getBibleList()]

    def do_GET(self):
        self.clientIP = self.client_address[0]
        self.session = self.getSession()
        if self.clientIP not in self.users:
            self.users.append(self.clientIP)
        if self.clientIP == self.users[0]:
            self.primaryUser = True
        self.updateData()
        if self.path == "" or self.path == "/" or self.path.startswith("/index.html") or config.displayLanguage != "en_GB":
            self.loadContent()
        else:
            return super().do_GET()

    def loadContent(self):
        features = {
            "config": self.configContent,
            "download": self.downloadContent,
            "history": self.historyContent,
            "import": self.importContent,
            "latest": self.latestContent,
            "layout": self.swapLayout,
            "library": self.libraryContent,
            "logout": self.logout,
            "search": self.searchContent,
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
            "setfavouritebibletc": lambda: self.setFavouriteBibleContent("favouriteBibleTC"),
            "setfavouritebibletc2": lambda: self.setFavouriteBibleContent("favouriteBibleTC2"),
            "setfavouritebibletc3": lambda: self.setFavouriteBibleContent("favouriteBibleTC3"),
            "setfavouritebiblesc": lambda: self.setFavouriteBibleContent("favouriteBibleSC"),
            "setfavouritebiblesc2": lambda: self.setFavouriteBibleContent("favouriteBibleSC2"),
            "setfavouritebiblesc3": lambda: self.setFavouriteBibleContent("favouriteBibleSC3"),
            "setversenosingleclickaction": self.setVerseNoClickActionContent,
            "setversenodoubleclickaction": lambda: self.setVerseNoClickActionContent(True),
            "setwebubaicon": self.setWebUBAIconContent,
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
                         )
        if self.primaryUser or not config.webPresentationMode:
            query_components = parse_qs(urlparse(self.path).query)
            self.initialCommandInput = ""
            initialCommand = self.initialCommand if config.webPublicVersion else config.history["main"][-1]
            if 'cmd' in query_components:
                self.command = query_components["cmd"][0].strip()
                # Convert command shortcut
                commandFunction = ""
                commandParam = ""
                if self.command.startswith(".") and ":::" in self.command:
                    commandFunction, commandParam = self.command.split(":::", 1)
                    commandFunction = commandFunction.lower()
                shortcuts = self.getShortcuts()
                commands = self.getCommands()
                commandLower = self.command.lower()
                if not self.command:
                    self.command = initialCommand
                    self.initialCommandInput = initialCommand
                    commandLower = initialCommand.lower()
                elif commandLower in config.customCommandShortcuts.keys():
                    self.command = config.customCommandShortcuts[commandLower]
                elif commandLower in shortcuts.keys():
                    self.command = shortcuts[commandLower]
                elif commandLower in commands.keys():
                    self.command = commands[commandLower]()
                #elif self.command.upper()[1:] in self.getVerseFeatures().keys():
                    #self.command = "{0}:::{1}".format(self.command.upper()[1:], self.getCurrentReference())
                elif self.command.upper()[1:] in self.getChapterFeatures().keys():
                    self.command = "{0}:::{1}".format(self.command.upper()[1:], self.getCurrentReference())
                    self.command = re.sub(":[0-9]+?$", "", self.command)
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
                        view, content, *_ = self.textCommandParser.parser(self.command, "http")
                    except:
                        content = "Error!"
                    if tempDeveloper:
                        config.developer = False
                    if content == "Downloaded!":
                        content = self.downloadContent()
                    elif not content:
                        content = "No content for display!"
                    elif not content in ("INVALID_COMMAND_ENTERED", "Error!", "No content for display!"):
                        self.textCommandParser.parent.addHistoryRecord(view, self.command)
            else:
                self.command = initialCommand
                self.initialCommandInput = initialCommand
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
            cookie = """document.cookie = "lastVerse={0}"; 
            document.cookie = "lastBookName={0}"; 
            document.cookie = "lastChapterNumber={0}"; 
            document.cookie = "lastVerseNumber={0}"; 
            """.format(self.getCurrentReference(), self.abbreviations[str(config.mainB)], config.mainC, config.mainV)
            config.setMainVerse = False
        else:
            cookie = ""
        #cookie = """document.cookie = "lastVerse={0}";""".format(self.getCurrentReference())
        html = """
            <html>
            <head>
                <link rel="icon" href="icons/{20}">
                <title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />

                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{9}.css?v=1.033'>
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
                  font-size: 25px;
                {5}

                #navBtns {4}
                  position: absolute;
                  top: 20;
                  left: 70px;
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
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/http_server.css?v=1.033'>
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.033'>
                <script src='js/common.js?v=1.023'></script>
                <script src='js/{9}.js?v=1.023'></script>
                <script src='w3.js?v=1.023'></script>
                <script src='js/http_server.js?v=1.023'></script>
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

                function openCommandInNewWindow() {4}
                    cmd = encodeURI(document.getElementById('commandInput').value);
                    var url;
                    if (cmd == "") {4}
                        url = "{19}";
                    {5} else {4}
                        url = "{19}?cmd="+cmd;
                    {5}
                    window.open(url, "_blank");
                {5}

                // Open and close side navigation bar
                function openSideNav() {4}
                    document.getElementById("mySidenav").style.width = "250px";
                {5}
                function closeSideNav() {4}
                    document.getElementById("mySidenav").style.width = "0";
                {5}
                document.querySelector('#commandInput').addEventListener('click', closeSideNav);
                {21}
                document.getElementById("lastVerse").innerHTML = getLastVerse();
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
            cookie,
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
        html = """<div id="navBtns">{0} {1} {2}</div>""".format(self.previousChapter(), self.passageSelectionButton(), self.nextChapter())
        #html += """<a href="#" onclick="submitCommand('.bible')">{0}</a>""".format(self.parser.bcvToVerseReference(config.mainB, config.mainC, config.mainV))
        html += """<a href="#" onclick="submitCommand('.bible')"><span id="lastVerse"></span></a>"""
        html += """<a href="#">{0}</a>""".format(self.verseActiionSelection())
        html += """<a href="#">{0}</a>""".format(self.bibleSelectionSide())
        sideNavItems = (
            (self.getFavouriteBible(), "TEXT:::{0}".format(self.getFavouriteBible())),
            (self.getFavouriteBible2(), "TEXT:::{0}".format(self.getFavouriteBible2())),
            (self.getFavouriteBible3(), "TEXT:::{0}".format(self.getFavouriteBible3())),
        )
        for item in sideNavItems:
            html += """<a href="#" onclick="submitCommand('{1}')">{0}</a>""".format(*item)
        html += "<hr>"
        sideNavItems = (
            ("{0} &#x1F50E;&#xFE0E;".format(config.thisTranslation["menu5_bible"]), ".biblemenu"),
            (config.thisTranslation["commentaries"], ".commentarymenu"),
            (config.thisTranslation["menu_library"], ".library"),
            (config.thisTranslation["html_timelines"], ".timelineMenu"),
            (config.thisTranslation["menu5_names"], ".names"),
            (config.thisTranslation["menu5_characters"], ".characters"),
            (config.thisTranslation["menu5_locations"], ".maps"),
            (config.thisTranslation["menu5_topics"], ".topics"),
            (config.thisTranslation["bibleHarmonies"], ".parallels"),
            (config.thisTranslation["biblePromises"], ".promises"),
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
        html += """<a href="#">&nbsp;</a>"""
        html += """<a href="#">&nbsp;</a>"""
        return html

    def getOrganisationIcon(self):
        if config.webOrganisationIcon and config.webOrganisationLink:
            print(999)
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
                    <td class='layout' style='width: 100%;'><input type="search" autocomplete="on" id="commandInput" style="width:100%" name="cmd" value="{5}"/></td>
                    <td class='layout' style='white-space: nowrap;'>&nbsp;{2}&nbsp;{6}&nbsp;{3}&nbsp;{0}</td>
                    </tr></table>
                    </form>
                """.format(
                    self.passageSelectionButton(),
                    self.openSideNav(),
                    self.submitButton(),
                    self.qrButton(),
                    config.webHomePage,
                    self.initialCommandInput.replace('"', '\\"'),
                    self.newWindowButton(),
                )
            else:
                return """
                    <form id="commandForm" action="{0}" action="get">
                    {10}&nbsp;&nbsp;{5}&nbsp;&nbsp;{3}&nbsp;&nbsp;{4}&nbsp;&nbsp;{6}&nbsp;&nbsp;{7}&nbsp;&nbsp;
                    {11}&nbsp;&nbsp;{12}{13}{14}{15}&nbsp;&nbsp;{8}&nbsp;&nbsp;{16}&nbsp;&nbsp;{19}&nbsp;&nbsp;{9}
                    <br/><br/>
                    <span onclick="focusCommandInput()">{1}</span>:
                    <input type="search" autocomplete="on" id="commandInput" style="width:60%" name="cmd" value="{17}"/>
                    {2}&nbsp;&nbsp;{18}
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
                    self.initialCommandInput.replace('"', '\\"'),
                    self.newWindowButton(),
                    self.internalHelpButton(),
                )
        else:
            return ""

    def getFavouriteBible(self):
        if config.webHomePage == "traditional.html":
            return config.favouriteBibleTC
        elif config.webHomePage == "simplified.html":
            return config.favouriteBibleSC
        else:
            return config.favouriteBible

    def getFavouriteBible2(self):
        if config.webHomePage == "traditional.html":
            return config.favouriteBibleTC2
        elif config.webHomePage == "simplified.html":
            return config.favouriteBibleSC2
        else:
            return config.favouriteBible2

    def getFavouriteBible3(self):
        if config.webHomePage == "traditional.html":
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
        html = ("""<!DOCTYPE html><html><head><link rel="icon" href="icons/{9}"><title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />"""
                "<style>body {2} font-size: {4}; font-family:'{5}';{3} "
                "zh {2} font-family:'{6}'; {3} "
                "{8}</style>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{7}.css?v=1.033'>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.033'>"
                "<script src='js/common.js?v=1.023'></script>"
                "<script src='js/{7}.js?v=1.023'></script>"
                "<script src='w3.js?v=1.023'></script>"
                "<script src='js/http_server.js?v=1.023'></script>"
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
                "<script src='js/custom.js?v=1.023'></script>"
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
                         config.webUBAIcon,)
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
        return self.formatSelectList("bookName", "submitBookCommand", self.books, str(config.mainB))

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
        html = "<button type='button' title='{1}' onclick='submitCommand(\"{0}\")'>&lt;</button>".format(command, config.thisTranslation["menu4_previous"])
        return html

    def nextChapter(self):
        newChapter = config.mainC
        if config.mainC < BibleBooks.getLastChapter(config.mainB):
            newChapter += 1
        command = self.parser.bcvToVerseReference(config.mainB, newChapter, 1)
        html = "<button type='button' title='{1}' onclick='submitCommand(\"{0}\")'>&gt;</button>".format(command, config.thisTranslation["menu4_next"])
        return html

    def toggleFullscreen(self):
        html = "<button type='button' title='{0}' onclick='fullScreenSwitch()'>+ / -</button>".format(config.thisTranslation["menu1_fullScreen"])
        return html

    def openSideNav(self):
        html = "<button type='button' title='{0}' onclick='openSideNav()'>&equiv;</button>".format(config.thisTranslation["menu_bibleMenu"])
        return html

    def getUserManual(self):
        if config.webHomePage in ("traditional.html", "simplified.html"):
            userManual = r"https://www.uniquebible.app/web/%E4%B8%AD%E6%96%87%E8%AA%AA%E6%98%8E"
        else:
            userManual = "https://www.uniquebible.app/web/english-manual"
        return userManual

    def internalHelpButton(self):
        html = """<button type='button' title='{0}' onclick='submitCommand(".help")'>&#9679;</button>""".format(config.thisTranslation["ubaCommands"])
        return html

    def externalHelpButton(self):
        #html = """<button type='button' title='{0}' onclick='submitCommand(".help")'>&quest;</button>""".format(config.thisTranslation["userManual"])
        html = """<button type='button' title='{0}' onclick='window.open("{1}", "_blank")'>&quest;</button>""".format(config.thisTranslation["userManual"], self.getUserManual())
        return html

    def submitButton(self):
        html = """<button type='button' title='{0}' onclick='document.getElementById("commandForm").submit();'>&crarr;</button>""".format(config.thisTranslation["enter"])
        return html

    def qrButton(self):
        html = """<button type='button' title='{0}' onclick='submitCommand("qrcode:::"+window.location.href)'>&#9641;</button>""".format(config.thisTranslation["qrcode"])
        return html

    def passageSelectionButton(self):
        html = """<button type='button' title='{1}' onclick='mod = "KJV"; updateBook("KJV", "{0}"); openNav("navB");'>&dagger;</button>""".format(config.webHomePage, config.thisTranslation["bibleNavigation"])
        return html

    def libraryButton(self):
        html = """<button type='button' onclick='submitCommand(".library")'>{0}</button>""".format(config.thisTranslation["menu_library"])
        return html

    def searchButton(self):
        html = """<button type='button' onclick='submitCommand(".search")'>{0}</button>""".format(config.thisTranslation["menu_search"])
        return html

    def newWindowButton(self):
        html = """<button type='button' title='{0}' onclick='openCommandInNewWindow()'>&#8663;</button>""".format(config.thisTranslation["openOnNewWindow"])
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
        if config.developer or config.webFullAccess or self.clientIP in self.adminUsers:
            return (True, "")
        else:
            return (False, config.thisTranslation["loginAdmin"])

    def displayMessage(self, message):
        return """
        <html>
            <head>
                <link rel="icon" href="icons/{1}">
                <title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head><body>{0}</body></html>""".format(message, config.webUBAIcon)

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
        view, content, *_ = self.textCommandParser.parser(self.getCurrentReference(), "http")
        return content

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

    def toggleSubheadings(self):
        config.addTitleToPlainChapter = not config.addTitleToPlainChapter
        return self.getBibleChapter()

    def toggleRegexCaseSensitive(self):
        if config.regexCaseSensitive:
            config.regexCaseSensitive = False
            return self.displayMessage("""<p>Option 'case sensitive' is turned off for searching bible with regular expression!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")
        else:
            config.regexCaseSensitive = True
            return self.displayMessage("""<p>Option 'case sensitive' is turned on for searching bible with regular expression!</p><p><ref onclick="window.parent.submitCommand('.bible')">Open Bible</ref></p>""")

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
        dotCommands = """
        <h2>Commands</h2>
        <p>Unique Bible App supports single-line commands to navigate or interact between resources.  This page documents available commands.  Web version commands are supported on UBA web version only.  UBA commands are shared by both desktop and web versions, though some UBA commands apply to desktop version only.</p>
        <h2>Web Version Commands [case insensitive]</h2>
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
        dotCommands += """<u>Study currently selected book [{0}]</u><br>
        <ref onclick="window.parent.submitCommand('.introduction')">.introduction</ref> - {1}.<br>
        <ref onclick="window.parent.submitCommand('.timelines')">.timelines</ref> - {2}.
        </p><p>""".format(self.abbreviations[str(config.mainB)], config.thisTranslation["html_introduction"], config.thisTranslation["html_timelines"])
        currentChapter = "{0} {1}".format(self.abbreviations[str(config.mainB)], config.mainC)
        dotCommands += "<u>Study currently selected chapter [{0}]</u><br>".format(currentChapter)
        dotCommands += "<br>".join(["""<ref onclick="window.parent.submitCommand('.{0}')">.{0}</ref> - {1}.""".format(key.lower(), value) for key, value in self.getChapterFeatures().items()])
        dotCommands += "</p><p>"
        currentVerse = "{0} {1}:{2}".format(self.abbreviations[str(config.mainB)], config.mainC, config.mainV)
        dotCommands += "<u>Study currently selected verse [{0}]</u><br>".format(currentVerse)
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
        <ref onclick="window.parent.submitCommand('.subheadings')">.subHeadings</ref> - Toggle 'sub-headings' for displaying bible chapters in plain mode.<br>
        <ref onclick="window.parent.submitCommand('.compareparallelmode')">.compareParallelMode</ref> - Toggle 'compare / parallel mode' for bible reading.<br>
        <ref onclick="window.parent.submitCommand('.regexcasesensitive')">.regexCaseSensitive</ref> - Toggle 'case sensitive' for searching bible with regular expression.<br>
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
                    content += """<ref onclick="document.title='download:::{0}:::{1}'">{2}</ref><br>"""\
                        .format(keyword, k.replace("'", "\\'"), k)
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
        return "{0} {1}:{2}".format(self.abbreviations[str(config.mainB)], config.mainC, config.mainV)

    def getQrCodeCommand(self):
        if config.httpServerViewerGlobalMode:
            return "QRCODE:::{0}/index.php?code={1}".format(config.httpServerViewerBaseUrl, self.session)
        else:
            return "QRCODE:::server"

    def libraryContent(self):
        self.textCommandParser.parent.setupResourceLists()
        content = ""
        reference = self.getCurrentReference()
        content += """<h2><ref onclick="window.parent.submitCommand('.commentarymenu')">{0}</ref></h2>""".format(config.thisTranslation["menu4_commentary"])
        content += "<br>".join(["""<ref onclick ="document.title = 'COMMENTARY:::{0}:::{1}'">{2}</ref>""".format(abb, reference, self.textCommandParser.parent.commentaryFullNameList[index]) for index, abb in enumerate(self.textCommandParser.parent.commentaryList)])
        content += "<h2>{0}</h2>".format(config.thisTranslation["menu5_selectBook"])
        content += "<br>".join(["""<ref onclick ="document.title = 'BOOK:::{0}'">{0}</ref>""".format(book) for book in self.textCommandParser.parent.referenceBookList])
        content += "<h2>PDF {0}</h2>".format(config.thisTranslation["file"])
        content += "<br>".join(["""<ref onclick ="document.title = 'PDF:::{0}'">{0}</ref>""".format(book)
            for book in self.textCommandParser.parent.pdfList])
        content += "<h2>EPUB {0}</h2>".format(config.thisTranslation["file"])
        content += "<br>".join(["""<ref onclick ="document.title = 'EPUB:::{0}'">{0}</ref>""".format(book)
            for book in self.textCommandParser.parent.epubList])
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
        content = "<h2>Select UniqueBible.app Icon:</h2>"
        content += " ".join(["""<ref onclick ="document.title = '_setconfig:::webUBAIcon:::\\'{0}\\''"><img src="icons/{0}"></ref>""".format(file) for file in files])
        return content

    def setFavouriteBibleContent(self, favouriteBible="favouriteBible"):
        content = "<h2>Select Faviourite Bible:</h2>"
        content += "<br>".join(["""<ref onclick ="document.title = '_setconfig:::{2}:::\\'{0}\\''">{1}</ref>""".format(abb, self.textCommandParser.parent.textFullNameList[index], favouriteBible) for index, abb in enumerate(self.textCommandParser.parent.textList)])
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
        abbList = ["HBN", "EXLBP", "EXLBL"]
        nameList = ["Bible Names", "Bible Characters", "Bible Locations"]
        content += self.formatSearchSection(config.thisTranslation["bibleBackground"], "SEARCHTOOL", "SEARCHTOOL", abbList, nameList)
        abbList = ["Bible_Promises", "Harmonies_and_Parallels", "FAV", "ALL"]
        nameList = ["Bible Promises", "Harmonies and Parallels", "Favourite Books", "All Books"]
        content += self.formatSearchSection(config.thisTranslation["collection"], "collection", "SEARCHBOOK", abbList, nameList)
        content += self.formatSearchSection(config.thisTranslation["menu5_topics"], "topics", "SEARCHTOOL", self.textCommandParser.parent.topicListAbb, self.textCommandParser.parent.topicList)
        content += self.formatSearchSection(config.thisTranslation["context1_dict"], "dictionary", "SEARCHTOOL", self.textCommandParser.parent.dictionaryListAbb, self.textCommandParser.parent.dictionaryList)
        content += self.formatSearchSection(config.thisTranslation["context1_encyclopedia"], "encyclopedia", "SEARCHTOOL", self.textCommandParser.parent.encyclopediaListAbb, self.textCommandParser.parent.encyclopediaList)
        content += self.formatSearchSection(config.thisTranslation["bibleConcordance"], "CONCORDANCE", "CONCORDANCE", self.textCommandParser.parent.strongBibles)
        content += self.formatSearchSection(config.thisTranslation["menu5_lexicon"], "LEXICON", "LEXICON", self.textCommandParser.parent.lexiconList)
        content += self.formatSearchSection(config.thisTranslation["installBooks"], "SEARCHBOOK", "SEARCHBOOK", self.textCommandParser.parent.referenceBookList)
        content += self.formatSearchSection(config.thisTranslation["menu5_3rdDict"], "SEARCHTHIRDDICTIONARY", "SEARCHTHIRDDICTIONARY", self.textCommandParser.parent.thirdPartyDictionaryList)
        return content

    def getSession(self):
        headers = {x: y for x, y in self.headers._headers}
        ip = self.client_address[0]
        browser = headers['User-Agent']
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
