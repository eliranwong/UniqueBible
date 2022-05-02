import sys, config
import webbrowser
from qtpy.QtWidgets import QLabel, QPushButton, QFrame, QDialog, QGridLayout, QColorDialog, QApplication
from qtpy.QtGui import QColor, QPalette

class MaterialColorDialog(QDialog):

    def __init__(self, parent=None):
        super(MaterialColorDialog, self).__init__(parent)
        self.parent = parent

        frameStyle = QFrame.Sunken | QFrame.Panel

        self.pushButtonBackgroundColor = QLabel()
        self.pushButtonBackgroundColor.setFrameStyle(frameStyle)
        self.pushButtonBackgroundColorButton = QPushButton("pushButtonBackgroundColor")
        self.pushButtonBackgroundColorButton.clicked.connect(self.setPushButtonBackgroundColor)

        self.pushButtonForegroundColor = QLabel()
        self.pushButtonForegroundColor.setFrameStyle(frameStyle)
        self.pushButtonForegroundColorButton = QPushButton("pushButtonForegroundColor")
        self.pushButtonForegroundColorButton.clicked.connect(self.setPushButtonForegroundColor)

        self.pushButtonBackgroundColorHover = QLabel()
        self.pushButtonBackgroundColorHover.setFrameStyle(frameStyle)
        self.pushButtonBackgroundColorHoverButton = QPushButton("pushButtonBackgroundColorHover")
        self.pushButtonBackgroundColorHoverButton.clicked.connect(self.setPushButtonBackgroundColorHover)

        self.pushButtonForegroundColorHover = QLabel()
        self.pushButtonForegroundColorHover.setFrameStyle(frameStyle)
        self.pushButtonForegroundColorHoverButton = QPushButton("pushButtonForegroundColorHover")
        self.pushButtonForegroundColorHoverButton.clicked.connect(self.setPushButtonForegroundColorHover)

        self.pushButtonBackgroundColorPressed = QLabel()
        self.pushButtonBackgroundColorPressed.setFrameStyle(frameStyle)
        self.pushButtonBackgroundColorPressedButton = QPushButton("pushButtonBackgroundColorPressed")
        self.pushButtonBackgroundColorPressedButton.clicked.connect(self.setPushButtonBackgroundColorPressed)

        self.pushButtonForegroundColorPressed = QLabel()
        self.pushButtonForegroundColorPressed.setFrameStyle(frameStyle)
        self.pushButtonForegroundColorPressedButton = QPushButton("pushButtonForegroundColorPressed")
        self.pushButtonForegroundColorPressedButton.clicked.connect(self.setPushButtonForegroundColorPressed)

        self.defaultButton = QPushButton(config.thisTranslation["default"])
        self.defaultButton.clicked.connect(self.setDefault)

        self.aboutButton = QPushButton(config.thisTranslation["menu_about"])
        self.aboutButton.clicked.connect(self.openWiki)

        self.setConfigColor()

        layout = QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(1, 250)

        layout.addWidget(self.pushButtonBackgroundColorButton, 0, 0)
        layout.addWidget(self.pushButtonBackgroundColor, 0, 1)
        layout.addWidget(self.pushButtonBackgroundColorHoverButton, 2, 0)
        layout.addWidget(self.pushButtonBackgroundColorHover, 2, 1)
        layout.addWidget(self.pushButtonBackgroundColorPressedButton, 4, 0)
        layout.addWidget(self.pushButtonBackgroundColorPressed, 4, 1)

        layout.addWidget(self.pushButtonForegroundColorButton, 1, 0)
        layout.addWidget(self.pushButtonForegroundColor, 1, 1)
        layout.addWidget(self.pushButtonForegroundColorHoverButton, 3, 0)
        layout.addWidget(self.pushButtonForegroundColorHover, 3, 1)
        layout.addWidget(self.pushButtonForegroundColorPressedButton, 5, 0)
        layout.addWidget(self.pushButtonForegroundColorPressed, 5, 1)

        layout.addWidget(self.defaultButton, 6, 0)
        layout.addWidget(self.aboutButton, 6, 1)

        self.setLayout(layout)

        self.setWindowTitle(config.thisTranslation["buttonColourCustomisation"])

    def openWiki(self):
        webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/Button-Colour-Customisation")

    def setLabelColor(self, label, color):
        label.setText(color.name())
        label.setPalette(QPalette(color))
        label.setAutoFillBackground(True)

    def setDefault(self):
        config.materialIconMaskColor = '#e7e7e7'
        config.maskBackground = True
        config.pushButtonBackgroundColor = '#e7e7e7'
        config.pushButtonForegroundColor = 'black'
        config.pushButtonBackgroundColorHover = '#f8f8a0'
        config.pushButtonForegroundColorHover = 'black'
        config.pushButtonBackgroundColorPressed = '#a2a934'
        config.pushButtonForegroundColorPressed = 'white'
        self.setConfigColor()
        self.parent.defineStyle()
        self.parent.setupMenuLayout("material")

    def setConfigColor(self):
        self.setLabelColor(self.pushButtonBackgroundColor, QColor(config.pushButtonBackgroundColor))
        self.setLabelColor(self.pushButtonForegroundColor, QColor(config.pushButtonForegroundColor))
        self.setLabelColor(self.pushButtonBackgroundColorHover, QColor(config.pushButtonBackgroundColorHover))
        self.setLabelColor(self.pushButtonForegroundColorHover, QColor(config.pushButtonForegroundColorHover))
        self.setLabelColor(self.pushButtonBackgroundColorPressed, QColor(config.pushButtonBackgroundColorPressed))
        self.setLabelColor(self.pushButtonForegroundColorPressed, QColor(config.pushButtonForegroundColorPressed))

    def setMaskColor(self):
        config.maskBackground = False
        config.materialIconMaskColor = config.pushButtonForegroundColor
        self.parent.defineStyle()
        self.parent.setupMenuLayout("material")

    def setPushButtonBackgroundColor(self):
        color = QColorDialog.getColor(QColor(config.pushButtonBackgroundColor), self)
        if color.isValid():
            self.setLabelColor(self.pushButtonBackgroundColor, color)
            config.pushButtonBackgroundColor = color.name()
            self.setMaskColor()

    def setPushButtonForegroundColor(self):
        color = QColorDialog.getColor(QColor(config.pushButtonForegroundColor), self)
        if color.isValid():
            self.setLabelColor(self.pushButtonForegroundColor, color)
            config.pushButtonForegroundColor = color.name()
            self.setMaskColor()

    def setPushButtonBackgroundColorHover(self):
        color = QColorDialog.getColor(QColor(config.pushButtonBackgroundColorHover), self)
        if color.isValid():
            self.setLabelColor(self.pushButtonBackgroundColorHover, color)
            config.pushButtonBackgroundColorHover = color.name()
            self.setMaskColor()

    def setPushButtonForegroundColorHover(self):
        color = QColorDialog.getColor(QColor(config.pushButtonForegroundColorHover), self)
        if color.isValid():
            self.setLabelColor(self.pushButtonForegroundColorHover, color)
            config.pushButtonForegroundColorHover = color.name()
            self.setMaskColor()

    def setPushButtonBackgroundColorPressed(self):
        color = QColorDialog.getColor(QColor(config.pushButtonBackgroundColorPressed), self)
        if color.isValid():
            self.setLabelColor(self.pushButtonBackgroundColorPressed, color)
            config.pushButtonBackgroundColorPressed = color.name()
            self.setMaskColor()

    def setPushButtonForegroundColorPressed(self):
        color = QColorDialog.getColor(QColor(config.pushButtonForegroundColorPressed), self)
        if color.isValid():
            self.setLabelColor(self.pushButtonForegroundColorPressed, color)
            config.pushButtonForegroundColorPressed = color.name()
            self.setMaskColor()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = MaterialColorDialog()
    sys.exit(dialog.exec_())
