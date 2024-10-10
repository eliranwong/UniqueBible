import re
import sys
import webbrowser
from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QCoreApplication, Qt
    from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QTextBrowser
    from PySide6.QtWidgets import QHBoxLayout
else:
    from qtpy.QtCore import QCoreApplication, Qt
    from qtpy.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QTextBrowser
    from qtpy.QtWidgets import QHBoxLayout                      
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.NetworkUtil import NetworkUtil


class InfoDialog(QDialog):

    def __init__(self, content=None, description=None):
        super(InfoDialog, self).__init__()

        self.wikiLink = "https://github.com/eliranwong/UniqueBible/wiki"

        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        self.setWindowTitle(config.thisTranslation["info"])
        self.layout = QVBoxLayout()

        self.appName = QLabel("UniqueBible.app - {:.2f}".format(config.version))
        self.appName.setStyleSheet("QLabel {font-size: 30px;}")
        self.appName.mouseReleaseEvent = self.openWiki
        self.layout.addWidget(self.appName)

        filesHBox = QHBoxLayout()

        filesVBox1 = QVBoxLayout()
        count = len(FileUtil.getAllFilesWithExtension(config.marvelData+"/bibles", ".bible"))
        filesVBox1.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["menu5_bible"], count)))
        count = len(FileUtil.getAllFilesWithExtension(config.marvelData+"/lexicons", ".lexicon"))
        filesVBox1.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["lexicons"], count)))
        count = len(FileUtil.getAllFilesWithExtension(config.marvelData+"/devotionals", ".devotional"))
        filesVBox1.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["devotionals"], count)))
        count = len(FileUtil.getAllFilesWithExtension("music", ".mp3"))
        filesVBox1.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["menu11_music"], count)))
        filesVBox1.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["menu1_menuLayout"], config.menuLayout)))
        filesHBox.addLayout(filesVBox1)

        filesVBox2 = QVBoxLayout()
        count = len(FileUtil.getAllFilesWithExtension(config.marvelData+"/commentaries", ".commentary"))
        filesVBox2.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["commentaries"], count)))
        count = len(FileUtil.getAllFilesWithExtension(config.marvelData+"/books", ".book"))
        filesVBox2.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["menu10_books"], count)))
        count = len(FileUtil.getAllFilesWithExtension("video", ".mp4"))
        filesVBox2.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["menu11_video"], count)))
        filesVBox2.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["menu_language"], config.displayLanguage)))
        filesVBox2.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["menu_shortcuts"], config.menuShortcuts)))
        filesHBox.addLayout(filesVBox2)

        filesVBox3 = QVBoxLayout()
        count = len(FileUtil.getAllFilesWithExtension(config.marvelData+"/pdf", ".pdf"))
        filesVBox3.addWidget(QLabel("{0}: {1}".format("PDF", count)))
        count = len(FileUtil.getAllFilesWithExtension(config.marvelData+"/epub", ".epub"))
        filesVBox3.addWidget(QLabel("{0}: {1}".format("EPUB", count)))
        count = len(FileUtil.getAllFilesWithExtension(config.marvelData+"/docx", ".docx"))
        filesVBox3.addWidget(QLabel("{0}: {1}".format("DOCX", count)))
        filesVBox3.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["menu_window"], config.windowStyle)))
        filesVBox3.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["menu_theme"], config.theme)))
        filesHBox.addLayout(filesVBox3)

        self.layout.addLayout(filesHBox)

        ipLabel = QLabel("IP: {0}".format(NetworkUtil.get_ip()))
        self.layout.addWidget(ipLabel)

        if content is None:
            with open("latest_changes.txt", "r", encoding="utf-8") as fileObject:
                text = fileObject.read()
        else:
            text = content
        html = text
        urls = re.compile(r"((https?):((//)|(\\\\))+[\w\d:#@%/;$~_?\+-=\\\.&]*)", re.MULTILINE | re.UNICODE)
        html = urls.sub(r'<a href="\1" >\1</a>', html)
        html = html.replace("\n", "<br>")
        latest = QLabel("{0}:".format(config.thisTranslation["latest_changes"] if description is None else description))
        latest.setStyleSheet("QLabel {font-size: 20px;}")
        self.layout.addWidget(latest)
        self.latestChanges = QTextBrowser()
        self.latestChanges.setOpenExternalLinks(True)
        self.latestChanges.insertHtml(html)
        self.latestChanges.setReadOnly(True)
        cursor = self.latestChanges.textCursor()
        cursor.setPosition(0)
        self.latestChanges.setTextCursor(cursor)
        self.layout.addWidget(self.latestChanges)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def openWiki(self, event):
        webbrowser.open(self.wikiLink)

if __name__ == '__main__':
    from uniquebible.util.ConfigUtil import ConfigUtil
    from uniquebible.util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")

    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = InfoDialog()
    window.exec_()
    window.close()