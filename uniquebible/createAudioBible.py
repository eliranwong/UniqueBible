"""
This script is written for macOS or Amazon Polly users only!

For macOS users:
Install ffmpeg & AudioConverter FIRST!
On macOS terminal, run:
> brew install ffmpeg
> pip install --upgrade AudioConverter

For Amazon Polly users:
Python: https://docs.aws.amazon.com/polly/latest/dg/get-started-what-next.html
Voices: https://docs.aws.amazon.com/polly/latest/dg/voicelist.html
"""

# User can change bible module in the following line:
# On macOS, select voice or adjust rate at System Preferences > Accessibility > Spoken Content
bibleModule = "MOB"

from uniquebible.db.BiblesSqlite_nogui import Bible, MorphologySqlite
# getBookList, getChapterList, readTextChapter
import os, re
from uniquebible import config
from uniquebible.install.module import *

# To work with Amazon Polly
# Install boto3 first
# > pip3 install boto3
from boto3 import Session
from botocore.exceptions import BotoCoreError, ClientError
from contextlib import closing
#import os
import sys
from tempfile import gettempdir

def savePollyTTSAudio(b, c, v, verseText):
    # To work out output file path
    moduleFolder = os.path.join(os.getcwd(), config.audioFolder, "bibles", bibleModule, "default")
    if not os.path.isdir(moduleFolder):
        os.makedirs(moduleFolder, exist_ok=True)
    chapterFolder = os.path.join(moduleFolder, "{0}_{1}".format(b, c))
    if not os.path.isdir(chapterFolder):
        os.makedirs(chapterFolder)
    audioFilename = "{0}_{1}_{2}_{3}.mp3".format(bibleModule, b, c, v)
    outputFile = os.path.join(chapterFolder, audioFilename)

    # Create a client using the credentials and region defined in the [adminuser]
    # section of the AWS credentials file (~/.aws/credentials).
    # session = Session(profile_name="adminuser")
    # Use default profile instead
# Run in terminal "aws configure" to set up, and check
#""" ~/.aws/credentials
#[default]
#aws_access_key_id = 
#aws_secret_access_key = 
#region = eu-west-2
#output = json
# """
    session = Session()
    polly = session.client("polly")

    try:
        # Request speech synthesis
        # These voices can be used with Newscaster speaking styles when used with the Neural format.
        # British accent: Amy
        # American accent: Joanna
        # American accent: Matthew
        response = polly.synthesize_speech(Text=verseText, OutputFormat="mp3",
                                            VoiceId="Amy")
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        print(error)
        sys.exit(-1)

    # Access the audio stream from the response
    if "AudioStream" in response:
        # Note: Closing the stream is important because the service throttles on the
        # number of parallel connections. Here we are using contextlib.closing to
        # ensure the close method of the stream object will be called automatically
        # at the end of the with statement's scope.
        with closing(response["AudioStream"]) as stream:
            #output = os.path.join(gettempdir(), "speech.mp3")

            try:
                # Open a file for writing the output as a binary stream
                with open(outputFile, "wb") as file:
                    file.write(stream.read())
            except IOError as error:
                # Could not write to file, exit gracefully
                print(error)
                sys.exit(-1)

    else:
        # The response didn't contain audio data, exit gracefully
        print("Could not stream audio")
        sys.exit(-1)

# To work with macOS
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

# To work with macOS
def saveMacTTSAudio(b, c, v, text, wordID=None, lexeme=None):
    module = bibleModule if wordID is None else "BHS5"

    moduleFolder = os.path.join(os.getcwd(), config.audioFolder, "bibles", f"{module}_aiff", "default")
    if not os.path.isdir(moduleFolder):
        os.makedirs(moduleFolder, exist_ok=True)
    chapterFolder = os.path.join(moduleFolder, "{0}_{1}".format(b, c))
    if not os.path.isdir(chapterFolder):
        os.makedirs(chapterFolder)
    if wordID is None:
        audioFilename = "{0}_{1}_{2}_{3}.aiff".format(module, b, c, v)
        outputFile = os.path.join(chapterFolder, audioFilename)
    else:
        verseFolder = os.path.join(chapterFolder, "{0}_{1}_{2}".format(b, c, v))
        if not os.path.isdir(verseFolder):
            os.makedirs(verseFolder)
        audioFilename = "{0}_{1}_{2}_{3}_{4}.aiff".format(module, b, c, v, wordID)
        outputFile = os.path.join(verseFolder, audioFilename)

    if text and not os.path.isfile(outputFile):
        # For non-English text, can use the following line direclty
        os.system(f"say -o {outputFile} {text}")
        #print(f"{outputFile} is created.")
        #with open('temp.txt', 'w') as file:
        #    file.write(text)
        #os.system(f"say -o {outputFile} -f temp.txt")

    if lexeme:
        audioFilename = "lex_{0}_{1}_{2}_{3}_{4}.aiff".format(module, b, c, v, wordID)
        outputFile = os.path.join(verseFolder, audioFilename)
        if not os.path.isfile(outputFile):
            os.system(f"say -o {outputFile} {lexeme}")

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
                    # The following line applies to WEB only.
                    #verseText = re.sub("\[.*?\]", "", verseText)
                    verseText = re.sub("<.*?>", "", verseText)
                    verseText = re.sub("[<>〔〕\[\]（）\(\)]", "", verseText)
                    # For testing:
                    #print(bibleModule, b, c, v, verseText)
                    # User can change text-to-speech module in the following line (saveCloudTTSAudio or saveGTTSAudio):
                    try:
                        # Use macOS TTS
                        saveMacTTSAudio(b, c, v, verseText)
                        # Use Amazon Polly
                        #savePollyTTSAudio(b, c, v, verseText)
                    except:
                        print("Failed to save {0}.{1}.{2}: {3}".format(b, c, v, verseText))

def processBooksWords(rangeBegin, rangeEnd):
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
                for b, c, v, *_ in textChapter:
                    words = morphology.allWords(b, c, v)
                    for wordID, b, c, v, word, lexeme in words:
                        try:
                            # Use macOS TTS
                            saveMacTTSAudio(b, c, v, word, wordID, lexeme)
                        except:
                            print("Failed to save {0}.{1}.{2}.{3}: {4}".format(b, c, v, wordID, word))


# main process begin from below
bible = Bible(bibleModule)
# For creating individual word audio only
morphology = MorphologySqlite()

# To test Amazon Polly
#savePollyTTSAudio(1, 1, 1, "test")

# O.T.
#processBooks(1, 40)
processBooksWords(1, 40)
# N.T.
#processBooks(40, 67)

# On mac ONLY:
#convertAiffToMP3()