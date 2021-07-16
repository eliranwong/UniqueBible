import os, glob
from itertools import (takewhile, repeat)


class FileUtil:

    @staticmethod
    # Note: pathlib.Path(file).stem does not work with file name containg more than one dot, e.g. "*.bible.sqlite"
    def fileNamesWithoutExtension(dir, ext):
        files = glob.glob(os.path.join(dir, "*.{0}".format(ext)))
        return sorted([file[len(dir)+1:-(len(ext)+1)] for file in files if os.path.isfile(file)])

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
        # "custom.css" is essential for custom css feature.
        # "custom.js" is essential for custom javascript feature.
        customCssFile = os.path.join("htmlResources", "css", "custom.css")
        customJsFile = os.path.join("htmlResources", "js", "custom.js")
        userFiles = ("config.py", customCssFile, customJsFile)
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

    @staticmethod
    def getBibleMP3File(text, book, folder, chapter):
        b = book
        a = "A"
        if b == 19:
            c = "{:03d}".format(chapter)
        else:
            c = "{:02d}".format(chapter)
        if b > 39:
            b -= 39
            a = "B"
        filesearch = "audio/bibles/{0}/{1}/{2}{3}*_{4}*.mp3".format(text, folder, a, "{:02d}".format(b), c)
        file = glob.glob(filesearch)
        if file:
            return file[0]
        filesearch = "audio/bibles/{0}/{1}/{2}*/{3}*_{4}*.mp3".format(text, folder, "{:02d}".format(book),
                                                                    "{:02d}".format(book), "{:03d}".format(chapter))
        files = glob.glob(filesearch)
        if files:
            file = files[0]
            return file
        else:
            filesearch = "audio/bibles/{0}/{1}/{2}*/{3}_*{4}.mp3".format(text, folder, "{:02d}".format(book),
                                                                         "{:02d}".format(book),
                                                                         "{:02d}".format(chapter))
            files = glob.glob(filesearch)
            if files:
                file = files[0]
                return file
        return None

# Test code

def test_insertStringIntoFile(filename, data, offset):
    FileUtil.insertStringIntoFile(filename, data, offset)

def test_updateStringIntoFile(filename, data, offset):
    FileUtil.updateStringIntoFile(filename, data, offset)

if __name__ == "__main__":

    test_insertStringIntoFile("testing.txt", "ppppp\n", -1)
