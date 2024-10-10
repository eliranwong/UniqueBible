from uniquebible import config
import webbrowser
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QMouseEvent
    from PySide6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit
else:
    from qtpy.QtGui import QMouseEvent
    from qtpy.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QLineEdit


class LanguageItemWindow(QDialog):

    def __init__(self, windowTitle):
        super().__init__()
        self.setWindowTitle(windowTitle)
        self.setMinimumWidth(380)

        layout0 = QVBoxLayout()
        layout0.setSpacing(20)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        layout.addWidget(QLabel("Wiki - Interface Language Files"))

        wikiLink = "https://github.com/eliranwong/UniqueBible/wiki/Interface-language-files"
        readWiki = QLabel(wikiLink)
        readWiki.mouseReleaseEvent = lambda event=QMouseEvent, wikiLink=wikiLink: webbrowser.open(wikiLink)
        layout.addWidget(readWiki)

        layout0.addLayout(layout)

        layout = QVBoxLayout()
        layout.setSpacing(5)

        layout.addWidget(QLabel("Key:"))
        self.key = QLineEdit()
        self.key.setText("")
        layout.addWidget(self.key)

        layout.addWidget(QLabel("Entry:"))
        self.entry = QLineEdit()
        self.entry.setText("")
        layout.addWidget(self.entry)

        button = QDialogButtonBox.Ok
        buttonBox = QDialogButtonBox(button)
        buttonBox.accepted.connect(self.accept)
        layout.addWidget(buttonBox)

        layout0.addLayout(layout)

        self.setLayout(layout0)
