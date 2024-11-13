from xml.dom.minidom import Node
import os, apsw, re, json, base64, logging
from uniquebible import config

if __name__ == '__main__':
    from uniquebible import config
    from uniquebible.util.ConfigUtil import ConfigUtil
    from uniquebible.util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.noQt = False
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")

from pathlib import Path
from shutil import copyfile
from uniquebible.db.BiblesSqlite import BiblesSqlite
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.db.BiblesSqlite import Bible
from xml.dom import minidom
from uniquebible.db.DevotionalSqlite import DevotionalSqlite
from uniquebible.db.ToolsSqlite import Commentary, Lexicon
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.TextUtil import TextUtil


class Converter:

    def __init__(self):
        self.logger = logging.getLogger('uba')

    # create UniqueBible.app commentary module
    def createCommentaryModule(self, abbreviation, title, description, content):
        config.commentariesFolder = os.path.join(config.marvelData, "commentaries")
        ubCommentary = os.path.join(config.commentariesFolder, "c{0}.commentary".format(abbreviation))
        if os.path.isfile(ubCommentary):
            os.remove(ubCommentary)
        with apsw.Connection(ubCommentary) as connection:
            # create a cusor object
            cursor = connection.cursor()
            # create two tables: "Details" & "Commentary"
            statements = (
                Bible.CREATE_DETAILS_TABLE,
                Bible.CREATE_COMMENTARY_TABLE
            )
            for create in statements:
                cursor.execute(create)
#                cursor.execute("COMMIT")
            # insert data to table "Details"
            insert = "INSERT INTO Details (Title, Abbreviation, Information, Version, OldTestament, NewTestament, Apocrypha, Strongs, Language) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(insert, (title, abbreviation, description, 1, 1, 1, 0, 0, ''))
#            cursor.execute("COMMIT")
            # insert data to table "Commentary"
            if content:
                insert = "INSERT INTO Commentary (Book, Chapter, Scripture) VALUES (?, ?, ?)"
                cursor.executemany(insert, content)
#                cursor.execute("COMMIT")

    def createBookModuleFromImages(self, folder):
        module = os.path.basename(folder)
        bookContent = []
        for filepath in sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not re.search(r"^[\._]", f)]):
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
        for filepath in sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not re.search(r"^[\._]", f)]):
            fileBasename = os.path.basename(filepath)
            self.logger.info("Converting {0}".format(fileBasename))
            fileName, fileExtension = os.path.splitext(fileBasename)
            if fileExtension.lower() in (".htm", ".html", ".xhtml"):
                with open(os.path.join(folder, filepath), "r", encoding="utf-8") as fileObject:
                    html = fileObject.read()
                    # Convert links
                    html = TextUtil.formulateUBACommandHyperlink(html)
                    if config.parseTextConvertHTMLToBook:
                        html = BibleVerseParser(config.parserStandarisation).parseText(html, False)
                    bookContent.append((fileName, html))
        if bookContent and module:
            self.createBookModule(module, bookContent)
            return True
        else:
            return False

    def createBookModuleFromNotes(self, folder, workspace=False):
        module = os.path.basename(folder)
        bookContent = []
        for filepath in sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not re.search(r"^[\._]", f)]):
            fileBasename = os.path.basename(filepath)
            fileName, fileExtension = os.path.splitext(fileBasename)
            isNoteFile = True if (not workspace and fileExtension.lower() == ".uba") or (workspace and (fileExtension.lower() == ".reader" or fileExtension.lower() == ".editor")) else False
            if isNoteFile:
                self.logger.info("Reading file {0}".format(filepath))
                with open(os.path.join(folder, filepath), "r", encoding="utf-8") as fileObject:
                    note = fileObject.read()
                    note = TextUtil.formulateUBACommandHyperlink(note)
                    if config.parseTextConvertNotesToBook:
                        note = BibleVerseParser(config.parserStandarisation).parseText(note, False, False, True)
                    bookContent.append((fileName[7:] if workspace else fileName, note))
        if bookContent and module:
            self.logger.info("Creating module {0}".format(module))
            self.createBookModule(module, bookContent)
            return True
        else:
            return False

    def createDevotionalFromNotes(self, folder):
        module = os.path.basename(folder)
        devotionalContent = []
        for filepath in sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not re.search(r"^[\._]", f)]):
            fileBasename = os.path.basename(filepath)
            fileName, fileExtension = os.path.splitext(fileBasename)
            if fileExtension.lower() == ".uba":
                with open(os.path.join(folder, filepath), "r", encoding="utf-8") as fileObject:
                    note = fileObject.read()
                    note = TextUtil.formulateUBACommandHyperlink(note)
                    if config.parseTextConvertNotesToBook:
                        note = BibleVerseParser(config.parserStandarisation).parseText(note)
                    try:
                        month = int(fileName[0:2])
                        day = int(fileName[3:5])
                    except:
                        return False
                    devotionalContent.append((month, day, note))
        if devotionalContent and module:
            DevotionalSqlite.createDevotional(module, devotionalContent)
            return True
        else:
            return False

    def createCommentaryFromNotes(self, folder):
        module = os.path.basename(folder)
        commentaryContent = []
        for filepath in sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not re.search(r"^[\._]", f)]):
            fileBasename = os.path.basename(filepath)
            fileName, fileExtension = os.path.splitext(fileBasename)
            if fileExtension.lower() == ".uba":
                with open(os.path.join(folder, filepath), "r", encoding="utf-8") as fileObject:
                    note = fileObject.read()
                    note = TextUtil.formulateUBACommandHyperlink(note)
                    if config.parseTextConvertNotesToBook:
                        note = BibleVerseParser(config.parserStandarisation).parseText(note)
                    try:
                        if "_" in fileName:
                            fields = fileName.split("_")
                        elif " " in fileName:
                            fields = fileName.split(" ")
                        else:
                            fields = [fileName, 0]
                        book = fields[0]
                        bibleVerseParser = BibleVerseParser(config.parserStandarisation)
                        bookNum = bibleVerseParser.bookNameToNum(book)
                        chapter = fields[1]
                        commentaryContent.append((bookNum, chapter, note))
                    except Exception as e:
                        logging.info("Could not convert {0} - {1}".format(fileName, e))
        if commentaryContent and module:
            Commentary.createCommentary(module, commentaryContent)
            Commentary().reloadFileLookup()
            return True
        else:
            return False

    def createLexiconFromNotes(self, folder):
        module = os.path.basename(folder)
        lexiconContent = []
        for filepath in sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not re.search(r"^[\._]", f)]):
            fileBasename = os.path.basename(filepath)
            fileName, fileExtension = os.path.splitext(fileBasename)
            if fileExtension.lower() == ".uba":
                with open(os.path.join(folder, filepath), "r", encoding="utf-8") as fileObject:
                    note = fileObject.read()
                    note = TextUtil.formulateUBACommandHyperlink(note)
                    if config.parseTextConvertNotesToBook:
                        note = BibleVerseParser(config.parserStandarisation).parseText(note)
                    lexiconContent.append((fileName, note))
        if lexiconContent and module:
            Lexicon.createLexicon(module, lexiconContent)
            return True
        else:
            return False

    def createBookModuleFromPDF(self, folder):
        module = os.path.basename(folder)
        bookContent = []
        for filepath in sorted([f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f)) and not re.search(r"^[\._]", f)]):
            fileBasename = os.path.basename(filepath)
            fileName, fileExtension = os.path.splitext(fileBasename)
            if fileExtension.lower() == ".pdf":
                with open(os.path.join(folder, filepath), "rb") as fileObject:
                    note = fileObject.read()
                    bookContent.append((fileName, note))
        if bookContent and module:
            self.createBookModule(module, bookContent)
            return True
        else:
            return False

    def createBookModuleFromHymnLyricsFile(self, inputFile):
        filename = os.path.join(inputFile)
        file = open(filename, "r")
        module = Path(filename).stem
        lines = file.readlines()
        bookContent = []
        count = 0
        chapter = ""
        readLyrics = False
        for line in lines:
            if line.startswith("Title:"):
                title = line[7:].strip()
                # title = title.replace("'", "")
            elif line.startswith("Author:") and len(line) > 9:
                chapter += line + "<br><br>"
            elif line.startswith("Lyrics:"):
                readLyrics = True
            elif line.startswith('---'):
                bookContent.append((title, chapter))
                readLyrics = False
                chapter = ""
                count += 1
                print(title)
            elif readLyrics:
                line = re.sub("<.*?>", "", line)
                chapter += line + "<br>"
        if bookContent and module:
            print(count)
            self.createBookModule(module, bookContent)
            return True
        else:
            return False

    # create UniqueBible.app book modules
    def createBookModule(self, module, content, blobData=None):
        self.logger.info("Creating book {0}".format(module))
        content = [(re.sub("['{0}]".format('"'), "_", chapter), chapterContent) for chapter, chapterContent in content]
        book = os.path.join(config.marvelData, "books", "{0}.book".format(module))
        if os.path.isfile(book):
            os.remove(book)
        with apsw.Connection(book) as connection:
            cursor = connection.cursor()
            # Create table for book content
            create = "CREATE TABLE Reference (Chapter NVARCHAR(100), Content TEXT)"
            cursor.execute(create)
