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
            "BBE (British accent)": ("BBE", "otseng/UniqueBible_MP3_BBE_british", "british"),
            "KJV (American accent)": ("KJV", "otseng/UniqueBible_MP3_KJV", "default"),
            "KJV (American soft music)": ("KJV", "otseng/UniqueBible_MP3_KJV_soft_music", "soft-music"),
            "NET (Google TTS)": ("NET", "eliranwong/NewEnglishTranslationMP3", "default"),
            "NHEB (Indian accent)": ("NHEB", "otseng/UniqueBible_MP3_NHEB_indian", "indian"),
            "WEB (American accent)": ("WEB", "otseng/UniqueBible_MP3_WEB", "default"),
            "CUV (Chinese)": ("CUV", "otseng/UniqueBible_MP3_CUV", "default"),
            "HHBD (Hindi)": ("HHBD", "otseng/UniqueBible_MP3_HHBD", "default"),
            "RVA (Spanish)": ("RVA", "otseng/UniqueBible_MP3_RVA", "default"),
            "TR (Modern Greek)": ("TR", "otseng/UniqueBible_MP3_TR", "modern"),
        }
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["gitHubBibleMp3Files"])
        self.setMinimumSize(150, 450)
        self.selectedRendition = None
        self.selectedText = None
        self.selectedRepo = None
        self.selectedDirectory = None
        self.settingBibles = False
        self.thread = None
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel(config.thisTranslation["gitHubBibleMp3Files"])
        mainLayout.addWidget(title)

        self.versionsLayout = QVBoxLayout()
        self.renditionsList = QListWidget()
        self.renditionsList.itemClicked.connect(self.selectItem)
        for rendition in self.bibles.keys():
            self.renditionsList.addItem(rendition)
        self.renditionsList.setMaximumHeight(100)
        self.versionsLayout.addWidget(self.renditionsList)
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

        self.renditionsList.item(0).setSelected(True)
        bible = self.renditionsList.item(0).text()
        self.selectRendition(bible)

        self.downloadButton.setDefault(True)
        QTimer.singleShot(0, self.downloadButton.setFocus)

    def selectItem(self, item):
        self.selectRendition(item.text())

    def selectRendition(self, rendition):
        from util.GithubUtil import GithubUtil

        self.selectedRendition = rendition
        self.downloadTable.setEnabled(True)
        self.selectedText, self.selectedRepo, self.selectedDirectory = self.bibles[self.selectedRendition]
        self.github = GithubUtil(self.selectedRepo)
        self.repoData = self.github.getRepoData()
        self.settingBibles = True
        self.dataViewModel.clear()
        rowCount = 0
        for file in self.repoData.keys():
            if len(str(file)) > 3:
                engFullBookName = file[3:]
            else:
                engFullBookName = BibleBooks().eng[str(int(file))][1]
            item = QStandardItem(file[:3].strip())
            folder = os.path.join("audio", "bibles", self.selectedText, self.selectedDirectory, file)
            folderWithName = os.path.join("audio", "bibles", self.selectedText, self.selectedDirectory, file + " " + engFullBookName)
            if os.path.exists(folder) or os.path.exists(folderWithName):
                item.setCheckable(False)
                item.setCheckState(Qt.Unchecked)
                item.setEnabled(False)
            else:
                item.setCheckable(True)
                item.setCheckState(Qt.Checked)
                item.setEnabled(True)
            self.dataViewModel.setItem(rowCount, 0, item)
            item = QStandardItem(engFullBookName)
            self.dataViewModel.setItem(rowCount, 1, item)
            if os.path.exists(folder) or os.path.exists(folderWithName):
                item = QStandardItem("Installed")
                self.dataViewModel.setItem(rowCount, 2, item)
            else:
                item = QStandardItem("")
                self.dataViewModel.setItem(rowCount, 2, item)
            rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels(
            [config.thisTranslation["menu_book"], config.thisTranslation["name"], ""])
        self.downloadTable.setColumnWidth(0, 90)
        self.downloadTable.setColumnWidth(1, 125)
        self.downloadTable.setColumnWidth(2, 125)
        # self.downloadTable.resizeColumnsToContents()
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
        folder = os.path.join("audio", "bibles", self.selectedText)
        if not os.path.exists(folder):
            os.mkdir(folder)
        folder = os.path.join("audio", "bibles", self.selectedText, self.selectedDirectory)
        if not os.path.exists(folder):
            os.mkdir(folder)
        self.thread = QThread()
        self.worker = DownloadFromGitHub(self.github, self.repoData, self.dataViewModel, self.selectedText, self.selectedDirectory)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.worker.deleteLater)
        self.worker.finished.connect(self.finishedDownloading)
        self.worker.progress.connect(self.setStatus)
        self.thread.start()

    def finishedDownloading(self, count):
        self.selectRendition(self.selectedRendition)
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

    def __init__(self, github, repoData, dataViewModel, selectedText, selectedDirectory):
        super(DownloadFromGitHub, self).__init__()
        self.github = github
        self.repoData = repoData
        self.dataViewModel = dataViewModel
        self.selectedText = selectedText
        self.selectedDirectory = selectedDirectory

    def run(self):
        self.progress.emit(config.thisTranslation["message_installing"])
        folder = os.path.join("audio", "bibles", self.selectedText, self.selectedDirectory)
        count = 0
        for index in range(self.dataViewModel.rowCount()):
            if self.dataViewModel.item(index).checkState() == Qt.Checked:
                bookNum = self.dataViewModel.item(index).text()
                filename = ""
                for key in self.repoData.keys():
                    if key.startswith(bookNum):
                        filename = key
                        break
                file = os.path.join(folder, filename+".zip")
                msg = "Download " + filename
                self.progress.emit(msg)
                self.github.downloadFile(file, self.repoData[filename])
                with zipfile.ZipFile(file, 'r') as zipped:
                    zipped.extractall(folder)
                os.remove(file)
                srcFiles = "{0}/{1}*.mp3".format(folder, bookNum)
                DownloadBibleMp3Util.moveFiles(srcFiles, folder)
                count += 1
        self.finished.emit(count)


