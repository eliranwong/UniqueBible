"""
Reading data from bibles.sqlite
"""
import os, sqlite3, config, re
from BibleVerseParser import BibleVerseParser

class BiblesSqlite:

    def __init__(self):
        # connect bibles.sqlite
        self.database = os.path.join("marvelData", "bibles.sqlite")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        self.rtlTexts = ["original", "MOB", "MAB", "MTB", "MIB", "MPB", "OHGB", "OHGBi"]

    def __del__(self):
        self.connection.close()

    def bibleInfo(self, text):
        query = "SELECT Scripture FROM {0} WHERE Book=0 AND Chapter=0 AND Verse=0".format(text)
        self.cursor.execute(query)
        info = self.cursor.fetchone()
        if info:
            return info[0]
        else:
            return ""

    def importBible(self, description, abbreviation, verses):
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
        verses.append((0, 0, 0, description))
        insert = "INSERT INTO {0} (Book, Chapter, Verse, Scripture) VALUES (?, ?, ?, ?)".format(abbreviation)
        self.cursor.executemany(insert, verses)
        self.connection.commit()

    def bcvToVerseReference(self, b, c, v):
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)

    def getMenu(self, command, source="main"):
        if source == "main":
            mainVerseReference = self.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
            menu = "<ref onclick='document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; Go to {0} - {1}</ref>".format(config.mainText, mainVerseReference)
        elif source == "study":
            mainVerseReference = self.bcvToVerseReference(config.studyB, config.studyC, config.studyV)
            menu = "<ref onclick='document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; Go to {0} - {1}</ref>".format(config.studyText, mainVerseReference)
        menu += "<hr><b>Bibles:</b> {0}".format(self.getTexts())
        items = command.split(".", 3)
        text = items[0]
        if not text == "":
            # i.e. text specified; add book menu
            menu += "<hr><b>Selected Bible:</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> <button class='feature' onclick='document.title=\"BIBLE:::{0}:::{1}\"'>open {1} in {0}</button>".format(text, mainVerseReference)
            menu += "<hr><b>Books:</b> {0}".format(self.getBooks(text))
            bcList = [int(i) for i in items[1:]]
            if bcList:
                check = len(bcList)
                if check >= 1:
                    # i.e. book specified; add chapter menu
                    menu += "<hr><b>Selected book:</b> <span style='color: brown;' onmouseover='bookName(\"{0}\")'>{0}</span>".format(self.bcvToVerseReference(bcList[0], 1, 1)[:-4])
                    menu += "<hr><b>Chapters:</b> {0}".format(self.getChapters(bcList[0], text))
                if check >= 2:
                    # i.e. both book and chapter specified; add verse menu
                    menu += "<hr><b>Selected chapter:</b> <span style='color: brown;' onmouseover='document.title=\"_info:::Chapter {1}\"'>{1}</span> <button class='feature' onclick='document.title=\"_openchapternote:::{0}.{1}\"'>chapter note</button>".format(bcList[0], bcList[1])
                    menu += "<hr><b>Verses:</b> {0}".format(self.getVerses(bcList[0], bcList[1], text))
                if check == 3:
                    if source == "main":
                        anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>go to left view</button>".format(text, mainVerseReference)
                    elif source == "study":
                        anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>go to right view</button>".format(text, mainVerseReference)
                    menu += "<hr><b>Selected verse:</b> <span style='color: brown;' onmouseover='document.title=\"_instantVerse:::{0}:::{1}.{2}.{3}\"'>{3}</span> <button class='feature' onclick='document.title=\"BIBLE:::{0}:::{4}\"'>open HERE</button> {5} <button class='feature' onclick='document.title=\"_openversenote:::{1}.{2}.{3}\"'>verse note</button>".format(text, bcList[0], bcList[1], bcList[2], mainVerseReference, anotherView)
                    menu += "<hr><b>Special Features:</b><br>"
                    features = (
                        ("COMPARE", "Compare All Versions"),
                        ("CROSSREFERENCE", "Cross References"),
                        ("TSKE", "TSK (Enhanced)"),
                        ("TRANSLATION", "Translations"),
                        ("DISCOURSE", "Discourse"),
                        ("WORDS", "Words"),
                        ("COMBO", "TDW Combo"),
                        ("COMMENTARY", "Commentary"),
                        ("INDEX", "Smart Indexes"),
                    )
                    for keyword, description in features:
                        menu += "<button class='feature' onclick='document.title=\"{0}:::{1}\"'>{2}</button> ".format(keyword, mainVerseReference, description)
                    versions = self.getBibleList()
                    menu += "<hr><b>Compare <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> with:</b><br>".format(text)
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='compare{0}'></div> ".format(version)
                            menu += "<script>versionList.push('{0}');</script>".format(version)
                    menu += "<br><button type='button' onclick='checkCompare();' class='feature'>Start Comparison</button>"
                    menu += "<hr><b>Parallel <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> with:</b><br>".format(text)
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='parallel{0}'></div> ".format(version)
                    menu += "<br><button type='button' onclick='checkParallel();' class='feature'>Start Parallel Reading</button>"
        return menu

    def formTextTag(self, text=config.mainText):
        return "<ref onclick='document.title=\"_menu:::{0}\"' onmouseover='textName(\"{0}\")'>".format(text)

    def formBookTag(self, b, text=config.mainText):
        bookAbb = self.bcvToVerseReference(b, 1, 1)[:-4]
        return "<ref onclick='document.title=\"_menu:::{0}.{1}\"' onmouseover='bookName(\"{2}\")'>".format(text, b, bookAbb)

    def formChapterTag(self, b, c, text=config.mainText):
        return "<ref onclick='document.title=\"_menu:::{0}.{1}.{2}\"' onmouseover='document.title=\"_info:::Chapter {2}\"'>".format(text, b, c)

    def formVerseTag(self, b, c, v, text=config.mainText):
        verseReference = self.bcvToVerseReference(b, c, v)
        return "<ref id='v{0}.{1}.{2}' onclick='document.title=\"BIBLE:::{3}:::{4}\"' onmouseover='document.title=\"_instantVerse:::{3}:::{0}.{1}.{2}\"' ondblclick='document.title=\"_menu:::{3}.{0}.{1}.{2}\"'>".format(b, c, v, text, verseReference)

    def readTextChapter(self, text, b, c):
        query = "SELECT * FROM {0} WHERE Book=? AND Chapter=? ORDER BY Verse".format(text)
        self.cursor.execute(query, (b, c))
        textChapter = self.cursor.fetchall()
        if not textChapter:
            return [(b, c, 1, "")]
        # return a list of tuple
        return textChapter

    def readTextVerse(self, text, b, c, v):
        query = "SELECT * FROM {0} WHERE Book=? AND Chapter=? AND Verse=?".format(text)
        self.cursor.execute(query, (b, c, v))
        textVerse = self.cursor.fetchone()
        if not textVerse:
            return (b, c, v, "")
        # return a tuple
        return textVerse

    def getBibleList(self):
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        self.cursor.execute(query, ("table",))
        versions = self.cursor.fetchall()
        exclude = ("Details", "lexicalEntry", "morphology", "original", "title", "interlinear")
        return [version[0] for version in versions if not version[0] in exclude]

    def getTexts(self):
        textList = self.getBibleList()
        return " ".join(["{0}<button class='feature'>{1}</button></ref>".format(self.formTextTag(text), text) for text in textList])

    def getBookList(self, text=config.mainText):
        query = "SELECT DISTINCT Book FROM {0} ORDER BY Book".format(text)
        self.cursor.execute(query)
        return [book[0] for book in self.cursor.fetchall() if not book[0] == 0]

    def getBooks(self, text=config.mainText):
        bookList = self.getBookList(text)
        standardAbbreviation = BibleVerseParser(config.parserStandarisation).standardAbbreviation
        return " ".join(["{0}<button class='feature'>{1}</button></ref>".format(self.formBookTag(book, text), standardAbbreviation[str(book)]) for book in bookList if str(book) in standardAbbreviation])

    def getChapterList(self, b=config.mainB, text=config.mainText):
        query = "SELECT DISTINCT Chapter FROM {0} WHERE Book=? ORDER BY Chapter".format(text)
        self.cursor.execute(query, (b,))
        return [chapter[0] for chapter in self.cursor.fetchall()]

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

    def getVerseList(self, b, c, text=config.mainText):
        query = "SELECT DISTINCT Verse FROM {0} WHERE Book=? AND Chapter=? ORDER BY Verse".format(text)
        self.cursor.execute(query, (b, c))
        return [verse[0] for verse in self.cursor.fetchall()]

    def getVerses(self, b=config.mainB, c=config.mainC, text=config.mainText):
        verseList = self.getVerseList(b, c, text)
        return " ".join(["{0}{1}</ref>".format(self.formVerseTag(b, c, verse, text), verse) for verse in verseList])

    def compareVerse(self, verseList, texts=["ALL"]):
        if len(verseList) == 1 and not texts == ["ALL"]:
            b, c, v = verseList[0]
            return self.compareVerseChapter(b, c, v, texts)
        else:
            return "".join([self.readTranslations(b, c, v, texts) for b, c, v in verseList])

    def compareVerseChapter(self, b, c, v, texts):
        verseList = self.getVerseList(b, c, texts[0])
        chapter = "<h2>{0}</h2><table style='width: 100%;'>".format(self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        for verse in verseList:
            row = 0
            for text in texts:
                row = row + 1
                if row % 2 == 0:
                    chapter += "<tr>"
                else:
                    chapter += "<tr style='background-color: #f2f2f2;'>"
                if row == 1:
                    chapter += "<td style='vertical-align: text-top;'><vid>{0}{1}</ref></vid> ".format(self.formVerseTag(b, c, verse, text), verse)
                else:
                    chapter += "<td>"
                textTdTag = "<td>"
                if b < 40 and text in self.rtlTexts:
                    textTdTag = "<td style='direction: rtl;'>"
                chapter += "</td><td><sup>({0}{1}</ref>)</sup></td>{2}{3}</td></tr>".format(self.formVerseTag(b, c, verse, text), text, textTdTag, self.readTextVerse(text, b, c, verse)[3])
        chapter += "</table>"
        return chapter

    def readTranslations(self, b, c, v, texts):
        if texts == ["ALL"]:
            bibleList = self.getBibleList()
            texts = ["OHGB", "OHGBi", "LXX"]
            exclude = ("LXX", "LXX1", "LXX1i", "LXX2", "LXX2i", "MOB", "MAB", "MIB", "MPB", "MTB", "OHGB", "OHGBi")
            for bible in bibleList:
                if not bible in exclude:
                    texts.append(bible)
        verses = "<h2>{0}</h2>".format(self.bcvToVerseReference(b, c, v))
        for text in texts:
            book, chapter, verse, verseText = self.readTextVerse(text, b, c, v)
            divTag = "<div>"
            if b < 40 and text in self.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), text, verseText.strip())
        return verses

    def countSearchBible(self, text, searchString, interlinear=False):
        if interlinear:
            content = "ISEARCH:::{0}:::{1}".format(text, searchString)
            showCommand = "SHOWISEARCH"
            searchFunction = "iSearchBibleBook"
        else:
            content = "SEARCH:::{0}:::{1}".format(text, searchString)
            showCommand = "SHOWSEARCH"
            searchFunction = "searchBibleBook"
        bookList = self.getBookList(text)
        bookCountList = [self.countSearchBook(text, book, searchString) for book in bookList]
        content += "<p>Total: <ref onclick='document.title=\"{3}:::{1}:::{2}\"'>{0} verse(s)</ref> found in {1}.</p><table><tr><th>Book</th><th>Verse(s)</th></tr>".format(sum(bookCountList), text, searchString, showCommand)
        for counter, bookCount in enumerate(bookCountList):
            book = bookList[counter]
            bookAbb = self.bcvToVerseReference(book, 1, 1)[:-4]
            content += "<tr><td><ref onclick='tbcv(\"{0}\", {1}, 1, 1)' onmouseover='bookName(\"{2}\")'>{2}</ref></td><td><ref onclick='{5}(\"{0}\", \"{1}\", \"{3}\")'>{4}</ref></td></tr>".format(text, book, bookAbb, searchString, bookCount, searchFunction)
        content += "</table>"
        return content

    def countSearchBook(self, text, book, searchString):
        query = "SELECT Verse FROM {0} WHERE Book = ? AND Scripture LIKE ?".format(text)
        t = (book, "%{0}%".format(searchString))
        self.cursor.execute(query, t)
        return len(self.cursor.fetchall())

    def searchBible(self, text, mode, searchString, interlinear=False):
        formatedText = ""
        query = "SELECT * FROM {0} WHERE ".format(text)
        if mode == "BASIC":
            searchCommand = "SHOWSEARCH"
            if interlinear:
                searchCommand = "SHOWISEARCH"
            formatedText += "{0}:::{1}:::{2}".format(searchCommand, text, searchString)
            t = ("%{0}%".format(searchString),)
            query += "Scripture LIKE ?"
        elif mode == "ADVANCED":
            searchCommand = "ADVANCEDSEARCH"
            if interlinear:
                searchCommand = "ADVANCEDISEARCH"
            formatedText += "{0}:::{1}:::{2}".format(searchCommand, text, searchString)
            t = ()
            query += searchString
        query += " ORDER BY Book, Chapter, Verse"
        self.cursor.execute(query, t)
        verses = self.cursor.fetchall()
        formatedText += "<p>x <b style='color: brown;'>{0}</b> verse(s)</p>".format(len(verses))
        for verse in verses:
            b, c, v, verseText = verse
            if b < 40 and text in self.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            else:
                divTag = "<div>"
            formatedText += "{0}<span style='color: purple;'>({1}{2}</ref>)</span> {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), self.bcvToVerseReference(b, c, v), verseText.strip())
            if interlinear:
                if b < 40:
                    divTag = "<div style='direction: rtl; border: 1px solid gray; border-radius: 2px; margin: 5px; padding: 5px;'>"
                else:
                    divTag = "<div style='border: 1px solid gray; border-radius: 2px; margin: 5px; padding: 5px;'>"
                formatedText += "{0}{1}</div>".format(divTag, self.readTextVerse("OHGB", b, c, v)[3])
        if mode == "BASIC" and not searchString == "z":
            formatedText = re.sub("("+searchString+")", r"<z>\1</z>", formatedText, flags=re.IGNORECASE)
        elif mode == "ADVANCED":
            searchWords = [m for m in re.findall("LIKE ['\"]%(.*?)%['\"]", searchString, flags=re.IGNORECASE)]
            searchWords = [m.split("%") for m in searchWords]
            searchWords = [m2 for m1 in searchWords for m2 in m1]
            for searchword in searchWords:
                if not searchword == "z":
                    formatedText = re.sub("("+searchword+")", r"<z>\1</z>", formatedText, flags=re.IGNORECASE)
        p = re.compile("(<[^<>]*?)<z>(.*?)</z>", flags=re.M)
        s = p.search(formatedText)
        while s:
            formatedText = re.sub(p, r"\1\2", formatedText)
            s = p.search(formatedText)
        return formatedText

    def readMultipleVerses(self, text, verseList):
        verses = ""
        for b, c, v in verseList:
            divTag = "<div>"
            if b < 40 and text in self.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            verses += "{0}({1}{2}</ref>) {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), self.bcvToVerseReference(b, c, v), self.readTextVerse(text, b, c, v)[3])
        return verses

    def readPlainChapter(self, text, verse):
        # expect bcv is a tuple
        b, c, v = verse
        chapter = "<h2>{0}{1}</ref></h2>".format(self.formChapterTag(b, c, text), self.bcvToVerseReference(b, c, v).split(":", 1)[0])
        titleList = self.getVerseList(b, c, "title")
        verseList = self.readTextChapter(text, b, c)
        for verseTuple in verseList:
            b, c, v, verseText = verseTuple
            divTag = "<div>"
            if b < 40 and text in self.rtlTexts:
                divTag = "<div style='direction: rtl;'>"
            if v in titleList:
                if not v == 1:
                    chapter += "<br>"
                chapter += "{0}<br>".format(self.readTextVerse("title", b, c, v)[3])
            chapter += "{0}<vid>{1}{2}</ref></vid> {3}</div>".format(divTag, self.formVerseTag(b, c, v, text), v, verseText)
        return chapter


