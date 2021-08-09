import os
import config
from util.FileUtil import FileUtil
from util.GitHubRepoInfo import GitHubRepoInfo
from util.GithubUtil import GithubUtil


class CatalogUtil:

    localCatalog = None
    bookCatalog = None
    folderLookup = {}

    @staticmethod
    def reloadLocalCatalog():
        CatalogUtil.localCatalog = None
        return CatalogUtil.loadLocalCatalog()

    @staticmethod
    def loadLocalCatalog():
        if CatalogUtil.localCatalog is None:
            CatalogUtil.localCatalog = []
            CatalogUtil.localCatalog += CatalogUtil.loadLocalFiles("PDF", config.marvelData + "/pdf", ".pdf")
            CatalogUtil.localCatalog += CatalogUtil.loadLocalFiles("MP3", "music", ".mp3")
            CatalogUtil.localCatalog += CatalogUtil.loadLocalFiles("MP4", "video", ".mp4")
            books = CatalogUtil.loadLocalFiles("BOOK", config.marvelData + "/books", ".book")
            CatalogUtil.bookCatalog = books
            CatalogUtil.localCatalog += books
            CatalogUtil.localCatalog += CatalogUtil.loadLocalFiles("DOCX", config.marvelData + "/docx", ".docx")
            CatalogUtil.localCatalog += CatalogUtil.loadLocalFiles("COMM", config.marvelData + "/commentaries", ".commentary")
        return CatalogUtil.localCatalog

    @staticmethod
    def loadLocalFiles(type, folder, extension):
        data = []
        files = FileUtil.getAllFilesWithExtension(folder, extension)
        for file in files:
            path = os.path.dirname(file)
            filename = os.path.basename(file)
            data.append((file, type, path, filename, folder, "", "", ""))
            CatalogUtil.folderLookup[filename] = path
        return data

    @staticmethod
    def getFolder(filename):
        return CatalogUtil.folderLookup[filename]

    @staticmethod
    def getBooks():
        if CatalogUtil.bookCatalog is None:
            CatalogUtil.loadLocalCatalog()
        books = []
        for record in CatalogUtil.bookCatalog:
            book = record[3].replace(".book", "")
            books.append(book)
        return books

    @staticmethod
    def loadRemoteCatalog():
        data = []
        data += CatalogUtil.loadRemoteFiles("PDF", GitHubRepoInfo.pdf)
        data += CatalogUtil.loadRemoteFiles("BOOK", GitHubRepoInfo.books)
        data += CatalogUtil.loadRemoteFiles("BOOK", GitHubRepoInfo.maps)
        data += CatalogUtil.loadRemoteFiles("COMM", GitHubRepoInfo.commentaries)
        return data

    @staticmethod
    def loadRemoteFiles(type, repo):
        data = []
        github = GithubUtil(repo[0])
        repoData = github.getRepoData()
        for file in repoData.keys():
            gitrepo = repo[0]
            installFolder = repo[1]
            sha = repoData[file]
            data.append((file, type, repo[0], file, "", gitrepo, installFolder, sha))
        return data
