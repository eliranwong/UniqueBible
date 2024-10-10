from uniquebible import config
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QDockWidget
    from PySide6.QtCore import Qt
else:
    from qtpy.QtWidgets import QDockWidget
    from qtpy.QtCore import Qt
from uniquebible.gui.NoteEditor import NoteEditorWindow

class NoteEditor(QDockWidget):

    def __init__(self, parent, noteType, noteFileName="", b=None, c=None, v=None, year=None, month=None, day=None):
        super().__init__()
        self.setWindowTitle(config.thisTranslation["note_editor"])
        self.parent, self.noteType, self.noteFileName, self.b, self.c, self.v, self.year, self.month, self.day = parent, noteType, noteFileName, b, c, v, year, month, day
        self.noteEditor = NoteEditorWindow(self, self.noteType, self.noteFileName, self.b, self.c, self.v, self.year, self.month, self.day)
        self.b, self.c, self.v = self.noteEditor.b, self.noteEditor.c, self.noteEditor.v
        self.setWidget(self.noteEditor)
        config.toggleDockWidget = self.toggleViewAction()
        self.parent.setupMenuLayout(config.menuLayout)
        # Show the dock widget around the main window
        # Options: https://doc.qt.io/qtforpython/PySide6/QtCore/Qt.html#PySide6.QtCore.PySide6.QtCore.Qt.DockWidgetArea
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.parent.addDockWidget(Qt.RightDockWidgetArea, self)
        if config.dockNoteEditorOnStartup:
            self.setFloating(False)
        else:
            self.setFloating(True)
        if config.doNotDockNoteEditorByDragging:
            self.setAllowedAreas(Qt.NoDockWidgetArea)
