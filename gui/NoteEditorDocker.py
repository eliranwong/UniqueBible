import config
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QDockWidget
    from PySide6.QtCore import Qt
else:
    from qtpy.QtWidgets import QDockWidget
    from qtpy.QtCore import Qt
from gui.NoteEditor import NoteEditorWindow

class NoteEditor(QDockWidget):

    def __init__(self, parent, noteType, noteFileName="", b=None, c=None, v=None):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["note_editor"])
        self.parent, self.noteType, self.noteFileName, self.b, self.c, self.v = parent, noteType, noteFileName, b, c, v
        if not self.noteType == "file":
            if v:
                self.b, self.c, self.v = b, c, v
            else:
                self.b, self.c, self.v = config.studyB, config.studyC, config.studyV

        self.noteEditor = NoteEditorWindow(self, self.noteType, self.noteFileName, self.b, self.c, self.v)
        self.setWidget(self.noteEditor)
        config.toggleDockWidget = self.toggleViewAction()
        self.parent.setupMenuLayout(config.menuLayout)
        # Show the dock widget around the main window
        # Options: https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.DockWidgetArea
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        if config.dockNoteEditorOnStartup:
            self.parent.addDockWidget(Qt.RightDockWidgetArea, self)
            self.setFloating(False)
        else:
            self.parent.addDockWidget(Qt.RightDockWidgetArea, self)
            self.setFloating(True)
