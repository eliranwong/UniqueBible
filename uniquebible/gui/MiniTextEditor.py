from uniquebible import config
import re, os
import uniquebible.shortcut as sc
from datetime import datetime
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtGui import QKeySequence, QShortcut
    from PySide6.QtWidgets import QMainWindow, QTextEdit, QToolBar, QFileDialog, QInputDialog, QLineEdit
else:
    from qtpy.QtCore import Qt, QTimer
    from qtpy.QtGui import QKeySequence
    from qtpy.QtWidgets import QMainWindow, QTextEdit, QToolBar, QFileDialog, QInputDialog, QLineEdit, QShortcut


class MiniTextEditor(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.wsName = "editor"
        self.wsFilename = ""
        self.html = True
        self.setupLayout()
        self.setupKeyboardShortcuts()
        # auto save changes
        self.lastChangeTime = datetime.now()
        self.editor.textChanged.connect(self.autoSaveTimer)
        self.savingInProgress = False

    def setupKeyboardShortcuts(self):
        if hasattr(self.parent, "name") and self.parent.name == "workspace":
            shortcut = QShortcut(QKeySequence(sc.swapWorkspaceWithMainWindow), self)
            shortcut.activated.connect(self.parent.parent.swapWorkspaceWithMainWindow)

    def setupLayout(self):
        menuBar = self.getMenuBar()
        # Use the following line is QWidget is used instead of QMainWindow
        #layout.addWidget(menuBar)
        self.addToolBar(menuBar)
        self.editor = QTextEdit()
        # Use the following line is QWidget is used instead of QMainWindow
        #layout = QVBoxLayout()
        #layout.addWidget(self.editor)
        #self.setLayout(layout)
        self.setCentralWidget(self.editor)

    def setHtml(self, html):
        self.editor.setHtml(html)

    def searchText(self, searchString):
        if searchString:
            cursor = self.editor.document().find(searchString, self.editor.textCursor())
        if cursor:
            self.editor.setTextCursor(cursor)
        self.hide()
        self.show()

    def getMenuBar(self):

        menuBar = QToolBar()
        menuBar.setWindowTitle(config.thisTranslation["workspace"])
        menuBar.setContextMenuPolicy(Qt.PreventContextMenu)

        icon = "material/editor/title/materialiconsoutlined/48dp/2x/outline_title_black_48dp.png"
        self.parent.parent.addMaterialIconButton("changeWindowTitle", icon, lambda: self.changeWindowTitle(self.windowTitle()), menuBar)

        #icon = "material/content/save/materialiconsoutlined/48dp/2x/outline_save_black_48dp.png"
        #self.parent.parent.addMaterialIconButton("note_save", icon, self.saveWsFile, menuBar)
        icon = "material/content/save_as/materialiconsoutlined/48dp/2x/outline_save_as_black_48dp.png"
        self.parent.parent.addMaterialIconButton("note_saveAs", icon, self.openSaveAsDialog, menuBar)

        icon = "material/communication/swap_calls/materialiconsoutlined/48dp/2x/outline_swap_calls_black_48dp.png"
        self.parent.parent.addMaterialIconButton("note_mode", icon, self.switchMode, menuBar)

        #menuBar.addSeparator()

        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setClearButtonEnabled(True)
        self.searchLineEdit.setToolTip(config.thisTranslation["menu5_search"])
        self.searchLineEdit.setMaximumWidth(400)
        self.searchLineEdit.returnPressed.connect(self.searchLineEntered)
        menuBar.addWidget(self.searchLineEdit)

        #menuBar.addSeparator()

        icon = "material/action/preview/materialiconsoutlined/48dp/2x/outline_preview_black_48dp.png"
        self.parent.parent.addMaterialIconButton("openInReader", icon, self.openInReader, menuBar)

        return menuBar

    def openInReader(self):
        html = self.editor.toHtml() if self.html else self.editor.toPlainText()
        windowTitle = self.windowTitle()
        self.parent.addHtmlContent(html, False, windowTitle)

    def searchLineEntered(self):
        searchString = self.searchLineEdit.text()
        if searchString:
            cursor = self.editor.document().find(searchString, self.editor.textCursor())
        if cursor:
            self.editor.setTextCursor(cursor)
        self.hide()
        self.show()

    # switching between "rich" & "plain" mode
    def switchMode(self):
        if self.html:
            note = self.editor.toHtml()
            note = re.sub("<body style={0}[ ]*?font-family:[ ]*?'[^']*?';[ ]*?font-size:[ ]*?[0-9]+?pt;".format('"'), "<body style={0}font-family:'{1}'; font-size:{2}pt;".format('"', config.font, config.fontSize), note)
            self.editor.setPlainText(note)
            self.html = False
        else:
            note = self.editor.toPlainText()
            self.editor.setHtml(note)
            self.html = True
        # without this hide / show command below, QTextEdit does not update the text in some devices
        self.hide()
        self.show()

    def openSaveAsDialog(self):
        defaultName = ""
        options = QFileDialog.Options()
        fileName, *_ = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                os.path.join("notes", defaultName),
                "UniqueBible.app Note Files (*.uba);;HTML Files (*.html);;HTM Files (*.htm);;All Files (*)", "", options)
        if fileName:
            if not os.path.basename(fileName).lower().endswith(".uba"):
                fileName = fileName + ".uba"
            self.saveHtml(fileName)

    def autoSaveTimer(self):
        self.lastChangeTime = datetime.now()
        lastChangeTime = self.lastChangeTime
        # Run auto-save 2 seconds after active changes in text entry were made.
        QTimer.singleShot(2000, lambda: self.autoSaveChanges(lastChangeTime))

    def autoSaveChanges(self, lastChangeTime):
        if lastChangeTime == self.lastChangeTime and self.parent.isVisible():
            #print("Save changes now")
            self.saveWsFile()

    def saveWsFile(self):
        if self.wsFilename:
            self.saveHtml(self.wsFilename)
            self.statusBar().showMessage(config.thisTranslation["saved"], 2000)

    def saveHtml(self, fileName):
        if not self.savingInProgress:
            self.savingInProgress = True
            if self.html:
                note = self.editor.toHtml()
            else:
                note = self.editor.toPlainText()
            note = self.fixNoteFont(note)
            with open(fileName, "w", encoding="utf-8") as fileObj:
                fileObj.write(note)
            self.savingInProgress = False

    def changeWindowTitle(self, windowTitle=""):
        if self.parent is config.mainWindow.ws:
            windowTitle, ok = QInputDialog.getText(self, config.thisTranslation["changeWindowTitle"],
                    config.thisTranslation["enter_text_here"], QLineEdit.Normal,
                    windowTitle)
            if ok and windowTitle:
                self.setWindowTitle(windowTitle)
                self.parent.saveWorkspace()

    def fixNoteFont(self, note):
        note = re.sub("<body style={0}[ ]*?font-family:[ ]*?'[^']*?';[ ]*?font-size:[ ]*?[0-9]+?pt;".format('"'), "<body style={0}font-family:'{1}'; font-size:{2}pt;".format('"', config.font, config.fontSize), note)
        if not config.includeStrictDocTypeInNote:
            note = re.sub("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n""", "", note)
        return note
