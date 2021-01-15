import os, sqlite3, re
import config

class Highlight:

    CREATE_HIGHLIGHT_TABLE = "CREATE TABLE IF NOT EXISTS Highlight (Book INT, Chapter INT, Verse INT, Code NVARCHAR(5))"

    def __init__(self):
        self.filename = os.path.join(config.marvelData, "highlights.bible")
        self.connection = sqlite3.connect(self.filename)
        self.cursor = self.connection.cursor()
        if not self.checkTableExists():
            self.createHighlightTable()

    def __del__(self):
        self.connection.commit()
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
        self.connection.commit()

    def getVerseDict(self, b, c):
        query = "SELECT Verse, Code FROM Highlight WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, (b, c))
        return {res[0]: res[1] for res in self.cursor.fetchall()}

    def highlightChapter(self, b, c, text):
        highlightDict = self.getVerseDict(b, c)
        for v in highlightDict.keys():
            find = '<verse>((<br>)*<vid id="v' + str(b) + '\.' + str(c) + '\.' + str(v) + '".*?)</verse>'
            text = re.sub(find, "<verse class=\"{0}\">\\1</verse>".format(highlightDict[v]), text)
        return text

if __name__ == "__main__":

    config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"
    hl = Highlight()
    # hl.deleteAll()
    # hl.highlightVerse(43, 3, 1, 'hl1')
    # hl.highlightVerse(43, 3, 16, 'hl1')
    # hl.highlightVerse(43, 3, 22, 'hl1')
    # hl.highlightVerse(1, 1, 1, 'hl2')
    # hl.highlightVerse(1, 1, 2, 'hl3')

    dict = hl.getVerseDict(50, 4)
    print(dict)

    chapter = '''<verse><vid id="v50.4.19" onclick="luV(19)" onmouseover="qV(19)" ondblclick="mV(19)">19</vid> And my God shall supply every need of yours according to his riches in glory in Christ Jesus.</verse>'''
    out = hl.highlightChapter(50, 4, chapter)
    print(out)