#            cursor.execute("COMMIT")
            # insert data for book content
            self.logger.info("Inserting reference data")
            insert = "INSERT INTO Reference (Chapter, Content) VALUES (?, ?)"
            cursor.executemany(insert, content)
#            cursor.execute("COMMIT")
            if blobData:
                # Create table for book content
                create = "CREATE TABLE data (Filename TEXT, Content BLOB)"
                cursor.execute(create)
#                cursor.execute("COMMIT")
                # insert data for book content
                self.logger.info("Inserting blob data")
                insert = "INSERT INTO data (Filename, Content) VALUES (?, ?)"
                cursor.executemany(insert, blobData)
#                cursor.execute("COMMIT")

    # create UniqueBible.app dictionary module
    def createDictionaryModule(self, module, content):
        filename = os.path.join("thirdParty", "dictionaries", "{0}.dic.bbp".format(module))
        if os.path.isfile(filename):
            os.remove(filename)
        with apsw.Connection(filename) as connection:
            cursor = connection.cursor()
            # create table "Dictionary"
            create = "CREATE TABLE Dictionary (Topic NVARCHAR(100), Definition TEXT)"
            cursor.execute(create)
#            cursor.execute("COMMIT")
            # insert data to table "Dictionary"
            insert = "INSERT INTO Dictionary (Topic, Definition) VALUES (?, ?)"
            cursor.executemany(insert, content)
#            cursor.execute("COMMIT")

    # create UniqueBible.app lexicon modules
    def createLexiconModule(self, module, content):
        book = os.path.join(config.marvelData, "lexicons", "{0}.lexicon".format(module))
        if os.path.isfile(book):
            os.remove(book)
        with apsw.Connection(book) as connection:
            cursor = connection.cursor()
            # create table "Lexicon"
            create = "CREATE TABLE Lexicon (Topic NVARCHAR(100), Definition TEXT)"
            cursor.execute(create)
#            cursor.execute("COMMIT")
            # insert data to table "Lexicon
            insert = "INSERT INTO Lexicon (Topic, Definition) VALUES (?, ?)"
            cursor.executemany(insert, content)
#            cursor.execute("COMMIT")

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

    # Export from uniquebible.installed bibles into JSON format; for use with DartBible project.
    # usage:
    # from ThirdParty import Converter
    # Converter().exportJsonBible("KJV")
    def exportMultipleBibles(self, bibleList):
        for bible in bibleList:
            self.exportJsonBible(bible)

    def exportJsonBible(self, bible):
        filename = os.path.join(config.marvelData, "bibles", "{0}.bible".format(bible))
        connection = apsw.Connection(filename)
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
        connection = apsw.Connection(filename)
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
        p = re.compile(r'｛｝([^｛｝]*?)(<vid id="v[0-9]+?\.[0-9]+?\.[0-9]+?"></vid>)(<vid)')
        s = p.search(chapterText)
        while s:
            chapterText = p.sub(r"｛｝\2｜\1\3", chapterText)
            s = p.search(chapterText)
        chapterText = chapterText.replace("｛｝", "<hr>")
        chapterText = chapterText.replace("</vid>｜", "</vid>")
        return chapterText

    def importAllFilesInAFolder(self, folder):
        files = [filename for filename in os.listdir(folder) if os.path.isfile(os.path.join(folder, filename)) and not re.search(r"^[\._]", filename)]
        validFiles = [filename for filename in files if re.search(r'(\.dct\.mybible|\.dcti|\.lexi|\.dictionary\.SQLite3|\.bbl\.mybible|\.cmt\.mybible|\.bok\.mybible|\.bbli|\.cmti|\.refi|\.commentaries\.SQLite3|\.SQLite3|\.xml|\.pdf|\.docx)$', filename)]
        if validFiles:
            for filename in validFiles:
                filename = os.path.join(folder, filename)
                try:
                    if re.search(r'(\.dct\.mybible|\.dcti|\.lexi|\.dictionary\.SQLite3)$', filename):
                        self.importThirdPartyDictionary(filename)
                    elif filename.endswith(".pdf"):
                        self.importPdf(filename)
                    elif filename.endswith(".docx"):
                        self.importDocx(filename)
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
                    elif filename.endswith(".xml"):
                        self.importXMLBible(filename)
                    else:
                        print("File type of '{0}' is not supported for conversion.".format(filename))
                except:
                    print("Failed to convert '{0}'.".format(filename))
            return True

    def importDocx(self, fileName):
        *_, name = os.path.split(fileName)
        destination = os.path.join(config.marvelData, "docx", name)
        try:
            copyfile(fileName, destination)
        except:
            print("Failed to copy '{0}'.".format(fileName))

    def importPdf(self, fileName):
        *_, name = os.path.split(fileName)
        destination = os.path.join(config.marvelData, "pdf", name)
        try:
            copyfile(fileName, destination)
        except:
            print("Failed to copy '{0}'.".format(fileName))

    def importThirdPartyDictionary(self, filename):
        *_, name = os.path.split(filename)
        destination = os.path.join("thirdParty", "dictionaries", name)
        try:
            copyfile(filename, destination)
        except:
            print("Failed to copy '{0}'.".format(filename))

    # Import e-Sword Bibles [Apple / macOS / iOS]
    def importESwordBible(self, filename):
        self.logger.info("Importing eSword Bible: " + filename)
        connection = apsw.Connection(filename)
        connection.text_factory = lambda b: b.decode(errors='ignore')
        cursor = connection.cursor()

        if self.checkColumnExists("Details", "Title", cursor):
            query = "SELECT Title, Abbreviation FROM Details"
        else:
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
        plainVerses = []
        for book, chapter, verse, scripture in verses:
            scripture = scripture.strip()
            if scripture.count("{") > 4:
                scripture = self.convertFromRichTextFormat(scripture, False)
            plainVerses.append((book, chapter, verse, scripture))

        self.eSwordBibleToPlainFormat(description, abbreviation, plainVerses)
        connection.close()
        if config.importRtlOT:
            config.rtlTexts.append(abbreviation)
        self.logger.info("Importing successful")

    def eSwordBibleToPlainFormat(self, description, abbreviation, verses):
        verses = [(book, chapter, verse, self.stripESwordBibleTags(scripture)) for book, chapter, verse, scripture in verses]
        biblesSqlite = BiblesSqlite()
        biblesSqlite.importBible(description, abbreviation, verses)
        del biblesSqlite

    def eSwordBibleToRichFormat(self, description, abbreviation, verses, notes, extended=False):
        formattedBible = os.path.join(config.marvelData, "bibles", "{0}.bible".format(abbreviation))
        if os.path.isfile(formattedBible):
            os.remove(formattedBible)
        connection = apsw.Connection(formattedBible)
        cursor = connection.cursor()

        statements = (
            Bible.CREATE_BIBLE_TABLE,
            Bible.CREATE_VERSES_TABLE,
            Bible.CREATE_DETAILS_TABLE,
            Bible.CREATE_NOTES_TABLE,
        )
        for create in statements:
            cursor.execute(create)
#            cursor.execute("COMMIT")

        formattedChapters = {}
        for book, chapter, verse, scripture in verses:
            # if extended:
            #     scripture = self.convertSuperStrongs(scripture)
            scripture = scripture.strip()
            if scripture.count("{") > 4:
                scripture = self.convertFromRichTextFormat(scripture)
            else:
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
#            cursor.execute("COMMIT")

        formattedChapters = [(book, chapter, formattedChapters[(book, chapter)]) for book, chapter in formattedChapters]
        insert = "INSERT INTO Bible (Book, Chapter, Scripture) VALUES (?, ?, ?)"
        cursor.executemany(insert, formattedChapters)
