import os, re, config
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite, Bible
from ToolsSqlite import CrossReferenceSqlite, ImageSqlite, IndexesSqlite, EncyclopediaData, LexiconData, DictionaryData, ExlbData, SearchSqlite, Commentary

class TextCommandParser:

    def __init__(self, parent):
        self.parent = parent

    def bcvToVerseReference(self, b, c, v):
        parser = BibleVerseParser("YES")
        verseReference = parser.bcvToVerseReference(b, c, v)
        del parser
        return verseReference

    def parser(self, textCommad, source="main"):
        interpreters = {
            "_instantverse": self.instantVerse,
            "_instantword": self.instantWord,
            "_menu": self.textMenu,
            "_commentary": self.textCommentaryMenu,
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
        }
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
        menu = biblesSqlite.getMenu(command, source)
        del biblesSqlite
        return (source, menu)

    def textCommentaryMenu(self, command, source):
        text, *_ = command.split(".")
        commentary = Commentary(text)
        commentaryMenu = commentary.getMenu(command)
        del commentary
        return ("study", commentaryMenu)

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
        config.mainB, config.mainC, config.mainV = bcvTuple
        self.parent.updateMainRefButton()

    def setStudyVerse(self, text, bcvTuple):
        config.studyText = text
        config.studyB, config.studyC, config.studyV = bcvTuple
        self.parent.updateStudyRefButton()
        config.commentaryB, config.commentaryC, config.commentaryV = bcvTuple
        self.parent.updateCommentaryRefButton()

    def setCommentaryVerse(self, text, bcvTuple):
        config.commentaryText = text
        config.commentaryB, config.commentaryC, config.commentaryV = bcvTuple
        self.parent.updateCommentaryRefButton()
        config.studyB, config.studyC, config.studyV = bcvTuple
        self.parent.updateStudyRefButton()

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
            bibleSqlite = Bible(text) # use plain bibles database when corresponding formatted version is not available
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

    def textCommentary(self, command, source):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.commentaryText, command)
        commandList = self.splitCommand(command)
        verseList = self.extractAllVerses(commandList[1])
        if not len(commandList) == 2 or not verseList:
            return self.invalidCommand()
        else:
            bcvTuple = verseList[0]
            module = commandList[0]
            commentary = Commentary(module)
            content =  commentary.getContent(bcvTuple)
            if not content == "INVALID_COMMAND_ENTERED":
                self.setCommentaryVerse(module, bcvTuple)
            del commentary
            return ("study", content)

    def textSearchTool(self, command, source="main"):
        module, entry = self.splitCommand(command)
        indexes = IndexesSqlite()
        toolList = [("", "[search other resources]"), ("EXLBP", "Exhaustive Library of Bible Characters"), ("EXLBL", "Exhaustive Library of Bible Locations")] + indexes.topicList + indexes.dictionaryList + indexes.encyclopediaList
        if module in dict(toolList[1:]).keys():
            action = "searchItem(this.value, \"{0}\")".format(entry)
            selectList = indexes.formatSelectList(action, toolList)
            if module in dict(indexes.topicList).keys():
                config.topic = module
            elif module in dict(indexes.dictionaryList).keys() and not module == "HBN":
                config.dictionary = module
            elif module in dict(indexes.encyclopediaList).keys():
                config.encyclopedia = module
            del indexes
            searchSqlite = SearchSqlite()
            exactMatch = searchSqlite.getContent(module, entry)
            similarMatch = searchSqlite.getSimilarContent(module, entry)
            del searchSqlite
            return ("study", "<h2>Search <span style='color: brown;'>{0}</span> for <span style='color: brown;'>{1}</span></h2><p>{4}</p><p><b>Exact match:</b><br><br>{2}</p><p><b>Partial match:</b><br><br>{3}</b>".format(module, entry, exactMatch, similarMatch, selectList))
        else:
            del indexes
            return self.invalidCommand()

    def textImage(self, command, source):
        module, entry = self.splitCommand(command)
        imageSqlite = ImageSqlite()
        imageSqlite.exportImage(module, entry)
        del imageSqlite
        content = "<img src='images/{0}/{0}_{1}'>".format(module, entry)
        return ("popover.{0}".format(source), content)

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
            views[source](config.mainText, verseList[-1])
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
            module, entry = commandList
            if module in ["exlbl", "exlbp", "exlbt"]:
                if module == "exlbt":
                    config.topic = "exlbt"
                exlbData = ExlbData()
                content = exlbData.getContent(commandList[0], commandList[1])
                del exlbData
                return ("study", content)
            else:
                return self.invalidCommand("study")
        else:
            return self.invalidCommand("study")

    def textDictionary(self, command, source):
        indexes = IndexesSqlite()
        dictionaryList = dict(indexes.dictionaryList).keys()
        del indexes
        module = command[:3]
        if module in dictionaryList:
            if not module == "HBN":
                config.dictionary = module
            dictionaryData = DictionaryData()
            content = dictionaryData.getContent(command)
            del dictionaryData
            return ("study", content)
        else:
            return self.invalidCommand("study")

    def textEncyclopedia(self, command, source):
        commandList = self.splitCommand(command)
        if commandList and len(commandList) == 2:
            module, entry = commandList
            indexes = IndexesSqlite()
            encyclopediaList = dict(indexes.encyclopediaList).keys()
            del indexes
            if module in encyclopediaList:
                config.encyclopedia = module
                encyclopediaData = EncyclopediaData()
                content = encyclopediaData.getContent(module, entry)
                del encyclopediaData
                return ("study", content)
            else:
                return self.invalidCommand("study")
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