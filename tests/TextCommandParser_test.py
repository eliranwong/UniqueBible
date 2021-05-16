import os
import unittest

from util.FileUtil import FileUtil
FileUtil.createCustomFiles()

import config

config.mainText = "MOB"
config.mainB = 1
config.mainC = 1
config.mainV = 1
config.commentaryB = "cEGNT"
config.commentaryC = "cEGNT"
config.useLiteVerseParsing = True
config.standardAbbreviation = "ENG"
config.parserStandarisation = "NO"
config.noOfLinesPerChunkForParsing = 100
config.convertChapterVerseDotSeparator = True
config.parseBookChapterWithoutSpace = False
config.marvelData = ""
config.parseBooklessReferences = True
config.parseEnglishBooksOnly = False
config.searchBibleIfCommandNotFound = True
config.regexSearchBibleIfCommandNotFound = False
config.noQt = True


from TextCommandParser import TextCommandParser

class TextCommandParserTestCase(unittest.TestCase):

    def setUp(self):
        config.standardAbbreviation = "ENG"
        config.useLiteVerseParsing = False
        self.parser = TextCommandParser("")

    # @unittest.skip
    def test_matt_textBibleVerseParser(self):
        config.useLiteVerseParsing = False
        command = "Matt. 1:1"
        res = self.parser.extractAllVerses(command)
        expected = [(40, 1, 1)]
        self.assertEqual(res, expected)

    # @unittest.skip
    def test_john_textBibleVerseParser(self):
        config.useLiteVerseParsing = False
        command = "John 1:1; John 10:10"
        res = self.parser.extractAllVerses(command)
        expected = [(43, 1, 1), (43, 10, 10)]
        self.assertEqual(res, expected)

    # @unittest.skip
    def test_mark_textBibleVerseParser(self):
        config.useLiteVerseParsing = False
        command = "John 1:1; John 10:10; Mark 2:4; Mark 6:7-8"
        res = self.parser.extractAllVerses(command)
        expected = [(43, 1, 1), (43, 10, 10), (41, 2, 4), (41, 6, 7, 6, 8)]
        self.assertEqual(res, expected)

    # @unittest.skip
    def test_mark_textBibleVerseParserNew(self):
        config.useLiteVerseParsing = False
        command = "John 1:1; John 10:10; Mark 2:4; Mark 6:7-8"
        res = self.parser.extractAllVerses(command)
        expected = [(43, 1, 1), (43, 10, 10), (41, 2, 4), (41, 6, 7, 6, 8)]
        self.assertEqual(res, expected)

    def test_randomtext1_textBibleVerseParser(self):
        config.useLiteVerseParsing = False
        command = "randometext abc Jn 3:16, randometext abc Rm 5:8 randometext abc"
        res = self.parser.extractAllVerses(command)
        expected = [(43, 3, 16), (45, 5, 8)]
        self.assertEqual(res, expected)

    def test_randomtext2_textBibleVerseParser(self):
        config.useLiteVerseParsing = False
        command = "BIBLE:::KJV:::randometext abc Jn 3:16, randometext abc Rm 5:8 randometext abc"
        res = self.parser.extractAllVerses(command)
        expected = [(43, 3, 16), (45, 5, 8)]
        self.assertEqual(res, expected)

    def test_randomtext3_textBibleVerseParser(self):
        config.useLiteVerseParsing = False
        command = "BIBLE:::KJV:::Jn 3:16, Rm 5:8"
        res = self.parser.extractAllVerses(command)
        expected = [(43, 3, 16), (45, 5, 8)]
        self.assertEqual(res, expected)

    def test_multijohn_textBibleVerseParser(self):
        config.useLiteVerseParsing = False
        command = "John 3:16, 18-20, 22; Rm 5:8"
        res = self.parser.extractAllVerses(command)
        expected = [(43, 3, 16), (43, 3, 18, 3, 20), (43, 3, 22), (45, 5, 8)]
        self.assertEqual(res, expected)

    # @unittest.skip
    def test_matt_textBibleVerseParserNew(self):
        config.useLiteVerseParsing = True
        command = "Matt 1:1"
        res = self.parser.extractAllVersesFast(command)
        expected = [(40, 1, 1)]
        self.assertEqual(res, expected)

    # @unittest.skip
    def test_mark_textBibleVerseParser(self):
        config.useLiteVerseParsing = True
        command = "john 1:1; john 10:10; mark 2:4; mark 6:7-8"
        res = self.parser.extractAllVersesFast(command)
        expected = [(43, 1, 1), (43, 10, 10), (41, 2, 4), (41, 6, 7, 6, 8)]
        self.assertEqual(res, expected)

    # @unittest.skip
    def test_romans_textBibleVerseParser(self):
        config.useLiteVerseParsing = True
        command = "rom 1:1"
        res = self.parser.extractAllVersesFast(command)
        expected = [(45, 1, 1)]
        self.assertEqual(res, expected)

    def test_romans2_textBibleVerseParser(self):
        config.useLiteVerseParsing = True
        command = "rom 1:1-10 , 1cor 10:1-13"
        res = self.parser.extractAllVersesFast(command)
        expected = [(45, 1, 1, 1, 10), (46, 10, 1, 10, 13)]
        self.assertEqual(res, expected)

