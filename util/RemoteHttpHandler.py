# https://docs.python.org/3/library/http.server.html
# https://ironpython-test.readthedocs.io/en/latest/library/simplehttpserver.html
import os
import re
import config
from http.server import SimpleHTTPRequestHandler

from BibleBooks import BibleBooks
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite
from TextCommandParser import TextCommandParser
from util.RemoteCliMainWindow import RemoteCliMainWindow
from urllib.parse import urlparse
from urllib.parse import parse_qs

class RemoteHttpHandler(SimpleHTTPRequestHandler):

    parser = None
    textCommandParser = None
    bibles = None
    books = None
    abbreviations = None

    def __init__(self, *args, **kwargs):
        if RemoteHttpHandler.textCommandParser is None:
            RemoteHttpHandler.textCommandParser = TextCommandParser(RemoteCliMainWindow())
        self.textCommandParser = RemoteHttpHandler.textCommandParser
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
        super().__init__(*args, directory="htmlResources", **kwargs)

    def do_GET(self):
        if self.path == "" or self.path == "/" or self.path.startswith("/index.html"):
            query_components = parse_qs(urlparse(self.path).query)
            if 'cmd' in query_components:
                self.command = query_components["cmd"][0].strip()
                if len(self.command) == 0:
                    self.command = self.abbreviations[config.mainB]
                if self.command.lower() in (".help", "?"):
                    content = self.helpContent()
                elif self.command.lower() in (".quit", ".stop"):
                    self.closeWindow()
                    config.enableHttpServer = False
                    return
                else:
                    view, content, dict = self.textCommandParser.parser(self.command, "http")
            else:
                self.command = self.abbreviations[str(config.mainB)]
                view, content, dict = self.textCommandParser.parser(self.command, "http")
            content = self.wrapHtml(content)
            outputFile = os.path.join("htmlResources", "main.html")
            fileObject = open(outputFile, "w", encoding="utf-8")
            fileObject.write(content)
            fileObject.close()
            self.indexPage()
        else:
            return super().do_GET()

    def indexPage(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        
        bcv = (config.mainText, config.mainB, config.mainC, config.mainV)
        activeBCVsettings = "<script>var mod = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(*bcv)
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

                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{9}.css'>
                <style>
                ::-webkit-scrollbar {4}
                  display: none;
                {5}
                ::-webkit-scrollbar-button {4}
                  display: none;
                {5}
                body {4}
                  font-size: {6};
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
                height: 90%;
                width: 100%;
                {5}
                zh {4} font-family:'{8}'; {5} 
                {10} {11}
                </style>
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/http_server.css'>
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css'>
                <script src='js/common.js'></script>
                <script src='js/{9}.js'></script>
                <script src='w3.js'></script>
                <script src='js/http_server.js'></script>
                <script>
                var queryString = window.location.search;	
                queryString = queryString.substring(1);
                var curPos;
                var tempMod; var tempB; var tempC; var tempV;
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
            <body style="padding-top: 10px;" onload="document.getElementById('commandInput').focus();" ontouchstart="">
                <span id='v0.0.0'></span>
                <form id="commandForm" action="index.html" action="get">
                {12}&nbsp;&nbsp;{13}&nbsp;&nbsp;{14}&nbsp;&nbsp;{15}
                <br/><br/>
                {1}: <input type="text" id="commandInput" style="width:60%" name="cmd" value="{0}"/>
                <input type="submit" value="{2}"/>
                </form>
                
                <div id="content">
                    <div id="bibleDiv" onscroll="scrollBiblesIOS(this.id)">
                        <iframe id="bibleFrame" name="main" onload="resizeSite()" width="100%" height="90%" src="main.html">Oops!</iframe>
                    </div>
                    <div id="toolDiv" onscroll="scrollBiblesIOS(this.id)">
                        <iframe id="toolFrame" name="tool" onload="resizeSite()" src="empty.html">Oops!</iframe>
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
            self.command,
            config.thisTranslation["menu_command"],
            config.thisTranslation["enter"],
            activeBCVsettings,
            "{",
            "}",
            fontSize,
            fontFamily,
            config.fontChinese,
            config.theme,
            self.getHighlightCss(),
            "",
            self.bibleSelection(),
            self.bookSelection(),
            self.previousChapter(),
            self.nextChapter()
        )
        self.wfile.write(bytes(html, "utf8"))

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
        activeBCVsettings = "<script>var mod = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(*bcv)
        html = ("""<!DOCTYPE html><html><head><title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />"""
                "<style>body {2} font-size: {4}; font-family:'{5}';{3} "
                "zh {2} font-family:'{6}'; {3} "
                "{8} {9}</style>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{7}.css'>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css'>"
                "<script src='js/common.js'></script>"
                "<script src='js/{7}.js'></script>"
                "<script src='w3.js'></script>"
                "<script src='js/http_server.js'></script>"
                """<script>
                var target = document.querySelector('title');
                var observer = new MutationObserver(function(mutations) {2}
                    mutations.forEach(function(mutation) {2}
                        if (document.title.startsWith("_")) {2}{3} else {2} window.parent.submitCommand(document.title); {3}
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
                "<script src='js/custom.js'></script>"
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

    def getHighlightCss(self):
        css = ""
        for i in range(len(config.highlightCollections)):
            code = "hl{0}".format(i + 1)
            css += ".{2} {0} background: {3}; {1} ".format("{", "}", code, config.highlightDarkThemeColours[i] if config.theme == "dark" else config.highlightLightThemeColours[i])
        return css

    def closeWindow(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        html = "<html><head><script>window.close();</script></head></html>"
        self.wfile.write(bytes(html, "utf8"))

    def helpContent(self):
        content = "\n".join(
            [re.sub("            #", "#", value[-1]) for value in self.textCommandParser.interpreters.values()])
        content = re.sub(r"\n", "<br/>", content)
        return content
