import config


class Connection:

    def __new__(self, database):
        if config.enableBinaryExecutionMode:
            import sqlite3
            return sqlite3.Connection(database)
        else:
            import apsw
            return apsw.Connection(database)


def commit(cursor):
    if config.enableBinaryExecutionMode:
        try:
            cursor.execute("COMMIT")
        except:
            pass

