import os, re, apsw
from uniquebible import config
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.util.DateUtil import DateUtil
from uniquebible.util.TextUtil import TextUtil


class NoteSqlite:

    def __init__(self):
        # connect the note file specified in config.py > config.bibleNotes
        self.database = os.path.join(config.marvelData, config.bibleNotes)
        self.connection = apsw.Connection(self.database)
        #self.connection.setbusytimeout(500)
        self.cursor = self.connection.cursor()
        create = (
            "CREATE TABLE IF NOT EXISTS BookNote (Book INT, Note TEXT)",
            "CREATE TABLE IF NOT EXISTS ChapterNote (Book INT, Chapter INT, Note TEXT)",
            "CREATE TABLE IF NOT EXISTS VerseNote (Book INT, Chapter INT, Verse INT, Note TEXT)",
        )
        for statement in create:
            self.cursor.execute(statement)
        if not self.checkColumnExists("ChapterNote", "Updated"):
            self.addColumnToTable("ChapterNote", "Updated", "INT")
            self.addColumnToTable("ChapterNote", "GistId", "NVARCHAR(40)")
        if not self.checkColumnExists("VerseNote", "Updated"):
            self.addColumnToTable("VerseNote", "Updated", "INT")
            self.addColumnToTable("VerseNote", "GistId", "NVARCHAR(40)")
        if not self.checkColumnExists("BookNote", "Updated"):
            self.addColumnToTable("BookNote", "Updated", "INT")
            self.addColumnToTable("BookNote", "GistId", "NVARCHAR(40)")
#        #self.cursor.execute("COMMIT")

    def __del__(self):
        self.connection.close()

    def getBookNote(self, b):
        query = "SELECT Note, Updated FROM BookNote WHERE Book=?"
        self.cursor.execute(query, (b,))
        content = self.cursor.fetchone()
        if content:
            return content
        else:
            return config.thisTranslation["empty"], 0

    def getChapterNote(self, b, c):
        query = "SELECT Note, Updated FROM ChapterNote WHERE Book=? AND Chapter=?"
        self.cursor.execute(query, (b, c))
        content = self.cursor.fetchone()
        if content:
            return content
        else:
            return config.thisTranslation["empty"], 0

    def getVerseNote(self, b, c, v):
        query = "SELECT Note, Updated FROM VerseNote WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, (b, c, v))
        content = self.cursor.fetchone()
        if content:
            return content
        else:
            return config.thisTranslation["empty"], 0

    def displayBookNote(self, b):
        content, updated = self.getBookNote(b)
        #content = self.customFormat(content)
        content = self.highlightSearch(content)
        return content, updated

    def displayChapterNote(self, b, c):
        content, updated = self.getChapterNote(b, c)
        #content = self.customFormat(content)
        content = self.highlightSearch(content)
        return content, updated

    def displayVerseNote(self, b, c, v):
        content, updated = self.getVerseNote(b, c, v)
        #content = self.customFormat(content)
        content = self.highlightSearch(content)
        return content, updated

    def isNotEmptyNote(self, text):
        p = re.compile("<body[^<>]*?>[ \r\n ]*?<p[^<>]*?>[ \r\n ]*?<br />[ \r\n ]*?</p>[ \r\n ]*?</body>[ \r\n ]*?</html>", flags=re.M)
        if p.search(text):
            return False
        else:
            return True

    def saveBookNote(self, b, note, updated=DateUtil.epoch()):
        delete = "DELETE FROM BookNote WHERE Book=?"
        self.cursor.execute(delete, (b,))
#        self.cursor.execute("COMMIT")
        if note and note != config.thisTranslation["empty"] and self.isNotEmptyNote(note):
            insert = "INSERT INTO BookNote (Book, Note, Updated) VALUES (?, ?, ?)"
            self.cursor.execute(insert, (b, note, updated))
