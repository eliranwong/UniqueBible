import glob
import os, re
from pathlib import Path

if __name__ == '__main__':
    from uniquebible.util.ConfigUtil import ConfigUtil
    ConfigUtil.setup()

from uniquebible import config
from uniquebible.util.BibleVerseParser import BibleVerseParser

from uniquebible.util.ThirdParty import Converter


class BibleDataConverter:

    # Free Bible Version
    # http://www.freebibleversion.org/
    # https://ebible.org/find/details.php?id=engfbv
    def convertFreeBibleVersion(self, directory):

        if not os.path.isdir(directory):
            print("{0} does not exist".format(directory))
            exit()

        text = "FBV"
        description = "Free Bible Version"

        bookNumDict = {
            "1ch": "13",
            "1co": "46",
            "1jn": "62",
            "1ki": "11",
            "1pe": "60",
            "1sa": "9",
            "1th": "52",
            "1ti": "54",
            "2ch": "14",
            "2co": "47",
            "2jn": "63",
            "2ki": "12",
            "2pe": "61",
            "2sa": "10",
            "2th": "53",
            "2ti": "55",
            "3jn": "64",
            "act": "44",
            "amo": "30",
            "col": "51",
            "dan": "27",
            "deu": "5",
            "ecc": "21",
            "eph": "49",
            "est": "17",
            "exo": "2",
            "ezk": "26",
            "ezr": "15",
            "gal": "48",
            "gen": "1",
            "hab": "35",
            "hag": "37",
            "heb": "58",
            "hos": "28",
            "isa": "23",
            "jas": "59",
            "jdg": "7",
            "jer": "24",
            "jhn": "43",
            "job": "18",
            "jol": "29",
            "jon": "32",
            "jos": "6",
            "jud": "65",
            "lam": "25",
            "lev": "3",
            "luk": "42",
            "mal": "39",
            "mat": "40",
            "mic": "33",
            "mrk": "41",
            "nam": "34",
            "neh": "16",
            "num": "4",
            "oba": "31",
            "phm": "57",
            "php": "50",
            "pro": "20",
            "psa": "19",
            "rev": "66",
            "rom": "45",
            "rut": "8",
            "sng": "22",
            "tit": "56",
            "zec": "38",
            "zep": "36",
        }

        versesData = []
        for filename in glob.glob(directory+"/eng*.txt"):
            f = Path(filename).stem
            (bookName, chapterNum) = re.search(r".*_.*_(.*)_(.*)_.*", f).groups()
            if bookName != "000":
                bookName = bookName.lower()
                bookNum = bookNumDict[bookName]
                file = open(filename, "r")
                lines = file.readlines()
                count = 0
                verseNum = 0
                for line in lines:
                    count += 1
                    if count > 2 and len(line) > 1:
                        verseNum += 1
                        row = [bookNum, chapterNum, verseNum, line]
                        versesData.append(row)

        Converter().mySwordBibleToRichFormat(description, text, versesData)
        Converter().mySwordBibleToPlainFormat(description, text, versesData)

    # New Heart Bible
    # https://nheb.net/
    def convertNewHeartBible(self, filename):

        if not os.path.isfile(filename):
            print("{0} does not exist".format(filename))
            exit()

        text = "NHEB"
        description = "New Heart English Bible"

        bookNumDict = {
            "Gen": "1",
            "Exo": "2",
            "Lev": "3",
            "Num": "4",
            "Deu": "5",
            "Jos": "6",
            "Jdg": "7",
            "Rut": "8",
            "1Sa": "9",
            "2Sa": "10",
            "1Ki": "11",
            "2Ki": "12",
            "1Ch": "13",
            "2Ch": "14",
            "Ezr": "15",
            "Neh": "16",
            "Est": "17",
            "Job": "18",
            "Psa": "19",
            "Pro": "20",
            "Ecc": "21",
            "Sol": "None",
            "Isa": "23",
            "Jer": "24",
            "Lam": "25",
            "Eze": "26",
            "Dan": "27",
            "Hos": "28",
            "Joe": "29",
            "Amo": "30",
            "Oba": "31",
            "Jon": "32",
            "Mic": "33",
            "Nah": "34",
            "Hab": "35",
            "Zep": "36",
            "Hag": "37",
            "Zec": "38",
            "Mal": "39",
            "Mat": "40",
            "Mar": "41",
            "Luk": "42",
            "Joh": "43",
            "Act": "44",
            "Rom": "45",
            "1Co": "46",
            "2Co": "47",
            "Gal": "48",
            "Eph": "49",
            "Phi": "50",
            "Col": "51",
            "1Th": "52",
            "2Th": "53",
            "1Ti": "54",
            "2Ti": "55",
            "Tit": "56",
            "Phm": "57",
            "Heb": "58",
            "Jam": "59",
            "1Pe": "60",
            "2Pe": "61",
            "1Jo": "62",
            "2Jo": "63",
            "3Jo": "64",
            "Jud": "65",
            "Rev": "66",
        }

        count = 0
        versesData = []
        file = open(filename, "r", encoding="ISO-8859-1")
        lines = file.readlines()
        for line in lines:
            count += 1
            if line.startswith("//"):
                if "Update" in line:
                    update = re.search(r"Update (.*) \(a\)", line).group(1)
                    description += " - " + update
            else:
                (bookName, chapterNum, verseNum, scripture) = re.search(r"(\S*) (\S*):(\S*) (.*$)", line).groups()
                bookNum = bookNumDict[bookName]
                row = [bookNum, chapterNum, verseNum, scripture]
                versesData.append(row)

        print("Read {0} lines".format(count))

        Converter().mySwordBibleToRichFormat(description, text, versesData)
        Converter().mySwordBibleToPlainFormat(description, text, versesData)

    def generateDict(self):
        bookNumDict = {}
        parser = BibleVerseParser(config.parserStandarisation)
        bookName = "Gen."
        bookNum = parser.bookNameToNum(bookName)
        bookNumDict[bookName] = bookNum
        for key in bookNumDict.keys():
            print('"{0}": "{1}",'.format(key, bookNumDict[key]))


if __name__ == '__main__':
    config.useLiteVerseParsing = True
    BibleDataConverter().convertFreeBibleVersion("/Users/otseng/Downloads/engfbv_readaloud")

    print("Done")
