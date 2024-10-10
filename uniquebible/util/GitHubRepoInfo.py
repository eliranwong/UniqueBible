
class GitHubRepoInfo:

    # repo, directory, language, extension
    bibles = ("otseng/UniqueBible_Bibles", "bibles", "githubBibles", "bible")
    biblesIndex = ("otseng/UniqueBible_Bibles_Index", "indexes/bible", "githubBiblesIndex", "index")
    commentaries = ("otseng/UniqueBible_Commentaries", "commentaries", "githubCommentaries", "commentary")
    books = ("darrelwright/UniqueBible_Books", "books", "githubBooks", "book")
    statistics = ("otseng/UniqueBible_Statistics", "statistics", "githubStatistics", "stats")
    hymnLyrics = ("otseng/UniqueBible_Hymn_Lyrics", "books", "githubHymnLyrics", "book")
    maps = ("darrelwright/UniqueBible_Maps-Charts", "books", "githubMaps", "book")
    pdf = ("otseng/UniqueBible_PDF", "pdf", "githubPdf", "pdf")
    epub = ("otseng/UniqueBible_EPUB", "epub", "githubEpub", "epub")
    pluginsContext = ("eliranwong/UniqueBible_Plugins_Context", "../plugins/context", "gitHubPluginsContext", "py")
    pluginsMenu = ("eliranwong/UniqueBible_Plugins_Menu", "../plugins/menu", "gitHubPluginsMenu", "py")
    pluginsStartup = ("otseng/UniqueBible_Plugins_Startup", "../plugins/startup", "gitHubPluginsStartup", "py")
    pluginsShutdown = ("otseng/UniqueBible_Plugins_Shutdown", "../plugins/shutdown", "gitHubPluginsShutdown", "py")
    pluginsLayout = ("otseng/UniqueBible_Plugins_Layout", "../plugins/layout", "gitHubPluginsLayout", "py")
    devotionals = ("otseng/UniqueBible_Devotionals", "devotionals", "gitHubDevotionals", "devotion")
    bibleAbbreviations = ("otseng/UniqueBible_Bible_Abbreviations", "../plugins/language", "gitHubBibleAbbreviations", "biblebooks")

    types = ["bibles", "books", "commentaries", "statistics", "devotionals", "pdf", "docx", "mp3", "mp4"]
             # "epub", "plugins-context", "plugins-layout", "plugins-menu", "plugins-startup", "plugins-shutdown"]

    @staticmethod
    def buildInfo(repo, type, directory=""):
        infoMap = {"bibles": ("bibles", "githubBibles", "bible"),
                   "books": ("books", "githubBooks", "book"),
                   "commentaries": ("commentaries", "githubCommentaries", "commentary"),
                   "devotionals": ("devotionals", "gitHubDevotionals", "devotion"),
                   "statistics": ("statistics", "githubStatistics", "stats"),
                   "epub": ("epub", "githubEpub", "epub"),
                   "pdf": ("pdf", "githubPdf", "pdf"),
                   "docx": ("docx", "wordDocument", "docx"),
                   "mp3": ("../music", "download_mp3", "mp3"),
                   "mp4": ("../video", "download_mp4", "mp4"),
                   "plugins-context": ("../plugins/context", "gitHubPluginsContext", "py"),
                   "plugins-layout": ("../plugins/layout", "gitHubPluginsLayout", "py"),
                   "plugins-menu": ("../plugins/menu", "gitHubPluginsMenu", "py"),
                   "plugins-startup": ("../plugins/startup", "gitHubPluginsStartup", "py"),
                   "plugins-shutdown": ("../plugins/shutdown", "gitHubPluginsShutdown", "py")
                   }
        repo = GitHubRepoInfo.fixRepoUrl(repo)
        data = (repo,) + infoMap[type]
        return data

    @staticmethod
    def getLibraryType(type):
        map = {"bibles": "BIBLE",
               "books": "BOOK",
               "commentaries": "COMM",
               "devotionals": "DEVOTIONAL",
               "stats": "STATS",
               "pdf": "PDF",
               "docx": "DOCX",
               "epub": "EPUB",
               "mp3": "MP3",
               "mp4": "MP4",
               "plugins-context": "PLUGIN",
               "plugins-layout": "PLUGIN",
               "plugins-menu": "PLUGIN",
               "plugins-startup": "PLUGIN",
               "plugins-shutdown": "PLUGIN",
               }
        return map[type]

    @staticmethod
    def fixRepoUrl(url):
        url = url.replace("https://github.com/", "")
        return url