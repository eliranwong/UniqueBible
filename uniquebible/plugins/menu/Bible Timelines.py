from uniquebible import config
import os
from uniquebible.gui.ImageViewer import ImageViewer
from uniquebible.util.BibleBooks import BibleBooks

imageListViewItems = [
    ("2210-2090 BCE", "books/Timelines/0.png"), #0
    ("2090-1970 BCE", "books/Timelines/1.png"),
    ("1970-1850 BCE", "books/Timelines/2.png"),
    ("1850-1730 BCE", "books/Timelines/3.png"),
    ("1750-1630 BCE", "books/Timelines/4.png"),
    ("1630-1510 BCE", "books/Timelines/5.png"), #5
    ("1510-1390 BCE", "books/Timelines/6.png"),
    ("1410-1290 BCE", "books/Timelines/7.png"),
    ("1290-1170 BCE", "books/Timelines/8.png"),
    ("1170-1050 BCE", "books/Timelines/9.png"),
    ("1050-930 BCE", "books/Timelines/10.png"), #10
    ("930-810 BCE", "books/Timelines/11.png"),
    ("810-690 BCE", "books/Timelines/12.png"),
    ("690-570 BCE", "books/Timelines/13.png"),
    ("570-450 BCE", "books/Timelines/14.png"),
    ("470-350 BCE", "books/Timelines/15.png"), #15
    ("350-230 BCE", "books/Timelines/16.png"),
    ("240-120 BCE", "books/Timelines/17.png"),
    ("120-1 BCE", "books/Timelines/18.png"),
    ("10-110 CE", "books/Timelines/19.png"), #19
    ("Matthew", "books/Timelines/20.png"), #20
    ("Mark", "books/Timelines/21.png"),
    ("Luke", "books/Timelines/22.png"),
    ("John", "books/Timelines/23.png"),
    ("All Four Gospels", "books/Timelines/24.png"),
]

initialIndexMap = {
    1: 0,
    2: 2,
    3: 6,
    4: 6,
    5: 6,
    6: 6,
    7: 7,
    8: 7,
    9: 9,
    10: 10,
    11: 10,
    12: 11,
    13: 10,
    14: 10,
    15: 14,
    16: 15,
    17: 14,
    18: 6,
    19: 10,
    20: 10,
    21: 10,
    22: 10,
    23: 12,
    24: 13,
    25: 13,
    26: 13,
    27: 13,
    28: 12,
    29: 11,
    30: 12,
    31: 11,
    32: 13,
    33: 12,
    34: 13,
    35: 13,
    36: 12,
    37: 14,
    38: 14,
    39: 15,
    40: 20,
    41: 21,
    42: 22,
    43: 23,
}

databaseFile = os.path.join(config.marvelData, "books", "Maps_ABS.book")
if os.path.isfile(databaseFile):
    initialScrollIndex = initialIndexMap.get(config.mainB, 19)
    config.mainWindow.imageViewer = ImageViewer(config.mainWindow, showLoadImageButton=False, showImageListView=True, imageListViewItems=imageListViewItems, initialScrollIndex=initialScrollIndex)
    config.mainWindow.imageViewer.show()
else:
    databaseInfo = ((config.marvelData, "books", "Maps_ABS.book"), "13hf1NvhAjNXmRQn-Cpq4hY0E2XbEfmEd")
    config.mainWindow.downloadHelper(databaseInfo)
