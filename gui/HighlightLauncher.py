if not __name__ == "__main__":
    import config
from functools import partial
from PySide2.QtCore import Qt
from PySide2.QtGui import QPalette, QColor
from PySide2.QtGui import QGuiApplication
from PySide2.QtWidgets import QBoxLayout, QHBoxLayout, QVBoxLayout, QLabel, QWidget, QPushButton, QColorDialog, QFrame, QInputDialog, QLineEdit

class HighlightLauncher(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle("Highlight Editor" if __name__ == "__main__" else config.thisTranslation["highlightEditor"])
        # setup interface
        self.setupUI()

    # window appearance
    def resizeWindow(self, widthFactor, heightFactor):
        availableGeometry = QGuiApplication.instance().desktop().availableGeometry()
        self.setMinimumWidth(500)
        self.resize(availableGeometry.width() * widthFactor, availableGeometry.height() * heightFactor)

    def setupUI(self):
        layout = QVBoxLayout()
        subLayout = QHBoxLayout()
        subSubLayout = QBoxLayout(QBoxLayout.LeftToRight)
        subSubLayout.addWidget(QLabel("Collections" if __name__ == "__main__" else config.thisTranslation["highlightEditorLabel"]))
        subLayout.addLayout(subSubLayout)
        subSubLayout = QBoxLayout(QBoxLayout.RightToLeft)
        subSubLayout.addWidget(QLabel("Change" if __name__ == "__main__" else config.thisTranslation["change"]))
        subLayout.addLayout(subSubLayout)
        layout.addLayout(subLayout)
        
        frameStyle = QFrame.Sunken | QFrame.Panel
        self.collectionLabel1, self.collectionLabel2, self.collectionLabel3, self.collectionLabel4, self.collectionLabel5, self.collectionLabel6, self.collectionLabel7, self.collectionLabel8, self.collectionLabel9, self.collectionLabel10 = QLabel(), QLabel(), QLabel(), QLabel(), QLabel(), QLabel(), QLabel(), QLabel(), QLabel(), QLabel()
        self.collectionLabels = (self.collectionLabel1, self.collectionLabel2, self.collectionLabel3, self.collectionLabel4, self.collectionLabel5, self.collectionLabel6, self.collectionLabel7, self.collectionLabel8, self.collectionLabel9, self.collectionLabel10)
        for index, label in enumerate(self.collectionLabels):
            subLayout = QHBoxLayout()
            label.setText("Highlight {0}".format(index + 1) if __name__ == "__main__" else config.highlightCollections[index])
            label.setFrameStyle(frameStyle)
            label.setAutoFillBackground(True)
            if __name__ == "__main__":
                label.setPalette(QPalette(QColor("#060166")))
            else:
                label.setPalette(QPalette(QColor(config.highlightDarkThemeColours[index] if config.theme == "dark" else config.highlightLightThemeColours[index])))
            subLayout.addWidget(label)
            button = QPushButton("name" if __name__ == "__main__" else config.thisTranslation["rename"])
            button.clicked.connect(partial(self.rename, index))
            subLayout.addWidget(button)
            subLayout.addWidget(QPushButton("colour" if __name__ == "__main__" else config.thisTranslation["changeColour"]))
            layout.addLayout(subLayout)

        self.setLayout(layout)

    def rename(self, index):
        print(index)
        newName, ok = QInputDialog.getText(self, "QInputDialog.getText()",
                config.thisTranslation["edit"], QLineEdit.Normal,
                config.highlightCollections[index])
        if ok and newName:
            config.highlightCollections[index] = newName
            self.collectionLabels[index].setText(newName)

    def changeColor(self):
        color = QColorDialog.getColor(Qt.green, self)
        if color.isValid():
            #self.colorLabel.setText(color.name())
            #self.colorLabel.setPalette(QPalette(color))
            #self.colorLabel.setAutoFillBackground(True)
            return (color.name(), QPalette(color))
        return ()

if __name__ == "__main__":
    import sys
    from PySide2.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    ui = HighlightLauncher(None)
    ui.show()
    sys.exit(app.exec_())
