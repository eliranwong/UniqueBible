import os
from uniquebible import config
from uniquebible.util.BibleBooks import BibleBooks

filename = os.path.join(config.marvelData, 'statistics', 'words.stats')
if not os.path.exists(filename):
    config.mainWindow.installGithubStatistics()

text = str(config.mainText)
if text[-1] not in ('+', '*', 'x'):
    filename = os.path.join(config.marvelData, 'bibles', 'KJVx.bible')
    if not os.path.exists(filename):
        config.mainWindow.displayMessage("Please download the KJVx.bible")
        config.mainWindow.installGithubBibles()
    text = "KJVx"

book = BibleBooks.abbrev["eng"][str(config.mainB)][0]

config.mainWindow.runTextCommand("DISPLAYWORDFREQUENCY:::{0}:::{1} {2}".format(text, book, config.mainC))
