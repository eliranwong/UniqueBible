import os, sqlite3, re, config
from BiblesSqlite import BiblesSqlite
from BibleVerseParser import BibleVerseParser

class VerseData:

    def __init__(self, filename):
        self.filename = filename

    def getContent(self, bcvTuple):
        b, *_ = bcvTuple
        if b < 40:
            verseData = VerseONTData("{0}OT".format(self.filename))
        else:
            verseData = VerseONTData("{0}NT".format(self.filename))
        content = verseData.getContent(bcvTuple)
        del verseData
        return content


class VerseONTData:

    def __init__(self, filename):
        # connect bibles.sqlite
        self.database = os.path.join(config.marvelData, "data", "{0}.data".format(filename))
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getContent(self, bcvTuple):
        query = "SELECT Scripture FROM Bible WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, bcvTuple)
        content = self.cursor.fetchone()
        if not content:
            return "[not applicable]"
        else:
            return content[0]


class CrossReferenceSqlite:

    def __init__(self):
        # connect cross-reference.sqlite
        self.database = os.path.join(config.marvelData, "cross-reference.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def bcvToVerseReference(self, b, c, v):
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)

    def scrollMapper(self, bcvTuple):
        query = "SELECT Information FROM ScrollMapper WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, bcvTuple)
        information = self.cursor.fetchone()
        if not information:
            return "[not applicable]"
        else:
            return information[0]

    def tske(self, bcvTuple):
        query = "SELECT Information FROM TSKe WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, bcvTuple)
        information = self.cursor.fetchone()
        if not information:
            return "[not applicable]"
        else:
            return information[0]


