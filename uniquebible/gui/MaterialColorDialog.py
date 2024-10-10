import sys, pprint, os
from uniquebible import config
import webbrowser

from uniquebible.util.ConfigUtil import ConfigUtil

if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QLabel, QPushButton, QFrame, QDialog, QGridLayout, QColorDialog, QApplication, \
    QFileDialog, QDialogButtonBox
    from PySide6.QtGui import QColor, QPalette
else:
    from qtpy.QtWidgets import QLabel, QPushButton, QFrame, QDialog, QGridLayout, QColorDialog, QApplication, \
        QFileDialog, QDialogButtonBox
    from qtpy.QtGui import QColor, QPalette
from uniquebible.util.TextUtil import TextUtil

class MaterialColorDialog(QDialog):

    def __init__(self, parent=None):
        super(MaterialColorDialog, self).__init__(parent)
        self.parent = parent

        frameStyle = QFrame.Sunken | QFrame.Panel

        self.widgetBackgroundColor = QLabel()
        self.widgetBackgroundColor.setFrameStyle(frameStyle)
        self.widgetBackgroundColorButton = QPushButton(TextUtil.formatConfigLabel("widgetBackgroundColor"))
        self.widgetBackgroundColorButton.clicked.connect(self.setPushButtonBackgroundColor)

        self.widgetForegroundColor = QLabel()
        self.widgetForegroundColor.setFrameStyle(frameStyle)
        self.widgetForegroundColorButton = QPushButton(TextUtil.formatConfigLabel("widgetForegroundColor"))
        self.widgetForegroundColorButton.clicked.connect(self.setPushButtonForegroundColor)

        self.widgetBackgroundColorHover = QLabel()
        self.widgetBackgroundColorHover.setFrameStyle(frameStyle)
        self.widgetBackgroundColorHoverButton = QPushButton(TextUtil.formatConfigLabel("widgetBackgroundColorHover"))
        self.widgetBackgroundColorHoverButton.clicked.connect(self.setPushButtonBackgroundColorHover)

        self.widgetForegroundColorHover = QLabel()
        self.widgetForegroundColorHover.setFrameStyle(frameStyle)
        self.widgetForegroundColorHoverButton = QPushButton(TextUtil.formatConfigLabel("widgetForegroundColorHover"))
        self.widgetForegroundColorHoverButton.clicked.connect(self.setPushButtonForegroundColorHover)

        self.widgetBackgroundColorPressed = QLabel()
        self.widgetBackgroundColorPressed.setFrameStyle(frameStyle)
        self.widgetBackgroundColorPressedButton = QPushButton(TextUtil.formatConfigLabel("widgetBackgroundColorPressed"))
        self.widgetBackgroundColorPressedButton.clicked.connect(self.setPushButtonBackgroundColorPressed)

        self.widgetForegroundColorPressed = QLabel()
        self.widgetForegroundColorPressed.setFrameStyle(frameStyle)
        self.widgetForegroundColorPressedButton = QPushButton(TextUtil.formatConfigLabel("widgetForegroundColorPressed"))
        self.widgetForegroundColorPressedButton.clicked.connect(self.setPushButtonForegroundColorPressed)

        self.textColour = QLabel()
        self.textColour.setFrameStyle(frameStyle)
        label = TextUtil.formatConfigLabel("darkThemeTextColor" if config.theme in ("dark", "night") else "lightThemeTextColor")
        self.textColourButton = QPushButton(label)
        self.textColourButton.clicked.connect(lambda: self.changeTextColour(True))

        self.activeVerseColour = QLabel()
        self.activeVerseColour.setFrameStyle(frameStyle)
        label = TextUtil.formatConfigLabel("darkThemeActiveVerseColor" if config.theme in ("dark", "night") else "lightThemeActiveVerseColor")
        self.activeVerseColourButton = QPushButton(label)
        self.activeVerseColourButton.clicked.connect(lambda: self.changeActiveVerseColour(True))

