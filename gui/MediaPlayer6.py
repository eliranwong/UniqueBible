# Modified from source: https://doc.qt.io/qtforpython/examples/example_multimedia__player.html

# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause

"""PySide6 Multimedia player example"""

import sys
from PySide6.QtCore import QStandardPaths, Qt, Slot, QUrl
from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog, QMainWindow, QSlider, QStyle, QToolBar, QWidget, QVBoxLayout
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaFormat
from PySide6.QtMultimediaWidgets import QVideoWidget


AVI = "video/x-msvideo"  # AVI
MP4 = "video/mp4"
MP3 = "audio/mpeg"


def get_supported_mime_types():
    result = []
    for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode):
        mime_type = QMediaFormat(f).mimeType()
        result.append(mime_type.name())
    return result


class MediaPlayer(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self._playlist = []  # FIXME 6.3: Replace by QMediaPlaylist?
        self._playlist_index = -1
        self._audio_output = QAudioOutput()
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)

        self._player.errorOccurred.connect(self._player_error)

        tool_bar = QToolBar()
        self.addToolBar(tool_bar)

        file_menu = self.menuBar().addMenu("&File")
        icon = QIcon.fromTheme("document-open")
        open_action = QAction(icon, "&Open...", self,
                              shortcut=QKeySequence.Open, triggered=self.open)
        file_menu.addAction(open_action)
        tool_bar.addAction(open_action)
        icon = QIcon.fromTheme("application-exit")
        exit_action = QAction(icon, "E&xit", self,
                              shortcut="Ctrl+Q", triggered=self.close)
        file_menu.addAction(exit_action)

        play_menu = self.menuBar().addMenu("&Play")
        style = self.style()
        icon = QIcon.fromTheme("media-playback-start.png",
                               style.standardIcon(QStyle.SP_MediaPlay))
        self._play_action = tool_bar.addAction(icon, "Play")
        self._play_action.triggered.connect(self._player.play)
        play_menu.addAction(self._play_action)

        icon = QIcon.fromTheme("media-skip-backward-symbolic.svg",
                               style.standardIcon(QStyle.SP_MediaSkipBackward))
        self._previous_action = tool_bar.addAction(icon, "Previous")
        self._previous_action.triggered.connect(self.previous_clicked)
        play_menu.addAction(self._previous_action)

        icon = QIcon.fromTheme("media-playback-pause.png",
                               style.standardIcon(QStyle.SP_MediaPause))
        self._pause_action = tool_bar.addAction(icon, "Pause")
        self._pause_action.triggered.connect(self._player.pause)
        play_menu.addAction(self._pause_action)

        icon = QIcon.fromTheme("media-skip-forward-symbolic.svg",
                               style.standardIcon(QStyle.SP_MediaSkipForward))
        self._next_action = tool_bar.addAction(icon, "Next")
        self._next_action.triggered.connect(self.next_clicked)
        play_menu.addAction(self._next_action)

        icon = QIcon.fromTheme("media-playback-stop.png",
                               style.standardIcon(QStyle.SP_MediaStop))
        self._stop_action = tool_bar.addAction(icon, "Stop")
        self._stop_action.triggered.connect(self._ensure_stopped)
        play_menu.addAction(self._stop_action)

        self._volume_slider = QSlider()
        self._volume_slider.setOrientation(Qt.Horizontal)
        self._volume_slider.setMinimum(0)
        self._volume_slider.setMaximum(100)
        available_width = self.screen().availableGeometry().width()
        self._volume_slider.setFixedWidth(available_width / 10)
        self._volume_slider.setValue(self._audio_output.volume())
        self._volume_slider.setTickInterval(10)
        self._volume_slider.setTickPosition(QSlider.TicksBelow)
        self._volume_slider.setToolTip("Volume")
        self._volume_slider.valueChanged.connect(self._audio_output.setVolume)
        # modified by Eliran Wong
        # set to maximum volume at launch
        self._volume_slider.setValue(100)
        tool_bar.addWidget(self._volume_slider)

        about_menu = self.menuBar().addMenu("&About")
        about_qt_act = QAction("About &Qt", self, triggered=QApplication.aboutQt)
        about_menu.addAction(about_qt_act)

        self._video_widget = QVideoWidget()
        #self.setCentralWidget(self._video_widget)
        self._player.playbackStateChanged.connect(self.update_buttons)
        self._player.setVideoOutput(self._video_widget)

        # Edited by Eliran Wong
        # Create a QSlider object for seeking through the video
        self.seek_slider = QSlider(Qt.Horizontal, self)
        self.seek_slider.setRange(0, 0)  # Set the range to 0 initially, as we don't know the duration yet
        self.seek_slider.sliderMoved.connect(self.on_slider_moved)  # Connect the sliderMoved signal to our on_slider_moved slot
        self._player.durationChanged.connect(self.on_duration_changed)  # Connect the durationChanged signal to our on_duration_changed slot
        self._player.positionChanged.connect(self.on_position_changed)  # Connect the positionChanged signal to our on_position_changed slot

        centralWidget = QWidget()
        centralWidgetLayout = QVBoxLayout()
        centralWidgetLayout.addWidget(self._video_widget)
        centralWidgetLayout.addWidget(self.seek_slider)
        centralWidget.setLayout(centralWidgetLayout)
        self.setCentralWidget(centralWidget)

        self.update_buttons(self._player.playbackState())
        self._mime_types = []

    def closeEvent(self, event):
        self._ensure_stopped()
        event.accept()

    @Slot()
    def open(self):
        self._ensure_stopped()
        file_dialog = QFileDialog(self)

        is_windows = sys.platform == 'win32'
        if not self._mime_types:
            self._mime_types = get_supported_mime_types()
            if (is_windows and AVI not in self._mime_types):
                self._mime_types.append(AVI)
            # modified
            for mimeType in (MP4, MP3):
                if not mimeType in self._mime_types:
                    self._mime_types.append(mimeType)

        file_dialog.setMimeTypeFilters(self._mime_types)

        default_mimetype = AVI if is_windows else MP4
        if default_mimetype in self._mime_types:
            file_dialog.selectMimeTypeFilter(default_mimetype)

        movies_location = QStandardPaths.writableLocation(QStandardPaths.MoviesLocation)
        file_dialog.setDirectory(movies_location)
        if file_dialog.exec() == QDialog.Accepted:
            url = file_dialog.selectedUrls()[0]
            self._playlist.append(url)
            self._playlist_index = len(self._playlist) - 1
            self._player.setSource(url)
            self._player.play()

    @Slot()
    def _ensure_stopped(self):
        if self._player.playbackState() != QMediaPlayer.StoppedState:
            self._player.stop()

    @Slot()
    def previous_clicked(self):
        # Go to previous track if we are within the first 5 seconds of playback
        # Otherwise, seek to the beginning.
        if self._player.position() <= 5000 and self._playlist_index > 0:
            self._playlist_index -= 1
            self._playlist.previous()
            self._player.setSource(self._playlist[self._playlist_index])
        else:
            self._player.setPosition(0)

    @Slot()
    def next_clicked(self):
        if self._playlist_index < len(self._playlist) - 1:
            self._playlist_index += 1
            self._player.setSource(self._playlist[self._playlist_index])

    @Slot("QMediaPlayer::PlaybackState")
    def update_buttons(self, state):
        media_count = len(self._playlist)
        self._play_action.setEnabled(media_count > 0
            and state != QMediaPlayer.PlayingState)
        self._pause_action.setEnabled(state == QMediaPlayer.PlayingState)
        self._stop_action.setEnabled(state != QMediaPlayer.StoppedState)
        self._previous_action.setEnabled(self._player.position() > 0)
        self._next_action.setEnabled(media_count > 1)

    def show_status_message(self, message):
        self.statusBar().showMessage(message, 5000)

    @Slot("QMediaPlayer::Error", str)
    def _player_error(self, error, error_string):
        print(error_string, file=sys.stderr)
        self.show_status_message(error_string)

    # The following methods were added by Eliran Wong
    def openSingleFile(self, filePath):
        url = QUrl.fromLocalFile(filePath)
        self._playlist = [url]
        self._playlist_index = len(self._playlist) - 1
        self._player.setSource(url)
        self._player.play()

    def openMultipleFiles(self, filePathList):
        if filePathList:
            urlList = [QUrl.fromLocalFile(filePath) for filePath in filePathList]
            self._playlist = urlList
            self._playlist_index = len(self._playlist) - 1
            self._player.setSource(urlList[0])
            self._player.play()

    def appendSingleFile(self, filePath):
        url = QUrl.fromLocalFile(filePath)
        self._playlist.append(url)
        self._playlist_index = len(self._playlist) - 1
        self._player.setSource(url)
        self._player.play()

    def appendMultipleFiles(self, filePathList):
        if filePathList:
            urlList = [QUrl.fromLocalFile(filePath) for filePath in filePathList]
            self._playlist = self._playlist + urlList
            self._playlist_index = len(self._playlist) - 1
            self._player.setSource(urlList[0])
            self._player.play()

    # to work with slider
    def on_slider_moved(self, position):
        # Seek to the position of the slider when it is moved
        self._player.setPosition(position)
        # note: need to reset audio output on Ubuntu to get audio working after chaning position
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)

    def on_duration_changed(self, duration):
        # Set the range of the slider to the duration of the video when it is known
        self.seek_slider.setRange(0, duration)

    def on_position_changed(self, position):
        # Set the value of the slider to the current position of the video
        self.seek_slider.setValue(position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MediaPlayer()
    available_geometry = main_win.screen().availableGeometry()
    main_win.resize(available_geometry.width() / 3, available_geometry.height() / 2)
    main_win.show()
    sys.exit(app.exec())