#            self.cursor.execute("COMMIT")

    def saveChapterNote(self, b, c, note, updated=DateUtil.epoch()):
        delete = "DELETE FROM ChapterNote WHERE Book=? AND Chapter=?"
        self.cursor.execute(delete, (b, c))
#        self.cursor.execute("COMMIT")
        if note and note != config.thisTranslation["empty"] and self.isNotEmptyNote(note):
            insert = "INSERT INTO ChapterNote (Book, Chapter, Note, Updated) VALUES (?, ?, ?, ?)"
            self.cursor.execute(insert, (b, c, note, updated))
#            self.cursor.execute("COMMIT")

    def setBookNoteUpdate(self, b, c, updated):
        update = "UPDATE BookNote set Updated=? WHERE Book=?"
        self.cursor.execute(update, (updated, b))
#        self.cursor.execute("COMMIT")

    def setChapterNoteUpdate(self, b, c, updated):
        update = "UPDATE ChapterNote set Updated=? WHERE Book=? and Chapter=?"
        self.cursor.execute(update, (updated, b, c))
#        self.cursor.execute("COMMIT")

    def setChapterNoteContent(self, b, c, content, updated):
        update = "UPDATE ChapterNote set Note=?, Updated=? WHERE Book=? and Chapter=?"
        self.cursor.execute(update, (content, updated, b, c))
#        self.cursor.execute("COMMIT")

    def saveVerseNote(self, b, c, v, note, updated=DateUtil.epoch()):
        delete = "DELETE FROM VerseNote WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(delete, (b, c, v))
#        #self.cursor.execute("COMMIT")
        if note and note != config.thisTranslation["empty"] and self.isNotEmptyNote(note):
            insert = "INSERT INTO VerseNote (Book, Chapter, Verse, Note, Updated) VALUES (?, ?, ?, ?, ?)"
            self.cursor.execute(insert, (b, c, v, note, updated))
#            #self.cursor.execute("COMMIT")

    def setVerseNoteUpdate(self, b, c, v, updated):
        update = "UPDATE VerseNote set Updated = ? WHERE Book=? and Chapter=? and Verse=?"
        self.cursor.execute(update, (updated, b, c, v))
#        self.cursor.execute("COMMIT")

    def setVerseNoteContent(self, b, c, v, content, updated):
        update = "UPDATE VerseNote set Note=?, Updated=? WHERE Book=? and Chapter=? and Verse=?"
        self.cursor.execute(update, (content, updated, b, c, v))
