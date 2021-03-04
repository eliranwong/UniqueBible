import config
from functools import partial
from qtpy.QtCore import Qt
#from qtpy.QtGui import QDesktopServices
from qtpy.QtWidgets import QAction, QApplication
from qtpy.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite
from Translator import Translator
from gui.WebEngineViewPopover import WebEngineViewPopover

class WebEngineView(QWebEngineView):
    
    def __init__(self, parent, name):
        super().__init__()
        self.parent = parent
        self.name = name
        self.setPage(WebEnginePage(self))
       
        # add context menu (triggered by right-clicking)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.selectionChanged.connect(self.updateContextMenu)
        self.addMenuActions()

    def displayMessage(self, message):
        self.parent.parent.displayMessage(message)

    def updateContextMenu(self):
        text = self.getText()
        parser = BibleVerseParser(config.parserStandarisation)
        book = parser.bcvToVerseReference(self.getBook(), 1, 1)[:-4]
        del parser
        self.searchText.setText("{1} {0}".format(text, config.thisTranslation["context1_search"]))
        self.searchTextInBook.setText("{2} {0} > {1}".format(text, book, config.thisTranslation["context1_search"]))
        self.searchBibleTopic.setText("{1} > {0}".format(config.topic, config.thisTranslation["menu5_topics"]))
        self.searchBibleDictionary.setText("{1} > {0}".format(config.dictionary, config.thisTranslation["context1_dict"]))
        self.searchBibleEncyclopedia.setText("{1} > {0}".format(config.encyclopedia, config.thisTranslation["context1_encyclopedia"]))
        self.searchThirdDictionary.setText("{1} > {0}".format(config.thirdDictionary, config.thisTranslation["menu5_3rdDict"]))

    def getText(self):
        text = {
            "main": config.mainText,
            "study": config.studyText,
            "instant": config.mainText,
        }
        return text[self.name]

    def getBook(self):
        book = {
            "main": config.mainB,
            "study": config.studyB,
            "instant": config.mainB,
        }
        return book[self.name]

    def addMenuActions(self):
        copyText = QAction(self)
        copyText.setText(config.thisTranslation["context1_copy"])
        copyText.triggered.connect(self.copySelectedText)
        self.addAction(copyText)

        if config.enableCopyHtmlCommand:
            copyHtml = QAction(self)
            copyHtml.setText(config.thisTranslation["context1_copy_html"])
            copyHtml.triggered.connect(self.copyHtmlCode)
            self.addAction(copyHtml)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        if self.name == "main":
            # Instant highlight feature
            action = QAction(self)
            action.setText(config.thisTranslation["instantHighlight"])
            action.triggered.connect(self.instantHighlight)
            self.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["removeInstantHighlight"])
            action.triggered.connect(self.removeInstantHighlight)
            self.addAction(action)

            separator = QAction(self)
            separator.setSeparator(True)
            self.addAction(separator)

        # TEXT-TO-SPEECH feature
        tts = QAction(self)
        tts.setText(config.thisTranslation["context1_speak"])
        tts.triggered.connect(self.textToSpeech)
        self.addAction(tts)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        # IBM-Watson Translation Service
        # Translate into English
        translateText = QAction(self)
        translateText.setText(config.thisTranslation["context1_english"])
        translateText.triggered.connect(self.selectedTextToEnglish)
        self.addAction(translateText)

        # Translate into User-defined Language
        if config.userLanguage and not config.userLanguage == "English":
            userLanguage = config.userLanguage
            translateText = QAction(self)
            translateText.setText("{0} {1}".format(config.thisTranslation["context1_translate"], userLanguage))
            translateText.triggered.connect(self.checkUserLanguage)
            self.addAction(translateText)

        # CHINESE TOOL - pinyin
        # Convert Chinese characters into pinyin
        if config.isPypinyinInstalled:
            pinyinText = QAction(self)
            pinyinText.setText(config.thisTranslation["context1_pinyin"])
            pinyinText.triggered.connect(self.pinyinSelectedText)
            self.addAction(pinyinText)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["menu7_create"])
        action.triggered.connect(self.insertIntoNewNote)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["searchPanel"])
        action.triggered.connect(self.searchPanel)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        self.searchText = QAction(self)
        self.searchText.setText(config.thisTranslation["context1_search"])
        self.searchText.triggered.connect(self.searchSelectedText)
        self.addAction(self.searchText)

        self.searchTextInBook = QAction(self)
        self.searchTextInBook.setText(config.thisTranslation["context1_current"])
        self.searchTextInBook.triggered.connect(self.searchSelectedTextInBook)
        self.addAction(self.searchTextInBook)

        searchFavouriteBible = QAction(self)
        searchFavouriteBible.setText(config.thisTranslation["context1_favourite"])
        searchFavouriteBible.triggered.connect(self.searchSelectedFavouriteBible)
        self.addAction(searchFavouriteBible)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        for keyword in ("SEARCHBOOKNOTE", "SEARCHCHAPTERNOTE", "SEARCHVERSENOTE"):
            action = QAction(self)
            action.setText(config.thisTranslation[keyword])
            action.triggered.connect(partial(self.searchBibleNote, keyword))
            self.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["removeNoteHighlight"])
        action.triggered.connect(self.removeNoteHighlight)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        searchTextOriginal = QAction(self)
        searchTextOriginal.setText(config.thisTranslation["context1_original"])
        searchTextOriginal.triggered.connect(self.searchSelectedTextOriginal)
        self.addAction(searchTextOriginal)

        self.searchLexicon = QAction(self)
        self.searchLexicon.setText(config.thisTranslation["context1_originalLexicon"])
        self.searchLexicon.triggered.connect(self.searchHebrewGreekLexicon)
        self.addAction(self.searchLexicon)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        searchFavouriteBooks = QAction(self)
        searchFavouriteBooks.setText(config.thisTranslation["context1_favouriteBooks"])
        searchFavouriteBooks.triggered.connect(self.searchSearchFavouriteBooks)
        self.addAction(searchFavouriteBooks)

        searchFavouriteBooks = QAction(self)
        searchFavouriteBooks.setText(config.thisTranslation["context1_allBooks"])
        searchFavouriteBooks.triggered.connect(self.searchAllBooks)
        self.addAction(searchFavouriteBooks)

        action = QAction(self)
        action.setText(config.thisTranslation["removeBookHighlight"])
        action.triggered.connect(self.removeBookHighlight)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        searchBibleCharacter = QAction(self)
        searchBibleCharacter.setText(config.thisTranslation["menu5_characters"])
        searchBibleCharacter.triggered.connect(self.searchCharacter)
        self.addAction(searchBibleCharacter)

        searchBibleName = QAction(self)
        searchBibleName.setText(config.thisTranslation["menu5_names"])
        searchBibleName.triggered.connect(self.searchName)
        self.addAction(searchBibleName)

        searchBibleLocation = QAction(self)
        searchBibleLocation.setText(config.thisTranslation["menu5_locations"])
        searchBibleLocation.triggered.connect(self.searchLocation)
        self.addAction(searchBibleLocation)

        self.searchBibleTopic = QAction(self)
        self.searchBibleTopic.setText(config.thisTranslation["menu5_topics"])
        self.searchBibleTopic.triggered.connect(self.searchTopic)
        self.addAction(self.searchBibleTopic)

        self.searchBibleEncyclopedia = QAction(self)
        self.searchBibleEncyclopedia.setText(config.thisTranslation["context1_encyclopedia"])
        self.searchBibleEncyclopedia.triggered.connect(self.searchEncyclopedia)
        self.addAction(self.searchBibleEncyclopedia)

        self.searchBibleDictionary = QAction(self)
        self.searchBibleDictionary.setText(config.thisTranslation["context1_dict"])
        self.searchBibleDictionary.triggered.connect(self.searchDictionary)
        self.addAction(self.searchBibleDictionary)

        self.searchThirdDictionary = QAction(self)
        self.searchThirdDictionary.setText(config.thisTranslation["menu5_3rdDict"])
        self.searchThirdDictionary.triggered.connect(self.searchThirdPartyDictionary)
        self.addAction(self.searchThirdDictionary)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        searchBibleReferences = QAction(self)
        searchBibleReferences.setText(config.thisTranslation["context1_extract"])
        searchBibleReferences.triggered.connect(self.extractAllReferences)
        self.addAction(searchBibleReferences)

        copyReferences = QAction(self)
        copyReferences.setText(config.thisTranslation["context1_copyReferences"])
        copyReferences.triggered.connect(self.copyAllReferences)
        self.addAction(copyReferences)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["openOnNewWindow"])
        action.triggered.connect(self.openOnNewWindow)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        runAsCommandLine = QAction(self)
        runAsCommandLine.setText(config.thisTranslation["context1_command"])
        runAsCommandLine.triggered.connect(self.runAsCommand)
        self.addAction(runAsCommandLine)

    def messageNoSelection(self):
        self.displayMessage("{0}\n{1}".format(config.thisTranslation["message_run"], config.thisTranslation["selectTextFirst"]))

    def messageNoTtsEngine(self):
        self.displayMessage(config.thisTranslation["message_noSupport"])

    def messageNoTtsVoice(self):
        self.displayMessage(config.thisTranslation["message_noTtsVoice"])

    def copySelectedText(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            self.page().triggerAction(self.page().Copy)

    def copyHtmlCode(self):
        self.page().runJavaScript("document.documentElement.outerHTML", 0, self.copyHtmlToClipboard)

    def copyHtmlToClipboard(self, html):
        QApplication.clipboard().setText(html)

    # Instant highligh feature
    def instantHighlight(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            config.instantHighlightString = selectedText
            self.parent.parent.reloadCurrentRecord()

    def removeInstantHighlight(self):
        if config.instantHighlightString:
            config.instantHighlightString = ""
            self.parent.parent.reloadCurrentRecord()

    # Translate selected words into English
    def selectedTextToEnglish(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            self.translateTextIntoUserLanguage(selectedText)

    # Translate selected words into Traditional Chinese
    def selectedTextToTraditionalChinese(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            self.translateTextIntoUserLanguage(selectedText, "zh-TW")

    # Translate selected words into Simplified Chinese
    def selectedTextToSimplifiedChinese(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            self.translateTextIntoUserLanguage(selectedText, "zh")

    # Check if config.userLanguage is set
    def checkUserLanguage(self):
        # Use IBM Watson service to translate text
        translator = Translator()
        if translator.language_translator is not None:
            if config.userLanguage and config.userLanguage in Translator.toLanguageNames:
                selectedText = self.selectedText()
                if not selectedText:
                    self.messageNoSelection()
                else:
                    userLanguage = Translator.toLanguageCodes[Translator.toLanguageNames.index(config.userLanguage)]
                    self.translateTextIntoUserLanguage(selectedText, userLanguage)
            else:
                self.parent.parent.openTranslationLanguageDialog()
        else:
            self.parent.parent.displayMessage(config.thisTranslation["ibmWatsonNotEnalbed"])

    # Translate selected words into user-defined language
    def translateTextIntoUserLanguage(self, text, userLanguage="en"):
        # Use IBM Watson service to translate text
        translator = Translator()
        if translator.language_translator is not None:
            translation = translator.translate(text, None, userLanguage)
            self.parent.parent.displayMessage(translation)
            if config.autoCopyTranslateResult:
                QApplication.clipboard().setText(translation)
        else:
            self.parent.parent.displayMessage(config.thisTranslation["ibmWatsonNotEnalbed"])

    # Translate Chinese characters into pinyin
    def pinyinSelectedText(self):
        from pypinyin import pinyin
        if not self.selectedText():
            self.messageNoSelection()
        else:
            pinyinList = pinyin(self.selectedText())
            pinyinList = [" ".join(list) for list in pinyinList]
            pinyinText = " ".join(pinyinList)
            if config.autoCopyChinesePinyinOutput:
                QApplication.clipboard().setText(pinyinText)
            self.displayMessage(pinyinText)

    # TEXT-TO-SPEECH feature
    def textToSpeech(self):
        if config.isTtsInstalled:
            selectedText = self.selectedText()
            if not selectedText:
                self.messageNoSelection()
            elif config.isLangdetectInstalled and config.useLangDetectOnTts:
                from langdetect import detect, DetectorFactory
                DetectorFactory.seed = 0
                # https://pypi.org/project/langdetect/
                language = detect(selectedText)
                speakCommand = "SPEAK:::{0}:::{1}".format(language, selectedText)
                self.parent.parent.textCommandChanged(speakCommand, self.name)
            else:
                speakCommand = "SPEAK:::{0}".format(selectedText)
                self.parent.parent.textCommandChanged(speakCommand, self.name)
        else:
            self.messageNoTtsEngine()

    def searchPanel(self):
        selectedText = self.selectedText()
        if selectedText:
            config.contextItem = selectedText
        self.parent.parent.openControlPanelTab(2)

    def insertIntoNewNote(self):
        selectedText = self.selectedText()
        if selectedText:
            config.contextItem = selectedText
        self.parent.parent.createNewNoteFile()

    def searchSelectedText(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format(self.getText(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedTextInBook(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "ADVANCEDSEARCH:::{0}:::Book = {1} AND Scripture LIKE '%{2}%'".format(self.getText(), self.getBook(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedFavouriteBible(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format(config.favouriteBible, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedTextOriginal(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format("MOB", selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchHebrewGreekLexicon(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "LEXICON:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSearchFavouriteBooks(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHBOOK:::FAV:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchAllBooks(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHBOOK:::ALL:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def removeBookHighlight(self):
        if config.bookSearchString:
            config.bookSearchString = ""
            self.parent.parent.reloadCurrentRecord()

    def searchBibleNote(self, keyword):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "{0}:::{1}".format(keyword, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def removeNoteHighlight(self):
        if config.noteSearchString:
            config.noteSearchString = ""
            self.parent.parent.reloadCurrentRecord()

    def searchResource(self, module):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTOOL:::{0}:::{1}".format(module, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchCharacter(self):
        self.searchResource("EXLBP")

    def searchName(self):
        self.searchResource("HBN")

    def searchLocation(self):
        self.searchResource("EXLBL")

    def searchTopic(self):
        self.searchResource(config.topic)

    def searchDictionary(self):
        self.searchResource(config.dictionary)

    def searchEncyclopedia(self):
        self.searchResource(config.encyclopedia)

    def searchThirdPartyDictionary(self):
        selectedText = self.selectedText()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(config.thirdDictionary, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def openOnNewWindow(self):
        self.page().runJavaScript("document.documentElement.outerHTML", 0, self.openNewWindow)

    def openNewWindow(self, html):
        self.openPopover(html=html)

    def extractAllReferences(self):
        selectedText = self.selectedText()
        parser = BibleVerseParser(config.parserStandarisation)
        verseList = parser.extractAllReferences(selectedText, False)
        del parser
        if not verseList:
            self.displayMessage(config.thisTranslation["message_noReference"])
        else:
            biblesSqlite = BiblesSqlite()
            verses = biblesSqlite.readMultipleVerses(self.getText(), verseList)
            del biblesSqlite
            self.openPopover(html=verses)

    def copyAllReferences(self):
        selectedText = self.selectedText()
        parser = BibleVerseParser(config.parserStandarisation)
        verseList = parser.extractAllReferences(selectedText, False)
        if not verseList:
            self.displayMessage(config.thisTranslation["message_noReference"])
        else:
            references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verseList])
            QApplication.clipboard().setText(references)
        del parser

    def runAsCommand(self):
        selectedText = self.selectedText()
        self.parent.parent.textCommandChanged(selectedText, "main")

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserWindow or windowType == QWebEnginePage.WebBrowserTab:
            self.openPopover()
        return super().createWindow(windowType)

    def openPopover(self, name="popover", html="UniqueBible.app"):
        # image options
        if config.exportEmbeddedImages:
            html = self.parent.parent.exportAllImages(html)
        if config.clickToOpenImage:
            html = self.parent.parent.addOpenImageAction(html)
        # format html content
        if self.name == "main":
            activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.mainText, config.mainB, config.mainC, config.mainV)
        elif self.name == "study":
            activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.studyText, config.studyB, config.studyC, config.studyV)
        html = "<!DOCTYPE html><html><head><title>UniqueBible.app</title><style>body {1} font-size: {3}px; font-family:'{4}'; {2} zh {1} font-family:'{5}'; {2} {8}</style><link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{7}.css'><link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css'><script src='js/{7}.js'></script><script src='w3.js'></script><script src='js/custom.js'></script>{6}<script>var versionList = []; var compareList = []; var parallelList = []; var diffList = []; var searchList = [];</script></head><body><span id='v0.0.0'></span>{0}</body></html>".format(html, "{", "}", config.fontSize, config.font, config.fontChinese, activeBCVsettings, config.theme, self.parent.parent.getHighlightCss())
        self.popoverView = WebEngineViewPopover(self, name, self.name)
        self.popoverView.setHtml(html, config.baseUrl)
        self.popoverView.show()

class WebEnginePage(QWebEnginePage):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def acceptNavigationRequest(self, url,  _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            # The following line opens a desktop browser
            #QDesktopServices.openUrl(url);

            # url here is a QUrl
            # can redirect to another link, e.g.
            # url = QUrl("https://marvel.bible")
            self.setUrl(url)
            return False
        return True
