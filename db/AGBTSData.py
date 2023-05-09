import config, apsw, os

class AGBTSData:

    def __init__(self, language=""):
        # connect bibles.sqlite
        self.database = os.path.join(config.marvelData, "AGBTS_data.sqlite")
        self.connection = apsw.Connection(self.database)
        #self.connection.createscalarfunction("REGEXP", TextUtil.regexp)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getchapterSubheadings(self, b, c):
        query = "SELECT * FROM subheadings WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, (b, c))
        return self.cursor.fetchall()
