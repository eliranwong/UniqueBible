import re, config
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite

class UbCommandParser:

    def parser(self, ubCommad):
        interpreters = {
            "bible": self.ubFormattedBible,
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
        commandList = re.split('[ ]*?:::[ ]*?', ubCommad, 1)
        if len(commandList) == 1:
            return self.ubBibleVerseParser(ubCommad)
        else:
            resourceType = commandList[0].lower()
            command = commandList[1]
            if resourceType in switcher:
                return interpreters[resourceType](command)
            else:
                return self.ubBibleVerseParser(ubCommad)

    def ubBibleVerseParser(self, command):
        Parser = BibleVerseParser("YES")
        verseList = Parser.extractAllReferences(command)
        del Parser
        numberOfVersesFound = len(verseList)
        if numberOfVersesFound == 0:
            return "No verse reference is found."
        elif numberOfVersesFound == 1:
            return self.ubFormattedBible(verseList[0])
        else:
            return self.ubPlainBible(verseList)

    def ubPlainBible(self, verseList):
        # expect verseList is a list of tuples
        biblesSqlite = BiblesSqlite()
        text = config.mainText
        verses = biblesSqlite.readMultipleVerses(text, verseList)
        del biblesSqlite
        return verses

    def ubFormattedBible(self, verse):
        # expect verse is a tuple
        biblesSqlite = BiblesSqlite() # use plain bibles database temporarily; for testing; will use bibles in marvelData/bibles instead
        text = config.mainText
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