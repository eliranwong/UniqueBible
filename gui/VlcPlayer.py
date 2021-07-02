import config
import os
import platform
import sys
from qtpy import QtWidgets, QtGui, QtCore
from qtpy.QtWidgets import QWidget
from qtpy.QtWidgets import QDesktopWidget
from qtpy.QtCore import QEvent, Qt
import vlc

"""
Code based on:
https://git.videolan.org/?p=vlc/bindings/python.git;a=blob_plain;f=examples/pyqt5vlc.py;hb=HEAD
"""

class VlcPlayer(QWidget):

    height_audio = 60
    width_audio = 400
    height_video = 460
    width_video = 650

    def __init__(self, filename=None):
        super().__init__()
        os.environ["VLC_VERBOSE"] = str("-1")  # turn off low level VLC logging
        self.setWindowTitle(config.thisTranslation["mediaPlayer"])
        self.instance = vlc.Instance()
        self.media = None
        self.mediaplayer = self.instance.media_player_new()
        self.create_ui()
        self.is_paused = False
        self.resize(self.width_audio, self.height_audio)
        self.center()
        if filename:
            self.load_file(filename)

    def create_ui(self):
        self.videoframe = QtWidgets.QFrame()
        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)
        self.positionslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)
        self.positionslider.sliderPressed.connect(self.set_position)

        self.hbuttonbox = QtWidgets.QHBoxLayout()
        self.openbutton = QtWidgets.QPushButton(config.thisTranslation["open"])
        self.hbuttonbox.addWidget(self.openbutton)
        self.openbutton.clicked.connect(self.open_file)
        self.playbutton = QtWidgets.QPushButton(config.thisTranslation["play"])
        self.hbuttonbox.addWidget(self.playbutton)
        self.playbutton.clicked.connect(self.play_pause)
        self.stopbutton = QtWidgets.QPushButton(config.thisTranslation["stop"])
        self.hbuttonbox.addWidget(self.stopbutton)
        self.stopbutton.clicked.connect(self.stop)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip(config.thisTranslation["volume"])
        self.hbuttonbox.addWidget(self.volumeslider)
        self.volumeslider.valueChanged.connect(self.set_volume)

        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.setLayout(self.vboxlayout)

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)

    def play_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.playbutton.setText(config.thisTranslation["play"])
            self.is_paused = True
            self.timer.stop()
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return

            self.mediaplayer.play()
            self.playbutton.setText(config.thisTranslation["pause"])
            self.timer.start()
            self.is_paused = False

    def stop(self):
        self.mediaplayer.stop()
        self.playbutton.setText(config.thisTranslation["play"])

    def open_file(self):
        filename, filter = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Media File", ".")
        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        if not os.path.exists(filename):
            return
        if filename.endswith(".mp3"):
            self.resize(self.width_audio, self.height_audio)
        else:
            self.resize(self.width_video, self.height_video)
        self.center()

        self.media = self.instance.media_new(filename)

        self.mediaplayer.set_media(self.media)
        self.media.parse()
        self.setWindowTitle(self.media.get_meta(0))

        # The media player has to be 'connected' to the QFrame (otherwise the
        # video would be displayed in it's own window). This is platform
        # specific, so we must give the ID of the QFrame (or similar object) to
        # vlc. Different platforms have different functions for this
        if platform.system() == "Linux": # for Linux using the X Server
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif platform.system() == "Windows": # for Windows
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))
        elif platform.system() == "Darwin": # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

        self.play_pause()

    def set_volume(self, volume):
        """Set the volume
        """
        self.mediaplayer.audio_set_volume(volume)

    def set_position(self):
        """Set the movie position according to the position slider.
        """

        # The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        # integer variables, so you need a factor; the higher the factor, the
        # more precise are the results (1000 should suffice).

        # Set the media position to where the slider was dragged
        self.timer.stop()
        pos = self.positionslider.value()
        self.mediaplayer.set_position(pos / 1000.0)
        self.timer.start()

    def update_ui(self):
        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.mediaplayer.get_position() * 1000)
        self.positionslider.setValue(media_pos)
        if not self.mediaplayer.is_playing():
            self.timer.stop()
            if not self.is_paused:
                self.stop()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def event(self, event):
        if event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Escape:
                self.close()
        return QWidget.event(self, event)

    def closeEvent(self, event):
        if self.mediaplayer.is_playing():
            self.mediaplayer.stop()
            self.timer.stop()
            self.stop()


def main():
    from util.LanguageUtil import LanguageUtil

    filename = "/Users/otseng/dev/UniqueBible/music/04 Made Me Glad (Live).mp3"
    # filename = "/Users/otseng/dev/UniqueBible/video/Luke 15_11 - The Prodigal Son.mp4"
    # filename = "doesnotexist.mp4"
    # filename = ""
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    app = QtWidgets.QApplication(sys.argv)
    player = VlcPlayer(filename)
    player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
