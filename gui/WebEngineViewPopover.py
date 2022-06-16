import os
import config
import shortcut as sc
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QKeySequence, QAction
    from PySide6.QtWidgets import QFileDialog
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QMenu
    from PySide6.QtWebEngineWidgets import QWebEngineView
else:
    from qtpy.QtGui import QKeySequence
    from qtpy.QtWidgets import QFileDialog
    from qtpy.QtCore import Qt
    from qtpy.QtWidgets import QAction, QMenu
    from qtpy.QtWebEngineWidgets import QWebEngineView

class WebEngineViewPopover(QWebEngineView):

    def __init__(self, parent, name, source, windowTitle=""):
        super().__init__()
        self.parent = parent
        self.name = name
        self.source = source
        self.setWindowTitle(windowTitle if windowTitle else "Unique Bible App")
        self.titleChanged.connect(self.popoverTextCommandChanged)
        self.page().loadFinished.connect(self.finishViewLoading)
        # add context menu (triggered by right-clicking)
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.addMenuActions()

    def finishViewLoading(self):
        activeVerseNoColour = config.darkThemeActiveVerseColor if config.theme == "dark" else config.lightThemeActiveVerseColor
        # scroll to the study verse
        self.page().runJavaScript("var activeVerse = document.getElementById('v"+str(config.studyB)+"."+str(config.studyC)+"."+str(config.studyV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = '"+activeVerseNoColour+"'; } else if (document.getElementById('v0.0.0') != null) { document.getElementById('v0.0.0').scrollIntoView(); }")

    def popoverTextCommandChanged(self, newTextCommand):
        # reset document.title
        changeTitle = "document.title = 'UniqueBible.app';"
        self.page().runJavaScript(changeTitle)
        # run textCommandChanged from parent
        if not newTextCommand == "ePubViewer.html" and not newTextCommand.endswith(".pdf") and not newTextCommand.startswith("viewer.html"):
            config.mainWindow.textCommandChanged(newTextCommand, self.source)

    def addToWorkspaceReadOnly(self):
        self.page().toHtml(self.addToWorkspaceReadOnlyAction)

    def addToWorkspaceEditable(self):
        self.page().toHtml(self.addToWorkspaceEditableAction)

    def addToWorkspaceReadOnlyAction(self, html):
        windowTitle = self.windowTitle() if not self.windowTitle() == "Unique Bible App" else ""
        config.mainWindow.addToWorkspaceReadOnlyAction(html, windowTitle)

    def addToWorkspaceEditableAction(self, html):
        windowTitle = self.windowTitle() if not self.windowTitle() == "Unique Bible App" else ""
        config.mainWindow.addToWorkspaceEditableAction(html, windowTitle)

    def addMenuActions(self):

        if not self.parent is config.mainWindow.ws:
            subMenu = QMenu()

            action = QAction(self)
            action.setText(config.thisTranslation["readOnly"])
            action.triggered.connect(self.addToWorkspaceReadOnly)
            subMenu.addAction(action)

            action = QAction(self)
            action.setText(config.thisTranslation["editable"])
            action.triggered.connect(self.addToWorkspaceEditable)
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

        qKey = QAction(self)
        qKey.setText("{0} | {1}".format(config.thisTranslation["close"], sc.closePopoverWindow))
        qKey.setShortcut(QKeySequence(sc.closePopoverWindow))
        qKey.triggered.connect(self.qKeyPressed)
        self.addAction(qKey)

    def messageNoSelection(self):
        config.mainWindow.studyView.currentWidget().displayMessage("{0}\n{1}".format(config.thisTranslation["message_run"], config.thisTranslation["selectTextFirst"]))

    def copySelectedText(self):
        if not self.selectedText():
            self.messageNoSelection()
        else:
            self.page().triggerAction(self.page().Copy)

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

    def saveHtml(self):
        self.page().toHtml(self.saveHtmlToFile)

    def saveHtmlToFile(self, html):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                "",
                "HTML Files (*.html)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".html"
            file = open(fileName, "w")
            file.write(html)
            file.close()
            config.mainWindow.studyView.currentWidget().displayMessage(config.thisTranslation["saved"])

    def addToWorkspaceReadOnly(self):
        self.page().toHtml(self.addToWorkspaceReadOnlyAction)

    def addToWorkspaceEditable(self):
        self.page().toHtml(self.addToWorkspaceEditableAction)
