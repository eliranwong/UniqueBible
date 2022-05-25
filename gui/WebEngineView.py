from util.Languages import Languages
from util.GoogleCloudTTSVoices import GoogleCloudTTS
import config, os, platform, webbrowser, re, subprocess
import shortcut as sc
from functools import partial
from qtpy.QtCore import Qt
from qtpy.QtCore import QUrl
from qtpy.QtGui import QGuiApplication, QKeySequence
from qtpy.QtWidgets import QAction, QApplication, QDesktopWidget, QMenu, QFileDialog, QInputDialog, QLineEdit
from qtpy.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineSettings
from util.BibleVerseParser import BibleVerseParser
from db.BiblesSqlite import BiblesSqlite
from util.Translator import Translator
from gui.WebEngineViewPopover import WebEngineViewPopover
from util.FileUtil import FileUtil
from util.TextUtil import TextUtil
from util.BibleBooks import BibleBooks
from util.HebrewTransliteration import HebrewTransliteration
from util.WebtopUtil import WebtopUtil
from util.ShortcutUtil import ShortcutUtil
from install.module import *


class WebEngineView(QWebEngineView):
    
    def __init__(self, parent, name):
        super().__init__()
        self.parent = parent
        self.name = name
        self.setPage(WebEnginePage(self))
        self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.page().fullScreenRequested.connect(lambda request: request.accept())
       
        # add context menu (triggered by right-clicking)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.selectionChanged.connect(self.updateContextMenu)
        self.addMenuActions()

    def displayMessage(self, message):
        self.parent.parent.displayMessage(message)

    def updateDefaultTtsVoice(self):
        display = "{0} [{1}] | {2}".format(config.thisTranslation["context1_speak"], config.ttsDefaultLangauge, sc.contextDefaultTTS)
        self.defaultTTSVoice.setText(display)

    def updateContextMenu(self):
        text = self.getText()
        book = BibleVerseParser(config.parserStandarisation).bcvToVerseReference(self.getBook(), 1, 1)[:-4]
        if self.name == "main":
            self.searchText.setText("{1} {0} | {2}".format(text, config.thisTranslation["context1_search"], sc.contextSearchBible))
        else:
            self.searchText.setText("{1} {0}".format(text, config.thisTranslation["context1_search"]))
        self.searchTextInBook.setText("{2} {0} > {1}".format(text, book, config.thisTranslation["context1_search"]))
        self.updateDefaultTtsVoice()
        #self.searchBibleTopic.setText("{1} > {0}".format(config.topic, config.thisTranslation["menu5_topics"]))
        #self.searchBibleDictionary.setText("{1} > {0}".format(config.dictionary, config.thisTranslation["context1_dict"]))
        #self.searchBibleEncyclopedia.setText("{1} > {0}".format(config.encyclopedia, config.thisTranslation["context1_encyclopedia"]))
        #self.searchThirdDictionary.setText("{1} > {0}".format(config.thirdDictionary, config.thisTranslation["menu5_3rdDict"]))

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

        # Open Content in

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
            action.setText(config.thisTranslation["menu1_fullScreen"])
            action.triggered.connect(self.openOnFullScreen)
            subMenu.addAction(action)

            #action = QAction(self)
            #action.setText(config.thisTranslation["pdfDocument"])
            #action.triggered.connect(self.exportToPdf)
            #subMenu.addAction(action)
    
            action = QAction(self)
            action.setText(config.thisTranslation["displayContentIn"])
            action.setMenu(subMenu)
            self.addAction(action)

            separator = QAction(self)
            separator.setSeparator(True)
            self.addAction(separator)

        # Open References in 

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
        action.setText(config.thisTranslation["openReferencesIn"])
        action.setMenu(subMenu)
        self.addAction(action)

        # Open Reference section

        subMenu = QMenu()

        for text in self.parent.parent.textList:
            action = QAction(self)
            action.setText(text)
            action.triggered.connect(partial(self.openReferenceInBibleVersion, text))
            subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["all"])
        action.triggered.connect(self.compareAllVersions)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["openReferencesWith"])
        action.setMenu(subMenu)
        self.addAction(action)

        # Open bookless reference

        subMenu = QMenu()

        bibleVerseParser = BibleVerseParser(config.parserStandarisation)
        for bookNo in range(1, 67):
            action = QAction(self)
            bookName = bibleVerseParser.standardFullBookName[str(bookNo)]
            action.setText(bookName)
            action.triggered.connect(partial(self.openReferencesInBook, bookName))
            subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["openBooklessReferences"])
        action.setMenu(subMenu)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        # Compare references

        action = QAction(self)
        action.setText(config.thisTranslation["compareReferenceSideBySide"])
        action.triggered.connect(partial(self.compareReference, "SIDEBYSIDE"))
        self.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["compareReferenceRowByRow"])
        action.triggered.connect(partial(self.compareReference, "COMPARE"))
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

