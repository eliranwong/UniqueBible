from html import entities
from uniquebible.util.Languages import Languages
from uniquebible.util.GoogleCloudTTSVoices import GoogleCloudTTS
from uniquebible import config
import os, platform, re
import uniquebible.shortcut as sc
from functools import partial
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtCore import QUrl
    from PySide6.QtGui import QGuiApplication, QAction
    from PySide6.QtWidgets import QApplication, QMenu, QFileDialog, QInputDialog, QLineEdit, QDialog
    from PySide6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings
    from PySide6.QtWebEngineWidgets import QWebEngineView
    from PySide6.QtPrintSupport import QPrinter, QPrintDialog
else:
    from qtpy.QtCore import Qt
    from qtpy.QtCore import QUrl
    from qtpy.QtGui import QGuiApplication
    from qtpy.QtWidgets import QAction, QApplication, QMenu, QFileDialog, QInputDialog, QLineEdit, QDialog
    from qtpy.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineSettings
    from qtpy.QtPrintSupport import QPrinter, QPrintDialog
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.db.BiblesSqlite import BiblesSqlite
from uniquebible.util.Translator import Translator
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
from uniquebible.gui.SimpleBrowser import SimpleBrowser
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.TextUtil import TextUtil
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.WebtopUtil import WebtopUtil
from uniquebible.util.HBN import HBN
#from uniquebible.util.HebrewTransliteration import HebrewTransliteration
#from uniquebible.util.ShortcutUtil import ShortcutUtil
#from uniquebible.install.module import *


