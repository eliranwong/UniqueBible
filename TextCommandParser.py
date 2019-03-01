import os, re, config, webbrowser
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite, Bible, ClauseData, MorphologySqlite
from ToolsSqlite import CrossReferenceSqlite, ImageSqlite, IndexesSqlite, EncyclopediaData, DictionaryData, ExlbData, SearchSqlite, Commentary, VerseData, WordData, BookData, Lexicon
from ThirdParty import ThirdPartyDictionary
from NoteSqlite import NoteSqlite

class TextCommandParser:

    def __init__(self, parent):
        self.parent = parent

    def parser(self, textCommad, source="main"):
        interpreters = {
            "_imv": self.instantMainVerse,
            "_instantverse": self.instantVerse,
            "_instantword": self.instantWord,
            "_menu": self.textMenu,
            "_commentary": self.textCommentaryMenu,
            "_book": self.textBookMenu,
            "_info": self.textInfo,
            "_bibleinfo": self.textBibleInfo,
            "_commentaryinfo": self.textCommentaryInfo,
            "_command": self.textCommand,
            "_history": self.textHistory,
            "_historyrecord": self.textHistoryRecord,
            "_image": self.textImage,
            "_editchapternote": self.editChapterNote,
            "_editversenote": self.editVerseNote,
            "_openchapternote": self.openChapterNote,
            "_openversenote": self.openVerseNote,
            "_openfile": self.textOpenFile,
            "_editfile": self.textEditFile,
            "_website": self.textWebsite,
            "_uba": self.textUba,
            "_biblenote": self.textBiblenote,
            "_lxxword": self.textLxxWord,
            "main": self.textMain,
            "study": self.textStudy,
            "bible": self.textBible,
            "text": self.textText,
            "compare": self.textCompare,
            "parallel": self.textParallel,
            "word": self.textWordData,
            "commentary": self.textCommentary,
            "commentary2": self.textCommentary2,
            "book": self.textBook,
            "searchbook": self.textSearchBook,
            "searchchapternote": self.textSearchChapterNote,
            "searchversenote": self.textSearchVerseNote,
            "clause": self.textClause,
            "combo": self.textCombo,
            "translation": self.textTranslation,
            "discourse": self.textDiscourse,
            "words": self.textWords,
            "lexicon": self.textLexicon,
            "search": self.textCountSearch,
            "showsearch": self.textSearchBasic,
            "advancedsearch": self.textSearchAdvanced,
            "andsearch": self.textAndSearch,
            "orsearch": self.textOrSearch,
            "isearch": self.textCountISearch,
            "andisearch": self.textAndISearch,
            "orisearch": self.textOrISearch,
            "showisearch": self.textISearchBasic,
            "advancedisearch": self.textISearchAdvanced,
            "searchtool": self.textSearchTool,
            "lemma": self.textLemma,
            "morphologycode": self.textMorphologyCode,
            "morphology": self.textMorphology,
            "searchmorphology": self.textSearchMorphology,
            "index": self.textIndex,
            "exlb": self.textExlb,
            "dictionary": self.textDictionary,
            "encyclopedia": self.textEncyclopedia,
            "crossreference": self.textCrossReference,
            "tske": self.tske,
            "searchthirddictionary": self.thirdDictionarySearch,
            "thirddictionary": self.thirdDictionaryOpen,
        }
        commandList = self.splitCommand(textCommad)
        updateViewConfig, viewText, *_ = self.getViewConfig(source)
        if len(commandList) == 1:
            if self.isDatabaseInstalled("bible"):
                return self.textBibleVerseParser(textCommad, viewText, source)
            else:
                return self.databaseNotInstalled("bible")
        else:
            keyword, command = commandList
            keyword = keyword.lower()
            if keyword in interpreters:
                if self.isDatabaseInstalled(keyword):
                    return interpreters[keyword](command, source)
                else:
                    return self.databaseNotInstalled(keyword)
            else:
                if self.isDatabaseInstalled("bible"):
                    return self.textBibleVerseParser(textCommad, viewText, source)
                else:
                    return self.databaseNotInstalled("bible")

    # check if a particular database is installed
    def databaseInfo(self):
        return {
            "_menu": self.getCoreBiblesInfo(),
            "_instantverse": self.getCoreBiblesInfo(),
            "_instantword": self.getCoreBiblesInfo(),
            "_bibleinfo": self.getCoreBiblesInfo(),
            "main": self.getCoreBiblesInfo(),
            "study": self.getCoreBiblesInfo(),
            "bible": self.getCoreBiblesInfo(),
            "text": self.getCoreBiblesInfo(),
            "compare": self.getCoreBiblesInfo(),
            "parallel": self.getCoreBiblesInfo(),
            "search": self.getCoreBiblesInfo(),
            "showsearch": self.getCoreBiblesInfo(),
            "advancedsearch": self.getCoreBiblesInfo(),
            "andsearch": self.getCoreBiblesInfo(),
            "orsearch": self.getCoreBiblesInfo(),
            "isearch": self.getCoreBiblesInfo(),
            "andisearch": self.getCoreBiblesInfo(),
            "orisearch": self.getCoreBiblesInfo(),
            "showisearch": self.getCoreBiblesInfo(),
            "advancedisearch": self.getCoreBiblesInfo(),
            "lemma": self.getCoreBiblesInfo(),
            "morphologycode": self.getCoreBiblesInfo(),
            "morphology": self.getCoreBiblesInfo(),
            "searchmorphology": self.getCoreBiblesInfo(),
            "_commentary": self.getLastCommentaryInfo(),
            "commentary": self.getLastCommentaryInfo(),
            "_openchapternote": self.getBibleNoteInfo(),
            "_openversenote": self.getBibleNoteInfo(),
            "_editchapternote": self.getBibleNoteInfo(),
            "_editversenote": self.getBibleNoteInfo(),
            "searchchapternote": self.getBibleNoteInfo(),
            "searchversenote": self.getBibleNoteInfo(),
            "_book": self.getBookInfo(),
            "book": self.getBookInfo(),
            "searchbook": self.getBookInfo(),
            "crossreference": self.getXRefInfo(),
            "tske": self.getXRefInfo(),
            "_image": (("marvelData", "images.sqlite"), "1_fo1CzhzT6h0fEHS_6R0JGDjf9uLJd3r"),
            "index": (("marvelData", "indexes.sqlite"), "1Fdq3C9hyoyBX7riniByyZdW9mMoMe6EX"),
            "searchtool": (("marvelData", "search.sqlite"), "1A4s8ewpxayrVXamiva2l1y1AinAcIKAh"),
            "word": (("marvelData", "data", "wordNT.data"), "11pmVhecYEtklcB4fLjNP52eL9pkytFdS"),
            "clause": (("marvelData", "data", "clauseNT.data"), "11pmVhecYEtklcB4fLjNP52eL9pkytFdS"),
            "translation": (("marvelData", "data", "translation.data"), "13d3QeUHhlttgOQ_U7Ag1jgawqrXzOaBq"),
            "discourse": (("marvelData", "data", "discourse.data"), "13d3QeUHhlttgOQ_U7Ag1jgawqrXzOaBq"),
            "words": (("marvelData", "data", "words.data"), "13d3QeUHhlttgOQ_U7Ag1jgawqrXzOaBq"),
            "combo": (("marvelData", "data", "words.data"), "13d3QeUHhlttgOQ_U7Ag1jgawqrXzOaBq"),
            "lexicon": (("marvelData", "lexicons", "MCGED.lexicon"), "157Le0xw2ovuoF2v9Bf6qeck0o15RGfMM"),
            "exlb": (("marvelData", "data", "exlb.data"), "1kA5appVfyQ1lWF1czEQWtts4idogHIpa"),
            "dictionary": (("marvelData", "data", "dictionary.data"), "1NfbkhaR-dtmT1_Aue34KypR3mfPtqCZn"),
            "encyclopedia": (("marvelData", "data", "encyclopedia.data"), "1OuM6WxKfInDBULkzZDZFryUkU1BFtym8"),
        }

    def getCoreBiblesInfo(self):
        return (("marvelData", "morphology.sqlite"), "1Vn3UXicjqDQSA41ek3_zJ7n2iAlspU_3")

    def getBibleNoteInfo(self):
        return (("marvelData", "note.sqlite"), "1OcHrAXLS-OLDG5Q7br6mt2WYCedk8lnW")

    def getBookInfo(self):
        return (("marvelData", "books", "Timelines.book"), "1nuhrsujL6LYYeviaT22Rhn_wk9kc6una")

    def getXRefInfo(self):
        return (("marvelData", "cross-reference.sqlite"), "1gZNqhwER_-IWYPaMNGZ229teJ5cSA7My")

    def getLastCommentaryInfo(self):
        return (("marvelData", "commentaries", "c{0}.commentary".format(config.commentaryText)), self.getCommentaryCloudID(config.commentaryText))

    def getMarvelBibles(self):
        return {
            "ASV": (("marvelData", "bibles", "ASV.bible"), "1oDuV54_zOl_L0GQqmYiLvgjk2pQu4iSr"),
            "BSB": (("marvelData", "bibles", "BSB.bible"), "1fQX8cT12LE9Q3dBUJyezTYg4a0AbdKbN"),
            "CUV": (("marvelData", "bibles", "CUV.bible"), "1iqsHxOWD_H-BABbjq03qIIrTu8u-UyjJ"),
            "CUVs": (("marvelData", "bibles", "CUVs.bible"), "1neY4KK3tfVtmnoLQu6YVMCyIhqcFEiPZ"),
            "ISV": (("marvelData", "bibles", "ISV.bible"), "1_nmaakABx8wVsQHdBL9rVh2wtRK8uyyW"),
            "KJV": (("marvelData", "bibles", "KJV.bible"), "1ycOkEJ2JI_4iwjllb4mE02wkDvrsPlNq"),
            "LEB": (("marvelData", "bibles", "LEB.bible"), "1p-_phmh3y54i4FSLhzEd33_v0kzSjAZn"),
            "LXX1": (("marvelData", "bibles", "LXX1.bible"), "1sjPa7oP9SnsrsPyQ1JPUGbwgMT8QE8F1"),
            "LXX1i": (("marvelData", "bibles", "LXX1i.bible"), "1pxj_pg7412ZA9ojnkI1iV46c6J3_7SJ9"),
            "LXX2": (("marvelData", "bibles", "LXX2.bible"), "1fK99KgtdFhEQssvYVp3fPQZNJBFBpEca"),
            "LXX2i": (("marvelData", "bibles", "LXX2i.bible"), "1E-i68TbbxxvDTzzzl-aFTXwmsro9LUjZ"),
            "MAB": (("marvelData", "bibles", "MAB.bible"), "1baA_5OkjO6-dk2dIQ4rcJ2VaAZqy1gRT"),
            "MIB": (("marvelData", "bibles", "MIB.bible"), "106g4L5fO5UBjzGv641H0rdXFvTB9COvs"),
            "MOB": (("marvelData", "bibles", "MOB.bible"), "1OG28pqdbEOxk1Kjly6EPvsMDRXJ4_RsR"),
            "MPB": (("marvelData", "bibles", "MPB.bible"), "1gl2KDzxXIjXOC71ZYVQZduAzqaSK3fEU"),
            "MTB": (("marvelData", "bibles", "MTB.bible"), "1HqJoGzWrsPqkys3IydAbogZ5NeI47WE8"),
            "NET": (("marvelData", "bibles", "NET.bible"), "1pJ_9Wk4CmDdFO08wioOxs4krKjNeh4Ur"),
            "ULT": (("marvelData", "bibles", "ULT.bible"), "10Udo5ND0a26hPIcJHNOuNqJ2feZuVXjT"),
            "UST": (("marvelData", "bibles", "UST.bible"), "1OFwdXRwC9gG4PJLt5j4NHWgFs9wcgXQk"),
            "WEB": (("marvelData", "bibles", "WEB.bible"), "1L9qAeamdZwGzVdf7jC4_ks05hyQa2R7l"),
        }

    def getCommentaryCloudID(self, commentary):
        cloudIDs = {
            "Barnes": "13uxButnFH2NRUV-YuyRZYCeh1GzWqO5J",
            "Benson": "1MSRUHGDilogk7_iZHVH5GWkPyf8edgjr",
            "BI": "1DUATP_0M7SwBqsjf20YvUDblg3_sOt2F",
            "Brooks": "1pZNRYE6LqnmfjUem4Wb_U9mZ7doREYUm",
            "Calvin": "1FUZGK9n54aXvqMAi3-2OZDtRSz9iZh-j",
            "CBSC": "1IxbscuAMZg6gQIjzMlVkLtJNDQ7IzTh6",
            "CECNT": "1MpBx7z6xyJYISpW_7Dq-Uwv0rP8_Mi-r",
            "CGrk": "1Jf51O0R911Il0V_SlacLQDNPaRjumsbD",
            "CHP": "1dygf2mz6KN_ryDziNJEu47-OhH8jK_ff",
            "Clarke": "1ZVpLAnlSmBaT10e5O7pljfziLUpyU4Dq",
            "CPBST": "14zueTf0ioI-AKRo_8GK8PDRKael_kB1U",
            "EBC": "1UA3tdZtIKQEx-xmXtM_SO1k8S8DKYm6r",
            "ECER": "1sCJc5xuxqDDlmgSn2SFWTRbXnHSKXeh_",
            "EGNT": "1ZvbWnuy2wwllt-s56FUfB2bS2_rZoiPx",
            "GCT": "1vK53UO2rggdcfcDjH6mWXAdYti4UbzUt",
            "Gill": "1O5jnHLsmoobkCypy9zJC-Sw_Ob-3pQ2t",
            "Henry": "1m-8cM8uZPN-fLVcC-a9mhL3VXoYJ5Ku9",
            "HH": "1RwKN1igd1RbN7phiJDiLPhqLXdgOR0Ms",
            "ICCNT": "1QxrzeeZYc0-GNwqwdDe91H4j1hGSOG6t",
            "JFB": "1NT02QxoLeY3Cj0uA_5142P5s64RkRlpO",
            "KD": "1rFFDrdDMjImEwXkHkbh7-vX3g4kKUuGV",
            "Lange": "1_PrTT71aQN5LJhbwabx-kjrA0vg-nvYY",
            "MacL": "1p32F9MmQ2wigtUMdCU-biSrRZWrFLWJR",
            "PHC": "1xTkY_YFyasN7Ks9me3uED1HpQnuYI8BW",
            "Pulpit": "1briSh0oDhUX7QnW1g9oM3c4VWiThkWBG",
            "Rob": "17VfPe4wsnEzSbxL5Madcyi_ubu3iYVkx",
            "Spur": "1OVsqgHVAc_9wJBCcz6PjsNK5v9GfeNwp",
            "Vincent": "1ZZNnCo5cSfUzjdEaEvZ8TcbYa4OKUsox",
            "Wesley": "1rerXER1ZDn4e1uuavgFDaPDYus1V-tS5",
            "Whedon": "1FPJUJOKodFKG8wsNAvcLLc75QbM5WO-9",
        }
        if commentary in cloudIDs:
            return cloudIDs[commentary]
        else:
            return ""

    def isDatabaseInstalled(self, keyword):
        if keyword in self.databaseInfo():
            fileItems = self.databaseInfo()[keyword][0]
            if os.path.isfile(os.path.join(*fileItems)):
                return True
            else:
                return False
        else:
            return True

    def databaseNotInstalled(self, keyword):
        databaseInfo = self.databaseInfo()[keyword]
        self.parent.downloadHelper(databaseInfo)
        return ("", "")

    # return invalid command
    def invalidCommand(self, source="main"):
        return (source, "INVALID_COMMAND_ENTERED")

    # sort out keywords from a single line command
    def splitCommand(self, command):
        commandList = re.split('[ ]*?:::[ ]*?', command, 1)
        return commandList

    # shared functions about config
    def getViewConfig(self, view):
        views = {
            "main": (self.setMainVerse, config.mainText, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV), config.mainB, config.mainC, config.mainV),
            "study": (self.setStudyVerse, config.studyText, self.bcvToVerseReference(config.studyB, config.studyC, config.studyV), config.studyB, config.studyC, config.studyV),
            "instant": (self.setMainVerse, config.mainText, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV), config.mainB, config.mainC, config.mainV),
        }
        return views[view]

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

    # shared functions about bible text
    def getConfirmedTexts(self, texts):
        biblesSqlite = BiblesSqlite()
        bibleList = biblesSqlite.getBibleList()
        del biblesSqlite
        confirmedTexts = [text for text in texts.split("_") if text in bibleList or text in self.getMarvelBibles()]
        return confirmedTexts

    def extractAllVerses(self, text, tagged=False):
        return BibleVerseParser(config.parserStandarisation).extractAllReferences(text, tagged)

    def bcvToVerseReference(self, b, c, v):
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)

    # default function if no special keyword is specified
    def textBibleVerseParser(self, command, text, view):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            formattedBiblesFolder = os.path.join("marvelData", "bibles")
            formattedBibles = [f[:-6] for f in os.listdir(formattedBiblesFolder) if os.path.isfile(os.path.join(formattedBiblesFolder, f)) and f.endswith(".bible") and not re.search("^[\._]", f)]
            if text in ("MOB", "MIB", "MTB", "MPB", "MAB", "LXX1i", "LXX2i") and not config.readFormattedBibles:
                config.readFormattedBibles = True
                self.parent.enableParagraphButtonAction(False)
            elif (text in ("OHGBi", "OHGB", "LXX1", "LXX2") or not text in formattedBibles) and config.readFormattedBibles:
                config.readFormattedBibles = False
                self.parent.enableParagraphButtonAction(False)
            if len(verseList) == 1:
                # i.e. only one verse reference is specified
                bcvTuple = verseList[0]
                chapters = self.getChaptersMenu(bcvTuple[0], bcvTuple[1], text)
                content = "{0}<hr>{1}<hr>{0}".format(chapters, self.textFormattedBible(bcvTuple, text))
            else:
                # i.e. when more than one verse reference is found
                content = self.textPlainBible(verseList, text)
                bcvTuple = verseList[-1]
            updateViewConfig, *_ = self.getViewConfig(view)
            updateViewConfig(text, bcvTuple)
            return (view, content)

    def getChaptersMenu(self, b, c, text):
        biblesSqlite = BiblesSqlite()
        chapteruMenu = biblesSqlite.getChaptersMenu(b, c, text)
        del biblesSqlite
        return chapteruMenu

    # access to formatted chapter or plain verses of a bible text, called by textBibleVerseParser
    def textPlainBible(self, verseList, text):
        biblesSqlite = BiblesSqlite()
        verses = biblesSqlite.readMultipleVerses(text, verseList)
        del biblesSqlite
        return verses

    def textFormattedBible(self, verse, text):
        formattedBiblesFolder = os.path.join("marvelData", "bibles")
        formattedBibles = [f[:-6] for f in os.listdir(formattedBiblesFolder) if os.path.isfile(os.path.join(formattedBiblesFolder, f)) and f.endswith(".bible") and not re.search("^[\._]", f)]
        #marvelBibles = ("MOB", "MIB", "MAB", "MPB", "MTB", "LXX1", "LXX1i", "LXX2", "LXX2i")
        marvelBibles = list(self.getMarvelBibles().keys())
        if text in formattedBibles and config.readFormattedBibles:
            bibleSqlite = Bible(text)
            chapter = bibleSqlite.readFormattedChapter(verse)
            del bibleSqlite
        else:
            # use plain bibles database when corresponding formatted version is not available
            biblesSqlite = BiblesSqlite()
            chapter = biblesSqlite.readPlainChapter(text, verse)
            del biblesSqlite
        return chapter

    # functions about bible

    # BIBLE:::
    def textBible(self, command, source):
        if command.count(":::") == 0:
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            command = "{0}:::{1}".format(viewText, command)
        texts, references = self.splitCommand(command)
        texts = self.getConfirmedTexts(texts)
        marvelBibles = self.getMarvelBibles()
        if not texts:
            return self.invalidCommand()
        else:
            text = texts[0]
            if text in marvelBibles:
                fileItems = marvelBibles[text][0]
                if os.path.isfile(os.path.join(*fileItems)):
                    return self.textBibleVerseParser(references, text, source)
                else:
                    databaseInfo = marvelBibles[text]
                    self.parent.downloadHelper(databaseInfo)
                    return ("", "")
            else:
                return self.textBibleVerseParser(references, text, source)

    # TEXT:::
    def textText(self, command, source):
        texts = self.getConfirmedTexts(command)
        if not texts:
            return self.invalidCommand()
        else:
            marvelBibles = self.getMarvelBibles()
            text = texts[0]
            if text in marvelBibles:
                fileItems = marvelBibles[text][0]
                if os.path.isfile(os.path.join(*fileItems)):
                    updateViewConfig, viewText, viewReference, *_ = self.getViewConfig(source)
                    return self.textBibleVerseParser(viewReference, texts[0], source)
                else:
                    databaseInfo = marvelBibles[text]
                    self.parent.downloadHelper(databaseInfo)
                    return ("", "")
            else:
                updateViewConfig, viewText, viewReference, *_ = self.getViewConfig(source)
                return self.textBibleVerseParser(viewReference, texts[0], source)

    # MAIN:::
    def textMain(self, command, source):
        return self.textAnotherView(command, source, "main")

    # STUDY:::
    def textStudy(self, command, source):
        return self.textAnotherView(command, source, "study")

    # called by MAIN::: & STUDY:::
    def textAnotherView(self, command, source, target):
        if command.count(":::") == 0:
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            command = "{0}:::{1}".format(viewText, command)
        texts, references = self.splitCommand(command)
        texts = self.getConfirmedTexts(texts)
        if not texts:
            return self.invalidCommand()
        else:
            marvelBibles = self.getMarvelBibles()
            text = texts[0]
            if text in marvelBibles:
                fileItems = marvelBibles[text][0]
                if os.path.isfile(os.path.join(*fileItems)):
                    return self.textBibleVerseParser(references, texts[0], target)
                else:
                    databaseInfo = marvelBibles[text]
                    self.parent.downloadHelper(databaseInfo)
                    return ("", "")
            else:
                return self.textBibleVerseParser(references, texts[0], target)

    # COMPARE:::
    def textCompare(self, command, source):
        if command.count(":::") == 0:
            confirmedTexts = ["ALL"]
            verseList = self.extractAllVerses(command)
        else:
            texts, references = self.splitCommand(command)
            confirmedTexts = self.getConfirmedTexts(texts)
            verseList = self.extractAllVerses(references)
        if not confirmedTexts or not verseList:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            verses = biblesSqlite.compareVerse(verseList, confirmedTexts)
            del biblesSqlite
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            if confirmedTexts == ["ALL"]:
                updateViewConfig(viewText, verseList[-1])
            else:
                updateViewConfig(confirmedTexts[-1], verseList[-1])
            return (source, verses)

    # PARALLEL:::
    def textParallel(self, command, source):
        updateViewConfig, viewText, *_ = self.getViewConfig(source)
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(viewText, command)
        texts, references = self.splitCommand(command)
        confirmedTexts = self.getConfirmedTexts(texts)
        if not confirmedTexts:
            return self.invalidCommand()
        else:
            marvelBibles = self.getMarvelBibles()
            missingMarvelTexts = [text for text in confirmedTexts if text in marvelBibles and not os.path.isfile(os.path.join(*marvelBibles[text][0]))]
            if missingMarvelTexts:
                databaseInfo = marvelBibles[missingMarvelTexts[0]]
                self.parent.downloadHelper(databaseInfo)
                return ("", "")
            else:
                tableList = [("<th><ref onclick='document.title=\"TEXT:::{0}\"'>{0}</ref></th>".format(text), "<td style='vertical-align: text-top;'>{0}</td>".format(self.textBibleVerseParser(references, text, source)[1])) for text in confirmedTexts]
                versions, verses = zip(*tableList)
                return (source, "<table style='width:100%; table-layout:fixed;'><tr>{0}</tr><tr>{1}</tr></table>".format("".join(versions), "".join(verses)))

    # _biblenote:::
    def textBiblenote(self, command, source):
        texts = {
            "main": config.mainText,
            "study": config.studyText,
        }
        if source in texts:
            bible = Bible(texts[source])
            note = bible.readBiblenote(command)
            del bible
            return ("study", note)
        else:
            return ("", "")

    # _openchapternote:::
    def openChapterNote(self, command, source):
        b, c = command.split(".")
        b, c = int(b), int(c)
        self.parent.openChapterNote(b, c)
        return ("", "")

    # _openversenote:::
    def openVerseNote(self, command, source):
        b, c, v = command.split(".")
        b, c, v = int(b), int(c), int(v)
        self.parent.openVerseNote(b, c, v)
        return ("", "")

    # _editchapternote:::
    def editChapterNote(self, command, source):
        if self.parent.noteSaved:
            self.parent.openNoteEditor("chapter")
        elif self.parent.warningNotSaved():
            self.parent.openNoteEditor("chapter")
        return ("", "")

    # _editversenote:::
    def editVerseNote(self, command, source):
        if self.parent.noteSaved:
            self.parent.openNoteEditor("verse")
        elif self.parent.warningNotSaved():
            self.parent.openNoteEditor("verse")
        else:
            self.parent.noteEditor.raise_()
        return ("", "")

    # _openfile:::
    def textOpenFile(self, command, source):
        fileName = config.history["external"][int(command)]
        if fileName:
            self.parent.openTextFile(fileName)
        return ("", "")

    # _editfile:::
    def textEditFile(self, command, source):
        if command:
            self.parent.editExternalFileHistoryRecord(int(command))
        return ("", "")

    # _website:::
    def textWebsite(self, command, source):
        if command:
            webbrowser.open(command)
            return ("", "")
        else:
            return self.invalidCommand()

    # _uba:::
    def textUba(self, command, source):
        if command:
            pathItems = command[8:].split("/")
            file = os.path.join(*pathItems)
            config.history["external"].append(file)
            self.parent.openExternalFileHistoryRecord(-1)
            return ("", "")
        else:
            return self.invalidCommand()

    # _info:::
    def textInfo(self, command, source):
        if config.instantInformationEnabled == 1:
            return ("instant", command)
        else:
            return ("", "")

    # _instantverse:::
    def instantVerse(self, command, source):
        if config.instantInformationEnabled == 1:
            commandList = self.splitCommand(command)
            morphologySqlite = MorphologySqlite()
            b, c, v = [int(i) for i in commandList[1].split(".")]
            info = morphologySqlite.instantVerse("interlinear", b, c, v)
            del morphologySqlite
            return ("instant", info)
        else:
            return ("", "")

    # _imv:::
    def instantMainVerse(self, command, source):
        if config.instantInformationEnabled == 1:
            b, c, v = [int(i) for i in command.split(".")]
            biblesSqlite = BiblesSqlite()
            b, c, v, verseText = biblesSqlite.readTextVerse(config.mainText, b, c, v)
            del biblesSqlite
            info = "<hl>{0}</hl> {1}".format(self.bcvToVerseReference(b, c, v), verseText)
            if config.mainText in config.rtlTexts and b < 40:
                info = "<div style='direction: rtl;'>{0}</div>".format(info)
            return ("instant", info)
        else:
            return ("", "")

    # _instantword:::
    def instantWord(self, command, source):
        if config.instantInformationEnabled == 1:
            commandList = self.splitCommand(command)
            morphologySqlite = MorphologySqlite()
            wordID = commandList[1]
            wordID = re.sub('^[h0]+?([^h0])', r'\1', wordID, flags=re.M)
            info = morphologySqlite.instantWord(int(commandList[0]), int(wordID))
            del morphologySqlite
            return ("instant", info)
        else:
            return ("", "")

    # _bibleinfo:::
    def textBibleInfo(self, command, source):
        if self.getConfirmedTexts(command):
            biblesSqlite = BiblesSqlite()
            info = biblesSqlite.bibleInfo(command)
            del biblesSqlite
            if info:
                return ("instant", info)
            else:
                return ("", "")
        else:
            return self.invalidCommand()

    # _commentaryinfo:::
    def textCommentaryInfo(self, command, source):
        commentaryName = {
            "Barnes": "Notes on the Old and New Testaments (Barnes) [26 vol.]",
            "Benson": "Commentary on the Old and New Testaments (Benson) [5 vol.]",
            "BI": "Biblical Illustrator (Exell) [58 vol.]",
            "Brooks": "Complete Summary of the Bible (Brooks) [2 vol.]",
            "Calvin": "John Calvin's Commentaries (Calvin) [22 vol.]",
            "Clarke": "Commentary on the Bible (Clarke) [6 vol.]",
            "CBSC": "Cambridge Bible for Schools and Colleges (Cambridge) [57 vol.]",
            "CECNT": "Critical And Exegetical Commentary on the NT (Meyer) [20 vol.]",
            "CGrk": "Cambridge Greek Testament for Schools and Colleges (Cambridge) [21 vol.]",
            "CHP": "Church Pulpit Commentary (Nisbet) [12 vol.]",
            "CPBST": "College Press Bible Study Textbook Series (College) [59 vol.]",
            "EBC": "Expositor's Bible Commentary (Nicoll) [49 vol.]",
            "ECER": "Commentary for English Readers (Ellicott) [8 vol.]",
            "EGNT": "Expositor's Greek New Testament (Nicoll) [5 vol.]",
            "GCT": "Greek Testament Commentary (Alford) [4 vol.]",
            "Gill": "Exposition of the Entire Bible (Gill) [9 vol.]",
            "Henry": "Exposition of the Old and New Testaments (Henry) [6 vol.]",
            "HH": "Horæ Homileticæ (Simeon) [21 vol.]",
            "ICCNT": "International Critical Commentary, NT (1896-1929) [16 vol.]",
            "JFB": "Jamieson, Fausset, and Brown Commentary (JFB) [6 vol.]",
            "KD": "Commentary on the Old Testament (Keil & Delitzsch) [10 vol.]",
            "Lange": "Commentary on the Holy Scriptures: Critical, Doctrinal, and Homiletical (Lange) [25 vol.]",
            "MacL": "Expositions of Holy Scripture (MacLaren) [32 vol.]",
            "PHC": "Preacher's Complete Homiletical Commentary (Exell) [37 vol.]",
            "Pulpit": "Pulpit Commentary (Spence) [23 vol.]",
            "Rob": "Word Pictures in the New Testament (Robertson) [6 vol.]",
            "Spur": "Spurgeon's Expositions on the Bible (Spurgeon) [3 vol.]",
            "Vincent": "Word Studies in the New Testament (Vincent) [4 vol.]",
            "Wesley": "John Wesley's Notes on the Whole Bible (Wesley) [3 vol.]",
            "Whedon": "Commentary on the Old and New Testaments (Whedon) [14 vol.]",
        }
        commentaryFile = os.path.join("marvelData", "commentaries", "c{0}.commentary".format(command))
        if os.path.isfile(commentaryFile):
            if command in commentaryName:
                return ("instant", commentaryName[command])
            else:
                commentarySqlite = Commentary(command)
                info = commentarySqlite.commentaryInfo()
                del commentarySqlite
                if info:
                    return ("instant", info)
                else:
                    return ("", "")
        else:
            return self.invalidCommand()

    # _menu:::
    def textMenu(self, command, source):
        biblesSqlite = BiblesSqlite()
        menu = biblesSqlite.getMenu(command, source)
        del biblesSqlite
        return (source, menu)

    # _commentary:::
    def textCommentaryMenu(self, command, source):
        text, *_ = command.split(".")
        commentary = Commentary(text)
        commentaryMenu = commentary.getMenu(command)
        del commentary
        return ("study", commentaryMenu)

    # _book:::
    def textBookMenu(self, command, source):
        bookData = BookData()
        bookMenu = bookData.getMenu(command)
        del bookData
        self.parent.bookButton.setText(config.book)
        return ("study", bookMenu)

    # _history:::
    def textHistory(self, command, source):
        if command in ("main", "study"):
            return (command, self.parent.getHistory(command))
        else:
            return self.invalidCommand()

    # _historyrecord:::
    def textHistoryRecord(self, command, source):
        if source in ("main", "study"):
            self.parent.openHistoryRecord(source, int(command))
            return ("", "")
        else:
            return self.invalidCommand()

    # _command:::
    def textCommand(self, command, source):
        return ("command", command)

    # _image:::
    def textImage(self, command, source):
        module, entry = self.splitCommand(command)
        imageSqlite = ImageSqlite()
        imageSqlite.exportImage(module, entry)
        del imageSqlite
        content = "<img src='images/{0}/{0}_{1}'>".format(module, entry)
        return ("popover.{0}".format(source), content)

    # COMMENTARY:::
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

    # COMMENTARY2:::
    def textCommentary2(self, command, source):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.commentaryText, command)
        commandList = self.splitCommand(command)
        reference = commandList[1]
        if re.search("^[0-9]+?\.[0-9]+?\.[0-9]+?$", reference):
            verseList = [tuple([int(i) for i in reference.split(".")])]
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
        else:
            return self.invalidCommand()

    # SEARCHTOOL:::
    def textSearchTool(self, command, source):
        module, entry = self.splitCommand(command)
        indexes = IndexesSqlite()
        toolList = [("", "[search other resources]"), ("EXLBP", "Exhaustive Library of Bible Characters"), ("EXLBL", "Exhaustive Library of Bible Locations")] + indexes.topicList + indexes.dictionaryList + indexes.encyclopediaList
        if module in dict(toolList[1:]).keys() or module in ("mRMAC", "mETCBC", "mLXX"):
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
            return ("study", "<h2>Search <span style='color: brown;'>{0}</span> for <span style='color: brown;'>{1}</span></h2><p>{4}</p><p><b>Exact match:</b><br><br>{2}</p><p><b>Partial match:</b><br><br>{3}".format(module, entry, exactMatch, similarMatch, selectList))
        else:
            del indexes
            return self.invalidCommand()

    # SEARCH:::
    def textCountSearch(self, command, source):
        return self.textCount(command, False)

    # ISEARCH:::
    def textCountISearch(self, command, source):
        return self.textCount(command, True)

    # called by SEARCH::: & ISEARCH:::
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

    # SHOWSEARCH:::
    def textSearchBasic(self, command, source):
        return self.textSearch(command, source, "BASIC")

    # SHOWISEARCH:::
    def textISearchBasic(self, command, source):
        return self.textSearch(command, source, "BASIC", True)

    # ADVANCEDSEARCH:::
    def textSearchAdvanced(self, command, source):
        return self.textSearch(command, source, "ADVANCED")

    # ADVANCEDISEARCH:::
    def textISearchAdvanced(self, command, source):
        return self.textSearch(command, source, "ADVANCED", True)

    # ANDSEARCH:::
    def textAndSearch(self, command, source):
        commandList = command.split(":::")
        commandList[-1] = " AND ".join(['Scripture LIKE "%{0}%"'.format(m.strip()) for m in commandList[-1].split("|")])
        command = ":::".join(commandList)
        return self.textSearch(command, source, "ADVANCED")

    # ANDISEARCH:::
    def textAndISearch(self, command, source):
        commandList = command.split(":::")
        commandList[-1] = " AND ".join(['Scripture LIKE "%{0}%"'.format(m.strip()) for m in commandList[-1].split("|")])
        command = ":::".join(commandList)
        return self.textSearch(command, source, "ADVANCED", True)

    # ORSEARCH:::
    def textOrSearch(self, command, source):
        commandList = command.split(":::")
        commandList[-1] = " OR ".join(['Scripture LIKE "%{0}%"'.format(m.strip()) for m in commandList[-1].split("|")])
        command = ":::".join(commandList)
        return self.textSearch(command, source, "ADVANCED")

    # ORISEARCH:::
    def textOrISearch(self, command, source):
        commandList = command.split(":::")
        commandList[-1] = " OR ".join(['Scripture LIKE "%{0}%"'.format(m.strip()) for m in commandList[-1].split("|")])
        command = ":::".join(commandList)
        return self.textSearch(command, source, "ADVANCED", True)

    # called by SHOWSEARCH::: & SHOWISEARCH::: & ADVANCEDSEARCH::: & ADVANCEDISEARCH:::
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

    # WORD:::
    def textWordData(self, command, source):
        book, wordId = self.splitCommand(command)
        bNo = int(book)
        morphologySqlite = MorphologySqlite()
        bcvTuple, content = morphologySqlite.wordData(bNo, int(wordId))
        del morphologySqlite

        # extra data for Greek words
        if bNo >= 40:
            wordData = WordData()
            content += re.sub('^.*?<br><br><b><i>TBESG', '<b><i>TBESG', wordData.getContent("NT", wordId))

        self.setStudyVerse(config.studyText, bcvTuple)
        return ("study", content)

    # LEXICON:::
    def textLexicon(self, command, source):
        if command.count(":::") == 0:
            defaultLexicon = {
                "H": "TBESH",
                "G": "TBESG",
                "E": "ConcordanceMorphology",
                "L": "LXX",
                "g": "MCGED",
                "l": "LN",
            }
            command = "{0}:::{1}".format(defaultLexicon[command[0]], command)
        module, entries = self.splitCommand(command)
        lexicon = Lexicon(module)
        content = "<hr>".join([lexicon.getContent(entry) for entry in entries.split("_")])
        del lexicon
        if not content or content == "INVALID_COMMAND_ENTERED":
            return self.invalidCommand()
        else:
            return ("study", content)

    # _lxxword:::
    def textLxxWord(self, command, source):
        if re.search("^(LXX1|LXX2):::", command):
            lxx, word = self.splitCommand(command)
            bibleSqlite = Bible(lxx)
            data = bibleSqlite.readLXXnote(word)
            del bibleSqlite
            if data:
                return ("study", data)
            else:
                return self.invalidCommand()
        else:
            return self.invalidCommand()

    # LEMMA:::
    def textLemma(self, command, source):
        return self.textMorphologyFeature(command, source, "LEMMA")

    # MORPHOLOGYCODE:::
    def textMorphologyCode(self, command, source):
        return self.textMorphologyFeature(command, source, "MORPHOLOGYCODE")

    # MORPHOLOGY:::
    def textMorphology(self, command, source):
        return self.textMorphologyFeature(command, source, "ADVANCED")

    # SEARCHMORPHOLOGY:::
    def textSearchMorphology(self, command, source):
        #﻿LexicalEntry LIKE '%E70746,%' AND
        if not command.count(":::") == 1:
            return self.invalidCommand("study")
        else:
            lexicalEntry, morphology = command.split(":::")
            lexicalEntry = "LexicalEntry LIKE '%{0},%'".format(lexicalEntry)
            morphology = " OR ".join(['Morphology LIKE "%{0}%"'.format(m.strip()) for m in morphology.split("|")])
            command = "{0} AND ({1})".format(lexicalEntry, morphology)
            return self.textMorphologyFeature(command, source, "ADVANCED")

    # called by LEMMA::: & MORPHOLOGYCODE::: & MORPHOLOGY::: & # SEARCHMORPHOLOGY:::
    def textMorphologyFeature(self, command, source, mode):
        morphologySqlite = MorphologySqlite()
        searchResult = morphologySqlite.searchMorphology(mode, command)
        del morphologySqlite
        return ("study", searchResult)

    # EXLB:::
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

    # CLAUSE:::
    def textClause(self, command, source):
        if command.count(":::") == 1:
            bcv, entry = self.splitCommand(command)
            b, c, v = [int(i) for i in bcv.split(".")]
            clauseData = ClauseData()
            if b < 40:
                testament = "OT"
            else:
                testament = "NT"
            content = "<h2>Clause id: c{0}</h2>{1}".format(entry, clauseData.getContent(testament, entry))
            del clauseData
            self.setStudyVerse(config.studyText, (b, c, v))
            return ("study", content)
        else:
            return self.invalidCommand("study")

    # DICTIONARY:::
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

    # ENCYCLOPEDIA:::
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

    # BOOK:::
    def textBook(self, command, source):
        commandList = self.splitCommand(command)
        if commandList and len(commandList) == 2:
            module, entry = commandList
            bookData = BookData()
            content = bookData.getContent(module, entry)
            del bookData
            if not content:
                return self.invalidCommand("study")
            else:
                self.parent.bookButton.setText(config.book)
                return ("study", content)
        else:
            return self.invalidCommand("study")

    # SEARCHBOOK:::
    def textSearchBook(self, command, source):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.book, command)
        module, searchString = self.splitCommand(command)
        if not searchString:
            return self.invalidCommand("study")
        else:
            config.bookSearchString = searchString
            bookData = BookData()
            content = bookData.getSearchedMenu(module, searchString)
            del bookData
            if not content:
                return self.invalidCommand("study")
            else:
                self.parent.bookButton.setText(config.book)
                return ("study", content)

    # SEARCHCHAPTERNOTE:::
    def textSearchChapterNote(self, command, source):
        if not command:
            return self.invalidCommand("study")
        else:
            config.noteSearchString = command
            noteSqlite = NoteSqlite()
            chapters = noteSqlite.getSearchedChapterList(command)
            del noteSqlite
            return ("study", "<p>\"<b style='color: brown;'>{0}</b>\" is found in <b style='color: brown;'>{1}</b> note(s) on chapter(s)</p><p>{2}</p>".format(command, len(chapters), "; ".join(chapters)))

    # SEARCHVERSENOTE:::
    def textSearchVerseNote(self, command, source):
        if not command:
            return self.invalidCommand("study")
        else:
            config.noteSearchString = command
            noteSqlite = NoteSqlite()
            verses = noteSqlite.getSearchedVerseList(command)
            del noteSqlite
            return ("study", "<p>\"<b style='color: brown;'>{0}</b>\" is found in <b style='color: brown;'>{1}</b> note(s) on verse(s)</p><p>{2}</p>".format(command, len(verses), "; ".join(verses)))

    # CROSSREFERENCE:::
    def textCrossReference(self, command, source):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            crossReferenceSqlite = CrossReferenceSqlite()
            content = ""
            for verse in verseList:
                b, c, v = verse
                content += "<h2>Cross-reference: <ref onclick='document.title=\"{0}\"'>{0}</ref></h2>".format(biblesSqlite.bcvToVerseReference(b, c, v))
                crossReferenceList = self.extractAllVerses(crossReferenceSqlite.scrollMapper(verse), True)
                if not crossReferenceList:
                    content += "[No cross-reference is found for this verse!]"
                else:
                    content += biblesSqlite.readMultipleVerses(config.mainText, crossReferenceList)
                content += "<hr>"
            del crossReferenceSqlite
            del biblesSqlite
            self.setStudyVerse(config.studyText, verseList[-1])
            return ("study", content)

    # TSKE:::
    def tske(self, command, source):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            crossReferenceSqlite = CrossReferenceSqlite()
            content = ""
            for verse in verseList:
                b, c, v = verse
                content += "<h2>TSKE: <ref onclick='document.title=\"{0}\"'>{0}</ref></h2>".format(biblesSqlite.bcvToVerseReference(b, c, v))
                tskeContent = crossReferenceSqlite.tske(verse)
                content += "<div style='margin: 10px; padding: 0px 10px; border: 1px solid gray; border-radius: 5px;'>{0}</div>".format(tskeContent)
                crossReferenceList = self.extractAllVerses(tskeContent, False)
                if not crossReferenceList:
                    content += "[No cross-reference is found for this verse!]"
                else:
                    content += biblesSqlite.readMultipleVerses(config.mainText, crossReferenceList)
                content += "<hr>"
            del crossReferenceSqlite
            del biblesSqlite
            self.setStudyVerse(config.studyText, verseList[-1])
            return ("study", content)

    # COMBO:::
    def textCombo(self, command, source):
        return ("study", "".join([self.textVerseData(command, source, feature) for feature in ("translation", "discourse", "words")]))

    # TRANSLATION:::
    def textTranslation(self, command, source):
        return ("study", self.textVerseData(command, source, "translation"))

    # DISCOURSE:::
    def textDiscourse(self, command, source):
        return ("study", self.textVerseData(command, source, "discourse"))

    # WORDS:::
    def textWords(self, command, source):
        return ("study", self.textVerseData(command, source, "words"))

    # called by TRANSLATION::: & WORDS::: & DISCOURSE::: & COMBO:::
    def textVerseData(self, command, source, filename):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            verseData = VerseData(filename)
            feature = "{0}{1}".format(filename[0].upper(), filename[1:])
            content = "<hr>".join(["<h2>{0}: <ref onclick='document.title=\"{1}\"'>{1}</ref></h2>{2}".format(feature, biblesSqlite.bcvToVerseReference(b, c, v), verseData.getContent((b, c, v))) for b, c, v in verseList])
            del verseData
            del biblesSqlite
            self.setStudyVerse(config.studyText, verseList[-1])
            return content

    # INDEX:::
    def textIndex(self, command, source):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            parser = BibleVerseParser(config.parserStandarisation)
            indexesSqlite = IndexesSqlite()
            for verse in verseList:
                b, c, v = verse
                content = "<h2>Indexes: <ref onclick='document.title=\"{0}\"'>{0}</ref></h2>{1}<hr>".format(parser.bcvToVerseReference(b, c, v), indexesSqlite.getAllIndexes(verse))
            del indexesSqlite
            del parser
            self.setStudyVerse(config.studyText, verseList[-1])
            return ("study", content)

    # Check if a third party dictionary exists:
    def isThridPartyDictionary(self, module):
        bibleBentoPlusLexicon = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(module, ".dic.bbp"))
        eSwordLexicon = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(module, ".lexi"))
        eSwordDictionary = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(module, ".dcti"))
        mySwordDictionary = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(module, ".dct.mybible"))
        myBibleDictionary = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(module, ".dictionary.SQLite3"))

        if os.path.isfile(bibleBentoPlusLexicon):
            return (module, ".dic.bbp")
        elif os.path.isfile(eSwordLexicon):
            return (module, ".lexi")
        elif os.path.isfile(eSwordDictionary):
            return (module, ".dcti")
        elif os.path.isfile(mySwordDictionary):
            return (module, ".dct.mybible")
        elif os.path.isfile(myBibleDictionary):
            return (module, ".dictionary.SQLite3")
        else:
            return None

    # SEARCHTHIRDDICTIONARY:::
    def thirdDictionarySearch(self, command, source):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.thirdDictionary, command)
        module, entry = self.splitCommand(command)
        module = self.isThridPartyDictionary(module)
        if not entry or not module:
            return self.invalidCommand("study")
        else:
            thirdPartyDictionary = ThirdPartyDictionary(module)
            content = thirdPartyDictionary.search(entry)
            del thirdPartyDictionary
            return ("study", content)

    # THIRDDICTIONARY:::
    def thirdDictionaryOpen(self, command, source):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.thirdDictionary, command)
        module, entry = self.splitCommand(command)
        module = self.isThridPartyDictionary(module)
        if not entry or not module:
            return self.invalidCommand("study")
        else:
            thirdPartyDictionary = ThirdPartyDictionary(module)
            content = thirdPartyDictionary.getData(entry)
            del thirdPartyDictionary
            return ("study", content)
