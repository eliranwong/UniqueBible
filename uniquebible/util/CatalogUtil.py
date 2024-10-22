import os
from uniquebible import config
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.GitHubRepoInfo import GitHubRepoInfo


class CatalogUtil:

    localCatalog = None
    bookCatalog = None
    pdfCatalog = None
    folderLookup = {}

    @staticmethod
    def reloadLocalCatalog():
        CatalogUtil.localCatalog = None
        return CatalogUtil.loadLocalCatalog()

    @staticmethod
    def loadLocalCatalog():
        if CatalogUtil.localCatalog is None:
            if config.enableHttpServer:
                config.marvelData = config.marvelDataPrivate if config.webHomePage == "{0}.html".format(config.webPrivateHomePage) else config.marvelDataPublic
            CatalogUtil.localCatalog = []
            pdf = CatalogUtil.loadLocalFiles("PDF", config.marvelData + "/pdf", ".pdf")
            CatalogUtil.pdfCatalog = pdf
            CatalogUtil.localCatalog += pdf
            CatalogUtil.localCatalog += CatalogUtil.loadLocalFiles("MP3", "music", ".mp3")
            CatalogUtil.localCatalog += CatalogUtil.loadLocalFiles("MP4", "video", ".mp4")
            books = CatalogUtil.loadLocalFiles("BOOK", config.marvelData + "/books", ".book")
            CatalogUtil.bookCatalog = books
            CatalogUtil.localCatalog += books
            CatalogUtil.localCatalog += CatalogUtil.loadLocalFiles("DEVOTIONAL", config.marvelData + "/devotionals", ".devotional")
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
        if filename in CatalogUtil.folderLookup:
            return CatalogUtil.folderLookup[filename]
        return ""

    @staticmethod
    def getBooks():
        if config.enableHttpServer:
            CatalogUtil.reloadLocalCatalog()
        elif CatalogUtil.bookCatalog is None:
            CatalogUtil.loadLocalCatalog()
        books = []
        for record in CatalogUtil.bookCatalog:
            book = record[3].replace(".book", "")
            books.append(book)
        return sorted(books)

    @staticmethod
    def getBookList():
        return [(book, book) for book in CatalogUtil.getBooks()]

    @staticmethod
    def getPDFs():
        if CatalogUtil.pdfCatalog is None:
            CatalogUtil.loadLocalCatalog()
        pdfs = []
        for record in CatalogUtil.pdfCatalog:
            pdf = record[3]
            pdfs.append(pdf)
        return sorted(pdfs)

    @staticmethod
    def loadRemoteCatalog():
        data = []
        data += CatalogUtil.loadRemoteFiles("PDF", GitHubRepoInfo.pdf)
        data += CatalogUtil.loadRemoteFiles("BOOK", GitHubRepoInfo.books)
        data += CatalogUtil.loadRemoteFiles("BOOK", GitHubRepoInfo.hymnLyrics)
        data += CatalogUtil.loadRemoteFiles("BOOK", GitHubRepoInfo.maps)
        data += CatalogUtil.loadRemoteFiles("COMM", GitHubRepoInfo.commentaries)
        data += CatalogUtil.loadRemoteFiles("DEVOTIONAL", GitHubRepoInfo.devotionals)
        return data

    @staticmethod
    def loadRemoteFiles(type, repo):
        from uniquebible.util.GithubUtil import GithubUtil
        data = []
        github = GithubUtil(repo[0])
        repoData = github.getRepoData()
        for file in repoData.keys():
            gitrepo = repo[0]
            installFolder = repo[1]
            sha = repoData[file]
            data.append((file, type, repo[0], file, "", gitrepo, installFolder, sha))
        return data
