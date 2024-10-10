if not __name__ == "__main__":
    from uniquebible import config
from functools import partial
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QColor
    from PySide6.QtWidgets import QRadioButton, QComboBox, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QColorDialog, QInputDialog, QLineEdit
else:
    from qtpy.QtGui import QColor
    from qtpy.QtWidgets import QRadioButton, QComboBox, QGroupBox, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QColorDialog, QInputDialog, QLineEdit
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.db.Highlight import Highlight

class HighlightLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle("Highlight Editor" if __name__ == "__main__" else config.thisTranslation["highlightEditor"])
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()

    def setupVariables(self):
        self.isRefreshing = False
        bibleVerseParser = BibleVerseParser(config.parserStandarisation)
        bookNo2Abb = bibleVerseParser.standardAbbreviation
        #bookNo2Name = bibleVerseParser.standardFullBookName
        bookList = [i + 1 for i in range(66)]
        self.searchList = [config.thisTranslation["filter"], "{0}-{1}".format(bookNo2Abb["1"], bookNo2Abb["66"]), "{0}-{1}".format(bookNo2Abb["1"], bookNo2Abb["39"]), "{0}-{1}".format(bookNo2Abb["40"], bookNo2Abb["66"])] + [bookNo2Abb[str(b)] for b in bookList]
        #self.searchListToolTips = [config.thisTranslation["filter"], "{0}-{1}".format(bookNo2Name["1"], bookNo2Name["66"]), "{0}-{1}".format(bookNo2Name["1"], bookNo2Name["39"]), "{0}-{1}".format(bookNo2Name["40"], bookNo2Name["66"])] + [bookNo2Name[str(b)] for b in bookList]

    def refresh(self):
        self.isRefreshing = True
        codes = Highlight().isHighlighted(self.parent.parent.bibleTab.b, self.parent.parent.bibleTab.c, self.parent.parent.bibleTab.v)
        if codes:
            index = int(codes[0][-1]) - 1
            self.collectionRadioButtons[index].setChecked(True)
            self.noHighlightRadioButton.setText(config.thisTranslation["removeHightlight"])
        else:
            self.noHighlightRadioButton.setChecked(True)
            self.noHighlightRadioButton.setText(config.thisTranslation["noHightlight"])
        self.isRefreshing = False
        
    def setupUI(self):

        layout = QVBoxLayout()

        columns = QHBoxLayout()
        leftColumn = QVBoxLayout()
        rightColumn = QVBoxLayout()

        self.collectionButton1, self.collectionButton2, self.collectionButton3, self.collectionButton4, self.collectionButton5, self.collectionButton6, self.collectionButton7, self.collectionButton8, self.collectionButton9, self.collectionButton10, self.collectionButton11, self.collectionButton12 = QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton()
        self.collectionButtons = (self.collectionButton1, self.collectionButton2, self.collectionButton3, self.collectionButton4, self.collectionButton5, self.collectionButton6, self.collectionButton7, self.collectionButton8, self.collectionButton9, self.collectionButton10, self.collectionButton11, self.collectionButton12)
        self.collectionColourButton1, self.collectionColourButton2, self.collectionColourButton3, self.collectionColourButton4, self.collectionColourButton5, self.collectionColourButton6, self.collectionColourButton7, self.collectionColourButton8, self.collectionColourButton9, self.collectionColourButton10, self.collectionColourButton11, self.collectionColourButton12 = QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton(), QPushButton()
        self.collectionColourButtons = (self.collectionColourButton1, self.collectionColourButton2, self.collectionColourButton3, self.collectionColourButton4, self.collectionColourButton5, self.collectionColourButton6, self.collectionColourButton7, self.collectionColourButton8, self.collectionColourButton9, self.collectionColourButton10, self.collectionColourButton11, self.collectionColourButton12)
        self.collectionRadioButton1, self.collectionRadioButton2, self.collectionRadioButton3, self.collectionRadioButton4, self.collectionRadioButton5, self.collectionRadioButton6, self.collectionRadioButton7, self.collectionRadioButton8, self.collectionRadioButton9, self.collectionRadioButton10, self.collectionRadioButton11, self.collectionRadioButton12 = QRadioButton(), QRadioButton(), QRadioButton(), QRadioButton(), QRadioButton(), QRadioButton(), QRadioButton(), QRadioButton(), QRadioButton(), QRadioButton(), QRadioButton(), QRadioButton()
        self.collectionRadioButtons = (self.collectionRadioButton1, self.collectionRadioButton2, self.collectionRadioButton3, self.collectionRadioButton4, self.collectionRadioButton5, self.collectionRadioButton6, self.collectionRadioButton7, self.collectionRadioButton8, self.collectionRadioButton9, self.collectionRadioButton10, self.collectionRadioButton11, self.collectionRadioButton12)
        for index, button in enumerate(self.collectionButtons):
            subLayout = QHBoxLayout()
            
            radioButton = self.collectionRadioButtons[index]
            radioButton.setFixedWidth(20)
            radioButton.toggled.connect(lambda checked, option=index: self.highlightOptionChanged(checked, option))
            radioButton.setToolTip(config.thisTranslation["selectApplyHighlight"])
            subLayout.addWidget(radioButton)

            button.setText("collection" if __name__ == "__main__" else config.highlightCollections[index])
            button.setFixedWidth(170)
            button.setToolTip(config.thisTranslation["rename"])
            button.clicked.connect(partial(self.rename, index))
            subLayout.addWidget(button)

            button = self.collectionColourButtons[index]
            button.setFixedWidth(50)
            buttonStyle = "QPushButton {0}background-color: {2}; color: {3};{1}".format("{", "}", config.highlightDarkThemeColours[index] if config.theme == "dark" else config.highlightLightThemeColours[index], "white" if config.theme == "dark" else "black")
            button.setStyleSheet(buttonStyle)
            button.setToolTip(config.thisTranslation["changeColour"])
            button.clicked.connect(partial(self.changeColor, index))
            subLayout.addWidget(button)
            combo = QComboBox()
            combo.setToolTip(config.thisTranslation["filterHighlight"])
            combo.addItems(self.searchList)
            #for index, toolTip in enumerate(self.searchListToolTips):
                #combo.setItemData(index, toolTip, Qt.ToolTipRole)
            combo.setFixedWidth(100)
            combo.currentIndexChanged.connect(lambda selectedIndex, index=index: self.searchHighlight(selectedIndex, index))
            subLayout.addWidget(combo)
            
            leftColumn.addLayout(subLayout) if (index % 2 == 0) else rightColumn.addLayout(subLayout)

        columns.addLayout(leftColumn)
        columns.addLayout(rightColumn)
        layout.addLayout(columns)

        subLayout0 = QHBoxLayout()
        subLayout = QHBoxLayout()
        self.noHighlightRadioButton = QRadioButton()
        self.noHighlightRadioButton.setFixedWidth(20)
        self.noHighlightRadioButton.toggled.connect(self.highlightOptionChanged)
        self.noHighlightRadioButton.setToolTip(config.thisTranslation["selectRemoveHighlight"])
        subLayout.addWidget(self.noHighlightRadioButton)
        button = QPushButton(config.thisTranslation["noHightlight"])
        button.setToolTip(config.thisTranslation["selectRemoveHighlight"])
        button.clicked.connect(lambda: self.highlightOptionChanged(True))
        subLayout.addWidget(button)
        subLayout0.addLayout(subLayout)
        subLayout = QHBoxLayout()
        button = QPushButton(config.thisTranslation["allCollections"])
        button.setToolTip(config.thisTranslation["allCollections"])
        button.clicked.connect(lambda: self.searchHighlight(1, "all"))
        subLayout.addWidget(button)
        #subLayout.addWidget(QLabel("All Collections in:"))
        combo = QComboBox()
        combo.setToolTip(config.thisTranslation["filterHighlight"])
        combo.addItems(self.searchList)
        combo.setFixedWidth(100)
        combo.currentIndexChanged.connect(lambda selectedIndex: self.searchHighlight(selectedIndex, "all"))
        subLayout.addWidget(combo)
        subLayout0.addLayout(subLayout)
        layout.addLayout(subLayout0)

        layout.addStretch()

        box = QGroupBox(config.thisTranslation["menu_highlights"])
        box.setLayout(layout)

        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(0)
        mainLayout.addWidget(box)
        mainLayout.addStretch()
        self.setLayout(mainLayout)

    def highlightOptionChanged(self, checked, option=None):
        if checked and not self.isRefreshing:
            if not config.enableVerseHighlighting:
                config.enableVerseHighlighting = True
            if option is None:
                code = "delete"
            else:
                code = "hl{0}".format(option + 1)
            command = "_HIGHLIGHT:::{0}:::{1}".format(code, self.parent.parent.bibleTab.getSelectedReference())
            self.parent.parent.runTextCommand(command, reloadMainWindow=True)

    def searchHighlight(self, selectedIndex, code):
        if selectedIndex != 0:
            if not config.enableVerseHighlighting:
                config.enableVerseHighlighting = True
            scopes = {
                1: "all",
                2: "ot",
                3: "nt",
            }
            scope = scopes.get(selectedIndex, self.searchList[selectedIndex])
            command = "SEARCHHIGHLIGHT:::{0}:::{1}".format(code if code == "all" else "hl" + str(code + 1), scope)
            self.parent.parent.runTextCommand(command)

    def rename(self, index):
        newName, ok = QInputDialog.getText(self, "QInputDialog.getText()",
                config.thisTranslation["edit"], QLineEdit.Normal,
                config.highlightCollections[index])
        if ok and newName:
            config.highlightCollections[index] = newName
            self.collectionButtons[index].setText(newName)

    def changeColor(self, index):
        color = QColorDialog.getColor(QColor(config.highlightDarkThemeColours[index] if config.theme == "dark" else config.highlightLightThemeColours[index]), self)
        if color.isValid():
            colorName = color.name()
            if config.theme in ("dark", "night"):
                config.highlightDarkThemeColours[index] = colorName
            else:
                config.highlightLightThemeColours[index] = colorName
            button = self.collectionColourButtons[index]
            buttonStyle = "QPushButton {0}background-color: {2}; color: {3};{1}".format("{", "}", colorName, "white" if config.theme == "dark" else "black")
            button.setStyleSheet(buttonStyle)

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    ui = HighlightLauncher(None)
    ui.show()
    sys.exit(app.exec_())
