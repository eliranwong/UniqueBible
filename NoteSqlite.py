import os, re, sqlite3, config

class NoteSqlite:

    def __init__(self):
        # connect note.sqlite
        self.database = os.path.join("marvelData", "note.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getChapterNote(self, bcTuple):
        query = "SELECT Note FROM ChapterNote WHERE Book=? AND Chapter=?"
        self.cursor.execute(query, bcTuple)
        content = self.cursor.fetchone()
        if content:
            return self.highlightSearch(content[0])
        else:
            return "[empty]"

    def getVerseNote(self, bcvTuple):
        query = "SELECT Note FROM VerseNote WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, bcvTuple)
        content = self.cursor.fetchone()
        if content:
            return self.highlightSearch(content[0])
        else:
            return "[empty]"

    def saveChapterNote(self, bcNoteTuple):
        b, c, note = bcNoteTuple
        delete = "DELETE FROM ChapterNote WHERE Book=? AND Chapter=?"
        self.cursor.execute(delete, (b, c))
        self.connection.commit()
        if note and note != "[empty]":
            insert = "INSERT INTO ChapterNote (Book, Chapter, Note) VALUES (?, ?, ?)"
            self.cursor.execute(insert, bcNoteTuple)
            self.connection.commit()

    def saveVerseNote(self, bcvNoteTuple):
        b, c, v, note = bcvNoteTuple
        delete = "DELETE FROM VerseNote WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(delete, (b, c, v))
        self.connection.commit()
        if note and note != "[empty]":
            insert = "INSERT INTO VerseNote (Book, Chapter, Verse, Note) VALUES (?, ?, ?, ?)"
            self.cursor.execute(insert, bcvNoteTuple)
            self.connection.commit()

    def getSearchedChapterList(self, searchString):
        searchString = "%{0}%".format(searchString)
        query = "SELECT DISTINCT Book, Chapter FROM ChapterNote WHERE Note LIKE ? ORDER BY Book, Chapter"
        self.cursor.execute(query, (searchString,))
        return [chapter for chapter in self.cursor.fetchall()]

    def highlightSearch(self, content):
        highlight = config.noteSearchString
        if highlight and not highlight == "z":
            content = re.sub("("+highlight+")", r"<z>\1</z>", content, flags=re.IGNORECASE)
            p = re.compile("(<[^<>]*?)<z>(.*?)</z>", flags=re.M)
            s = p.search(content)
            while s:
                content = re.sub(p, r"\1\2", content)
                s = p.search(content)
        return content
