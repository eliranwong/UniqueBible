import os, re, config
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite, BibleSqlite
from ToolsSqlite import CrossReferenceSqlite, ImageSqlite, IndexesSqlite, EncyclopediaData, LexiconData, DictionaryData, ExlbData, SearchSqlite

class TextCommandParser:

    def parser(self, textCommad, source="main"):
        interpreters = {
            "_instantverse": self.instantVerse,
            "_instantword": self.instantWord,
            "_menu": self.textMenu,
            "_info": self.textInfo,
            "_image": self.textImage,
            "_command": self.textCommand,
            "main": self.textMain,
            "study": self.textStudy,
            "bible": self.textBible,
            "compare": self.textCompare,
            "parallel": self.textParallel,
            "verse": self.textVerseData,
            "word": self.textWordData,
            "commentary": self.textCommentary,
            "lexicon": self.textLexicon,
            "discourse": self.textDiscourse,
            "search": self.textCountSearch,
            "showsearch": self.textSearchBasic,
            "advancedsearch": self.textSearchAdvanced,
            "isearch": self.textCountISearch,
            "showisearch": self.textISearchBasic,
            "advancedisearch": self.textISearchAdvanced,
            "searchtool": self.textSearchTool,
            "lemma": self.textLemma,
            "morphologycode": self.textMorphologyCode,
            "morphology": self.textMorphology,
            "searchbook": self.textSearchBook,
            "index": self.textIndex,
            "exlb": self.textExlb,
            "dictionary": self.textDictionary,
            "encyclopedia": self.textEncyclopedia,
            "crossreference": self.textCrossReference,
            "tske": self.tske,
        } # add more later
        commandList = self.splitCommand(textCommad)
        if len(commandList) == 1:
            return self.textBibleVerseParser(textCommad, config.mainText)
        else:
            resourceType = commandList[0].lower()
            command = commandList[1]
            if resourceType in interpreters:
                return interpreters[resourceType](command, source)
            else:
                return self.textBibleVerseParser(textCommad, config.mainText)        

    def textCommand(self, command, source="main"):
        return ("command", command)

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
                    menu += "<hr><b>Special Features:</b><br>"
                    menu += "<button class='feature' onclick='document.title=\"COMPARE:::{0}\"'>Compare All Versions</button> ".format(mainVerseReference)
                    menu += "<button class='feature' onclick='document.title=\"CROSSREFERENCE:::{0}\"'>Scroll Mapper</button> ".format(mainVerseReference)
                    menu += "<button class='feature' onclick='document.title=\"TSKE:::{0}\"'>TSK (Enhanced)</button> ".format(mainVerseReference)
                    menu += "<button class='feature' onclick='document.title=\"INDEX:::{0}\"'>Smart Indexes</button>".format(mainVerseReference)
                    versions = biblesSqlite.getBibleList()
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
        parser = BibleVerseParser("YES")
        verseList = parser.extractAllReferences(text, tagged)
        del parser
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

    def textBibleVerseParser(self, command, text, view="main"):
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
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.mainText, command)
        commandList = self.splitCommand(command)
        texts = self.getConfirmedTexts(commandList[0])
        if not len(commandList) == 2 or not texts:
            return self.invalidCommand()
        else:
            return self.textBibleVerseParser(commandList[1], texts[0], source)

    def textSearchTool(self, command, source="main"):
        module, entry = self.splitCommand(command)
        searchSqlite = SearchSqlite()
        exactMatch = searchSqlite.getContent(module, entry)
        similarMatch = searchSqlite.getSimilarContent(module, entry)
        del searchSqlite
        return ("study", "<h2>Search <span style='color: brown;'>{0}</span> for <span style='color: brown;'>{1}</span></h2><p><b>Exact match:</b><br><br>{2}</p><p><b>Partial match:</b><br><br>{3}</b>".format(module, entry, exactMatch, similarMatch))

    def textImage(self, command, source):
        module, entry = self.splitCommand(command)
        imageSqlite = ImageSqlite()
        imageSqlite.exportImage(module, entry)
        del imageSqlite
        content = "<img src='images/{0}/{0}_{1}'>".format(module, entry)
        return ("popover", content)

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

    def textMain(self, command, source):
        return self.textAnotherView(command, "main")

    def textStudy(self, command, source):
        return self.textAnotherView(command, "study")

    def textAnotherView(self, command, target):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.mainText, command)
        commandList = self.splitCommand(command)
        texts = self.getConfirmedTexts(commandList[0])
        if not len(commandList) == 2 or not texts:
            return self.invalidCommand()
        else:
            return self.textBibleVerseParser(commandList[1], texts[0], target)

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
                parser = BibleVerseParser("YES")
                mainVerseReference = parser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
                del parser
                titles = ""
                verses = ""
                for text in confirmedTexts:
                    titles += "<th><ref onclick='document.title=\"BIBLE:::{0}:::{1}\"'>{0}</ref></th>".format(text, mainVerseReference)
                    verses += "<td style='vertical-align: text-top;'>{0}</td>".format(self.textBibleVerseParser(commandList[1], text)[1], source)
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

    def textCountSearch(self, command, source):
        return self.textCount(command, False)

    def textCountISearch(self, command, source):
        return self.textCount(command, True)

    def textCount(self, command, interlinear):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.mainText, command)
        commandList = self.splitCommand(command)
        texts = self.getConfirmedTexts(commandList[0])
        if not len(commandList) == 2 or not texts:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            searchResult = biblesSqlite.countSearchBible(texts[0], commandList[1], interlinear)
            del biblesSqlite
            return ("study", searchResult)

    def textSearchBasic(self, command, source):
        return self.textSearch(command, source, "BASIC")

    def textISearchBasic(self, command, source):
        return self.textSearch(command, source, "BASIC", True)

    def textSearchAdvanced(self, command, source):
        return self.textSearch(command, source, "ADVANCED")

    def textISearchAdvanced(self, command, source):
        return self.textSearch(command, source, "ADVANCED", True)

    def textSearch(self, command, source, mode, interlinear=False):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.mainText, command)
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

    def textSearchBook(self, command, source):
        return command # pending further development

    def textExlb(self, command, source):
        commandList = self.splitCommand(command)
        if commandList and len(commandList) == 2:
            exlbData = ExlbData()
            content = exlbData.getContent(commandList[0], commandList[1])
            del exlbData
            if not content:
                return self.invalidCommand("study")
            else:
                return ("study", content)
        else:
            return self.invalidCommand("study")


    def textDictionary(self, command, source):
        dictionaryData = DictionaryData()
        content = dictionaryData.getContent(command)
        del dictionaryData
        if not content:
            return self.invalidCommand("study")
        else:
            return ("study", content)

    def textEncyclopedia(self, command, source):
        commandList = self.splitCommand(command)
        if commandList and len(commandList) == 2:
            encyclopediaData = EncyclopediaData()
            content = encyclopediaData.getContent(commandList[0], commandList[1])
            del encyclopediaData
            if not content:
                return self.invalidCommand("study")
            else:
                return ("study", content)
        else:
            return self.invalidCommand("study")

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
        return ("study", content)

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
        return ("study", content)

    def textIndex(self, command, source):
        verseList = self.extractAllVerses(command)
        parser = BibleVerseParser("YES")
        indexesSqlite = IndexesSqlite()
        content = ""
        if not verseList:
            return self.invalidCommand()
        else:
            for verse in verseList:
                b, c, v = verse
                content += "<h2>Indexes: {0}</h2>".format(parser.bcvToVerseReference(b, c, v))
                content += indexesSqlite.getAllIndexes(verse)
                content += "<hr>"
        del indexesSqlite
        del parser
        return ("study", content)