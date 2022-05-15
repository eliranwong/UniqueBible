import sys, config, pprint, os
import webbrowser
from qtpy.QtWidgets import QLabel, QPushButton, QFrame, QDialog, QGridLayout, QColorDialog, QApplication, QFileDialog
from qtpy.QtGui import QColor, QPalette

class MaterialColorDialog(QDialog):

    def __init__(self, parent=None):
        super(MaterialColorDialog, self).__init__(parent)
        self.parent = parent

        frameStyle = QFrame.Sunken | QFrame.Panel

        self.widgetBackgroundColor = QLabel()
        self.widgetBackgroundColor.setFrameStyle(frameStyle)
        self.widgetBackgroundColorButton = QPushButton("widgetBackgroundColor")
        self.widgetBackgroundColorButton.clicked.connect(self.setPushButtonBackgroundColor)

        self.widgetForegroundColor = QLabel()
        self.widgetForegroundColor.setFrameStyle(frameStyle)
        self.widgetForegroundColorButton = QPushButton("widgetForegroundColor")
        self.widgetForegroundColorButton.clicked.connect(self.setPushButtonForegroundColor)

        self.widgetBackgroundColorHover = QLabel()
        self.widgetBackgroundColorHover.setFrameStyle(frameStyle)
        self.widgetBackgroundColorHoverButton = QPushButton("widgetBackgroundColorHover")
        self.widgetBackgroundColorHoverButton.clicked.connect(self.setPushButtonBackgroundColorHover)

        self.widgetForegroundColorHover = QLabel()
        self.widgetForegroundColorHover.setFrameStyle(frameStyle)
        self.widgetForegroundColorHoverButton = QPushButton("widgetForegroundColorHover")
        self.widgetForegroundColorHoverButton.clicked.connect(self.setPushButtonForegroundColorHover)

        self.widgetBackgroundColorPressed = QLabel()
        self.widgetBackgroundColorPressed.setFrameStyle(frameStyle)
        self.widgetBackgroundColorPressedButton = QPushButton("widgetBackgroundColorPressed")
        self.widgetBackgroundColorPressedButton.clicked.connect(self.setPushButtonBackgroundColorPressed)

        self.widgetForegroundColorPressed = QLabel()
        self.widgetForegroundColorPressed.setFrameStyle(frameStyle)
        self.widgetForegroundColorPressedButton = QPushButton("widgetForegroundColorPressed")
        self.widgetForegroundColorPressedButton.clicked.connect(self.setPushButtonForegroundColorPressed)

        self.activeVerseColour = QLabel()
        self.activeVerseColour.setFrameStyle(frameStyle)
        self.activeVerseColourButton = QPushButton("activeVerseColourDark" if config.theme in ("dark", "night") else "activeVerseColourLight")
        self.activeVerseColourButton.clicked.connect(self.changeActiveVerseColour)

        self.textSelectionColor = QLabel()
        self.textSelectionColor.setFrameStyle(frameStyle)
        self.textSelectionColorButton = QPushButton("textSelectionColor")
        self.textSelectionColorButton.clicked.connect(self.changeTextSelectionColor)

        self.saveButton = QPushButton(config.thisTranslation["note_saveAs"])
        self.saveButton.clicked.connect(self.openSaveAsDialog)
        self.loadButton = QPushButton(config.thisTranslation["loadMySettings"])
        self.loadButton.clicked.connect(self.openFileDialogAction)

        self.defaultButton = QPushButton(config.thisTranslation["default"])
        self.defaultButton.clicked.connect(self.setDefault)

        self.aboutButton = QPushButton(config.thisTranslation["menu_about"])
        self.aboutButton.clicked.connect(self.openWiki)

        self.setConfigColor()

        layout = QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(1, 250)

        layout.addWidget(self.widgetBackgroundColorButton, 0, 0)
        layout.addWidget(self.widgetBackgroundColor, 0, 1)
        layout.addWidget(self.widgetForegroundColorButton, 1, 0)
        layout.addWidget(self.widgetForegroundColor, 1, 1)
        layout.addWidget(self.widgetBackgroundColorHoverButton, 2, 0)
        layout.addWidget(self.widgetBackgroundColorHover, 2, 1)
        layout.addWidget(self.widgetForegroundColorHoverButton, 3, 0)
        layout.addWidget(self.widgetForegroundColorHover, 3, 1)
        layout.addWidget(self.widgetBackgroundColorPressedButton, 4, 0)
        layout.addWidget(self.widgetBackgroundColorPressed, 4, 1)
        layout.addWidget(self.widgetForegroundColorPressedButton, 5, 0)
        layout.addWidget(self.widgetForegroundColorPressed, 5, 1)

        layout.addWidget(self.activeVerseColourButton, 6, 0)
        layout.addWidget(self.activeVerseColour, 6, 1)
        layout.addWidget(self.textSelectionColorButton, 7, 0)
        layout.addWidget(self.textSelectionColor, 7, 1)

        layout.addWidget(self.saveButton, 8, 0)
        layout.addWidget(self.loadButton, 8, 1)

        layout.addWidget(self.defaultButton, 9, 0)
        layout.addWidget(self.aboutButton, 9, 1)

        self.setLayout(layout)

        self.setWindowTitle(config.thisTranslation["colourCustomisation"])

    def openWiki(self):
        webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/Customise-Interface-Colours")

    def setLabelColor(self, label, color):
        label.setText(color.name())
        label.setPalette(QPalette(color))
        label.setAutoFillBackground(True)

    def openFileDialogAction(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                config.thisTranslation["menu7_open"],
                "",
                "UniqueBible.app Color Settings (*.color)", "", options)
        if fileName:
            with open(fileName, "r") as f:
                settings = f.read()
                exec(settings)
            self.parent.resetUI()
            self.setConfigColor()

    def openSaveAsDialog(self):
        defaultName = "uba.color"
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                defaultName,
                "UniqueBible.app Color Settings (*.color)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".color"
            self.saveData(fileName)

    def saveData(self, fileName):
        data = (
            ("config.maskMaterialIconColor", config.maskMaterialIconColor),
            ("config.maskMaterialIconBackground", config.maskMaterialIconBackground),
            ("config.widgetBackgroundColor", config.widgetBackgroundColor),
            ("config.widgetForegroundColor", config.widgetForegroundColor),
            ("config.widgetBackgroundColorHover", config.widgetBackgroundColorHover),
            ("config.widgetForegroundColorHover", config.widgetForegroundColorHover),
            ("config.widgetBackgroundColorPressed", config.widgetBackgroundColorPressed),
            ("config.widgetForegroundColorPressed", config.widgetForegroundColorPressed),
            ("config.activeVerseColourLight", config.activeVerseColourLight),
            ("config.activeVerseColourDark", config.activeVerseColourDark),
            ("config.textSelectionColor", config.textSelectionColor),
        )
        with open(fileName, "w", encoding="utf-8") as fileObj:
            for name, value in data:
                fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))

    def setDefault(self):
        self.parent.setTheme(config.theme)
        self.setConfigColor()

    def setConfigColor(self):
        self.setLabelColor(self.widgetBackgroundColor, QColor(config.widgetBackgroundColor))
        self.setLabelColor(self.widgetForegroundColor, QColor(config.widgetForegroundColor))
        self.setLabelColor(self.widgetBackgroundColorHover, QColor(config.widgetBackgroundColorHover))
        self.setLabelColor(self.widgetForegroundColorHover, QColor(config.widgetForegroundColorHover))
        self.setLabelColor(self.widgetBackgroundColorPressed, QColor(config.widgetBackgroundColorPressed))
        self.setLabelColor(self.widgetForegroundColorPressed, QColor(config.widgetForegroundColorPressed))
        self.setLabelColor(self.activeVerseColour, QColor(config.activeVerseColourDark if config.theme in ("dark", "night") else config.activeVerseColourLight))
        self.setLabelColor(self.textSelectionColor, QColor(config.textSelectionColor))

    def setMaskColor(self):
        config.maskMaterialIconBackground = False
        config.maskMaterialIconColor = config.widgetForegroundColor
        #config.defineStyle()
        #self.parent.setupMenuLayout("material")
        self.parent.resetUI()

    def setPushButtonBackgroundColor(self):
        color = QColorDialog.getColor(QColor(config.widgetBackgroundColor), self)
        if color.isValid():
            config.widgetBackgroundColor = color.name()
            self.setMaskColor()
            self.setLabelColor(self.widgetBackgroundColor, color)

    def setPushButtonForegroundColor(self):
        color = QColorDialog.getColor(QColor(config.widgetForegroundColor), self)
        if color.isValid():
            config.widgetForegroundColor = color.name()
            self.setMaskColor()
            self.setLabelColor(self.widgetForegroundColor, color)

    def setPushButtonBackgroundColorHover(self):
        color = QColorDialog.getColor(QColor(config.widgetBackgroundColorHover), self)
        if color.isValid():
            config.widgetBackgroundColorHover = color.name()
            self.setMaskColor()
            self.setLabelColor(self.widgetBackgroundColorHover, color)

    def setPushButtonForegroundColorHover(self):
        color = QColorDialog.getColor(QColor(config.widgetForegroundColorHover), self)
        if color.isValid():
            config.widgetForegroundColorHover = color.name()
            self.setMaskColor()
            self.setLabelColor(self.widgetForegroundColorHover, color)

    def setPushButtonBackgroundColorPressed(self):
        color = QColorDialog.getColor(QColor(config.widgetBackgroundColorPressed), self)
        if color.isValid():
            config.widgetBackgroundColorPressed = color.name()
            self.setMaskColor()
            self.setLabelColor(self.widgetBackgroundColorPressed, color)

    def setPushButtonForegroundColorPressed(self):
        color = QColorDialog.getColor(QColor(config.widgetForegroundColorPressed), self)
        if color.isValid():
            config.widgetForegroundColorPressed = color.name()
            self.setMaskColor()
            self.setLabelColor(self.widgetForegroundColorPressed, color)

    def changeActiveVerseColour(self):
        color = QColorDialog.getColor(QColor(config.activeVerseColourDark if config.theme in ("dark", "night") else config.activeVerseColourLight), self)
        if color.isValid():
            self.setLabelColor(self.activeVerseColour, color)
            colorName = color.name()
            if config.theme in ("dark", "night"):
                config.activeVerseColourDark = colorName
            else:
                config.activeVerseColourLight = colorName
            self.parent.reloadCurrentRecord(True)

    def changeTextSelectionColor(self):
        color = QColorDialog.getColor(QColor(config.textSelectionColor), self)
        if color.isValid():
            self.setLabelColor(self.textSelectionColor, color)
            config.textSelectionColor = color.name()
            self.parent.reloadCurrentRecord(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    dialog = MaterialColorDialog()
    sys.exit(dialog.exec_())
