#!/usr/bin/env python

"""
A python utility to parse bible verse references.
It is both useful for tagging and extracting bible verse references from a text.

This was originally created to format resources <a href="https://marvel.bible">https://marvel.bible</a>.
(The original version is available at https://github.com/eliranwong/bible-verse-parser)

This is now integrated into UniqueBible.app as a core utility.

Features:
1. Search for verse references from text file(s)
2. Add taggings on verse references
3. Support books of bible canon and apocrypha
4. Support tagging on chains of refernces, e.g. Rom 1:2, 3, 5, 8; 9:2, 10
5. Support books of one chapter only, like Obadiah 2, Jude 3, 3John 4, etc.
6. Support chapter references [references without verse number specified], e.g. Gen 1, 3-4; 8, 9-10.
7. Support standardisation of book abbreviations and verse reference format.
8. Support parsing multiple files in one go.
9. Support extracting all references in a text.

Usage [standalone]:
Command line: python BibleVerseParser.py

User Interaction:
Prompting question (1) "Enter a file / folder name here: "<br>
Enter the name of a file, which you want to parse.
OR
Enter the name of a directory containing files, which you want you parse.

Prompting question (2) "Do you want to standardise the format of all bible verse references? [YES/NO] "<br>
Enter YES if you want to standardise all verse references with SBL-style-abbreviations and common format like Gen 2:4; Deut 6:4, etc.<br>
Any answers other than "YES" [case-insensitive] skip the standarisation.
"""
import logging
import os

# import modules, which are ESSENTIAL for running BibleVerseParser
import re, glob, sys
from ast import literal_eval
from uniquebible import config
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.RegexSearch import RegexSearch

"""
START - class BibleVerseParser
"""