class DownloadBibleMp3Util:

    @staticmethod
    def moveFiles(sourceDir, destDir, debugOutput = False):
        if not sourceDir.endswith(("*.mp3")):
            sourceDir = os.path.join(sourceDir, "*.mp3")
        files = glob.glob(sourceDir)
        for file in sorted(files):
            base = os.path.basename(file)
            folder = base[:2]
            # folder = int(base[1:3])
            bookNum = int(folder)
            if base[0] == 'B':
                bookNum += 39
            bookName = BibleBooks.eng[str(bookNum)][1]
            bookName = bookName.replace(" ", "")
            destFolder = os.path.join(destDir, folder + " " + bookName)
            if not os.path.exists(destFolder):
                os.mkdir(destFolder)
            newFile = os.path.join(destFolder, base)
            os.rename(file, newFile)
            if debugOutput:
                print(newFile)

    @staticmethod
    def moveGreekFiles(sourceDir, destDir, debugOutput = False):
        for bookNum in range(40, 67):
            dirs = glob.glob("{0}/{1} *".format(sourceDir, bookNum))
            dir = dirs[0]
            baseDir = os.path.basename(dir)
            files = glob.glob("{0}/{1}".format(dir, "*.mp3"))
            for file in files:
                baseFile = os.path.basename(file)
                destFolder = os.path.join(destDir, baseDir)
                if not os.path.exists(destFolder):
                    os.mkdir(destFolder)
                newFile = os.path.join(destDir, "{0}/{1}_{2}".format(baseDir, bookNum, baseFile))
                os.rename(file, newFile)
                if debugOutput:
                    print("From:" + file)
                    print("To:" + newFile)

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
            # if count >= 39:
            #     break

    @staticmethod
    def renameChinese(sourceDir, destDir, debugOutput = False):
        offset = 0
        sourceFiles = sourceDir
        if not sourceFiles.endswith("*.mp3"):
            sourceFiles += "/*.mp3"
        files = glob.glob(sourceFiles)
        for file in sorted(files):
            base = os.path.basename(file)
            bookNum = int(base[:2]) + offset
            bookName = BibleBooks.eng[str(bookNum)][1]
            bookName = bookName.replace(" ", "")
            try:
                chapter = int(base[-7:-4])
            except:
                try:
                    chapter = int(base[-6:-4])
                except:
                    try:
                        chapter = int(base[-5:-4])
                    except:
                        chapter = 1
            newFile = "{0}_{1}{2}.mp3".format("{:02d}".format(bookNum), bookName, "{:03d}".format(chapter))
            os.rename(os.path.join(sourceDir, file), os.path.join(sourceDir, newFile))
            if debugOutput:
                print(newFile)

    @staticmethod
    def fixFilenamesInAllSubdirectories(sourceDir, debugOutput = False):
        directories = [d for d in os.listdir(sourceDir) if
                       os.path.isdir(os.path.join(sourceDir, d)) and not d == ".git"]
        for subdir in sorted(directories):
            dir = os.path.join(sourceDir, subdir)
            DownloadBibleMp3Util.fixFilenamesInDirectory(dir, debugOutput)

    @staticmethod
    def fixFilenamesInDirectory(sourceDir, debugOutput=False):
        if "Matthew" in sourceDir:
            pass
        sourceFiles = os.path.join(sourceDir, "*.mp3")
        files = glob.glob(sourceFiles)
        for file in sorted(files):
            base = os.path.basename(file)

            # bookNum = int(base[1:3])
            # if base[0] == 'B':
            #     bookNum += 39

            # bookNum = int(base[:2])

            bookNum = int(base[:2])
            bookNum += 39

            bookName = BibleBooks.eng[str(bookNum)][1]
            bookName = bookName.replace(" ", "")
            try:
                chapter = int(base[-6:-4])
                # chapter = int(base[6:8])
            except:
                try:
                    chapter = int(base[-6:-4])
                except:
                    try:
                        chapter = int(base[-5:-4])
                    except:
                        chapter = 1
            newFile = "{0}_{1}{2}.mp3".format("{:02d}".format(bookNum), bookName, "{:03d}".format(chapter))
            os.rename(os.path.join(sourceDir, file), os.path.join(sourceDir, newFile))
            if debugOutput:
                print(newFile)

    @staticmethod
    def renameDirs(sourceDir, debugOutput=False):
        directories = [d for d in os.listdir(sourceDir) if
                       os.path.isdir(os.path.join(sourceDir, d)) and not d == ".git"]
        for dir in sorted(directories):
            bookNum = dir[:2]
            if bookNum != dir:
                os.rename(os.path.join(sourceDir, dir), os.path.join(sourceDir, bookNum))
                if debugOutput:
                    print(bookNum)

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
    # main()

    """
    KJV
    https://www.audiotreasure.com/audioindex.htm
    """
    # sourceDir = "/Users/otseng/Downloads/temp"
    # destDir = "/Users/otseng/dev/UniqueBible/audio/bibles/KJV/soft-music"
    # DownloadBibleMp3Util.fixFilenamesInDirectory(sourceDir, True)
    # DownloadBibleMp3Util.moveFiles(sourceDir, destDir, True)
    # DownloadBibleMp3Util.zipFiles(destDir, True)

    # destDir = "/Users/otseng/dev/UniqueBible/audio/bibles/KJV/soft-music"
    # DownloadBibleMp3Util.zipFiles(destDir, True)

    '''
    Chinese
    https://www.audiotreasure.com/audioindex.htm
    '''
    # sourceDir = "/Users/otseng/Downloads"
    # destDir = "/Users/otseng/dev/UniqueBible/audio/bibles/CUV/default"
    # DownloadBibleMp3Util.renameChinese(sourceDir, destDir, True)
    # DownloadBibleMp3Util.moveFiles(sourceDir, destDir, True)

    # sourceDir = "/Users/otseng/dev/UniqueBible/audio/bibles/CUV/default"
    # DownloadBibleMp3Util.zipFiles(sourceDir, True)

    # sourceDir = "/Users/otseng/Downloads"
    # destDir = "/Users/otseng/dev/UniqueBible/audio/bibles/CUV/default"
    # DownloadBibleMp3Util.renameChinese(sourceDir, destDir, True)
    # DownloadBibleMp3Util.moveFiles(sourceDir, destDir, True)

    '''
    WEB
    https://www.audiotreasure.com/webindex.htm
    '''
    # sourceDir = "/Users/otseng/Downloads/temp"
    # DownloadBibleMp3Util.fixFilenamesInDirectory(sourceDir, True)

    # sourceDir = "/Users/otseng/Downloads/temp"
    # destDir = "/Users/otseng/dev/UniqueBible/audio/bibles/WEB/default"
    # DownloadBibleMp3Util.moveFiles(sourceDir, destDir, True)

    # sourceDir = "/Users/otseng/dev/UniqueBible/audio/bibles/WEB/default"
    # DownloadBibleMp3Util.zipFiles(sourceDir, True)

    '''
    ESV
    '''
    # sourceDir = "/Users/otseng/dev/UniqueBible/audio/bibles/ESV/default"
    # DownloadBibleMp3Util.fixFilenamesInAllSubdirectories(sourceDir, True)

    # sourceDir = "/Users/otseng/dev/UniqueBible/audio/bibles/ESV/default"
    # DownloadBibleMp3Util.zipFiles(sourceDir, True)

    '''
    NSRV
    '''
    # sourceDir = "/Users/otseng/Downloads/save"
    # destDir = "/Users/otseng/dev/UniqueBible/audio/bibles/NSRV/default"
    # DownloadBibleMp3Util.moveFiles(sourceDir, destDir, True)

    '''
    NHEB
    '''
    # sourceDir = "/Users/otseng/Downloads"
    # destDir = "/Users/otseng/dev/UniqueBible/audio/bibles/NHEB/indian"
    # DownloadBibleMp3Util.moveFiles(sourceDir, destDir, True)

    # sourceDir = "/Users/otseng/dev/UniqueBible/audio/bibles/NHEB/indian"
    # DownloadBibleMp3Util.zipFiles(sourceDir, True)

    '''
    BBE
    '''
    # sourceDir = "/Users/otseng/Downloads/save"
    # destDir = "/Users/otseng/dev/UniqueBible/audio/bibles/BBE/british"
    # DownloadBibleMp3Util.moveFiles(sourceDir, destDir, True)

    # sourceDir = "/Users/otseng/dev/UniqueBible/audio/bibles/BBE/british"
    # DownloadBibleMp3Util.zipFiles(sourceDir, True)

    '''
    RV
    '''
    # sourceDir = "/Users/otseng/Downloads/save"
    # destDir = "/Users/otseng/dev/UniqueBible/audio/bibles/RVA/default"
    # DownloadBibleMp3Util.moveFiles(sourceDir, destDir, True)

    # sourceDir = "/Users/otseng/dev/UniqueBible/audio/bibles/RVA/default"
    # DownloadBibleMp3Util.zipFiles(sourceDir, True)

    '''
    AFV
    https://afaithfulversion.org/genesis/
    '''
    # sourceDir = "/Users/otseng/Downloads/save"
    # destDir = "/Users/otseng/dev/UniqueBible/audio/bibles/AFV/default"
    # DownloadBibleMp3Util.moveFiles(sourceDir, destDir, True)

    '''
    Greek NT
    http://getbible.net/scriptureinstall/Greek__NT_Textus_Receptus_(1550_1894)__text__LTR.txt
    '''
    # sourceDir = "/Users/otseng/Downloads"
    # destDir = "/Users/otseng/dev/UniqueBible/audio/bibles/TR/modern"
    # DownloadBibleMp3Util.moveGreekFiles(sourceDir, destDir, True)

    # sourceDir = "/Users/otseng/dev/UniqueBible/audio/bibles/TR/modern"
    # DownloadBibleMp3Util.zipFiles(sourceDir, True)

    '''
    HHBD
    '''
    # sourceDir = "/Users/otseng/Downloads/HHBD"
    # DownloadBibleMp3Util.fixFilenamesInAllSubdirectories(sourceDir, True)

    sourceDir = "/Users/otseng/dev/UniqueBible/audio/bibles/HHBD/default"
    DownloadBibleMp3Util.zipFiles(sourceDir, True)
