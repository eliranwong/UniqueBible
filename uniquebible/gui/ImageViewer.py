#############################################################################
## 
## The Image Viewer here modified Qt official example "Image Viewer"
## For Qt code licensing, read https://www.qt.io/licensing/
## Major changes:
## * changed layout
## * hide menu
## * added support of PySide2 or PyQt5 via qtpy
## * added method _fit_to_window_KeepAspectRatio
## * added method _save_as_alternative
## * added method _open_alternative
## * added loading images from a list
## * modified method _save_file
## 
#############################################################################

from uniquebible import config
import os

if config.qtLibrary == "pyside6":
    from PySide6.QtPrintSupport import QPrintDialog, QPrinter
    from PySide6.QtWidgets import (QPushButton, QWidget, QApplication, QDialog, QFileDialog, QLabel,
                                QMainWindow, QMessageBox, QScrollArea,
                                QSizePolicy, QHBoxLayout, QVBoxLayout, QComboBox)
    from PySide6.QtGui import (QColorSpace, QGuiApplication,
                            QImageReader, QImageWriter, QKeySequence,
                            QPalette, QPainter, QPixmap)
    from PySide6.QtCore import QDir, QStandardPaths, Qt, Slot, QByteArray
else:
    from qtpy.QtPrintSupport import QPrintDialog, QPrinter
    from qtpy.QtWidgets import (QPushButton, QWidget, QApplication, QDialog, QFileDialog, QLabel,
                                QMainWindow, QMessageBox, QScrollArea,
                                QSizePolicy, QHBoxLayout, QVBoxLayout, QComboBox)
    from qtpy.QtGui import (QColorSpace, QGuiApplication,
                            QImageReader, QImageWriter, QKeySequence,
                            QPalette, QPainter, QPixmap)
    from qtpy.QtCore import QDir, QStandardPaths, Qt, Slot, QByteArray

ABOUT = """<p>The <b>Image Viewer</b> example shows how to combine QLabel
and QScrollArea to display an image. QLabel is typically used
for displaying a text, but it can also display an image.
QScrollArea provides a scrolling view around another widget.
If the child widget exceeds the size of the frame, QScrollArea
automatically provides scroll bars. </p><p>The example
demonstrates how QLabel's ability to scale its contents
(QLabel.scaledContents), and QScrollArea's ability to
automatically resize its contents
(QScrollArea.widgetResizable), can be used to implement
zooming and scaling features. </p><p>In addition the example
shows how to use QPainter to print an image.</p>
"""


