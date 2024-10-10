from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QTabWidget
    from PySide6.QtWebEngineCore import QWebEnginePage
else:
    from qtpy.QtWidgets import QTabWidget
    from qtpy.QtWebEngineWidgets import QWebEnginePage


class TabWidget(QTabWidget):

    def __init__(self, parent, name):
        super().__init__()
        self.parent = parent
        self.name = name
        self.currentChanged.connect(self.tabSelected)
        # notes:
        # the first tab is indexed with 0.  the rest with 1,2,3,4,etc.
        # to get the index of current tab, print(self.currentIndex())
        # to change the current tab, self.setCurrentWidget(self.widget(4))

    def translateTextIntoUserLanguage(self, text, message):
        self.currentWidget().translateTextIntoUserLanguage(text, message)

    def setHtml(self, html, baseUrl):
        self.currentWidget().setHtml(html, baseUrl)

    def load(self, path):
        self.currentWidget().load(path)

    def tabSelected(self):
        if self.name == "main":
            self.parent.parent.setMainPage()
        elif self.name == "study":
            self.parent.parent.setStudyPage()
