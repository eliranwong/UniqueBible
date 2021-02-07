"""
Reading data from bibles.sqlite
"""
import os, sqlite3, config, re, logging
from NoteSqlite import NoteSqlite
from BibleVerseParser import BibleVerseParser
from BibleBooks import BibleBooks
from NoteSqlite import NoteSqlite
from db.Highlight import Highlight
from themes import Themes
from util.NoteService import NoteService

try:
    from diff_match_patch import diff_match_patch
except:
    print("Package 'diff_match_patch' is missing.  Read https://github.com/eliranwong/UniqueBible#install-dependencies for guideline on installation.")

class BiblesSqlite:

    def __init__(self):
        # connect bibles.sqlite
        self.database = os.path.join(config.marvelData, "bibles.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        self.marvelBibles = ("MOB", "MIB", "MAB", "MPB", "MTB", "LXX1", "LXX1i", "LXX2", "LXX2i")
        self.logger = logging.getLogger('uba')

    def __del__(self):
        self.connection.close()

    # to-do list
    # sort out download helper

    def getBibleList(self, includeMarvelBibles=True):
        return sorted(self.getPlainBibleList() + self.getFormattedBibleList(includeMarvelBibles))

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
                formattedBible = Bible(bible)
                formattedBible.importPlainFormat(verses)
                del formattedBible
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
                bible = Bible(text)
                info = bible.bibleInfo()
                del bible
                return info
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
            bible = Bible(abbreviation)
            bible.importPlainFormat(verses, description)
            del bible

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
        if source == "main":
            mainVerseReference = parser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
            menu = "<ref onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; {0} - {1}</ref>".format(config.mainText, mainVerseReference)
        elif source == "study":
            mainVerseReference = parser.bcvToVerseReference(config.studyB, config.studyC, config.studyV)
            menu = "<ref onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; {0} - {1}</ref>".format(config.studyText, mainVerseReference)
        # select bible versions
        menu += "<hr><b>{1}</b> {0}".format(self.getTexts(), config.thisTranslation["html_bibles"])
        if text:
            # i.e. text specified; add book menu
            if config.openBibleInMainViewOnly:
                menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> <button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button>".format(text, mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_open"])
            else:
                if source == "main":
                    anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openStudy"])
                elif source == "study":
                    anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openMain"])
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
                    if config.openBibleInMainViewOnly:
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_open"])
                    else:
                        if source == "main":
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_openStudy"])
                        elif source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_openMain"])
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
                    if config.openBibleInMainViewOnly:
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_open"])
                    else:
                        if source == "main":
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_openStudy"])
                        elif source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_openMain"])
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, chapterReference, anotherView, config.thisTranslation["html_openHere"])
                    # overview button
                    overviewButton = "<button class='feature' onclick='document.title=\"OVERVIEW:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_overview"])
                    # chapter index button
                    chapterIndexButton = "<button class='feature' onclick='document.title=\"CHAPTERINDEX:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_chapterIndex"])
                    # summary button
                    summaryButton = "<button class='feature' onclick='document.title=\"SUMMARY:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_summary"])
                    # chapter commentary button
                    chapterCommentaryButton = "<button class='feature' onclick='document.title=\"COMMENTARY:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["menu4_commentary"])
                    # selected chapter
                    menu += "<br><br><b>{3}</b> <span style='color: brown;' onmouseover='document.title=\"_info:::Chapter {1}\"'>{1}</span> {2} <button class='feature' onclick='document.title=\"_openchapternote:::{0}.{1}\"'>{4}</button><br>{5} {6} {7} {8}".format(bookNo, chapterNo, openOption, config.thisTranslation["html_current"], config.thisTranslation["menu6_notes"], overviewButton, chapterIndexButton, summaryButton, chapterCommentaryButton)
                    # building verse list of slected chapter
                    menu += "<hr><b>{1}</b> {0}".format(self.getVerses(bookNo, chapterNo, text), config.thisTranslation["html_verse"])
                if check == 3:
                    verseNo = bcList[2]
                    if config.openBibleInMainViewOnly:
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_open"])
                    else:
                        if source == "main":
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openStudy"])
                        elif source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openMain"])
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, mainVerseReference, anotherView, config.thisTranslation["html_openHere"])
                    menu += "<br><br><b>{5}</b> <span style='color: brown;' onmouseover='document.title=\"_instantVerse:::{0}:::{1}.{2}.{3}\"'>{3}</span> {4} <button class='feature' onclick='document.title=\"_openversenote:::{1}.{2}.{3}\"'>{6}</button>".format(text, bookNo, chapterNo, verseNo, openOption, config.thisTranslation["html_current"], config.thisTranslation["menu6_notes"])
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
            for searchMode in ("SEARCH", "SEARCHREFERENCE", "SHOWSEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH"):
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
            for searchMode in ("SEARCH", "SEARCHREFERENCE", "SHOWSEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH"):
                menu += "<button id='multi{0}' type='button' onclick='checkMultiSearch(\"{0}\");' class='feature'>{0}</button> ".format(searchMode)
            # Perform search when "ENTER" key is pressed
            menu += self.inputEntered("bibleSearch", "SEARCH")
            menu += self.inputEntered("multiBibleSearch", "multiSEARCH")
        return menu

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
        return "<ref id='v{0}.{1}.{2}' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{3}:::{4}\"' onmouseover='document.title=\"_instantVerse:::{3}:::{0}.{1}.{2}\"' ondblclick='document.title=\"_menu:::{3}.{0}.{1}.{2}\"'>".format(b, c, v, text, verseReference)

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
            bible = Bible(text)
            textChapter = bible.readTextChapter(b, c)
            del bible
            return textChapter

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
            bible = Bible(text)
            textVerse = bible.readTextVerse(b, c, v)
            del bible
            return textVerse

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
            bible = Bible(text)
            bookList = bible.getBookList()
            del bible
            return bookList

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
            bible = Bible(text)
            chapterList = bible.getChapterList(b)
            del bible
            return chapterList

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

    def getVerseList(self, b, c, text=config.mainText):
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
            b, c, v = verseList[0]
            return self.compareVerseChapter(b, c, v, texts)
        else:
            return "".join([self.readTranslations(b, c, v, texts) for b, c, v in verseList])

    def diffVerse(self, verseList, texts=["ALL"]):
        return "".join([self.readTranslationsDiff(b, c, v, texts) for b, c, v in verseList])

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
                chapter += "</td><td><sup>({0}{1}</ref>)</sup></td>{2}{3}</td></tr>".format(self.formVerseTag(b, c, verse, text), text, textTdTag, self.readTextVerse(text, b, c, verse)[3])
        chapter += "</table>"
        return chapter

    def readTranslations(self, b, c, v, texts):
        plainBibleList, formattedBibleList = self.getTwoBibleLists(False)

        if texts == ["ALL"]:
            texts = plainBibleList + formattedBibleList

        verses = "<h2>{0}</h2>".format(self.bcvToVerseReference(b, c, v))
        for text in texts:
            book, chapter, verse, verseText = self.readTextVerse(text, b, c, v)
            divTag = "<div>"
            if b < 40 and text in config.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), text, verseText.strip())
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
        try:
            dmp = diff_match_patch()
            *_, mainVerseText = self.readTextVerse(mainText, b, c, v)
            for text in texts:
                book, chapter, verse, verseText = self.readTextVerse(text, b, c, v)
                if not text == mainText and not text in config.originalTexts:
                    diff = dmp.diff_main(mainVerseText, verseText)
                    verseText = dmp.diff_prettyHtml(diff)
                divTag = "<div>"
                if b < 40 and text in config.rtlTexts:
                    divTag = "<div style='direction: rtl;'>"
                verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), text, verseText.strip())
            config.mainText = mainText
            return verses
        except:
            return "Package 'diff_match_patch' is missing.  Read <ref onclick={0}website('https://github.com/eliranwong/UniqueBible#install-dependencies'){0}>https://github.com/eliranwong/UniqueBible#install-dependencies</ref> for guideline on installation.".format('"')

    def removeVowelAccent(self, text):
        searchReplace = (
            (r"[\֑\֒\֓\֔\֕\֖\֗\֘\֙\֚\֛\֜\֝\֞\֟\֠\֡\֣\֤\֥\֦\֧\֨\֩\֪\֫\֬\֭\֮\ֽ\ׄ\ׅ\‍\‪\‬\̣\ְ\ֱ\ֲ\ֳ\ִ\ֵ\ֶ\ַ\ָ\ֹ\ֺ\ֻ\ׂ\ׁ\ּ\ֿ\(\)\[\]\*\־\׀\׃\׆]", ""),
            ("[שׂשׁ]", "ש"),
            ("[ἀἄᾄἂἆἁἅᾅἃάᾴὰᾶᾷᾳ]", "α"),
            ("[ἈἌἎἉἍἋ]", "Α"),
            ("[ἐἔἑἕἓέὲ]", "ε"),
            ("[ἘἜἙἝἛ]", "Ε"),
            ("[ἠἤᾔἢἦᾖᾐἡἥἣἧᾗᾑήῄὴῆῇῃ]", "η"),
            ("[ἨἬἪἮἩἭἫ]", "Η"),
            ("[ἰἴἶἱἵἳἷίὶῖϊΐῒ]", "ι"),
            ("[ἸἼἹἽ]", "Ι"),
            ("[ὀὄὂὁὅὃόὸ]", "ο"),
            ("[ὈὌὉὍὋ]", "Ο"),
            ("[ῥ]", "ρ"),
            ("[Ῥ]", "Ρ"),
            ("[ὐὔὒὖὑὕὓὗύὺῦϋΰῢ]", "υ"),
            ("[ὙὝὟ]", "Υ"),
            ("[ὠὤὢὦᾠὡὥὧᾧώῴὼῶῷῳ]", "ω"),
            ("[ὨὬὪὮὩὭὯ]", "Ω"),
            (r"[\-\—\,\;\:\\\?\.\·\·\‘\’\‹\›\“\”\«\»\(\)\[\]\{\}\⧼\⧽\〈\〉\*\‿\᾽\⇔\¦]", ""),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        return text

    def countSearchBible(self, text, searchString, interlinear=False):
        content = "SEARCH:::{0}:::{1}".format(text, searchString)
        showCommand = "SHOWSEARCH"
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
                searchString = self.removeVowelAccent(searchString)
            bible = Bible(text)
            count = bible.countSearchBook(book, searchString)
            del bible
            return count

    def searchBible(self, text, mode, searchString, interlinear=False, referenceOnly=False):
        if text in self.marvelBibles and not text in ["LXX1", "LXX1i", "LXX2", "LXX2i"]:
                searchString = self.removeVowelAccent(searchString)

        plainBibleList, formattedBibleList = self.getTwoBibleLists()

        formatedText = "<b>{1}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span><br><br>".format(text, config.thisTranslation["html_searchBible2"])
        if text in plainBibleList:
            query = "SELECT * FROM {0} WHERE ".format(text)
        elif text in formattedBibleList:
            query = "SELECT * FROM Verses WHERE "
        if mode == "BASIC":
            if referenceOnly:
                searchCommand = "SEARCHREFERENCE"
            else:
                searchCommand = "SHOWSEARCH"
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
            bible = Bible(text)
            verses = bible.getSearchVerses(query, t)
            del bible
        formatedText += "<p>x <b style='color: brown;'>{0}</b> verse(s)</p>".format(len(verses))
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
            # fix searching LXX / SBLGNT words
            formatedText = re.sub(r"<z>([LS][0-9]+?)</z>'\)"'"'">(.*?)</grk>", r"\1'\)"'"'r"><z>\2</z></grk>", formatedText)
            # remove misplacement of tags <z> & </z>
            p = re.compile("(<[^<>]*?)<z>(.*?)</z>", flags=re.M)
            s = p.search(formatedText)
            while s:
                formatedText = re.sub(p, r"\1\2", formatedText)
                s = p.search(formatedText)
        return formatedText

    def getSearchVerses(self, query, binding):
        self.cursor.execute(query, binding)
        return self.cursor.fetchall()

    def readMultipleVerses(self, inputText, verseList, displayRef=True):
        verses = ""
        if config.addFavouriteToMultiRef and not inputText == config.favouriteBible:
            textList = [inputText, config.favouriteBible]
        else:
            textList = [inputText]
        for verse in verseList:
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
                    verseReference = "{0}-{1}".format(self.bcvToVerseReference(b, c, vs), ve)
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
                        verseReference = "{0}-{1}".format(self.bcvToVerseReference(b, cs, vs), ve)
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
                if not displayRef or (counter == 1 and text == config.favouriteBible):
                    verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), text, verseText)
                else:
                    verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), verseReference, verseText)
        return verses

    def readPlainChapter(self, text, verse):
        # expect verse is a tuple
        b, c, v, *_ = verse
        # format a chapter
        chapter = "<h2>"
        if config.showNoteIndicatorOnBibleChapter:
            noteSqlite = NoteSqlite()
            if noteSqlite.isBookNote(b):
                chapter += '<ref onclick="nB()">&#9997</ref> '
            del noteSqlite
        chapter += "{0}{1}</ref>".format(self.formChapterTag(b, c, text), self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        # get a verse list of available notes
        noteVerseList = []
        highlightDict = {}
        if config.showNoteIndicatorOnBibleChapter:
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
            hlClass = ''
            if v in highlightDict.keys():
                hlClass = " class='" + highlightDict[v] + "'"
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

class Bible:

    CREATE_DETAILS_TABLE = '''CREATE TABLE IF NOT EXISTS Details (Title NVARCHAR(100), 
                           Abbreviation NVARCHAR(50), Information TEXT, Version INT, OldTestament BOOL,
                           NewTestament BOOL, Apocrypha BOOL, Strongs BOOL, Language NVARCHAR(10))'''

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
        query = "SELECT Title FROM Details limit 1"
        self.cursor.execute(query)
        info = self.cursor.fetchone()
        if info:
            return info[0]
        else:
            return ""

    def bibleInfoOld(self):
        query = "SELECT Scripture FROM Verses WHERE Book=0 AND Chapter=0 AND Verse=0"
        self.cursor.execute(query)
        info = self.cursor.fetchone()
        if info:
            return info[0]
        else:
            return ""

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
        if config.showNoteIndicatorOnBibleChapter:
            noteSqlite = NoteSqlite()
            if noteSqlite.isBookNote(b):
                chapter += '<ref onclick="nB()">&#9997</ref> '
            del noteSqlite
        chapter += "{0}{1}</ref>".format(biblesSqlite.formChapterTag(b, c, self.text), biblesSqlite.bcvToVerseReference(b, c, v).split(":", 1)[0])
        del biblesSqlite
        self.thisVerseNoteList = []
        if config.showNoteIndicatorOnBibleChapter:
            noteSqlite = NoteSqlite()
            self.thisVerseNoteList = noteSqlite.getChapterVerseList(b, c)
            if noteSqlite.isChapterNote(b, c):
                chapter += ' <ref onclick="nC()">&#9997</ref>'.format(v)
            del noteSqlite
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
        query = "SELECT Verse FROM Verses WHERE Book = ? AND Scripture LIKE ?"
        t = (book, "%{0}%".format(searchString))
        self.cursor.execute(query, t)
        return len(self.cursor.fetchall())

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

    def deleteOldBibleInfo(self):
        query = "DELETE FROM Verses WHERE Book=0 AND Chapter=0 AND Verse=0"
        self.cursor.execute(query)

    def getCount(self, table):
        self.cursor.execute('SELECT COUNT(*) from ' + table)
        count = self.cursor.fetchone()[0]
        return count

    def fixDatabase(self):
        if not self.checkTableExists("Details"):
            self.createDetailsTable()
        if not self.checkColumnExists("Details", "Language"):
            self.addColumnToTable("Details", "Language", "NVARCHAR(10)")
        if self.getCount("Details") == 0:
            self.insertDetailsTable(self.text, self.text)

class ClauseData:

    def getContent(self, testament, entry):
        clauseData = ClauseONTData(testament)
        content = clauseData.getContent(entry)
        del clauseData
        return content


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

    def instantVerse(self, text, b, c, v):
        interlinearVerse = self.readTextVerse("interlinear", b, c, v)[3]
        if b < 40:
            divTag = "<div style='direction: rtl;'>"
        else:
            divTag = "<div>"
        interlinearVerse = "{0}{1}</div>".format(divTag, interlinearVerse)
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
        return "{0} <span style='color: gray'>{1}</span> {2} {3} <span style='color: brown'>{4}</span> <span style='color: blue'>{5}</span>".format(textWord, transliteration, lexeme, morphology, interlinear, translation)

    def wordData(self, book, wordId):
        t = (book, wordId)
        query = "SELECT * FROM morphology WHERE Book = ? AND WordID = ?"
        self.cursor.execute(query, t)
        word = self.cursor.fetchone()
        wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronuciation, interlinear, translation, gloss = word
        verseReference = self.bcvToVerseReference(b, c, v)
        firstLexicalEntry = lexicalEntry.split(",")[0]
        lexicalEntry = " ".join(["<button class='feature' onclick='lex(\"{0}\")'>{0}</button>".format(entry) for entry in lexicalEntry[:-1].split(",")])
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
        clauseData = ClauseData()
        clauseContent = clauseData.getContent(testament, clauseID)
        del clauseData
        return ((b, c, v), "<p><button class='feature' onclick='document.title=\"{0}\"'>{0}</button> <button class='feature' onclick='document.title=\"COMPARE:::{0}\"'>Compare</button> <button class='feature' onclick='document.title=\"CROSSREFERENCE:::{0}\"'>X-Ref</button> <button class='feature' onclick='document.title=\"TSKE:::{0}\"'>TSKE</button> <button class='feature' onclick='document.title=\"COMBO:::{0}\"'>TDW</button> <button class='feature' onclick='document.title=\"INDEX:::{0}\"'>Indexes</button></p><div style='border: 1px solid gray; border-radius: 5px; padding: 2px 5px;'>{13}</div><h3>{1} [<transliteration>{2}</transliteration> / <transliteration>{3}</transliteration>]</h3><p><b>Lexeme:</b> {4}<br><b>Morphology code:</b> {5}<br><b>Morphology:</b> {6}<table><tr><th>Gloss</th><th>Interlinear</th><th>Translation</th></tr><tr><td>{7}</td><td>{8}</td><td>{9}</td></tr></table><br>{10} <button class='feature' onclick='lexicon(\"ConcordanceBook\", \"{14}\")'>Concordance [Book]</button> <button class='feature' onclick='lexicon(\"ConcordanceMorphology\", \"{14}\")'>Concordance [Morphology]</button></p>".format(verseReference, textWord, transliteration, pronuciation, lexeme, morphologyCode, morphology, gloss, interlinear, translation, lexicalEntry, clauseID, wordID, clauseContent, firstLexicalEntry))

    def searchWord(self, portion, wordID):
        if portion == "1":
            query = "SELECT Lexeme, LexicalEntry, Morphology FROM morphology WHERE Book < 40 AND WordID = ?"
        else:
            query = "SELECT Lexeme, LexicalEntry, Morphology FROM morphology WHERE Book >= 40 AND WordID = ?"
        t = (wordID,)
        self.cursor.execute(query, t)
        return self.cursor.fetchone()

    def searchMorphology(self, mode, searchString):
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
        for word in words:
            wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronuciation, interlinear, translation, gloss = word
            firstLexicalEntry = lexicalEntry.split(",")[0]
            if b < 40:
                textWord = "<heb onclick='w({1},{2})' onmouseover='iw({1},{2})'>{0}</heb>".format(textWord, b, wordID)
            else:
                textWord = "<grk onclick='w({1},{2})' onmouseover='iw({1},{2})'>{0}</grk>".format(textWord, b, wordID)
            formatedText += "<span style='color: purple;'>({0}{1}</ref>)</span> {2} <ref onclick='searchCode(\"{4}\", \"{3}\")'>{3}</ref><br>".format(self.formVerseTag(b, c, v, config.mainText), self.bcvToVerseReference(b, c, v), textWord, morphologyCode, firstLexicalEntry)
        return formatedText


if __name__ == '__main__':
    from Languages import Languages

    config.thisTranslation = Languages.translation
    config.parserStandarisation = 'NO'
    config.standardAbbreviation = 'ENG'
    config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"

    Bibles = BiblesSqlite()

    text = "John"
    verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(text)
    result = Bibles.readMultipleVerses("KJV", verses)
    print(result)

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
