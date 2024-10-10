import base64
import glob
import hashlib
import json
import logging
import os
import re
import urllib
from datetime import datetime, timezone
from pathlib import Path

from uniquebible import config
from http import HTTPStatus

from http.server import SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from uniquebible.db.AGBTSData import AGBTSData
from uniquebible.db.BiblesSqlite import BiblesSqlite, Bible, MorphologySqlite
from uniquebible.db.DevotionalSqlite import DevotionalSqlite
from uniquebible.db.ToolsSqlite import Commentary, LexiconData, IndexesSqlite, Book, Lexicon, CrossReferenceSqlite, DictionaryData, \
    SearchSqlite, VerseData
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.util.CatalogUtil import CatalogUtil
from uniquebible.util.LexicalData import LexicalData


class ApiRequestHandler(SimpleHTTPRequestHandler):
    def list_directory(self, path):
        self.send_error(
            HTTPStatus.NOT_FOUND,
            "Not found")
        return None

class RemoteApiHandler(ApiRequestHandler):

    jsonData = {}

    ONE_SEC = "1"
    ONE_HOUR = "3600"
    ONE_DAY = "86400"
    ONE_MONTH = "2592000"
    ONE_YEAR = "31536000"

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger('uba')
        config.internet = True
        config.showHebrewGreekWordAudioLinks = False
        try:
            super().__init__(*args, directory="htmlResources", **kwargs)
        except Exception as ex:
            print("Could not run init")
            print(ex)

    def do_POST(self):
        self.handleBadRequests()

    def do_HEAD(self):
        self.handleBadRequests()

    def handleBadRequests(self):
        self.jsonData = {'status': 'Error', 'message': 'Unsupported method'}
        self.sendJsonData()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header("Access-Control-Allow-Headers", '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.end_headers()

    def sendJsonData(self):
        data = json.dumps(self.jsonData)
        self.commonHeader()
        self.wfile.write(bytes(data, "utf8"))

    def commonHeader(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.send_header("charset", "UTF-8")
        self.send_header("Pragma", "no-cache"),
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "max-age=" + RemoteApiHandler.ONE_DAY + ", stale-while-revalidate=" + RemoteApiHandler.ONE_DAY),
        self.end_headers()

    def sendError(self, message):
        self.jsonData = {'status': 'Error', 'message': message}

    def do_GET(self):
        try:
            self.clientIP = self.client_address[0]
            self.processRequest(self.path)
        except Exception as ex:
            self.jsonData = {'status': 'Error', 'exception': str(ex)}
        self.sendJsonData()

    def processRequest(self, request):
        self.securityCheck()
        query = parse_qs(urlparse(request).query)
        self.jsonData = {'status': "OK"}
        if "?" in request:
            request = request.split("?")[0]
        self.jsonData['request'] = request
        config.marvelData = 'marvelData'
        if query:
            self.jsonData['query'] = query
            if "lang" in query.keys():
                lang = query["lang"][0]
                if os.path.exists('marvelData_' + lang):
                    config.marvelData = 'marvelData_' + lang
        if request.startswith("/api"):
            request = request[4:]
        cmd = request[1:].split("/")
        if len(cmd) > 0:
            command = cmd[0].lower()
            if command == "data":
                self.processDataCommand(cmd, query)
            elif command == "list":
                self.processListCommand(cmd)
            elif command == "bible":
                self.processBibleCommand(cmd)
            elif command == "compare":
                self.processCompareCommand(cmd, query)
            elif command == "book":
                self.processBookCommand(cmd)
            elif command == "commentary":
                self.processCommentaryCommand(cmd)
            elif command == "lexicon":
                self.processLexiconCommand(cmd)
            elif command == "lexiconreverse":
                self.processLexiconReverseCommand(cmd)
            elif command == "devotional":
                self.processDevotionalCommand(cmd)
            elif command == "dictionary":
                self.processDictionaryCommand(cmd)
            elif command == "crossreference":
                self.processCrossReferenceCommand(cmd)
            elif command == "crossreference":
                self.processCrossReferenceCommand(cmd)
            elif command == "search":
                self.processSearchCommand(cmd, query)
            elif command == "concordance":
                self.processConcordanceCommand(cmd, query)
            elif command == "morphology":
                self.processMorphologyCommand(cmd)
            elif command == "searchtool":
                self.processSearchToolCommand(cmd)
            elif command == "discourse":
                self.processDiscourseCommand(cmd)
            elif command == "subheadings":
                self.processSubheadingsCommand(cmd)

    # /data/bible/abbreviations?lang=[eng,sc,tc]
    # /data/bible/book2number?lang=[eng,sc,tc]
    # /data/bible/chapters
    # /data/bible/verses
    # /data/bible/books/TRLIT
    # /data/lex/H3068
    def processDataCommand(self, cmd, query):
        if cmd[1].lower() == "bible":
            if cmd[2].lower() == "abbreviations":
                lang = "eng"
                if query and "lang" in query.keys():
                    lang = query["lang"][0]
                data = []
                for key, value in BibleBooks().abbrev[lang].items():
                    data.append({'i': key, 'a': value[0], 'n': value[1]})
                self.jsonData['data'] = data
            elif cmd[2].lower() == "book2number":
                lang = "eng"
                if query and "lang" in query.keys():
                    lang = query["lang"][0]
                data = []
                for key, value in BibleBooks.name2number.items():
                    data.append({'b': key, 'n': value})
                self.jsonData['data'] = data
            elif cmd[2].lower() == "chapters":
                self.jsonData['data'] = BibleBooks.chapters
            elif cmd[2].lower() == "verses":
                self.jsonData['data'] = BibleBooks.verses
            elif cmd[2].lower() == "books":
                self.jsonData['data'] = [book for book in BiblesSqlite().getBookList(cmd[3])]
        elif cmd[1].lower() == "lex":
            self.jsonData['data'] = LexicalData.getLexicalDataRaw(cmd[2])

    def securityCheck(self):
        if config.apiServerClientId == '':
            return
        else:
            clients = {config.apiServerClientId: {'secret': self.encodeSecret(config.apiServerClientSecret)}}
            auth = self.headers['Authorization']
            if auth:
                basic, creds = auth.split()
                clientId, clientSecret = base64.b64decode(creds).decode().split(':')
                if clientId in clients.keys():
                    if clientSecret == clients[clientId]['secret']:
                        return
            raise Exception('Unauthorized')

    def encodeSecret(self, secret):
        secret = secret + str(datetime.now(timezone.utc).month)
        secret = hashlib.md5(secret.encode())
        secret = secret.hexdigest()
        return secret

    # /bible
    # /bible/KJV/43/3
    # /bible/KJV/44/3/16
    def processBibleCommand(self, cmd):
        if len(cmd) == 1:
            self.jsonData['data'] = [bible for bible in BiblesSqlite().getBibleList()]
            return
        elif len(cmd) < 4:
            self.sendError("Invalid Bible command")
            return
        if len(cmd) == 4:
            if cmd[1] in ["MOB", "MAB", "MIB", "MPB", "MTB"]:
                book, chapter, scripture = Bible(cmd[1]).readTextChapterRaw(cmd[2], cmd[3])
                data = re.findall("<verse>(.*?)</verse>", scripture)
                verses = []
                count = 1
                for passage in data:
                    verses.append([cmd[2], cmd[3], count, passage])
                    count += 1
            else:
                verses = BiblesSqlite().readTextChapter(cmd[1], cmd[2], cmd[3])
        elif len(cmd) == 5:
            verses = [BiblesSqlite().readTextVerse(cmd[1], cmd[2], cmd[3], cmd[4])]
        rows = []
        for verse in verses:
            rows.append({'b': verse[0], 'c': verse[1], 'v': verse[2], 't': verse[3]})
        self.jsonData['data'] = rows

    # /book
    # /book/Hymn+Lyrics+-+English
    # /book/Hymn+Lyrics+-+English/Amazing+Grace
    def processBookCommand(self, cmd):
        CatalogUtil.reloadLocalCatalog()
        if len(cmd) == 1:
            self.jsonData['data'] = [book for book in CatalogUtil.getBooks()]
            return
        elif len(cmd) < 2:
            self.sendError("Invalid Book command")
            return
        module = cmd[1].replace("+", " ")
        module = module.replace("&quest;", "?")
        module = urllib.parse.unquote(module)
        if len(cmd) == 2:
            self.jsonData['data'] = [topic for topic in Book(module).getTopicList()]
        else:
            chapter = cmd[2].replace("+", " ")
            chapter = chapter.replace("&quest;", "?")
            chapter = urllib.parse.unquote(chapter)
            # chapter = chapter.replace("%3C", "<")
            # chapter = chapter.replace("%3E", ">")
            data = Book(module).getContentByChapter(chapter)
            self.jsonData['data'] = data if data else ("[Not found]",)

    # /commentary/ABC/43/1
    def processCommentaryCommand(self, cmd):
        config.commentariesFolder = os.path.join(config.marvelData, "commentaries")
        if len(cmd) == 1:
            self.jsonData['data'] = [commentary for commentary in Commentary().getCommentaryList()]
            return
        elif len(cmd) < 4:
            self.sendError("Invalid Commentary command")
            return
        commentary = urllib.parse.unquote(cmd[1])
        data = Commentary(commentary).getRawContent(cmd[2], cmd[3])
        self.jsonData['data'] = data if data else ("[Not found]",)

    # /lexicon
    # /lexicon/TBESG/G5
    def processLexiconCommand(self, cmd):
        CatalogUtil.reloadLocalCatalog()
        if len(cmd) == 1:
            self.jsonData['data'] = [lexicon for lexicon in LexiconData().lexiconList]
            return
        elif len(cmd) < 3:
            self.sendError("Invalid Lexicon command")
            return
        data = Lexicon(cmd[1]).getRawContent(cmd[2])
        self.jsonData['data'] = data if data else ("[Not found]",)

    # /lexiconreverse
    # /lexiconreverse/TRLIT/love
    def processLexiconReverseCommand(self, cmd):
        CatalogUtil.reloadLocalCatalog()
        if len(cmd) == 1:
            self.jsonData['data'] = [lexicon for lexicon in LexiconData().lexiconList]
            return
        elif len(cmd) < 3:
            self.sendError("Invalid Lexicon command")
            return
        data = Lexicon(cmd[1]).getRawReverseContent(cmd[2])
        self.jsonData['data'] = data if data else ("[Not found]",)

    # /devotional
    # /devotional/Chambers+-+My+Utmost+For+His+Highest/12/25
    def processDevotionalCommand(self, cmd):
        if len(cmd) == 1:
            self.jsonData['data'] = [Path(devotional).stem for devotional in sorted(glob.glob(os.path.join(config.marvelData, "devotionals", "*.devotional")))]
            return
        elif len(cmd) < 4:
            self.sendError("Invalid Lexicon command")
            return
        devotional = cmd[1].replace("+", " ")
        self.jsonData['data'] = DevotionalSqlite(devotional).getEntry(cmd[2], cmd[3])

    # /dictionary
    # /dictionary/search/FAU/temple
    # /dictionary/content/FAU3650
    def processDictionaryCommand(self, cmd):
        if len(cmd) == 1:
            self.jsonData['data'] = [dictionary[0] for dictionary in IndexesSqlite().dictionaryList]
            return
        elif len(cmd) < 3:
            self.sendError("Invalid Dictionary command")
            return
        if cmd[1].lower() == "search":
            self.jsonData['data'] = {'exact': SearchSqlite().getContent(cmd[2], cmd[3]),
                                     'similar': SearchSqlite().getSimilarContent(cmd[2], cmd[3])}
        elif cmd[1].lower() == "content":
            self.jsonData['data'] = DictionaryData().getRawContent(cmd[2])

    # /crossreference/1/1/1
    # /crossreference/1/1/1/KJV
    def processCrossReferenceCommand(self, cmd):
        if len(cmd) < 4:
            self.sendError("Invalid Cross Reference command")
            return
        data = CrossReferenceSqlite().getCrossReferenceList((cmd[1], cmd[2], cmd[3]))
        if len(cmd) == 4:
            self.jsonData['data'] = data
        else:
            versesData = []
            verses = BibleVerseParser(config.parserStandarisation).extractAllReferencesFast(data)
            text = cmd[4]
            for (b, c, v, *_) in verses:
                record = Bible(text).readTextVerse(b, c, v)
                versesData.append(record)
            self.jsonData['data'] = versesData

    # /compare/1/1/1?text=KJV&text=TRLIT&text=WEB
    def processCompareCommand(self, cmd, query):
        if len(cmd) < 4:
            self.sendError("Invalid Compare command")
            return
        if query:
            texts = query["text"]
        else:
            texts = ['KJV']
        self.jsonData['data'] = BiblesSqlite().compareVerseRaw((cmd[1], cmd[2], cmd[3]), texts)

    # /search?searchText=faith
    def processSearchCommand(self, cmd, query):
        try:
            searchText = query["searchText"][0]
            type = query["type"][0] if "type" in query.keys() else "bible"
            if type == "bible":
                text = query["text"][0] if "text" in query.keys() else "KJV"
                query = "SELECT Book, Chapter, Verse, Scripture FROM Verses "
                query += "WHERE "
                query += "(Scripture LIKE ?) "
                query += "ORDER BY Book, Chapter, Verse "
                query += "LIMIT 5000 "
                if '"' in searchText:
                    searchText = searchText.replace('"', '')
                else:
                    searchText = searchText.replace(" ", "%").replace("+", "%")
                t = ("%{0}%".format(searchText),)
                verses = Bible(text).getSearchVerses(query, t)

                self.jsonData['data'] = verses
        except Exception as ex:
            self.sendError("Invalid search command - " + ex)

    # /concordance/KJVx/G1654
    def processConcordanceCommand(self, cmd, query):
        try:
            text = cmd[1]
            strongs = cmd[2]
            query = "SELECT Book, Chapter, Verse, Scripture FROM Verses "
            query += "WHERE "
            query += "(Scripture LIKE ?) "
            query += "ORDER BY Book, Chapter, Verse "
            query += "LIMIT 5000 "
            t = ("%{0} %".format(strongs),)
            verses = Bible(text).getSearchVerses(query, t)

            processed = []
            for data in verses:
                verse = data[3].replace(strongs + " ", "XXXXX")
                verse = re.sub(r"[HG][0-9]+? ", "", verse)
                verse = re.sub(r" ([,.;:])", "\\1", verse)
                verse = verse.replace("XXXXX", strongs + " ")
                processed.append((data[0], data[1], data[2], verse))

            self.jsonData['data'] = processed
        except Exception as ex:
            self.sendError("Invalid search command - " + ex)

    # /morphology/1/34684
    def processMorphologyCommand(self, cmd):
        if len(cmd) < 3:
            self.sendError("Invalid Morphology command")
            return
        morphologySqlite = MorphologySqlite()
        wordID, clauseID, b, c, v, textWord, lexicalEntry, morphologyCode, morphology, lexeme, transliteration, pronuciation, interlinear, translation, gloss = morphologySqlite.searchWordRaw(cmd[1], cmd[2])
        lexicalEntry = lexicalEntry.split(",")[0]
        translations = morphologySqlite.distinctMorphology(lexicalEntry)
        self.jsonData['data'] = (textWord, lexeme, lexicalEntry, morphologyCode, morphology, transliteration, pronuciation, interlinear, translation, gloss, translations)

    # /searchtool/mETCBC/adjv.f.pl.a
    def processSearchToolCommand(self, cmd):
        try:
            data = SearchSqlite().getContent(cmd[1], cmd[2])
            self.jsonData['data'] = data
        except Exception as ex:
            self.sendError("Invalid search command - " + ex)

    # /discourse/1/1/1
    def processDiscourseCommand(self, cmd):
        try:
            verseData = VerseData("discourse")
            data = verseData.getContent((int(cmd[1]), int(cmd[2]), int(cmd[3])))
            self.jsonData['data'] = data
        except Exception as ex:
            self.sendError("Invalid discourse command - " + ex)

    # /subheadings/1/1
    def processSubheadingsCommand(self, cmd):
        try:
            if len(cmd) != 3:
                self.sendError("Invalid subheadings command")
                return
            agbtsData = AGBTSData()
            data = {str(i[2]): i[3] for i in agbtsData.getchapterSubheadings(cmd[1], cmd[2])}
            self.jsonData['data'] = data
        except Exception as ex:
            self.sendError("Invalid subheadings command - " + ex)
