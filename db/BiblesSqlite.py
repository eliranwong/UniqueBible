"""
Reading data from bibles.sqlite
"""
import os, sqlite3, config, re, logging

from util.BibleVerseParser import BibleVerseParser
from util.BibleBooks import BibleBooks
from db.NoteSqlite import NoteSqlite
from db.Highlight import Highlight
from util.themes import Themes
from util.NoteService import NoteService
from util.TextUtil import TextUtil
from util.LexicalData import LexicalData

class BiblesSqlite:

    def __init__(self, language=""):
        # connect bibles.sqlite
        defaultDatabase = os.path.join(config.marvelData, "bibles.sqlite")
        langDatabase = os.path.join(config.marvelData, "bibles_{0}.sqlite".format(language))
        self.database = langDatabase if language and os.path.isfile(langDatabase) else defaultDatabase
        self.connection = sqlite3.connect(self.database)
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
                self.connection.commit()
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
            self.connection.commit()
            insert = "INSERT INTO {0} (Book, Chapter, Verse, Scripture) VALUES (?, ?, ?, ?)".format(abbreviation)
            self.cursor.executemany(insert, verses)
            self.connection.commit()
        else:
            Bible(abbreviation).importPlainFormat(verses, description)

    def bcvToVerseReference(self, b, c, v, *args, isChapter=False):
        if args:
            return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v, *args, isChapter)
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v, isChapter)

    def getMenu(self, command, source="main"):
        parser = BibleVerseParser(config.parserStandarisation)
        items = command.split(".", 3)
        text = items[0]
        versions = self.getBibleList()
        # provide a link to go back the last opened bible verse
        if source == "study":
            mainVerseReference = parser.bcvToVerseReference(config.studyB, config.studyC, config.studyV)
            menu = "<ref onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; {0} - {1}</ref>".format(config.studyText, mainVerseReference)
        else:
            mainVerseReference = parser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
            menu = "<ref onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; {0} - {1}</ref>".format(config.mainText, mainVerseReference)
        # select bible versions
        menu += "<hr><b>{1}</b> {0}".format(self.getTexts(), config.thisTranslation["html_bibles"])
        if text:
            # i.e. text specified; add book menu
            if config.openBibleInMainViewOnly or config.enableHttpServer:
                menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> <button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button>".format(text, mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_open"])
            else:
                if source == "study":
                    anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openMain"])
                else:
                    anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openStudy"])
                menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> <button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {4}".format(text, mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_openHere"], anotherView)
            menu += "<hr><b>{1}</b> {0}".format(self.getBooks(text), config.thisTranslation["html_book"])
            # create a list of inters b, c, v
            bcList = [int(i) for i in items[1:]]
            if bcList:
                check = len(bcList)
                bookNo = bcList[0]
                engFullBookName = BibleBooks().eng[str(bookNo)][-1]
                engFullBookNameWithoutNumber = engFullBookName
                matches = re.match("^[0-9]+? (.*?)$", engFullBookName)
                if matches:
                    engFullBookNameWithoutNumber = matches.group(1)
                # check book name
                #print(engFullBookName)
                if check >= 1:
                    # i.e. book specified; add chapter menu
                    bookReference = parser.bcvToVerseReference(bookNo, 1, 1)
                    bookAbb = bookReference[:-4]
                    # build open book button
                    if config.openBibleInMainViewOnly or config.enableHttpServer:
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, bookReference, anotherView, config.thisTranslation["html_openHere"])
                    # build search book by book introduction button
                    introductionButton = "<button class='feature' onclick='document.title=\"SEARCHBOOKCHAPTER:::Tidwell_The_Bible_Book_by_Book:::{0}\"'>{1}</button>".format(engFullBookName, config.thisTranslation["html_introduction"])
                    # build search timelines button
                    timelinesButton = "<button class='feature' onclick='document.title=\"SEARCHBOOKCHAPTER:::Timelines:::{0}\"'>{1}</button>".format(engFullBookName, config.thisTranslation["html_timelines"])
                    # build search encyclopedia button
                    encyclopediaButton = "<button class='feature' onclick='document.title=\"SEARCHTOOL:::{0}:::{1}\"'>{2}</button>".format(config.encyclopedia, engFullBookNameWithoutNumber, config.thisTranslation["context1_encyclopedia"])
                    # build search dictionary button
                    dictionaryButton = "<button class='feature' onclick='document.title=\"SEARCHTOOL:::{0}:::{1}\"'>{2}</button>".format(config.dictionary, engFullBookNameWithoutNumber, config.thisTranslation["context1_dict"])
                    # display selected book
                    menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='bookName(\"{0}\")'>{0}</span> {1}<br>{3} {4} {5} {6}".format(bookAbb, openOption, config.thisTranslation["html_current"], introductionButton, timelinesButton, dictionaryButton, encyclopediaButton)
                    # add chapter menu
                    menu += "<hr><b>{1}</b> {0}".format(self.getChapters(bookNo, text), config.thisTranslation["html_chapter"])
                if check >= 2:
                    chapterNo = bcList[1]
                    # i.e. both book and chapter specified; add verse menu
                    chapterReference = parser.bcvToVerseReference(bookNo, chapterNo, 1)
                    # build open chapter button
                    if config.openBibleInMainViewOnly or config.enableHttpServer:
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, chapterReference, anotherView, config.thisTranslation["html_openHere"])
                    # overview button
                    overviewButton = "<button class='feature' onclick='document.title=\"OVERVIEW:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_overview"])
                    # chapter index button
                    chapterIndexButton = "<button class='feature' onclick='document.title=\"CHAPTERINDEX:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_chapterIndex"])
                    # summary button
                    summaryButton = "<button class='feature' onclick='document.title=\"SUMMARY:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_summary"])
                    # chapter commentary button
                    chapterCommentaryButton = "<button class='feature' onclick='document.title=\"COMMENTARY:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["menu4_commentary"])
                    # chapter note button
                    chapterNoteButton = " <button class='feature' onclick='document.title=\"_openchapternote:::{0}.{1}\"'>{2}</button>".format(bookNo, chapterNo, config.thisTranslation["menu6_notes"])
                    # selected chapter
                    menu += "<br><br><b>{3}</b> <span style='color: brown;' onmouseover='document.title=\"_info:::Chapter {1}\"'>{1}</span> {2}{4}<br>{5} {6} {7} {8}".format(bookNo, chapterNo, openOption, config.thisTranslation["html_current"], "" if config.enableHttpServer else chapterNoteButton, overviewButton, chapterIndexButton, summaryButton, chapterCommentaryButton)
                    # building verse list of slected chapter
                    menu += "<hr><b>{1}</b> {0}".format(self.getVersesMenu(bookNo, chapterNo, text), config.thisTranslation["html_verse"])
                if check == 3:
                    verseNo = bcList[2]
                    if config.openBibleInMainViewOnly or config.enableHttpServer:
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, mainVerseReference, anotherView, config.thisTranslation["html_openHere"])
                    verseNoteButton = " <button class='feature' onclick='document.title=\"_openversenote:::{0}.{1}.{2}\"'>{3}</button>".format(bookNo, chapterNo, verseNo, config.thisTranslation["menu6_notes"])
                    menu += "<br><br><b>{5}</b> <span style='color: brown;' onmouseover='document.title=\"_instantVerse:::{0}:::{1}.{2}.{3}\"'>{3}</span> {4}{6}".format(text, bookNo, chapterNo, verseNo, openOption, config.thisTranslation["html_current"], "" if config.enableHttpServer else verseNoteButton)
                    #menu += "<hr><b>{0}</b> ".format(config.thisTranslation["html_features"])
                    menu += "<br>"
                    features = (
                        ("COMPARE", config.thisTranslation["menu4_compareAll"]),
                        ("CROSSREFERENCE", config.thisTranslation["menu4_crossRef"]),
                        ("TSKE", config.thisTranslation["menu4_tske"]),
                        ("TRANSLATION", config.thisTranslation["menu4_traslations"]),
                        ("DISCOURSE", config.thisTranslation["menu4_discourse"]),
                        ("WORDS", config.thisTranslation["menu4_words"]),
                        ("COMBO", config.thisTranslation["menu4_tdw"]),
                        ("COMMENTARY", config.thisTranslation["menu4_commentary"]),
                        ("INDEX", config.thisTranslation["menu4_indexes"]),
                    )
                    for keyword, description in features:
                        menu += "<button class='feature' onclick='document.title=\"{0}:::{1}\"'>{2}</button> ".format(keyword, mainVerseReference, description)
                    #versions = self.getBibleList()
                    # Compare menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='compare{0}'></div> ".format(version)
                            menu += "<script>versionList.push('{0}');</script>".format(version)
                    menu += "<br><button type='button' onclick='checkCompare();' class='feature'>{0}</button>".format(config.thisTranslation["html_showCompare"])
                    # Parallel menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='parallel{0}'></div> ".format(version)
                    menu += "<br><button type='button' onclick='checkParallel();' class='feature'>{0}</button>".format(config.thisTranslation["html_showParallel"])
                    # Diff menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='diff{0}'></div> ".format(version)
                    menu += "<br><button type='button' onclick='checkDiff();' class='feature'>{0}</button>".format(config.thisTranslation["html_showDifference"])
        else:
            # menu - Search a bible
            if source == "study":
                defaultSearchText = config.studyText
            else:
                defaultSearchText = config.mainText
            menu += "<hr><b>{1}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span>".format(defaultSearchText, config.thisTranslation["html_searchBible2"])
            menu += "<br><br><input type='text' id='bibleSearch' style='width:95%' autofocus><br><br>"
            searchOptions = ("SEARCH", "SEARCHREFERENCE", "SEARCHOT", "SEARCHNT", "SEARCHALL", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
            for searchMode in searchOptions:
                menu += "<button  id='{0}' type='button' onclick='checkSearch(\"{0}\", \"{1}\");' class='feature'>{0}</button> ".format(searchMode, defaultSearchText)
            # menu - Search multiple bibles
            menu += "<hr><b>{0}</b> ".format(config.thisTranslation["html_searchBibles2"])
            for version in versions:
                if version == defaultSearchText or version == config.favouriteBible:
                    menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='search{0}' checked></div> ".format(version)
                else:
                    menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='search{0}'></div> ".format(version)
                menu += "<script>versionList.push('{0}');</script>".format(version)
            menu += "<br><br><input type='text' id='multiBibleSearch' style='width:95%'><br><br>"
            for searchMode in searchOptions:
                menu += "<button id='multi{0}' type='button' onclick='checkMultiSearch(\"{0}\");' class='feature'>{0}</button> ".format(searchMode)
            # Perform search when "ENTER" key is pressed
            menu += self.inputEntered("bibleSearch", "SEARCH")
            menu += self.inputEntered("multiBibleSearch", "multiSEARCH")
        return menu

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
                        chapter += "<tr style='background-color: {0};'>".format(Themes.getComparisonBackgroundColor())
                    else:
                        chapter += "<tr style='background-color: {0};'>".format(Themes.getComparisonAlternateBackgroundColor())
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
        for text in texts:
            verses += "<tr>"
            verses += "<td>({0}{1}</ref>)</td>".format(self.formVerseTag(b, c, v, text), text)
            book, chapter, verse, verseText = self.readTextVerse(text, b, c, v)
            if not text == mainText and not text in config.originalTexts:
                diff = dmp.diff_main(mainVerseText, verseText)
                verseText = dmp.diff_prettyHtml(diff)
                if config.theme == "dark":
                    verseText = self.adjustDarkThemeColorsForDiff(verseText)
            divTag = "<div>"
            if b < 40 and text in config.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            verses += "<td>{0}{1}</div></td>".format(divTag, verseText.strip())
            verses += "</tr>"
        config.mainText = mainText
        verses += "</table>"
        return verses

    def countSearchBible(self, text, searchString, interlinear=False):
        content = "SEARCH:::{0}:::{1}".format(text, searchString)
        showCommand = "SEARCHALL"
        searchFunction = "searchBibleBook"
        bookList = self.getBookList(text)
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
            query = "SELECT Verse FROM {0} WHERE Book = ? AND Scripture LIKE ?".format(text)
            t = (book, "%{0}%".format(searchString))
            self.cursor.execute(query, t)
            return len(self.cursor.fetchall())
        elif text in formattedBibleList:
            if text in self.marvelBibles and not text in ["LXX1", "LXX1i", "LXX2", "LXX2i"]:
                searchString = TextUtil.removeVowelAccent(searchString)
            return Bible(text).countSearchBook(book, searchString)

    def searchBible(self, text, mode, searchString, interlinear=False, referenceOnly=False):
        if text in self.marvelBibles and not text in ["LXX1", "LXX1i", "LXX2", "LXX2i"]:
                searchString = TextUtil.removeVowelAccent(searchString)

        plainBibleList, formattedBibleList = self.getTwoBibleLists()

        formatedText = "<b>{1}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span><br><br>".format(text, config.thisTranslation["html_searchBible2"])
        if text in plainBibleList:
            query = "SELECT * FROM {0}".format(text)
        elif text in formattedBibleList:
            query = "SELECT * FROM Verses"
        if not mode == "REGEX":
            query += " WHERE "
        else:
            t = ()
        if mode == "BASIC":
            if referenceOnly:
                searchCommand = "SEARCHREFERENCE"
            else:
                searchCommand = "SEARCHALL"
            formatedText += "{0}:::<z>{1}</z>:::{2}".format(searchCommand, text, searchString)
            t = ("%{0}%".format(searchString),)
            query += "Scripture LIKE ?"
        elif mode == "ADVANCED":
            t = tuple()
            searchCommand = "ADVANCEDSEARCH"
            formatedText += "{0}:::<z>{1}</z>:::{2}".format(searchCommand, text, searchString)
            query += searchString
        query += " ORDER BY Book, Chapter, Verse"
        if text in plainBibleList:
            verses = self.getSearchVerses(query, t)
        elif text in formattedBibleList:
            verses = Bible(text).getSearchVerses(query, t)
        # Search fetched result with regular express here
        if mode == "REGEX":
            formatedText += "REGEXSEARCH:::<z>{0}</z>:::{1}".format(text, searchString)
            verses = [(b, c, v, re.sub("({0})".format(searchString), r"<z>\1</z>", verseText, flags=0 if config.regexCaseSensitive else re.IGNORECASE)) for b, c, v, verseText in verses if re.search(searchString, verseText, flags=0 if config.regexCaseSensitive else re.IGNORECASE)]
        formatedText += "<p>x <b style='color: brown;'>{0}</b> verse(s)</p><p>".format(len(verses))
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
            if mode == "BASIC" and not searchString == "z":
                for searchWord in searchString.split("%"):
                    formatedText = re.sub("("+searchWord+")", r"<z>\1</z>", formatedText, flags=re.IGNORECASE)
            elif mode == "ADVANCED":
                searchWords = [m for m in re.findall("LIKE ['\"]%(.*?)%['\"]", searchString, flags=re.IGNORECASE)]
                searchWords = [m.split("%") for m in searchWords]
                searchWords = [m2 for m1 in searchWords for m2 in m1]
                for searchword in searchWords:
                    if not searchword == "z":
                        formatedText = re.sub("("+searchword+")", r"<z>\1</z>", formatedText, flags=re.IGNORECASE)
            # fix highlighting
            formatedText = TextUtil.fixTextHighlighting(formatedText)
            formatedText += "</p>"
        return formatedText

    def getSearchVerses(self, query, binding):
        self.cursor.execute(query, binding)
        return self.cursor.fetchall()

    def readMultipleVerses(self, inputText, verseList, displayRef=True, presentMode=False):
        verses = ""
        if config.addFavouriteToMultiRef and not inputText == config.favouriteBible and not presentMode:
            textList = [inputText, config.favouriteBible]
        else:
            textList = [inputText]
        for index, verse in enumerate(verseList):
            for counter, text in enumerate(textList):
                b = verse[0]
                # format opening tag
                if counter == 1 and text == config.favouriteBible:
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
                elif not displayRef or (counter == 1 and text == config.favouriteBible):
                    verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), text, verseText)
                else:
                    verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), verseReference, verseText)
        return verses

    def readPlainChapter(self, text, verse):
        # expect verse is a tuple
        b, c, v, *_ = verse
        # format a chapter
        chapter = "<h2>"
        if config.showNoteIndicatorOnBibleChapter and not config.enableHttpServer:
            if NoteSqlite().isBookNote(b):
                chapter += '<ref onclick="nB()">&#9997</ref> '
        chapter += "{0}{1}</ref>".format(self.formChapterTag(b, c, text), self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        # get a verse list of available notes
        noteVerseList = []
        highlightDict = {}
        if config.showNoteIndicatorOnBibleChapter and not config.enableHttpServer:
            noteVerseList = NoteService.getChapterVerseList(b, c)
            if NoteService.isChapterNote(b, c):
                chapter += ' <ref onclick="nC()">&#9997</ref>'.format(v)
        if config.enableVerseHighlighting:
            highlightDict = Highlight().getVerseDict(b, c)
        chapter += "</h2>"
        titleList = self.getVerseList(b, c, "title")
        verseList = self.readTextChapter(text, b, c)
        for verseTuple in verseList:
            b, c, v, verseText = verseTuple
            divTag = "<div>"
            if b < 40 and text in config.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            if v in titleList and config.addTitleToPlainChapter:
                if not v == 1:
                    chapter += "<br>"
                chapter += "{0}<br>".format(self.readTextVerse("title", b, c, v)[3])
            chapter += divTag
            if config.enableVerseHighlighting and config.showHighlightMarkers:
                chapter += '<ref onclick="hiV({0},{1},{2},\'hl1\')" class="ohl1">&#9678;</ref>'.format(b, c, v)
                chapter += '<ref onclick="hiV({0},{1},{2},\'hl2\')" class="ohl2">&#9678;</ref>'.format(b, c, v)
                chapter += '<ref onclick="hiV({0},{1},{2},\'ul1\')" class="oul1">&#9683;</ref>'.format(b, c, v)
            chapter += '<vid id="v{0}.{1}.{2}" onclick="luV({2})" onmouseover="qV({2})" ondblclick="mV({2})">{2}</vid> '.format(b, c, v)
            # add note indicator
            if v in noteVerseList:
                chapter += '<ref onclick="nV({0})">&#9997</ref> '.format(v)
            hlClass = ""
            if v in highlightDict.keys():
                hlClass = " class='{0}'".format(highlightDict[v])
            chapter += "<span id='s{0}.{1}.{2}'{3}>".format(b, c, v, hlClass)
            chapter += "{0}".format(verseText)
            chapter += "</span>"
            chapter += "</div>"
        return chapter

    def migrateDatabaseContent(self):
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
        self.database = os.path.join(config.marvelData, "bibles", text+".bible")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.commit()
        self.connection.close()

    def bcvToVerseReference(self, b, c, v):
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)

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
        self.connection.commit()
        insert = "INSERT INTO Verses (Book, Chapter, Verse, Scripture) VALUES (?, ?, ?, ?)"
        self.cursor.executemany(insert, verses)
        self.connection.commit()

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
        if config.showNoteIndicatorOnBibleChapter and not config.enableHttpServer:
            if NoteSqlite().isBookNote(b):
                chapter += '<ref onclick="nB()">&#9997</ref> '
        chapter += "{0}{1}</ref>".format(biblesSqlite.formChapterTag(b, c, self.text), self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        self.thisVerseNoteList = []
        if config.showNoteIndicatorOnBibleChapter and not config.enableHttpServer:
            noteSqlite = NoteSqlite()
            self.thisVerseNoteList = noteSqlite.getChapterVerseList(b, c)
            if noteSqlite.isChapterNote(b, c):
                chapter += ' <ref onclick="nC()">&#9997</ref>'.format(v)
        chapter += "</h2>"
        query = "SELECT Scripture FROM Bible WHERE Book=? AND Chapter=?"
        self.cursor.execute(query, verse[0:2])
        scripture = self.cursor.fetchone()
        if scripture:
            chapter += re.sub(r'onclick="luV\(([0-9]+?)\)"(.*?>.*?</vid>)', self.formatVerseNumber, scripture[0])
            divTag = "<div>"
            if self.text in config.rtlTexts and b < 40:
                divTag = "<div style='direction: rtl;'>"
            chapter = "{0}{1}</div>".format(divTag, chapter)
            if config.enableVerseHighlighting:
                chapter = Highlight().highlightChapter(b, c, chapter)
            return chapter
        else:
            return "<span style='color:gray;'>['{0}' does not contain this chapter.]</span>".format(self.text)

    def formatVerseNumber(self, match):
        v, tagEnding = match.groups()
        verseTag = 'onclick="luV({0})" onmouseover="qV({0})" ondblclick="mV({0})"{1}'.format(v, tagEnding)
        v = int(v)
        if v in self.thisVerseNoteList:
            verseTag += ' <ref onclick="nV({0})">&#9997</ref>'.format(v)
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
        query = "SELECT COUNT(Verse) FROM Verses WHERE Book = ? AND Scripture LIKE ?"
        t = (book, "%{0}%".format(searchString))
        self.cursor.execute(query, t)
        return self.cursor.fetchone()[0]

    def getSearchVerses(self, query, binding):
        self.cursor.execute(query, binding)
        return self.cursor.fetchall()

    def checkTableExists(self, table):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        if self.cursor.fetchone():
            return True
        else:
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
        self.connection.commit()

    def updateLanguage(self, language):
        sql = "UPDATE Details set Language = ?"
        self.cursor.execute(sql, (language,))
        self.connection.commit()

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
        connection = sqlite3.connect(formattedBible)
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

        connection.commit()


class ClauseData:

    def getContent(self, testament, entry):
        return ClauseONTData(testament).getContent(entry)


class ClauseONTData:

    def __init__(self, testament):
        self.testament = testament
        # connect images.sqlite
        self.database = os.path.join(config.marvelData, "data", "clause{0}.data".format(self.testament))
        self.connection = sqlite3.connect(self.database)
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
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

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
        query = "SELECT Lexeme FROM morphology WHERE LexicalEntry LIKE ?"
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
        query = "SELECT DISTINCT LexicalEntry FROM morphology WHERE LexicalEntry LIKE ?"
        t = ("{0},%".format(lexicalEntry),)
        self.cursor.execute(query, t)
        return [strongNo for entry in self.cursor for strongNo in entry[0].split(",") if strongNo.startswith("H")]

    def distinctMorphologyVerse(self, lexicalEntry):
        query = "SELECT DISTINCT Book, Chapter, Verse, WordID FROM morphology WHERE LexicalEntry LIKE ?"
        t = ("%{0},%".format(lexicalEntry),)
        self.cursor.execute(query, t)
        return self.cursor.fetchall()

    def distinctMorphology(self, lexicalEntry, item="Interlinear"):
        query = "SELECT DISTINCT {0} FROM morphology WHERE LexicalEntry LIKE ?".format(item)
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
        query = "SELECT * FROM morphology WHERE "
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
            formatedText += "<span style='color: purple;'>({0}{1}</ref>)</span> {2} <ref onclick='searchCode(\"{4}\", \"{3}\")'>{3}</ref>".format(self.formVerseTag(b, c, v, config.mainText), self.bcvToVerseReference(b, c, v), textWord, morphologyCode, firstLexicalEntry)
            if config.addOHGBiToMorphologySearch and ohgbiInstalled:
                formatedText += ohgbiBible.getHighlightedOHGBVerse(b, c, v, wordID, False, index + 1 > config.maximumOHGBiVersesDisplayedInSearchResult)
            formatedText += "<br>"
        #end = time.time()
        #print(end - start)
        return formatedText


if __name__ == '__main__':
    # config.thisTranslation = Languages.translation
    # config.parserStandarisation = 'NO'
    # config.standardAbbreviation = 'ENG'
    # config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"
    #
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

    # fileList = glob.glob(config.marvelData+"/bibles/*.bible")
    # for file in fileList:
    #     if os.path.isfile(file):
    #         bibleName = Path(file).stem
    #         bible = Bible(bibleName)
    #         description = bible.bibleInfo()
    #         print("{0}:{1}".format(bibleName, description))

    bible = Bible("KJVx")
    bible.renameGlossToRef()
    print("Done")