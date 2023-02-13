import config, os
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QUrl
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineProfile
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtWidgets import QWidget, QVBoxLayout
else:
    from qtpy.QtCore import QUrl
    from qtpy.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
    from qtpy.QtGui import QGuiApplication
    from qtpy.QtWidgets import QWidget, QVBoxLayout

class ChatGPT(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle("OpenAI ChatGPT")
        # set variables
        #self.setupVariables()
        # setup interface
        self.setupUI()
        # set initial window size
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)
    
    def setupUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        profile = QWebEngineProfile("chatGPT", self)
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        storagePath = os.path.join(os.getcwd(), "webstorage")
        profile.setCachePath(storagePath)
        profile.setPersistentStoragePath(storagePath)
        profile.setDownloadPath(storagePath)
        webview = QWebEngineView(profile)
        webview.setUrl(QUrl("https://chat.openai.com/chat"))
        layout.addWidget(webview)

config.mainWindow.chatGPT = ChatGPT(config.mainWindow)
config.mainWindow.chatGPT.show()