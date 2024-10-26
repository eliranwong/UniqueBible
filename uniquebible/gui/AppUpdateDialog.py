import sys
from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout
else:
    from qtpy.QtWidgets import QApplication, QDialog, QDialogButtonBox, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout
from uniquebible.util.DateUtil import DateUtil
from uniquebible.util.LanguageUtil import LanguageUtil
from uniquebible.util.TextUtil import TextUtil
from uniquebible.util.UpdateUtil import UpdateUtil


class AppUpdateDialog(QDialog):

    def __init__(self, parent):
        super(AppUpdateDialog, self).__init__()

        self.parent = parent
        self.setWindowTitle(config.thisTranslation["App_Updater"])
        self.layout = QVBoxLayout()

        self.latestVersion = UpdateUtil.getLatestVersion()
        self.currentVersion = UpdateUtil.getCurrentVersion()

        if not config.internet:
            error = QLabel(config.thisTranslation["Could_not_connect_to_internet"])
            error.setStyleSheet("color: rgb(253, 128, 8);")
            self.layout.addWidget(error)
        else:
            if UpdateUtil.currentIsLatest(self.currentVersion, self.latestVersion):
                self.uptodate = True
            else:
                self.uptodate = False

            if not self.uptodate:
                self.layout.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["Latest_version"], self.latestVersion)))
            self.layout.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["Current_version"], self.currentVersion)))

            self.updateNowButton = QPushButton(config.thisTranslation["Update_now"])
            self.updateNowButton.setEnabled(True)
            self.updateNowButton.clicked.connect(self.updateNow)
            if self.uptodate:
                ubaUptodate = QLabel(config.thisTranslation["UBA_is_uptodate"])
                if config.theme in ("dark", "night"):
                    ubaUptodate.setStyleSheet("color: green;")
                else:
                    ubaUptodate.setStyleSheet("color: blue;")
                self.layout.addWidget(ubaUptodate)
            else:
                self.layout.addWidget(self.updateNowButton)

        self.layout.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["Last_check"],
            DateUtil.formattedLocalDate(UpdateUtil.lastAppUpdateCheckDateObject()))))
        self.layout.addWidget(QLabel("{0}: {1}".format(config.thisTranslation["Next_check"],
            DateUtil.formattedLocalDate(
                DateUtil.addDays(UpdateUtil.lastAppUpdateCheckDateObject(), int(config.daysElapseForNextAppUpdateCheck)
                )))))

        row = QHBoxLayout()
        row.addWidget(QLabel("{0}:".format(config.thisTranslation["Days_between_checks"])))
        self.daysInput = QLineEdit()
        self.daysInput.setText(str(config.daysElapseForNextAppUpdateCheck))
        self.daysInput.setMaxLength(3)
        self.daysInput.setMaximumWidth(60)
        row.addWidget(self.daysInput)
        self.layout.addLayout(row)

        buttons = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(buttons)
        self.buttonBox.accepted.connect(self.setDaysElapse)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

        if config.internet:
            self.updateNowButton.setFocus()

            if self.uptodate:
                self.daysInput.setFocus()
            else:
                # self.setTabOrder(self.updateNowButton, self.daysInput)
                # self.setTabOrder(self.daysInput, self.updateNowButton)
                self.updateNowButton.setFocus()

    def updateNow(self):
        return None # remove old way of update
        debug = False
        self.updateNowButton.setText(config.thisTranslation["Updating"])
        self.updateNowButton.setEnabled(False)
        UpdateUtil.updateUniqueBibleApp(self.parent, debug)
        self.close()

    def setDaysElapse(self):
        digits = TextUtil.getDigits(self.daysInput.text())
        if digits == '':
            digits = '0'
        config.daysElapseForNextAppUpdateCheck = digits


if __name__ == '__main__':
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    config.theme = 'default'
    app = QApplication(sys.argv)
    window = AppUpdateDialog(None)
    window.exec_()