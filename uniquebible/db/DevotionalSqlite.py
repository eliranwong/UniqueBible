import os, apsw
from uniquebible import config


class DevotionalSqlite:

    CREATE_DEVOTIONAL_TABLE = """
            CREATE TABLE "devotional" (
            "month"	TEXT,
            "day"	TEXT,
            "devotion"	TEXT);"""

    def __init__(self, devotional):
        self.database = os.path.join(config.marvelData, "devotionals", "{0}.devotional".format(devotional))
        self.connection = None
        if os.path.exists(self.database):
            self.connection = apsw.Connection(self.database)
            self.cursor = self.connection.cursor()

    def __del__(self):
        if self.connection is not None:
            self.connection.close()

    def getEntry(self, month, day):
        if self.connection is not None:
            query = "SELECT devotion FROM devotional WHERE month=? and day=?"
            self.cursor.execute(query, (str(month), str(day)))
            content = self.cursor.fetchone()
            if content:
                text = content[0]
                return text
        return config.thisTranslation["empty"]

    def checkTableExists(self, table):
        if self.connection:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if self.cursor.fetchone():
                return True
            else:
                return False
        return False

    @staticmethod
    def createDevotional(devotional, content):
        database = os.path.join(config.marvelData, "devotionals", "{0}.devotional".format(devotional))
        if os.path.isfile(database):
            os.remove(database)
        with apsw.Connection(database) as connection:
            cursor = connection.cursor()
            cursor.execute(DevotionalSqlite.CREATE_DEVOTIONAL_TABLE)
#            cursor.execute("COMMIT")
            insert = "INSERT INTO devotional (month, day, devotion) VALUES (?, ?, ?)"
            cursor.executemany(insert, content)
#            cursor.execute("COMMIT")


if __name__ == "__main__":
    from uniquebible.util.ConfigUtil import ConfigUtil
    from uniquebible.util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")

    d = DevotionalSqlite("Meyer - Our Daily Walk")
    # d = DevotionalSqlite("Chambers - My Utmost For His Highest")
    print(d.getEntry("1-10"))


