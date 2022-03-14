import os

zipFiles = {
    1: "01_Genesis.zip",
    2: "02_Exodus.zip",
    3: "03_Leviticus.zip",
    4: "04_Numbers.zip",
    5: "05_Deuteronomy.zip",
    6: "06_Joshua.zip",
    7: "07_Judges.zip",
    8: "08_Ruth.zip",
    9: "09_1Samuel.zip",
    10: "10_2Samuel.zip",
    11: "11_1Kings.zip",
    12: "12_2Kings.zip",
    13: "13_1Chronicles.zip",
    14: "14_2Chronicles.zip",
    15: "15_Ezra.zip",
    16: "16_Nehemiah.zip",
    17: "17_Esther.zip",
    18: "18_Job.zip",
    19: "19_Psalms.zip",
    20: "20_Proverbs.zip",
    21: "21_Ecclesiastes.zip",
    22: "22_Song_of_Songs.zip",
    23: "23_Isaiah.zip",
    24: "24_Jeremiah.zip",
    25: "25_Lamentations.zip",
    26: "26_Ezekiel.zip",
    27: "27_Daniel.zip",
    28: "28_Hosea.zip",
    29: "29_Joel.zip",
    30: "30_Amos.zip",
    31: "31_Obadiah.zip",
    32: "32_Jonah.zip",
    33: "33_Micah.zip",
    34: "34_Nahum.zip",
    35: "35_Habakkuk.zip",
    36: "36_Zephaniah.zip",
    37: "37_Haggai.zip",
    38: "38_Zechariah.zip",
    39: "39_Malachi.zip",
    40: "40_Matthew.zip",
    41: "41_Mark.zip",
    42: "42_Luke.zip",
    43: "43_John.zip",
    44: "44_Acts_of_Apostles.zip",
    45: "45_Romans.zip",
    46: "46_1Corinthians.zip",
    47: "47_2Corinthians.zip",
    48: "48_Galatians.zip",
    49: "49_Ephesians.zip",
    50: "50_Philippians.zip",
    51: "51_Colossians.zip",
    52: "52_1Thessalonians.zip",
    53: "53_2Thessalonians.zip",
    54: "54_1Timothy.zip",
    55: "55_2Timothy.zip",
    56: "56_Titus.zip",
    57: "57_Philemon.zip",
    58: "58_Hebrews.zip",
    59: "59_James.zip",
    60: "60_1Peter.zip",
    61: "61_2Peter.zip",
    62: "62_1John.zip",
    63: "63_2John.zip",
    64: "64_3John.zip",
    65: "65_Jude.zip",
    66: "66_Revelation.zip",
}

def getSingleBookFolders(b):
    folderList = []
    items = os.listdir(os.getcwd())
    for item in items:
        if os.path.isdir(item) and item.startswith(f"{b}_"):
            folderList.append(item)
    return " ".join(folderList) if folderList else ""

for b in range(1, 67):
    folderList = getSingleBookFolders(b)
    if folderList:
        os.system(f"zip -r {zipFiles[b]} {folderList}")

