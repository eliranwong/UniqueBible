import os, sqlite3, config, re
from BiblesSqlite import BiblesSqlite
from BibleVerseParser import BibleVerseParser

class Converter:

    # Import MySword Bibles
    def importMySwordBible(self, file):
        connection = sqlite3.connect(file)
        cursor = connection.cursor()

        query = "SELECT Description, Abbreviation FROM Details"
        cursor.execute(query)
        description, abbreviation = cursor.fetchone()
        query = "SELECT * FROM Bible ORDER BY Book, Chpater, Verse"
        cursor.execute(query)
        verses = cursor.fetchall()
        connection.close()

        abbreviation = abbreviation.replace("+", "s")
        self.mySwordBibleToPlainFormat(description, abbreviation, verses)
        self.mySwordBibleToRichFormat(description, abbreviation, verses)

    def mySwordBibleToPlainFormat(self, description, abbreviation, verses):
        verses = [(book, chapter, verse, self.stripMySwordBibleTags(scripture)) for book, chapter, verse, scripture in verses]
        biblesSqlite = BiblesSqlite()
        biblesSqlite.importBible(description, abbreviation, verses)
        del biblesSqlite

    def mySwordBibleToRichFormat(self, description, abbreviation, verses):
        formattedBible = os.path.join("marvelData", "bibles", "{0}.bible".format(abbreviation))
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

        for book, chapter, verse, scripture in verses:
            scripture, notes = self.convertMySwordBibleTags(scripture)

            if notes:
                insert = "INSERT INTO Notes (Book, Chapter, Verse, ID, Note) VALUES (?, ?, ?, ?, ?)"
                for counter, note in enumerate(notes):
                    cursor.execute(insert, (book, chapter, verse, str(counter), note))
                connection.commit()

            if scripture:

                # fix bible note links
                scripture = re.sub("｛([0-9]+?)｝", r"{0}, {1}, {2}, \1".format(book, chapter, verse), scripture)
                # verse number formatting
                scripture = self.formatVerseNumber(book, chapter, verse, scripture)

                query = "SELECT Scripture FROM Bible WHERE Book=? AND Chapter=?"
                cursor.execute(query, (book, chapter))
                chapterText = cursor.fetchone()

                if chapterText:
                    chapterText = chapterText[0] + scripture
                    update = "UPDATE Bible SET Scripture=? WHERE Book=? AND Chapter=?"
                    cursor.execute(update, (chapterText, book, chapter))
                    connection.commit()
                else:
                    insert = "INSERT INTO Bible (Book, Chapter, Scripture) VALUES (?, ?, ?)"
                    cursor.execute(insert, (book, chapter, scripture))
                    connection.commit()

        connection.close()

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

    def stripMySwordBibleTags(self, text):
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
        text = re.sub("</ref></sup><sup><ref", "</ref> <ref", text)
        text = text.strip()
        return (text, notes)

    def convertMySwordRxTag(self, match):
        b, c, v = match.group()[1:-1].split("｜")
        bookName = BibleVerseParser(config.parserStandarisation).standardAbbreviation[b]
        return '<ref onclick="bcv({0},{1},{2})">{3} {1}:{2}</ref>'.format(b, c, v, bookName)

    def convertMySwordRfTag(self, text):
        notes = [m for m in re.findall("<RF[^\n<>]*?>(.*?)<Rf>", text)]
        p = re.compile("<RF[^\n<>]*?>.*?<Rf>")
        s = p.search(text)
        noteID = 0
        while s:
            text = p.sub("<sup><ref onclick='bn(｛{0}｝)'>&oplus;</ref></sup>".format(noteID), text)
            noteID += 1
            s = p.search(text)
        return (text, notes)

    # Import MySword Commentaries
    def importMySwordCommentary(self, file):
        # connect MySword commentary
        connection = sqlite3.connect(file)
        cursor = connection.cursor()

        # process 3 tables: details, commentary, data (mainly contain images)
        query = "SELECT title, abbreviation, description FROM details"
        cursor.execute(query)
        title, abbreviation, description = cursor.fetchone()
        query = "SELECT DISTINCT book, chapter FROM commentary ORDER BY book, chapter, fromverse, toverse"
        cursor.execute(query)
        chapters = cursor.fetchall()

        # create an UB commentary
        ubCommentary = os.path.join("marvelData", "commentaries", "c{0}.commentary".format(abbreviation))
        if os.path.isfile(ubCommentary):
            os.remove(ubCommentary)
        ubFileConnection = sqlite3.connect(ubCommentary)
        ubFileCursor = ubFileConnection.cursor()

        statements = (
            "CREATE TABLE Commentary (Book INT, Chapter INT, Scripture TEXT)",
            "CREATE TABLE Details (Title NVARCHAR(100), Abbreviation NVARCHAR(50), Information TEXT, Version INT, OldTestament BOOL, NewTestament BOOL, Apocrypha BOOL, Strongs BOOL)"
        )
        for create in statements:
            ubFileCursor.execute(create)
            ubFileConnection.commit()
        insert = "INSERT INTO Details (Title, Abbreviation, Information, Version, OldTestament, NewTestament, Apocrypha, Strongs) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        ubFileCursor.execute(insert, (title, abbreviation, description, 1, 1, 1, 0, 0))
        ubFileConnection.commit()

        for chapter in chapters:
            b, c = chapter
            biblesSqlite = BiblesSqlite()
            verseList = biblesSqlite.getVerseList(b, c, "KJV")
            del biblesSqlite
            
            verseDict = {v: ['<vid id="v{0}.{1}.{2}"></vid>'.format(b, c, v)] for v in verseList}
            
            query = "SELECT book, chapter, fromverse, toverse, data FROM commentary WHERE book=? AND chapter=? ORDER BY book, chapter, fromverse, toverse"
            cursor.execute(query, chapter)
            verses = cursor.fetchall()
            
            for verse in verses:
                verseContent = '<ref onclick="bcv({0},{1},{2})"><u><b>{1}:{2}-{3}</b></u></ref><br>{4}'.format(*verse)
                verseContent = self.formatCommentaryVerse(verseContent)

                fromverse = verse[2]
                item = verseDict.get(fromverse, "not found")
                if item == "not found":
                    verseDict[fromverse] = ['<vid id="v{0}.{1}.{2}"></vid>'.format(b, c, fromverse), verseContent]
                else:
                    item.append(verseContent)

            sortedVerses = sorted(verseDict.keys())
            
            chapterText = ""
            for sortedVerse in sortedVerses:
                chapterText += "<hr>".join(verseDict[sortedVerse])

            # write in UB commentary file
            insert = "INSERT INTO Commentary (Book, Chapter, Scripture) VALUES (?, ?, ?)"
            ubFileCursor.execute(insert, (b, c, chapterText))
            ubFileConnection.commit()

        connection.close()
        ubFileConnection.close()

    def formatCommentaryVerse(self, text):
        text = re.sub(r"<u><b>([0-9]+?):([0-9]+?)-\2</b></u>", r"<u><b>\1:\2</b></u>", text)
        text = self.formatNonBibleModule(text)
        return text

    def formatNonBibleModule(self, text):
        # convert bible reference tag like <a class='bible' href='#bGen 1:1'>
        text = re.sub("<a [^<>]*?href='[#]*?b[0-9]*?[A-Za-z]+? [0-9][^<>]*?>", self.extractBibleReferences, text)
        # convert bible reference tag like <a class='bible' href='#b1.1.1'>
        text = re.sub("<a [^<>]*?href='[#]*?b([0-9]+?)\.([0-9]+?)\.([0-9]+?)[^0-9][^<>]*?>", r'<a href="javascript:void(0)" onclick="bcv(\1,\2,\3)">', text)

        # convert commentary reference tag like <a href='#c-CSBC Gen 1:1'>
        text = re.sub("<a [^<>]*?href='[#]*?c\-[^ ]+? [0-9]*?[A-Za-z]+? [0-9][^<>]*?>", self.extractSpecificCommentaryReferences, text)
        # convert commentary reference tag like <a href='#cGen 1:1'>
        text = re.sub("<a [^<>]*?href='[#]*?c[0-9]*?[A-Za-z]+? [0-9][^<>]*?>", self.extractCommentaryReferences, text)
        # convert commentary reference tag like <a href='#c1.1.1'>
        text = re.sub("<a [^<>]*?href='[#]*?c([0-9]+?)\.([0-9]+?)\.([0-9]+?)[^0-9][^<>]*?>", r'<a href="javascript:void(0)" onclick="cbcv(\1,\2,\3)">', text)

        return text

    def extractBibleReferences(self, match):
        value = match.group()
        references = BibleVerseParser(config.parserStandarisation).extractAllReferences(value)
        if references:
            b, c, v = references[0]
            return '<a href="javascript:void(0)" onclick="bcv({0},{1},{2})">'.format(b, c, v)
        else:
            return value

    def extractSpecificCommentaryReferences(self, match):
        value = match.group()
        commentary = re.sub("<a [^<>]*?href='[#]*?c\-([^ ]+?) [0-9]*?[A-Za-z]+? [0-9][^<>]*?>", r"\1", value)
        references = BibleVerseParser(config.parserStandarisation).extractAllReferences(value)
        if references:
            b, c, v = references[0]
            return '<a href="javascript:void(0)" onclick="ctbcv({4}{0}{4},{1},{2},{3})">'.format(commentary, b, c, v, "'")
        else:
            return value

    def extractCommentaryReferences(self, match):
        value = match.group()
        references = BibleVerseParser(config.parserStandarisation).extractAllReferences(value)
        if references:
            b, c, v = references[0]
            return '<a href="javascript:void(0)" onclick="cbcv({0},{1},{2})">'.format(b, c, v)
        else:
            return value


