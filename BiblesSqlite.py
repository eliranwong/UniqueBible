"""
Reading data from bibles.sqlite
"""
import os, sqlite3
from BibleVerseParser import BibleVerseParser

class BiblesSqlite:

    # connect bibles.sqlite
    database = os.path.join("marvelData", "bibles.sqlite")
    connection = sqlite3.connect(database)
    cursor = connection.cursor()

    def readTextVerse(self, text, b, c, v):
        t = (b, c, v)
        query = "SELECT * FROM "+text+" WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, t)
        textVerse = self.cursor.fetchone()
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
        parser = BibleVerseParser("YES")
        verseReferenceString = parser.bcvToVerseReference(b, c, v)
        comparison = "Compare "+verseReferenceString+"\n"
        comparison += self.readOriginal(b, c, v)
        comparison += self.readLXX(b, c, v)
        comparison += self.readTranslations(b, c, v)
        return comparison

    def searchBible(self, text, mode, searchString):
        query = "SELECT * FROM "+text+" WHERE "
        if mode == "BASIC":
            t = ("%"+searchString+"%",)
            query += "Scripture LIKE ? ORDER BY Book ASC, Chapter ASC, Verse ASC"
        elif mode == "ADVANCED":
            query += searchString
            query += " ORDER BY Book ASC, Chapter ASC, Verse ASC"
        self.cursor.execute(query)
        verses = self.cursor.fetchall()
        formatedText = ""
        for verse in verses:
            b = verse[0]
            c = verse[1]
            v = verse[2]
            verseText = verse[3].strip()
            parser = BibleVerseParser("YES")
            verseReferenceString = parser.bcvToVerseReference(b, c, v)
            formatedText += "("+verseReferenceString+") "+verseText+"\n"
        return formatedText

if __name__ == '__main__':
    bibles = BiblesSqlite()

    # test verse comparison
    print(bibles.compareVerse(1,1,1))

    # test search bible - BASIC
    # searchString = input("Search Bible [Basic]\nSearch for: ")
    # print(bibles.searchBible("NET", "BASIC", searchString))

    # test search bible - ADVANCED
    # searchString = input("Search Bible [Advanced]\nFilter for search: ")
    # print(bibles.searchBible("NET", "ADVANCED", searchString))