class BibleVerseParser:

    standardAbbreviation = {}

    # initialisation
    def __init__(self, standardisation, noOfLinesPerChunkForParsing=None):
        self.logger = logging.getLogger('uba')
        # set standard abbreviation, displayed in UniqueBible
        self.updateStandardAbbreviation()
        # noOfLinesPerChunkForParsing
        self.noOfLinesPerChunkForParsing = config.noOfLinesPerChunkForParsing if noOfLinesPerChunkForParsing is None else noOfLinesPerChunkForParsing
        # set preference of standardisation
        self.standardisation = (standardisation in (True, "YES", "yes", "Yes"))
        self.bibleBooksDict = {}
        self.bibleBooksDictCanonBooksOnly = {}
        pattern = re.compile("[a-zA-Z]")
        bookNames = [bookName for bookName in BibleBooks.name2number.keys() if re.search(pattern, bookName)] if config.parseEnglishBooksOnly else BibleBooks.name2number.keys()
        for bookName in bookNames:
            num = int(BibleBooks.name2number[bookName])
            self.bibleBooksDict[bookName] = num
            if num <= 66:
                self.bibleBooksDictCanonBooksOnly[bookName] = num
            if config.useLiteVerseParsing:
                if "." in bookName:
                    bookName = bookName.replace(".", "")
                    self.bibleBooksDict[bookName] = int(num)
                if bookName[0] < 'a':
                    bookName = bookName.lower()
                    self.bibleBooksDict[bookName] = int(num)
        sortedNames = sorted(self.bibleBooksDict.keys())
        self.sortedNames = sorted(sortedNames, key=len, reverse=True)
        sortedNamesCanonBooksOnly = sorted(self.bibleBooksDictCanonBooksOnly.keys())
        self.sortedNamesCanonBooksOnly = sorted(sortedNamesCanonBooksOnly, key=len, reverse=True)

    # function for converting b c v integers to verse reference string
    def bcvToVerseReference(self, b, c, v, *args, isChapter=False):
        bookNo = str(b)
        if bookNo in self.standardAbbreviation:
            abbreviation = self.standardAbbreviation[bookNo]
            if isChapter:
                return "{0} {1}".format(abbreviation, c)
            if args and len(args) == 2:
                c2, v2 = args
                if c2 == c:
                    if v2 > v:
                        return "{0} {1}:{2}-{3}".format(abbreviation, c, v, v2)
                    elif v2 == v:
                        return "{0} {1}:{2}".format(abbreviation, c, v)
                    else:
                        return ""
                elif c2 > c:
                    return "{0} {1}:{2}-{3}:{4}".format(abbreviation, c, v, c2, v2)
            else:
                return "{0} {1}:{2}".format(abbreviation, c, v)
        else:
            return ""

    # update self.standardAbbreviation
    def updateStandardAbbreviation(self):
        self.checkConfig()
        self.standardAbbreviation = BibleBooks().booksMap.get(config.standardAbbreviation, BibleBooks.abbrev["eng"])
        self.standardFullBookName = {key: value[1] for key, value in self.standardAbbreviation.items()}
        self.standardAbbreviation = {key: value[0] for key, value in self.standardAbbreviation.items()}

    # The following two lines are written for use of this parser outside UniqueBible.app
    # This function check if there is an existing value of config.standardAbbreviation
    def checkConfig(self):
        if not hasattr(config, "standardAbbreviation"):
            config.standardAbbreviation = "ENG"
            config.convertChapterVerseDotSeparator = True
            config.useLiteVerseParsing = False
            config.noOfLinesPerChunkForParsing = 100
            config.parseBookChapterWithoutSpace = True
            config.parseBooklessReferences = True
            config.parseEnglishBooksOnly = False
            config.parseClearSpecialCharacters = False

    # To format of all references by using standard abbreviations.
    def standardReference(self, text):
        for booknumber in self.standardAbbreviation:
            abbreviation = self.standardAbbreviation[booknumber]
            searchReplace = (
                (r'<ref onclick="bcv\('+booknumber+r',([0-9]+?),([0-9]+?)\)">.*?</ref>', '<ref onclick="bcv('+booknumber+r',\1,\2)">'+abbreviation+r' \1:\2</ref>'),
                (r'<ref onclick="bcv\('+booknumber+r',([0-9]+?),([0-9]+?),([0-9]+?),([0-9]+?)\)">.*?</ref>', '<ref onclick="bcv('+booknumber+r',\1,\2,\3,\4)">'+abbreviation+r' \1:\2-\3:\4</ref>'),
                (r' ([0-9]+?):([0-9]+?)-\1:([0-9]+?)</ref>', r' \1:\2-\3</ref>'),
            )
            text = RegexSearch.replace(text, searchReplace)
        return text

    def parseText(self, text, splitInChunks=True, parseBooklessReferences=False, canonicalOnly=False):
        if splitInChunks:
            parsedText = ""
            chunks = text.splitlines(True)
            chunks = [chunks[x:x+self.noOfLinesPerChunkForParsing] for x in range(0, len(chunks), self.noOfLinesPerChunkForParsing)]
            for chunk in chunks:
                parsedText += self.runParseText("".join(chunk), parseBooklessReferences, canonicalOnly)
        else:
            text = text.replace("\n", "")
            parsedText = ""
            start = 0
            end = 0
            # Do not parse embedded images
            while end < len(text):
                if '<img src="data:image' in text[start:]:
                    imgstart = text.find('<img src="data:image', start)

                    block = text[start:imgstart]
                    parsedText += self.runParseText(block, parseBooklessReferences, canonicalOnly)
                    end = text.find(' />', imgstart+10)+3
                    parsedText += text[imgstart:end]
                    start = end
                else:
                    end = len(text)
                    block = text[start: end]
                    parsedText += self.runParseText(block, parseBooklessReferences, canonicalOnly)
            parsedText = parsedText.replace("</p>", "</p>\n")
        return parsedText

    def runParseText(self, text, parseBooklessReferences=False, canonicalOnly=False):
        # Add a space at the end of the text, to avoid indefinite loop in some of the following processes.
        # This extra space will be removed when parsing is finished.
        text = text + " "

        # remove bcv tags, if any, to avoid duplication of tagging in later steps
        searchPattern = r'<ref onclick="bcv\([0-9]+?,[0-9]+?,[0-9][^\(\)]*?\)">(.*?)</ref>'
        searchReplace = (
            (searchPattern, r'\1'),
        )
        text = RegexSearch.deepReplace(text, searchPattern, searchReplace)

        searchBooks = self.sortedNames
        if canonicalOnly:
            searchBooks = self.sortedNamesCanonBooksOnly
        for name in searchBooks:
            # get the string of book name
            bookName = name
            searchReplace = (
                (r'\.', r'[\.]*?'), # make dot "." optional for an abbreviation
                ('^([0-9]+?) ', r'\1[ ]*?'), # make space " " optional in some cases
                ('^([I]+?) ', r'\1[ ]*?'),
                ('^(IV) ', r'\1[ ]*?'),
            )
            bookName = RegexSearch.replace(bookName, searchReplace)
            # get assigned book number from dictionary
            bookNumber = str(self.bibleBooksDict[name])
            # search & replace for marking book
            # bypass the rest of parsing if input text contains a single book name only
            if re.match('^('+bookName+') $', text):
                return RegexSearch.replace(text, (('^('+bookName+') $', r'<ref onclick="bcv({0},1,1)">\1 1:1</ref>'.format(bookNumber)),))
            searchReplace = (
                ('('+bookName+') ([0-9])', '『'+bookNumber+r'｜\1』 \2'),
            )
            text = RegexSearch.replace(text, searchReplace)
            if config.parseBookChapterWithoutSpace:
                text = RegexSearch.replace(text, (('('+bookName+')([0-9])', '『'+bookNumber+r'｜\1』 \2'),))

        # In case a dot sign, instead of a colon sign, is used to separate chapter number and verse number.
        if config.convertChapterVerseDotSeparator:
            text = RegexSearch.replace(text, ((r"』 ([0-9]+?)\.([0-9])", r"』 \1:\2"),))
        searchReplace = (
            # 1st set of taggings
            ('『([0-9]+?)｜([^『』]*?)』 ([0-9]+?):([0-9]+?)([^0-9])', r'<ref onclick="bcv(\1,\3,\4)">\2 \3:\4</ref｝\5'),
            ('『([0-9]+?)｜([^『』]*?)』 ([0-9]+?)([^0-9])', r'<ref onclick="bcv(\1,\3,)">\2 \3</ref｝\4'),
            # fix references without verse numbers
            # fix books with one chapter ONLY; oneChapterBook = [31,57,63,64,65,72,73,75,79,85]
            (r'<ref onclick="bcv\((31|57|63|64|65|72|73|75|79|85),([0-9]+?),\)">', r'<ref onclick="bcv(\1,1,\2)">'),
            # fix chapter references without verse number; assign verse number 1 in taggings
            (r'<ref onclick="bcv\(([0-9]+?),([0-9]+?),\)">', r'<ref onclick="bcv(\1,\2,1)">＊'),
        )
        text = RegexSearch.replace(text, searchReplace)

        # bypass the rest of parsing if input text contains a single reference only
        if re.match('<ref onclick="bcv[^<>]+?>[^<>]+?</ref｝ ', text):
            text = text.replace("｝", ">")
            return text.replace("＊", "")[:-1]

        # check if tagged references are followed by untagged references, e.g. Book 1:1-2:1; 3:2-4, 5; Jude 1
        if parseBooklessReferences and config.parseBooklessReferences:
            searchReplace = (
                ("[EGH][0-9]+?([^0-9])", r"\1"),
                ("｝[^｝,-–;0-9][^｝<>]*?([0-9])", r"｝; \1"),
                ("([0-9])[^｝,-–;0-9][^｝<>]*?([0-9])", r"\1; \2"),
            )
            text = RegexSearch.replace(text, searchReplace)
        searchPattern = '</ref｝[,-–;][ ]*?[0-9]'
        searchReplace = (
            (r'<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([^｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?):([0-9]+?)([^0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\6,\7)">\6:\7</ref｝\8'),
            (r'<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([^＊][^｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?)([^:0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\2,\6)">\6</ref｝\7'),
            (r'<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([^＊][^｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?):([^0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\2,\6)">\6</ref｝:\7'),
            (r'<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">(＊[^｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?)([^:0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\6,1)">＊\6</ref｝\7'),
            (r'<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">(＊[^｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?):([^0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\6,1)">＊\6</ref｝:\7'),
        )
        text = RegexSearch.deepReplace(text, searchPattern, searchReplace)

        if config.parseClearSpecialCharacters:
            searchReplace = (
                ('『[0-9]+?|([^『』]*?)』', r'\1'),
            )
            text = RegexSearch.replace(text, searchReplace)

        searchReplace = (
            (r'(<ref onclick="bcv\([0-9]+?,[0-9]+?,[0-9]+?\)">)＊', r'\1'),
            ('</ref｝', '</ref>'),
        )
        text = RegexSearch.replace(text, searchReplace)

        # handling range of verses
        # e.g. John 3:16 is tagged as <ref onclick="bcv(43,3,16)">John 3:16</ref>
        # e.g. John 3:14-16 is tagged as <ref onclick="bcv(43,3,14,3,16)">John 3:14-16</ref>
        # e.g. John 3:14-4:3 is tagged as <ref onclick="bcv(43,3,14,4,3)">John 3:14-4:3</ref>
        searchPattern = r'<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([^<>]*?)</ref>([-–])<ref onclick="bcv\({0},([0-9]+?),([0-9]+?)\)">'.format(r'\1')
        searchReplace = (
            (searchPattern, r'<ref onclick="bcv(\1,\2,\3,\6,\7)">\4\5'),
        )
        text = RegexSearch.deepReplace(text, searchPattern, searchReplace)

        # final clean up
        searchPattern = r'(<ref onclick="bcv[^>]*?)([\(, ])0([1-9])'
        searchReplace = (
            (searchPattern, r'\1\2\3'),
        )
        text = RegexSearch.deepReplace(text, searchPattern, searchReplace)
        text = RegexSearch.deepReplace(text, "<ref [^>]*?<", (("(<ref [^>]*?)<[^<>]*?>", r"\1"),))

        # return the tagged text, without the extra space added at the beginning of this function.
        return text[:-1]

    def extractAllReferences(self, text, tagged=False, splitInChunks=True):
        if splitInChunks:
            allReferences = []
            chunks = text.splitlines(True)
            chunks = [chunks[x:x+self.noOfLinesPerChunkForParsing] for x in range(0, len(chunks), self.noOfLinesPerChunkForParsing)]
            for chunk in chunks:
                allReferences += self.runExtractAllReferences("".join(chunk), tagged)
        else:
            allReferences = self.runExtractAllReferences(text, tagged)
        return allReferences

    def extractAllReferencesReadable(self, text, tagged=False, splitInChunks=True) -> str:
        allReferences = self.extractAllReferences(text=text, tagged=tagged, splitInChunks=splitInChunks)
        allReferences = [self.bcvToVerseReference(*i) for i in allReferences]
        return "; ".join(allReferences)


    def runExtractAllReferences(self, text, tagged=False):
        if re.search(r"^[0-9]+?\.[0-9]+?\.[0-9]+?$", text.strip()):
            return [tuple([int(i) for i in text.strip().split(".")])]
        if not tagged:
            text = self.parseText(text, False, True)
        # return a list of tuples (b, c, v) or (b, cs, vs, ce, ve)
        return [literal_eval(m) for m in re.findall(r'bcv(\([0-9]+?,[ ]*[0-9]+?,[ ]*[0-9, ]*?\))', text)]

    def extractAllReferencesFast(self, text, tagged=False):
        if tagged:
            return "This is not supported"
        sep = ";"
        if "," in text:
            sep = ","
        ret = [self.verseReferenceToBCV(verse) for verse in text.split(sep)]
        return ret

    def parseFile(self, inputFile, splitInChunks=True):
        # set output filename here
        path, file = os.path.split(inputFile)
        outputFile = os.path.join(path, "tagged_{0}".format(file))

        # open file and read input text
        with open(inputFile, "r", encoding="utf-8") as f:
            originalText = f.read()
        newText = self.replaceTextWithReference(originalText, splitInChunks)
        with open(outputFile, "w", encoding="utf-8") as f:
            f.write(newText)

    def replaceTextWithReference(self, originalText, splitInChunks, canonicalOnly=False):
        newText = ""
        if splitInChunks:
            # Create or empty a file
            chunks = originalText.splitlines(True)
            chunks = [chunks[x:x+self.noOfLinesPerChunkForParsing] for x in range(0, len(chunks), self.noOfLinesPerChunkForParsing)]
            for chunk in chunks:
                parsedText = self.runParseText("".join(chunk), canonicalOnly)
                # standardise the format of bible verse references
                if self.standardisation:
                    parsedText = self.standardReference(parsedText)
                newText += parsedText
        else:
            parsedText = self.runParseText(originalText, canonicalOnly)
            # standardise the format of bible verse references
            if self.standardisation:
                parsedText = self.standardReference(parsedText)
            newText += parsedText
        return newText

    def parseFilesInFolder(self, folder):
        fileList = glob.glob(folder+"/*")
        for file in fileList:
            if os.path.isfile(file):
                self.parseFile(file)

    def extractAllReferencesStartParsing(self, inputName):
        # check if input is a file or a folder
        if os.path.isfile(inputName):
            # parse file
            self.parseFile(inputName)
        elif os.path.isdir(inputName):
            # parse file(s) in a directory
            self.parseFilesInFolder(inputName)
        else:
            # input name is neither a file or a folder
            print("'{0}' is not found.".format(inputName))

    def bookNameToNum(self, bookName):
        bookName = bookName.strip()
        for key in self.sortedNames:
            keyWihtoutDot = re.sub(r"\.$", "", key)
            if bookName.startswith(keyWihtoutDot):
                return self.bibleBooksDict[key]
        return None

    def verseReferenceToBCV(self, text):
        text = text.strip()
        bible = 0
        for key in self.sortedNames:
            if text.startswith(key):
                bible = self.bibleBooksDict[key]
                break
        reference = text[len(key):]
        res = re.search(r'(\s*)(\d*):*(\d*) *-* *(\d*):*(\d*)', reference).groups()
        if res[1] == '':
            return (bible, 1, 1)
        elif res[2] == '' and res[3] == '':
            return bible, int(res[1]), 1
        elif res[2] == '' and not res[3] == '':
            return bible, int(res[1]), 1, int(res[3]), 1
        elif res[3] == '' and res[4] == '':
            return bible, int(res[1]), int(res[2])
        elif res[4] == '':
            return bible, int(res[1]), int(res[2]), int(res[1]), int(res[3])
        else:
            return bible, int(res[1]), int(res[2]), int(res[3]), int(res[4])

    # Convert a book string range into a list of book numbers
    # Gen. -> [1]
    # Gen,Exodus,Matt -> [1, 2, 40]
    # Jude-Rev -> [65, 66]
    # Psa, Matt-John, Rev -> [19, 40, 41, 42, 43, 66]
    # OT -> [1, ..., 39]
    # NT -> [40, ..., 66]
    def extractBookList(self, inputString):
        try:
            books = []
            sections = re.split(",", inputString)
            for section in sections:
                if "-" in section:
                    ranges = re.split("-", section)
                    start = self.bookNameToNum(ranges[0])
                    end = self.bookNameToNum(ranges[1])
                    if start is not None and end is not None:
                        for book in range(start, end + 1):
                            books.append(book)
                else:
                    if section.lower() == "ot":
                        for book in range(1, 40):
                            books.append(book)
                    elif section.lower() == "nt":
                        for book in range(40, 67):
                            books.append(book)
                    elif section.lower() in ("all", "clear"):
                        for book in range(1, 500):
                            books.append(book)
                    else:
                        books.append(self.bookNameToNum(section))
            return books
        except:
            return None

    def extractBookListAsString(self, inputString):
        books = self.extractBookList(inputString)
        if books:
            return ",".join([str(book) for book in books if book])
        return ""

    def extractBookListAsBookNameList(self, inputString):
        books = self.extractBookList(inputString)
        bookList = []
        for book in books:
            if book is not None:
                bookList.append(BibleBooks.abbrev["eng"][str(book)][0])
        return bookList

    def extractBookListAsBookNumberList(self, inputString):
        books = self.extractBookList(inputString)
        bookList = []
        for book in books:
            if book is not None:
                bookList.append(int(book))
        return bookList

