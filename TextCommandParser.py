import os, re, config
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite, BibleSqlite
from ToolsSqlite import CrossReferenceSqlite, LexiconData, ImageSqlite

class TextCommandParser:

    def parser(self, textCommad, source="main"):
        interpreters = {
            "_instantverse": self.instantVerse,
            "_instantword": self.instantWord,
            "_menu": self.textMenu,
            "_info": self.textInfo,
            "main": self.textAnotherView,
            "study": self.textAnotherView,
            "bible": self.textBible,
            "compare": self.textCompare,
            "parallel": self.textParallel,
            "verse": self.textVerseData,
            "word": self.textWordData,
            "commentary": self.textCommentary,
            "lexicon": self.textLexicon,
            "discourse": self.textDiscourse,
            "search": self.textSearchBasic,
            "advancedsearch": self.textSearchAdvanced,
            "isearch": self.textISearchBasic,
            "advancedisearch": self.textISearchAdvanced,
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

    def textInfo(self, command, source="main"):
        return ("instant", command)

    def textMenu(self, command, source="main"):
        biblesSqlite = BiblesSqlite()
        mainVerseReference = biblesSqlite.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        menu = "<ref onclick='document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; Go back to {1}</ref>".format(config.mainText, mainVerseReference)
        menu += "<hr><b>Texts:</b> {0}".format(biblesSqlite.getTexts())
        #menu = biblesSqlite.getTexts()
        items = command.split(".", 3)
        text = items[0]
        if not text == "":
            # i.e. text specified; add book menu
            menu += "<hr><b>Selected Text:</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span>".format(text)
            menu += "<hr><b>Books:</b> {0}".format(biblesSqlite.getBooks(text))
            bcList = [int(i) for i in items[1:]]
            if bcList:
                check = len(bcList)
                if check >= 1:
                    # i.e. book specified; add chapter menu
                    menu += "<hr><b>Selected book:</b> <span style='color: brown;' onmouseover='bookName(\"{0}\")'>{0}</span>".format(biblesSqlite.bcvToVerseReference(bcList[0], 1, 1)[:-4])
                    menu += "<hr><b>Chapters:</b> {0}".format(biblesSqlite.getChapters(bcList[0], text))
                if check >= 2:
                    # i.e. both book and chapter specified; add verse menu
                    menu += "<hr><b>Selected chapter:</b> <span style='color: brown;' onmouseover='document.title=\"_info:::Chapter {0}\"'>{0}</span>".format(bcList[1])
                    menu += "<hr><b>Verses:</b> {0}".format(biblesSqlite.getVerses(bcList[0], bcList[1], text))
                if check == 3:
                    if source == "main":
                        anotherView = "<ref onclick='document.title=\"STUDY:::{0}:::{1}\"'>open on Study View</ref>".format(text, mainVerseReference)
                    elif source == "study":
                        anotherView = "<ref onclick='document.title=\"MAIN:::{0}:::{1}\"'>open on Main View</ref>".format(text, mainVerseReference)
                    menu += "<hr><b>Selected verse:</b> <span style='color: brown;' onmouseover='document.title=\"_instantVerse:::{0}:::{1}.{2}.{3}\"'>{3}</span> [{4}]".format(text, bcList[0], bcList[1], bcList[2], anotherView)
                    menu += "<hr>"
                    menu += "<ref onclick='document.title=\"COMPARE:::{0}\"'>Compare All Versions</ref> | ".format(mainVerseReference)
                    menu += "<ref onclick='document.title=\"CROSSREFERENCE:::{0}\"'>Scroll Mapper</ref> | ".format(mainVerseReference)
                    menu += "<ref onclick='document.title=\"TSKE:::{0}\"'>TSK (Enhanced)</ref>".format(mainVerseReference)
                    versions = biblesSqlite.getBibleList()
                    menu += "<hr><b>Compare <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> with:</b> ".format(text)
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='compare{0}'></div> ".format(version)
                            menu += "<script>versionList.push('{0}');</script>".format(version)
                    menu += "<button type='button' onclick='checkCompare();'>Start Comparison</button>"
                    menu += "<hr><b>Parallel <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> with:</b> ".format(text)
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='parallel{0}'></div> ".format(version)
                    menu += "<button type='button' onclick='checkParallel();'>Start Parallel Reading</button>"
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
                chapters = self.getChaptersMenu(verseList[0][0], text)
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

    def instantVerse(self, command, source="main"):
        commandList = self.splitCommand(command)
        biblesSqlite = BiblesSqlite()
        b, c, v = [int(i) for i in commandList[1].split(".")]
        info = biblesSqlite.instantVerse("interlinear", b, c, v)
        del biblesSqlite
        return ("instant", info)

    def instantWord(self, command, source="main"):
        commandList = self.splitCommand(command)
        biblesSqlite = BiblesSqlite()
        wordID = commandList[1]
        wordID = re.sub('^[h0]+?([^h0])', r'\1', wordID, flags=re.M)
        info = biblesSqlite.instantWord(int(commandList[0]), int(wordID))
        del biblesSqlite
        return ("instant", info)

    def textAnotherView(self, command, source):
        commandList = self.splitCommand(command)
        texts = self.getConfirmedTexts(commandList[0])
        if not len(commandList) == 2 or not texts:
            return self.invalidCommand()
        else:
            anotherView = {
                "main": "study",
                "study": "main",
            }
            return self.textBibleVerseParser(commandList[1], texts[0], anotherView[source])

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
            return (source, "<table style='width:100%; table-layout:fixed;'><tr>{0}</tr><tr>{1}</tr></table>".format(titles, verses))
        else:
            return self.invalidCommand()

    def textVerseData(self, command):
        return command # pending further development

    def textWordData(self, command, source):
        commandList = self.splitCommand(command)
        biblesSqlite = BiblesSqlite()
        info = biblesSqlite.wordData(int(commandList[0]), int(commandList[1]))
        del biblesSqlite
        return ("study", info)

    def textCommentary(self, command):
        return command # pending further development

    def textLexicon(self, command, source):
        commandList = self.splitCommand(command)
        if len(commandList) == 2:
            lexiconData = LexiconData()
            content = lexiconData.lexicon(commandList[0], commandList[1])
            del lexiconData
            return ("study", content)
        elif len(commandList) == 1:
            type = commandList[0][0]
            defaultLexicon = {
                "H": "TBESH",
                "G": "TBESG",
                "E": "ConcordanceMorphology",
                "L": "LXX",
            }
            defaultLexicon = defaultLexicon[type]
            lexiconData = LexiconData()
            content = lexiconData.lexicon(defaultLexicon, commandList[0])
            del lexiconData
            return ("study", content)
        else:
            return self.invalidCommand()

    def textDiscourse(self, command, source):
        return command # pending further development

    def textSearchBasic(self, command, source):
        return self.textSearch(command, source, "BASIC")

    def textISearchBasic(self, command, source):
        return self.textSearch(command, source, "BASIC", True)

    def textSearchAdvanced(self, command, source):
        return self.textSearch(command, source, "ADVANCED")

    def textISearchAdvanced(self, command, source):
        return self.textSearch(command, source, "ADVANCED", True)

    def textSearch(self, command, source, mode, interlinear=False):
        commandList = self.splitCommand(command)
        texts = self.getConfirmedTexts(commandList[0])
        if not len(commandList) == 2 or not texts:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            searchResult = biblesSqlite.searchBible(texts[0], mode, commandList[1], interlinear)
            del biblesSqlite
            return ("study", searchResult)

    def textLemma(self, command, source):
        return self.textSearchMorphology(command, source, "LEMMA")

    def textMorphologyCode(self, command, source):
        return self.textSearchMorphology(command, source, "MORPHOLOGYCODE")

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