class ImageViewer(QMainWindow):
    def __init__(self, parent=None, showLoadImageButton=False, showImageListView=False, imageListViewItems=None, initialScrollIndex=None):
        super().__init__(parent)
        self.parent = parent
        self.imageListViewItems = imageListViewItems
        self.setupVariables()
        self.setupUI(showLoadImageButton, showImageListView)

        if initialScrollIndex is not None:
            self.imageListView.setCurrentIndex(initialScrollIndex)

        if self._scale_factor < 1.0:
            self._normal_size()

    def setupVariables(self):
        self._scale_factor = 1.0
        self._first_file_dialog = True

    def setupUI(self, showLoadImageButton, showImageListView):
        widget = QWidget()
        layout000 = QVBoxLayout()
        widget.setLayout(layout000)

        self._image_label = QLabel()
        self._image_label.setBackgroundRole(QPalette.Base)
        self._image_label.setSizePolicy(QSizePolicy.Ignored,
                                       QSizePolicy.Ignored)
        self._image_label.setScaledContents(True)

        self._scroll_area = QScrollArea()
        self._scroll_area.setBackgroundRole(QPalette.Dark)
        self._scroll_area.setWidget(self._image_label)
        #self._scroll_area.setVisible(False)
        self._scroll_area.setVisible(True)

        if showImageListView and self.imageListViewItems:
            prevButton = QPushButton("＜")
            prevButton.setToolTip(config.thisTranslation["previous"])
            prevButton.clicked.connect(self._open_previous_image)
            nextButton = QPushButton("＞")
            nextButton.setToolTip(config.thisTranslation["next"])
            nextButton.clicked.connect(self._open_next_image)
            self.titleList = []
            self.tooltipList = []
            for title, filepath in self.imageListViewItems:
                self.titleList.append(title)
                filepath = filepath.split("/")
                filepath = os.path.join(os.getcwd(), config.marvelData, *filepath)
                self.tooltipList.append(filepath)
            self.imageListView = QComboBox()
            self.imageListView.addItems(self.titleList)
            for index, tooltip in enumerate(self.tooltipList):
                self.imageListView.setItemData(index, tooltip, Qt.ToolTipRole)
            self.imageListView.currentIndexChanged.connect(self.loadSelectedItem)
        if showLoadImageButton:
            openButton = QPushButton(config.thisTranslation["loadImage"])
            openButton.clicked.connect(self._open_alternative)
        zoomInButton = QPushButton(config.thisTranslation["zoomIn"])
        zoomInButton.clicked.connect(self._zoom_in)
        zoomOutButton = QPushButton(config.thisTranslation["zoomOut"])
        zoomOutButton.clicked.connect(self._zoom_out)
        normalSizeButton = QPushButton(config.thisTranslation["actualSize"])
        normalSizeButton.clicked.connect(self._normal_size)
        fitWindowSizeButton = QPushButton(config.thisTranslation["fitToWindow"])
        fitWindowSizeButton.clicked.connect(self._fit_to_window_KeepAspectRatio)
        saveAsButton = QPushButton(config.thisTranslation["note_saveAs"])
        saveAsButton.clicked.connect(self._save_as_alternative)

        buttonLayout = QHBoxLayout()
        if showImageListView and self.imageListViewItems:
            buttonLayout.addWidget(prevButton)
            buttonLayout.addWidget(self.imageListView)
            buttonLayout.addWidget(nextButton)
        buttonLayout.addStretch()
        if showLoadImageButton:
            buttonLayout.addWidget(openButton)
        buttonLayout.addWidget(normalSizeButton)
        buttonLayout.addWidget(fitWindowSizeButton)
        buttonLayout.addWidget(zoomInButton)
        buttonLayout.addWidget(zoomOutButton)
        buttonLayout.addWidget(saveAsButton)
        layout000.addLayout(buttonLayout)
        layout000.addWidget(self._scroll_area)

        self.setCentralWidget(widget)
        #self._create_actions()
        self.resize(QGuiApplication.primaryScreen().availableSize() * 3 / 4)
    
    def show(self):
        super().show()
        if hasattr(self, "imageListView") and self.imageListViewItems:
            self.load_file(self.tooltipList[0])

    def loadSelectedItem(self, index):
        filepath = self.tooltipList[index]
        self.load_file(filepath)

    @Slot()
    def _open_previous_image(self):
        index = self.imageListView.currentIndex()
        index -= 1
        if index < 0:
            index = len(self.imageListViewItems) - 1
        self.imageListView.setCurrentIndex(index)

    @Slot()
    def _open_next_image(self):
        index = self.imageListView.currentIndex()
        index += 1
        if index >= len(self.imageListViewItems):
            index = 0
        self.imageListView.setCurrentIndex(index)

    def load_file(self, fileName):
        reader = QImageReader(fileName)
        reader.setAutoTransform(True)
        new_image = reader.read()
        native_filename = QDir.toNativeSeparators(fileName)
        if new_image.isNull():
            error = reader.errorString()
            QMessageBox.information(self, QGuiApplication.applicationDisplayName(),
                                    f"Cannot load {native_filename}: {error}")
            return False
        self._set_image(new_image)
        self.setWindowFilePath(fileName)

        w = self._image.width()
        h = self._image.height()
        d = self._image.depth()
        color_space = self._image.colorSpace()
        try:
            description = color_space.description() if color_space.isValid() else "unknown"
        except:
            description = "unknown"
        message = f'Opened "{native_filename}", {w}x{h}, Depth: {d} ({description})'
        self.statusBar().showMessage(message)
        return True

    def _set_image(self, new_image):
        self._image = new_image
        if self._image.colorSpace().isValid():
            self._image.convertToColorSpace(QColorSpace.SRgb)
        self._image_label.setPixmap(QPixmap.fromImage(self._image))

        self._scroll_area.setVisible(True)
        #self._print_act.setEnabled(True)
        #self._fit_to_window_act.setEnabled(True)
        #self._update_actions()

        #if not self._fit_to_window_act.isChecked():
        #    self._image_label.adjustSize()

        #self._scale_factor = 1.0
        #self._image_label.adjustSize()
        self._fit_to_window_KeepAspectRatio()

    def _save_file(self, fileName):
        writer = QImageWriter(fileName)
        fileExtension = fileName.split(".")[-1].lower()
        if fileExtension in ("bmp", "jpg", "jpeg", "png", "pbm", "pgm", "ppm", "xbm", "xpm"):
            writer.setFormat(fileExtension.encode("ASCII"))
        else:
            fileName = "{0}.png".format(fileName)
            writer.setFormat(QByteArray("png".encode('ASCII')))

        native_filename = QDir.toNativeSeparators(fileName)
        if not writer.write(self._image):
            error = writer.errorString()
            message = f"Cannot write {native_filename}: {error}"
            QMessageBox.information(self, QGuiApplication.applicationDisplayName(),
                                    message)
            return False
        self.statusBar().showMessage(f'Wrote "{native_filename}"')
        return True

    @Slot()
    def _open(self):
        dialog = QFileDialog(self, "Open File")
        self._initialize_image_filedialog(dialog, QFileDialog.AcceptOpen)
        while (dialog.exec() == QDialog.Accepted
               and not self.load_file(dialog.selectedFiles()[0])):
            pass

    @Slot()
    def _open_alternative(self):
        options = QFileDialog.Options()
        fileName, *_ = QFileDialog.getOpenFileName(self,
                config.thisTranslation["menu7_open"],
                "",
                "Portable Network Graphics (*.png);;"
                "Joint Photographic Experts Group (*.jpg);;"
                "Joint Photographic Experts Group (*.jpeg);;"
                "Windows Bitmap (*.bmp);;"
                "Portable Bitmap (*.pbm);;"
                "Portable Graymap (*.pgm);;"
                "Portable Pixmap (*.ppm);;"
                "X11 Bitmap (*.xbm);;"
                "X11 Pixmap (*.xpm)", "", options)
        if fileName:
            self.load_file(fileName)

    @Slot()
    def _save_as(self):
        dialog = QFileDialog(self, "Save File As")
        self._initialize_image_filedialog(dialog, QFileDialog.AcceptSave)
        while (dialog.exec() == QDialog.Accepted
               and not self._save_file(dialog.selectedFiles()[0])):
            pass

    @Slot()
    def _save_as_alternative(self):
        defaultName = "image"
        options = QFileDialog.Options()
        fileName, *_ = QFileDialog.getSaveFileName(self,
                config.thisTranslation["note_saveAs"],
                defaultName,
                "Portable Network Graphics (*.png);;"
                "Joint Photographic Experts Group (*.jpg);;"
                "Joint Photographic Experts Group (*.jpeg);;"
                "Windows Bitmap (*.bmp);;"
                "Portable Bitmap (*.pbm);;"
                "Portable Graymap (*.pgm);;"
                "Portable Pixmap (*.ppm);;"
                "X11 Bitmap (*.xbm);;"
                "X11 Pixmap (*.xpm);;"
                "All Files (*)", "", options)
        if fileName:
            if not "." in os.path.basename(fileName):
                fileName = fileName + ".png"
            self._save_file(fileName)

    @Slot()
    def _print_(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec() == QDialog.Accepted:
            with QPainter(printer) as painter:
                pixmap = self._image_label.pixmap()
                rect = painter.viewport()
                size = pixmap.size()
                size.scale(rect.size(), Qt.KeepAspectRatio)
                painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
                painter.setWindow(pixmap.rect())
                painter.drawPixmap(0, 0, pixmap)

    @Slot()
    def _copy(self):
        QGuiApplication.clipboard().setImage(self._image)

    @Slot()
    def _paste(self):
        new_image = QGuiApplication.clipboard().image()
        if new_image.isNull():
            self.statusBar().showMessage("No image in clipboard")
        else:
            self._set_image(new_image)
            self.setWindowFilePath('')
            w = new_image.width()
            h = new_image.height()
            d = new_image.depth()
            message = f"Obtained image from clipboard, {w}x{h}, Depth: {d}"
            self.statusBar().showMessage(message)

    @Slot()
    def _zoom_in(self):
        self._scale_image(1.25)

    @Slot()
    def _zoom_out(self):
        self._scale_image(0.8)

    @Slot()
    def _normal_size(self):
        self._image_label.adjustSize()
        self._scale_factor = 1.0

    @Slot()
    def _fit_to_window(self):
        # The following codes stretches the image and fit the window, but it does not keep the aspect ratio.
        fit_to_window = self._fit_to_window_act.isChecked()
        self._scroll_area.setWidgetResizable(fit_to_window)
        if not fit_to_window:
            self._normal_size()
        #self._update_actions()

    @Slot()
    def _fit_to_window_KeepAspectRatio(self):
        pixmap = self._image_label.pixmap()
        size = pixmap.size()
        actualHeight = size.height()
        size.scale(self._scroll_area.size(), Qt.KeepAspectRatio)
        self._image_label.resize(size)
        #self._scroll_area.setWidgetResizable(True)
        #print(self._scale_factor)
        self._scale_factor = float(size.height() / actualHeight)
        #print(self._scale_factor)

    @Slot()
    def _about(self):
        QMessageBox.about(self, "About Image Viewer", ABOUT)

    def _create_actions(self):
        file_menu = self.menuBar().addMenu("&File")

        self._open_act = file_menu.addAction("&Open...")
        self._open_act.triggered.connect(self._open)
        self._open_act.setShortcut(QKeySequence.Open)

        self._save_as_act = file_menu.addAction("&Save As...")
        self._save_as_act.triggered.connect(self._save_as)
        self._save_as_act.setEnabled(False)

        self._print_act = file_menu.addAction("&Print...")
        self._print_act.triggered.connect(self._print_)
        self._print_act.setShortcut(QKeySequence.Print)
        self._print_act.setEnabled(False)

        file_menu.addSeparator()

        self._exit_act = file_menu.addAction("E&xit")
        self._exit_act.triggered.connect(self.close)
        self._exit_act.setShortcut("Ctrl+Q")

        edit_menu = self.menuBar().addMenu("&Edit")

        self._copy_act = edit_menu.addAction("&Copy")
        self._copy_act.triggered.connect(self._copy)
        self._copy_act.setShortcut(QKeySequence.Copy)
        self._copy_act.setEnabled(False)

        self._paste_act = edit_menu.addAction("&Paste")
        self._paste_act.triggered.connect(self._paste)
        self._paste_act.setShortcut(QKeySequence.Paste)

        view_menu = self.menuBar().addMenu("&View")

        self._zoom_in_act = view_menu.addAction("Zoom &In (25%)")
        self._zoom_in_act.setShortcut(QKeySequence.ZoomIn)
        self._zoom_in_act.triggered.connect(self._zoom_in)
        self._zoom_in_act.setEnabled(False)

        self._zoom_out_act = view_menu.addAction("Zoom &Out (25%)")
        self._zoom_out_act.triggered.connect(self._zoom_out)
        self._zoom_out_act.setShortcut(QKeySequence.ZoomOut)
        self._zoom_out_act.setEnabled(False)

        self._normal_size_act = view_menu.addAction("&Normal Size")
        self._normal_size_act.triggered.connect(self._normal_size)
        self._normal_size_act.setShortcut("Ctrl+S")
        self._normal_size_act.setEnabled(False)

        view_menu.addSeparator()

        self._fit_to_window_act = view_menu.addAction("&Fit to Window")
        self._fit_to_window_act.triggered.connect(self._fit_to_window)
        self._fit_to_window_act.setEnabled(False)
        self._fit_to_window_act.setCheckable(True)
        self._fit_to_window_act.setShortcut("Ctrl+F")

        help_menu = self.menuBar().addMenu("&Help")

        about_act = help_menu.addAction("&About")
        about_act.triggered.connect(self._about)
        about_qt_act = help_menu.addAction("About &Qt")
        about_qt_act.triggered.connect(QApplication.aboutQt)

    def _update_actions(self):
        has_image = not self._image.isNull()
        self._save_as_act.setEnabled(has_image)
        self._copy_act.setEnabled(has_image)
        enable_zoom = not self._fit_to_window_act.isChecked()
        self._zoom_in_act.setEnabled(enable_zoom)
        self._zoom_out_act.setEnabled(enable_zoom)
        self._normal_size_act.setEnabled(enable_zoom)

    def _scale_image(self, factor):
        self._scale_factor *= factor
        new_size = self._scale_factor * self._image_label.pixmap().size()
        self._image_label.resize(new_size)

        self._adjust_scrollbar(self._scroll_area.horizontalScrollBar(), factor)
        self._adjust_scrollbar(self._scroll_area.verticalScrollBar(), factor)

        #self._zoom_in_act.setEnabled(self._scale_factor < 3.0)
        #self._zoom_out_act.setEnabled(self._scale_factor > 0.333)

    def _adjust_scrollbar(self, scrollBar, factor):
        pos = int(factor * scrollBar.value()
                  + ((factor - 1) * scrollBar.pageStep() / 2))
        scrollBar.setValue(pos)

    def _initialize_image_filedialog(self, dialog, acceptMode):
        if self._first_file_dialog:
            self._first_file_dialog = False
            locations = QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)
            directory = locations[-1] if locations else QDir.currentPath()
            dialog.setDirectory(directory)

        mime_types = [m.data().decode('utf-8') for m in QImageWriter.supportedMimeTypes()]
        mime_types.sort()

        dialog.setMimeTypeFilters(mime_types)
        dialog.selectMimeTypeFilter("image/jpeg")
        dialog.setAcceptMode(acceptMode)
        if acceptMode == QFileDialog.AcceptSave:
            dialog.setDefaultSuffix("jpg")