#        self.textSelectionColor = QLabel()
#        self.textSelectionColor.setFrameStyle(frameStyle)
#        self.textSelectionColorButton = QPushButton(TextUtil.formatConfigLabel("textSelectionColor"))
#        self.textSelectionColorButton.clicked.connect(self.changeTextSelectionColor)

        self.saveButton = QPushButton(config.thisTranslation["export"])
        self.saveButton.clicked.connect(self.openSaveAsDialog)
        self.loadButton = QPushButton(config.thisTranslation["import"])
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

        layout.addWidget(self.textColourButton, 6, 0)
        layout.addWidget(self.textColour, 6, 1)
        layout.addWidget(self.activeVerseColourButton, 7, 0)
        layout.addWidget(self.activeVerseColour, 7, 1)
        #layout.addWidget(self.textSelectionColorButton, 8, 0)
        #layout.addWidget(self.textSelectionColor, 8, 1)

        layout.addWidget(self.saveButton, 8, 0)
        layout.addWidget(self.loadButton, 8, 1)

        layout.addWidget(self.defaultButton, 9, 0)
        layout.addWidget(self.aboutButton, 9, 1)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.accepted.connect(self.saveColors)
        layout.addWidget(self.buttonBox, 10, 1)

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
                os.getcwd(),
                "UniqueBible.app Color Settings (*.color)", "", options)
        if fileName:
            ConfigUtil.loadColorConfig(fileName)
            self.setConfigColor()
            self.saveColors()
            self.parent.setTheme(config.theme, setColours=True)
            self.parent.reloadCurrentRecord(True)

    def openSaveAsDialog(self):
        defaultName = os.path.join(os.getcwd(), "uba.color")
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
            ("config.theme", config.theme),
            ("config.maskMaterialIconColor", config.maskMaterialIconColor),
            ("config.maskMaterialIconBackground", config.maskMaterialIconBackground),
            ("config.widgetBackgroundColor", config.widgetBackgroundColor),
            ("config.widgetForegroundColor", config.widgetForegroundColor),
            ("config.widgetBackgroundColorHover", config.widgetBackgroundColorHover),
            ("config.widgetForegroundColorHover", config.widgetForegroundColorHover),
            ("config.widgetBackgroundColorPressed", config.widgetBackgroundColorPressed),
            ("config.widgetForegroundColorPressed", config.widgetForegroundColorPressed),
            ("config.lightThemeTextColor", config.lightThemeTextColor),
            ("config.darkThemeTextColor", config.darkThemeTextColor),
            ("config.lightThemeActiveVerseColor", config.lightThemeActiveVerseColor),
            ("config.darkThemeActiveVerseColor", config.darkThemeActiveVerseColor),
            #("config.textSelectionColor", config.textSelectionColor),
        )
        with open(fileName, "w", encoding="utf-8") as fileObj:
            for name, value in data:
                fileObj.write("{0} = {1}\n".format(name, pprint.pformat(value)))

    def setDefault(self):
        self.parent.setColours()
        self.saveColors()
        self.parent.setTheme(config.theme)
        self.setConfigColor()

    def setConfigColor(self):
        self.setLabelColor(self.widgetBackgroundColor, QColor(config.widgetBackgroundColor))
        self.setLabelColor(self.widgetForegroundColor, QColor(config.widgetForegroundColor))
        self.setLabelColor(self.widgetBackgroundColorHover, QColor(config.widgetBackgroundColorHover))
        self.setLabelColor(self.widgetForegroundColorHover, QColor(config.widgetForegroundColorHover))
        self.setLabelColor(self.widgetBackgroundColorPressed, QColor(config.widgetBackgroundColorPressed))
        self.setLabelColor(self.widgetForegroundColorPressed, QColor(config.widgetForegroundColorPressed))
        self.setLabelColor(self.textColour, QColor(config.darkThemeTextColor if config.theme in ("dark", "night") else config.lightThemeTextColor))
        self.setLabelColor(self.activeVerseColour, QColor(config.darkThemeActiveVerseColor if config.theme in ("dark", "night") else config.lightThemeActiveVerseColor))
        #self.setLabelColor(self.textSelectionColor, QColor(config.textSelectionColor))

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

    def changeTextColour(self, reload=True):
        color = QColorDialog.getColor(QColor(config.darkThemeTextColor if config.theme in ("dark", "night") else config.lightThemeTextColor), self)
        if color.isValid():
            self.setLabelColor(self.textColour, color)
            colorName = color.name()
            if config.theme in ("dark", "night"):
                config.darkThemeTextColor = colorName
            else:
                config.lightThemeTextColor = colorName
            if reload:
                self.saveColors()
                self.parent.reloadCurrentRecord(True)
                self.parent.resetUI()

    def changeActiveVerseColour(self, reload=True):
        color = QColorDialog.getColor(QColor(config.darkThemeActiveVerseColor if config.theme in ("dark", "night") else config.lightThemeActiveVerseColor), self)
        if color.isValid():
            self.setLabelColor(self.activeVerseColour, color)
            colorName = color.name()
            if config.theme in ("dark", "night"):
                config.darkThemeActiveVerseColor = colorName
            else:
                config.lightThemeActiveVerseColor = colorName
            if reload:
                self.saveColors()
                self.parent.reloadCurrentRecord(True)

#    def changeTextSelectionColor(self):
#        color = QColorDialog.getColor(QColor(config.textSelectionColor), self)
#        if color.isValid():
#            self.setLabelColor(self.textSelectionColor, color)
#            config.textSelectionColor = color.name()
#            self.parent.reloadCurrentRecord(True)

    def saveColors(self):
        fileName = ConfigUtil.getColorConfigFilename()
        self.saveData(fileName)


if __name__ == '__main__':
    from uniquebible.util.LanguageUtil import LanguageUtil

    ConfigUtil.setup()
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")

    app = QApplication(sys.argv)
    dialog = MaterialColorDialog()
    sys.exit(dialog.exec_())
