#!/usr/bin/env python3

import re, glob, os, sys, pprint
#import platform
#if (platform.system() != "Windows"):
from ast import literal_eval

class RegexSearch:

    # A simple search & replace.
    @staticmethod
    def replace(text, searchReplace, multiLine=True):
        for search, replace in searchReplace:
            if multiLine:
                text = re.sub(search, replace, text, flags=re.M)
            else:
                text = re.sub(search, replace, text)
        return text

    # Searching in a loop until a specific pattern is no longer found.
    @staticmethod
    def deepReplace(text, searchPattern, searchReplace, multiLine=True):
        p = re.compile(searchPattern, flags=re.M) if multiLine else re.compile(searchPattern)
        while p.search(text):
            for search, replace in searchReplace:
                if multiLine:
                    text = re.sub(search, replace, text, flags=re.M)
                else:
                    text = re.sub(search, replace, text)
        return text

    def searchFile(self, inputFile, searchReplace=None, overwrite=False, deepSearchPattern=None):
        # set output filename
        path, filename = os.path.split(inputFile)
        if overwrite:
            outputFilename = filename
            outputFile = inputFile
        else:
            outputFilename = "replaced_{0}".format(filename)
            outputFile = os.path.join(path, outputFilename)
        # open file and read input text
        print("Processing '{0}' ...".format(filename))
        with open(inputFile, "r", encoding="utf-8") as f:
            newData = f.read()
        # work on non-empty text
        if newData:
            # search and replace the text
            newData = self.processInputText(newData, searchReplace, deepSearchPattern)
            # save output text in a separate file
            with open(outputFile, "w", encoding="utf-8") as f:
                f.write(newData)
                print("Processed.  Saved output as '{0}'.".format(outputFilename))
        else:
            print("No data is read.")

    def searchFilesInFolder(self, folder, searchReplace=None, overwrite=False, deepSearchPattern=None):
        fileList = glob.glob(folder+"/*")
        for file in fileList:
            if os.path.isfile(file):
                self.searchFile(file, searchReplace, overwrite, deepSearchPattern)

    def processInput(self, inputName, searchReplace=None, overwrite=False, deepSearchPattern=None):
        # check if user's input is a file or a folder
        if os.path.isfile(inputName):
            self.searchFile(inputName, searchReplace, overwrite, deepSearchPattern)
        elif os.path.isdir(inputName):
            self.searchFilesInFolder(inputName, searchReplace, overwrite, deepSearchPattern)
        else:
            print("\""+inputName+"\"", "is not found!")

    def processInputText(self, text, searchReplace=None, deepSearchPattern=None):
        if searchReplace:
            if deepSearchPattern:
                text = self.deepReplace(text, deepSearchPattern, searchReplace)
            else:
                text = self.replace(text, searchReplace)
        # Advanced users add customised search & items below:
        # an example of a simple search & replace
#        searchReplace = (
#            ('search1', 'replace1'),
#            ('search2', 'replace2'),
#            ('search3', 'replace3'),
#        )
#        text = self.replace(text, searchReplace)
        # an example of a repetitive search until a pre-defined pattern is no longer found.
#        searchPattern = 'pattern'
#        searchReplace = (
#            ('search1', 'replace1'),
#            ('search2', 'replace2'),
#            ('search3', 'replace3'),
#        )
#        text = self.deepReplace(text, searchPattern, searchReplace)
        return text

