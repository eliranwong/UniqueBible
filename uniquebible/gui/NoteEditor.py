import os, re, base64, webbrowser, markdown
from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QIcon, QTextCursor, QFont, QGuiApplication
    from PySide6.QtPrintSupport import QPrinter, QPrintDialog
    from PySide6.QtWidgets import QMessageBox, QComboBox, QInputDialog, QLineEdit, QMainWindow, QPushButton, QToolBar, QDialog, QFileDialog, QTextEdit, QFontDialog, QColorDialog
else:
    from qtpy.QtCore import Qt
    from qtpy.QtGui import QIcon, QTextCursor, QFont, QGuiApplication
    from qtpy.QtPrintSupport import QPrinter, QPrintDialog
    from qtpy.QtWidgets import QMessageBox, QComboBox, QInputDialog, QLineEdit, QMainWindow, QPushButton, QToolBar, QDialog, QFileDialog, QTextEdit, QFontDialog, QColorDialog
from uniquebible.util.NoteService import NoteService
from uniquebible.util.Translator import Translator
from uniquebible.db.JournalSqlite import JournalSqlite


class NoteEditorWindow(QMainWindow):

    def __init__(self, parent, noteType, noteFileName="", b=None, c=None, v=None, year=None, month=None, day=None):
        super().__init__()
        # Five noteType = "journal", "file", "book", "chapter", "verse"
        self.parent, self.noteType, self.noteFileName, self.b, self.c, self.v, self.year, self.month, self.day = parent, noteType, noteFileName, b, c, v, year, month, day
        if self.noteType in ("book", "chapter", "verse") and v is None:
            self.b, self.c, self.v = config.studyB, config.studyC, config.studyV

        # default - "Rich" mode for editing
        self.html = True
        # default - text is not modified; no need for saving new content
        self.parent.parent.noteSaved = True
        #config.noteOpened = True
        config.lastOpenedNote = (noteType, b, c, v, year, month, day)

        # specify window size
        self.resizeWindow(2/3, 2/3)

        # setup interface
        self.setupMenuBar()
        self.addToolBarBreak()
        self.setupToolBar()
        if config.hideNoteEditorStyleToolbar:
            self.toolBar.hide()
        self.addToolBarBreak()
        self.setupTextUtility()
        if config.hideNoteEditorTextUtility:
            self.ttsToolbar.hide()
            self.translateToolbar.hide()
        self.setupLayout()

        # display content when first launched
        self.displayInitialContent()
        self.editor.setFocus()

        # specify window title
        self.updateWindowTitle()

    def resetVariables(self):
        self.parent.parent.noteSaved = True
        self.noteType, self.noteFileName, self.b, self.c, self.v, self.year, self.month, self.day = None, None, None, None, None, None, None, None

    # re-implementing close event, when users close this widget
    def closeEvent(self, event):
        if self.parent.parent.noteSaved:
            #config.noteOpened = False
            event.accept()
            if config.lastOpenedNote and config.openBibleNoteAfterEditorClosed:
                #if config.lastOpenedNote[0] == "file":
                #    self.parent.parent.externalFileButtonClicked()
                if config.lastOpenedNote[0] == "book":
                    self.parent.parent.openStudyBookNote()
                elif config.lastOpenedNote[0] == "chapter":
                    self.parent.parent.openStudyChapterNote()
                elif config.lastOpenedNote[0] == "verse":
                    self.parent.parent.openStudyVerseNote()
        else:
            if self.parent.parent.warningNotSaved():
                self.parent.parent.noteSaved = True
                #config.noteOpened = False
                event.accept()
            else:
                self.parent.parent.bringToForeground(self)
                event.ignore()

    # re-implement keyPressEvent, control+S for saving file
    def keyPressEvent(self, event):
        keys = {
            Qt.Key_O: self.openFileDialog,
            Qt.Key_S: self.saveNote,
            Qt.Key_B: self.format_bold,
            Qt.Key_I: self.format_italic,
            Qt.Key_U: self.format_underline,
            Qt.Key_M: self.format_custom,
            Qt.Key_D: self.format_clear,
            Qt.Key_F: self.focusSearchField,
        }
        key = event.key()
        if event.modifiers() == Qt.ControlModifier and key in keys:
            keys[key]()

    # window appearance
    def resizeWindow(self, widthFactor, heightFactor):
        #availableGeometry = QGuiApplication.instance().desktop().availableGeometry()
        availableGeometry = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(int(availableGeometry.width() * widthFactor), int(availableGeometry.height() * heightFactor))

    def updateWindowTitle(self):
        if self.noteType == "journal":
            title = "{0}-{1}-{2}".format(self.year, self.month, self.day)
        elif self.noteType == "file":
            if self.noteFileName:
                *_, title = os.path.split(self.noteFileName)
            else:
                title = "NEW"
        else:
            title = self.parent.parent.bcvToVerseReference(self.b, self.c, self.v)
            if self.noteType == "book":
                title, *_ = title.split(" ")            
            elif self.noteType == "chapter":
                title, *_ = title.split(":")
        mode = {True: "rich", False: "plain"}
        notModified = {True: "", False: " [modified]"}
        self.parent.setWindowTitle("Note Editor ({1} mode) - {0}{2}".format(title, mode[self.html], notModified[self.parent.parent.noteSaved]))

    # switching between "rich" & "plain" mode
    def switchMode(self):
        if self.html:
            note = self.editor.toHtml()
            note = re.sub("<body style={0}[ ]*?font-family:[ ]*?'[^']*?';[ ]*?font-size:[ ]*?[0-9]+?pt;".format('"'), "<body style={0}font-family:'{1}'; font-size:{2}pt;".format('"', config.font, config.fontSize), note)
            self.editor.setPlainText(note)
            self.html = False
            self.updateWindowTitle()
        else:
            note = self.editor.toPlainText()
            self.editor.setHtml(note)
            self.html = True
            self.updateWindowTitle()
        # without this hide / show command below, QTextEdit does not update the text in some devices
        self.hide()
        self.show()

    def setupMenuBar(self):
        if config.menuLayout == "material":
            self.setupMenuBarStandardIconSizeMaterial()
        elif config.toolBarIconFullSize:
            self.setupMenuBarFullIconSize()
        else:
            self.setupMenuBarStandardIconSize()

    def setupMenuBarStandardIconSize(self):

        self.menuBar = QToolBar()
        self.menuBar.setWindowTitle(config.thisTranslation["note_title"])
        self.menuBar.setContextMenuPolicy(Qt.PreventContextMenu)
        # In QWidget, self.menuBar is treated as the menubar without the following line
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(self.menuBar)

        newButton = QPushButton()
        #newButton.setToolTip("{0}\n[Ctrl/Cmd + N]".format(config.thisTranslation["menu7_create"]))
        newButton.setToolTip(config.thisTranslation["menu7_create"])
        newButtonFile = os.path.join("htmlResources", "newfile.png")
        newButton.setIcon(QIcon(newButtonFile))
        newButton.clicked.connect(self.newNoteFile)
        self.menuBar.addWidget(newButton)

        openButton = QPushButton()
        #openButton.setToolTip("{0}\n[Ctrl/Cmd + O]".format(config.thisTranslation["menu7_open"]))
        openButton.setToolTip(config.thisTranslation["menu7_open"])
        openButtonFile = os.path.join("htmlResources", "open.png")
        openButton.setIcon(QIcon(openButtonFile))
        openButton.clicked.connect(self.openFileDialog)
        self.menuBar.addWidget(openButton)

        self.menuBar.addSeparator()

        saveButton = QPushButton()
        saveButton.setToolTip("{0}\n[Ctrl/Cmd + S]".format(config.thisTranslation["note_save"]))
        saveButtonFile = os.path.join("htmlResources", "save.png")
        saveButton.setIcon(QIcon(saveButtonFile))
        saveButton.clicked.connect(self.saveNote)
        self.menuBar.addWidget(saveButton)

        saveAsButton = QPushButton()
        saveAsButton.setToolTip(config.thisTranslation["note_saveAs"])
        saveAsButtonFile = os.path.join("htmlResources", "saveas.png")
        saveAsButton.setIcon(QIcon(saveAsButtonFile))
        saveAsButton.clicked.connect(self.openSaveAsDialog)
        self.menuBar.addWidget(saveAsButton)

        self.menuBar.addSeparator()

        toolBarButton = QPushButton()
        toolBarButton.setToolTip(config.thisTranslation["note_print"])
        toolBarButtonFile = os.path.join("htmlResources", "print.png")
        toolBarButton.setIcon(QIcon(toolBarButtonFile))
        toolBarButton.clicked.connect(self.printNote)
        self.menuBar.addWidget(toolBarButton)

        self.menuBar.addSeparator()

        switchButton = QPushButton()
        switchButton.setToolTip(config.thisTranslation["note_mode"])
        switchButtonFile = os.path.join("htmlResources", "switch.png")
        switchButton.setIcon(QIcon(switchButtonFile))
        switchButton.clicked.connect(self.switchMode)
        self.menuBar.addWidget(switchButton)

        self.menuBar.addSeparator()

