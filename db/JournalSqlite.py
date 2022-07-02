import config, os, apsw, re


class JournalSqlite:

    def __init__(self):
        # connect the note file specified in config.py > config.bibleNotes
        self.database = os.path.join(config.marvelData, "journal.sqlite")
        self.connection = apsw.Connection(self.database)
        self.cursor = self.connection.cursor()
        create = (
            "CREATE TABLE IF NOT EXISTS Journal (year INT, month INT, day INT, note TEXT)",
        )
        for statement in create:
            self.cursor.execute(statement)

    def getJournalNote(self, year, month, day):
        query = "SELECT note FROM Journal WHERE year=? AND month=? AND day=?"
        self.cursor.execute(query, (year, month, day))
        content = self.cursor.fetchone()
        if content:
            return content[0]
        else:
            return config.thisTranslation["empty"]

    def saveJournalNote(self, year, month, day, note):
        delete = "DELETE FROM Journal WHERE year=? AND month=? AND day=?"
        self.cursor.execute(delete, (year, month, day))
        if note and note != config.thisTranslation["empty"] and self.isNotEmptyNote(note):
            insert = "INSERT INTO Journal (year, month, day, note) VALUES (?, ?, ?, ?)"
            self.cursor.execute(insert, (year, month, day, note))

    def isNotEmptyNote(self, text):
        p = re.compile("<body[^<>]*?>[ \r\n ]*?<p[^<>]*?>[ \r\n ]*?<br />[ \r\n ]*?</p>[ \r\n ]*?</body>[ \r\n ]*?</html>", flags=re.M)
        if p.search(text):
            return False
        else:
            return True
