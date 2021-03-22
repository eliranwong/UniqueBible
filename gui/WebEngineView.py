from Languages import Languages
import config, os, platform, webbrowser
from functools import partial
from qtpy.QtCore import Qt
#from qtpy.QtGui import QDesktopServices
from qtpy.QtGui import QGuiApplication, QKeySequence
from qtpy.QtWidgets import QAction, QApplication, QDesktopWidget, QMenu
from qtpy.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite
from Translator import Translator
from gui.WebEngineViewPopover import WebEngineViewPopover
from util.FileUtil import FileUtil

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

    def switchToCli(self):
        if config.isHtmlTextInstalled:
            config.pluginContext = self.name
            QGuiApplication.instance().setApplicationName("UniqueBible.app CLI")
            config.pluginContext = ""
        else:
            self.displayMessage("CLI feature is not enabled! \n Install module 'html-text' first, by running 'pip3 install html-text'!")

    def addMenuActions(self):

        subMenu = QMenu()

        copyText = QAction(self)
        copyText.setText(config.thisTranslation["text"])
        copyText.triggered.connect(self.copySelectedText)
        subMenu.addAction(copyText)

        copyReferences = QAction(self)
        copyReferences.setText(config.thisTranslation["bibleReferences"])
        copyReferences.triggered.connect(self.copyAllReferences)
        subMenu.addAction(copyReferences)

        copyHtml = QAction(self)
        copyHtml.setText(config.thisTranslation["htmlCode"])
        copyHtml.triggered.connect(self.copyHtmlCode)
        subMenu.addAction(copyHtml)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_copy"])
        action.setMenu(subMenu)
        self.addAction(action)

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
        languages = self.parent.parent.getTtsLanguages()
        tts = QAction(self)
        tts.setText("{0} [{1}]".format(config.thisTranslation["context1_speak"], languages[config.ttsDefaultLangauge][1].capitalize()))
        tts.triggered.connect(self.textToSpeech)
        self.addAction(tts)

        if config.isTtsInstalled:
            ttsMenu = QMenu()
            languageCodes = list(languages.keys())
            items = [languages[code][1] for code in languageCodes]
            for index, item in enumerate(items):
                languageCode = languageCodes[index]
                action = QAction(self)
                action.setText(item.capitalize())
                action.triggered.connect(partial(self.textToSpeechLanguage, languageCode))
                ttsMenu.addAction(action)

            tts = QAction(self)
            tts.setText(config.thisTranslation["context1_speak"])
            tts.setMenu(ttsMenu)
            self.addAction(tts)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        # IBM-Watson Translation Service

        # Translate into User-defined Language
        userLanguage = config.userLanguage
        translateText = QAction(self)
        translateText.setText("{0} [{1}]".format(config.thisTranslation["context1_translate"], userLanguage))
        translateText.triggered.connect(self.checkUserLanguage)
        self.addAction(translateText)

        translateMenu = QMenu()
        for index, item in enumerate(Translator.toLanguageNames):
            languageCode = Translator.toLanguageCodes[index]
            action = QAction(self)
            action.setText(item)
            action.triggered.connect(partial(self.selectedTextToSelectedLanguage, languageCode))
            translateMenu.addAction(action)

        translate = QAction(self)
        translate.setText(config.thisTranslation["watsonTranslator"])
        translate.setMenu(translateMenu)
        self.addAction(translate)

        translateMenu = QMenu()
        for language, languageCode in Languages.googleTranslateCodes.items():
            action = QAction(self)
            action.setText(language)
            action.triggered.connect(partial(self.googleTranslate, languageCode))
            translateMenu.addAction(action)

        translate = QAction(self)
        translate.setText(config.thisTranslation["googleTranslate"])
        translate.setMenu(translateMenu)
        self.addAction(translate)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_search"])
        action.triggered.connect(self.searchPanel)
        self.addAction(action)

        subMenu = QMenu()

        self.searchText = QAction(self)
        self.searchText.setText("{0} [{1}]".format(config.thisTranslation["context1_search"], config.mainText))
        self.searchText.triggered.connect(self.searchSelectedText)
        subMenu.addAction(self.searchText)

        self.searchTextInBook = QAction(self)
        self.searchTextInBook.setText(config.thisTranslation["context1_current"])
        self.searchTextInBook.triggered.connect(self.searchSelectedTextInBook)
        subMenu.addAction(self.searchTextInBook)

        searchFavouriteBible = QAction(self)
        searchFavouriteBible.setText(config.thisTranslation["context1_favourite"])
        searchFavouriteBible.triggered.connect(self.searchSelectedFavouriteBible)
        subMenu.addAction(searchFavouriteBible)

        action = QAction(self)
        action.setText(config.thisTranslation["bibleText"])
        action.setMenu(subMenu)
        self.addAction(action)

        subMenu = QMenu()
        for keyword in ("SEARCHBOOKNOTE", "SEARCHCHAPTERNOTE", "SEARCHVERSENOTE"):
            action = QAction(self)
            action.setText(config.thisTranslation[keyword])
            action.triggered.connect(partial(self.searchBibleNote, keyword))
            subMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subMenu.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["removeNoteHighlight"])
        action.triggered.connect(self.removeNoteHighlight)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["menu6_notes"])
        action.setMenu(subMenu)
        self.addAction(action)

        subMenu = QMenu()
        searchFavouriteBooks = QAction(self)
        searchFavouriteBooks.setText(config.thisTranslation["context1_favouriteBooks"])
        searchFavouriteBooks.triggered.connect(self.searchSearchFavouriteBooks)
        subMenu.addAction(searchFavouriteBooks)

        searchFavouriteBooks = QAction(self)
        searchFavouriteBooks.setText(config.thisTranslation["context1_allBooks"])
        searchFavouriteBooks.triggered.connect(self.searchAllBooks)
        subMenu.addAction(searchFavouriteBooks)

        action = QAction(self)
        action.setText(config.thisTranslation["removeBookHighlight"])
        action.triggered.connect(self.removeBookHighlight)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["installBooks"])
        action.setMenu(subMenu)
        self.addAction(action)

        subMenu = QMenu()

        searchBibleCharacter = QAction(self)
        searchBibleCharacter.setText(config.thisTranslation["menu5_characters"])
        searchBibleCharacter.triggered.connect(self.searchCharacter)
        subMenu.addAction(searchBibleCharacter)

        searchBibleName = QAction(self)
        searchBibleName.setText(config.thisTranslation["menu5_names"])
        searchBibleName.triggered.connect(self.searchName)
        subMenu.addAction(searchBibleName)

        searchBibleLocation = QAction(self)
        searchBibleLocation.setText(config.thisTranslation["menu5_locations"])
        searchBibleLocation.triggered.connect(self.searchLocation)
        subMenu.addAction(searchBibleLocation)

        self.searchBibleTopic = QAction(self)
        self.searchBibleTopic.setText(config.thisTranslation["menu5_topics"])
        self.searchBibleTopic.triggered.connect(self.searchTopic)
        subMenu.addAction(self.searchBibleTopic)

        self.searchBibleDictionary = QAction(self)
        self.searchBibleDictionary.setText(config.thisTranslation["context1_dict"])
        self.searchBibleDictionary.triggered.connect(self.searchDictionary)
        subMenu.addAction(self.searchBibleDictionary)

        self.searchBibleEncyclopedia = QAction(self)
        self.searchBibleEncyclopedia.setText(config.thisTranslation["context1_encyclopedia"])
        self.searchBibleEncyclopedia.triggered.connect(self.searchEncyclopedia)
        subMenu.addAction(self.searchBibleEncyclopedia)

        self.searchLexicon = QAction(self)
        self.searchLexicon.setText(config.thisTranslation["menu5_lexicon"])
        self.searchLexicon.triggered.connect(self.searchHebrewGreekLexicon)
        subMenu.addAction(self.searchLexicon)

        self.searchThirdDictionary = QAction(self)
        self.searchThirdDictionary.setText(config.thisTranslation["menu5_3rdDict"])
        self.searchThirdDictionary.triggered.connect(self.searchThirdPartyDictionary)
        subMenu.addAction(self.searchThirdDictionary)

        action = QAction(self)
        action.setText(config.thisTranslation["menu5_lookup"])
        action.setMenu(subMenu)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        subMenu = QMenu()

        searchBibleReferences = QAction(self)
        searchBibleReferences.setText(config.thisTranslation["openOnNewWindow"])
        searchBibleReferences.triggered.connect(self.displayVersesInNewWindow)
        subMenu.addAction(searchBibleReferences)

        searchBibleReferences = QAction(self)
        searchBibleReferences.setText(config.thisTranslation["bar1_menu"])
        searchBibleReferences.triggered.connect(self.displayVersesInBibleWindow)
        subMenu.addAction(searchBibleReferences)

        searchBibleReferences = QAction(self)
        searchBibleReferences.setText(config.thisTranslation["bottomWindow"])
        searchBibleReferences.triggered.connect(self.displayVersesInBottomWindow)
        subMenu.addAction(searchBibleReferences)

        action = QAction(self)
        action.setText(config.thisTranslation["displayVerses"])
        action.setMenu(subMenu)
        self.addAction(action)

        if self.name in ("main", "study"):

            subMenu = QMenu()
    
            if hasattr(config, "cli"):
                action = QAction(self)
                action.setText(config.thisTranslation["cli"])
                action.triggered.connect(self.switchToCli)
                subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["openOnNewWindow"])
            action.triggered.connect(self.openOnNewWindow)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["pdfDocument"])
            action.triggered.connect(self.exportToPdf)
            subMenu.addAction(action)
    
            action = QAction(self)
            action.setText(config.thisTranslation["displayContent"])
            action.setMenu(subMenu)
            self.addAction(action)

        # Context menu plugins
        if config.enablePlugins:

            separator = QAction(self)
            separator.setSeparator(True)
            self.addAction(separator)

            subMenu = QMenu()

            for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "context"), "py"):
                action = QAction(self)
                if "_" in plugin:
                    feature, shortcut = plugin.split("_", 1)
                    action.setText(feature)
                    # The following line does not work
                    #action.setShortcut(QKeySequence(shortcut))
                    self.parent.parent.addContextPluginShortcut(plugin, shortcut)
                else:
                    action.setText(plugin)
                action.triggered.connect(partial(self.runPlugin, plugin))
                subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["menu_plugins"])
            action.setMenu(subMenu)
            self.addAction(action)

    def runPlugin(self, fileName):
        config.contextSource = self
        config.pluginContext = self.selectedText().strip()
        script = os.path.join(os.getcwd(), "plugins", "context", "{0}.py".format(fileName))
        self.parent.parent.execPythonFile(script)
        config.pluginContext = ""
        config.contextSource = None

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
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            config.instantHighlightString = selectedText
            self.parent.parent.reloadCurrentRecord()

    def removeInstantHighlight(self):
        if config.instantHighlightString:
            config.instantHighlightString = ""
            self.parent.parent.reloadCurrentRecord()

    # Translate selected words into Selected Language (Google Translate)
    # Url format to translate a phrase:
    # http://translate.google.com/#origin_language_or_auto|destination_language|encoded_phrase
    # or
    # http://translate.google.com/translate?js=n&sl=auto&tl=destination_language&text=encoded_phrase
    # Url format to translate a webpage:
    # http://translate.google.com/translate?js=n&sl=auto&tl=destination_language&u=http://example.net
    def googleTranslate(self, language):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            selectedText = selectedText.replace("\n", "%0D%0A")
            url = "https://translate.google.com/?sl=origin_language_or_auto&tl={0}&text={1}&op=translate".format(language, selectedText)
            webbrowser.open(url)

    # Translate selected words into Selected Language (Watson Translator)
    def selectedTextToSelectedLanguage(self, language):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            self.translateTextIntoUserLanguage(selectedText, language)

    # Check if config.userLanguage is set
    def checkUserLanguage(self):
        # Use IBM Watson service to translate text
        translator = Translator()
        if translator.language_translator is not None:
            if config.userLanguage and config.userLanguage in Translator.toLanguageNames:
                selectedText = self.selectedText().strip()
                if not selectedText:
                    self.messageNoSelection()
                else:
                    userLanguage = Translator.toLanguageCodes[Translator.toLanguageNames.index(config.userLanguage)]
                    self.translateTextIntoUserLanguage(selectedText, userLanguage)
            else:
                self.parent.parent.openTranslationLanguageDialog()
        else:
            self.parent.parent.displayMessage(config.thisTranslation["ibmWatsonNotEnalbed"])
            config.mainWindow.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/IBM-Watson-Language-Translator")

    # Translate selected words into user-defined language
    def translateTextIntoUserLanguage(self, text, userLanguage="en"):
        # Use IBM Watson service to translate text
        translator = Translator()
        if translator.language_translator is not None:
            translation = translator.translate(text, None, userLanguage)
            self.openPopover(html=translation)
        else:
            self.parent.parent.displayMessage(config.thisTranslation["ibmWatsonNotEnalbed"])
            config.mainWindow.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/IBM-Watson-Language-Translator")

    # TEXT-TO-SPEECH feature
    def textToSpeech(self):
        if config.isTtsInstalled:
            selectedText = self.selectedText().strip()
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

    def textToSpeechLanguage(self, language):
        if config.isTtsInstalled:
            selectedText = self.selectedText().strip()
            if not selectedText:
                self.messageNoSelection()
            speakCommand = "SPEAK:::{0}:::{1}".format(language, selectedText)
            self.parent.parent.textCommandChanged(speakCommand, self.name)
        else:
            self.messageNoTtsEngine()

    def searchPanel(self):
        selectedText = self.selectedText().strip()
        if selectedText:
            config.contextItem = selectedText
        self.parent.parent.openControlPanelTab(2)

    def searchSelectedText(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format(self.getText(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedTextInBook(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "ADVANCEDSEARCH:::{0}:::Book = {1} AND Scripture LIKE '%{2}%'".format(self.getText(), self.getBook(), selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedFavouriteBible(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format(config.favouriteBible, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedTextOriginal(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format("MOB", selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchHebrewGreekLexicon(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "LEXICON:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSearchFavouriteBooks(self):
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHBOOK:::FAV:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchAllBooks(self):
        selectedText = self.selectedText().strip()
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
        selectedText = self.selectedText().strip()
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
        selectedText = self.selectedText().strip()
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
        selectedText = self.selectedText().strip()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(config.thirdDictionary, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def exportToPdf(self):
        if self.name == "main":
            self.parent.parent.printMainPage()
        elif self.name == "study":
            self.parent.parent.printStudyPage()

    def openOnNewWindow(self):
        self.page().runJavaScript("document.documentElement.outerHTML", 0, self.openNewWindow)

    def openNewWindow(self, html):
        self.openPopover(html=html)

    def displayVersesInBottomWindow(self):
        selectedText = self.selectedText().strip()
        if selectedText:
            verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
            if verses:
                html = BiblesSqlite().readMultipleVerses(self.getText(), verses)
                self.parent.parent.displayPlainTextOnBottomWindow(html)
        else:
            self.messageNoSelection()

    def displayVersesInNewWindow(self):
        selectedText = self.selectedText().strip()
        if selectedText:
            verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
            if verses:
                html = BiblesSqlite().readMultipleVerses(self.getText(), verses)
                self.openPopover(html=html)
        else:
            self.messageNoSelection()

    def displayVersesInBibleWindow(self):
        selectedText = self.selectedText().strip()
        if selectedText:
            parser = BibleVerseParser(config.parserStandarisation)
            verses = parser.extractAllReferences(selectedText, False)
            if verses:
                references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verses])
                self.parent.parent.textCommandChanged(references, "main")
            del parser
        else:
            self.messageNoSelection()

    def copyAllReferences(self):
        selectedText = self.selectedText().strip()
        if selectedText:
            parser = BibleVerseParser(config.parserStandarisation)
            verseList = parser.extractAllReferences(selectedText, False)
            if not verseList:
                self.displayMessage(config.thisTranslation["message_noReference"])
            else:
                references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verseList])
                QApplication.clipboard().setText(references)
            del parser
        else:
            self.messageNoSelection()

    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserWindow or windowType == QWebEnginePage.WebBrowserTab:
            self.openPopover()
        return super().createWindow(windowType)

    def openPopover(self, name="popover", html="UniqueBible.app", fullScreen=False, screenNo=-1):
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
        if not hasattr(self, "popoverView") or not self.popoverView.isVisible:
            self.popoverView = WebEngineViewPopover(self, name, self.name)
        self.popoverView.setHtml(html, config.baseUrl)
        if fullScreen:
            monitor = QDesktopWidget().screenGeometry(screenNo)
            self.popoverView.move(monitor.left(), monitor.top())
            if platform.system() == "Linux":
                # Using self.popoverView.showFullScreen() directly does not work on Linux
                self.popoverView.showMaximized()
                self.popoverView.escKeyPressed()
            else:
                self.popoverView.showFullScreen()
        else:
            self.popoverView.setMinimumWidth(config.popoverWindowWidth)
            self.popoverView.setMinimumHeight(config.popoverWindowHeight)
        self.popoverView.show()

    def closePopover(self):
        if hasattr(self, "popoverView"):
            self.popoverView.close()

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

