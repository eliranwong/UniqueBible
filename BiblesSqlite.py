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

if __name__ == '__main__':
    bibles = BiblesSqlite()
    text = bibles.compareVerse(1,1,1)
    print(text)
