
import config, re
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QIcon
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QMainWindow, QMdiArea, QTextEdit, QToolBar
else:
    from qtpy.QtGui import QIcon
    from qtpy.QtCore import Qt
    from qtpy.QtWidgets import QMainWindow, QMdiArea, QTextEdit, QToolBar
from gui.WebEngineViewPopover import WebEngineViewPopover
from util.TextUtil import TextUtil


class Workspace(QMainWindow):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.appIcon = QIcon(config.desktopUBAIcon)
        self.setWindowIcon(self.appIcon)
        self.setWindowTitle("Unique Bible App - {0}".format(config.thisTranslation["workspace"]))

        self.mda = QMdiArea()
        self.mda.tileSubWindows()
        self.setCentralWidget(self.mda)

        self.setupMenuBarMaterial()

    def setupMenuBarMaterial(self):

        self.menuBar = QToolBar()
        self.menuBar.setWindowTitle(config.thisTranslation["workspace"])
        self.menuBar.setContextMenuPolicy(Qt.PreventContextMenu)
        # In QWidget, self.menuBar is treated as the menubar without the following line
        # In QMainWindow, the following line adds the configured QToolBar as part of the toolbar of the main window
        self.addToolBar(Qt.LeftToolBarArea, self.menuBar)

        icon = "material/file/grid_view/materialiconsoutlined/48dp/2x/outline_grid_view_black_48dp.png"
        self.parent.addMaterialIconButton("tile", icon, self.mda.tileSubWindows, self.menuBar)
        icon = "material/content/dynamic_feed/materialiconsoutlined/48dp/2x/outline_dynamic_feed_black_48dp.png"
        self.parent.addMaterialIconButton("cascade", icon, self.mda.cascadeSubWindows, self.menuBar)
        self.menuBar.addSeparator()
        icon = "material/editor/edit_note/materialiconsoutlined/48dp/2x/outline_edit_note_black_48dp.png"
        self.parent.addMaterialIconButton("textEditor", icon, lambda: self.addHtmlContent("", True, config.thisTranslation["textEditor"]), self.menuBar)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def addWidgetAsSubWindow(self, widget, windowTitle="", windowTooltip=""):
        # Display Workspace
        self.show()
        self.activateWindow()
        self.raise_()
        # Add widget to Workspace
        subWindow = self.mda.addSubWindow(widget)
        subWindow.setWindowIcon(self.appIcon)
        if windowTitle:
            subWindow.setWindowTitle(windowTitle)
        if windowTooltip:
            subWindow.setToolTip(windowTooltip)
        subWindow.show()
        subWindow.activateWindow()
        subWindow.raise_()
        # Arrange subWindows
        self.mda.tileSubWindows()

    def addHtmlContent(self, html, editable=False, windowTitle="", windowTooltip=""):
        html = config.mainWindow.wrapHtml(html)
        if editable:
            widget = QTextEdit()
            widget.setHtml(html)
        else:
            widget = WebEngineViewPopover(self, "main", "main")
            widget.setHtml(html, config.baseUrl)
        if not windowTitle:
            windowTitle = TextUtil.htmlToPlainText(html)
            windowTitle = windowTitle.replace("\n", " ")
            windowTitle = re.sub("UniqueBible.app|Unique Bible App", "", windowTitle)
            windowTitle = windowTitle.strip()
        self.addWidgetAsSubWindow(widget, windowTitle, windowTooltip)
