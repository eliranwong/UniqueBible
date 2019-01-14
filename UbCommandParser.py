import os, re, config
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite

class UbCommandParser:

    def parser(self, ubCommad):
        interpreters = {
            "text": self.ubText,
            "book": self.ubBook,
            "chapter": self.ubChapter,
            "verse": self.ubVerse,
            "bible": self.ubBible,
            "compare": self.ubCompare,
            "parallel": self.ubParallel,
            "verse": self.ubVerseData,
            "word": self.ubWordData,
            "commentary": self.ubCommentary,
            "lexicon": self.ubLexicon,
            "discourse": self.ubDiscourse,
            "searchbible": self.ubSearchBible,
            "searchmorphology": self.ubSearchMorphology,
            "searchbook": self.ubSearchBook,
            "exlb": self.ubEXLB,
            "dictionary": self.ubDictionary,
            "encyclopedia": self.ubEncyclopedia,
            "crossreference": self.ubCrossReference,
        } # add more later
        commandList = self.splitCommand(ubCommad)
        if len(commandList) == 1:
            return self.ubBibleVerseParser(ubCommad)
        else:
            resourceType = commandList[0].lower()
            command = commandList[1]
            if resourceType in interpreters:
                return interpreters[resourceType](command)
            else:
                return self.ubBibleVerseParser(ubCommad)

    def ubText(self):
        pass

    def ubBook(self):
        pass

    def ubChapter(self, command):
        biblesSqlite = BiblesSqlite()
        chapterList = biblesSqlite.getChapterList(config.mainB)
        del biblesSqlite
        chapters = ""
        for chapter in chapterList:
            chapters += "{} ".format(chapter)
        return ("main", chapters)

    def ubVerse(self):
        pass

    def splitCommand(self, command):
        commandList = re.split('[ ]*?:::[ ]*?', command, 1)
        return commandList

    def getConfirmedTexts(self, texts):
        biblesSqlite = BiblesSqlite()
        bibleList = biblesSqlite.getBibleList()
        del biblesSqlite
        texts = texts.split("_")
        confirmedTexts = [text for text in texts if text in bibleList]
        return confirmedTexts

    def extractAllVerses(self, text):
        Parser = BibleVerseParser("YES")
        verseList = Parser.extractAllReferences(text)
        del Parser
        return verseList

    def invalidCommand(self):
        return ("main", "INVALID_COMMAND_ENTERED")

    def setMainVerse(self, text, bcvTuple):
        config.mainText = text
        config.mainB = bcvTuple[0]
        config.mainC = bcvTuple[1]
        config.mainV = bcvTuple[2]

    def ubPlainBible(self, verseList, text=config.mainText):
        # expect verseList is a list of tuples
        biblesSqlite = BiblesSqlite()
        verses = biblesSqlite.readMultipleVerses(text, verseList)
        del biblesSqlite
        return verses

    def ubFormattedBible(self, verse, text=config.mainText):
        chapter = ""
        formattedBiblesFolder = os.path.join("marvelData", "bibles")
        formattedBibles = [f[:-6] for f in os.listdir(formattedBiblesFolder) if os.path.isfile(os.path.join(formattedBiblesFolder, f)) and f.endswith(".bible")]
        if text in formattedBibles:
            return "[pending revision here]"
        else:
            # expect verse is a tuple
            biblesSqlite = BiblesSqlite() # use plain bibles database when corresponding formatted version is not available
            chapter += biblesSqlite.readPlainChapter(text, verse)
            del biblesSqlite
            return chapter # pending further development

    def ubBibleVerseParser(self, command, text=config.mainText):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            self.setMainVerse(text, verseList[0])
            if len(verseList) == 1:
                return ("main", self.ubFormattedBible(verseList[0], text))
            else:
                return ("main", self.ubPlainBible(verseList, text))

    def ubBible(self, command):
        commandList = self.splitCommand(command)
        texts = self.getConfirmedTexts(commandList[0])
        if not len(commandList) == 2 or not texts:
            return self.invalidCommand()
        else:
            return self.ubBibleVerseParser(commandList[1], texts[0])

    def ubCompare(self, command):
        commandText = ""
        commandList = self.splitCommand(command)
        if len(commandList) == 2:
            confirmedTexts = self.getConfirmedTexts(commandList[0])
            verseList = self.extractAllVerses(commandList[1])
        elif len(commandList) == 1:
            confirmedTexts = ["ALL"]
            verseList = self.extractAllVerses(commandList[0])
        if not confirmedTexts or not verseList:
            return self.invalidCommand()
        else:
            self.setMainVerse(config.mainText, verseList[len(verseList) - 1])
            biblesSqlite = BiblesSqlite()
            verses = biblesSqlite.compareVerse(verseList, confirmedTexts)
            del biblesSqlite
            return ("main", verses)

    def ubParallel(self, command):
        commandList = self.splitCommand(command)
        if len(commandList) == 2:
            texts = commandList[0]
            confirmedTexts = self.getConfirmedTexts(texts)
            if not confirmedTexts:
                return self.invalidCommand()
            else:
                titles = ""
                verses = ""
                for text in confirmedTexts:
                    titles += "<th>{0}</th>".format(text)
                    verses += "<td style='vertical-align: text-top;'>{0}</td>".format(self.ubBibleVerseParser(commandList[1], text)[1])
            return ("main", "<table style='width:100%'><tr>{0}</tr><tr>{1}</tr></table>".format(titles, verses))
        else:
            return self.invalidCommand()

    def ubVerseData(self, command):
        return command # pending further development

    def ubWordData(self, command):
        return command # pending further development

    def ubCommentary(self, command):
        return command # pending further development

    def ubLexicon(self, command):
        return command # pending further development

    def ubDiscourse(self, command):
        return command # pending further development

    def ubSearchBible(self, command):
        return command # pending further development

    def ubSearchMorphology(self, command):
        return command # pending further development

    def ubSearchBook(self, command):
        return command # pending further development

    def ubEXLB(self, command):
        return command # pending further development

    def ubDictionary(self, command):
        return command # pending further development

    def ubEncyclopedia(self, command):
        return command # pending further development

    def ubCrossReference(self, command):
        return command # pending further development

    # add more later