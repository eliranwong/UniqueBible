import os, sqlite3

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
            return content[0]
        else:
            return "[empty]"

    def getVerseNote(self, bcvTuple):
        query = "SELECT Note FROM VerseNote WHERE Book=? AND Chapter=? AND Verse=?"
        self.cursor.execute(query, bcvTuple)
        content = self.cursor.fetchone()
        if content:
            return content[0]
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
