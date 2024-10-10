import os, apsw, re
from uniquebible import config
from uniquebible.util.BibleVerseParser import BibleVerseParser


class Highlight:

    CREATE_HIGHLIGHT_TABLE = "CREATE TABLE IF NOT EXISTS Highlight (Book INT, Chapter INT, Verse INT, Code NVARCHAR(5))"

    codes = {"underline": "ul1", "ul1": "ul1"}

    def __init__(self):
        for i in range(len(config.highlightCollections)):
            code = "hl{0}".format(i + 1)
            self.codes[code] = code
        self.filename = os.path.join(config.marvelData, "highlights.bible")
        self.connection = apsw.Connection(self.filename)
        self.cursor = self.connection.cursor()
        if not self.checkTableExists():
            self.createHighlightTable()

    def __del__(self):
#        #self.cursor.execute("COMMIT")
        self.connection.close()

    def createHighlightTable(self):
        self.cursor.execute(Highlight.CREATE_HIGHLIGHT_TABLE)

    def checkTableExists(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Highlight'")
        if self.cursor.fetchone():
            return True
        else:
            return False

    def highlightVerse(self, b, c, v, code="hl1"):
        self.removeHighlight(b, c, v)
        insert = "INSERT INTO Highlight (Book, Chapter, Verse, Code) VALUES (?, ?, ?, ?)"
        self.cursor.execute(insert, (b, c, v, code))

    def removeHighlight(self, b, c, v):
        delete = "DELETE FROM Highlight WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(delete, (b, c, v))

    def deleteAll(self):
        delete = "DELETE FROM Highlight"
        self.cursor.execute(delete)
#        self.cursor.execute("COMMIT")

    def getVerseDict(self, b, c):
        query = "SELECT Verse, Code FROM Highlight WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, (b, c))
        return {verse: code for verse, code in self.cursor.fetchall()}

    def isHighlighted(self, b, c, v):
        query = "SELECT Code FROM Highlight WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, (b, c, v))
        return self.cursor.fetchone()

    def getHighlightedVerses(self, where=""):
        query = "SELECT Book, Chapter, Verse, Code FROM Highlight {0} ORDER BY Book, Chapter, Verse".format(where)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def highlightChapter(self, b, c, text):
        highlightDict = self.getVerseDict(b, c)
        text = re.sub("<verse>", "＠＠＠", text)
        for v in highlightDict.keys():
            find = '＠＠＠([^＠]*?<vid id="v' + str(b) + '\.' + str(c) + '\.' + str(v) + '")'
            text = re.sub(find, "<verse class=\"{0}\">\\1".format(highlightDict[v]), text)
        text = re.sub("＠＠＠", "<verse>", text)
        return text

    def highlightSearchResults(self, text, verses):
        for verse in verses:
            find = '<div style(.*?id=\'v' + str(verse[0]) + '\.' + str(verse[1]) + '\.' + str(verse[2]) + '\'.*?)</div>'
            text = re.sub(find, "<div class=\"{0}\" style\\1</div>".format(verse[3]), text)
        return text

    def decode(self, code):
        if code in Highlight.codes.keys():
            return Highlight.codes[code]
        else:
            return "hl1"

    def getHighlightedBcvList(self, highlight, reference):
        highlight = highlight.lower()
        if highlight == "" or highlight == "all":
            where = "WHERE 1=1 "
        else:
            code = self.decode(highlight)
            where = "WHERE CODE='{0}' ".format(code)
        if reference == "nt":
            where += "AND Book >= 40"
        elif reference == "ot":
            where += "AND Book < 40"
        elif not(reference == "" or reference == "all"):
            ref = BibleVerseParser(config.standardAbbreviation).extractAllReferences("{0} 1".format(reference))
            if ref:
                where += "AND Book={0}".format(ref[0][0])
        return self.getHighlightedVerses(where)

if __name__ == "__main__":

    config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"
    hl = Highlight()
    # hl.deleteAll()
    # hl.highlightVerse(43, 3, 1, 'hl1')
    # hl.highlightVerse(43, 3, 16, 'hl1')
    # hl.highlightVerse(43, 3, 22, 'hl1')
    # hl.highlightVerse(1, 1, 1, 'hl2')
    # hl.highlightVerse(1, 1, 2, 'hl3')
    # dict = hl.getVerseDict(50, 4)
    # print

    text = '''
    <div style=''>(<ref id='v39.1.3' onclick='document.title="_stayOnSameTab:::"; document.title="BIBLE:::KJV:::Mal 1:3"' onmouseover='document.title="_instantVerse:::KJV:::39.1.3"' ondblclick='document.title="_menu:::KJV.39.1.3"'>Mal 1:3</ref>) And I hated Esau, and laid his mountains and his heritage waste for the dragons of the wilderness. </div><div style=''>(<ref id='v39.1.5' onclick='document.title="_stayOnSameTab:::"; document.title="BIBLE:::KJV:::Mal 1:5"' onmouseover='document.title="_instantVerse:::KJV:::39.1.5"' ondblclick='document.title="_menu:::KJV.39.1.5"'>Mal 1:5</ref>) And your eyes shall see, and ye shall say, The LORD will be magnified from the border of Israel. </div>
    '''

    verses = [(39, 1, 1, 'hl1'), (39, 1, 3, 'ul1'), (39, 1, 5, 'hl2'), (39, 1, 6, 'hl2'), (43, 13, 34, 'hl1'), (43, 13, 35, 'ul1'), (50, 4, 1, 'hl1'), (50, 4, 3, 'hl1'), (50, 4, 4, 'hl2')]

    print(hl.highlightSearchResults(text, verses))
