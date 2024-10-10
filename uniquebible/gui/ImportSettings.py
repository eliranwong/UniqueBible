from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QGridLayout, QPushButton, QDialog, QLabel, QCheckBox
else:
    from qtpy.QtWidgets import QGridLayout, QPushButton, QDialog, QLabel, QCheckBox

class ImportSettings(QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        #self.setModal(True)

        self.setWindowTitle(config.thisTranslation["menu8_settings"])

        self.setupLayout()

    def setupLayout(self):
        titleBibles = QLabel(config.thisTranslation["menu5_bible"])

        self.linebreak = QCheckBox()
        self.linebreak.setText(config.thisTranslation["import_linebreak"])
        self.linebreak.setChecked(config.importAddVerseLinebreak)

        self.stripStrNo = QCheckBox()
        self.stripStrNo.setText(config.thisTranslation["import_strongNo"])
        self.stripStrNo.setChecked(config.importDoNotStripStrongNo)

        self.stripMorphCode = QCheckBox()
        self.stripMorphCode.setText(config.thisTranslation["import_morphCode"])
        self.stripMorphCode.setChecked(config.importDoNotStripMorphCode)

        self.importRtlOT = QCheckBox()
        self.importRtlOT.setText(config.thisTranslation["import_rtl"])
        self.importRtlOT.setChecked(config.importRtlOT)

        self.importInterlinear = QCheckBox()
        self.importInterlinear.setText(config.thisTranslation["import_interlinear"])
        self.importInterlinear.setChecked(config.importInterlinear)

        saveButton = QPushButton(config.thisTranslation["note_save"])
        saveButton.clicked.connect(self.saveSettings)

        cancelButton = QPushButton(config.thisTranslation["message_cancel"])
        cancelButton.clicked.connect(self.close)

        self.layout = QGridLayout()
        self.layout.addWidget(titleBibles, 0, 0)
        self.layout.addWidget(self.linebreak, 1, 0)
        self.layout.addWidget(self.stripStrNo, 2, 0)
        self.layout.addWidget(self.stripMorphCode, 3, 0)
        self.layout.addWidget(self.importRtlOT, 4, 0)
        self.layout.addWidget(self.importInterlinear, 5, 0)
        self.layout.addWidget(saveButton, 6, 0)
        self.layout.addWidget(cancelButton, 7, 0)
        self.setLayout(self.layout)

    def saveSettings(self):
        if self.linebreak.isChecked():
            config.importAddVerseLinebreak = True
        else:
            config.importAddVerseLinebreak = False

        if self.stripStrNo.isChecked():
            config.importDoNotStripStrongNo = True
        else:
            config.importDoNotStripStrongNo = False

        if self.stripMorphCode.isChecked():
            config.importDoNotStripMorphCode = True
        else:
            config.importDoNotStripMorphCode = False

        if self.importRtlOT.isChecked():
            config.importRtlOT = True
        else:
            config.importRtlOT = False

        if self.importInterlinear.isChecked():
            config.importInterlinear = True
        else:
            config.importInterlinear = False

        self.close()
