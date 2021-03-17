import config
from qtpy.QtWidgets import QWidget

class ConfigurePresentationWindow(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        # set title
        self.setWindowTitle("Configure Presentation")
        # set variables
        self.setupVariables()
        # setup interface
        self.setupUI()

    def setupVariables(self):
        pass

    def setupUI(self):

        from qtpy.QtCore import Qt
        from qtpy.QtWidgets import QHBoxLayout, QFormLayout, QSlider, QPushButton, QPlainTextEdit, QCheckBox

        layout = QHBoxLayout()

        layout1 = QFormLayout()

        self.fontsizeslider = QSlider(Qt.Horizontal)
        self.fontsizeslider.setMinimum(1)
        self.fontsizeslider.setMaximum(12)
        self.fontsizeslider.setTickInterval(2)
        self.fontsizeslider.setSingleStep(2)
        self.fontsizeslider.setValue(config.presentationFontSize / 0.5)
        self.fontsizeslider.setToolTip(str(config.presentationFontSize))
        self.fontsizeslider.valueChanged.connect(self.presentationFontSizeChanged)
        layout1.addRow("Font Size", self.fontsizeslider)

        self.changecolorbutton = QPushButton()
        buttonStyle = "QPushButton {0}background-color: {2}; color: {3};{1}".format("{", "}", config.presentationColorOnDarkTheme if config.theme == "dark" else config.presentationColorOnLightTheme, "white" if config.theme == "dark" else "black")
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

        checkbox = QCheckBox()
        checkbox.setText("")
        checkbox.setChecked(config.presentationParser)
        checkbox.stateChanged.connect(self.presentationParserChanged)
        checkbox.setToolTip("Parse bible verse reference in the entered text")
        layout1.addRow("Bible Reference", checkbox)

        layout2 = QFormLayout()

        self.textEntry = QPlainTextEdit("John 3:16; Rm 5:8")
        layout2.addWidget(self.textEntry)

        button = QPushButton("Presentation")
        button.setToolTip("Go to Presentation")
        button.clicked.connect(self.goToPresentation)
        layout2.addWidget(button)

        layout.addLayout(layout1)
        layout.addLayout(layout2)
        self.setLayout(layout)

    def goToPresentation(self):
        command = "SCREEN:::{0}".format(self.textEntry.toPlainText())
        self.parent.runTextCommand(command)

    def changeColor(self):

        from qtpy.QtGui import QColor
        from qtpy.QtWidgets import QColorDialog

        color = QColorDialog.getColor(QColor(config.presentationColorOnDarkTheme if config.theme == "dark" else config.presentationColorOnLightTheme), self)
        if color.isValid():
            colorName = color.name()
            if config.theme == "dark":
                config.presentationColorOnDarkTheme = colorName
            else:
                config.presentationColorOnLightTheme = colorName
            buttonStyle = "QPushButton {0}background-color: {2}; color: {3};{1}".format("{", "}", colorName, "white" if config.theme == "dark" else "black")
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


config.mainWindow.configurePresentationWindow = ConfigurePresentationWindow(config.mainWindow)
config.mainWindow.configurePresentationWindow.show()
