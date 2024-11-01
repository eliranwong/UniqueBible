from uniquebible import config
import re, os, base64, glob, webbrowser, markdown
from datetime import datetime
import uniquebible.shortcut as sc
from uniquebible.util.SystemUtil import SystemUtil

if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QIcon, QKeySequence, QShortcut
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import QMainWindow, QMdiArea, QToolBar, QFileDialog, QInputDialog, QLineEdit, QMessageBox
else:
    from qtpy.QtGui import QIcon, QKeySequence
    from qtpy.QtCore import Qt, QTimer
    from qtpy.QtWidgets import QMainWindow, QMdiArea, QToolBar, QFileDialog, QInputDialog, QLineEdit, QMessageBox, QShortcut
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
from uniquebible.gui.MiniTextEditor import MiniTextEditor
from uniquebible.util.TextUtil import TextUtil
from uniquebible.util.ThirdParty import Converter


class Workspace(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.exemptSaving = True
        self.parent = parent
        self.name = "workspace"

        self.appIcon = QIcon(config.desktopUBAIcon)
        self.setWindowIcon(self.appIcon)
        self.updateWindowTitle()

        self.mda = QMdiArea()
        self.mda.tileSubWindows()
        self.setCentralWidget(self.mda)

        if config.menuLayout == "material":
            self.setupMenuBarMaterial()

        # load last saved content
        self.loadWorkspaceFiles()

        self.setupKeyboardShortcuts()

        # Automate saving
        self.lastChangeTime = datetime.now()
        self.mda.subWindowActivated.connect(self.autoSaveTimer)
        self.exemptSaving = False

    def autoSaveTimer(self):
        self.lastChangeTime = datetime.now()
        lastChangeTime = self.lastChangeTime
        # Run auto-save 2 seconds after active changes in sub-window activation were made.
        QTimer.singleShot(2000, lambda: self.autoSaveChanges(lastChangeTime))

    def autoSaveChanges(self, lastChangeTime):
        if lastChangeTime == self.lastChangeTime and self.isVisible():
            #print("Save changes now")
            self.saveWorkspace()

    def setupKeyboardShortcuts(self):
        shortcut = QShortcut(QKeySequence(sc.swapWorkspaceWithMainWindow), self)
        shortcut.activated.connect(self.parent.swapWorkspaceWithMainWindow)

    def updateWindowTitle(self):
        self.setWindowTitle("Unique Bible App - {0} - {1}".format(config.thisTranslation["workspace"], os.path.basename(config.workspaceDirectory)))

    def setupMenuBarMaterial(self):

        menuBar = QToolBar()
        menuBar.setWindowTitle(config.thisTranslation["workspace"])
        menuBar.setContextMenuPolicy(Qt.PreventContextMenu)
        # In QWidget, menuBar is treated as the menubar without the following line
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(Qt.LeftToolBarArea, menuBar)

        icon = "material/navigation/refresh/materialiconsoutlined/48dp/2x/outline_refresh_black_48dp.png"
        self.parent.addMaterialIconButton("menu1_reload", icon, self.refreshWorkspace, menuBar)
        icon = "material/file/folder/materialiconsoutlined/48dp/2x/outline_folder_black_48dp.png"
        self.parent.addMaterialIconButton("loadWorkspaceFromDirectory", icon, self.changeWorkspaceDirectory, menuBar)
        icon = "material/file/drive_file_move/materialiconsoutlined/48dp/2x/outline_drive_file_move_black_48dp.png"
        self.parent.addMaterialIconButton("saveWorkspaceInDirectory", icon, self.saveAsWorkspaceDirectory, menuBar)
        icon = "material/action/book/materialiconsoutlined/48dp/2x/outline_book_black_48dp.png"
        self.parent.addMaterialIconButton("createReferenceBookFromWorkspace", icon, self.createBookModuleFromWorkspace, menuBar)
        menuBar.addSeparator()
        icon = "material/file/grid_view/materialiconsoutlined/48dp/2x/outline_grid_view_black_48dp.png"
        self.parent.addMaterialIconButton("tile", icon, self.tileSubWindows, menuBar)
        icon = "material/content/dynamic_feed/materialiconsoutlined/48dp/2x/outline_dynamic_feed_black_48dp.png"
        self.parent.addMaterialIconButton("cascade", icon, self.cascadeSubWindows, menuBar)
        icon = "material/communication/cancel_presentation/materialiconsoutlined/48dp/2x/outline_cancel_presentation_black_48dp.png"
        self.parent.addMaterialIconButton("clearAll", icon, self.clearWorkspace, menuBar)
        menuBar.addSeparator()
        icon = "material/editor/edit_note/materialiconsoutlined/48dp/2x/outline_edit_note_black_48dp.png"
        self.parent.addMaterialIconButton("textEditor", icon, lambda: self.addHtmlContent("", True, config.thisTranslation["textEditor"]), menuBar)
        menuBar.addSeparator()
        icon = "material/action/assignment/materialiconsoutlined/48dp/2x/outline_assignment_black_48dp.png"
        self.parent.addMaterialIconButton("openDocumentInReader", icon, self.extractTextFromDocument, menuBar)
        icon = "material/device/note_alt/materialiconsoutlined/48dp/2x/outline_note_alt_black_48dp.png"
        self.parent.addMaterialIconButton("openDocumentInEditor", icon, lambda: self.extractTextFromDocument(True), menuBar)
        menuBar.addSeparator()
        icon = "material/editor/insert_photo/materialiconsoutlined/48dp/2x/outline_insert_photo_black_48dp.png"
        self.parent.addMaterialIconButton("insertImageIntoReader", icon, self.openImageDialog, menuBar)
        icon = "material/device/wallpaper/materialiconsoutlined/48dp/2x/outline_wallpaper_black_48dp.png"
        self.parent.addMaterialIconButton("insertImageIntoEditor", icon, lambda: self.openImageDialog(True), menuBar)
        menuBar.addSeparator()
        icon = "material/image/auto_fix_normal/materialiconsoutlined/48dp/2x/outline_auto_fix_normal_black_48dp.png"
        self.parent.addMaterialIconButton("instantHighlight", icon, self.instantHighlight, menuBar)
        icon = "material/image/auto_fix_off/materialiconsoutlined/48dp/2x/outline_auto_fix_off_black_48dp.png"
        self.parent.addMaterialIconButton("removeInstantHighlight", icon, self.removeInstantHighlight, menuBar)
        menuBar.addSeparator()
        icon = "material/hardware/keyboard_return/materialiconsoutlined/48dp/2x/outline_keyboard_return_black_48dp.png"
        self.parent.addMaterialIconButton("mainInterface", icon, self.parent.showFromTray, menuBar)
        menuBar.addSeparator()
        icon = "material/action/help_outline/materialiconsoutlined/48dp/2x/outline_help_outline_black_48dp.png"
        self.parent.addMaterialIconButton("help", icon, lambda: webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/Workspace"), menuBar)

    def tileSubWindows(self):
        self.exemptSaving = True
        self.mda.tileSubWindows()
        self.exemptSaving = False

    def cascadeSubWindows(self):
        self.exemptSaving = True
        self.mda.cascadeSubWindows()
        self.exemptSaving = False

    def closeEvent(self, event):
        event.ignore()
        self.saveWorkspace()
        self.exemptSaving = True
        self.hide()
        self.exemptSaving = True

    def addWidgetAsSubWindow(self, widget, windowTitle="", windowTooltip="", autoSave=True):
        self.exemptSaving = True
        # Display Workspace
        self.show()
        if not SystemUtil.isWayland():
            self.activateWindow()
        self.raise_()
        # Add widget to Workspace
        subWindow = self.mda.addSubWindow(widget)
        subWindow.setWindowIcon(self.appIcon)
        if windowTitle:
            if config.limitWorkspaceFilenameLength and len(windowTitle) > 20:
                windowTitle = windowTitle[:20]
            widget.setWindowTitle(windowTitle)
        if windowTooltip:
            widget.setToolTip(windowTooltip)
        subWindow.show()
        if not SystemUtil.isWayland():
            subWindow.activateWindow()
        subWindow.raise_()
        # set cursor focus
        if hasattr(widget, "wsName") and widget.wsName == "editor":
            widget.editor.setFocus()
        # Arrange subWindows
        self.mda.tileSubWindows()
        # Auto-save file
        self.exemptSaving = False
        if autoSave:
            #self.saveWorkspace()
            QTimer.singleShot(1000, self.saveWorkspace)

    def addHtmlContent(self, html, editable=False, windowTitle="", windowTooltip="", autoSave=True):
        #html = self.parent.wrapHtml(html)
        if editable:
            widget = MiniTextEditor(self)
            widget.setHtml(html)
        else:
            widget = WebEngineViewPopover(self, "main", "main")
            widget.setHtml(html, config.baseUrl)
        if not windowTitle:
            windowTitle = TextUtil.htmlToPlainText(html)
            windowTitle = windowTitle.replace("\n", " ")
            windowTitle = re.sub("UniqueBible.app|Unique Bible App", "", windowTitle)
            windowTitle = windowTitle.strip()
        self.addWidgetAsSubWindow(widget, windowTitle, windowTooltip, autoSave=autoSave)

    def extractTextFromDocument(self, editable=False):
        extensions = ("txt", "uba", "md", "csv", "doc", "docx", "eml", "epub", "gif", "jpg", "jpeg", "json", "html", "htm", "mp3", "msg", "odt", "ogg", "pdf", "png", "pptx", "ps", "rtf", "tiff", "tif", "wav", "xlsx", "xls")
        filters = ["{0} Files (*.{1})".format(extension.upper(), extension) for extension in extensions]

        options = QFileDialog.Options()
        fileName, *_ = QFileDialog.getOpenFileName(self,
                                                    config.thisTranslation["menu7_open"],
                                                    config.mainWindow.openFileNameLabel.text(),
                                                    ";;".join(filters),
                                                    "", options)
        if fileName:
            if fileName.lower().endswith(".uba") or fileName.lower().endswith(".html") or fileName.lower().endswith(".htm") or fileName.lower().endswith(".md"):
                with open(fileName, "r", encoding="utf-8") as fileObj:
                    html = fileObj.read()
                if fileName.lower().endswith(".md"):
                    html = markdown.markdown(html)
                html = self.fixNoteFont(html)
                html = config.mainWindow.htmlWrapper(html, True, html=False if fileName.lower().endswith(".md") else True)
            else:
                try:
                    import textract
                    html = textract.process(fileName).decode()
                    html = config.mainWindow.htmlWrapper(html, True, html=False)
                except:
                    self.parent.displayMessage("Optional package 'textract' is not installed!")
            self.addHtmlContent(html, editable, os.path.basename(fileName))

    def fixNoteFont(self, note):
        note = re.sub("<body style={0}[ ]*?font-family:[ ]*?'[^']*?';[ ]*?font-size:[ ]*?[0-9]+?pt;".format('"'), "<body style={0}font-family:'{1}'; font-size:{2}pt;".format('"', config.font, config.fontSize), note)
        if not config.includeStrictDocTypeInNote:
            note = re.sub("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n""", "", note)
        return note

    def openVideoDialog(self):
        options = QFileDialog.Options()
        fileName, *_ = QFileDialog.getOpenFileName(self,
                config.thisTranslation["html_open"],
                config.mainWindow.openFileNameLabel.text(),
                "MP4 Video (*.mp4);;All Files (*)", "", options)
        if fileName:
            self.openVideo(fileName)

    def openVideo(self, fileName):
        name, extension = os.path.splitext(os.path.basename(fileName))
        html = """
<video controls>
  <source src="{0}" type="video/mp4">
Your browser does not support the video tag.
</video>""".format(fileName) if extension.lower() == ".mp4" else ""
        if html:
            self.addHtmlContent(html, False, name)

    def openImageDialog(self, editable=False):
        options = QFileDialog.Options()
        fileName, *_ = QFileDialog.getOpenFileName(self,
                config.thisTranslation["html_open"],
                config.mainWindow.openFileNameLabel.text(),
                "JPG Files (*.jpg);;JPEG Files (*.jpeg);;PNG Files (*.png);;GIF Files (*.gif);;BMP Files (*.bmp);;All Files (*)", "", options)
        if fileName:
            self.openImage(fileName, editable)

    def openImage(self, fileName, editable=False):
        name, extension = os.path.splitext(os.path.basename(fileName))
        with open(fileName, "rb") as fileObject:
            binaryData = fileObject.read()
            encodedData = base64.b64encode(binaryData)
            asciiString = encodedData.decode('ascii')
            imageTag = '<img src="data:image/{2};base64,{0}" alt="{1}">'.format(asciiString, name, extension[1:])
            html = config.mainWindow.htmlWrapper(imageTag, parsing=False, linebreak=False, html=False)
            self.addHtmlContent(html, editable, name)

    def getWorkspaceFiles(self, folderName=""):
        if not folderName:
            folderName = config.workspaceDirectory
        fileList = glob.glob(os.path.join(folderName, "uba_ws_*.reader")) + glob.glob(os.path.join(folderName, "uba_ws_*.editor"))
        wsFiles = [fileName for fileName in sorted(fileList)] if fileList else []
        return wsFiles

    def getDirectory(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["workspaceDirectory"],
                                                     config.workspaceDirectory, options)
        return directory if directory else ""

    def changeWorkspaceDirectory(self):
        directory = self.getDirectory()
        if directory:
            config.workspaceDirectory = directory
            self.updateWindowTitle()
            self.mda.closeAllSubWindows()
            self.loadWorkspaceFiles()

    def clearWorkspaceWarning(self):
        msgBox = QMessageBox(QMessageBox.Warning,
                             config.thisTranslation["attention"],
                             config.thisTranslation["warnCloseAllWindows"],
                             QMessageBox.NoButton, self)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        msgBox.addButton("&Continue", QMessageBox.AcceptRole)
        answer = msgBox.exec_()
        if True:
        #if answer == 1 or answer == QMessageBox.AcceptRole:
            # Continue
            return True
        else:
            # Cancel
            return False

    def clearWorkspace(self):
        if self.clearWorkspaceWarning():
            self.mda.closeAllSubWindows()
            self.deleteWorkspaceFiles(config.workspaceDirectory)

    def refreshWorkspace(self):
        self.exemptSaving = True
        self.mda.closeAllSubWindows()
        self.loadWorkspaceFiles()
        self.exemptSaving = False

    def saveAsWorkspaceDirectory(self):
        directory = self.getDirectory()
        if directory:
            # Set config value
            config.workspaceDirectory = directory
            self.updateWindowTitle()
            # Save Files
            self.saveWorkspace()
            # Notify about saving
            # Do not remove this line for reloading to work
            # Without this line, windows close before reader html is saved, as *.page().toHtml() takes time
            # Workaround is to get the html codes ready when page is finished loading.  We implement this workaround in WebEngineViewPopover.py
            #self.parent.displayMessage(config.thisTranslation["message_done"])
            # Reload according to the saving order
            self.refreshWorkspace()

    def loadWorkspaceFiles(self, folderName=""):
        self.exemptSaving = True
        if not folderName:
            folderName = config.workspaceDirectory
        for fileName in self.getWorkspaceFiles(folderName):
            with open(fileName, "r", encoding="utf-8") as fileObj:
                html = fileObj.read()
            editable = True if fileName.endswith(".editor") else False
            windowTitle = os.path.basename(fileName)[10:-7]
            self.addHtmlContent(html, editable, windowTitle, autoSave=False)
        self.exemptSaving = False

    def deleteWorkspaceFiles(self, folderName=""):
        if not folderName:
            folderName = config.workspaceDirectory
        for fileName in self.getWorkspaceFiles(folderName):
            os.remove(fileName)

    def createBookModuleFromWorkspace(self, folderName=""):
        if not folderName:
            folderName = config.workspaceDirectory
        if Converter().createBookModuleFromNotes(folderName, workspace=True):
            self.parent.reloadResources()
            bookFileName = "{0}.book".format(os.path.basename(folderName))
            self.parent.displayMessage("{0}\n{1}".format(config.thisTranslation["fileCreated"], bookFileName))
        else:
            self.parent.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def saveWorkspace(self, folderName=""):
        if not self.exemptSaving:
            self.exemptSaving = True
            if not folderName or not isinstance(folderName, str):
                folderName = config.workspaceDirectory
            self.deleteWorkspaceFiles(folderName)
            savingOrder = {
                0: QMdiArea.WindowOrder.CreationOrder,
                1: QMdiArea.WindowOrder.StackingOrder,
                2: QMdiArea.WindowOrder.ActivationHistoryOrder,
            }
            for index, subWindow in enumerate(self.mda.subWindowList(order=savingOrder[config.workspaceSavingOrder])):
                widget = subWindow.widget()
                if hasattr(widget, "wsName"):
                    windowTitle = widget.windowTitle()
                    if config.limitWorkspaceFilenameLength and len(windowTitle) > 20:
                        windowTitle = windowTitle[:20]
                    fileName = "uba_ws_{3}{0}_{1}.{2}".format(index, windowTitle, widget.wsName, "0" if index < 10 else "")
                    fileName = os.path.join(folderName, fileName)
                    widget.saveHtml(fileName)
                    widget.wsFilename = fileName
            self.exemptSaving = False
            self.statusBar().showMessage(config.thisTranslation["saved"], 2000)

    def getSearchString(self):
        searchString, ok = QInputDialog.getText(self, config.thisTranslation["instantHighlight"],
                config.thisTranslation["enter_text_here"], QLineEdit.Normal,
                "")
        return searchString if ok and searchString else ""

    def instantHighlight(self):
        searchString = self.getSearchString()
        if searchString:
            for subWindow in self.mda.subWindowList():
                widget = subWindow.widget()
                if hasattr(widget, "wsName"):
                    widget.searchText(searchString)

    def removeInstantHighlight(self):
        for subWindow in self.mda.subWindowList():
            widget = subWindow.widget()
            if hasattr(widget, "wsName"):
                widget.searchText("")