import os, re, config, base64
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QTextCursor, QFont, QGuiApplication
from PySide2.QtPrintSupport import QPrinter, QPrintDialog
from PySide2.QtWidgets import (QInputDialog, QLineEdit, QMainWindow, QPushButton, QToolBar, QDialog, QFileDialog, QTextEdit, QFontDialog, QColorDialog)
from NoteSqlite import NoteSqlite
from util.NoteService import NoteService


class NoteEditor(QMainWindow):

    def __init__(self, parent, noteType, noteFileName="", b=None, c=None, v=None):
        super().__init__()
        self.parent, self.noteType = parent, noteType
        self.noteFileName = noteFileName
        if not self.noteType == "file":
            if v:
                self.b, self.c, self.v = b, c, v
            else:
                self.b, self.c, self.v = config.studyB, config.studyC, config.studyV

        # default - "Rich" mode for editing
        self.html = True
        # default - show toolbar with formatting items
        self.showToolBar = True
        # default - text is not modified; no need for saving new content
        self.parent.noteSaved = True
        config.noteOpened = True
        config.lastOpenedNote = (noteType, b, c, v)

        # specify window size
        self.resizeWindow(2/3, 2/3)

        # setup interface
        self.setupMenuBar()
        self.addToolBarBreak()
        self.setupToolBar()
        self.setupLayout()

        # display content when first launched
        self.displayInitialContent()

        # specify window title
        self.updateWindowTitle()

    # re-implementing close event, when users close this widget
    def closeEvent(self, event):
        if self.parent.noteSaved:
            config.noteOpened = False
            event.accept()
            if config.lastOpenedNote:
                if config.lastOpenedNote[0] == "file":
                    self.parent.externalFileButtonClicked()
                elif config.lastOpenedNote[0] == "book":
                    self.parent.openStudyBookNote()
                elif config.lastOpenedNote[0] == "chapter":
                    self.parent.openStudyChapterNote()
                elif config.lastOpenedNote[0] == "verse":
                    self.parent.openStudyVerseNote()
        else:
            if self.parent.warningNotSaved():
                self.parent.noteSaved = True
                config.noteOpened = False
                event.accept()
            else:
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
        availableGeometry = QGuiApplication.instance().desktop().availableGeometry()
        self.resize(availableGeometry.width() * widthFactor, availableGeometry.height() * heightFactor)

    def updateWindowTitle(self):
        if self.noteType == "file":
            if self.noteFileName:
                *_, title = os.path.split(self.noteFileName)
            else:
                title = "NEW"
        else:
            title = self.parent.bcvToVerseReference(self.b, self.c, self.v)
            if self.noteType == "book":
                title, *_ = title.split(" ")            
            elif self.noteType == "chapter":
                title, *_ = title.split(":")
        mode = {True: "rich", False: "plain"}
        notModified = {True: "", False: " [modified]"}
        self.setWindowTitle("Note Editor ({1} mode) - {0}{2}".format(title, mode[self.html], notModified[self.parent.noteSaved]))

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
        if config.toolBarIconFullSize:
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
        newButton.setToolTip("{0}\n[Ctrl/Cmd + N]".format(config.thisTranslation["menu7_create"]))
        newButtonFile = os.path.join("htmlResources", "newfile.png")
        newButton.setIcon(QIcon(newButtonFile))
        newButton.clicked.connect(self.newNoteFile)
        self.menuBar.addWidget(newButton)

        openButton = QPushButton()
        openButton.setToolTip("{0}\n[Ctrl/Cmd + O]".format(config.thisTranslation["menu7_open"]))
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
        self.searchLineEdit.setToolTip(config.thisTranslation["menu5_search"])
        self.searchLineEdit.setMaximumWidth(400)
        self.searchLineEdit.returnPressed.connect(self.searchLineEntered)
        self.menuBar.addWidget(self.searchLineEdit)

        self.menuBar.addSeparator()

        toolBarButton = QPushButton()
        toolBarButton.setToolTip(config.thisTranslation["note_toolbar"])
        toolBarButtonFile = os.path.join("htmlResources", "toolbar.png")
        toolBarButton.setIcon(QIcon(toolBarButtonFile))
        toolBarButton.clicked.connect(self.toogleToolbar)
        self.menuBar.addWidget(toolBarButton)

        self.menuBar.addSeparator()

    def setupMenuBarFullIconSize(self):

        self.menuBar = QToolBar()
        self.menuBar.setWindowTitle(config.thisTranslation["note_title"])
        self.menuBar.setContextMenuPolicy(Qt.PreventContextMenu)
        # In QWidget, self.menuBar is treated as the menubar without the following line
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(self.menuBar)

        iconFile = os.path.join("htmlResources", "newfile.png")
        self.menuBar.addAction(QIcon(iconFile), "{0}\n[Ctrl/Cmd + N]".format(config.thisTranslation["menu7_create"]), self.newNoteFile)

        iconFile = os.path.join("htmlResources", "open.png")
        self.menuBar.addAction(QIcon(iconFile), "{0}\n[Ctrl/Cmd + O]".format(config.thisTranslation["menu7_open"]), self.openFileDialog)

        self.menuBar.addSeparator()

        iconFile = os.path.join("htmlResources", "save.png")
        self.menuBar.addAction(QIcon(iconFile), "{0}\n[Ctrl/Cmd + S]".format(config.thisTranslation["note_save"]), self.saveNote)

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
        self.searchLineEdit.setToolTip("{0}\n[Ctrl/Cmd + F]".format(config.thisTranslation["menu5_search"]))
        self.searchLineEdit.setMaximumWidth(400)
        self.searchLineEdit.returnPressed.connect(self.searchLineEntered)
        self.menuBar.addWidget(self.searchLineEdit)

        self.menuBar.addSeparator()

        iconFile = os.path.join("htmlResources", "toolbar.png")
        self.menuBar.addAction(QIcon(iconFile), config.thisTranslation["note_toolbar"], self.toogleToolbar)

        self.menuBar.addSeparator()

    def toogleToolbar(self):
        if self.showToolBar:
            self.toolBar.hide()
            self.showToolBar = False
        else:
            self.toolBar.show()
            self.showToolBar = True

    def printNote(self):
        #document = QTextDocument("Sample Page")
        document = self.editor.document()
        printer = QPrinter()

        myPrintDialog = QPrintDialog(printer, self)
        if myPrintDialog.exec_() == QDialog.Accepted:
            return document.print_(printer)

    def setupToolBar(self):
        if config.toolBarIconFullSize:
            self.setupToolBarFullIconSize()
        else:
            self.setupToolBarStandardIconSize()

    def setupToolBarStandardIconSize(self):

        self.toolBar = QToolBar()
        self.toolBar.setWindowTitle(config.thisTranslation["noteTool_title"])
        self.toolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        # self.toolBar can be treated as an individual widget and positioned with a specified layout
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(self.toolBar)

        fontButton = QPushButton()
        fontButton.setToolTip(config.thisTranslation["noteTool_textFont"])
        fontButtonFile = os.path.join("htmlResources", "font.png")
        fontButton.setIcon(QIcon(fontButtonFile))
        fontButton.clicked.connect(self.format_font)
        self.toolBar.addWidget(fontButton)

        fontButton = QPushButton()
        fontButton.setToolTip(config.thisTranslation["noteTool_textColor"])
        fontButtonFile = os.path.join("htmlResources", "textColor.png")
        fontButton.setIcon(QIcon(fontButtonFile))
        fontButton.clicked.connect(self.format_textColor)
        self.toolBar.addWidget(fontButton)

        fontButton = QPushButton()
        fontButton.setToolTip(config.thisTranslation["noteTool_textBackgroundColor"])
        fontButtonFile = os.path.join("htmlResources", "textBgColor.png")
        fontButton.setIcon(QIcon(fontButtonFile))
        fontButton.clicked.connect(self.format_textBackgroundColor)
        self.toolBar.addWidget(fontButton)

        self.toolBar.addSeparator()

        headerButton = QPushButton()
        headerButton.setToolTip(config.thisTranslation["noteTool_header1"])
        headerButtonFile = os.path.join("htmlResources", "header1.png")
        headerButton.setIcon(QIcon(headerButtonFile))
        headerButton.clicked.connect(self.format_header1)
        self.toolBar.addWidget(headerButton)

        headerButton = QPushButton()
        headerButton.setToolTip(config.thisTranslation["noteTool_header2"])
        headerButtonFile = os.path.join("htmlResources", "header2.png")
        headerButton.setIcon(QIcon(headerButtonFile))
        headerButton.clicked.connect(self.format_header2)
        self.toolBar.addWidget(headerButton)

        headerButton = QPushButton()
        headerButton.setToolTip(config.thisTranslation["noteTool_header3"])
        headerButtonFile = os.path.join("htmlResources", "header3.png")
        headerButton.setIcon(QIcon(headerButtonFile))
        headerButton.clicked.connect(self.format_header3)
        self.toolBar.addWidget(headerButton)

        self.toolBar.addSeparator()
        
        boldButton = QPushButton()
        boldButton.setToolTip("{0}\n[Ctrl/Cmd + B]".format(config.thisTranslation["noteTool_bold"]))
        boldButtonFile = os.path.join("htmlResources", "bold.png")
        boldButton.setIcon(QIcon(boldButtonFile))
        boldButton.clicked.connect(self.format_bold)
        self.toolBar.addWidget(boldButton)

        italicButton = QPushButton()
        italicButton.setToolTip("{0}\n[Ctrl/Cmd + I]".format(config.thisTranslation["noteTool_italic"]))
        italicButtonFile = os.path.join("htmlResources", "italic.png")
        italicButton.setIcon(QIcon(italicButtonFile))
        italicButton.clicked.connect(self.format_italic)
        self.toolBar.addWidget(italicButton)

        underlineButton = QPushButton()
        underlineButton.setToolTip("{0}\n[Ctrl/Cmd + U]".format(config.thisTranslation["noteTool_underline"]))
        underlineButtonFile = os.path.join("htmlResources", "underline.png")
        underlineButton.setIcon(QIcon(underlineButtonFile))
        underlineButton.clicked.connect(self.format_underline)
        self.toolBar.addWidget(underlineButton)

        self.toolBar.addSeparator()

        customButton = QPushButton()
        customButton.setToolTip("{0}\n[Ctrl/Cmd + M]\n\n{1}\n* {4}\n* {5}\n* {6}\n\n{2}\n*1 {4}\n*2 {5}\n*3 {6}\n\n{3}\n{10}{4}|{5}|{6}{11}\n{10}{7}|{8}|{9}{11}".format(config.thisTranslation["noteTool_trans0"], config.thisTranslation["noteTool_trans1"], config.thisTranslation["noteTool_trans2"], config.thisTranslation["noteTool_trans3"], config.thisTranslation["noteTool_no1"], config.thisTranslation["noteTool_no2"], config.thisTranslation["noteTool_no3"], config.thisTranslation["noteTool_no4"], config.thisTranslation["noteTool_no5"], config.thisTranslation["noteTool_no6"], "{", "}"))
        customButtonFile = os.path.join("htmlResources", "custom.png")
        customButton.setIcon(QIcon(customButtonFile))
        customButton.clicked.connect(self.format_custom)
        self.toolBar.addWidget(customButton)

        self.toolBar.addSeparator()

        leftButton = QPushButton()
        leftButton.setToolTip(config.thisTranslation["noteTool_left"])
        leftButtonFile = os.path.join("htmlResources", "align_left.png")
        leftButton.setIcon(QIcon(leftButtonFile))
        leftButton.clicked.connect(self.format_left)
        self.toolBar.addWidget(leftButton)

        centerButton = QPushButton()
        centerButton.setToolTip(config.thisTranslation["noteTool_centre"])
        centerButtonFile = os.path.join("htmlResources", "align_center.png")
        centerButton.setIcon(QIcon(centerButtonFile))
        centerButton.clicked.connect(self.format_center)
        self.toolBar.addWidget(centerButton)

        rightButton = QPushButton()
        rightButton.setToolTip(config.thisTranslation["noteTool_right"])
        rightButtonFile = os.path.join("htmlResources", "align_right.png")
        rightButton.setIcon(QIcon(rightButtonFile))
        rightButton.clicked.connect(self.format_right)
        self.toolBar.addWidget(rightButton)

        justifyButton = QPushButton()
        justifyButton.setToolTip(config.thisTranslation["noteTool_justify"])
        justifyButtonFile = os.path.join("htmlResources", "align_justify.png")
        justifyButton.setIcon(QIcon(justifyButtonFile))
        justifyButton.clicked.connect(self.format_justify)
        self.toolBar.addWidget(justifyButton)

        self.toolBar.addSeparator()

        clearButton = QPushButton()
        clearButton.setToolTip("{0}\n[Ctrl/Cmd + D]".format(config.thisTranslation["noteTool_delete"]))
        clearButtonFile = os.path.join("htmlResources", "clearFormat.png")
        clearButton.setIcon(QIcon(clearButtonFile))
        clearButton.clicked.connect(self.format_clear)
        self.toolBar.addWidget(clearButton)

        self.toolBar.addSeparator()

        hyperlinkButton = QPushButton()
        hyperlinkButton.setToolTip(config.thisTranslation["noteTool_hyperlink"])
        hyperlinkButtonFile = os.path.join("htmlResources", "hyperlink.png")
        hyperlinkButton.setIcon(QIcon(hyperlinkButtonFile))
        hyperlinkButton.clicked.connect(self.openHyperlinkDialog)
        self.toolBar.addWidget(hyperlinkButton)

        imageButton = QPushButton()
        imageButton.setToolTip(config.thisTranslation["noteTool_externalImage"])
        imageButtonFile = os.path.join("htmlResources", "gallery.png")
        imageButton.setIcon(QIcon(imageButtonFile))
        imageButton.clicked.connect(self.openImageDialog)
        self.toolBar.addWidget(imageButton)

        self.toolBar.addSeparator()

        imageButton = QPushButton()
        imageButton.setToolTip(config.thisTranslation["noteTool_image"])
        imageButtonFile = os.path.join("htmlResources", "addImage.png")
        imageButton.setIcon(QIcon(imageButtonFile))
        imageButton.clicked.connect(self.addInternalImage)
        self.toolBar.addWidget(imageButton)

        imageButton = QPushButton()
        imageButton.setToolTip(config.thisTranslation["noteTool_exportImage"])
        imageButtonFile = os.path.join("htmlResources", "export.png")
        imageButton.setIcon(QIcon(imageButtonFile))
        imageButton.clicked.connect(self.exportNoteImages)
        self.toolBar.addWidget(imageButton)

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
        self.toolBar.addAction(QIcon(iconFile), "{0}\n[Ctrl/Cmd + D]".format(config.thisTranslation["noteTool_delete"]), self.format_clear)

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
        if self.parent.noteSaved:
            self.parent.noteSaved = False
            self.updateWindowTitle()

    # display content when first launched
    def displayInitialContent(self):
        if self.noteType == "file":
            if self.noteFileName:
                self.openNoteFile(self.noteFileName)
            else:
                self.newNoteFile()
        else:
            self.openBibleNote()

        self.editor.selectAll()
        self.editor.setFontPointSize(config.noteEditorFontSize)
        self.editor.moveCursor(QTextCursor.Start, QTextCursor.MoveAnchor)

        self.parent.noteSaved = True

    def getEmptyPage(self):
        return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li {0} white-space: pre-wrap; {1}