class CollectionsSqlite:

    def __init__(self):
        # connect collections.sqlite
        self.database = os.path.join(config.marvelData, "collections3.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def readData(self, table, toolNumber):
        query = "SELECT Topic, Passages FROM {0} WHERE Tool=? AND Number=?".format(table)
        self.cursor.execute(query, toolNumber)
        information = self.cursor.fetchone()
        if not information:
            return "[not applicable]"
        else:
            return information

    def getChapterParallels(self, b, c):
        query = "SELECT Tool, Number, Topic FROM PARALLEL WHERE Passages LIKE ?"
        searchString = '%<ref onclick="bcv({0},{1},%'.format(b, c)
        self.cursor.execute(query, (searchString,))
        return "<br>".join(['<ref onclick="harmony({0}, {1})">[Go to]</ref> {2}'.format(tool, number, topic) for tool, number, topic in self.cursor.fetchall()])

    def getChapterPromises(self, b, c):
        query = "SELECT Tool, Number, Topic FROM PROMISES WHERE Passages LIKE ?"
        searchString = '%<ref onclick="bcv({0},{1},%'.format(b, c)
        self.cursor.execute(query, (searchString,))
        return "<br>".join(['<ref onclick="promise({0}, {1})">[Go to]</ref> {2}'.format(tool, number, topic) for tool, number, topic in self.cursor.fetchall()])

class ImageSqlite:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "images.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def exportImage(self, module, entry):
        query = "SELECT image FROM {0} WHERE path = ?".format(module)
        entry = "{0}_{1}".format(module, entry)
        self.cursor.execute(query, (entry,))
        information = self.cursor.fetchone()
        if information:
            htmlImageFolder = os.path.join("htmlResources", "images")
            if not os.path.isdir(htmlImageFolder):
                os.mkdir(htmlImageFolder)
            if module == "EXLBL":
                module = "exlbl"
            imageFolder = os.path.join(htmlImageFolder, module)
            if not os.path.isdir(imageFolder):
                os.mkdir(imageFolder)
            imageFilePath = os.path.join(imageFolder, entry)
            if not os.path.isfile(imageFilePath):
                imagefile = open(imageFilePath, "wb")
                imagefile.write(information[0])
                imagefile.close()


class IndexesSqlite:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "indexes2.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        self.setResourceList()

    def __del__(self):
        self.connection.close()

    def setResourceList(self):
        self.topicList = [
            ("HIT", "Hitchcock's New and Complete Analysis of the Bible"),
            ("NAV", "Nave's Topical Bible"),
            ("TCR", "Thompson Chain References"),
            ("TNT", "Torrey's New Topical Textbook"),
            ("TOP", "Topical Bible"),
            ("EXLBT", "Search ALL Topical References")
        ]
        self.dictionaryList = [
            ("AMT", "American Tract Society Dictionary"),
            ("BBD", "Bridgeway Bible Dictionary"),
            ("BMC", "Freeman's Handbook of Bible Manners and Customs"),
            ("BUC", "Buck's A Theological Dictionary"),
            ("CBA", "Companion Bible Appendices"),
            ("DRE", "Dictionary Of Religion And Ethics"),
            ("EAS", "Easton's Illustrated Bible Dictionary"),
            ("FAU", "Fausset's Bible Dictionary"),
            ("FOS", "Bullinger's Figures of Speech"),
            ("HBN", "Hitchcock's Bible Names Dictionary"),
            ("MOR", "Morrish's Concise Bible Dictionary"),
            ("PMD", "Poor Man's Dictionary"),
            ("SBD", "Smith's Bible Dictionary"),
            ("USS", "Annals of the World"),
            ("VNT", "Vine's Expository Dictionary of New Testament Words"),
        ]
        self.encyclopediaList = [
            ("DAC", "Hasting's Dictionary of the Apostolic Church"),
            ("DCG", "Hasting's Dictionary Of Christ And The Gospels"),
            ("HAS", "Hasting's Dictionary of the Bible"),
            ("ISB", "International Standard Bible Encyclopedia"),
            ("KIT", "Kitto's Cyclopedia of Biblical Literature"),
            ("MSC", "McClintock & Strong's Cyclopedia of Biblical Literature"),
        ]

    def getAllIndexes(self, bcvTuple):
        indexItems = (
            (config.thisTranslation["menu5_characters"], "exlbp", self.searchCharacters()),
            (config.thisTranslation["menu5_locations"], "exlbl", self.searchLocations()),
            (config.thisTranslation["menu5_topics"], "exlbt", self.searchTopics()),
            (config.thisTranslation["context1_dict"], "dictionaries", self.searchDictionaries()),
            (config.thisTranslation["context1_encyclopedia"], "encyclopedia", self.searchEncyclopedia()),
        )
        content = ""
        for feature, module, searchOption in indexItems:
            content += "<h2>{0}</h2>".format(feature)
            content += self.getContent(module, bcvTuple)
            content += "<p>{0}</p>".format(searchOption)
        return content

    def getChapterIndexes(self, bcTuple):
        indexItems = (
            (config.thisTranslation["menu5_characters"], "exlbp", self.searchCharacters()),
            (config.thisTranslation["menu5_locations"], "exlbl", self.searchLocations()),
            #(config.thisTranslation["menu5_topics"], "exlbt", self.searchTopics()),
            #(config.thisTranslation["context1_dict"], "dictionaries", self.searchDictionaries()),
            #(config.thisTranslation["context1_encyclopedia"], "encyclopedia", self.searchEncyclopedia()),
        )
        content = ""
        for feature, module, searchOption in indexItems:
            content += "<h2>{0}</h2>".format(feature)
            content += self.getChapterContent(module, bcTuple)
            content += "<p>{0}</p>".format(searchOption)
        return content

    def searchCharacters(self):
        content = "<button class='feature' onclick='document.title={0}_command:::SEARCHTOOL:::EXLBP:::{0}'>search for a character</button>".format('"')
        content += "<br><button class='feature' onclick='document.title={0}_command:::SEARCHTOOL:::HBN:::{0}'>search for a name & its meaning</button>".format('"')
        return content

    def searchLocations(self):
        return "<button class='feature' onclick='document.title={0}_command:::SEARCHTOOL:::EXLBL:::{0}'>search for a location</button>".format('"')

    def searchTopics(self):
        action = "searchResource(this.value)"
        optionList = [("", "[search a topical reference]")] + self.topicList
        return self.formatSelectList(action, optionList)

    def searchDictionaries(self):
        action = "searchResource(this.value)"
        optionList = [("", "[search a dictionary]")] + self.dictionaryList
        return self.formatSelectList(action, optionList)

    def searchEncyclopedia(self):
        action = "searchResource(this.value)"
        optionList = [("", "[search an encyclopeida]")] + self.encyclopediaList
        return self.formatSelectList(action, optionList)

    def formatSelectList(self, action, optionList):
        selectForm = "<select onchange='{0}'>".format(action)
        for value, description in optionList:
            selectForm += "<option value='{0}'>{1}</option>".format(value, description)
        selectForm += "</select>"
        return selectForm

    def getContent(self, table, bcvTuple):
        query = "SELECT Information FROM {0} WHERE Book = ? AND Chapter = ? AND Verse = ?".format(table)
        self.cursor.execute(query, bcvTuple)
        content = self.cursor.fetchone()
        if not content:
            return "[not applicable]"
        else:
            if table == "dictionaries" or table == "encyclopedia":
                return "<table>{0}</table>".format(content[0])
            else:
                return content[0]

    def getChapterContent(self, table, bcTuple):
        query = "SELECT * FROM {0} WHERE Book = ? AND Chapter = ?".format(table)
        self.cursor.execute(query, bcTuple)
        parser = BibleVerseParser(config.parserStandarisation)
        content = "<br>".join(['[<ref onclick="bcv({0},{1},{2})">{1}:{2}</ref>] {3}'.format(b, c, v, re.sub("<p>|</p>", " ", text)) for b, c, v, text in self.cursor.fetchall()])
        if not content:
            return "[not applicable]"
        else:
            if table == "dictionaries" or table == "encyclopedia":
                return "<table>{0}</table>".format(content)
            else:
                return content


class SearchSqlite:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "search.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getContent(self, module, entry):
        query = "SELECT link FROM {0} WHERE EntryID = ?".format(module)
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return content[0]

    def getSimilarContent(self, module, entry):
        query = "SELECT link FROM {0} WHERE EntryID LIKE ? AND EntryID != ?".format(module)
        self.cursor.execute(query, ("%{0}%".format(entry), entry))
        contentList = [m[0] for m in self.cursor.fetchall()]
        if not contentList:
            return "[not found]"
        else:
            return "<br>".join(contentList)


class DictionaryData:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "data", "dictionary.data")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getContent(self, entry):
        query = "SELECT content FROM Dictionary WHERE path = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            contentText = content[0]

            # deal with images
            imageList = [m for m in re.findall('src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', contentText)]
            if imageList:
                imageSqlite = ImageSqlite()
                for (imgModule, imgEntry) in imageList:
                    imageSqlite.exportImage(imgModule, imgEntry)
                del imageSqlite
            contentText = re.sub('src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', r'src="images/\1/\1_\2"', contentText)
            contentText = re.sub("src='getImage\.php\?resource=([^']*?)&id=([^']*?)'", r"src='images/\1/\1_\2'", contentText)

            abb = entry[:3]
            moduleName = dict(IndexesSqlite().dictionaryList)[abb]
            searchButton = "&ensp;<button class='feature' onclick='document.title=\"_command:::SEARCHTOOL:::{0}:::\"'>search</button>".format(abb)
            return "<p><b>{0}</b> {1}</p>{2}".format(moduleName, searchButton, contentText)


