import glob
import os
import zipfile
import config
from qtpy.QtCore import Qt
from qtpy.QtCore import QObject
from qtpy.QtCore import Signal
from qtpy.QtCore import QThread
from qtpy.QtCore import QTimer
from qtpy.QtGui import QStandardItemModel, QStandardItem
from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
from qtpy.QtWidgets import QApplication
from qtpy.QtWidgets import QListWidget
from util.BibleBooks import BibleBooks


class DownloadBibleMp3Dialog(QDialog):

    def __init__(self, parent):
        super().__init__()

        self.bibles = {
            "KJV": "otseng/UniqueBible_MP3_KJV"
        }
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["gitHubBibleMp3Files"])
        self.setMinimumSize(150, 400)
        self.selectedBible = None
        self.settingBibles = False
        self.default = "default"
        self.thread = None
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel(config.thisTranslation["gitHubBibleMp3Files"])
        mainLayout.addWidget(title)

        self.versionsLayout = QVBoxLayout()
        self.versionsList = QListWidget()
        self.versionsList.itemClicked.connect(self.selectItem)
        self.versionsList.addItem("KJV")
        self.versionsList.setMaximumHeight(50)
        self.versionsLayout.addWidget(self.versionsList)
        mainLayout.addLayout(self.versionsLayout)

        self.downloadTable = QTableView()
        self.downloadTable.setEnabled(False)
        self.downloadTable.setFocusPolicy(Qt.StrongFocus)
        self.downloadTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.downloadTable.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.downloadTable)
        self.downloadTable.setModel(self.dataViewModel)
        mainLayout.addWidget(self.downloadTable)

        buttonsLayout = QHBoxLayout()
        selectAllButton = QPushButton(config.thisTranslation["selectAll"])
        selectAllButton.setFocusPolicy(Qt.StrongFocus)
        selectAllButton.clicked.connect(self.selectAll)
        buttonsLayout.addWidget(selectAllButton)
        selectNoneButton = QPushButton(config.thisTranslation["selectNone"])
        selectNoneButton.setFocusPolicy(Qt.StrongFocus)
        selectNoneButton.clicked.connect(self.selectNone)
        buttonsLayout.addWidget(selectNoneButton)
        otButton = QPushButton("1-39")
        otButton.setFocusPolicy(Qt.StrongFocus)
        otButton.clicked.connect(self.selectOT)
        buttonsLayout.addWidget(otButton)
        ntButton = QPushButton("40-66")
        ntButton.setFocusPolicy(Qt.StrongFocus)
        ntButton.clicked.connect(self.selectNT)
        buttonsLayout.addWidget(ntButton)
        # buttonsLayout.addStretch()
        mainLayout.addLayout(buttonsLayout)

        self.downloadButton = QPushButton(config.thisTranslation["download"])
        self.downloadButton.setFocusPolicy(Qt.StrongFocus)
        self.downloadButton.setAutoDefault(True)
        self.downloadButton.setFocus()
        self.downloadButton.clicked.connect(self.download)
        mainLayout.addWidget(self.downloadButton)

        self.status = QLabel("")
        mainLayout.addWidget(self.status)

        buttonLayout = QHBoxLayout()
        self.closeButton = QPushButton(config.thisTranslation["close"])
        self.closeButton.setFocusPolicy(Qt.StrongFocus)
        self.closeButton.clicked.connect(self.closeDialog)
        buttonLayout.addWidget(self.closeButton)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

        self.versionsList.item(0).setSelected(True)
        bible = self.versionsList.item(0).text()
        self.selectBible(bible)

        self.downloadButton.setDefault(True)
        QTimer.singleShot(0, self.downloadButton.setFocus)

    def selectItem(self, item):
        self.selectBible(item.text())

    def selectBible(self, bible):
        from util.GithubUtil import GithubUtil

        self.selectedBible = bible
        self.downloadTable.setEnabled(True)
        self.selectedRepo = self.bibles[self.selectedBible]
        self.github = GithubUtil(self.selectedRepo)
        self.repoData = self.github.getRepoData()
        self.settingBibles = True
        self.dataViewModel.clear()
        rowCount = 0
        for file in self.repoData.keys():
            item = QStandardItem(file)
            folder = os.path.join("audio", "bibles", self.selectedBible, self.default, file)
            if not os.path.exists(folder):
                item.setCheckable(True)
                item.setCheckState(Qt.Checked)
                item.setEnabled(True)
            else:
                item.setCheckable(False)
                item.setCheckState(Qt.Unchecked)
                item.setEnabled(False)
            self.dataViewModel.setItem(rowCount, 0, item)
            engFullBookName = BibleBooks().eng[str(int(file))][1]
            item = QStandardItem(engFullBookName)
            self.dataViewModel.setItem(rowCount, 1, item)
            if not os.path.exists(folder):
                item = QStandardItem("")
                self.dataViewModel.setItem(rowCount, 2, item)
            else:
                item = QStandardItem("Installed")
                self.dataViewModel.setItem(rowCount, 2, item)
            rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels(
            [config.thisTranslation["menu_book"], config.thisTranslation["name"], ""])
        self.downloadTable.resizeColumnsToContents()
        self.settingBibles = False

    def selectAll(self):
        for index in range(self.dataViewModel.rowCount()):
            item = self.dataViewModel.item(index)
            if item.isEnabled():
                item.setCheckState(Qt.Checked)

    def selectNone(self):
        for index in range(self.dataViewModel.rowCount()):
            item = self.dataViewModel.item(index)
            item.setCheckState(Qt.Unchecked)

    def selectOT(self):
        for index in range(self.dataViewModel.rowCount()):
            item = self.dataViewModel.item(index)
            bookNum = int(item.text())
            if bookNum <= 39:
                if item.isEnabled():
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Unchecked)

    def selectNT(self):
        for index in range(self.dataViewModel.rowCount()):
            item = self.dataViewModel.item(index)
            bookNum = int(item.text())
            if bookNum >= 40:
                if item.isEnabled():
                    item.setCheckState(Qt.Checked)
                else:
                    item.setCheckState(Qt.Unchecked)
            else:
                item.setCheckState(Qt.Unchecked)

    def download(self):
        self.downloadButton.setEnabled(False)
        self.setStatus(config.thisTranslation["message_installing"])
        self.closeButton.setEnabled(False)
        folder = os.path.join("audio", "bibles")
        if not os.path.exists(folder):
            os.mkdir(folder)
        folder = os.path.join("audio", "bibles", self.selectedBible)
        if not os.path.exists(folder):
            os.mkdir(folder)
        folder = os.path.join("audio", "bibles", self.selectedBible, self.default)
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.thread = QThread()
        self.worker = DownloadFromGitHub(self.github, self.repoData, self.dataViewModel, self.selectedBible, self.default)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.finishedDownloading)
        self.worker.progress.connect(self.setStatus)
        self.thread.start()

    def finishedDownloading(self, count):
        self.selectBible(self.selectedBible)
        self.setStatus("")
        self.downloadButton.setEnabled(True)
        self.closeButton.setEnabled(True)
        if count > 0:
            self.parent.displayMessage(config.thisTranslation["message_installed"])

    def setStatus(self, message):
        self.status.setText(message)
        QApplication.processEvents()

    def closeDialog(self):
        if self.thread:
            if self.thread.isRunning():
                self.thread.quit()
        self.close()