</style></head><body style="font-family:'{2}'; font-size:{3}pt; font-weight:400; font-style:normal;">
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><br /></p></body></html>""".format("{", "}", config.font, config.fontSize)

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
        if self.parent.noteSaved:
            self.newNoteFileAction()
        elif self.parent.warningNotSaved():
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
        self.parent.noteSaved = True
        self.updateWindowTitle()
        self.hide()
        self.show()

    def openFileDialog(self):
        if self.parent.noteSaved:
            self.openFileDialogAction()
        elif self.parent.warningNotSaved():
            self.openFileDialogAction()

    def openFileDialogAction(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                config.thisTranslation["menu7_open"],
                self.parent.openFileNameLabel.text(),
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
        self.parent.noteSaved = True
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
                self.parent.openBookNote(self.b,)
            self.parent.noteSaved = True
            self.updateWindowTitle()
        elif self.noteType == "chapter":
            NoteService.saveChapterNote(self.b, self.c, note)
            if config.openBibleNoteAfterSave:
                self.parent.openChapterNote(self.b, self.c)
            self.parent.noteSaved = True
            self.updateWindowTitle()
        elif self.noteType == "verse":
            NoteService.saveVerseNote(self.b, self.c, self.v, note)
            if config.openBibleNoteAfterSave:
                self.parent.openVerseNote(self.b, self.c, self.v)
            self.parent.noteSaved = True
            self.updateWindowTitle()
        elif self.noteType == "file":
            if self.noteFileName == "":
                self.openSaveAsDialog()
            else:
                self.saveAsNote(self.noteFileName)

    def openSaveAsDialog(self):
        if self.noteFileName:
            *_, defaultName = os.path.split(self.noteFileName)
        else:
            defaultName = "new.uba"
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                defaultName,
                "UniqueBible.app Note Files (*.uba);;HTML Files (*.html);;HTM Files (*.htm);;All Files (*)", "", options)
        if fileName:
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
        self.parent.addExternalFileHistory(fileName)
        self.parent.setExternalFileButton()
        self.parent.noteSaved = True
        self.updateWindowTitle()

    def fixNoteFont(self, note):
        return re.sub("<body style={0}[ ]*?font-family:[ ]*?'[^']*?';[ ]*?font-size:[ ]*?[0-9]+?pt;".format('"'), "<body style={0}font-family:'{1}'; font-size:{2}pt;".format('"', config.font, config.fontSize), note)

    # formatting styles
    def format_clear(self):
        selectedText = self.editor.textCursor().selectedText()
        if self.html:
            selectedText = """<span style="font-family:'{0}'; font-size:{1}pt;">{2}</span>""".format(config.font, config.fontSize, selectedText)
            self.editor.insertHtml(selectedText)
        else:
            selectedText = re.sub("<[^\n<>]*?>", "", selectedText)
            self.editor.insertPlainText(selectedText)

    def format_header1(self):
        if self.html:
            self.editor.insertHtml("<h1>{0}</h1>".format(self.editor.textCursor().selectedText()))
        else:
            self.editor.insertPlainText("<h1>{0}</h1>".format(self.editor.textCursor().selectedText()))

    def format_header2(self):
        if self.html:
            self.editor.insertHtml("<h2>{0}</h2>".format(self.editor.textCursor().selectedText()))
        else:
            self.editor.insertPlainText("<h2>{0}</h2>".format(self.editor.textCursor().selectedText()))

    def format_header3(self):
        if self.html:
            self.editor.insertHtml("<h3>{0}</h3>".format(self.editor.textCursor().selectedText()))
        else:
            self.editor.insertPlainText("<h3>{0}</h3>".format(self.editor.textCursor().selectedText()))

    def format_font(self):
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
                self.editor.insertPlainText("{0}{1}</span>".format(spanTag, self.editor.textCursor().selectedText()))

    def format_textColor(self):
        color = QColorDialog.getColor(Qt.darkRed, self)
        if color.isValid():
            if self.html:
                self.editor.setTextColor(color)
            else:
                self.editor.insertPlainText('<span style="color:{0};">{1}</span>'.format(color.name(), self.editor.textCursor().selectedText()))

    def format_textBackgroundColor(self):
        color = QColorDialog.getColor(Qt.yellow, self)
        if color.isValid():
            if self.html:
                self.editor.setTextBackgroundColor(color)
            else:
                self.editor.insertPlainText('<span style="background-color:{0};">{1}</span>'.format(color.name(), self.editor.textCursor().selectedText()))

    def format_bold(self):
        if self.html:
            # Reference: https://doc.qt.io/qt-5/qfont.html#Weight-enum
            # Bold = 75
            self.editor.setFontWeight(75)
        else:
            self.editor.insertPlainText("<b>{0}</b>".format(self.editor.textCursor().selectedText()))

    def format_italic(self):
        if self.html:
            self.editor.setFontItalic(True)
        else:
            self.editor.insertPlainText("<i>{0}</i>".format(self.editor.textCursor().selectedText()))

    def format_underline(self):
        if self.html:
            self.editor.setFontUnderline(True)
        else:
            self.editor.insertPlainText("<u>{0}</u>".format(self.editor.textCursor().selectedText()))

    def format_center(self):
        if self.html:
            self.editor.setAlignment(Qt.AlignCenter)
        else:
            self.editor.insertPlainText("<div style='text-align:center;'>{0}</div>".format(self.editor.textCursor().selectedText()))

    def format_justify(self):
        if self.html:
            self.editor.setAlignment(Qt.AlignJustify)
        else:
            self.editor.insertPlainText("<div style='text-align:justify;'>{0}</div>".format(self.editor.textCursor().selectedText()))

    def format_left(self):
        if self.html:
            self.editor.setAlignment(Qt.AlignLeft)
        else:
            self.editor.insertPlainText("<div style='text-align:left;'>{0}</div>".format(self.editor.textCursor().selectedText()))

    def format_right(self):
        if self.html:
            self.editor.setAlignment(Qt.AlignRight)
        else:
            self.editor.insertPlainText("<div style='text-align:right;'>{0}</div>".format(self.editor.textCursor().selectedText()))

    def format_custom(self):
        selectedText = self.editor.textCursor().selectedText()
        selectedText = self.customFormat(selectedText)
        if self.html:
            self.editor.insertHtml(selectedText)
        else:
            self.editor.insertPlainText(selectedText)

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
                self.parent.openFileNameLabel.text(),
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
                self.parent.directoryLabel.text(), options)
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

    def addHyperlink(self, hyperlink):
        hyperlink = '<a href="{0}">{1}</a>'.format(hyperlink, self.editor.textCursor().selectedText())
        hyperlink = """<span style="font-family:'{0}'; font-size:{1}pt;">{2}</span>""".format(config.font, config.fontSize, hyperlink)
        if self.html:
            self.editor.insertHtml(hyperlink)
        else:
            self.editor.insertPlainText(hyperlink)

    def openHyperlinkDialog(self):
        selectedText = self.editor.textCursor().selectedText()
        if selectedText:
            hyperlink = selectedText
        else:
            hyperlink = "https://BibleTools.app"
        text, ok = QInputDialog.getText(self, "UniqueBible.app",
                config.thisTranslation["noteTool_hyperlink"], QLineEdit.Normal,
                hyperlink)
        if ok and text != '':
            self.addHyperlink(text)
