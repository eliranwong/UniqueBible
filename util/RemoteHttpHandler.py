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
        html = """
            <html>
            <head>
                <title>UniqueBible.app</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
                <meta http-equiv="Pragma" content="no-cache" />
                <meta http-equiv="Expires" content="0" />
            </head>
            <body onload="document.getElementById('cmd').focus();">
                <form action="index.html" action="get">
                {1}: <input type="text" id="cmd" style="width:70%" name="cmd" value="{0}"/>
                <input type="submit" value="{2}"/>
                </form>
                <iframe width="100%" height="95%" src="main.html"/>
            </body>
            </html>
        """.format(self.command, config.thisTranslation["menu_command"], config.thisTranslation["enter"])
        self.wfile.write(bytes(html, "utf8"))

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
