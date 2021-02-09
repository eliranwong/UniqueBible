import sys
import config

from PySide2.QtCore import QThread
from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QCheckBox, QLabel, QLineEdit, \
    QPushButton
from util.GitHubGist import GitHubGist
from util.NoteService import SyncNotesWithGist


class GistWindow(QDialog):

    def __init__(self):
        super(GistWindow, self).__init__()

        self.thread = None
        self.worker = None
        self.gistToken = config.gistToken
        self.connected = False

        self.setWindowTitle("Gist")
        self.setMinimumWidth(380)
        self.layout = QVBoxLayout()

        self.testStatus = QLabel("")
        self.layout.addWidget(self.testStatus)

        self.layout.addWidget(QLabel("Gist Token"))
        self.gistTokenInput = QLineEdit()
        self.gistTokenInput.setText(self.gistToken)
        self.gistTokenInput.setMaxLength(40)
        self.gistTokenInput.textChanged.connect(self.enableButtons)
        self.layout.addWidget(self.gistTokenInput)

        self.testButton = QPushButton("Test Connection")
        self.testButton.setEnabled(False)
        self.testButton.clicked.connect(self.checkStatus)
        self.layout.addWidget(self.testButton)

        # self.syncHighlightsButton = QPushButton("Synch Highlights")
        # self.syncHighlightsButton.setEnabled(False)
        # self.syncHighlightsButton.clicked.connect(self.syncHighlights)
        # self.layout.addWidget(self.syncHighlightsButton)

        self.syncBibleNotesButton = QPushButton("Synch Bibles Notes")
        self.syncBibleNotesButton.setEnabled(False)
        self.syncBibleNotesButton.clicked.connect(self.syncBibleNotes)
        self.layout.addWidget(self.syncBibleNotesButton)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.stopSync)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        self.enableButtons()
        self.checkStatus()

    def enableButtons(self):
        if len(self.gistTokenInput.text()) >= 40:
            self.testButton.setEnabled(True)
        else:
            self.testButton.setEnabled(False)
            self.connected = False
            self.setStatus("Not connected", False)
        if self.connected:
            self.testButton.setEnabled(False)
            self.syncBibleNotesButton.setEnabled(True)
        else:
            self.syncBibleNotesButton.setEnabled(False)

    def checkStatus(self):
        if len(self.gistTokenInput.text()) < 40:
            self.setStatus("Not connected", False)
            self.connected = False
        else:
            self.gh = GitHubGist(self.gistTokenInput.text())
            if self.gh.connected:
                self.setStatus("Connected to " + self.gh.user.name, True)
                self.connected = True
                config.gistToken = self.gistTokenInput.text()
            else:
                self.setStatus("Not connected", False)
                self.connected = False
        self.enableButtons()

    def setStatus(self, message, connected=True):
        self.testStatus.setText("Status: " + message)
        if connected:
            self.testStatus.setStyleSheet("color: rgb(128, 255, 7);")
        else:
            self.testStatus.setStyleSheet("color: rgb(253, 128, 8);")
        QApplication.processEvents()

    def syncBibleNotes(self):
        self.setStatus("Syncing ...", True)
        self.syncBibleNotesButton.setEnabled(False)

        self.thread = QThread()
        self.worker = SyncNotesWithGist()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.syncCompleted)
        self.worker.progress.connect(self.setStatus)
        self.thread.start()

    def syncCompleted(self, count):
        self.setStatus("Done! Processed {0} notes".format(count), True)

    def stopSync(self):
        if self.thread and self.thread.isRunning():
            self.thread.quit()


if __name__ == '__main__':
    from Languages import Languages
    config.thisTranslation = Languages.translation
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    gistWindow = GistWindow()
    gistWindow.exec_()