#        cursor.execute("COMMIT")

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
            ("{.*?super (.*?)}", r"<gloss onclick='lex({0}\1{0})'>\1</gloss>".format('"')),
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
            ("{.*?super (.*?)}", r"<gloss onclick='lex({0}\1{0})'>\1</gloss>".format('"')),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        text = text.strip()
        return text

    def convertFromRichTextFormat(self, text, includeStrongs = True):
        out = ""
        foundBrace = False
        index = 0
        element = ""
        while index < len(text):
            c = text[index]
            if c == "{":
                foundBrace = True
            elif c == "}":
                out += self.parseRtfElement(element, includeStrongs)
                foundBrace = False
                element = ""
            elif foundBrace:
                element += c
            index += 1
        out = out.replace("\\bullet", "")
        return out

    def parseRtfElement(self, element, includeStrongs):
        out = ""
        if " " in element:
            element = element.replace("  ", " ")
            tokens = element.split(" ")
            command = tokens[0]
            text = " ".join(tokens[1:])
            if command == "\\cf2":
                out = self.decodeString(text)
                out += " "
            elif includeStrongs and "\\cf11" in command:
                out = self.extractStrongs(text) + " "
            out = out.replace(",", " ")
        return out

    def decodeString(self, text):
        if "'" in text:
            out = re.sub("\\'([a-z0-9]{2})", lambda x: self.decodeHex(x.group(1)), text)
            out = out.replace("\\", "")
        else:
            out = text
        return out

    def decodeHex(self, hex):
        return chr(int(hex, 16))

    def extractStrongs(self, text):
        out = ""
        if ":" in text:
            out = text.split(":")[0]
            # if re.search("[GH][0-9]*", text):
            #     out = re.sub(".*([GH][0-9]*).*", "\\1", text)
        else:
            out = text
        return out

    # Import e-Sword Commentaries
    def importESwordCommentary(self, filename):
        # connect e-Sword commentary
        with apsw.Connection(filename) as connection:
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
        self.logger.info("Importing MySword Bible: " + filename)
        connection = apsw.Connection(filename)
        cursor = connection.cursor()

        query = "SELECT Description, Abbreviation FROM Details"
        cursor.execute(query)
        description, abbreviation = cursor.fetchone()
        abbreviation = abbreviation.replace("-", "")
        abbreviation = abbreviation.replace("'", "")
        abbreviation = abbreviation.replace('"', "")
        abbreviation = abbreviation.replace("+", "x")
        query = "SELECT Book, Chapter, Verse, Scripture FROM Bible ORDER BY Book, Chapter, Verse"
        cursor.execute(query)
        verses = cursor.fetchall()
        connection.close()

        self.mySwordBibleToRichFormat(description, abbreviation, verses)
        self.mySwordBibleToPlainFormat(description, abbreviation, verses)
        if config.importRtlOT:
            config.rtlTexts.append(abbreviation)
        self.logger.info("Import successful")

    def mySwordBibleToPlainFormat(self, description, abbreviation, verses):
        verses = [(book, chapter, verse, scripture) for book, chapter, verse, scripture in verses]
        biblesSqlite = BiblesSqlite()
        biblesSqlite.importBible(description, abbreviation, verses)
        del biblesSqlite

    def mySwordBibleToRichFormat(self, description, abbreviation, verses, strongs=None):
        formattedBible = os.path.join(config.marvelData, "bibles", "{0}.bible".format(abbreviation))
        if os.path.isfile(formattedBible):
            os.remove(formattedBible)
        connection = apsw.Connection(formattedBible)
        cursor = connection.cursor()

        statements = (
            Bible.CREATE_BIBLE_TABLE,
            Bible.CREATE_NOTES_TABLE,
            Bible.CREATE_DETAILS_TABLE,
        )
        for create in statements:
            cursor.execute(create)
#            cursor.execute("COMMIT")

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
#        cursor.execute("COMMIT")

        formattedChapters = [(book, chapter, formattedChapters[(book, chapter)]) for book, chapter in formattedChapters]
        insert = "INSERT INTO Bible (Book, Chapter, Scripture) VALUES (?, ?, ?)"
        cursor.executemany(insert, formattedChapters)
#        cursor.execute("COMMIT")

        self.populateDetails(cursor, description, abbreviation, "", 0)

        connection.close()

    def populateDetails(self, cursor, description, abbreviation, language="", strongs=None):
        cursor.execute("SELECT COUNT(DISTINCT(Book)) FROM Bible")
        count = cursor.fetchone()[0]

        information = description
        version = 1
        oldTestamentFlag = 1
        newTestamentFlag = 1
        apocryphaFlag = 0
        if strongs is None:
            strongsFlag = 1 if config.importDoNotStripStrongNo else 0
        else:
            strongsFlag = strongs
        if count <= 27:
            oldTestamentFlag = 0
        elif count == 39:
            newTestamentFlag = 0
        elif count > 66:
            apocryphaFlag = 1

        insert = "INSERT INTO Details VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(insert, (description[:100], abbreviation[:50], information, version, oldTestamentFlag,
                                newTestamentFlag, apocryphaFlag, strongsFlag, language, "", ""))