class DownloadFromGitHub(QObject):
    finished = Signal(int)
    progress = Signal(str)

    def __init__(self, github, repoData, dataViewModel, selectedBible, default):
        super(DownloadFromGitHub, self).__init__()
        self.github = github
        self.repoData = repoData
        self.dataViewModel = dataViewModel
        self.selectedBible = selectedBible
        self.default = default

    def run(self):
        self.progress.emit(config.thisTranslation["message_installing"])
        folder = os.path.join("audio", "bibles", self.selectedBible, self.default)
        count = 0
        for index in range(self.dataViewModel.rowCount()):
            if self.dataViewModel.item(index).checkState() == Qt.Checked:
                filename = self.dataViewModel.item(index).text()
                file = os.path.join(folder, filename+".zip")
                msg = "Download " + filename
                self.progress.emit(msg)
                self.github.downloadFile(file, self.repoData[filename])
                with zipfile.ZipFile(file, 'r') as zipped:
                    zipped.extractall(folder)
                os.remove(file)
                DownloadBibleMp3Util.moveFiles("{0}/{1}*.mp3".format(folder, filename), folder)
                count += 1
        self.finished.emit(count)


class DownloadBibleMp3Util:

    @staticmethod
    def moveFiles(sourceDir, destDir, debugOutput = False):
        files = glob.glob(sourceDir)
        for file in sorted(files):
            base = os.path.basename(file)
            folder = base[:2]
            destFolder = os.path.join(destDir, folder)
            if not os.path.exists(destFolder):
                os.mkdir(destFolder)
            newFile = os.path.join(destFolder, base)
            os.rename(file, newFile)
            if debugOutput:
                print(newFile)

    @staticmethod
    def zipFiles(directory, debugOutput = False):
        import shutil
        directories = [d for d in os.listdir(directory) if
                       os.path.isdir(os.path.join(directory, d)) and not d == ".git"]
        count = 0
        for dir in sorted(directories):
            if debugOutput:
                print(dir)
            zipFile = os.path.join(directory, dir)
            shutil.make_archive(zipFile, 'zip', zipFile)
            count += 1
            if count > 66:
                break


class DummyParent():
    def displayMessage(self, text):
        pass

def main():
    import sys
    from qtpy.QtWidgets import QApplication
    from qtpy.QtCore import QCoreApplication
    from util.ConfigUtil import ConfigUtil
    from util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.noQt = False
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    dialog = DownloadBibleMp3Dialog(DummyParent())
    dialog.exec_()

if __name__ == '__main__':
    main()

    sourceDir = "/Users/otseng/Downloads/KJV_OT_Audio_TB/*"
    destDir = "/Users/otseng/workspace/UniqueBible_MP3_KJV"
    # DownloadBibleMp3Util.moveFiles(sourceDir, destDir, True)
    # DownloadBibleMp3Util.zipFiles(destDir, True)
