# coding=utf-8
import glob, pprint, traceback, pydoc, threading, asyncio, shutil
import os, re, webbrowser, platform, zipfile, subprocess, logging
from uniquebible import config
from prompt_toolkit.input import create_input
from prompt_toolkit.keys import Keys
from datetime import date
from openai import OpenAI

from uniquebible.util.DatafileLocation import DatafileLocation
from uniquebible.db.StatisticsWordsSqlite import StatisticsWordsSqlite
from uniquebible.util.VlcUtil import VlcUtil
from uniquebible.util.exlbl import allLocations, tc_location_names, sc_location_names
from uniquebible.util.PluginEventHandler import PluginEventHandler
from uniquebible.util.WebtopUtil import WebtopUtil
from uniquebible.util.CatalogUtil import CatalogUtil
from uniquebible.util.GitHubRepoInfo import GitHubRepoInfo
from uniquebible.util.HtmlGeneratorUtil import HtmlGeneratorUtil
from uniquebible.util.TextUtil import TextUtil
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.LexicalData import LexicalData
from uniquebible.util.readings import allDays
from functools import partial
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.db.AGBTSData import AGBTSData
from uniquebible.db.BiblesSqlite import BiblesSqlite, Bible, ClauseData
from uniquebible.db.ToolsSqlite import CrossReferenceSqlite, CollectionsSqlite, ImageSqlite, IndexesSqlite, EncyclopediaData, \
    DictionaryData, ExlbData, SearchSqlite, Commentary, VerseData, WordData, BookData, \
    Lexicon, LexiconData
from uniquebible.util.ThirdParty import ThirdPartyDictionary
from uniquebible.util.HebrewTransliteration import HebrewTransliteration
from uniquebible.db.NoteSqlite import NoteSqlite
from uniquebible.util.Translator import Translator
from uniquebible.db.Highlight import Highlight
from uniquebible.util.TtsLanguages import TtsLanguages
from uniquebible.db.BiblesSqlite import MorphologySqlite
from uniquebible.db.JournalSqlite import JournalSqlite

#from uniquebible.gui.Downloader import Downloader
from uniquebible.install.module import *
from uniquebible.util.DatafileLocation import DatafileLocation

if config.qtLibrary == "pyside6":
    try:
        #QtTextToSpeech is currently not in PySide6 pip3 package
        #ModuleNotFoundError: No module named 'PySide6.QtTextToSpeech'
        from PySide6.QtTextToSpeech import QTextToSpeech
    except:
        pass
else:
    try:
        # Note: qtpy.QtTextToSpeech is not found!
        from PySide2.QtTextToSpeech import QTextToSpeech
    except:
        try:
            from PyQt5.QtTextToSpeech import QTextToSpeech
        except:
            pass


