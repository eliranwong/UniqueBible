import os, re, sqlite3, config
from BibleVerseParser import BibleVerseParser

class NoteSqlite:

    def __init__(self):
        # connect note.sqlite
        self.database = os.path.join(config.marvelData, "note.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        create = (
            "CREATE TABLE IF NOT EXISTS ChapterNote (Book INT, Chapter INT, Note TEXT)",
            "CREATE TABLE IF NOT EXISTS VerseNote (Book INT, Chapter INT, Verse INT, Note TEXT)",
        )
        for statement in create:
            self.cursor.execute(statement)
        self.connection.commit()

    def __del__(self):
        self.connection.close()

    def getChapterNote(self, bcTuple):
        query = "SELECT Note FROM ChapterNote WHERE Book=? AND Chapter=?"
        self.cursor.execute(query, bcTuple)
        content = self.cursor.fetchone()
        if content:
            return content[0]
        else:
            return config.thisTranslation["empty"]

    def getVerseNote(self, bcvTuple):
        query = "SELECT Note FROM VerseNote WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, bcvTuple)
        content = self.cursor.fetchone()
        if content:
            return content[0]
        else:
            return config.thisTranslation["empty"]

    def displayChapterNote(self, bcTuple):
        content = self.getChapterNote(bcTuple)
        #content = self.customFormat(content)
        content = self.highlightSearch(content)
        return content

    def displayVerseNote(self, bcvTuple):
        content = self.getVerseNote(bcvTuple)
        #content = self.customFormat(content)
        content = self.highlightSearch(content)
        return content

    def isNotEmptyNote(self, text):
        p = re.compile("<body[^<>]*?>[ \r\n ]*?<p[^<>]*?>[ \r\n ]*?<br />[ \r\n ]*?</p>[ \r\n ]*?</body>[ \r\n ]*?</html>", flags=re.M)
        if p.search(text):
            return False
        else:
            return True

    def saveChapterNote(self, bcNoteTuple):
        b, c, note = bcNoteTuple
        delete = "DELETE FROM ChapterNote WHERE Book=? AND Chapter=?"
        self.cursor.execute(delete, (b, c))
        self.connection.commit()
        if note and note != config.thisTranslation["empty"] and self.isNotEmptyNote(note):
            insert = "INSERT INTO ChapterNote (Book, Chapter, Note) VALUES (?, ?, ?)"
            self.cursor.execute(insert, bcNoteTuple)
            self.connection.commit()

    def saveVerseNote(self, bcvNoteTuple):
        b, c, v, note = bcvNoteTuple
        delete = "DELETE FROM VerseNote WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(delete, (b, c, v))
        self.connection.commit()
        if note and note != config.thisTranslation["empty"] and self.isNotEmptyNote(note):
            insert = "INSERT INTO VerseNote (Book, Chapter, Verse, Note) VALUES (?, ?, ?, ?)"
            self.cursor.execute(insert, bcvNoteTuple)
            self.connection.commit()

    def getSearchedChapterList(self, searchString):
        searchString = "%{0}%".format(searchString)
        query = "SELECT DISTINCT Book, Chapter FROM ChapterNote WHERE Note LIKE ? ORDER BY Book, Chapter"
        self.cursor.execute(query, (searchString,))
        return ["<ref onclick='document.title=\"_openchapternote:::{0}.{1}\"'>{2}</ref>".format(book, chapter, BibleVerseParser(config.parserStandarisation).bcvToVerseReference(book, chapter, 1)[:-2]) for book, chapter in self.cursor.fetchall()]

    def getSearchedVerseList(self, searchString):
        searchString = "%{0}%".format(searchString)
        query = "SELECT DISTINCT Book, Chapter, Verse FROM VerseNote WHERE Note LIKE ? ORDER BY Book, Chapter, Verse"
        self.cursor.execute(query, (searchString,))
        return ["<ref onclick='document.title=\"_openversenote:::{0}.{1}.{2}\"'>{3}</ref>".format(book, chapter, verse, BibleVerseParser(config.parserStandarisation).bcvToVerseReference(book, chapter, verse)) for book, chapter, verse in self.cursor.fetchall()]

    def getChapterVerseList(self, b, c):
        query = "SELECT DISTINCT Verse FROM VerseNote WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, (b, c))
        return [verse[0] for verse in self.cursor.fetchall()]

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
            p = re.compile("(<[^<>]*?)<z>(.*?)</z>", flags=re.M)
            s = p.search(content)
            while s:
                content = re.sub(p, r"\1\2", content)
                s = p.search(content)
            # add an id so as to scroll to the first result
            content = re.sub("<z>", "<z id='v{0}.{1}.{2}'>".format(config.studyB, config.studyC, config.studyV), content, count=1)
        return content
