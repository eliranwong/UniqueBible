import unittest

import config
from TextCommandParser import TextCommandParser

class TextCommandParserTestCase(unittest.TestCase):

    def setUp(self):
        config.standardAbbreviation = "ENG"
        self.parser = TextCommandParser("")

    # @unittest.skip
    def test_matt_textBibleVerseParser(self):
        command = "Matt 1:1"
        res = self.parser.extractAllVerses(command)
        expected = [(40, 1, 1)]
        self.assertEqual(res, expected)

    # @unittest.skip
    def test_john_textBibleVerseParser(self):
        command = "john 1:1; john 10:10"
        res = self.parser.extractAllVerses(command)
        expected = [(43, 1, 1), (43, 10, 10)]
        self.assertEqual(res, expected)

    # @unittest.skip
    def test_mark_textBibleVerseParser(self):
        command = "john 1:1; john 10:10; mark 2:4; mark 6:7-8"
        res = self.parser.extractAllVerses(command)
        expected = [(43, 1, 1), (43, 10, 10), (41, 2, 4), (41, 6, 7, 6, 8)]
        self.assertEqual(res, expected)

    def test_matt_textBibleVerseParserNew(self):
        command = "Matt 1:1"
        res = self.parser.extractAllVersesNew(command)
        expected = [(40, 1, 1)]
        self.assertEqual(res, expected)

    def test_mark_textBibleVerseParserNew(self):
        command = "john 1:1; john 10:10; mark 2:4; mark 6:7-8"
        res = self.parser.extractAllVersesNew(command)
        expected = [(43, 1, 1), (43, 10, 10), (41, 2, 4), (41, 6, 7, 6, 8)]
        self.assertEqual(res, expected)