class EncyclopediaData:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "data", "encyclopedia.data")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getContent(self, module, entry):
        query = "SELECT content FROM {0} WHERE path = ?".format(module)
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            contentText = content[0]

            # deal with images
            imageList = [m for m in re.findall('src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', contentText)]
            if imageList:
                imageSqlite = ImageSqlite()
                for (imgModule, imgEntry) in imageList:
                    imageSqlite.exportImage(imgModule, imgEntry)
                del imageSqlite
            contentText = re.sub('src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', r'src="images/\1/\1_\2"', contentText)
            contentText = re.sub("src='getImage\.php\?resource=([^']*?)&id=([^']*?)'", r"src='images/\1/\1_\2'", contentText)

            moduleName = dict(IndexesSqlite().encyclopediaList)[module]
            searchButton = "&ensp;<button class='feature' onclick='document.title=\"_command:::SEARCHTOOL:::{0}:::\"'>search</button>".format(module)
            return "<p><b>{0}</b> {1}</p>{2}".format(moduleName, searchButton, contentText)


class WordData:

    def getContent(self, testament, entry):
        wordData = WordONTData(testament)
        content = wordData.getContent(entry)
        del wordData
        return content


class WordONTData:

    def __init__(self, testament):
        self.testament = testament
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "data", "word{0}.data".format(self.testament))
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getContent(self, entry):
        query = "SELECT Information FROM {0} WHERE EntryID = ?".format(self.testament)
        if self.testament == "NT":
            entry = "{0:06d}".format(int(entry))
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return content[0]


