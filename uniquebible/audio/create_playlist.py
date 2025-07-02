# create audio playlist for each chapter

import re, glob, os

books = (
    "",
    "Genesis",
    "Exodus",
    "Leviticus",
    "Numbers",
    "Deuteronomy",
    "Joshua",
    "Judges",
    "Ruth",
    "1Samuel",
    "2Samuel",
    "1Kings",
    "2Kings",
    "1Chronicles",
    "2Chronicles",
    "Ezra",
    "Nehemiah",
    "Esther",
    "Job",
    "Psalm",
    "Proverbs",
    "Ecclesiastes",
    "SongofSongs",
    "Isaiah",
    "Jeremiah",
    "Lamentations",
    "Ezekiel",
    "Daniel",
    "Hosea",
    "Joel",
    "Amos",
    "Obadiah",
    "Jonah",
    "Micah",
    "Nahum",
    "Habakkuk",
    "Zephaniah",
    "Haggai",
    "Zechariah",
    "Malachi",
    "Matthew",
    "Mark",
    "Luke",
    "John",
    "Acts",
    "Romans",
    "1Corinthians",
    "2Corinthians",
    "Galatians",
    "Ephesians",
    "Philippians",
    "Colossians",
    "1Thessalonians",
    "2Thessalonians",
    "1Timothy",
    "2Timothy",
    "Titus",
    "Philemon",
    "Hebrews",
    "James",
    "1Peter",
    "2Peter",
    "1John",
    "2John",
    "3John",
    "Jude",
    "Revelation",
)

cwd = os.getcwd()

for i in os.listdir():
    if os.path.isdir(i):
        for i2 in os.listdir(os.path.join(i, "default")):
            chapterFolder = os.path.join(i, "default", i2)
            if os.path.isdir(chapterFolder):
                if os.listdir(chapterFolder):
                    if os.path.isdir(chapterFolder) and re.search("[0-9]_[0-9]", chapterFolder):
                        ver = re.sub("/default/.*?$", "", chapterFolder)
                        print(ver)
                        bc = re.sub("^.*?/default/", "", chapterFolder)
                        print(bc)
                        b, c = re.sub("^.*?/default/", "", chapterFolder).split("_")
                        os.chdir(chapterFolder)

                        if glob.glob("*.m3u"):
                            os.chdir(cwd)
                            continue

                        prefix = re.sub("_[0-9]+?.mp3", "", glob.glob("*.mp3")[0])

                        for i3 in range(180):
                            mp3file = prefix + "_" + str(i3) + ".mp3"
                            if os.path.isfile(mp3file):
                                bkname = books[int(b)]
                                with open(f"{ver}_{bkname}_{c}.m3u", "a") as fileObj:
                                    fileObj.write(mp3file + "\n")

                        os.chdir(cwd)
