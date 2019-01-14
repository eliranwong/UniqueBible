import os, re, config
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

    def extractAllVerses(self, text):
        Parser = BibleVerseParser("YES")
        verseList = Parser.extractAllReferences(text)
        del Parser
        return verseList

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
        biblesSqlite = BiblesSqlite()
        bibleList = biblesSqlite.getBibleList()
        del biblesSqlite
        commandList = self.splitCommand(command)
        text = commandList[0]
        if text in bibleList and len(commandList) == 2:
            return self.ubBibleVerseParser(commandList[1], text)
        return self.invalidCommand()

    def ubCompare(self, command):
        commandText = ""
        commandList = self.splitCommand(command)
        if len(commandList) == 2:
            texts = commandList[0].split("_")
            commandText = commandList[1]
            verseList = self.extractAllVerses(commandText)
            if not texts or not verseList:
                return self.invalidCommand()
            else:
                self.setMainVerse(config.mainText, verseList[len(verseList) - 1])
                biblesSqlite = BiblesSqlite()
                verses = biblesSqlite.compareVerseList(verseList, texts)
                del biblesSqlite
                return ("main", verses)
        elif len(commandList) == 1:
            commandText = commandList[0]
            verseList = self.extractAllVerses(commandText)
            if not verseList:
                return self.invalidCommand()
            else:
                self.setMainVerse(config.mainText, verseList[len(verseList) - 1])
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
            textsConfirmed = [text for text in texts if text in bibleList]
            if not textsConfirmed:
                return self.invalidCommand()
            else:
                for text in textsConfirmed:
                    titles += "<th>"+text+"</th>"
                    verses += "<td style='vertical-align: text-top;'>"+self.ubBibleVerseParser(commandList[1], text)[1]+"</td>"
            titles += "</tr>"
            verses += "</tr>"
            return ("main", "<table style='width:100%'>"+titles+verses+"</table>")
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