import glob
import os
import sys

from PySide2.QtCore import Qt

import config

from PySide2 import QtCore
from PySide2.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, \
    QComboBox, QSpacerItem, QSizePolicy

from util.TextUtil import TextUtil


class ModifyDatabaseDialog(QDialog):

    def __init__(self, filetype, filename):
        super().__init__()

        from BiblesSqlite import Bible

        self.filetype = filetype
        self.filename = filename

        self.setWindowTitle(config.thisTranslation["modify_database"])
        self.layout = QVBoxLayout()
        self.setMinimumWidth(300)

        if filetype == "bible":
            self.bible = Bible(filename)
            self.bible.addMissingColumns()

            self.layout.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["name"], filename)))

            row = QHBoxLayout()
            row.addWidget(QLabel("{0}: ".format(config.thisTranslation["title"])))
            self.bibleTitle = QLineEdit()
            self.bibleTitle.setText(self.bible.bibleInfo())
            self.bibleTitle.setMaxLength(100)
            row.addWidget(self.bibleTitle)
            self.layout.addLayout(row)

            (fontName, fontSize) = self.bible.getFontInfo()
            row = QHBoxLayout()
            row.addWidget(QLabel("{0}: ".format(config.thisTranslation["menu2_fontSize"])))
            self.fontSize = QLineEdit()
            self.fontSize.setText(fontSize)
            self.fontSize.setMaxLength(20)
            row.addWidget(self.fontSize)
            self.layout.addLayout(row)

            fonts = sorted(glob.glob("htmlResources/fonts/*.ttf"))
            self.fonts = [''] + [os.path.basename(font) for font in fonts]
            try:
                index = self.fonts.index(fontName)
            except:
                index = 0
            row = QHBoxLayout()
            row.addWidget(QLabel("{0}: ".format(config.thisTranslation["font_name"])))
            self.fontList = QComboBox()
            self.fontList.addItems(self.fonts)
            self.fontList.setCurrentIndex(index)
            row.addWidget(self.fontList)
            self.layout.addLayout(row)
        else:
            self.layout.addWidget(QLabel("{0} is not supported".format(filetype)))

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.save)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def save(self):
        if self.filetype == "bible":
            self.bible.updateTitleAndFontInfo(self.bibleTitle.text(),
                                              self.fontSize.text(),
                                              self.fonts[self.fontList.currentIndex()])

if __name__ == '__main__':
    from util.ConfigUtil import ConfigUtil
    from util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.thisTranslation = LanguageUtil.loadTranslation("en_GB")

    config.mainText = "MOV"
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = ModifyDatabaseDialog("bible", config.mainText)
    window.exec_()
    window.close()