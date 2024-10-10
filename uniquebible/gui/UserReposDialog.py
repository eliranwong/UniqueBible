import os
import pprint
from uniquebible import config
from uniquebible.util.CatalogUtil import CatalogUtil
from uniquebible.util.GitHubRepoInfo import GitHubRepoInfo
from uniquebible.util.GithubUtil import GithubUtil

if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QStandardItemModel, QStandardItem
    from PySide6.QtWidgets import QMessageBox
    from PySide6.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
    from PySide6.QtWidgets import QFileDialog
    from PySide6.QtWidgets import QDialogButtonBox
else:
    from qtpy.QtCore import Qt
    from qtpy.QtGui import QStandardItemModel, QStandardItem
    from qtpy.QtWidgets import QMessageBox
    from qtpy.QtWidgets import QDialog, QLabel, QTableView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QPushButton
    from qtpy.QtWidgets import QFileDialog
    from qtpy.QtWidgets import QDialogButtonBox
from uniquebible.db.UserRepoSqlite import UserRepoSqlite
from uniquebible.gui.MultiLineInputDialog import MultiLineInputDialog

class UserReposDialog(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setWindowTitle(config.thisTranslation["User Custom Repos"])
        self.setMinimumSize(650, 400)
        self.db = UserRepoSqlite()
        self.userRepos = None
        self.setupUI()

    def setupUI(self):
        mainLayout = QVBoxLayout()

        title = QLabel(config.thisTranslation["User Custom Repos"])
        mainLayout.addWidget(title)

        self.reposTable = QTableView()
        self.reposTable.setEnabled(True)
        self.reposTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.reposTable.setSortingEnabled(True)
        self.dataViewModel = QStandardItemModel(self.reposTable)
        self.reposTable.setModel(self.dataViewModel)
        self.dataViewModel.itemChanged.connect(self.repoSelectionChanged)
        self.selectionModel = self.reposTable.selectionModel()
        self.selectionModel.selectionChanged.connect(self.handleSelection)
        mainLayout.addWidget(self.reposTable)
        self.reloadRepos()

        buttonsLayout = QHBoxLayout()
        addButton = QPushButton(config.thisTranslation["add"])
        addButton.clicked.connect(self.addNewRepo)
        buttonsLayout.addWidget(addButton)
        removeButton = QPushButton(config.thisTranslation["remove"])
        removeButton.clicked.connect(self.removeRepo)
        buttonsLayout.addWidget(removeButton)
        editButton = QPushButton(config.thisTranslation["edit"])
        editButton.clicked.connect(self.editRepo)
        buttonsLayout.addWidget(editButton)
        testButton = QPushButton(config.thisTranslation["show"])
        testButton.clicked.connect(self.showRepo)
        buttonsLayout.addWidget(testButton)
        mainLayout.addLayout(buttonsLayout)

        buttonsLayout = QHBoxLayout()
        buildIndexButton = QPushButton(config.thisTranslation["Build Index"])
        buildIndexButton.clicked.connect(self.buildIndex)
        buttonsLayout.addWidget(buildIndexButton)
        importButton = QPushButton(config.thisTranslation["import"])
        importButton.clicked.connect(self.importFile)
        buttonsLayout.addWidget(importButton)
        exportButton = QPushButton(config.thisTranslation["export"])
        exportButton.clicked.connect(self.exportFile)
        buttonsLayout.addWidget(exportButton)
        buttonsLayout.addStretch()
        mainLayout.addLayout(buttonsLayout)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.close)
        self.buttonBox.rejected.connect(self.reject)
        mainLayout.addWidget(self.buttonBox)

        self.setLayout(mainLayout)

    def close(self):
        self.parent.setupMenuLayout(config.menuLayout)

    def reloadRepos(self):
        self.userRepos = self.db.getAll()
        self.dataViewModel.clear()
        rowCount = 0
        for id, active, name, type, repo, directory in self.userRepos:
            item = QStandardItem(str(id))
            self.dataViewModel.setItem(rowCount, 0, item)
            item = QStandardItem(name)
            self.dataViewModel.setItem(rowCount, 1, item)
            item = QStandardItem(type)
            self.dataViewModel.setItem(rowCount, 2, item)
            item = QStandardItem(repo)
            self.dataViewModel.setItem(rowCount, 3, item)
            # item = QStandardItem(directory)
            # self.dataViewModel.setItem(rowCount, 4, item)
            rowCount += 1
        self.dataViewModel.setHorizontalHeaderLabels(["ID", "Name", "Type", "Repo"])
        self.reposTable.resizeColumnsToContents()

    def handleSelection(self, selected, deselected):
        for item in selected:
            row = item.indexes()[0].row()
            self.selectedRepoId = self.dataViewModel.item(row, 0).text()
            self.selectedRepoName = GitHubRepoInfo.fixRepoUrl(self.dataViewModel.item(row, 1).text())
            self.selectedRepoType = self.dataViewModel.item(row, 2).text()
            self.selectedRepoUrl = self.dataViewModel.item(row, 3).text()
            self.selectedRepoDirectory = self.dataViewModel.item(row, 4).text()

    def repoSelectionChanged(self, item):
        pass

    def addNewRepo(self):
        fields = [("Name", ""),
                  ("Type", GitHubRepoInfo.types),
                  ("Repo", ""),
                  ]
        dialog = MultiLineInputDialog("New Repo", fields)
        if dialog.exec():
            data = dialog.getInputs()
            self.db.insert(data[0], data[1], data[2])
            self.reloadRepos()

    def removeRepo(self):
        reply = QMessageBox.question(self, "Delete",
                                     f'Delete {self.selectedRepoName}?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db.delete(self.selectedRepoId)
            self.reloadRepos()

    def editRepo(self):
        fields = [("Name", self.selectedRepoName),
                  ("Type", GitHubRepoInfo.types, self.selectedRepoType),
                  ("Repo", self.selectedRepoUrl)]
        dialog = MultiLineInputDialog("Edit Repo", fields)
        if dialog.exec():
            data = dialog.getInputs()
            self.db.update(self.selectedRepoId, data[0], data[1], data[2], data[3])
            self.reloadRepos()

    def showRepo(self):
        try:
            github = GithubUtil(self.selectedRepoUrl)
            if github.repo is None:
                QMessageBox.information(self, config.thisTranslation["User Custom Repos"],
                                        f"Could not connect to {self.selectedRepoName}")
            else:
                self.parent.runTextCommand(f"_website:::https://github.com/{self.selectedRepoUrl}")
        except Exception as ex:
            QMessageBox.information(self, config.thisTranslation["User Custom Repos"],
                                    f"Could not connect to {self.selectedRepoName}")

    def buildIndex(self):
        data = []
        for id, active, name, type, repo, directory in self.userRepos:
            try:
                data += CatalogUtil.loadRemoteFiles(GitHubRepoInfo.getLibraryType(type),
                                                GitHubRepoInfo.buildInfo(repo, type, directory))
            except:
                pass
        with open("util/GitHubCustomRepoCache.py", "w", encoding="utf-8") as fileObj:
            fileObj.write("gitHubCustomRepoCacheData = {0}\n".format(pprint.pformat(data)))
        QMessageBox.information(self, config.thisTranslation["User Custom Repos"],
                                f"Built custom repo index")

    def importFile(self):
        options = QFileDialog.Options()
        filename, filtr = QFileDialog.getOpenFileName(self,
                                                      config.thisTranslation["import"],
                                                      config.thisTranslation["User Custom Repos"],
                                                      "File (*.repo)",
                                                      "", options)
        if filename:
            try:
                with open(filename, errors='ignore') as f:
                    for line in f:
                        data = line.split(":::")
                        name = data[0].strip()
                        type = data[1].strip()
                        repo = data[2].strip()
                        directory = data[3].strip()
                        if not self.db.checkRepoExists(name, type, repo, directory):
                            self.db.insert(name, type, repo, directory)
            except Exception as e:
                print(e)
            self.reloadRepos()

    def exportFile(self):
        options = QFileDialog.Options()
        fileName, *_ = QFileDialog.getSaveFileName(self,
                                           config.thisTranslation["export"],
                                           config.thisTranslation["User Custom Repos"],
                                           "File (*.repo)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".repo"
            data = ""
            for id, active, name, type, repo, directory in self.db.getAll():
                data += f"{name}:::{type}:::{repo}:::{directory}\n"
            f = open(fileName, "w", encoding="utf-8")
            f.write(data)
            f.close()


class Dummy:

    def __init__(self):
        pass

    def setupMenuLayout(self, layout):
        pass

    def disableBiblesInParagraphs(self):
        pass

    def runTextCommand(self):
        pass

if __name__ == '__main__':
    import sys
    from qtpy.QtWidgets import QApplication
    from qtpy.QtCore import QCoreApplication
    from uniquebible.util.ConfigUtil import ConfigUtil
    from uniquebible.util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.noQt = False
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    dialog = UserReposDialog(Dummy())
    dialog.exec_()