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

    def readTextChapter(self, text, b, c):
        t = (b, c)
        query = "SELECT * FROM "+text+" WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, t)
        textChapter = self.cursor.fetchall()
        if not textChapter:
            return [(b, c, 1, "")]
        # return a list of tuple
        return textChapter

    def readTextVerse(self, text, b, c, v):
        t = (b, c, v)
        query = "SELECT * FROM "+text+" WHERE Book=? AND Chapter=? AND Verse=?"
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
        names = self.cursor.fetchall()
        exclude = ["Details", "lexicalEntry", "morphology", "original"]
        bibleList = [name[0] for name in names if not name[0] in exclude]
        return bibleList

    def getBookList(self, text=config.mainText):
        query = "SELECT DISTINCT Book FROM "+text+" ORDER BY Book"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def getChapterList(self, b, text=config.mainText):
        t = (b)
        query = "SELECT DISTINCT Chapter FROM "+text+" WHERE Book=? ORDER BY Chapter"
        self.cursor.execute(query, t)
        return self.cursor.fetchall()

    def getVerseList(self, b, c, text=config.mainText):
        t = (b, c)
        query = "SELECT DISTINCT Verse FROM "+text+" WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, t)
        return self.cursor.fetchall()

    def readTranslations(self, b, c, v, texts):
        bibleList = self.getBibleList()
        if texts == ["ALL"]:
            texts = ["original", "LXX"]
            exclude = ("LXX", "LXX1", "LXX1i", "LXX2", "LXX2i", "MOB", "MAB", "MIB", "MPB", "MTB")
            for bible in bibleList:
                if not bible in exclude:
                    texts.append(bible)
        Parser = BibleVerseParser("YES")
        verseReferenceString = Parser.bcvToVerseReference(b, c, v)
        del Parser
        verses = "<h2>"+verseReferenceString+"</h2>"
        for text in texts:
            if text in bibleList:
                verseTuple = self.readTextVerse(text, b, c, v)
                book = str(verseTuple[0])
                chapter = str(verseTuple[1])
                verse = str(verseTuple[2])
                scripture = verseTuple[3].strip()
                verses += "<vid id='v"+book+"."+chapter+"."+verse+"' onclick='luV("+verse+")'>"+verse+"</vid> "
                verses += scripture
                verses += "<br>"
        return verses

    def readAllTranslations(self, b, c, v):
        t = ("table",)
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        self.cursor.execute(query, t)
        names = self.cursor.fetchall()
        exclude = ["Details", "LXX", "LXX1", "LXX1i", "LXX2", "LXX2i", "MOB", "MAB", "MIB", "MPB", "MTB", "lexicalEntry", "morphology", "original"]
        verses = ""
        for name in names:
            text = name[0]
            if not text in exclude:
                verses += "<sup style='color: brown;'>"+text+"</sup> "
                verses += self.readTextVerse(text, b, c, v)[3].strip()
                verses += "<br>"
        return verses

    def compareVerse(self, b, c, v):
        Parser = BibleVerseParser("YES")
        verseReferenceString = Parser.bcvToVerseReference(b, c, v)
        del Parser
        comparison = "<h2>"+verseReferenceString+"</h2>"
        comparison += "<sup style='color: brown;'>MOB</sup> "+self.readTextVerse("original", b, c, v)[3].strip()+"<br>"
        comparison += "<sup style='color: brown;'>LXX</sup> "+self.readTextVerse("LXX", b, c, v)[3].strip()+"<br>"
        comparison += self.readAllTranslations(b, c, v)
        return comparison

    def compareChapterVerse(self, b, c, v, texts):
        #highlightVerse == v
        verseList = self.getVerseList(b, c, texts[0])
        Parser = BibleVerseParser("YES")
        chapterReferenceString = Parser.bcvToVerseReference(b, c, v)
        del Parser
        chapterReferenceString = chapterReferenceString.split(":", 1)[0]
        chapter = "<h2>"+chapterReferenceString+"</h2><table style='width: 100%;'>"
        for verse in verseList:
            verseNumber = verse[0]
            row = 0
            for text in texts:
                row = row + 1
                if row % 2 == 0:
                    chapter += "<tr>"
                else:
                    chapter += "<tr style='background-color: #f2f2f2;'>"
                if row == 1:
                    chapter += "<td style='vertical-align: text-top;'><vid id='v"+str(b)+"."+str(c)+"."+str(verseNumber)+"' onclick='luV("+str(verseNumber)+")'>"+str(verseNumber)+"</vid> "
                else:
                    chapter += "<td>"
                chapter += "</td><td><sup>("+text+")</sup></td><td>"
                chapter += self.readTextVerse(text, b, c, verseNumber)[3]
                chapter += "</td></tr>"
        chapter += "</table>"
        return chapter

    def compareVerseList(self, verseList, texts=["ALL"]):
        verses = ""
        if len(verseList) == 1 and not texts == ["ALL"]:
            b = verseList[0][0]
            c = verseList[0][1]
            v = verseList[0][2]
            return self.compareChapterVerse(b, c, v, texts)
        else:
            for verse in verseList:
                b = verse[0]
                c = verse[1]
                v = verse[2]
                if texts == ["ALL"]:
                    verses += self.compareVerse(b, c, v)
                    #verses += self.readTranslations(b, c, v, texts)
                else:
                    verses += self.readTranslations(b, c, v, texts)
        return verses

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

    def readMultipleVerses(self, text, verseList):
        verses = ""
        Parser = BibleVerseParser("YES")
        for verse in verseList:
            b = verse[0]
            c = verse[1]
            v = verse[2]
            verseReferenceString = Parser.bcvToVerseReference(b, c, v)
            verses += "("+verseReferenceString+") "+self.readTextVerse(text, b, c, v)[3]
            verses += "<br>"
        del Parser
        return verses

    def readPlainChapter(self, text, verse):
        # expect bcv is a tuple
        b = verse[0]
        c = verse[1]
        v = verse[2]
        Parser = BibleVerseParser("YES")
        chapterReferenceString = Parser.bcvToVerseReference(b, c, v)
        del Parser
        chapterReferenceString = chapterReferenceString.split(":", 1)[0]
        chapter = "<h2>"+chapterReferenceString+"</h2>"
        verseList = self.readTextChapter(text, b, c)
        for verseTuple in verseList:
            verseNumber = str(verseTuple[2])
            scripture = verseTuple[3]
            chapter += "<vid id='v"+str(b)+"."+str(c)+"."+verseNumber+"' onclick='luV("+verseNumber+")'>"+verseNumber+"</vid> "
            chapter += scripture
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
