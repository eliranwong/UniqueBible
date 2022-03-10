# coding=utf-8
import glob
import os, signal, re, webbrowser, platform, multiprocessing, zipfile, subprocess, config

from util.CatalogUtil import CatalogUtil
from util.GitHubRepoInfo import GitHubRepoInfo
from util.HtmlGeneratorUtil import HtmlGeneratorUtil
from util.TextUtil import TextUtil
from util.LexicalData import LexicalData
from functools import partial
from util.BibleVerseParser import BibleVerseParser
from util.BibleBooks import BibleBooks
from db.BiblesSqlite import BiblesSqlite, Bible, ClauseData
from db.ToolsSqlite import CrossReferenceSqlite, CollectionsSqlite, ImageSqlite, IndexesSqlite, EncyclopediaData, \
    DictionaryData, ExlbData, SearchSqlite, Commentary, VerseData, WordData, BookData, \
    Lexicon, LexiconData
from util.ThirdParty import ThirdPartyDictionary
from util.HebrewTransliteration import HebrewTransliteration
from db.NoteSqlite import NoteSqlite
from util.Translator import Translator
from db.Highlight import Highlight
from util.TtsLanguages import TtsLanguages
from db.BiblesSqlite import MorphologySqlite

#from gui.Downloader import Downloader
from install.module import *
from util.DatafileLocation import DatafileLocation

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
        self.lastKeyword = None
        self.cliTtsProcess = None
        self.qtTtsEngine = None

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
            "parallelverses": (self.textParallelVerses, """
            # [KEYWORD] PARALLELVERSES
            # Feature - Display bible versions of the same chapter in parallel columns with verses aligned"""),
            "parallelverse": (self.textParallelVerses, ""),
            "passages": (self.textPassages, """
            # [KEYWORD] PASSAGES
            # Feature - Display different bible passages of the same bible version in parallel columns. It is created for studying similar passages.
            # Usage - PARALLEL:::[BIBLE_VERSION]:::[BIBLE_REFERENCE]
            # Remarks:
            # 1) Only the bible version last opened on main view is opened if "[BIBLE_VERSION(S)]:::" is omitted.
            # 2) Only the first bible version specified in the command is taken, even multiple bible versions are entered and separated by "_".
            # 3) Users can read an additional version by setting config.addFavouriteToMultiRef as True.
            # 4) Book abbreviations and ranges of verses are supported for bible references.
            # 5) If a chapter reference is entered, only verse 1 of the chapter specified is displayed.
            # e.g. PASSAGES:::Mat 3:13-17; Mark 1:9-11; Luk 3:21-23
            # e.g. PASSAGES:::KJV:::Mat 3:13-17; Mark 1:9-11; Luk 3:21-23"""),
            "overview": (self.textChapterOverview, """
            # [KEYWORD] OVERVIEW
            # e.g. overview:::John 3"""),
            "summary": (self.textChapterSummary, """
            # [KEYWORD] SUMMARY
            # e.g. summary:::John 3"""),
            "concordance": (self.textConcordance, """
            # [KEYWORD] CONCORDANCE
            # Feature - Search a Strong's number bible
            # Usage - CONCORDANCE:::[BIBLE_VERSION(S)]:::[STRONG_NUMBER]
            # Assigning "ALL" as "BIBLE_VERSION(S)" to search all installed Strong's number bibles.
            # e.g. CONCORDANCE:::KJVx:::G3087
            # e.g. CONCORDANCE:::ESVx_KJVx_NIVx_WEBx:::G3087
            # e.g. CONCORDANCE:::ALL:::G3087"""),
            "search": (self.textCountSearch, """
            # [KEYWORD] SEARCH
            # Feature - Search bible / bibles for a string, displaying numbers of hits in individual bible books
            # Usage - SEARCH:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]:::[BIBLE_BOOKS]
            # To search for a string in a bible
            # e.g. SEARCH:::KJV:::love
            # To search with a wild card character "%"
            # e.g. SEARCH:::KJV:::Christ%Jesus
            # To search multiple bibles, separate versions with a character "_"
            # e.g. SEARCH:::KJV_WEB:::love
            # e.g. SEARCH:::KJV_WEB:::Christ%Jesus
            # To search specific books of bible
            # e.g. SEARCH:::KJV:::love:::Matt-John, 1Cor, Rev
            # e.g. SEARCH:::KJV:::temple:::OT
            """),
            "searchall": (self.textSearchBasic, """
            # [KEYWORD] SEARCHALL
            # Feature - Search bible / bibles for a string
            # Usage - SEARCHALL:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]:::[BIBLE_BOOKS]
            # SEARCHALL::: is different from SEARCH::: that SEARCH::: shows the number of hits in individual books only whereas SEARCHALL::: display all texts of the result.
            # e.g. SEARCHALL:::KJV:::love
            # To work on multiple bibles, separate bible versions with a character "_":
            # e.g. SEARCHALL:::KJV_WEB:::love
            # To search specific books of bible
            # e.g. SEARCHALL:::KJV:::love:::Matt-John, 1Cor, Rev
            # e.g. SEARCHALL:::KJV:::temple:::OT
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
            "crossreference": (self.textCrossReference, """
            # [KEYWORD] CROSSREFERENCE
            # e.g. CROSSREFERENCE:::Gen 1:1
            # e.g. CROSSREFERENCE:::[Cross reference file]:::Rev 1:1
            """),
            "tske": (self.tske, """
            # [KEYWORD] TSKE
            # e.g. TSKE:::Gen 1:1"""),
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
            # Usage - COMMENTARY2:::[COMMENTARY_MODULE]:::[BIBLE_REFERENCE]
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
            # e.g. SEARCHTHIRDDICTIONARY:::faith"""),
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
            # similar to searchbook:::, difference is that "searchbookchapter:::" searches chapters only"""),
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
            "vlc": (self.openVlcPlayer, """
            # [KEYWORD] VLC
            # Feature: run VLC player to play mp3 and mp4 files
            # e.g. VLC
            # e.g. VLC:::music/AmazingGrace.mp3
            # e.g. VLC:::video/ProdigalSon.mp4
            """),
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
            "download": (self.download, """
            # [KEYWORD] DOWNLOAD
            # Feature - Download marvel data, github files
            # Usage - DOWNLOAD:::[source]:::[file]
            # source can be MarvelData, HymnLyrics, GitHubBible, GitHubBook, GitHubCommentary
            # e.g. DOWNLOAD:::MarvelBible:::KJV
            """),
            "import": (self.importResources, """
            # [KEYWORD] IMPORT
            # Feature - Import third party resources
            # Usage - IMPORT:::[directory_path_containing_supported_3rd_party_files]
            # Remarks: If a directory is not specified, "import" is used by default.
            # e.g. IMPORT:::import
            """),
            "devotional": (self.openDevotional, """
            # [KEYWORD] DEVOTIONAL
            # Feature - Open today's devotional entry
            # e.g. DEVOTIONAL:::Meyer
            """),
            #
            # Keywords starting with "_" are mainly internal commands for GUI operations
            # They are not recorded in history records.
            #
            "_imv": (self.instantMainVerse, """
            # [KEYWORD] _imv
            # e.g. _imv:::1.1.1
            # e.g. _imv:::43.3.16"""),
            "_imvr": (self.instantMainVerseReference, """
            # [KEYWORD] _imvr
            # 
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
            # [KEYWORD] _htmlimage"""),
            "_openbooknote": (self.openBookNote, """
            # [KEYWORD] _openbooknote
            # e.g. _openbooknote:::43"""),
            "_openchapternote": (self.openChapterNote, """
            # [KEYWORD] _openchapternote
            # e.g. _openchapternote:::43.3"""),
            "_openversenote": (self.openVerseNote, """
            # [KEYWORD] _openversenote
            # e.g. _openversenote:::43.3.16"""),
            "_editbooknote": (self.editBookNote, """
            # [KEYWORD] _editbooknote
            # e.g. _editbooknote:::43"""),
            "_editchapternote": (self.editChapterNote, """
            # [KEYWORD] _editchapternote
            # e.g. _editchapternote:::43.3"""),
            "_editversenote": (self.editVerseNote, """
            # [KEYWORD] _editversenote
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
            # e.g. _biblenote:::1.1.1.[1]"""),
            "_wordnote": (self.textWordNote, """
            # [KEYWORD] _wordnote
            # e.g. _wordnote:::LXX1:::l1"""),
            "_searchword": (self.textSearchWord, """
            # [KEYWORD] _searchword
            # Usage: _searchword:::[1=OT, 2=NT]:::[wordID]
            # e.g. _searchword:::1:::1"""),
            "_harmony": (self.textHarmony, """
            # [KEYWORD] _harmony"""),
            "_promise": (self.textPromise, """
            # [KEYWORD] _promise"""),
            "_paste": (self.pasteFromClipboard, """
            # [KEYWORD] _paste
            # e.g. _paste:::"""),
            "_mastercontrol": (self.openMasterControl, """
            # [KEYWORD] _mastercontrol
            # Usage: _mastercontrol:::
            # Usage: _mastercontrol:::[0-4]"""),
            "_highlight": (self.highlightVerse, """
            # [KEYWORD] _highlight
            # Feature - Highlight a verse
            # Usage - _HIGHLIGHT:::[code]:::[BIBLE_REFERENCE(S)]
            # Examples:
            # e.g. _HIGHLIGHT:::hl1:::John 3:16
            # e.g. _HIGHLIGHT:::hl2:::John 3:16
            # e.g. _HIGHLIGHT:::ul1:::John 3:16
            # e.g. _HIGHLIGHT:::delete:::John 3:16"""),
            "_savepdfcurrentpage": (self.savePdfCurrentPage, """
            # [KEYWORD] _savePdfCurrentPage
            # Feature - Save the current page of PDF
            # Usage - _SAVEPDFCURRENTPAGE:::[page]
            # Example:
            # e.g. _SAVEPDFCURRENTPAGE:::100"""),
            "_setconfig": (self.textSetConfig, """
            # [KEYWORD] _setconfig
            # Feature - Set a config value in config.py.
            # Usage - _setconfig:::[item]:::[value]
            # WARNING! Do NOT use this command unless you know well about config.py.  A mistake can prevent UBA from startup.
            # Remarks: This command works ONLY when config.developer is set to True.
            # Example:
            # e.g. _setconfig:::favouriteBible:::'BSB'"""),
            "fixlinksincommentary": (self.fixLinksInCommentary, """
            # Usage - FIXLINKSINCOMMENTARY:::[commentary]
            # Example:
            # FIXLINKSINCOMMENTARY:::Dakes
            """),
        }
        for key, value in BibleBooks.eng.items():
            book = value[0]
            self.interpreters[book.lower()] = (partial(self.textSearchSingleBook, key), """
            # [KEYWORD] {0}
            # Feature - Search '{0}' ONLY
            # Usage - {0}:::[BIBLE_VERSION(S)]:::[LOOK_UP_STRING]
            # e.g. {0}:::KJV:::love""".format(book))

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
            if keyword in self.interpreters:
                if self.isDatabaseInstalled(keyword):
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
            "search": self.getCoreBiblesInfo(),
            "searchall": self.getCoreBiblesInfo(),
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
        return self.parent.bibleInfo

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
        return ("", "", {})

    # return invalid command
    def invalidCommand(self, source="main"):
        return (source, "INVALID_COMMAND_ENTERED", {})

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
        self.parent.updateMainRefButton()

    def setStudyVerse(self, text, bcvTuple):
        config.studyText = text
        config.studyB, config.studyC, config.studyV, *_ = bcvTuple
        self.parent.updateStudyRefButton()
        config.commentaryB, config.commentaryC, config.commentaryV, *_ = bcvTuple
        self.parent.updateCommentaryRefButton()

    def setCommentaryVerse(self, text, bcvTuple):
        config.commentaryText = text
        config.commentaryB, config.commentaryC, config.commentaryV, *_ = bcvTuple
        self.parent.updateCommentaryRefButton()
        config.studyB, config.studyC, config.studyV, *_ = bcvTuple
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

    def extractAllVersesFast(self, text):
        return BibleVerseParser(config.parserStandarisation).extractAllReferencesFast(text)

    def bcvToVerseReference(self, b, c, v):
        return BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)

    # default function if no special keyword is specified
    def textBibleVerseParser(self, command, text, view, parallel=False):
        compareMatches = re.match("^[Cc][Oo][Mm][Pp][Aa][Rr][Ee]:::(.*?:::)", config.history["main"][-1])
        if config.enforceCompareParallel and view in ("main", "http") and compareMatches and not parallel:
            config.tempRecord = "COMPARE:::{0}{1}".format(compareMatches.group(1), command)
            return self.textCompare("{0}{1}".format(compareMatches.group(1), command), view)
        parallelMatches = re.match("^[Pp][Aa][Rr][Aa][Ll][Ll][Ee][Ll]:::(.*?:::)", config.history["main"][-1])
        if config.enforceCompareParallel and view in ("main", "http") and parallelMatches and not parallel:
            config.tempRecord = "PARALLEL:::{0}{1}".format(parallelMatches.group(1), command)
            return self.textParallel("{0}{1}".format(parallelMatches.group(1), command), view)
        if config.useLiteVerseParsing:
            verseList = self.extractAllVersesFast(command)
            if verseList[0][0] == 0:
                command = re.sub(r" \d+:?\d?$", "", command)
                if config.regexSearchBibleIfCommandNotFound:
                    return self.textSearchRegex("{0}:::{1}".format(text, command), "main")
                elif config.searchBibleIfCommandNotFound:
                    return self.textCountSearch("{0}:::{1}".format(text, command), "main")
                else:
                    return self.invalidCommand()
        else:
            verseList = self.extractAllVerses(command)
        if not verseList:
            if config.regexSearchBibleIfCommandNotFound:
                return self.textSearchRegex("{0}:::{1}".format(text, command), "main")
            elif config.searchBibleIfCommandNotFound:
                return self.textCountSearch("{0}:::{1}".format(text, command), "main")
            else:
                return self.invalidCommand()
        else:
            formattedBiblesFolder = os.path.join(config.marvelData, "bibles")
            formattedBibles = [f[:-6] for f in os.listdir(formattedBiblesFolder) if os.path.isfile(os.path.join(formattedBiblesFolder, f)) and f.endswith(".bible") and not re.search(r"^[\._]", f)]
            if text in ("MOB", "MIB", "MTB", "MPB", "MAB", "LXX1i", "LXX2i", "LXX1", "LXX2") and not config.readFormattedBibles:
                config.readFormattedBibles = True
                self.parent.enableParagraphButtonAction(False)
            elif config.readFormattedBibles and (((text in ("OHGBi", "OHGB") or not text in formattedBibles) and view == "main") or text == "LXX"):
                config.readFormattedBibles = False
                self.parent.enableParagraphButtonAction(False)

            # Custom font styling for Bible
            (fontFile, fontSize, css) = Bible(text).getFontInfo()
            if view == "main":
                config.mainCssBibleFontStyle = css
            elif view == "study":
                config.studyCssBibleFontStyle = css
            if (len(verseList) == 1) and (len(verseList[0]) == 3):
                # i.e. only one verse reference is specified
                bcvTuple = verseList[0]
                # Force book to 1 if it's 0 (when viewing a commentary intro)
                if bcvTuple[1] == 0:
                    bcvTuple = (bcvTuple[0], 1, 1)
                chapters = self.getChaptersMenu(bcvTuple[0], bcvTuple[1], text)
                content = "{0}<hr>{1}<hr>{0}".format(chapters, self.textFormattedBible(bcvTuple, text, view))
            else:
                # i.e. when more than one verse reference is found
                content = self.textPlainBible(verseList, text)
                bcvTuple = verseList[-1]
            content = self.toggleBibleText(content)
            # Add text tag for custom font styling
            content = "<bibletext class='{0}'>{1}</bibletext>".format(text, content)
            if config.openBibleInMainViewOnly:
                self.setMainVerse(text, bcvTuple)
                self.setStudyVerse(text, bcvTuple)
                return ("main", content, {})
            else:
                updateViewConfig, *_ = self.getViewConfig(view)
                updateViewConfig(text, bcvTuple)
                return (view, content, {'tab_title': text})

    def toggleBibleText(self, text):
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
        del biblesSqlite
        return chapteruMenu

    # access to formatted chapter or plain verses of a bible text, called by textBibleVerseParser
    def textPlainBible(self, verseList, text):
        biblesSqlite = BiblesSqlite()
        verses = biblesSqlite.readMultipleVerses(text, verseList)
        del biblesSqlite
        return verses

    def textFormattedBible(self, verse, text, source=""):
        formattedBiblesFolder = os.path.join(config.marvelData, "bibles")
        formattedBibles = [f[:-6] for f in os.listdir(formattedBiblesFolder) if os.path.isfile(os.path.join(formattedBiblesFolder, f)) and f.endswith(".bible") and not re.search(r"^[\._]", f)]
        #marvelBibles = ("MOB", "MIB", "MAB", "MPB", "MTB", "LXX1", "LXX1i", "LXX2", "LXX2i")
        #marvelBibles = list(self.getMarvelBibles().keys())
        # bibleSqlite = Bible(text)
        #if source in ("cli"):
        #    b, c, v, *_ = verse
        #    bibleSqlite = Bible(text)
        #    b, c, v, content = bibleSqlite.readTextVerse(b, c, v)
        #    del bibleSqlite
        if text in formattedBibles and text not in ("OHGB", "OHGBi", "LXX") and config.readFormattedBibles:
            bibleSqlite = Bible(text)
            content = bibleSqlite.readFormattedChapter(verse)
            del bibleSqlite
        else:
            # use plain bibles database when corresponding formatted version is not available
            language = Bible(text).getLanguage()
            content = BiblesSqlite(language).readPlainChapter(text, verse, source)
        return content

    # cmd:::
    # run os command
    def osCommand(self, command, source):
        window = ""
        display = ""
        if config.runMode == "http-server" and not config.enableCmd:
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
        language = "en"
        text = command
        if command.count(":::") != 0:
            language, text = self.splitCommand(command)
        
        # fine-tune
        text = re.sub("[\[\]\(\)'\"]", "", text)
        language = re.sub("\-.*?$", "", language)
        if language in ("iw", "he"):
            text = HebrewTransliteration().transliterateHebrew(text)
            language = "el"
        elif language == "el":
            text = TextUtil.removeVowelAccent(text)

        if not platform.system() == "Windows" and config.gTTS:
            if not self.isCommandInstalled("gtts-cli"):
                installmodule("gTTS")
            if self.isCommandInstalled("gtts-cli") and self.isCommandInstalled("play"):
                command = "gtts-cli '{0}' --lang {1} --nocheck | play -t mp3 -".format(text, language)
                print(command)
                self.cliTtsProcess = subprocess.Popen([command], shell=True, preexec_fn=os.setpgrp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif self.isCommandInstalled("gtts-cli") and not self.isCommandInstalled("play"):
                message = "Install sox FIRST! \nFor examples, run: \non macOS, 'brew install sox' \non Ubuntu / Debian, 'sudo apt install sox' \non Arch Linux, 'sudo pacman -S sox'"
                self.parent.displayMessage(message)
            elif not self.isCommandInstalled("gtts-cli") and not self.isCommandInstalled("play"):
                message = "Install gTTS and sox FIRST! \nFor example, on Arch Linux, run:\n'pip3 install gTSS' and \n'sudo pacman -S sox'"
                self.parent.displayMessage(message)
        return ("", "", {})

    # speak:::
    # run text to speech feature
    def textToSpeech(self, command, source):
        # Stop current playing first if any:
        self.stopTtsAudio()

        # Language codes: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
        language = config.ttsDefaultLangauge
        text = command
        if command.count(":::") != 0:
            language, text = self.splitCommand(command)

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

        if platform.system() == "Linux" and config.espeak:
            if self.isEspeakInstalled:
                isoLang2epeakLang = TtsLanguages().isoLang2epeakLang
                languages = TtsLanguages().isoLang2epeakLang.keys()
                if not (config.ttsDefaultLangauge in languages):
                    config.ttsDefaultLangauge = "en"
                if not (language in languages):
                    self.parent.displayMessage(config.thisTranslation["message_noTtsVoice"])
                    language = config.ttsDefaultLangauge
                language = isoLang2epeakLang[language][0]
                # subprocess is used
                # Discussion on use of "preexec_fn=os.setpgrp": https://stackoverflow.com/questions/23811650/is-there-a-way-to-make-os-killpg-not-kill-the-script-that-calls-it
                self.cliTtsProcess = subprocess.Popen(["espeak -s {0} -v {1} '{2}'".format(config.espeakSpeed, language, text)], shell=True, preexec_fn=os.setpgrp, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
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
                    self.parent.displayMessage(config.thisTranslation["message_noTtsVoice"])

        return ("", "", {})

    def stopTtsAudio(self):
        if (config.espeak or config.gTTS) and (self.cliTtsProcess is not None):
            # The following two lines do not work:
            #self.cliTtsProcess.kill()
            #self.cliTtsProcess.terminate()
            # Therefore, we use:
            os.killpg(os.getpgid(self.cliTtsProcess.pid), signal.SIGTERM)
            self.cliTtsProcess = None
        elif (self.qtTtsEngine is not None):
            self.qtTtsEngine.stop()

    # mp3:::
    def mp3Download(self, command, source):
        downloadCommand = "yt-dlp -x --audio-format mp3"
        if not platform.system() == "Linux":
            # version 1: known issue - the download process blocks the main window
            self.downloadYouTubeFile(downloadCommand, command, config.musicFolder)
        else:
            # version 2: known issue - only works on Linux, but not macOS or Windows
            multiprocessing.Process(target=self.downloadYouTubeFile, args=(downloadCommand, command, config.musicFolder)).start()
            self.parent.displayMessage(config.thisTranslation["downloading"])
        self.parent.reloadResources()
        return ("", "", {})

    # mp4:::
    def mp4Download(self, command, source):
        downloadCommand = "yt-dlp -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"
        if not platform.system() == "Linux":
            # version 1: known issue - the download process blocks the main window
            self.downloadYouTubeFile(downloadCommand, command, config.videoFolder)
        else:
            # version 2: known issue - only works on Linux, but not macOS or Windows
            multiprocessing.Process(target=self.downloadYouTubeFile, args=(downloadCommand, command, config.videoFolder)).start()
            self.parent.displayMessage(config.thisTranslation["downloading"])
        self.parent.reloadResources()
        return ("", "", {})

    def youtubeDownload(self, downloadCommand, youTubeLink):
        if not platform.system() == "Linux":
            # version 1: known issue - the download process blocks the main window
            self.downloadYouTubeFile(downloadCommand, youTubeLink, config.videoFolder, True)
        else:
            # version 2: known issue - only works on Linux, but not macOS or Windows
            multiprocessing.Process(target=self.downloadYouTubeFile, args=(downloadCommand, youTubeLink, config.videoFolder, True)).start()
            self.parent.displayMessage(config.thisTranslation["downloading"])

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
        if self.isFfmpegInstalled() or noFfmpeg:
            if platform.system() == "Linux":
                try:
                    subprocess.run(["cd {2}; {0} {1}".format(downloadCommand, youTubeLink, outputFolder)], shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                    subprocess.Popen([config.open, outputFolder])
                except subprocess.CalledProcessError as err:
                    self.parent.displayMessage(err, title="ERROR:")
            # on Windows
            elif platform.system() == "Windows":
                try:
                    os.system(r"cd .\{2}\ & {0} {1}".format(downloadCommand, youTubeLink, outputFolder))
                    os.system(r"{0} {1}".format(config.open, outputFolder))
                except:
                    self.parent.displayMessage(config.thisTranslation["noSupportedUrlFormat"], title="ERROR:")
            # on Unix-based system, like macOS
            else:
                try:
                    os.system(r"cd {2}; {0} {1}".format(downloadCommand, youTubeLink, outputFolder))
                    os.system(r"{0} {1}".format(config.open, outputFolder))
                except:
                    self.parent.displayMessage(config.thisTranslation["noSupportedUrlFormat"], title="ERROR:")
        else:
            self.parent.displayMessage(config.thisTranslation["ffmpegNotFound"])
            wikiPage = "https://github.com/eliranwong/UniqueBible/wiki/Install-ffmpeg"
            if config.enableHttpServer:
                subprocess.Popen("{0} {1}".format(config.open, wikiPage), shell=True)
            else:
                webbrowser.open(wikiPage)

    # READCHAPTER:::
    def readChapter(self, command, source):
        try:
            text, b, c = command.split(".")
            self.parent.playAudioBibleChapterVerseByVerse(text, b, c)
            return ("", "", {})
        except:
            return self.invalidCommand()

    # READVERSE:::
    def readVerse(self, command, source):
        try:
            text, b, c, v = command.split(".")
            folder = os.path.join(config.musicFolder, text, "{0}_{1}".format(b, c))
            audioFile = os.path.join(folder, "{0}_{1}_{2}_{3}.mp3".format(text, b, c, v))
            self.openVlcPlayer(audioFile, "main")
        except:
            return self.invalidCommand()

    # VLC:::
    def openVlcPlayer(self, command, source):
        if config.isVlcInstalled:
            from gui.VlcPlayer import VlcPlayer
            filename = command
            if self.parent.vlcPlayer is None:
                self.parent.vlcPlayer = VlcPlayer(self, filename)
            else:
                # Fix issue: https://github.com/eliranwong/UniqueBible/issues/947
                #self.parent.vlcPlayer.stop()
                #self.parent.vlcPlayer.loadAndPlayFile(filename)
                self.parent.vlcPlayer.close()
                self.parent.vlcPlayer = VlcPlayer(self, filename)
            self.parent.vlcPlayer.show()
        return ("", "", {})

    # READBIBLE:::
    def readBible(self, command, source):
        if config.isVlcInstalled:
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

    # overview:::
    def textChapterOverview(self, command, source):
        verseList = self.extractAllVerses(command)
        if not verseList:
            return self.invalidCommand()
        else:
            content = ""
            for b, c, *_ in verseList:
                chapterReference = self.bcvToVerseReference(b, c, 1)[:-2]
                subheadings = BiblesSqlite().getChapterSubheadings(b, c)
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
            html = "<hr>".join([Bible(text).formatStrongConcordance(strongNo) for text in texts])
            return ("study", html, {})

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
                    return ("", "", {})
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
                    if config.enforceCompareParallel:
                        self.parent.enforceCompareParallelButtonClicked()
                    updateViewConfig, viewText, viewReference, *_ = self.getViewConfig(source)
                    return self.textBibleVerseParser(viewReference, texts[0], source)
                else:
                    databaseInfo = marvelBibles[text]
                    self.parent.downloadHelper(databaseInfo)
                    return ("", "", {})
            else:
                if config.enforceCompareParallel:
                    self.parent.enforceCompareParallelButtonClicked()
                updateViewConfig, viewText, viewReference, *_ = self.getViewConfig(source)
                return self.textBibleVerseParser(viewReference, texts[0], source)

    # MAIN:::
    def textMain(self, command, source):
        return self.textAnotherView(command, source, "main")

    # STUDY:::
    def textStudy(self, command, source):
        return self.textAnotherView(command, source, "study")

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
            self.parent.displayMessage(translation)
            if config.autoCopyTranslateResult and not config.noQt:
                from qtpy.QtWidgets import QApplication
                QApplication.clipboard().setText(translation)
        else:
            self.parent.displayMessage(config.thisTranslation["ibmWatsonNotEnalbed"])
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
            self.parent.mainView.translateTextIntoUserLanguage(text, language)
        else:
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
            marvelBibles = self.getMarvelBibles()
            text = texts[0]
            if text in marvelBibles:
                fileItems = marvelBibles[text][0]
                if os.path.isfile(os.path.join(*fileItems)):
                    return self.textBibleVerseParser(references, texts[0], target)
                else:
                    databaseInfo = marvelBibles[text]
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
            config.mainCssBibleFontStyle = ""
            texts = confirmedTexts
            if confirmedTexts == ["ALL"]:
                plainBibleList, formattedBibleList = biblesSqlite.getTwoBibleLists()
                texts = set(plainBibleList + formattedBibleList)
            for text in texts:
                (fontFile, fontSize, css) = Bible(text).getFontInfo()
                config.mainCssBibleFontStyle += css
            verses = biblesSqlite.compareVerse(verseList, confirmedTexts)
            del biblesSqlite
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            if confirmedTexts == ["ALL"]:
                updateViewConfig(viewText, verseList[-1])
            else:
                updateViewConfig(confirmedTexts[0], verseList[-1])
            return ("main", verses, {})

    # PARALLELVERSES:::
    def textParallelVerses(self, command, source):
        if command.count(":::") == 0:
            return ("", "", {})
        else:
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
            del biblesSqlite
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            if confirmedTexts == ["ALL"]:
                updateViewConfig(viewText, verseList[-1])
            else:
                updateViewConfig(confirmedTexts[0], verseList[-1])
            return ("main", verses, {})

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
            del biblesSqlite
            updateViewConfig, viewText, *_ = self.getViewConfig(source)
            if confirmedTexts == ["ALL"]:
                updateViewConfig(viewText, verseList[-1])
            else:
                updateViewConfig(confirmedTexts[-1], verseList[-1])
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
                self.parent.downloadHelper(databaseInfo)
                return ("", "", {})
            else:
                if source in ('cli'):
                    tableList = ["{0} {1}".format(text, self.textBibleVerseParser(references, text, source, True)[1])
                                 for text in confirmedTexts]
                    return("main", "<br>".join(tableList), {})
                else:
                    tableList = [("<th><ref onclick='document.title=\"TEXT:::{0}\"'>{0}</ref></th>".format(text),
                                  "<td style='vertical-align: text-top;'><bibletext class={1}>{0}</bibletext></td>"
                                  .format(self.textBibleVerseParser(references, text, source, True)[1], text))
                                 for text in confirmedTexts]
                    versions, verses = zip(*tableList)
                    config.mainCssBibleFontStyle = ""
                    for text in confirmedTexts:
                        (fontFile, fontSize, css) = Bible(text).getFontInfo()
                        config.mainCssBibleFontStyle += css
                    return ("main", "<table style='width:100%; table-layout:fixed;'><tr>{0}</tr><tr>{1}</tr></table>".format("".join(versions), "".join(verses)), {})

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
                self.parent.downloadHelper(databaseInfo)
                return ("", "", {})
            else:
                bibleVerseParser = BibleVerseParser(config.parserStandarisation)
                biblesSqlite = BiblesSqlite()
                passages = bibleVerseParser.extractAllReferences(references)
                tableList = [("<th><ref onclick='document.title=\"BIBLE:::{0}\"'>{0}</ref></th>".format(bibleVerseParser.bcvToVerseReference(*passage)), "<td style='vertical-align: text-top;'>{0}</td>".format(biblesSqlite.readMultipleVerses(text, [passage], displayRef=False))) for passage in passages]
                versions, verses = zip(*tableList)
                return ("study", "<table style='width:100%; table-layout:fixed;'><tr>{0}</tr><tr>{1}</tr></table>".format("".join(versions), "".join(verses)), {})

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
                self.parent.downloadHelper(databaseInfo)
                return ("", "", {})
            else:
                bibleVerseParser = BibleVerseParser(config.parserStandarisation)
                biblesSqlite = BiblesSqlite()
                cs = CollectionsSqlite()
                topic, passagesString = cs.readData("PARALLEL", references.split("."))
                del cs
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
                self.parent.downloadHelper(databaseInfo)
                return ("", "", {})
            else:
                bibleVerseParser = BibleVerseParser(config.parserStandarisation)
                biblesSqlite = BiblesSqlite()
                cs = CollectionsSqlite()
                topic, passagesString = cs.readData("PROMISES", references.split("."))
                del cs
                passages = bibleVerseParser.extractAllReferences(passagesString, tagged=True)
                return ("study", "<h2>{0}</h2>{1}".format(topic, biblesSqlite.readMultipleVerses(text, passages)), {})

    # _biblenote:::
    def textBiblenote(self, command, source):
        if source == "http":
            source = "main"
        texts = {
            "main": config.mainText,
            "study": config.studyText,
        }
        if source in texts:
            bible = Bible(texts[source])
            note = bible.readBiblenote(command)
            del bible
            return ("study", note, {})
        else:
            return ("", "", {})

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
        b, *_ = command.split(".")
        b = int(b)
        self.parent.openBookNote(b)
        return ("", "", {})

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
        b, c, *_ = command.split(".")
        b, c = int(b), int(c)
        self.parent.openChapterNote(b, c)
        return ("", "", {})

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
        b, c, v, *_ = command.split(".")
        b, c, v = int(b), int(c), int(v)
        self.parent.openVerseNote(b, c, v)
        return ("", "", {})

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
        if command:
            b, *_ = command.split(".")
            c = 1
            v = 1
        else:
            b, c, v = None, None, None
        if self.parent.noteSaved or self.parent.warningNotSaved():
            self.parent.openNoteEditor("book", b=b, c=c, v=v)
        return ("", "", {})

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
        if command:
            b, c, *_ = command.split(".")
            v = 1
        else:
            b, c, v = None, None, None
        if self.parent.noteSaved or self.parent.warningNotSaved():
            self.parent.openNoteEditor("chapter", b=b, c=c, v=v)
        return ("", "", {})

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
        if command:
            b, c, v, *_ = command.split(".")
        else:
            b, c, v = None, None, None
        if self.parent.noteSaved or self.parent.warningNotSaved():
            self.parent.openNoteEditor("verse", b=b, c=c, v=v)
        else:
            self.parent.noteEditor.raise_()
        return ("", "", {})

    # _open:::
    def openMarvelDataFile(self, command, source):
        fileitems = command.split("/")
        filePath = os.path.join(config.marvelData, *fileitems)
        if config.enableHttpServer and re.search("\.jpg$|\.jpeg$|\.png$|\.bmp$|\.gif$", filePath.lower()):
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
        else:
            self.parent.openExternalFile(filePath)
            return ("", "", {})

    # open:::
    def openExternalFile(self, command, source):
        fileitems = command.split("/")
        filePath = os.path.join(*fileitems)
        if config.enableHttpServer:
            return ("study", TextUtil.imageToText(filePath), {})
        else:
            self.parent.openExternalFile(filePath)
            return ("", "", {})

    # docx:::
    def openDocxReader(self, command, source):
        if command:
            self.parent.openTextFile(os.path.join(config.marvelData, "docx", command))
        return ("", "", {})

    # opennote:::
    def textOpenNoteFile(self, command, source):
        if command:
            self.parent.openTextFile(command)
        return ("", "", {})

    # _openfile:::
    def textOpenFile(self, command, source):
        fileName = config.history["external"][int(command)]
        if fileName:
            self.parent.openTextFile(fileName)
        return ("", "", {})

    # _editfile:::
    def textEditFile(self, command, source):
        if command:
            self.parent.editExternalFileHistoryRecord(int(command))
        return ("", "", {})

    # _website:::
    def textWebsite(self, command, source):
        if command:
            if config.enableHttpServer and command.startswith("http"):
                subprocess.Popen("{0} {1}".format(config.open, command), shell=True)
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
        info = LexicalData.getLexicalData(command, True)
        return ("instant", info, {})

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
    def instantMainVerse(self, command, source, text=config.mainText):
        if config.instantInformationEnabled and command:
            bcvList = [int(i) for i in command.split(".")]
            info = BiblesSqlite().readMultipleVerses(text, [bcvList])
            if text in config.rtlTexts and bcvList[0] < 40:
                info = "<div style='direction: rtl;'>{0}</div>".format(info)
            return ("instant", info, {})
        else:
            return ("", "", {})

    # _instantword:::
    def instantWord(self, command, source):
        if config.instantInformationEnabled:
            commandList = self.splitCommand(command)
            morphologySqlite = MorphologySqlite()
            wordID = commandList[1]
            wordID = re.sub('^[h0]+?([^h0])', r'\1', wordID, flags=re.M)
            info = morphologySqlite.instantWord(int(commandList[0]), int(wordID))
            del morphologySqlite
            return ("instant", info, {})
        else:
            return ("", "", {})

    # _bibleinfo:::
    def textBibleInfo(self, command, source):
        if self.getConfirmedTexts(command):
            biblesSqlite = BiblesSqlite()
            info = biblesSqlite.bibleInfo(command)
            del biblesSqlite
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
                del commentarySqlite
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
                bibleCommand = "BIBLE:::{0}:::{1} {2}:{3}".format(text, BibleBooks.eng[b][0], config.mainC, config.mainV)
                self.parent.addHistoryRecord("main", bibleCommand)
            menu = HtmlGeneratorUtil().getMenu(command, source)
            return (source, menu, {})
        except:
            return self.invalidCommand()

    # _vndc:::
    def verseNoDoubleClick(self, command, source):
        dotCount = command.count(".")
        if dotCount == 3 and config.enableHttpServer:
            text, b, c, v = command.split(".")
            config.mainText, config.mainB, config.mainC, config.mainV = text, int(b), int(c), int(v)
            bibleCommand = "BIBLE:::{0}:::{1} {2}:{3}".format(text, BibleBooks.eng[b][0], config.mainC, config.mainV)
            self.parent.addHistoryRecord("main", bibleCommand)
        if dotCount != 3 or config.verseNoDoubleClickAction == "_menu" or (config.enableHttpServer and config.verseNoDoubleClickAction.startswith("_cp")):
            if dotCount == 2 and not config.preferHtmlMenu and not config.enableHttpServer:
                text, b, c = command.split(".")
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
            self.parent.openControlPanelTab(index, int(b), int(c), int(v), text),
            return ("", "", {})
        else:
            *_, b, c, v = command.split(".")
            verseReference = "{0} {1}:{2}".format(BibleBooks().eng[b][0], c, v)
            self.parent.addHistoryRecord("main" if config.verseNoDoubleClickAction == "COMPARE" else "study", "{0}:::{1}".format(config.verseNoDoubleClickAction, verseReference))
            return self.mapVerseAction(config.verseNoDoubleClickAction, verseReference, source)

    # _vnsc:::
    def verseNoSingleClick(self, command, source):
        if command.count(".") != 4:
            return self.invalidCommand()
        else:
            text, b, c, v, verseReference = command.split(".")
            bibleCommand = "BIBLE:::{0}:::{1}".format(text, verseReference)
            if config.enableHttpServer:
                config.mainText, config.mainB, config.mainC, config.mainV = text, int(b), int(c), int(v)
                self.parent.addHistoryRecord("main", bibleCommand)
            elif not config.verseNoSingleClickAction == "COMPARE":
                self.parent.passRunTextCommand(bibleCommand, True, source)
            if config.verseNoSingleClickAction == "_menu" or (config.enableHttpServer and config.verseNoSingleClickAction.startswith("_cp")):
                menu = HtmlGeneratorUtil().getMenu("{0}.{1}.{2}.{3}".format(text, b, c, v), source)
                return (source, menu, {})
            elif config.verseNoSingleClickAction.startswith("_cp"):
                index = int(config.verseNoSingleClickAction[-1])
                self.parent.openControlPanelTab(index, int(b), int(c), int(v), text),
                return ("", "", {})
            else:
                if not config.verseNoSingleClickAction == "COMPARE" and config.syncStudyWindowBibleWithMainWindow:
                    self.parent.nextStudyWindowTab()
                self.parent.addHistoryRecord("main" if config.verseNoSingleClickAction == "COMPARE" else "study", "{0}:::{1}".format(config.verseNoSingleClickAction, verseReference))
                return self.mapVerseAction(config.verseNoSingleClickAction, verseReference, source)

    # _cp:::
    # _mastercontrol:::
    def openMasterControl(self, command, source):
        try:
            if command and int(command) < 5:
                index = int(command)
            else:
                index = 0
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
        del commentary
        return ("study", commentaryMenu, {})

    # _book:::
    def textBookMenu(self, command, source):
        bookData = BookData()
        bookMenu = bookData.getMenu(command)
        config.bookChapNum = 0
        del bookData
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
        self.parent.pasteFromClipboard()
        return ("", "", {})

    # _htmlimage:::
    def textHtmlImage(self, command, source):
        content = "<p align='center'><img src='images/{0}'><br><br><ref onclick='openHtmlFile({1}images/{0}{1})'>{0}</ref></p>".format(command, '"')
        return ("popover.{0}".format(source), content, {})

    # _image:::
    def textImage(self, command, source):
        module, entry = self.splitCommand(command)
        imageSqlite = ImageSqlite()
        imageSqlite.exportImage(module, entry)
        del imageSqlite
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
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.commentaryText, command)
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
            content = commentary.getContent(bcvTuple)
            if not content == "INVALID_COMMAND_ENTERED":
                self.setCommentaryVerse(module, bcvTuple)
            del commentary
            return ("study", content, {'tab_title':'Com:' + module})

    # COMMENTARY2:::
    def textCommentary2(self, command, source):
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
                del commentary
                return ("study", content, {})
        else:
            return self.invalidCommand()

    # SEARCHTOOL:::
    def textSearchTool(self, command, source):
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
                del searchSqlite
                content += "<h2>Search <span style='color: brown;'>{0}</span> for <span style='color: brown;'>{1}</span></h2><p>{4}</p><p><b>Exact match:</b><br><br>{2}</p><p><b>Partial match:</b><br><br>{3}".format(module, entry, exactMatch, similarMatch, selectList)
        del indexes
        if len(content) > 0:
            return ("study", content, {'tab_title': 'Search:' + origModule + ':' + entry})
        else:
            return self.invalidCommand()

    # SEARCH:::
    def textCountSearch(self, command, source):
        return self.textCount(command, config.addFavouriteToMultiRef)

    # called by SEARCH:::
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
            del biblesSqlite
            return ("study", searchResult, {})

    # SEARCHALL:::
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

    # called by SEARCHALL::: & ANDSEARCH::: & ORSEARCH::: & ADVANCEDSEARCH::: & REGEXSEARCH:::
    def textSearch(self, command, source, mode, favouriteVersion=False, referenceOnly=False):
        if command.count(":::") == 0:
            command = "{0}:::{1}".format(config.mainText, command)
        commandList = self.splitCommand(command)
        texts = self.getConfirmedTexts(commandList[0])
        searchEntry = commandList[1]
        booksRange = ""
        if searchEntry.count(":::") > 0:
            searchEntry, booksRange = self.splitCommand(searchEntry)
        if not texts:
            return self.invalidCommand()
        else:
            biblesSqlite = BiblesSqlite()
            searchResult = "<hr>".join([biblesSqlite.searchBible(text, mode, searchEntry, favouriteVersion, referenceOnly, booksRange) for text in texts])
            del biblesSqlite
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
        return ("study", content, {'tab_title': 'Mor:' + wordId})

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
            showLexiconMenu = True
        entries = entries.strip()
        if config.useLiteVerseParsing and not config.noQt:
            try:
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
                if not reverse and not module.startswith("Concordance") and entry.startswith("E"):
                    entryList += morphologySqlite.etcbcLexemeNo2StrongNo(entry)
                else:
                    entryList.append(entry)
            if reverse:
                content += "<hr>".join([lexicon.getReverseContent(entry) for entry in entryList])
            else:
                content += "<hr>".join([lexicon.getContent(entry, showLexiconMenu) for entry in entryList])
            del lexicon
        if not content or content == "INVALID_COMMAND_ENTERED":
            return self.invalidCommand()
        else:
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
            del lexicon
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
        del lexicon
        searchSqlite = SearchSqlite()
        morphologyDescription = "<hr>".join([searchSqlite.getContent("m"+morphologyModule.upper(), code) for code in morphologyCode.split("_")])
        del searchSqlite
        return ("study", "{0}<hr>{1}".format(morphologyDescription, lexiconContent), {})

    # _wordnote:::
    def textWordNote(self, command, source):
        if re.search("^(LXX1|LXX2|LXX1i|LXX2i|SBLGNT|SBLGNTl):::", command):
            module, wordID = self.splitCommand(command)
            bibleSqlite = Bible(module)
            data = bibleSqlite.readWordNote(wordID)
            del bibleSqlite
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
        del morphologySqlite
        return ("study", searchResult, {})

    # _searchword:::
    def textSearchWord(self, command, source):
        portion, wordID = self.splitCommand(command)
        morphologySqlite = MorphologySqlite()
        lexeme, lexicalEntry, morphologyString = morphologySqlite.searchWord(portion, wordID)
        lexicalEntry = lexicalEntry.split(",")[0]
        translations = morphologySqlite.distinctMorphology(lexicalEntry)
        items = (lexeme, lexicalEntry, morphologyString, translations)
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
        if config.developer or config.webFullAccess:
            item, value = self.splitCommand(command)
            if not item in config.help.keys():
                return self.invalidCommand("study")
            else:
                newConfig = "{0} = {1}".format(item, value)
                try:
                    exec("config."+newConfig)
                    return ("study", "<p>Configuration changed to:<br>{0}</p>".format(newConfig), {})
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
                exlbData = ExlbData()
                content = exlbData.getContent(commandList[0], commandList[1])
                del exlbData
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
            del clauseData
            self.setStudyVerse(config.studyText, (b, c, v))
            return ("study", content, {})
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
            del indexes
            if module in encyclopediaList:
                config.encyclopedia = module
                encyclopediaData = EncyclopediaData()
                content = encyclopediaData.getContent(module, entry)
                del encyclopediaData
                return ("study", content, {})
            else:
                return self.invalidCommand("study")
        else:
            return self.invalidCommand("study")

    # BOOK:::
    def textBook(self, command, source):
        bookData = BookData()
        bookList = [book for book, *_ in bookData.getCatalogBookList()]
        if command.count(":::") == 0:
        # if command.count(":::") == 0 and command in bookList:
            config.book = command
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
            del bookData
            if not content:
                return self.invalidCommand("study")
            else:
                if not isPDF and config.theme in ("dark", "night"):
                    content = self.adjustDarkThemeColorsForExternalBook(content)
                if config.openBookInNewWindow:
                    self.parent.updateBookButton()
                    return ("popover.study", content, {'tab_title': module[:20], 'pdf_filename': pdfFilename})
                else:
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
            del bookData
            if not content:
                return ("study", config.thisTranslation["search_notFound"], {})
                #return self.invalidCommand("study")
            else:
                self.parent.updateBookButton()
                return ("study", content, {})

    # SEARCHALLBOOKSPDF:::
    def textSearchAllBooksAndPdf(self, command, source):
        view, content1, *_ = self.textSearchBook("ALL:::{0}".format(command), source)
        view, content2, *_ = self.searchPdf(command, source)
        return ("study", content1+content2, {'tab_title': "Books/PDF"})

    # SEARCHBOOKNOTE:::
    def textSearchBookNote(self, command, source):
        if not command:
            return self.invalidCommand("study")
        else:
            config.noteSearchString = command
            noteSqlite = NoteSqlite()
            books = noteSqlite.getSearchedBookList(command)
            del noteSqlite
            return ("study", "<p>\"<b style='color: brown;'>{0}</b>\" is found in <b style='color: brown;'>{1}</b> note(s) on book(s)</p><p>{2}</p>".format(command, len(books), "; ".join(books)), {})

    # SEARCHCHAPTERNOTE:::
    def textSearchChapterNote(self, command, source):
        if not command:
            return self.invalidCommand("study")
        else:
            config.noteSearchString = command
            noteSqlite = NoteSqlite()
            chapters = noteSqlite.getSearchedChapterList(command)
            del noteSqlite
            return ("study", "<p>\"<b style='color: brown;'>{0}</b>\" is found in <b style='color: brown;'>{1}</b> note(s) on chapter(s)</p><p>{2}</p>".format(command, len(chapters), "; ".join(chapters)), {})

    # SEARCHVERSENOTE:::
    def textSearchVerseNote(self, command, source):
        if not command:
            return self.invalidCommand("study")
        else:
            config.noteSearchString = command
            noteSqlite = NoteSqlite()
            verses = noteSqlite.getSearchedVerseList(command)
            del noteSqlite
            return ("study", "<p>\"<b style='color: brown;'>{0}</b>\" is found in <b style='color: brown;'>{1}</b> note(s) on verse(s)</p><p>{2}</p>".format(command, len(verses), "; ".join(verses)), {})

    # CROSSREFERENCE:::
    def textCrossReference(self, command, source):
        if command.count(":::") == 1:
            file, verses = self.splitCommand(command)
            files = [file]
        else:
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
                    content += biblesSqlite.readMultipleVerses(config.mainText, crossReferenceList)
                content += "<hr>"
        del crossReferenceSqlite
        del biblesSqlite
        self.setStudyVerse(config.studyText, verseList[-1])
        return ("study", content, {})

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
                content += "<h2>TSKE: <ref  id='v{0}.{1}.{2}' onclick='document.title=\"{3}\"'>{3}</ref></h2>".format(*verse[:3], biblesSqlite.bcvToVerseReference(*verse))
                tskeContent = crossReferenceSqlite.tske(verse)
                content += "<div style='margin: 10px; padding: 0px 10px; border: 1px solid gray; border-radius: 5px;'>{0}</div>".format(tskeContent)
                crossReferenceList = self.extractAllVerses(tskeContent)
                if not crossReferenceList:
                    content += "[No cross-reference is found for this verse!]"
                else:
                    crossReferenceList.insert(0, tuple(verse))
                    content += biblesSqlite.readMultipleVerses(config.mainText, crossReferenceList)
                content += "<hr>"
            del crossReferenceSqlite
            del biblesSqlite
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
            content = ""
            for verse in verseList:
                b, c, v = verse
                content += "<h2>{0} - <ref onclick='document.title=\"{1}\"'>{1}</ref></h2>{2}<hr>".format(config.thisTranslation["menu4_indexes"], parser.bcvToVerseReference(b, c, v), indexesSqlite.getAllIndexes(verse))
            del indexesSqlite
            del parser
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
            del indexesSqlite
            del parser
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
            showMenu = True
        content = ""
        for module in modules:
            module = self.parent.isThridPartyDictionary(module)
            if entry and module:
                thirdPartyDictionary = ThirdPartyDictionary(module)
                content += thirdPartyDictionary.search(entry, showMenu)
                del thirdPartyDictionary
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
            del thirdPartyDictionary
            return ("study", content, {})

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
            self.parent.openPdfReader(pdfFile, page)
            return ("", "", {})

    # PDFFIND:::
    def openPdfReaderFind(self, command, source):
        pdfFile, find = self.splitCommand(command)
        if source == "http":
            return self.parent.openPdfReader(pdfFile, 0, False, False, find)
        else:
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
        self.parent.openPdfReader(pdfFile, page, True)
        return ("", "", {})

    # _SAVEPDFCURRENTPAGE:::
    def savePdfCurrentPage(self, page, source):
        command = "ANYPDF:::{0}:::{1}".format(config.pdfTextPath, page)
        self.parent.addHistoryRecord("study", command)
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
            self.parent.openEpubReader(pdfFile, page)
            return ("", "", {})

    # IMPORT:::
    def importResources(self, command, source):
        if not command:
            command = "import"
        self.parent.importModulesInFolder(command)
        return ("", "", {})

    # DOWNLOAD:::
    def download(self, command, source):
        if config.isDownloading:
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
                    self.parent.displayMessage("{0} {1}".format(action, config.thisTranslation["unknown"]))
                    return ("", "", {})
                if filename in dataset.keys():
                    databaseInfo = dataset[filename]
                    if os.path.isfile(os.path.join(*databaseInfo[0])):
                        self.parent.displayMessage("{0} {1}".format(filename, config.thisTranslation["alreadyExists"]))
                    else:
                        # self.parent.downloader = Downloader(self.parent, databaseInfo, True)
                        # self.parent.downloader.show()
                        self.parent.displayMessage("{0} {1}".format(config.thisTranslation["Downloading"], filename))
                        self.parent.downloadFile(databaseInfo, False)
                        self.parent.reloadControlPanel(False)
                else:
                    self.parent.displayMessage("{0} {1}".format(filename, config.thisTranslation["notFound"]))
            elif action.startswith("github"):
                if not config.isPygithubInstalled:
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
                    self.parent.displayMessage("{0} {1}".format(action, config.thisTranslation["unknown"]))
                    return ("", "", {})
                from util.GithubUtil import GithubUtil
                github = GithubUtil(repo)
                repoData = github.getRepoData()
                folder = os.path.join(config.marvelData, directory)
                shortFilename = GithubUtil.getShortname(filename)
                shortFilename += "." + extension
                if os.path.isfile(os.path.join(folder, shortFilename)):
                    self.parent.displayMessage("{0} {1}".format(filename, config.thisTranslation["alreadyExists"]))
                else:
                    file = os.path.join(folder, shortFilename+".zip")
                    github.downloadFile(file, repoData[filename])
                    with zipfile.ZipFile(file, 'r') as zipped:
                        zipped.extractall(folder)
                    os.remove(file)
                    self.parent.reloadControlPanel(False)
                    self.parent.displayMessage("{0} {1}".format(filename, config.thisTranslation["message_installed"]))
            else:
                self.parent.displayMessage("{0} {1}".format(action, config.thisTranslation["unknown"]))

        return ("study", "Downloaded!", {})

    def noAction(self, command, source):
        if config.enableHttpServer:
            return self.textText(config.mainText, source)
        else:
            return ("", "", {})

    # FIXLINKSINCOMMENTARY:::
    def fixLinksInCommentary(self, command, source):
        commentary = Commentary(command)
        if commentary.connection is None:
            self.parent.displayMessage("{0} {1}".format(command, config.thisTranslation["notFound"]))
        else:
            commentary.fixLinksInCommentary()
            self.parent.displayMessage(config.thisTranslation["message_done"])

    # DEVOTIONAL:::
    def openDevotional(self, command, source):
        if command.count(":::") == 1:
            devotional, date = self.splitCommand(command)
        else:
            devotional = command
            date = ""
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