#        cursor.execute("COMMIT")

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
            (r"<W([GH][0-9]+?[a-z]*?)>", r"<sup><ref onclick='lex({0}\1{0})'>\1</ref></sup>".format('"')),
            (r"<WT([^\n<>]*?)>", r"<sup><ref onclick='rmac({0}\1{0})'>\1</ref></sup>".format('"')),
            (r"<RX ([0-9]+?)\.([0-9]+?)\.([0-9]+?)>", r"『\1｜\2｜\3』"),
            (r"<RX ([0-9]+?)\.([0-9]+?)\.([0-9]+?)-[0-9]+?>", r"『\1｜\2｜\3』"),
            (r"<RX ([0-9]+?)\.([0-9]+?)\.([0-9]+?)-[0-9]+?:[0-9]+?>", r"『\1｜\2｜\3』"),
            (r"『([0-9]+?)｜([0-9]+?)｜([0-9]+?)』", self.convertMySwordRxTag),
            (r"<sup>(<RF[^\n<>]*?>)|(<RF[^\n<>]*?>)<sup>", r"\1"),
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
        with apsw.Connection(filename) as connection:
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
        with apsw.Connection(filename) as connection:
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
        text = re.sub(r"<a [^<>]*?href=['{0}][#]*?b([0-9]+?)\.([0-9]+?)\.([0-9]+?)[^0-9][^<>]*?>".format('"'), r'<a href="javascript:void(0)" onclick="bcv(\1,\2,\3)">', text)
        # convert commentary reference tag like <a href='#c-CSBC Gen 1:1'>
        text = re.sub(r"<a [^<>]*?href=(['{0}])[#]*?c\-([^ ]+?) ([0-9]*?[A-Za-z]+? [0-9][^<>]*?)\1>".format('"'), r"<a href='javascript:void(0)' onclick='document.title={0}COMMENTARY:::\2:::\3{0}'>".format('"'), text)
        # convert commentary reference tag like <a href='#cGen 1:1'>
        text = re.sub(r"<a [^<>]*?href=(['{0}])[#]*?c([0-9]*?[A-Za-z]+? [0-9][^<>]*?)\1>".format('"'), r"<a href='javascript:void(0)' onclick='document.title={0}COMMENTARY:::\2{0}'>".format('"'), text)
        # convert commentary reference tag like <a href='#c1.1.1'>
        text = re.sub(r"<a [^<>]*?href=['{0}][#]*?c([0-9]+?)\.([0-9]+?)\.([0-9]+?)[^0-9][^<>]*?>".format('"'), r'<a href="javascript:void(0)" onclick="cbcv(\1,\2,\3)">', text)
        # convert Strong's no tag, e.g. <a class='strong' href='#sH1'>H1</a>
        text = re.sub(r"<a [^<>]*?href=(['{0}])[#]*?s([HG][0-9a-z\.]+?)\1[^<>]*?>".format('"'), r'<a href="javascript:void(0)" onclick="lex({0}\2{0})">'.format("'"), text)
        # return formatted text
        return text

    # Import MyBible Bibles
    def importMyBibleBible(self, filename):
        connection = apsw.Connection(filename)
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
            noteConnection = apsw.Connection(noteFile)
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

    def importXMLBible(self, filename):
        file = open(filename, "r")
        contents = file.read()
        if "2001" in filename:
            contents = contents.replace("…", "...")
            for token in ("‘", "’"):
                contents = contents.replace(token, "'")
            for token in ("&nbsp;", "<b>", "</b>", "<i>", "</i>"):
                contents = contents.replace(token, " ")
        doc = minidom.parseString(contents)
        if len(doc.getElementsByTagName("XMLBIBLE")) > 0:
            self.importZefaniaBible(filename, doc)
        elif len(doc.getElementsByTagName("osis")) > 0:
            self.importOsisBible(filename, doc)
        elif "2001" in filename and len(doc.getElementsByTagName("bible")) == 1:
            self.import2001Bible(filename, doc)
        elif len(doc.getElementsByTagName("bible")) > 0 and len(doc.getElementsByTagName("testament")) > 0:
            self.importBebliaBible(filename, doc)
        else:
            self.logger.error("Cannot process XML file {0}".format(filename))

    # Import Beblia XML Bibles
    # https://github.com/Beblia/Holy-Bible-XML-Format
    def importBebliaBible(self, filename, doc):
        self.logger.info("Importing Beblia XML Bible: " + filename)
        work = doc.getElementsByTagName("bible")[0]
        description = work.getAttribute("translation")
        biblename = Path(filename).stem
        biblename = biblename.upper()
        if not description:
            description = biblename
        self.logger.info("Creating " + biblename)
        abbreviation = biblename
        books = doc.getElementsByTagName("book")
        data = []
        for book in books:
            bookNum = book.getAttribute("number")
            chapters = book.getElementsByTagName("chapter")
            for chapter in chapters:
                chapterNum = chapter.getAttribute("number")
                verses = chapter.getElementsByTagName("verse")
                for verse in verses:
                    verseNum = verse.getAttribute("number")
                    if verse.firstChild:
                        scripture = verse.firstChild.nodeValue.strip()
                        row = [bookNum, chapterNum, verseNum, scripture]
                        data.append(row)
        self.mySwordBibleToRichFormat(description, abbreviation, data)
        self.mySwordBibleToPlainFormat(description, abbreviation, data)
        self.logger.info("Import successful")

    # Import 2001 Translation
    # https://2001translation.org/
    # Note: requires a lot of XML cleanup prior to being imported
    def import2001Bible(self, filename, doc):
        self.logger.info("Importing 2001 XML Bible: " + filename)
        work = doc.getElementsByTagName("bible")[0]
        biblename = "2001"
        description = "https://2001translation.org/"
        self.logger.info("Creating " + biblename)
        abbreviation = biblename
        books = doc.getElementsByTagName("book")
        data = []
        for bookNum in range(1,67):
            bookInfo = BibleBooks.abbrev["eng"][str(bookNum)]
            bookName = bookInfo[1]
            bookTag = "_" + bookName.lower().replace(" ", "")
            print("{0}-{1}".format(bookTag, bookNum))
            book = doc.getElementsByTagName(bookTag)[0]
            chapters = BibleBooks.chapters[bookNum]
            for chapterNum in range(1, chapters+1):
                chapterStr = "chapter{0}".format(chapterNum)
                chapter = book.getElementsByTagName(chapterStr)[0]
                # print(chapterStr)
                verses = BibleBooks.verses[bookNum][chapterNum]
                for verseNum in range(1, verses+1):
                    scripture = ""
                    try:
                        verse = chapter.getElementsByTagName("v{0}".format(verseNum))[0]
                        for curNode in verse.childNodes:
                            if (curNode.nodeType == Node.TEXT_NODE):
                                scripture += curNode.nodeValue
                            elif (curNode.nodeType == Node.ELEMENT_NODE):
                                if curNode.localName == 'a':
                                    if curNode.firstChild.nodeValue:
                                        scripture += "<a href='" + curNode.attributes['href'].nodeValue + "'>"
                                        scripture += curNode.firstChild.nodeValue
                                        scripture += "</a>"
                    except Exception as ex:
                        print("Error {0}-{1} {2}:{3}".format(bookName, bookNum, chapterNum, verseNum))
                    row = [bookNum, chapterNum, verseNum, scripture]
                    data.append(row)
        self.mySwordBibleToRichFormat(description, abbreviation, data)
        self.mySwordBibleToPlainFormat(description, abbreviation, data)
        self.logger.info("Import successful")

    # Import OSIS XML Bibles
    # https://github.com/gratis-bible/bible/tree/master/en
    def importOsisBible(self, filename, doc):
        self.logger.info("Importing OSIS XML Bible: " + filename)
        work = doc.getElementsByTagName("work")[0]
        description = work.getElementsByTagName("title")[0].firstChild.nodeValue.strip()
        biblename = Path(filename).stem
        biblename = biblename.upper()
        if not description:
            description = biblename
        self.logger.info("Creating " + biblename)
        abbreviation = biblename
        books = doc.getElementsByTagName("div")
        data = []
        parser = BibleVerseParser(config.parserStandarisation)
        for book in books:
            chapters = book.getElementsByTagName("chapter")
            for chapter in chapters:
                verses = chapter.getElementsByTagName("verse")
                for verse in verses:
                    if verse.firstChild:
                        osisID = verse.getAttribute("osisID")
                        (bookName, chapterNum, verseNum) = osisID.split(".")
                        scripture = verse.firstChild.nodeValue.strip()
                        bookNum = parser.bookNameToNum(bookName)
                        row = [bookNum, chapterNum, verseNum, scripture]
                        data.append(row)
        self.mySwordBibleToRichFormat(description, abbreviation, data)
        self.mySwordBibleToPlainFormat(description, abbreviation, data)
        self.logger.info("Import successful")

    # Import Zefania XML Bibles
    # https://www.ph4.org/b4_mobi.php?q=zefania
    # http://sourceforge.net/projects/zefania-sharp/files/
    def importZefaniaBible(self, filename, doc):
        self.logger.info("Importing Zefania XML Bible: " + filename)
        translation = doc.getElementsByTagName("XMLBIBLE")[0]
        description = translation.getAttribute("biblename")
        biblename = Path(filename).stem
        biblename = biblename.replace("Bible_English_", "")
        biblename = biblename.replace("_", "")
        if not description:
            description = biblename
        self.logger.info("Creating " + biblename)
        abbreviation = biblename
        books = doc.getElementsByTagName("BIBLEBOOK")
        data = []
        for book in books:
            chapters = book.getElementsByTagName("CHAPTER")
            book_number = book.getAttribute("bnumber")
            for chapter in chapters:
                chapter_number = chapter.getAttribute("cnumber")
                verses = chapter.getElementsByTagName("VERS")
                for verse in verses:
                    verse_number = verse.getAttribute("vnumber")
                    if verse.firstChild:
                        scripture = verse.firstChild.nodeValue.strip()
                        row = [book_number, chapter_number, verse_number, scripture]
                        data.append(row)
        self.mySwordBibleToRichFormat(description, abbreviation, data)
        self.mySwordBibleToPlainFormat(description, abbreviation, data)
        self.logger.info("Import successful")

    def importTheWordBible(self, filename):
        biblename = Path(filename).stem
        extension = Path(filename).suffix
        chapter = 1
        verse = 1
        if extension == ".nt":
            book = 40
        else:
            book = 1
        data = []
        count = 0
        with open(filename, errors='ignore') as f:
            for line in f:
                count += 1
                line = line.strip()
                if "�" in line:
                    line = ""
                else:
                    line = self.stripTheWordTags(line)
                row = [book, chapter, verse, line]
                # print("{0} - {1}:{2}:{3}:{4}".format(count, book, chapter, verse, line))
                data.append(row)
                verse += 1
                if verse > BibleBooks.verses[book][chapter]:
                    chapter += 1
                    verse = 1
                    if chapter > BibleBooks.chapters[book]:
                        book += 1
                        chapter = 1
                if book > 66:
                    break
        self.mySwordBibleToRichFormat(biblename, biblename, data)
        self.mySwordBibleToPlainFormat(biblename, biblename, data)
        if config.importRtlOT:
            config.rtlTexts.append(biblename)
        self.logger.info("Import successful")

    def importTXTBible(self, filename):
        biblename = Path(filename).stem
        extension = Path(filename).suffix
        data = []
        with open(filename, errors='ignore') as f:
            for line in f:
                line = line.strip()
                (book, chapter, verse, scripture) = line.split("||")
                book = book.replace("N", "")
                row = [book, chapter, verse, scripture]
                # print("{0} - {1}:{2}:{3}:{4}".format(count, book, chapter, verse, line))
                data.append(row)
        self.mySwordBibleToRichFormat(biblename, biblename, data)
        self.mySwordBibleToPlainFormat(biblename, biblename, data)
        self.logger.info("Import successful")

    # https://github.com/scrollmapper/bible_databases_deuterocanonical
    def importScrollmapperDeuterocanonicalFiles(self, filename):
        biblename = "DEUT"
        count = 0
        data = []
        record = ""
        with open(filename, errors='ignore') as f:
            for line in f:
                if line.startswith("|"):
                    if record.startswith("|"):
                        (bookName, chapter, verse, scripture) = re.search(r"\|(.*)\|(.*)\|(.*)\|(.*)$", line).groups()
                        if bookName in BibleBooks.name2number:
                            book = BibleBooks.name2number[bookName]
                            row = [book, chapter, verse, scripture]
                            data.append(row)
                        else:
                            print("{0} not found".format(bookName))
                    record = line
                else:
                    record += " " + line
        self.mySwordBibleToRichFormat(biblename, biblename, data)
        self.mySwordBibleToPlainFormat(biblename, biblename, data)


    def stripTheWordTags(self, line):
        if config.importDoNotStripStrongNo:
            line = re.sub(r"<W([HG]\d*)>", " <gloss> \\1 </gloss> ", line)
        if config.importDoNotStripMorphCode:
            line = line.replace("<wt>", "")
            line = re.sub(r"""<WT(.*?) l="(.*?)">""",
                          """ <gloss> \\1 </gloss> """, line)
            line = re.sub("<v.*?>", "", line)
            line = line.replace("<O>", "<heb>")
            line = line.replace("<o>", "</heb>")
            line = line.replace("<OG>", "<grk>")
            line = line.replace("<og>", "</grk>")
        else:
            line = re.sub(r"<.*?>", "", line)
        return line

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
        connection = apsw.Connection(formattedBible)
        cursor = connection.cursor()

        statements = (
            Bible.CREATE_BIBLE_TABLE,
            Bible.CREATE_VERSES_TABLE,
            Bible.CREATE_DETAILS_TABLE,
            Bible.CREATE_NOTES_TABLE,
        )
        for create in statements:
            cursor.execute(create)
