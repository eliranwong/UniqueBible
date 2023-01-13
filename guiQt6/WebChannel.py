import os, config

from PySide6.QtCore import QUrl, Slot
from PySide6.QtGui import QIcon, QGuiApplication
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWebChannel import QWebChannel
from gui.WebEngineViewPopover import WebEngineViewPopover

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # setup UI
        self.setWindowTitle("UniqueBible.app [version {0:.2f}]".format(config.version))
        appIcon = QIcon(config.desktopUBAIcon)
        QGuiApplication.setWindowIcon(appIcon)

        self.setupBaseUrl()
        self.contentView = WebEngineViewPopover(self, "main", "main", windowTitle="Testing Qt Web Channel", enableCloseAction=False)
        # setup channel
        self.channel = QWebChannel()
        self.channel.registerObject('backend', self)
        self.contentView.page().setWebChannel(self.channel)
        html = """
<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8"/>        
        <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <script>
            var backend;
            new QWebChannel(qt.webChannelTransport, function (channel) {
                backend = channel.objects.backend;
            });
        </script>
    </head>
    <body> <h2 id="header">Testing Qt Web Channel</h2> <button type="button" onclick="backend.textCommandChanged('hello');alert('world');">Click Me!</button></body>
    <script>
        document.getElementById("header").addEventListener("click", function(){
            backend.textCommandChanged('hello world');
        });
    </script>
</html>
        """
        self.contentView.setHtml(html, config.baseUrl)

        self.centralWidget = self.contentView
        self.setCentralWidget(self.centralWidget)

    @Slot(str)
    def textCommandChanged(self, command, source="main"):
        if source == "main" and not command.endswith("UniqueBibleApp.png"):
            print(command)

    def closeMediaPlayer(self):
        pass

    # base folder for webViewEngine
    def setupBaseUrl(self):
        # Variable "baseUrl" is shared by multiple classes
        # External objects, such as stylesheets or images referenced in the HTML document, are located RELATIVE TO baseUrl .
        # e.g. put all local files linked by html's content in folder "htmlResources"
        global baseUrl
        relativePath = os.path.join("htmlResources", "UniqueBibleApp.png")
        absolutePath = os.path.abspath(relativePath)
        baseUrl = QUrl.fromLocalFile(absolutePath)
        config.baseUrl = baseUrl
