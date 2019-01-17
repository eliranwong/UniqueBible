import os, re, config
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite, BibleSqlite
from ToolsSqlite import CrossReferenceSqlite

class TextCommandParser:

    def parser(self, textCommad, source="main"):
        interpreters = {
            "_instant": self.instant,
            "_menu": self.textMenu,
            "bible": self.textBible,
            "study": self.textStudy,
            "compare": self.textCompare,
            "parallel": self.textParallel,
            "verse": self.textVerseData,
            "word": self.textWordData,
            "commentary": self.textCommentary,
            "lexicon": self.textLexicon,
            "discourse": self.textDiscourse,
            "search": self.textSearchBasic,
            "advancedsearch": self.textSearchAdvanced,
            "lemma": self.textLemma,
            "morphologycode": self.textMorphologyCode,
            "morphology": self.textMorphology,
            "searchbook": self.textSearchBook,
            "exlb": self.textEXLB,
            "dictionary": self.textDictionary,
            "encyclopedia": self.textEncyclopedia,
            "crossreference": self.textCrossReference,
            "tske": self.tske,
        } # add more later
        commandList = self.splitCommand(textCommad)
        if len(commandList) == 1:
            return self.textBibleVerseParser(textCommad)
        else:
            resourceType = commandList[0].lower()
            command = commandList[1]
            if resourceType in interpreters:
                return interpreters[resourceType](command, source)
            else:
                return self.textBibleVerseParser(textCommad)        

    def textMenu(self, command, source="main"):
        biblesSqlite = BiblesSqlite()
        mainVerseReference = biblesSqlite.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        menu = "&lt;&lt;&lt; <ref onclick='document.title=\"BIBLE:::{0}:::{1}\"'>Go back to {1}</ref>".format(config.mainText, mainVerseReference)
        menu += "<hr><b>Texts:</b> {0}".format(biblesSqlite.getTexts())
        #menu = biblesSqlite.getTexts()
        items = command.split(".", 3)
        text = items[0]
        if not text == "":
            # i.e. text specified; add book menu
            menu += "<hr><b>Selected Text:</b> "+text
            menu += "<hr><b>Books:</b> {0}".format(biblesSqlite.getBooks(text))
            bcList = [int(i) for i in items[1:]]
            if bcList:
                check = len(bcList)
                if check >= 1:
                    # i.e. book specified; add chapter menu
                    menu += "<hr><b>Selected book:</b> {0}".format(biblesSqlite.bcvToVerseReference(bcList[0], 1, 1)[:-4])
                    menu += "<hr><b>Chapters:</b> {0}".format(biblesSqlite.getChapters(bcList[0], text))
                if check == 2:
                    # i.e. both book and chapter specified; add verse menu
                    menu += "<hr><b>Selected chapter:</b> {0}".format(bcList[1])
                    menu += "<hr><b>Verses:</b> {0}".format(biblesSqlite.getVerses(bcList[0], bcList[1], text))
        del biblesSqlite
        return (source, menu)

    def getChaptersMenu(self, b=config.mainB, text=config.mainText):
        biblesSqlite = BiblesSqlite()
        chapters = biblesSqlite.getChaptersMenu(b, text)
        del biblesSqlite
        return chapters

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

    def extractAllVerses(self, text, tagged=False):
        Parser = BibleVerseParser("YES")
        verseList = Parser.extractAllReferences(text, tagged)
        del Parser
        return verseList

    def invalidCommand(self, source="main"):
        return (source, "INVALID_COMMAND_ENTERED")

    def setMainVerse(self, text, bcvTuple):
        config.mainText = text
        config.mainB = bcvTuple[0]
        config.mainC = bcvTuple[1]
        config.mainV = bcvTuple[2]

    def setStudyVerse(self, text, bcvTuple):
        config.studyText = text
        config.studyB = bcvTuple[0]
        config.studyC = bcvTuple[1]
        config.studyV = bcvTuple[2]

    def textPlainBible(self, verseList, text=config.mainText):
        # expect verseList is a list of tuples
        biblesSqlite = BiblesSqlite()
        verses = biblesSqlite.readMultipleVerses(text, verseList)
        del biblesSqlite
        return verses

    def textFormattedBible(self, verse, text=config.mainText):
        chapter = ""
        formattedBiblesFolder = os.path.join("marvelData", "bibles")
        formattedBibles = [f[:-6] for f in os.listdir(formattedBiblesFolder) if os.path.isfile(os.path.join(formattedBiblesFolder, f)) and f.endswith(".bible")]
        if text in formattedBibles:
            # expect verse is a tuple
            bibleSqlite = BibleSqlite(text) # use plain bibles database when corresponding formatted version is not available
            chapter += bibleSqlite.readFormattedChapter(verse)
            del bibleSqlite
            return chapter
        else:
            # expect verse is a tuple
            biblesSqlite = BiblesSqlite() # use plain bibles database when corresponding formatted version is not available
            chapter += biblesSqlite.readPlainChapter(text, verse)
            del biblesSqlite
            return chapter

    def textBibleVerseParser(self, command, text=config.mainText, view="main"):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            views = {
                "main": self.setMainVerse,
                "study": self.setStudyVerse,
            }
            views[view](text, verseList[0])
            if len(verseList) == 1:
                chapters = self.getChaptersMenu()
                chapterMenuTop = chapters+"<hr>"
                chapterMenuBottom = "<hr>"+chapters
                content = "{0}{1}{2}".format(chapterMenuTop, self.textFormattedBible(verseList[0], text), chapterMenuBottom)
                return (view, content)
            else:
                content = self.textPlainBible(verseList, text)
                return (view, content)

    def textBible(self, command, source="main"):
        commandList = self.splitCommand(command)
        texts = self.getConfirmedTexts(commandList[0])
        if not len(commandList) == 2 or not texts:
            return self.invalidCommand()
        else:
            return self.textBibleVerseParser(commandList[1], texts[0], source)

    def instant(self, command, source="main"):
        commandList = self.splitCommand(command)
        biblesSqlite = BiblesSqlite()
        wordID = commandList[1]
        wordID = re.sub('^[h0]+?([^h0])', r'\1', wordID, flags=re.M)
        info = biblesSqlite.instantMorphology(int(commandList[0]), int(wordID))
        del biblesSqlite
        return ("instant", info)

    def textStudy(self, command, source):
        commandList = self.splitCommand(command)
        texts = self.getConfirmedTexts(commandList[0])
        if not len(commandList) == 2 or not texts:
            return self.invalidCommand()
        else:
            return self.textBibleVerseParser(commandList[1], texts[0], "study")

    def textCompare(self, command, source="main"):
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
            views = {
                "main": self.setMainVerse,
                "study": self.setStudyVerse,
            }
            views[source](config.mainText, verseList[len(verseList) - 1])
            biblesSqlite = BiblesSqlite()
            verses = biblesSqlite.compareVerse(verseList, confirmedTexts)
            del biblesSqlite
            return (source, verses)

    def textParallel(self, command, source="main"):
        commandList = self.splitCommand(command)
        if len(commandList) == 2:
            texts = commandList[0]
            confirmedTexts = self.getConfirmedTexts(texts)
            if not confirmedTexts:
                return self.invalidCommand()
            else:
                biblesSqlite = BiblesSqlite()
                mainVerseReference = biblesSqlite.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
                del biblesSqlite
                titles = ""
                verses = ""
                for text in confirmedTexts:
                    titles += "<th><ref onclick='document.title=\"BIBLE:::{0}:::{1}\"'>{0}</ref></th>".format(text, mainVerseReference)
                    verses += "<td style='vertical-align: text-top;'>{0}</td>".format(self.textBibleVerseParser(commandList[1], text)[1])
            return (source, "<table style='width:100%'><tr>{0}</tr><tr>{1}</tr></table>".format(titles, verses))
        else:
            return self.invalidCommand()

    def textVerseData(self, command):
        return command # pending further development

    def textWordData(self, command):
        return command # pending further development

    def textCommentary(self, command):
        return command # pending further development

    def textLexicon(self, command):
        return command # pending further development

    def textDiscourse(self, command):
        return command # pending further development

    def textSearchBasic(self, command, source):
        return self.textSearch(command, source, "BASIC")

    def textSearchAdvanced(self, command, source):
        return self.textSearch(command, source, "ADVANCED")

    def textSearch(self, command, source, mode):
        commandList = self.splitCommand(command)
        texts = self.getConfirmedTexts(commandList[0])
        if not len(commandList) == 2 or not texts:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            searchResult = biblesSqlite.searchBible(texts[0], mode, commandList[1])
            del biblesSqlite
            return ("study", searchResult)

    def textLemma(self, command, source):
        return self.textSearchMorphology(command, source, "LEMMA")

    def textMorphologyCode(self, command, source):
        return self.textSearchMorphology(command, source, "CODE")

    def textMorphology(self, command, source):
        return self.textSearchMorphology(command, source, "ADVANCED")

    def textSearchMorphology(self, command, source, mode):
        biblesSqlite = BiblesSqlite()
        searchResult = biblesSqlite.searchMorphology(mode, command)
        del biblesSqlite
        return ("study", searchResult)

    def textSearchBook(self, command):
        return command # pending further development

    def textEXLB(self, command):
        return command # pending further development

    def textDictionary(self, command):
        return command # pending further development

    def textEncyclopedia(self, command):
        return command # pending further development

    def textCrossReference(self, command, source):
        verseList = self.extractAllVerses(command)
        biblesSqlite = BiblesSqlite()
        crossReferenceSqlite = CrossReferenceSqlite()
        content = ""
        if not verseList:
            return self.invalidCommand()
        else:
            for verse in verseList:
                b, c, v = verse
                content += "<h2>Cross-reference: {0}</h2>".format(biblesSqlite.bcvToVerseReference(b, c, v))
                crossReferenceList = self.extractAllVerses(crossReferenceSqlite.scrollMapper(verse), True)
                if not crossReferenceList:
                    content += "[No cross-reference is found for this verse!]"
                else:
                    content += biblesSqlite.readMultipleVerses(config.mainText, crossReferenceList)
                content += "<hr>"
            del crossReferenceSqlite
            del biblesSqlite
            return ("study", content) # pending further development

    def tske(self, command, source):
        verseList = self.extractAllVerses(command)
        biblesSqlite = BiblesSqlite()
        crossReferenceSqlite = CrossReferenceSqlite()
        content = ""
        if not verseList:
            return self.invalidCommand()
        else:
            for verse in verseList:
                b, c, v = verse
                content += "<h2>TSKE: {0}</h2>".format(biblesSqlite.bcvToVerseReference(b, c, v))
                tskeContent = crossReferenceSqlite.tske(verse)
                content += "<div style='margin: 10px; padding: 0px 10px; border: 1px solid gray; border-radius: 5px;'>{0}</div>".format(tskeContent)
                crossReferenceList = self.extractAllVerses(tskeContent, False)
                if not crossReferenceList:
                    content += "[No content is found for this verse!]"
                else:
                    content += biblesSqlite.readMultipleVerses(config.mainText, crossReferenceList)
                content += "<hr>"
            del crossReferenceSqlite
            del biblesSqlite
            return ("study", content) # pending further development