#            cursor.execute("COMMIT")

        if stories:
            stories = self.storiesToTitles(stories)

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
#            cursor.execute("COMMIT")

        formattedChapters = [(book, chapter, formattedChapters[(book, chapter)]) for book, chapter in formattedChapters]
        insert = "INSERT INTO Bible (Book, Chapter, Scripture) VALUES (?, ?, ?)"
        cursor.executemany(insert, formattedChapters)
#        cursor.execute("COMMIT")

        self.populateDetails(cursor, description, abbreviation)

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
        with apsw.Connection(filename) as connection:
            cursor = connection.cursor()
            # draw data from two tables: info, commentaries
            # table: info
            query = "SELECT value FROM info WHERE name = 'description'"
            cursor.execute(query)
            description = cursor.fetchone()[0]
            title = description
            *_, inputFileName = os.path.split(filename)
            abbreviation = inputFileName[:-21]
            abbreviation = re.sub(r"^(.*?)\-c$", r"\1", abbreviation)
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
        text = re.sub(r"<a [^<>]*?href=['{0}]C:@([0-9]+?) ([\-0-9:]+?)[^\-0-9:][^<>]*?>".format('"'), self.formatMyBibleCommentaryLink, text)
        text = self.formatNonBibleMyBibleModule(text, abbreviation)
        return text

    def formatMyBibleCommentaryLink(self, match):
        bookNo, cv = match.groups()
        standardAbbreviation = BibleVerseParser(config.parserStandarisation).standardAbbreviation
        if bookNo in standardAbbreviation:
            return "<a href='javascript:void(0)' onclick='document.title={0}COMMENTARY:::{1} {2}{0}'>".format('"', standardAbbreviation[bookNo], cv)
        else:
            return "<a href='javascript:void(0)' onclick='document.title={0}COMMENTARY:::{1}.{2}{0}'>".format('"', bookNo, cv.replace(":", "."))

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
            192: 78,
            220: 18,
            230: 19,
            232: 86,
            240: 20,
            250: 21,
            260: 22,
            290: 23,
            300: 24,
            310: 25,
            323: 72,
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
            # 232: 90, # Eliran's customised no.
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
            (r"href=['{0}]ref://([0-9]+?)\.([0-9]+?)\.([0-9]+?);['{0}]".format('"'), r'href="javascript:void(0)" onclick="bcv(\1,\2,\3)"'),
            (r"href=['{0}]lexi://(.*?)['{0}]".format('"'), r'href="javascript:void(0)" onclick="lex({0}\1{0})"'.format("'")),
            (r"href=['{0}]gk://(.*?)['{0}]".format('"'), r'href="javascript:void(0)" onclick="lex({0}gk\1{0})"'.format("'")),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        return text

    def importBBPlusLexiconInAFolder(self, folder):
        files = [filename for filename in os.listdir(folder) if os.path.isfile(os.path.join(folder, filename)) and not re.search(r"^[\._]", filename)]
        validFiles = [filename for filename in files if re.search(r'^Dict.*?\.json$', filename)]
        if validFiles:
            for filename in validFiles:
                module = filename[4:-5]
                jsonList = self.readJsonFile(os.path.join(folder, filename))
                jsonList = [(jsonEntry["top"], self.convertBibleBentoPlusTag(jsonEntry["def"])) for jsonEntry in jsonList]
                self.createLexiconModule(module, jsonList)
            return True

    def importBBPlusDictionaryInAFolder(self, folder):
        files = [filename for filename in os.listdir(folder) if os.path.isfile(os.path.join(folder, filename)) and not re.search(r"^[\._]", filename)]
        validFiles = [filename for filename in files if re.search(r'^Dict.*?\.json$', filename)]
        if validFiles:
            for filename in validFiles:
                module = filename[4:-5]
                jsonList = self.readJsonFile(os.path.join(folder, filename))
                jsonList = [(jsonEntry["top"], jsonEntry["def"]) for jsonEntry in jsonList]
                self.createDictionaryModule(module, jsonList)
            return True

    def convertOldLexiconData(self):
        database = os.path.join(config.marvelData, "data", "lexicon.data")
        connection = apsw.Connection(database)
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
        connection = apsw.Connection(database)
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
        connection = apsw.Connection(filename)
        cursor = connection.cursor()

        query = "SELECT Chapter, Content FROM Reference"
        cursor.execute(query)
        content = cursor.fetchall()
        data = []
        for chapter, chapterContent in content:
            self.logger.info("Converting {0}".format(chapter))
            chapterContent = self.formatNonBibleESwordModule(chapterContent)
            chapterContent = BibleVerseParser(config.parserStandarisation).parseText(chapterContent, splitInChunks=False,
                                                                           parseBooklessReferences=False,
                                                                           canonicalOnly=True)
            data.append((chapter, chapterContent))
        self.createBookModule(module, data)

        connection.close()

    def importESwordDevotional(self, filename):
        *_, module = os.path.split(filename)
        module = Path(module).stem
        connection = apsw.Connection(filename)
        cursor = connection.cursor()

        query = "SELECT Month, Day, Devotion from Devotions"
        cursor.execute(query)
        content = cursor.fetchall()
        data = []
        for month, day, devotion in content:
            devotion = self.convertRtfToHtml(devotion)
            data.append((month, day, devotion))
        DevotionalSqlite.createDevotional(module, data)
        connection.close()

    def checkColumnExists(self, table, column, cursor):
        cursor.execute("SELECT * FROM pragma_table_info(?) WHERE name=?", (table, column))
        if cursor.fetchone():
            return True
        else:
            return False


    # Import TheWord cross references
    def importTheWordXref(self, filename):
        xrefFilename = Path(filename).stem.replace(".xrefs", "")
        with apsw.Connection(filename) as connection:
            cursor = connection.cursor()
            query = "SELECT value FROM config where name='tables.xrefs.description'"
            cursor.execute(query)
            description = cursor.fetchone()[0]
            query = "SELECT fbi, fci, fvi, tbi, tci, tvi, tspan FROM xrefs_bcv order by fbi, fci, fvi"
            cursor.execute(query)
            xrefs = cursor.fetchall()
            self.createXrefModule(xrefFilename, description, description, xrefs)

    # create cross reference module
    def createXrefModule(self, filename, title, description, xrefs):
        xrefFolder = os.path.join(config.marvelData, "xref")
        xrefFile = os.path.join(xrefFolder, "{0}.xref".format(filename))
        if os.path.isfile(xrefFile):
            os.remove(xrefFile)
        with apsw.Connection(xrefFile) as connection:
            cursor = connection.cursor()
            statements = (
                """CREATE TABLE "CrossReference" (Book INT, Chapter INT, Verse INT, Information TEXT)""",
                """CREATE TABLE "Details" ("Title"	NVARCHAR(100), "Information" TEXT)"""
            )
            for create in statements:
                cursor.execute(create)
#                cursor.execute("COMMIT")
            insert = "INSERT INTO Details (Title, Information) VALUES (?, ?)"
            cursor.execute(insert, (title, description))
