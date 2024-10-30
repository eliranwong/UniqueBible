from uniquebible import config
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.CatalogUtil import CatalogUtil
from uniquebible.util.RegexSearch import RegexSearch

if __name__ == "__main__":
    from uniquebible.util.ConfigUtil import ConfigUtil
    config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"
    config.noQt = True
    ConfigUtil.setup()
    config.noQt = True

import logging
from logging import handlers
import os, apsw, re
from uniquebible.db.BiblesSqlite import BiblesSqlite
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.util.TextUtil import TextUtil

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
        self.connection = apsw.Connection(self.database)
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

    def __init__(self, file=None):
        self.file = file
        if file is None:
            filename = "cross-reference.sqlite"
        else:
            file = os.path.basename(file)
            if not file.endswith(".xref"):
                file += ".xref"
            filename = os.path.join("xref", file)
        self.connection = None
        self.database = os.path.join(config.marvelData, filename)
        if os.path.exists(self.database):
            self.connection = apsw.Connection(self.database)
            self.cursor = self.connection.cursor()

    def __del__(self):
        if self.connection is not None:
            self.connection.close()

    def bcvToVerseReference(self, b, c, v):
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)

    def getCrossReferenceList(self, bcvTuple):
        if self.file is None:
            query = "SELECT Information FROM ScrollMapper WHERE Book=? AND Chapter=? AND Verse=?"
        else:
            query = "SELECT Information FROM CrossReference WHERE Book=? AND Chapter=? AND Verse=?"
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
        self.connection = apsw.Connection(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def readData(self, table, toolNumber):
        query = "SELECT Topic, Passages FROM {0} WHERE Tool=? AND Number=?".format(table)
        self.cursor.execute(query, toolNumber)
        if table == "PARALLEL":
            try:
                parallels, parallelsEntry = toolNumber
                config.parallels, config.parallelsEntry = int(parallels), int(parallelsEntry)
            except:
                pass
        elif table == "PROMISES":
            try:
                promises, promisesEntry = toolNumber
                config.promises, config.promisesEntry = int(promises), int(promisesEntry)
            except:
                pass
        information = self.cursor.fetchone()
        if not information:
            return "[not applicable]"
        else:
            return information

    def getChapterParallels(self, b, c):
        query = TextUtil.getQueryPrefix()
        query += "SELECT Tool, Number, Topic FROM PARALLEL WHERE Passages LIKE ?"
        searchString = '%<ref onclick="bcv({0},{1},%'.format(b, c)
        self.cursor.execute(query, (searchString,))
        return "<br>".join(['<ref onclick="harmony({0}, {1})">[Go to]</ref> {2}'.format(tool, number, topic) for tool, number, topic in self.cursor.fetchall()])

    def getChapterPromises(self, b, c):
        query = TextUtil.getQueryPrefix()
        query += "SELECT Tool, Number, Topic FROM PROMISES WHERE Passages LIKE ?"
        searchString = '%<ref onclick="bcv({0},{1},%'.format(b, c)
        self.cursor.execute(query, (searchString,))
        return "<br>".join(['<ref onclick="promise({0}, {1})">[Go to]</ref> {2}'.format(tool, number, topic) for tool, number, topic in self.cursor.fetchall()])

class ImageSqlite:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "images.sqlite")
        self.connection = apsw.Connection(self.database)
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
        self.connection = apsw.Connection(self.database)
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
        content = "<button class='ubaButton' onclick='document.title={0}_command:::SEARCHTOOL:::EXLBP:::{0}'>search for a character</button>".format('"')
        content += "<br><button class='ubaButton' onclick='document.title={0}_command:::SEARCHTOOL:::HBN:::{0}'>search for a name & its meaning</button>".format('"')
        return content

    def searchLocations(self):
        return "<button class='ubaButton' onclick='document.title={0}_command:::SEARCHTOOL:::EXLBL:::{0}'>search for a location</button>".format('"')

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
        #parser = BibleVerseParser(config.parserStandarisation)
        content = "<br>".join(['[<ref onclick="bcv({0},{1},{2})">{1}:{2}</ref>] {3}'.format(b, c, v, re.sub("<p>|</p>", " ", text)) for b, c, v, text in self.cursor.fetchall()])
        if not content:
            return "[not applicable]"
        else:
            if table == "dictionaries" or table == "encyclopedia":
                return "<table>{0}</table>".format(content)
            else:
                return content

    def getBookLocations(self, b):
        query = "SELECT Information FROM exlbl WHERE Book = ?"
        keys = (b,)
        self.cursor.execute(query, keys)
        return self.cursor.fetchall()

    def getChapterLocations(self, b, c, startV=None, endV=None):
        if startV is not None and endV is not None:
            query = "SELECT Information FROM exlbl WHERE Book = ? AND Chapter = ? AND Verse >= ? AND Verse <= ?"
            keys = (b, c, startV, endV)
        elif startV is not None:
            query = "SELECT Information FROM exlbl WHERE Book = ? AND Chapter = ? AND Verse >= ?"
            keys = (b, c, startV)
        elif endV is not None:
            query = "SELECT Information FROM exlbl WHERE Book = ? AND Chapter = ? AND Verse <= ?"
            keys = (b, c, endV)
        else:
            query = "SELECT Information FROM exlbl WHERE Book = ? AND Chapter = ?"
            keys = (b, c)
        self.cursor.execute(query, keys)
        return self.cursor.fetchall()

    def getVerseLocations(self, b, c, v):
        query = "SELECT Information FROM exlbl WHERE Book = ? AND Chapter = ? AND Verse = ?"
        keys = (b, c, v)
        self.cursor.execute(query, keys)
        return self.cursor.fetchall()


