import os, sqlite3, re, config
from BiblesSqlite import BiblesSqlite
from BibleVerseParser import BibleVerseParser

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
        content = "<button class='feature' onclick='document.title={0}_command:::SEARCHTOOL:::EXLBP:::{0}'>search for a character</button>".format('"')
        content += "<br><button class='feature' onclick='document.title={0}_command:::SEARCHTOOL:::HBN:::{0}'>search for a name & its meaning</button>".format('"')
        return content

    def searchLocations(self):
        return "<button class='feature' onclick='document.title={0}_command:::SEARCHTOOL:::EXLBL:::{0}'>search for a location</button>".format('"')

    def searchTopics(self):
        action = "searchResource(this.value)"
        optionList = [
            ("HIT", "Hitchcock's New and Complete Analysis of the Bible"),
            ("NAV", "Nave's Topical Bible"),
            ("TCR", "Thompson Chain References"),
            ("TNT", "Torrey's New Topical Textbook"),
            ("TOP", "Topical Bible"),
            ("EXLBT", "Search ALL above")
        ]
        return self.formatSelectList(action, optionList)

    def searchDictionaries(self):
        action = "searchResource(this.value)"
        optionList = [
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
            ("VNT", "Vine's Expository Dictionary of New Testament Words")
        ]
        return self.formatSelectList(action, optionList)

    def searchEncyclopedia(self):
        action = "searchResource(this.value)"
        optionList = [
            ("DAC", "Hasting's Dictionary of the Apostolic Church"),
            ("DCG", "Hasting's Dictionary Of Christ And The Gospels"),
            ("HAS", "Hasting's Dictionary of the Bible"),
            ("ISB", "International Standard Bible Encyclopedia"),
            ("KIT", "Kitto's Cyclopedia of Biblical Literature"),
            ("MSC", "McClintock & Strong's Cyclopedia of Biblical Literature")
        ]
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
        exclude = ("Details", "LGNTDF")
        return [version[0] for version in versions if not version[0] in exclude]

    def getSelectForm(self, lexiconList, entry):
        lexiconName = {
            "SECE": "Strong's Exhaustive Concordance [Enhanced]",
            "BDB": "Brown-Driver-Briggs Hebrew-English Lexicon",
            "LSJ": "Liddell-Scott-Jones Greek-English Lexicon",
            "TBESH": "Tyndale Brief lexicon of Extended Strongs for Hebrew",
            "TBESG": "Tyndale Brief lexicon of Extended Strongs for Greek",
            "MGLNT": "Manual Greek Lexicon of the New Testament",
            "Mounce": "Mounce Concise Greek-English Dictionary",
            "Thayer": "Thayer's Greek-English Lexicon",
            "LXX": "LXX Lexicon",
            "LCT": "新舊約字典彙編",
            "Morphology": "Morphology",
            "ConcordanceBook": "Concordance (sorted by book)",
            "ConcordanceMorphology": "Concordance (sorted by morphology)",
        }
        selectForm = '<p><form action=""><select id="{0}" name="{0}" onchange="lexicon(this.value, this.id)"><option value="">More lexicons HERE</option>'.format(entry)
        for lexicon in lexiconList:
            selectForm += '<option value="{0}">{1}</option>'.format(lexicon, lexiconName[lexicon])
        selectForm += '</select></form></p>'
        return selectForm

    def lexicon(self, module, entry):
        query = "SELECT Information FROM {0} WHERE EntryID = ?".format(module)
        self.cursor.execute(query, (entry,))
        information = self.cursor.fetchone()
        if not information:
            return "[not applicable]"
        else:
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
            return "[not applicable]"
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
            return "[not applicable]"
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
            return "[not applicable]"
        else:
            if module == "exlbl":
                content = re.sub('href="getImage\.php\?resource=([^"]*?)&id=([^"]*?)"', r'href="javascript:void(0)" onclick="openImage({0}\1{0},{0}\2{0})"'.format("'"), content[0])
                return content.replace("[MYGOOGLEAPIKEY]", config.myGoogleApiKey)
            else:
                return content[0]


