from uniquebible import config
from uniquebible.db.IndexSqlite import IndexSqlite

if __name__ == "__main__":
    config.noQt = True

from uniquebible.db.BiblesSqlite import BiblesSqlite, Bible


class IndexerUtil:

    @staticmethod
    def createBibleIndex(bibleName, startBookNum=1, endBookNum=66):
        biblesSqlite = BiblesSqlite()
        bibleInfo = biblesSqlite.bibleInfo(bibleName)
        indexSqlite = IndexSqlite("bible", bibleName, True)
        if bibleInfo:
            print(f"Creating index for {bibleName}")
            bookList = biblesSqlite.getBookList(bibleName)
            for bookNum in bookList:
                if bookNum > endBookNum:
                    break
                if bookNum < startBookNum:
                    continue
                chapterList = biblesSqlite.getChapterList(bookNum, bibleName)
                print(f"Indexing {bookNum}:{chapterList}")
                for chapterNum in chapterList:
                    verseList = biblesSqlite.getVerseList(bookNum, chapterNum, bibleName)
                    for verseNum in verseList:
                        verseData = biblesSqlite.readTextVerse(bibleName, bookNum, chapterNum, verseNum)
                        words = verseData[3].split()
                        print(f"Inserting {bookNum}:{chapterNum}:{verseNum}:{words}")
                        indexContent = []
                        for word in words:
                            if len(word) > 1:
                                indexContent.append((word, bookNum, chapterNum, verseNum))
                        indexSqlite.insertBibleData(indexContent)
            IndexerUtil.updateIndexRef(bibleName)
        else:
            print(f"Could not find Bible {bibleName}")

    @staticmethod
    def testDelete(bibleName):
        indexSqlite = IndexSqlite("bible", bibleName, True)
        indexSqlite.deleteBook(1)

    @staticmethod
    def updateIndexRef(bibleName):
        indexSqlite = IndexSqlite("bible", bibleName)
        indexSqlite.updateRef()

    @staticmethod
    def updateBibleRef(bibleName):
        Bible(bibleName).updateRef()

    @staticmethod
    def testGetVerses(bibleName, word):
        indexSqlite = IndexSqlite("bible", bibleName)
        if indexSqlite.exists:
            verses = indexSqlite.getVerses(word)
            whereList = []
            for verse in verses:
                whereList.append(f"'{verse[0]}-{verse[1]}-{verse[2]}'")
            sql = 'SELECT * FROM Verses WHERE REF IN ({})'.format(",".join(whereList))
            print(sql)

if __name__ == "__main__":

    bibleName = "TRx"
    IndexerUtil.createBibleIndex(bibleName, 1, 66)
    # IndexerUtil.testGetVerses(bibleName, "Adam")
    # IndexerUtil.updateIndexRef(bibleName)
    # IndexerUtil.updateBibleRef(bibleName)
    print("Done")
