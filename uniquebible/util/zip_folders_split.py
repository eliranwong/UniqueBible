import os

zipFiles = {
    1: "01_Genesis",
    2: "02_Exodus",
    3: "03_Leviticus",
    4: "04_Numbers",
    5: "05_Deuteronomy",
    6: "06_Joshua",
    7: "07_Judges",
    8: "08_Ruth",
    9: "09_1Samuel",
    10: "10_2Samuel",
    11: "11_1Kings",
    12: "12_2Kings",
    13: "13_1Chronicles",
    14: "14_2Chronicles",
    15: "15_Ezra",
    16: "16_Nehemiah",
    17: "17_Esther",
    18: "18_Job",
    19: "19_Psalms",
    20: "20_Proverbs",
    21: "21_Ecclesiastes",
    22: "22_Song_of_Songs",
    23: "23_Isaiah",
    24: "24_Jeremiah",
    25: "25_Lamentations",
    26: "26_Ezekiel",
    27: "27_Daniel",
    28: "28_Hosea",
    29: "29_Joel",
    30: "30_Amos",
    31: "31_Obadiah",
    32: "32_Jonah",
    33: "33_Micah",
    34: "34_Nahum",
    35: "35_Habakkuk",
    36: "36_Zephaniah",
    37: "37_Haggai",
    38: "38_Zechariah",
    39: "39_Malachi",
    40: "40_Matthew",
    41: "41_Mark",
    42: "42_Luke",
    43: "43_John",
    44: "44_Acts_of_Apostles",
    45: "45_Romans",
    46: "46_1Corinthians",
    47: "47_2Corinthians",
    48: "48_Galatians",
    49: "49_Ephesians",
    50: "50_Philippians",
    51: "51_Colossians",
    52: "52_1Thessalonians",
    53: "53_2Thessalonians",
    54: "54_1Timothy",
    55: "55_2Timothy",
    56: "56_Titus",
    57: "57_Philemon",
    58: "58_Hebrews",
    59: "59_James",
    60: "60_1Peter",
    61: "61_2Peter",
    62: "62_1John",
    63: "63_2John",
    64: "64_3John",
    65: "65_Jude",
    66: "66_Revelation",
}

def getSingleBookFolders(b):
    folderList = []
    items = os.listdir(os.getcwd())
    for item in items:
        if os.path.isdir(item) and item.startswith(f"{b}_"):
            folderList.append(item)
    #return " ".join(folderList) if folderList else ""
    return len(folderList) if folderList else ""

maxChapterNoInZip = 7

for b in range(1, 67):
    folderNum = getSingleBookFolders(b)
    if folderNum:
        folderList = []
        for c in range(1, (folderNum + 1)):
            folderName = f"{b}_{c}"
            folderList.append(folderName)
            subListNum = len(folderList)
            if subListNum == 1 and c == folderNum:
                start = c
                os.system(f"zip -r {zipFiles[b]}_{start}.zip {folderName}")
                folderList = []
            elif subListNum == 1:
                start = c
            elif len(folderList) == maxChapterNoInZip or c == folderNum:
                end = c
                folders = " ".join(folderList)
                os.system(f"zip -r {zipFiles[b]}_{start}-{end}.zip {folders}")
                folderList = []