"""
END - class BibleVerseParser
"""

def extractFromFile():

    inputName = ""
    standardisation = ""
    arguments = sys.argv

    if (len(arguments) > 1):
        inputName = " ".join(arguments[1:])
        standardisation = "NO"
    else:
        # User Interaction - ask for filename / folder name
        inputName = input("Enter a file / folder name here: ")
        # ask if standardising abbreviations and reference format
        standardisation = input("Do you want to standardise the format of all bible verse references? [YES/NO] ")

    # create an instance of BibleVerseParser
    parser = BibleVerseParser(standardisation, noOfLinesPerChunkForParsing=100)
    # start parsing
    parser.extractAllReferencesStartParsing(inputName)

    # delete object
    del parser

def parseImage():
    text = """<html><body>John 1:1, Acts 10:10, <p><img src="data:image/png;base64,iVBOTkSuQmCC" alt="UniqueBibleApp_black" /></p>Rev 22:1</body></html>"""
    result = BibleVerseParser(True).parseText(text, False, False)
    expectedResult = """<html><body><ref onclick="bcv(43,1,1)">John 1:1</ref>, <ref onclick="bcv(44,10,10)">Acts 10:10</ref>, <p><img src="data:image/png;base64,iVBOTkSuQmCC" alt="UniqueBibleApp_black" /></p><ref onclick="bcv(66,22,1)">Rev 22:1</ref></body></html>"""
    print(result == expectedResult)