class Commentary:

    def __init__(self, text):
        self.text = text
        if self.text in self.getCommentaryList():
            self.database = os.path.join("marvelData", "commentaries", "c{0}.commentary".format(text))
            self.connection = sqlite3.connect(self.database)
            self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def bcvToVerseReference(self, b, c, v):
        parser = BibleVerseParser("YES")
        verseReference = parser.bcvToVerseReference(b, c, v)
        del parser
        return verseReference

    def formCommentaryTag(self, commentary):
        return "<ref onclick='document.title=\"_commentary:::{0}\"' onmouseover='commentaryName(\"{0}\")'>".format(commentary)

    def formBookTag(self, b):
        bookAbb = self.bcvToVerseReference(b, 1, 1)[:-4]
        return "<ref onclick='document.title=\"_commentary:::{0}.{1}\"' onmouseover='bookName(\"{2}\")'>".format(self.text, b, bookAbb)

    def formChapterTag(self, b, c):
        return "<ref onclick='document.title=\"_commentary:::{0}.{1}.{2}\"' onmouseover='document.title=\"_info:::Chapter {2}\"'>".format(self.text, b, c)

    def formVerseTag(self, b, c, v):
        verseReference = self.bcvToVerseReference(b, c, v)
        return "<ref id='v{0}.{1}.{2}' onclick='document.title=\"COMMENTARY:::{3}:::{4}\"' onmouseover='document.title=\"_instantVerse:::{3}:::{0}.{1}.{2}\"' ondblclick='document.title=\"_commentary:::{3}.{0}.{1}.{2}\"'>".format(b, c, v, self.text, verseReference)

    def getCommentaryList(self):
        commentaryFolder = os.path.join("marvelData", "commentaries")
        commentaryList = [f[1:-11] for f in os.listdir(commentaryFolder) if os.path.isfile(os.path.join(commentaryFolder, f)) and f.endswith(".commentary")]
        return commentaryList

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
        return " ".join(["{0}<button class='feature'>{1}</button></ref>".format(self.formBookTag(book), self.bcvToVerseReference(book, 1, 1)[:-4]) for book in bookList])

    def getChapterList(self, b=config.commentaryB):
        t = (b,)
        query = "SELECT DISTINCT Chapter FROM Commentary WHERE Book=? ORDER BY Chapter"
        self.cursor.execute(query, t)
        return [chapter[0] for chapter in self.cursor.fetchall()]

    def getChapters(self, b=config.commentaryB):
        chapterList = self.getChapterList(b)
        return " ".join(["{0}{1}</ref>".format(self.formChapterTag(b, chapter), chapter) for chapter in chapterList])

    def getChaptersMenu(self, b=config.commentaryB, text=config.commentaryText):
        chapterList = self.getChapterList(b, text)
        return " ".join(["{0}{1}</ref>".format(self.formVerseTag(b, chapter, 1), chapter) for chapter in chapterList])

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
            menu = "<ref onclick='document.title=\"COMMENTARY:::{0}:::{1}\"'>&lt;&lt;&lt; Go to {0} - {1}</ref>".format(config.commentaryText, mainVerseReference)
            menu += "<hr><b>Commentaries:</b> {0}".format(self.getCommentaries())
            items = command.split(".", 3)
            text = items[0]
            if not text == "":
                # i.e. text specified; add book menu
                menu += "<hr><b>Selected Commentary:</b> <span style='color: brown;' onmouseover='commentaryName(\"{0}\")'>{0}</span>  <button class='feature' onclick='document.title=\"COMMENTARY:::{0}:::{1}\"'>open {1} in {0}</button>".format(self.text, mainVerseReference)
                menu += "<hr><b>Books:</b> {0}".format(self.getBooks())
                bcList = [int(i) for i in items[1:]]
                if bcList:
                    check = len(bcList)
                    if check >= 1:
                        # i.e. book specified; add chapter menu
                        menu += "<hr><b>Selected book:</b> <span style='color: brown;' onmouseover='bookName(\"{0}\")'>{0}</span>".format(self.bcvToVerseReference(bcList[0], 1, 1)[:-4])
                        menu += "<hr><b>Chapters:</b> {0}".format(self.getChapters(bcList[0]))
                    if check >= 2:
                        # i.e. both book and chapter specified; add verse menu
                        menu += "<hr><b>Selected chapter:</b> <span style='color: brown;' onmouseover='document.title=\"_info:::Chapter {0}\"'>{0}</span>".format(bcList[1])
                        menu += "<hr><b>Verses:</b> {0}".format(self.getVerses(bcList[0], bcList[1]))
                    if check == 3:
                        menu += "<hr><b>Selected verse:</b> <span style='color: brown;' onmouseover='document.title=\"_instantVerse:::{0}:::{1}.{2}.{3}\"'>{3}</span> <button class='feature' onclick='document.title=\"COMMENTARY:::{0}:::{4}\"'>open HERE</button>".format(self.text, bcList[0], bcList[1], bcList[2], mainVerseReference)
            return menu
        else:
            return "INVALID_COMMAND_ENTERED"

    def getContent(self, verse):
        if self.text in self.getCommentaryList():
            b, c, v = verse
            biblesSqlite = BiblesSqlite()
            chapter = "<h2>{0}{1}</ref></h2>".format(biblesSqlite.formChapterTag(b, c, config.studyText), self.bcvToVerseReference(b, c, v).split(":", 1)[0])
            del biblesSqlite
            query = "SELECT Scripture FROM Commentary WHERE Book=? AND Chapter=?"
            self.cursor.execute(query, verse[:-1])
            scripture = self.cursor.fetchone()
            chapter += re.sub('onclick="luV\(([0-9]+?)\)"', r'onclick="luV(\1)" onmouseover="qV(\1)" ondblclick="mV(\1)"', scripture[0])
            if not scripture:
                return "[No content is found for this chapter!]"
            else:
                return "<div>{0}</div>".format(chapter)
        else:
            return "INVALID_COMMAND_ENTERED"
