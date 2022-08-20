"""
Reading data from bibles.sqlite
"""
import glob
import os, dbw, config, re, logging
from pathlib import Path

if __name__ == "__main__":
    from util.ConfigUtil import ConfigUtil
    config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"
    config.noQt = True
    ConfigUtil.setup()
    config.noQt = True

from util.BibleVerseParser import BibleVerseParser
from util.BibleBooks import BibleBooks
from db.NoteSqlite import NoteSqlite
from db.Highlight import Highlight
from util.ConfigUtil import ConfigUtil
from util.FileUtil import FileUtil
#from util.themes import Themes
from util.NoteService import NoteService
from util.TextUtil import TextUtil
from util.LexicalData import LexicalData

class BiblesSqlite:

    def __init__(self, language=""):
        # connect bibles.sqlite
        defaultDatabase = os.path.join(config.marvelData, "bibles.sqlite")
        langDatabase = os.path.join(config.marvelData, "bibles_{0}.sqlite".format(language))
        self.database = langDatabase if language and os.path.isfile(langDatabase) else defaultDatabase
        self.connection = dbw.Connection(self.database)
        self.cursor = self.connection.cursor()
        self.marvelBibles = ("MOB", "MIB", "MAB", "MPB", "MTB", "LXX1", "LXX1i", "LXX2", "LXX2i")
        self.logger = logging.getLogger('uba')

    def __del__(self):
        self.connection.close()

    # to-do list
    # sort out download helper

    def getBibleList(self, includeMarvelBibles=True):
        bibles = self.getPlainBibleList() + self.getFormattedBibleList(includeMarvelBibles)
        return sorted(set(bibles))

    # legacy list before version 0.56
    def getBibleList2(self):
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        self.cursor.execute(query, ("table",))
        versions = self.cursor.fetchall()
        exclude = ("Details", "lexicalEntry", "morphology", "original", "title", "interlinear", "kjvbcv")
        return [version[0] for version in versions if not version[0] in exclude]

    def getTwoBibleLists(self, includeMarvelBibles=True):
        return [self.getPlainBibleList(), self.getFormattedBibleList(includeMarvelBibles)]

    def getPlainBibleList(self):
        return self.getBibleList2()
        # return ["OHGB", "OHGBi", "LXX"]

    def getFormattedBibleList(self, includeMarvelBibles=True):
        formattedBiblesFolder = os.path.join(config.marvelData, "bibles")
        formattedBibles = [f[:-6] for f in os.listdir(formattedBiblesFolder) if os.path.isfile(os.path.join(formattedBiblesFolder, f)) and f.endswith(".bible") and not re.search(r"^[\._]", f)]
        if not includeMarvelBibles:
            formattedBibles = [bible for bible in formattedBibles if not bible in self.marvelBibles]
        return sorted(formattedBibles)

    def migratePlainFormattedBibles(self):
        self.installKJVversification()
        plainBibleList = self.getBibleList2()
        formattedBibleList = self.getFormattedBibleList()
        return list(set(plainBibleList) & set(formattedBibleList))

    def proceedMigration(self, biblesWithBothVersions):
            for bible in biblesWithBothVersions:
                # retrieve plain verses from bibles.sqlite
                query = "SELECT * FROM {0} ORDER BY Book, Chapter, Verse".format(bible)
                self.cursor.execute(query)
                verses = self.cursor.fetchall()
                # import into formatted bible database
                Bible(bible).importPlainFormat(verses)
                # delete plain verses from bibles.sqlite
                delete = "DROP TABLE {0}".format(bible)
                self.cursor.execute(delete)
                if config.enableBinaryExecutionMode:
                    self.cursor.execute("COMMIT")
            self.connection.execute("VACUUM")

    def installKJVversification(self):
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        self.cursor.execute(query, ("table",))
        versions = self.cursor.fetchall()
        versions = [version[0] for version in versions]
        if "KJV" in versions and not "kjvbcv" in versions:
            query = "SELECT * FROM KJV ORDER BY Book, Chapter, Verse"
            self.cursor.execute(query)
            verses = self.cursor.fetchall()
            verses = [(b, c, v, "") for b, c, v, *_ in verses]
            self.importBible("KJV versification", "kjvbcv", verses)

    def bibleInfo(self, text):
        plainBibleList, formattedBibleList = self.getTwoBibleLists()
        if text in plainBibleList:
            query = "SELECT Scripture FROM {0} WHERE Book=0 AND Chapter=0 AND Verse=0".format(text)
            self.cursor.execute(query)
            info = self.cursor.fetchone()
            if info:
                return info[0]
            else:
                return ""
        elif text in formattedBibleList:
            try:
                return Bible(text).bibleInfo()
            except:
                print("Could not open Bible " + text)

    def importBible(self, description, abbreviation, verses):
        plainBibleList, formattedBibleList = self.getTwoBibleLists()
        if abbreviation in plainBibleList or abbreviation == "kjvbcv":
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
            self.cursor.execute(query, (abbreviation,))
            table = self.cursor.fetchone()
            if table:
                delete = "DELETE from {0}".format(abbreviation)
                self.cursor.execute(delete)
            else:
                create = "CREATE TABLE {0} (Book INT, Chapter INT, Verse INT, Scripture TEXT)".format(abbreviation)
                self.cursor.execute(create)
            if config.enableBinaryExecutionMode:
                self.cursor.execute("COMMIT")
            insert = "INSERT INTO {0} (Book, Chapter, Verse, Scripture) VALUES (?, ?, ?, ?)".format(abbreviation)
            self.cursor.executemany(insert, verses)
            if config.enableBinaryExecutionMode:
                self.cursor.execute("COMMIT")
        else:
            Bible(abbreviation).importPlainFormat(verses, description)

    def bcvToVerseReference(self, b, c, v, *args, isChapter=False):
        if args:
            return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v, *args, isChapter)
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v, isChapter)

    def getVersesMenu(self, b=config.mainB, c=config.mainC, text=config.mainText):
        verseList = self.getVerseList(b, c, text)
        return " ".join(["{0}{1}</ref>".format(self.formVerseTagMenu(b, c, verse, text), verse) for verse in verseList])

    def formVerseTagMenu(self, b, c, v, text=config.mainText):
        verseReference = self.bcvToVerseReference(b, c, v)
        return "<ref id='v{0}.{1}.{2}' onclick='document.title=\"_menu:::{3}.{0}.{1}.{2}\"' onmouseover='document.title=\"_instantVerse:::{3}:::{0}.{1}.{2}\"' ondblclick='document.title=\"_menu:::{3}.{0}.{1}.{2}\"'>".format(b, c, v, text, verseReference)

    def inputEntered(self, inputID, buttonID):
        return """
<script>
var input = document.getElementById('{2}');
input.addEventListener('keyup', function(event) {0}
  if (event.keyCode === 13) {0}
   event.preventDefault();
   document.getElementById('{3}').click();
  {1}
{1});
</script>""".format("{", "}", inputID, buttonID)

    def formTextTag(self, text=config.mainText):
        return "<ref onclick='document.title=\"_menu:::{0}\"' onmouseover='textName(\"{0}\")'>".format(text)

    def formBookTag(self, b, text=config.mainText):
        bookAbb = self.bcvToVerseReference(b, 1, 1)[:-4]
        return "<ref onclick='document.title=\"_menu:::{0}.{1}\"' onmouseover='bookName(\"{2}\")'>".format(text, b, bookAbb)

    def formChapterTag(self, b, c, text=config.mainText):
        return "<ref onclick='document.title=\"_menu:::{0}.{1}.{2}\"' onmouseover='document.title=\"_info:::Chapter {2}\"'>".format(text, b, c)

    def formVerseTag(self, b, c, v, text=config.mainText):
        verseReference = self.bcvToVerseReference(b, c, v)
        return "<ref id='v{0}.{1}.{2}' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{3}:::{4}\";' onmouseover='document.title=\"_instantVerse:::{3}:::{0}.{1}.{2}\"' ondblclick='document.title=\"_menu:::{3}.{0}.{1}.{2}\"'>".format(b, c, v, text, verseReference)

    def readTextChapter(self, text, b, c):
        plainBibleList, formattedBibleList = self.getTwoBibleLists()
        if text in plainBibleList:
            query = "SELECT * FROM {0} WHERE Book=? AND Chapter=? ORDER BY Verse".format(text)
            self.cursor.execute(query, (b, c))
            textChapter = self.cursor.fetchall()
            if not textChapter:
                return [(b, c, 1, "")]
            # return a list of tuple
            return textChapter
        elif text in formattedBibleList:
            return Bible(text).readTextChapter(b, c)

    def readTextVerse(self, text, b, c, v):
        plainBibleList, formattedBibleList = self.getTwoBibleLists()
        if text in plainBibleList or text == "title":
            query = "SELECT * FROM {0} WHERE Book=? AND Chapter=? AND Verse=?".format(text)
            self.cursor.execute(query, (b, c, v))
            textVerse = self.cursor.fetchone()
            if not textVerse:
                return (b, c, v, "")
            # return a tuple
            return textVerse
        else:
            return Bible(text).readTextVerse(b, c, v)

    def getTexts(self):
        textList = self.getBibleList()
        return " ".join(["{0}<button class='feature'>{1}</button></ref>".format(self.formTextTag(text), text) for text in textList])

    def getBookList(self, text=config.mainText):
        plainBibleList, formattedBibleList = self.getTwoBibleLists()
        if not text in plainBibleList and not text in formattedBibleList:
            if formattedBibleList:
                text = formattedBibleList[0]
            elif plainBibleList:
                text = plainBibleList[0]
        if text in plainBibleList:
            query = "SELECT DISTINCT Book FROM {0} ORDER BY Book".format(text)
            self.cursor.execute(query)
            return [book[0] for book in self.cursor.fetchall() if not book[0] == 0]
        elif text in formattedBibleList:
            return Bible(text).getBookList()

    def getBooks(self, text=config.mainText):
        bookList = self.getBookList(text)
        standardAbbreviation = BibleVerseParser(config.parserStandarisation).standardAbbreviation
        return " ".join(["{0}<button class='feature'>{1}</button></ref>".format(self.formBookTag(book, text), standardAbbreviation[str(book)]) for book in bookList if str(book) in standardAbbreviation])

    def getChapterList(self, b=config.mainB, text=config.mainText):
        plainBibleList, formattedBibleList = self.getTwoBibleLists()
        if not text in plainBibleList and not text in formattedBibleList:
            if formattedBibleList:
                text = formattedBibleList[0]
            elif plainBibleList:
                text = plainBibleList[0]
        if text in plainBibleList:
            query = "SELECT DISTINCT Chapter FROM {0} WHERE Book=? ORDER BY Chapter".format(text)
            self.cursor.execute(query, (b,))
            return [chapter[0] for chapter in self.cursor.fetchall()]
        elif text in formattedBibleList:
            return Bible(text).getChapterList(b)

    def getChapters(self, b=config.mainB, text=config.mainText):
        chapterList = self.getChapterList(b, text)
        return " ".join(["{0}{1}</ref>".format(self.formChapterTag(b, chapter, text), chapter) for chapter in chapterList])

    def getChaptersMenu(self, b=config.mainB, c=config.mainC, text=config.mainText):
        chapterList = self.getChapterList(b, text)
        chaptersMenu = []
        for chapter in chapterList:
            if chapter == c:
                chaptersMenu.append("<b style='font-size: 95%;'>{0}</b>".format(chapter))
            else:
                chaptersMenu.append("{0}{1}</ref>".format(self.formVerseTag(b, chapter, 1, text), chapter))
        return " ".join(chaptersMenu)

    def getChapterSubheadings(self, b, c):
        query = "SELECT * FROM title WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, (b, c))
        return "<br>".join(['<ref onclick="bcv({0},{1},{2})">[{1}:{2}]</ref> {3}'.format(b, c, v, text.replace("<br>", " ")) for b, c, v, text in self.cursor.fetchall()])

    def getVerseList(self, b, c, text=config.mainText, language=""):
        plainBibleList, formattedBibleList = self.getTwoBibleLists()
        if not text in plainBibleList and not text in formattedBibleList:
            if formattedBibleList:
                text = formattedBibleList[0]
            elif plainBibleList:
                text = plainBibleList[0]
        if text in plainBibleList or text in ("kjvbcv", "title"):
            query = "SELECT DISTINCT Verse FROM {0} WHERE Book=? AND Chapter=? ORDER BY Verse".format(text)
            self.cursor.execute(query, (b, c))
            return [verse[0] for verse in self.cursor.fetchall()]
        elif text in formattedBibleList:
            bible = Bible(text)
            return bible.getVerseList(b, c)

    def getVerses(self, b=config.mainB, c=config.mainC, text=config.mainText):
        verseList = self.getVerseList(b, c, text)
        return " ".join(["{0}{1}</ref>".format(self.formVerseTag(b, c, verse, text), verse) for verse in verseList])

    def compareVerse(self, verseList, texts=["ALL"]):
        if len(verseList) == 1 and not texts == ["ALL"]:
            b, c, v, *_ = verseList[0]
            return self.compareVerseChapter(b, c, v, texts)
        else:
            return "".join([self.readTranslations(b, c, v, texts) for b, c, v, *_ in verseList])

    def parallelVerse(self, verseList, texts):
        b, c, v, *_ = verseList[0]
        content = """<h2><ref onclick="document.title='{0}'">{0}</ref></h2>""".format(self.bcvToVerseReference(b, c, v))
        content += "<table>"
        content += "<tr>"
        for text in texts:
            content += "<td><h2>{0}</h2></td>".format(text)
        content += "</tr>"
        for b, c, v, *_ in verseList:
            content += self.readTranslationsAsRow(b, c, v, texts)
        content += "</table>"
        return content

    def diffVerse(self, verseList, texts=["ALL"]):
        if config.isDiffMatchPatchInstalled:
            return "".join([self.readTranslationsDiff(b, c, v, texts) for b, c, v, *_ in verseList])
        else:
            return config.thisTranslation["message_noSupport"]

    def compareVerseChapter(self, b, c, v, texts):
        # get a combined verse list without duplication
        combinedVerseList = [self.getVerseList(b, c, text) for text in texts]
        uniqueVerseList = []
        for verseList in combinedVerseList:
            for verseNo in verseList:
                if not verseNo in uniqueVerseList:
                    uniqueVerseList.append(verseNo)

        chapter = "<h2>{0}</h2><table style='width: 100%;'>".format(self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        for verse in uniqueVerseList:
            row = 0
            for text in texts:
                row = row + 1
                if row % 2 == 0:
                    chapter += "<tr>"
                else:
                    if row == 1:
                        pass
                        #chapter += "<tr style='background-color: {0};'>".format(Themes.getComparisonBackgroundColor())
                    else:
                        pass
                        #chapter += "<tr style='background-color: {0};'>".format(Themes.getComparisonAlternateBackgroundColor())
                if row == 1:
                    chapter += "<td style='vertical-align: text-top;'><vid>{0}{1}</ref></vid> ".format(self.formVerseTag(b, c, verse, text), verse)
                else:
                    chapter += "<td>"
                textTdTag = "<td>"
                if b < 40 and text in config.rtlTexts:
                    textTdTag = "<td style='direction: rtl;'>"
                chapter += "</td><td><sup>({0}{1}</ref>)</sup></td>{2}<bibletext class='{1}'>{3}</bibletext></td></tr>".format(self.formVerseTag(b, c, verse, text), text, textTdTag, self.readTextVerse(text, b, c, verse)[3])
        chapter += "</table>"
        return chapter

    def readTranslations(self, b, c, v, texts):
        plainBibleList, formattedBibleList = self.getTwoBibleLists(False)

        if texts == ["ALL"]:
            texts = plainBibleList + formattedBibleList

        verses = """<h2><ref onclick="document.title='{0}'">{0}</ref></h2>""".format(self.bcvToVerseReference(b, c, v))
        verses += "<table>"
        for text in texts:
            *_, verseText = self.readTextVerse(text, b, c, v)
            if not (verseText == "" and config.hideBlankVerseCompare):
                verses += "<tr>"
                verses += "<td>({0}{1}</ref>)</td>".format(self.formVerseTag(b, c, v, text), text)
                divTag = "<div style='direction: rtl;'>" if b < 40 and text in config.rtlTexts else "<div>"
                verses += "<td><bibleText class='{0}'>{1}{2}</div></bibleText></td>".format(text, divTag, verseText.strip())
                verses += "</tr>"
        verses += "</table>"
        return verses

    def readTranslationsAsRow(self, b, c, v, texts):
        combinedVerseList = [self.getVerseList(b, c, text) for text in texts]
        uniqueVerseList = []
        for verseList in combinedVerseList:
            for verseNo in verseList:
                if not verseNo in uniqueVerseList:
                    uniqueVerseList.append(verseNo)
        content = ""
        for verse in verseList:
            content += "<tr>"
            for text in texts:
                *_, verseText = self.readTextVerse(text, b, c, verse)
                divTag = "<div style='direction: rtl;'>" if b < 40 and text in config.rtlTexts else "<div>"
                ref = "<sup>{0}{1}:{2}</ref></sup> ".format(self.formVerseTag(b, c, verse, text), c, verse)
                verseBlock = "<span id='s{0}.{1}.{2}'>".format(b, c, verse)
                verseBlock += "{0}".format(verseText)
                verseBlock += "</span>"
                content += "<td valign='top'><bibleText class='{0}'>{1}{2}{3}</div></bibleText></td>".format(text, divTag, ref, verseBlock)
            content += "</tr>"
        return content

    def readTranslationsDiff(self, b, c, v, texts):
        plainBibleList, formattedBibleList = self.getTwoBibleLists(False)
        mainText = config.mainText

        if texts == ["ALL"]:
            texts = plainBibleList + formattedBibleList
        if mainText in texts:
            texts.remove(mainText)
        texts.insert(0, mainText)

        verses = "<h2>{0}</h2>".format(self.bcvToVerseReference(b, c, v))
        verses += "<table>"
        from diff_match_patch import diff_match_patch
        dmp = diff_match_patch()
        *_, mainVerseText = self.readTextVerse(mainText, b, c, v)
        mainVerseText = TextUtil.htmlToPlainText(mainVerseText)
        for text in texts:
            verses += "<tr>"
            verses += "<td>({0}{1}</ref>)</td>".format(self.formVerseTag(b, c, v, text), text)
            book, chapter, verse, verseText = self.readTextVerse(text, b, c, v)
            if not text == mainText and not text in config.originalTexts:
                verseText = TextUtil.htmlToPlainText(verseText)
                diff = dmp.diff_main(mainVerseText, verseText)
                verseText = dmp.diff_prettyHtml(diff)
                if config.theme in ("dark", "night"):
                    verseText = self.adjustDarkThemeColorsForDiff(verseText)
            divTag = "<div>"
            if b < 40 and text in config.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            verses += "<td>{0}{1}</div></td>".format(divTag, verseText.strip())
            verses += "</tr>"
        config.mainText = mainText
        verses += "</table>"
        return verses

    def countSearchBible(self, text, searchString, interlinear=False, booksRange=""):
        if text in self.marvelBibles and not text in ["LXX1", "LXX1i", "LXX2", "LXX2i"]:
            searchString = TextUtil.removeVowelAccent(searchString)
            searchString = TextUtil.removeSpecialCharacters(searchString)
        content = "SEARCH:::{0}:::{1}".format(text, searchString)
        if booksRange:
            content += ":::{0}".format(booksRange)
            bookList = BibleVerseParser(config.parserStandarisation).extractBookListAsBookNumberList(booksRange)
        else:
            bookList = self.getBookList(text)
        showCommand = "SEARCHALL"
        searchFunction = "searchBibleBook"
        bookCountList = [self.countSearchBook(text, book, searchString) for book in bookList]
        content += "<p>Total: <ref onclick='document.title=\"{3}:::{1}:::{2}\"'>{0} verse(s)</ref> found in {1}. <ref onclick='document.title=\"SEARCHREFERENCE:::{1}:::{2}\"'>***</ref></p><table><tr><th>Book</th><th>Verse(s)</th></tr>".format(sum(bookCountList), text, searchString, showCommand)
        for counter, bookCount in enumerate(bookCountList):
            book = bookList[counter]
            bookAbb = self.bcvToVerseReference(book, 1, 1)[:-4]
            content += "<tr><td><ref onclick='tbcv(\"{0}\", {1}, 1, 1)' onmouseover='bookName(\"{2}\")'>{2}</ref></td><td><ref onclick='{5}(\"{0}\", \"{1}\", \"{3}\")'>{4}</ref></td></tr>".format(text, book, bookAbb, searchString, bookCount, searchFunction)
        content += "</table>"
        return content

    def countSearchBook(self, text, book, searchString):
        plainBibleList, formattedBibleList = self.getTwoBibleLists()
        if text in plainBibleList:
            query = TextUtil.getQueryPrefix()
            query += "SELECT Verse FROM {0} WHERE Book = ? AND Scripture LIKE ?".format(text)
            t = (book, "%{0}%".format(searchString))
            self.cursor.execute(query, t)
            return len(self.cursor.fetchall())
        elif text in formattedBibleList:
            return Bible(text).countSearchBook(book, searchString)

    def searchBible(self, text, mode, searchString, interlinear=False, referenceOnly=False, booksRange=""):
        if text in self.marvelBibles and not text in ["LXX1", "LXX1i", "LXX2", "LXX2i"]:
            searchString = TextUtil.removeVowelAccent(searchString)
        if not mode == "REGEX":
            searchString = TextUtil.removeSpecialCharacters(searchString)

        plainBibleList, formattedBibleList = self.getTwoBibleLists()

        query = TextUtil.getQueryPrefix()
        formatedText = "<b>{1}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span><br><br>".format(text, config.thisTranslation["html_searchBible2"])
        if text in plainBibleList:
            query += "SELECT * FROM {0}".format(text)
        elif text in formattedBibleList:
            query += "SELECT * FROM Verses"
        query += " WHERE "
        t = tuple()
        if mode == "BASIC":
            if referenceOnly:
                searchCommand = "SEARCHREFERENCE"
            else:
                searchCommand = "SEARCHALL"
            formatedText += "{0}:::<z>{1}</z>:::{2}".format(searchCommand, text, searchString)
            t = ("%{0}%".format(searchString),)
            query += "(Scripture LIKE ?)"
        elif mode == "ADVANCED":
            searchCommand = "ADVANCEDSEARCH"
            formatedText += "{0}:::<z>{1}</z>:::{2}".format(searchCommand, text, searchString)
            query += "({0})".format(searchString)
        elif mode == "REGEX":
            formatedText = "REGEXSEARCH:::<aa>{0}</aa>:::{1}".format(text, searchString)
            t = (searchString,)
            query += "(Scripture REGEXP ?)"
        else:
            query += " 1=1"
        if booksRange:
            query += " AND "
            query += "Book in ({0})".format(BibleVerseParser(config.parserStandarisation).extractBookListAsString(booksRange))
            formatedText += ":::{0}".format(booksRange)
        query += " ORDER BY Book, Chapter, Verse"
        if text in plainBibleList:
            verses = self.getSearchVerses(query, t)
        elif text in formattedBibleList:
            verses = Bible(text).getSearchVerses(query, t)
        # Old way to search fetched result with regular express here
#        if mode == "REGEX":
#            formatedText = "REGEXSEARCH:::<z>{0}</z>:::{1}".format(text, searchString)
#            if booksRange:
#                formatedText += ":::{0}".format(booksRange)
#            verses = [(b, c, v, re.sub("({0})".format(searchString), r"<z>\1</z>", verseText, flags=0 if config.regexCaseSensitive else re.IGNORECASE)) for b, c, v, verseText in verses if re.search(searchString, verseText, flags=0 if config.regexCaseSensitive else re.IGNORECASE)]
        formatedText += "<p>x <b id='searchResultCount' style='color: brown;'>{0}</b> verse(s)</p><p>".format(len(verses))
        if referenceOnly:
            parser = BibleVerseParser(config.parserStandarisation)
            formatedText += "; ".join(["<ref onclick='bcv({0}, {1}, {2})'>{3}</ref>".format(b, c, v, parser.bcvToVerseReference(b, c, v)) for b, c, v, *_ in verses])
        else:
            for verse in verses:
                b, c, v, verseText = verse
                if b < 40 and text in config.rtlTexts:
                    divTag = "<div style='direction: rtl;'>"
                else:
                    divTag = "<div>"
                formatedText += "{0}<span style='color: purple;'>({1}{2}</ref>)</span> {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), self.bcvToVerseReference(b, c, v), verseText.strip())
                if interlinear and not config.favouriteBible == text:
                    if b < 40 and config.favouriteBible in config.rtlTexts:
                        divTag = "<div style='direction: rtl; border: 1px solid gray; border-radius: 2px; margin: 5px; padding: 5px;'>"
                    else:
                        divTag = "<div style='border: 1px solid gray; border-radius: 2px; margin: 5px; padding: 5px;'>"
                    formatedText += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, config.favouriteBible), config.favouriteBible, self.readTextVerse(config.favouriteBible, b, c, v)[3])
            # add highlighting to search string with tags <z>...</z>
            if mode == "REGEX":
                formatedText = TextUtil.highlightSearchString(formatedText, searchString)
            elif mode == "BASIC":
                for eachString in searchString.split("%"):
                    formatedText = TextUtil.highlightSearchString(formatedText, eachString)
            elif mode == "ADVANCED":
                searchWords = [m for m in re.findall("LIKE ['\"]%(.*?)%['\"]", searchString, flags=0 if config.enableCaseSensitiveSearch else re.IGNORECASE)]
                searchWords = [m.split("%") for m in searchWords]
                searchWords = [m2 for m1 in searchWords for m2 in m1]
                for eachString in searchWords:
                    formatedText = TextUtil.highlightSearchString(formatedText, eachString)
            # fix highlighting
            formatedText = TextUtil.fixTextHighlighting(formatedText)
            formatedText += "</p>"
        return formatedText

    def getSearchVerses(self, query, binding):
        self.cursor.execute(query, binding)
        return self.cursor.fetchall()

    def getFavouriteBible(self):
        if config.enableHttpServer and config.webHomePage == "{0}.html".format(config.webPrivateHomePage):
            return config.favouriteBiblePrivate
        elif config.enableHttpServer and config.webHomePage == "traditional.html":
            return config.favouriteBibleTC
        elif config.enableHttpServer and config.webHomePage == "simplified.html":
            return config.favouriteBibleSC
        else:
            return config.favouriteBible

    def getFavouriteBible2(self):
        if config.enableHttpServer and config.webHomePage == "{0}.html".format(config.webPrivateHomePage):
            return config.favouriteBiblePrivate2
        elif config.enableHttpServer and config.webHomePage == "traditional.html":
            return config.favouriteBibleTC2
        elif config.enableHttpServer and config.webHomePage == "simplified.html":
            return config.favouriteBibleSC2
        else:
            return config.favouriteBible2

    def readMultipleVerses(self, inputText, verseList, displayRef=True, presentMode=False):
        verses = ""
        if config.addFavouriteToMultiRef and not presentMode:
            favouriteBible = self.getFavouriteBible()
            if inputText == favouriteBible:
                favouriteBible = self.getFavouriteBible2()
            (fontFile, fontSize, css) = Bible(favouriteBible).getFontInfo()
            config.mainCssBibleFontStyle += css
            textList = [inputText, favouriteBible]
        else:
            textList = [inputText]
        for index, verse in enumerate(verseList):
            for counter, text in enumerate(textList):
                b = verse[0]
                verses += "<div class={0}>".format(text)
                # format opening tag
                if counter == 1 and text == favouriteBible:
                    extraStyle = " border: 1px solid gray; border-radius: 2px; margin: 5px; padding: 5px;"
                else:
                    extraStyle = ""
                if b < 40 and text in config.rtlTexts:
                    divTag = "<div style='direction: rtl;{0}'>".format(extraStyle)
                else:
                    divTag = "<div style='{0}'>".format(extraStyle)
                # format verse text
                verseText = ""
                if len(verse) == 3:
                    b, c, v = verse
                    verseReference = self.bcvToVerseReference(b, c, v)
                    verseText = self.readTextVerse(text, b, c, v)[3].strip()
                    verseText += " "
                elif len(verse) == 4:
                    b, c, vs, ve = verse
                    verseReference = self.bcvToVerseReference(b, c, vs) if vs == ve else "{0}-{1}".format(self.bcvToVerseReference(b, c, vs), ve)
                    v = vs
                    while (v <= ve):
                        if config.showVerseNumbersInRange:
                            verseText += "{0}<vid>{1}</vid></ref> {2}".format(self.formVerseTag(b, c, v, text), v, self.readTextVerse(text, b, c, v)[3].strip())
                        else:
                            verseText += self.readTextVerse(text, b, c, v)[3].strip()
                        verseText += " "
                        v += 1
                    v = vs
                elif len(verse) == 5:
                    b, cs, vs, ce, ve = verse
                    if (cs > ce):
                        pass
                    elif (cs == ce):
                        verseReference = self.bcvToVerseReference(b, cs, vs) if vs == ve else "{0}-{1}".format(self.bcvToVerseReference(b, cs, vs), ve)
                        v = vs
                        while (v <= ve):
                            if config.showVerseNumbersInRange:
                                verseText += "{0}<vid>{1}</vid></ref> {2}".format(self.formVerseTag(b, cs, v, text), v, self.readTextVerse(text, b, cs, v)[3].strip())
                            else:
                                verseText += self.readTextVerse(text, b, cs, v)[3].strip()
                            verseText += " "
                            v += 1
                        c = cs
                        v = vs
                    else:
                        verseReference = "{0}-{1}:{2}".format(self.bcvToVerseReference(b, cs, vs), ce, ve)
                        verseText = ""
                        c = cs
                        v = vs
                        while (self.readTextVerse(text, b, c, v)[3].strip()):
                            if config.showVerseNumbersInRange:
                                verseText += "{0}<vid>{3}:{1}</vid></ref> {2}".format(self.formVerseTag(b, c, v, text), v, self.readTextVerse(text, b, c, v)[3].strip(), c)
                            else:
                                verseText += self.readTextVerse(text, b, c, v)[3].strip()
                            verseText += " "
                            v += 1
                        c += 1
                        while (c < ce):
                            v = 1
                            while (self.readTextVerse(text, b, c, v)[3].strip()):
                                if config.showVerseNumbersInRange:
                                    verseText += "{0}<vid>{3}:{1}</vid></ref> {2}".format(self.formVerseTag(b, c, v, text), v, self.readTextVerse(text, b, c, v)[3].strip(), c)
                                else:
                                    verseText += self.readTextVerse(text, b, c, v)[3].strip()
                                verseText += " "
                                v += 1
                            c += 1
                        v = 1
                        while (v <= ve):
                            if config.showVerseNumbersInRange:
                                verseText += "{0}<vid>{3}:{1}</vid></ref> {2}".format(self.formVerseTag(b, c, v, text), v, self.readTextVerse(text, b, c, v)[3].strip(), c)
                            else:
                                verseText += self.readTextVerse(text, b, c, v)[3].strip()
                            verseText += " "
                            v += 1
                        c = cs
                        v = vs
                if presentMode:
                    verses += "{2} ({0}, {1})".format(verseReference, text, verseText)
                    if index != len(verseList) - 1:
                        verses += "<br><br>"
                elif not displayRef or (counter == 1 and text == favouriteBible):
                    verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), text, verseText)
                else:
                    verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), verseReference, verseText)
                verses += "</div>"
        return verses

    def readPlainChapter(self, text, verse, source):
        # expect verse is a tuple
        b, c, v, *_ = verse
        # format a chapter
        chapter = "<h2>"
        if config.showUserNoteIndicator and not config.enableHttpServer:
            if NoteSqlite().isBookNote(b):
                chapter += '<ref onclick="nB()">&#9998;</ref> '
        chapter += "{0}{1}</ref>".format(self.formChapterTag(b, c, text), self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        # get a verse list of available notes
        noteVerseList = []
        highlightDict = {}
        # add tts indicator
        audioFolder = os.path.join(os.getcwd(), config.audioFolder, "bibles", text, "default", "{0}_{1}".format(b, c))
        if os.path.isdir(audioFolder):
            chapter += ' <ref onclick="rC()">{0}</ref>'.format(config.audioBibleIcon)
        # add note indicator
        if config.showUserNoteIndicator and not config.enableHttpServer:
            noteVerseList = NoteService.getChapterVerseList(b, c)
            if NoteService.isChapterNote(b, c):
                chapter += ' <ref onclick="nC()">&#9998;</ref>'.format(v)
        if config.enableVerseHighlighting:
            highlightDict = Highlight().getVerseDict(b, c)
        readChapter = ""
        if source == "main":
            readChapter = Bible.insertReadBibleLink(text, b, c)
            chapter += readChapter
        chapter += "</h2>"
        titleList = self.getVerseList(b, c, "title")
        verseList = self.readTextChapter(text, b, c)
        for verseTuple in verseList:
            b, c, v, verseText = verseTuple
            divTag = "<div>"
            if b < 40 and text in config.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            if v in titleList and config.addTitleToPlainChapter:
                #if not v == 1:
                #    chapter += "<br>"
                #chapter += "{0}<br>".format(self.readTextVerse("title", b, c, v)[3])
                chapter += self.readTextVerse("title", b, c, v)[3]
            chapter += divTag
            if config.enableVerseHighlighting and config.showHighlightMarkers:
                chapter += '<ref onclick="hiV({0},{1},{2},\'hl1\')" class="ohl1">&#9678;</ref>'.format(b, c, v)
                chapter += '<ref onclick="hiV({0},{1},{2},\'hl2\')" class="ohl2">&#9678;</ref>'.format(b, c, v)
                chapter += '<ref onclick="hiV({0},{1},{2},\'ul1\')" class="oul1">&#9683;</ref>'.format(b, c, v)
            chapter += '<vid id="v{0}.{1}.{2}" onclick="luV({2})" onmouseover="qV({2})" ondblclick="mV({2})">{2}</vid> '.format(b, c, v)
            # add read verse icon
            readVerse = Bible.insertReadBibleLink(text, b, c, v)
            if readVerse:
                chapter += readVerse
            # add note indicator
            if v in noteVerseList:
                chapter += '<ref onclick="nV({0})">&#9998;</ref> '.format(v)
            hlClass = ""
            if v in highlightDict.keys():
                hlClass = " class='{0}'".format(highlightDict[v])
            chapter += "<span id='s{0}.{1}.{2}'{3}>".format(b, c, v, hlClass)
            chapter += "{0}".format(verseText)
            chapter += "</span>"
            chapter += "</div>"
        return chapter

    def migrateDatabaseContent(self):
        if not self.connection is None:
            self.logger.debug("Migrating Bible name to Details table")
            self.migrateFormattedDatabaseContent()
            self.migratePlainDatabaseContent()
            config.migrateDatabaseBibleNameToDetailsTable = False

    def migrateFormattedDatabaseContent(self):
        self.logger.debug("Migrating formatted Bibles")
        bibleList = self.getFormattedBibleList()
        for name in bibleList:
            bible = Bible(name)
            if bible.checkTableExists('Verses'):
                bibleFullname = bible.bibleInfoOld()
                if bibleFullname:
                    if not bible.checkTableExists('Details'):
                        self.logger.debug("Creating " + name)
                        bible.createDetailsTable()
                        bible.insertDetailsTable(bibleFullname, name)
                    else:
                        self.logger.debug("Updating " + name)
                        bible.updateDetailsTable(bibleFullname, name)
                    bible.deleteOldBibleInfo()
                else:
                    self.logger.debug("Already migrated:" + name)
            else:
                self.logger.debug("Verses table does not exist:" + name)

    def migratePlainDatabaseContent(self):
        self.logger.debug("Migrating plain Bibles")
        bibleList = self.getPlainBibleList()
        for name in bibleList:
            bible = Bible(name)
            if bible.checkTableExists('Verses'):
                bibleFullname = bible.bibleInfoOld()
                if bibleFullname:
                    if not bible.checkTableExists('Details'):
                        self.logger.debug("Creating " + name)
                        bible.createDetailsTable()
                        bible.insertDetailsTable(bibleFullname, name)
                    else:
                        self.logger.debug("Updating " + name)
                        bible.updateDetailsTable(bibleFullname, name)
                    bible.deleteOldBibleInfo()
                else:
                    self.logger.debug("Already migrated:" + name)
            else:
                self.logger.debug("Verses table does not exist:" + name)

    def adjustDarkThemeColorsForDiff(self, content):
        content = content.replace("#e6ffe6", "#6b8e6b")
        content = content.replace("#ffe6e6", "#555555")
        return content


class Bible:

    CREATE_DETAILS_TABLE = '''CREATE TABLE IF NOT EXISTS Details (Title NVARCHAR(100), 
                           Abbreviation NVARCHAR(50), Information TEXT, Version INT, OldTestament BOOL,
                           NewTestament BOOL, Apocrypha BOOL, Strongs BOOL, Language NVARCHAR(10),
                           FontSize NVARCHAR(20), FontName NVARCHAR(100))'''

    CREATE_BIBLE_TABLE = "CREATE TABLE Bible (Book INT, Chapter INT, Scripture TEXT)"

    CREATE_VERSES_TABLE = "CREATE TABLE IF NOT EXISTS Verses (Book INT, Chapter INT, Verse INT, Scripture TEXT)"

    CREATE_NOTES_TABLE = "CREATE TABLE Notes (Book INT, Chapter INT, Verse INT, ID TEXT, Note TEXT)"

    CREATE_COMMENTARY_TABLE = "CREATE TABLE Commentary (Book INT, Chapter INT, Scripture TEXT)"

    def __init__(self, text):
        # connect [text].bible
        self.text = text
        self.connection = None
        self.cursor = None
        self.database = os.path.join(config.marvelData, "bibles", text+".bible")
        if os.path.exists(self.database):
            self.connection = dbw.Connection(self.database)
            self.cursor = self.connection.cursor()

    def __del__(self):
        if not self.connection is None:
            if config.enableBinaryExecutionMode:
                self.cursor.execute("COMMIT")
            self.connection.close()

    def bcvToVerseReference(self, b, c, v):
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)

    def getFirstBook(self):
        query = "select min(book) from bible"
        self.cursor.execute(query)
        info = self.cursor.fetchone()
        return info[0]

    def getLastBook(self):
        query = "select max(book) from bible"
        self.cursor.execute(query)
        info = self.cursor.fetchone()
        return info[0]

    def getNextBook(self, book):
        query = "select book from bible where book > ? order by book asc limit 1"
        self.cursor.execute(query, (book,))
        info = self.cursor.fetchone()
        return info[0]

    def getPreviousBook(self, book):
        query = "select book from bible where book < ? order by book desc limit 1"
        self.cursor.execute(query, (book,))
        info = self.cursor.fetchone()
        return info[0]

    def getBookList(self):
        query = "SELECT DISTINCT Book FROM Verses ORDER BY Book"
        self.cursor.execute(query)
        return [book[0] for book in self.cursor.fetchall() if not book[0] == 0]

    def getChapterList(self, b=config.mainB):
        query = "SELECT DISTINCT Chapter FROM Verses WHERE Book=? ORDER BY Chapter"
        self.cursor.execute(query, (b,))
        return [chapter[0] for chapter in self.cursor.fetchall()]

    def getVerseList(self, b, c):
        query = "SELECT DISTINCT Verse FROM Verses WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, (b, c))
        return [verse[0] for verse in self.cursor.fetchall()]

    def bibleInfo(self):
        if self.connection is None:
            return ""
        # It is observed that some files have Details table and some do not.
        try:
            query = "SELECT Title FROM Details limit 1"
            self.cursor.execute(query)
            info = self.cursor.fetchone()
        except:
            try:
                query = "SELECT Scripture FROM Verses WHERE Book=? AND Chapter=? AND Verse=? limit 1"
                self.cursor.execute(query, (0, 0, 0))
                info = self.cursor.fetchone()
            except:
                return self.text
        if info:
            return info[0]
        else:
            return self.text

    def bibleStrong(self):
        # It is observed that some files have Details table and some do not.
        try:
            query = "SELECT Strongs FROM Details limit 1"
            self.cursor.execute(query)
            strong = self.cursor.fetchone()
            if strong:
                return strong[0]
        except:
            return 0

    def getLanguage(self):
        try:
            query = "SELECT Language FROM Details limit 1"
            self.cursor.execute(query)
            info = self.cursor.fetchone()
            if info and info[0] is not None:
                return info[0]
            else:
                return ""
        except:
            return ""

    def getFontInfo(self):
        try:
            query = "SELECT FontName, FontSize FROM Details limit 1"
            self.cursor.execute(query)
            info = self.cursor.fetchone()
            if info:
                fontFile = info[0]
                fontSize = info[1]
                fontFormat = ''
                fontDefinition = ''
                fontSizeFormat = ''
                if fontFile and len(fontFile) > 0:
                    if ".ttf" in fontFile:
                        fontName = fontFile.replace(".ttf", "")
                        fontDefinition = "@font-face {0} font-family: '{1}'; src: url('fonts/{2}') format('truetype'); {3}".format(
                            "{", fontName, fontFile, "}")
                        fontFormat = "font-family: '{0}';".format(fontName)
                    if ".builtin" in fontFile:
                        fontName = fontFile.replace(".builtin", "")
                        fontFormat = "font-family: '{0}';".format(fontName)
                if fontSize and len(fontSize) > 0:
                    fontSizeFormat = "font-size: {0};".format(fontSize)
                css = "{0} .{1} {2} {3} {4} {5}".format(fontDefinition, self.text, "{", fontFormat, fontSizeFormat, "}", )
                return (fontFile, fontSize, css)
            else:
                return ("", "", "")
        except:
            return ("", "", "")

    def bibleInfoOld(self):
        query = "SELECT Scripture FROM Verses WHERE Book=0 AND Chapter=0 AND Verse=0"
        self.cursor.execute(query)
        info = self.cursor.fetchone()
        if info:
            return info[0]
        else:
            return ""

    def formatStrongConcordance(self, strongNo):
        if self.text == "OHGBi":
            return MorphologySqlite().formatConcordance(strongNo)
        lexicalData = LexicalData.getLexicalData(strongNo)
        sNumList = ["[{0}]".format(strongNo)]
        verseHits, snHits, uniqueWdList, verses = Bible(self.text).searchStrongNumber(sNumList)
        html = """<h1>Strong's Concordance - {5}</h1><h2><ref onclick='lex("{0}")'>{0}</ref> x {2} Hit(s) in {1} Verse(s)</h2>{6}<h3>Translation:</h3><p>{3}</p><h3>Verses:</h3><p>{4}</p>""".format(strongNo, verseHits, snHits, " <mbn>|</mbn> ".join(uniqueWdList), "<br>".join(verses), self.text, lexicalData)
        return html

    def searchStrongNumber(self, sNumList):    
        self.cursor.execute('SELECT * FROM Verses')
    
        #csv = ['Idx,Book,Ref.,KJB Verse,KJB Word,Original,Transliteration,Definition']
        csv = []
        wdListAll = []
        verseHits = 0
        snHits = 0

        for b, c, v, vsTxt in self.cursor:
            vsTxt = re.sub("([HG][0-9]+?) ", r" [\1] ", vsTxt)
            vsTxt = re.sub("([HG][0-9]+?)[a-z] ", r" [\1] ", vsTxt)
            
            if any(sn in vsTxt for sn in sNumList):
                vsTxt = re.sub(r'\[\([HG]\d+\)\]', r'', vsTxt)
                vsTxt = re.sub(r'\[\([GH]\d+\)\]|<fn>\d+</fn>|<.+?>|[\r\n]', r'', vsTxt)
                wdGrpList = re.findall(r'[^\]]+\]', vsTxt)
                
                wdList = []
                wdGrpListFix = []
                for wdGrp in wdGrpList:
                    if all(sn not in wdGrp for sn in sNumList):
                        wdGrp = re.sub(r'\[[HG][0-9]+?\]|\[[HG][0-9]+?[a-z]\]', r'', wdGrp)
                    else:
                        wds, *_ = wdGrp.split('[')
                        wdGrp = re.sub(r'(\W?\s?)(.+)', r'\1<z>\2</z>', wdGrp )
                        if wds.strip():
                            wdList.append( '%s' % (re.sub(r'[^\w\s]','', wds).strip()))
                        
                    wdGrpListFix.append(wdGrp)
                
                vsTxtFix = ''.join(wdGrpListFix)
                
                #wdHits = re.findall(r'[^\s]\*\*([^\[]+)', vsTxtFix)
                snHits += len(re.findall(r'\[[GH]\d+\]', vsTxtFix))
                #', '.join(wdList)
                wdListAll += wdList
                
                verseReference = self.bcvToVerseReference(b, c, v)
                line = """<ref onclick="document.title='BIBLE:::{0}'">({0})</ref> {1}""".format(verseReference, vsTxtFix)
                
                csv.append(line)
                verseHits +=1
        
        return (verseHits, snHits, list(set(wdListAll)), csv)

    def importPlainFormat(self, verses, description=""):
        query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
        self.cursor.execute(query, ("Verses",))
        table = self.cursor.fetchone()
        if table:
            delete = "DELETE from Verses"
            self.cursor.execute(delete)
        else:
            create = Bible.CREATE_VERSES_TABLE
            self.cursor.execute(create)
        if config.enableBinaryExecutionMode:
            self.cursor.execute("COMMIT")
        insert = "INSERT INTO Verses (Book, Chapter, Verse, Scripture) VALUES (?, ?, ?, ?)"
        self.cursor.executemany(insert, verses)
        if config.enableBinaryExecutionMode:
            self.cursor.execute("COMMIT")

    def readTextChapter(self, b, c):
        query = "SELECT * FROM Verses WHERE Book=? AND Chapter=? ORDER BY Verse"
        self.cursor.execute(query, (b, c))
        textChapter = self.cursor.fetchall()
        if not textChapter:
            return [(b, c, 1, "")]
        # return a list of tuple
        return textChapter

    def getHighlightedOHGBVerse(self, b, c, v, wordID, showReference=False, linkOnly=False):
        if self.text in ("OHGB", "OHGBi"):
            reference = """(<ref onclick="document.title='BIBLE:::{0}'">{0}</ref>) """.format(self.bcvToVerseReference(b, c, v)) if showReference else ""
            if linkOnly:
                return """{4} [<ref onclick="tbcv('OHGBi', {0}, {1}, {2})" onmouseover="ohgbi({0}, {1}, {2}, {3})">OHGBi</ref>] """.format(b, c, v, wordID, reference)
            else:
                verseText = self.readTextVerse(b, c, v)[-1]
                ohgbi = "<div style='direction: rtl;' class='remarks'>{0}{1}</div>".format(reference, verseText) if b < 40 else "<div class='remarks'>{0}{1}</div>".format(reference, verseText)
                # highlight the matched word
                return re.sub(r"""<(heb|grk)( onclick="w\({0},{1}\)".*?</\1>)""".format(b, wordID), r"<z><\1\2</z>", ohgbi)
        else:
            return ""

    def readTextVerse(self, b, c, v):
        if self.checkTableExists("Verses"):
            query = "SELECT * FROM Verses WHERE Book=? AND Chapter=? AND Verse=?"
            self.cursor.execute(query, (b, c, v))
            textVerse = self.cursor.fetchone()
            if not textVerse:
                return (b, c, v, "")
            # return a tuple
            return textVerse
        else:
            print("Verse table does not exist")
            return (b, c, v, "")

    def readFormattedChapter(self, verse):
        b, c, v, *_ = verse
        biblesSqlite = BiblesSqlite()
        chapter = "<h2>"
        if config.showUserNoteIndicator and not config.enableHttpServer:
            if NoteSqlite().isBookNote(b):
                chapter += '<ref onclick="nB()">&#9998;</ref> '
        chapter += "{0}{1}</ref>".format(biblesSqlite.formChapterTag(b, c, self.text), self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        self.thisVerseNoteList = []
        # add tts indicator
        audioFolder = os.path.join(os.getcwd(), config.audioFolder, "bibles", self.text, "default", "{0}_{1}".format(b, c))
        if os.path.isdir(audioFolder):
            chapter += ' <ref onclick="rC()">{0}</ref>'.format(config.audioBibleIcon)
        # add note indicator
        if config.showUserNoteIndicator and not config.enableHttpServer:
            noteSqlite = NoteSqlite()
            self.thisVerseNoteList = noteSqlite.getChapterVerseList(b, c)
            if noteSqlite.isChapterNote(b, c):
                chapter += ' <ref onclick="nC()">&#9998;</ref>'
        directory = "audio/bibles/{0}/{1}/{2}".format(self.text, "default", b)
        chapter += Bible.insertReadBibleLink(self.text, b, c)
        chapter += "</h2>"
        query = "SELECT Scripture FROM Bible WHERE Book=? AND Chapter=?"
        self.cursor.execute(query, verse[0:2])
        scripture = self.cursor.fetchone()
        if scripture:
            # e.g. <vid id="v1.1.1" onclick="luV(1)">1</vid>
            chapter += re.sub(r'<vid id="v([0-9]+?).([0-9]+?).([0-9]+?)" onclick="luV\([0-9]+?\)"(.*?>.*?</vid>)', self.formatVerseNumber, scripture[0])
            divTag = "<div>"
            if self.text in config.rtlTexts and b < 40:
                divTag = "<div style='direction: rtl;'>"
            chapter = "{0}{1}</div>".format(divTag, chapter)
            if config.enableVerseHighlighting:
                chapter = Highlight().highlightChapter(b, c, chapter)
            return chapter
        else:
            return "<span style='color:gray;'>['{0}' does not contain this chapter.]</span>".format(self.text)

    @staticmethod
    def insertReadBibleLink(text, b, c, v=None):
        text = FileUtil.getMP3TextFile(text)
        data = ""
        if config.runMode == "gui" and config.isVlcInstalled:
            directory = os.path.join(config.audioFolder, "bibles", text)
            if os.path.isdir(directory):
                directories = [d for d in sorted(os.listdir(directory)) if
                               os.path.isdir(os.path.join(directory, d))]
                for index, dir in enumerate(directories):
                    if index > 2:
                        index = 2
                    file = FileUtil.getBibleMP3File(text, b, dir, c, v)
                    if file:
                        icon = config.audioBibleIcon
                        if v is not None:
                            command = "READBIBLE:::{0}:::{1} {2}:{3}:::{4}".format(text, BibleBooks.abbrev["eng"][str(b)][0], c, v, dir)
                        else:
                            command = "READBIBLE:::@{0}".format(dir)
                        data += """ <ref onclick="document.title='{0}'" style="font-size: 1em">{1}</ref> """.format(command, icon)
        return data

    def formatVerseNumber(self, match):
        b, c, v, tagEnding = match.groups()
        verseTag = '<vid id="v{2}.{3}.{0}" onclick="luV({0})" onmouseover="qV({0})" ondblclick="mV({0})"{1}'.format(v, tagEnding, b, c)
        v = int(v)
        # add tts indicator
        audioFolder = os.path.join(os.getcwd(), config.audioFolder, "bibles", self.text, "default", "{0}_{1}".format(b, c))
        audioFilename = os.path.join(audioFolder, "{0}_{1}_{2}_{3}.mp3".format(self.text, b, c, v))
        if os.path.isfile(audioFilename):
            verseTag += ' <ref onclick="rV({0})">{1}</ref> '.format(v, config.audioBibleIcon)
        # add note indicator
        if v in self.thisVerseNoteList:
            verseTag += ' <ref onclick="nV({0})">&#9998;</ref>'.format(v)
        return verseTag

    def readBiblenote(self, bcvi):
        b, c, v, i = bcvi.split(".")
        query = "Select Note FROM Notes WHERE Book=? AND Chapter=? AND Verse=? AND ID=?"
        self.cursor.execute(query, (int(b), int(c), int(v), i))
        note = self.cursor.fetchone()
        if note:
            note = note[0]
        return note

    # apply to LXX1, LXX1i, LXX2, LXX2i, SBLGNT & its variants only
    def readWordNote(self, entry):
        query = "Select content FROM Note WHERE path=?"
        self.cursor.execute(query, (entry,))
        note = self.cursor.fetchone()
        if note:
            note = note[0]
        return note

    def countSearchBook(self, book, searchString):
        query = TextUtil.getQueryPrefix()
        query += "SELECT COUNT(Verse) FROM Verses WHERE Book = ? AND Scripture LIKE ?"
        t = (book, "%{0}%".format(searchString))
        self.cursor.execute(query, t)
        return self.cursor.fetchone()[0]

    def getSearchVerses(self, query, binding):
        self.cursor.execute(query, binding)
        return self.cursor.fetchall()

    def checkTableExists(self, table):
        if self.cursor:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if self.cursor.fetchone():
                return True
            else:
                return False
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

    def addLanguageColumn(self):
        self.addColumnToTable("Details", "Language", "NVARCHAR(10)")

    def addFontNameColumn(self):
        self.addColumnToTable("Details", "FontName", "NVARCHAR(100)")

    def addFontSizeColumn(self):
        self.addColumnToTable("Details", "FontSize", "NVARCHAR(20)")

    def createDetailsTable(self):
        self.cursor.execute(Bible.CREATE_DETAILS_TABLE)

    def createVersesTable(self):
        self.cursor.execute(Bible.CREATE_VERSES_TABLE)

    def insertDetailsTable(self, bibleFullname, bibleAbbrev, language=''):
        sql = ("INSERT INTO Details (Title, Abbreviation, Information, Version, OldTestament, NewTestament,"
               "Apocrypha, Strongs, Language) VALUES (?, ?, '', 1, 1, 1, 0, 0, ?)")
        self.cursor.execute(sql, (bibleFullname, bibleAbbrev, language))

    def updateDetailsTable(self, bibleFullname, bibleAbbrev):
        sql = "UPDATE Details set Title = ?, Abbreviation = ?"
        self.cursor.execute(sql, (bibleFullname, bibleAbbrev))

    def updateTitleAndFontInfo(self, bibleFullname, fontSize, fontName):
        sql = "UPDATE Details set Title = ?, FontSize = ?, FontName = ?"
        self.cursor.execute(sql, (bibleFullname, fontSize, fontName))
        if config.enableBinaryExecutionMode:
            self.cursor.execute("COMMIT")

    def updateLanguage(self, language):
        sql = "UPDATE Details set Language = ?"
        self.cursor.execute(sql, (language,))
        if config.enableBinaryExecutionMode:
            self.cursor.execute("COMMIT")

    def deleteOldBibleInfo(self):
        query = "DELETE FROM Verses WHERE Book=0 AND Chapter=0 AND Verse=0"
        self.cursor.execute(query)

    def getCount(self, table):
        self.cursor.execute('SELECT COUNT(*) from ' + table)
        return self.cursor.fetchone()[0]

    def addMissingColumns(self):
        if not self.checkTableExists("Details"):
            self.createDetailsTable()
        if not self.checkColumnExists("Details", "Language"):
            self.addLanguageColumn()
        if not self.checkColumnExists("Details", "FontSize"):
            self.addFontSizeColumn()
        if not self.checkColumnExists("Details", "FontName"):
            self.addFontNameColumn()
        if self.getCount("Details") == 0:
            self.insertDetailsTable(self.text, self.text)

    def renameGlossToRef(self):
        description = self.bibleInfo()
        self.addMissingColumns()

        query = "SELECT * from Details"
        self.cursor.execute(query)
        details = self.cursor.fetchone()

        query = "SELECT Book, Chapter, Verse, Scripture FROM Verses ORDER BY Book, Chapter, Verse"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        versesData = []
        for record in records:
            scripture = record[3]
            scripture = scripture.replace("<gloss", "<sup><ref")
            scripture = scripture.replace("</gloss>", "</ref></sup>")
            bookNum = record[0]
            chapterNum = record[1]
            verseNum = record[2]
            row = [bookNum, chapterNum, verseNum, scripture]
            versesData.append(row)

        query = "SELECT Book, Chapter, Scripture FROM Bible ORDER BY Book, Chapter"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        bibleData = []
        for record in records:
            scripture = record[2]
            scripture = scripture.replace("<gloss", "<sup><ref")
            scripture = scripture.replace("</gloss>", "</ref></sup>")
            bookNum = record[0]
            chapterNum = record[1]
            row = [bookNum, chapterNum, scripture]
            bibleData.append(row)

        abbreviation = self.text + ".new"
        formattedBible = os.path.join(config.marvelData, "bibles", "{0}.bible".format(abbreviation))
        if os.path.isfile(formattedBible):
            os.remove(formattedBible)
        connection = dbw.Connection(formattedBible)
        cursor = connection.cursor()

        cursor.execute(Bible.CREATE_VERSES_TABLE)
        insert = "INSERT INTO Verses (Book, Chapter, Verse, Scripture) VALUES (?, ?, ?, ?)"
        cursor.executemany(insert, versesData)

        cursor.execute(Bible.CREATE_BIBLE_TABLE)
        insert = "INSERT INTO Bible (Book, Chapter, Scripture) VALUES (?, ?, ?)"
        cursor.executemany(insert, bibleData)

        cursor.execute(Bible.CREATE_DETAILS_TABLE)
        insert = "INSERT INTO Details VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(insert, details)

        if config.enableBinaryExecutionMode:
            self.cursor.execute("COMMIT")


class ClauseData:

    def getContent(self, testament, entry):
        return ClauseONTData(testament).getContent(entry)


class ClauseONTData:

    def __init__(self, testament):
        self.testament = testament
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "data", "clause{0}.data".format(self.testament))
        self.connection = dbw.Connection(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getContent(self, entry):
        query = "SELECT Information FROM {0} WHERE EntryID = ?".format(self.testament)
        self.cursor.execute(query, ("c{0}".format(entry),))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return content[0]


class MorphologySqlite:

    def __init__(self):
        # connect bibles.sqlite
        self.database = os.path.join(config.marvelData, "morphology.sqlite")
        self.connection = dbw.Connection(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def allWords(self, b, c, v):
        query = """
        SELECT WordID, Book, Chapter, Verse, Word, Lexeme FROM morphology WHERE
        Book = {0} AND
        Chapter = {1} AND
        Verse = {2}
        order by Book, Chapter, Verse, WordID
        """.format(b, c, v)
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records

    def bcvToVerseReference(self, b, c, v):
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)

    def formVerseTag(self, b, c, v, text=config.mainText):
        verseReference = self.bcvToVerseReference(b, c, v)
        return "<ref id='v{0}.{1}.{2}' onclick='document.title=\"BIBLE:::{3}:::{4}\"' onmouseover='document.title=\"_instantVerse:::{3}:::{0}.{1}.{2}\"' ondblclick='document.title=\"_menu:::{3}.{0}.{1}.{2}\"'>".format(b, c, v, text, verseReference)

    def readTextVerse(self, text, b, c, v):
        query = "SELECT * FROM {0} WHERE Book=? AND Chapter=? AND Verse=?".format(text)
        self.cursor.execute(query, (b, c, v))
        textVerse = self.cursor.fetchone()
        if not textVerse:
            return (b, c, v, "")
        # return a tuple
        return textVerse

    def instantVerse(self, b, c, v, wordID="", text="interlinear"):
        # Note: Verses drawn from interlinear are suitable to be placed on bottom window, as they have no mouse over feature.
        *_, verseText = self.readTextVerse(text, b, c, v)
        interlinearVerse = """{0}(<ref onclick="document.title='MAIN:::OHGBi:::{1}'">{1}</ref>) {2}</div>""".format("<div style='direction: rtl;'>" if b < 40 else "<div>", self.bcvToVerseReference(b, c, v), verseText)
        if wordID:
            interlinearVerse = re.sub(r"""<(heb|grk)( onclick="w\({0},{1}\)".*?</\1>)""".format(b, wordID), r"<z><\1\2</z>", interlinearVerse)
        return interlinearVerse

    def instantWord(self, book, wordId):
        t = (book, wordId)
        query = "SELECT * FROM morphology WHERE Book = ? AND WordID = ?"
        self.cursor.execute(query, t)
        word = self.cursor.fetchone()
        wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronuciation, interlinear, translation, gloss = word
        morphology = morphology.replace(",", ", ")
        if b < 40:
            textWord = "<heb>{0}</heb>".format(textWord)
            lexeme = "<heb>{0}</heb>".format(lexeme)
        else:
            textWord = "<grk>{0}</grk>".format(textWord)
            lexeme = "<grk>{0}</grk>".format(lexeme)
        return "{0} <transliteration>{1}</transliteration> {2} {3} <e>{4}</e> <esblu>{5}</esblu>".format(textWord, transliteration, lexeme, morphology, interlinear, translation)

    def wordData(self, book, wordId):
        t = (book, wordId)
        query = "SELECT * FROM morphology WHERE Book = ? AND WordID = ?"
        self.cursor.execute(query, t)
        word = self.cursor.fetchone()
        wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronuciation, interlinear, translation, gloss = word
        verseReference = self.bcvToVerseReference(b, c, v)
        firstLexicalEntry = lexicalEntry.split(",")[0]
        lexicalEntryButtons = ""
        for index, entry in enumerate(lexicalEntry[:-1].split(",")):
            if index == 0:
                lexicalEntryButtons += "<button class='feature' onclick='concord(\"{0}\")'>{0}</button>".format(entry)
            else:
                lexicalEntryButtons += " <button class='feature' onclick='lex(\"{0}\")'>{0}</button>".format(entry)
        lexicalEntry = lexicalEntryButtons
        #lexicalEntry = " ".join(["<button class='feature' onclick='lex(\"{0}\")'>{0}</button>".format(entry) for entry in lexicalEntry[:-1].split(",")])
        morphologyCode = "<ref onclick='searchCode(\"{0}\", \"{1}\")'>{1}</ref>".format(firstLexicalEntry, morphologyCode)
        morphology = ", ".join(["<ref onclick='searchMorphologyItem(\"{0}\", \"{1}\")'>{1}</ref>".format(firstLexicalEntry, morphologyItem) for morphologyItem in morphology[:-1].split(",")])
        if b < 40:
            testament = "OT"
            textWord = "<heb>{0}</heb>".format(textWord)
            lexeme = "<ref onclick='searchLexicalEntry(\"{0}\")'><heb>{1}</heb></ref> &ensp;<button class='feature' onclick='lexicon(\"Morphology\", \"{0}\")'>Analytical Lexicon</button>".format(firstLexicalEntry, lexeme)
        else:
            testament = "NT"
            textWord = "<grk>{0}</grk>".format(textWord)
            lexeme = "<ref onclick='searchLexicalEntry(\"{0}\")'><grk>{1}</grk></ref> &ensp;<button class='feature' onclick='lexicon(\"Morphology\", \"{0}\")'>Analytical Lexicon</button>".format(firstLexicalEntry, lexeme)
        clauseContent = ClauseData().getContent(testament, clauseID)
        return ((b, c, v), "<p><button class='feature' onclick='document.title=\"{0}\"'>{0}</button> <button class='feature' onclick='document.title=\"COMPARE:::{0}\"'>Compare</button> <button class='feature' onclick='document.title=\"CROSSREFERENCE:::{0}\"'>X-Ref</button> <button class='feature' onclick='document.title=\"TSKE:::{0}\"'>TSKE</button> <button class='feature' onclick='document.title=\"COMBO:::{0}\"'>TDW</button> <button class='feature' onclick='document.title=\"INDEX:::{0}\"'>Indexes</button></p><div style='border: 1px solid gray; border-radius: 5px; padding: 2px 5px;'>{13}</div><h3>{1} [<transliteration>{2}</transliteration> / <transliteration>{3}</transliteration>]</h3><p><b>Lexeme:</b> {4}<br><b>Morphology code:</b> {5}<br><b>Morphology:</b> {6}<table><tr><th>Gloss</th><th>Interlinear</th><th>Translation</th></tr><tr><td>{7}</td><td>{8}</td><td>{9}</td></tr></table><br>{10} <button class='feature' onclick='lexicon(\"ConcordanceBook\", \"{14}\")'>Concordance [Book]</button> <button class='feature' onclick='lexicon(\"ConcordanceMorphology\", \"{14}\")'>Concordance [Morphology]</button></p>".format(verseReference, textWord, transliteration, pronuciation, lexeme, morphologyCode, morphology, gloss, interlinear, translation, lexicalEntry, clauseID, wordID, clauseContent, firstLexicalEntry))

    def searchWord(self, portion, wordID):
        if portion == "1":
            query = "SELECT Lexeme, LexicalEntry, Morphology FROM morphology WHERE Book < 40 AND WordID = ?"
        else:
            query = "SELECT Lexeme, LexicalEntry, Morphology FROM morphology WHERE Book >= 40 AND WordID = ?"
        t = (wordID,)
        self.cursor.execute(query, t)
        return self.cursor.fetchone()

    def searchByLexicalAndMorphology(self, startBook, endBook, word, morphologyList):
        return self.searchByMorphology(startBook, endBook, "lexicalentry", word, morphologyList)

    def searchByWordAndMorphology(self, startBook, endBook, word, morphologyList):
        return self.searchByMorphology(startBook, endBook, "word", word, morphologyList)

    def searchByGlossAndMorphology(self, startBook, endBook, word, morphologyList):
        return self.searchByMorphology(startBook, endBook, "gloss", word, morphologyList)

    def searchByMorphology(self, startBook, endBook, type, word, morphologyList):
        #references = []
        morphology = ""
        for search in morphologyList:
            morphology += "and morphology LIKE '%{0}%' ".format(search)
        query = TextUtil.getQueryPrefix()
        query += """
        SELECT * FROM morphology WHERE {0} LIKE '%{1}%'
        and book >= {2} and book <= {3}
        {4}
        order by Book, Chapter, Verse
        """.format(type, word, startBook, endBook, morphology)
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return records

    def formatOHGBiVerseText(self, bcv):
        query = "SELECT WordID, Word, LexicalEntry, Interlinear FROM morphology WHERE Book=? AND Chapter=? AND Verse=? ORDER BY WordID"
        self.cursor.execute(query, bcv)
        verseText = """(<ref onclick="document.title='BIBLE:::{0}'">{0}</ref>) """.format(self.bcvToVerseReference(*bcv))
        b = bcv[0]
        for wordID, word, lexicalEntry, interlinear in self.cursor:
            action = ' onclick="w({0},{1})" onmouseover="iw({0},{1})"'.format(b, wordID)
            word = "<heb{1}>{0}</heb>".format(word, action) if b < 40 else "<grk{1}>{0}</grk>".format(word, action)
            interlinear = "<gloss>{0}</gloss>".format(interlinear)
            lexicalEntry = " ".join(["[{0}]".format(entry) for entry in lexicalEntry.split(",") if entry])
            verseText += "{0}{1} {2} ".format(word, interlinear, lexicalEntry)
        return "<div style='direction: rtl;'>{0}</div>".format(verseText) if b < 40 else "<div>{0}</div>".format(verseText)

    def getLexemeData(self, lexicalEntry):
        query = TextUtil.getQueryPrefix()
        query += "SELECT Lexeme FROM morphology WHERE LexicalEntry LIKE ?"
        t = ("%{0},%".format(lexicalEntry),)
        self.cursor.execute(query, t)
        data = self.cursor.fetchone()
        return "<heb>{0}</heb>".format(data[0]) if data is not None else ""            

    def formatConcordance(self, lexicalEntry):
        verses = self.distinctMorphologyVerse(lexicalEntry)
        snHits = len(verses)
        verseHits = len(set([verse[:-1] for verse in verses]))
        ohgbiBible = Bible("OHGBi")
        verses = "".join([ohgbiBible.getHighlightedOHGBVerse(*verse, True, index + 1 > config.maximumOHGBiVersesDisplayedInSearchResult) for index, verse in enumerate(verses)])
        lexicalData = LexicalData.getLexicalData(lexicalEntry)
        literalTranslation = " <mbn>|</mbn> ".join(self.distinctMorphology(lexicalEntry))
        dynamicTranslation = " <mbn>|</mbn> ".join(self.distinctMorphology(lexicalEntry, "Translation"))
        html = """<h1>OHGB Concordance</h1><h2><ref onclick='lex("{0}")'>{0}</ref> x {2} Hit(s) in {1} Verse(s)</h2>{6}<h3>Literal Translation:</h3><p>{3}</p><h3>Dynamic Translation:</h3><p>{5}</p><h3>Verses:</h3><p>{4}</p>""".format(lexicalEntry, verseHits, snHits, literalTranslation, verses, dynamicTranslation, lexicalData)
        return html

    def etcbcLexemeNo2StrongNo(self, lexicalEntry):
        query = TextUtil.getQueryPrefix()
        query += "SELECT DISTINCT LexicalEntry FROM morphology WHERE LexicalEntry LIKE ?"
        t = ("{0},%".format(lexicalEntry),)
        self.cursor.execute(query, t)
        return [strongNo for entry in self.cursor for strongNo in entry[0].split(",") if strongNo.startswith("H")]

    def distinctMorphologyVerse(self, lexicalEntry):
        query = TextUtil.getQueryPrefix()
        query += "SELECT DISTINCT Book, Chapter, Verse, WordID FROM morphology WHERE LexicalEntry LIKE ?"
        t = ("%{0},%".format(lexicalEntry),)
        self.cursor.execute(query, t)
        return self.cursor.fetchall()

    def distinctMorphology(self, lexicalEntry, item="Interlinear"):
        query = TextUtil.getQueryPrefix()
        query += "SELECT DISTINCT {0} FROM morphology WHERE LexicalEntry LIKE ?".format(item)
        t = ("%{0},%".format(lexicalEntry),)
        self.cursor.execute(query, t)
        return list(set([self.simplifyTranslation(translation[0]) for translation in self.cursor if translation[0].strip()]))

    def simplifyTranslation(self, translation):
        translation.strip()
        translation = re.sub(r"^(.+?) \+\[[^\[\]]*?\]$", r"\1", translation)
        translation = re.sub(r"^\+*\[[^\[\]]*?\](.+?)$", r"\1", translation)
        translation = re.sub(r"^(.+?)\[[^\[\]]*?\]\+*$", r"\1", translation)
        translation = re.sub(r"^[^A-Za-z]*?([A-Za-z].*?)[^A-Za-z]*?$", r"\1", translation)
        return translation

    def searchMorphology(self, mode, searchString):
        #import time
        #start = time.time()
        formatedText = ""
        query = TextUtil.getQueryPrefix()
        query += "SELECT * FROM morphology WHERE "
        if mode == "LEMMA":
            formatedText += "<p>LEMMA:::{0}</p>".format(searchString)
            t = ("%{0},%".format(searchString),)
            query += "LexicalEntry LIKE ?"
        elif mode == "MORPHOLOGYCODE":
            formatedText += "<p>MORPHOLOGYCODE:::{0}</p>".format(searchString)
            searchList = searchString.split(',')
            t = ("%{0},%".format(searchList[0]), searchList[1])
            query += "LexicalEntry LIKE ? AND MorphologyCode = ?"
        elif mode == "ADVANCED":
            formatedText += "<p>MORPHOLOGY:::{0}</p>".format(searchString)
            t = ()
            query += searchString
        query += " ORDER BY Book, Chapter, Verse, WordID"
        self.cursor.execute(query, t)
        words = self.cursor.fetchall()
        formatedText += "<p>x <b style='color: brown;'>{0}</b> hits</p>".format(len(words))
        ohgbiInstalled = os.path.isfile(os.path.join(config.marvelData, "bibles", "OHGBi.bible"))
        if config.addOHGBiToMorphologySearch and ohgbiInstalled:
            ohgbiBible = Bible("OHGBi")
        for index, word in enumerate(words):
            #wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronuciation, interlinear, translation, gloss = word
            wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, *_ = word
            firstLexicalEntry = lexicalEntry.split(",")[0]
            textWord = "<{3} onclick='w({1},{2})' onmouseover='iw({1},{2})'>{0}</{3}>".format(textWord, b, wordID, "heb" if b < 40 else "grk")
            formatedText += "<div><span style='color: purple;'>({0}{1}</ref>)</span> {2} <ref onclick='searchCode(\"{4}\", \"{3}\")'>{3}</ref>".format(self.formVerseTag(b, c, v, config.mainText), self.bcvToVerseReference(b, c, v), textWord, morphologyCode, firstLexicalEntry)
            if config.addOHGBiToMorphologySearch and ohgbiInstalled:
                formatedText += ohgbiBible.getHighlightedOHGBVerse(b, c, v, wordID, False, index + 1 > config.maximumOHGBiVersesDisplayedInSearchResult)
            formatedText += "<br></div>"
        #end = time.time()
        #print(end - start)
        return formatedText


if __name__ == '__main__':
    # Bibles = BiblesSqlite()
    #
    # text = "John"
    # verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(text)
    # result = Bibles.readMultipleVerses("KJV", verses)
    # print(result)

    # test search bible - BASIC
    # searchString = input("Search Bible [Basic]\nSearch for: ")
    # print(Bibles.searchBible("NET", "BASIC", searchString))

    # test search bible - ADVANCED
    # e.g. Scripture LIKE '%God%' AND Scripture LIKE '%love%'
    # searchString = input("Search Bible [Advanced]\nFilter for search: ")
    # print(Bibles.searchBible("NET", "ADVANCED", searchString))

    # test search morphology - lexicalEntry
    # e.g. H7225
    # searchString = input("Search Morphology [Lexical Entry]\nSearch for: ")
    # print(Bibles.searchMorphology("LEMMA", searchString))

    # test search morphology - MorphologyCode
    # e.g. E70020,verb.qal.wayq.p1.u.sg
    # searchString = input("Search Morphology [Morphology Code]\nFilter for search: ")
    # print(Bibles.searchMorphology("CODE", searchString))

    # test search morphology - ADVANCED
    # e.g. LexicalEntry LIKE '%E70020,%' AND Morphology LIKE '%third person%' AND (Book = 9 OR Book = 10)
    # searchString = input("Search Morphology [ADVANCED]\nFilter for search: ")
    # print(Bibles.searchMorphology("ADVANCED", searchString))

    # del Bibles

    # bible = Bible("KJVx")
    # bible.renameGlossToRef()
    # print("Done")

    # fileList = glob.glob(config.marvelData+"/bibles/*.bible")
    # for file in fileList:
    #     bible = None
    #     try:
    #         if os.path.isfile(file):
    #             bibleName = Path(file).stem
    #             bible = Bible(bibleName)
    #             description = bible.bibleInfo()
    #             lastBook = bible.getLastBook()
    #             print("{0}:{1}:{2}".format(bibleName, lastBook, description))
    #     except:
    #         print("Error in {0}".format(bible))


    fileList = glob.glob(config.marvelData+"")
    for file in fileList:
        bible = None
        try:
            if os.path.isfile(file):
                bibleName = Path(file).stem
                bible = Bible(bibleName)
                description = bible.bibleInfo()
                lastBook = bible.getLastBook()
                print("{0}:{1}:{2}".format(bibleName, lastBook, description))
        except:
            print("Error in {0}".format(bible))