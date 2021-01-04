import os, sqlite3, config, re, json, base64, logging
from shutil import copyfile
from BiblesSqlite import BiblesSqlite
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import Bible

class Converter:

    # create UniqueBible.app commentary module
    def createCommentaryModule(self, abbreviation, title, description, content):
        ubCommentary = os.path.join(config.marvelData, "commentaries", "c{0}.commentary".format(abbreviation))
        if os.path.isfile(ubCommentary):
            os.remove(ubCommentary)
        with sqlite3.connect(ubCommentary) as connection:
            # create a cusor object
            cursor = connection.cursor()
            # create two tables: "Details" & "Commentary"
            statements = (
                "CREATE TABLE Details (Title NVARCHAR(100), Abbreviation NVARCHAR(50), Information TEXT, Version INT, OldTestament BOOL, NewTestament BOOL, Apocrypha BOOL, Strongs BOOL)",
                "CREATE TABLE Commentary (Book INT, Chapter INT, Scripture TEXT)",
            )
            for create in statements:
                cursor.execute(create)
                connection.commit()
            # insert data to table "Details"
            insert = "INSERT INTO Details (Title, Abbreviation, Information, Version, OldTestament, NewTestament, Apocrypha, Strongs) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(insert, (title, abbreviation, description, 1, 1, 1, 0, 0))
            connection.commit()
            # insert data to table "Commentary"
            if content:
                insert = "INSERT INTO Commentary (Book, Chapter, Scripture) VALUES (?, ?, ?)"
                cursor.executemany(insert, content)
                connection.commit()

    def createBookModuleFromImages(self, folder):
        module = os.path.basename(folder)
        bookContent = []
        for filepath in sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not re.search("^[\._]", f)]):
            fileBasename = os.path.basename(filepath)
            fileName, fileExtension = os.path.splitext(fileBasename)
            if fileExtension.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
                # read a binary file
                with open(os.path.join(folder, filepath), "rb") as fileObject:
                    binaryData = fileObject.read()
                    encodedData = base64.b64encode(binaryData)
                    binaryString = encodedData.decode("ascii")
                    htmlTag = '<img src="data:image/{2};base64,{0}" alt="{1}">'.format(binaryString, fileBasename, fileExtension[1:])
                    bookContent.append((fileName, htmlTag))
        if bookContent and module:
            self.createBookModule(module, bookContent)
            return True
        else:
            return False

    def createBookModuleFromHTML(self, folder):
        module = os.path.basename(folder)
        bookContent = []
        for filepath in sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not re.search("^[\._]", f)]):
            fileBasename = os.path.basename(filepath)
            fileName, fileExtension = os.path.splitext(fileBasename)
            if fileExtension.lower() in (".htm", ".html", ".xhtml"):
                with open(os.path.join(folder, filepath), "r", encoding="utf-8") as fileObject:
                    html = fileObject.read()
                    html = BibleVerseParser(config.parserStandarisation).parseText(html)
                    bookContent.append((fileName, html))
        if bookContent and module:
            self.createBookModule(module, bookContent)
            return True
        else:
            return False

    def createBookModuleFromNotes(self, folder):
        module = os.path.basename(folder)
        bookContent = []
        for filepath in sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not re.search("^[\._]", f)]):
            fileBasename = os.path.basename(filepath)
            fileName, fileExtension = os.path.splitext(fileBasename)
            if fileExtension.lower() == ".uba":
                with open(os.path.join(folder, filepath), "r", encoding="utf-8") as fileObject:
                    note = fileObject.read()
                    note = BibleVerseParser(config.parserStandarisation).parseText(note)
                    bookContent.append((fileName, note))
        if bookContent and module:
            self.createBookModule(module, bookContent)
            return True
        else:
            return False

    # create UniqueBible.app book modules
    def createBookModule(self, module, content, blobData=None):
        content = [(re.sub("['{0}]".format('"'), "_", chapter), chapterContent) for chapter, chapterContent in content]
        book = os.path.join(config.marvelData, "books", "{0}.book".format(module))
        if os.path.isfile(book):
            os.remove(book)
        with sqlite3.connect(book) as connection:
            cursor = connection.cursor()
            # Create table for book content
            create = "CREATE TABLE Reference (Chapter NVARCHAR(100), Content TEXT)"
            cursor.execute(create)
            connection.commit()
            # insert data for book content
            insert = "INSERT INTO Reference (Chapter, Content) VALUES (?, ?)"
            cursor.executemany(insert, content)
            connection.commit()
            if blobData:
                # Create table for book content
                create = "CREATE TABLE data (Filename TEXT, Content BLOB)"
                cursor.execute(create)
                connection.commit()
                # insert data for book content
                insert = "INSERT INTO data (Filename, Content) VALUES (?, ?)"
                cursor.executemany(insert, blobData)
                connection.commit()

    # create UniqueBible.app dictionary module
    def createDictionaryModule(self, module, content):
        filename = os.path.join("thirdParty", "dictionaries", "{0}.dic.bbp".format(module))
        if os.path.isfile(filename):
            os.remove(filename)
        with sqlite3.connect(filename) as connection:
            cursor = connection.cursor()
            # create table "Dictionary"
            create = "CREATE TABLE Dictionary (Topic NVARCHAR(100), Definition TEXT)"
            cursor.execute(create)
            connection.commit()
            # insert data to table "Dictionary"
            insert = "INSERT INTO Dictionary (Topic, Definition) VALUES (?, ?)"
            cursor.executemany(insert, content)
            connection.commit()

    # create UniqueBible.app lexicon modules
    def createLexiconModule(self, module, content):
        book = os.path.join(config.marvelData, "lexicons", "{0}.lexicon".format(module))
        if os.path.isfile(book):
            os.remove(book)
        with sqlite3.connect(book) as connection:
            cursor = connection.cursor()
            # create table "Lexicon"
            create = "CREATE TABLE Lexicon (Topic NVARCHAR(100), Definition TEXT)"
            cursor.execute(create)
            connection.commit()
            # insert data to table "Lexicon
            insert = "INSERT INTO Lexicon (Topic, Definition) VALUES (?, ?)"
            cursor.executemany(insert, content)
            connection.commit()

    # export image files
    def exportImageData(self, module, images):
        module = module.replace(" ", "_")
        imageFolder = os.path.join("htmlResources", "images", module)
        if not os.path.isdir(imageFolder):
            os.makedirs(imageFolder)
        for filename, blobData in images:
            imageFilePath = os.path.join(imageFolder, filename)
            if not os.path.isfile(imageFilePath):
                with open(imageFilePath, "wb") as imagefile:
                    imagefile.write(blobData)

    # Export from installed bibles into JSON format; for use with DartBible project.
    # usage:
    # from ThirdParty import Converter
    # Converter().exportJsonBible("KJV")
    def exportMultipleBibles(self, bibleList):
        for bible in bibleList:
            self.exportJsonBible(bible)

    def exportJsonBible(self, bible):
        filename = os.path.join(config.marvelData, "bibles", "{0}.bible".format(bible))
        connection = sqlite3.connect(filename)
        cursor = connection.cursor()

        query = "SELECT * FROM Verses ORDER BY Book, Chapter, Verse"
        cursor.execute(query)
        verses = cursor.fetchall()

        jsonString = "[\n"
        for book, chapter, verse, scripture in verses:
            jsonString += "{\n"
            jsonString += '"bNo": {0},\n'.format(book)
            jsonString += '"cNo": {0},\n'.format(chapter)
            jsonString += '"vNo": {0},\n'.format(verse)
            jsonString += '"vText": "{0}"\n'.format(scripture.strip().replace('"', '\\"'))
            jsonString += "},\n"
        jsonString = jsonString[:-2]
        jsonString += "\n]\n"

        jsonFile = os.path.join(config.marvelData, "bibles", "{0}.json".format(bible))
        fileObj = open(jsonFile, "w", encoding="utf-8")
        fileObj.write(jsonString)
        fileObj.close()

    # if exportMarvelBible doesn't work, use exportMarvelBible2 instead
    def exportJsonBible2(self, bible):
        filename = os.path.join(config.marvelData, "bibles", "{0}.bible".format(bible))
        connection = sqlite3.connect(filename)
        cursor = connection.cursor()

        query = "SELECT * FROM Verses ORDER BY Book, Chapter, Verse"
        cursor.execute(query)
        verses = cursor.fetchall()

        jsonString = "[\n"
        jsonObject = []
        for book, chapter, verse, scripture in verses:
            verseObject = {}
            verseObject["bNo"] = book
            verseObject["cNo"] = chapter
            verseObject["vNo"] = verse
            verseObject["vText"] = scripture
            jsonObject.append(verseObject)
        jsonString = json.dumps(jsonObject) # Please note that "json.dumps()" converts unicode characters.

        jsonFile = os.path.join(config.marvelData, "bibles", "{0}.json".format(bible))
        fileObj = open(jsonFile, "w", encoding="utf-8")
        fileObj.write(jsonString)
        fileObj.close()

    # bible modules verse number format
    def formatVerseNumber(self, book, chapter, verse, text):
        text = '<vid id="v{0}.{1}.{2}" onclick="luV({2})">{2}</vid> {3}'.format(book, chapter, verse, text)
        p = re.compile("(<vid .*?</vid> )(<u><b>.*?</b></u>|<br>|&emsp;|&ensp;| )")
        s = p.search(text)
        while s:
            text = p.sub(r"\2\1", text)
            s = p.search(text)
        text = text.strip()
        if config.importAddVerseLinebreak:
            text = "<verse>{0}</verse><br>".format(text)
        else:
            text = "<verse>{0}</verse> ".format(text)
        return text

    def fixCommentaryScrolling(self, chapterText):
        p = re.compile('｛｝([^｛｝]*?)(<vid id="v[0-9]+?\.[0-9]+?\.[0-9]+?"></vid>)(<vid)')
        s = p.search(chapterText)
        while s:
            chapterText = p.sub(r"｛｝\2｜\1\3", chapterText)
            s = p.search(chapterText)
        chapterText = chapterText.replace("｛｝", "<hr>")
        chapterText = chapterText.replace("</vid>｜", "</vid>")
        return chapterText

    def importAllFilesInAFolder(self, folder):
        files = [filename for filename in os.listdir(folder) if os.path.isfile(os.path.join(folder, filename)) and not re.search("^[\._]", filename)]
        validFiles = [filename for filename in files if re.search('(\.dct\.mybible|\.dcti|\.lexi|\.dictionary\.SQLite3|\.bbl\.mybible|\.cmt\.mybible|\.bok\.mybible|\.bbli|\.cmti|\.refi|\.commentaries\.SQLite3|\.SQLite3)$', filename)]
        if validFiles:
            for filename in validFiles:
                filename = os.path.join(folder, filename)
                try:
                    if re.search('(\.dct\.mybible|\.dcti|\.lexi|\.dictionary\.SQLite3)$', filename):
                        self.importThirdPartyDictionary(filename)
                    elif filename.endswith(".bbl.mybible"):
                        self.importMySwordBible(filename)
                    elif filename.endswith(".cmt.mybible"):
                        self.importMySwordCommentary(filename)
                    elif filename.endswith(".bok.mybible"):
                        self.importMySwordBook(filename)
                    elif filename.endswith(".bbli"):
                        self.importESwordBible(filename)
                    elif filename.endswith(".cmti"):
                        self.importESwordCommentary(filename)
                    elif filename.endswith(".refi"):
                        self.importESwordBook(filename)
                    elif filename.endswith(".commentaries.SQLite3"):
                        self.importMyBibleCommentary(filename)
                    elif filename.endswith(".SQLite3"):
                        self.importMyBibleBible(filename)
                    else:
                        print("File type of '{0}' is not supported for conversion.".format(filename))
                except:
                    print("Failed to convert '{0}'.".format(filename))
            return True

    def importThirdPartyDictionary(self, filename):
        *_, name = os.path.split(filename)
        destination = os.path.join("thirdParty", "dictionaries", name)
        try:
            copyfile(filename, destination)
        except:
            print("Failed to copy '{0}'.".format(filename))

    # Import e-Sword Bibles [Apple / macOS / iOS]
    def importESwordBible(self, filename):
        logger = logging.getLogger('uba')
        logger.info("Importing eSword Bible: " + filename)
        connection = sqlite3.connect(filename)
        cursor = connection.cursor()

        query = "SELECT Title, Abbreviation FROM Details"
        cursor.execute(query)
        description, abbreviation = cursor.fetchone()
        abbreviation = abbreviation.replace("-", "")
        abbreviation = abbreviation.replace("'", "")
        abbreviation = abbreviation.replace('"', "")
        abbreviation = abbreviation.replace("+", "x")
        query = "SELECT * FROM Bible ORDER BY Book, Chapter, Verse"
        cursor.execute(query)
        verses = cursor.fetchall()

        # check existing table names
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        cursor.execute(query, ("table",))
        tables = cursor.fetchall()
        tables = [table[0] for table in tables]
        if "Notes" in tables:
            query = "SELECT * FROM Notes"
            cursor.execute(query)
            notes = cursor.fetchall()
            self.eSwordBibleToRichFormat(description, abbreviation, verses, notes)
        else:
            self.eSwordBibleToRichFormat(description, abbreviation, verses, [])
        self.eSwordBibleToPlainFormat(description, abbreviation, verses)
        connection.close()
        if config.importRtlOT:
            config.rtlTexts.append(abbreviation)
        logger.info("Importing successful")

    def eSwordBibleToPlainFormat(self, description, abbreviation, verses):
        verses = [(book, chapter, verse, self.stripESwordBibleTags(scripture)) for book, chapter, verse, scripture in verses]
        biblesSqlite = BiblesSqlite()
        biblesSqlite.importBible(description, abbreviation, verses)
        del biblesSqlite

    def eSwordBibleToRichFormat(self, description, abbreviation, verses, notes):
        formattedBible = os.path.join(config.marvelData, "bibles", "{0}.bible".format(abbreviation))
        if os.path.isfile(formattedBible):
            os.remove(formattedBible)
        connection = sqlite3.connect(formattedBible)
        cursor = connection.cursor()

        statements = (
            "CREATE TABLE Bible (Book INT, Chapter INT, Scripture TEXT)",
            "CREATE TABLE Notes (Book INT, Chapter INT, Verse INT, ID TEXT, Note TEXT)",
            ("CREATE TABLE Details (Title NVARCHAR(100), Abbreviation NVARCHAR(50), Information TEXT,"
             "Version INT, OldTestament BOOL, NewTestament BOOL, Apocrypha BOOL, Strongs BOOL)")
        )
        for create in statements:
            cursor.execute(create)
            connection.commit()

        noteList = []
        formattedChapters = {}
        for book, chapter, verse, scripture in verses:
            scripture = self.convertESwordBibleTags(scripture)

            if scripture:

                # fix bible note links
                if notes:
                    scripture = re.sub("<not>([^\n<>]+?)</not>", r"<sup><ref onclick='bn({0}, {1}, {2}, {3}\1{3})'>&oplus;</ref></sup>".format(book, chapter, verse, '"'), scripture)

                # verse number formatting
                scripture = self.formatVerseNumber(book, chapter, verse, scripture)

                if (book, chapter) in formattedChapters:
                    formattedChapters[(book, chapter)] = formattedChapters[(book, chapter)] + scripture
                else:
                    formattedChapters[(book, chapter)] = scripture

        if notes:
            insert = "INSERT INTO Notes (Book, Chapter, Verse, ID, Note) VALUES (?, ?, ?, ?, ?)"
            notes = [(book, chapter, verse, id, self.formatNonBibleESwordModule(note)) for book, chapter, verse, id, note in notes]
            cursor.executemany(insert, notes)
            connection.commit()

        formattedChapters = [(book, chapter, formattedChapters[(book, chapter)]) for book, chapter in formattedChapters]
        insert = "INSERT INTO Bible (Book, Chapter, Scripture) VALUES (?, ?, ?)"
        cursor.executemany(insert, formattedChapters)
        connection.commit()

        self.populateDetails(cursor, description, abbreviation)

        connection.close()

    def stripESwordBibleTags(self, text):
        if config.importDoNotStripStrongNo:
            text = re.sub("[ ]*?<num>([GH][0-9]+?[a-z]*?)</num>", r" \1 ", text)
        else:
            text = re.sub("[ ]*?<num>([GH][0-9]+?[a-z]*?)</num>", "", text)
        if config.importDoNotStripMorphCode:
            text = re.sub("[ ]*?<tvm>([^\n<>]*?)</tvm>", r" \1 ", text)
        else:
            text = re.sub("[ ]*?<tvm>([^\n<>]*?)</tvm>", "", text)
        searchReplace = (
            ("<p>|</p>|<h[0-9]+?>|</h[0-9]+?>|<sup>", " "),
            ("<not>.*?</not>|<[^\n<>]*?>", ""),
            (" [ ]+?([^ ])", r" \1"),
        )
        text = text.strip()
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        text = text.strip()
        return text

    def convertESwordBibleTags(self, text):
        searchReplace = (
            ("[ ]*?<num>([GH][0-9]+?[a-z]*?)</num>", r"<sup><ref onclick='lex({0}\1{0})'>\1</ref></sup>".format('"')),
            ("[ ]*?<tvm>([^\n<>]*?)</tvm>", r"<sup><ref onclick='rmac({0}\1{0})'>\1</ref></sup>".format('"')),
            ("<red>", "<woj>"),
            ("</red>", "</woj>"),
            ("<blu>", "<esblu>"),
            ("</blu>", "</esblu>"),
            ("</ref><ref", "</ref>; <ref"),
            ("</ref></sup>[ ]*?<sup><ref", "</ref> <ref"),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        text = text.strip()
        return text

    # Import e-Sword Commentaries
    def importESwordCommentary(self, filename):
        # connect e-Sword commentary
        with sqlite3.connect(filename) as connection:
            cursor = connection.cursor()
            # process 4 tables: Details, BookCommentary, ChapterCommentary, VerseCommentary
            # table: Details
            query = "SELECT Title, Abbreviation, Information FROM Details"
            cursor.execute(query)
            title, abbreviation, description = cursor.fetchone()
            abbreviation = abbreviation.replace(" ", "_")
            # check availability tables
            query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
            cursor.execute(query, ("table",))
            tables = cursor.fetchall()
            tables = [table[0] for table in tables]
            # commentary content
            commentaryContent = []
            # table: BookCommentary
            if "BookCommentary" in tables:
                query = "SELECT Book, Comments FROM BookCommentary ORDER BY Book"
                cursor.execute(query)
                bookCommentaries = cursor.fetchall()
                if bookCommentaries:
                    commentaryContent += [(bookBook, 0, bookComments) for bookBook, bookComments in bookCommentaries]
            # distinct chapters from table: ChapterCommentary
            distinctChapters1 = []
            if "ChapterCommentary" in tables:
                query = "SELECT DISTINCT Book, Chapter FROM ChapterCommentary ORDER BY Book, Chapter"
                cursor.execute(query)
                distinctChapters1 = cursor.fetchall()
            # distinct chapters from table: VerseCommentary
            distinctChapters2 = []
            if "VerseCommentary" in tables:
                query = "SELECT DISTINCT Book, ChapterBegin FROM VerseCommentary ORDER BY Book, ChapterBegin, VerseBegin, ChapterEnd, VerseEnd"
                cursor.execute(query)
                distinctChapters2 = cursor.fetchall()
            # combine distinct chapters
            distinctChapters = list(set().union(distinctChapters1, distinctChapters2))
            # draw data on distinct chapters
            bibleSqlite = BiblesSqlite()
            for b, c in distinctChapters:
                # check KJV verse list with a specific book and chapter
                verseList = bibleSqlite.getVerseList(b, c, "kjvbcv")
                # create a temporary verse dictionary
                verseDict = {v: ['<vid id="v{0}.{1}.{2}"></vid>'.format(b, c, v)] for v in verseList}
                # create a temporary list for holding content
                verses = []
                # data from table: ChapterCommentary
                if "ChapterCommentary" in tables:
                    query = "SELECT Book, Chapter, Comments FROM ChapterCommentary WHERE Book=? AND Chapter=? ORDER BY Book, Chapter"
                    cursor.execute(query, (b, c))
                    chapterCommentary = cursor.fetchone()
                    if chapterCommentary:
                        chapterBook, chapterChapter, chapterComments = chapterCommentary
                        verses += [(chapterBook, chapterChapter, 0, chapterChapter, 0, chapterComments)]
                # data from table: VerseCommentary
                if "VerseCommentary" in tables:
                    query = "SELECT Book, ChapterBegin, VerseBegin, ChapterEnd, VerseEnd, Comments FROM VerseCommentary WHERE Book=? AND ChapterBegin=? ORDER BY Book, ChapterBegin, VerseBegin, ChapterEnd, VerseEnd"
                    cursor.execute(query, (b, c))
                    verses += cursor.fetchall()
                # formating the content
                for verse in verses:
                    verseContent = '<ref onclick="bcv({0},{1},{2})"><u><b>{1}:{2}-{3}:{4}</b></u></ref><br>{5}'.format(*verse)
                    # check fromverse is a key in verseDict
                    fromverse = verse[2]
                    item = verseDict.get(fromverse, "not found")
                    if item == "not found":
                        verseDict[fromverse] = ['<vid id="v{0}.{1}.{2}"></vid>'.format(b, c, fromverse), verseContent]
                    else:
                        item.append(verseContent)
                # sort the verse numbers
                sortedVerseNo = sorted(verseDict.keys())
                # format chapter text
                chapterText = ""
                for verseNo in sortedVerseNo:
                    chapterText += "｛｝".join(verseDict[verseNo])
                # fix commentary scrolling
                chapterText = self.fixCommentaryScrolling(chapterText)
                # add data to commentary content
                commentaryContent.append((b, c, chapterText))
            # convert e-Sword format to UniqueBible format
            commentaryContent = [(b, c, self.formatESwordCommentaryVerse(chapterText)) for b, c, chapterText in commentaryContent]
            # write to a UB commentary file
            self.createCommentaryModule(abbreviation, title, description, commentaryContent)

    def formatESwordCommentaryVerse(self, text):
        text = re.sub(r"<u><b>([0-9]+?:[0-9]+?)-\1</b></u>", r"<u><b>\1</b></u>", text)
        text = re.sub(r"<u><b>([0-9]+?):([0-9]+?)-\1:([0-9]+?)</b></u>", r"<u><b>\1:\2-\3</b></u>", text)
        text = self.formatNonBibleESwordModule(text)
        return text

    def formatNonBibleESwordModule(self, text):
        searchReplace = {
            ("<ref>(.+?)</ref>", self.convertESwordBibleReference),
            ("<num>(.*?)</num>", r"<ref onclick='lex({0}\1{0})'>\1</ref>".format('"')),
            ("<tvm>(.*?)</tvm>", r"<ref onclick='rmac({0}\1{0})'>\1</ref>".format('"')),
        }
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        return text

    def convertESwordBibleReference(self, match):
        value = match.group(1).replace("_", " ")
        return "<ref onclick='document.title={0}BIBLE:::{1}{0}'>{1}</ref>".format('"', value)
#        reference = self.parseESwordReference("{0} ".format(value))
#        if reference:
#            return "{0}{1}</ref>".format(reference, value)
#        else:
#            return "<ref onclick='document.title={0}BIBLE:::{1}{0}'>{1}</ref>".format('"', value)

    def parseESwordReference(self, text):
        if re.search("^([1-9A-Z][A-Za-z][a-z]) ([0-9]+?):([0-9]+?)[^0-9].*?$", text):
            b, cv = text.split(" ", 1)
            b = self.convertESwordBookAbb(b)
            if b == 0:
                return ""
            else:
                c, v = re.sub("^([0-9]+?):([0-9]+?)[^0-9].*?$", r"\1,\2", cv).split(",")
                return "<ref onclick='bcv({0}, {1}, {2})'>".format(b, c, v)
        elif re.search("^([1-9A-Z][A-Za-z][a-z]) ([0-9]+?)[^0-9].*?$", text):
            b, c = text.split(" ", 1)
            b = self.convertESwordBookAbb(b)
            if b == 0:
                return ""
            else:
                c = re.sub("^([0-9]+?)[^0-9].*?$", r"\1", c)
                return "<ref onclick='bcv({0}, {1}, {2})'>".format(b, c, 1)
        else:
            return ""

    def convertESwordBookAbb(self, eSwordAbb):
        ubNo = {
            "Gen": 1,
            "Exo": 2,
            "Lev": 3,
            "Num": 4,
            "Deu": 5,
            "Jos": 6,
            "Jdg": 7,
            "Rth": 8,
            "1Sa": 9,
            "2Sa": 10,
            "1Ki": 11,
            "2Ki": 12,
            "1Ch": 13,
            "2Ch": 14,
            "Ezr": 15,
            "Neh": 16,
            "Est": 17,
            "Job": 18,
            "Psa": 19,
            "Pro": 20,
            "Ecc": 21,
            "Son": 22,
            "Isa": 23,
            "Jer": 24,
            "Lam": 25,
            "Eze": 26,
            "Dan": 27,
            "Hos": 28,
            "Joe": 29,
            "Amo": 30,
            "Oba": 31,
            "Jon": 32,
            "Mic": 33,
            "Nah": 34,
            "Hab": 35,
            "Zep": 36,
            "Hag": 37,
            "Zec": 38,
            "Mal": 39,
            "Mat": 40,
            "Mar": 41,
            "Luk": 42,
            "Joh": 43,
            "Act": 44,
            "Rom": 45,
            "1Co": 46,
            "2Co": 47,
            "Gal": 48,
            "Eph": 49,
            "Php": 50,
            "Col": 51,
            "1Th": 52,
            "2Th": 53,
            "1Ti": 54,
            "2Ti": 55,
            "Tit": 56,
            "Phm": 57,
            "Heb": 58,
            "Jas": 59,
            "1Pe": 60,
            "2Pe": 61,
            "1Jn": 62,
            "2Jn": 63,
            "3Jn": 64,
            "Jud": 65,
            "Rev": 66,
            "1Es": 76,
            "2Es": 77,
            "Tob": 88,
            "Jdt": 80,
            "1Ma": 81,
            "2Ma": 82,
            "3Ma": 83,
            "4Ma": 84,
            "Man": 85,
            "Wis": 89,
            "Sir": 87,
            "Bar": 70,
        }
        if eSwordAbb in ubNo:
            return ubNo[eSwordAbb]
        else:
            return 0

    # Import MySword Bibles
    def importMySwordBible(self, filename):
        logger = logging.getLogger('uba')
        logger.info("Importing MySword Bible: " + filename)
        connection = sqlite3.connect(filename)
        cursor = connection.cursor()

        query = "SELECT Description, Abbreviation FROM Details"
        cursor.execute(query)
        description, abbreviation = cursor.fetchone()
        abbreviation = abbreviation.replace("-", "")
        abbreviation = abbreviation.replace("'", "")
        abbreviation = abbreviation.replace('"', "")
        abbreviation = abbreviation.replace("+", "x")
        query = "SELECT * FROM Bible ORDER BY Book, Chapter, Verse"
        cursor.execute(query)
        verses = cursor.fetchall()
        connection.close()

        self.mySwordBibleToRichFormat(description, abbreviation, verses)
        self.mySwordBibleToPlainFormat(description, abbreviation, verses)
        if config.importRtlOT:
            config.rtlTexts.append(abbreviation)
        logger.info("Import successful")

    def mySwordBibleToPlainFormat(self, description, abbreviation, verses):
        verses = [(book, chapter, verse, self.stripMySwordBibleTags(scripture)) for book, chapter, verse, scripture in verses]
        biblesSqlite = BiblesSqlite()
        biblesSqlite.importBible(description, abbreviation, verses)
        del biblesSqlite

    def mySwordBibleToRichFormat(self, description, abbreviation, verses):
        formattedBible = os.path.join(config.marvelData, "bibles", "{0}.bible".format(abbreviation))
        if os.path.isfile(formattedBible):
            os.remove(formattedBible)
        connection = sqlite3.connect(formattedBible)
        cursor = connection.cursor()

        statements = (
            "CREATE TABLE Bible (Book INT, Chapter INT, Scripture TEXT)",
            "CREATE TABLE Notes (Book INT, Chapter INT, Verse INT, ID TEXT, Note TEXT)",
            ("CREATE TABLE Details (Title NVARCHAR(100), Abbreviation NVARCHAR(50), Information TEXT,"
                "Version INT, OldTestament BOOL, NewTestament BOOL, Apocrypha BOOL, Strongs BOOL)")
        )
        for create in statements:
            cursor.execute(create)
            connection.commit()

        noteList = []
        formattedChapters = {}
        for book, chapter, verse, scripture in verses:
            scripture, notes = self.convertMySwordBibleTags(scripture)

            if notes:
                for counter, note in enumerate(notes):
                    noteList.append((book, chapter, verse, str(counter), note))

            if scripture:

                # fix bible note links
                scripture = re.sub("｛([0-9]+?)｝", r"{0}, {1}, {2}, \1".format(book, chapter, verse), scripture)
                # verse number formatting
                scripture = self.formatVerseNumber(book, chapter, verse, scripture)

                if (book, chapter) in formattedChapters:
                    formattedChapters[(book, chapter)] = formattedChapters[(book, chapter)] + scripture
                else:
                    formattedChapters[(book, chapter)] = scripture

        insert = "INSERT INTO Notes (Book, Chapter, Verse, ID, Note) VALUES (?, ?, ?, ?, ?)"
        cursor.executemany(insert, noteList)
        connection.commit()

        formattedChapters = [(book, chapter, formattedChapters[(book, chapter)]) for book, chapter in formattedChapters]
        insert = "INSERT INTO Bible (Book, Chapter, Scripture) VALUES (?, ?, ?)"
        cursor.executemany(insert, formattedChapters)
        connection.commit()

        self.populateDetails(cursor, description, abbreviation)

        connection.close()

    def populateDetails(self, cursor, description, abbreviation):
        cursor.execute("SELECT COUNT(DISTINCT(Book)) FROM Bible")
        count = cursor.fetchone()[0]

        information = ''
        version = 1
        oldTestamentFlag = 1
        newTestamentFlag = 1
        apocryphaFlag = 0
        strongsFlag = 0
        if count <= 27:
            oldTestamentFlag = 0
        elif count == 39:
            newTestamentFlag = 0
        elif count > 66:
            apocryphaFlag = 1

        insert = "INSERT INTO Details VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(insert, (description[:100], abbreviation[:50], information, version, oldTestamentFlag,
                                newTestamentFlag, apocryphaFlag, strongsFlag))
        cursor.connection.commit()

    def stripMySwordBibleTags(self, text):
        if config.importDoNotStripStrongNo:
            text = re.sub("<W([GH][0-9]+?[a-z]*?)>", r" \1 ", text)
        if config.importDoNotStripMorphCode:
            text = re.sub("<WT([^\n<>]*?)>", r" \1 ", text)
        searchReplace = (
            ("<CM>|<CL>|<PI[0-9]*?>|<PF[0-9]*?>|<TS[0-9]*?>.*?<Ts>", " "),
            ("<sup><a.*?</a></sup>|<RF[^\n<>]*?>.*?<Rf>|<[^\n<>]*?>", ""),
            (" [ ]+?([^ ])", r" \1"),
        )
        text = text.strip()
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        text = text.strip()
        return text

    def convertMySwordBibleTags(self, text):
        searchReplace = (
            ("<CI>(<CL>|<CM>)", r"\1"),
            ("(<CL>|<CM>)<CI>", r"\1"),
            ("<CI>", " "),
            ("<CL><CM>|<CM><CL>|<CM>", "<br><br>"),
            ("<CL>", "<br>"),
            ("<PI[0-9]*?><PF[0-9]*?>|<PF[0-9]*?><PI[0-9]*?>|<PF[0-9]*?>|<PI[0-9]*?>", "<br>&emsp;&emsp;"),
            ("<TS[0-9]*?>(.*?)<Ts>", r"<u><b>\1</b></u><br><br>"),
            ("[ ]+?<br>", "<br>"),
            ("<br><br><br><br><br>|<br><br><br><br>|<br><br><br>", "<br><br>"),
            ("</b></u><br><br><u><b>", "</b></u><br><u><b>"),
            ("<FI>", "<i>"),
            ("<Fi>", "</i>"),
            ("<FO>", "<ot>"),
            ("<Fo>", "</ot>"),
            ("<FR>", "<woj>"),
            ("<Fr>", "</woj>"),
            ("<FU>", "<u>"),
            ("<Fu>", "</u>"),
            ("<W([GH][0-9]+?[a-z]*?)>", r"<sup><ref onclick='lex({0}\1{0})'>\1</ref></sup>".format('"')),
            ("<WT([^\n<>]*?)>", r"<sup><ref onclick='rmac({0}\1{0})'>\1</ref></sup>".format('"')),
            ("<RX ([0-9]+?)\.([0-9]+?)\.([0-9]+?)>", r"『\1｜\2｜\3』"),
            ("<RX ([0-9]+?)\.([0-9]+?)\.([0-9]+?)-[0-9]+?>", r"『\1｜\2｜\3』"),
            ("<RX ([0-9]+?)\.([0-9]+?)\.([0-9]+?)-[0-9]+?:[0-9]+?>", r"『\1｜\2｜\3』"),
            ("『([0-9]+?)｜([0-9]+?)｜([0-9]+?)』", self.convertMySwordRxTag),
            ("<sup>(<RF[^\n<>]*?>)|(<RF[^\n<>]*?>)<sup>", r"\1"),
            ("<Rf></sup>|</sup><Rf>", "<Rf>"),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        text, notes = self.convertMySwordRfTag(text)
        text = re.sub("</ref><ref", "</ref>; <ref", text)
        text = re.sub("</ref></sup>[ ]*?<sup><ref", "</ref> <ref", text)
        text = text.strip()
        return (text, notes)

    def convertMySwordRxTag(self, match):
        b, c, v = match.groups()
        bookName = BibleVerseParser(config.parserStandarisation).standardAbbreviation[b]
        return '<ref onclick="bcv({0},{1},{2})">{3} {1}:{2}</ref>'.format(b, c, v, bookName)

    def convertMySwordRfTag(self, text):
        notes = re.findall("<RF[^\n<>]*?>(.*?)<Rf>", text)
        p = re.compile("<RF[^\n<>]*?>.*?<Rf>")
        s = p.search(text)
        noteID = 0
        while s:
            text = p.sub("<sup><ref onclick='bn(｛{0}｝)'>&oplus;</ref></sup>".format(noteID), text)
            noteID += 1
            s = p.search(text)
        return (text, notes)

    # Import MySword Commentaries
    def importMySwordCommentary(self, filename):
        # variable to hold commentary content
        commentaryContent = []
        # connect MySword commentary
        with sqlite3.connect(filename) as connection:
            cursor = connection.cursor()
            # process 2 tables: details, commentary
            query = "SELECT title, abbreviation, description FROM details"
            cursor.execute(query)
            title, abbreviation, description = cursor.fetchone()
            abbreviation = abbreviation.replace(" ", "_")
            query = "SELECT DISTINCT book, chapter FROM commentary ORDER BY book, chapter, fromverse, toverse"
            cursor.execute(query)
            chapters = cursor.fetchall()
            # check if table "data" exists; (mainly contain images)
            query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
            cursor.execute(query, ("table",))
            tables = cursor.fetchall()
            tables = [table[0] for table in tables]
            if "data" in tables:
                query = "SELECT filename, content FROM data"
                cursor.execute(query)
                images = cursor.fetchall()
                if images:
                    self.exportImageData(abbreviation, images)
            # format chapters
            biblesSqlite = BiblesSqlite()
            for chapter in chapters:
                b, c = chapter
                verseList = biblesSqlite.getVerseList(b, c, "kjvbcv")
                # create a dictionary to hold verse content
                verseDict = {v: ['<vid id="v{0}.{1}.{2}"></vid>'.format(b, c, v)] for v in verseList}
                # get verse data of a specific book and chapter
                query = "SELECT book, chapter, fromverse, toverse, data FROM commentary WHERE book=? AND chapter=? ORDER BY book, chapter, fromverse, toverse"
                cursor.execute(query, chapter)
                verses = cursor.fetchall()
                # format verse content
                for verse in verses:
                    verseContent = '<ref onclick="bcv({0},{1},{2})"><u><b>{1}:{2}-{3}</b></u></ref><br>{4}'.format(*verse)
                    # convert imageTag
                    verseContent = re.sub(r"<img [^<>]*?src=(['{0}])([^<>]+?)\1[^<>]*?>".format('"'), r"<img src=\1images/{0}/\2\1/>".format(abbreviation.replace(" ", "_")), verseContent)
                    # check if verse number is a standard kjv verse number
                    fromverse = verse[2]
                    item = verseDict.get(fromverse, "not found")
                    if item == "not found":
                        verseDict[fromverse] = ['<vid id="v{0}.{1}.{2}"></vid>'.format(b, c, fromverse), verseContent]
                    else:
                        item.append(verseContent)
                # sorty verse numbers
                sortedVerses = sorted(verseDict.keys())
                # format chapter text
                chapterText = ""
                for sortedVerse in sortedVerses:
                    chapterText += "｛｝".join(verseDict[sortedVerse])
                chapterText = self.fixCommentaryScrolling(chapterText)
                # add to commentary content
                commentaryContent.append((b, c, chapterText))
            # convert MySword format to UniqueBible format
            commentaryContent = [(b, c, self.formatMySwordCommentaryVerse(chapterText)) for b, c, chapterText in commentaryContent]
            # write to a UB commentary file
            self.createCommentaryModule(abbreviation, title, description, commentaryContent)

    def formatMySwordCommentaryVerse(self, text):
        text = re.sub(r"<u><b>([0-9]+?):([0-9]+?)-\2</b></u>", r"<u><b>\1:\2</b></u>", text)
        text = self.formatNonBibleMySwordModule(text)
        return text

    def importMySwordBook(self, filename):
        *_, module = os.path.split(filename)
        module = module[:-12]

        # connect MySword *.bok.mybible file
        with sqlite3.connect(filename) as connection:
            cursor = connection.cursor()

            query = "SELECT title, content FROM journal"
            cursor.execute(query)
            content = cursor.fetchall()
            content = [(chapter, self.formatNonBibleMySwordModule(chapterContent)) for chapter, chapterContent in content]

            # check if table "data" exists; (mainly contain images)
            query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
            cursor.execute(query, ("table",))
            tables = cursor.fetchall()
            tables = [table[0] for table in tables]
            if "data" in tables:
                query = "SELECT filename, content FROM data"
                cursor.execute(query)
                images = cursor.fetchall()
                if images:
                    # rework imgage link in book content
                    content = [(chapter, re.sub(r"<img [^<>]*?src=(['{0}])([^<>]+?)\1[^<>]*?>".format('"'), r"<img src=\1images/{0}/\2\1/>".format(module.replace(" ", "_")), chapterContent)) for chapter, chapterContent in content]
                    # export image data
                    self.exportImageData(module, images)
            # send data to create a UniqueBible book module
            self.createBookModule(module, content)

    def formatNonBibleMySwordModule(self, text):
        # convert bible reference tag like <a class='bible' href='#bGen 1:1'>
        text = re.sub(r"<a [^<>]*?href=(['{0}])[#]*?b([0-9]*?[A-Za-z]+? [0-9][^<>]*?)\1>".format('"'), r"<a href='javascript:void(0)' onclick='document.title={0}BIBLE:::\2{0}'>".format('"'), text)
        # convert bible reference tag like <a class='bible' href='#b1.1.1'>
        text = re.sub("<a [^<>]*?href=['{0}][#]*?b([0-9]+?)\.([0-9]+?)\.([0-9]+?)[^0-9][^<>]*?>".format('"'), r'<a href="javascript:void(0)" onclick="bcv(\1,\2,\3)">', text)
        # convert commentary reference tag like <a href='#c-CSBC Gen 1:1'>
        text = re.sub("<a [^<>]*?href=(['{0}])[#]*?c\-([^ ]+?) ([0-9]*?[A-Za-z]+? [0-9][^<>]*?)\1>".format('"'), r"<a href='javascript:void(0)' onclick='document.title={0}COMMENTARY:::\2:::\3{0}'>".format('"'), text)
        # convert commentary reference tag like <a href='#cGen 1:1'>
        text = re.sub(r"<a [^<>]*?href=(['{0}])[#]*?c([0-9]*?[A-Za-z]+? [0-9][^<>]*?)\1>".format('"'), r"<a href='javascript:void(0)' onclick='document.title={0}COMMENTARY:::\2{0}'>".format('"'), text)
        # convert commentary reference tag like <a href='#c1.1.1'>
        text = re.sub("<a [^<>]*?href=['{0}][#]*?c([0-9]+?)\.([0-9]+?)\.([0-9]+?)[^0-9][^<>]*?>".format('"'), r'<a href="javascript:void(0)" onclick="cbcv(\1,\2,\3)">', text)
        # convert Strong's no tag, e.g. <a class='strong' href='#sH1'>H1</a>
        text = re.sub(r"<a [^<>]*?href=(['{0}])[#]*?s([HG][0-9a-z\.]+?)\1[^<>]*?>".format('"'), r'<a href="javascript:void(0)" onclick="lex({0}\2{0})">'.format("'"), text)
        # return formatted text
        return text

    # Import MyBible Bibles
    def importMyBibleBible(self, filename):
        connection = sqlite3.connect(filename)
        cursor = connection.cursor()

        query = "SELECT value FROM info WHERE name = 'description'"
        cursor.execute(query)
        description = cursor.fetchone()[0]
        inputFilePath, inputFileName = os.path.split(filename)
        originalModuleName = inputFileName[:-8]
        abbreviation = originalModuleName
        abbreviation = abbreviation.replace("-", "")
        abbreviation = abbreviation.replace("'", "")
        abbreviation = abbreviation.replace('"', "")
        abbreviation = abbreviation.replace("+", "x")

        query = "SELECT value FROM info WHERE name = 'strong_numbers_prefix'"
        cursor.execute(query)
        strong_numbers_prefix = cursor.fetchone()
        if strong_numbers_prefix:
            strong_numbers_prefix = strong_numbers_prefix[0]
        else:
            strong_numbers_prefix = ""

        # check existing table names
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        cursor.execute(query, ("table",))
        tables = cursor.fetchall()
        tables = [table[0] for table in tables]
        stories = []
        if "stories" in tables:
            try:
                query = "SELECT book_number, chapter, verse, title FROM stories ORDER BY book_number, chapter, verse"
                cursor.execute(query)
            except:
                query = "SELECT book_number, chapter, verse, text FROM stories ORDER BY book_number, chapter, verse"
                cursor.execute(query)
            stories = cursor.fetchall()

        query = "SELECT * FROM verses ORDER BY book_number, chapter, verse"
        cursor.execute(query)
        verses = cursor.fetchall()
        if verses:
            verses = [(self.convertMyBibleBookNo(mbBook), mbChapter, mbVerse, mbText) for mbBook, mbChapter, mbVerse, mbText in verses]

        # check if notes are available in commentary format
        noteFile = os.path.join(inputFilePath, "{0}.commentaries.SQLite3".format(originalModuleName))
        if os.path.isfile(noteFile):
            noteConnection = sqlite3.connect(noteFile)
            noteCursor = noteConnection.cursor()

            query = "SELECT book_number, chapter_number_from, verse_number_from, marker, text FROM commentaries"
            noteCursor.execute(query)
            notes = noteCursor.fetchall()
            self.myBibleBibleToRichFormat(description, abbreviation, verses, notes, strong_numbers_prefix, stories)
            noteConnection.close()
        else:
            self.myBibleBibleToRichFormat(description, abbreviation, verses, [], strong_numbers_prefix, stories)
        self.myBibleBibleToPlainFormat(description, abbreviation, verses, strong_numbers_prefix)
        connection.close()
        if config.importRtlOT:
            config.rtlTexts.append(abbreviation)

    def storiesToTitles(self, stories):
        titles = {}
        for story in stories:
            b, c, v, title = story
            if title:
                b = self.convertMyBibleBookNo(b)
                title = re.sub("<x>(.*?)</x>", self.convertMyBibleXRef, title)
                title = "<u><b>{0}</b></u>".format(title)
                item = titles.get((b, c, v), "not found")
                if item == "not found":
                    titles[(b, c, v)] = [title]
                else:
                    item.append(title)
        titles = {key: "<br>".join(titles[key]) for key in titles}
        return titles

    def convertMyBibleXRef(self, match):
        value = match.group(0)
        mbBookNoString, reference = match.group(1).split(" ", 1)
        if mbBookNoString and reference:
            ubBookNoString = str(self.convertMyBibleBookNo(int(mbBookNoString)))
            ubBookName = BibleVerseParser(config.parserStandarisation).standardAbbreviation[ubBookNoString]
            value = "<ref onclick='document.title={0}BIBLE:::{1} {2}{0}'>{1} {2}</ref>".format('"', ubBookName, reference)
        return value

    def myBibleBibleToPlainFormat(self, description, abbreviation, verses, strong_numbers_prefix):
        verses = [(book, chapter, verse, self.stripMyBibleBibleTags(scripture, book, strong_numbers_prefix)) for book, chapter, verse, scripture in verses]
        biblesSqlite = BiblesSqlite()
        biblesSqlite.importBible(description, abbreviation, verses)
        del biblesSqlite

    def myBibleBibleToRichFormat(self, description, abbreviation, verses, notes, strong_numbers_prefix, stories):
        formattedBible = os.path.join(config.marvelData, "bibles", "{0}.bible".format(abbreviation))
        if os.path.isfile(formattedBible):
            os.remove(formattedBible)
        connection = sqlite3.connect(formattedBible)
        cursor = connection.cursor()

        statements = (
            "CREATE TABLE Bible (Book INT, Chapter INT, Scripture TEXT)",
            "CREATE TABLE Notes (Book INT, Chapter INT, Verse INT, ID TEXT, Note TEXT)"
        )
        for create in statements:
            cursor.execute(create)
            connection.commit()

        if stories:
            stories = self.storiesToTitles(stories)

        noteList = []
        formattedChapters = {}
        for book, chapter, verse, scripture in verses:

            if scripture:

                # fix sub-heading(s)
                if (book, chapter, verse) in stories:
                    if verse == 1:
                        scripture = "{0}<br><br>{1}".format(stories[(book, chapter, verse)], scripture)
                    else:
                        scripture = "<br><br>{0}<br><br>{1}".format(stories[(book, chapter, verse)], scripture)

                scripture = self.convertMyBibleBibleTags(scripture, book, strong_numbers_prefix)

                # fix bible note links
                if notes:
                    scripture = re.sub("<f>([^\n<>]+?)</f>", r"<sup><ref onclick='bn({0}, {1}, {2}, {3}\1{3})'>&oplus;</ref></sup>".format(book, chapter, verse, '"'), scripture)

                # verse number formatting
                scripture = self.formatVerseNumber(book, chapter, verse, scripture)

                if (book, chapter) in formattedChapters:
                    formattedChapters[(book, chapter)] = formattedChapters[(book, chapter)] + scripture
                else:
                    formattedChapters[(book, chapter)] = scripture

        if notes:
            insert = "INSERT INTO Notes (Book, Chapter, Verse, ID, Note) VALUES (?, ?, ?, ?, ?)"
            notes = [(self.convertMyBibleBookNo(book), chapter, verse, id, self.formatNonBibleMyBibleModule(note, abbreviation)) for book, chapter, verse, id, note in notes]
            cursor.executemany(insert, notes)
            connection.commit()

        formattedChapters = [(book, chapter, formattedChapters[(book, chapter)]) for book, chapter in formattedChapters]
        insert = "INSERT INTO Bible (Book, Chapter, Scripture) VALUES (?, ?, ?)"
        cursor.executemany(insert, formattedChapters)
        connection.commit()

        connection.close()

    def stripMyBibleBibleTags(self, text, book, strong_numbers_prefix):
        if text:
            if config.importDoNotStripStrongNo:
                if book >= 40 or strong_numbers_prefix == "G":
                    text = re.sub("<S>([0-9]+?[a-z]*?)</S>", r" G\1 ", text)
                else:
                    text = re.sub("<S>([0-9]+?[a-z]*?)</S>", r" H\1 ", text)
            else:
                text = re.sub("<S>([0-9]+?[a-z]*?)</S>", "", text)
            if config.importDoNotStripMorphCode:
                text = re.sub("<m>([^\n<>]*?)</m>", r" \1 ", text)
            else:
                text = re.sub("<m>([^\n<>]*?)</m>", "", text)
            searchReplace = (
                ("<pb/>|<h>.*?</h>|<t>", " "),
                ("<f>.*?</f>|<[^\n<>]*?>", ""),
                (" [ ]+?([^ ])", r" \1"),
            )
            text = text.strip()
            for search, replace in searchReplace:
                text = re.sub(search, replace, text)
            text = text.strip()
        else:
            text = ""
        return text

    def convertMyBibleBibleTags(self, text, book, strong_numbers_prefix):
        if config.importInterlinear:
            wordTag = "heb"
            if book >= 40 or strong_numbers_prefix == "G":
                wordTag = "grk"
            text = re.sub("<br/>|<br>", "＠", text)
            text = re.sub("</n>([ ]*?)<n>", r"\1", text)
            # convert format like "The book <n>Βίβλος</n><S>976</S><m>N-NSF</m>"
            text = re.sub("([^＠]+?)<n>([^<>]+?)</n>(<S>[^<>]+?</S>)(<m>[^<>]+?</m>)", r'<div class="int"><wgloss>\1</wgloss>＠<wform><{0}>\2</{0}></wform>＠\3＠\4</div> '.format(wordTag), text)
            searchPattern = '</div> ([^＠]+?)<n>([^<>]+?)</n>'
            p = re.compile(searchPattern, flags=re.M)
            while p.search(text):
                text = re.sub(searchPattern, r'</div> <div class="int"><wgloss>\1</wgloss>＠<wform><{0}>\2</{0}></wform>＠&nbsp;＠&nbsp;</div> '.format(wordTag), text)
            searchPattern = '(<div class="int"><wgloss>)(<div class="int">.*?</div> )'
            p = re.compile(searchPattern, flags=re.M)
            while p.search(text):
                text = re.sub(searchPattern, r'\2\1', text)
            # convert format like "Βίβλος<S>976</S><m>N-NSF</m> <n>The book</n>"
            text = re.sub("([^＠]+?)(<S>[^<>]+?</S>)(<m>[^<>]+?</m>)[ ]*?<n>([^＠]+?)</n>", r'<div class="int"><wform><{0}>\1</{0}></wform>＠\2＠\3＠<wgloss>\4</wgloss></div> '.format(wordTag), text)
            # deal with original words without corresponding translation
            searchPattern = '<div class="int"><wform><{0}>([^＠]+?)(<S>[^<>]+?</S>)(<m>[^<>]+?</m>)'.format(wordTag)
            p = re.compile(searchPattern, flags=re.M)
            while p.search(text):
                text = re.sub(searchPattern, r'<div class="int"><wform><{0}>\1</{0}></wform>＠\2＠\3＠&nbsp;</div> <div class="int"><wform><{0}>'.format(wordTag), text)
        if book >= 40 or strong_numbers_prefix == "G":
            text = re.sub("<S>([0-9]+?[a-z]*?)</S>", r"<sup><ref onclick='lex({0}G\1{0})'>G\1</ref></sup>".format('"'), text)
        else:
            text = re.sub("<S>([0-9]+?[a-z]*?)</S>", r"<sup><ref onclick='lex({0}H\1{0})'>H\1</ref></sup>".format('"'), text)
        searchReplace = (
            ("<m>([^\n<>]*?)</m>", r"<sup><ref onclick='rmac({0}\1{0})'>\1</ref></sup>".format('"')),
            ("<J>", "<woj>"),
            ("</J>", "</woj>"),
            ("<e>", "<mbe>"),
            ("</e>", "</mbe>"),
            ("<n>", "<mbn>"),
            ("</n>", "</mbn>"),
            ("<t>", "<br>&emsp;&emsp;"),
            ("</t>", "<br>"),
            ("<h>(.*?)</h>", r"<u><b>\1</b></u><br><br>"),
            ("<br/>|＠", "<br>"),
            ("[ ]+?<br>", "<br>"),
            ("<br><br><br><br><br>|<br><br><br><br>|<br><br><br>", "<br><br>"),
            ("</b></u><br><br><u><b>", "</b></u><br><u><b>"),
            ("</ref><ref", "</ref>; <ref"),
            ("</ref></sup>[ ]*?<sup><ref", "</ref> <ref"),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        text = text.strip()
        return text

    # Import MyBible Commentaries
    def importMyBibleCommentary(self, filename):
        # variable to hold commentary content
        commentaryContent = []
        # connect MySword commentary
        with sqlite3.connect(filename) as connection:
            cursor = connection.cursor()
            # draw data from two tables: info, commentaries
            # table: info
            query = "SELECT value FROM info WHERE name = 'description'"
            cursor.execute(query)
            description = cursor.fetchone()[0]
            title = description
            *_, inputFileName = os.path.split(filename)
            abbreviation = inputFileName[:-21]
            abbreviation = re.sub("^(.*?)\-c$", r"\1", abbreviation)
            # table: commentaries
            # 6 columns in commentaries: book_number, chapter_number_from, verse_number_from, chapter_number_to, verse_number_to, text
            query = "SELECT DISTINCT book_number, chapter_number_from FROM commentaries ORDER BY book_number, chapter_number_from, verse_number_from, chapter_number_to, verse_number_to"
            cursor.execute(query)
            chapters = cursor.fetchall()
            # format chapters
            biblesSqlite = BiblesSqlite()
            for chapter in chapters:
                b, c = chapter
                b = self.convertMyBibleBookNo(b)
                # get standard kjv verse list for a chapter
                verseList = biblesSqlite.getVerseList(b, c, "kjvbcv")
                # use a dictionary to hold verse content
                verseDict = {v: ['<vid id="v{0}.{1}.{2}"></vid>'.format(b, c, v)] for v in verseList}
                # get verse data
                query = "SELECT book_number, chapter_number_from, verse_number_from, chapter_number_to, verse_number_to, text FROM commentaries WHERE book_number=? AND chapter_number_from=? ORDER BY book_number, chapter_number_from, verse_number_from, chapter_number_to, verse_number_to"
                cursor.execute(query, chapter)
                verses = cursor.fetchall()
                # format verses
                for verse in verses:
                    book_number, chapter_number_from, verse_number_from, chapter_number_to, verse_number_to, text = verse
                    book_number = self.convertMyBibleBookNo(book_number)
                    verseContent = '<ref onclick="bcv({0},{1},{2})"><u><b>{1}:{2}-{3}:{4}</b></u></ref><br>{5}'.format(book_number, chapter_number_from, verse_number_from, chapter_number_to, verse_number_to, text)
                    # check fromverse if it is included in a standard kjv verse list
                    # convert to integer below, as some modules are found containing string, probably by mistake
                    fromverse = int(verse_number_from)
                    item = verseDict.get(fromverse, "not found")
                    if item == "not found":
                        verseDict[fromverse] = ['<vid id="v{0}.{1}.{2}"></vid>'.format(b, c, fromverse), verseContent]
                    else:
                        item.append(verseContent)
                # sort verse numbers in a chapter
                sortedVerses = sorted(verseDict.keys())
                # combine verse content into a single chapter
                chapterText = ""
                for sortedVerse in sortedVerses:
                    chapterText += "｛｝".join(verseDict[sortedVerse])
                # fix scrolling for commentary modules
                chapterText = self.fixCommentaryScrolling(chapterText)
                # add to commentary content
                commentaryContent.append((b, c, chapterText))
            # convert MyBible format to UniqueBible format
            commentaryContent = [(b, c, self.formatMyBibleCommentaryVerse(chapterText, abbreviation)) for b, c, chapterText in commentaryContent]
            # write to a UB commentary file
            self.createCommentaryModule(abbreviation, title, description, commentaryContent)

    def formatMyBibleCommentaryVerse(self, text, abbreviation):
        text = re.sub(r"<u><b>([0-9]+?:[0-9]+?)-\1</b></u>", r"<u><b>\1</b></u>", text)
        text = re.sub(r"<u><b>([0-9]+?):([0-9]+?)-\1:([0-9]+?)</b></u>", r"<u><b>\1:\2-\3</b></u>", text)
        text = text.replace("-None:None</b></u></ref><br>", "</b></u></ref><br>")
        text = text.replace(":0</b></u></ref><br>", "</b></u></ref><br>")
        text = text.replace(":0-0</b></u></ref><br>", "</b></u></ref><br>")
        # deal with internal links like <a class="contents" href="C:@1002 0:0">
        text = re.sub("<a [^<>]*?href=['{0}]C:@([0-9]+?) ([\-0-9:]+?)[^\-0-9:][^<>]*?>".format('"'), self.formatMyBibleCommentaryLink, text)
        text = self.formatNonBibleMyBibleModule(text, abbreviation)
        return text

    def formatMyBibleCommentaryLink(self, match):
        bookNo, cv = match.groups()
        standardAbbreviation = BibleVerseParser(config.parserStandarisation).standardAbbreviation
        if bookNo in standardAbbreviation:
            return "<a href='javascript:void(0)' onclick='document.title={0}COMMENTARY:::{1} {2}{0}'>".format('"', standardAbbreviation[bookNo], cv)
        else:
            return "<a href='javascript:void(0)' onclick='document.title={0}COMMENTARY2:::{1}.{2}{0}'>".format('"', bookNo, cv.replace(":", "."))

    def formatNonBibleMyBibleModule(self, text, abbreviation):
        searchReplace = (
            ("<a [^<>]*?href=['{0}]B:([0-9]+?) ([0-9]+?):([0-9]+?)[^0-9][^<>]*?>".format('"'), r'<a href="javascript:void(0)" onclick="cr(\1,\2,\3)">'),
            ("<a [^<>]*?href=['{0}]B:([0-9]+?) ([0-9]+?)[^0-9:][^<>]*?>".format('"'), r'<a href="javascript:void(0)" onclick="cr(\1,\2,1)">'),
            ("<a [^<>]*?href=['{0}]B:([0-9]+?)[^0-9: ][^<>]*?>".format('"'), r'<a href="javascript:void(0)" onclick="cr(\1,1,1)">'),
            ("<a [^<>]*?href=['{0}]S:([GH][0-9]+?)[^0-9][^<>]*?>".format('"'), r"<a href='javascript:void(0)' onclick='lex({0}\1{0})'>".format('"')),
            ("<a [^<>]*?href=['{0}]S:([^'{0}<>]*?)['{0}]>".format('"'), r"<a href='javascript:void(0)' onclick='searchThirdDictionary({0}{1}{0}, {0}\1{0})'>".format('"', abbreviation)),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        return text

    def convertMyBibleBookNo(self, myBibleNo):
        # UB's book numbers: https://github.com/eliranwong/bible-verse-parser/blob/master/abbreviations/SBL-style-abbreviation.xlsx

        # official MyBible's references: https://mybible.zone/code-eng.php
        # notes from Oleg
        # 2 Ésdras (in Russian Orthodox Bible) = Έσδράς Α' (in Septuaguint) = 1 Esdras (English)
        # 3 Esdras (Russian) = 4 Esdras (Vulgata) = 2 Esdras (English)

        # Five extra non-standard numbers in Oleg's Barach module
        # 326 Susanna > 75
        # 71 Judges > 7
        # 171 Tobit > 88
        # 235 Psalms of Solomon > 90
        # 245 Odes > 91
        # 341 Daniel > 71
        # 346 Bel and Dragon > 73
        # 61 Joshua > 6

        # customised numbers used in some Eliran Wong's MyBible modules
        # e.g. https://github.com/eliranwong/LXX-Rahlfs-1935/tree/master/11_end-users_files/MyBible
        # Prayer of Manasseh = 469 > 85
        # GreekEsth = 191 > 78
        # Psalm 151 = 231 > 86
        # Psalms of Solomon = 232 > 90
        # Odes = 800 > 91

        ubNo = {
            10: 1,
            20: 2,
            30: 3,
            40: 4,
            50: 5,
            60: 6,
            61: 6, # Oleg's Barach module
            70: 7,
            71: 7, # Oleg's Barach module
            80: 8,
            90: 9,
            100: 10,
            110: 11,
            120: 12,
            130: 13,
            140: 14,
            150: 15,
            160: 16,
            190: 17,
            220: 18,
            230: 19,
            240: 20,
            250: 21,
            260: 22,
            290: 23,
            300: 24,
            310: 25,
            330: 26,
            340: 27,
            350: 28,
            360: 29,
            370: 30,
            380: 31,
            390: 32,
            400: 33,
            410: 34,
            420: 35,
            430: 36,
            440: 37,
            450: 38,
            460: 39,
            470: 40,
            480: 41,
            490: 42,
            500: 43,
            510: 44,
            520: 45,
            530: 46,
            540: 47,
            550: 48,
            560: 49,
            570: 50,
            580: 51,
            590: 52,
            600: 53,
            610: 54,
            620: 55,
            630: 56,
            640: 57,
            650: 58,
            660: 59,
            670: 60,
            680: 61,
            690: 62,
            700: 63,
            710: 64,
            720: 65,
            730: 66,
            165: 76,
            468: 77,
            170: 88,
            171: 88, # Oleg's Barach module
            180: 80,
            270: 89,
            280: 87,
            305: 72,
            315: 79,
            320: 70,
            325: 75,
            326: 75, # Oleg's Barach module
            345: 73,
            346: 73, # Oleg's Barach module
            462: 81,
            464: 82,
            466: 83,
            467: 84,
            780: 92,
            790: 85,
            469: 85, # Eliran's customised no.
            191: 78, # Eliran's customised no.
            231: 86, # Eliran's customised no.
            232: 90, # Eliran's customised no.
            235: 90, # Oleg's Barach module
            800: 91, # Eliran's customised no.
            245: 91, # Oleg's Barach module
            341: 71, # Oleg's Barach module
        }
        if myBibleNo in ubNo:
            return ubNo[myBibleNo]
        else:
            # use source number if a mapped number is not found.
            return myBibleNo

    # Read BibleBento Plus Json files
    def readJsonFile(self, inputFile):
        try:
            f = open(inputFile, "r", encoding="utf-8")
            newData = f.read()
            f.close()
            newData = json.loads(newData)
            return newData
        except:
            print("File not found! Please make sure if you enter filename correctly and try again.")
            return []

    def convertBibleBentoPlusTag(self, text):
        searchReplace = (
            ("href=['{0}]ref://([0-9]+?)\.([0-9]+?)\.([0-9]+?);['{0}]".format('"'), r'href="javascript:void(0)" onclick="bcv(\1,\2,\3)"'),
            ("href=['{0}]lexi://(.*?)['{0}]".format('"'), r'href="javascript:void(0)" onclick="lex({0}\1{0})"'.format("'")),
            ("href=['{0}]gk://(.*?)['{0}]".format('"'), r'href="javascript:void(0)" onclick="lex({0}gk\1{0})"'.format("'")),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        return text

    def importBBPlusLexiconInAFolder(self, folder):
        files = [filename for filename in os.listdir(folder) if os.path.isfile(os.path.join(folder, filename)) and not re.search("^[\._]", filename)]
        validFiles = [filename for filename in files if re.search('^Dict.*?\.json$', filename)]
        if validFiles:
            for filename in validFiles:
                module = filename[4:-5]
                jsonList = self.readJsonFile(os.path.join(folder, filename))
                jsonList = [(jsonEntry["top"], self.convertBibleBentoPlusTag(jsonEntry["def"])) for jsonEntry in jsonList]
                self.createLexiconModule(module, jsonList)
            return True

    def importBBPlusDictionaryInAFolder(self, folder):
        files = [filename for filename in os.listdir(folder) if os.path.isfile(os.path.join(folder, filename)) and not re.search("^[\._]", filename)]
        validFiles = [filename for filename in files if re.search('^Dict.*?\.json$', filename)]
        if validFiles:
            for filename in validFiles:
                module = filename[4:-5]
                jsonList = self.readJsonFile(os.path.join(folder, filename))
                jsonList = [(jsonEntry["top"], jsonEntry["def"]) for jsonEntry in jsonList]
                self.createDictionaryModule(module, jsonList)
            return True

    def convertOldLexiconData(self):
        database = os.path.join(config.marvelData, "data", "lexicon.data")
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        t = ("table",)
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        cursor.execute(query, t)
        versions = cursor.fetchall()
        exclude = ("Details")
        lexiconList = [version[0] for version in versions if not version[0] in exclude]

        for lexicon in lexiconList:
            query = "SELECT EntryID, Information FROM {0}".format(lexicon)
            cursor.execute(query)
            content = cursor.fetchall()
            self.createLexiconModule(lexicon, content)

        connection.close()

    def convertOldBookData(self):
        database = os.path.join(config.marvelData, "data", "book.data")
        connection = sqlite3.connect(database)
        cursor = connection.cursor()

        t = ("table",)
        query = "SELECT name FROM sqlite_master WHERE type=? ORDER BY name"
        cursor.execute(query, t)
        versions = cursor.fetchall()
        exclude = ("Details")
        bookList = [version[0] for version in versions if not version[0] in exclude]

        for book in bookList:
            query = "SELECT Topic, Note FROM {0}".format(book)
            cursor.execute(query)
            content = cursor.fetchall()
            self.createBookModule(book, content)

        connection.close()

    def importESwordBook(self, filename):
        *_, module = os.path.split(filename)
        module = module[:-5]

        # connect e-Sword *.refi file
        connection = sqlite3.connect(filename)
        cursor = connection.cursor()

        query = "SELECT Chapter, Content FROM Reference"
        cursor.execute(query)
        content = cursor.fetchall()
        content = [(chapter, self.formatNonBibleESwordModule(chapterContent)) for chapter, chapterContent in content]

        self.createBookModule(module, content)

        connection.close()


class ThirdPartyDictionary:

    def __init__(self, moduleTuple):
        self.module, self.fileExtension = moduleTuple
        self.moduleList = self.getModuleList()
        if self.module in self.moduleList:
            self.database = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(self.module, self.fileExtension))
            self.connection = sqlite3.connect(self.database)
            self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getModuleList(self):
        moduleFolder = os.path.join("thirdParty", "dictionaries")
        bbPlusDictionaries = [f[:-8] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".dic.bbp") and not re.search("^[\._]", f)]
        mySwordDictionaries = [f[:-12] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".dct.mybible") and not re.search("^[\._]", f)]
        eSwordDictionaries = [f[:-5] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".dcti") and not re.search("^[\._]", f)]
        eSwordLexicons = [f[:-5] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".lexi") and not re.search("^[\._]", f)]
        myBibleDictionaries = [f[:-19] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".dictionary.SQLite3") and not re.search("^[\._]", f)]
        moduleList = set(bbPlusDictionaries + mySwordDictionaries + eSwordDictionaries + eSwordLexicons + myBibleDictionaries)
        moduleList = sorted(list(moduleList))
        return moduleList

    def search(self, entry):
        if not self.database:
            return "INVALID_COMMAND_ENTERED"
        else:
            exactMatch = self.getExactWord(entry)
            similarMatch = self.getSimilarWord(entry)
            action = "searchThirdDictionary(this.value, \"{0}\")".format(entry)
            optionList = [(m, m) for m in self.moduleList]
            selectList = self.formatSelectList(action, optionList)
            config.thirdDictionary = self.module
            return "<h2>Search <span style='color: brown;'>{0}</span> for <span style='color: brown;'>{1}</span></h2><p>{4}</p><p><b>Exact match:</b><br><br>{2}</p><p><b>Partial match:</b><br><br>{3}".format(self.module, entry, exactMatch, similarMatch, selectList)

    def formatSelectList(self, action, optionList):
        selectForm = "<select onchange='{0}'>".format(action)
        for value, description in optionList:
            if value == self.module:
                selectForm += "<option value='{0}' selected='selected'>{1}</option>".format(value, description)
            else:
                selectForm += "<option value='{0}'>{1}</option>".format(value, description)
        selectForm += "</select>"
        return selectForm

    def getExactWord(self, entry):
        if not self.database:
            return "INVALID_COMMAND_ENTERED"
        else:
            getDictionaryData = {
                ".dic.bbp": self.getBibleBentoPlusDicExactWord,
                ".dcti": self.getESwordDicExactWord,
                ".lexi": self.getESwordLexExactWord,
                ".dct.mybible": self.getMySwordExactWord,
                ".dictionary.SQLite3": self.getMyBibleExactWord,
            }
            return getDictionaryData[self.fileExtension](entry)

    def getSimilarWord(self, entry):
        if not self.database:
            return "INVALID_COMMAND_ENTERED"
        else:
            getDictionaryData = {
                ".dic.bbp": self.getBibleBentoPlusDicSimilarWord,
                ".dcti": self.getESwordDicSimilarWord,
                ".lexi": self.getESwordLexSimilarWord,
                ".dct.mybible": self.getMySwordSimilarWord,
                ".dictionary.SQLite3": self.getMyBibleSimilarWord,
            }
            return getDictionaryData[self.fileExtension](entry)

    def getData(self, entry):
        if not self.database:
            return "INVALID_COMMAND_ENTERED"
        else:
            getDictionaryData = {
                ".dic.bbp": self.getBibleBentoPlusDicDictionaryData,
                ".dcti": self.getESwordDicDictionaryData,
                ".lexi": self.getESwordLexDictionaryData,
                ".dct.mybible": self.getMySwordDictionaryData,
                ".dictionary.SQLite3": self.getMyBibleDictionaryData,
            }
            return getDictionaryData[self.fileExtension](entry)

    # BibleBentoPlus dictionaries
    def getBibleBentoPlusDicExactWord(self, entry):
        query = "SELECT Topic FROM Dictionary WHERE Topic = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return "<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, content[0])

    def getBibleBentoPlusDicSimilarWord(self, entry):
        query = "SELECT Topic FROM Dictionary WHERE Topic LIKE ? AND Topic != ?"
        self.cursor.execute(query, ("%{0}%".format(entry), entry))
        contentList = ["<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, m[0]) for m in self.cursor.fetchall()]
        if not contentList:
            return "[not found]"
        else:
            return "<br>".join(contentList)

    def getBibleBentoPlusDicDictionaryData(self, entry):
        query = "SELECT Definition FROM Dictionary WHERE Topic = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            action = "searchThirdDictionary(this.value, \"{0}\")".format(entry)
            optionList = [(m, m) for m in self.moduleList]
            selectList = self.formatSelectList(action, optionList)
            config.thirdDictionary = self.module
            content = Converter().convertBibleBentoPlusTag(content[0])
            return "<h2>{0}</h2><p>{1}</p><p>{2}</p>".format(entry, selectList, content)

    # e-Sword dictionaries
    def getESwordDicExactWord(self, entry):
        query = "SELECT Topic FROM Dictionary WHERE Topic = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return "<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, content[0])

    def getESwordDicSimilarWord(self, entry):
        query = "SELECT Topic FROM Dictionary WHERE Topic LIKE ? AND Topic != ?"
        self.cursor.execute(query, ("%{0}%".format(entry), entry))
        contentList = ["<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, m[0]) for m in self.cursor.fetchall()]
        if not contentList:
            return "[not found]"
        else:
            return "<br>".join(contentList)

    def getESwordDicDictionaryData(self, entry):
        query = "SELECT Definition FROM Dictionary WHERE Topic = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            action = "searchThirdDictionary(this.value, \"{0}\")".format(entry)
            optionList = [(m, m) for m in self.moduleList]
            selectList = self.formatSelectList(action, optionList)
            config.thirdDictionary = self.module
            content = Converter().formatNonBibleESwordModule(content[0])
            return "<h2>{0}</h2><p>{1}</p><p>{2}</p>".format(entry, selectList, content)

    # e-Sword lexicon
    def getESwordLexExactWord(self, entry):
        query = "SELECT Topic FROM Lexicon WHERE Topic = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return "<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, content[0])

    def getESwordLexSimilarWord(self, entry):
        query = "SELECT Topic FROM Lexicon WHERE Topic LIKE ? AND Topic != ?"
        self.cursor.execute(query, ("%{0}%".format(entry), entry))
        contentList = ["<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, m[0]) for m in self.cursor.fetchall()]
        if not contentList:
            return "[not found]"
        else:
            return "<br>".join(contentList)

    def getESwordLexDictionaryData(self, entry):
        query = "SELECT Definition FROM Lexicon WHERE Topic = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            action = "searchThirdDictionary(this.value, \"{0}\")".format(entry)
            optionList = [(m, m) for m in self.moduleList]
            selectList = self.formatSelectList(action, optionList)
            config.thirdDictionary = self.module
            content = Converter().formatNonBibleESwordModule(content[0])
            return "<h2>{0}</h2><p>{1}</p><p>{2}</p>".format(entry, selectList, content)

    # MySword dictionaries
    def getMySwordExactWord(self, entry):
        query = "SELECT word FROM dictionary WHERE word = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return "<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, content[0])

    def getMySwordSimilarWord(self, entry):
        query = "SELECT word FROM dictionary WHERE word LIKE ? AND word != ?"
        self.cursor.execute(query, ("%{0}%".format(entry), entry))
        contentList = ["<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, m[0]) for m in self.cursor.fetchall()]
        if not contentList:
            return "[not found]"
        else:
            return "<br>".join(contentList)

    def getMySwordDictionaryData(self, entry):
        query = "SELECT data FROM dictionary WHERE word = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            action = "searchThirdDictionary(this.value, \"{0}\")".format(entry)
            optionList = [(m, m) for m in self.moduleList]
            selectList = self.formatSelectList(action, optionList)
            config.thirdDictionary = self.module
            content = content[0]
            content = re.sub(r"<a [^<>]*?href=(['{0}])[#]*?[ds]([^\n<>]*?)\1>(.*?)</a>".format('"'), r"<ref onclick='openThirdDictionary({1}{0}{1}, {1}\2{1})'>\3</ref>".format(self.module, '"'), content)
            content = Converter().formatNonBibleMySwordModule(content)
            return "<h2>{0}</h2><p>{1}</p><p>{2}</p>".format(entry, selectList, content)

    # MyBible Dictionaries
    def getMyBibleExactWord(self, entry):
        query = "SELECT topic FROM dictionary WHERE topic = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return "<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, content[0])

    def getMyBibleSimilarWord(self, entry):
        query = "SELECT topic FROM dictionary WHERE topic LIKE ? AND topic != ?"
        self.cursor.execute(query, ("%{0}%".format(entry), entry))
        contentList = ["<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, m[0]) for m in self.cursor.fetchall()]
        if not contentList:
            return "[not found]"
        else:
            return "<br>".join(contentList)

    def getMyBibleDictionaryData(self, entry):
        query = "SELECT definition FROM dictionary WHERE topic = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            action = "searchThirdDictionary(this.value, \"{0}\")".format(entry)
            optionList = [(m, m) for m in self.moduleList]
            selectList = self.formatSelectList(action, optionList)
            config.thirdDictionary = self.module
            content = Converter().formatNonBibleMyBibleModule(content[0], self.module)
            return "<h2>{0}</h2><p>{1}</p><p>{2}</p>".format(entry, selectList, content)
