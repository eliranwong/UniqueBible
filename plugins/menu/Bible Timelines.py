import config
from gui.ImageViewer import ImageViewer

imageListViewItems = [
    ("2210-2090_BCE", "books/Timelines/0.png"),
    ("2090-1970_BCE", "books/Timelines/1.png"),
    ("1970-1850_BCE", "books/Timelines/2.png"),
    ("1850-1730_BCE", "books/Timelines/3.png"),
    ("1750-1630_BCE", "books/Timelines/4.png"),
    ("1630-1510_BCE", "books/Timelines/5.png"),
    ("1510-1390_BCE", "books/Timelines/6.png"),
    ("1410-1290_BCE", "books/Timelines/7.png"),
    ("1290-1170_BCE", "books/Timelines/8.png"),
    ("1170-1050_BCE", "books/Timelines/9.png"),
    ("1050-930_BCE", "books/Timelines/10.png"),
    ("930-810_BCE", "books/Timelines/11.png"),
    ("810-690_BCE", "books/Timelines/12.png"),
    ("690-570_BCE", "books/Timelines/13.png"),
    ("570-450_BCE", "books/Timelines/14.png"),
    ("470-350_BCE", "books/Timelines/15.png"),
    ("350-230_BCE", "books/Timelines/16.png"),
    ("240-120_BCE", "books/Timelines/17.png"),
    ("120-1_BCE", "books/Timelines/18.png"),
    ("10-110_CE", "books/Timelines/19.png"),
    ("by_Matthew", "books/Timelines/20.png"),
    ("by_Mark", "books/Timelines/21.png"),
    ("by_Luke", "books/Timelines/22.png"),
    ("by_John", "books/Timelines/23.png"),
    ("by_All_4_Gospels", "books/Timelines/24.png"),
]

config.mainWindow.imageViewer = ImageViewer(config.mainWindow, showLoadImageButton=False, showImageListView=True, imageListViewItems=imageListViewItems)
config.mainWindow.imageViewer.show()