if __name__ == '__main__':
    import config

    config.parserStandarisation = False
    bibleVerseParser = BibleVerseParser(config.parserStandarisation)

    print(bibleVerseParser.parseText("I like Jn 3:16-18 and Deu 6:4.")) # I like <ref onclick="bcv(43,3,16,3,18)">Jn 3:16-18</ref> and <ref onclick="bcv(5,6,4)">Deu 6:4</ref>.
    print(bibleVerseParser.standardReference(bibleVerseParser.parseText("I like Jn 3:16-18 and Deu 6:4."))) # I like <ref onclick="bcv(43,3,16,3,18)">John 3:16-18</ref> and <ref onclick="bcv(5,6,4)">Deut 6:4</ref>.
    print(bibleVerseParser.extractAllReferences("I like John 3:16-18 and Deut 6:4.")) # [(43, 3, 16, 3, 18), (5, 6, 4)]
    print(bibleVerseParser.extractAllReferencesReadable("I like John 3:16-18 and Deut 6:4.")) # John 3:16-18; Deut 6:4
    print(bibleVerseParser.verseReferenceToBCV("John 3:16-18")) # (43, 3, 16, 3, 18)
    print(bibleVerseParser.bcvToVerseReference(*(43,3,16,3,18))) # John 3:16-18

    print(bibleVerseParser.bookNameToNum("Exodus")) # 2
    print(bibleVerseParser.extractBookList("1Pe-Rev")) # [60, 61, 62, 63, 64, 65, 66]
    print(bibleVerseParser.extractBookList("Psa, Matt-John, Rev")) # [60, 61, 62, 63, 64, 65, 66]
    print(bibleVerseParser.extractBookListAsBookNameList("Psa, Matt-John, Rev")) # ['Ps', 'Matt', 'Mark', 'Luke', 'John', 'Rev']
    print(bibleVerseParser.extractBookListAsBookNumberList("Psa, Matt-John, Rev")) # [19, 40, 41, 42, 43, 66]
    print(bibleVerseParser.extractBookListAsString("nt")) # 40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66
    print(bibleVerseParser.extractBookList("Oadf")) # [None]

    # Note: `extractBookListAsBookNumberList` is pretty much the same as `extractBookList`, except its name is more self-explanatory.