#            cursor.execute("COMMIT")
            if xrefs:
                data = []
                book = 0
                chapter = 0
                verse = 0
                info = ""
                for xref in xrefs:
                    fbi, fci, fvi, tbi, tci, tvi, tspan = xref
                    if not (fbi == book and fci == chapter and fvi == verse):
                        if len(info) > 0:
                            data.append((book, chapter, verse, info))
                        book = fbi
                        chapter = fci
                        verse = fvi
                        info = ""
                    if len(info) > 0:
                        info += "; "
                    info += BibleVerseParser(config.parserStandarisation).bcvToVerseReference(tbi, tci, tvi)
                    if int(tspan) > 0:
                        info += "-{0}".format(int(tvi)+int(tspan))
                data.append((book, chapter, verse, info))
                insert = "INSERT INTO CrossReference (Book, Chapter, Verse, Information) VALUES (?, ?, ?, ?)"
                cursor.executemany(insert, data)
#                cursor.execute("COMMIT")

    def convertRtfToHtml(self, rtf):
        rtf = rtf.replace("\\pard", "<p>\n")
        rtf = rtf.replace("\\par", "<p>\n")
        lines = rtf.split("\n")
        output = ""
        for line in lines:
            center = False
            line = line.replace("\\line", "<br>")
            line = line.replace("\\s18tap01", "<br>")
            line = line.replace("\\par", "<br>")
            line = line.replace("\\i0", "</i>")
            line = line.replace("\\i ", "<i>")
            line = line.replace("\\b0", "</b>")
            line = line.replace("\\b ", "<b>")
            line = line.replace("\\'91", "'")
            line = line.replace("\\'92", "'")
            line = line.replace("\\'93", '"')
            line = line.replace("\\'94", '"')
            line = line.replace("\\'97", ' - ')
            line = line.replace("\\cs51", ':')
            if "\\qc" in line:
                if len(line) < 80:
                    center = True
                    line = line.replace("\\qc", "<center>")
                else:
                    line = line.replace("\\qc", "")
            line = re.sub("^\\\[^ ]+?<", "<", line)
            line = re.sub("^\\\[^ ]+$", "", line)
            line = re.sub("^\{.*\}$", "", line)
            line = re.sub("^\\\[^ ]+? ", "", line)
            line = re.sub("\\\\tx[0-9]*", "", line)
            line = re.sub("\\\sb[0-9]*", "", line)
            line = re.sub("\\\sl[0-9]*", "", line)
            replace = [
                       "\\cf11",
                       "\\cf0none",
                       "\\cf1",
                       "\\cs505",
                       "\\cs52",
                       "\\f0",
                       "\\hich",
                       "\\keep",
                       "\\keepn1",
                       "\\li1440",
                       "\\li360",
                       "\\li4320",
                       "\\li720",
                       "\\loch",
                       "\\nosupersub",
                       "\\nowidctlpar",
                       "\\ri360",
                       "\\lmult1",
                       "\\qc",
                       "\\ul",
                       "\\ulnone",
                       "\\s18tap0",
                       "\\s18tap01",
                       "\\s22tap0",
                       "\\s22tap0n1",
                       "\\widctlparmult",
                       "\\cf0none",
                       "\\b",
                       "\\i",
                       ]
            if len(line) > 0:
                for r in replace:
                    line = line.replace(r, "")
                line = line.replace("_", " ")
            if center:
                line += "</center>"
            output += line + "\n"
        return output


class ThirdPartyDictionary:

    def __init__(self, moduleTuple=None):
        self.connection = None
        self.moduleList = self.getModuleList()
        if moduleTuple is not None:
            self.module, self.fileExtension = moduleTuple
            if self.module in self.moduleList:
                self.database = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(self.module, self.fileExtension))
                self.connection = apsw.Connection(self.database)
                self.cursor = self.connection.cursor()

    def __del__(self):
        if self.connection is not None:
            self.connection.close()

    def getModuleList(self):
        moduleFolder = os.path.join("thirdParty", "dictionaries")
        bbPlusDictionaries = [f[:-8] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".dic.bbp") and not re.search(r"^[\._]", f)]
        mySwordDictionaries = [f[:-12] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".dct.mybible") and not re.search(r"^[\._]", f)]
        eSwordDictionaries = [f[:-5] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".dcti") and not re.search(r"^[\._]", f)]
        eSwordLexicons = [f[:-5] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".lexi") and not re.search(r"^[\._]", f)]
        myBibleDictionaries = [f[:-19] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".dictionary.SQLite3") and not re.search(r"^[\._]", f)]
        moduleList = set(bbPlusDictionaries + mySwordDictionaries + eSwordDictionaries + eSwordLexicons + myBibleDictionaries)
        moduleList = sorted(list(moduleList))
        return moduleList

    def search(self, entry, showMenu=True):
        if not self.database:
            return "INVALID_COMMAND_ENTERED"
        else:
            exactMatch = self.getExactWord(entry)
            similarMatch = self.getSimilarWord(entry)
            action = "searchThirdDictionary(this.value, \"{0}\")".format(entry)
            optionList = [(m, m) for m in self.moduleList]
            selectList = self.formatSelectList(action, optionList) if showMenu else ""
            config.thirdDictionary = self.module
            selectList = f"<p>{selectList}</p><p>" if not config.runMode == "terminal" else ""
            return "<h2>Search <span style='color: brown;'>{0}</span> for <span style='color: brown;'>{1}</span></h2>{4}<b>Exact match:</b><br><br>{2}</p><p><b>Partial match:</b><br><br>{3}".format(self.module, entry, exactMatch, similarMatch, selectList)

    def formatSelectList(self, action, optionList):
        if config.runMode == "terminal":
            return ""
        selectForm = "<select onchange='{0}'>".format(action)
        for value, description in optionList:
            if value == self.module:
                selectForm += "<option value='{0}' selected='selected'>{1}</option>".format(value, description)
            else:
                selectForm += "<option value='{0}'>{1}</option>".format(value, description)
        selectForm += "</select>"
        return selectForm

    def getAllEntries(self):
        if not self.database:
            return []
        else:
            getDictionaryData = {
                ".dic.bbp": self.getBibleBentoPlusDicAll,
                ".dcti": self.getESwordDicAll,
                ".lexi": self.getESwordLexAll,
                ".dct.mybible": self.getMySwordAll,
                ".dictionary.SQLite3": self.getMyBibleAll,
            }
            return getDictionaryData[self.fileExtension]()

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

    def getBibleBentoPlusDicAll(self):
        query = TextUtil.getQueryPrefix()
        query += "SELECT Topic FROM Dictionary"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def getBibleBentoPlusDicSimilarWord(self, entry):
        query = TextUtil.getQueryPrefix()
        query += "SELECT Topic FROM Dictionary WHERE Topic LIKE ? AND Topic != ?"
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

    def getESwordDicAll(self):
        query = TextUtil.getQueryPrefix()
        query += "SELECT Topic FROM Dictionary"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def getESwordDicSimilarWord(self, entry):
        query = TextUtil.getQueryPrefix()
        query += "SELECT Topic FROM Dictionary WHERE Topic LIKE ? AND Topic != ?"
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

    def getESwordLexAll(self):
        query = TextUtil.getQueryPrefix()
        query += "SELECT Topic FROM Lexicon"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def getESwordLexSimilarWord(self, entry):
        query = TextUtil.getQueryPrefix()
        query += "SELECT Topic FROM Lexicon WHERE Topic LIKE ? AND Topic != ?"
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

    def getMySwordAll(self):
        query = TextUtil.getQueryPrefix()
        query += "SELECT word FROM dictionary"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def getMySwordSimilarWord(self, entry):
        query = TextUtil.getQueryPrefix()
        query += "SELECT word FROM dictionary WHERE word LIKE ? AND word != ?"
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

    def getMyBibleAll(self):
        query = TextUtil.getQueryPrefix()
        query += "SELECT topic FROM dictionary"
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def getMyBibleSimilarWord(self, entry):
        query = TextUtil.getQueryPrefix()
        query += "SELECT topic FROM dictionary WHERE topic LIKE ? AND topic != ?"
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

    # Import TheWord Commentaries
    def importTheWordCommentary(self, filename):
        commentaryContent = []
        with apsw.Connection(filename) as connection:
            cursor = connection.cursor()
            query = "SELECT value FROM config where name='title'"
            cursor.execute(query)
            description = cursor.fetchone()[0]
            title = description
            *_, inputFileName = os.path.split(filename)
            abbreviation = inputFileName[:-21]
            abbreviation = re.sub(r"^(.*?)\-c$", r"\1", abbreviation)
            query = "SELECT topic_id, DISTINCT book_number, chapter_number_from FROM commentaries ORDER BY book_number, chapter_number_from, verse_number_from, chapter_number_to, verse_number_to"
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


