"""
Reading data from bibles.sqlite
"""
import os, sqlite3, config
from BibleVerseParser import BibleVerseParser

class BiblesSqlite:

    def __init__(self):
        # connect bibles.sqlite
        self.database = os.path.join("marvelData", "bibles.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def bcvToVerseReference(self, b, c, v):
        Parser = BibleVerseParser("YES")
        verseReference = Parser.bcvToVerseReference(b, c, v)
        del Parser
        return verseReference

    def formVidTagCrossRefLink(self, b, c, v, text=config.mainText):
        verseReference = self.bcvToVerseReference(b, c, v)
        return "<vid id='v{0}.{1}.{2}' onclick='document.title=\"BIBLE:::{3}:::{4}\"'>".format(b, c, v, text, verseReference)

    def readTextChapter(self, text, b, c):
        t = (b, c)
        query = "SELECT * FROM {0} WHERE Book=? AND Chapter=? ORDER BY Verse".format(text)
        self.cursor.execute(query, t)
        textChapter = self.cursor.fetchall()
        if not textChapter:
            return [(b, c, 1, "")]
        # return a list of tuple
        return textChapter

    def readTextVerse(self, text, b, c, v):
        t = (b, c, v)
        query = "SELECT * FROM {0} WHERE Book=? AND Chapter=? AND Verse=?".format(text)
        self.cursor.execute(query, t)
        textVerse = self.cursor.fetchone()
        if not textVerse:
            return (b, c, v, "")
        # return a tuple
        return textVerse

    def getBibleList(self):
        t = ("table",)
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        self.cursor.execute(query, t)
        versions = self.cursor.fetchall()
        exclude = ("Details", "lexicalEntry", "morphology", "original")
        return [version[0] for version in versions if not version[0] in exclude]

    def getBookList(self, text=config.mainText):
        query = "SELECT DISTINCT Book FROM {0} ORDER BY Book".format(text)
        self.cursor.execute(query)
        return [book[0] for book in self.cursor.fetchall()]

    def getChapterList(self, b=config.mainB, text=config.mainText):
        t = (b,)
        query = "SELECT DISTINCT Chapter FROM {0} WHERE Book=? ORDER BY Chapter".format(text)
        self.cursor.execute(query, t)
        return [chapter[0] for chapter in self.cursor.fetchall()]

    def getChapters(self, b=config.mainB, text=config.mainText):
        chapterList = self.getChapterList(b, text)
        chapters = ""
        for chapter in chapterList:
            chapters += "{0}{1}</vid> ".format(self.formVidTagCrossRefLink(b, chapter, 1, text), chapter)
        return chapters

    def getVerseList(self, b, c, text=config.mainText):
        t = (b, c)
        query = "SELECT DISTINCT Verse FROM {0} WHERE Book=? AND Chapter=? ORDER BY Verse".format(text)
        self.cursor.execute(query, t)
        return [verse[0] for verse in self.cursor.fetchall()]

    def compareVerse(self, verseList, texts=["ALL"]):
        if len(verseList) == 1 and not texts == ["ALL"]:
            b, c, v = verseList[0]
            return self.compareVerseChapter(b, c, v, texts)
        else:
            verses = ""
            for verse in verseList:
                b, c, v = verse
                verses += self.readTranslations(b, c, v, texts)
            return verses

    def compareVerseChapter(self, b, c, v, texts):
        verseList = self.getVerseList(b, c, texts[0])
        chapter = "<h2>{0}</h2><table style='width: 100%;'>".format(self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        for verse in verseList:
            row = 0
            for text in texts:
                row = row + 1
                if row % 2 == 0:
                    chapter += "<tr>"
                else:
                    chapter += "<tr style='background-color: #f2f2f2;'>"
                if row == 1:
                    chapter += "<td style='vertical-align: text-top;'>{0}{1}</vid> ".format(self.formVidTagCrossRefLink(b, c, verse, text), verse)
                else:
                    chapter += "<td>"
                chapter += "</td><td><sup>({0})</sup></td><td>{1}</td></tr>".format(text, self.readTextVerse(text, b, c, verse)[3])
        chapter += "</table>"
        return chapter

    def readTranslations(self, b, c, v, texts):
        if texts == ["ALL"]:
            bibleList = self.getBibleList()
            texts = ["original", "LXX"]
            exclude = ("LXX", "LXX1", "LXX1i", "LXX2", "LXX2i", "MOB", "MAB", "MIB", "MPB", "MTB")
            for bible in bibleList:
                if not bible in exclude:
                    texts.append(bible)
        verses = "<h2>{0}</h2>".format(self.bcvToVerseReference(b, c, v))
        for text in texts:
            book, chapter, verse, verseText = self.readTextVerse(text, b, c, v)
            verses += "({0}{1}</vid>) {2}<br>".format(self.formVidTagCrossRefLink(b, c, v, text), text, verseText.strip())
        return verses

    def searchBible(self, text, mode, searchString):
        query = "SELECT * FROM {0} WHERE ".format(text)
        if mode == "BASIC":
            t = ("%{0}%".format(searchString),)
            query += "Scripture LIKE ?"
        elif mode == "ADVANCED":
            t = ()
            query += searchString
        query += " ORDER BY Book ASC, Chapter ASC, Verse ASC"
        self.cursor.execute(query, t)
        verses = self.cursor.fetchall()
        formatedText = ""
        for verse in verses:
            b, c, v, verseText = verse
            formatedText += "({0}) {1}<br>".format(self.bcvToVerseReference(b, c, v), verseText.strip())
        return formatedText

    def searchMorphology(self, mode, searchString):
        query = "SELECT * FROM morphology WHERE "
        if mode == "LexicalEntry":
            t = ("%{0},%".format(searchString),)
            query += "LexicalEntry LIKE ?"
        elif mode == "MorphologyCode":
            searchList = searchString.split(',')
            t = ("%{0},%".format(searchList[0]), searchList[1])
            query += "LexicalEntry LIKE ? AND MorphologyCode = ?"
        elif mode == "ADVANCED":
            t = ()
            query += searchString
        query += " ORDER BY Book ASC, Chapter ASC, Verse ASC, WordID"
        self.cursor.execute(query, t)
        words = self.cursor.fetchall()
        formatedText = ""
        for word in words:
            wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, morphology = word
            formatedText += "({0}) {1} {2}<br>".format(self.bcvToVerseReference(b, c, v), textWord, morphologyCode)
        return formatedText

    def plainVerseChapter(self, b, c):
        print("pending")

    def parallelVertical(self, b, c):
        print("pending")

    def parallelHorizontal(self, b, c):
        print("pending")

    def addInterlinearInSearchResult(self, b, c, v):
        print("pending")

    def readMultipleVerses(self, text, verseList):
        verses = ""
        for verse in verseList:
            b, c, v = verse
            verses += "({0}) {1}<br>".format(self.bcvToVerseReference(b, c, v), self.readTextVerse(text, b, c, v)[3])
        return verses

    def readPlainChapter(self, text, verse):
        # expect bcv is a tuple
        b, c, v = verse
        chapter = "<h2>{0}</h2>".format(self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        verseList = self.readTextChapter(text, b, c)
        for verseTuple in verseList:
            b, c, v, verseText = verseTuple
            chapter += "{0}{1}</vid> {2}<br>".format(self.formVidTagCrossRefLink(b, c, v, text), v, verseText)
        return chapter

    def readVerseCrossReferences(self, b, c, v):
        print("pending")

#if __name__ == '__main__':
    # Bibles = BiblesSqlite()

    # test search bible - BASIC
    # searchString = input("Search Bible [Basic]\nSearch for: ")
    # print(Bibles.searchBible("NET", "BASIC", searchString))

    # test search bible - ADVANCED
    # e.g. Scripture LIKE '%God%' AND Scripture LIKE '%love%'
    # searchString = input("Search Bible [Advanced]\nFilter for search: ")
    # print(Bibles.searchBible("NET", "ADVANCED", searchString))

    # test search morphology - lexicalEntry
    # e.g. H7225
    # searchString = input("Search Morphology [Lexical Entry]\nSearch for: ")
    # print(Bibles.searchMorphology("LexicalEntry", searchString))

    # test search morphology - MorphologyCode
    # e.g. E70020,verb.qal.wayq.p1.u.sg
    # searchString = input("Search Morphology [Morphology Code]\nFilter for search: ")
    # print(Bibles.searchMorphology("MorphologyCode", searchString))

    # test search morphology - ADVANCED
    # e.g. LexicalEntry LIKE '%E70020,%' AND Morphology LIKE '%third person%' AND (Book = 9 OR Book = 10)
    # searchString = input("Search Morphology [ADVANCED]\nFilter for search: ")
    # print(Bibles.searchMorphology("ADVANCED", searchString))

    # del Bibles