#        self.cursor.execute("COMMIT")
    
    def getSearchedBookList(self, searchString):
        searchString = "%{0}%".format(searchString)
        query = TextUtil.getQueryPrefix()
        query += "SELECT DISTINCT Book FROM BookNote WHERE Note LIKE ? ORDER BY Book"
        self.cursor.execute(query, (searchString,))
        standardAbbreviation = BibleVerseParser(config.parserStandarisation).standardAbbreviation
        return ["<ref onclick='document.title=\"_openbooknote:::{0}\"'>{1}</ref>".format(book[0], standardAbbreviation[str(book[0])]) for book in self.cursor.fetchall()]

    def getSearchedChapterList(self, searchString):
        searchString = "%{0}%".format(searchString)
        query = TextUtil.getQueryPrefix()
        query += "SELECT DISTINCT Book, Chapter FROM ChapterNote WHERE Note LIKE ? ORDER BY Book, Chapter"
        self.cursor.execute(query, (searchString,))
        parser = BibleVerseParser(config.parserStandarisation)
        return ["<ref onclick='document.title=\"_openchapternote:::{0}.{1}\"'>{2}</ref>".format(book, chapter, parser.bcvToVerseReference(book, chapter, 1)[:-2]) for book, chapter in self.cursor.fetchall()]

    def getSearchedVerseList(self, searchString):
        searchString = "%{0}%".format(searchString)
        query = TextUtil.getQueryPrefix()
        query += "SELECT DISTINCT Book, Chapter, Verse FROM VerseNote WHERE Note LIKE ? ORDER BY Book, Chapter, Verse"
        self.cursor.execute(query, (searchString,))
        parser = BibleVerseParser(config.parserStandarisation)
        return ["<ref onclick='document.title=\"_openversenote:::{0}.{1}.{2}\"'>{3}</ref>".format(book, chapter, verse, parser.bcvToVerseReference(book, chapter, verse)) for book, chapter, verse in self.cursor.fetchall()]

    def getChapterVerseList(self, b, c):
        query = "SELECT DISTINCT Verse FROM VerseNote WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, (b, c))
        return [verse[0] for verse in self.cursor.fetchall()]

    def isBookNote(self, b):
        query = "SELECT DISTINCT Book FROM BookNote WHERE Book=?"
        self.cursor.execute(query, (b,))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def isChapterNote(self, b, c):
        query = "SELECT DISTINCT Chapter FROM ChapterNote WHERE Book=? AND Chapter=?"
        self.cursor.execute(query, (b, c))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def highlightSearch(self, content):
        highlight = config.noteSearchString
        if highlight and not highlight == "z":
            content = re.sub("("+highlight+")", r"<z>\1</z>", content, flags=re.IGNORECASE)
            content = TextUtil.fixTextHighlighting(content)
            # add an id so as to scroll to the first result
            content = re.sub("<z>", "<span id='v{0}.{1}.{2}'></span><z>".format(config.studyB, config.studyC, config.studyV), content, count=1)
        return content

    def getAllBooks(self):
        query = "SELECT Book, 0, 0, Note, Updated FROM BookNote ORDER BY Book"
        self.cursor.execute(query)
        content = self.cursor.fetchall()
        return content

    def getAllChapters(self):
        query = "SELECT Book, Chapter, 0, Note, Updated FROM ChapterNote ORDER BY Book, Chapter"
        self.cursor.execute(query)
        content = self.cursor.fetchall()
        return content

    def getAllVerses(self):
        query = "SELECT Book, Chapter, Verse, Note, Updated FROM VerseNote ORDER BY Book, Chapter, Verse"
        self.cursor.execute(query)
        content = self.cursor.fetchall()
        return content

    def getBookCount(self):
        query = "SELECT count(*) FROM BookNote"
        dataCopy = self.cursor.execute(query)
        result = dataCopy.fetchone()
        return result[0]

    def getChapterCount(self):
        query = "SELECT count(*) FROM ChapterNote"
        dataCopy = self.cursor.execute(query)
        result = dataCopy.fetchone()
        return result[0]

    def getVerseCount(self):
        query = "SELECT count(*) FROM VerseNote"
        dataCopy = self.cursor.execute(query)
        result = dataCopy.fetchone()
        return result[0]

    def deleteAllNotes(self):
        self.deleteBookNotes()
        self.deleteChapterNotes()
        self.deleteVerseNotes()

    def deleteBookNotes(self):
        self.cursor.execute("DELETE FROM BookNote")
#        self.cursor.execute("COMMIT")

    def deleteChapterNotes(self):
        self.cursor.execute("DELETE FROM ChapterNote")
#        self.cursor.execute("COMMIT")

    def deleteVerseNotes(self):
        self.cursor.execute("DELETE FROM VerseNote")
#        self.cursor.execute("COMMIT")

    def checkColumnExists(self, table, column):
        self.cursor.execute("SELECT * FROM pragma_table_info(?) WHERE name=?", (table, column))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def addColumnToTable(self, table, column, column_type):
        sql = "ALTER TABLE " + table + " ADD COLUMN " + column + " " + column_type
        self.cursor.execute(sql)


# Only used for test

# def test_deleteAllNotes():
#     ns = NoteSqlite()
#     ns.deleteAllNotes()

def test_printAllCount():
    ns = NoteSqlite()
    print("Books: {0}".format(ns.getBookCount()))
    print("Chapters: {0}".format(ns.getChapterCount()))
    print("Verses: {0}".format(ns.getVerseCount()))

if __name__ == "__main__":

    test_printAllCount()


