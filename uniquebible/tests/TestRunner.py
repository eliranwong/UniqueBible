import unittest

from tests import BibleVerseParser_test, TextCommandParser_test, LanguageUtil_test

loader = unittest.TestLoader()
suite = unittest.TestSuite()

suite.addTests(loader.loadTestsFromModule(BibleVerseParser_test))
suite.addTests(loader.loadTestsFromModule(TextCommandParser_test))
suite.addTests(loader.loadTestsFromModule(LanguageUtil_test))

runner = unittest.TextTestRunner(verbosity=3)
result = runner.run(suite)
