import os, sqlite3, re

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
        imageList = [m for m in re.findall('src="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', contentText)]
        if imageList:
            imageSqlite = ImageSqlite()
            for (module, entry) in imageList:
                content = imageSqlite.exportImage(module, entry)
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
        content = self.cursor.fetchone()[0]
        return content

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
        content = self.cursor.fetchone()[0]
        return content