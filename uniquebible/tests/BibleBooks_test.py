import unittest

from uniquebible.util.BibleBooks import BibleBooks

class BibleBooksTestCase(unittest.TestCase):

    # @unittest.skip
    def test_getLastChapter(self):
        self.assertEqual(BibleBooks.getLastChapter(1), 50)
        self.assertEqual(BibleBooks.getLastChapter(2), 40)
        self.assertEqual(BibleBooks.getLastChapter(66), 22)
        self.assertEqual(BibleBooks.getLastChapter(100), 100)


