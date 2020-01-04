#!/usr/bin/env python

import re, glob, os, sys, pprint
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
        p = re.compile(searchPattern, flags=re.M)
        while p.search(text):
            for search, replace in searchReplace:
                if multiLine:
                    text = re.sub(search, replace, text, flags=re.M)
                else:
                    text = re.sub(search, replace, text)
        return text

    def searchFile(self, inputFile, searchReplace=None, overwrite=False):
        # set output filename
        path, filename = os.path.split(inputFile)
        if overwrite:
            outputFilename = filename
            outputFile = inputFile
        else:
            outputFilename = "replaced_{0}".format(filename)
            outputFile = os.path.join(path, outputFilename)
        # open file and read input text
        with open(inputFile,'r') as f:
            newData = f.read()
        # work on non-empty text
        if newData:
            # search and replace the text
            newData = self.processInputText(newData, searchReplace)
            # save output text in a separate file
            with open(outputFile,'w') as f:
                f.write(newData)
                print("File '{0}' was processed, with output saved in file '{1}'.".format(filename, outputFilename))
        else:
            print("No data is read.")

    def searchFilesInFolder(self, folder, searchReplace=None, overwrite=False):
        fileList = glob.glob(folder+"/*")
        for file in fileList:
            if os.path.isfile(file):
                self.searchFile(file, searchReplace, overwrite)

    def processInput(self, inputName, searchReplace=None, overwrite=False):
        # check if user's input is a file or a folder
        if os.path.isfile(inputName):
            self.searchFile(inputName, searchReplace, overwrite)
        elif os.path.isdir(inputName):
            self.searchFilesInFolder(inputName, searchReplace, overwrite)
        else:
            print("\""+inputName+"\"", "is not found!")

    def processInputText(self, text, searchReplace=None):
        if searchReplace:
            text = self.replace(text, searchReplace)
        # an example of a simple search & replace
#        searchReplace = (
#            ('search1', 'replace1'),
#            ('search2', 'replace2'),
#            ('search3', 'replace3'),
#        )
#        text = self.replace(text, searchReplace)
        # an example of searching in a loop until a search pattern is no longer found.
#        searchPattern = 'pattern'
#        searchReplace = (
#            ('search1', 'replace1'),
#            ('search2', 'replace2'),
#            ('search3', 'replace3'),
#        )
#        text = self.deepReplace(text, searchPattern, searchReplace)
        return text

if __name__ == '__main__':
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
    if (len(arguments) > 2):
        try:
            searchReplace = literal_eval(arguments[1])
        except:
            print("Process cancelled.  Reason: Search & replace option is not properly formatted.")
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
                            print("Process cancelled.  Reason: Search & replace option is not properly formatted.")
                            exit()
    elif (len(arguments) == 2):
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
            inputNames = literal_eval(input("Enter a list of files or folders: "))
        else:
            inputName = input("Enter a file or folder: ")
        # Ask if overwriting original file(s)
        checkOverwrite = input("Overwrite? [yes/No] ").lower()
        overwrite = (checkOverwrite == "yes" or checkOverwrite == "y")
        # formulate a nested list of tuples, according to user input
        searchReplace = []
        addSearchReplace = True
        while addSearchReplace:
            print("Adding a pair of search & replace items ...")
            search = input("Search: ")
            if search:
                replace = input("Replace: ")
                checkLiteral = input("Are they literal strings? [yes/No] ").lower()
                literal = (checkLiteral == "yes" or checkLiteral == "y")
                if literal:
                    try:
                        searchReplace.append((literal_eval(search), literal_eval(replace)))
                    except:
                        print("Failed to add this pair of search & replace items.  Reason: Literal expression is not found.")
                else:
                    searchReplace.append((search, replace))
                    print("Added successfully.")
            print("Your current search & replace items: ")
            print(pprint.pformat(searchReplace))checkAddSearchReplace = input("Add more search & replace items? [yes/No] ").lower()
            addSearchReplace = (checkAddSearchReplace == "yes" or checkAddSearchReplace == "y")
        try:
            if multiple and inputNames:
                for inputName in inputNames:
                    RegexSearch().processInput(inputName, searchReplace=searchReplace, overwrite=overwrite)
            elif not multiple and inputName:
                RegexSearch().processInput(inputName, searchReplace=searchReplace, overwrite=overwrite)
        except:
            print("Process cancelled.  Reason: At least one of your search & replace items is not properly formulated.")
            exit()