class ExlbData:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "data", "exlb3.data")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getContent(self, module, entry):
        query = "SELECT content FROM {0} WHERE path = ?".format(module)
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            if module == "exlbl":
                content = content[0]
                if not config.myGoogleApiKey or not config.internet or config.alwaysDisplayStaticMaps:
                    # display static google map if users do not have a google api key or internet connection
                    content = re.sub('<blid="(.*?)">.*?MYGOOGLEAPIKEY\]&callback=myMap"></script>', r'<p align="center"><img src="images/exlbl_large/\1.png"></p>', content)
                    # adjust zoom level with the following line
                    #content = content.replace("&z=10'", "&z=8'")
                else:
                    content = content.replace("[MYGOOGLEAPIKEY]", config.myGoogleApiKey)
                return content
            else:
                moduleName = {
                    "exlbp": "Exhaustive Library of Bible People",
                    "exlbl": "Exhaustive Library of Bible Locations",
                    "exlbt": "Exhaustive Library of Bible Topics",
                }
                searchButton = "&ensp;<button class='feature' onclick='document.title=\"_command:::SEARCHTOOL:::{0}:::\"'>search</button>".format(module.upper())
                return "<p><b>{0}</b> {1}</p>{2}".format(moduleName[module], searchButton, content[0])


class Commentary:

    def __init__(self, text=False):
        if text:
            self.text = text
            if self.text in self.getCommentaryList():
                self.database = os.path.join(config.marvelData, "commentaries", "c{0}.commentary".format(text))
                self.connection = sqlite3.connect(self.database)
                self.cursor = self.connection.cursor()

    def __del__(self):
        try:
            self.connection.close()
        except:
            pass

    def commentaryInfo(self):
        query = "SELECT title FROM Details"
        self.cursor.execute(query)
        info = self.cursor.fetchone()
        if info:
            return info[0]
        else:
            return ""

    def bcvToVerseReference(self, b, c, v):
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)

    def formCommentaryTag(self, commentary):
        return "<ref onclick='document.title=\"_commentary:::{0}\"' onmouseover='commentaryName(\"{0}\")'>".format(commentary)

    def formBookTag(self, b):
        bookAbb = self.bcvToVerseReference(b, 1, 1)[:-4]
        return "<ref onclick='document.title=\"_commentary:::{0}.{1}\"' onmouseover='bookName(\"{2}\")'>".format(self.text, b, bookAbb)

    def formChapterTag(self, b, c):
        return "<ref onclick='document.title=\"_commentary:::{0}.{1}.{2}\"' onmouseover='document.title=\"_info:::Chapter {2}\"'>".format(self.text, b, c)

    def formVerseTag(self, b, c, v):
        verseReference = self.bcvToVerseReference(b, c, v)
        return "<ref id='v{0}.{1}.{2}' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"COMMENTARY:::{3}:::{4}\"' onmouseover='document.title=\"_instantVerse:::{3}:::{0}.{1}.{2}\"' ondblclick='document.title=\"_commentary:::{3}.{0}.{1}.{2}\"'>".format(b, c, v, self.text, verseReference)

    def getCommentaryList(self):
        commentaryFolder = os.path.join(config.marvelData, "commentaries")
        commentaryList = [f[1:-11] for f in os.listdir(commentaryFolder) if os.path.isfile(os.path.join(commentaryFolder, f)) and f.endswith(".commentary") and not re.search("^[\._]", f)]
        return sorted(commentaryList)

    def getCommentaries(self):
        commentaryList = self.getCommentaryList()
        commentaries = " ".join(["{0}<button class='feature'>{1}</button></ref>".format(self.formCommentaryTag(commentary), commentary) for commentary in commentaryList])
        return commentaries

    def getBookList(self):
        query = "SELECT DISTINCT Book FROM Commentary ORDER BY Book"
        self.cursor.execute(query)
        return [book[0] for book in self.cursor.fetchall()]

    def getBooks(self):
        bookList = self.getBookList()
        standardAbbreviation = BibleVerseParser(config.parserStandarisation).standardAbbreviation
        return " ".join(["{0}<button class='feature'>{1}</button></ref>".format(self.formBookTag(book), standardAbbreviation[str(book)]) for book in bookList if str(book) in standardAbbreviation])

    def getChapterList(self, b=config.commentaryB):
        t = (b,)
        query = "SELECT DISTINCT Chapter FROM Commentary WHERE Book=? ORDER BY Chapter"
        self.cursor.execute(query, t)
        return [chapter[0] for chapter in self.cursor.fetchall()]

    def getChapters(self, b=config.commentaryB):
        chapterList = self.getChapterList(b)
        return " ".join(["{0}{1}</ref>".format(self.formChapterTag(b, chapter), chapter) for chapter in chapterList])

    def getVerseList(self, b, c):
        biblesSqlite = BiblesSqlite()
        verseList = biblesSqlite.getVerseList(b, c, "KJV")
        del biblesSqlite
        return verseList

    def getVerses(self, b=config.commentaryB, c=config.commentaryC):
        verseList = self.getVerseList(b, c)
        return " ".join(["{0}{1}</ref>".format(self.formVerseTag(b, c, verse), verse) for verse in verseList])

    def getMenu(self, command):
        if self.text in self.getCommentaryList():
            mainVerseReference = self.bcvToVerseReference(config.commentaryB, config.commentaryC, config.commentaryV)
            menu = "<ref onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"COMMENTARY:::{0}:::{1}\"'>&lt;&lt;&lt; {0} - {1}</ref>".format(config.commentaryText, mainVerseReference)
            menu += "<hr><b>{1}</b> {0}".format(self.getCommentaries(), config.thisTranslation["menu4_commentary"])
            items = command.split(".", 3)
            text = items[0]
            if not text == "":
                # i.e. text specified; add book menu
                menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='commentaryName(\"{0}\")'>{0}</span>  <button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"COMMENTARY:::{0}:::{1}\"'>{3}</button>".format(self.text, mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_open"])
                menu += "<hr><b>{1}</b> {0}".format(self.getBooks(), config.thisTranslation["html_book"])
                bcList = [int(i) for i in items[1:]]
                if bcList:
                    check = len(bcList)
                    if check >= 1:
                        # i.e. book specified; add chapter menu
                        menu += "<br><br><b>{1}</b> <span style='color: brown;' onmouseover='bookName(\"{0}\")'>{0}</span>   <button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"COMMENTARY:::{3}:::{0} 1\"'>{2}</button>".format(self.bcvToVerseReference(bcList[0], 1, 1)[:-4], config.thisTranslation["html_current"], config.thisTranslation["html_open"], self.text)
                        menu += "<hr><b>{1}</b> {0}".format(self.getChapters(bcList[0]), config.thisTranslation["html_chapter"])
                    if check >= 2:
                        # i.e. both book and chapter specified; add verse menu
                        menu += "<br><br><b>{3}</b> <span style='color: brown;' onmouseover='document.title=\"_info:::Chapter {0}\"'>{0}</span>  <button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"COMMENTARY:::{1}:::{2}\"'>{4}</button>".format(bcList[1], self.text, self.bcvToVerseReference(bcList[0], bcList[1], 1)[:-2], config.thisTranslation["html_current"], config.thisTranslation["html_open"])
                        menu += "<hr><b>{1}</b> {0}".format(self.getVerses(bcList[0], bcList[1]), config.thisTranslation["html_verse"])
                    if check == 3:
                        menu += "<br><br><b>{5}</b> <span style='color: brown;' onmouseover='document.title=\"_instantVerse:::{0}:::{1}.{2}.{3}\"'>{3}</span> <button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"COMMENTARY:::{0}:::{4}\"'>{6}</button>".format(self.text, bcList[0], bcList[1], bcList[2], mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_open"])
            return menu
        else:
            return "INVALID_COMMAND_ENTERED"

    def getContent(self, verse):
        if self.text in self.getCommentaryList():
            b, c, v, *_ = verse
            chapter = "<h2>{0}{1}</ref></h2>".format(self.formChapterTag(b, c), self.bcvToVerseReference(b, c, v).split(":", 1)[0])
            query = "SELECT Scripture FROM Commentary WHERE Book=? AND Chapter=?"
            self.cursor.execute(query, verse[0:2])
            scripture = self.cursor.fetchone()
            data = scripture[0]
            if config.theme == "dark":
                data = data.replace('color:#000080;', 'color:gray;')
            if scripture:
                chapter += re.sub('onclick="luV\(([0-9]+?)\)"', r'onclick="luV(\1)" onmouseover="qV(\1)" ondblclick="mV(\1)"', data)
                return "<div>{0}</div>".format(chapter)
            else:
                return "<span style='color:gray;'>['{0}' does not contain this chapter.]</span>".format(self.text)
        else:
            return "INVALID_COMMAND_ENTERED"


class LexiconData:

    def __init__(self):
        self.lexiconList = self.getLexiconList()

    def getLexiconList(self):
        lexiconFolder = os.path.join(config.marvelData, "lexicons")
        lexiconList = [f[:-8] for f in os.listdir(lexiconFolder) if os.path.isfile(os.path.join(lexiconFolder, f)) and f.endswith(".lexicon") and not re.search("^[\._]", f)]
        return sorted(lexiconList)

    def getSelectForm(self, entry, module=""):
        lexiconList = [lexicon for lexicon in self.lexiconList if not lexicon == module]
        selectForm = '<p><form action=""><select id="{0}" name="{0}" onchange="lexicon(this.value, this.id)"><optgroup><option value="">More lexicons HERE</option>'.format(entry)
        for lexicon in lexiconList:
            selectForm += '<option value="{0}">{1}</option>'.format(lexicon, Lexicon(lexicon).getInfo())
        selectForm += '</optgroup></select></form></p>'
        return selectForm


class Lexicon:

    def __init__(self, module):
        # connect lexicon module
        self.module = module

        self.database = os.path.join(config.marvelData, "lexicons", "{0}.lexicon".format(module))
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getInfo(self):
        try:
            query = "SELECT Definition FROM Lexicon WHERE Topic = 'info'"
            self.cursor.execute(query)
            info = self.cursor.fetchone()
            if info:
                return info[0]
            else:
                return self.module
        except:
            return self.module

    def getContent(self, entry):
        lexiconData = LexiconData()
        lexiconList = lexiconData.lexiconList

        query = "SELECT Definition FROM Lexicon WHERE Topic = ?"
        self.cursor.execute(query, (entry,))
        information = self.cursor.fetchone()
        contentText = "<h2>{0} - {1}</h2>".format(self.module, entry)
        contentText += "<p>{0}</p>".format(lexiconData.getSelectForm(entry, self.module))
        if not information:
            return contentText+"[not found]"
        else:
            contentText += information[0]
            # deal with images
            imageList = [m for m in re.findall('src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', contentText)]
            if imageList:
                imageSqlite = ImageSqlite()
                for (imgModule, imgEntry) in imageList:
                    imageSqlite.exportImage(imgModule, imgEntry)
                del imageSqlite
            contentText = re.sub('src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', r'src="images/\1/\1_\2"', contentText)
            contentText = re.sub("src='getImage\.php\?resource=([^']*?)&id=([^']*?)'", r"src='images/\1/\1_\2'", contentText)
            return contentText


class BookData:

    def __init__(self):
        self.bookList = self.getBookList()

    def getBookList(self):
        bookFolder = os.path.join(config.marvelData, "books")
        bookList = [f[:-5] for f in os.listdir(bookFolder) if os.path.isfile(os.path.join(bookFolder, f)) and f.endswith(".book") and not re.search("^[\._]", f)]
        bookList = sorted(bookList)
        return [(book, book) for book in bookList]

    def getMenu(self, module=""):
        if module == "":
            module = config.book
        if module in dict(self.bookList).keys():
            books = self.formatSelectList("listBookTopic(this.value)", self.bookList, module)
            topicList = Book(module).getTopicList()
            topics = "<br>".join(["<ref onclick='document.title=\"BOOK:::{0}:::{1}\"'>{1}</ref>".format(module, topic) for topic in topicList])
            config.book = module
            return "<p>{0} &ensp;<button class='feature' onclick='document.title=\"_command:::SEARCHBOOK:::{1}:::\"'>search</button></p><p>{2}</p>".format(books, module, topics)
        else:
            return "INVALID_COMMAND_ENTERED"

    def getSearchedMenu(self, module, searchString, chapterOnly=False):
        if module in dict(self.bookList).keys():
            books = self.formatSelectList("listBookTopic(this.value)", self.bookList, module)
            topicList = Book(module).getSearchedTopicList(searchString, chapterOnly=chapterOnly)
            topics = "<br>".join(["<ref onclick='document.title=\"BOOK:::{0}:::{1}\"'>{1}</ref>".format(module, topic) for topic in topicList])
            config.book = module
            if topics:
                if chapterOnly:
                    searchCommand = "SEARCHBOOKCHAPTER"
                else:
                    searchCommand = "SEARCHBOOK"
                return "<p>{0} &ensp;<button class='feature' onclick='document.title=\"_command:::{3}:::{1}:::\"'>search</button></p><p>{2}</p>".format(books, module, topics, searchCommand)
            else:
                return ""
        else:
            return "INVALID_COMMAND_ENTERED"

    def formatSelectList(self, action, optionList, default):
        selectForm = "<select onchange='{0}'>".format(action)
        for value, description in optionList:
            if value == default:
                selectForm += "<option value='{0}' selected='selected'>{1}</option>".format(value, description)
            else:
                selectForm += "<option value='{0}'>{1}</option>".format(value, description)
        selectForm += "</select>"
        return selectForm

    def getContent(self, module, entry):
        return Book(module).getContent(entry)


class Book:

    def __init__(self, module):
        # connect book module
        self.module = module

        self.database = os.path.join(config.marvelData, "books", "{0}.book".format(module))
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getTopicList(self):
        query = "SELECT DISTINCT Chapter FROM Reference ORDER BY ROWID"
        self.cursor.execute(query)
        return [topic[0] for topic in self.cursor.fetchall()]

    def getSearchedTopicList(self, searchString, chapterOnly=False):
        searchString = "%{0}%".format(searchString)
        if chapterOnly:
            query = "SELECT DISTINCT Chapter FROM Reference WHERE Chapter LIKE ? ORDER BY ROWID"
            self.cursor.execute(query, (searchString,))
        else:
            query = "SELECT DISTINCT Chapter FROM Reference WHERE Chapter LIKE ? OR Content LIKE ? ORDER BY ROWID"
            self.cursor.execute(query, (searchString, searchString))
        return [topic[0] for topic in self.cursor.fetchall()]

    def getContent(self, entry):
        query = "SELECT Content FROM Reference WHERE Chapter=?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not applicable]"
        else:
            config.book = self.module
            content = content[0]
            if config.overwriteBookFont:
                content = re.sub("font-family:[^<>]*?([;'{0}])".format('"'), r"font-family:{0}\1".format(config.font), content)
            if config.overwriteBookFontSize:
                content = re.sub("font-size:[^<>]*?;", "", content)
            for searchString in config.bookSearchString.split("%"):
                if searchString and not searchString == "z":
                    content = re.sub("({0})".format(searchString), r"<z>\1</z>", content, flags=re.IGNORECASE)
                    p = re.compile("(<[^<>]*?)<z>(.*?)</z>", flags=re.M)
                    s = p.search(content)
                    while s:
                        content = re.sub(p, r"\1\2", content)
                        s = p.search(content)
            # add an id so as to scroll to the first result
            content = re.sub("<z>", "<z id='v{0}.{1}.{2}'>".format(config.studyB, config.studyC, config.studyV), content, count=1)
            # return content
            return "<p><ref onclick='document.title={3}BOOK:::{0}{3}'>{0}</ref><br>&gt; <b>{1}</b></p>{2}".format(self.module, entry, content, '"')