class TextCommandParser:

    last_lexicon_entry = ''
    last_text_search = ''

    def __init__(self, parent):
        self.parent = parent
        self.logger = logging.getLogger('uba')
        self.lastKeyword = None
        self.cliTtsProcess = None
        self.qtTtsEngine = None
        self.llamaIndexUpdated = False
        self.locationMap = {exlbl_entry: (name[0].upper(), name, float(latitude), float(longitude)) for exlbl_entry, name, latitude, longitude in allLocations}

        self.interpreters = {
            "bible": (self.textBible, """
            # [KEYWORD] BIBLE
            # Feature - Open a bible chapter or multiples verses on main or study view.
            # Usage - BIBLE:::[BIBLE_VERSION]:::[BIBLE_REFERENCE(S)]
            # Remarks:
            # 1) The bible version last opened on main view is opened by default if "[BIBLE_VERSION]:::" or "BIBLE:::[BIBLE_VERSION]:::" is omitted.
            # 2) If "BIBLE:::" command is called from manual entry via command field or a link within the content on main view, bible text is opened on main view.
            # 3) If "BIBLE:::" command is called from a link within the content on study view and "Bible Display on Study View" is enabled, bible text is opened on study view.
            # 4) If "BIBLE:::" command is called from a link within the content on study view and "Bible Display on Study View" is disabled, bible text is opened on main view.
            # 5) Common abbreviations of bible references are supported.
            # Examples:
            # e.g. John 3:16
            # e.g. Jn 3:16; Rm 5:8; Deu 6:4
            # e.g. BIBLE:::John 3:16
            # e.g. BIBLE:::Jn 3:16; Rm 5:8; Deu 6:4
            # e.g. BIBLE:::KJV:::John 3:16
            # e.g. BIBLE:::KJV:::Jn 3:16; Rm 5:8; Deu 6:4"""),
            "chapter": (self.textFormattedChapter, """
            # [KEYWORD] CHAPTER
            # Feature - Open bible versions of a single chapter.
            # Usage - CHAPTER:::[BIBLE_VERSION(S)]:::[BIBLE_CHAPTER]"""),
            "main": (self.textMain, """
            # [KEYWORD] MAIN
            # Feature - Open a bible chapter or multiples verses on main view.
            # Usage - MAIN:::[BIBLE_VERSION]:::[BIBLE_REFERENCE(S)]
            # Remarks:
            # 1) The bible version last opened on main view is opened by default if "[BIBLE_VERSION]:::" or "MAIN:::[BIBLE_VERSION]:::" is omitted.
            # 2) Common abbreviations of bible references are supported.
            # Examples:
            # e.g. John 3:16
            # e.g. Jn 3:16; Rm 5:8; Deu 6:4
            # e.g. MAIN:::John 3:16
            # e.g. MAIN:::Jn 3:16; Rm 5:8; Deu 6:4
            # e.g. MAIN:::KJV:::John 3:16
            # e.g. MAIN:::KJV:::Jn 3:16; Rm 5:8; Deu 6:4"""),
            "study": (self.textStudy, """
            # [KEYWORD] STUDY
            # Feature - Open a bible chapter or multiples verses on study / main view.
            # Usage - STUDY:::[BIBLE_VERSION]:::[BIBLE_REFERENCE(S)]
            # Remarks:
            # 1) The bible version last opened on study view is opened by default if "[BIBLE_VERSION]:::" is omitted.
            # 2) If "Bible Display on Study View" is enabled, bible text is opened on study view.
            # 3) If "Bible Display on Study View" is disabled, bible text is opened on main view.
            # 4) Common abbreviations of bible references are supported.
            # Examples:
            # e.g. STUDY:::John 3:16
            # e.g. STUDY:::Jn 3:16; Rm 5:8; Deu 6:4
            # e.g. STUDY:::KJV:::John 3:16
            # e.g. STUDY:::KJV:::Jn 3:16; Rm 5:8; Deu 6:4"""),
            "text": (self.textText, """
            # [KEYWORD] TEXT
            # Feature - Change the bible version of the last opened passage on main view.
            # Usage - TEXT:::[BIBLE_VERSION]
            # e.g. TEXT:::KJV
            # e.g. TEXT:::NET"""),
            "studytext": (self.textStudyText, """
            # [KEYWORD] STUDYTEXT
            # Feature - Change the bible version of the last opened passage on study view.
            # Usage - STUDYTEXT:::[BIBLE_VERSION]
            # e.g. STUDYTEXT:::KJV
            # e.g. STUDYTEXT:::NET"""),
            "compare": (self.textCompare, """
            # [KEYWORD] COMPARE
            # Feature - Compare bible versions of a single or multiple references.
            # Usage - COMPARE:::[BIBLE_VERSION(S)]:::[BIBLE_REFERENCE(S)]
            # Remarks:
            # 1) All installed bible versions are opened for comparison if "[BIBLE_VERSION(S)]:::" is omitted.
            # 2) Multiple bible versions for comparison are separated by "_".
            # 3) If a single reference is entered and bible versions for comparison are specified, verses of the same chapter of the entered reference are opened.
            # 4) Muliple verse references are supported for comparison.
            # e.g. COMPARE:::John 3:16
            # e.g. COMPARE:::KJV_NET_CUV:::John 3:16
            # e.g. COMPARE:::KJV_NET_CUV:::John 3:16; Rm 5:8"""),
            "comparechapter": (self.textCompareChapter, """
            # [KEYWORD] COMPARECHAPTER
            # Feature - Compare bible versions of a single chapter.
            # Usage - COMPARECHAPTER:::[BIBLE_VERSION(S)]:::[BIBLE_CHAPTER]"""),
            "sidebyside": (self.textCompareSideBySide, """
            # [KEYWORD] SIDEBYSIDE
            # Feature - Compare bible versions side by side
            # Usage - SIDEBYSIDE:::[BIBLE_VERSION(S)]:::[BIBLE_REFERENCE]
            # Remarks: Multiple bible versions for comparison are separated by "_"."""),
            "difference": (self.textDiff, """
            # [KEYWORD] DIFFERENCE
            # Feature - same as [KEYWORD] DIFF
            # Usage - DIFFERENCE:::[BIBLE_VERSION(S)]:::[BIBLE_REFERENCE(S)]
            # Remarks:
            # 1) Last-opened bible version is always displayed at the top for comparison.
            # 2) All installed bible versions are opened for comparison if "[BIBLE_VERSION(S)]:::" is omitted.
            # 3) Multiple bible versions for comparison are separated by "_".
            # 4) Muliple verse references are supported for comparison.
            # e.g. DIFFERENCE:::Joh 3:16
            # e.g. DIFFERENCE:::KJV_ASV_WEB:::Joh 3:16; Rm 5:8"""),
            "parallel": (self.textParallel, """
            # [KEYWORD] PARALLEL
            # Feature - Display bible versions of the same chapter in parallel columns.
            # Usage - PARALLEL:::[BIBLE_VERSION(S)]:::[BIBLE_REFERENCE]
            # Remarks:
            # 1) Multiple bible versions for comparison are separated by "_".
            # 2) If a single reference is entered and bible versions for comparison are specified, verses of the same chapter of the entered reference are opened.
            # 3) Muliple verse references are supported for comparison.
            # 4) Only the bible version last opened on main view is opened if "[BIBLE_VERSION(S)]:::" is omitted.
            # e.g. PARALLEL:::NIV_CCB_CEB:::John 3:16
            # e.g. PARALLEL:::NIV_CCB_CEB:::John 3:16; Rm 5:8"""),
            "passages": (self.textPassages, """
            # [KEYWORD] PASSAGES
            # Feature - Display different bible passages of the same bible version in parallel columns. It is created for studying similar passages.
            # Usage - PASSAGES:::[BIBLE_VERSION]:::[BIBLE_REFERENCE]
            # Remarks:
            # 1) Only the bible version last opened on main view is opened if "[BIBLE_VERSION(S)]:::" is omitted.
            # 2) Only the first bible version specified in the command is taken, even multiple bible versions are entered and separated by "_".
            # 3) Users can read an additional version by setting config.addFavouriteToMultiRef as True.
            # 4) Book abbreviations and ranges of verses are supported for bible references.
            # 5) If a chapter reference is entered, only verse 1 of the chapter specified is displayed.
            # e.g. PASSAGES:::Mat 3:13-17; Mark 1:9-11; Luk 3:21-23
            # e.g. PASSAGES:::KJV:::Mat 3:13-17; Mark 1:9-11; Luk 3:21-23"""),
            "outline": (self.textBookOutline, """
            # [KEYWORD] OUTLINE
            # Feature - Display all subheadings in a bible book
            # Usage - OUTLINE:::[BIBLE_BOOK]
            # e.g. outline:::John"""),
            "overview": (self.textChapterOverview, """
            # [KEYWORD] OVERVIEW
            # Feature - Display overview of a bible chapter
            # Usage - OVERVIEW:::[BIBLE_CHAPTER]
            # e.g. overview:::John 3"""),
            "summary": (self.textChapterSummary, """
            # [KEYWORD] SUMMARY
            # Feature - Display summary of a bible chapter
            # Usage - SUMMARY:::[BIBLE_CHAPTER]
            # e.g. summary:::John 3"""),
            "concordance": (self.textConcordance, """
            # [KEYWORD] CONCORDANCE
            # Feature - Search a Strong's number bible
            # Usage - CONCORDANCE:::[BIBLE_VERSION(S)]:::[STRONG_NUMBER]
            # Assigning "ALL" as "BIBLE_VERSION(S)" to search all installed Strong's number bibles.
            # e.g. CONCORDANCE:::KJVx:::G3087
            # e.g. CONCORDANCE:::ESVx_KJVx_NIVx_WEBx:::G3087
            # e.g. CONCORDANCE:::ALL:::G3087"""),
            "count": (self.textCountSearch, """
            # [KEYWORD] COUNT
            # Feature - Count occurrences of a string in bible books.
            # Usage - COUNT:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]:::[BIBLE_BOOKS]
            # To search for a string in a bible
            # e.g. COUNT:::KJV:::love
            # To search with a wild card character "%"
            # e.g. COUNT:::KJV:::Christ%Jesus
            # To search multiple bibles, separate versions with a character "_"
            # e.g. COUNT:::KJV_WEB:::love
            # e.g. COUNT:::KJV_WEB:::Christ%Jesus
            # To search specific books of bible
            # e.g. COUNT:::KJV:::love:::Matt-John, 1Cor, Rev
            # e.g. COUNT:::KJV:::temple:::OT
            """),
            "search": (self.textSearchBasic, """
            # [KEYWORD] SEARCH
            # Feature - Search bible / bibles for a string
            # Usage - SEARCH:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]:::[BIBLE_BOOKS]
            # SEARCH::: is different from COUNT::: that COUNT::: shows the number of hits in individual books only whereas SEARCH::: display all texts of the result.
            # e.g. SEARCH:::KJV:::love
            # To work on multiple bibles, separate bible versions with a character "_":
            # e.g. SEARCH:::KJV_WEB:::love
            # To search specific books of bible
            # e.g. SEARCH:::KJV:::love:::Matt-John, 1Cor, Rev
            # e.g. SEARCH:::KJV:::temple:::OT
            """),
            "searchreference": (self.textSearchReference, """
            # [KEYWORD] SEARCHREFERENCE"""),
            "searchtnk": (self.textSearchOT, """
            # [KEYWORD] SEARCHTNK
            # Feature - Search Tanakh ONLY
            # Usage - SEARCHTNK:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]
            # e.g. SEARCHTNK:::KJV_WEB:::love
            # e.g. SEARCHTNK:::KJV_WEB:::God%kind"""),
            "searchot": (self.textSearchOT, """
            # [KEYWORD] SEARCHOT
            # Feature - Search O.T. ONLY
            # Usage - SEARCHOT:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]
            # e.g. SEARCHOT:::KJV_WEB:::love
            # e.g. SEARCHOT:::KJV_WEB:::God%kind"""),
            "searchnt": (self.textSearchNT, """
            # [KEYWORD] SEARCHNT
            # Feature - Search N.T. ONLY
            # Usage - SEARCHNT:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]
            # e.g. SEARCHNT:::KJV_WEB:::love
            # e.g. SEARCHNT:::KJV_WEB:::Christ%Jesus"""),
            "regexsearch": (self.textSearchRegex, """
            # [KEYWORD] REGEXSEARCH
            # Feature - Search bible / bibles with regular expression
            # Usage - REGEXSEARCH:::[BIBLE_VERSION(S)]:::[REGEX_PATTERN]:::[BIBLE_BOOKS]
            # e.g. REGEXSEARCH:::KJV:::God.*?heaven
            # To search specific books of bible
            # e.g. REGEXSEARCH:::KJV:::God.*?love:::Matt-John, 1Cor, Rev
            # e.g. REGEXSEARCH:::KJV:::God.*?temple:::OT
            """),
            "advancedsearch": (self.textSearchAdvanced, """
            # [KEYWORD] ADVANCEDSEARCH
            # Feature - Search bible / bibles with a sql string
            # Usage - ADVANCEDSEARCH:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]:::[BIBLE_BOOKS]
            # e.g. ADVANCEDSEARCH:::KJV:::Book = 1 AND Scripture LIKE '%love%'
            # To work on multiple bibles, separate bible versions with a character "_":
            # e.g. ADVANCEDSEARCH:::KJV_WEB:::Book = 1 AND Scripture LIKE '%love%'"""),
            "andsearch": (self.textAndSearch, """
            # [KEYWORD] ANDSEARCH
            # Feature - Search bible / bibles for combinations of words without taking order into consideration
            # Usage - ANDSEARCH:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]:::[BIBLE_BOOKS]
            # Words are separated by a character "|" in a search string.
            # e.g. ANDSEARCH:::KJV:::love|Jesus
            # alias of, e.g. ADVANCEDSEARCH:::KJV:::Scripture LIKE "%love%" AND Scripture LIKE "%Jesus%" """),
            "orsearch": (self.textOrSearch, """
            # [KEYWORD] ORSEARCH
            # Feature - Search bible / bibles for verses containing at least on of the words given in a string
            # Usage - ORSEARCH:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]:::[BIBLE_BOOKS]
            # Words are separated by a character "|" in a search string.
            # e.g. ORSEARCH:::KJV:::love|Jesus
            # alias of, e.g. ADVANCEDSEARCH:::KJV:::Scripture LIKE "%love%" OR Scripture LIKE "%Jesus%" """),
            "searchhighlight": (self.highlightSearch, """
            # [KEYWORD] SEARCHHIGHLIGHT
            # Feature - Search for highlight
            # Usage - SEARCHHIGHLIGHT:::[COLOR]:::[BIBLE_REFERENCE]
            # To search entire Bible for all highlight
            # e.g. SEARCHHIGHLIGHT:::all
            # To search entire Bible for yellow highlight
            # e.g. SEARCHHIGHLIGHT:::yellow:::all
            # e.g. SEARCHHIGHLIGHT:::yellow
            # To search New Testament for blue highlight
            # e.g. SEARCHHIGHLIGHT:::blue:::nt
            # To search Old Testament for blue highlight
            # e.g. SEARCHHIGHLIGHT:::blue:::ot
            # To search Matthew for blue highlight
            # e.g. SEARCHHIGHLIGHT:::hl2:::Matthew
            # To search James for underline highlight
            # e.g. SEARCHHIGHLIGHT:::underline:::James
            # e.g. SEARCHHIGHLIGHT:::ul1:::James"""),
            "index": (self.textIndex, """
            # [KEYWORD] INDEX
            # e.g. INDEX:::Gen 1:1"""),
            "chapterindex": (self.textChapterIndex, """
            # [KEYWORD] CHAPTERINDEX
            # e.g. CHAPTERINDEX:::Gen 1"""),
            "data": (self.textData, """
            # [KEYWORD] DATA
            # Feature - Display a data list into a table
            # Usage - DATA:::[menu_plugin_bible_data_filename]
            # e.g. DATA:::Bible Chronology"""),
            "day": (self.textDay, """
            # [KEYWORD] DAY
            # Feature - Display 365 Day Bible Reading Content
            # Usage - DAY:::[BIBLE_VERSION]:::[day_number]
            # e.g. DAY:::1
            # e.g. DAY:::NET:::1"""),
            "dayaudio": (self.textDayAudio, """
            # [KEYWORD] DAYAUDIO
            # Feature - Open 365 Day Bible Reading Audio
            # Usage - DAYAUDIO:::[BIBLE_VERSION]:::[day_number]
            # e.g. DAYAUDIO:::1
            # e.g. DAYAUDIO:::NET:::1"""),
            "dayaudioplus": (self.textDayAudioPlus, """
            # [KEYWORD] DAYAUDIOPLUS
            # Feature - Open 365 Day Bible Reading Audio in two translations
            # Usage - DAYAUDIOPLUS:::[BIBLE_VERSION(S)]:::[day_number]
            # e.g. DAYAUDIOPLUS:::1
            # e.g. DAYAUDIOPLUS:::NET:::1"""),
            "map": (self.textMap, """
            # [KEYWORD] MAP
            # Feature - Open a Google map with bible locations pinned
            # Usage - MAP:::[BIBLE_REFERENCE]
            # e.g. MAP:::Act 15:36-18:22"""),
            "locations": (self.textLocations, """
            # [KEYWORD] LOCATIONS
            # Feature - Customise a Google map with bible locations pinned; locations separated by |
            # Usage - LOCATIONS:::[BIBLE_LOCATIONS]
            # e.g. LOCATIONS:::BL634|BL636"""),
            "crossreference": (self.textCrossReference, """
            # [KEYWORD] CROSSREFERENCE
            # e.g. CROSSREFERENCE:::Gen 1:1
            # e.g. CROSSREFERENCE:::[BIBLE_VERSION]:::Rev 1:1
            # e.g. CROSSREFERENCE:::[Cross reference file]:::Rev 1:1
            """),
            "tske": (self.tske, """
            # [KEYWORD] TSKE
            # e.g. TSKE:::Gen 1:1
            # e.g. TSKE:::NET:::Gen 1:1"""),
            "commentary": (self.textCommentary, """
            # [KEYWORD] COMMENTARY
            # Feature - Open commentary of a bible reference.
            # Usage - COMMENTARY:::[COMMENTARY_MODULE]:::[BIBLE_REFERENCE]
            # Remarks:
            # 1) The last opened commentary module is opened if "[COMMENTARY_MODULE]:::" is omitted.
            # 2) Commentary is opened on study view.
            # e.g. COMMENTARY:::John 3:16
            # e.g. COMMENTARY:::CBSC:::John 3:16"""),
            "commentary2": (self.textCommentary2, """
            # [KEYWORD] COMMENTARY2
            # Feature - Open commentary of a bible reference.
            # Usage - COMMENTARY2:::[BOOK_NO].[CHAPTER_NO].[VERSE_NO]
            # Usage - COMMENTARY2:::[COMMENTARY_MODULE]:::[BOOK_NO].[CHAPTER_NO].[VERSE_NO]
            # Remarks:
            # 1) The last opened commentary module is opened if "[COMMENTARY_MODULE]:::" is omitted.
            # 2) Commentary is opened on study view.
            # 3) Bible reference used with "COMMENTARY2:::" is formatted as [BOOK_NUMBER.CHAPTER_NUMBER.VERSE_NUMBER], see examples below.
            # e.g. COMMENTARY2:::43.3.16
            # e.g. COMMENTARY2:::CBSC:::43.3.16"""),
            "distinctinterlinear": (self.distinctInterlinear, """
            # [KEYWORD] DISTINCTINTERLINEAR
            # e.g. DISTINCTINTERLINEAR:::G746"""),
            "distincttranslation": (self.distinctTranslation, """
            # [KEYWORD] DISTINCTTRANSLATION
            # e.g. DISTINCTTRANSLATION:::G746"""),
            "combo": (self.textCombo, """
            # [KEYWORD] COMBO
            # e.g. COMBO:::Gen 1:1"""),
            "translation": (self.textTranslation, """
            # [KEYWORD] TRANSLATION
            # e.g. TRANSLATION:::Gen 1:1"""),
            "discourse": (self.textDiscourse, """
            # [KEYWORD] DISCOURSE
            # e.g. DISCOURSE:::Gen 1:1"""),
            "words": (self.textWords, """
            # [KEYWORD] WORDS
            # e.g. WORDS:::Gen 1:1"""),
            "lexicon": (self.textLexicon, """
            # [KEYWORD] LEXICON
            # Usage - LEXICON:::[LEXICON_MODULE]:::[LEXICAL_ENTRY]
            # Usage - LEXICON:::[LEXICON_MODULE]:::[LEXICAL_ENTRIES]
            # e.g. LEXICON:::BDB:::H7225
            # e.g. LEXICON:::BDB:::H7225_H123"""),
            "searchlexicon": (self.searchLexicon, """
            # [KEYWORD] SEARCHLEXICON
            # Usage - SEARCHLEXICON:::[LEXICON_MODULE]:::[TOPIC ENTRY SEARCH]
            # e.g. SEARCHLEXICON:::BDB:::H7225
            # e.g. SEARCHLEXICON:::Dake-topics:::Jesus
            # e.g. SEARCHLEXICON:::ALL:::Peace
            """),
            "reverselexicon": (self.textReverseLexicon, """
            # [KEYWORD] REVERSELEXICON
            # Usage - REVERSELEXICON:::[LEXICON_MODULE]:::[DEFINITION]
            # Usage - REVERSELEXICON:::[LEXICON_MODULE]:::[DEFINITION_ENTRIES]
            # e.g. REVERSELEXICON:::TRLIT:::Jesus"""),
            "lmcombo": (self.textLMcombo, """
            # [KEYWORD] LMCOMBO
            # e.g. LMCOMBO:::E70002:::ETCBC:::subs.f.sg.a"""),
            "lemma": (self.textLemma, """
            # [KEYWORD] LEMMA
            # e.g. LEMMA:::E70002
            # e.g. LEMMA:::H7225"""),
            "morphologycode": (self.textMorphologyCode, """
            # [KEYWORD] MORPHOLOGYCODE
            # e.g. MORPHOLOGYCODE:::E70002,subs.f.sg.a"""),
            "morphology": (self.textMorphology, """
            # [KEYWORD] MORPHOLOGY
            # e.g. MORPHOLOGY:::LexicalEntry LIKE '%E70002,%' AND Morphology LIKE '%feminine%'"""),
            "searchmorphology": (self.textSearchMorphology, """
            # [KEYWORD] SEARCHMORPHOLOGY
            # e.g. SEARCHMORPHOLOGY:::E70002:::feminine
            # alias of e.g. MORPHOLOGY:::LexicalEntry LIKE '%E70002,%' AND (Morphology LIKE "%feminine%")
            # e.g. SEARCHMORPHOLOGY:::E70002:::feminine|noun
            # alias of e.g. MORPHOLOGY:::LexicalEntry LIKE '%E70002,%' AND (Morphology LIKE "%feminine%" OR Morphology LIKE "%noun%")"""),
            "searchmorphologybylex": (self.searchMorphologyByLex, """
            # [KEYWORD] SEARCHMORPHOLOGYBYLEX
            # e.g. SEARCHMORPHOLOGYBYLEX:::G2424:::Noun,Nominative,Masculine
            # e.g. SEARCHMORPHOLOGYBYLEX:::G2424:::Noun,Nominative,Masculine:::40-66
            """),
            "searchmorphologybyword": (self.searchMorphologyByWord, """
            # [KEYWORD] SEARCHMORPHOLOGYBYWORD
            # e.g. SEARCHMORPHOLOGYBYWORD:::Ἰησοῦς:::Noun,Dative,Masculine
            # e.g. SEARCHMORPHOLOGYBYWORD:::Ἰησοῦς:::Noun,Dative,Masculine:::40
            """),
            "searchmorphologybygloss": (self.searchMorphologyByGloss, """
            # [KEYWORD] SEARCHMORPHOLOGYBYGLOSS
            # e.g. SEARCHMORPHOLOGYBYGLOSS:::Joshua:::Noun,Dative,Masculine
            # e.g. SEARCHMORPHOLOGYBYGLOSS:::Joshua:::Noun,Dative,Masculine:::1-66
            """),
            "word": (self.textWordData, """
            # [KEYWORD] WORD
            # Usage - WORD:::[BOOK_NO]:::[WORD_NO]
            # e.g. WORD:::1:::2"""),
            "clause": (self.textClause, """
            # [KEYWORD] CLAUSE
            # e.g. Embed in the first clause of Gen 1:1 in MAB
            # e.g. CLAUSE:::1.1.1:::1"""),
            "searchtool": (self.textSearchTool, """
            # [KEYWORD] SEARCHTOOL
            # e.g. SEARCHTOOL:::EXLBP:::Jesus
            # e.g. SEARCHTOOL:::HBN:::Jesus
            # e.g. SEARCHTOOL:::EXLBL:::Jerusalem
            # e.g. SEARCHTOOL:::EXLBT:::faith
            # e.g. SEARCHTOOL:::EAS:::faith
            # e.g. SEARCHTOOL:::ISB:::faith
            # e.g. SEARCHTOOL:::mETCBC:::prep"""),
            "exlb": (self.textExlb, """
            # [KEYWORD] EXLB
            # e.g. EXLB:::exlbp:::BP904
            # e.g. EXLB:::exlbl:::BL636"""),
            "dictionary": (self.textDictionary, """
            # [KEYWORD] DICTIONARY
            # e.g. DICTIONARY:::EAS1312"""),
            "encyclopedia": (self.textEncyclopedia, """
            # [KEYWORD] ENCYCLOPEDIA
            # e.g. ENCYCLOPEDIA:::ISB:::ISBE3333"""),
            "searchthirddictionary": (self.thirdDictionarySearch, """
            # [KEYWORD] SEARCHTHIRDDICTIONARY
            # e.g. SEARCHTHIRDDICTIONARY:::faith
            # e.g. SEARCHTHIRDDICTIONARY:::webster:::faith"""),
            "thirddictionary": (self.thirdDictionaryOpen, """
            # [KEYWORD] THIRDDICTIONARY
            # e.g. THIRDDICTIONARY:::webster:::FAITH"""),
            "book": (self.textBook, """
            # [KEYWORD] BOOK
            # Usage - BOOK:::[BOOK_MODULE]:::[OPTIONAL_TOPIC]
            # To view all the available topics of a book
            # e.g. BOOK:::Timelines
            # To specify a particular topic
            # e.g. BOOK:::Timelines:::2210-2090_BCE"""),
            "searchbook": (self.textSearchBook, """
            # [KEYWORD] SEARCHBOOK
            # To search the last opened book module
            # e.g. SEARCHBOOK:::Abraham
            # To search a particular book module
            # e.g. SEARCHBOOK:::OT_History1:::Abraham
            # To search mutliple books, separate book modules with a comma ",".
            # e.g. SEARCHBOOK:::OT_History1,OT_History2:::Abraham
            # To search all favourite book modules
            # e.g. SEARCHBOOK:::FAV:::Jerusalem
            # To search all installed book modules
            # e.g. SEARCHBOOK:::ALL:::Jerusalem
            # Remarks: Module creator should avoid comma for naming a book module."""),
            "searchbookchapter": (self.textSearchBookChapter, """
            # [KEYWORD] SEARCHBOOKCHAPTER
            # similar to searchbook:::, difference is that "searchbookchapter:::" searches chapters only
            # e.g. SEARCHBOOKCHAPTER:::Bible_Promises:::index"""),
            "searchallbookspdf": (self.textSearchAllBooksAndPdf, """
            # [KEYWORD] SEARCHALLBOOKSPDF
            # Search all books and all PDF files"""),
            "cmd": (self.osCommand, """
            # [KEYWORD] cmd
            # Feature - Run an os command
            # Warning! Make sure you know what you are running before you use this keyword.  The running command may affect data outside UniqueBible folder.
            # Remarks: This command works ONLY when config.enableCmd is set to True.
            # Examples on Windows:
            # e.g. cmd:::notepad
            # e.g. cmd:::start latest_changes.txt
            # Examples on macOS:
            # e.g. cmd:::open latest_changes.txt
            # e.g. cmd:::open "~/Applications/Visual Studio Code.app"/
            # Examples on Linux:
            # e.g. cmd:::firefox
            # e.g. cmd:::mkdir -p myNotes; cd myNotes; gedit test.txt
            # e.g. cmd:::rm -rf myNotes
            # e.g. cmd:::google-chrome https://uniquebible.app"""),
            "speak": (self.textToSpeech, """
            # [KEYWORD] SPEAK
            # Feature: run text-to-speech function
            # e.g. SPEAK:::All Scripture is inspired by God
            # e.g. SPEAK:::en-gb:::All Scripture is inspired by God
            # e.g. SPEAK:::zh-cn:::聖經都是上帝所默示的
            # e.g. SPEAK:::zh-tw:::聖經都是上帝所默示的"""),
            "gtts": (self.googleTextToSpeech, """
            # [KEYWORD] GTTS
            # Feature: run text-to-speech function
            # e.g. GTTS:::All Scripture is inspired by God
            # e.g. GTTS:::en:::All Scripture is inspired by God
            # e.g. GTTS:::zh:::聖經都是上帝所默示的"""),
            "mp3": (self.mp3Download, """
            # [KEYWORD] MP3
            # Feature: run yt-dlp to download mp3 from youtube, provided that yt-dlp is installed on user's system
            # Usage - MP3:::[youtube_link]"""),
            "mp4": (self.mp4Download, """
            # [KEYWORD] MP4
            # Usage - MP4:::[youtube_link]"""),
            "media": (self.openMediaPlayer, """
            # [KEYWORD] MEDIA
            # Feature: run media player to play mp3 and mp4 files
            # e.g. MEDIA:::music/AmazingGrace.mp3
            # e.g. MEDIA:::video/ProdigalSon.mp4
            """),
            "read": (self.textRead, """
            # [KEYWORD] READ
            # Feature - Read a single bible passage or multiple bible passages.
            # Usage - READ:::[BIBLE_VERSION(S)]:::[BIBLE_REFERENCE(S)]
            # Remarks:
            # 1) The bible version last opened on main view is opened by default if "[BIBLE_VERSION]:::" is omitted.
            # e.g. READ:::Jn 3:16-18
            # e.g. READ:::KJV:::Jn 3:16-18; Deut 6:4
            # e.g. READ:::KJV_CUV:::Jn 3:16-18; Deut 6:4
            """),
            "readsync": (self.textReadSync, """
            # [KEYWORD] READSYNC
            # Feature - Read a single bible passage or multiple bible passages, with text display synchronisation.
            # Usage - READSYNC:::[BIBLE_VERSION(S)]:::[BIBLE_REFERENCE(S)]
            # Remarks:
            # 1) The bible version last opened on main view is opened by default if "[BIBLE_VERSION]:::" is omitted.
            # e.g. READSYNC:::Jn 3:16-18
            # e.g. READSYNC:::KJV:::Jn 3:16-18; Deut 6:4
            # e.g. READSYNC:::KJV_CUV:::Jn 3:16-18; Deut 6:4
            """), #textReadSync
            "readchapter": (self.readChapter, """
            # [KEYWORD] READCHAPTER
            # Feature: read a bible chapter verse by verse
            # e.g. READCHAPTER:::CUV.1.1
            """),
            "readverse": (self.readVerse, """
            # [KEYWORD] READVERSE
            # Feature: read a bible verse
            # e.g. READVERSE:::CUV.1.1.1
            """),
            "readword": (self.readWord, """
            # [KEYWORD] READWORD
            # Feature: read a word
            # Usage - READWORD:::[BIBLE_VERSION].[BOOK_NO].[CHAPTER_NO].[VERSE_NO].[WORD_NO]
            # e.g. READWORD:::BHS5.1.1.1.1
            """),
            "readlexeme": (self.readLexeme, """
            # [KEYWORD] READLEXEME
            # Feature: read a lexeme
            # Usage - READLEXEME:::[BIBLE_VERSION].[BOOK_NO].[CHAPTER_NO].[VERSE_NO].[WORD_NO]
            # e.g. READLEXEME:::BHS5.1.1.1.1
            """),
            "readbible": (self.readBible, """
            # [KEYWORD] READBIBLE
            # Feature: Play Bible mp3 file recording of a chapter
            # mp3 files should be placed under audio/bibles/[Bible Text]/default/[Chapter number]/
            # for example, audio/bibles/KJV/default/40/
            # each file should be a recording of a chapter with the filename "[Book number]_[Name][Chapter number].mp3
            # for example, 40_Matthew001.mp3.  Chapter numbers should be three digits (eg `001`).
            # mp3 files can be downloaded from https://www.audiotreasure.com/audioindex.htm
            # Usage:
            # e.g. READBIBLE:::                                 # Reads current Bible and current chapter
            # e.g. READBIBLE:::@soft-music                      # Reads from soft-music folder instead of default folder
            # e.g. READBIBLE:::Matt. 1                          # Reads chapter from current Bible
            # e.g. READBIBLE:::Matt. 1,John. 1                  # Reads chapters from current Bible
            # e.g. READBIBLE:::Matt. 1-28                       # Reads chapters from current Bible
            # e.g. READBIBLE:::KJV:::Matt. 1                    # Reads chapter from Bible
            # e.g. READBIBLE:::KJV:::Matt. 1,Matt. 2            # Reads chapters from Bible
            # e.g. READBIBLE:::KJV:::Matt. 1-4:::soft-music     # Reads from soft-music folder instead of default folder
            """),
            "opennote": (self.textOpenNoteFile, """
            # [KEYWORD] opennote
            # e.g. opennote:::file_path"""),
            "open": (self.openExternalFile, """
            # [KEYWORD] open
            # open::: is different from opennote::: that open::: uses system default application to open the file.
            # e.g. open:::."""),
            "pdf": (self.openPdfReader, """
            # [KEYWORD] PDF
            # Feature: Open PDF file, located in directory marvelData/pdf/
            # Usage - PDF:::[PDF_filename]
            # Usage - PDF:::[PDF_filename]:::[page_number]
            # e.g. PDF:::Newton - Olney Hymns.pdf:::110"""),
            "pdffind": (self.openPdfReaderFind, """
            # [KEYWORD] PDFFIND
            # Feature: Open PDF file, located in directory marvelData/pdf/ and search for text
            # Usage - PDFFIND:::[PDF_filename]:::[TEXT]
            # e.g. PDFFIND:::Newton - Olney Hymns.pdf:::Amazing"""),
            "searchpdf": (self.searchPdf, """
            # [KEYWORD] SEARCHPDF
            # Feature: Search for text inside PDFs in marvelData/pdf/
            # Usage - SEARCHPDF:::[TEXT]
            # e.g. SEARCHPDF:::Jesus"""),
            "anypdf": (self.openPdfReaderFullpath, """
            # [KEYWORD] ANYPDF
            # Feature: Open PDF file, located in local device where users have read permission.
            # Remarks: It works basically the same as keyword PDF:::, except ANYPDF::: accepts full pdf file path only.
            # Usage - ANYPDF:::[PDF_filename_fullpath]
            # Usage - ANYPDF:::[PDF_filename_fullpath]:::[page_number]
            # e.g. ANYPDF:::file.pdf:::110"""),
            "epub": (self.openEpubReader, """
            # [KEYWORD] EPUB
            # Feature: Open EPUB file, located in directory marvelData/epub/
            # Usage - EPUB:::[EPUB_filename]"""),
            "docx": (self.openDocxReader, """
            # [KEYWORD] DOCX
            # Feature: Open Word Document
            # Usage - DOCX:::[DOCX_filename]
            # e.g. DOCX:::test.docx"""),
            "translate": (self.translateText, """
            # [KEYWORD] TRANSLATE
            # Feature - Use IBM Watson service to translate entered 
            # It works only if user install python package 'ibm-watson'
            # Usage - TRANSLATE:::[text to be translated]
            # Usage - TRANSLATE:::[source_language_code]-[target_language_code]:::[text to be translated]
            # Language code of config.userLanguage is used by default if language code is not provided.  If config.userLanguage is not defined, "en" is used.
            # e.g. TRANSLATE:::測試
            # e.g. TRANSLATE:::en-zh:::test"""),
            "openbooknote": (self.openBookNoteRef, """
            # [KEYWORD] openbooknote
            # e.g. openbooknote:::John"""),
            "openchapternote": (self.openChapterNoteRef, """
            # [KEYWORD] openchapternote
            # e.g. openchapternote:::John 3"""),
            "openversenote": (self.openVerseNoteRef, """
            # [KEYWORD] openversenote
            # e.g. openversenote:::John 3:16"""),
            "editbooknote": (self.editBookNoteRef, """
            # [KEYWORD] editbooknote
            # e.g. editbooknote:::John"""),
            "editchapternote": (self.editChapterNoteRef, """
            # [KEYWORD] editchapternote
            # e.g. editchapternote:::John 3"""),
            "editversenote": (self.editVerseNoteRef, """
            # [KEYWORD] editversenote
            # e.g. editversenote:::John 3:16"""),
            "searchbooknote": (self.textSearchBookNote, """
            # [KEYWORD] SEARCHBOOKNOTE
            # e.g. SEARCHBOOKNOTE:::faith"""),
            "searchchapternote": (self.textSearchChapterNote, """
            # [KEYWORD] SEARCHCHAPTERNOTE
            # e.g. SEARCHCHAPTERNOTE:::faith"""),
            "searchversenote": (self.textSearchVerseNote, """
            # [KEYWORD] SEARCHVERSENOTE
            # e.g. SEARCHVERSENOTE:::faith"""),
            "openjournal": (self.openJournalNote, """
            # [KEYWORD] OPENJOURNAL
            # Feature - Open personal journal
            # Usage - OPENJOURNAL:::
            # Usage - OPENJOURNAL:::[year]-[month]-[day]
            # Remarks: Journal of the day is opened by default when a day is not specified.
            # e.g. OPENJOURNAL:::
            # e.g. OPENJOURNAL:::2022-12-25"""),
            "editjournal": (self.editJournalNote, """
            # [KEYWORD] EDITJOURNAL
            # Feature - Open personal journal in text editor
            # Usage - EDITJOURNAL:::
            # Usage - EDITJOURNAL:::[year]-[month]-[day]
            # Remarks: Journal of the day is opened in text editor by default when a day is not specified.
            # e.g. EDITJOURNAL:::
            # e.g. EDITJOURNAL:::2022-12-25"""),
            "searchjournal": (self.searchJournalNote, """
            # [KEYWORD] SEARCHJOURNAL
            # Feature - Search personal journal
            # Usage - SEARCHJOURNAL:::[LOOK_UP_STRING]
            # e.g. SEARCHJOURNAL:::faith"""),
            "download": (self.download, """
            # [KEYWORD] DOWNLOAD
            # Feature - Download marvel data, github files
            # Usage - DOWNLOAD:::[source]:::[file]
            # Available sources: ["MarvelData", "MarvelBible", "MarvelCommentary", "GitHubBible", "GitHubCommentary", "GitHubBook", "GitHubMap", "GitHubPdf", "GitHubEpub"]
            # e.g. DOWNLOAD:::marvelbible:::KJV
            """),
            "import": (self.importResources, """
            # [KEYWORD] IMPORT
            # Feature - Import third party resources
            # Usage - IMPORT:::
            # Usage - IMPORT:::[directory_path_containing_supported_3rd_party_files]
            # Remarks: If a directory is not specified, "import" is used by default.
            # e.g. IMPORT:::import
            """),
            "devotional": (self.openDevotional, """
            # [KEYWORD] DEVOTIONAL
            # Feature - Open today's devotional entry
            # e.g. DEVOTIONAL:::Meyer
            """),
            "displaywordfrequency": (self.displayWordFrequency, """
            # [KEYWORD] DISPLAYWORDFREQUENCY
            # Feature - Displays the word frequency for Bibles with Strongs numbers
            # and highlights with different colors based on frequency
            # Usage - DISPLAYWORDFREQUENCY:::[BIBLE_VERSION]:::[BIBLE_REFERENCE(S)]
            # This will only highlight Bibles that contain Strongs numbers
            """),
            #
            # Keywords starting with "_" are mainly internal commands for GUI operations
            # They are not recorded in history records.
            #
            "_imv": (self.instantMainVerse, """
            # [KEYWORD] _imv
            # Feature - Display a single verse text.  It takes book, chapter and verse numbers.
            # Usage - _imv:::[BOOK_NO].[CHAPTER_NO].[VERSE_NO]
            # e.g. _imv:::1.1.1
            # e.g. _imv:::43.3.16"""),
            "_imvr": (self.instantMainVerseReference, """
            # [KEYWORD] _imvr
            # Feature - Display a single verse text.  It takes a bible reference.
            # Usage - _imv:::[BIBLE_REFERENCE]
            # e.g. _imvr:::Gen 1:1
            # e.g. _imvr:::John 3:16"""),
            "_instantverse": (self.instantVerse, """
            # [KEYWORD] _instantverse
            # Feature - Display interlinear verse text on bottom window.
            # OHGB_WORD_ID is optional.  Corresponding Hebrew / Greek word is highlighted if OHGB_WORD_ID is given.
            # Usage: _instantverse:::[BOOK_NO].[CHAPTER_NO].[VERSE_NO]
            # Usage: _instantverse:::[BOOK_NO].[CHAPTER_NO].[VERSE_NO].[OHGB_WORD_ID]
            # e.g. _instantVerse:::1.1.1
            # e.g. _instantVerse:::1.1.1.1"""),
            "_instantword": (self.instantWord, """
            # [KEYWORD] _instantword
            # e.g. _instantWord:::1:::h2"""),
            "_lexicaldata": (self.instantLexicalData, """
            # [KEYWORD] _lexicaldata
            # Feature - Display lexical data on bottom window.
            # Usage: _lexicaldata:::[LEXICAL_ENTRY]
            # e.g. _lexicaldata:::G1234"""),
            "_vnsc": (self.verseNoSingleClick, """
            # [KEYWORD] _vnsc
            # Feature -Verse number single-click action
            # e.g. _vnsc:::KJV.43.3.16.John 3:16"""),
            "_vndc": (self.verseNoDoubleClick, """
            # [KEYWORD] _vndc
            # Feature - Verse number double-click action
            # e.g. _vnsc:::KJV.43.3.16"""),
            "_menu": (self.textMenu, """
            # [KEYWORD] _menu
            # Feature - Open UBA classic html menu
            # e.g. _menu:::
            # e.g. _menu:::43
            # e.g. _menu:::43.3
            # e.g. _menu:::43.3.16"""),
            "_comparison": (self.textComparisonMenu, """
            # [KEYWORD] _comparison
            # Feature - Open html menu for bible version comparison
            # e.g. _comparison:::"""),
            "_chapters": (self.textChapters, """
            # [KEYWORD] _chapters
            # Feature - Display all available chapters of a bible version.
            # Usage - _chapters:::[BIBLE_VERSION]
            # e.g. _chapters:::KJV
            # e.g. _chapters:::NET"""),
            "_verses": (self.textVerses, """
            # [KEYWORD] _verses
            # Feature - Display all available verses of a bible chapter.
            # Usage - _verses:::[BIBLE_VERSION]:::[BIBLE_REFERENCE]
            # e.g. _verses:::Jn 3
            # e.g. _verses:::KJV:::Jn 3
            # e.g. _verses:::NET:::Jn 3"""),
            "_commentaries": (self.textCommentaries, """
            # [KEYWORD] _commentaries
            # Feature - Display all available commentary modules.
            # Usage - _commentaries:::
            # e.g. _commentaries:::"""),
            "_commentarychapters": (self.textCommentaryChapters, """
            # [KEYWORD] _commentarychapters
            # Feature - Display commentary chapter menu.
            # Usage - _commentarychapters:::[COMMENTARY]
            # e.g. _commentarychapters:::BI
            # e.g. _commentarychapters:::CBSC"""),
            "_commentaryverses": (self.textCommentaryVerses, """
            # [KEYWORD] _commentaryverses
            # Feature - Display commentary verse menu.
            # Usage - _commentaryverses:::[COMMENTARY]:::[BIBLE_REFERENCE]
            # e.g. _commentaryverses:::Jn 3
            # e.g. _commentaryverses:::BI:::Jn 3
            # e.g. _commentaryverses:::CBSC:::Jn 3"""),
            "_commentary": (self.textCommentaryMenu, """
            # [KEYWORD] _commentary
            # e.g. _commentary:::CBSC.1.1.1"""),
            "_book": (self.textBookMenu, """
            # [KEYWORD] _book
            # e.g. _book:::"""),
            "_info": (self.textInfo, """
            # [KEYWORD] _info
            # e.g. _info:::Genesis"""),
            "_bibleinfo": (self.textBibleInfo, """
            # [KEYWORD] _bibleinfo
            # e.g. _bibleinfo:::KJV"""),
            "_commentaryinfo": (self.textCommentaryInfo, """
            # [KEYWORD] _commentaryinfo
            # e.g. _commentaryinfo:::CBSC"""),
            "_command": (self.textCommand, """
            # [KEYWORD] _command
            # e.g. _command:::testing"""),
            "_history": (self.textHistory, """
            # [KEYWORD] _history
            # e.g. _history:::main
            # e.g. _history:::study"""),
            "_historyrecord": (self.textHistoryRecord, """
            # [KEYWORD] _historyrecord
            # e.g. _historyrecord:::1"""),
            "_image": (self.textImage, """
            # [KEYWORD] _image
            # e.g. _image:::EXLBL:::1.jpg"""),
            "_htmlimage": (self.textHtmlImage, """
            # [KEYWORD] _htmlimage
            # Feature - open image file located in 'htmlResources/images/'
            # Usage - _htmlimage:::[filepath_relative_to_images_directory]
            # e.g. _htmlimage:::exlbl_largeHD/BL1263.png"""),
            "_openbooknote": (self.openBookNote, """
            # [KEYWORD] _openbooknote
            # Feature - open bible book note
            # Usage - _openbooknote:::[BOOK_NO]
            # e.g. _openbooknote:::43"""),
            "_openchapternote": (self.openChapterNote, """
            # [KEYWORD] _openchapternote
            # Feature - open bible chapter note
            # Usage - _openchapternote:::[BOOK_NO].[CHAPTER_NO]
            # e.g. _openchapternote:::43.3"""),
            "_openversenote": (self.openVerseNote, """
            # [KEYWORD] _openversenote
            # Feature - open bible verse note
            # Usage - _openversenote:::[BOOK_NO].[CHAPTER_NO].[VERSE_NO]
            # e.g. _openversenote:::43.3.16"""),
            "_editbooknote": (self.editBookNote, """
            # [KEYWORD] _editbooknote
            # Feature - edit bible book note
            # Usage - _editbooknote:::[BOOK_NO]
            # e.g. _editbooknote:::43"""),
            "_editchapternote": (self.editChapterNote, """
            # [KEYWORD] _editchapternote
            # Feature - edit bible chapter note
            # Usage - _editchapternote:::[BOOK_NO].[CHAPTER_NO]
            # e.g. _editchapternote:::43.3"""),
            "_editversenote": (self.editVerseNote, """
            # [KEYWORD] _editversenote
            # Feature - edit bible verse note
            # Usage - _editversenote:::[BOOK_NO].[CHAPTER_NO].[VERSE_NO]
            # e.g. _editversenote:::43.3.16"""),
            "_open": (self.openMarvelDataFile, """
            # [KEYWORD] _open
            # open a file inside marvelData folder
            # e.g. _open:::.
            # e.g. _open:::bibles"""),
            "_openfile": (self.textOpenFile, """
            # [KEYWORD] _openfile
            # Usage: _openfile:::[external_note_history_record_index]
            # e.g. _openfile:::-1
            # Remarks: -1 is the latest record"""),
            "_editfile": (self.textEditFile, """
            # [KEYWORD] _editfile
            # Usage: _editfile:::[external_note_history_record_index]
            # e.g. _editfile:::-1
            # Remarks: -1 is the latest record"""),
            "_website": (self.textWebsite, """
            # [KEYWORD] _website
            # e.g. _website:::https://marvel.bible"""),
            "_uba": (self.textUba, """
            # [KEYWORD] _uba
            # e.g. _uba:::file://notes.uba
            # e.g. _uba:::file://note_editor_key_combo.uba"""),
            "_biblenote": (self.textBiblenote, """
            # [KEYWORD] _biblenote
            # Feature - retrieve bible module note(s) of a single verse.
            # Usage - _biblenote:::[BIBLE_VERSION].[BOOK_NO].[CHAPTER_NO].[VERSE_NO]
            # Usage - _biblenote:::[BIBLE_VERSION].[BOOK_NO].[CHAPTER_NO].[VERSE_NO].[NOTE_INDICATOR]
            # e.g. _biblenote:::KJV:::1.1.1
            # e.g. _biblenote:::KJV:::1.1.1.1"""),
            "_wordnote": (self.textWordNote, """
            # [KEYWORD] _wordnote
            # e.g. _wordnote:::LXX1:::l1"""),
            "_searchword": (self.textSearchWord, """
            # [KEYWORD] _searchword
            # Usage: _searchword:::[1=OT, 2=NT]:::[wordID]
            # e.g. _searchword:::1:::1"""),
            "_harmony": (self.textHarmony, """
            # [KEYWORD] _harmony
            # Feature - Display verses from a harmony collection.
            # Usage - _harmony:::[collection_number].[entry_number]
            # e.g. _harmony:::4.1"""),
            "_promise": (self.textPromise, """
            # [KEYWORD] _promise
            # Feature - Display verses from a bible collection.
            # Usage - _promise:::[collection_number].[entry_number]
            # e.g. _promise:::4.1"""),
            "_paste": (self.pasteFromClipboard, """
            # [KEYWORD] _paste
            # Feature - Display clipboard text.
            # e.g. _paste:::"""),
            "_mastercontrol": (self.openMasterControl, """
            # [KEYWORD] _mastercontrol
            # Usage: _mastercontrol:::
            # Usage: _mastercontrol:::[0-4]"""),
            "_highlight": (self.highlightVerse, """
            # [KEYWORD] _highlight
            # Feature - Highlight a verse
            # Usage - _highlight:::[code]:::[BIBLE_REFERENCE(S)]
            # Examples:
            # e.g. _highlight:::hl1:::John 3:16
            # e.g. _highlight:::hl2:::John 3:16
            # e.g. _highlight:::ul1:::John 3:16
            # e.g. _highlight:::delete:::John 3:16"""),
            "_savepdfcurrentpage": (self.savePdfCurrentPage, """
            # [KEYWORD] _savePdfCurrentPage
            # Feature - Save the current page of PDF
            # Usage - _savePdfCurrentPage:::[page]
            # Example:
            # e.g. _savePdfCurrentPage:::100"""),
            "_setconfig": (self.textSetConfig, """
            # [KEYWORD] _setconfig
            # Feature - Set a config value in config.py.
            # Usage - _setconfig:::[item]:::[value]
            # WARNING! Do NOT use this command unless you know well about config.py.  A mistake can prevent UBA from uniquebible.startup.
            # Remarks: This command works ONLY when config.developer or config.webFullAccess is set to True.
            # Remarks: All configurable settings are displayed if both item and value are not provided.
            # Remarks: Help content about an item if an item is provided without value.
            # Remarks: Use single quotation mark ' for string value.
            # Example:
            # e.g. _setconfig:::
            # e.g. _setconfig:::favouriteBible
            # e.g. _setconfig:::favouriteBible:::'BSB'"""),
            "_fixlinksincommentary": (self.fixLinksInCommentary, """
            # Usage - _fixlinksincommentary:::[commentary]
            # Example:
            # _fixlinksincommentary:::Dakes
            """),
            "_copy": (self.copyText, """
            # Usage - _copy:::[text]
            # Remarks: This commands works only on desktop or webtop version.
            # Example:
            # _copy:::Unique Bible App
            """),
            "_whatis": (self.textWhatIs, """
            # [KEYWORD] _whatis
            # Feature - Display brief description about a command keyword
            # Usage - _whatis:::[command_keyword]
            # e.g. _whatis:::bible
            # e.g. _whatis:::read"""),
        }
        for key, value in BibleBooks.abbrev["eng"].items():
            book = value[0]
            self.interpreters[book.lower()] = (partial(self.textSearchSingleBook, key), """
            # [KEYWORD] {0}
            # Feature - Search '{0}' ONLY
            # Usage - {0}:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]
            # e.g. {0}:::KJV:::love""".format(book))

    ''' old - will make a change
            # semantic search requires OpenAI API key
            "semantic": (self.textSemanticSearch, """
            # [KEYWORD] SEMANTIC
            # Feature - Bible Query via OpenAI API and Llama Index.
            # Usage - SEMANTIC:::[BIBLE_VERSION]:::[QUERY]
            # e.g. SEMANTIC:::KJV:::quote verses on "God created the earth"
            # e.g. SEMANTIC:::KJV:::write a summary on Exodus 14
            # e.g. SEMANTIC:::KJV:::compare Mark 1 and John 1
            """),
            # gpt index search requires OpenAI API key
            "gptsearch": (self.textGPTSEARCHSearch, """
            # [KEYWORD] GPTSEARCH
            # Feature - Use natural language to search bible modules.
            # Usage - GPTSEARCH:::[BIBLE_VERSION]:::[QUERY]
            # e.g. GPTSEARCH:::NET:::slow to speak
            # e.g. GPTSEARCH:::NET:::verses contain both Jesus and love
            # e.g. GPTSEARCH:::NET:::verses contain spirit but not holy
            # e.g. GPTSEARCH:::NET:::faith in chapter 3
            # e.g. GPTSEARCH:::verses that contain both 'God' and 'faith' in the book of Isaiah
            """),
    '''

    def parser(self, textCommand, source="main"):
        commandList = self.splitCommand(textCommand)
        updateViewConfig, viewText, *_ = self.getViewConfig(source)
        if len(commandList) == 1:
            textCommand = textCommand.strip()
            if self.isDatabaseInstalled("bible"):
                self.lastKeyword = "bible"
                return self.textBibleVerseParser(textCommand, viewText, source)
            else:
                return self.databaseNotInstalled("bible")
        else:
            keyword, command = commandList
            keyword = keyword.lower()
            if keyword in ("bible", "study", "text") and config.runMode == "terminal":
                config.terminalBibleComparison = False
            if config.runMode == "terminal" and keyword in config.mainWindow.unsupportedCommands:
                return ("study", f"{keyword}::: command is currently not supported in terminal mode.", {})
            if keyword in self.interpreters:
                if self.isDatabaseInstalled(keyword):
                    command = command.strip()
                    if not command:
                        currentBibleReference = self.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
                        if keyword in ("bible", "study", "compare", "crossreference", "diff", "difference", "tske", "translation", "discourse", "words", "combo", "commentary", "index", "openversenote", "displaywordfrequency"):
                            command = currentBibleReference
                            print(f"Running '{keyword}:::{command}' ...")
                        elif keyword in ("openbooknote",):
                            command = re.sub(" [0-9]+?:[0-9]+?$", "", currentBibleReference)
                            print(f"Running '{keyword}:::{command}' ...")
                        elif keyword in ("openchapternote", "overview", "summary", "chapterindex"):
                            command = currentBibleReference.split(":", 1)[0]
                            print(f"Running '{keyword}:::{command}' ...")
                        elif not keyword in ("_mastercontrol", "_paste", "_commentaries", "commentary2", "_comparison", "_menu", "import", "_setconfig", "openjournal", "editjournal", "searchjournal", "searchbooknote", "searchchapternote", "searchversenote", "_openbooknote", "_openchapternote", "_openversenote", "_editbooknote", "_editchapternote", "_editversenote", "_vnsc", "_vndc"):
                            return self.textWhatIs(keyword, source)
                    self.lastKeyword = keyword
                    return self.interpreters[keyword][0](command, source)
                else:
                    return self.databaseNotInstalled(keyword)
            else:
                if self.isDatabaseInstalled("bible"):
                    self.lastKeyword = "bible"
                    return self.textBibleVerseParser(textCommand, viewText, source)
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
            "passages": self.getCoreBiblesInfo(),
            "diff": self.getCoreBiblesInfo(),
            "difference": self.getCoreBiblesInfo(),
            "count": self.getCoreBiblesInfo(),
            "search": self.getCoreBiblesInfo(),
            "semantic": self.getCoreBiblesInfo(),
            "gptsearch": self.getCoreBiblesInfo(),
            "advancedsearch": self.getCoreBiblesInfo(),
            "andsearch": self.getCoreBiblesInfo(),
            "orsearch": self.getCoreBiblesInfo(),
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
            "overview": self.getCollectionsInfo(),
            "summary": ((config.marvelData, "commentaries", "cBrooks.commentary"), "1pZNRYE6LqnmfjUem4Wb_U9mZ7doREYUm"),
            "_harmony": self.getCollectionsInfo(),
            "_promise": self.getCollectionsInfo(),
            "_book": self.getBookInfo(),
            "book": self.getBookInfo(),
            "searchbook": self.getBookInfo(),
            "searchbookchapter": self.getBookInfo(),
            "crossreference": self.getXRefInfo(),
            "tske": self.getXRefInfo(),
            "_image": ((config.marvelData, "images.sqlite"), "1_fo1CzhzT6h0fEHS_6R0JGDjf9uLJd3r"),
            "index": ((config.marvelData, "indexes2.sqlite"), "1hY-QkBWQ8UpkeqM8lkB6q_FbaneU_Tg5"),
            "chapterindex": ((config.marvelData, "indexes2.sqlite"), "1hY-QkBWQ8UpkeqM8lkB6q_FbaneU_Tg5"),
            "searchtool": ((config.marvelData, "search.sqlite"), "1A4s8ewpxayrVXamiva2l1y1AinAcIKAh"),
            "word": ((config.marvelData, "data", "wordNT.data"), "11pmVhecYEtklcB4fLjNP52eL9pkytFdS"),
            "clause": ((config.marvelData, "data", "clauseNT.data"), "11pmVhecYEtklcB4fLjNP52eL9pkytFdS"),
            "translation": ((config.marvelData, "data", "translationNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
            "discourse": ((config.marvelData, "data", "discourseNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
            "words": ((config.marvelData, "data", "wordsNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
            "combo": ((config.marvelData, "data", "wordsNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
            "lexicon": ((config.marvelData, "lexicons", "MCGED.lexicon"), "157Le0xw2ovuoF2v9Bf6qeck0o15RGfMM"),
            "exlb": ((config.marvelData, "data", "exlb3.data"), "1gp2Unsab85Se-IB_tmvVZQ3JKGvXLyMP"),
            "dictionary": ((config.marvelData, "data", "dictionary.data"), "1NfbkhaR-dtmT1_Aue34KypR3mfPtqCZn"),
            "encyclopedia": ((config.marvelData, "data", "encyclopedia.data"), "1OuM6WxKfInDBULkzZDZFryUkU1BFtym8"),
        }

    def getCoreBiblesInfo(self):
        return ((config.marvelData, "images.sqlite"), "1-aFEfnSiZSIjEPUQ2VIM75I4YRGIcy5-")

    def getBibleNoteInfo(self):
        return ((config.marvelData, "note.sqlite"), "1OcHrAXLS-OLDG5Q7br6mt2WYCedk8lnW")

    def getCollectionsInfo(self):
        return ((config.marvelData, "collections3.sqlite"), "18dRwEc3SL2Z6JxD1eI1Jm07oIpt9i205")

    def getBookInfo(self):
        return ((config.marvelData, "books", "Maps_ABS.book"), "13hf1NvhAjNXmRQn-Cpq4hY0E2XbEfmEd")

    def getXRefInfo(self):
        return ((config.marvelData, "cross-reference.sqlite"), "1fTf0L7l1k_o1Edt4KUDOzg5LGHtBS3w_")

    def getLastCommentaryInfo(self):
        return ((config.marvelData, "commentaries", "c{0}.commentary".format(config.commentaryText)), self.getCommentaryCloudID(config.commentaryText))

    def getMarvelBibles(self):
        return DatafileLocation.marvelBibles

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
        if self.parent is not None:
            self.parent.downloadHelper(databaseInfo)
        return ("", "", {})

    # return invalid command
    def invalidCommand(self, source="main"):
        if config.developer:
            print(traceback.format_exc())
        return (source, "INVALID_COMMAND_ENTERED", {})

    # return no audio
    def noAudio(self, source="main"):
        return (source, "NO_AUDIO", {})

    # return no Hebrew audio
    def noHebrewAudio(self, source="main"):
        return (source, "NO_HEBREW_AUDIO", {})

    # return no Greek audio
    def noGreekAudio(self, source="main"):
        return (source, "NO_GREEK_AUDIO", {})

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
            "cli": (self.setMainVerse, config.mainText, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV), config.mainB, config.mainC, config.mainV),
            "http": (self.setMainVerse, config.mainText, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV), config.mainB, config.mainC, config.mainV),
        }
        return views[view]

    def setMainVerse(self, text, bcvTuple):
        config.mainText = text
        config.mainB, config.mainC, config.mainV, *_ = bcvTuple
        config.setMainVerse = True
        if self.parent is not None:
            self.parent.updateMainRefButton()

    def setStudyVerse(self, text, bcvTuple):
        config.studyText = text
        config.studyB, config.studyC, config.studyV, *_ = bcvTuple
        if self.parent is not None:
            self.parent.updateStudyRefButton()
        config.commentaryB, config.commentaryC, config.commentaryV, *_ = bcvTuple
        if self.parent is not None:
            self.parent.updateCommentaryRefButton()

    def setCommentaryVerse(self, text, bcvTuple):
        config.commentaryText = text
        config.commentaryB, config.commentaryC, config.commentaryV, *_ = bcvTuple
        if self.parent is not None:
            self.parent.updateCommentaryRefButton()
        config.studyB, config.studyC, config.studyV, *_ = bcvTuple
        if self.parent is not None:
            self.parent.updateStudyRefButton()

    # shared functions about bible text
    def getConfirmedTexts(self, texts, allowEmptyList=False):
        biblesSqlite = BiblesSqlite()
        bibleList = biblesSqlite.getBibleList()
        confirmedTexts = [text for text in texts.split("_") if text in bibleList or text in self.getMarvelBibles()]
        if not confirmedTexts:
            if allowEmptyList:
                return []
            confirmedTexts = [config.favouriteBible]
        #return sorted(list(set(confirmedTexts)))
        confirmedTexts = list(set(confirmedTexts))
        if config.mainText in confirmedTexts:
            confirmedTexts.remove(config.mainText)
            confirmedTexts = [config.mainText] + sorted(confirmedTexts)
        return confirmedTexts

    def extractAllVerses(self, text, tagged=False):
        return BibleVerseParser(config.parserStandarisation).extractAllReferences(text, tagged)

    def extractAllVersesFast(self, text):
        return BibleVerseParser(config.parserStandarisation).extractAllReferencesFast(text)

    def bcvToVerseReference(self, b, c, v):
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)

    def isTextInCompareTexts(self, text, compareTexts):
        return True if text in compareTexts[:-3].split("_") else False

    def switchCompareView(self):
        if self.parent.enforceCompareParallelButton:
            if self.parent is not None:
                self.parent.enforceCompareParallelButtonClicked()
        else:
            config.enforceCompareParallel = not config.enforceCompareParallel

    # default function if no special keyword is specified
    def textBibleVerseParser(self, command, text, view, parallel=False):
        if config.enforceCompareParallel and not parallel:
            compareMatches = re.match("^[Cc][Oo][Mm][Pp][Aa][Rr][Ee]:::(.*?:::)", config.history["main"][-1])
            if view in ("main", "http") and compareMatches:
                compareTexts = compareMatches.group(1)
                if self.isTextInCompareTexts(text, compareTexts):
                    config.tempRecord = "COMPARE:::{0}{1}".format(compareTexts, command)
                    return self.textCompare("{0}{1}".format(compareTexts, command), view)
                else:
                    self.switchCompareView()
            parallelMatches = re.match("^[Pp][Aa][Rr][Aa][Ll][Ll][Ee][Ll]:::(.*?:::)", config.history["main"][-1])
            if view in ("main", "http") and parallelMatches:
                compareTexts = parallelMatches.group(1)
                if self.isTextInCompareTexts(text, compareTexts):
                    config.tempRecord = "PARALLEL:::{0}{1}".format(compareTexts, command)
                    return self.textParallel("{0}{1}".format(compareTexts, command), view)
                else:
                    self.switchCompareView()
            compareSideBySideMatches = re.match("^[Ss][Ii][Dd][Ee][Bb][Yy][Ss][Ii][Dd][Ee]:::(.*?:::)", config.history["main"][-1])
            if view in ("main", "http") and compareSideBySideMatches:
                compareTexts = compareSideBySideMatches.group(1)
                if self.isTextInCompareTexts(text, compareTexts):
                    config.tempRecord = "SIDEBYSIDE:::{0}{1}".format(compareTexts, command)
                    return self.textCompareSideBySide("{0}{1}".format(compareTexts, command), view)
                else:
                    self.switchCompareView()
        # Direct to bible search when there is no valid reference.
        # Use the latest search mode for bible search.
        # Qt library users can change bible search mode via master control
        # Terminal mode users can change default search mode via ".changebiblesearchmode"
        searchModes = ("COUNT", "SEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH", "GPTSEARCH", "SEMANTIC")
        if config.useLiteVerseParsing:
            verseList = self.extractAllVersesFast(command)
            if verseList[0][0] == 0:
                command = re.sub(r" \d+:?\d?$", "", command)
                command = f"{searchModes[config.bibleSearchMode]}:::{config.mainText}:::{command}"
                return self.parser(command, view)
        else:
            verseList = self.extractAllVerses(command)
        if not verseList:
            command = f"{searchModes[config.bibleSearchMode]}:::{config.mainText}:::{command}"
            return self.parser(command, view)
        else:
            formattedBiblesFolder = os.path.join(config.marvelData, "bibles")
            formattedBibles = [f[:-6] for f in os.listdir(formattedBiblesFolder) if os.path.isfile(os.path.join(formattedBiblesFolder, f)) and f.endswith(".bible") and not re.search(r"^[\._]", f)]
            if text in ("MOB", "MIB", "MTB", "MPB", "MAB", "LXX1i", "LXX2i", "LXX1", "LXX2") and not config.readFormattedBibles:
                config.readFormattedBibles = True
                if self.parent is not None:
                    self.parent.enableParagraphButtonAction(False)
            elif config.readFormattedBibles and (((text in ("OHGBi", "OHGB") or not text in formattedBibles) and view == "main") or text == "LXX"):
                config.readFormattedBibles = False
                if self.parent is not None:
                    self.parent.enableParagraphButtonAction(False)

            # Custom font styling for Bible
            (fontFile, fontSize, css) = Bible(text).getFontInfo()
            if view == "main":
                config.mainCssBibleFontStyle = css
            elif view == "study":
                config.studyCssBibleFontStyle = css
            if (len(verseList) == 1) and (len(verseList[0]) == 3):
                compareParallelList = "_".join(config.compareParallelList)
                if config.runMode == "terminal" and config.terminalBibleParallels:
                    return self.textCompareSideBySide(f"{compareParallelList}:::{command}", view)
                elif config.runMode == "terminal" and config.terminalBibleComparison:
                    return self.textCompare(f"{compareParallelList}:::{command}", view)
                # i.e. only one verse reference is specified
                bcvTuple = verseList[0]
                # Force book to 1 if it's 0 (when viewing a commentary intro)
                if bcvTuple[1] == 0:
                    bcvTuple = (bcvTuple[0], 1, 1)
                chapters = self.getChaptersMenu(bcvTuple[0], bcvTuple[1], text) if config.displayChapterMenuTogetherWithBibleChapter else ""
                content = "{0}{2}{1}{2}{0}".format(chapters, self.textFormattedBible(bcvTuple, text, view), "<hr>" if config.displayChapterMenuTogetherWithBibleChapter else "")
            else:
                # i.e. when more than one verse reference is found
                content = self.textPlainBible(verseList, text)
                bcvTuple = verseList[-1]
            content = self.toggleBibleText(content)
            # Add text tag for custom font styling
            content = "<bibletext class='{0}'>{1}</bibletext>".format(text, content)
            config.eventContent = content
            PluginEventHandler.handleEvent("post_parse_bible", command)
            content = config.eventContent
            if config.openBibleInMainViewOnly:
                self.setMainVerse(text, bcvTuple)
                #self.setStudyVerse(text, bcvTuple)
                return ("main", content, {})
            else:
                updateViewConfig, *_ = self.getViewConfig(view)
                updateViewConfig(text, bcvTuple)
                return (view, content, {'tab_title': text})

    def toggleBibleText(self, text):
        # The following line does not work when config.displayChapterMenuTogetherWithBibleChapter is set to True.
        #isMarvelBibles = True if re.search("_instantVerse:::(MOB|MIB|MPB|MTB|MAB|OHGB|OHGBi):::", text) else False
        # use the following line instead
        isMarvelBibles = True if re.search("_chapters:::(MOB|MIB|MPB|MTB|MAB|OHGB|OHGBi)_", text) else False
        # The following line does not work when config.displayChapterMenuTogetherWithBibleChapter is set to True.
        #isMIB = ("_instantVerse:::MIB:::" in text)
        # use the following line instead
        isMIB = ("_chapters:::MIB_" in text)
        if (config.showHebrewGreekWordAudioLinks and isMarvelBibles) or (config.showHebrewGreekWordAudioLinksInMIB and isMIB):
            text = re.sub("(<pm>|</pm>|<n>|</n>)", "", text)
            text = re.sub("""(<heb id="wh)([0-9]+?)("[^<>]*?onclick="luW\()([0-9]+?)(,[^<>]*?>[^<>]+?</heb>[ ]*)""", r"""\1\2\3\4\5 <ref onclick="wah(\4,\2)">{0}</ref>""".format(config.audioBibleIcon), text)
            text = re.sub("""(<grk id="w[0]*?)([1-9]+[0-9]*?)("[^<>]*?onclick="luW\()([0-9]+?)(,[^<>]*?>[^<>]+?</grk>[ ]*)""", r"""\1\2\3\4\5 <ref onclick="wag(\4,\2)">{0}</ref>""".format(config.audioBibleIcon), text)
            if isMIB:
                text = text.replace(config.audioBibleIcon, "＊＊＊")
                text = re.sub("""([ ]*<ref onclick="wa[gh])(\([0-9]+?,[0-9]+?\)">[^<>]+?</ref>)(.*?</wform>.*?<wlex>.*?</wlex></ref>)""", r"\1\2\3\1l\2", text)
                text = text.replace("＊＊＊", config.audioBibleIcon)
        if not config.showVerseReference:
            text = re.sub('<vid .*?>.*?</vid>', '', text)
        if not config.showBibleNoteIndicator:
            text = re.sub("<sup><ref onclick='bn\([^\(\)]*?\)'>&oplus;</ref></sup>", '', text)
        if config.hideLexicalEntryInBible and re.search("onclick=['{0}]lex".format('"'), text):
            p = re.compile(r"<[^\n<>]+?onclick='lex\({0}([^\n<>]+?){0}\)'>[^\n<>]+?</[^\n<>]+?>[ ]*?<[^\n<>]+?onclick='lex\({0}([^\n<>]+?){0}\)'>[^\n<>]+?</[^\n<>]+?>".format('"'))
            while p.search(text):
                text = p.sub(r"<ref onclick='lex({0}\1_\2{0})'>*</ref>".format('"'), text)
            p = re.compile(r"<[^\n<>]+?onclick='rmac\({0}([^\n<>]+?){0}\)'>[^\n<>]+?</[^\n<>]+?>[ ]*?<[^\n<>]+?onclick='rmac\({0}([^\n<>]+?){0}\)'>[^\n<>]+?</[^\n<>]+?>".format('"'))
            while p.search(text):
                text = p.sub(r"<ref onclick='rmac({0}\1_\2{0})'>*</ref>".format('"'), text)
            searchReplace = {
                (r"<sup><[^\n<>]+?onclick='lex\({0}([^\n<>]+?){0}\)'>[^\n<>]+?</[^\n<>]+?> <[^\n<>]+?onclick='rmac\({0}([^\n<>]+?){0}\)'>[^\n<>]+?</[^\n<>]+?></sup>".format('"'), r"<sup><ref onclick='lmCombo({0}\1{0}, {0}rmac{0}, {0}\2{0})'>*</ref></sup>".format('"')),
                (r"<sup><[^\n<>]+?onclick='lex\({0}([^\n<>]+?){0}\)'>[^\n<>]+?</[^\n<>]+?></sup>".format('"'), r"<sup><ref onclick='lex({0}\1{0})'>*</ref></sup>".format('"')),
            }
            for search, replace in searchReplace:
                text = re.sub(search, replace, text)
            p = re.compile(r"(<sup><ref onclick='bn\([^\n\(\)]*?\)'>&oplus;</ref></sup>|<woj>⸃</woj>|</woj>|</i>|</ot>|</mbe>|</mbn>)(<sup><ref onclick='l[^\r<>]*?>\*</ref></sup>)")
            while p.search(text):
                text = p.sub(r"\2\1", text)
            p = re.compile(r"([^\n<>]+?)<sup><ref (onclick='l[^\r<>]*?>)\*</ref></sup>")
            while p.search(text):
                text = p.sub(r"<tag \2\1</tag>", text)
        return text

    def getChaptersMenu(self, b, c, text):
        biblesSqlite = BiblesSqlite()
        chapteruMenu = biblesSqlite.getChaptersMenu(b, c, text)
        return chapteruMenu

    # access to formatted chapter or plain verses of a bible text, called by textBibleVerseParser
    def textPlainBible(self, verseList, text):
        biblesSqlite = BiblesSqlite()
        verses = biblesSqlite.readMultipleVerses(text, verseList)
        return verses

    def textFormattedBible(self, verse, text, source="", rawOutputChapter=False):
        if config.rawOutput and not rawOutputChapter:
            return self.textPlainBible([verse], text)
        formattedBiblesFolder = os.path.join(config.marvelData, "bibles")
        formattedBibles = [f[:-6] for f in os.listdir(formattedBiblesFolder) if os.path.isfile(os.path.join(formattedBiblesFolder, f)) and f.endswith(".bible") and not re.search(r"^[\._]", f)]
        #marvelBibles = ("MOB", "MIB", "MAB", "MPB", "MTB", "LXX1", "LXX1i", "LXX2", "LXX2i")
        #marvelBibles = list(self.getMarvelBibles().keys())
        # bibleSqlite = Bible(text)
        #if source in ("cli"):
        #    b, c, v, *_ = verse
        #    bibleSqlite = Bible(text)
        #    b, c, v, content = bibleSqlite.readTextVerse(b, c, v)
        bibleSqlite = Bible(text)
        if text in formattedBibles and text not in ("OHGB", "OHGBi", "LXX") and config.readFormattedBibles:
            content = bibleSqlite.readFormattedChapter(verse, source)
        else:
            # use plain bibles database when corresponding formatted version is not available
            language = bibleSqlite.getLanguage()
            content = BiblesSqlite(language).readPlainChapter(text, verse, source)
        if config.runMode == "terminal":
            if config.terminalEnablePager:
                singleVerse = self.textPlainBible([verse], text)
                content = f"{singleVerse}<br>{config.mainWindow.divider}<br>{content}"
            else:
                singleVerse = self.textPlainBible([verse], text)
                content = f"{content}<br>{config.mainWindow.divider}<br>{singleVerse}"
        return content

    def textFormattedChapter(self, command, source):
        if command.count(":::") == 0:
            if config.openBibleInMainViewOnly:
                updateViewConfig, viewText, *_ = self.getViewConfig("main")
            else:
                updateViewConfig, viewText, *_ = self.getViewConfig(source)
            command = "{0}:::{1}".format(viewText, command)
        texts, references = self.splitCommand(command)
        verseList = self.extractAllVerses(references)
        if not verseList:
            return self.invalidCommand()
        firstVerse = verseList[0]
        texts = self.getConfirmedTexts(texts)
        marvelBibles = self.getMarvelBibles()
        if not texts:
            return self.invalidCommand()
        else:
            self.cancelBibleParallels()
            text = texts[0]
            if text in marvelBibles:
                fileItems = marvelBibles[text][0]
                if os.path.isfile(os.path.join(*fileItems)):
                    content = self.textFormattedBible(firstVerse, text, source, rawOutputChapter=True)
                    self.setMainVerse(text, firstVerse)
                    return ("main", content, {})
                else:
                    databaseInfo = marvelBibles[text]
                    if self.parent is not None:
                        self.parent.downloadHelper(databaseInfo)
                    return ("", "", {})
            else:
                content = self.textFormattedBible(firstVerse, text, source, rawOutputChapter=True)
                self.setMainVerse(text, firstVerse)
                return ("main", content, {})

    # cmd:::
    # run os command
    def osCommand(self, command, source):
        window = ""
        display = ""
        if (config.runMode == "docker"):
            WebtopUtil.run(command)
        elif config.runMode == "http-server" and not config.enableCmd:
            print("Command keyword CMD::: is not enabled for security reason.  To enable it, set 'enableCmd = True' in file 'config.py'.")
        else:
            runCmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = runCmd.communicate()
            output = stdout.decode("utf-8").replace("\n", "<br>")
            error = stderr.decode("utf-8").replace("\n", "<br>")
            if config.displayCmdOutput:
                window = "study"
                display = "<h2>Output</h2><p>{0}</p><h2>Error</h2><p>{1}</p>".format(output if output else "[no output]", error if error else "[no error]")
            #if platform.system() == "Linux":
                #subprocess.Popen([command], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            #else:
                #os.system(command)
        return (window, display, {})

    # check if espeak is installed.
    def isEspeakInstalled(self):
        espeakInstalled, _ = subprocess.Popen("which espeak", shell=True, stdout=subprocess.PIPE).communicate()
        if espeakInstalled:
            return True
        else:
            return False

    # check if module is installed.
    def isCommandInstalled(self, command):
        commandInstalled, _ = subprocess.Popen("which {0}".format(command), shell=True, stdout=subprocess.PIPE).communicate()
        if commandInstalled:
            return True
        else:
            return False

    # gtts:::
    # run google text to speech feature
    # internet is required
    def googleTextToSpeech(self, command, source):
        # Stop current playing first if any:
        self.stopTtsAudio()

        # Language codes: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        if command.count(":::") != 0:
            language, text = self.splitCommand(command)
        else:
            language = "en-GB" if config.isGoogleCloudTTSAvailable else "en"
            text = command
        
        # fine-tune
        text, language = self.parent.fineTuneGtts(text, language)

        try:
            if config.runMode == "terminal" and config.terminalEnableTermuxAPI:
                # Option 1
                config.mainWindow.createAudioPlayingFile()
                text = re.sub("(\. |。)", r"\1＊", text)
                for i in text.split("＊"):
                    if not os.path.isfile(config.audio_playing_file):
                        break
                    print(i)
                    pydoc.pipepager(i, cmd=f"termux-tts-speak -l {language} -r {config.terminalTermuxttsSpeed}")
                config.mainWindow.removeAudioPlayingFile()
                # Output file shared by option 2 and option 3
                #outputFile = os.path.join("terminal_history", "gtts")
                #with open(outputFile, "w", encoding="utf-8") as f:
                #    f.write(text)
                #command = f"cat {outputFile} | termux-tts-speak -l {language} -r {config.terminalTermuxttsSpeed}"
                # Option 2
                #WebtopUtil.run(command)
                # Option 3
                #config.cliTtsProcess = subprocess.Popen([command], shell=True, preexec_fn=os.setpgrp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                # Define default tts language
                config.ttsDefaultLangauge = language
                return ("", "", {})
            else:
                if config.isGoogleCloudTTSAvailable:
                    if self.parent is not None:
                        self.parent.saveCloudTTSAudio(text, language)
                else:
                    if self.parent is not None:
                        self.parent.saveGTTSAudio(text, language)

                audioFile = self.parent.getGttsFilename()
                if os.path.isfile(audioFile):
                    self.openMediaPlayer(audioFile, "main", gui=False)
        except:
            if config.developer:
                print(traceback.format_exc())
            else:
                if self.parent is not None:
                    self.parent.displayMessage(config.thisTranslation["message_fail"])

# Keep the following codes for future reference
# The following method does not work on Windows
#        if not platform.system(") == "Windows" and (Gtts" in config.enabled):
#            if not self.isCommandInstalled("gtts-cli"):
#                installmodule("gTTS")
#            if self.isCommandInstalled("gtts-cli") and self.isCommandInstalled("play"):
#                command = "gtts-cli '{0}' --lang {1} --nocheck | play -t mp3 -".format(text, language)
#                print(command)
#                self.cliTtsProcess = subprocess.Popen([command], shell=True, preexec_fn=os.setpgrp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
#            elif self.isCommandInstalled("gtts-cli") and not self.isCommandInstalled("play"):
#                message = "Install sox FIRST! \nFor examples, run: \non macOS, 'brew install sox' \non Ubuntu / Debian, 'sudo apt install sox' \non Arch Linux, 'sudo pacman -S sox'"
#                self.parent.displayMessage(message)
#            elif not self.isCommandInstalled("gtts-cli") and not self.isCommandInstalled("play"):
#                message = "Install gTTS and sox FIRST! \nFor example, on Arch Linux, run:\n'pip3 install gTSS' and \n'sudo pacman -S sox'"
#                self.parent.displayMessage(message)
        return ("", "", {})

    # speak:::
    # run text to speech feature
    def textToSpeech(self, command, source):
        def getHideOutputSuffix():
            return f" > /dev/null 2>&1"
        if config.forceOnlineTts:
            return self.googleTextToSpeech(command, source)
        # Stop current playing first if any:
        self.stopTtsAudio()

        # Language codes: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        language = config.ttsDefaultLangauge
        text = command
        if command.count(":::") != 0:
            language, text = self.splitCommand(command)

        if language.startswith("["):
            if language in config.macVoices:
                # save a text file first to avoid quotation marks in the text
                if language.startswith("[el_GR]"):
                    text = TextUtil.removeVowelAccent(text)
                with open('temp/temp.txt', 'w') as file:
                    file.write(text)
                voice = re.sub("^\[.*?\] ", "", language)
                # The following does not support "stop" feature
                #WebtopUtil.run(f"say -v {voice} -f temp/temp.txt")
                command = f"say -r {config.macOSttsSpeed} -v {voice} -f temp/temp.txt"
                self.cliTtsProcess = subprocess.Popen([command], shell=True, preexec_fn=os.setpgrp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                if self.parent is not None:
                    self.parent.displayMessage(config.thisTranslation["message_noTtsVoice"])
        else:
            # espeak has no support of "ko", "ko" here is used to correct detection of traditional chinese
            # It is not recommended to use "ko" to correct language detection for "zh-tw", if qt built-in tts engine is used.
            # Different from espeak, Qt text-to-speech has a qlocale on Korean.
            # If the following two lines are uncommented, Korean text cannot be read.
            # In case the language is wrongly detected, users can still use command line to specify a correct language.
            if (config.espeak) and (language == "ko"):
                language = "zh-tw"
            if (language == "zh-cn") or (language == "zh-tw"):
                if config.ttsChineseAlwaysCantonese:
                    language = "zh-tw"
                elif config.ttsChineseAlwaysMandarin:
                    language = "zh-cn"
            elif (language == "en") or (language == "en-gb"):
                if config.ttsEnglishAlwaysUS:
                    language = "en"
                elif config.ttsEnglishAlwaysUK:
                    language = "en-gb"
            elif (language == "el"):
                # Modern Greek
                #language = "el"
                # Ancient Greek
                # To read accented Greek text, language have to be "grc" instead of "el" for espeak
                # In dictionary mapping language to qlocale, we use "grc" for Greek language too.
                language = "grc"
            elif (config.espeak) and (language == "he"):
                # espeak itself does not support Hebrew language
                # Below workaround on Hebrew text-to-speech feature for espeak
                # Please note this workaround is not a perfect solution, but something workable.
                text = HebrewTransliteration().transliterateHebrew(text)
                # Use "grc" to read, becuase it sounds closer to "he" than "en" does.
                language = "grc"

            if platform.system() == "Linux" and config.piper and (shutil.which("cvlc") or shutil.which("aplay")):
                model_dir = os.path.join(os.getcwd(), "audio")
                model_path = f"""{os.path.join(model_dir, config.piperVoice)}.onnx"""
                model_config_path = f"""{model_path}.json"""
                if os.path.isfile(model_path):
                    if shutil.which("cvlc"):
                        cmd = f'''"{shutil.which("piper")}" --model "{model_path}" --config "{model_config_path}" --output-raw | cvlc --play-and-exit --rate {config.vlcSpeed} --demux=rawaud --rawaud-channels=1 --rawaud-samplerate=22050 -{getHideOutputSuffix()}'''
                    elif shutil.which("aplay"):
                        cmd = f'''"{shutil.which("piper")}" --model "{model_path}" --config "{model_config_path}" --output-raw | aplay -r 22050 -f S16_LE -t raw -{getHideOutputSuffix()}'''
                else:
                    print("[Downloading voice ...] ")
                    if shutil.which("cvlc"):
                        cmd = f'''"{shutil.which("piper")}" --model {config.piperVoice} --download-dir "{model_dir}" --data-dir "{model_dir}" --output-raw | cvlc --play-and-exit --rate {config.vlcSpeed} --demux=rawaud --rawaud-channels=1 --rawaud-samplerate=22050 -{getHideOutputSuffix()}'''
                    elif shutil.which("aplay"):
                        cmd = f'''"{shutil.which("piper")}" --model {config.piperVoice} --download-dir "{model_dir}" --data-dir "{model_dir}" --output-raw | aplay -r 22050 -f S16_LE -t raw -{getHideOutputSuffix()}'''
                pydoc.pipepager(text, cmd=cmd)
            elif platform.system() == "Linux" and config.espeak:
                if WebtopUtil.isPackageInstalled("espeak"):
                    isoLang2epeakLang = TtsLanguages().isoLang2epeakLang
                    languages = isoLang2epeakLang.keys()
                    if not (config.ttsDefaultLangauge in languages):
                        config.ttsDefaultLangauge = "en"
                    if not (language in languages):
                        if config.runMode == "terminal":
                            print(f"'{language}' is not found!")
                            print("Available languages:", languages)
                        else:
                            if self.parent is not None:
                                self.parent.displayMessage(config.thisTranslation["message_noTtsVoice"])
                        language = config.ttsDefaultLangauge
                        print(f"Language changed to '{language}'")
                    language = isoLang2epeakLang[language][0]
                    # subprocess is used
                    WebtopUtil.run("espeak -s {0} -v {1} '{2}'".format(config.espeakSpeed, language, text))
                else:
                    if self.parent is not None:
                        self.parent.displayMessage(config.thisTranslation["message_noEspeak"])
            else:
                # use qt built-in tts engine
                engineNames = QTextToSpeech.availableEngines()
                if engineNames:
                    self.qtTtsEngine = QTextToSpeech(engineNames[0])
                    #locales = self.qtTtsEngine.availableLocales()
                    #print(locales)

                    isoLang2qlocaleLang = TtsLanguages().isoLang2qlocaleLang
                    languages = TtsLanguages().isoLang2qlocaleLang.keys()
                    if not (config.ttsDefaultLangauge in languages):
                        config.ttsDefaultLangauge = "en"
                    if not (language in languages):
                        if self.parent is not None:
                            self.parent.displayMessage(config.thisTranslation["message_noTtsVoice"])
                        language = config.ttsDefaultLangauge
                    self.qtTtsEngine.setLocale(isoLang2qlocaleLang[language][0])

                    self.qtTtsEngine.setVolume(1.0)
                    engineVoices = self.qtTtsEngine.availableVoices()
                    if engineVoices:
                        self.qtTtsEngine.setVoice(engineVoices[0])

                        # Control speed here
                        self.qtTtsEngine.setRate(config.qttsSpeed)

                        self.qtTtsEngine.say(text)
                    else:
                        if self.parent is not None:
                            self.parent.displayMessage(config.thisTranslation["message_noTtsVoice"])
        return ("", "", {})

    def stopTtsAudio(self):
        if self.parent is not None:
            self.parent.closeMediaPlayer()
#        if self.cliTtsProcess is not None:
#            #print(self.cliTtsProcess)
#            # The following two lines do not work:
#            #self.cliTtsProcess.kill()
#            #self.cliTtsProcess.terminate()
#            # Therefore, we use:
#            try:
#                os.killpg(os.getpgid(self.cliTtsProcess.pid), signal.SIGTERM)
#            except:
#                pass
#            self.cliTtsProcess = None
#        elif self.qtTtsEngine is not None:
#            self.qtTtsEngine.stop()

    def terminalDownloadYoutubeFile(self, downloadCommand, command, outputFolder):
        if self.isFfmpegInstalled():
            try:
                print(config.mainWindow.divider)
                #print("Downloading ...")
                #subprocess.run(["cd {2}; {0} {1}".format(downloadCommand, command, outputFolder)], shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
                # use os.system instead, as it displays download status ...
                os.system("cd {2}; {0} {1}".format(downloadCommand, command, outputFolder))
                if WebtopUtil.isPackageInstalled("pkill"):
                    os.system("pkill yt-dlp")
                print(f"Downloaded in directory '{outputFolder}'!")
            except:
                print("Errors!")
            #except subprocess.CalledProcessError as err:
                #config.mainWindow.displayMessage(err, title="ERROR:")
                
        else:
            print("Tool 'ffmpeg' is not found on your system!")
        return ("", "", {})

    # mp3:::
    def mp3Download(self, command, source):
        downloadCommand = "yt-dlp -x --audio-format mp3"

        if config.runMode == "terminal":
            return self.terminalDownloadYoutubeFile(downloadCommand, command, config.musicFolder)
        else:
            self.downloadYouTubeFile(downloadCommand, command, config.musicFolder)
        """
        if not platform.system() == "Linux":
            # version 1: known issue - the download process blocks the main window
            self.downloadYouTubeFile(downloadCommand, command, config.musicFolder)
        else:
            # version 2: known issue - only works on Linux, but not macOS or Windows
            multiprocessing.Process(target=self.downloadYouTubeFile, args=(downloadCommand, command, config.musicFolder)).start()
            if self.parent is not None:
                self.parent.displayMessage(config.thisTranslation["downloading"])
        """
        #self.parent.reloadResources()
        return ("", "", {})

    # mp4:::
    def mp4Download(self, command, source):
        downloadCommand = "yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"

        if config.runMode == "terminal":
            return self.terminalDownloadYoutubeFile(downloadCommand, command, config.videoFolder)
        else:
            self.downloadYouTubeFile(downloadCommand, command, config.videoFolder)
        """
        if not platform.system() == "Linux":
            # version 1: known issue - the download process blocks the main window
            self.downloadYouTubeFile(downloadCommand, command, config.videoFolder)
        else:
            # version 2: known issue - only works on Linux, but not macOS or Windows
            multiprocessing.Process(target=self.downloadYouTubeFile, args=(downloadCommand, command, config.videoFolder)).start()
            if self.parent is not None:
                self.parent.displayMessage(config.thisTranslation["downloading"])
        """
        #self.parent.reloadResources()
        return ("", "", {})

    def youtubeDownload(self, downloadCommand, youTubeLink):
        self.downloadYouTubeFile(downloadCommand, youTubeLink, config.videoFolder)
        """
        if not platform.system() == "Linux":
            # version 1: known issue - the download process blocks the main window
            self.downloadYouTubeFile(downloadCommand, youTubeLink, config.videoFolder)
        else:
            # version 2: known issue - only works on Linux, but not macOS or Windows
            multiprocessing.Process(target=self.downloadYouTubeFile, args=(downloadCommand, youTubeLink, config.videoFolder)).start()
            if self.parent is not None:
                self.parent.displayMessage(config.thisTranslation["downloading"])
        """
        #self.parent.reloadResources()

    def isFfmpegInstalled(self):
        ffmpegVersion = subprocess.Popen("ffmpeg -version", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        *_, stderr = ffmpegVersion.communicate()
        return False if stderr else True

    def getYouTubeDownloadOptions(self, url):
        options = subprocess.Popen("yt-dlp --list-formats {0}".format(url), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, *_ = options.communicate()
        options = stdout.decode("utf-8").split("\n")
        return [option for option in options if re.search(r"^[0-9]+? ", option)]

    def downloadYouTubeFile(self, downloadCommand, youTubeLink, outputFolder, noFfmpeg=False):
        # Download / upgrade to the latest version
        if not hasattr(config, "youtubeDlIsUpdated") or (hasattr(config, "youtubeDlIsUpdated") and not config.youtubeDlIsUpdated):
            installmodule("--upgrade yt-dlp")
            config.youtubeDlIsUpdated = True
        if self.isFfmpegInstalled() or not noFfmpeg:
            if config.runMode in ("", "cli", "gui"):
                if self.parent is not None:
                    self.parent.workOnDownloadYouTubeFile(downloadCommand, youTubeLink, outputFolder)
            """
            elif platform.system() == "Linux":
                try:
                    subprocess.run(["cd {2}; {0} {1}".format(downloadCommand, youTubeLink, outputFolder)], shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                    subprocess.Popen([config.open, outputFolder])
                except subprocess.CalledProcessError as err:
                    if self.parent is not None:
                        self.parent.displayMessage(err, title="ERROR:")
            # on Windows
            elif platform.system() == "Windows":
                try:
                    os.system(r"cd .\{2}\ & {0} {1}".format(downloadCommand, youTubeLink, outputFolder))
                    os.system(r"{0} {1}".format(config.open, outputFolder))
                except:
                    if self.parent is not None:
                        self.parent.displayMessage(config.thisTranslation["noSupportedUrlFormat"], title="ERROR:")
            # on Unix-based system, like macOS
            else:
                try:
                    os.system(r"cd {2}; {0} {1}".format(downloadCommand, youTubeLink, outputFolder))
                    if (config.runMode == "docker"):
                        WebtopUtil.openDir(dir)
                    else:
                        os.system(r"{0} {1}".format(config.open, outputFolder))
                except:
                    if self.parent is not None:
                        self.parent.displayMessage(config.thisTranslation["noSupportedUrlFormat"], title="ERROR:")
            """
        else:
            if self.parent is not None:
                self.parent.displayMessage(config.thisTranslation["ffmpegNotFound"])
            wikiPage = "https://github.com/eliranwong/UniqueBible/wiki/Install-ffmpeg"
            if config.enableHttpServer:
                subprocess.Popen("{0} {1}".format(config.open, wikiPage), shell=True)
            else:
                webbrowser.open(wikiPage)

    def keyToStopStreaming(self, playback_event):
        async def readKeys() -> None:
            done = False
            input = create_input()

            def keys_ready():
                nonlocal done
                for key_press in input.read_keys():
                    #print(key_press)
                    if key_press.key in (Keys.ControlQ, Keys.ControlZ):
                        print("\nStopping audio playback ...")
                        if self.parent is not None:
                            self.parent.closeMediaPlayer()
                        done = True
                        playback_event.set()

            with input.raw_mode():
                with input.attach(keys_ready):
                    while not done:
                        if config.playback_finished:
                            break
                        await asyncio.sleep(0.1)

        asyncio.run(readKeys())

    # READSYNC:::
    def textReadSync(self, command, source):
        return self.textRead(command, source, True) if config.runMode == "terminal" else ("study", "Currently, only terminal mode supports running READSYNC::: command.", {})

    # READ:::
    def textRead(self, command, source, displayText=False):
        if command.count(":::") == 0:
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            command = "{0}:::{1}".format(viewText, command)
        texts, references = self.splitCommand(command)
        texts = list(set([FileUtil.getMP3TextFile(text) for text in self.getConfirmedTexts(texts)]))
        verseList = self.extractAllVerses(references)
        if verseList:
            allPlayList = []
            allTextList = []
            for verse in verseList:
                for text in texts:
                    everySingleVerseList = Bible(text).getEverySingleVerseList((verse,))
                    playlist = []
                    textList = []
                    for b, c, v in everySingleVerseList:
                        folder = os.path.join(config.audioFolder, "bibles", text, "default", "{0}_{1}".format(b, c))
                        audioFile = os.path.join(folder, "{0}_{1}_{2}_{3}.mp3".format(text, b, c, v))
                        if os.path.isfile(audioFile):
                            playlist.append(audioFile)
                            if config.runMode == "terminal" and displayText:
                                try:
                                    *_, verseText = Bible(text).readTextVerse(b, c, v)
                                    verseText = TextUtil.htmlToPlainText(f"[<ref>{self.bcvToVerseReference(b, c, v)}</ref> ]{verseText}").strip()
                                    verseText = verseText.replace("audiotrack ", "")
                                    textList.append(verseText)
                                except:
                                    textList.append("")
                    allPlayList += playlist
                    allTextList += textList
            if config.enableHttpServer:
                target = "study"
                allPlayList = [(os.path.basename(fullpath), fullpath) for fullpath in allPlayList]
                content = HtmlGeneratorUtil().getAudioPlayer(allPlayList)
            else:
                target = ""
                content = ""
                if config.runMode == "terminal":
                    # Create a new thread for the streaming task
                    config.playback_finished = False
                    playback_event = threading.Event()
                    if displayText:
                        self.playback_thread = threading.Thread(target=self.parent.playAudioBibleFilePlayListPlusDisplayText, args=(allPlayList, allTextList, False, playback_event))
                    else:
                        self.playback_thread = threading.Thread(target=self.parent.playAudioBibleFilePlayList, args=(allPlayList,))
                    # Start the streaming thread
                    self.playback_thread.start()

                    # wait while text output is steaming; capture key combo 'ctrl+q' or 'ctrl+z' to stop the streaming
                    self.keyToStopStreaming(playback_event)

                    # when streaming is done or when user press "ctrl+q"
                    self.playback_thread.join()

                    # old way
                    #self.parent.playAudioBibleFilePlayListPlusDisplayText(allPlayList, allTextList) if displayText else self.parent.playAudioBibleFilePlayList(allPlayList)
                else:
                    if self.parent is not None:
                        self.parent.playAudioBibleFilePlayList(allPlayList)
            return (target, content, {})
        else:
            return self.invalidCommand()

    # READCHAPTER:::
    def readChapter(self, command, source):
        #try:
        content = ""
        target = "study" if config.enableHttpServer else ""
        items = command.split(".")
        if len(items) == 3:
            text, b, c = items
            if config.enableHttpServer:
                playlist = self.parent.playAudioBibleChapterVerseByVerse(text, b, c)
                content = HtmlGeneratorUtil().getAudioPlayer(playlist)
            else:
                if self.parent is not None:
                    self.parent.playAudioBibleChapterVerseByVerse(text, b, c)
        elif len(items) == 4:
            text, b, c, startVerse = items
            if config.enableHttpServer:
                playlist = self.parent.playAudioBibleChapterVerseByVerse(text, b, c, int(startVerse))
                content = HtmlGeneratorUtil().getAudioPlayer(playlist)
            else:
                if self.parent is not None:
                    self.parent.playAudioBibleChapterVerseByVerse(text, b, c, int(startVerse))
        return (target, content, {})
        #except:
        #    return self.invalidCommand()

    # READVERSE:::
    def readVerse(self, command, source):
        if self.parent is not None:
            self.parent.closeMediaPlayer()
        text, b, c, v = command.split(".")
        folder = os.path.join(config.audioFolder, "bibles", text, "default", "{0}_{1}".format(b, c))
        filename = "{0}_{1}_{2}_{3}.mp3".format(text, b, c, v)
        audioFile = os.path.join(folder, filename)
        if os.path.isfile(audioFile):
            if config.enableHttpServer:
                playlist = [(filename, audioFile)]
                content = HtmlGeneratorUtil().getAudioPlayer(playlist)
                return ("study", content, {})
            else:
                try:
                    if config.mainWindow.audioPlayer is not None:
                        config.mainWindow.addToAudioPlayList(audioFile, True)
                    elif config.isVlcAvailable:
                        VlcUtil.playMediaFile(audioFile, config.vlcSpeed, (not config.hideVlcInterfaceReadingSingleVerse))
                    else:
                        if self.parent is not None:
                            self.parent.displayMessage(config.thisTranslation["noMediaPlayer"])
                    return ("", "", {})
                except:
                    return self.invalidCommand()
        else:
            return self.noAudio()

    # READWORD:::
    def readWord(self, command, source):
        if not source == 'http':
            if self.parent is not None:
                self.parent.closeMediaPlayer()
        text, b, c, v, wordID = command.split(".")
        folder = os.path.join(config.audioFolder, "bibles", text, "default", "{0}_{1}".format(b, c))
        filename = "{0}_{1}_{2}_{3}_{4}.mp3".format(text, b, c, v, wordID)
        audioFile = os.path.join(folder, filename)
        if os.path.isfile(audioFile):
            if config.enableHttpServer:
                playlist = [(filename, audioFile)]
                content = HtmlGeneratorUtil().getAudioPlayer(playlist)
                return ("study", content, {})
            else:
                try:
                    if config.mainWindow.audioPlayer is not None:
                        config.mainWindow.addToAudioPlayList(audioFile, True)
                    elif config.isVlcAvailable:
                        VlcUtil.playMediaFile(audioFile, config.vlcSpeed, False)
                    else:
                        if self.parent is not None:
                            self.parent.displayMessage(config.thisTranslation["noMediaPlayer"])
                    return ("", "", {})
                except:
                    return self.invalidCommand()
        else:
            if text == "BHS5":
                return self.noHebrewAudio()
            if text == "OGNT":
                return self.noGreekAudio()
            else:
                return self.noAudio()

    # READLEXEME:::
    def readLexeme(self, command, source):
        if self.parent is not None:
            self.parent.closeMediaPlayer()
        text, b, c, v, wordID = command.split(".")
        folder = os.path.join(config.audioFolder, "bibles", text, "default", "{0}_{1}".format(b, c))
        filename = "lex_{0}_{1}_{2}_{3}_{4}.mp3".format(text, b, c, v, wordID)
        audioFile = os.path.join(folder, filename)
        if os.path.isfile(audioFile):
            if config.enableHttpServer:
                playlist = [(filename, audioFile)]
                content = HtmlGeneratorUtil().getAudioPlayer(playlist)
                return ("study", content, {})
            else:
                try:
                    if config.mainWindow.audioPlayer is not None:
                        config.mainWindow.addToAudioPlayList(audioFile, True)
                    elif config.isVlcAvailable:
                        VlcUtil.playMediaFile(audioFile, config.vlcSpeed, False)
                    else:
                        if self.parent is not None:
                            self.parent.displayMessage(config.thisTranslation["noMediaPlayer"])
                    return ("", "", {})
                except:
                    return self.invalidCommand()
        else:
            if text == "BHS5":
                return self.noHebrewAudio()
            if text == "OGNT":
                return self.noGreekAudio()
            else:
                return self.noAudio()

    # MEDIA:::
    def openMediaPlayer(self, command, source, gui=True):
        command = command.strip()
        if not os.path.isfile(command):
            return self.invalidCommand()
        if self.parent is not None:
            self.parent.closeMediaPlayer()
        try:
            if config.mainWindow.audioPlayer is not None:
                config.mainWindow.addToAudioPlayList(command, True)
            elif config.isVlcAvailable:
                VlcUtil.playMediaFile(command, config.vlcSpeed, gui)
            else:
                if self.parent is not None:
                    self.parent.displayMessage(config.thisTranslation["noMediaPlayer"])
        except:
            WebtopUtil.openFile(command)
        return ("", "", {})

    # READBIBLE:::
    def readBible(self, command, source):
        text = config.mainText
        book = config.mainB
        chapter = config.mainC
        folder = config.defaultMP3BibleFolder
        playlist = []
        if command:
            count = command.count(":::")
            if count == 0:
                if command.startswith("@"):
                    folder = command[1:]
                    playlist.append((text, book, chapter, None, folder))
                else:
                    playlist = self.getBiblePlaylist(command, text, folder)
            elif count == 1:
                text, reference = self.splitCommand(command)
                playlist = self.getBiblePlaylist(reference, text, folder)
            elif count == 2:
                text, commandList = self.splitCommand(command)
                reference, folder = self.splitCommand(commandList)
                playlist = self.getBiblePlaylist(reference, text, folder)
        else:
            playlist.append((text, book, chapter, None, folder))
        if self.parent is not None:
            self.parent.playBibleMP3Playlist(playlist)
        return ("", "", {})

    def getBiblePlaylist(self, command, text, folder):
        playlist = []
        if "," in command:
            parts = command.split(",")
            for part in parts:
                verseList = self.extractAllVerses(part)
                book, chapter, verse = verseList[0]
                playlist.append((text, book, chapter, None, folder))
        elif "-" in command:
            start, end = command.split("-")
            verseList = self.extractAllVerses(start)
            book, chapter, verse = verseList[0]
            if ":" in start:
                for index in range(int(verse), int(end)+1):
                    playlist.append((text, book, chapter, index, folder))
            else:
                for index in range(int(chapter), int(end)+1):
                    playlist.append((text, book, index, None, folder))
        else:
            verseList = self.extractAllVerses(command)
            book, chapter, verse = verseList[0]
            if ":" not in command:
                verse = None
            playlist.append((text, book, chapter, verse, folder))
        return playlist

    # functions about bible

    # outline:::
    def textBookOutline(self, command, source):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            b, *_ = verseList[0]
            bookName = BibleBooks.abbrev["eng"][str(b)][-1]
            content = f"<h2>{bookName}</h2>"
            for c in Bible(config.mainText).getChapterList(b):
                #subheadings = BiblesSqlite().getChapterSubheadings(b, c)
                subheadings = AGBTSData().getChapterFormattedSubheadings(b, c)
                content += f"<p>{subheadings}</p>"
            return ("study", content, {})

    # overview:::
    def textChapterOverview(self, command, source):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            content = ""
            for b, c, *_ in verseList:
                chapterReference = self.bcvToVerseReference(b, c, 1)[:-2]
                #subheadings = BiblesSqlite().getChapterSubheadings(b, c)
                subheadings = AGBTSData().getChapterFormattedSubheadings(b, c)
                if subheadings:
                    subheadings = "<p>{0}</p>".format(subheadings)
                parallels = CollectionsSqlite().getChapterParallels(b, c)
                if parallels:
                    parallels = "<hr><p><bb>Harmonies and Parallels</bb></p><p>{0}</p>".format(parallels)
                promises = CollectionsSqlite().getChapterPromises(b, c)
                if promises:
                    promises = "<hr><p><bb>Bible Promises</bb></p><p>{0}</p>".format(promises)
                content += "<p><bb>{0}</bb></p>{1}{2}{3}<hr>".format(chapterReference, subheadings, parallels, promises)
            return ("study", content, {})

    # summary:::
    def textChapterSummary(self, command, source):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            content = ""
            for b, c, *_ in verseList:
                chapterSummary =  Commentary("Brooks").getContent((b, c, 1))
                if chapterSummary:
                    chapterSummary = "<p><bb>Complete Summary of the Bible (Brooks)</bb></p><p>{0}</p><hr>".format(chapterSummary)
                content += chapterSummary
            return ("study", content, {})

    # CONCORDANCE:::
    def textConcordance(self, command, source):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format("OHGBi", command)
        texts, strongNo = self.splitCommand(command)
        if texts == "ALL":
            texts = self.parent.strongBibles
        else:
            texts = self.getConfirmedTexts(texts)
            texts = ["OHGBi" if text in ("MOB", "MIB", "MTB", "MAB", "MPB", "OHGB") else text for text in texts]
            texts = [text for text in texts if text in self.parent.strongBibles]
            texts = list(set(texts))
        if not texts or not re.match("^[EGH][0-9]+?$", strongNo):
            return self.invalidCommand()
        else:
            config.concordance = texts[-1]
            config.concordanceEntry = strongNo
            html = "<hr>".join([Bible(text).formatStrongConcordance(strongNo) for text in texts])
            return ("study", html, {})

    def cancelBibleParallels(self):
        if config.runMode == "terminal":
            config.terminalBibleParallels = False
            config.terminalBibleComparison = False

    # DISPLAYWORDFREQUENCY:::KJVx:::Matt 1
    # DISPLAYWORDFREQUENCY:::KJVx:::Matt 1:::custom
    def displayWordFrequency(self, command, source):
        customFile = "custom"
        if command.count(":::") == 2:
            texts, references, customFile = command.split(":::")
        else:
            texts, references = command.split(":::")
        config.readFormattedBibles = False
        statisticsSqlite = StatisticsWordsSqlite()

        data = self.textBible(f"{texts}:::{references}", source)

        text = data[1]
        matches = re.findall(r" ([GH][0-9]*?) ", text)

        highlightMapping = statisticsSqlite.loadHighlightMappingFile(customFile)

        for strongs in set(matches):
            frequency = statisticsSqlite.getFrequency(strongs)
            color = ""
            for map in highlightMapping:
                if frequency >= int(map[0]) and frequency <= int(map[1]):
                    if config.theme in ("dark", "night"):
                        color = map[3]
                    else:
                        color = map[2]
            if color:
                text = statisticsSqlite.addHighlightTagToPreviousWord(text, strongs, color, frequency)
        return (data[0], text, data[2])

    # BIBLE:::
    def textBible(self, command, source):
        if command.count(":::") == 0:
            if config.openBibleInMainViewOnly:
                updateViewConfig, viewText, *_ = self.getViewConfig("main")
            else:
                updateViewConfig, viewText, *_ = self.getViewConfig(source)
            command = "{0}:::{1}".format(viewText, command)
        texts, references = self.splitCommand(command)
        texts = self.getConfirmedTexts(texts)
        marvelBibles = self.getMarvelBibles()
        if not texts:
            return self.invalidCommand()
        else:
            self.cancelBibleParallels()
            text = texts[0]
            if text in marvelBibles:
                fileItems = marvelBibles[text][0]
                if os.path.isfile(os.path.join(*fileItems)):
                    return self.textBibleVerseParser(references, text, source)
                else:
                    databaseInfo = marvelBibles[text]
                    if self.parent is not None:
                        self.parent.downloadHelper(databaseInfo)
                    return ("", "", {})
            else:
                return self.textBibleVerseParser(references, text, source)

    # TEXT:::
    def textText(self, command, source):
        texts = self.getConfirmedTexts(command)
        if not texts:
            return self.invalidCommand()
        else:
            self.cancelBibleParallels()
            marvelBibles = self.getMarvelBibles()
            text = texts[0]
            if text in marvelBibles:
                fileItems = marvelBibles[text][0]
                if os.path.isfile(os.path.join(*fileItems)):
                    if config.enforceCompareParallel:
                        if self.parent is not None:
                            self.parent.enforceCompareParallelButtonClicked()
                    updateViewConfig, viewText, viewReference, *_ = self.getViewConfig(source)
                    return self.textBibleVerseParser(viewReference, texts[0], source)
                else:
                    databaseInfo = marvelBibles[text]
                    if self.parent is not None:
                        self.parent.downloadHelper(databaseInfo)
                    return ("", "", {})
            else:
                if config.enforceCompareParallel:
                    if self.parent is not None:
                        self.parent.enforceCompareParallelButtonClicked()
                updateViewConfig, viewText, viewReference, *_ = self.getViewConfig(source)
                return self.textBibleVerseParser(viewReference, texts[0], source)

    # _chapters:::
    def textChapters(self, command, source):
        texts = self.getConfirmedTexts(command)
        if not texts:
            return self.invalidCommand()
        else:
            books = BibleBooks().booksMap.get(config.standardAbbreviation, BibleBooks.abbrev["eng"])

            text = texts[0]
            bible = Bible(text)
            info = bible.bibleInfo()
            bookList = bible.getBookList()
            html = """<h2 style='text-align: center;'>{0} <button title='{1}' type='button' class='ubaButton' onclick='document.title="_menu:::"'><span class="material-icons-outlined">more_vert</span></button></h2>""".format(info, config.thisTranslation["menu_more"])
            for bNo in bookList:
                if bNo == config.mainB:
                    html += f'<span id="v{config.mainB}.{config.mainC}.{config.mainV}"></span>'
                bkNoStr = str(bNo)
                if bkNoStr in books:
                    abb = books[bkNoStr][0]
                    chapterList = bible.getChapterList(bNo)
                    commandPrefix = f"_verses:::{text}:::{abb} "
                    html += HtmlGeneratorUtil.getBibleChapterTable(books[bkNoStr][1], abb, chapterList, commandPrefix)
            return (source, html, {})

    # _verses:::
    def textVerses(self, command, source):
        if command.count(":::") == 0:
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            command = "{0}:::{1}".format(viewText, command)
        texts, references = self.splitCommand(command)
        texts = self.getConfirmedTexts(texts)
        verseList = self.extractAllVerses(references)
        if texts and verseList:
            text = texts[0]
            books = BibleBooks().booksMap.get(config.standardAbbreviation, BibleBooks.abbrev["eng"])
            b, c, *_ = verseList[0]
            abb = books[str(b)][0]
            bible = Bible(text)
            chapterVerseList = bible.getVerseList(b, c)
            window = "STUDY" if source.lower() == "study" else "BIBLE"
            commandPrefix = f"{window}:::{text}:::{abb} {c}:"
            html = "<h2 style='text-align: center;'>{0}</h2>".format(text)
            html += HtmlGeneratorUtil.getBibleVerseTable(books[str(b)][1], abb, c, chapterVerseList, commandPrefix)
            return (source, html, {})
        else:
            return self.invalidCommand()

    # _commentaries:::
    def textCommentaries(self, command, source):
        html = ""
        for index, text in enumerate(self.parent.commentaryList):
            fullName = self.parent.commentaryFullNameList[index]
            html += """<p style='text-align: center;'><button title='{0}' type='button' class='ubaButton' onclick='document.title="_commentarychapters:::{0}"'>{1}</button></p>""".format(text, fullName)
        return ("study", html, {})

    # _commentarychapters:::
    def textCommentaryChapters(self, command, source):
        if not command in self.parent.commentaryList:
            return self.invalidCommand()
        else:
            books = BibleBooks().booksMap.get(config.standardAbbreviation, BibleBooks.abbrev["eng"])

            commentary = Commentary(command)
            bookList = commentary.getBookList()
            info = commentary.commentaryInfo()
            if info == "https://Marvel.Bible Commentary" and command in Commentary.marvelCommentaries:
                info = Commentary.marvelCommentaries[command]
            #moreLink = """<p style='text-align: center;'>[ <ref onclick="window.parent.submitCommand('.library')">{0}</ref> ]</p>""".format(config.thisTranslation["change"]) if config.enableHttpServer else ""
            html = """<h2 style='text-align: center;'>{0} <button title='{1}' type='button' class='ubaButton' onclick='document.title="_commentaries:::"'><span class="material-icons-outlined">more_vert</span></button></h2>""".format(info, config.thisTranslation["menu_more"])
            for bNo in bookList:
                bkNoStr = str(bNo)
                if bkNoStr in books:
                    abb = books[bkNoStr][0]
                    chapterList = commentary.getChapterList(bNo)
                    commandPrefix = f"_commentaryverses:::{command}:::{abb} "
                    html += HtmlGeneratorUtil.getBibleChapterTable(books[bkNoStr][1], abb, chapterList, commandPrefix)
            return ("study", html, {})

    # _commentaryverses:::
    def textCommentaryVerses(self, command, source):
        if command.count(":::") == 0:
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            command = "{0}:::{1}".format(viewText, command)
        text, references = self.splitCommand(command)
        verseList = self.extractAllVerses(references)
        if text in self.parent.commentaryList and verseList:
            b, c, *_ = verseList[0]
            if b > 0 and b <= 66:
                books = BibleBooks().booksMap.get(config.standardAbbreviation, BibleBooks.abbrev["eng"])
                abb = books[str(b)][0]
                bible = Bible("KJV")
                chapterVerseList = bible.getVerseList(b, c)
                commandPrefix = f"COMMENTARY:::{text}:::{abb} {c}:"
                html = "<h2 style='text-align: center;'>{0}</h2>".format(text)
                html += HtmlGeneratorUtil.getBibleVerseTable(books[str(b)][1], abb, c, chapterVerseList, commandPrefix)
                return ("study", html, {})
        else:
            return self.invalidCommand()

    # MAIN:::
    def textMain(self, command, source):
        return self.textAnotherView(command, source, "main")

    # STUDY:::
    def textStudy(self, command, source):
        if config.openBibleInMainViewOnly and not config.noQt:
            if self.parent is not None:
                self.parent.enableStudyBibleButtonClicked()
        return self.textAnotherView(command, source, "study")

    # STUDYTEXT:::
    def textStudyText(self, command, source):
        command = "{0}:::{1}".format(command, self.bcvToVerseReference(config.studyB, config.studyC, config.studyV))
        return self.textStudy(command, "study")

    # _copy:::
    def copyText(self, command, source):
        try:
            if config.runMode == "terminal":
                config.mainWindow.copy(command)
            elif config.qtLibrary == "pyside6":
                from PySide6.QtWidgets import QApplication
            else:
                from qtpy.QtWidgets import QApplication
            QApplication.clipboard().setText(command)
            if self.parent is not None:
                self.parent.displayMessage(config.thisTranslation["copied"])
        except:
            return self.invalidCommand()
        return ("", "", {})

    # TRANSLATE:::
    # Translate text using IBM Watson service
    # It works only if user entered their own personal credential and store in config.py locally on users' computer.
    # The store credentials are only used only for communicating with IBM Watson service with python package 'ibm-watson'
    # UBA does not collect any of these data.
    def translateText(self, command, source):
        translator = Translator()
        # Use IBM Watson service to translate text
        if translator.language_translator is not None:
            # unpack command
            if command.count(":::") == 0:
                fromLanguage = translator.identify(command)
                toLanguage = "en"
                if not fromLanguage in Translator.fromLanguageCodes:
                    fromLanguage = "en"
                if config.userLanguage in Translator.toLanguageCodes:
                    toLanguage = config.userLanguage
                text = command
            else:
                language, text = self.splitCommand(command)
                if "fr-CA" in language:
                    language = language.replace("fr-CA", "fr@CA")
                if "zh-TW" in language:
                    language = language.replace("zh-TW", "zh@TW")
                if language.count("-") != 1:
                    if self.parent is not None:
                        self.parent.displayMessage(config.thisTranslation["message_invalid"])
                else:
                    fromLanguage, toLanguage = language.split("-")
                    if "@" in fromLanguage:
                        fromLanguage = fromLanguage.replace("@", "-")
                    if "@" in toLanguage:
                        toLanguage = toLanguage.replace("@", "-")
                    if not fromLanguage in Translator.fromLanguageCodes:
                        fromLanguage = "en"
                    if not toLanguage in Translator.toLanguageCodes:
                        toLanguage = "en"
            # translate here
            translation = translator.translate(text, fromLanguage, toLanguage)
            if self.parent is not None:
                self.parent.displayMessage(translation)
            if config.autoCopyTranslateResult and not config.noQt:
                if config.qtLibrary == "pyside6":
                    from PySide6.QtWidgets import QApplication
                else:
                    from qtpy.QtWidgets import QApplication
                QApplication.clipboard().setText(translation)
        else:
            if self.parent is not None:
                self.parent.displayMessage(config.thisTranslation["ibmWatsonNotEnalbed"])
            if self.parent is not None:
                self.parent.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/IBM-Watson-Language-Translator")
        return ("", "", {})

    # This function below is an old way to process TRANSLATE::: command with goolgetrans
    # However, we found googletrans no longer works with UBA.
    # We keep the following function for further reference only.
    def translateText_old(self, command, source):
        languages = Languages().codes
        # unpack command
        if command.count(":::") == 0:
            if config.userLanguage:
                language = languages[config.userLanguage]
            else:
                language = "en"
            text = command
        else:
            language, text = self.splitCommand(command)
        # run google translate
        if language in languages.values():
            if self.parent is not None:
                self.parent.mainView.translateTextIntoUserLanguage(text, language)
        else:
            if self.parent is not None:
                self.parent.mainView.displayMessage(config.thisTranslation["message_invalid"])
        return ("", "", {})

    # called by MAIN::: & STUDY:::
    def textAnotherView(self, command, source, target):
        if command.count(":::") == 0:
            updateViewConfig, viewText, *_ = self.getViewConfig(target)
            command = "{0}:::{1}".format(viewText, command)
        texts, references = self.splitCommand(command)
        texts = self.getConfirmedTexts(texts)
        if not texts:
            return self.invalidCommand()
        else:
            self.cancelBibleParallels()
            marvelBibles = self.getMarvelBibles()
            text = texts[0]
            if text in marvelBibles:
                fileItems = marvelBibles[text][0]
                if os.path.isfile(os.path.join(*fileItems)):
                    return self.textBibleVerseParser(references, texts[0], target)
                else:
                    databaseInfo = marvelBibles[text]
                    if self.parent is not None:
                        self.parent.downloadHelper(databaseInfo)
                    return ("", "", {})
            else:
                return self.textBibleVerseParser(references, texts[0], target)

    # distinctinterlinear:::
    def distinctInterlinear(self, command, source):
        translations = MorphologySqlite().distinctMorphology(command)
        display = " | ".join(translations)
        return ("study", display, {})

    # distincttranslation:::
    def distinctTranslation(self, command, source):
        translations = MorphologySqlite().distinctMorphology(command, "Translation")
        display = " | ".join(translations)
        return ("study", display, {})

    def getAllFavouriteBibles(self):
        favouriteVersions = set([config.mainText, config.studyText, config.favouriteBible, config.favouriteBible2, config.favouriteBible3, config.favouriteBiblePrivate, config.favouriteBiblePrivate2, config.favouriteBiblePrivate3])
        return self.getConfirmedTexts("_".join(favouriteVersions))

    # COMPARE:::
    def textCompare(self, command, source):
        if command.count(":::") == 0:
            confirmedTexts = self.getAllFavouriteBibles()
            verseList = self.extractAllVerses(command)
        else:
            texts, references = self.splitCommand(command)
            confirmedTexts = self.getConfirmedTexts(texts)
            verseList = self.extractAllVerses(references)
        if not confirmedTexts or not verseList:
            return self.invalidCommand()
        else:
            if config.runMode == "terminal" and not confirmedTexts == ["ALL"]:
                config.compareParallelList = confirmedTexts
                config.terminalBibleComparison = True
            biblesSqlite = BiblesSqlite()
            config.mainCssBibleFontStyle = ""
            texts = confirmedTexts
            if confirmedTexts == ["ALL"]:
                #plainBibleList, formattedBibleList = biblesSqlite.getTwoBibleLists()
                #texts = set(plainBibleList + formattedBibleList)
                texts = self.getAllFavouriteBibles()
            for text in texts:
                (fontFile, fontSize, css) = Bible(text).getFontInfo()
                config.mainCssBibleFontStyle += css
            verses = biblesSqlite.compareVerse(verseList, confirmedTexts)
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            updateViewConfig(viewText, verseList[-1])
            return ("study" if config.compareOnStudyWindow else "main", verses, {})

    # COMPARECHAPTER:::
    def textCompareChapter(self, command, source):
        if command.count(":::") == 0:
            confirmedTexts = self.getAllFavouriteBibles()
            verseList = self.extractAllVerses(command)
        else:
            texts, references = self.splitCommand(command)
            confirmedTexts = self.getConfirmedTexts(texts)
            verseList = self.extractAllVerses(references)
        if not confirmedTexts or not verseList:
            return self.invalidCommand()
        else:
            if config.runMode == "terminal" and not confirmedTexts == ["ALL"]:
                config.compareParallelList = confirmedTexts
                config.terminalBibleComparison = True
            biblesSqlite = BiblesSqlite()
            config.mainCssBibleFontStyle = ""
            texts = confirmedTexts
            if confirmedTexts == ["ALL"]:
                #plainBibleList, formattedBibleList = biblesSqlite.getTwoBibleLists()
                texts = self.getAllFavouriteBibles()
            for text in texts:
                (fontFile, fontSize, css) = Bible(text).getFontInfo()
                config.mainCssBibleFontStyle += css
            #verses = biblesSqlite.compareVerse(verseList, confirmedTexts)
            b, c, v, *_ = verseList[0]
            verses = biblesSqlite.compareVerseChapter(b, c, v, confirmedTexts)
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            updateViewConfig(viewText, verseList[0])
            return ("study" if config.compareOnStudyWindow else "main", verses, {})

    # SIDEBYSIDE:::
    def textCompareSideBySide(self, command, source):
        if command.count(":::") == 0:
            if config.compareParallelList:
                versions = "_".join(config.compareParallelList)
                command = f"{versions}:::{command}"
            else:
                return ("", "", {})
        texts, references = self.splitCommand(command)
        confirmedTexts = self.getConfirmedTexts(texts)
        verseList = self.extractAllVerses(references)
        if not confirmedTexts or not verseList:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            config.mainCssBibleFontStyle = ""
            texts = confirmedTexts
            for text in texts:
                (fontFile, fontSize, css) = Bible(text).getFontInfo()
                config.mainCssBibleFontStyle += css
            verses = biblesSqlite.parallelVerse(verseList, confirmedTexts)
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            updateViewConfig(viewText, verseList[-1])
            if config.runMode == "terminal":
                verses = f"[BROWSER]{verses}"
            return ("study" if config.compareOnStudyWindow else "main", verses, {})

    # DIFF:::
    # DIFFERENCE:::
    def textDiff(self, command, source):
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
            verses = biblesSqlite.diffVerse(verseList, confirmedTexts)
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            updateViewConfig(viewText, verseList[-1])
            return (source, verses, {})

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
                if self.parent is not None:
                    self.parent.downloadHelper(databaseInfo)
                return ("", "", {})
            else:
                if source in ('cli'):
                    tableList = ["{0} {1}".format(text, self.textBibleVerseParser(references, text, source, True)[1])
                                 for text in confirmedTexts]
                    return("study" if config.compareOnStudyWindow else "main", "<br>".join(tableList), {})
                else:
                    mainText = config.mainText
                    tableList = [("<th><ref onclick='document.title=\"TEXT:::{0}\"'>{0}</ref></th>".format(text),
                                  "<td style='vertical-align: text-top;'><bibletext class={1}>{0}</bibletext></td>"
                                  .format(self.textBibleVerseParser(references, text, source, True)[1], text))
                                 for text in confirmedTexts]
                    versions, verses = zip(*tableList)
                    config.maiupdateViewConfignCssBibleFontStyle = ""
                    for text in confirmedTexts:
                        (fontFile, fontSize, css) = Bible(text).getFontInfo()
                        config.mainCssBibleFontStyle += css
                    config.mainText = mainText
                    if self.parent is not None:
                        self.parent.setBibleSelection()
                    return ("study" if config.compareOnStudyWindow else "main", "<table style='width:100%; table-layout:fixed;'><tr>{0}</tr><tr>{1}</tr></table>".format("".join(versions), "".join(verses)), {})

   # PASSAGES:::
    def textPassages(self, command, source):
        updateViewConfig, viewText, *_ = self.getViewConfig(source)
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(viewText, command)
        texts, references = self.splitCommand(command)
        confirmedTexts = self.getConfirmedTexts(texts)
        if not confirmedTexts:
            return self.invalidCommand()
        else:
            text = confirmedTexts[0]
            marvelBibles = self.getMarvelBibles()
            if text in marvelBibles and not os.path.isfile(os.path.join(*marvelBibles[text][0])):
                databaseInfo = marvelBibles[text]
                if self.parent is not None:
                    self.parent.downloadHelper(databaseInfo)
                return ("", "", {})
            else:
                bibleVerseParser = BibleVerseParser(config.parserStandarisation)
                biblesSqlite = BiblesSqlite()
                passages = bibleVerseParser.extractAllReferences(references)
                if passages:
                    tableList = [("<th><ref onclick='document.title=\"BIBLE:::{0}\"'>{0}</ref></th>".format(bibleVerseParser.bcvToVerseReference(*passage)), "<td style='vertical-align: text-top;'>{0}</td>".format(biblesSqlite.readMultipleVerses(text, [passage], displayRef=False))) for passage in passages]
                    versions, verses = zip(*tableList)
                    b, c, v, *_ = passages[-1]
                    updateViewConfig(text, (b, c, v))
                    return (source, "<table style='width:100%; table-layout:fixed;'><tr>{0}</tr><tr>{1}</tr></table>".format("".join(versions), "".join(verses)), {})
                else:
                    return self.invalidCommand()

    # _harmony:::
    def textHarmony(self, command, source):
        updateViewConfig, viewText, *_ = self.getViewConfig(source)
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(viewText, command)
        texts, references = self.splitCommand(command)
        confirmedTexts = self.getConfirmedTexts(texts)
        if not confirmedTexts:
            return self.invalidCommand()
        else:
            text = confirmedTexts[0]
            marvelBibles = self.getMarvelBibles()
            if text in marvelBibles and not os.path.isfile(os.path.join(*marvelBibles[text][0])):
                databaseInfo = marvelBibles[text]
                if self.parent is not None:
                    self.parent.downloadHelper(databaseInfo)
                return ("", "", {})
            else:
                bibleVerseParser = BibleVerseParser(config.parserStandarisation)
                biblesSqlite = BiblesSqlite()
                cs = CollectionsSqlite()
                topic, passagesString = cs.readData("PARALLEL", references.split("."))
                passages = bibleVerseParser.extractAllReferences(passagesString, tagged=True)
                tableList = [("<th><ref onclick='document.title=\"BIBLE:::{0}\"'>{0}</ref></th>".format(bibleVerseParser.bcvToVerseReference(*passage)), "<td style='vertical-align: text-top;'>{0}</td>".format(biblesSqlite.readMultipleVerses(text, [passage], displayRef=False))) for passage in passages]
                versions, verses = zip(*tableList)
                window = "main" if config.openBibleInMainViewOnly else "study"
                return (window,
                        "<h2>{2}</h2><table style='width:100%; table-layout:fixed;'><tr>{0}</tr><tr>{1}</tr></table>"
                        .format("".join(versions), "".join(verses), topic), {})

    # _promise:::
    def textPromise(self, command, source):
        updateViewConfig, viewText, *_ = self.getViewConfig(source)
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(viewText, command)
        texts, references = self.splitCommand(command)
        confirmedTexts = self.getConfirmedTexts(texts)
        if not confirmedTexts:
            return self.invalidCommand()
        else:
            text = confirmedTexts[0]
            marvelBibles = self.getMarvelBibles()
            if text in marvelBibles and not os.path.isfile(os.path.join(*marvelBibles[text][0])):
                databaseInfo = marvelBibles[text]
                if self.parent is not None:
                    self.parent.downloadHelper(databaseInfo)
                return ("", "", {})
            else:
                bibleVerseParser = BibleVerseParser(config.parserStandarisation)
                biblesSqlite = BiblesSqlite()
                cs = CollectionsSqlite()
                topic, passagesString = cs.readData("PROMISES", references.split("."))
                passages = bibleVerseParser.extractAllReferences(passagesString, tagged=True)
                return ("study", "<h2>{0}</h2>{1}".format(topic, biblesSqlite.readMultipleVerses(text, passages)), {})

    # _biblenote:::
    def textBiblenote(self, command, source):
        text, references = self.splitCommand(command)
        if text in self.getConfirmedTexts(text):
            bible = Bible(text)
            note = bible.readBiblenote(references)
            return ("study", note, {})
        else:
            return self.invalidCommand()

    # openbooknote:::
    def openBookNoteRef(self, command, source):
        if not " " in command:
            command = "{0} 1".format(command)
        verseList = self.extractAllVerses(command)
        if verseList:
            b, *_ = verseList[0]
            return self.openBookNote(str(b), source)
        else:
            return self.invalidCommand()

    # _openbooknote:::
    def openBookNote(self, command, source):
        try:
            if command:
                b, *_ = command.split(".")
                b = int(b)
            else:
                b = config.mainB
            if config.runMode == "terminal":
                content = NoteSqlite().getBookNote(b)[0]
                return ("", content, {})
            else:
                if self.parent is not None:
                    self.parent.openBookNote(b)
            return ("", "", {})
        except:
            return self.invalidCommand()

    # openchapternote:::
    def openChapterNoteRef(self, command, source):
        verseList = self.extractAllVerses(command)
        if verseList:
            b, c, *_ = verseList[0]
            return self.openChapterNote("{0}.{1}".format(b, c), source)
        else:
            return self.invalidCommand()

    # _openchapternote:::
    def openChapterNote(self, command, source):
        try:
            if command:
                b, c, *_ = command.split(".")
                b, c = int(b), int(c)
            else:
                b, c = config.mainB, config.mainC
            if config.runMode == "terminal":
                content = NoteSqlite().getChapterNote(b, c)[0]
                return ("", content, {})
            else:
                if self.parent is not None:
                    self.parent.openChapterNote(b, c)
            return ("", "", {})
        except:
            return self.invalidCommand()

    # openversenote:::
    def openVerseNoteRef(self, command, source):
        verseList = self.extractAllVerses(command)
        if verseList:
            b, c, v, *_ = verseList[0]
            return self.openVerseNote("{0}.{1}.{2}".format(b, c, v), source)
        else:
            return self.invalidCommand()

    # _openversenote:::
    def openVerseNote(self, command, source):
        try:
            if command:
                b, c, v, *_ = command.split(".")
                b, c, v = int(b), int(c), int(v)
            else:
                b, c, v = config.mainB, config.mainC, config.mainV
            if config.runMode == "terminal":
                content = NoteSqlite().getVerseNote(b, c, v)[0]
                return ("", content, {})
            else:
                if self.parent is not None:
                    self.parent.openVerseNote(b, c, v)
            return ("", "", {})
        except:
            return self.invalidCommand()

    # editbooknote:::
    def editBookNoteRef(self, command, source):
        if not " " in command:
            command = "{0} 1".format(command)
        verseList = self.extractAllVerses(command)
        if verseList:
            b, *_ = verseList[0]
            return self.editBookNote(str(b), source)
        else:
            return self.invalidCommand()

    # _editbooknote:::
    def editBookNote(self, command, source):
        try:
            if command:
                b, *_ = command.split(".")
                c = 1
                v = 1
            else:
                b, c, v = config.mainB, 1, 1
            if config.runMode == "terminal":
                config.mainWindow.openNoteEditor("book", b=b, c=c, v=v)
                return ("", "[MESSAGE]Text Editor Closed", {})
            elif self.parent.noteSaved or self.parent.warningNotSaved():
                if self.parent is not None:
                    self.parent.openNoteEditor("book", b=b, c=c, v=v)
            return ("", "", {})
        except:
            return self.invalidCommand()

    # editchapternote:::
    def editChapterNoteRef(self, command, source):
        verseList = self.extractAllVerses(command)
        if verseList:
            b, c, *_ = verseList[0]
            return self.editChapterNote("{0}.{1}".format(b, c), source)
        else:
            return self.invalidCommand()

    # _editchapternote:::
    def editChapterNote(self, command, source):
        try:
            if command:
                b, c, *_ = command.split(".")
                v = 1
            else:
                b, c, v = config.mainB, config.mainC, 1
            if config.runMode == "terminal":
                config.mainWindow.openNoteEditor("chapter", b=b, c=c, v=v)
                return ("", "[MESSAGE]Text Editor Closed", {})
            elif self.parent.noteSaved or self.parent.warningNotSaved():
                if self.parent is not None:
                    self.parent.openNoteEditor("chapter", b=b, c=c, v=v)
            return ("", "", {})
        except:
            return self.invalidCommand()

    # editversenote:::
    def editVerseNoteRef(self, command, source):
        verseList = self.extractAllVerses(command)
        if verseList:
            b, c, v, *_ = verseList[0]
            return self.editVerseNote("{0}.{1}.{2}".format(b, c, v), source)
        else:
            return self.invalidCommand()

    # _editversenote:::
    def editVerseNote(self, command, source):
        try:
            if command:
                b, c, v, *_ = command.split(".")
            else:
                b, c, v = config.mainB, config.mainC, config.mainV
            if config.runMode == "terminal":
                config.mainWindow.openNoteEditor("verse", b=b, c=c, v=v)
                return ("", "[MESSAGE]Text Editor Closed", {})
            elif self.parent.noteSaved or self.parent.warningNotSaved():
                if self.parent is not None:
                    self.parent.openNoteEditor("verse", b=b, c=c, v=v)
            #else:
                #self.parent.noteEditor.raise_()
            return ("", "", {})
        except:
            return self.invalidCommand()

    # openjournal:::
    def openJournalNote(self, command, source):
        try:
            if command:
                year, month, day, *_ = command.split("-")
                year, month, day = int(year), int(month), int(day)
            else:
                today = date.today()
                year, month, day = today.year, today.month, today.day
            journalSqlite = JournalSqlite()
            note = journalSqlite.getJournalNote(year, month, day)
            return ("study", note, {})
        except:
            return self.invalidCommand()

    # editjournal:::
    def editJournalNote(self, command, source):
        try:
            if command:
                year, month, day, *_ = command.split("-")
            else:
                today = date.today()
                year, month, day = today.year, today.month, today.day
            if config.runMode == "terminal":
                config.mainWindow.openNoteEditor("journal", year=year, month=month, day=day)
                return ("", "[MESSAGE]Text Editor Closed", {})
            elif self.parent.noteSaved or self.parent.warningNotSaved():
                if self.parent is not None:
                    self.parent.openNoteEditor("journal", year=year, month=month, day=day)
            return ("", "", {})
        except:
            return self.invalidCommand()

    # _open:::
    def openMarvelDataFile(self, command, source):
        fileitems = command.split("/")
        filePath = os.path.join(config.marvelData, *fileitems)
        if config.runMode == "terminal":
            return self.osCommand(f"{config.open} {filePath}", source)
        elif config.enableHttpServer and re.search("\.jpg$|\.jpeg$|\.png$|\.bmp$|\.gif$", filePath.lower()):
            fullPath = os.path.join(os.getcwd(), filePath)
            if os.path.isfile(fullPath):
                # config.marvelData is a relative path
                # relative path outside htmlresource directory does not work on http-server, though it works on desktop version
                #filePath = "../"+filePath
                #return ("study", "<img src='{0}'>".format(filePath), {})
                return ("study", TextUtil.imageToText(fullPath), {})
            elif os.path.isfile(filePath):
                # config.marvelData is an absolute path
                return ("study", TextUtil.imageToText(filePath), {})
            else:
                return ("study", "Image not found!", {})
        elif config.enableHttpServer:
            return ("study", "[File type not supported!]", {})
        elif re.search("\.bmp$|\.jpg$|\.jpeg$|\.png$|\.pbm$|\.pgm$|\.ppm$|\.xbm$|\.xpm$", filePath.lower()):
            from uniquebible.gui.ImageViewer import ImageViewer
            imageViewer = ImageViewer(self.parent)
            imageViewer.show()
            imageViewer.load_file(filePath)
            return ("", "", {})
        else:
            if self.parent is not None:
                self.parent.openExternalFile(filePath)
            return ("", "", {})

    # open:::
    def openExternalFile(self, command, source):
        fileitems = command.split("/")
        filePath = os.path.join(*fileitems)
        if config.runMode == "terminal":
            return self.osCommand(f"{config.open} {filePath}", source)
        elif config.enableHttpServer:
            return ("study", TextUtil.imageToText(filePath), {})
        elif re.search("\.bmp$|\.jpg$|\.jpeg$|\.png$|\.pbm$|\.pgm$|\.ppm$|\.xbm$|\.xpm$", filePath.lower()):
            from uniquebible.gui.ImageViewer import ImageViewer
            imageViewer = ImageViewer(self.parent)
            imageViewer.show()
            imageViewer.load_file(filePath)
            return ("", "", {})
        else:
            if self.parent is not None:
                self.parent.openExternalFile(filePath)
            return ("", "", {})

    # docx:::
    def openDocxReader(self, command, source):
        if command:
            if self.parent is not None:
                self.parent.openTextFile(os.path.join(config.marvelData, "docx", command))
        return ("", "", {})

    # opennote:::
    def textOpenNoteFile(self, command, source):
        if command:
            if self.parent is not None:
                self.parent.openTextFile(command)
        return ("", "", {})

    # _openfile:::
    def textOpenFile(self, command, source):
        fileName = config.history["external"][int(command)]
        if fileName:
            if self.parent is not None:
                self.parent.openTextFile(fileName)
        return ("", "", {})

    # _editfile:::
    def textEditFile(self, command, source):
        if command:
            if self.parent is not None:
                self.parent.editExternalFileHistoryRecord(int(command))
        return ("", "", {})

    # _website:::
    def textWebsite(self, command, source):
        if command:
            if config.enableHttpServer and command.startswith("http"):
                subprocess.Popen("{0} {1}".format(config.open, command), shell=True)
            elif config.runMode == "terminal" and config.terminalEnableTermuxAPI:
                #os.system(f"{config.open} command")
                return self.osCommand(f"{config.open} {command}", source)
            else:
                webbrowser.open(command)
            return ("", "", {})
        else:
            return self.invalidCommand()

    # _uba:::
    def textUba(self, command, source):
        if command:
            pathItems = command[7:].split("/")
            file = os.path.join(*pathItems)
            config.history["external"].append(file)
            if self.parent is not None:
                self.parent.openExternalFileHistoryRecord(-1)
            return ("", "", {})
        else:
            return self.invalidCommand()

    # _info:::
    def textInfo(self, command, source):
        if config.instantInformationEnabled:
            return ("instant", command, {})
        else:
            return ("", "", {})

    # _lexicaldata:::
    def instantLexicalData(self, command, source):
        allInfo = []
        for item in command.split("_"):
            info = LexicalData.getLexicalData(item, True)
            if info:
                allInfo.append(info)
        allInfo = "<hr>".join(allInfo)
        return ("instant", allInfo, {})

    # _instantverse:::
    def instantVerse(self, command, source):
        if config.instantInformationEnabled:
            morphologySqlite = MorphologySqlite()
            *_, commandList = self.splitCommand(command)
            elements = commandList.split(".")
            if len(elements) == 3:
                b, c, v = [int(i) for i in elements]
                info = morphologySqlite.instantVerse(b, c, v)
                return ("instant", info, {})
            elif len(elements) == 4:
                b, c, v, wordID = elements
                info = morphologySqlite.instantVerse(int(b), int(c), int(v), wordID)
                return ("instant", info, {})
            else:
                return self.invalidCommand()
        else:
            return ("", "", {})

    # _imvr:::
    def instantMainVerseReference(self, command, source):
        text = config.mainText
        if ":::" in command:
            text, verseList = self.splitCommand(command)
        verseList = self.extractAllVerses(command)
        if verseList:
            return self.instantMainVerse(".".join([str(i) for i in verseList[0]]), source, text)
        else:
            return ("", "", {})

    # _imv:::
    def instantMainVerse(self, command, source, text=""):
        if not text or not text in self.parent.textList:
            text = config.mainText
        if config.instantInformationEnabled and command:
            info = self.getInstantMainVerseInfo(command, text)
            return ("instant", info, {})
        else:
            return ("", "", {})

    def getInstantMainVerseInfo(self, command, text):
        bcvList = [int(i) for i in command.split(".")]
        info = BiblesSqlite().readMultipleVerses(text, [bcvList])
        if text in config.rtlTexts and bcvList[0] < 40:
            info = "<div style='direction: rtl;'>{0}</div>".format(info)
        return info

    # _instantword:::
    def instantWord(self, command, _):
        if config.instantInformationEnabled:
            info = self.getInstantWordInfo(command)
            return ("instant", info, {})
        else:
            return ("", "", {})

    def getInstantWordInfo(self, command):
        commandList = self.splitCommand(command)
        morphologySqlite = MorphologySqlite()
        wordID = commandList[1]
        wordID = re.sub('^[h0]+?([^h0])', r'\1', wordID, flags=re.M)
        return morphologySqlite.instantWord(int(commandList[0]), int(wordID))

    # _bibleinfo:::
    def textBibleInfo(self, command, source):
        if self.getConfirmedTexts(command):
            biblesSqlite = BiblesSqlite()
            info = biblesSqlite.bibleInfo(command)
            if info:
                return ("instant", info, {})
            else:
                return ("", "", {})
        else:
            return self.invalidCommand()

    # _commentaryinfo:::
    def textCommentaryInfo(self, command, source):
        commentaryFile = os.path.join(config.commentariesFolder, "c{0}.commentary".format(command))
        if os.path.isfile(commentaryFile):
            if command in Commentary.marvelCommentaries:
                return ("instant", Commentary.marvelCommentaries[command], {})
            else:
                commentarySqlite = Commentary(command)
                info = commentarySqlite.commentaryInfo()
                if info:
                    return ("instant", info, {})
                else:
                    return ("", "", {})
        else:
            return self.invalidCommand()

    # mapping verse action
    def mapVerseAction(self, keyword, verseReference, source):
        if self.isDatabaseInstalled(keyword.lower()):
            self.lastKeyword = keyword.lower()
            actionMap = {
                "COMPARE": self.textCompare,
                "CROSSREFERENCE": self.textCrossReference,
                "TSKE": self.tske,
                "TRANSLATION": self.textTranslation,
                "DISCOURSE": self.textDiscourse,
                "WORDS": self.textWords,
                "COMBO": self.textCombo,
                "INDEX": self.textIndex,
                "COMMENTARY": self.textCommentary,
                "STUDY": self.textStudy,
                "_noAction": self.noAction,
            }
            return actionMap[keyword](verseReference, source)
        else:
            return self.databaseNotInstalled(keyword.lower())

    # _menu:::
    def textMenu(self, command, source):
        try:
            dotCount = command.count(".")
            if dotCount == 3 and config.enableHttpServer:
                text, b, c, v = command.split(".")
                config.mainText, config.mainB, config.mainC, config.mainV = text, int(b), int(c), int(v)
                bibleCommand = "BIBLE:::{0}:::{1} {2}:{3}".format(text, BibleBooks.abbrev["eng"][b][0], config.mainC, config.mainV)
                if self.parent is not None:
                    self.parent.addHistoryRecord("main", bibleCommand)
            menu = HtmlGeneratorUtil().getMenu(command, source)
            return (source, menu, {})
        except:
            return self.invalidCommand()

    # _comparison:::
    def textComparisonMenu(self, command, source):
        try:
            menu = HtmlGeneratorUtil().getComparisonMenu(command, source)
            return (source, menu, {})
        except:
            return self.invalidCommand()

    # _vndc:::
    def verseNoDoubleClick(self, command, source):
        if not command:
            command = f"{config.mainText}.{config.mainB}.{config.mainC}.{config.mainV}"
        dotCount = command.count(".")
        if dotCount == 3 and config.enableHttpServer:
            text, b, c, v = command.split(".")
            config.mainText, config.mainB, config.mainC, config.mainV = text, int(b), int(c), int(v)
            bibleCommand = "BIBLE:::{0}:::{1} {2}:{3}".format(text, BibleBooks.abbrev["eng"][b][0], config.mainC, config.mainV)
            if self.parent is not None:
                self.parent.addHistoryRecord("main", bibleCommand)
        if dotCount != 3 or config.verseNoDoubleClickAction == "_menu" or (config.enableHttpServer and config.verseNoDoubleClickAction.startswith("_cp")):
            if dotCount == 2 and not config.preferHtmlMenu and not config.enableHttpServer:
                text, b, c = command.split(".")
                if self.parent is not None:
                    self.parent.openControlPanelTab(0, int(b), int(c), int(1), text),
                return ("", "", {})
            else:
                menu = HtmlGeneratorUtil().getMenu(command, source)
                return (source, menu, {})
        elif config.verseNoDoubleClickAction in ("none", "_noAction"):
            return self.noAction(command, source)
        elif config.verseNoDoubleClickAction.startswith("_cp"):
            index = int(config.verseNoDoubleClickAction[-1])
            text, b, c, v = command.split(".")
            if self.parent is not None:
                self.parent.openControlPanelTab(index, int(b), int(c), int(v), text),
            return ("", "", {})
        else:
            compareOnMain = (config.verseNoSingleClickAction == "COMPARE" and not config.compareOnStudyWindow)
            *_, b, c, v = command.split(".")
            verseReference = "{0} {1}:{2}".format(BibleBooks().abbrev["eng"][b][0], c, v)
            if self.parent is not None:
                self.parent.addHistoryRecord("main" if compareOnMain else "study", "{0}:::{1}".format(config.verseNoDoubleClickAction, verseReference))
            return self.mapVerseAction(config.verseNoDoubleClickAction, verseReference, source)

    # _vnsc:::
    def verseNoSingleClick(self, command, source):
        if not command:
            command = f"{config.mainText}.{config.mainB}.{config.mainC}.{config.mainV}"
        if command.count(".") != 4:
            return self.invalidCommand()
        compareOnMain = (config.verseNoSingleClickAction == "COMPARE" and not config.compareOnStudyWindow)
        text, b, c, v, verseReference = command.split(".")
        bibleCommand = "BIBLE:::{0}:::{1}".format(text, verseReference)
        if config.enableHttpServer:
            config.mainText, config.mainB, config.mainC, config.mainV = text, int(b), int(c), int(v)
            if self.parent is not None:
                self.parent.addHistoryRecord("main", bibleCommand)
        elif not compareOnMain:
            if self.parent is not None:
                self.parent.passRunTextCommand(bibleCommand, True, source)
        if not config.verseNoSingleClickAction.upper() == config.syncAction.upper():
            if config.verseNoSingleClickAction == "_menu" or (config.enableHttpServer and config.verseNoSingleClickAction.startswith("_cp")):
                menu = HtmlGeneratorUtil().getMenu("{0}.{1}.{2}.{3}".format(text, b, c, v), source)
                return (source, menu, {})
            elif config.verseNoSingleClickAction.startswith("_cp"):
                index = int(config.verseNoSingleClickAction[-1])
                if self.parent is not None:
                    self.parent.openControlPanelTab(index, int(b), int(c), int(v), text),
                return ("", "", {})
            else:
                if not compareOnMain and config.syncAction == "STUDY":
                    if self.parent is not None:
                        self.parent.nextStudyWindowTab()
                if self.parent is not None:
                    self.parent.addHistoryRecord("main" if compareOnMain else "study", "{0}:::{1}".format(config.verseNoSingleClickAction, verseReference))
                return self.mapVerseAction(config.verseNoSingleClickAction, verseReference, source)
        return ("", "", {})

    # _cp:::
    # _mastercontrol:::
    def openMasterControl(self, command, source):
        try:
            if command and int(command) < 5:
                index = int(command)
            else:
                index = 0
            if self.parent is not None:
                self.parent.openControlPanelTab(index, config.mainB, config.mainC, config.mainV, config.mainText),
            return ("", "", {})
        except:
            return self.invalidCommand()

    # _commentary:::
    def textCommentaryMenu(self, command, source):
        if config.enableHttpServer:
            config.commentaryB, config.commentaryC, config.commentaryV = config.mainB, config.mainC, config.mainV
        text, *_ = command.split(".")
        commentary = Commentary(text)
        commentaryMenu = commentary.getMenu(command)
        return ("study", commentaryMenu, {})

    # _book:::
    def textBookMenu(self, command, source):
        bookData = BookData()
        bookMenu = bookData.getMenu(command)
        config.bookChapNum = 0
        if self.parent is not None:
            self.parent.updateBookButton()
        return ("study", bookMenu, {'tab_title':command[:20]})

    # _history:::
    def textHistory(self, command, source):
        if command in ("main", "study"):
            return (command, self.parent.getHistory(command), {})
        else:
            return self.invalidCommand()

    # _historyrecord:::
    def textHistoryRecord(self, command, source):
        if source == "http":
            source = "main"
        if source in ("main", "study"):
            recordNumber = int(command)
            config.currentRecord[source] = recordNumber
            textCommand = config.history[source][recordNumber]
            return self.parser(textCommand, source)
        else:
            return self.invalidCommand()

    # _command:::
    def textCommand(self, command, source):
        return ("command", command, {})

    # _paste:::
    def pasteFromClipboard(self, command, source):
        if config.runMode == "terminal":
            config.mainWindow.getclipboardtext()
        elif ("Pyperclip" in config.enabled) and config.runMode == "terminal":
            import pyperclip
            content = pyperclip.paste()
            return ("study", content, {})
        else:
            if self.parent is not None:
                self.parent.pasteFromClipboard()
        return ("", "", {})

    # _whatis:::
    def textWhatIs(self, command, source):
        try:
            command = command.lower().strip()
            if config.runMode == "terminal" and command in config.mainWindow.dotCommands:
                return ("study", config.mainWindow.dotCommands[command][0], {})
            elif ":::"in command:
                command, *_ = command.split(":::", 1)
            content = self.interpreters[command][-1]
            content = re.sub("            #", "<br>#", content)
            return ("study", content, {})
        except:
            return self.invalidCommand()

    # _htmlimage:::
    def textHtmlImage(self, command, source):
        if config.runMode == "terminal":
            filepath = os.path.join("htmlResources", "images", command)
            if config.terminalEnableTermuxAPI:
                os.system(f"termux-share {filepath}")
            else:
                os.system(f"{config.open} {filepath}")
            return ("", "", {})
        else:
            content = "<p align='center'><img src='images/{0}'><br><br><ref onclick='openHtmlFile({1}images/{0}{1})'>{0}</ref></p>".format(command, '"')
            return ("popover.{0}".format(source), content, {})

    # _image:::
    def textImage(self, command, source):
        module, entry = self.splitCommand(command)
        imageSqlite = ImageSqlite()
        imageSqlite.exportImage(module, entry)
        if module == "EXLBL":
            imageFile = "htmlResources/images/exlbl/EXLBL_{0}".format(entry)
        else:
            imageFile = "htmlResources/images/{0}/{0}_{1}".format(module, entry)
        self.openExternalFile(imageFile, source)
        return ("", "", {})
        #content = "<img src='images/{0}/{0}_{1}'>".format(module, entry)
        #return ("popover.{0}".format(source), content)

    # COMMENTARY:::
    def textCommentary(self, command, source):
        try:
            if command.count(":::") == 0:
                command = "{0}:::{1}".format(config.commentaryText, command)
            elif command.count(":::") == 1 and command.endswith(":::"):
                command = "{0}{1}".format(command, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV))
            commandList = self.splitCommand(command)
            if " " in commandList[1]:
                verseList = self.extractAllVerses(commandList[1])
            else:
                verseList = [(BibleBooks.name2number[commandList[1]], 0, 0)]
            if not len(commandList) == 2 or not verseList:
                return self.invalidCommand()
            else:
                bcvTuple = verseList[0]
                if config.enableHttpServer:
                    config.mainB, config.mainC, config.mainV, *_ = bcvTuple
                module = commandList[0]
                commentary = Commentary(module)
                fullVerseList = Bible("KJV").getEverySingleVerseList((bcvTuple,))
                if config.runMode == "terminal" or config.rawOutput:
                    content = commentary.getContent(bcvTuple, fullVerseList=fullVerseList)
                else:
                    content = commentary.getContent(bcvTuple)
                if not content == "INVALID_COMMAND_ENTERED":
                    self.setCommentaryVerse(module, bcvTuple)
                return ("study", content, {'tab_title':'Com:' + module})
        except:
            return self.invalidCommand()

    # COMMENTARY2:::
    def textCommentary2(self, command, source):
        if not command:
            command = f"{config.commentaryB}.{config.commentaryC}.{config.commentaryV}"
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.commentaryText, command)
        commandList = self.splitCommand(command)
        reference = commandList[1]
        if re.search(r"^[0-9]+?\.[0-9]+?\.[0-9]+?$", reference):
            verseList = [tuple([int(i) for i in reference.split(".")])]
            if not len(commandList) == 2 or not verseList:
                return self.invalidCommand()
            else:
                bcvTuple = verseList[0]
                module = commandList[0]
                commentary = Commentary(module)
                content = commentary.getContent(bcvTuple)
                if not content == "INVALID_COMMAND_ENTERED":
                    self.setCommentaryVerse(module, bcvTuple)
                return ("study", content, {})
        else:
            return self.invalidCommand()

    # SEARCHTOOL:::
    def textSearchTool(self, command, source):
        try:
            origModule, entry = self.splitCommand(command)
            if origModule == config.thisTranslation['searchAllDictionaries']:
                modules = self.parent.dictionaryListAbb
            else:
                modules = [origModule]
            TextCommandParser.last_text_search = entry
            indexes = IndexesSqlite()
            content = ""
            toolList = [("", "[search other resources]"), ("EXLBP", "Exhaustive Library of Bible Characters"), ("EXLBL", "Exhaustive Library of Bible Locations")] + indexes.topicList + indexes.dictionaryList + indexes.encyclopediaList
            for module in modules:
                if module in dict(toolList[1:]).keys() or module in ("mRMAC", "mETCBC", "mLXX"):
                    action = "searchItem(this.value, \"{0}\")".format(entry)
                    selectList = indexes.formatSelectList(action, toolList)
                    if module in dict(indexes.topicList).keys():
                        config.topic = module
                    elif module in dict(indexes.dictionaryList).keys() and not module == "HBN":
                        config.dictionary = module
                    elif module in dict(indexes.encyclopediaList).keys():
                        config.encyclopedia = module
                    searchSqlite = SearchSqlite()
                    exactMatch = searchSqlite.getContent(module, entry)
                    similarMatch = searchSqlite.getSimilarContent(module, entry)
                    selectList = f"<p>{selectList}</p><p>" if not config.runMode == "terminal" else ""
                    content += "<h2>Search <span style='color: brown;'>{0}</span> for <span style='color: brown;'>{1}</span></h2>{4}<b>Exact match:</b><br><br>{2}</p><p><b>Partial match:</b><br><br>{3}".format(module, entry, exactMatch, similarMatch, selectList)
            if len(content) > 0:
                return ("study", f"[MESSAGE]{content}" if config.runMode == "terminal" else content, {'tab_title': 'Search:' + origModule + ':' + entry})
            else:
                return self.invalidCommand()
        except:
            return self.invalidCommand()

    # GPTSEARCH:::
    def textGPTSEARCHSearch(self, command, source):
        import openai, traceback
        try:
            openai.api_key = os.environ["OPENAI_API_KEY"] = config.openaiApiKey
            openai.organization = config.openaiApiOrganization

            
            if command.count(":::") == 0:
                texts = ""
                query = command
            else:
                commandList = self.splitCommand(command)
                texts, query = commandList

            prompt = f"""Formulate a sql query over a table created with statement "CREATE TABLE Verses (Book INT, Chapter INT, Verse INT, Scripture TEXT)".
The book numbers range from 1 to 66, corresponding to the canonical order from Genesis to Revevlation in the bible.
I am providing you below with WHERE condition described in natural language.
Give me only the sql query statement, starting with "SELECT * FROM Verses WHERE " without any extra explanation or comment.
The WHERE condition is described as: {query}"""

            # run ChatGPT to get a standard sql query
            messages = [
                {"role": "system", "content" : "You’re a kind helpful assistant"},
                {"role": "user", "content" : prompt}
            ]
            completion = OpenAI().chat.completions.create(
                model=config.chatGPTApiModel,
                messages=messages,
                n=1,
                temperature=0.0,
                max_tokens=2048,
            )
            sqlQuery = completion.choices[0].message.content
            # check
            #print(sqlQuery)

            sqlQuery = re.sub("^SELECT . FROM Verses WHERE ", "", sqlQuery)
            command = f"{texts}:::{sqlQuery}" if texts else sqlQuery
            return self.textSearch(command, source, "ADVANCED", config.addFavouriteToMultiRef)
        except:
            response = "GPT search feature requires an OpenAI API Key; read https://github.com/eliranwong/UniqueBible/wiki/Search-Bible-with-Natural-Language-via-ChatGPT ; " + traceback.format_exc()
        return ("study", response, {})

    # SEMANTIC:::
    def textSemanticSearch(self, command, source):
        # upgrade package llama_index
        if not self.llamaIndexUpdated:
            try:
                os.system("pip3 install --upgrade llama_index")
            except:
                pass
            self.llamaIndexUpdated = True
        # import packages
        import openai, traceback, shutil
        from llama_index.llms import OpenAI
        from llama_index import SimpleDirectoryReader, ServiceContext, GPTVectorStoreIndex, StorageContext, load_index_from_storage
        #from pathlib import Path
        try:
            openai.api_key = os.environ["OPENAI_API_KEY"] = config.openaiApiKey
            openai.organization = config.openaiApiOrganization

            if command.count(":::") == 0:
                command = "{0}:::{1}".format(config.mainText, command)
            commandList = self.splitCommand(command)
            text, query = commandList
            if not text in BiblesSqlite().getBibleList():
                return self.invalidCommand()

            persist_dir = os.path.join("llama_index", f"{text}_md_index")
            bible_dir = os.path.join("temp", text)
            def removeTempDir():
                if os.path.isdir(bible_dir):
                    shutil.rmtree(bible_dir)
            # build index if it does not exist
            if not os.path.isdir(persist_dir):
                # notify users
                message = "Create indexes now ..."
                print(message) if config.noQt else self.parent.displayMessage(message)
                # load book information
                #bibleBooks = BibleBooks()
                # export bible text in markdown format
                Bible(text).exportToMarkdown(standardReference=True)
                # create index
                # define LLM
                llm = OpenAI(temperature=config.chatGPTApiTemperature, model=config.chatGPTApiModel, max_tokens=config.chatGPTApiMaxTokens)
                service_context = ServiceContext.from_defaults(llm=llm)
                documents = SimpleDirectoryReader(bible_dir, recursive=True, required_exts=[".md"]).load_data()
                index = GPTVectorStoreIndex.from_documents(documents, service_context=service_context)
                index.storage_context.persist(persist_dir=persist_dir)
                # remove exported bible text after indexes are created
                removeTempDir()
            # load index
            storage_context = StorageContext.from_defaults(persist_dir=persist_dir)
            index = load_index_from_storage(storage_context)
            # run query
            query_engine = index.as_query_engine()
            response = query_engine.query(query).response
            # parse bible reference
            if not config.runMode in ("terminal", "telnet-server"):
                response = self.parent.htmlWrapper(response, parsing=True, view="study", linebreak=True, html=False)
        except:
            response = "Semantic search feature requires an OpenAI API Key; read https://github.com/eliranwong/UniqueBible/wiki/Semantic-Search ; " + traceback.format_exc()
        return ("study", response, {})

    # COUNT:::
    def textCountSearch(self, command, source):
        return self.textCount(command, config.addFavouriteToMultiRef)

    # called by COUNT:::
    def textCount(self, command, interlinear):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.mainText, command)
        commandList = self.splitCommand(command)
        texts, searchEntry = commandList
        booksRange = ""
        if searchEntry.count(":::") > 0:
            searchEntry, booksRange = self.splitCommand(searchEntry)
        texts = self.getConfirmedTexts(texts)
        if texts and re.match("^[EHG][0-9]+?$", searchEntry):
            return self.textConcordance(command, "study")
        elif not len(commandList) == 2 or not texts:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            searchResult = "<hr>".join([biblesSqlite.countSearchBible(text, searchEntry, interlinear, booksRange) for text in texts])
            return ("study", searchResult, {})

    # SEARCH:::
    def textSearchBasic(self, command, source):
        return self.textSearch(command, source, "BASIC", config.addFavouriteToMultiRef)

    # SEARCHREFERECE:::
    def textSearchReference(self, command, source):
        return self.textSearch(command, source, "BASIC", config.addFavouriteToMultiRef, referenceOnly=True)

    # REGEXSEARCH:::
    def textSearchRegex(self, command, source):
        return self.textSearch(command, source, "REGEX", config.addFavouriteToMultiRef)

    # ADVANCEDSEARCH:::
    def textSearchAdvanced(self, command, source):
        return self.textSearch(command, source, "ADVANCED", config.addFavouriteToMultiRef)

    # SEARCHOT:::
    def textSearchOT(self, command, source):
        commandList = command.split(":::")
        commandList[-1] = 'Scripture LIKE "%{0}%" AND Book < 40'.format(commandList[-1])
        command = ":::".join(commandList)
        return self.textSearch(command, source, "ADVANCED", config.addFavouriteToMultiRef)

    # SEARCHNT:::
    def textSearchNT(self, command, source):
        commandList = command.split(":::")
        commandList[-1] = 'Scripture LIKE "%{0}%" AND Book >= 40 AND Book <= 66'.format(commandList[-1])
        command = ":::".join(commandList)
        return self.textSearch(command, source, "ADVANCED", config.addFavouriteToMultiRef)

    # SEARCHSINGLE:::
    def textSearchSingleBook(self, book, command, source):
        commandList = command.split(":::")
        commandList[-1] = 'Scripture LIKE "%{0}%" AND Book = {1}'.format(commandList[-1], book)
        command = ":::".join(commandList)
        return self.textSearch(command, source, "ADVANCED", config.addFavouriteToMultiRef)

    # ANDSEARCH:::
    def textAndSearch(self, command, source):
        commandList = command.split(":::")
        index = -2 if command.count(":::") == 2 else -1
        commandList[index] = " AND ".join(['Scripture LIKE "%{0}%"'.format(m.strip()) for m in commandList[index].split("|")])
        command = ":::".join(commandList)
        return self.textSearch(command, source, "ADVANCED", config.addFavouriteToMultiRef)

    # ORSEARCH:::
    def textOrSearch(self, command, source):
        commandList = command.split(":::")
        index = -2 if command.count(":::") == 2 else -1
        commandList[index] = " OR ".join(['Scripture LIKE "%{0}%"'.format(m.strip()) for m in commandList[index].split("|")])
        command = ":::".join(commandList)
        return self.textSearch(command, source, "ADVANCED", config.addFavouriteToMultiRef)

    # called by SEARCH::: & ANDSEARCH::: & ORSEARCH::: & ADVANCEDSEARCH::: & REGEXSEARCH:::
    def textSearch(self, command, source, mode, favouriteVersion=False, referenceOnly=False):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.mainText, command)
        commandList = self.splitCommand(command)
        texts = self.getConfirmedTexts(commandList[0], True)
        if not texts:
            texts = [config.mainText]
        searchEntry = commandList[1] if texts[0] in commandList[0] else command
        booksRange = ""
        if searchEntry.count(":::") > 0:
            searchEntry, booksRange = self.splitCommand(searchEntry)
        if not texts:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            searchResult = "<hr>".join([biblesSqlite.searchBible(text, mode, searchEntry, favouriteVersion, referenceOnly, booksRange) for text in texts])
            return ("study", searchResult, {})

    # SEARCHHIGHLIGHT:::
    def highlightSearch(self, command, source):
        if config.enableVerseHighlighting:
            if command.count(":::") == 0:
                command += ":::all"
            code, reference = self.splitCommand(command)
            highlight = Highlight()
            verses = highlight.getHighlightedBcvList(code, reference)
            bcv = [(b, c, v) for b, c, v, *_ in verses]
            text = BiblesSqlite().readMultipleVerses(config.mainText, bcv)
            text = highlight.highlightSearchResults(text, verses)
            return ("study", text, {})
        else:
            return ("", "", {})

    # WORD:::
    def textWordData(self, command, source):
        try:
            book, wordId = self.splitCommand(command)
            bNo = int(book)
            morphologySqlite = MorphologySqlite()
            bcvTuple, content = morphologySqlite.wordData(bNo, int(wordId))

            # extra data for Greek words
            if bNo >= 40:
                wordData = WordData()
                content += re.sub('^.*?<br><br><b><i>TBESG', '<b><i>TBESG', wordData.getContent("NT", wordId))

            self.setStudyVerse(config.studyText, bcvTuple)
            return ("study", content, {'tab_title': 'Mor:' + wordId})
        except:
            return self.invalidCommand()

    # return default lexicons
    def getDefaultLexicons(self):
        return {
            "H": config.defaultLexiconStrongH,
            "G": config.defaultLexiconStrongG,
            "E": config.defaultLexiconETCBC,
            "L": config.defaultLexiconLXX,
            "g": config.defaultLexiconGK,
            "l": config.defaultLexiconLN,
        }
    
    # LEXICON:::
    def textLexicon(self, command, source):
        return self.textLexiconSearch(command, source, False)

    # REVERSELEXICON:::
    def textReverseLexicon(self, command, source):
        return self.textLexiconSearch(command, source, True)

    def textLexiconSearch(self, command, source, reverse):
        if command.count(":::") == 0:
            defaultLexicon = self.getDefaultLexicons()
            command = "{0}:::{1}".format(defaultLexicon[command[0]], command)
        module, entries = self.splitCommand(command)
        if module == config.thisTranslation['searchAllLexicons']:
            modules = LexiconData().lexiconList
            showLexiconMenu = False
        else:
            modules = [module]
            showLexiconMenu = True if not config.runMode == "terminal" else False
        entries = entries.strip()
        if config.useLiteVerseParsing and not config.noQt:
            try:
                if config.qtLibrary == "pyside6":
                    from PySide6.QtWidgets import QApplication
                else:
                    from qtpy.QtWidgets import QApplication
                QApplication.clipboard().setText(entries)
            except:
                pass
        TextCommandParser.last_lexicon_entry = entries
        content = ""
        for module in modules:
            config.lexicon = module
            lexicon = Lexicon(module)
            # Convert ETCBC Hebrew lexeme codes, if any, to Hebrew Strong's numbers
            morphologySqlite = MorphologySqlite()
            entriesSplit = entries.split("_")
            entryList = []
            for entry in entriesSplit:
                config.eventEntry = entry
                PluginEventHandler.handleEvent("lexicon_entry", entry)
                entry = config.eventEntry
                if not reverse and not module.startswith("Concordance") and not module == "Morphology" and entry.startswith("E"):
                    entryList += morphologySqlite.etcbcLexemeNo2StrongNo(entry)
                else:
                    entryList.append(entry)
            if reverse:
                content += "<hr>".join([lexicon.getReverseContent(entry) for entry in entryList])
            else:
                content += "<hr>".join([lexicon.getContent(entry, showLexiconMenu) for entry in entryList])
        if not content or content == "INVALID_COMMAND_ENTERED":
            return self.invalidCommand()
        else:
            if config.runMode == "terminal":
                if module == "ConcordanceBook":
                    def searchBookLink(match):
                        lexicalEntry = match.group(1)
                        bookAbb = match.group(2)
                        try:
                            bookNo = BibleBooks.name2number[bookAbb]
                        except:
                            bookNo = BibleBooks.name2number[f"{bookAbb}."]
                        return f"""<br>[<ref>MORPHOLOGY:::LexicalEntry LIKE '%{lexicalEntry},%' AND Book = {bookNo}</ref>]"""

                    p = re.compile("""\[<ref onclick="searchBook\('([^']+?)','([^']+?)'\)">search</ref>\]""")
                    content = p.sub(searchBookLink, content)
                elif module == "ConcordanceMorphology":
                    def searchMorphologyLink(match):
                        lexicalEntry = match.group(1)
                        morphologyCode = match.group(2)
                        return f"""<br>[<ref>MORPHOLOGYCODE:::{lexicalEntry},{morphologyCode}</ref>]"""

                    p = re.compile("""\[<ref onclick="searchCode\('([^']+?)','([^']+?)'\)">search</ref>\]""")
                    content = p.sub(searchMorphologyLink, content)

                    def morphologyDescription(match):
                        morphologyModule = match.group(1)
                        if morphologyModule.endswith("morph"):
                            morphologyModule = morphologyModule[:-5]
                        morphologyModule = morphologyModule.upper()
                        morpohlogyCode = match.group(2)
                        return f"<u><b>{morpohlogyCode}</b></u><br>[<ref>SEARCHTOOL:::m{morphologyModule}:::{morpohlogyCode}</ref>]"

                    p = re.compile("""<u><b><ref onclick="(rmac|etcbcmorph|lxxmorph)\('([^']+?)'\)">[^<>]*?</ref></b></u>""")
                    content = p.sub(morphologyDescription, content)

            title = "RevLex" if reverse else "Lex"
            return ("study", content, {'tab_title': title + ':' + module + ':' + entries})

    # SEARCHLEXICON:::
    def searchLexicon(self, command, source):
        if command.count(":::") == 0:
            defaultLexicon = self.getDefaultLexicons()
            command = "{0}:::{1}".format(defaultLexicon[command[0]], command)
        moduleList, search = self.splitCommand(command)
        search = search.strip()
        TextCommandParser.last_lexicon_entry = search
        if moduleList == config.thisTranslation["all"]:
            modules = LexiconData().getLexiconList()
        else:
            modules = moduleList.split("_")
        content = ""
        for module in modules:
            config.lexicon = module
            lexicon = Lexicon(module)
            content += lexicon.searchTopic(search)
        if not content or content == "INVALID_COMMAND_ENTERED":
            return self.invalidCommand()
        else:
            return ("study", content, {'tab_title': 'SearchLex:' + module + ':' + search})

    # LMCOMBO:::
    def textLMcombo(self, command, source):
        if command.count(":::") == 2:
            lexicalEntry, morphologyModule, morphologyCode = command.split(":::")
            defaultLexicon = self.getDefaultLexicons()[lexicalEntry[0]]
            return self.getLexiconMorphologyContent(defaultLexicon, lexicalEntry, morphologyModule, morphologyCode)
        elif command.count(":::") == 3:
            lexicon, lexicalEntry, morphologyModule, morphologyCode = command.split(":::")
            return self.getLexiconMorphologyContent(lexicon, lexicalEntry, morphologyModule, morphologyCode)
        else:
            return self.invalidCommand()

    def getLexiconMorphologyContent(self, lexicon, lexicalEntry, morphologyModule, morphologyCode):
        lexicon = Lexicon(lexicon)
        lexiconContent = "<hr>".join([lexicon.getContent(entry) for entry in lexicalEntry.split("_")])
        searchSqlite = SearchSqlite()
        morphologyDescription = "<hr>".join([searchSqlite.getContent("m"+morphologyModule.upper(), code) for code in morphologyCode.split("_")])
        return ("study", "{0}<hr>{1}".format(morphologyDescription, lexiconContent), {})

    # _wordnote:::
    def textWordNote(self, command, source):
        if re.search("^(LXX1|LXX2|LXX1i|LXX2i|SBLGNT|SBLGNTl):::", command):
            module, wordID = self.splitCommand(command)
            bibleSqlite = Bible(module)
            data = bibleSqlite.readWordNote(wordID)
            if data:
                return ("study", data, {})
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
        return ("study", searchResult, {})

    # _searchword:::
    def textSearchWord(self, command, source):
        portion, wordID = self.splitCommand(command)
        morphologySqlite = MorphologySqlite()
        lexeme, lexicalEntry, morphologyString = morphologySqlite.searchWord(portion, wordID)
        lexicalEntry = lexicalEntry.split(",")[0]
        translations = morphologySqlite.distinctMorphology(lexicalEntry)
        items = (lexeme, lexicalEntry, morphologyString, translations)
        if self.parent is not None:
            self.parent.openMorphDialog(items)
        return ("", "", {})

    # SEARCHMORPHOLOGYBYLEX:::
    def searchMorphologyByLex(self, command, source):
        return self.searchMorphologyCommon(command, source, "LEX")

    # SEARCHMORPHOLOGYBYWORD:::
    def searchMorphologyByWord(self, command, source):
        return self.searchMorphologyCommon(command, source, "WORD")

    # SEARCHMORPHOLOGYBYGLOSS:::
    def searchMorphologyByGloss(self, command, source):
        return self.searchMorphologyCommon(command, source, "GLOSS")

    def searchMorphologyCommon(self, command, source, mode):
        commands = command.split(":::")
        searchTerm = commands[0]
        morphology = commands[1]
        startBook = 1
        endBook = 66
        if len(commands) > 2:
            range = commands[2]
            if "-" in range:
                startBook, endBook = range.split("-")
            else:
                startBook = range
                endBook = range
        morphologyList = morphology.split(",")
        morphologySqlist = MorphologySqlite()
        if mode == "LEX":
            searchTerm += ","
            records = morphologySqlist.searchByLexicalAndMorphology(startBook, endBook, searchTerm, morphologyList)
        elif mode == "WORD":
            records = morphologySqlist.searchByWordAndMorphology(startBook, endBook, searchTerm, morphologyList)
        elif mode == "GLOSS":
            records = morphologySqlist.searchByGlossAndMorphology(startBook, endBook, searchTerm, morphologyList)
        fontStart = ""
        fontEnd = ""
        if len(records) > 0:
            b = records[0][2]
            if b < 40:
                fontStart = "<heb>"
                fontEnd = "</heb>"
            else:
                fontStart = "<grk>"
                fontEnd = "</grk>"
        formatedText = "<p>{3}{0}{4}:::{1} <b style='color: brown;'>{2}</b> hits</p>".format(
            searchTerm, morphology, len(records), fontStart, fontEnd)
        ohgbiInstalled = os.path.isfile(os.path.join(config.marvelData, "bibles", "OHGBi.bible"))
        if config.addOHGBiToMorphologySearch and ohgbiInstalled:
            ohgbiBible = Bible("OHGBi")
        for index, word in enumerate(records):
            wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronuciation, interlinear, translation, gloss = word
            firstLexicalEntry = lexicalEntry.split(",")[0]
            textWord = "<{3} onclick='w({1},{2})' onmouseover='iw({1},{2})'>{0}</{3}>".format(textWord, b, wordID, "heb" if b < 40 else "grk")
            formatedText += "<div><span style='color: purple;'>({0}{1}</ref>)</span> {2} <ref onclick='searchCode(\"{4}\", \"{3}\")'>{3}</ref>".format(morphologySqlist.formVerseTag(b, c, v, config.mainText), morphologySqlist.bcvToVerseReference(b, c, v), textWord, morphologyCode, firstLexicalEntry)
            if config.addOHGBiToMorphologySearch and ohgbiInstalled:
                formatedText += ohgbiBible.getHighlightedOHGBVerse(b, c, v, wordID, False, index + 1 > config.maximumOHGBiVersesDisplayedInSearchResult)
            formatedText += "<br></div>"
        return ("study", formatedText, {})

    # _setconfig:::
    def textSetConfig(self, command, source):
        if config.developer:
            try:
                # when argument is empty
                if not command:
                    # key only without value
                    content = "<h2>Configurable Settings</h2>"
                    content += pprint.pformat(list(config.help.keys()))
                    return ("study", content, {})
                elements = self.splitCommand(command)
                if len(elements) == 1:
                    key = elements[0]
                    content = f"<h2>{key}</h2>"
                    content += f"<ref>Description:</ref><br>{config.help[key]}<br>"
                    content += f"<ref>Current value</ref>: {(eval('pprint.pformat(config.'+key+')'))}<br>"
                    typeString = type(eval(f"config.{key}")).__name__
                    content += f"<ref>Type</ref>: {typeString}"
                    return ("study", content, {})
                if config.developer or config.webFullAccess:
                    item, value = self.splitCommand(command)
                    if not item in config.help.keys():
                        return self.invalidCommand("study")
                    else:
                        # use """ to allow using ' or " for string
                        newConfig = """{0} = {1}""".format(item, value)
                        exec("config."+newConfig)
                        message = f"The value of config.{item} is now changed to {newConfig}."
                        if config.runMode == "terminal":
                            print(message)
                            return ("study", ".restart", {})
                        return ("study", message, {})
                else:
                    return self.invalidCommand("study")
            except:
                return self.invalidCommand("study")
        else:
            return self.invalidCommand("study")

    # EXLB:::
    def textExlb(self, command, source):
        commandList = self.splitCommand(command)
        if commandList and len(commandList) == 2:
            module, *_ = commandList
            if module in ["exlbl", "exlbp", "exlbt"]:
                if module == "exlbt":
                    config.topic = "EXLBT"
                    config.topicEntry = commandList[1]
                elif module == "exlbp":
                    config.characterEntry = commandList[1]
                elif module == "exlbl":
                    config.locationEntry = commandList[1]
                exlbData = ExlbData()
                content = exlbData.getContent(commandList[0], commandList[1])
                if config.runMode == "terminal" and module == "exlbl":
                    #<p align="center">[<ref onclick="website('https://maps.google.com/?q=31.777444,35.234935&ll=31.777444,35.234935&z=10')">Click HERE for a Live Google Map</ref>]</p>
                    content = re.sub("""<p align="center">\[<ref onclick="website\('(.*?)'\)">Click HERE for a Live Google Map</ref>\]</p>""", r"[<ref>\1</ref> ]", content)
                if config.theme in ("dark", "night"):
                    content = self.adjustDarkThemeColorsForExl(content)
                return ("study", content, {})
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
            self.setStudyVerse(config.studyText, (b, c, v))
            return ("study", content, {})
        else:
            return self.invalidCommand("study")

    # DICTIONARY:::
    def textDictionary(self, command, source):
        indexes = IndexesSqlite()
        dictionaryList = dict(indexes.dictionaryList).keys()
        module = command[:3]
        if module in dictionaryList:
            if not module == "HBN":
                config.dictionary = module
            dictionaryData = DictionaryData()
            content = dictionaryData.getContent(command)
            config.dictionaryEntry = command
            return ("study", content, {})
        else:
            return self.invalidCommand("study")

    # ENCYCLOPEDIA:::
    def textEncyclopedia(self, command, source):
        commandList = self.splitCommand(command)
        if commandList and len(commandList) == 2:
            module, entry = commandList
            indexes = IndexesSqlite()
            encyclopediaList = dict(indexes.encyclopediaList).keys()
            if module in encyclopediaList:
                config.encyclopedia = module
                encyclopediaData = EncyclopediaData()
                content = encyclopediaData.getContent(module, entry)
                return ("study", content, {})
            else:
                return self.invalidCommand("study")
        else:
            return self.invalidCommand("study")

    # BOOK:::
    def textBook(self, command, source):
        bookData = BookData()
        #bookList = [book for book, *_ in bookData.getCatalogBookList()]
        if command.count(":::") == 0:
        # if command.count(":::") == 0 and command in bookList:
            config.book = command
            if self.parent is not None:
                self.parent.updateBookButton()
            return ("study", bookData.getMenu(module=config.book), {'tab_title': command[:20]})
        commandList = self.splitCommand(command)
        if commandList and len(commandList) == 2:
            module, entry = commandList
            anchor = None
            if '#' in entry:
                parts = re.split("#", entry)
                entry = parts[0]
                anchor = parts[1]
            content = bookData.getContent(module, entry)
            isPDF = True if type(content) == bytes and content[0] == 37 and content[1] == 80 and content[2] == 68 else False
            pdfFilename = None
            if isPDF:
                pdfFilename = entry
            if not content:
                return self.invalidCommand("study")
            else:
                if not isPDF and config.theme in ("dark", "night"):
                    content = self.adjustDarkThemeColorsForExternalBook(content)
                if config.openBookInNewWindow:
                    if self.parent is not None:
                        self.parent.updateBookButton()
                    return ("popover.study", content, {'tab_title': module[:20], 'pdf_filename': pdfFilename})
                else:
                    if self.parent is not None:
                        self.parent.updateBookButton()
                    return ("study", content, {'tab_title': module[:20], 'jump_to': anchor, 'pdf_filename': pdfFilename})
        else:
            return self.invalidCommand("study")

    # SEARCHBOOKCHAPTER:::
    def textSearchBookChapter(self, command, source):
        return self.textSearchBook(command, source, chapterOnly=True)

    # SEARCHBOOK:::
    def textSearchBook(self, command, source, chapterOnly=False):
        bookData = BookData()
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.book, command)
        modules, searchString = self.splitCommand(command)
        if modules == "ALL":
            modules = ",".join(CatalogUtil.getBooks())
        elif modules == "FAV":
            modules = ",".join(config.favouriteBooks)
            if not config.book in config.favouriteBooks:
                modules = "{0},{1}".format(config.book, modules)
        if not searchString:
            return self.invalidCommand("study")
        else:
            config.bookSearchString = searchString
            modules = modules.split(",")
            content = "<hr>".join([bookData.getSearchedMenu(module, searchString, chapterOnly=chapterOnly) for module in modules])
            if not content:
                return ("study", config.thisTranslation["search_notFound"], {})
                #return self.invalidCommand("study")
            else:
                if self.parent is not None:
                    self.parent.updateBookButton()
                return ("study", content, {})

    # SEARCHALLBOOKSPDF:::
    def textSearchAllBooksAndPdf(self, command, source):
        view, content1, *_ = self.textSearchBook("ALL:::{0}".format(command), source)
        view, content2, *_ = self.searchPdf(command, source)
        return ("study", content1+content2, {'tab_title': "Books/PDF"})

    # SEARCHJOURNAL:::
    def searchJournalNote(self, command, source):
        config.noteSearchString = command
        noteSqlite = JournalSqlite()
        days = noteSqlite.getSearchJournalList(command)
        days = [f"{y}-{m}-{d}" for y, m, d in days]
        prefix = "[MESSAGE]" if config.runMode == "terminal" else ""
        return ("study", "{3}<p>\"<b style='color: brown;'>{0}</b>\" is found in <b style='color: brown;'>{1}</b> note(s) on book(s)</p><p>{2}</p>".format(command, len(days), "; ".join(days), prefix), {})

    # SEARCHBOOKNOTE:::
    def textSearchBookNote(self, command, source):
        config.noteSearchString = command
        noteSqlite = NoteSqlite()
        books = noteSqlite.getSearchedBookList(command)
        prefix = "[MESSAGE]" if config.runMode == "terminal" else ""
        return ("study", "{3}<p>\"<b style='color: brown;'>{0}</b>\" is found in <b style='color: brown;'>{1}</b> note(s) on book(s)</p><p>{2}</p>".format(command, len(books), "; ".join(books), prefix), {})

    # SEARCHCHAPTERNOTE:::
    def textSearchChapterNote(self, command, source):
        config.noteSearchString = command
        noteSqlite = NoteSqlite()
        chapters = noteSqlite.getSearchedChapterList(command)
        prefix = "[MESSAGE]" if config.runMode == "terminal" else ""
        return ("study", "{3}<p>\"<b style='color: brown;'>{0}</b>\" is found in <b style='color: brown;'>{1}</b> note(s) on chapter(s)</p><p>{2}</p>".format(command, len(chapters), "; ".join(chapters), prefix), {})

    # SEARCHVERSENOTE:::
    def textSearchVerseNote(self, command, source):
        config.noteSearchString = command
        noteSqlite = NoteSqlite()
        verses = noteSqlite.getSearchedVerseList(command)
        prefix = "[MESSAGE]" if config.runMode == "terminal" else ""
        return ("study", "{3}<p>\"<b style='color: brown;'>{0}</b>\" is found in <b style='color: brown;'>{1}</b> note(s) on verse(s)</p><p>{2}</p>".format(command, len(verses), "; ".join(verses), prefix), {})

    # DAY:::
    def getDayEntry(self, entry): 
        dayEntry = allDays[int(entry)][-1]
        if config.runMode == "terminal":
            print(f"Scripture: {dayEntry}")
        dayEntry = dayEntry.split(", ")
        parser = BibleVerseParser(config.parserStandarisation)
        for index, reference in enumerate(dayEntry):
            if not ":" in reference:
                b, c, *_ = parser.extractAllReferences(reference)[0]
                lastVerse = Bible(config.mainText).getLastVerse(b, c)
                fullReference = parser.bcvToVerseReference(b, c, 1, c, lastVerse)
                dayEntry[index] = fullReference
        return ", ".join(dayEntry)

    def textDay(self, command, source):
        try:
            if command.count(":::") == 0:
                if config.enableHttpServer and config.webHomePage == "traditional.html":
                    config.mainText = "CUV"
                    command = "CUV:::{0}".format(command)
                elif config.enableHttpServer and config.webHomePage == "simplified.html":
                    config.mainText = "CUVs"
                    command = "CUVs:::{0}".format(command)
                else:
                    command = "{0}:::{1}".format(config.mainText, command)
            commandPrefix, entry, *_ = command.split(":::")
            dayEntry = self.getDayEntry(entry)
            command = "{0}:::{1}".format(commandPrefix, dayEntry)
            return self.textBible(command, source)
        except:
            return self.invalidCommand("study")

    # DAYAUDIO:::
    def textDayAudio(self, command, source):
        try:
            if command.count(":::") == 0:
                if config.enableHttpServer and config.webHomePage == "traditional.html":
                    config.mainText = "CUV"
                    command = "CUV:::{0}".format(command)
                elif config.enableHttpServer and config.webHomePage == "simplified.html":
                    config.mainText = "CUVs"
                    command = "CUVs:::{0}".format(command)
                else:
                    command = "{0}:::{1}".format(config.mainText, command)
            commandPrefix, entry, *_ = command.split(":::")
            dayEntry = self.getDayEntry(entry)
            command = "{0}:::{1}".format(commandPrefix, dayEntry)
            return self.textRead(command, source)
        except:
            return self.invalidCommand("study")

    # DAYAUDIOPLUS:::
    def textDayAudioPlus(self, command, source):
        try:
            if command.count(":::") == 0:
                if config.enableHttpServer and config.webHomePage == "traditional.html":
                    config.mainText = "CUV"
                elif config.enableHttpServer and config.webHomePage == "simplified.html":
                    config.mainText = "CUVs"

                biblesSqlite = BiblesSqlite()
                favBible1 = biblesSqlite.getFavouriteBible()
                favBible2 = biblesSqlite.getFavouriteBible2()
                favBible3 = biblesSqlite.getFavouriteBible3()
                plusBible = ""
                if not config.mainText == favBible1:
                    plusBible = favBible1
                elif not config.mainText == favBible2:
                    plusBible = favBible2
                elif not config.mainText == favBible3:
                    plusBible = favBible3
                
                command = "{1}_{2}:::{0}".format(command, config.mainText, plusBible)
            commandPrefix, entry, *_ = command.split(":::")
            dayEntry = self.getDayEntry(entry)
            command = "{0}:::{1}".format(commandPrefix, dayEntry)
            return self.textRead(command, source)
        except:
            return self.invalidCommand("study")

    # DATA:::
    def textData(self, command, source):
        config.dataset = command
        filepath = os.path.join(config.packageDir, "plugins", "menu", "Bible_Data", "{0}.txt".format(command))
        if not os.path.isfile(filepath) or not ("Tabulate" in config.enabled):
            return self.invalidCommand("study")
        with open(filepath, 'r', encoding='utf8') as fileObj:
            dataList = fileObj.read().split("\n")

        table = []
        headers = [command]
        #parser = BibleVerseParser(config.parserStandarisation)
        for text in dataList:
            # Remove CLRF linebreak
            text = re.sub("\r", "", text)
            #text = parser.parseText(text)
            table.append([text])
        from tabulate import tabulate
        html = tabulate(table, headers, tablefmt="html")
        html = BibleVerseParser(config.parserStandarisation).parseText(html)
        return ("study", html, {'tab_title': "Data"})

    def getLocationsFromReference(self, reference):
        if reference:
            combinedLocations = []
            indexesSqlite = IndexesSqlite()
            if len(reference) == 5:
                b, c, v, ce, ve = reference
                if c == ce:
                    if v == ve:
                        combinedLocations += indexesSqlite.getVerseLocations(b, c, v)
                    elif ve > v:
                        combinedLocations += indexesSqlite.getChapterLocations(b, c, startV=v, endV=ve)
                elif ce > c:
                    combinedLocations += indexesSqlite.getChapterLocations(b, c, startV=v)
                    combinedLocations += indexesSqlite.getChapterLocations(b, ce, endV=ve)
                    if (ce - c) > 1:
                        for i in range(c+1, ce):
                            combinedLocations += indexesSqlite.getChapterLocations(b, i)
            else:
                b, c, v, *_ = reference
                combinedLocations += indexesSqlite.getVerseLocations(b, c, v)
            return combinedLocations
        else:
            return []

    # MAP:::
    def textMap(self, command, source):
        verseList = self.extractAllVerses(command)
        if not verseList or not ("Gmplot" in config.enabled):
            return self.invalidCommand()
        else:
            combinedLocations = []
            #reference = verseList[0]
            #combinedLocations = self.getLocationsFromReference(reference)
            for reference in verseList:
                combinedLocations += self.getLocationsFromReference(reference)
            try:
                selectedLocations = self.selectLocations(combinedLocations)
                html = self.displayMap(selectedLocations)
                return ("study", html, {'tab_title': "Map"})
            except:
                return self.invalidCommand()

    # LOCATIONS:::
    def textLocations(self, command, source):
        selectedLocations = command.split("|")
        selectedLocations = self.selectLocations(defaultChecklist=[i[2:] for i in selectedLocations])
        html = self.displayMap(selectedLocations)
        return ("study", html, {'tab_title': "Map"})

    def selectLocations(self, locations=[], defaultChecklist=[]):
        if defaultChecklist:
            checkList = defaultChecklist
        else:
            checkList = []
            for location in locations:
                # e.g. <p><ref onclick="exlbl('BL1163')">Hiddekel</ref> ... <ref onclick="exlbl('BL421')">Euphrates</ref></p>
                searchPattern = "exlbl\('BL([0-9]+?)'\)"
                found = re.findall(searchPattern, location[0])
                if found:
                    for entry in found:
                        checkList.append(entry)
        checkList = [int(item) for item in checkList]
        checkList = list(set(checkList))
        #checkList.sort()

        formattedList = []
        for num in checkList:
            exlbl_entry = "BL{0}".format(num)
            if exlbl_entry in self.locationMap:
                formattedList.append("{0}. {1}".format(num, self.locationMap[exlbl_entry][1]))

        formattedList = list(set(formattedList))
        # e.g. For Acts 15:36-18:22, formattedList = ['1160. Thyatira', '76. Apollonia', '87. Areopagus/Mars Hill', '590. Iconium', '636. Jerusalem', '880. Neapolis', '108. Asia/Achaia', '118. Athens', '16. Achaia', '431. Galatia', '956. Pontus', '918. Pamphylia', '1025. Samothracia', '266. Caesarea', '281. Cenchrea', '177. Berea', '1182. Troas', '1122. Syria/Syrians', '1158. Thessalonica', '400. Ephesus', '1013. Rome', '601. Italy', '68. Antioch', '865. Mysia', '747. Macedonia', '330. Derbe', '250. Bithynia', '306. Corinth', '59. Amphipolis', '742. Lystra', '946. Phrygia', '316. Chittim/Cyprus', '300. Cilicia', '942. Philippi']

        return formattedList

    def displayMap(self, selectedLocations, browser=False):
        import gmplot
        gmap = gmplot.GoogleMapPlotter(33.877444, 34.234935, 6, map_type='hybrid')
        if config.myGoogleApiKey:
            gmap.apikey = config.myGoogleApiKey

        if selectedLocations:
            for item in selectedLocations:
                try:
                    num = int(re.sub("\..*?$", "", item))
                    exlbl_entry = "BL{0}".format(num)
                    label, name, latitude, longitude = self.locationMap[exlbl_entry]
                    if config.standardAbbreviation == "TC" and exlbl_entry in tc_location_names and tc_location_names[exlbl_entry]:
                        name = tc_location_names[exlbl_entry]
                    elif config.standardAbbreviation == "SC" and exlbl_entry in sc_location_names and sc_location_names[exlbl_entry]:
                        name = sc_location_names[exlbl_entry]
                    googleEarthLink = "https://earth.google.com/web/search/{0},+{1}".format(str(latitude).replace(".", "%2e"), str(longitude).replace(".", "%2e"))
                    if browser:
                        weblink = self.getWeblink(f"EXLB:::exlbl:::{exlbl_entry}", filterCommand=False)
                        info = "<a href='{0}' target='_blank'>{1}</a> [<a href='{2}' target='_blank'>3D</a>]".format(weblink, name, googleEarthLink)
                    elif config.enableHttpServer:
                        info = """<a href="#" onclick="document.title = 'EXLB:::exlbl:::{0}';">{1}</a> [<a href='{2}' target='_blank'>3D</a>]""".format(exlbl_entry, name, googleEarthLink)
                    else:
                        info = """<a href="#" onclick="document.title = 'EXLB:::exlbl:::{0}';">{1}</a> [<a href="#" onclick="document.title = 'online:::{2}';">3D</a>]""".format(exlbl_entry, name, googleEarthLink)
                    gmap.marker(latitude, longitude, label=label, title=name, info_window=info)
                except:
                    pass
        else:
            googleEarthLink = r"https://earth.google.com/web/search/31%2e777444,+35%2e234935"
            if browser:
                weblink = self.getWeblink("EXLB:::exlbl:::BL636", filterCommand=False)
                info = "<a href='{0}' target='_blank'>Jerusalem</a> [<a href='{1}' target='_blank'>3D</a>]".format(weblink, googleEarthLink)
            elif config.enableHttpServer:
                info = """<ref onclick="document.title = 'EXLB:::exlbl:::BL636';">Jerusalem</ref> [<a href='{0}' target='_blank'>3D</a>]""".format(googleEarthLink)
            else:
                info = """<ref onclick="document.title = 'EXLB:::exlbl:::BL636';">Jerusalem</ref> [<ref onclick="document.title = 'online:::{0}';">3D</ref>]""".format(googleEarthLink)
            gmap.marker(31.777444, 35.234935, label="J", title="Jerusalem", info_window=info)

        # HTML text
        return gmap.get()

    def getWeblink(self, command="", filterCommand=True):
        if config.runMode == "terminal":
            server = "http://localhost:8080"
            if not config.mainWindow.isUrlAlive(server):
                server = ""
        else:
            server = ""
        return TextUtil.getWeblink(config.mainWindow.getCommand(command) if config.runMode == "terminal" and filterCommand else command, server=server)

    # CROSSREFERENCE:::
    def textCrossReference(self, command, source):
        if command.count(":::") == 1:
            file, verses = self.splitCommand(command)
            texts = self.getConfirmedTexts(file, True)
            if texts:
                files = [None]
                bibleText = texts[0]
            else:
                files = [file]
                bibleText = config.mainText
        else:
            bibleText = config.mainText
            verses = command
            files = [None]
            for file in glob.glob(config.marvelData + "/xref/*.xref"):
                files.append(os.path.basename(file).replace(".xref", ""))
        verseList = self.extractAllVerses(verses)
        if not verseList:
            return self.invalidCommand()
        biblesSqlite = BiblesSqlite()
        content = ""
        for file in files:
            crossReferenceSqlite = CrossReferenceSqlite(file)
            xrefFile = ""
            if file is not None:
                xrefFile = " ({0})".format(file)
            for verse in verseList:
                content += "<h2>Cross-reference{1}: <ref onclick='document.title=\"{0}\"'>{0}</ref></h2>".format(biblesSqlite.bcvToVerseReference(*verse), xrefFile)
                crossReferenceList = self.extractAllVerses(crossReferenceSqlite.getCrossReferenceList(verse))
                if crossReferenceList:
                    crossReferenceList.insert(0, tuple(verse))
                    content += biblesSqlite.readMultipleVerses(bibleText, crossReferenceList)
                content += "<hr>"
        self.setStudyVerse(config.studyText, verseList[-1])
        return ("study", content, {})

    # TSKE:::
    def tske(self, command, source):
        if not ":::" in command:
            command = f"{config.mainText}:::{command}"
        texts, references = self.splitCommand(command)
        texts = self.getConfirmedTexts(texts, True)
        bibleText = texts[0] if texts else config.mainText
        verseList = self.extractAllVerses(references)
        if not verseList:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            crossReferenceSqlite = CrossReferenceSqlite()
            content = ""
            for verse in verseList:
                content += "<h2>TSKE: <ref  id='v{0}.{1}.{2}' onclick='document.title=\"{3}\"'>{3}</ref></h2>".format(*verse[:3], biblesSqlite.bcvToVerseReference(*verse))
                tskeContent = crossReferenceSqlite.tske(verse)
                content += "<div style='margin: 10px; padding: 0px 10px; border: 1px solid gray; border-radius: 5px;'>{0}</div>".format(tskeContent)
                crossReferenceList = self.extractAllVerses(tskeContent)
                if not crossReferenceList:
                    content += "[No cross-reference is found for this verse!]"
                else:
                    crossReferenceList.insert(0, tuple(verse))
                    content += biblesSqlite.readMultipleVerses(bibleText, crossReferenceList)
                content += "<hr>"
            self.setStudyVerse(config.studyText, verseList[-1])
            return ("study", content, {})

    # COMBO:::
    def textCombo(self, command, source):
        return ("study", "".join([self.textVerseData(command, source, feature) for feature in ("translation", "discourse", "words")]), {})

    # TRANSLATION:::
    def textTranslation(self, command, source):
        return ("study", self.textVerseData(command, source, "translation"), {})

    # DISCOURSE:::
    def textDiscourse(self, command, source):
        return ("study", self.textVerseData(command, source, "discourse"), {})

    # WORDS:::
    def textWords(self, command, source):
        return ("study", self.textVerseData(command, source, "words"), {})

    # called by TRANSLATION::: & WORDS::: & DISCOURSE::: & COMBO:::
    def textVerseData(self, command, source, filename):
        try:
            verseList = self.extractAllVerses(command)
            if not verseList:
                return self.invalidCommand()
            else:
                biblesSqlite = BiblesSqlite()
                verseData = VerseData(filename)
                feature = "{0}{1}".format(filename[0].upper(), filename[1:])
                #content = "<hr>".join(["<h2>{0}: <ref onclick='document.title=\"{1}\"'>{1}</ref></h2>{2}".format(feature, biblesSqlite.bcvToVerseReference(b, c, v), verseData.getContent((b, c, v))) for b, c, v in verseList])
                contentList = []
                for b, c, v in verseList:
                    subContent = "<h2>{0}: <ref onclick='document.title=\"{1}\"'>{1}</ref></h2>{2}".format(feature, biblesSqlite.bcvToVerseReference(b, c, v), verseData.getContent((b, c, v)))
                    if filename == "discourse":
                        subContent = re.sub("(<pm>|</pm>|<n>|</n>)", "", subContent)
                    if b < 40:
                        subContent = re.sub("""(<heb id="wh)([0-9]+?)("[^<>]*?>[^<>]+?</heb>[ ]*)""", r"""\1\2\3 <ref onclick="document.title='READWORD:::BHS5.{0}.{1}.{2}.\2'">{3}</ref>""".format(b, c, v, config.audioBibleIcon), subContent)
                    else:
                        subContent = re.sub("""(<grk id="w[0]*?)([1-9]+[0-9]*?)("[^<>]*?>[^<>]+?</grk>[ ]*)""", r"""\1\2\3 <ref onclick="document.title='READWORD:::OGNT.{0}.{1}.{2}.\2'">{3}</ref>""".format(b, c, v, config.audioBibleIcon), subContent)
                    if filename == "words":
                        if b < 40:
                            subContent = re.sub("""(<ref onclick="document.title=')READWORD(.*?)(<tlit>[^<>]*?</tlit><br><hlr><heb>[^<>]+?</heb>)""", r"\1READWORD\2\3 \1READLEXEME\2", subContent)
                        else:
                            subContent = re.sub("""(<ref onclick="document.title=')READWORD(.*?)(<tlit>[^<>]*?</tlit><br><hlr><grk>[^<>]+?</grk>)""", r"\1READWORD\2\3 \1READLEXEME\2", subContent)
                    contentList.append(subContent)
                content = "<hr>".join(contentList)
                self.setStudyVerse(config.studyText, verseList[-1])
                return content
        except:
            return self.invalidCommand()

    # INDEX:::
    def textIndex(self, command, source):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            parser = BibleVerseParser(config.parserStandarisation)
            indexesSqlite = IndexesSqlite()
            content = ""
            for verse in verseList:
                b, c, v = verse
                content += "<h2>{0} - <ref onclick='document.title=\"{1}\"'>{1}</ref></h2>{2}<hr>".format(config.thisTranslation["menu4_indexes"], parser.bcvToVerseReference(b, c, v), indexesSqlite.getAllIndexes(verse))
            self.setStudyVerse(config.studyText, verseList[-1])
            return ("study", content, {})

    # CHAPTERINDEX:::
    def textChapterIndex(self, command, source):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            parser = BibleVerseParser(config.parserStandarisation)
            indexesSqlite = IndexesSqlite()
            content = ""
            for verse in verseList:
                b, c, v = verse
                content += "<h2>Indexes: <ref onclick='document.title=\"{0}\"'>{0}</ref></h2>{1}<hr>".format(parser.bcvToVerseReference(b, c, v, isChapter=True), indexesSqlite.getChapterIndexes(verse[:2]))
            self.setStudyVerse(config.studyText, verseList[-1])
            return ("study", content, {})

    # SEARCHTHIRDDICTIONARY:::
    def thirdDictionarySearch(self, command, source):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.thirdDictionary, command)
        module, entry = self.splitCommand(command)
        if module == config.thisTranslation['searchAllDictionaries']:
            modules = self.parent.thirdPartyDictionaryList
            showMenu = False
        else:
            modules = [module]
            showMenu = False if config.runMode == "terminal" else True
        content = ""
        for module in modules:
            module = self.parent.isThridPartyDictionary(module)
            if module:
                thirdPartyDictionary = ThirdPartyDictionary(module)
                if entry:
                    content += thirdPartyDictionary.search(entry, showMenu)
                elif not entry:
                    allTopics = [f"<ref>{i[0]}</ref>" if config.runMode == "terminal" else f"""<ref onclick="document.title='THIRDDICTIONARY:::{module[0]}:::{i[0]}'">{i[0]}</ref>""" for i in thirdPartyDictionary.getAllEntries()]
                    content += "<br>".join(allTopics)
        if len(content) > 0:
            return ("study", content, {})
        else:
            return self.invalidCommand("study")

    # THIRDDICTIONARY:::
    def thirdDictionaryOpen(self, command, source):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.thirdDictionary, command)
        module, entry = self.splitCommand(command)
        module = self.parent.isThridPartyDictionary(module)
        if not entry or not module:
            return self.invalidCommand("study")
        else:
            thirdPartyDictionary = ThirdPartyDictionary(module)
            content = thirdPartyDictionary.getData(entry)
            config.thirdDictionaryEntry = entry
            return ("study", f"[MESSAGE]{content}" if config.runMode == "terminal" else content, {})

    # _HIGHLIGHT:::
    def highlightVerse(self, command, source):
        hl = Highlight()
        if command.count(":::") == 0:
            command = "delete:::" + command.strip()
        code, reference = self.splitCommand(command)
        verseList = self.extractAllVerses(reference)
        for b, c, v in verseList:
            if code == "delete":
                hl.removeHighlight(b, c, v)
            else:
                hl.highlightVerse(b, c, v, code)
        return ("", "", {})

    def adjustDarkThemeColorsForExl(self, content):
        content = content.replace("#FFFFFF", "#555555")
        content = content.replace("#DFDFDF", "gray")
        content = content.replace('color="navy"', 'color="#609b00"')
        return content

    def adjustDarkThemeColorsForExternalBook(self, content):
        content = content.replace("background-color:#FFFFFF", "background-color:#323232")
        return content

    # PDF:::
    def openPdfReader(self, command, source):
        if command.count(":::") == 0:
            command += ":::1"
        pdfFile, page = self.splitCommand(command)
        if source == "http":
            return self.parent.openPdfReader(pdfFile, page)
        else:
            if self.parent is not None:
                self.parent.openPdfReader(pdfFile, page)
            return ("", "", {})

    # PDFFIND:::
    def openPdfReaderFind(self, command, source):
        pdfFile, find = self.splitCommand(command)
        if source == "http":
            return self.parent.openPdfReader(pdfFile, 0, False, False, find)
        else:
            if self.parent is not None:
                self.parent.openPdfReader(pdfFile, 0, False, False, find)
            return ("", "", {})

    # SEARCHPDF:::
    def searchPdf(self, command, source):
        content = "<h2>Search PDF for <span style='color: brown;'>{0}</span></h2>".format(command)
        for file in glob.glob(r"{0}/pdf/*.pdf".format(config.marvelData)):
            with open(file, 'rb') as f:
                datafile = f.readlines()
                for line in datafile:
                    try:
                        if command in line.decode("utf-8"):
                            basename = os.path.basename(file)
                            content += """<ref onclick='document.title="PDFFIND:::{0}:::{1}"'>{0}</ref><br>""".format(basename, command)
                            break
                    except Exception as e:
                        pass
        return ("study", content, {'tab_title': "PDF search"})

    # ANYPDF:::
    def openPdfReaderFullpath(self, command, source):
        if command.count(":::") == 0:
            command += ":::1"
        pdfFile, page = self.splitCommand(command)
        if self.parent is not None:
            self.parent.openPdfReader(pdfFile, page, True)
        return ("", "", {})

    # _SAVEPDFCURRENTPAGE:::
    def savePdfCurrentPage(self, page, source):
        command = "ANYPDF:::{0}:::{1}".format(config.pdfTextPath, page)
        if self.parent is not None:
            self.parent.addHistoryRecord("study", command)
        if self.parent is not None:
            self.parent.displayMessage(config.thisTranslation["saved"])
        return ("", "", {})

    # EPUB:::
    def openEpubReader(self, command, source):
        if command.count(":::") == 0:
            command += ":::1"
        pdfFile, page = self.splitCommand(command)
        if source == "http":
            return self.parent.openEpubReader(pdfFile, page)
        else:
            if self.parent is not None:
                self.parent.openEpubReader(pdfFile, page)
            return ("", "", {})

    # IMPORT:::
    def importResources(self, command, source):
        if not command:
            command = "import"
        if self.parent is not None:
            self.parent.importModulesInFolder(command)
        return ("", "", {})

    # DOWNLOAD:::
    def download(self, command, source):
        if config.isDownloading:
            if self.parent is not None:
                self.parent.displayMessage(config.thisTranslation["previousDownloadIncomplete"])
            return ("", config.thisTranslation["previousDownloadIncomplete"], {})
        else:
            action, filename = self.splitCommand(command)
            action = action.lower()
            if action.startswith("marvel") or action.startswith("hymn"):
                if action == "marvelbible":
                    dataset = DatafileLocation.marvelBibles
                elif action == "marvelcommentary":
                    dataset = DatafileLocation.marvelCommentaries
                elif action == "marveldata":
                    dataset = DatafileLocation.marvelData
                else:
                    if self.parent is not None:
                        self.parent.displayMessage("{0} {1}".format(action, config.thisTranslation["unknown"]))
                    return ("", "", {})
                if filename in dataset.keys():
                    databaseInfo = dataset[filename]
                    if os.path.isfile(os.path.join(*databaseInfo[0])):
                        if self.parent is not None:
                            self.parent.displayMessage("{0} {1}".format(filename, config.thisTranslation["alreadyExists"]))
                    else:
                        # self.parent.downloader = Downloader(self.parent, databaseInfo, True)
                        # self.parent.downloader.show()
                        if self.parent is not None:
                            self.parent.displayMessage("{0} {1}".format(config.thisTranslation["Downloading"], filename))
                        if self.parent is not None:
                            self.parent.downloadFile(databaseInfo, False)
                        if self.parent is not None:
                            self.parent.reloadControlPanel(False)
                else:
                    if self.parent is not None:
                        self.parent.displayMessage("{0} {1}".format(filename, config.thisTranslation["notFound"]))
            elif action.startswith("github"):
                if not ("Pygithub" in config.enabled):
                    return ("", "", {})

                if action == "githubbible":
                    repo, directory, text, extension = GitHubRepoInfo.bibles
                elif action == "githubcommentary":
                    repo, directory, text, extension = GitHubRepoInfo.commentaries
                elif action == "githubbook":
                    repo, directory, text, extension = GitHubRepoInfo.books
                elif action == "githubmap":
                    repo, directory, text, extension = GitHubRepoInfo.maps
                elif action == "githubpdf":
                    repo, directory, text, extension = GitHubRepoInfo.pdf
                elif action == "githubepub":
                    repo, directory, text, extension = GitHubRepoInfo.epub
                else:
                    if self.parent is not None:
                        self.parent.displayMessage("{0} {1}".format(action, config.thisTranslation["unknown"]))
                    return ("", "", {})
                from uniquebible.util.GithubUtil import GithubUtil
                github = GithubUtil(repo)
                repoData = github.getRepoData()
                folder = os.path.join(config.marvelData, directory)
                shortFilename = GithubUtil.getShortname(filename)
                shortFilename += "." + extension
                if os.path.isfile(os.path.join(folder, shortFilename)):
                    if self.parent is not None:
                        self.parent.displayMessage("{0} {1}".format(filename, config.thisTranslation["alreadyExists"]))
                else:
                    file = os.path.join(folder, shortFilename+".zip")
                    if filename in repoData.keys():
                        github.downloadFile(file, repoData[filename])
                    elif shortFilename in repoData.keys():
                        github.downloadFile(file, repoData[shortFilename])
                    else:
                        if self.parent is not None:
                            self.parent.displayMessage(
                            "{0} {1}".format(filename, config.thisTranslation["notFound"]))
                        return
                    with zipfile.ZipFile(file, 'r') as zipped:
                        zipped.extractall(folder)
                    os.remove(file)
                    if self.parent is not None:
                        self.parent.reloadControlPanel(False)
                    if self.parent is not None:
                        self.parent.displayMessage("{0} {1}".format(filename, config.thisTranslation["message_installed"]))
            else:
                if self.parent is not None:
                    self.parent.displayMessage("{0} {1}".format(action, config.thisTranslation["unknown"]))

        return ("study", "Downloaded!", {})

    def noAction(self, command, source):
        if config.enableHttpServer:
            return self.textText(config.mainText, source)
        else:
            return ("", "", {})

    # _fixlinksincommentary:::
    def fixLinksInCommentary(self, command, source):
        commentary = Commentary(command)
        if commentary.connection is None:
            if self.parent is not None:
                self.parent.displayMessage("{0} {1}".format(command, config.thisTranslation["notFound"]))
        else:
            commentary.fixLinksInCommentary()
            if self.parent is not None:
                self.parent.displayMessage(config.thisTranslation["message_done"])
        return ("", "", {})

    # DEVOTIONAL:::
    def openDevotional(self, command, source):
        if command.count(":::") == 1:
            devotional, date = self.splitCommand(command)
        else:
            devotional = command
            date = ""
        if self.parent is not None:
            self.parent.openDevotional(devotional, date)
        return ("", "", {})


if __name__ == "__main__":
    from Languages import Languages

    config.thisTranslation = Languages.translation
    config.parserStandarisation = 'NO'
    config.standardAbbreviation = 'ENG'
    config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"

    parser = TextCommandParser("")
    command = "searchhighlight:::all:::mal"
    parser.parser(command)
