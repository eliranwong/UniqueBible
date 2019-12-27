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

import os

# File "config.py" is essential for running module "config"
# Create file "config.py" if it is missing.
# The following two lines are written for use of this parser outside UniqueBible.app
if not os.path.isfile("config.py"):
    open("config.py", "a").close()

# import modules, which are ESSENTIAL for running BibleVerseParser
import re, glob, config, sys
from ast import literal_eval
from BibleBooks import BibleBooks
from RegexSearch import RegexSearch

"""
START - class BibleVerseParser
"""

class BibleVerseParser:

    standardAbbreviation = {}

    # initialisation
    def __init__(self, standardisation):
        # set standard abbreviation, displayed in UniqueBible
        self.updateStandardAbbreviation()
        # set preference of standardisation
        self.standardisation = standardisation

    # function for converting b c v integers to verse reference string
    def bcvToVerseReference(self, b, c, v, *args, isChapter=False):
        bookNo = str(b)
        if bookNo in self.standardAbbreviation:
            abbreviation = self.standardAbbreviation[bookNo]
            if isChapter:
                return "{0} {1}".format(abbreviation, c)
            if args and len(args) == 2:
                c2, v2 = args
                if c2 == c and v2 > v:
                    return "{0} {1}:{2}-{3}".format(abbreviation, c, v, v2)
                elif c2 > c:
                    return "{0} {1}:{2}-{3}:{4}".format(abbreviation, c, v, c2, v2)
            else:
                return "{0} {1}:{2}".format(abbreviation, c, v)
        else:
            return "BOOK 0:0"

    # update self.standardAbbreviation
    def updateStandardAbbreviation(self):
        standardAbbreviations = {
            "ENG": BibleBooks.eng,
            "TC": BibleBooks.tc,
            "SC": BibleBooks.sc,
        }
        self.checkConfig()
        self.standardAbbreviation = standardAbbreviations[config.standardAbbreviation]
        self.standardAbbreviation = {key: value[0] for key, value in self.standardAbbreviation.items()}

    # The following two lines are written for use of this parser outside UniqueBible.app
    # This function check if there is an existing value of config.standardAbbreviation
    def checkConfig(self):
        if not hasattr(config, "standardAbbreviation"):
            config.standardAbbreviation = "ENG"
            with open("config.py", "w") as fileObj:
                name, value = ("standardAbbreviation = ", config.standardAbbreviation),
                fileObj.write(name+pprint.pformat(value))

    # To format of all references by using standard abbreviations.
    def standardReference(self, text):
        for booknumber in self.standardAbbreviation:
            abbreviation = self.standardAbbreviation[booknumber]
            searchReplace = (
                ('<ref onclick="bcv\('+booknumber+',([0-9]+?),([0-9]+?)\)">.*?</ref>', '<ref onclick="bcv('+booknumber+r',\1,\2)">'+abbreviation+r' \1:\2</ref>'),
                ('<ref onclick="bcv\('+booknumber+',([0-9]+?),([0-9]+?),([0-9]+?),([0-9]+?)\)">.*?</ref>', '<ref onclick="bcv('+booknumber+r',\1,\2,\3,\4)">'+abbreviation+r' \1:\2-\3:\4</ref>'),
                (r' ([0-9]+?):([0-9]+?)-\1:([0-9]+?)</ref>', r' \1:\2-\3</ref>'),
            )
            text = RegexSearch.replace(text, searchReplace)
        return text

    def parseText(self, text):
        # Add a space at the end of the text, to avoid indefinite loop in some of the following processes.
        # This extra space will be removed when parsing is finished.
        text = text + " "

        # remove bcv tags, if any, to avoid duplication of tagging in later steps
        searchPattern = '<ref onclick="bcv\([0-9]+?,[0-9]+?,[0-9][^\(\)]*?\)">(.*?)</ref>'
        searchReplace = (
            (searchPattern, r'\1'),
        )
        text = RegexSearch.deepReplace(text, searchPattern, searchReplace)

        # search for books; mark them with book numbers, used by https://marvel.bible
        # sorting books by alphabet, then by length
        sortedNames = sorted(BibleBooks.name2number.keys())
        sortedNames = sorted(sortedNames, key=len, reverse=True)
        for name in sortedNames:
            # get the string of book name
            bookName = name
            searchReplace = (
                ('\.', r'[\.]*?'), # make dot "." optional for an abbreviation
                ('^([0-9]+?) ', r'\1[ ]*?'), # make space " " optional in some cases
                ('^([I]+?) ', r'\1[ ]*?'),
                ('^(IV) ', r'\1[ ]*?'),
            )
            bookName = RegexSearch.replace(bookName, searchReplace)
            # get assigned book number from dictionary
            bookNumber = BibleBooks.name2number[name]
            # search & replace for marking book
            searchReplace = (
                ('('+bookName+') ([0-9])', '『'+bookNumber+r'｜\1』 \2'),
            )
            text = RegexSearch.replace(text, searchReplace)

        searchReplace = (
            # 1st set of taggings
            ('『([0-9]+?)｜([^『』]*?)』 ([0-9]+?):([0-9]+?)([^0-9])', r'<ref onclick="bcv(\1,\3,\4)">\2 \3:\4</ref｝\5'),
            ('『([0-9]+?)｜([^『』]*?)』 ([0-9]+?)([^0-9])', r'<ref onclick="bcv(\1,\3,)">\2 \3</ref｝\4'),
            # fix references without verse numbers
            # fix books with one chapter ONLY; oneChapterBook = [31,57,63,64,65,72,73,75,79,85]
            ('<ref onclick="bcv\((31|57|63|64|65|72|73|75|79|85),([0-9]+?),\)">', r'<ref onclick="bcv(\1,1,\2)">'),
            # fix chapter references without verse number; assign verse number 1 in taggings
            ('<ref onclick="bcv\(([0-9]+?),([0-9]+?),\)">', r'<ref onclick="bcv(\1,\2,1)">＊'),
        )
        text = RegexSearch.replace(text, searchReplace)

        # check if tagged references are followed by untagged references, e.g. Book 1:1-2:1; 3:2-4, 5; Jude 1
        searchPattern = '</ref｝[,-–;][ ]*?[0-9]'
        searchReplace = (
            ('<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([^｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?):([0-9]+?)([^0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\6,\7)">\6:\7</ref｝\8'),
            ('<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([^＊][^｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?)([^:0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\2,\6)">\6</ref｝\7'),
            ('<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([^＊][^｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?):([^0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\2,\6)">\6</ref｝:\7'),
            ('<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">(＊[^｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?)([^:0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\6,1)">＊\6</ref｝\7'),
            ('<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">(＊[^｝]*?)</ref｝([,-–;][ ]*?)([0-9]+?):([^0-9])', r'<ref onclick="bcv(\1,\2,\3)">\4</ref｝\5<ref onclick="bcv(\1,\6,1)">＊\6</ref｝:\7'),
        )
        text = RegexSearch.deepReplace(text, searchPattern, searchReplace)

        # clear special markers
        searchReplace = (
            ('『[0-9]+?|([^『』]*?)』', r'\1'),
            ('(<ref onclick="bcv\([0-9]+?,[0-9]+?,[0-9]+?\)">)＊', r'\1'),
            ('</ref｝', '</ref>'),
        )
        text = RegexSearch.replace(text, searchReplace)

        # handling range of verses
        # e.g. John 3:16 is tagged as <ref onclick="bcv(43,3,16)">John 3:16</ref>
        # e.g. John 3:14-16 is tagged as <ref onclick="bcv(43,3,14,3,16)">John 3:14-16</ref>
        # e.g. John 3:14-4:3 is tagged as <ref onclick="bcv(43,3,14,4,3)">John 3:14-4:3</ref>
        searchPattern = '<ref onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([^<>]*?)</ref>([-–])<ref onclick="bcv\({0},([0-9]+?),([0-9]+?)\)">'.format(r'\1')
        searchReplace = (
            (searchPattern, r'<ref onclick="bcv(\1,\2,\3,\6,\7)">\4\5'),
        )
        text = RegexSearch.deepReplace(text, searchPattern, searchReplace)

        # return the tagged text, without the extra space added at the beginning of this function.
        return text[:-1]

    def extractAllReferences(self, text, tagged=False):
        if not tagged:
            text = self.parseText(text)
        # return a list of tuples (b, c, v)
        return [literal_eval(m) for m in re.findall('bcv(\([0-9]+?,[ ]*[0-9]+?,[ ]*[0-9, ]*?\))', text)]

    def parseFile(self, inputFile):
        # set output filename here
        path, file = os.path.split(inputFile)
        outputFile = os.path.join(path, "tagged_{0}".format(file))

        # open file and read input text
        with open(inputFile, "r") as f:
            newData = f.read()

        if newData:
            # parse the opened text
            newData = self.parseText(newData)
            print("'{0}' is parsed.".format(inputFile))

            # standardise the format of bible verse references
            # standardisation is running only if user's answer is 'YES' [case-insensitive]
            if self.standardisation.lower() == "yes":
                newData = self.standardReference(newData)
                print("Verse reference format is standardised.")
            else:
                print("Original verse reference format is reserved.")

            # save output text in a separate file
            with open(outputFile, "w") as f:
                f.write(newData)
                print("New file is saved as '{0}'.".format(outputFile))
        else:
            print("No data is read.")

    def parseFilesInFolder(self, folder):
        fileList = glob.glob(folder+"/*")
        for file in fileList:
            if os.path.isfile(file):
                self.parseFile(file)

    def startParsing(self, inputName):
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

"""
END - class BibleVerseParser
"""

if __name__ == '__main__':
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
    parser = BibleVerseParser(standardisation)
    # start parsing
    parser.startParsing(inputName)

    # delete object
    del parser
