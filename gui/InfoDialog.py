import sys
import webbrowser
import config

from qtpy.QtCore import QCoreApplication, Qt
from qtpy.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPlainTextEdit


class InfoDialog(QDialog):

    def __init__(self):
        super(InfoDialog, self).__init__()

        self.wikiLink = "https://github.com/eliranwong/UniqueBible/wiki"

        self.setMinimumWidth(350)
        self.setWindowTitle(config.thisTranslation["info"])
        self.layout = QVBoxLayout()

        self.appName = QLabel("UniqueBible.app [{0} {1}]".format(config.thisTranslation["version"], config.version))
        self.appName.mouseReleaseEvent = self.openWiki
        self.layout.addWidget(self.appName)

        with open("latest_changes.txt", "r", encoding="utf-8") as fileObject:
            text = fileObject.read()
        self.layout.addWidget(QLabel("{0}:".format(config.thisTranslation["latest_changes"])))
        self.latestChanges = QPlainTextEdit()
        self.latestChanges.setPlainText(text)
        self.latestChanges.setReadOnly(True)
        self.layout.addWidget(self.latestChanges)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def openWiki(self, event):
        webbrowser.open(self.wikiLink)

if __name__ == '__main__':
    from util.ConfigUtil import ConfigUtil
    from util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = InfoDialog()
    window.exec_()
    window.close()