class WebEngineView(QWebEngineView):
    
    def __init__(self, parent, name):
        super().__init__()
        self.parent = parent
        self.name = name
        self.html = None
        self.setPage(WebEnginePage(self))
        self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.page().fullScreenRequested.connect(lambda request: request.accept())
       
        # add context menu (triggered by right-clicking)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.selectionChanged.connect(self.updateContextMenu)
        self.addMenuActions()

        # selection monitoring
        self.selectionChanged.connect(self.selectionMonitoringFeature)

    def load(self, url):
        try:
            filepath = url.toLocalFile()
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='utf8') as fileObj:
                    self.html = fileObj.read()
                self.htmlStored = True
            else:
                self.htmlStored = False
        except:
            self.htmlStored = False
        super().load(url)

    def setHtml(self, html, baseUrl=QUrl()):
        if config.bibleWindowContentTransformers:
            for transformer in config.bibleWindowContentTransformers:
                html = transformer(html)
        self.html = html
        self.htmlStored = True
        super().setHtml(html, baseUrl)

    def selectionMonitoringFeature(self):
        if config.enableSelectionMonitoring:
            # check English definition of selected word
            selectedText = self.selectedText().strip()
            if selectedText in HBN.entries:
                definition = HBN.entries[selectedText]
            else:
                definition = self.getDefinition(selectedText)
                if not definition and hasattr(config, "lemmatizer"):
                    lemma = config.lemmatizer.lemmatize(selectedText)
                    definition = self.getDefinition(lemma)
                    if definition:
                        definition = "<b>{0}</b> - {1}".format(lemma, definition)
                    elif ("Chineseenglishlookup" in config.enabled) and hasattr(config, "cedict"):
                        definition = "<b>{0}</b> - {1}".format(lemma, config.cedict.lookup(lemma))
                else:
                    definition = "<b>{0}</b> - {1}".format(selectedText, definition)
            self.parent.parent.runTextCommand("_info:::{0}".format(definition))

    def getDefinition(self, entry):
        definition = ""
        if hasattr(config, "wordnet"):
            synsets = config.wordnet.synsets(entry)
            if synsets:
                definition = synsets[0].definition()
        return definition

    def displayMessage(self, message):
        self.parent.parent.displayMessage(message)

    def updateDefaultTtsVoice(self):
        display = "{0} {3}{1}{4} | {2}".format(config.thisTranslation["context1_speak"], config.ttsDefaultLangauge, sc.contextDefaultTTS, "" if config.macVoices else "[", "" if config.macVoices else "]")
        self.defaultTTSVoice.setText(display)

    def updateContextMenu(self):
        text = self.getText()
        book = BibleVerseParser(config.parserStandarisation).bcvToVerseReference(self.getBook(), 1, 1)[:-4]
        if self.name == "main":
            self.searchText.setText("{1} {0}".format(text, config.thisTranslation["context1_search"]))
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
        if ("Htmltext" in config.enabled):
            config.pluginContext = self.name
            QGuiApplication.instance().setApplicationName("UniqueBible.app CLI")
            config.pluginContext = ""
        else:
            self.displayMessage("CLI feature is not enabled! \n Install module 'html-text' first, by running 'pip3 install html-text'!")

    def addMenuActions(self):

        # Open Content in

        subMenu1 = QMenu()
        action = QAction(self)
        action.setText(config.thisTranslation["readOnly"])
        action.triggered.connect(self.addToWorkspaceReadOnly)
        subMenu1.addAction(action)
        action = QAction(self)
        action.setText(config.thisTranslation["editable"])
        action.triggered.connect(self.addToWorkspaceEditable)
        subMenu1.addAction(action)

        subMenu2 = QMenu()
        action = QAction(self)
        action.setText(config.thisTranslation["readOnly"])
        action.triggered.connect(self.addTextSelectionToWorkspace)
        subMenu2.addAction(action)
        action = QAction(self)
        action.setText(config.thisTranslation["editable"])
        action.triggered.connect(lambda: self.addTextSelectionToWorkspace(editable=True))
        subMenu2.addAction(action)

        subMenu3 = QMenu()
        action = QAction(self)
        action.setText(config.thisTranslation["readOnly"])
        action.triggered.connect(self.addBibleReferencesInTextSelectionToWorkspace)
        subMenu3.addAction(action)
        action = QAction(self)
        action.setText(config.thisTranslation["editable"])
        action.triggered.connect(lambda: self.addBibleReferencesInTextSelectionToWorkspace(editable=True))
        subMenu3.addAction(action)

        subMenu = QMenu()
        action = QAction(self)
        action.setText(config.thisTranslation["all"])
        action.setMenu(subMenu1)
        subMenu.addAction(action)
        action = QAction(self)
        action.setText(config.thisTranslation["textOnly"])
        action.setMenu(subMenu2)
        subMenu.addAction(action)
        action = QAction(self)
        action.setText(config.thisTranslation["bibleReferencesInTextSelection"])
        action.setMenu(subMenu3)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["addToWorkSpace"])
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
            action.setText(config.thisTranslation["menu1_fullScreen"])
            action.triggered.connect(self.openOnFullScreen)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["note_editor"])
            action.triggered.connect(self.openInNoteEditor)
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
        searchBibleReferences.setText("{0}{1}{2}".format(config.thisTranslation["bar1_menu"], " | " if sc.parseAndOpenBibleReference else "", sc.parseAndOpenBibleReference))
        searchBibleReferences.triggered.connect(self.displayVersesInBibleWindow)
        self.parent.parent.addContextMenuShortcut(partial(self.displayVersesInBibleWindow, activeSelection=True), sc.parseAndOpenBibleReference)
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

        if ("Markdown" in config.enabled):
            action = QAction(self)
            action.setText(config.thisTranslation["markdownFile"])
            action.triggered.connect(self.saveMarkdown)
            subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["pdfFile"])
        action.triggered.connect(self.savePdf)
        subMenu.addAction(action)

        if ("Htmldocx" in config.enabled):
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
        action.setText("{0}{1}{2}".format(config.thisTranslation["context1_search"], " | " if sc.openControlPanelTab3 else "", sc.openControlPanelTab3))
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

        searchBibleName = QAction(self)
        searchBibleName.setText(config.thisTranslation["menu5_names"])
        searchBibleName.triggered.connect(self.searchName)
        subMenu.addAction(searchBibleName)

        searchBibleCharacter = QAction(self)
        searchBibleCharacter.setText(config.thisTranslation["menu5_characters"])
        searchBibleCharacter.triggered.connect(self.searchCharacter)
        subMenu.addAction(searchBibleCharacter)

        searchBibleLocation = QAction(self)
        searchBibleLocation.setText(config.thisTranslation["menu5_locations"])
        searchBibleLocation.triggered.connect(self.searchLocation)
        subMenu.addAction(searchBibleLocation)

        searchBibleParallel = QAction(self)
        searchBibleParallel.setText(config.thisTranslation["bibleHarmonies"])
        searchBibleParallel.triggered.connect(self.searchParallel)
        subMenu.addAction(searchBibleParallel)

        searchBiblePromise = QAction(self)
        searchBiblePromise.setText(config.thisTranslation["biblePromises"])
        searchBiblePromise.triggered.connect(self.searchPromise)
        subMenu.addAction(searchBiblePromise)

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
            action.triggered.connect(partial(self.searchTopic, module))
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
            action.triggered.connect(partial(self.searchDictionary, module))
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
            action.triggered.connect(partial(self.searchEncyclopedia, module))
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

        #action = QAction(self)
        #action.setText(config.thisTranslation["all"])
        #action.triggered.connect(partial(self.searchHebrewGreekLexiconSelected, config.thisTranslation["all"]))
        #subSubMenu.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        subSubMenu.addAction(separator)

        for module in self.parent.parent.lexiconList:
            action = QAction(self)
            action.setText(module)
            action.triggered.connect(partial(self.searchHebrewGreekLexicon, module))
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
            action.triggered.connect(partial(self.searchThirdPartyDictionary, module))
            subSubMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["menu5_3rdDict"])
        action.setMenu(subSubMenu)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["searchMore"])
        action.setMenu(subMenu)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        # End of Search section

        # Google TEXT-TO-SPEECH feature
        if config.isGoogleCloudTTSAvailable or ((not ("OfflineTts" in config.enabled) or config.forceOnlineTts) and ("Gtts" in config.enabled)):

            languageCodes = GoogleCloudTTS.getLanguages() if config.isGoogleCloudTTSAvailable else Languages.gTTSLanguageCodes

            self.defaultTTSVoice = QAction(self)
            self.defaultTTSVoice.triggered.connect(self.googleTextToSpeechLanguage)
            self.parent.parent.addContextMenuShortcut(partial(self.googleTextToSpeechLanguage, "", True), sc.contextDefaultTTS)
            self.addAction(self.defaultTTSVoice)

            ttsMenu = QMenu()
            for language, languageCode in languageCodes.items():
                action = QAction(self)
                action.setText("{0} [{1}]".format(language, languageCode))
                action.triggered.connect(partial(self.googleTextToSpeechLanguage, languageCode))
                ttsMenu.addAction(action)

            tts = QAction(self)
            tts.setText(config.thisTranslation["tts_utility"])
            tts.setMenu(ttsMenu)
            self.addAction(tts)

            # MP3 export
            ttsMenu = QMenu()
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
        elif ("OfflineTts" in config.enabled):

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
                action.setText(item if config.ttsDefaultLangauge.startswith("[") else item.capitalize())
                action.triggered.connect(partial(self.textToSpeechLanguage, languageCode))
                ttsMenu.addAction(action)

            tts = QAction(self)
            tts.setText(config.thisTranslation["tts_utility"])
            tts.setMenu(ttsMenu)
            self.addAction(tts)

            # Support *.aiff and *.mp3 export on macOS
            if config.ttsDefaultLangauge.startswith("["):
                ttsMenu = QMenu()
                languageCodes = list(languages.keys())
                items = [languages[code][1] for code in languageCodes]
                for index, item in enumerate(items):
                    languageCode = languageCodes[index]
                    action = QAction(self)
                    action.setText(item)
                    action.triggered.connect(partial(self.exportAiffOnMacOS, languageCode))
                    ttsMenu.addAction(action)

                tts = QAction(self)
                tts.setText("{0} AIFF".format(config.thisTranslation["note_saveAs"]))
                tts.setMenu(ttsMenu)
                self.addAction(tts)

                if ("Audioconverter" in config.enabled) and WebtopUtil.isPackageInstalled("ffmpeg"):
                    ttsMenu = QMenu()
                    languageCodes = list(languages.keys())
                    items = [languages[code][1] for code in languageCodes]
                    for index, item in enumerate(items):
                        languageCode = languageCodes[index]
                        action = QAction(self)
                        action.setText(item)
                        action.triggered.connect(partial(self.exportMp3OnMacOS, languageCode))
                        ttsMenu.addAction(action)

                    tts = QAction(self)
                    tts.setText("{0} MP3".format(config.thisTranslation["note_saveAs"]))
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
            for ff in (config.packageDir, config.ubaUserDir):
                for plugin in FileUtil.fileNamesWithoutExtension(os.path.join(ff, "plugins", "context"), "py"):
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
        action.triggered.connect(lambda: self.openSimpleBrowser("https://github.com/eliranwong/UniqueBible/wiki/Context-Menu"))
        self.addAction(action)

    def openSimpleBrowser(self, urlString):
        simpleBrowser = SimpleBrowser(self.parent.parent)
        simpleBrowser.setUrl(QUrl(urlString))
        simpleBrowser.show()

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
            text, ok = QInputDialog.getText(self.parent.parent, "Unique Bible App",
                    config.thisTranslation["enter_text_here"], QLineEdit.Normal,
                    "")
            if ok and text:
                selectedText = text
        return selectedText

    def runPlugin(self, fileName, selectedText=None, activeSelection=False):
        #if selectedText is None:
        # Note: Tested in Arch Linux using pyqt5, selectedText = False.  Therefore, the line above does not work.
        if not selectedText:
            selectedText = self.selectedTextProcessed(activeSelection)
        config.contextSource = self
        config.pluginContext = selectedText
        script = os.path.join(config.packageDir, "plugins", "context", "{0}.py".format(fileName))
        if os.path.isfile(script):
            self.parent.parent.execPythonFile(script)
        script = os.path.join(config.ubaUserDir, "plugins", "context", "{0}.py".format(fileName))
        if os.path.isfile(script):
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
            self.page().triggerAction(QWebEnginePage.Copy)

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
        if self.htmlStored:
            self.copyHtmlToClipboard(self.html)
        else:
            self.page().toHtml(self.copyHtmlToClipboard)

    def copyPlainText(self):
        self.page().toPlainText(self.copyHtmlToClipboard)

    def copyHtmlToClipboard(self, text):
        QApplication.clipboard().setText(text)

    # Add to Workspace
    def addToWorkspaceReadOnly(self):
        if self.htmlStored:
            self.addToWorkspaceReadOnlyAction(self.html)
        else:
            self.page().toHtml(self.addToWorkspaceReadOnlyAction)

    def addToWorkspaceEditable(self):
        if self.htmlStored:
            self.addToWorkspaceEditableAction(self.html)
        else:
            self.page().toHtml(self.addToWorkspaceEditableAction)

    def addToWorkspaceReadOnlyAction(self, html):
        windowTitle = ""
        if self.name == "main":
            windowTitle = self.parent.parent.mainView.tabText(self.parent.parent.mainView.currentIndex()).strip()
        elif self.name == "study":
            windowTitle = self.parent.parent.studyView.tabText(self.parent.parent.studyView.currentIndex()).strip()
        config.mainWindow.ws.addHtmlContent(html, False, windowTitle)

    def addToWorkspaceEditableAction(self, html):
        windowTitle = ""
        if self.name == "main":
            windowTitle = self.parent.parent.mainView.tabText(self.parent.parent.mainView.currentIndex()).strip()
        elif self.name == "study":
            windowTitle = self.parent.parent.studyView.tabText(self.parent.parent.studyView.currentIndex()).strip()
        config.mainWindow.ws.addHtmlContent(html, True, windowTitle)

    def addTextSelectionToWorkspace(self, selectedText=None, editable=False):
        if not selectedText:
            selectedText = self.selectedTextProcessed()
        if selectedText:
            self.parent.parent.addTextSelectionToWorkspace(selectedText, editable)
        else:
            self.messageNoSelection()

    def addBibleReferencesInTextSelectionToWorkspace(self, selectedText=None, editable=False):
        if not selectedText:
            selectedText = self.selectedTextProcessed()
        if selectedText:
            self.parent.parent.addBibleReferencesInTextSelectionToWorkspace(selectedText, editable)
        else:
            self.messageNoSelection()

    # Open in Note Editor
    def openInNoteEditor(self):
        if self.htmlStored:
            config.mainWindow.displayContentInNoteEditor(self.html)
        else:
            self.page().toHtml(config.mainWindow.displayContentInNoteEditor)

    # Instant highligh feature
    def instantHighlight(self, selectionMonitoring=False):
        if selectionMonitoring:
            selectedText = self.selectedText().strip()
            self.findText(selectedText, QWebEnginePage.FindFlags())
        else:
            selectedText = self.selectedTextProcessed()
            self.findText(selectedText, QWebEnginePage.FindFlags(), self.checkIfTextIsFound)

    def checkIfTextIsFound(self, found):
        if not found:
            self.displayMessage(config.thisTranslation["notFound"])

    def removeInstantHighlight(self):
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
            self.openSimpleBrowser(url)

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
        if ("OfflineTts" in config.enabled):
            selectedText = self.selectedTextProcessed(activeSelection)
            if not selectedText:
                self.messageNoSelection()
            elif ("Langdetect" in config.enabled) and config.useLangDetectOnTts:
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

    def exportAiffOnMacOS(self, language):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            # Ask for a filename
            options = QFileDialog.Options()
            fileName, *_ = QFileDialog.getSaveFileName(self,
                    config.thisTranslation["note_saveAs"],
                    "music",
                    "AIFF Files (*.aiff)", "", options)
            if fileName:
                if not fileName.endswith(".aiff"):
                    fileName = fileName + ".aiff"
                # Save aiff file
                try:
                    if language.startswith("[el_GR]"):
                        selectedText = TextUtil.removeVowelAccent(selectedText)
                    with open('temp/temp.txt', 'w') as file:
                        file.write(selectedText)
                    voice = re.sub("^\[.*?\] ", "", language)
                    os.system(f"say -r {config.macOSttsSpeed} -v {voice} -o {fileName} -f temp/temp.txt")
                except:
                    self.displayMessage(config.thisTranslation["message_fail"])

    def exportMp3OnMacOS(self, language):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            # Ask for a filename
            options = QFileDialog.Options()
            fileName, *_ = QFileDialog.getSaveFileName(self,
                    config.thisTranslation["note_saveAs"],
                    "music",
                    "MP3 Files (*.mp3)", "", options)
            if fileName:
                if not fileName.endswith(".mp3"):
                    fileName = fileName + ".mp3"
                # Save aiff file first and convert it to mp3
                aiffFilename = re.sub("\.mp3$", ".aiff", os.path.basename(fileName))
                outputFolder = os.path.dirname(fileName)
                try:
                    if language.startswith("[el_GR]"):
                        selectedText = TextUtil.removeVowelAccent(selectedText)
                    with open('temp/temp.txt', 'w') as file:
                        file.write(selectedText)
                    voice = re.sub("^\[.*?\] ", "", language)
                    try:
                        os.system("rm -rf temp/*.aiff")
                    except:
                        pass
                    os.system(f"say -r {config.macOSttsSpeed} -v {voice} -o temp/{aiffFilename} -f temp/temp.txt")
                    os.system(f"audioconvert convert temp/ {outputFolder}/")
                except:
                    self.displayMessage(config.thisTranslation["message_fail"])

    def textToSpeechLanguage(self, language, activeSelection=False, selectedText=""):
        if ("OfflineTts" in config.enabled):
            if not selectedText:
                selectedText = self.selectedTextProcessed(activeSelection)
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

    def googleTextToSpeechLanguage(self, language="", activeSelection=False, selectedText=""):
        if not language:
            language = config.ttsDefaultLangauge
        if config.isGoogleCloudTTSAvailable and language == "en":
            language = "en-GB"
        if not selectedText:
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
        elif ("OnlineTts" in config.enabled):
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
            searchCommand = "COUNT:::{0}:::{1}".format(self.getText() if text is None or not text else text, selectedText)
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
            searchCommand = "COUNT:::{0}:::{1}".format(config.favouriteBible, selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchSelectedTextOriginal(self):
        selectedText = self.selectedTextProcessed()
        if not selectedText:
            self.messageNoSelection()
        else:
            searchCommand = "COUNT:::{0}:::{1}".format("MOB", selectedText)
            self.parent.parent.textCommandChanged(searchCommand, self.name)

    def searchHebrewGreekLexicon(self, module=""):
#        selectedText = self.selectedTextProcessed()
#        if not selectedText:
#            self.messageNoSelection()
#        else:
#            searchCommand = "LEXICON:::{0}".format(selectedText)
#            self.parent.parent.textCommandChanged(searchCommand, self.name)
        if module and not module == config.lexicon:
            config.lexiconEntry = ""
            config.lexicon = module
        config.pluginContext = self.name
        self.parent.parent.runPlugin("Bible Lexicons")
        config.pluginContext = ""

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
        #self.searchResource("EXLBP")
        config.pluginContext = self.name
        self.parent.parent.runPlugin("Bible Characters")
        config.pluginContext = ""

    def searchName(self):
        #self.searchResource("HBN")
        config.dataset = "Bible Names"
        config.pluginContext = self.name
        self.parent.parent.runPlugin("Bible_Data")
        config.pluginContext = ""

    def searchPromise(self):
        config.pluginContext = self.name
        self.parent.parent.runPlugin("Bible Promises")
        config.pluginContext = ""

    def searchParallel(self):
        config.pluginContext = self.name
        self.parent.parent.runPlugin("Bible Parallels")
        config.pluginContext = ""

    def searchLocation(self):
        #self.searchResource("EXLBL")
        config.pluginContext = self.name
        self.parent.parent.runPlugin("Bible Locations")
        config.pluginContext = ""

    def searchTopic(self, module=""):
        #self.searchResource(config.topic)
        if module and not module == config.topic:
            config.topicEntry = ""
            config.topic = module
        config.pluginContext = self.name
        self.parent.parent.runPlugin("Bible Topics")
        config.pluginContext = ""

    def searchDictionary(self, module=""):
        #self.searchResource(config.dictionary)
        if module and not module == config.dictionary:
            config.dictionaryEntry = ""
            config.dictionary = module
        config.pluginContext = self.name
        self.parent.parent.runPlugin("Bible Dictionaries")
        config.pluginContext = ""

    def searchEncyclopedia(self, module=""):
        #self.searchResource(config.encyclopedia)
        if module and not module == config.encyclopedia:
            config.encyclopediaEntry = ""
            config.encyclopedia = module
        config.pluginContext = self.name
        self.parent.parent.runPlugin("Bible Encyclopedia")
        config.pluginContext = ""

    def searchThirdPartyDictionary(self, module=""):
#        selectedText = self.selectedTextProcessed()
#        if not selectedText:
#            self.messageNoSelection()
#        else:
#            searchCommand = "SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(config.thirdDictionary, selectedText)
#            self.parent.parent.textCommandChanged(searchCommand, self.name)
        if module and not module == config.thirdDictionary:
            config.thirdDictionaryEntry = ""
            config.thirdDictionary = module
        config.pluginContext = self.name
        self.parent.parent.runPlugin("Third Party Dictionaries")
        config.pluginContext = ""

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
            if self.htmlStored:
                self.openNewWindow(self.html)
            else:
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
            if self.htmlStored:
                self.openNewWindow(self.html, True)
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
            command = "STUDY:::{0}:::{1} {2}:{3}".format(bible, BibleBooks.abbrev["eng"][str(config.studyB)][0], config.studyC, config.studyV)
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
            command = "STUDY:::{0}:::{1} {2}:{3}".format(bible, BibleBooks.abbrev["eng"][str(config.studyB)][0], config.studyC, config.studyV)
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
            command = "STUDY:::{0}:::{1} {2}:{3}".format(bible, BibleBooks.abbrev["eng"][str(config.studyB)][0], config.studyC, config.studyV)
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
                self.openPopover(html=self.parent.parent.wrapHtml(html))
            else:
                self.displayMessage(config.thisTranslation["message_noReference"])
        else:
            self.messageNoSelection()

    def displayVersesInBibleWindow(self, selectedText=None, activeSelection=False):
        #if selectedText is None:
        if not selectedText:
            selectedText = self.selectedTextProcessed(activeSelection)
        if selectedText:
            parser = BibleVerseParser(config.parserStandarisation)
            verses = parser.extractAllReferences(selectedText, False)
            if verses:
                references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verses])
                self.parent.parent.textCommandChanged(references, "main")
            else:
                self.displayMessage(config.thisTranslation["message_noReference"])
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
        #html = self.parent.parent.wrapHtml(html)
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
            #monitor = QDesktopWidget().screenGeometry(screenNo)
            monitor = QGuiApplication.screens()[screenNo].availableGeometry()
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
            #monitor = QDesktopWidget().screenGeometry(screenNo)
            monitor = QGuiApplication.screens()[screenNo].availableGeometry()
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
        if self.htmlStored:
            self.saveHtmlToFile(self.html)
        else:
            self.page().toHtml(self.saveHtmlToFile)

    def saveMarkdown(self):
        if self.htmlStored:
            self.saveMarkdownToFile(self.html)
        else:
            self.page().toHtml(self.saveMarkdownToFile)

    def savePlainText(self):
        self.page().toPlainText(self.savePlainTextToFile)

    def saveDocx(self):
        if self.htmlStored:
            self.saveDocxFile(self.html)
        else:
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

    def printContent(self):
        printer = QPrinter()
        myPrintDialog = QPrintDialog(printer, self)
        if myPrintDialog.exec_() == QDialog.Accepted:
            return self.print(printer)


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

