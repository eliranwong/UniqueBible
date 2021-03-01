import unittest

from util.LanguageUtil import LanguageUtil


class LanguageUtilTestCase(unittest.TestCase):

    # @unittest.skip
    def test_allLanguageFilesAreSameSize(self):
        languages = LanguageUtil.getCodesSupportedLanguages()
        englishSize = len(LanguageUtil.loadTranslation("en_US"))
        for lang in languages:
            trans = LanguageUtil.loadTranslation(lang)
            self.assertEqual(englishSize, len(trans))