class ThirdPartyDictionary:

    def __init__(self, module):
        self.module = module
        self.moduleList = self.getModuleList()
        if self.module in self.moduleList:
            self.database = os.path.join("thirdParty", "dictionaries", "{0}.dct.mybible".format(module))
            self.connection = sqlite3.connect(self.database)
            self.cursor = self.connection.cursor()

    def __del__(self):
        self.connection.close()

    def getModuleList(self):
        moduleFolder = os.path.join("thirdParty", "dictionaries")
        return [f[:-12] for f in os.listdir(moduleFolder) if os.path.isfile(os.path.join(moduleFolder, f)) and f.endswith(".dct.mybible")]

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
        query = "SELECT word FROM dictionary WHERE word = ?"
        self.cursor.execute(query, (entry,))
        content = self.cursor.fetchone()
        if not content:
            return "[not found]"
        else:
            return "<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, content[0])

    def getSimilarWord(self, entry):
        query = "SELECT word FROM dictionary WHERE word LIKE ? AND word != ?"
        self.cursor.execute(query, ("%{0}%".format(entry), entry))
        contentList = ["<ref onclick='openThirdDictionary(\"{0}\", \"{1}\")'>{1}</ref>".format(self.module, m[0]) for m in self.cursor.fetchall()]
        if not contentList:
            return "[not found]"
        else:
            return "<br>".join(contentList)

    def getData(self, entry):
        if not self.database:
            return "INVALID_COMMAND_ENTERED"
        else:
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
                content = re.sub("<a href='#d([^\n<>]*?)'>(.*?)</a>", r"<ref onclick='openThirdDictionary({1}{0}{1}, {1}\1{1})'>\2</ref>".format(self.module, '"'), content[0])
                content = Converter().formatNonBibleModule(content)
                return "<h2>{0}</h2><p>{1}</p><p>{2}</p>".format(entry, selectList, content)
