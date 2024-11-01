import glob, importlib, locale, sys
from uniquebible import config
from os import path
from uniquebible.util.Languages import Languages
from uniquebible.util.Translator import Translator
from uniquebible.util.FileUtil import FileUtil

# config.updateModules("Ibmwatson", True)


class LanguageUtil:

    @staticmethod
    def getCodesSupportedLanguages():
        files = sorted(glob.glob("lang/language_*.py"))
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
        file = "uniquebible.lang.language_{0}".format(lang)
        module = importlib.import_module(file)
        trans = importlib.reload(module)
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
            FileUtil.insertStringIntoFile(filename, missing, -1)
            print("{0} lines inserted into {1}".format(count, filename))


    @staticmethod
    def addLanguageStringToAllFiles(key, englishTranslation):
        codes = LanguageUtil.getCodesSupportedLanguages()
        translator = Translator()
        for code in codes:
            translation = LanguageUtil.loadTranslation(code)
            if key not in translation.keys():
                filename = "lang/language_" + code + ".py"
                if code[:2] == "en":
                    result = englishTranslation
                else:
                    result = translator.translate(englishTranslation, "en", "zh-TW" if code == "zh_HANT" else code[:2])
                data = '    "{0}": "{1}",\n'.format(key, result)
                FileUtil.insertStringIntoFile(filename, data, -1)
                print("Inserted '{0}' into {1}".format(result, code))

    @staticmethod
    def updateLanguageStringToAllFiles(key, englishTranslation):
        codes = LanguageUtil.getCodesSupportedLanguages()
        translator = Translator()
        for code in codes:
            translation = LanguageUtil.loadTranslation(code)
            if key in translation.keys():
                filename = "lang/language_" + code + ".py"
                if code[:2] == "en":
                    result = englishTranslation
                else:
                    result = translator.translate(englishTranslation, "en", "zh-TW" if code == "zh_HANT" else code[:2])
                data = '    "{0}": "{1}",\n'.format(key, result)
                FileUtil.updateStringIntoFile(filename, data)
                print("updated '{0}' into {1}".format(result, code))

    @staticmethod
    def checkLanguageStringToAllFiles(key):
        codes = LanguageUtil.getCodesSupportedLanguages()
        translator = Translator()
        for code in codes:
            translation = LanguageUtil.loadTranslation(code)
            if key in translation.keys():
                print("Founded '{0}' in {1}".format(translation[key], code))
            else:
                print("Not founded in {0}".format(code))

    @staticmethod
    def saveLanguageFile(lang, data):
        filename = "lang/language_" + lang + ".py"
        with open(filename, "w", encoding="utf-8") as fileObj:
            fileObj.write("translation = {\n")
            for line in data:
                key = line[0]
                text = line[1]
                text = text.replace("\n", "\\n")
                fileObj.write('    "{0}": "{1}",\n'.format(key, text))
            fileObj.write("}")
            fileObj.close()


# Test code

def printCodesSupportedLanguages():
    for lang in LanguageUtil.getCodesSupportedLanguages():
        print(lang)

def printNamesSupportedLanguages():
    for lang in LanguageUtil.getNamesSupportedLanguages():
        print(lang)

def printDefaultLanguage():
    print(LanguageUtil.getSystemDefaultLanguage())

def printLoadTranslation():
    print(LanguageUtil.loadTranslation("en_US"))

def validateLanguageFileSizes():
    LanguageUtil.validateLanguageFileSizes()

def compareLanguageFiles(lang1, lang2):
    LanguageUtil.compareLanguageFiles(lang1, lang2)

def createNewLanguageFile(lang, force=False):
    LanguageUtil.createNewLanguageFile(lang, force)

def updateLanguageFile(lang):
    LanguageUtil.updateLanguageFile(lang)

def addLanguageStringToAllFiles(key, englishTranslation):
    LanguageUtil.addLanguageStringToAllFiles(key, englishTranslation)

def updateLanguageStringToAllFiles(key, englishTranslation):
    LanguageUtil.updateLanguageStringToAllFiles(key, englishTranslation)

def checkLanguageStringToAllFiles(key):
    LanguageUtil.checkLanguageStringToAllFiles(key)

def translateWord(text, code):
    translator = Translator()
    result = translator.translate(text, "en", code)
    print(result)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            method = sys.argv[1].strip()
            if len(sys.argv) == 2:
                globals()[method]()
            else:
                name1 = sys.argv[2].strip()
                if len(sys.argv) == 3:
                    globals()[method](name1)
                else:
                    name2 = sys.argv[3].strip()
                    globals()[method](name1, name2)
            print("Done")
        except Exception as e:
            print("Error executing: " + str(e))
    else:
        # printCodesSupportedLanguages()
        addLanguageStringToAllFiles("githubStatistics", "GitHub Statistics")
