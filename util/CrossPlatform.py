import config, os, glob, re
from db.BiblesSqlite import BiblesSqlite, Bible
from db.ToolsSqlite import BookData, IndexesSqlite, Commentary
from db.ToolsSqlite import LexiconData
from util.BibleBooks import BibleBooks
from util.CatalogUtil import CatalogUtil
from util.ThirdParty import ThirdPartyDictionary

class CrossPlatform:

    def setupResourceLists(self):
        # bible versions
        self.textList = BiblesSqlite().getBibleList()
        if not config.enableHttpServer and self.textList and not config.mainText in self.textList:
            config.mainText = "KJV" if "KJV" in self.textList else self.textList[0]
        self.textFullNameList = [Bible(text).bibleInfo() for text in self.textList]
        bibleOHGBiPath = os.path.join(config.marvelData, "bibles", "OHGBi.bible")
        morphologyDatabase = os.path.join(config.marvelData, "morphology.sqlite")
        self.strongBibles = ["OHGBi"] if os.path.isfile(bibleOHGBiPath) and os.path.isfile(morphologyDatabase) else []
        self.strongBibles += [text for text in self.textList if Bible(text).bibleStrong()]
        #if self.versionCombo is not None and config.menuLayout in ("focus", "Starter"):
        #    for index, fullName in enumerate(self.textFullNameList):
        #        self.versionCombo.setItemData(index, fullName, Qt.ToolTipRole)
        # commentaries
        self.commentaryList = Commentary().getCommentaryList()
        if self.commentaryList and not config.commentaryText in self.commentaryList:
            config.commentaryText = "CBSC" if "CBSC" in self.commentaryList else self.commentaryList[0]
        #self.commentaryFullNameList = [Commentary(module).commentaryInfo() for module in self.commentaryList]
        self.commentaryFullNameList = []
        for module in self.commentaryList:
            info = Commentary(module).commentaryInfo()
            if info == "https://Marvel.Bible Commentary" and module in Commentary.marvelCommentaries:
                info = Commentary.marvelCommentaries[module]
            self.commentaryFullNameList.append(info)
        # reference book
        # menu10_dialog
        bookData = BookData()
        self.referenceBookList = [book for book, *_ in bookData.getBookList()]
        # open database
        indexes = IndexesSqlite()
        # topic
        # menu5_topics
        topicDictAbb2Name = {abb: name for abb, name in indexes.topicList}
        self.topicListAbb = list(topicDictAbb2Name.keys())
        topicDict = {name: abb for abb, name in indexes.topicList}
        self.topicList = list(topicDict.keys())
        # lexicon
        # context1_originalLexicon
        self.lexiconList = LexiconData().lexiconList
        # dictionary
        # context1_dict
        dictionaryDictAbb2Name = {abb: name for abb, name in indexes.dictionaryList}
        self.dictionaryListAbb = list(dictionaryDictAbb2Name.keys())
        dictionaryDict = {name: abb for abb, name in indexes.dictionaryList}
        self.dictionaryList = list(dictionaryDict.keys())
        # encyclopedia
        # context1_encyclopedia
        encyclopediaDictAbb2Name = {abb: name for abb, name in indexes.encyclopediaList}
        self.encyclopediaListAbb = list(encyclopediaDictAbb2Name.keys())
        encyclopediaDict = {name: abb for abb, name in indexes.encyclopediaList}
        self.encyclopediaList = list(encyclopediaDict.keys())
        # 3rd-party dictionary
        # menu5_3rdDict
        self.thirdPartyDictionaryList = ThirdPartyDictionary(self.isThridPartyDictionary(config.thirdDictionary)).moduleList
        # pdf list
        # self.pdfList = sorted([os.path.basename(file) for file in glob.glob(r"{0}/pdf/*.pdf".format(config.marvelData))])
        self.pdfList = CatalogUtil.getPDFs()
        # epub list
        self.epubList = sorted([os.path.basename(file) for file in glob.glob(r"{0}/epub/*.epub".format(config.marvelData))])
        # docx list
        self.docxList = sorted([os.path.basename(file) for file in glob.glob(r"{0}/docx/*.docx".format(config.marvelData))])

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

    # History record management

    def addHistoryRecord(self, view, textCommand, tab="0"):
        if not (config.enableHttpServer and config.webHomePage == "{0}.html".format(config.webPrivateHomePage)):
            if view == "http":
                view = "main"
            if not textCommand.startswith("_") and not re.search("^download:::|^qrcode:::", textCommand.lower()):
    
                if view in ("main", "study"):
                    compareParallel = (textCommand.lower().startswith("compare:::") or textCommand.lower().startswith("parallel:::") or textCommand.lower().startswith("comparesidebyside:::"))
                    if config.enforceCompareParallel and not config.tempRecord:
                        if not ":::" in textCommand:
                            view = "study"
                            textCommand = "STUDY:::{0}".format(textCommand)
                        elif textCommand.lower().startswith("bible:::"):
                            view = "study"
                            textCommand = re.sub("^.*?:::", "STUDY:::", textCommand)
                    if config.tempRecord:
                        self.runAddHistoryRecord("main", config.tempRecord, tab)
                        config.tempRecord = ""
                    elif not (view == "main" and config.enforceCompareParallel) or compareParallel:
                        self.runAddHistoryRecord(view, textCommand, tab)
                else:
                    self.runAddHistoryRecord(view, textCommand, tab)

    def runAddHistoryRecord(self, view, textCommand, tab):
        if view in ("main", "study"):
            command = textCommand
            if command.count(":::") == 0:
                if view == "main":
                    command = "BIBLE:::{0}:::{1}".format(config.mainText, command)
                elif view == "study":
                    command = "STUDY:::{0}:::{1}".format(config.mainText, command)
            elif command.count(":::") == 1:
                verse = command.find(":::") + 3
                if view == "main":
                    if command.lower().startswith("bible"):
                        command = "BIBLE:::{0}:::{1}".format(config.mainText, command[verse:])
                    elif command.lower().startswith("main"):
                        command = "MAIN:::{0}:::{1}".format(config.mainText, command[verse:])
                elif view == "study" and command.lower().startswith("study"):
                    command = "STUDY:::{0}:::{1}".format(config.mainText, command[verse:])
            config.tabHistory[view][tab] = command
        if view and textCommand and view in config.history:
            viewhistory = config.history[view]
            if not (viewhistory[-1] == textCommand):
                viewhistory.append(textCommand)
                # set maximum number of history records for each view here
                maximumHistoryRecord = config.maximumHistoryRecord
                if len(viewhistory) > maximumHistoryRecord:
                    viewhistory = viewhistory[-maximumHistoryRecord:]
                config.history[view] = viewhistory
                config.currentRecord[view] = len(viewhistory) - 1

    def getHistory(self, view):
        historyRecords = [(counter, record) for counter, record in enumerate(config.history[view])]
        if view == "external":
            html = "<br>".join([
                                   "<button class='ubaButton' onclick='openExternalRecord({0})'>{1}</button> [<ref onclick='editExternalRecord({0})'>edit</ref>]".format(
                                       counter, record) for counter, record in reversed(historyRecords)])
        else:
            html = "<br>".join(
                ["<button class='ubaButton' onclick='openHistoryRecord({0})'>{1}</button>".format(counter, record) for
                 counter, record in reversed(historyRecords)])
        return html

    # Plugins

    def runPlugin(self, fileName):
        script = os.path.join(os.getcwd(), "plugins", "menu", "{0}.py".format(fileName))
        self.execPythonFile(script)

    def execPythonFile(self, script):
        if config.developer:
            with open(script) as f:
                code = compile(f.read(), script, 'exec')
                exec(code, globals())
        else:
            try:
                with open(script) as f:
                    code = compile(f.read(), script, 'exec')
                    exec(code, globals())
            except:
                print("Failed to run '{0}'!".format(os.path.basename(script)))