if __name__ == '__main__':
    # sys.platform
    # https://docs.python.org/3/library/sys.html#sys.platform
    if (sys.platform == "linux") or (sys.platform == "darwin"):
        import readline

    inputName = ""
    arguments = sys.argv

    # Usage:
    # RegexSearch.py [a nested tuple of search & replace items] [file1 / folder1] [file2 / folder2] [file3 / folder3] ...
    # Support multple files / folders, starting from the second parameter.
    # To make this script executable, run:
    # chmod +x RegexSearch.py
    # To provide a nested tuple / list of search & replace items on command line:
    # e.g. ./RegexSearch.py '(("test", "TEST"), ("[a-e]", r"x\1x"))' test.txt test1.txt
    # To work with dynamic scripting, edit the content of function "processInputText" and run:
    # e.g. ./RegexSearch.py '()' test.txt test1.txt
    # The first parameter is optional to work on a single file or a single folder.  This assumes power users edit the content of function "processInputText" according to their own needs.
    # e.g. ./RegexSearch.py test.txt
    # To run interactive mode, simply run:
    # ./RegexSearch.py
    if len(arguments) > 2:
        try:
            searchReplace = literal_eval(arguments[1])
        except:
            print("Process cancelled!  Reason: Search & replace items are not properly formatted.")
            exit()
        if searchReplace and isinstance(searchReplace, (list, tuple)):
            regexSearch = RegexSearch()
            overwrite = (arguments[2] == "--overwrite")
            if overwrite and (len(arguments) > 3):
                files = arguments[3:]
            else:
                files = arguments[2:]
            if files:
                for inputName in files:
                    if inputName:
                        try:
                            regexSearch.processInput(inputName, searchReplace=searchReplace, overwrite=overwrite)
                        except:
                            print("Process cancelled!  Reason: Search & replace items are not properly formatted.")
                            exit()
    elif len(arguments) == 2 and not arguments[1] == "--deep":
        inputName = arguments[1]
        if inputName:
            RegexSearch().processInput(inputName)
    else:
        # User Interaction
        print("[A search & seplace utility, written by Eliran Wong]")
        # Ask for name(s) of file(s) / folder(s)
        checkMultiple = input("Work on more than one file or folder? [yes/No] ").lower()
        multiple = (checkMultiple == "yes" or checkMultiple == "y")
        if multiple:
            print("Enter the names of your files / folders, separated by comma ',', for examples:")
            print("filename1.txt, filename2.txt, folderName1, folderName2")
            inputNames = input("Enter here: ")
            inputNames = [inputName.strip() for inputName in inputNames.split(",")]
            print("Total of {0} item(s) entered: {1}".format(len(inputNames), inputNames))
        else:
            inputName = input("Enter a file or folder: ")
        # Ask if overwriting original file(s)
        checkOverwrite = input("Overwrite? [yes/No] ").lower()
        overwrite = (checkOverwrite == "yes" or checkOverwrite == "y")
        # check if running deep mode
        deepSearchPattern = None
        if len(arguments) == 2 and arguments[1] == "--deep":
            print("Deep mode is enabled.  Search & replace are performed repetitively until a pre-defined pattern is no longer found.")
            userPattern = input("Define a pattern here: ")
            checkPatternLiteral = input("Is this pattern a string literal? [yes/No] ").lower()
            patternLiteral = (checkPatternLiteral == "yes" or checkPatternLiteral == "y")
            if userPattern:
                if patternLiteral:
                    try:
                        deepSearchPattern = literal_eval(userPattern)
                    except:
                        print("Deep mode is disabled!  Reason: Entered pattern is not properly formatted.")
                        deepSearchPattern = None
                else:
                    deepSearchPattern = userPattern
            else:
                print("Deep mode is disabled!  Reason: Entered pattern is empty.")
        # formulate a nested list of tuples, according to user input
        searchReplace = []
        addSearchReplace = True
        while addSearchReplace:
            print("Adding a pair of search & replace items ...")
            search = input("Search: ")
            if search:
                replace = input("Replace: ")
                checkLiteral = input("Are these items string literals? [yes/No] ").lower()
                literal = (checkLiteral == "yes" or checkLiteral == "y")
                if literal:
                    try:
                        searchReplace.append((literal_eval(search), literal_eval(replace)))
                    except:
                        print("Failed to add this pair of search & replace items!  Reason: One of entered items is not string literal.")
                else:
                    searchReplace.append((search, replace))
                    print("Added successfully.")
            print("Here are your search & replace items: ")
            print(pprint.pformat(searchReplace))
            checkAddSearchReplace = input("Add more search & replace items? [yes/No] ").lower()
            addSearchReplace = (checkAddSearchReplace == "yes" or checkAddSearchReplace == "y")
        try:
            if multiple and inputNames:
                for inputName in inputNames:
                    RegexSearch().processInput(inputName, searchReplace=searchReplace, overwrite=overwrite, deepSearchPattern=deepSearchPattern)
            elif not multiple and inputName:
                RegexSearch().processInput(inputName, searchReplace=searchReplace, overwrite=overwrite, deepSearchPattern=deepSearchPattern)
        except:
            print("Process cancelled!  Reason: One of search & replace items is not properly formatted.")
            exit()