#        decreaseFontSizeButton = QPushButton()
#        decreaseFontSizeButton.setToolTip(config.thisTranslation["menu2_smaller"])
#        decreaseFontSizeButtonFile = os.path.join("htmlResources", "fontMinus.png")
#        decreaseFontSizeButton.setIcon(QIcon(decreaseFontSizeButtonFile))
#        decreaseFontSizeButton.clicked.connect(self.decreaseNoteEditorFontSize)
#        self.menuBar.addWidget(decreaseFontSizeButton)
#
#        increaseFontSizeButton = QPushButton()
#        increaseFontSizeButton.setToolTip(config.thisTranslation["menu2_larger"])
#        increaseFontSizeButtonFile = os.path.join("htmlResources", "fontPlus.png")
#        increaseFontSizeButton.setIcon(QIcon(increaseFontSizeButtonFile))
#        increaseFontSizeButton.clicked.connect(self.increaseNoteEditorFontSize)
#        self.menuBar.addWidget(increaseFontSizeButton)

#        self.menuBar.addSeparator()

        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setClearButtonEnabled(True)
        self.searchLineEdit.setToolTip(config.thisTranslation["menu5_search"])
        self.searchLineEdit.setMaximumWidth(400)
        self.searchLineEdit.returnPressed.connect(self.searchLineEntered)
        self.menuBar.addWidget(self.searchLineEdit)

        self.menuBar.addSeparator()

        toolBarButton = QPushButton()
        toolBarButton.setToolTip(config.thisTranslation["note_toolbar"])
        toolBarButtonFile = os.path.join("htmlResources", "toolbar.png")
        toolBarButton.setIcon(QIcon(toolBarButtonFile))
        toolBarButton.clicked.connect(self.toggleToolbar)
        self.menuBar.addWidget(toolBarButton)

        toolBarButton = QPushButton()
        toolBarButton.setToolTip(config.thisTranslation["note_textUtility"])
        toolBarButtonFile = os.path.join("htmlResources", "textUtility.png")
        toolBarButton.setIcon(QIcon(toolBarButtonFile))
        toolBarButton.clicked.connect(self.toggleTextUtility)
        self.menuBar.addWidget(toolBarButton)

        self.menuBar.addSeparator()

    def setupMenuBarStandardIconSizeMaterial(self):

        self.menuBar = QToolBar()
        self.menuBar.setWindowTitle(config.thisTranslation["note_title"])
        self.menuBar.setContextMenuPolicy(Qt.PreventContextMenu)
        # In QWidget, self.menuBar is treated as the menubar without the following line
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(self.menuBar)

        icon = "material/action/note_add/materialiconsoutlined/48dp/2x/outline_note_add_black_48dp.png"
        #toolTip = "{0}\n[Ctrl/Cmd + N]".format(config.thisTranslation["menu7_create"])
        toolTip = config.thisTranslation["menu7_create"]
        self.parent.parent.addMaterialIconButton(toolTip, icon, self.newNoteFile, self.menuBar, None, False)

        icon = "material/file/file_open/materialiconsoutlined/48dp/2x/outline_file_open_black_48dp.png"
        #toolTip = "{0}\n[Ctrl/Cmd + O]".format(config.thisTranslation["menu7_open"])
        toolTip = config.thisTranslation["menu7_open"]
        self.parent.parent.addMaterialIconButton(toolTip, icon, self.openFileDialog, self.menuBar, None, False)

        #self.menuBar.addSeparator()

        icon = "material/content/save/materialiconsoutlined/48dp/2x/outline_save_black_48dp.png"
        #toolTip = "{0}\n[Ctrl/Cmd + S]".format(config.thisTranslation["note_save"])
        toolTip = config.thisTranslation["note_save"]
        self.parent.parent.addMaterialIconButton(toolTip, icon, self.saveNote, self.menuBar, None, False)

        icon = "material/content/save_as/materialiconsoutlined/48dp/2x/outline_save_as_black_48dp.png"
        toolTip = config.thisTranslation["note_saveAs"]
        self.parent.parent.addMaterialIconButton(toolTip, icon, self.openSaveAsDialog, self.menuBar, None, False)

        #self.menuBar.addSeparator()

        icon = "material/action/preview/materialiconsoutlined/48dp/2x/outline_preview_black_48dp.png"
        toolTip = config.thisTranslation["displayOnStudyWindow"]
        self.parent.parent.addMaterialIconButton(toolTip, icon, self.readNote, self.menuBar, None, False)

        icon = "material/maps/local_printshop/materialiconsoutlined/48dp/2x/outline_local_printshop_black_48dp.png"
        toolTip = config.thisTranslation["note_print"]
        self.parent.parent.addMaterialIconButton(toolTip, icon, self.printNote, self.menuBar, None, False)

        #self.menuBar.addSeparator()

        icon = "material/communication/swap_calls/materialiconsoutlined/48dp/2x/outline_swap_calls_black_48dp.png"
        toolTip = config.thisTranslation["note_mode"]
        self.parent.parent.addMaterialIconButton(toolTip, icon, self.switchMode, self.menuBar, None, False)

        self.menuBar.addSeparator()

        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setClearButtonEnabled(True)
        self.searchLineEdit.setToolTip(config.thisTranslation["menu5_search"])
        self.searchLineEdit.setMaximumWidth(400)
        self.searchLineEdit.returnPressed.connect(self.searchLineEntered)
        self.menuBar.addWidget(self.searchLineEdit)

        self.menuBar.addSeparator()

        icon = "material/notification/more/materialiconsoutlined/48dp/2x/outline_more_black_48dp.png"
        toolTip = config.thisTranslation["note_toolbar"]
        self.parent.parent.addMaterialIconButton(toolTip, icon, self.toggleToolbar, self.menuBar, None, False)

        #icon = "material/navigation/campaign/materialiconsoutlined/48dp/2x/outline_campaign_black_48dp.png"
        #icon = "material/action/record_voice_over/materialiconsoutlined/48dp/2x/outline_record_voice_over_black_48dp.png"
        icon = "material/action/translate/materialiconsoutlined/48dp/2x/outline_translate_black_48dp.png"
        toolTip = config.thisTranslation["note_textUtility"]
        self.parent.parent.addMaterialIconButton(toolTip, icon, self.toggleTextUtility, self.menuBar, None, False)

        self.menuBar.addSeparator()

    def setupMenuBarFullIconSize(self):

        self.menuBar = QToolBar()
        self.menuBar.setWindowTitle(config.thisTranslation["note_title"])
        self.menuBar.setContextMenuPolicy(Qt.PreventContextMenu)
        # In QWidget, self.menuBar is treated as the menubar without the following line
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(self.menuBar)

        iconFile = os.path.join("htmlResources", "newfile.png")
        #self.menuBar.addAction(QIcon(iconFile), "{0}\n[Ctrl/Cmd + N]".format(config.thisTranslation["menu7_create"]), self.newNoteFile)
        self.menuBar.addAction(QIcon(iconFile), config.thisTranslation["menu7_create"], self.newNoteFile)

        iconFile = os.path.join("htmlResources", "open.png")
        self.menuBar.addAction(QIcon(iconFile), config.thisTranslation["menu7_open"], self.openFileDialog)

        self.menuBar.addSeparator()

        iconFile = os.path.join("htmlResources", "save.png")
        self.menuBar.addAction(QIcon(iconFile), config.thisTranslation["note_save"], self.saveNote)

        iconFile = os.path.join("htmlResources", "saveas.png")
        self.menuBar.addAction(QIcon(iconFile), config.thisTranslation["note_saveAs"], self.openSaveAsDialog)

        self.menuBar.addSeparator()

        iconFile = os.path.join("htmlResources", "print.png")
        self.menuBar.addAction(QIcon(iconFile), config.thisTranslation["note_print"], self.printNote)

        self.menuBar.addSeparator()

        iconFile = os.path.join("htmlResources", "switch.png")
        self.menuBar.addAction(QIcon(iconFile), config.thisTranslation["note_mode"], self.switchMode)

        self.menuBar.addSeparator()

