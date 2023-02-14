import config, os, webbrowser
from util.TextUtil import TextUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
    from PySide6.QtGui import QGuiApplication
    from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLineEdit
    from PySide6.QtCore import QUrl
else:
    from qtpy.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
    from qtpy.QtGui import QGuiApplication
    from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLineEdit
    from qtpy.QtCore import QUrl

class SimpleBrowser(QWidget):

    def __init__(self, parent, title="UniqueBible.app", profileName="UBA"):
        super().__init__()
        self.parent = parent
        self.profileName = profileName
        # set title
        self.setWindowTitle(title)
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()
        # set initial window size
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)

    def setupVariables(self):
        self.home = None

    def setupUI(self):
        mainLayout = QVBoxLayout()
        topLayout = QHBoxLayout()
        mainLayout.addLayout(topLayout)
        self.setLayout(mainLayout)

        # go home button
        icon = "material/action/home/materialiconsoutlined/48dp/2x/outline_home_black_48dp.png"
        button = config.mainWindow.getIconPushButton(icon)
        button.setToolTip(config.thisTranslation["homePage"])
        button.clicked.connect(lambda: self.setUrl(self.home))
        topLayout.addWidget(button)
        # go back button
        icon = "material/image/navigate_before/materialiconsoutlined/48dp/2x/outline_navigate_before_black_48dp.png"
        button = config.mainWindow.getIconPushButton(icon)
        button.setToolTip(config.thisTranslation["youtube_back"])
        button.clicked.connect(lambda: self.webview.page().triggerAction(QWebEnginePage.Back))
        topLayout.addWidget(button)
        # go forward button
        icon = "material/image/navigate_next/materialiconsoutlined/48dp/2x/outline_navigate_next_black_48dp.png"
        button = config.mainWindow.getIconPushButton(icon)
        button.setToolTip(config.thisTranslation["youtube_forward"])
        button.clicked.connect(lambda: self.webview.page().triggerAction(QWebEnginePage.Forward))
        topLayout.addWidget(button)
        # url entry
        self.addressBar = QLineEdit()
        self.addressBar.setClearButtonEnabled(True)
        self.addressBar.setToolTip(config.thisTranslation["enter_fullURL"])
        self.addressBar.returnPressed.connect(self.addressEntered)
        topLayout.addWidget(self.addressBar)
        # reload button
        icon = "material/navigation/refresh/materialiconsoutlined/48dp/2x/outline_refresh_black_48dp.png"
        button = config.mainWindow.getIconPushButton(icon)
        button.setToolTip(config.thisTranslation["menu_reload"])
        button.clicked.connect(lambda: self.webview.page().triggerAction(QWebEnginePage.Reload))
        topLayout.addWidget(button)
        # open in web browser button
        icon = "material/action/open_in_new/materialiconsoutlined/48dp/2x/outline_open_in_new_black_48dp.png"
        button = config.mainWindow.getIconPushButton(icon)
        button.setToolTip(config.thisTranslation["browser"])
        button.clicked.connect(lambda: webbrowser.open(self.addressBar.text()))
        topLayout.addWidget(button)

        # webview
        self.webview = QWebEngineView()
        self.webview.urlChanged.connect(lambda url: self.addressBar.setText(url.toString()))
        # set up a non-off-the-record profile that supports cookies
        profile = QWebEngineProfile(self.profileName, self.webview)
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        storagePath = os.path.join(os.getcwd(), "webstorage")
        profile.setCachePath(storagePath)
        profile.setPersistentStoragePath(storagePath)
        profile.setDownloadPath(storagePath)
        # set up web engine page
        webpage = QWebEnginePage(profile, self)
        #webpage.newWindowRequested.connect(lambda request: self.setUrl(request.requestedUrl()))
        webpage.newWindowRequested.connect(self.newWindowRequested)
        self.webview.setPage(webpage)
        mainLayout.addWidget(self.webview)

    def newWindowRequested(self, request):
        # open in the same window
        #self.setUrl(request.requestedUrl())

        # open in a new window
        newWindow = SimpleBrowser(config.mainWindow, "New Window", self.profileName)
        newWindow.setUrl(QUrl(request.requestedUrl()))
        newWindow.show()

    def setUrl(self, url):
        if self.home is None:
            # set home link when the first link is opened
            self.home = url
        if url.isValid():
            self.webview.setUrl(url)
            #self.webview.load(url)
        else:
            # search
            query = TextUtil.plainTextToUrl(self.addressBar.text())
            url = QUrl(f"https://www.google.com/search?q={query}")
            self.webview.load(url)

    def addressEntered(self):
        address = self.addressBar.text()
        if address:
            if not "://" in address:
                address = f"https://{address}"
            self.setUrl(QUrl(address))