class SearchSqlite:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "search.sqlite")
        self.connection = apsw.Connection(self.database)
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
            #content = re.sub("""(<ref onclick="[^<>]+?\(')([^<>]+?)('\)">)""", r"[<ref>\2</ref> ] " if config.runMode == "terminal" else r"\1\2\3", content[0])
            content = content[0]
            return content

    def getSimilarContent(self, module, entry):
        query = TextUtil.getQueryPrefix()
        query += "SELECT link FROM {0} WHERE EntryID LIKE ? AND EntryID != ?".format(module)
        self.cursor.execute(query, ("%{0}%".format(entry), entry))
        contentList = [m[0] for m in self.cursor.fetchall()]
        if not contentList:
            return "[not found]"
        else:
            content = "<br>".join(contentList)
            #content = re.sub("""(<ref onclick="[^<>]+?\(')([^<>]+?)('\)">)""", r"[<ref>\2</ref> ] " if config.runMode == "terminal" else r"\1\2\3", content)
            return content


class DictionaryData:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "data", "dictionary.data")
        self.connection = apsw.Connection(self.database)
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
            imageList = [m for m in re.findall(r'src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', contentText)]
            if imageList:
                imageSqlite = ImageSqlite()
                for (imgModule, imgEntry) in imageList:
                    imageSqlite.exportImage(imgModule, imgEntry)
                del imageSqlite
            contentText = re.sub(r'src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', r'src="images/\1/\1_\2"', contentText)
            contentText = re.sub(r"src='getImage\.php\?resource=([^']*?)&id=([^']*?)'", r"src='images/\1/\1_\2'", contentText)

            abb = entry[:3]
            moduleName = dict(IndexesSqlite().dictionaryList)[abb]
            searchButton = "&ensp;<button class='ubaButton' onclick='document.title=\"_command:::SEARCHTOOL:::{0}:::\"'>search</button>".format(abb)
            return "<p><b>{0}</b> {1}</p>{2}".format(moduleName, searchButton, contentText)

    def getRawContent(self, entry):
        query = "SELECT content FROM Dictionary WHERE path = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return content[0]


class EncyclopediaData:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "data", "encyclopedia.data")
        self.connection = apsw.Connection(self.database)
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
            config.encyclopediaEntry = entry
            contentText = content[0]

            # deal with images
            imageList = [m for m in re.findall(r'src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', contentText)]
            if imageList:
                imageSqlite = ImageSqlite()
                for (imgModule, imgEntry) in imageList:
                    imageSqlite.exportImage(imgModule, imgEntry)
                del imageSqlite
            contentText = re.sub(r'src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', r'src="images/\1/\1_\2"', contentText)
            contentText = re.sub(r"src='getImage\.php\?resource=([^']*?)&id=([^']*?)'", r"src='images/\1/\1_\2'", contentText)

            moduleName = dict(IndexesSqlite().encyclopediaList)[module]
            searchButton = "&ensp;<button class='ubaButton' onclick='document.title=\"_command:::SEARCHTOOL:::{0}:::\"'>search</button>".format(module)
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
        self.connection = apsw.Connection(self.database)
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
        self.connection = apsw.Connection(self.database)
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
                    content = re.sub(r'<blid="(.*?)">.*?MYGOOGLEAPIKEY\]&callback=myMap"></script>', r'<p align="center"><img src="images/exlbl_large/\1.png"></p>', content)
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
                searchButton = "&ensp;<button class='ubaButton' onclick='document.title=\"_command:::SEARCHTOOL:::{0}:::\"'>search</button>".format(module.upper())
                return "<p><b>{0}</b> {1}</p>{2}".format(moduleName[module], searchButton, content[0])


