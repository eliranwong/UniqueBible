from uniquebible import config
import webbrowser
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit
else:
    from qtpy.QtGui import QMouseEvent
    from qtpy.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit


class WatsonCredentialWindow(QDialog):

    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["ibmWatsonCredentials"])
        self.setMinimumWidth(380)

        layout0 = QVBoxLayout()
        layout0.setSpacing(20)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        layout.addWidget(QLabel(config.thisTranslation["ibmWatsonCredentials"]))

        wikiLink = "https://github.com/eliranwong/UniqueBible/wiki/IBM-Watson-Language-Translator"
        readWiki = QLabel(wikiLink)
        readWiki.mouseReleaseEvent = lambda event=QMouseEvent, wikiLink=wikiLink: webbrowser.open(wikiLink)
        layout.addWidget(readWiki)

        layout0.addLayout(layout)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        layout.addWidget(QLabel("API key:"))
        self.inputApiKey = QLineEdit()
        self.inputApiKey.setText(config.myIBMWatsonApikey)
        layout.addWidget(self.inputApiKey)

        layout.addWidget(QLabel("URL:"))
        self.inputURL = QLineEdit()
        self.inputURL.setText(config.myIBMWatsonUrl)
        layout.addWidget(self.inputURL)

        layout.addWidget(QLabel("Version:"))
        self.inputVersion = QLineEdit()
        self.inputVersion.setText(config.myIBMWatsonVersion)
        layout.addWidget(self.inputVersion)

        button = QDialogButtonBox.Ok
        buttonBox = QDialogButtonBox(button)
        buttonBox.accepted.connect(self.accept)
        layout.addWidget(buttonBox)

        layout0.addLayout(layout)

        self.setLayout(layout0)
