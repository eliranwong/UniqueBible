import os, apsw
from uniquebible import config


class LiveFilterSqlite:

    TABLE_NAME = "LiveFilter"
    CREATE_TABLE = "CREATE TABLE IF NOT EXISTS {0} (Filter NVARCHAR(50), Pattern NVARCHAR(1000))".format(TABLE_NAME)

    def __init__(self):
        self.filename = os.path.join(config.marvelData, "livefilter.sqlite")
        self.connection = apsw.Connection(self.filename)
        self.cursor = self.connection.cursor()
        if not self.checkTableExists():
            self.createTable()
            self.insert("Jesus", "jesus|christ")

    def __del__(self):
#        #self.cursor.execute("COMMIT")
        self.connection.close()

    def createTable(self):
        self.cursor.execute(LiveFilterSqlite.CREATE_TABLE)

    def checkTableExists(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='{0}'".format(self.TABLE_NAME))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def insert(self, filter, pattern):
        if not self.checkFilterExists(filter):
            insert = "INSERT INTO {0} (Filter, Pattern) VALUES (?, ?)".format(self.TABLE_NAME)
            self.cursor.execute(insert, (filter, pattern))
#            self.cursor.execute("COMMIT")

    def delete(self, filter):
        delete = "DELETE FROM {0} WHERE Filter=?".format(self.TABLE_NAME)
        self.cursor.execute(delete, (filter,))
#        self.cursor.execute("COMMIT")

    def deleteAll(self):
        delete = "DELETE FROM {0}".format(self.TABLE_NAME)
        self.cursor.execute(delete)
#        self.cursor.execute("COMMIT")

    def checkFilterExists(self, filter):
        query = "SELECT * FROM {0} WHERE Filter=?".format(self.TABLE_NAME)
        self.cursor.execute(query, (filter,))
        if self.cursor.fetchone():
            return True
        else:
            return False

    def getPattern(self, filter):
        query = "SELECT Pattern FROM {0} WHERE Filter=?".format(self.TABLE_NAME)
        self.cursor.execute(query, (filter,))
        return self.cursor.fetchone()[0]

    def getAll(self):
        query = "SELECT Filter, Pattern FROM {0} ORDER BY Filter".format(self.TABLE_NAME)
        self.cursor.execute(query)
        return self.cursor.fetchall()


if __name__ == "__main__":

    config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"

    db = LiveFilterSqlite()
    db.deleteAll()
    db.insert("Jesus", "Jesus")
    db.insert("God", "God")
    db.insert("Apostles", "Matthew|Peter|Andrew|James|John|Philip|Bartholomew|Thomas|James|Judas|Simon")
    filters = db.getAll()
    for filter in filters:
        print("{0}:{1}".format(filter[0], filter[1]))

