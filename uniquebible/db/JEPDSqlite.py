import os, apsw, re
from uniquebible import config
from uniquebible.db import JEPDData
from uniquebible.util.BibleBooks import BibleBooks

class JEPDSqlite:

    CREATE_MAPPING_TABLE = "CREATE TABLE IF NOT EXISTS Mapping (Book INT, Chapter INT, Verse INT, Start INT, End INT, Source NVARCHAR(5))"
    CREATE_VERSES_TABLE = "CREATE TABLE IF NOT EXISTS Verses (Book INT, Chapter INT, Verse INT, Start INT, End INT, Source NVARCHAR(5), Bible NVARCHAR(20), Scripture TEXT)"

    def __init__(self):
        self.filename = os.path.join(config.marvelData, "JEPD.sqlite")
        self.connection = apsw.Connection(self.filename)
        self.cursor = self.connection.cursor()
        if not self.checkTableExists("Mapping"):
            self.createMappingTable()
        if not self.checkTableExists("Verses"):
            self.createVersesTable()

    def __del__(self):
        try:
            self.connection.close()
        except:
            pass

    def createMappingTable(self):
        self.cursor.execute(JEPDSqlite.CREATE_MAPPING_TABLE)

    def createVersesTable(self):
        self.cursor.execute(JEPDSqlite.CREATE_VERSES_TABLE)

    def checkTableExists(self, tablename):
        self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tablename}'")
        if self.cursor.fetchone():
            return True
        else:
            return False

    def deleteAll(self, table):
        delete = f"DELETE FROM {table}"
        self.cursor.execute(delete)

    def deleteBibleFromVerses(self, bible):
        delete = f"DELETE FROM Verses where Bible=?"
        self.cursor.execute(delete, (bible,))

    def getMapping(self, b, c, v):
        query = "SELECT Book, Chapter, Verse, Start, End, Source FROM Mapping WHERE Book=? AND Chapter=? AND Verse=? ORDER BY Start"
        self.cursor.execute(query, (b, c, v))
        return self.cursor.fetchall()

    def insertMapping(self, b, c, v, start, end, source, printLine=False):
        if printLine:
            print(f"Inserting {b},{c},{v},{start},{end},{source}")
        else:
            insert = "INSERT INTO Mapping (Book, Chapter, Verse, Start, End, Source) VALUES (?, ?, ?, ?, ?, ?)"
            self.cursor.execute(insert, (b, c, v, start, end, source))

    def getVerses(self, b, c, v, bible):
        query = "SELECT Book, Chapter, Verse, Start, End, Source, Scripture FROM Verses WHERE Book=? AND Chapter=? AND Verse=? AND Bible=? ORDER BY Start"
        self.cursor.execute(query, (b, c, v, bible))
        return self.cursor.fetchall()

    def insertVerse(self, b, c, v, start, end, source, bible, scripture, printLine=False):
        if printLine:
            print(f"Inserting {b},{c},{v},{start},{end},{source},{bible},{scripture}")
        else:
            insert = "INSERT INTO Verses (Book, Chapter, Verse, Start, End, Source, Bible, Scripture) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            self.cursor.execute(insert, (b, c, v, start, end, source, bible, scripture))

    def processLine(self, book, line, source):
        start = ''
        end = ''
        # print(f">>>>> {line}")
        if "-" not in line:
            # 31:49
            values = line.split(":")
            chapter = int(values[0])
            verse = int(values[1])
            self.insertMapping(book, chapter, verse, start, end, source)
        else:
            values = line.split("-")
            passageStart = values[0]
            verseEnd = values[1]
            if ":" not in verseEnd:
                # 50:1-11
                values = passageStart.split(":")
                chapter = int(values[0])
                verseStart = values[1]
                for verse in range(int(verseStart), int(verseEnd)+1):
                    self.insertMapping(book, chapter, verse, start, end, source)
            else:
                try:
                    values = line.split("-")
                    passageStart = values[0]
                    passageEnd = values[1]
                    values = passageStart.split(":")
                    chapterStart = int(values[0])
                    if "." not in values[1]:
                        verseStart = int(values[1])
                        values = passageEnd.split(":")
                        chapterEnd = int(values[0])
                        verseEnd = int(values[1])
                        if chapterStart == chapterEnd:
                            # 41:1-41:45
                            for verse in range(int(verseStart), int(verseEnd) + 1):
                                self.insertMapping(book, chapterStart, verse, start, end, source)
                        else:
                            # 12:1-26:15
                            for chapter in range(chapterStart, chapterEnd):
                                verseCount = BibleBooks.verses[int(book)][chapter]
                                for verse in range(1, verseCount):
                                    self.insertMapping(book, chapter, verse, '', '', source)
                            for verse in range(1, verseEnd+1):
                                self.insertMapping(book, chapterEnd, verse, '', '', source)
                    else:
                        values = values[1].split(".")
                        verseStart = int(values[0])
                        chunkStart = int(values[1])
                        values = passageEnd.split(":")
                        values = values[1].split(".")
                        verseEnd = int(values[0])
                        chunkEnd = int(values[1])
                        if verseStart == verseEnd:
                            # 21:1.1-21:1.6
                            # 46:5.5-46:5.99
                            self.insertMapping(book, chapterStart, verseStart, chunkStart, chunkEnd, source)
                        else:
                            # 12:1.1-12:4.9
                            # 2:4.6 - 2:25.99
                            if chunkStart == 1:
                                self.insertMapping(book, chapterStart, verseStart, '', '', source)
                            else:
                                self.insertMapping(book, chapterStart, verseStart, chunkStart, 99, source)
                            for verse in range(verseStart+1, verseEnd):
                                self.insertMapping(book, chapterStart, verse, '', '', source)
                            if chunkEnd == 99:
                                self.insertMapping(book, chapterStart, verseEnd, '', '', source)
                            else:
                                self.insertMapping(book, chapterStart, verseEnd, 1, chunkEnd, source)
                except Exception as ex:
                    print(ex)
                    print(f"Cannot process {line}")


    def loadMappingData(self):
        data = JEPDData.jepd

        for book, bookData in data.items():
            for source, info in bookData.items():
                lines = info.splitlines()
                for line in lines:
                    line = line.replace(",", "").strip()
                    if (line):
                        if line[-1] == ".":
                            line = line[0:-1]
                        self.processLine(book, line, source)

if __name__ == "__main__":
    jepd = JEPDSqlite()

    # Step 1 - Create the mapping database
    jepd.deleteAll("Mapping")
    jepd.loadMappingData()

    # Test 1 - Check the mapping data
    # data = [(5, 34, 7), (5, 12, 1), (5, 26, 15), (4, 16, 27), (1, 2, 4)]
    # for test in data:
    #     print(jepd.getMapping(*test))