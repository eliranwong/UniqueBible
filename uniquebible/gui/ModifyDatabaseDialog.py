import glob
import os
import sys
from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QFontDatabase
    from PySide6 import QtCore
    from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QComboBox, QRadioButton, QGridLayout
else:
    from qtpy.QtGui import QFontDatabase
    from qtpy import QtCore
    from qtpy.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QComboBox, QRadioButton, QGridLayout
from uniquebible.util.Languages import Languages


class ModifyDatabaseDialog(QDialog):

    def __init__(self, filetype, filename):
        super().__init__()

        from uniquebible.db.BiblesSqlite import Bible
        self.fontDatabase = QFontDatabase()

        self.filetype = filetype
        self.filename = filename

        self.setWindowTitle(config.thisTranslation["modify_database"])
        self.layout = QVBoxLayout()
        self.setMinimumWidth(300)

        if filetype == "bible":
            self.bible = Bible(filename)
            self.bible.addMissingColumns()
            (fontName, fontSize, css) = self.bible.getFontInfo()
            if fontName is None:
                fontName = ""
            if fontSize is None:
                fontSize = ""

            self.layout.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["name"], filename)))

            row = QHBoxLayout()
            row.addWidget(QLabel("{0}: ".format(config.thisTranslation["title"])))
            self.bibleTitle = QLineEdit()
            self.bibleTitle.setText(self.bible.bibleInfo())
            self.bibleTitle.setMaxLength(100)
            row.addWidget(self.bibleTitle)
            self.layout.addLayout(row)

            grid = QGridLayout()

            self.builtinFonts = [""] + self.fontDatabase.families()
            try:
                index = self.builtinFonts.index(fontName.replace(".builtin", ""))
            except:
                index = 0
            self.useBuiltinFont = QRadioButton()
            self.useBuiltinFont.clicked.connect(lambda: self.selectRadio("builtin"))
            grid.addWidget(self.useBuiltinFont, 0, 0)
            grid.addWidget(QLabel("{0}: ".format("Built-in font")), 0, 1)
            self.builtinFontList = QComboBox()
            self.builtinFontList.addItems(self.builtinFonts)
            self.builtinFontList.setCurrentIndex(index)
            grid.addWidget(self.builtinFontList, 0, 2)

            fonts = sorted(glob.glob(r"htmlResources/fonts/*.*"))
            self.fontFiles = [''] + [os.path.basename(font) for font in fonts]
            try:
                index = self.fontFiles.index(fontName)
            except:
                index = 0
            row = QHBoxLayout()
            self.useFileFont = QRadioButton()
            self.useFileFont.clicked.connect(lambda: self.selectRadio("file"))
            grid.addWidget(self.useFileFont, 1, 0)
            row.addStretch(1)
            grid.addWidget(QLabel("{0}: ".format("Font file")), 1, 1)
            self.fileFontList = QComboBox()
            self.fileFontList.addItems(self.fontFiles)
            self.fileFontList.setCurrentIndex(index)
            grid.addWidget(self.fileFontList, 1, 2)
            self.layout.addLayout(grid)
        else:
            self.layout.addWidget(QLabel("{0} is not supported".format(filetype)))

        row = QHBoxLayout()
        row.addWidget(QLabel("{0}: ".format(config.thisTranslation["menu2_fontSize"])))
        self.fontSize = QLineEdit()
        self.fontSize.setText(fontSize)
        self.fontSize.setMaxLength(20)
        row.addWidget(self.fontSize)
        self.layout.addLayout(row)

        self.languageCodes = [""] + [value for value in Languages.code.values()]

        row = QHBoxLayout()
        row.addWidget(QLabel("{0}: ".format(config.thisTranslation["menu_language"])))
        self.languageList = QComboBox()
        row.addWidget(self.languageList)
        self.languageList.addItems(self.languageCodes)
        self.languageList.setCurrentIndex(self.languageCodes.index(self.bible.getLanguage()))
        self.layout.addLayout(row)

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.save)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        if ".ttf" in fontName:
            self.selectRadio("file")
        else:
            self.selectRadio("builtin")

    def selectRadio(self, option):
        if option == "builtin":
            self.useBuiltinFont.setChecked(True)
            self.builtinFontList.setEnabled(True)
            self.fileFontList.setEnabled(False)
        else:
            self.useFileFont.setChecked(True)
            self.builtinFontList.setEnabled(False)
            self.fileFontList.setEnabled(True)

    def save(self):
        if self.filetype == "bible":
            if self.useBuiltinFont.isChecked():
                font = self.builtinFonts[self.builtinFontList.currentIndex()]
                font += ".builtin"
            else:
                font = self.fontFiles[self.fileFontList.currentIndex()]
            self.bible.updateTitleAndFontInfo(self.bibleTitle.text(),
                                              self.fontSize.text(), font)
            language = self.languageCodes[self.languageList.currentIndex()]
            self.bible.updateLanguage(language)

if __name__ == '__main__':
    from uniquebible.util.ConfigUtil import ConfigUtil
    from uniquebible.util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.thisTranslation = LanguageUtil.loadTranslation("en_GB")

    config.mainText = "KJV"
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = ModifyDatabaseDialog("bible", config.mainText)
    window.exec_()
    window.close()
