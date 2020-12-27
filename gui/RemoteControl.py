import config
from PySide2.QtWidgets import (QVBoxLayout, QHBoxLayout, QGroupBox, QLineEdit, QPushButton, QWidget)
from BibleVerseParser import BibleVerseParser

class RemoteControl(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Remote Control")
        self.parent = parent
        # specify window size
        self.resizeWindow(2/3, 2/3)
        # setup interface
        self.setupUI()

    # window appearance
    def resizeWindow(self, widthFactor, heightFactor):
        availableGeometry = qApp.desktop().availableGeometry()
        self.resize(availableGeometry.width() * widthFactor, availableGeometry.height() * heightFactor)

    # re-implementing close event, when users close this widget
    # avoid closing by mistake
    # this window can be closed via "Remote Control [On / Off]" in menu bar
    def closeEvent(self, event):
        event.ignore()

    # setup ui
    def setupUI(self):
        mainLayout = QVBoxLayout()

        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setToolTip("Enter command here ...")
        self.searchLineEdit.returnPressed.connect(self.searchLineEntered)
        mainLayout.addWidget(self.searchLineEdit)

        parser = BibleVerseParser(config.parserStandarisation)
        self.bookMap = parser.standardAbbreviation
        bookNums = list(self.bookMap.keys())
        bookNumGps = [
            bookNums[0:10],
            bookNums[10:20],
            bookNums[20:30],
            bookNums[30:39],
            bookNums[39:49],
            bookNums[49:59],
            bookNums[59:66],
        ]
        actionMap = {
            "1": self.updateCommand1,
            "2": self.updateCommand2,
            "3": self.updateCommand3,
            "4": self.updateCommand4,
            "5": self.updateCommand5,
            "6": self.updateCommand6,
            "7": self.updateCommand7,
            "8": self.updateCommand8,
            "9": self.updateCommand9,
            "10": self.updateCommand10,
            "11": self.updateCommand11,
            "12": self.updateCommand12,
            "13": self.updateCommand13,
            "14": self.updateCommand14,
            "15": self.updateCommand15,
            "16": self.updateCommand16,
            "17": self.updateCommand17,
            "18": self.updateCommand18,
            "19": self.updateCommand19,
            "20": self.updateCommand20,
            "21": self.updateCommand21,
            "22": self.updateCommand22,
            "23": self.updateCommand23,
            "24": self.updateCommand24,
            "25": self.updateCommand25,
            "26": self.updateCommand26,
            "27": self.updateCommand27,
            "28": self.updateCommand28,
            "29": self.updateCommand29,
            "30": self.updateCommand30,
            "31": self.updateCommand31,
            "32": self.updateCommand32,
            "33": self.updateCommand33,
            "34": self.updateCommand34,
            "35": self.updateCommand35,
            "36": self.updateCommand36,
            "37": self.updateCommand37,
            "38": self.updateCommand38,
            "39": self.updateCommand39,
            "40": self.updateCommand40,
            "41": self.updateCommand41,
            "42": self.updateCommand42,
            "43": self.updateCommand43,
            "44": self.updateCommand44,
            "45": self.updateCommand45,
            "46": self.updateCommand46,
            "47": self.updateCommand47,
            "48": self.updateCommand48,
            "49": self.updateCommand49,
            "50": self.updateCommand50,
            "51": self.updateCommand51,
            "52": self.updateCommand52,
            "53": self.updateCommand53,
            "54": self.updateCommand54,
            "55": self.updateCommand55,
            "56": self.updateCommand56,
            "57": self.updateCommand57,
            "58": self.updateCommand58,
            "59": self.updateCommand59,
            "60": self.updateCommand60,
            "61": self.updateCommand61,
            "62": self.updateCommand62,
            "63": self.updateCommand63,
            "64": self.updateCommand64,
            "65": self.updateCommand65,
            "66": self.updateCommand66,
        }

        otBooks = QGroupBox("Old Testament")
        otLayout = QVBoxLayout()
        for bookNumGp in bookNumGps[0:4]:
            gp = QWidget()
            layout = QHBoxLayout()
            for bookNum in bookNumGp:
                button = QPushButton(self.bookMap[bookNum])
                button.clicked.connect(actionMap[bookNum])
                layout.addWidget(button)
            gp.setLayout(layout)
            otLayout.addWidget(gp)
        otBooks.setLayout(otLayout)
        mainLayout.addWidget(otBooks)

        ntBooks = QGroupBox("New Testament")
        ntLayout = QVBoxLayout()
        for bookNumGp in bookNumGps[4:7]:
            gp = QWidget()
            layout = QHBoxLayout()
            for bookNum in bookNumGp:
                button = QPushButton(self.bookMap[bookNum])
                button.clicked.connect(actionMap[bookNum])
                layout.addWidget(button)
            gp.setLayout(layout)
            ntLayout.addWidget(gp)
        ntBooks.setLayout(ntLayout)
        mainLayout.addWidget(ntBooks)

        self.setLayout(mainLayout)

    # search field entered
    def searchLineEntered(self):
        searchString = self.searchLineEdit.text()
        self.parent.runTextCommand(searchString)

    # modify search field
    def updateCommand(self, book):
        self.searchLineEdit.setText("{0} ".format(self.bookMap[book]))
        self.searchLineEdit.setFocus()

    def updateCommand1(self):
        self.updateCommand("1")

    def updateCommand2(self):
        self.updateCommand("2")

    def updateCommand3(self):
        self.updateCommand("3")

    def updateCommand4(self):
        self.updateCommand("4")

    def updateCommand5(self):
        self.updateCommand("5")

    def updateCommand6(self):
        self.updateCommand("6")

    def updateCommand7(self):
        self.updateCommand("7")

    def updateCommand8(self):
        self.updateCommand("8")

    def updateCommand9(self):
        self.updateCommand("9")

    def updateCommand10(self):
        self.updateCommand("10")

    def updateCommand11(self):
        self.updateCommand("11")

    def updateCommand12(self):
        self.updateCommand("12")

    def updateCommand13(self):
        self.updateCommand("13")

    def updateCommand14(self):
        self.updateCommand("14")

    def updateCommand15(self):
        self.updateCommand("15")

    def updateCommand16(self):
        self.updateCommand("16")

    def updateCommand17(self):
        self.updateCommand("17")

    def updateCommand18(self):
        self.updateCommand("18")

    def updateCommand19(self):
        self.updateCommand("19")

    def updateCommand20(self):
        self.updateCommand("20")

    def updateCommand21(self):
        self.updateCommand("21")

    def updateCommand22(self):
        self.updateCommand("22")

    def updateCommand23(self):
        self.updateCommand("23")

    def updateCommand24(self):
        self.updateCommand("24")

    def updateCommand25(self):
        self.updateCommand("25")

    def updateCommand26(self):
        self.updateCommand("26")

    def updateCommand27(self):
        self.updateCommand("27")

    def updateCommand28(self):
        self.updateCommand("28")

    def updateCommand29(self):
        self.updateCommand("29")

    def updateCommand30(self):
        self.updateCommand("30")

    def updateCommand31(self):
        self.updateCommand("31")

    def updateCommand32(self):
        self.updateCommand("32")

    def updateCommand33(self):
        self.updateCommand("33")

    def updateCommand34(self):
        self.updateCommand("34")

    def updateCommand35(self):
        self.updateCommand("35")

    def updateCommand36(self):
        self.updateCommand("36")

    def updateCommand37(self):
        self.updateCommand("37")

    def updateCommand38(self):
        self.updateCommand("38")

    def updateCommand39(self):
        self.updateCommand("39")

    def updateCommand40(self):
        self.updateCommand("40")

    def updateCommand41(self):
        self.updateCommand("41")

    def updateCommand42(self):
        self.updateCommand("42")

    def updateCommand43(self):
        self.updateCommand("43")

    def updateCommand44(self):
        self.updateCommand("44")

    def updateCommand45(self):
        self.updateCommand("45")

    def updateCommand46(self):
        self.updateCommand("46")

    def updateCommand47(self):
        self.updateCommand("47")

    def updateCommand48(self):
        self.updateCommand("48")

    def updateCommand49(self):
        self.updateCommand("49")

    def updateCommand50(self):
        self.updateCommand("50")

    def updateCommand51(self):
        self.updateCommand("51")

    def updateCommand52(self):
        self.updateCommand("52")

    def updateCommand53(self):
        self.updateCommand("53")

    def updateCommand54(self):
        self.updateCommand("54")

    def updateCommand55(self):
        self.updateCommand("55")

    def updateCommand56(self):
        self.updateCommand("56")

    def updateCommand57(self):
        self.updateCommand("57")

    def updateCommand58(self):
        self.updateCommand("58")

    def updateCommand59(self):
        self.updateCommand("59")

    def updateCommand60(self):
        self.updateCommand("60")

    def updateCommand61(self):
        self.updateCommand("61")

    def updateCommand62(self):
        self.updateCommand("62")

    def updateCommand63(self):
        self.updateCommand("63")

    def updateCommand64(self):
        self.updateCommand("64")

    def updateCommand65(self):
        self.updateCommand("65")

    def updateCommand66(self):
        self.updateCommand("66")
