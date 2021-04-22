import os
import unittest

if not os.path.isfile("config.py"):
    open("config.py", "w").close()

import config

from BibleVerseParser import BibleVerseParser

class BibleVerseParserTestCase(unittest.TestCase):
    def setUp(self):
        config.standardAbbreviation = 'ENG'
        self.parser = BibleVerseParser(config.standardAbbreviation, 100)

    def test_gen_parseText(self):
        input = "Genesis 1:1-3:1"
        expected = '<ref onclick="bcv(1,1,1,3,1)">Genesis 1:1-3:1</ref>'
        res = self.parser.parseText(input)
        self.assertEqual(expected, res)

    def test_prov_parseText(self):
        input = "Prov 1:1"
        expected = '<ref onclick="bcv(20,1,1)">Prov 1:1</ref>'
        res = self.parser.parseText(input)
        self.assertEqual(expected, res)

    def test_prov_extractAllReferences(self):
        input = "Prov 1:1"
        expected = [(20, 1, 1)]
        res = self.parser.extractAllReferences(input)
        self.assertEqual(expected, res)

    def test_matt_extractAllReferences(self):
        input = "Matt 28:18-20"
        expected = [(40, 28, 18, 28, 20)]
        res = self.parser.extractAllReferences(input)
        self.assertEqual(expected, res)

    def test_1cor_extractAllReferences(self):
        input = "1 Cor 13"
        expected = [(46, 13, 1)]
        res = self.parser.extractAllReferences(input)
        self.assertEqual(expected, res)

    def test_rev_extractAllReferences(self):
        input = "rev 1-10"
        expected = [(66, 1, 1, 10, 1)]
        res = self.parser.extractAllReferences(input)
        self.assertEqual(expected, res)

    def test_gen_verseReferenceToBCV(self):
        input = "gen"
        expected = (1, 1, 1)
        res = self.parser.verseReferenceToBCV(input)
        self.assertEqual(expected, res)

    def test_num_verseReferenceToBCV(self):
        input = "Num. 10"
        expected = (4, 10, 1)
        res = self.parser.verseReferenceToBCV(input)
        self.assertEqual(expected, res)

    def test_job_verseReferenceToBCV(self):
        input = "Job 2-10"
        expected = (18, 2, 1, 10, 1)
        res = self.parser.verseReferenceToBCV(input)
        self.assertEqual(expected, res)

    def test_psa_verseReferenceToBCV(self):
        input = "Psalms 23:1-10"
        expected = (19, 23, 1, 23, 10)
        res = self.parser.verseReferenceToBCV(input)
        self.assertEqual(expected, res)

    def test_pro_verseReferenceToBCV(self):
        input = "Prov. 2:1-10:6"
        expected = (20, 2, 1, 10, 6)
        res = self.parser.verseReferenceToBCV(input)
        self.assertEqual(expected, res)

    def test_1sam_verseReferenceToBCV(self):
        input = "1Sam. 4:5-   10:6"
        expected = (9, 4, 5, 10, 6)
        res = self.parser.verseReferenceToBCV(input)
        self.assertEqual(expected, res)

    def test_2kings_verseReferenceToBCV(self):
        input = "II Ki. 4:5 - 10:6"
        expected = (12, 4, 5, 10, 6)
        res = self.parser.verseReferenceToBCV(input)
        self.assertEqual(expected, res)

    def test_1sam_verseReferenceToBCV(self):
        input = "1 S.  4:5 - 10:9999"
        expected = (9, 4, 5, 10, 9999)
        res = self.parser.verseReferenceToBCV(input)
        self.assertEqual(expected, res)


    def test_mark_verseReferenceToBCV(self):
        input = "mar  3:2"
        expected = (41, 3, 2)
        res = self.parser.verseReferenceToBCV(input)
        self.assertEqual(expected, res)

    def test_2tim_verseReferenceToBCV(self):
        input = " 2 Timothy  5 "
        expected = (55, 5, 1)
        res = self.parser.verseReferenceToBCV(input)
        self.assertEqual(expected, res)

    def test_adddaniel_verseReferenceToBCV(self):
        input = "Additions to Daniel 10"
        expected = (71, 10, 1)
        res = self.parser.verseReferenceToBCV(input)
        self.assertEqual(expected, res)

