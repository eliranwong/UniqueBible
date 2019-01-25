import os, sqlite3, re, config

class CrossReferenceSqlite:

    def __init__(self):
        # connect bibles.sqlite
        self.database = os.path.join("marvelData", "cross-reference.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def bcvToVerseReference(self, b, c, v):
        parser = BibleVerseParser("YES")
        verseReference = parser.bcvToVerseReference(b, c, v)
        del parser
        return verseReference

    def scrollMapper(self, bcvTuple):
        query = "SELECT Information FROM ScrollMapper WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, bcvTuple)
        information = self.cursor.fetchone()
        if not information:
            return ""
        else:
            return information[0]

    def tske(self, bcvTuple):
        query = "SELECT Information FROM TSKe WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, bcvTuple)
        information = self.cursor.fetchone()
        if not information:
            return ""
        else:
            return information[0]


class ImageSqlite:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join("marvelData", "images.sqlite")
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
        self.database = os.path.join("marvelData", "indexes.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getAllIndexes(self, bcvTuple):
        indexList = ["exlbp", "exlbl", "exlbt", "dictionaries", "encyclopedia"]
        indexItems = [
            ("Characters", self.searchCharacters()),
            ("Locations", self.searchLocations()),
            ("Topics", self.searchTopics()),
            ("Dictionaries", self.searchDictionaries()),
            ("Encyclopedia", self.searchEncyclopedia())
        ]
        content = ""
        for counter, index in enumerate(indexList):
            content += "<h2>{0}</h2>".format(indexItems[counter][0])
            content += self.getContent(index, bcvTuple)
            content += "<p>{0}</p>".format(indexItems[counter][1])
        return content

    def searchCharacters(self):
        content = "<ref onclick='document.title={0}_command:::SEARCHTOOL:::EXLBP:::{0}'>Search for a character</ref>".format('"')
        content += "<br><ref onclick='document.title={0}_command:::SEARCHTOOL:::HBN:::{0}'>Search for a name & its meaning</ref>".format('"')
        return content

    def searchLocations(self):
        return "<ref onclick='document.title={0}_command:::SEARCHTOOL:::EXLBL:::{0}'>Search for a location</ref>".format('"')

    def searchTopics(self):
        return "<ref onclick='document.title={0}_command:::SEARCHTOOL:::EXLBT:::{0}'>Search for a topic</ref>".format('"')

    def searchDictionaries(self):
        return ""

    def searchEncyclopedia(self):
        return ""

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


class SearchSqlite:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join("marvelData", "search.sqlite")
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


class LexiconData:

    def __init__(self):
        # connect lexicon.data
        self.database = os.path.join("marvelData", "data", "lexicon.data")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getLexiconList(self):
        t = ("table",)
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        self.cursor.execute(query, t)
        versions = self.cursor.fetchall()
        exclude = ("Details",)
        return [version[0] for version in versions if not version[0] in exclude]

    def getSelectForm(self, lexiconList, entry):
        selectForm = '<p><form action=""><select id="{0}" name="{0}" onchange="lexicon(this.value, this.id)"><option value="">More lexicons HERE</option>'.format(entry)
        for lexicon in lexiconList:
            selectForm += '<option value="{0}">{0}</option>'.format(lexicon)
        selectForm += '</select></form></p>'
        return selectForm

    def lexicon(self, module, entry):
        query = "SELECT Information FROM {0} WHERE EntryID = ?".format(module)
        self.cursor.execute(query, (entry,))
        information = self.cursor.fetchone()
        contentText = "<h2>{0} - {1}</h2>".format(module, entry)
        contentText += "<p>{0}</p>".format(self.getSelectForm([m for m in self.getLexiconList() if not m == module], entry))
        contentText += information[0]
        # deal with images
        imageList = [m for m in re.findall('src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', contentText)]
        if imageList:
            imageSqlite = ImageSqlite()
            for (module, entry) in imageList:
                imageSqlite.exportImage(module, entry)
            del imageSqlite
        contentText = re.sub('src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', r'src="images/\1/\1_\2"', contentText)
        if not information:
            return ""
        else:
            return contentText


class DictionaryData:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join("marvelData", "data", "dictionary.data")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getContent(self, entry):
        query = "SELECT content FROM Dictionary WHERE path = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return ""
        else:
            return content[0]


class EncyclopediaData:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join("marvelData", "data", "encyclopedia.data")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getContent(self, module, entry):
        query = "SELECT content FROM {0} WHERE path = ?".format(module)
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return ""
        else:
            return content[0]


class ExlbData:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join("marvelData", "data", "exlb.data")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getContent(self, module, entry):
        query = "SELECT content FROM {0} WHERE path = ?".format(module)
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return ""
        else:
            if module == "exlbl":
                content = re.sub('href="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', r'href="javascript:void(0)" onclick="openImage({0}\1{0},{0}\2{0})"'.format("'"), content[0])
                return content.replace("[MYGOOGLEAPIKEY]", config.myGoogleApiKey)
            else:
                return content[0]
