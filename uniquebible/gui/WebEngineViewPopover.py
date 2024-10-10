from genericpath import isfile
import os
from uniquebible import config
import shortcut as sc
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QKeySequence, QAction, QShortcut
    from PySide6.QtWidgets import QFileDialog, QInputDialog, QLineEdit
    from PySide6.QtCore import Qt, QUrl
    from PySide6.QtWidgets import QMenu
    from PySide6.QtWebEngineCore import QWebEnginePage
    from PySide6.QtWebEngineWidgets import QWebEngineView
else:
    from qtpy.QtGui import QKeySequence
    from qtpy.QtWidgets import QFileDialog, QInputDialog, QLineEdit, QShortcut
    from qtpy.QtCore import Qt, QUrl
    from qtpy.QtWidgets import QAction, QMenu
    from qtpy.QtWebEngineWidgets import QWebEngineView, QWebEnginePage


class WebEngineViewPopover(QWebEngineView):

    def __init__(self, parent, name, source, windowTitle="", enableCloseAction=True):
        super().__init__()
        self.parent = parent
        self.name = name
        self.enableCloseAction = enableCloseAction
        self.wsName = "reader"
        self.wsFilename = ""
        self.source = source
        self.html = None
        self.setWindowTitle(windowTitle if windowTitle else "Unique Bible App")
        self.titleChanged.connect(self.popoverTextCommandChanged)
        self.page().loadFinished.connect(self.finishViewLoading)
        # add context menu (triggered by right-clicking)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.addMenuActions()
        self.setupKeyboardShortcuts()

    def setupKeyboardShortcuts(self):
        if hasattr(self.parent, "name") and self.parent.name == "workspace":
            shortcut = QShortcut(QKeySequence(sc.swapWorkspaceWithMainWindow), self)
            shortcut.activated.connect(self.parent.parent.swapWorkspaceWithMainWindow)

    def finishViewLoading(self):
        activeVerseNoColour = config.darkThemeActiveVerseColor if config.theme == "dark" else config.lightThemeActiveVerseColor
        # scroll to the study verse
        self.page().runJavaScript("var activeVerse = document.getElementById('v"+str(config.studyB)+"."+str(config.studyC)+"."+str(config.studyV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = '"+activeVerseNoColour+"'; } else if (document.getElementById('v0.0.0') != null) { document.getElementById('v0.0.0').scrollIntoView(); }")
        if not self.htmlStored:
            self.page().toHtml(self.getHtml)
    
    def load(self, url):
        try:
            filepath = url.toLocalFile()
            if os.path.isfile(filepath):
                with open(filepath, 'r', encoding='utf8') as fileObj:
                    self.html = fileObj.read()
                self.htmlStored = True
            else:
                self.htmlStored = False
        except:
            self.htmlStored = False
        super().load(url)

    def setHtml(self, html, baseUrl=QUrl()):
        if config.bibleWindowContentTransformers:
            for transformer in config.bibleWindowContentTransformers:
                html = transformer(html)
        self.html = html
        self.htmlStored = True
        super().setHtml(html, baseUrl)

    def getHtml(self, html):
        # store html in a variable when page is finished loading to facilitate file saving
        self.html = html
        self.htmlStored = True

    def popoverTextCommandChanged(self, newTextCommand):
        # reset document.title
        changeTitle = "document.title = 'UniqueBible.app';"
        self.page().runJavaScript(changeTitle)
        # run textCommandChanged from parent
        if not newTextCommand == "ePubViewer.html" and not newTextCommand.endswith(".pdf") and not newTextCommand.startswith("viewer.html"):
            #print(newTextCommand, self.source)
            config.mainWindow.textCommandChanged(newTextCommand, self.source)

    def addToWorkspaceReadOnly(self):
        if self.htmlStored:
            self.addToWorkspaceReadOnlyAction(self.html)
        else:
            self.page().toHtml(self.addToWorkspaceReadOnlyAction)

    def addToWorkspaceEditable(self):
        if self.htmlStored:
            self.addToWorkspaceEditableAction(self.html)
        else:
            self.page().toHtml(self.addToWorkspaceEditableAction)

    def addToWorkspaceReadOnlyAction(self, html):
        windowTitle = self.windowTitle() if not self.windowTitle() == "Unique Bible App" else ""
        config.mainWindow.addToWorkspaceReadOnlyAction(html, windowTitle)

    def addToWorkspaceEditableAction(self, html):
        windowTitle = self.windowTitle() if not self.windowTitle() == "Unique Bible App" else ""
        config.mainWindow.addToWorkspaceEditableAction(html, windowTitle)

    def addMenuActions(self):

        if hasattr(self.parent, "name") and self.parent.name == "workspace":
            action = QAction(self)
            action.setText(config.thisTranslation["changeWindowTitle"])
            action.triggered.connect(self.changeWindowTitle)
            self.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["openInEditor"])
            action.triggered.connect(self.openInEditor)
            self.addAction(action)
        else:
            subMenu1 = QMenu()
            action = QAction(self)
            action.setText(config.thisTranslation["readOnly"])
            action.triggered.connect(self.addToWorkspaceReadOnly)
            subMenu1.addAction(action)
            action = QAction(self)
            action.setText(config.thisTranslation["editable"])
            action.triggered.connect(self.addToWorkspaceEditable)
            subMenu1.addAction(action)

            subMenu2 = QMenu()
            action = QAction(self)
            action.setText(config.thisTranslation["readOnly"])
            action.triggered.connect(self.addTextSelectionToWorkspace)
            subMenu2.addAction(action)
            action = QAction(self)
            action.setText(config.thisTranslation["editable"])
            action.triggered.connect(lambda: self.addTextSelectionToWorkspace(editable=True))
            subMenu2.addAction(action)

            subMenu3 = QMenu()
            action = QAction(self)
            action.setText(config.thisTranslation["readOnly"])
            action.triggered.connect(self.addBibleReferencesInTextSelectionToWorkspace)
            subMenu3.addAction(action)
            action = QAction(self)
            action.setText(config.thisTranslation["editable"])
            action.triggered.connect(lambda: self.addBibleReferencesInTextSelectionToWorkspace(editable=True))
            subMenu3.addAction(action)

            subMenu = QMenu()
            action = QAction(self)
            action.setText(config.thisTranslation["all"])
            action.setMenu(subMenu1)
            subMenu.addAction(action)
            action = QAction(self)
            action.setText(config.thisTranslation["textOnly"])
            action.setMenu(subMenu2)
            subMenu.addAction(action)
            action = QAction(self)
            action.setText(config.thisTranslation["bibleReferencesInTextSelection"])
            action.setMenu(subMenu3)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["addToWorkSpace"])
            action.setMenu(subMenu)
            self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        copyText = QAction(self)
        copyText.setText(config.thisTranslation["context1_copy"])
        copyText.triggered.connect(self.copySelectedText)
        self.addAction(copyText)

        action = QAction(self)
        action.setText(config.thisTranslation["saveHtml"])
        action.triggered.connect(self.saveHtml)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        subMenu = QMenu()

        if not self.name == "popover":
            action = QAction(self)
            action.setText("{0} | {1}".format(config.thisTranslation["openOnNewWindow"], sc.displayReferenceOnNewWindowPopover))
            action.setShortcut(QKeySequence(sc.displayReferenceOnNewWindowPopover))
            action.triggered.connect(self.displayVersesInNewWindow)
            subMenu.addAction(action)

        action = QAction(self)
        action.setText("{0} | {1}".format(config.thisTranslation["bar1_menu"], sc.displayReferenceOnBibleWindowPopover))
        action.setShortcut(QKeySequence(sc.displayReferenceOnBibleWindowPopover))
        action.triggered.connect(self.displayVersesInBibleWindow)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["bottomWindow"])
        action.triggered.connect(self.displayVersesInBottomWindow)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText("{0} | {1}".format(config.thisTranslation["presentation"], sc.presentPopover))
        action.setShortcut(QKeySequence(sc.presentPopover))
        action.triggered.connect(self.displayVersesInPresentation)
        subMenu.addAction(action)

        action = QAction(self)
        action.setText(config.thisTranslation["displayVerses"])
        action.setMenu(subMenu)
        self.addAction(action)

        if hasattr(config, "macroIsRunning") and config.macroIsRunning:
            spaceBar = QAction(self)
            spaceBar.setShortcut(QKeySequence(" "))
            spaceBar.triggered.connect(self.spaceBarPressed)
            self.addAction(spaceBar)
    
            escKey = QAction(self)
            escKey.setShortcut(QKeySequence(Qt.Key_Escape))
            escKey.triggered.connect(self.escKeyPressed)
            self.addAction(escKey)

            qKey = QAction(self)
            qKey.setShortcut(QKeySequence(Qt.Key_Q))
            qKey.triggered.connect(self.qKeyPressed)
            self.addAction(qKey)
        
        subMenu = QMenu()

        action = QAction(self)
        action.setText(config.thisTranslation["bar2_menu"])
        action.triggered.connect(self.openInStudyWindow)
        subMenu.addAction(action)
        
        escKey = QAction(self)
        escKey.setText(config.thisTranslation["menu1_fullScreen"])
        escKey.setShortcut(QKeySequence(Qt.Key_Escape))
        escKey.triggered.connect(self.escKeyPressed)
        subMenu.addAction(escKey)

        action = QAction(self)
        action.setText(config.thisTranslation["displayContent"])
        action.setMenu(subMenu)
        self.addAction(action)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        action = QAction(self)
        action.setText("{0} | {1}".format(config.thisTranslation["context1_search"], sc.searchPopover))
        action.setShortcut(QKeySequence(sc.searchPopover))
        action.triggered.connect(self.searchPanel)
        self.addAction(action)
        
        runAsCommandLine = QAction(self)
        runAsCommandLine.setText("{0} | {1}".format(config.thisTranslation["context1_command"], sc.runCommandPopover))
        runAsCommandLine.setShortcut(QKeySequence(sc.runCommandPopover))
        runAsCommandLine.triggered.connect(self.runAsCommand)
        self.addAction(runAsCommandLine)

        separator = QAction(self)
        separator.setSeparator(True)
        self.addAction(separator)

        if self.enableCloseAction and not (hasattr(self.parent, "name") and self.parent.name == "workspace"):
            qKey = QAction(self)
            qKey.setText("{0} | {1}".format(config.thisTranslation["close"], sc.closePopoverWindow))
            qKey.setShortcut(QKeySequence(sc.closePopoverWindow))
            qKey.triggered.connect(self.qKeyPressed)
            self.addAction(qKey)

    def openInEditor(self):
        self.page().toPlainText(self.openInEditorAction)

    def openInEditorAction(self, plainText):
        windowTitle = self.windowTitle()
        html = config.mainWindow.htmlWrapper(plainText, parsing=True, html=False)
        self.parent.addHtmlContent(html, True, windowTitle)

    def messageNoSelection(self):
        config.mainWindow.studyView.currentWidget().displayMessage("{0}\n{1}".format(config.thisTranslation["message_run"], config.thisTranslation["selectTextFirst"]))

    def copySelectedText(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            self.page().triggerAction(QWebEnginePage.Copy)

    def displayVersesInNewWindow(self):
        selectedText = self.selectedText().strip()
        config.mainWindow.studyView.currentWidget().displayVersesInNewWindow(selectedText)
    
    def displayVersesInBibleWindow(self):
        selectedText = self.selectedText().strip()
        config.mainWindow.studyView.currentWidget().displayVersesInBibleWindow(selectedText)

    def displayVersesInBottomWindow(self):
        selectedText = self.selectedText().strip()
        config.mainWindow.studyView.currentWidget().displayVersesInBottomWindow(selectedText)

    def displayVersesInPresentation(self):
        selectedText = self.selectedText().strip()
        config.mainWindow.studyView.currentWidget().runPlugin("Presentation_Ctrl+Shift+Y", selectedText)

    def searchPanel(self):
        selectedText = self.selectedText().strip()
        config.mainWindow.studyView.currentWidget().searchPanel(selectedText)

    def openInStudyWindow(self):
        if self.name.lower().endswith("pdf"):
            openPdfViewerInNewWindow = config.openPdfViewerInNewWindow
            config.openPdfViewerInNewWindow = False
            config.mainWindow.openPdfReader(self.name, fullPath=True)
            config.openPdfViewerInNewWindow = openPdfViewerInNewWindow
        elif self.name == "EPUB":
            config.mainWindow.runPlugin("ePub Viewer")
        else:
            if self.htmlStored:
                self.openHtmlInStudyWindow(self.html)
            else:
                self.page().toHtml(self.openHtmlInStudyWindow)
        self.close()
    
    def openHtmlInStudyWindow(self, html):
        config.mainWindow.openTextOnStudyView(html, tab_title="study")

    def runAsCommand(self):
        selectedText = self.selectedText()
        config.mainWindow.textCommandChanged(selectedText, "main")

    def closeEvent(self, event):
        if hasattr(config, "macroIsRunning") and config.macroIsRunning:
            config.pauseMode = False

    def spaceBarPressed(self):
        if hasattr(config, "macroIsRunning") and config.macroIsRunning:
            config.pauseMode = False

    def qKeyPressed(self):
        if hasattr(config, "macroIsRunning") and config.macroIsRunning:
            config.quitMacro = True
            config.pauseMode = False
        self.close()

    def escKeyPressed(self):
        if self.isMaximized():
            self.showFullScreen()
        else:
            self.showMaximized()

    def saveHtml(self, fileName=""):
        if self.html is None:
            if not fileName:
                if self.htmlStored:
                    self.saveHtmlToFile(self.html)
                else:
                    self.page().toHtml(self.saveHtmlToFile)
            else:
                if self.htmlStored:
                    self.saveHtmlToFileAction(self.html, fileName)
                else:
                    self.page().toHtml(lambda html, fileName=fileName: self.saveHtmlToFileAction(html, fileName))
        else:
            if not fileName:
                self.saveHtmlToFile(self.html)
            else:
                self.saveHtmlToFileAction(self.html, fileName)

    def saveHtmlToFile(self, html):
        options = QFileDialog.Options()
        fileName, *_ = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                "",
                "HTML Files (*.html)", "", options)
        if fileName:
            if not os.path.basename(fileName).lower().endswith(".html"):
                fileName = fileName + ".html"
            self.saveHtmlToFileAction(html, fileName, True)

    def saveHtmlToFileAction(self, html, fileName, showSavedMessage=False):
        with open(fileName, "w", encoding="utf-8") as fileObj:
            fileObj.write(html)
        if showSavedMessage:
            config.mainWindow.displayMessage(config.thisTranslation["saved"])

    def changeWindowTitle(self, windowTitle=""):
        if self.parent is config.mainWindow.ws:
            if not windowTitle:
                windowTitle, ok = QInputDialog.getText(self, config.thisTranslation["changeWindowTitle"],
                        config.thisTranslation["enter_text_here"], QLineEdit.Normal,
                        "")
                if ok and windowTitle:
                    self.setWindowTitle(windowTitle)
                    self.parent.saveWorkspace()
            else:
                self.setWindowTitle(windowTitle)
                self.parent.saveWorkspace()

    def addTextSelectionToWorkspace(self, selectedText=None, editable=False):
        if not selectedText:
            selectedText = self.selectedTextProcessed()
        if selectedText:
            config.mainWindow.addTextSelectionToWorkspace(selectedText, editable)
        else:
            self.messageNoSelection()

    def addBibleReferencesInTextSelectionToWorkspace(self, selectedText=None, editable=False):
        if not selectedText:
            selectedText = self.selectedTextProcessed()
        if selectedText:
            config.mainWindow.addBibleReferencesInTextSelectionToWorkspace(selectedText, editable)
        else:
            self.messageNoSelection()

    def selectedTextProcessed(self, activeSelection=False):
        if not activeSelection:
            selectedText = self.selectedText().strip()
        else:
            selectedText = config.mainWindow.mainView.currentWidget().selectedText().strip()
            if not selectedText:
                selectedText = config.mainWindow.studyView.currentWidget().selectedText().strip()
        if not selectedText and config.commandTextIfNoSelection:
            selectedText = config.mainWindow.textCommandLineEdit.text().strip()
        if not selectedText:
            text, ok = QInputDialog.getText(config.mainWindow, "Unique Bible App",
                    config.thisTranslation["enter_text_here"], QLineEdit.Normal,
                    "")
            if ok and text:
                selectedText = text
        return selectedText

    def searchText(self, searchString):
        self.findText(searchString, QWebEnginePage.FindFlags())
