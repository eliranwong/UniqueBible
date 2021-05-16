# https://docs.python.org/3/library/http.server.html
# https://ironpython-test.readthedocs.io/en/latest/library/simplehttpserver.html
import os
import re
import config
from http.server import SimpleHTTPRequestHandler
from TextCommandParser import TextCommandParser
from util.RemoteCliMainWindow import RemoteCliMainWindow
from urllib.parse import urlparse
from urllib.parse import parse_qs

class RemoteHttpHandler(SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        self.textCommandParser = TextCommandParser(RemoteCliMainWindow())
        super().__init__(*args, directory="htmlResources", **kwargs)

    def do_GET(self):
        if self.path == "" or self.path == "/" or self.path.startswith("/index.html"):
            query_components = parse_qs(urlparse(self.path).query)
            if 'cmd' in query_components:
                self.command = query_components["cmd"][0].strip()
                if len(self.command) == 0 or self.command.lower() in (".help", "?"):
                    content = self.helpContent()
                elif self.command.lower() in (".quit", ".stop"):
                    self.closeWindow()
                    config.enableHttpServer = False
                    return
                else:
                    view, content, dict = self.textCommandParser.parser(self.command, "http")
            else:
                self.command = ""
                content = self.helpContent()
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

                <style>body {4} font-size: {6}; font-family:'{7}';{5} 
                zh {4} font-family:'{8}'; {5} 
                {10} {11}</style>
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{9}.css'>
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css'>
                <script src='js/common.js'></script>
                <script src='js/{9}.js'></script>
                <script src='w3.js'></script>
                <script src='js/custom.js'></script>
                {3}
                <script>var versionList = []; var compareList = []; var parallelList = []; 
                var diffList = []; var searchList = [];</script>

            </head>
            <body style="padding-top: 10px;" onload="document.getElementById('cmd').focus();">
            <span id='v0.0.0'></span>
                <form action="index.html" action="get">
                {1}: <input type="text" id="cmd" style="width:60%" name="cmd" value="{0}"/>
                <input type="submit" value="{2}"/>
                </form>
                <iframe width="100%" height="90%" src="main.html"/>
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
            ""
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
        activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(*bcv)
        html = ("<!DOCTYPE html><html><head><title>UniqueBible.app</title>"
                "<style>body {2} font-size: {4}; font-family:'{5}';{3} "
                "zh {2} font-family:'{6}'; {3} "
                "{8} {9}</style>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{7}.css'>"
                "<link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css'>"
                "<script src='js/common.js'></script>"
                "<script src='js/{7}.js'></script>"
                "<script src='w3.js'></script>"
                "<script src='js/custom.js'></script>"
                "{0}"
                "<script>var versionList = []; var compareList = []; var parallelList = []; "
                "var diffList = []; var searchList = [];</script></head>"
                "<body><span id='v0.0.0'></span>{1}</body></html>"
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