class Commentary:

    CREATE_COMMENTARY_TABLE = "CREATE TABLE Commentary (Book INT, Chapter INT, Scripture TEXT)"
    CREATE_DETAILS_TABLE = "CREATE TABLE Details (Title NVARCHAR(100), Abbreviation NVARCHAR(50), Information TEXT, Version INT, OldTestament BOOL, NewTestament BOOL, Apocrypha BOOL, Strongs BOOL)"

    marvelCommentaries = {
        "Barnes": "Notes on the Old and New Testaments (Barnes) [26 vol.]",
        "Benson": "Commentary on the Old and New Testaments (Benson) [5 vol.]",
        "BI": "Biblical Illustrator (Exell) [58 vol.]",
        "Brooks": "Complete Summary of the Bible (Brooks) [2 vol.]",
        "Calvin": "John Calvin's Commentaries (Calvin) [22 vol.]",
        "Clarke": "Commentary on the Bible (Clarke) [6 vol.]",
        "CBSC": "Cambridge Bible for Schools and Colleges (Cambridge) [57 vol.]",
        "CECNT": "Critical And Exegetical Commentary on the NT (Meyer) [20 vol.]",
        "CGrk": "Cambridge Greek Testament for Schools and Colleges (Cambridge) [21 vol.]",
        "CHP": "Church Pulpit Commentary (Nisbet) [12 vol.]",
        "CPBST": "College Press Bible Study Textbook Series (College) [59 vol.]",
        "EBC": "Expositor's Bible Commentary (Nicoll) [49 vol.]",
        "ECER": "Commentary for English Readers (Ellicott) [8 vol.]",
        "EGNT": "Expositor's Greek New Testament (Nicoll) [5 vol.]",
        "GCT": "Greek Testament Commentary (Alford) [4 vol.]",
        "Gill": "Exposition of the Entire Bible (Gill) [9 vol.]",
        "Henry": "Exposition of the Old and New Testaments (Henry) [6 vol.]",
        "HH": "Horæ Homileticæ (Simeon) [21 vol.]",
        "ICCNT": "International Critical Commentary, NT (1896-1929) [16 vol.]",
        "JFB": "Jamieson, Fausset, and Brown Commentary (JFB) [6 vol.]",
        "KD": "Commentary on the Old Testament (Keil & Delitzsch) [10 vol.]",
        "Lange": "Commentary on the Holy Scriptures: Critical, Doctrinal, and Homiletical (Lange) [25 vol.]",
        "MacL": "Expositions of Holy Scripture (MacLaren) [32 vol.]",
        "PHC": "Preacher's Complete Homiletical Commentary (Exell) [37 vol.]",
        "Pulpit": "Pulpit Commentary (Spence) [23 vol.]",
        "Rob": "Word Pictures in the New Testament (Robertson) [6 vol.]",
        "Spur": "Spurgeon's Expositions on the Bible (Spurgeon) [3 vol.]",
        "Vincent": "Word Studies in the New Testament (Vincent) [4 vol.]",
        "Wesley": "John Wesley's Notes on the Whole Bible (Wesley) [3 vol.]",
        "Whedon": "Commentary on the Old and New Testaments (Whedon) [14 vol.]",
    }

    fileLookup = None

    def __init__(self, text=False):
        self.connection = None
        self.logger = logging.getLogger('uba')
        if config.enableHttpServer:
            config.marvelData = config.marvelDataPrivate if config.webHomePage == "{0}.html".format(config.webPrivateHomePage) else config.marvelDataPublic
            config.commentariesFolder = os.path.join(config.marvelData, "commentaries")
        if text:
            self.text = text
            if self.text in self.getCommentaryList():
                self.database = os.path.join(config.commentariesFolder, "c{0}.commentary".format(text))
                self.connection = apsw.Connection(self.database)
                self.cursor = self.connection.cursor()
        if Commentary.fileLookup is None:
            self.reloadFileLookup()

    @staticmethod
    def createCommentary(commentary, content):
        database = os.path.join(config.commentariesFolder, "c{0}.commentary".format(commentary))
        with apsw.Connection(database) as connection:
            cursor = connection.cursor()
            if not ToolsSqlite.checkTableExists(cursor, "Commentary"):
                cursor.execute(Commentary.CREATE_COMMENTARY_TABLE)
            if not ToolsSqlite.checkTableExists(cursor, "Details"):
                cursor.execute(Commentary.CREATE_DETAILS_TABLE)
                sql = ("INSERT INTO Details (Title, Abbreviation, Information, Version, OldTestament, NewTestament,"
                       "Apocrypha, Strongs) VALUES (?, ?, ?, 1, 1, 1, 0, 0)")
                cursor.execute(sql, (commentary, commentary, commentary))
#            cursor.execute("COMMIT")
            deleteData = []
            insertData = []
            for data in content:
                deleteData.append((data[0], data[1]))
                if data[2]:
                    insertData.append((data[0], data[1], data[2]))
            delete = "DELETE FROM Commentary WHERE Book=? AND Chapter=?"
            cursor.executemany(delete, deleteData)
            insert = "INSERT INTO Commentary (Book, Chapter, Scripture) VALUES (?, ?, ?)"
            cursor.executemany(insert, insertData)