if __name__ == '__main__':

    # note = "***[BOOK:::Thrones of our Soul:::0.4.3 The insight of Moses|Go to chapter]"
    # note = re.sub(r"\*\*\*\[(.+?)\|(.+?)\]", r"""<ref onclick="document.title='\1'">\2</ref>""", note)
    # print(note)
    # Converter().createBookModuleFromHymnLyricsFile("Hymn Lyrics - Romanian.txt")

    # text = " {\f2\'e5\'cc}{\sub 1}  {\cf11\super  CC}  {\cf2 mas}  {\f2\'ee\'c5}{\sub 2}  {\cf11\super  PM}  {\cf2 del}  {\f2\'f2\'c5\'f5}{\sub 3}  {\cf11\super  H6086:NCcSMC}  {\cf2 árbol}  {\f2\u8592?}  {\cf16 de}  {\f2\'e4\'c7}{\sub 4}  {\cf11\super  XD}  {\cf2 la}  {\f2\'e3\'cc\'c7\'f2\'c7\'fa}{\sub 5}  {\cf11\super  H1847:VqAT---NH}  {\cf2 ciencia}  \bullet  {\cf2 del}  {\f2\'e8\'c9\'e5\'e1}{\sub 6}  {\cf11\super  H2896:NCcSMN}  {\cf2 bien}  {\f2\'e5\'c8}{\sub 7}  {\cf11\super  CC}  {\cf2 y}  \bullet  {\cf2 del}  {\f2\'f8\'c8\'f2}{\sub 8}  {\cf11\super  H7451:NCcSMP}  {\cf2 mal}  {\f2\'ec\'c9\'e0}{\sub 9}  {\cf11\super  H3808:ANN}  {\cf2 no}  {\f2\'fa\'c9\'e0\'eb\'c7\'ec}{\sub 10}  {\cf11\super  H398:VqAMSM2}  {\cf2 comerás;}  {\f2\'ee\'c4\'ee\'cc}{\sub 11}  {\cf11\super  H4480:PM}   {\cf2\bullet}   {\f2\'c6\'f0\'cc\'e5\'cc}{\sub 12}  {\cf11\super  RBSM3}  {\cf2 \bullet}  {\f2\'eb\'cc\'c4\'e9}{\sub 13}  {\cf11\super  H3588:CK}  {\cf2 porque}  \bullet  {\cf2 el}  {\f2\'e1\'cc\'c0}{\sub 14}  {\cf11\super  PB}   {\cf2\bullet}   {\f2\'e9\'c9\'e5\'ed}{\sub 15}  {\cf11\super  H3117:NCcSMC}  {\cf2 día}  \bullet  {\cf2 que}  {\f2\'ee\'c4\'ee\'cc}{\sub 18}  {\cf11\super  PM}  {\cf2 de}  {\f2\'c6\'f0\'cc\'e5\'cc}{\sub 19}  {\cf11\super  RBSM3}  {\cf2 él}  \'8b  {\f2\'e0\'c2\'eb\'c8\'ec}{\sub 16}  {\f2\'c0\'ea\'c8}{\sub 17} \'9b  {\cf11\super  H398:VqAT---S, RBSM2}  {\cf2 comieres,}  \'8b  {\f2\'ee\'c9\'e5\'fa}{\sub 20}  {\f2\'fa\'cc\'c8\'ee\'e5\'cc\'fa}{\sub 21} \'9b  {\cf11\super  H4191:VqAa, VqAMSM2}  {\cf2 ciertamente}  {\f2\u8592?}  {\cf16 morirás.}"
    # text = " {\f1\'c2\'df\'e2\'eb\'ef\'f2\sub 1}  {\cf11\super  Biblos G976 NNSF}  {\cf2 Libro}  {\f1\u8594?}  {\cf16 de}  {\f1\u8594?}  {\cf16 la}  {\f1\'e3\'e5\'ed\'dd\'f3\'e5\'f9\'f2\sub 2}  {\cf11\super  geneseôs G1078 NGSF}  {\cf2 genealogía}  {\f1\u8594?}  {\cf16 de}  \'8b  {\f1\u7992?\'e7\'f3\'ef\u8166?{\sub 3} \'d8\'f1\'e9\'f3\'f4\'ef\u8166?\sub 4} \'9b  {\cf11\super  Iêsou Christou G2424 G5547 NGSM NGSM}  {\cf2 Jesucristo,}  {\f1\'f5\u7985?\'ef\u8166?\sub 5}  {\cf11\super  huiou G5207 NGSM}  {\cf2 hijo}  {\f1\u8594?}  {\cf16 de}  {\f1\'c4\'e1\'e2\'df\'e4\sub 6}  {\cf11\super  Dabid G1138 XP}  {\cf2 David,}  {\f1\'f5\u7985?\'ef\u8166?\sub 7}  {\cf11\super  huiou G5207 NGSM}  {\cf2 hijo}  {\f1\u8594?}  {\cf16 de}  {\f1\u7944?\'e2\'f1\'e1\'dc\'ec\sub 8}  {\cf11\super  Abraam G11 XP}  {\cf2 Abraham.}"
    # text = " \'8b  {\f2\'e5\'c7}{\sub 1}  {\f2\'fa\'cc\'c9\'f1\'c6\'f3}{\åsub 2} \'9b  {\cf11\super  Cc, VhAmSF3}  {\cf2 Después}  \'8b  {\f2\'ec\'c8}{\sub 3}  {\f2\'ec\'c6\'e3\'c6\'fa}{\sub 4} \'9b  {\cf11\super  PL, VqAT---C}  {\cf2 dio}  {\f2\u8592?}  {\cf16 a}  {\f2\u8592?}  {\cf16 luz}  {\f2\'e0\'c6\'fa}{\sub 5}  {\cf11\super  H853:PA}  {\cf2 a}  {\f2\'e5}{\sub 7}  {\cf11\super  RBSM3}  {\cf2 su}  {\f2\'e0\'c8\'e7\'c4\'e9}{\sub 6}  {\cf11\super  H251:NCcSMS}  {\cf2 hermano}  {\f2\'e0\'c6\'fa}{\sub 8}  {\cf11\super  H853:PA}   {\cf2\bullet}   {\f2\'e4\'c8\'e1\'c6\'ec}{\sub 9}  {\cf11\super  H1893:NPHSMP}  {\cf2 Abel.}  {\f2\'e5\'c7}{\sub 10}  {\cf11\super  Cc}  {\cf2 Y}  {\f2\'e4\'c6\'e1\'c6\'ec}{\sub 12}  {\cf11\super  H1893:NPHSMN}  {\cf2 Abel}  {\f2\'e9\'c0\'e4\'c4\'e9}{\sub 11}  {\cf11\super  H1961:VqAmSM3}  {\cf2 fue}  \'8b  {\f2\'f8\'c9\'f2\'c5\'e4}{\sub 13}  {\f2\'f6\'c9\'e0\'ef}{\sub 14} \'9b  {\cf11\super  H6629:VqAtSM-C, NCcCMN}  {\cf2 pastor}  {\f2\u8592?}  {\cf16 de}  {\f2\u8592?}  {\cf16 ovejas,}  {\f2\'e5\'c0}{\sub 15}  {\cf11\super  CC}  {\cf2 y}  {\f2\'f7\'c7\'e9\'c4\'ef}{\sub 16}  {\cf11\super  H7014:NPHSMN}  {\cf2 Caín}  {\f2\'e4\'c8\'e9\'c8\'e4}{\sub 17}  {\cf11\super  H1961:VqAsSM3}  {\cf2 fue}  \'8b  {\f2\'f2\'c9\'e1\'c5\'e3}{\sub 18}  {\f2\'e0\'c2\'e3\'c8\'ee\'c8\'e4}{\sub 19} \'9b  {\cf11\super  H127:VqAtSM-C, NCcSFN}  {\cf2 labrador}  {\f2\u8592?}  {\cf16 de}  {\f2\u8592?}  {\cf16 la}  {\f2\u8592?}  {\cf16 tierra.}"
    # text = " {\f1\'c2\'df\'e2\'eb\'ef\'f2\sub 1}  {\cf11\super  Biblos G976 NNSF}  {\cf2 Libro}  {\f1\u8594?}  {\cf16 de}  {\f1\u8594?}  {\cf16 la}  {\f1\'e3\'e5\'ed\'dd\'f3\'e5\'f9\'f2\sub 2}  {\cf11\super  geneseôs G1078 NGSF}  {\cf2 genealogía}  {\f1\u8594?}  {\cf16 de}  \'8b  {\f1\u7992?\'e7\'f3\'ef\u8166?{\sub 3} \'d8\'f1\'e9\'f3\'f4\'ef\u8166?\sub 4} \'9b  {\cf11\super  Iêsou Christou G2424 G5547 NGSM NGSM}  {\cf2 Jesucristo,}  {\f1\'f5\u7985?\'ef\u8166?\sub 5}  {\cf11\super  huiou G5207 NGSM}  {\cf2 hijo}  {\f1\u8594?}  {\cf16 de}  {\f1\'c4\'e1\'e2\'df\'e4\sub 6}  {\cf11\super  Dabid G1138 XP}  {\cf2 David,}  {\f1\'f5\u7985?\'ef\u8166?\sub 7}  {\cf11\super  huiou G5207 NGSM}  {\cf2 hijo}  {\f1\u8594?}  {\cf16 de}  {\f1\u7944?\'e2\'f1\'e1\'dc\'ec\sub 8}  {\cf11\super  Abraam G11 XP}  {\cf2 Abraham.}"
    # out = Converter().convertFromRichTextFormat(text, True)
    # print(out)

    # file = "/Users/otseng/Downloads/TR.txt"
    # Converter().importTXTBible(file)

    # line = "In <FI>the<Fi> beginning<WH7225><WTHR><WTHNcfsa> God<WH430><WTHNcmpa> created<WH1254><WTHVqp3ms> <WH853><WTHTo> the heavens<WH8064><WTHTd><WTHNcmpa> and<WH853><WTHC><WTHTo> the earth.<WH776><WTHTd><WTHNcbsa>"
    # line = """And God<WH430><WTHNcmpa> said,<WH559><WTHC><WTHVqw3ms> "Let there be<WH1961><WTHVqj3ms> light."<WH216><WTHNcbsa> And there was<WH1961><WTHC><WTHVqw3ms> light.<WH216><WTHNcbsa>"""
    # line = """<v="Gen.1.1/Gen.1.1"><wt>ἐν<WTP l="ἐν"> <wt>ἀρχῇ<WTN1-DSF l="ἀρχή"> <wt>ἐποίησεν<WTVAI-AAI3S l="ποιέω"> <wt>ὁ<WTRA-NSM l="ὁ"> <wt>θεὸς<WTN2-NSM l="θεός"> <wt>τὸν<WTRA-ASM l="ὁ"> <wt>οὐρανὸν<WTN2-ASM l="οὐρανός"> <wt>καὶ<WTC l="καί"> <wt>τὴν<WTRA-ASF l="ὁ"> <wt>γῆν<WTN1-ASF l="γῆ">"""
    # out = Converter().stripTheWordTags(line)
    # print(out)

    # file = "/Users/otseng/Downloads/apocrypha.txt"
    # print("Processing " + file)
    # Converter().importScrollmapperDeuterocanonicalFiles(file)

    # file = "/Users/otseng/Downloads/FruchtenbaumOTRev.xrefs.twm"
    # Converter().importTheWordXref(file)

    # line = "\\tx123dev\\tx2345abc"
    # print(re.sub("\\\\tx[0-9]*", "", line))

    # filename = "/home/oliver/Downloads/Miller - Devotional Hours with the Bible.devx"
    # Converter().importESwordDevotional(filename)

    # line = '﻿<TS>The Creation<Ts><wt><E>In the beginning<e><O> בְּרֵאשִׁ֖ית<o><T> bə·rê·šîṯ<t><WH7225><WTPrep-b+N-fs l="רֵאשִׁית"><RX 43.1.1+4><RX 58.11.1+2><wt><E> God<e><O> אֱלֹהִ֑ים<o><T> ’ĕ·lō·hîm<t><WH430><WTN-mp l="אֱלֹהִים"><wt><E> -<e><O> אֵ֥ת<o><T> ’êṯ<t><WH853><WTDirObjM l="אֵת"><wt><E> created<e><O> בָּרָ֣א<o><T> bā·rā<t><WH1254><WTV-Qal-Perf-3ms l="בָּרָא"><wt><E> the heavens<e><O> הַשָּׁמַ֖יִם<o><T> haš·šā·ma·yim<t><WH8064><WTArt+N-mp l="שָׁמַיִם"><wt><E> and<e><O> וְאֵ֥ת<o><T> wə·’êṯ<t><WH853><WTConj-w+DirObjM l="אֵת"><wt><E> the earth.<e><O> הָאָֽרֶץ׃<o><T> hā·’ā·reṣ<t><WH776><WTArt+N-fs l="אֶרֶץ">'
    # line = '<TS>Nothing May Be Added or Removed<Ts><wt><E>I<e><OG> ἐγὼ<og><T> egō<t><WG1473><WTPPro-N1S l="ἐγώ"><wt><E> testify<e><OG> Μαρτυρῶ<og><T> Martyrō<t><WG3140><WTV-PIA-1S l="μαρτυρέω"><wt><E> to everyone<e><OG> παντὶ<og><T> panti<t><WG3956><WTAdj-DMS l="πᾶς"><wt><E> who<e><OG> τῷ<og><T> tō<t><WG3588><WTArt-DMS l="ὁ"><wt><E> hears<e><OG> ἀκούοντι<og><T> akouonti<t><WG191><WTV-PPA-DMS l="ἀκούω"><wt><E> the<e><OG> τοὺς<og><T> tous<t><WG3588><WTArt-AMP l="ὁ"><wt><E> words<e><OG> λόγους<og><T> logous<t><WG3056><WTN-AMP l="λόγος"><wt><E> of<e><OG> τῆς<og><T> tēs<t><WG3588><WTArt-GFS l="ὁ"><wt><E> prophecy<e><OG> προφητείας<og><T> prophēteias<t><WG4394><WTN-GFS l="προφητεία"><wt><E> in this<e><OG> τούτου·<og><T> toutou·<t><WG3778><WTDPro-GNS l="οὗτος"><wt><E> -<e><OG> τοῦ<og><T> tou<t><WG3588><WTArt-GNS l="ὁ"><wt><E> book:<e><OG> βιβλίου<og><T> bibliou<t><WG975><WTN-GNS l="βιβλίον"><wt><E> If<e><OG> ἐάν<og><T> ean<t><WG1437><WTConj l="ἐάν"><wt><E> anyone<e><OG> τις<og><T> tis<t><WG5100><WTIPro-NMS l="τίς"><wt><E> adds<e><OG> ἐπιθῇ<og><T> epithē<t><WG2007><WTV-ASA-3S l="ἐπιτίθημι"><wt><E> to<e><OG> ἐπ’<og><T> ep’<t><WG1909><WTPrep l="ἐπί"><wt><E> them,<e><OG> αὐτά,<og><T> auta,<t><WG846><WTPPro-AN3P l="αὐτός"><wt><E> -<e><OG> ὁ<og><T> ho<t><WG3588><WTArt-NMS l="ὁ"><wt><E> God<e><OG> Θεὸς<og><T> Theos<t><WG2316><WTN-NMS l="θεός"><wt><E> will add<e><OG> ἐπιθήσει<og><T> epithēsei<t><WG2007><WTV-FIA-3S l="ἐπιτίθημι"><wt><E> to<e><OG> ἐπ’<og><T> ep’<t><WG1909><WTPrep l="ἐπί"><wt><E> him<e><OG> αὐτὸν<og><T> auton<t><WG846><WTPPro-AM3S l="αὐτός"><wt><E> the<e><OG> τὰς<og><T> tas<t><WG3588><WTArt-AFP l="ὁ"><wt><E> plagues<e><OG> πληγὰς<og><T> plēgas<t><WG4127><WTN-AFP l="πληγή"><wt><E> -<e><OG> τὰς<og><T> tas<t><WG3588><WTArt-AFP l="ὁ"><wt><E> described<e><OG> γεγραμμένας<og><T> gegrammenas<t><WG1125><WTV-RPM/P-AFP l="γράφω"><wt><E> in<e><OG> ἐν<og><T> en<t><WG1722><WTPrep l="ἔν"><wt><E> this<e><OG> τούτῳ.<og><T> toutō.<t><WG3778><WTDPro-DNS l="οὗτος"><wt><E> -<e><OG> τῷ<og><T> tō<t><WG3588><WTArt-DNS l="ὁ"><wt><E> book.<e><OG> βιβλίῳ<og><T> bibliō<t><WG975><WTN-DNS l="βιβλίον">'
    # out = Converter().stripTheWordTags(line)
    # print(out)

    file = "/home/oliver/Downloads/temp/2001b.xml"
    Converter().importXMLBible(file)
