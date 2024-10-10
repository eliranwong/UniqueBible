from uniquebible import config
import apsw, os

class AGBTSData:

    def __init__(self):
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

    def getChapterFormattedSubheadings(self, b, c):
        query = "SELECT * FROM subheadings WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, (b, c))
        return "<br>".join(['<ref onclick="bcv({0},{1},{2})">[{1}:{2}]</ref> {3}'.format(b, c, v, text) for b, c, v, text in self.cursor.fetchall()])

    def getchapterParagraphs(self, b, c):
        query = "SELECT * FROM paragraphs WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, (b, c))
        return self.cursor.fetchall()