#        iconFile = os.path.join("htmlResources", "fontMinus.png")
#        self.menuBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_smaller"], self.decreaseNoteEditorFontSize)
#
#        iconFile = os.path.join("htmlResources", "fontPlus.png")
#        self.menuBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_larger"], self.increaseNoteEditorFontSize)

#        self.menuBar.addSeparator()

        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setToolTip(config.thisTranslation["menu5_search"])
        self.searchLineEdit.setMaximumWidth(400)
        self.searchLineEdit.returnPressed.connect(self.searchLineEntered)
        self.menuBar.addWidget(self.searchLineEdit)

        self.menuBar.addSeparator()

        iconFile = os.path.join("htmlResources", "toolbar.png")
        self.menuBar.addAction(QIcon(iconFile), config.thisTranslation["note_toolbar"], self.toggleToolbar)

        iconFile = os.path.join("htmlResources", "textUtility.png")
        self.menuBar.addAction(QIcon(iconFile), config.thisTranslation["note_textUtility"], self.toggleTextUtility)

        self.menuBar.addSeparator()

    def toggleToolbar(self):
        if config.hideNoteEditorStyleToolbar:
            self.toolBar.show()
            config.hideNoteEditorStyleToolbar = False
        else:
            self.toolBar.hide()
            config.hideNoteEditorStyleToolbar = True

    def toggleTextUtility(self):
        if config.hideNoteEditorTextUtility:
            self.ttsToolbar.show()
            self.translateToolbar.show()
            config.hideNoteEditorTextUtility = False
        else:
            self.ttsToolbar.hide()
            self.translateToolbar.hide()
            config.hideNoteEditorTextUtility = True

    def readNote(self):
        html = self.editor.toHtml()
        html = self.parent.parent.fixNoteFontDisplay(html)
        html = self.parent.parent.htmlWrapper(html, True, "study", False)
        self.parent.parent.openTextOnStudyView(html, tab_title=config.thisTranslation["menu_notes"], toolTip=config.thisTranslation["menu_notes"])

    def printNote(self):
        #document = QTextDocument("Sample Page")
        document = self.editor.document()
        printer = QPrinter()

        myPrintDialog = QPrintDialog(printer, self)
        if myPrintDialog.exec_() == QDialog.Accepted:
            return document.print_(printer)

    def setupToolBar(self):
        if config.menuLayout == "material":
            self.setupToolBarStandardIconSizeMaterial()
        elif config.toolBarIconFullSize:
            self.setupToolBarFullIconSize()
        else:
            self.setupToolBarStandardIconSize()

    def setupToolBarStandardIconSizeMaterial(self):

        self.toolBar = QToolBar()
        self.toolBar.setWindowTitle(config.thisTranslation["noteTool_title"])
        self.toolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        # self.toolBar can be treated as an individual widget and positioned with a specified layout
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(self.toolBar)
        
        items = (
            ("noteTool_textFont", "material/editor/format_size/materialiconsoutlined/48dp/2x/outline_format_size_black_48dp.png", self.format_font),
            ("noteTool_textColor", "material/editor/format_color_text/materialiconsoutlined/48dp/2x/outline_format_color_text_black_48dp.png", self.format_textColor),
            ("noteTool_textBackgroundColor", "material/editor/format_color_fill/materialiconsoutlined/48dp/2x/outline_format_color_fill_black_48dp.png", self.format_textBackgroundColor),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addMaterialIconButton(toolTip, icon, action, self.toolBar)

        self.toolBar.addSeparator()

        items = (
            ("noteTool_header1", "H1", self.format_header1),
            ("noteTool_header2", "H2", self.format_header2),
            ("noteTool_header3", "H3", self.format_header3),
        )
        for item in items:
            toolTip, buttonTitle, action = item
            #toolTip, action, toolbar, button=None, translation=True)
            button = QPushButton(buttonTitle)
            button.setFixedWidth(30)
            self.parent.parent.addStandardTextButton(toolTip, action, self.toolBar, button)

        self.toolBar.addSeparator()
        
        items = (
            #("{0}\n[Ctrl/Cmd + B]".format(config.thisTranslation["noteTool_bold"]), "material/editor/format_bold/materialiconsoutlined/48dp/2x/outline_format_bold_black_48dp.png", self.format_bold),
            #("{0}\n[Ctrl/Cmd + I]".format(config.thisTranslation["noteTool_italic"]), "material/editor/format_italic/materialiconsoutlined/48dp/2x/outline_format_italic_black_48dp.png", self.format_italic),
            #("{0}\n[Ctrl/Cmd + U]".format(config.thisTranslation["noteTool_underline"]), "material/editor/format_underlined/materialiconsoutlined/48dp/2x/outline_format_underlined_black_48dp.png", self.format_underline),
            (config.thisTranslation["noteTool_bold"], "material/editor/format_bold/materialiconsoutlined/48dp/2x/outline_format_bold_black_48dp.png", self.format_bold),
            (config.thisTranslation["noteTool_italic"], "material/editor/format_italic/materialiconsoutlined/48dp/2x/outline_format_italic_black_48dp.png", self.format_italic),
            (config.thisTranslation["noteTool_underline"], "material/editor/format_underlined/materialiconsoutlined/48dp/2x/outline_format_underlined_black_48dp.png", self.format_underline),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addMaterialIconButton(toolTip, icon, action, self.toolBar, translation=False)

        self.toolBar.addSeparator()

        items = (
            ("noteTool_superscript", "material/editor/superscript/materialiconsoutlined/48dp/2x/outline_superscript_black_48dp.png", self.format_superscript),
            ("noteTool_subscript", "material/editor/subscript/materialiconsoutlined/48dp/2x/outline_subscript_black_48dp.png", self.format_subscript),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addMaterialIconButton(toolTip, icon, action, self.toolBar)

        self.toolBar.addSeparator()

        #self.parent.parent.addMaterialIconButton("{0}\n[Ctrl/Cmd + M]".format(config.thisTranslation["convertFromMarkdown"]), "material/image/auto_fix_high/materialiconsoutlined/48dp/2x/outline_auto_fix_high_black_48dp.png", self.format_custom, self.toolBar, translation=False)
        self.parent.parent.addMaterialIconButton(config.thisTranslation["convertFromMarkdown"], "material/image/auto_fix_high/materialiconsoutlined/48dp/2x/outline_auto_fix_high_black_48dp.png", self.format_custom, self.toolBar, translation=False)

        self.toolBar.addSeparator()

        items = (
            ("noteTool_left", "material/editor/format_align_left/materialiconsoutlined/48dp/2x/outline_format_align_left_black_48dp.png", self.format_left),
            ("noteTool_centre", "material/editor/format_align_center/materialiconsoutlined/48dp/2x/outline_format_align_center_black_48dp.png", self.format_center),
            ("noteTool_right", "material/editor/format_align_right/materialiconsoutlined/48dp/2x/outline_format_align_right_black_48dp.png", self.format_right),
            ("noteTool_justify", "material/editor/format_align_justify/materialiconsoutlined/48dp/2x/outline_format_align_justify_black_48dp.png", self.format_justify),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addMaterialIconButton(toolTip, icon, action, self.toolBar)

        self.toolBar.addSeparator()

        #self.parent.parent.addMaterialIconButton("{0}\n[Ctrl/Cmd + D]".format(config.thisTranslation["noteTool_delete"]), "material/editor/format_clear/materialiconsoutlined/48dp/2x/outline_format_clear_black_48dp.png", self.format_clear, self.toolBar, translation=False)
        self.parent.parent.addMaterialIconButton(config.thisTranslation["noteTool_delete"], "material/editor/format_clear/materialiconsoutlined/48dp/2x/outline_format_clear_black_48dp.png", self.format_clear, self.toolBar, translation=False)

        self.toolBar.addSeparator()

        items = (
            ("noteTool_hyperlink", "material/content/add_link/materialiconsoutlined/48dp/2x/outline_add_link_black_48dp.png", self.openHyperlinkDialog),
            ("noteTool_externalImage", "material/image/add_photo_alternate/materialiconsoutlined/48dp/2x/outline_add_photo_alternate_black_48dp.png", self.openImageDialog),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addMaterialIconButton(toolTip, icon, action, self.toolBar)

        self.toolBar.addSeparator()

        items = (
            ("noteTool_image", "material/editor/insert_photo/materialiconsoutlined/48dp/2x/outline_insert_photo_black_48dp.png", self.addInternalImage),
            ("noteTool_exportImage", "material/device/sim_card_download/materialiconsoutlined/48dp/2x/outline_sim_card_download_black_48dp.png", self.exportNoteImages),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addMaterialIconButton(toolTip, icon, action, self.toolBar)

        self.toolBar.addSeparator()

    def setupToolBarStandardIconSize(self):

        self.toolBar = QToolBar()
        self.toolBar.setWindowTitle(config.thisTranslation["noteTool_title"])
        self.toolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        # self.toolBar can be treated as an individual widget and positioned with a specified layout
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(self.toolBar)
        
        items = (
            ("noteTool_textFont", "font.png", self.format_font),
            ("noteTool_textColor", "textColor.png", self.format_textColor),
            ("noteTool_textBackgroundColor", "textBgColor.png", self.format_textBackgroundColor),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addStandardIconButton(toolTip, icon, action, self.toolBar)

        self.toolBar.addSeparator()

        items = (
            ("noteTool_header1", "header1.png", self.format_header1),
            ("noteTool_header2", "header2.png", self.format_header2),
            ("noteTool_header3", "header3.png", self.format_header3),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addStandardIconButton(toolTip, icon, action, self.toolBar)

        self.toolBar.addSeparator()
        
        items = (
            #("{0}\n[Ctrl/Cmd + B]".format(config.thisTranslation["noteTool_bold"]), "bold.png", self.format_bold),
            #("{0}\n[Ctrl/Cmd + I]".format(config.thisTranslation["noteTool_italic"]), "italic.png", self.format_italic),
            #("{0}\n[Ctrl/Cmd + U]".format(config.thisTranslation["noteTool_underline"]), "underline.png", self.format_underline),
            (config.thisTranslation["noteTool_bold"], "bold.png", self.format_bold),
            (config.thisTranslation["noteTool_italic"], "italic.png", self.format_italic),
            (config.thisTranslation["noteTool_underline"], "underline.png", self.format_underline),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addStandardIconButton(toolTip, icon, action, self.toolBar, translation=False)

        self.toolBar.addSeparator()

        items = (
            ("noteTool_superscript", "superscript.png", self.format_superscript),
            ("noteTool_subscript", "subscript.png", self.format_subscript),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addStandardIconButton(toolTip, icon, action, self.toolBar)

        self.toolBar.addSeparator()

        self.parent.parent.addStandardIconButton("{0}\n[Ctrl/Cmd + M]\n\n{1}\n* {4}\n* {5}\n* {6}\n\n{2}\n*1 {4}\n*2 {5}\n*3 {6}\n\n{3}\n{10}{4}|{5}|{6}{11}\n{10}{7}|{8}|{9}{11}".format(config.thisTranslation["noteTool_trans0"], config.thisTranslation["noteTool_trans1"], config.thisTranslation["noteTool_trans2"], config.thisTranslation["noteTool_trans3"], config.thisTranslation["noteTool_no1"], config.thisTranslation["noteTool_no2"], config.thisTranslation["noteTool_no3"], config.thisTranslation["noteTool_no4"], config.thisTranslation["noteTool_no5"], config.thisTranslation["noteTool_no6"], "{", "}"), "custom.png", self.format_custom, self.toolBar, translation=False)

        self.toolBar.addSeparator()

        items = (
            ("noteTool_left", "align_left.png", self.format_left),
            ("noteTool_centre", "align_center.png", self.format_center),
            ("noteTool_right", "align_right.png", self.format_right),
            ("noteTool_justify", "align_justify.png", self.format_justify),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addStandardIconButton(toolTip, icon, action, self.toolBar)

        self.toolBar.addSeparator()

        self.parent.parent.addStandardIconButton("{0}\n[Ctrl/Cmd + D]".format(config.thisTranslation["noteTool_delete"]), "clearFormat.png", self.format_clear, self.toolBar, translation=False)

        self.toolBar.addSeparator()

        items = (
            ("noteTool_hyperlink", "hyperlink.png", self.openHyperlinkDialog),
            ("noteTool_externalImage", "gallery.png", self.openImageDialog),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addStandardIconButton(toolTip, icon, action, self.toolBar)

        self.toolBar.addSeparator()

        items = (
            ("noteTool_image", "addImage.png", self.addInternalImage),
            ("noteTool_exportImage", "export.png", self.exportNoteImages),
        )
        for item in items:
            toolTip, icon, action = item
            self.parent.parent.addStandardIconButton(toolTip, icon, action, self.toolBar)

        self.toolBar.addSeparator()

    def setupToolBarFullIconSize(self):

        self.toolBar = QToolBar()
        self.toolBar.setWindowTitle(config.thisTranslation["noteTool_title"])
        self.toolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        # self.toolBar can be treated as an individual widget and positioned with a specified layout
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(self.toolBar)

        iconFile = os.path.join("htmlResources", "font.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_textFont"], self.format_font)

        iconFile = os.path.join("htmlResources", "textColor.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_textColor"], self.format_textColor)

        iconFile = os.path.join("htmlResources", "textBgColor.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_textBackgroundColor"], self.format_textBackgroundColor)

        self.toolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "header1.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_header1"], self.format_header1)

        iconFile = os.path.join("htmlResources", "header2.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_header2"], self.format_header2)

        iconFile = os.path.join("htmlResources", "header3.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_header3"], self.format_header3)

        self.toolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "bold.png")
        self.toolBar.addAction(QIcon(iconFile), "{0}\n[Ctrl/Cmd + B]".format(config.thisTranslation["noteTool_bold"]), self.format_bold)

        iconFile = os.path.join("htmlResources", "italic.png")
        self.toolBar.addAction(QIcon(iconFile), "{0}\n[Ctrl/Cmd + I]".format(config.thisTranslation["noteTool_italic"]), self.format_italic)

        iconFile = os.path.join("htmlResources", "underline.png")
        self.toolBar.addAction(QIcon(iconFile), "{0}\n[Ctrl/Cmd + U]".format(config.thisTranslation["noteTool_underline"]), self.format_underline)

        self.toolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "custom.png")
        self.toolBar.addAction(QIcon(iconFile), "{0}\n[Ctrl/Cmd + M]\n\n{1}\n* {4}\n* {5}\n* {6}\n\n{2}\n*1 {4}\n*2 {5}\n*3 {6}\n\n{3}\n{10}{4}|{5}|{6}{11}\n{10}{7}|{8}|{9}{11}".format(config.thisTranslation["noteTool_trans0"], config.thisTranslation["noteTool_trans1"], config.thisTranslation["noteTool_trans2"], config.thisTranslation["noteTool_trans3"], config.thisTranslation["noteTool_no1"], config.thisTranslation["noteTool_no2"], config.thisTranslation["noteTool_no3"], config.thisTranslation["noteTool_no4"], config.thisTranslation["noteTool_no5"], config.thisTranslation["noteTool_no6"], "{", "}"), self.format_custom)

        self.toolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "align_left.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_left"], self.format_left)

        iconFile = os.path.join("htmlResources", "align_center.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_centre"], self.format_center)

        iconFile = os.path.join("htmlResources", "align_right.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_right"], self.format_right)

        iconFile = os.path.join("htmlResources", "align_justify.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_justify"], self.format_justify)

        self.toolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "clearFormat.png")
        #self.toolBar.addAction(QIcon(iconFile), "{0}\n[Ctrl/Cmd + D]".format(config.thisTranslation["noteTool_delete"]), self.format_clear)
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_delete"], self.format_clear)

        self.toolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "hyperlink.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_hyperlink"], self.openHyperlinkDialog)

        iconFile = os.path.join("htmlResources", "gallery.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_externalImage"], self.openImageDialog)

        self.toolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "addImage.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_image"], self.addInternalImage)

        iconFile = os.path.join("htmlResources", "export.png")
        self.toolBar.addAction(QIcon(iconFile), config.thisTranslation["noteTool_exportImage"], self.exportNoteImages)

        self.toolBar.addSeparator()

    def setupLayout(self):
        self.editor = QTextEdit()  
        self.editor.setStyleSheet("font-family:'{0}'; font-size:{1}pt;".format(config.font, config.fontSize));
        self.editor.textChanged.connect(self.textChanged)
        self.setCentralWidget(self.editor)

        #self.layout = QGridLayout()
        #self.layout.setMenuBar(self.menuBar)
        #self.layout.addWidget(self.toolBar, 0, 0)
        #self.layout.addWidget(self.editor, 1, 0)
        #self.setLayout(self.layout)

    # adjustment of note editor font size
    def increaseNoteEditorFontSize(self):
        if self.html:
            self.editor.selectAll()
            config.noteEditorFontSize += 1
            self.editor.setFontPointSize(config.noteEditorFontSize)
            self.hide()
            self.show()

    def decreaseNoteEditorFontSize(self):
        if self.html and not config.noteEditorFontSize == 0:
            self.editor.selectAll()
            config.noteEditorFontSize -= 1
            self.editor.setFontPointSize(config.noteEditorFontSize)
            self.hide()
            self.show()

    # search field entered
    def searchLineEntered(self):
        searchString = self.searchLineEdit.text()
        if searchString:
            cursor = self.editor.document().find(searchString, self.editor.textCursor())
        if cursor:
            self.editor.setTextCursor(cursor)
        self.hide()
        self.show()

    def focusSearchField(self):
        self.searchLineEdit.setFocus()

    # track if the text being modified
    def textChanged(self):
        if self.parent.parent.noteSaved:
            self.parent.parent.noteSaved = False
            self.updateWindowTitle()

    # display content when first launched
    def displayInitialContent(self, noteType=None, b=None, c=None, v=None, year=None, month=None, day=None):
        if self.parent.parent.noteSaved or self.parent.parent.warningNotSaved():
            if noteType is not None:
                self.noteType = noteType
            if b is not None:
                self.b = b
            if c is not None:
                self.c = c
            if v is not None:
                self.v = v
            if year is not None:
                self.year = year
            if month is not None:
                self.month = month
            if day is not None:
                self.day = day
            if self.noteType == "journal":
                self.openJournalNote()
            elif self.noteType == "file":
                if self.noteFileName:
                    self.openNoteFile(self.noteFileName)
                else:
                    self.newNoteFile()
            else:
                self.openBibleNote()

            config.lastOpenedNote = (noteType, b, c, v, year, month, day)

            self.editor.selectAll()
            self.editor.setFontPointSize(config.noteEditorFontSize)
            self.editor.moveCursor(QTextCursor.Start, QTextCursor.MoveAnchor)

            self.parent.parent.noteSaved = True
            self.updateWindowTitle()

    def getEmptyPage(self):
        strict = ''
        if config.includeStrictDocTypeInNote:
            strict = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">'
        return """{4}<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li {0} white-space: pre-wrap; {1}
</style></head><body style="font-family:'{2}'; font-size:{3}pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html>"""\
            .format("{", "}", config.font, config.fontSize, strict)

    def openJournalNote(self):
        journalSqlite = JournalSqlite()
        note = journalSqlite.getJournalNote(self.year, self.month, self.day)
        if note == config.thisTranslation["empty"]:
            note = self.getEmptyPage()
        else:
            note = self.fixNoteFont(note)
        if self.html:
            self.editor.setHtml(note)
        else:
            self.editor.setPlainText(note)

    # load chapter / verse notes from sqlite database
    def openBibleNote(self):
        if self.noteType == "book":
            note = NoteService.getBookNote(self.b)
        elif self.noteType == "chapter":
            note = NoteService.getChapterNote(self.b, self.c)
        elif self.noteType == "verse":
            note = NoteService.getVerseNote(self.b, self.c, self.v)
        if note == config.thisTranslation["empty"]:
            note = self.getEmptyPage()
        else:
            note = self.fixNoteFont(note)
        if self.html:
            self.editor.setHtml(note)
        else:
            self.editor.setPlainText(note)

    # File I / O
    def newNoteFile(self):
        if self.parent.parent.noteSaved or self.parent.parent.warningNotSaved():
            self.newNoteFileAction()

    def newNoteFileAction(self):
        self.noteType = "file"
        self.noteFileName = ""
        #self.editor.clear()
        defaultText = self.getEmptyPage()
        if self.html:
            self.editor.setHtml(defaultText)
        else:
            self.editor.setPlainText(defaultText)
        self.parent.parent.noteSaved = True
        self.updateWindowTitle()
        self.hide()
        self.show()

    def openFileDialog(self):
        if self.parent.parent.noteSaved or self.parent.parent.warningNotSaved():
            self.openFileDialogAction()

    def openFileDialogAction(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                config.thisTranslation["menu7_open"],
                "notes",
                "UniqueBible.app Note Files (*.uba);;HTML Files (*.html);;HTM Files (*.htm);;All Files (*)", "", options)
        if fileName:
            self.openNoteFile(fileName)

    def openNoteFile(self, fileName):
        try:
            f = open(fileName, "r", encoding="utf-8")
        except:
            print("Failed to open '{0}'".format(fileName))
        note = f.read()
        f.close()
        self.noteType = "file"
        self.noteFileName = fileName
        note = self.fixNoteFont(note)
        if self.html:
            self.editor.setHtml(note)
        else:
            self.editor.setPlainText(note)
        self.parent.parent.noteSaved = True
        self.updateWindowTitle()
        self.hide()
        self.show()

    def saveNote(self):
        if self.html:
            note = self.editor.toHtml()
        else:
            note = self.editor.toPlainText()
        note = self.fixNoteFont(note)
        if self.noteType == "book":
            NoteService.saveBookNote(self.b, note)
            if config.openBibleNoteAfterSave:
                self.parent.parent.openBookNote(self.b,)
        elif self.noteType == "chapter":
            NoteService.saveChapterNote(self.b, self.c, note)
            if config.openBibleNoteAfterSave:
                self.parent.parent.openChapterNote(self.b, self.c)
        elif self.noteType == "verse":
            NoteService.saveVerseNote(self.b, self.c, self.v, note)
            if config.openBibleNoteAfterSave:
                self.parent.parent.openVerseNote(self.b, self.c, self.v)
        elif self.noteType == "file":
            if self.noteFileName == "":
                self.openSaveAsDialog()
            else:
                self.saveAsNote(self.noteFileName)
        elif self.noteType == "journal":
            JournalSqlite().saveJournalNote(self.year, self.month, self.day, note)
        # Refresh
        if not self.noteType == "file":
            self.parent.parent.noteSaved = True
            self.updateWindowTitle()
            if config.refreshWindowsAfterSavingNote:
                self.parent.parent.reloadCurrentRecord(True)

    def openSaveAsDialog(self):
        if self.noteFileName:
            *_, defaultName = os.path.split(self.noteFileName)
        else:
            defaultName = "new.uba"
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                os.path.join("notes", defaultName),
                "UniqueBible.app Note Files (*.uba);;HTML Files (*.html);;HTM Files (*.htm);;All Files (*)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".uba"
            self.saveAsNote(fileName)

    def saveAsNote(self, fileName):
        if self.html:
            note = self.editor.toHtml()
        else:
            note = self.editor.toPlainText()
        note = self.fixNoteFont(note)
        f = open(fileName, "w", encoding="utf-8")
        f.write(note)
        f.close()
        self.noteFileName = fileName
        self.parent.parent.addExternalFileHistory(fileName)
        self.parent.parent.setExternalFileButton()
        self.parent.parent.noteSaved = True
        self.updateWindowTitle()

    def fixNoteFont(self, note):
        note = re.sub("<body style={0}[ ]*?font-family:[ ]*?'[^']*?';[ ]*?font-size:[ ]*?[0-9]+?pt;".format('"'), "<body style={0}font-family:'{1}'; font-size:{2}pt;".format('"', config.font, config.fontSize), note)
        if not config.includeStrictDocTypeInNote:
            note = re.sub("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n""", "", note)
        return note

    # formatting styles
    def format_clear(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                selectedText = """<span style="font-family:'{0}'; font-size:{1}pt;">{2}</span>""".format(config.font, config.fontSize, selectedText)
                self.editor.insertHtml(selectedText)
            else:
                selectedText = re.sub("<[^\n<>]*?>", "", selectedText)
                self.editor.insertPlainText(selectedText)
        else:
            self.selectTextFirst()

    def format_header1(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                self.editor.insertHtml("<h1>{0}</h1>".format(selectedText))
            else:
                self.editor.insertPlainText("<h1>{0}</h1>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_header2(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                self.editor.insertHtml("<h2>{0}</h2>".format(selectedText))
            else:
                self.editor.insertPlainText("<h2>{0}</h2>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_header3(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                self.editor.insertHtml("<h3>{0}</h3>".format(selectedText))
            else:
                self.editor.insertPlainText("<h3>{0}</h3>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_font(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            ok, font = QFontDialog.getFont(QFont(config.font, config.fontSize), self)
            if ok:
                if self.html:
                    self.editor.setCurrentFont(font)
                else:
                    fontFamily, fontSize, i1, i2, fontWeight, italic, underline, strikeout, *_ = font.key().split(",")
                    spanTag = """<span style="font-family:'{0}'; font-size:{1}pt;""".format(fontFamily, fontSize)
                    # add font weight
                    if fontWeight == "25":
                        spanTag += " font-weight:200;"
                    elif fontWeight == "75":
                        spanTag += " font-weight:600;"
                    # add italic style
                    if italic == "1":
                        spanTag += " font-style:italic;"
                    # add both underline and strikeout style
                    if underline == "1" and strikeout == "1":
                        spanTag += " text-decoration: underline line-through;"
                    # add underline style
                    elif underline == "1":
                        spanTag += " text-decoration: underline;"
                    # add strikeout style
                    elif strikeout == "1":
                        spanTag += " text-decoration: line-through;"
                    # close tag
                    spanTag += '">'
                    self.editor.insertPlainText("{0}{1}</span>".format(spanTag, selectedText))
        else:
            self.selectTextFirst()
        
    def format_textColor(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            color = QColorDialog.getColor(Qt.darkRed, self)
            if color.isValid():
                if self.html:
                    self.editor.setTextColor(color)
                else:
                    self.editor.insertPlainText('<span style="color:{0};">{1}</span>'.format(color.name(), self.editor.textCursor().selectedText()))
        else:
            self.selectTextFirst()

    def format_textBackgroundColor(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            color = QColorDialog.getColor(Qt.yellow, self)
            if color.isValid():
                if self.html:
                    self.editor.setTextBackgroundColor(color)
                else:
                    self.editor.insertPlainText('<span style="background-color:{0};">{1}</span>'.format(color.name(), selectedText))
        else:
            self.selectTextFirst()

    def format_bold(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                # Reference: https://doc.qt.io/qt-5/qfont.html#Weight-enum
                # Bold = 75
                self.editor.setFontWeight(75)
            else:
                self.editor.insertPlainText("<b>{0}</b>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_italic(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                self.editor.setFontItalic(True)
            else:
                self.editor.insertPlainText("<i>{0}</i>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_underline(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                self.editor.setFontUnderline(True)
            else:
                self.editor.insertPlainText("<u>{0}</u>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_superscript(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                self.editor.insertHtml("<sup>{0}</sup>".format(selectedText))
            else:
                self.editor.insertPlainText("<sup>{0}</sup>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_subscript(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                self.editor.insertHtml("<sub>{0}</sub>".format(selectedText))
            else:
                self.editor.insertPlainText("<sub>{0}</sub>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_center(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                self.editor.setAlignment(Qt.AlignCenter)
            else:
                self.editor.insertPlainText("<div style='text-align:center;'>{0}</div>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_justify(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                self.editor.setAlignment(Qt.AlignJustify)
            else:
                self.editor.insertPlainText("<div style='text-align:justify;'>{0}</div>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_left(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                self.editor.setAlignment(Qt.AlignLeft)
            else:
                self.editor.insertPlainText("<div style='text-align:left;'>{0}</div>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_right(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            if self.html:
                self.editor.setAlignment(Qt.AlignRight)
            else:
                self.editor.insertPlainText("<div style='text-align:right;'>{0}</div>".format(selectedText))
        else:
            self.selectTextFirst()

    def format_custom(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            #selectedText = self.customFormat(selectedText)
            selectedText = markdown.markdown(selectedText)
            if self.html:
                self.editor.insertHtml(selectedText)
            else:
                self.editor.insertPlainText(selectedText)
        else:
            self.selectTextFirst()

    def customFormat(self, text):
        # QTextEdit's line break character by pressing ENTER in plain & html mode " "
        # please note that " " is not an empty string
        text = text.replace(" ", "\n")

        text = re.sub("^\*[0-9]+? (.*?)$", r"<ol><li>\1</li></ol>", text, flags=re.M)
        text = text.replace("</ol>\n<ol>", "\n")
        text = re.sub("^\* (.*?)$", r"<ul><li>\1</li></ul>", text, flags=re.M)
        text = text.replace("</ul>\n<ul>", "\n")
        text = re.sub("^{.*?}$", self.formatHTMLTable, text, flags=re.M)
        text = text.replace("</table>\n<table>", "\n")

        # add style to table here
        # please note that QTextEdit supports HTML 4, rather than HTML 5
        # take this old reference: https://www.w3schools.com/tags/tag_table.asp
        text = text.replace('<table>', '<table border="1" cellpadding="5">')

        # convert back to QTextEdit linebreak
        text = text.replace("\n", " ")

        # wrap with default font and font-size
        text = """<span style="font-family:'{0}'; font-size:{1}pt;">{2}</span>""".format(config.font, config.fontSize, text)
        return text

    def formatHTMLTable(self, match):
        row = match.group()[1:-1]
        row = "".join(["<td>{0}</td>".format(cell) for cell in row.split("|")])
        return "<table><tr>{0}</tr></table>".format(row)

    def addInternalImage(self):
        self.openImageDialog(external=False)

    def openImageDialog(self, external=True):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                config.thisTranslation["html_open"],
                self.parent.parent.openFileNameLabel.text(),
                "JPG Files (*.jpg);;JPEG Files (*.jpeg);;PNG Files (*.png);;GIF Files (*.gif);;BMP Files (*.bmp);;All Files (*)", "", options)
        if fileName:
            if external:
                self.linkExternalImage(fileName)
            else:
                self.embedImage(fileName)

    def embedImage(self, fileName):
        name, extension = os.path.splitext(os.path.basename(fileName))
        with open(fileName, "rb") as fileObject:
            binaryData = fileObject.read()
            encodedData = base64.b64encode(binaryData)
            asciiString = encodedData.decode('ascii')
            imageTag = '<img src="data:image/{2};base64,{0}" alt="{1}">'.format(asciiString, name, extension[1:])
            if self.html:
                self.editor.insertHtml(imageTag)
            else:
                self.editor.insertPlainText(imageTag)

    def exportNoteImages(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                config.thisTranslation["select_a_folder"],
                self.parent.parent.directoryLabel.text(), options)
        if directory:
            if self.html:
                htmlText = self.editor.toHtml()
            else:
                htmlText = self.editor.toPlainText()
            searchPattern = r'src=(["{0}])data:image/([^<>]+?);[ ]*?base64,[ ]*?([^ <>]+?)\1'.format("'")
            for counter, value in enumerate(re.findall(searchPattern, htmlText)):
                *_, ext, asciiString = value
                binaryString = asciiString.encode("ascii")
                binaryData = base64.b64decode(binaryString)
                imageFilePath = os.path.join(directory, "image{0}.{1}".format(counter + 1, ext))
                with open(imageFilePath, "wb") as fileObject:
                    fileObject.write(binaryData)

    def linkExternalImage(self, fileName):
        imageTag = '<img src="{0}" alt="UniqueBible.app">'.format(fileName)
        if self.html:
            self.editor.insertHtml(imageTag)
        else:
            self.editor.insertPlainText(imageTag)

    def openHyperlinkDialog(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            text, ok = QInputDialog.getText(self, "UniqueBible.app",
                    config.thisTranslation["noteTool_hyperlink"], QLineEdit.Normal,
                    selectedText)
            if ok and text != '':
                hyperlink = '<a href="{0}">{1}</a>'.format(text, selectedText)
                hyperlink = """<span style="font-family:'{0}'; font-size:{1}pt;">{2}</span>""".format(config.font, config.fontSize, hyperlink)
                if self.html:
                    self.editor.insertHtml(hyperlink)
                else:
                    self.editor.insertPlainText(hyperlink)
        else:
            self.selectTextFirst()

    def setupTextUtility(self):

        self.ttsToolbar = QToolBar()
        self.ttsToolbar.setWindowTitle(config.thisTranslation["noteTool_title"])
        self.ttsToolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        # self.toolBar can be treated as an individual widget and positioned with a specified layout
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(self.ttsToolbar)

        self.languageCombo = QComboBox()
        self.ttsToolbar.addWidget(self.languageCombo)
        languages = self.parent.parent.getTtsLanguages()
        self.languageCodes = list(languages.keys())
        for code in self.languageCodes:
            self.languageCombo.addItem(languages[code][1])
        # Check if selected tts engine has the language user specify.
        if not (config.ttsDefaultLangauge in self.languageCodes):
            config.ttsDefaultLangauge = "en-GB" if config.isGoogleCloudTTSAvailable else "en"
        # Set initial item
        initialIndex = self.languageCodes.index(config.ttsDefaultLangauge)
        self.languageCombo.setCurrentIndex(initialIndex)

        button = QPushButton(config.thisTranslation["speak"])
        button.setToolTip(config.thisTranslation["speak"])
        button.clicked.connect(self.speakText)
        self.ttsToolbar.addWidget(button)
        button = QPushButton(config.thisTranslation["stop"])
        button.setToolTip(config.thisTranslation["stop"])
        button.clicked.connect(self.parent.parent.textCommandParser.stopTtsAudio)
        self.ttsToolbar.addWidget(button)

        self.translateToolbar = QToolBar()
        self.translateToolbar.setWindowTitle(config.thisTranslation["noteTool_title"])
        self.translateToolbar.setContextMenuPolicy(Qt.PreventContextMenu)
        # self.toolBar can be treated as an individual widget and positioned with a specified layout
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(self.translateToolbar)

        self.fromLanguageCombo = QComboBox()
        self.translateToolbar.addWidget(self.fromLanguageCombo)
        self.fromLanguageCombo.addItems(["[Auto]"] +Translator.fromLanguageNames)
        initialIndex = 0
        self.fromLanguageCombo.setCurrentIndex(initialIndex)

        button = QPushButton(config.thisTranslation["context1_translate"])
        button.setToolTip(config.thisTranslation["context1_translate"])
        button.clicked.connect(self.translateText)
        self.translateToolbar.addWidget(button)

        self.toLanguageCombo = QComboBox()
        self.translateToolbar.addWidget(self.toLanguageCombo)
        self.toLanguageCombo.addItems(Translator.toLanguageNames)
        initialIndex = Translator.toLanguageNames.index(config.userLanguage)
        self.toLanguageCombo.setCurrentIndex(initialIndex)

    def speakText(self):
        text = self.editor.textCursor().selectedText()
        if text:
            if config.noTtsFound:
                self.displayMessage(config.thisTranslation["message_noSupport"])
            else:
                if ":::" in text:
                    text = text.split(":::")[-1]
                if config.isGoogleCloudTTSAvailable or ((not ("OfflineTts" in config.enabled) or config.forceOnlineTts) and ("Gtts" in config.enabled)):
                    command = "GTTS:::{0}:::{1}".format(self.languageCodes[self.languageCombo.currentIndex()], text)
                else:
                    command = "SPEAK:::{0}:::{1}".format(self.languageCodes[self.languageCombo.currentIndex()], text)
                self.parent.parent.runTextCommand(command)
        else:
            self.selectTextFirst()

    def translateText(self):
        text = self.editor.textCursor().selectedText()
        if text:
            translator = Translator()
            if translator.language_translator is not None:
                fromLanguage = Translator.fromLanguageCodes[self.fromLanguageCombo.currentIndex() - 1] if self.fromLanguageCombo.currentIndex() != 0 else translator.identify(text)
                toLanguage = Translator.toLanguageCodes[self.toLanguageCombo.currentIndex()]
                result = translator.translate(text, fromLanguage, toLanguage)
                self.editor.insertPlainText(result)
            else:
                self.displayMessage(config.thisTranslation["ibmWatsonNotEnalbed"])
                webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/IBM-Watson-Language-Translator")
        else:
            self.selectTextFirst()

    def selectTextFirst(self):
        self.displayMessage(config.thisTranslation["selectTextFirst"])

    def displayMessage(self, message="", title="UniqueBible"):
        reply = QMessageBox.information(self, title, message)
