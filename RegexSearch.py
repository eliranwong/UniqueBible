#!/usr/bin/env python

import re, glob, os, sys
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
            outputFile = inputFile
        else:
            filename = "replaced_{0}".format(filename)
            outputFile = os.path.join(path, filename)
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
                print("File '{0}' was processed, with output saved in file '{0}'.".format(inputName))
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
        searchReplace = literal_eval(arguments[1])
        if searchReplace and isinstance(searchReplace, (list, tuple)):
            regexSearch = RegexSearch()
            for inputName in arguments[2:]:
                if inputName:
                    regexSearch.processInput(inputName, searchReplace=searchReplace, overwrite=True)
    elif (len(arguments) == 2):
        inputName = arguments[1]
        if inputName:
            RegexSearch().processInput(inputName)
    else:
        # User Interaction - ask for filename / folder name
        inputName = input("Enter a file / folder name here: ")
        if inputName:
            RegexSearch().processInput(inputName)
