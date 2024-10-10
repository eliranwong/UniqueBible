from uniquebible import config
import os, webbrowser, re
from uniquebible.util.NetworkUtil import NetworkUtil
from uniquebible.util.TextUtil import TextUtil
if config.qtLibrary == "pyside6":
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
    from PySide6.QtGui import QGuiApplication, QKeySequence, QShortcut
    from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLineEdit
    from PySide6.QtCore import QUrl
else:
    from qtpy.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
    from qtpy.QtGui import QGuiApplication
    from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QShortcut
    from qtpy.QtCore import QUrl
    from qtpy.QtGui import QKeySequence

class SimpleBrowser(QWidget):

    def __init__(self, parent, title="UniqueBible.app", profileName="simplebrowser"):
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
        # setup keyboard shortcuts
        self.setupKeyboardShortcuts()

    def setupKeyboardShortcuts(self):
        shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut.activated.connect(self.toggleInstantHighlight)

    def setupVariables(self):
        self.home = None
        self.enableInstantHighlight = False
        self.urlString = ""

    def setupUI(self):
        mainLayout = QVBoxLayout()
        topLayout = QHBoxLayout()
        secondLayout = QHBoxLayout()
        mainLayout.addLayout(topLayout)
        mainLayout.addLayout(secondLayout)
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
        # highlight button
        icon = "material/image/auto_fix_off/materialiconsoutlined/48dp/2x/outline_auto_fix_off_black_48dp.png"
        self.highlightButton = config.mainWindow.getIconPushButton(icon)
        self.highlightButton.setToolTip(config.thisTranslation["instantHighlight"])
        self.highlightButton.clicked.connect(self.toggleInstantHighlight)
        topLayout.addWidget(self.highlightButton)
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

        # find entry
        self.findBar = QLineEdit()
        self.findBar.setClearButtonEnabled(True)
        self.findBar.setToolTip(config.thisTranslation["menu5_searchItems"])
        self.findBar.textChanged.connect(lambda: self.highlightContent(True))
        self.findBar.returnPressed.connect(lambda: self.highlightContent(True))
        secondLayout.addWidget(self.findBar)

        # go back button
        icon = "material/image/navigate_before/materialiconsoutlined/48dp/2x/outline_navigate_before_black_48dp.png"
        self.findButtonBackward = config.mainWindow.getIconPushButton(icon)
        self.findButtonBackward.setToolTip(config.thisTranslation["youtube_back"])
        self.findButtonBackward.clicked.connect(lambda: self.highlightContent(False))
        secondLayout.addWidget(self.findButtonBackward)
        # go forward button
        icon = "material/image/navigate_next/materialiconsoutlined/48dp/2x/outline_navigate_next_black_48dp.png"
        self.findButtonForward = config.mainWindow.getIconPushButton(icon)
        self.findButtonForward.setToolTip(config.thisTranslation["youtube_forward"])
        self.findButtonForward.clicked.connect(lambda: self.highlightContent(True))
        secondLayout.addWidget(self.findButtonForward)

        self.toggleInstantHighlight()

        # profile, webpage, and webview
        # set up a non-off-the-record profile that supports cookies
        profile = QWebEngineProfile(self.profileName, self)
        profile.setHttpCacheType(QWebEngineProfile.DiskHttpCache)
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        storagePath = os.path.join(os.getcwd(), "webstorage")
        profile.setCachePath(os.path.join(storagePath, "Cache"))
        profile.setPersistentStoragePath(os.path.join(storagePath, "PersistentStorage"))
        homeDownloads = os.path.join(os.path.expanduser("~"), "Downloads")
        homeDownload = os.path.join(os.path.expanduser("~"), "Download")
        # set download path and handler of download request
        if os.path.isdir(homeDownloads):
            self.downloadPath = homeDownloads
        elif os.path.isdir(homeDownload):
            self.downloadPath = homeDownload
        else:
            self.downloadPath = os.path.join(storagePath, "Downloads")
        profile.setDownloadPath(self.downloadPath)
        profile.downloadRequested.connect(self.downloadRequested)
        # set up web engine page
        webpage = QWebEnginePage(profile, self)
        if config.qtLibrary == "pyside6":
            webpage.newWindowRequested.connect(self.newWindowRequested)
        else:
            webpage.createWindow = self.createWindow
        # set up webview
        self.webview = QWebEngineView()
        self.webview.setPage(webpage)
        # Alternately, construct a QWebEngineView with a QWebEnginePage directly in PySide6
        #self.webview = QWebEngineView(webpage)
        self.webview.urlChanged.connect(lambda url: self.addressBar.setText(url.toString()))
        self.webview.loadFinished.connect(self.loadFinished)
        mainLayout.addWidget(self.webview)

    def toggleInstantHighlight(self):
        def getInstantHighlightDisplay():
            if self.enableInstantHighlight:
                return config.mainWindow.getCrossplatformPath("material/image/auto_fix_normal/materialiconsoutlined/48dp/2x/outline_auto_fix_normal_black_48dp.png")
            else:
                return config.mainWindow.getCrossplatformPath("material/image/auto_fix_off/materialiconsoutlined/48dp/2x/outline_auto_fix_off_black_48dp.png")
        self.findBar.setVisible(self.enableInstantHighlight)
        self.findButtonBackward.setVisible(self.enableInstantHighlight)
        self.findButtonForward.setVisible(self.enableInstantHighlight)
        self.highlightButton.setStyleSheet(config.mainWindow.getQIcon(getInstantHighlightDisplay()))
        self.enableInstantHighlight = not self.enableInstantHighlight

    def highlightContent(self, forward):
        searchString = self.findBar.text().strip()
        if forward:
            self.webview.findText(searchString)
        else:
            self.webview.findText(searchString, QWebEnginePage.FindBackward)

    def downloadRequested(self, request):
        def isFinishedChanged(obj=None):
            if request.isFinished():
                os.system(f"{config.open} {self.downloadPath}")
        request.isFinishedChanged.connect(isFinishedChanged)
        request.accept()

    # work in PySide2 or PyQt5, but not in PySide6
    def createWindow(self, windowType):
        if windowType in (QWebEnginePage.WebBrowserWindow, QWebEnginePage.WebBrowserTab):
            newWindow = SimpleBrowser(config.mainWindow, "New", self.profileName)
            newWindow.show()
            return newWindow.webview.page()

    # work in PySide6, but not in PySide2 or PyQt5
    def newWindowRequested(self, request):
        newWindow = SimpleBrowser(config.mainWindow, "New", self.profileName)
        newWindow.setUrl(QUrl(request.requestedUrl()))
        newWindow.show()

    def setUrl(self, url):
        urlString = url.toString()
        if self.home is None:
            # set home link when the first link is opened
            self.home = url
        if url.isValid() and NetworkUtil.is_valid_url(urlString):
            #self.webview.setUrl(url)
            self.urlString = urlString
            self.webview.load(url)
        else:
            self.searchGoogle()

    def loadFinished(self, ok):
        if not ok and not self.urlString == self.home.toString() and not self.urlString.startswith("https://www.google.com/"):
            self.searchGoogle()

    def searchGoogle(self):
        #if NetworkUtil.check_internet_connection():
        address = self.addressBar.text().strip()
        query = re.sub("^https://(.*?)[/]*$", r"\1", address)
        if not address == query:
            self.addressBar.setText(query)
        # search
        query = TextUtil.plainTextToUrl(query)
        url = QUrl(f"https://www.google.com/search?q={query}")
        self.webview.load(url)

    def addressEntered(self):
        address = self.addressBar.text()
        if address:
            if not "://" in address:
                address = f"https://{address}"
            self.setUrl(QUrl(address))
