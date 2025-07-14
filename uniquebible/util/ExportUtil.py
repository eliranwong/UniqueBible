from uniquebible import config
if __name__ == "__main__":
    from uniquebible.util.ConfigUtil import ConfigUtil
    config.marvelData = "/Users/otseng/UniqueBible/marvelData/"
    config.noQt = True
    ConfigUtil.setup()
    config.noQt = True
import sys
from uniquebible.db.BiblesSqlite import BiblesSqlite
from uniquebible.util.BibleVerseParser import BibleVerseParser
from bs4 import BeautifulSoup

from uniquebible.db.ToolsSqlite import Commentary
class ExportUtil:

    def __init__(self):
        self.biblesSqlite = BiblesSqlite()

    def getAllBibles(self):
        bibles = self.biblesSqlite.getBibleList()
        return bibles

    def getBibleInfo(self, text):
        return self.biblesSqlite.bibleInfo(text)

    def printAllCommentaries(self):
        commentaries = Commentary().getCommentaryList()
        for commentary in commentaries:
            print(commentary)

    def getAvailableCommentaries(self, bookName, chapter):
        bookNum = BibleVerseParser(config.parserStandarisation).bookNameToNum(bookName)
        commentaries = Commentary().getCommentaryListThatHasBookAndChapter(bookNum, chapter)
        return commentaries

    def getCommentaryText(self, commentary, bookNum, chapter):
        commentary = Commentary(commentary)
        content = commentary.getRawContent(bookNum, chapter)
        if content:
            content = BeautifulSoup(content[0], "html5lib").get_text()
            return content
        else:
            return ''

    def exportCommentary(self, outputDir, bookName, chapter):

        print("Generating " + bookName + " chapter " + str(chapter))
        export = ExportUtil()
        filename = "Commentary_" + bookName + "_" + str(chapter) + ".txt"
        outputFile = outputDir + filename
        file = open(outputFile, "w")

        bookNum = BibleVerseParser(config.parserStandarisation).bookNameToNum(bookName)
        commentaries = export.getAvailableCommentaries(bookName, chapter)
        for commentary in commentaries:
            content = export.getCommentaryText(commentary[0], bookNum, chapter)
            file.write(content)
        file.close()

if __name__ == "__main__":
    export = ExportUtil()
    print("Start")

    # outputDir = "/Users/otseng/Downloads/"
    # bookName = "Hosea"
    # chapter = 9
    #
    # export.exportCommentary(outputDir, bookName, chapter)

    bibles = export.getAllBibles()
    for bible in bibles:
        info = export.getBibleInfo(bible)
        print(bible + ", " + info)

    print("Done")
