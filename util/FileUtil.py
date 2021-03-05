import os

from itertools import (takewhile, repeat)


class FileUtil:

    # https://stackoverflow.com/a/27518377/1397431
    @staticmethod
    def getLineCount(filename):
        try:
            f = open(filename, 'rb')
            bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
            return sum(buf.count(b'\n') for buf in bufgen)
        except Exception as e:
            # print(str(e))
            return -1

    @staticmethod
    def createCustomFiles():
        # Create files for user customisation
        # "config.py" is essential for running module "config".
        # "custom.py" is essential for custom python script feature.
        # "custom.css" is essential for custom css feature.
        # "custom.js" is essential for custom javascript feature.
        customCssFile = os.path.join("htmlResources", "css", "custom.css")
        customJsFile = os.path.join("htmlResources", "js", "custom.js")
        userFiles = ("config.py", "custom.py", customCssFile, customJsFile)
        for userFile in userFiles:
            if not os.path.isfile(userFile):
                open(userFile, "w", encoding="utf-8").close()

    @staticmethod
    def insertStringIntoFile(filename, data, offset):
        try:
            if not os.path.exists(filename):
                return
            targetFile = open(filename, "r")
            contents = targetFile.readlines()
            targetFile.close()
            if offset >= 0:
                contents.insert(offset, data)
            else:
                contents.insert(len(contents) + offset, data)
            targetFile = open(filename, "w")
            targetFile.writelines(contents)
            targetFile.close()
        except:
            pass

    @staticmethod
    def updateStringIntoFile(filename, data):
        try:
            if not os.path.exists(filename):
                return
            with open(filename, "r") as f:
                lines = f.readlines()
            with open(filename, "w") as f:
                for line in lines:
                    if line.startswith('{0}"'.format(data.split('": ')[0])):
                        f.write(data)
                    else:
                        f.write(line)
        except:
            pass

# Test code

def test_insertStringIntoFile(filename, data, offset):
    FileUtil.insertStringIntoFile(filename, data, offset)

def test_updateStringIntoFile(filename, data, offset):
    FileUtil.updateStringIntoFile(filename, data, offset)

if __name__ == "__main__":

    test_insertStringIntoFile("testing.txt", "ppppp\n", -1)
