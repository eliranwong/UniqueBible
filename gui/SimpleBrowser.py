import config, os
if config.qtLibrary == "pyside6":
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtWidgets import QVBoxLayout
else:
    from qtpy.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
    from qtpy.QtGui import QGuiApplication
    from qtpy.QtWidgets import QVBoxLayout

class SimpleBrowser(QWebEngineView):

    def __init__(self, parent, title="UniqueBible.app", profileName="UBA"):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle(title)
        # set variables
        #self.setupVariables()
        # setup interface
        self.setupUI(profileName)
        # set initial window size
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)
    
    def setupUI(self, profileName):
        layout = QVBoxLayout()
        self.setLayout(layout)

        profile = QWebEngineProfile(profileName, self)
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        storagePath = os.path.join(os.getcwd(), "webstorage")
        profile.setCachePath(storagePath)
        profile.setPersistentStoragePath(storagePath)
        profile.setDownloadPath(storagePath)

        webpage = QWebEnginePage(profile, self)
        webpage.newWindowRequested.connect(lambda request: self.setUrl(request.requestedUrl()))
        self.setPage(webpage)