class ClauseData:

    def __init__(self):
        # connect images.sqlite
        self.database = os.path.join("marvelData", "data", "clause.data")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getContent(self, testament, entry):
        query = "SELECT Information FROM {0} WHERE EntryID = ?".format(testament)
        self.cursor.execute(query, ("c{0}".format(entry),))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return content[0]


class Bible:

    def __init__(self, text):
        # connect bibles.sqlite
        self.text = text
        self.database = os.path.join("marvelData", "bibles", text+".bible")
        self.connection = sqlite3.connect(self.database)
        self.cursor = self.connection.cursor()
        self.rtlTexts = ["original", "MOB", "MAB", "MTB", "MIB", "MPB", "OHGB", "OHGBi"]

    def __del__(self):
        self.connection.close()

    def readFormattedChapter(self, verse):
        b, c, v = verse
        biblesSqlite = BiblesSqlite()
        chapter = "<h2>{0}{1}</ref></h2>".format(biblesSqlite.formChapterTag(b, c, self.text), biblesSqlite.bcvToVerseReference(b, c, v).split(":", 1)[0])
        del biblesSqlite
        query = "SELECT Scripture FROM Bible WHERE Book=? AND Chapter=?"
        self.cursor.execute(query, verse[:-1])
        scripture = self.cursor.fetchone()
        if scripture:
            chapter += re.sub('onclick="luV\(([0-9]+?)\)"', r'onclick="luV(\1)" onmouseover="qV(\1)" ondblclick="mV(\1)"', scripture[0])
            if not scripture:
                return "<span style='color:gray;'>['{0}' does not contain this chapter.]</span>".format(self.text)
            else:
                divTag = "<div>"
                if self.text in self.rtlTexts and b < 40:
                    divTag = "<div style='direction: rtl;'>"
                return "{0}{1}</div>".format(divTag, chapter)
        else:
            return "<span style='color:gray;'>['{0}' does not contain this chapter.]</span>".format(self.text)

    def readBiblenote(self, bcvi):
        b, c, v, i = bcvi.split(".")
        query = "Select Note FROM Notes WHERE Book=? AND Chapter=? AND Verse=? AND ID=?"
        self.cursor.execute(query, (int(b), int(c), int(v), i))
        note = self.cursor.fetchone()
        if note:
            note = note[0]
        return note

class MorphologySqlite:

    def __init__(self):
        # connect bibles.sqlite
        self.database = os.path.join("marvelData", "morphology.sqlite")
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


#if __name__ == '__main__':
    # Bibles = BiblesSqlite()

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
