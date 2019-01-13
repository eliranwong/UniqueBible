import re, config
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite

class UbCommandParser:

    def parser(self, ubCommad):
        interpreters = {
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

    def splitCommand(self, command):
        commandList = re.split('[ ]*?:::[ ]*?', command, 1)
        return commandList

    def invalidCommand(self):
        return ("main", "INVALID_COMMAND_ENTERED")

    def ubBibleVerseParser(self, command, text=config.mainText):
        Parser = BibleVerseParser("YES")
        verseList = Parser.extractAllReferences(command)
        del Parser
        numberOfVersesFound = len(verseList)
        if numberOfVersesFound == 0:
            return self.invalidCommand()
        elif numberOfVersesFound == 1:
            return ("main", self.ubFormattedBible(verseList[0], text))
        else:
            return ("main", self.ubPlainBible(verseList, text))

    def ubBible(self, command):
        biblesSqlite = BiblesSqlite()
        bibleList = biblesSqlite.getBibleList()
        del biblesSqlite
        commandList = self.splitCommand(command)
        text = commandList[0]
        if text in bibleList and len(commandList) == 2:
            config.mainText = text
            return self.ubBibleVerseParser(commandList[1], text)
        return self.invalidCommand()

    def ubCompare(self, command):
        commandText = ""
        commandList = self.splitCommand(command)
        if len(commandList) == 2:
            texts = commandList[0].split("_")
            commandText = commandList[1]
            Parser = BibleVerseParser("YES")
            verseList = Parser.extractAllReferences(commandText)
            del Parser
            if not texts or not verseList:
                return self.invalidCommand()
            else:
                biblesSqlite = BiblesSqlite()
                verses = biblesSqlite.compareVerseList(verseList, texts)
                del biblesSqlite
                return ("main", verses)
        elif len(commandList) == 1:
            commandText = commandList[0]
            Parser = BibleVerseParser("YES")
            verseList = Parser.extractAllReferences(commandText)
            del Parser
            if not verseList:
                return self.invalidCommand()
            else:
                biblesSqlite = BiblesSqlite()
                verses = biblesSqlite.compareVerseList(verseList)
                del biblesSqlite
                return ("main", verses)

    def ubParallel(self, command):
        biblesSqlite = BiblesSqlite()
        bibleList = biblesSqlite.getBibleList()
        del biblesSqlite
        commandList = self.splitCommand(command)
        if len(commandList) == 2:
            titles = "<tr>"
            verses = "<tr>"
            bibles = commandList[0]
            texts = bibles.split("_")
            for text in texts:
                if text in bibleList:
                    titles += "<th>"+text+"</th>"
                    verses += "<td style='vertical-align: text-top;'>"+self.ubBibleVerseParser(commandList[1], text)[1]+"</td>"
            titles += "</tr>"
            verses += "</tr>"
            return ("main", "<table style='width:100%'>"+titles+verses+"</table>")
        else:
            return self.invalidCommand()
            

    def ubPlainBible(self, verseList, text=config.mainText):
        # expect verseList is a list of tuples
        biblesSqlite = BiblesSqlite()
        verses = biblesSqlite.readMultipleVerses(text, verseList)
        del biblesSqlite
        return verses

    def ubFormattedBible(self, verse, text=config.mainText):
        # expect verse is a tuple
        biblesSqlite = BiblesSqlite() # use plain bibles database temporarily; for testing; will use bibles in marvelData/bibles instead
        chapter = biblesSqlite.readPlainChapter(text, verse)
        del biblesSqlite
        return chapter # pending further development

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