#            cursor.execute("COMMIT")

    def reloadFileLookup(self):
            Commentary.fileLookup = {}
            commentaryFolder = config.commentariesFolder
            commentaryList = [f[1:-11] for f in os.listdir(commentaryFolder) if
                              os.path.isfile(os.path.join(commentaryFolder, f)) and f.endswith(
                                  ".commentary") and not re.search(r"^[\._]", f)]
            for commentary in sorted(commentaryList):
                if commentary in Commentary.marvelCommentaries.keys():
                    description = Commentary.marvelCommentaries[commentary]
                else:
                    database = os.path.join(config.commentariesFolder, "c{0}.commentary".format(commentary))
                    connection = apsw.Connection(database)
                    cursor = connection.cursor()
                    query = "SELECT title FROM Details"
                    cursor.execute(query)
                    description = cursor.fetchone()[0]
                Commentary.fileLookup[commentary] = description

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
            return self.text

    def bcvToVerseReference(self, b, c, v):
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)

    def formCommentaryTag(self, commentary):
        return "<ref onclick='document.title=\"_commentary:::{0}\"' onmouseover='commentaryName(\"{0}\")'>".format(commentary)

    def formBookTag(self, b):
        bookAbb = self.bcvToVerseReference(b, 1, 1)[:-4]
        return "<ref onclick='document.title=\"_commentary:::{0}.{1}\"' onmouseover='bookName(\"{2}\")'>".format(self.text, b, bookAbb)

    def formChapterTag(self, b, c):
        #return "<ref onclick='document.title=\"_commentary:::{0}.{1}.{2}\"' onmouseover='document.title=\"_info:::Chapter {2}\"'>".format(self.text, b, c)
        return "<ref onclick='document.title=\"_commentarychapters:::{0}\"' onmouseover='document.title=\"_info:::Chapter {1}\"'>".format(self.text, c)

    def formVerseTag(self, b, c, v):
        verseReference = self.bcvToVerseReference(b, c, v)
        return "<ref id='v{0}.{1}.{2}' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"COMMENTARY:::{3}:::{4}\"' onmouseover='document.title=\"_instantVerse:::{3}:::{0}.{1}.{2}\"' ondblclick='document.title=\"_commentary:::{3}.{0}.{1}.{2}\"'>".format(b, c, v, self.text, verseReference)

    def getCommentaryList(self):
        commentaryFolder = config.commentariesFolder
        commentaryList = [f[1:-11] for f in os.listdir(commentaryFolder) if os.path.isfile(os.path.join(commentaryFolder, f)) and f.endswith(".commentary") and not re.search(r"^[\._]", f)]
        return sorted(commentaryList)

    def getCommentaryListThatHasBookAndChapter(self, book, chapter):
        commentaryFolder = config.commentariesFolder
        commentaryList = [f[1:-11] for f in os.listdir(commentaryFolder) if os.path.isfile(os.path.join(commentaryFolder, f)) and f.endswith(".commentary") and not re.search(r"^[\._]", f)]
        activeCommentaries = []
        for commentary in sorted(commentaryList):
            database = os.path.join(config.commentariesFolder, "c{0}.commentary".format(commentary))
            connection = apsw.Connection(database)
            cursor = connection.cursor()
            query = "select book from commentary where book=? and chapter=?"
            cursor.execute(query, (book, chapter))
            if cursor.fetchone():
                activeCommentaries.append((commentary, Commentary.fileLookup[commentary]))
        return activeCommentaries

    def getCommentaries(self):
        commentaryList = self.getCommentaryList()
        commentaries = " ".join(["{0}<button class='ubaButton'>{1}</button></ref>".format(self.formCommentaryTag(commentary), commentary) for commentary in commentaryList])
        return commentaries

    def getBookList(self):
        query = "SELECT DISTINCT Book FROM Commentary ORDER BY Book"
        self.cursor.execute(query)
        return [book[0] for book in self.cursor.fetchall()]

    def getBooks(self):
        bookList = self.getBookList()
        standardAbbreviation = BibleVerseParser(config.parserStandarisation).standardAbbreviation
        return " ".join(["{0}<button class='ubaButton'>{1}</button></ref>".format(self.formBookTag(book), standardAbbreviation[str(book)]) for book in bookList if str(book) in standardAbbreviation])

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
                menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='commentaryName(\"{0}\")'>{0}</span>  <button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"COMMENTARY:::{0}:::{1}\"'>{3}</button>".format(self.text, mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_open"])
                menu += "<hr><b>{1}</b> {0}".format(self.getBooks(), config.thisTranslation["html_book"])
                bcList = [int(i) for i in items[1:]]
                if bcList:
                    check = len(bcList)
                    if check >= 1:
                        # i.e. book specified; add chapter menu
                        menu += "<br><br><b>{1}</b> <span style='color: brown;' onmouseover='bookName(\"{0}\")'>{0}</span>   <button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"COMMENTARY:::{3}:::{0} 1\"'>{2}</button>".format(self.bcvToVerseReference(bcList[0], 1, 1)[:-4], config.thisTranslation["html_current"], config.thisTranslation["html_open"], self.text)
                        menu += "<hr><b>{1}</b> {0}".format(self.getChapters(bcList[0]), config.thisTranslation["html_chapter"])
                    if check >= 2:
                        # i.e. both book and chapter specified; add verse menu
                        menu += "<br><br><b>{3}</b> <span style='color: brown;' onmouseover='document.title=\"_info:::Chapter {0}\"'>{0}</span>  <button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"COMMENTARY:::{1}:::{2}\"'>{4}</button>".format(bcList[1], self.text, self.bcvToVerseReference(bcList[0], bcList[1], 1)[:-2], config.thisTranslation["html_current"], config.thisTranslation["html_open"])
                        menu += "<hr><b>{1}</b> {0}".format(self.getVerses(bcList[0], bcList[1]), config.thisTranslation["html_verse"])
                    if check == 3:
                        menu += "<br><br><b>{5}</b> <span style='color: brown;' onmouseover='document.title=\"_instantVerse:::{0}:::{1}.{2}.{3}\"'>{3}</span> <button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"COMMENTARY:::{0}:::{4}\"'>{6}</button>".format(self.text, bcList[0], bcList[1], bcList[2], mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_open"])
            return menu
        else:
            return "INVALID_COMMAND_ENTERED"

    def getContent(self, verse, fullVerseList=[]):
        if self.text in self.getCommentaryList():
            b, c, v, *_ = verse
            if c > 0:
                chapter = "<h2>{0}{1}</ref></h2>".format(self.formChapterTag(b, c), self.bcvToVerseReference(b, c, v).split(":", 1)[0])
            else:
                chapter = "<h2>{0}</h2>".format(BibleBooks.abbrev["eng"][b][0])
            query = "SELECT Scripture FROM Commentary WHERE Book=? AND Chapter=?"
            self.cursor.execute(query, verse[0:2])
            scripture = self.cursor.fetchone()
            if scripture:
                data = scripture[0]
                if fullVerseList:
                    fullVerseList = [f'<vid id="v{b}.{c}.{v}"' for b, c, v, *_ in fullVerseList]

                    pattern = '(<vid id="v[0-9]+?.[0-9]+?.[0-9]+?"></vid>)<hr>'
                    searchReplaceItems = ((pattern, r"<hr>\1"),)
                    chapterCommentary = RegexSearch.deepReplace(data, pattern, searchReplaceItems)
                    verseCommentaries = chapterCommentary.split("<hr>")

                    loaded = []
                    for i in verseCommentaries:
                        for ii in fullVerseList:
                            if i.strip() and not i in loaded and ii in i:
                                loaded.append(i)
                    data = "<hr>".join(loaded)
                if c == 0:
                    data = data.replace("<b>0:0</b>", "")
                    data = data.replace("<u><b>0</b></u>", "")
                if config.rawOutput:
                    return data
                if config.theme in ("dark", "night"):
                    data = data.replace('color:#000080;', 'color:gray;')
                chapter += re.sub(r'onclick="luV\(([0-9]+?)\)"', r'onclick="luV(\1)" onmouseover="qV(\1)" ondblclick="mV(\1)"', data)
                if config.runMode == "terminal":
                    chapter = re.sub("""(<vid id="v{0}.{1}.{2}" onclick="bcv\({0},{1},{2}\)">)""".format(b, c, v), r"<z>******* {0}:{1} *******</z><br>\1".format(c, v), chapter)
                return "<div>{0}</div>".format(chapter)
            else:
                return "<span style='color:gray;'>['{0}' does not contain this chapter.]</span>".format(self.text)
        else:
            return "INVALID_COMMAND_ENTERED"

    def getRawContent(self, b, c):
        if self.text in self.getCommentaryList():
            query = "SELECT Scripture FROM Commentary WHERE Book=? AND Chapter=?"
            self.cursor.execute(query, (b, c))
            data = self.cursor.fetchone()
            return data
        else:
            return ""

    def fixLinksInCommentary(self):
        query = "SELECT Book, Chapter, Scripture FROM Commentary ORDER BY Book, Chapter"
        self.cursor.execute(query)
        for record in self.cursor.fetchall():
            scripture = record[2]
            scripture = BibleVerseParser("no").replaceTextWithReference(scripture, False)
            update = "Update Commentary SET Scripture = ? WHERE Book = ? AND Chapter = ?"
            self.cursor.execute(update, (scripture, record[0], record[1]))
#            self.cursor.execute("COMMIT")
            if int(record[1]) >= 1:
                self.logger.info("Fix commentary {0} - {1}:{2}".format(self.text, record[0], record[1]))

    def fixClosingTagsInCommentary(self):
        query = "SELECT Book, Chapter, Scripture FROM Commentary ORDER BY Book, Chapter"
        self.cursor.execute(query)
        for record in self.cursor.fetchall():
            scripture = record[2]
            scripture = re.sub(r"<heb>(.*?)</span>", r"<heb>\1</heb>", scripture)
            scripture = re.sub(r"<grk>(.*?)</span>", r"<grk>\1</grk>", scripture)
            update = "Update Commentary SET Scripture = ? WHERE Book = ? AND Chapter = ?"
            self.cursor.execute(update, (scripture, record[0], record[1]))
#            self.cursor.execute("COMMIT")
            if int(record[1]) >= 1:
                self.logger.info("Fix commentary {0} - {1}:{2}".format(self.text, record[0], record[1]))

class LexiconData:

    def __init__(self):
        self.lexiconList = self.getLexiconList()

    def getLexiconList(self):
        lexiconFolder = os.path.join(config.marvelData, "lexicons")
        lexiconList = [f[:-8] for f in os.listdir(lexiconFolder) if os.path.isfile(os.path.join(lexiconFolder, f)) and f.endswith(".lexicon") and not re.search(r"^[\._]", f)]
        return sorted(lexiconList)

    def getSelectForm(self, entry, module=""):
        lexiconList = [lexicon for lexicon in self.lexiconList if not lexicon == module]
        selectForm = '<p><form action=""><select id="{0}" name="{0}" onchange="lexicon(this.value, this.id)"><optgroup><option value="">More lexicons HERE</option>'.format(entry)
        for lexicon in lexiconList:
            selectForm += '<option value="{0}">{1}</option>'.format(lexicon, Lexicon(lexicon).getInfo())
        selectForm += '</optgroup></select></form></p>'
        return selectForm


class Lexicon:

    CREATE_LEXICON_TABLE = "CREATE TABLE Lexicon (Topic NVARCHAR(100), Definition TEXT)"

    def __init__(self, module):
        # connect lexicon module
        self.module = module

        self.database = os.path.join(config.marvelData, "lexicons", "{0}.lexicon".format(module))
        self.connection = apsw.Connection(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    @staticmethod
    def createLexicon(lexicon, content):
        database = os.path.join(config.marvelData, "lexicons", "{0}.lexicon".format(lexicon))
        with apsw.Connection(database) as connection:
            cursor = connection.cursor()
            if not ToolsSqlite.checkTableExists(cursor, "Lexicon"):
                cursor.execute(Lexicon.CREATE_LEXICON_TABLE)
                sql = ("INSERT INTO Lexicon (Topic, Definition) VALUES (?, ?)")
                cursor.execute(sql, ('info', lexicon))
#            cursor.execute("COMMIT")
            deleteData = []
            insertData = []
            for data in content:
                deleteData.append((data[0],))
                if data[1]:
                    insertData.append((data[0], data[1]))
            delete = "DELETE FROM Lexicon WHERE Topic=?"
            cursor.executemany(delete, deleteData)
            insert = "INSERT INTO Lexicon (Topic, Definition) VALUES (?, ?)"
            cursor.executemany(insert, insertData)
#            cursor.execute("COMMIT")

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

    def getSampleTopics(self):
        try:
            query = "select topic from Lexicon where rowid in (5, 5000, 10000, 20000)"
            self.cursor.execute(query)
            topics = self.cursor.fetchall()
            sample = ",".join(topic[0] for topic in topics)
            return sample
        except:
            return ""

    def getAllTopics(self):
        query = "SELECT Topic FROM Lexicon"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def getHebrewTopics(self):
        query = "SELECT Topic FROM Lexicon WHERE Topic like 'H%'"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def getGreekTopics(self):
        query = "SELECT Topic FROM Lexicon WHERE Topic like 'G%'"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def searchTopic(self, search):
        try:
            searchString = "%{0}%".format(search)
            query = TextUtil.getQueryPrefix()
            query += "SELECT DISTINCT Topic FROM Lexicon WHERE Topic LIKE ? ORDER BY Topic"
            self.cursor.execute(query, (searchString,))
            topics = self.cursor.fetchall()
            contentText = """<h2>{0}</h2>""".format(self.module)
            query = TextUtil.getQueryPrefix()
            query += "SELECT DISTINCT Topic FROM Lexicon WHERE DEFINITION LIKE ? and TOPIC NOT LIKE ? ORDER BY Topic LIMIT 0, 500"
            self.cursor.execute(query, (searchString, searchString))
            topics += self.cursor.fetchall()
            for topic in topics:
                t = topic[0]
                e = t.replace("'", "\\\'").replace('"', '\\\"')
                entry = """<div><ref onclick="document.title='LEXICON:::{0}:::{1}'">{2}</ref></div>""".format(self.module, e, t)
                if config.runMode == "terminal":
                    config.lexiconEntry = e
                contentText += entry
            return contentText
        except:
            return "Could not search {0} in {1}".format(searchString, self.module)

    def getContent(self, entry, showMenu=True):
        try:
            if config.runMode == "terminal":
                config.lexiconEntry = entry
            lexiconData = LexiconData()
            query = "SELECT Definition FROM Lexicon WHERE Topic = ?"
            self.cursor.execute(query, (entry,))
            information = self.cursor.fetchone()
            contentText = """<h2>{0} - <ref onclick='concord("{1}")'>{1}</ref></h2>""".format(self.module, entry)
            if showMenu:
                contentText += "<p>{0}</p>".format(lexiconData.getSelectForm(entry, self.module))
            if not information:
                return contentText+"[not found]"
            else:
                contentText += information[0]
                # deal with images
                imageList = [m for m in re.findall(r'src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', contentText)]
                if imageList:
                    imageSqlite = ImageSqlite()
                    for (imgModule, imgEntry) in imageList:
                        imageSqlite.exportImage(imgModule, imgEntry)
                    del imageSqlite
                contentText = re.sub(r'src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', r'src="images/\1/\1_\2"', contentText)
                contentText = re.sub(r"src='getImage\.php\?resource=([^']*?)&id=([^']*?)'", r"src='images/\1/\1_\2'", contentText)
                return contentText
        except Exception as ex:
            print(f"Cannot open {self.database}")
            print(ex)
            return ""

    def getRawContent(self, entry):
        try:
            query = "SELECT Definition FROM Lexicon WHERE Topic = ?"
            self.cursor.execute(query, (entry,))
            return self.cursor.fetchone()
        except Exception as ex:
            return ""

    def getReverseContent(self, entry):
        search = "%{0}%".format(entry)
        query = TextUtil.getQueryPrefix()
        query += "SELECT Topic, Definition FROM Lexicon WHERE Definition LIKE ? ORDER BY Topic"
        self.cursor.execute(query, (search,))
        records = self.cursor.fetchall()
        contentText = """<h2>{0}</h2>""".format(self.module)
        if not records:
            return contentText+"[not found]"
        else:
            for record in records:
                if re.search(r"\b{0}\b".format(entry), record[1]):
                    contentText += "<div><h3>{0}</h3>{1}</div>".format(record[0], record[1])
            contentText = re.sub("(" + entry + ")", r"<z>\1</z>", contentText, flags=re.IGNORECASE)
        return contentText

    def getRawReverseContent(self, entry):
        try:
            search = "%{0}%".format(entry)
            query = "SELECT Topic, Definition FROM Lexicon WHERE Definition LIKE ? ORDER BY Topic"
            self.cursor.execute(query, (search,))
            return self.cursor.fetchall()
        except Exception as ex:
            return ""


class BookData:

    def __init__(self):
        if config.enableHttpServer:
            config.marvelData = config.marvelDataPrivate if config.webHomePage == "{0}.html".format(config.webPrivateHomePage) else config.marvelDataPublic
            config.booksFolder = os.path.join(config.marvelData, "books")
        self.bookList = self.getBookList()
        self.catalogBookList = self.getCatalogBookList()

    def getDirectories(self):
        bookFolder = config.booksFolder
        dirList = ["{0}/".format(f) for f in os.listdir(bookFolder) if os.path.isdir(os.path.join(bookFolder, f)) and not f.startswith("__") and not f.startswith(".")]
        dirList = sorted(dirList)
        return dirList

    def getBooks(self):
        bookFolder = config.booksFolder
        bookList = [f[:-5] for f in os.listdir(bookFolder) if os.path.isfile(os.path.join(bookFolder, f)) and f.endswith(".book") and not re.search(r"^[\._]", f)]
        bookList = sorted(bookList)
        return bookList

    def getBookList(self):
        return [(book, book) for book in self.getBooks()]

    def getCatalogBookList(self):
        return [(book, book) for book in CatalogUtil.getBooks()]

    def getMenu(self, module=""):
        if module == "":
            module = config.book
        if module in dict(self.catalogBookList).keys():
            books = self.formatSelectList("listBookTopic(this.value)", self.catalogBookList, module)
            topicList = Book(module).getTopicList()
            topics = "<br>".join(["<ref onclick='document.title=\"BOOK:::{0}:::{1}\"'>{2}</ref>".format(module, re.sub("'", "@", topic), topic) for topic in topicList])
            config.book = module
            return topics if config.runMode == "terminal" else "<p>{0} &ensp;<button class='ubaButton' onclick='document.title=\"_command:::SEARCHBOOK:::{1}:::\"'>search</button></p><p>{2}</p>".format(books, module, topics)
        else:
            return "INVALID_COMMAND_ENTERED"

    def getSearchedMenu(self, module, searchString, chapterOnly=False):
        searchString = searchString.strip()
        if module in dict(self.catalogBookList).keys():
            books = self.formatSelectList("listBookTopic(this.value)", CatalogUtil.getBookList(), module)
            topicList = Book(module).getSearchedTopicList(searchString, chapterOnly=chapterOnly)
            topics = "<br>".join(["<ref onclick='document.title=\"BOOK:::{0}:::{1}\"'>{2}</ref>".format(module, re.sub("'", "@", topic), topic) for topic in topicList])
            config.book = module
            if topics:
                if chapterOnly:
                    searchCommand = "SEARCHBOOKCHAPTER"
                else:
                    searchCommand = "SEARCHBOOK"
                if config.runMode == "terminal":
                    return topics
                else:
                    return "<p>{0} &ensp;<button class='ubaButton' onclick='document.title=\"_command:::{3}:::{1}:::\"'>search</button></p><p>{2}</p>".format(books, module, topics, searchCommand)
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
        entry = re.sub("@", "'", entry)
        if entry.isdecimal():
            content = Book(module).getContentByRowId(entry)
        else:
            content = Book(module).getContentByChapter(entry)
        if config.runMode == "terminal":
            #<ref onclick="promise(0, 86)">[Go to]</ref>
            #_promise:::0.86
            content = re.sub("""<ref onclick="promise\(([0-9]+?), ([0-9]+?)\)">\[Go to\]</ref>""", r"[<ref>_promise:::\1.\2</ref> ]", content)
            content = re.sub("""<ref onclick="harmony\(([0-9]+?), ([0-9]+?)\)">\[Go to\]</ref>""", r"[<ref>_harmony:::\1.\2</ref> ]", content)
        return content


class Book:

    def __init__(self, module):
        self.logger = logging.getLogger('uba')
        # connect book module
        self.module = module
        self.cursor = None
        self.connection = None

        module = "{0}.book".format(module)
        if config.enableHttpServer:
            config.marvelData = config.marvelDataPrivate if config.webHomePage == "{0}.html".format(config.webPrivateHomePage) else config.marvelDataPublic
            folder = os.path.join(config.marvelData, "books")
        else:
            folder = CatalogUtil.getFolder(module)
        self.database = os.path.join(folder, module)
        if not os.path.exists(self.database):
            self.module = ""
        else:
            self.connection = apsw.Connection(self.database)
            self.cursor = self.connection.cursor()

    def __del__(self):
        if self.connection:
            self.connection.close()

    def getTopicList(self):
        if self.connection:
            query = "SELECT DISTINCT Chapter FROM Reference ORDER BY ROWID"
            self.cursor.execute(query)
            return [topic[0] for topic in self.cursor.fetchall()]
        return []

    def getSearchedTopicList(self, searchString, chapterOnly=False):
        try:
            query = TextUtil.getQueryPrefix()
            searchString = "%{0}%".format(searchString)
            if chapterOnly:
                query += "SELECT DISTINCT Chapter FROM Reference WHERE Chapter LIKE ? ORDER BY ROWID"
                self.cursor.execute(query, (searchString,))
            else:
                query += "SELECT DISTINCT Chapter FROM Reference WHERE Chapter LIKE ? OR Content LIKE ? ORDER BY ROWID"
                self.cursor.execute(query, (searchString, searchString))
            return [topic[0] for topic in self.cursor.fetchall()]
        except:
            self.logger.error("Could not search {0}".format(self.module))
            return []

    def getChapterCount(self):
        if self.connection:
            query = "SELECT MAX(ROWID) from Reference"
            result = self.cursor.execute(query).fetchone()
            return result[0]
        return 0

    def getContentByChapter(self, entry):
        if self.connection:
            query = "SELECT Chapter, Content, ROWID FROM Reference WHERE Chapter=?"
            content = self.getContentData(query, entry)
            return content
        return ""

    def getParagraphSectionsByChapter(self, entry):
        query = "SELECT Content FROM Reference WHERE Chapter=?"
        self.cursor.execute(query, (entry,))
        data = self.cursor.fetchone()[0]
        if ("Htmltext" in config.enabled):
            import html_text
            data = data.replace("\n", "[nl]")
            data = data.replace("<br><br>", "<br>")
            data = data.replace("<br>", "[br]")
            data = data.replace("<br />", "[br]")
            data = html_text.extract_text(data)
            data = data.replace("\n\n", "\n")
            data = data.replace("[nl]", "\n")
            data = data.replace("[br]", "<br>")
        lines = data.split('\n')
        sections = []
        section = ''
        for line in lines:
            if line.startswith("Author:"):
                pass
            elif line == '<br>':
                if len(section) > 0:
                    sections.append(section)
                section = ''
            else:
                if len(line) > 0 and not line.startswith("<br>"):
                    line = "<br>" + line
                section += line
        if len(section) > 0:
            sections.append(section)
        return sections

    def getContentByRowId(self, entry):
        if self.connection:
            query = "SELECT Chapter, Content, ROWID FROM Reference WHERE ROWID=?"
            return self.getContentData(query, entry)

    def getContentData(self, query, entry):
        self.cursor.execute(query, (entry,))
        row = self.cursor.fetchone()
        if not row:
            return "[not applicable]"
        else:
            config.book = self.module
            config.bookChapter = row[0]
            content = row[1]
            config.bookChapNum = row[2]
            isPDF = True if type(content) == bytes and content[0] == 37 and content[1] == 80 and content[2] == 68 else False
            if isPDF:
                return content
            if config.overwriteBookFont:
                fontFamily = config.font
                if config.overwriteBookFontFamily:
                    fontFamily = config.overwriteBookFontFamily
                content = re.sub("font-family:[^<>]*?;", r"font-family:'{0}';".format(fontFamily), content)
            if config.overwriteBookFontSize:
                if type(config.overwriteBookFontSize) == bool:
                    content = re.sub("font-size:[^<>]*?;", "", content)
                elif type(config.overwriteBookFontSize) == int:
                    content = re.sub("font-size:[^<>]*?;", r"font-size:'{0}px';".format(config.overwriteBookFontSize),
                                     content)
                elif type(config.overwriteBookFontSize) == str:
                    content = re.sub("font-size:[^<>]*?;", r"font-size:'{0}';".format(config.overwriteBookFontSize),
                                     content)
            for searchString in config.bookSearchString.split("%"):
                if searchString and not searchString == "z":
                    content = re.sub("({0})".format(searchString), r"<z>\1</z>", content, flags=re.IGNORECASE)
                    content = TextUtil.fixTextHighlighting(content)
            # add an id so as to scroll to the first result
            content = re.sub("<z>", "<span id='v{0}.{1}.{2}'></span><z>".format(config.studyB, config.studyC, config.studyV), content, count=1)
            if config.theme in ("dark", "night"):
                content = self.adjustDarkThemeColorsForBook(content)
            # return content
            return "<p><ref onclick='document.title={3}BOOK:::{0}{3}'>{0}</ref><br>&gt; <b>{1}</b></p>{2}".format(self.module, config.bookChapter, content, '"')

    def adjustDarkThemeColorsForBook(self, content):
        content = content.replace('<body style="background-attachment: fixed" background="http://www.swartzentrover.com/cotor/Bootstrap/img/bg/sdf/BK249.GIF">', '<body>')
        content = content.replace('<body style="background-attachment: fixed" background="http://www.swartzentrover.com/Web Graphics/BackGrounds/concrete/concrete12.jpg">', '<body>')
        content = content.replace('cellpadding="0"', 'cellpadding="5"')
        return content


class ToolsSqlite:
    @staticmethod
    def checkTableExists(cursor, table):
        if cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if cursor.fetchone():
                return True
            else:
                return False
        return False


if __name__ == "__main__":

    # logger = logging.getLogger('uba')
    # logger.setLevel(logging.DEBUG)
    # logHandler = handlers.TimedRotatingFileHandler('uba.log', when='D', interval=1, backupCount=0)
    # logHandler.setLevel(logging.DEBUG)
    # logger.addHandler(logHandler)
    #
    # print("Start")
    # config.parseEnglishBooksOnly = True
    # config.parseClearSpecialCharacters = False
    # commentary = Commentary("OwenHebrews")
    # # commentary.fixClosingTagsInCommentary()
    # print("Finished")
    #
    # scripture = """<heb>&#x05D5;&#x05D1;&#x05BC;&#x05B0;&#x05D4;&#x05B8;&#x05DC;&#x05B5;&#x05D9;&#x05DF;</span><heb> </span><heb>&#x05D9;&#x05B7;&#x05D5;&#x05B0;&#x05DE;&#x05B8;&#x05D7;&#x05B5;&#x05D0;</span><heb> </span><heb>&#x05D0;&#x05B7;&#x05D7;&#x05B2;&#x05E8;&#x05B7;&#x05D9;&#x05B4;&#x05D0;&#x05BC;</span>"""
    # scripture = re.sub(r"<heb>(.*?)</span>", r"<heb>\1</heb>", scripture)
    # print(scripture)
    # list = Commentary().getCommentaryListThatHasBookAndChapter(40, 0)
    # print(",".join(list))

    s = "asdfadcryadsfa cryasdfads cry adfasdf"
    e = "cry"
    print(s)
    print(re.search(r"\b{0}\b".format(e), s))

    print("Finished")
