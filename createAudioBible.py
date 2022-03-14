"""
This script is written for macOS users only!
Install ffmpeg & AudioConverter FIRST!
On macOS terminal, run:
> brew install ffmpeg
> pip install --upgrade AudioConverter
"""

# User can change bible module in the following line:
# On macOS, select voice or adjust rate at System Preferences > Accessibility > Spoken Content
bibleModule = "KJV"

from db.BiblesSqlite_nogui import Bible
# getBookList, getChapterList, readTextChapter
import os, re, config
from install.module import *


def convertAiffToMP3():
    aiffFolder = os.path.join(os.getcwd(), config.audioFolder, "bibles", f"{bibleModule}_aiff", "default")
    moduleFolder = os.path.join(os.getcwd(), config.audioFolder, "bibles", bibleModule, "default")
    if not os.path.isdir(moduleFolder):
        os.makedirs(moduleFolder, exist_ok=True)
    folders = os.listdir(aiffFolder)
    for folder in folders:
        inputFolder = os.path.join(aiffFolder, folder)
        outputFolder = os.path.join(moduleFolder, folder)
        if not os.path.isdir(outputFolder):
            os.makedirs(moduleFolder, exist_ok=True)
        os.system(f"audioconvert convert {inputFolder} {outputFolder}")

def saveMacTTSAudio(b, c, v, verseText):

    moduleFolder = os.path.join(os.getcwd(), config.audioFolder, "bibles", f"{bibleModule}_aiff", "default")
    if not os.path.isdir(moduleFolder):
        os.makedirs(moduleFolder, exist_ok=True)
    chapterFolder = os.path.join(moduleFolder, "{0}_{1}".format(b, c))
    if not os.path.isdir(chapterFolder):
        os.makedirs(chapterFolder)
    audioFilename = "{0}_{1}_{2}_{3}.aiff".format(bibleModule, b, c, v)
    outputFile = os.path.join(chapterFolder, audioFilename)

    # For non-English text, can use the following line direclty
    #os.system(f"say -o {outputFile} {verseText}")
    with open('temp.txt', 'w') as file:
        file.write(verseText)
    os.system(f"say -o {outputFile} -f temp.txt")

def processBooks(rangeBegin, rangeEnd):
    # For testing
    # For selected books
    #for book in (2,):
    # For a range of book in a row
    for book in range(rangeBegin, rangeEnd):
    # The following two lines do all books in one go, but it is not recommended
    #books = bible.getBookList()
    #for book in books:
        chapters = bible.getChapterList(book)
        for chapter in chapters:
            # Change the start chapter if last process break somewhere
            if chapter >= 0:
                textChapter = bible.readTextChapter(book, chapter)
                for b, c, v, verseText in textChapter:
                    verseText = re.sub("<.*?>", "", verseText)
                    verseText = re.sub("[<>〔〕\[\]（）\(\)]", "", verseText)
                    # For testing:
                    #print(bibleModule, b, c, v, verseText)
                    # User can change text-to-speech module in the following line (saveCloudTTSAudio or saveGTTSAudio):
                    try:
                        saveMacTTSAudio(b, c, v, verseText)
                    except:
                        print("Failed to save {0}.{1}.{2}: {3}".format(b, c, v, verseText))


# main process begin from below
bible = Bible(bibleModule)

print("hi")
# O.T.
processBooks(1, 40)
# N.T.
processBooks(40, 67)

convertAiffToMP3()