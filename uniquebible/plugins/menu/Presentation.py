from uniquebible import config
import sys
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QApplication, QWidget
else:
    from qtpy.QtWidgets import QApplication, QWidget

from uniquebible.util.BibleBooks import BibleBooks


class ConfigurePresentationWindow(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle("Configure Presentation")
        # set variables
        self.setupVariables()
        # setup Hymn Lyrics
        from glob import glob
        from pathlib import Path
        books = glob(r"./marvelData/books/Hymn Lyrics*.book") + glob(r"./marvelData/books/*Songs.book")
        self.books = sorted([Path(filename).stem for filename in books])
        if len(self.books) > 0:
            self.setMinimumHeight(550)
        # setup interface
        self.setupUI()

    def setupVariables(self):
        pass

    def setupUI(self):

        from functools import partial
        if config.qtLibrary == "pyside6":
            from PySide6.QtCore import Qt
            from PySide6.QtWidgets import QHBoxLayout, QFormLayout, QSlider, QPushButton, QPlainTextEdit, QCheckBox, QComboBox
            from PySide6.QtWidgets import QRadioButton, QWidget, QVBoxLayout, QListView, QSpacerItem, QSizePolicy
        else:
            from qtpy.QtCore import Qt
            from qtpy.QtWidgets import QHBoxLayout, QFormLayout, QSlider, QPushButton, QPlainTextEdit, QCheckBox, QComboBox
            from qtpy.QtWidgets import QRadioButton, QWidget, QVBoxLayout, QListView, QSpacerItem, QSizePolicy

        layout = QHBoxLayout()

        layout1 = QFormLayout()

        self.fontsizeslider = QSlider(Qt.Horizontal)
        self.fontsizeslider.setMinimum(1)
        self.fontsizeslider.setMaximum(12)
        self.fontsizeslider.setTickInterval(2)
        self.fontsizeslider.setSingleStep(2)
        self.fontsizeslider.setValue(int(config.presentationFontSize / 0.5))
        self.fontsizeslider.setToolTip(str(config.presentationFontSize))
        self.fontsizeslider.valueChanged.connect(self.presentationFontSizeChanged)
        layout1.addRow("Font Size", self.fontsizeslider)

        self.changecolorbutton = QPushButton()
        buttonStyle = "QPushButton {0}background-color: {2}; color: {3};{1}".format("{", "}", config.presentationColorOnDarkTheme if config.theme in ("dark", "night") else config.presentationColorOnLightTheme, "white" if config.theme in ("dark", "night") else "black")
        self.changecolorbutton.setStyleSheet(buttonStyle)
        self.changecolorbutton.setToolTip("Change Color")
        self.changecolorbutton.clicked.connect(self.changeColor)
        layout1.addRow("Font Color", self.changecolorbutton)

        self.marginslider = QSlider(Qt.Horizontal)
        self.marginslider.setMinimum(0)
        self.marginslider.setMaximum(200)
        self.marginslider.setTickInterval(50)
        self.marginslider.setSingleStep(50)
        self.marginslider.setValue(config.presentationMargin)
        self.marginslider.setToolTip(str(config.presentationMargin))
        self.marginslider.valueChanged.connect(self.presentationMarginChanged)
        layout1.addRow("Margin", self.marginslider)

        self.verticalpositionslider = QSlider(Qt.Horizontal)
        self.verticalpositionslider.setMinimum(10)
        self.verticalpositionslider.setMaximum(90)
        self.verticalpositionslider.setTickInterval(10)
        self.verticalpositionslider.setSingleStep(10)
        self.verticalpositionslider.setValue(config.presentationVerticalPosition)
        self.verticalpositionslider.setToolTip(str(config.presentationVerticalPosition))
        self.verticalpositionslider.valueChanged.connect(self.presentationVerticalPositionChanged)
        layout1.addRow("Vertical Position", self.verticalpositionslider)

        self.horizontalpositionslider = QSlider(Qt.Horizontal)
        self.horizontalpositionslider.setMinimum(10)
        self.horizontalpositionslider.setMaximum(90)
        self.horizontalpositionslider.setTickInterval(10)
        self.horizontalpositionslider.setSingleStep(10)
        self.horizontalpositionslider.setValue(config.presentationHorizontalPosition)
        self.horizontalpositionslider.setToolTip(str(config.presentationHorizontalPosition))
        self.horizontalpositionslider.valueChanged.connect(self.presentationHorizontalPositionChanged)
        layout1.addRow("Horizontal Position", self.horizontalpositionslider)

        self.showBibleSelection = QRadioButton()
        self.showBibleSelection.setChecked(True)
        self.showBibleSelection.clicked.connect(lambda: self.selectRadio("bible"))
        layout1.addRow("Bible", self.showBibleSelection)

        if len(self.books) > 0:
            self.showHymnsSelection = QRadioButton()
            self.showHymnsSelection.setChecked(False)
            self.showHymnsSelection.clicked.connect(lambda: self.selectRadio("hymns"))
            layout1.addRow("Songs", self.showHymnsSelection)

        # Second column

        layout2 = QVBoxLayout()

        self.bibleWidget = QWidget()
        self.bibleLayout = QFormLayout()

        checkbox = QCheckBox()
        checkbox.setText("")
        checkbox.setChecked(config.presentationParser)
        checkbox.stateChanged.connect(self.presentationParserChanged)
        checkbox.setToolTip("Parse bible verse reference in the entered text")
        self.bibleLayout.addRow("Bible Reference", checkbox)

        versionCombo = QComboBox()
        self.bibleVersions = self.parent.textList
        versionCombo.addItems(self.bibleVersions)
        initialIndex = 0
        if config.mainText in self.bibleVersions:
            initialIndex = self.bibleVersions.index(config.mainText)
        versionCombo.setCurrentIndex(initialIndex)
        versionCombo.currentIndexChanged.connect(self.changeBibleVersion)
        self.bibleLayout.addRow("Bible Version", versionCombo)

        defaultVerse = "{0} {1}:{2}".format(BibleBooks.abbrev["eng"][str(config.mainB)][0], config.mainC, config.mainV)
        self.textEntry = QPlainTextEdit(defaultVerse)
        self.bibleLayout.addRow(self.textEntry)

        button = QPushButton("Presentation")
        button.setToolTip("Go to Presentation")
        button.clicked.connect(self.goToPresentation)
        self.bibleLayout.addWidget(button)

        self.bibleLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.bibleWidget.setLayout(self.bibleLayout)

        self.hymnWidget = QWidget()
        self.hymnLayout = QFormLayout()

        selected = 0
        book = "Hymn Lyrics - English"
        if book in self.books:
            selected = self.books.index(book)
        self.bookList = QComboBox()
        self.bookList.addItems(self.books)
        self.bookList.setCurrentIndex(selected)
        self.bookList.currentIndexChanged.connect(self.selectHymnBook)
        self.hymnLayout.addWidget(self.bookList)

        self.chapterlist = QListView()
        self.chapterlist.clicked.connect(self.selectHymn)
        # self.chapterlist.selectionModel().selectionChanged.connect(self.selectHymn)
        self.hymnLayout.addWidget(self.chapterlist)

        self.buttons = []
        for count in range(0, 10):
            hymnButton = QPushButton()
            hymnButton.setText(" ")
            hymnButton.setEnabled(False)
            hymnButton.clicked.connect(partial(self.selectParagraph, count))
            self.hymnLayout.addWidget(hymnButton)
            self.buttons.append(hymnButton)

        self.selectHymnBook(selected)

        self.hymnWidget.setLayout(self.hymnLayout)
        self.hymnWidget.hide()

        layout2.addWidget(self.bibleWidget)
        if len(self.books) > 0:
            layout2.addWidget(self.hymnWidget)

        layout.addLayout(layout1)
        layout.addLayout(layout2)
        self.setLayout(layout)

    def selectRadio(self, option):
        if option == "bible":
            self.bibleWidget.show()
            if len(self.books) > 0:
                self.hymnWidget.hide()
        elif option == "hymns":
            self.bibleWidget.hide()
            if len(self.books) > 0:
                self.hymnWidget.show()

    def selectHymnBook(self, option):
        from uniquebible.db.ToolsSqlite import Book
        if config.qtLibrary == "pyside6":
            from PySide6.QtCore import QStringListModel
        else:
            from qtpy.QtCore import QStringListModel
        if len(self.books) > 0:
            self.hymnBook = self.books[option]
            self.hymns = sorted(Book(self.hymnBook).getTopicList())
            self.chapterModel = QStringListModel(self.hymns)
            self.chapterlist.setModel(self.chapterModel)

    def selectHymn(self, option):
        from uniquebible.db.ToolsSqlite import Book
        row = option.row()
        self.hymn = self.hymns[row]
        book = Book(self.hymnBook)
        sections = book.getParagraphSectionsByChapter(self.hymn)
        count = 0
        for button in self.buttons:
            if count < len(sections):
                section = sections[count]
                text = section.replace("<br>", "")[:30]
                button.setText(text)
                button.setEnabled(True)
            else:
                button.setText(" ")
                button.setEnabled(False)
            count += 1

    def selectParagraph(self, paragraph):
        command = "SCREENBOOK:::{0}:::{1}:::{2}".format(self.hymnBook, self.hymn, paragraph)
        self.parent.runTextCommand(command)

    def goToPresentation(self):
        command = "SCREEN:::{0}".format(self.textEntry.toPlainText())
        self.parent.runTextCommand(command)

    def changeColor(self):
        if config.qtLibrary == "pyside6":
            from PySide6.QtGui import QColor
            from PySide6.QtWidgets import QColorDialog
        else:
            from qtpy.QtGui import QColor
            from qtpy.QtWidgets import QColorDialog

        color = QColorDialog.getColor(QColor(config.presentationColorOnDarkTheme if config.theme in ("dark", "night") else config.presentationColorOnLightTheme), self)
        if color.isValid():
            colorName = color.name()
            if config.theme in ("dark", "night"):
                config.presentationColorOnDarkTheme = colorName
            else:
                config.presentationColorOnLightTheme = colorName
            buttonStyle = "QPushButton {0}background-color: {2}; color: {3};{1}".format("{", "}", colorName, "white" if config.theme in ("dark", "night") else "black")
            self.changecolorbutton.setStyleSheet(buttonStyle)

    def presentationFontSizeChanged(self, value):
        config.presentationFontSize = value * 0.5
        self.fontsizeslider.setToolTip(str(config.presentationFontSize))

    def presentationMarginChanged(self, value):
        config.presentationMargin = value
        self.marginslider.setToolTip(str(config.presentationMargin))

    def presentationVerticalPositionChanged(self, value):
        config.presentationVerticalPosition = value
        self.verticalpositionslider.setToolTip(str(config.presentationVerticalPosition))
    
    def presentationHorizontalPositionChanged(self, value):
        config.presentationHorizontalPosition = value
        self.horizontalpositionslider.setValue(config.presentationHorizontalPosition)

    def presentationParserChanged(self):
        config.presentationParser = not config.presentationParser

    def changeBibleVersion(self, index):
        if __name__ == '__main__':
            config.mainText = self.bibleVersions[index]
        else:
            command = "TEXT:::{0}".format(self.bibleVersions[index])
            self.parent.runTextCommand(command)


if __name__ == '__main__':
    from uniquebible.util.ConfigUtil import ConfigUtil
    ConfigUtil.setup()
    config.activeVerseNoColour = "white"
    from uniquebible.gui.MainWindow import MainWindow
    app = QApplication(sys.argv)
    config.mainWindow = MainWindow()
    config.presentationParser = True
    from plugins.startup.screenCommand import presentReferenceOnFullScreen
    config.mainWindow.textCommandParser.interpreters["screen"] = (presentReferenceOnFullScreen, "")

config.mainWindow.configurePresentationWindow = ConfigurePresentationWindow(config.mainWindow)
config.mainWindow.configurePresentationWindow.show()

if __name__ == '__main__':
    sys.exit(app.exec_())