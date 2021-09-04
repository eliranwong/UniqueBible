import os, sqlite3, config

from util.DateUtil import DateUtil


class DevotionalSqlite:

    def __init__(self, devotional):
        self.database = os.path.join(config.marvelData, "devotionals", "{0}.devotional".format(devotional))
        self.connection = None
        if os.path.exists(self.database):
            self.connection = sqlite3.connect(self.database)
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


if __name__ == "__main__":
    from util.ConfigUtil import ConfigUtil
    from util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")

    d = DevotionalSqlite("Meyer - Our Daily Walk")
    # d = DevotionalSqlite("Chambers - My Utmost For His Highest")
    print(d.getEntry("1-10"))


