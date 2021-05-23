# https://docs.python.org/3/library/http.server.html
# https://ironpython-test.readthedocs.io/en/latest/library/simplehttpserver.html
import os, re, config, pprint
import subprocess
from http.server import SimpleHTTPRequestHandler
from time import gmtime

from BibleBooks import BibleBooks
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite
from TextCommandParser import TextCommandParser
from util.RemoteCliMainWindow import RemoteCliMainWindow
from urllib.parse import urlparse
from urllib.parse import parse_qs
from util.FileUtil import FileUtil
from util.NetworkUtil import NetworkUtil

class RemoteHttpHandler(SimpleHTTPRequestHandler):

    parser = None
    textCommandParser = None
    bibles = None
    books = None
    abbreviations = None
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
        self.books = RemoteHttpHandler.books
        self.users = RemoteHttpHandler.users
        self.primaryUser = False
        super().__init__(*args, directory="htmlResources", **kwargs)

    def getShortcuts(self):
        return {
            ".myqrcode": "qrcode:::server",
            ".bible": self.getCurrentReference(),
            ".biblemenu": "_menu:::",
            ".commentarymenu": "_commentary:::{0}".format(config.commentaryText),
            ".timelinemenu": "BOOK:::Timelines",
            ".maps": "SEARCHTOOL:::EXLBL:::",
            ".characters": "SEARCHTOOL:::EXLBP:::",
            ".names": "SEARCHTOOL:::HBN:::",
            ".promises": "BOOK:::Bible_Promises",
            ".parallels": "BOOK:::Harmonies_and_Parallels",
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
            "increasefontsize": self.increaseFontSize,
            "decreasefontsize": self.decreaseFontSize,
        }
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
                    if not self.command:
                        self.command = config.history["main"][-1]
                    elif self.command.lower() in shortcuts.keys():
                        self.command = shortcuts[self.command.lower()]
                    elif self.command.upper()[1:] in self.getVerseFeatures().keys():
                        self.command = "{0}:::{1}".format(self.command.upper()[1:], self.getCurrentReference())
                    elif self.command.upper()[1:] in self.getChapterFeatures().keys():
                        self.command = "{0}:::{1}".format(self.command.upper()[1:], self.getCurrentReference())
                        self.command = re.sub(":[0-9]+?$", "", self.command)
                    # Parse command
                    if self.command.lower() in (".help", "?"):
                        content = self.helpContent()
                    elif self.command.lower().startswith(".") and self.command.lower()[1:] in features.keys():
                        content = features[self.command.lower()[1:]]()
                    elif self.command.lower() == ".stop":
                        permission, message = self.checkPermission()
                        if not permission:
                            content = message
                        else:
                            self.closeWindow()
                            config.enableHttpServer = False
                            return
                    elif self.command.lower() == ".restart":
                        permission, message = self.checkPermission()
                        if not permission:
                            content = message
                        else:
                            return self.restartServer()
                    elif self.command.lower() == ".update":
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
                        if not content:
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
                outputFile = os.path.join("htmlResources", "main.html")
                with open(outputFile, "w", encoding="utf-8") as fileObject:
                    fileObject.write(content)
                self.indexPage()
            else:
                self.mainPage()
        else:
            return super().do_GET()

    def indexPage(self):
        self.commonHeader()
        bcv = (config.mainText, config.mainB, config.mainC, config.mainV)
        activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(*bcv)
        fontSize = "{0}px".format(config.fontSize)
        fontFamily = config.font

        html = """
            <html>
            <head>
                <title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />

                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{9}.css?v=1.007'>
                <style>
                ::-webkit-scrollbar {4}
                  display: none;
                {5}
                ::-webkit-scrollbar-button {4}
                  display: none;
                {5}
                body {4}
                  {6}
                  font-family:'{7}';
                  -ms-overflow-style:none;
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
                {10} {11}
                </style>
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/http_server.css?v=1.007'>
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.007'>
                <script src='js/common.js?v=1.007'></script>
                <script src='js/{9}.js?v=1.007'></script>
                <script src='w3.js?v=1.007'></script>
                <script src='js/http_server.js?v=1.007'></script>
                <script>
                var queryString = window.location.search;	
                queryString = queryString.substring(1);
                var curPos;
                var tempActiveText; var tempB; var tempC; var tempV;
                var para = 2; var annoClause = 1; var annoPhrase = 1; var highlights = 1;
                var paraWin = 1; var syncBible = 1; var paraContent = ''; var triggerPara = 0;
                var currentZone; var currentB; var currentC; var currentV;
                var fullScreen = 0; var toolDivLoaded = 0; var landscape;
                var toolB; var toolC; var toolV;
                </script>
                {3}
                <script>
                var versionList = []; var compareList = []; var parallelList = []; 
                var diffList = []; var searchList = [];
                </script>

            </head>
            <body style="padding-top: 10px;" onload="onBodyLoad()" ontouchstart="">
                <span id='v0.0.0'></span>
                {0}
                <div id="content">
                    <div id="bibleDiv" onscroll="scrollBiblesIOS(this.id)">
                        <iframe id="bibleFrame" name="main-{2}" onload="resizeSite()" width="100%" height="{1}%" src="main.html">Oops!</iframe>
                    </div>
                    <div id="toolDiv" onscroll="scrollBiblesIOS(this.id)">
                        <iframe id="toolFrame" name="tool-{2}" onload="resizeSite()" src="empty.html">Oops!</iframe>
                    </div>
                </div>

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
                </script>
            </body>
            </html>
        """.format(
            self.buildForm(),
            95 if config.webUI == "mini" else 85,
            gmtime(),
            activeBCVsettings,
            "{",
            "}",
            "", #"font-size: {0};".format(fontSize),
            fontFamily,
            config.fontChinese,
            config.theme,
            self.getHighlightCss(),
            "",
        )
        self.wfile.write(bytes(html, "utf8"))

    def mainPage(self):
        self.commonHeader()
        html = open(os.path.join("htmlResources", "main.html"), 'r').read()
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

    def buildForm(self):
        if self.primaryUser or not config.webPresentationMode:
            if config.webUI == "mini":
                return """
                    <form id="commandForm" action="index.html" action="get">
                    {1} <input type="text" id="commandInput" style="width:60%" name="cmd" value="{0}"/>
                    <input type="submit" value="{2}"/> {3} {4}
                    </form>
                """.format(
                    "",
                    self.toggleFullscreen(),
                    config.thisTranslation["run"],
                    self.helpButton(),
                    self.featureButton(),
                )
            else:
                return """
                    <form id="commandForm" action="index.html" action="get">
                    {7}&nbsp;&nbsp;{3}&nbsp;&nbsp;{4}&nbsp;&nbsp;{5}&nbsp;&nbsp;{6}&nbsp;&nbsp;{10}&nbsp;&nbsp;{11}{12}{13}&nbsp;&nbsp;{8}&nbsp;&nbsp;{9}
                    <br/><br/>
                    {1}: <input type="text" id="commandInput" style="width:60%" name="cmd" value="{0}"/>
                    <input type="submit" value="{2}"/>
                    </form>
                    """.format(
                    "",
                    config.thisTranslation["menu_command"],
                    config.thisTranslation["enter"],
                    self.bibleSelection(),
                    self.bookSelection(),
                    self.previousChapter(),
                    self.nextChapter(),
                    self.toggleFullscreen(),
                    self.helpButton(),
                    self.featureButton(),
                    self.libraryButton(),
                    self.searchButton(),
                    "&nbsp;&nbsp;{0}".format(self.historyButton()) if self.checkPermission()[0] else "",
                    "&nbsp;&nbsp;{0}".format(self.layoutButton()) if self.checkPermission()[0] else "",
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
        html = ("""<!DOCTYPE html><html><head><title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />"""
                "<style>body {2} font-size: {4}; font-family:'{5}';{3} "
                "zh {2} font-family:'{6}'; {3} "
                "{8} {9}</style>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{7}.css?v=1.007'>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.007'>"
                "<script src='js/common.js?v=1.007'></script>"
                "<script src='js/{7}.js?v=1.007'></script>"
                "<script src='w3.js?v=1.007'></script>"
                "<script src='js/http_server.js?v=1.007'></script>"
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
                "<script src='js/custom.js?v=1.007'></script>"
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

    def previousChapter(self):
        newChapter = config.mainC - 1
        if newChapter < 1:
            newChapter = 1
        command = self.parser.bcvToVerseReference(config.mainB, newChapter, 1)
        html = "<button type='button' style='width: 50px' onclick='submitCommand(\"{0}\")'>&lt;</button>".format(command)
        return html

    def nextChapter(self):
        newChapter = config.mainC
        if config.mainC < BibleBooks.getLastChapter(config.mainB):
            newChapter += 1
        command = self.parser.bcvToVerseReference(config.mainB, newChapter, 1)
        html = "<button type='button' style='width: 50px' onclick='submitCommand(\"{0}\")'>&gt;</button>".format(command)
        return html

    def toggleFullscreen(self):
        html = "<button type='button' onclick='fullScreenSwitch()'>+ / -</button>"
        return html

    def helpButton(self):
        html = """<button type='button' style='width: 25px' onclick='window.parent.submitCommand(".help")'>?</button>"""
        return html

    def featureButton(self):
        html = """<button type='button' style='width: 25px' onclick='window.parent.submitCommand("_menu:::")'>*</button>"""
        return html

    def libraryButton(self):
        html = """<button type='button' onclick='window.parent.submitCommand(".library")'>{0}</button>""".format(config.thisTranslation["menu_library"])
        return html

    def searchButton(self):
        html = """<button type='button' onclick='window.parent.submitCommand(".search")'>{0}</button>""".format(config.thisTranslation["menu_search"])
        return html

    def layoutButton(self):
        html = """<button type='button' onclick='window.parent.submitCommand(".layout")'>{0}</button>""".format(config.thisTranslation["layout"])
        return html

    def historyButton(self):
        html = """<button type='button' onclick='window.parent.submitCommand(".history")'>{0}</button>""".format(config.thisTranslation["menu3_history"])
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
            return self.displayMessage("Font size changed to {0}!".format(config.fontSize))

    def decreaseFontSize(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            if config.fontSize >= 4:
                config.fontSize = config.fontSize - 1
                return self.displayMessage("Font size changed to {0}!".format(config.fontSize))
            else:
                return self.displayMessage("Current font size is too small to be changed!")

    def swapLayout(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            config.webUI = "" if config.webUI == "mini" else "mini"
            return self.displayMessage("Layout changed!")

    def swapTheme(self):
        permission, message = self.checkPermission()
        if not permission:
            return message
        else:
            config.theme = "default" if config.theme == "dark" else "dark"
            return self.displayMessage("Theme changed!")

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
        dotCommands = """<h2>Http-server Commands</h2>
        <p>
        <ref onclick="displayCommand('.help')">.help</ref> - Display help page with list of available commands.<br>
        <ref onclick="window.parent.submitCommand('.myqrcode')">.myqrcode</ref> - Display a QR code for other users connecting to the same UBA http-server.<br>
        <ref onclick="window.parent.submitCommand('.bible')">.bible</ref> - Open the last opened bible chapter.<br>
        <ref onclick="window.parent.submitCommand('.biblemenu')">.biblemenu</ref> - Open bible menu.<br>
        <ref onclick="window.parent.submitCommand('.commentarymenu')">.commentarymenu</ref> - Open Commentary menu.<br>
        <ref onclick="window.parent.submitCommand('.timelinemenu')">.timelinemenu</ref> - Open Timeline menu.<br>
        <ref onclick="window.parent.submitCommand('.names')">.names</ref> - Open bible names content page.<br>
        <ref onclick="window.parent.submitCommand('.characters')">.characters</ref> - Open bible characters content page.<br>
        <ref onclick="window.parent.submitCommand('.maps')">.maps</ref> - Open bible maps content page.<br>
        <ref onclick="window.parent.submitCommand('.parallels')">.parallels</ref> - Open bible parallels content page.<br>
        <ref onclick="window.parent.submitCommand('.promises')">.promises</ref> - Open bible promises content page.<br>
        <ref onclick="window.parent.submitCommand('.download')">.download</ref> - Display downloadable resources.<br>
        <ref onclick="window.parent.submitCommand('.library')">.library</ref> - Display installed bible commentaries and references books.<br>
        <ref onclick="window.parent.submitCommand('.search')">.search</ref> - Display search options.
        </p><p>"""
        dotCommands += """<p>
        <u>Bible feature shortcut on currently selected book [{0}]</u><br>
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
        <ref onclick="window.parent.submitCommand('.increasefontsize')">.increasefontsize</ref> - Increase font size.<br>
        <ref onclick="window.parent.submitCommand('.decreasefontsize')">.decreasefontsize</ref> - Decrease font size.<br>
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
            ("GitHub Books", "GitHubMap", "darrelwright/UniqueBible_Maps-Charts", (config.marvelData, "books"), ".book"),
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

    def libraryContent(self):
        content = ""
        reference = self.getCurrentReference()
        content += "<h2>Commentary</h2>"
        content += "<br>".join(["""<ref onclick ="document.title = 'COMMENTARY:::{0}:::{1}'">{2}</ref>""".format(abb, reference, self.textCommandParser.parent.commentaryFullNameList[index]) for index, abb in enumerate(self.textCommandParser.parent.commentaryList)])
        content += "<h2>Reference Book</h2>"
        content += "<br>".join(["""<ref onclick ="document.title = 'BOOK:::{0}'">{0}</ref>""".format(book) for book in self.textCommandParser.parent.referenceBookList])
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
