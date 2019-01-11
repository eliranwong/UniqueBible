"""
Reading data from bibles.sqlite
"""
import os, sqlite3
from BibleVerseParser import BibleVerseParser

class BiblesSqlite:

    def __init__(self):
        # connect bibles.sqlite
        self.database = os.path.join("marvelData", "bibles.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def readTextChapter(self, text, b, c):
        t = (b, c)
        query = "SELECT * FROM "+text+" WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, t)
        textChapter = self.cursor.fetchall()
        # return a list of tuple
        return textChapter

    def readTextVerse(self, text, b, c, v):
        t = (b, c, v)
        query = "SELECT * FROM "+text+" WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, t)
        textVerse = self.cursor.fetchone()
        # return a tuple
        return textVerse

    def readOriginal(self, b, c, v):
        verse = self.readTextVerse("original", b, c, v)[3].strip()+"\n"
        return verse

    def readLXX(self, b, c, v):
        verse = self.readTextVerse("LXX", b, c, v)[3].strip()+"\n"
        return verse

    def readTranslations(self, b, c, v):
        t = ("table",)
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        self.cursor.execute(query, t)
        translations = self.cursor.fetchall()
        verses = ""
        for translation in translations:
            excludeList = ["Details", "LXX", "LXX1", "LXX1i", "LXX2", "LXX2i", "MOB", "MAB", "MIB", "MPB", "MTB", "lexicalEntry", "morphology", "original"]
            text = translation[0]
            if not text in excludeList:
                verses += self.readTextVerse(text, b, c, v)[3].strip()+"\n"
        return verses

    def compareVerse(self, b, c, v):
        Parser = BibleVerseParser("YES")
        verseReferenceString = Parser.bcvToVerseReference(b, c, v)
        comparison = "Compare "+verseReferenceString+"\n"
        comparison += self.readOriginal(b, c, v)
        comparison += self.readLXX(b, c, v)
        comparison += self.readTranslations(b, c, v)
        del Parser
        return comparison

    def searchBible(self, text, mode, searchString):
        query = "SELECT * FROM "+text+" WHERE "
        if mode == "BASIC":
            t = ("%"+searchString+"%",)
            query += "Scripture LIKE ?"
        elif mode == "ADVANCED":
            t = ()
            query += searchString
        query += " ORDER BY Book ASC, Chapter ASC, Verse ASC"
        self.cursor.execute(query, t)
        verses = self.cursor.fetchall()
        formatedText = ""
        Parser = BibleVerseParser("YES")
        for verse in verses:
            b = verse[0]
            c = verse[1]
            v = verse[2]
            verseText = verse[3].strip()
            verseReferenceString = Parser.bcvToVerseReference(b, c, v)
            formatedText += "("+verseReferenceString+") "+verseText+"\n"
        del Parser
        return formatedText

    def searchMorphology(self, mode, searchString):
        query = "SELECT * FROM morphology WHERE "
        if mode == "LexicalEntry":
            t = ("%"+searchString+",%",)
            query += "LexicalEntry LIKE ?"
        elif mode == "MorphologyCode":
            searchList = searchString.split(',')
            t = ("%"+searchList[0]+",%", searchList[1])
            query += "LexicalEntry LIKE ? AND MorphologyCode = ?"
        elif mode == "ADVANCED":
            t = ()
            query += searchString
        query += " ORDER BY Book ASC, Chapter ASC, Verse ASC, WordID"
        self.cursor.execute(query, t)
        words = self.cursor.fetchall()
        formatedText = ""
        Parser = BibleVerseParser("YES")
        for word in words:
            wordID = word[0]
            clauseID = word[1]
            b = word[2]
            c = word[3]
            v = word[4]
            textWord = word[5]
            lexicalEntry = word[6]
            morphologyCode = word[7]
            morphology = word[8]
            verseReferenceString = Parser.bcvToVerseReference(b, c, v)
            formatedText += "("+verseReferenceString+") "+textWord+" "+morphologyCode+"\n"
        del Parser
        return formatedText

    def plainVerseChapter(self, b, c):
        print("pending")

    def parallelVertical(self, b, c):
        print("pending")

    def parallelHorizontal(self, b, c):
        print("pending")

    def addInterlinearInSearchResult(self, b, c, v):
        print("pending")

    def readMultipleVerses(self, verseList):
        verses = ""
        Parser = BibleVerseParser("YES")
        for verse in verseList:
            b = verse[0]
            c = verse[1]
            v = verse[2]
            verseReferenceString = Parser.bcvToVerseReference(b, c, v)
            verses += "("+verseReferenceString+") "+self.readTextVerse("NET", b, c, v)[3] # use "NET" for testing only
            verses += "<br>"
        del Parser
        return verses

    def readPlainChapter(self, verse):
        # expect bcv is a tuple
        b = verse[0]
        c = verse[1]
        v = verse[2]
        Parser = BibleVerseParser("YES")
        chapterReferenceString = Parser.bcvToVerseReference(b, c, v)
        del Parser
        chapterReferenceString = chapterReferenceString.split(":", 1)[0]
        chapter = "<h2>"+chapterReferenceString+"</h2>"
        verseList = self.readTextChapter("NET", b, c) # use "NET" for testing only
        for verse in verseList:
            chapter += verse[3]
            chapter += "<br>"
        return chapter

    def readVerseCrossReferences(self, b, c, v):
        print("pending")

if __name__ == '__main__':
    Bibles = BiblesSqlite()

    # test verse comparison
    print(Bibles.compareVerse(1,1,1))

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

    del Bibles
