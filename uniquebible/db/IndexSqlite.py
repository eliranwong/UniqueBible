import os, apsw, logging
from uniquebible import config

class IndexSqlite:

    def __init__(self, type, filename, createFile=False):
        self.exists = False

        if "." not in filename:
            filename += ".index"
        indexDir = os.path.join(config.marvelData, "indexes")
        if not os.path.exists(indexDir):
            os.mkdir(indexDir)
        indexDir = os.path.join(indexDir, type)
        if not os.path.exists(indexDir):
            os.mkdir(indexDir)
        filePath = os.path.join(indexDir, filename)
        if not os.path.exists(filePath) and not createFile:
            return

        self.type = type
        self.filename = filename
        self.connection = apsw.Connection(filePath)
        self.cursor = self.connection.cursor()
        self.logger = logging.getLogger('uba')
        if not self.checkTableExists():
            if not createFile:
                return
            else:
                self.createTable()

        self.exists = True

    def __del__(self):
        if self.exists:
            self.connection.close()

    def createTable(self):
        if self.type == "bible":
            sql = "CREATE TABLE IF NOT EXISTS Index_Data (Word NVARCHAR(50), Book INT, Chapter INT, Verse INT, Ref TEXT)"
            self.cursor.execute(sql)

    def insertBibleData(self, content):
        insert = "INSERT INTO Index_Data (Word, Book, Chapter, Verse) VALUES (?, ?, ?, ?)"
        self.cursor.executemany(insert, content)
#        self.cursor.execute("COMMIT")

    def updateRef(self):
        if not self.checkColumnExists("Index_Data", "Ref"):
            self.addColumnToTable("Index_Data", "Ref", "TEXT")
        update = "UPDATE Index_Data SET Ref=Book || '-' || Chapter || '-' || Verse"
        self.cursor.execute(update)
        create = 'CREATE INDEX "Index_Word" ON "Index_Data" ("Word")'
        self.cursor.execute(create)
#        self.cursor.execute("COMMIT")

    def getVerses(self, word):
        sql = "SELECT Book, Chapter, Verse FROM Index_Data WHERE Word=? ORDER BY Book, Chapter, Verse"
        self.cursor.execute(sql, (word,))
        data = self.cursor.fetchall()
        return data

    def getRefs(self, word):
        sql = "SELECT Ref FROM Index_Data WHERE Word=? ORDER BY Book, Chapter, Verse"
        self.cursor.execute(sql, (word,))
        data = self.cursor.fetchall()
        return data

    def deleteAll(self):
        delete = "DELETE FROM Index_Data"
        self.cursor.execute(delete)
#        self.cursor.execute("COMMIT")

    def deleteBook(self, book):
        delete = "DELETE FROM Index_Data WHERE Book=?"
        self.cursor.execute(delete, (book,))
#        self.cursor.execute("COMMIT")

    def checkTableExists(self):
        if self.type == "bible":
            self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='Index_Data'")
            if self.cursor.fetchone():
                return True
        return False

    def checkColumnExists(self, table, column):
        self.cursor.execute("SELECT * FROM pragma_table_info(?) WHERE name=?", (table, column))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def addColumnToTable(self, table, column, column_type):
        sql = "ALTER TABLE " + table + " ADD COLUMN " + column + " " + column_type
        self.cursor.execute(sql)