#        subMenu = QMenu()
#
#        for text in self.parent.parent.textList:
#            action = QAction(self)
#            action.setText(text)
#            action.triggered.connect(partial(self.parallelReferenceWithBibleVersion, text))
#            subMenu.addAction(action)
#        
#        separator = QAction(self)
#        separator.setSeparator(True)
#        subMenu.addAction(separator)
#
#        action = QAction(self)
#        action.setText(config.thisTranslation["all"])
#        action.triggered.connect(self.compareAllVersions)
#        subMenu.addAction(action)
#
#        action = QAction(self)
#        action.setText(config.thisTranslation["compareReferenceSideBySide"])
#        action.setMenu(subMenu)
#        self.addAction(action)
#
#        subMenu = QMenu()
#
#        for text in self.parent.parent.textList:
#            action = QAction(self)
#            action.setText(text)
#            action.triggered.connect(partial(self.compareReferenceWithBibleVersion, text))
#            subMenu.addAction(action)
#        
#        separator = QAction(self)
#        separator.setSeparator(True)
#        subMenu.addAction(separator)
#
#        action = QAction(self)
#        action.setText(config.thisTranslation["all"])
#        action.triggered.connect(self.compareAllVersions)
#        subMenu.addAction(action)
#
#        action = QAction(self)
#        action.setText(config.thisTranslation["compareReferenceRowByRow"])
#        action.setMenu(subMenu)
#        self.addAction(action)
#
#        separator = QAction(self)
#        separator.setSeparator(True)
#        self.addAction(separator)

        # Copy

        subMenu = QMenu()

        copyText = QAction(self)
        copyText.setText(config.thisTranslation["text"])
        copyText.triggered.connect(self.copySelectedText)
        subMenu.addAction(copyText)

        copyText = QAction(self)
        copyText.setText(config.thisTranslation["textWithReference"])
        copyText.triggered.connect(self.copySelectedTextWithReference)
        subMenu.addAction(copyText)

        copyReferences = QAction(self)
        copyReferences.setText(config.thisTranslation["bibleReferences"])
        copyReferences.triggered.connect(self.copyAllReferences)
        subMenu.addAction(copyReferences)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_copy"])
        action.setMenu(subMenu)
        self.addAction(action)

        # Copy All

        subMenu = QMenu()

        copyHtml = QAction(self)
        copyHtml.setText(config.thisTranslation["plainText"])
        copyHtml.triggered.connect(self.copyPlainText)
        subMenu.addAction(copyHtml)

        copyHtml = QAction(self)
        copyHtml.setText(config.thisTranslation["htmlCode"])
        copyHtml.triggered.connect(self.copyHtmlCode)
        subMenu.addAction(copyHtml)

        action = QAction(self)
        action.setText(config.thisTranslation["copyAll"])
        action.setMenu(subMenu)
        self.addAction(action)

        # Save As

        subMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["plainTextFile"])
        action.triggered.connect(self.savePlainText)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["htmlFile"])
        action.triggered.connect(self.saveHtml)
        subMenu.addAction(action)

        if config.isMarkdownInstalled:
            action = QAction(self)
            action.setText(config.thisTranslation["markdownFile"])
            action.triggered.connect(self.saveMarkdown)
            subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["pdfFile"])
        action.triggered.connect(self.savePdf)
        subMenu.addAction(action)

        if config.isHtmldocxInstalled:
            action = QAction(self)
            action.setText(config.thisTranslation["wordFile"])
            action.triggered.connect(self.saveDocx)
            subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["exportTo"])
        action.setMenu(subMenu)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        # Instant highlight feature
        subMenu = QMenu()
        
        action = QAction(self)
        action.setText(config.thisTranslation["menu_highlight"])
        action.triggered.connect(self.instantHighlight)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["remove"])
        action.triggered.connect(self.removeInstantHighlight)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["instantHighlight"])
        action.setMenu(subMenu)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        # Start Search section
        action = QAction(self)
        action.setText(config.thisTranslation["context1_search"])
        action.triggered.connect(self.searchPanel)
        self.addAction(action)

        # Search in currently selected bible
        #subMenu = QMenu()

        self.searchText = QAction(self)
        #self.searchText.setText("{0} [{1}] | {2}".format(config.thisTranslation["context1_search"], config.mainText, sc.contextSearchBible))
        self.searchText.triggered.connect(self.searchSelectedText)
        self.parent.parent.addContextMenuShortcut(partial(self.searchSelectedText, activeSelection=True), sc.contextSearchBible)
        self.addAction(self.searchText)

        self.searchTextInBook = QAction(self)
        self.searchTextInBook.setText(config.thisTranslation["context1_current"])
        self.searchTextInBook.triggered.connect(self.searchSelectedTextInBook)
        self.addAction(self.searchTextInBook)

        #searchFavouriteBible = QAction(self)
        #searchFavouriteBible.triggered.connect(self.searchSelectedFavouriteBible)
        #searchFavouriteBible.setText(config.thisTranslation["context1_favourite"])
        #subMenu.addAction(searchFavouriteBible)

        #action = QAction(self)
        #action.setText(config.thisTranslation["cp0"])
        #action.setMenu(subMenu)
        #self.addAction(action)

        # Search in other books & versions

        subMenu = QMenu()

        bibleVerseParser = BibleVerseParser(config.parserStandarisation)
        for bookNo in range(1, 67):
            action = QAction(self)
            action.setText(bibleVerseParser.standardFullBookName[str(bookNo)])
            action.triggered.connect(partial(self.searchSelectedTextInBook, bookNo))
            subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["searchOtherBibleBooks"])
        action.setMenu(subMenu)
        self.addAction(action)

        subMenu = QMenu()

        for text in self.parent.parent.textList:
            action = QAction(self)
            action.setText(text)
            action.triggered.connect(partial(self.searchSelectedText, text))
            subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["searchOtherBibleVersions"])
        action.setMenu(subMenu)
        self.addAction(action)

        # Search Other Resources

        # Search Bible Notes

        subMenu = QMenu()
        notes = {"SEARCHBOOKNOTE": "menu_bookNotes", "SEARCHCHAPTERNOTE": "menu_chapterNotes", "SEARCHVERSENOTE": "menu_verseNotes"}
        for keyword, translation in notes.items():
            action = QAction(self)
            action.setText(config.thisTranslation[translation])
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
        action.setText(config.thisTranslation["searchNotes"])
        action.setMenu(subMenu)
        self.addAction(action)

        # Search Strong's number bibles, if installed
        if self.parent.parent.strongBibles:
            subMenu = QMenu()
            for text in self.parent.parent.strongBibles:
                action = QAction(self)
                action.setText(text)
                action.triggered.connect(partial(self.searchStrongBible, text))
                subMenu.addAction(action)

            separator = QAction(self)
            separator.setSeparator(True)
            subMenu.addAction(separator)
    
            action = QAction(self)
            action.setText(config.thisTranslation["all"])
            action.triggered.connect(self.searchAllStrongBible)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["searchConcordance"])
            action.setMenu(subMenu)
            self.addAction(action)

        # Search Reference Books

        subMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchPreviousBook)
        subMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subMenu.addAction(separator)

        subSubMenu = QMenu()

        for module in config.favouriteBooks:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchSelectedBook, module))
            subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["all"])
        action.triggered.connect(self.searchFavouriteBooks)
        subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_favouriteBooks"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_allBooks"])
        action.triggered.connect(self.searchAllBooks)
        subMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subMenu.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["removeBookHighlight"])
        action.triggered.connect(self.removeBookHighlight)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["searchReferenceBooks"])
        action.setMenu(subMenu)
        self.addAction(action)

        # Search Other Resources

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

        subSubMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchTopic)
        subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        for module in self.parent.parent.topicListAbb:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchResource, module))
            subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["menu5_topics"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        subSubMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchDictionary)
        subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        for module in self.parent.parent.dictionaryListAbb:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchResource, module))
            subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_dict"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        subSubMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchEncyclopedia)
        subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        for module in self.parent.parent.encyclopediaListAbb:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchResource, module))
            subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["context1_encyclopedia"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        subSubMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchHebrewGreekLexicon)
        subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["all"])
        action.triggered.connect(partial(self.searchHebrewGreekLexiconSelected, config.thisTranslation["all"]))
        subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        for module in self.parent.parent.lexiconList:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchHebrewGreekLexiconSelected, module))
            subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["menu5_lexicon"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        subSubMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["previous"])
        action.triggered.connect(self.searchThirdPartyDictionary)
        subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        for module in self.parent.parent.thirdPartyDictionaryList:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchThirdPartyDictionarySelected, module))
            subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["menu5_3rdDict"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["searchOtherResources"])
        action.setMenu(subMenu)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        # End of Search section

        # Google TEXT-TO-SPEECH feature
        if config.isGoogleCloudTTSAvailable or ((not config.isOfflineTtsInstalled or config.forceOnlineTts) and config.isGTTSInstalled):

            self.defaultTTSVoice = QAction(self)
            self.defaultTTSVoice.triggered.connect(self.googleTextToSpeechLanguage)
            self.parent.parent.addContextMenuShortcut(partial(self.googleTextToSpeechLanguage, "", True), sc.contextDefaultTTS)
            self.addAction(self.defaultTTSVoice)

            ttsMenu = QMenu()
            languageCodes = GoogleCloudTTS.getLanguages() if config.isGoogleCloudTTSAvailable else Languages.gTTSLanguageCodes
            for language, languageCode in languageCodes.items():
                action = QAction(self)
                action.setText("{0} [{1}]".format(language, languageCode))
                action.triggered.connect(partial(self.googleTextToSpeechLanguage, languageCode))
                ttsMenu.addAction(action)

            tts = QAction(self)
            tts.setText(config.thisTranslation["tts_utility"])
            tts.setMenu(ttsMenu)
            self.addAction(tts)

            ttsMenu = QMenu()
            languageCodes = GoogleCloudTTS.getLanguages() if config.isGoogleCloudTTSAvailable else Languages.gTTSLanguageCodes
            for language, languageCode in languageCodes.items():
                action = QAction(self)
                action.setText("{0} [{1}]".format(language, languageCode))
                action.triggered.connect(partial(self.googleTextToSpeechAudio, languageCode))
                ttsMenu.addAction(action)

            tts = QAction(self)
            tts.setText("{0} MP3".format(config.thisTranslation["note_saveAs"]))
            tts.setMenu(ttsMenu)
            self.addAction(tts)

            separator = QAction(self)
            separator.setSeparator(True)
            self.addAction(separator)

        # OFFLINE TEXT-TO-SPEECH feature
        elif config.isOfflineTtsInstalled:
            languages = self.parent.parent.getTtsLanguages()
            self.defaultTTSVoice = QAction(self)
            self.defaultTTSVoice.triggered.connect(self.textToSpeech)
            self.parent.parent.addContextMenuShortcut(partial(self.textToSpeech, True), sc.contextDefaultTTS)
            self.addAction(self.defaultTTSVoice)

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

        watsonTranslate = QAction(self)
        watsonTranslate.setText(config.thisTranslation["watsonTranslator"])
        watsonTranslate.setMenu(translateMenu)

        translateMenu = QMenu()
        for language, languageCode in Languages.googleTranslateCodes.items():
            action = QAction(self)
            action.setText(language)
            action.triggered.connect(partial(self.googleTranslate, languageCode))
            translateMenu.addAction(action)

        googleTranslate = QAction(self)
        googleTranslate.setText(config.thisTranslation["googleTranslate"])
        googleTranslate.setMenu(translateMenu)

        translateWrapper = QAction(self)
        translateWrapper.setText(config.thisTranslation["translate"])
        translateWrapperMenu = QMenu()
        translateWrapperMenu.addAction(watsonTranslate)
        translateWrapperMenu.addAction(googleTranslate)
        translateWrapper.setMenu(translateWrapperMenu)
        self.addAction(translateWrapper)

        # Context menu plugins
        if config.enablePlugins:

            separator = QAction(self)
            separator.setSeparator(True)
            self.addAction(separator)

            subMenu = QMenu()

            for plugin in FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "context"), "py"):
                if not plugin in config.excludeContextPlugins:
                    action = QAction(self)
                    if "_" in plugin:
                        feature, shortcut = plugin.split("_", 1)
                        action.setText("{0} | {1}".format(feature, shortcut) if shortcut else feature)
                        # The following line does not work
                        #action.setShortcut(QKeySequence(shortcut))
                        self.parent.parent.addContextPluginShortcut(plugin, shortcut)
                    else:
                        action.setText(plugin)
                    action.triggered.connect(partial(self.runPlugin, plugin))
                    subMenu.addAction(action)
            
            separator = QAction(self)
            separator.setSeparator(True)
            subMenu.addAction(separator)

            action = QAction(self)
            action.setText(config.thisTranslation["enableIndividualPlugins"])
            action.triggered.connect(self.parent.parent.enableIndividualPluginsWindow)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["menu_plugins"])
            action.setMenu(subMenu)
            self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        action = QAction(self)
        action.setText(config.thisTranslation["menu_about"])
        action.triggered.connect(lambda: webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/Context-Menu"))
        self.addAction(action)

    def selectedTextProcessed(self, activeSelection=False):
        if not activeSelection:
            selectedText = self.selectedText().strip()
        else:
            selectedText = self.parent.parent.mainView.currentWidget().selectedText().strip()
            if not selectedText:
                selectedText = self.parent.parent.studyView.currentWidget().selectedText().strip()
        if not selectedText and config.commandTextIfNoSelection:
            selectedText = self.parent.parent.textCommandLineEdit.text().strip()
        if not selectedText:
            text, ok = QInputDialog.getText(self.parent.parent, "QInputDialog.getText()",
                    config.thisTranslation["enter_text_here"], QLineEdit.Normal,
                    "")
            if ok and text:
                selectedText = text
        return selectedText

    def runPlugin(self, fileName, selectedText=None):
        #if selectedText is None:
        # Note: Tested in Arch Linux using pyqt5, selectedText = False.  Therefore, the line above does not work.
        if not selectedText:
            selectedText = self.selectedTextProcessed()
        config.contextSource = self
        config.pluginContext = selectedText
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
        if not self.selectedTextProcessed():
            self.messageNoSelection()
        else:
            self.page().triggerAction(self.page().Copy)

    def copySelectedTextWithReference(self):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            verse = config.mainV
            lastVerse = None
            try:
                firstVerse = re.findall(r'\d+', selectedText)[0]
                lastVerse = re.findall(r'\d+', selectedText)[-1]
                if firstVerse:
                    verse = firstVerse
                    if int(firstVerse) == int(lastVerse):
                        lastVerse = None
            except:
                pass
            reference = self.parent.parent.bcvToVerseReference(config.mainB, config.mainC, verse)
            if lastVerse:
                reference += "-" + lastVerse
            text = "{0} ({1})\n{2}".format(reference, config.mainText, selectedText)
            QApplication.clipboard().setText(text)

    def copyHtmlCode(self):
        #self.page().runJavaScript("document.documentElement.outerHTML", 0, self.copyHtmlToClipboard)
        self.page().toHtml(self.copyHtmlToClipboard)

    def copyPlainText(self):
        self.page().toPlainText(self.copyHtmlToClipboard)

    def copyHtmlToClipboard(self, text):
        QApplication.clipboard().setText(text)

    # Instant highligh feature
    def instantHighlight(self):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            #self.messageNoSelection()
            text, ok = QInputDialog.getText(self.parent.parent, "QInputDialog.getText()",
                    config.thisTranslation["menu5_search"], QLineEdit.Normal,
                    "")
            if ok and text != '':
                self.findText(text, QWebEnginePage.FindFlags(), self.checkIfTextIsFound)
        else:
            #config.instantHighlightString = selectedText
            #self.parent.parent.reloadCurrentRecord()
            self.findText(selectedText, QWebEnginePage.FindFlags(), self.checkIfTextIsFound)

    def checkIfTextIsFound(self, found):
        if not found:
            self.displayMessage(config.thisTranslation["notFound"])

    def removeInstantHighlight(self):
        #if config.instantHighlightString:
        #    config.instantHighlightString = ""
        #    self.parent.parent.reloadCurrentRecord()
        self.findText("", QWebEnginePage.FindFlags())

    # Translate selected words into Selected Language (Google Translate)
    # Url format to translate a phrase:
    # http://translate.google.com/#origin_language_or_auto|destination_language|encoded_phrase
    # or
    # http://translate.google.com/translate?js=n&sl=auto&tl=destination_language&text=encoded_phrase
    # Url format to translate a webpage:
    # http://translate.google.com/translate?js=n&sl=auto&tl=destination_language&u=http://example.net
    def googleTranslate(self, language):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            selectedText = TextUtil.plainTextToUrl(selectedText)
            url = "https://translate.google.com/?sl=origin_language_or_auto&tl={0}&text={1}&op=translate".format(language, selectedText)
            webbrowser.open(url)

    # Translate selected words into Selected Language (Watson Translator)
    def selectedTextToSelectedLanguage(self, language):
        selectedText = self.selectedTextProcessed()
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
                selectedText = self.selectedTextProcessed()
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
    def textToSpeech(self, activeSelection=False):
        if config.isOfflineTtsInstalled:
            selectedText = self.selectedTextProcessed(activeSelection)
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
        if config.isOfflineTtsInstalled:
            selectedText = self.selectedTextProcessed()
            if not selectedText:
                self.messageNoSelection()
            speakCommand = "SPEAK:::{0}:::{1}".format(language, selectedText)
            self.parent.parent.textCommandChanged(speakCommand, self.name)
        else:
            self.messageNoTtsEngine()

    def isGttsLanguage(self, languageCode):
        languageCodes = GoogleCloudTTS.getLanguages() if config.isGoogleCloudTTSAvailable else Languages.gTTSLanguageCodes
        if languageCode in [languageCode for *_, languageCode in languageCodes.items()]:
            return True
        else:
            self.messageNoTtsVoice()
            return False

    def googleTextToSpeechLanguage(self, language="", activeSelection=False):
        if not language:
            language = config.ttsDefaultLangauge
        if config.isGoogleCloudTTSAvailable and language == "en":
            language = "en-GB"
        selectedText = self.selectedTextProcessed(activeSelection)
        if not selectedText:
            self.messageNoSelection()
        elif self.isGttsLanguage(language):
            speakCommand = "GTTS:::{0}:::{1}".format(language, selectedText)
            self.parent.parent.textCommandChanged(speakCommand, self.name)

    def googleTextToSpeechAudio(self, language):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        elif config.isOnlineTtsInstalled:
            # fine-tune
            selectedText, language = self.parent.parent.fineTuneGtts(selectedText, language)

            if self.isGttsLanguage(language):
                # Ask for a filename
                options = QFileDialog.Options()
                fileName, *_ = QFileDialog.getSaveFileName(self,
                        config.thisTranslation["note_saveAs"],
                        "music",
                        "MP3 Files (*.mp3)", "", options)
                if fileName:
                    if not "." in os.path.basename(fileName):
                        fileName = fileName + ".mp3"
                    # Save mp3 file
                    try:
                        if config.isGoogleCloudTTSAvailable:
                            self.parent.parent.saveCloudTTSAudio(selectedText, language, fileName)
                        else:
                            self.parent.parent.saveGTTSAudio(selectedText, language, fileName)

                        if os.path.isfile(fileName):
                            # Open the directory where the file is saved
                            outputFolder = os.path.dirname(fileName)
                            try:
                                WebtopUtil.run(f"{config.open} {outputFolder}")
                            except:
                                os.system(r"{0} {1}".format(config.open, outputFolder))
                    except:
                        self.displayMessage(config.thisTranslation["message_fail"])

    def searchPanel(self, selectedText=None):
        #if selectedText is None:
        if not selectedText:
            selectedText = self.selectedTextProcessed()
        if selectedText:
            config.contextItem = selectedText
        self.parent.parent.openControlPanelTab(3)

    def searchSelectedText(self, text=None, activeSelection=False):
        selectedText = self.selectedTextProcessed(activeSelection)
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format(self.getText() if text is None or not text else text, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def openReferencesInBook(self, book):
        selectedText = self.selectedTextProcessed()
        command = "{0} {1}".format(book, selectedText) if selectedText else book
        self.parent.parent.textCommandChanged(command, self.name)

    def searchSelectedTextInBook(self, book=None):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "ADVANCEDSEARCH:::{0}:::Book = {1} AND Scripture LIKE '%{2}%'".format(self.getText(), self.getBook() if book is None or not book else book, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedFavouriteBible(self):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format(config.favouriteBible, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedTextOriginal(self):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCH:::{0}:::{1}".format("MOB", selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchHebrewGreekLexicon(self):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "LEXICON:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchHebrewGreekLexiconSelected(self, module):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHLEXICON:::{0}:::{1}".format(module, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchPreviousBook(self):
        self.searchSelectedBook(config.book)

    def searchSelectedBook(self, book):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHBOOK:::{0}:::{1}".format(book, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchFavouriteBooks(self):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHBOOK:::FAV:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchAllBooks(self):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHBOOK:::ALL:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def removeBookHighlight(self):
        if config.bookSearchString:
            config.bookSearchString = ""
            self.parent.parent.reloadCurrentRecord(True)

    def searchBibleNote(self, keyword):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "{0}:::{1}".format(keyword, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def removeNoteHighlight(self):
        if config.noteSearchString:
            config.noteSearchString = ""
            self.parent.parent.reloadCurrentRecord(True)

    def searchStrongBible(self, module):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        elif re.match("^[EGH][0-9]+?$", selectedText):
            searchCommand = "CONCORDANCE:::{0}:::{1}".format(module, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)
        else:
            self.parent.parent.displayMessage(config.thisTranslation["notStrongNumber"])

    def searchAllStrongBible(self):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        elif re.match("^[EGH][0-9]+?$", selectedText):
            searchCommand = "STRONGBIBLE:::ALL:::{0}".format(selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)
        else:
            self.parent.parent.displayMessage(config.thisTranslation["notStrongNumber"])

    def searchResource(self, module):
        selectedText = self.selectedTextProcessed()
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
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(config.thirdDictionary, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchThirdPartyDictionarySelected(self, module):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(module, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def exportToPdf(self):
        if self.name == "main":
            self.parent.parent.printMainPage()
        elif self.name == "study":
            self.parent.parent.printStudyPage()

    def openOnNewWindow(self):
        toolTip = self.parent.mainView.tabToolTip(self.parent.mainView.currentIndex()) if self.name == "main" else self.parent.studyView.tabToolTip(self.parent.studyView.currentIndex())
        if toolTip.lower().endswith(".pdf"):
            openPdfViewerInNewWindow = config.openPdfViewerInNewWindow
            config.openPdfViewerInNewWindow = True
            self.parent.parent.openPdfReader(toolTip, fullPath=True)
            config.openPdfViewerInNewWindow = openPdfViewerInNewWindow
        elif toolTip == "EPUB":
            self.parent.parent.runPlugin("ePub Viewer New Window")
        else:
            #self.page().runJavaScript("document.documentElement.outerHTML", 0, self.openNewWindow)
            self.page().toHtml(self.openNewWindow)

    def openOnFullScreen(self):
        #toolText = self.parent.mainView.tabText(self.parent.mainView.currentIndex()) if self.name == "main" else self.parent.studyView.tabText(self.parent.studyView.currentIndex())
        toolTip = self.parent.mainView.tabToolTip(self.parent.mainView.currentIndex()) if self.name == "main" else self.parent.studyView.tabToolTip(self.parent.studyView.currentIndex())
        if toolTip.lower().endswith(".pdf"):
            openPdfViewerInNewWindow = config.openPdfViewerInNewWindow
            config.openPdfViewerInNewWindow = True
            self.parent.parent.openPdfReader(toolTip, fullPath=True, fullScreen=True)
            config.openPdfViewerInNewWindow = openPdfViewerInNewWindow
        elif toolTip == "EPUB":
            self.parent.parent.runPlugin("ePub Viewer Full Screen")
        else:
            self.page().toHtml(lambda html: self.openNewWindow(html, True))

    def openNewWindow(self, html, fullScreen=False):
        self.openPopover(html=html, fullScreen=fullScreen)

    def displayVersesInBottomWindow(self, selectedText=None):
        #if selectedText is None:
        if not selectedText:
            selectedText = self.selectedTextProcessed()
        if selectedText:
            verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
            if verses:
                html = BiblesSqlite().readMultipleVerses(self.getText(), verses)
                self.parent.parent.displayPlainTextOnBottomWindow(html)
            else:
                self.displayMessage(config.thisTranslation["message_noReference"])
        else:
            self.messageNoSelection()

    def openReferenceInBibleVersion(self, bible):
        selectedText = self.selectedTextProcessed()
        useLiteVerseParsing = config.useLiteVerseParsing
        config.useLiteVerseParsing = False
        verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
        config.useLiteVerseParsing = useLiteVerseParsing
        if verses:
            command = "BIBLE:::{0}:::{1}".format(bible, selectedText)
        elif not config.openBibleInMainViewOnly and self.name == "study":
            command = "STUDY:::{0}:::{1} {2}:{3}".format(bible, BibleBooks.eng[str(config.studyB)][0], config.studyC, config.studyV)
        else:
            command = "TEXT:::{0}".format(bible)
        self.parent.parent.textCommandChanged(command, self.name)

    def compareReference(self, keyword):
        selectedText = self.selectedTextProcessed()
        useLiteVerseParsing = config.useLiteVerseParsing
        config.useLiteVerseParsing = False
        verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
        config.useLiteVerseParsing = useLiteVerseParsing
        if verses:
            self.parent.parent.runCompareAction(keyword, selectedText)
        else:
            self.displayMessage(config.thisTranslation["message_noReference"])

    def compareReferenceWithBibleVersion(self, bible):
        selectedText = self.selectedTextProcessed()
        useLiteVerseParsing = config.useLiteVerseParsing
        config.useLiteVerseParsing = False
        verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
        config.useLiteVerseParsing = useLiteVerseParsing
        if verses:
            command = "COMPARE:::{0}_{1}:::{2}".format(config.mainText, bible, selectedText)
        elif not config.openBibleInMainViewOnly and self.name == "study":
            command = "STUDY:::{0}:::{1} {2}:{3}".format(bible, BibleBooks.eng[str(config.studyB)][0], config.studyC, config.studyV)
        else:
            command = "TEXT:::{0}".format(bible)
        self.parent.parent.textCommandChanged(command, self.name)

    def parallelReferenceWithBibleVersion(self, bible):
        selectedText = self.selectedTextProcessed()
        useLiteVerseParsing = config.useLiteVerseParsing
        config.useLiteVerseParsing = False
        verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
        config.useLiteVerseParsing = useLiteVerseParsing
        if verses:
            command = "SIDEBYSIDE:::{0}_{1}:::{2}".format(config.mainText, bible, selectedText)
        elif not config.openBibleInMainViewOnly and self.name == "study":
            command = "STUDY:::{0}:::{1} {2}:{3}".format(bible, BibleBooks.eng[str(config.studyB)][0], config.studyC, config.studyV)
        else:
            command = "TEXT:::{0}".format(bible)
        self.parent.parent.textCommandChanged(command, self.name)

    def compareAllVersions(self):
        selectedText = self.selectedTextProcessed()
        if selectedText:
            verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
            if verses:
                command = "COMPARE:::{0}".format(selectedText)
                self.parent.parent.textCommandChanged(command, self.name)
            else:
                self.displayMessage(config.thisTranslation["message_noReference"])
        else:
            self.messageNoSelection()

    def displayVersesInNewWindow(self, selectedText=None):
        #if selectedText is None:
        if not selectedText:
            selectedText = self.selectedTextProcessed()
        if selectedText:
            verses = BibleVerseParser(config.parserStandarisation).extractAllReferences(selectedText, False)
            if verses:
                html = BiblesSqlite().readMultipleVerses(self.getText(), verses)
                self.openPopover(html=html)
            else:
                self.displayMessage(config.thisTranslation["message_noReference"])
        else:
            self.messageNoSelection()

    def displayVersesInBibleWindow(self, selectedText=None):
        #if selectedText is None:
        if not selectedText:
            selectedText = self.selectedTextProcessed()
        if selectedText:
            parser = BibleVerseParser(config.parserStandarisation)
            verses = parser.extractAllReferences(selectedText, False)
            if verses:
                references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verses])
                self.parent.parent.textCommandChanged(references, "main")
            else:
                self.displayMessage(config.thisTranslation["message_noReference"])
            del parser
        else:
            self.messageNoSelection()

    def copyAllReferences(self):
        selectedText = self.selectedTextProcessed()
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

    def openPopover(self, name="popover", html="UniqueBible.app", fullScreen=False, screenNo=-1, forceNewWindow=False):
        # image options
        if config.exportEmbeddedImages:
            html = self.parent.parent.exportAllImages(html)
        if config.clickToOpenImage:
            html = self.parent.parent.addOpenImageAction(html)
        # format html content
        html = self.parent.parent.wrapHtml(html)
        if self.parent.popoverView is None or forceNewWindow:
            self.parent.popoverView = WebEngineViewPopover(self, name, self.name)
            if not fullScreen:
                self.parent.popoverView.setMinimumWidth(config.popoverWindowWidth)
                self.parent.popoverView.setMinimumHeight(config.popoverWindowHeight)
        if config.forceGenerateHtml or len(html) > 1000000:
            outputFile = os.path.join("htmlResources", "popover.html")
            fileObject = open(outputFile, "w", encoding="utf-8")
            fileObject.write(html)
            fileObject.close()
            fullOutputPath = os.path.abspath(outputFile)
            self.parent.popoverView.load(QUrl.fromLocalFile(fullOutputPath))
        else:
            self.parent.popoverView.setHtml(html, config.baseUrl)
        if fullScreen:
            monitor = QDesktopWidget().screenGeometry(screenNo)
            self.parent.popoverView.move(monitor.left(), monitor.top())
            if platform.system() == "Linux":
                # Using self.parent.popoverView.showFullScreen() directly does not work on Linux
                self.parent.popoverView.showMaximized()
                self.parent.popoverView.escKeyPressed()
            else:
                self.parent.popoverView.showFullScreen()
        self.parent.popoverView.show()
        self.parent.parent.bringToForeground(self.parent.popoverView)

    def openPopoverUrl(self, url, name="popover", fullScreen=False, screenNo=-1):
        if self.parent.popoverUrlView is None:
            self.parent.popoverUrlView = WebEngineViewPopover(self, name, self.name)
        self.parent.popoverUrlView.load(url)
        if fullScreen:
            monitor = QDesktopWidget().screenGeometry(screenNo)
            self.parent.popoverUrlView.move(monitor.left(), monitor.top())
            if platform.system() == "Linux":
                # Using self.parent.popoverUrlView.showFullScreen() directly does not work on Linux
                self.parent.popoverUrlView.showMaximized()
                self.parent.popoverUrlView.escKeyPressed()
            else:
                self.parent.popoverUrlView.showFullScreen()
        else:
            self.parent.popoverUrlView.setMinimumWidth(config.popoverWindowWidth)
            self.parent.popoverUrlView.setMinimumHeight(config.popoverWindowHeight)
        self.parent.popoverUrlView.show()
        self.parent.parent.bringToForeground(self.parent.popoverUrlView)

    def closePopover(self):
        if self.parent.popoverView is not None:
            self.parent.popoverView.close()

    def saveHtml(self):
        self.page().toHtml(self.saveHtmlToFile)

    def saveMarkdown(self):
        self.page().toHtml(self.saveMarkdownToFile)

    def savePlainText(self):
        self.page().toPlainText(self.savePlainTextToFile)

    def saveDocx(self):
        self.page().toHtml(self.saveDocxFile)

    def saveDocxFile(self, html):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                "",
                "Word Documents (*.docx)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".docx"
            self.parent.parent.exportHtmlToDocx(html, fileName)
            self.displayMessage(config.thisTranslation["saved"])

    def savePdf(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                "",
                "PDF Files (*.pdf)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".pdf"
            self.page().printToPdf(fileName)
            self.displayMessage(config.thisTranslation["saved"])

    def savePlainTextToFile(self, text):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                "",
                "Plain Text Files (*.txt)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".txt"
            with open(fileName, "w") as fileObj:
                fileObj.write(text)
                fileObj.close()
            self.displayMessage(config.thisTranslation["saved"])

    def saveMarkdownToFile(self, html):
        from markdownify import markdownify
        md = markdownify(html, heading_style=config.markdownifyHeadingStyle)
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                "",
                "Markdown Files (*.md)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".md"
            with open(fileName, "w") as fileObj:
                fileObj.write(md)
                fileObj.close()
            self.displayMessage(config.thisTranslation["saved"])

    def saveHtmlToFile(self, html):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                "",
                "HTML Files (*.html)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".html"
            with open(fileName, "w") as fileObj:
                fileObj.write(html)
                fileObj.close()
            self.displayMessage(config.thisTranslation["saved"])


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

