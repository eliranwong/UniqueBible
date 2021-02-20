import glob
import importlib
import locale
from os import path

import config
from Languages import Languages
from Translator import Translator


class LanguageUtil:

    @staticmethod
    def getCodesSupportedLanguages():
        files = sorted(glob.glob("lang/language_*.py"))
        # for file in files:
        #     print(file[14:-3])
        return [file[14:-3] for file in files]

    @staticmethod
    def getNamesSupportedLanguages():
        codes = LanguageUtil.getCodesSupportedLanguages()
        return [Languages.decode(code) for code in codes]

    @staticmethod
    def getSystemDefaultLanguage():
        locale.setlocale(locale.LC_ALL, "")
        return locale.getlocale(locale.LC_MESSAGES)[0]

    @staticmethod
    def determineDefaultLanguage():
        supportedLanguages = LanguageUtil.getCodesSupportedLanguages()
        if hasattr(config, "displayLanguage") and config.displayLanguage in supportedLanguages:
            return config.displayLanguage
        systemLang = LanguageUtil.getSystemDefaultLanguage()
        if systemLang in supportedLanguages:
            return systemLang
        else:
            return "en_US"

    @staticmethod
    def loadTranslation(lang):
        file = "lang.language_{0}".format(lang)
        trans = importlib.import_module(file)
        return trans.translation

    @staticmethod
    def validateLanguageFileSizes():
        languages = LanguageUtil.getCodesSupportedLanguages()
        for lang in languages:
            trans = LanguageUtil.loadTranslation(lang)
            print("{0} has size {1}".format(lang, len(trans)))

    @staticmethod
    def compareLanguageFiles(lang1, lang2):
        count = 0
        trans1 = LanguageUtil.loadTranslation(lang1)
        trans2 = LanguageUtil.loadTranslation(lang2)
        for key1 in trans1.keys():
            if key1 not in trans2.keys():
                count += 1
                print("{0} not in {1} : {2}".format(key1, lang2, trans1[key1]))
        for key2 in trans2.keys():
            if key2 not in trans1.keys():
                count += 1
                print("{0} not in {1} : {2}".format(key2, lang1, trans2[key2]))
        if count == 0:
            print("{0} and {1} contain same keys".format(lang1, lang2))

    @staticmethod
    def createNewLanguageFile(lang, force=False):
        filename = "lang/language_" + lang + ".py"
        if not force and path.exists(filename):
            print(filename + " already exists")
        else:
            print("Creating " + filename)
            master = LanguageUtil.loadTranslation("en_US")
            print("Translating {0} records...".format(len(master)))
            with open(filename, "w", encoding="utf-8") as fileObj:
                fileObj.write("translation = {\n")
                translator = Translator()
                count = 0
                for key in master.keys():
                    count += 1
                    print(count)
                    if count > 1000:
                        break
                    text = master[key]
                    if key in ["menu1_app"]:
                        result = text
                    else:
                        result = translator.translate(text, "en", lang[:2])
                    fileObj.write('    "{0}": "{1}",\n'.format(key, result))
                fileObj.write("}")
                fileObj.close()
                print("{0} lines translated".format(count))

    @staticmethod
    def updateLanguageFile(lang):
        filename = "lang/language_" + lang + ".py"
        if not path.exists(filename):
            print(filename + " does not exist")
        else:
            pass
            english = LanguageUtil.loadTranslation("en_US")
            target = LanguageUtil.loadTranslation(lang)
            missing = ""
            translator = Translator()
            count = 0
            for key in english.keys():
                if key not in target.keys():
                    count += 1
                    print(count)
                    text = english[key]
                    result = translator.translate(text, "en", lang[:2])
                    missing += '    "{0}": "{1}",\n'.format(key, result)
            targetFile = open(filename, "r")
            contents = targetFile.readlines()
            targetFile.close()
            print(len(contents))
            contents.insert(len(contents)-1, missing)
            targetFile = open(filename, "w")
            targetFile.writelines(contents)
            targetFile.close()
            print("{0} lines inserted into {1}".format(count, filename))


# Test code

def test_getCodesSupportedLanguages():
    for lang in LanguageUtil.getCodesSupportedLanguages():
        print(lang)

def test_getNamesSupportedLanguages():
    for lang in LanguageUtil.getNamesSupportedLanguages():
        print(lang)

def test_defaultLanguage():
    print(LanguageUtil.getSystemDefaultLanguage())

def test_loadTranslation():
    print(LanguageUtil.loadTranslation("en_US"))

def validateLanguageFileSizes():
    LanguageUtil.validateLanguageFileSizes()

def compareLanguageFiles(lang1, lang2):
    LanguageUtil.compareLanguageFiles(lang1, lang2)

def createNewLanguageFile(lang, force=False):
    LanguageUtil.createNewLanguageFile(lang, force)

def updateLanguageFile(lang):
    LanguageUtil.updateLanguageFile(lang)

if __name__ == "__main__":

    # test_defaultLanguage()
    # test_getNamesSupportedLanguages()
    # test_loadTranslation()
    # validateLanguageFileSizes()
    # createNewLanguageFile("hi")
    compareLanguageFiles("en_US", "hi")
