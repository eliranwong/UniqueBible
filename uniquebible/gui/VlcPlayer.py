from uniquebible import config
import os
import platform
import sys
if config.qtLibrary == "pyside6":
    from PySide6 import QtWidgets, QtGui, QtCore
    from PySide6.QtWidgets import QWidget
    from PySide6.QtCore import QEvent, Qt
else:
    from qtpy import QtWidgets, QtGui, QtCore
    from qtpy.QtWidgets import QWidget
    from qtpy.QtCore import QEvent, Qt
import vlc

"""
Code based on:
https://git.videolan.org/?p=vlc/bindings/python.git;a=blob_plain;f=examples/pyqt5vlc.py;hb=HEAD
"""

class VlcPlayer(QWidget):

    heightAudio = 60
    widthAudio = 400
    heightVideo = 460
    widthVideo = 650

    def __init__(self, parent, filename=None):
        super().__init__()
        self.playlist = []
        os.environ["VLC_VERBOSE"] = str("-1")  # turn off low level VLC logging
        self.setWindowTitle(config.thisTranslation["mediaPlayer"])
        self.parent = parent
        self.instance = vlc.Instance()
        self.media = None
        self.mediaplayer = self.instance.media_player_new()
        self.create_ui()
        self.is_paused = False
        self.resize(self.widthAudio, self.heightAudio)
        self.centeredFirstTime = False
        self.timer = None
        self.resetTimer()
        if filename:
            self.loadAndPlayFile(filename)
        self.mediaplayer.audio_set_mute(False)
        self.mediaplayer.audio_set_volume(100)
        self.update()

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

        self.openbutton = QtWidgets.QPushButton()
        self.openbutton.setToolTip(config.thisTranslation["open"])
        if config.menuLayout == "material":
            file = "material/file/file_open/materialiconsoutlined/48dp/2x/outline_file_open_black_48dp.png"
        else:
            file = os.path.join("buttons", "playlist.png")
        iconFile = self.parent.getQIcon(file)
        if config.menuLayout == "material":
            self.openbutton.setStyleSheet(iconFile)
        else:
            self.openbutton.setIcon(iconFile)
        self.openbutton.clicked.connect(self.open_file)
        self.hbuttonbox.addWidget(self.openbutton)

        self.playbutton = QtWidgets.QPushButton()
        self.playbutton.setToolTip(config.thisTranslation["play"])
        if config.menuLayout == "material":
            file = "material/av/play_circle_outline/materialiconsoutlined/48dp/2x/outline_play_circle_outline_black_48dp.png"
        else:
            file = os.path.join("buttons", "play.png")
        iconFile = self.parent.getQIcon(file)
        if config.menuLayout == "material":
            self.playbutton.setStyleSheet(iconFile)
        else:
            self.playbutton.setIcon(iconFile)
        self.playbutton.clicked.connect(self.play_pause)
        self.playbutton.setEnabled(True)
        self.hbuttonbox.addWidget(self.playbutton)

        self.stopbutton = QtWidgets.QPushButton()
        self.stopbutton.setToolTip(config.thisTranslation["stop"])
        if config.menuLayout == "material":
            file = "material/av/stop_circle/materialiconsoutlined/48dp/2x/outline_stop_circle_black_48dp.png"
        else:
            file = os.path.join("buttons", "stop.png")
        iconFile = self.parent.getQIcon(file)
        if config.menuLayout == "material":
            self.stopbutton.setStyleSheet(iconFile)
        else:
            self.stopbutton.setIcon(iconFile)
        self.stopbutton.clicked.connect(self.stop)
        self.stopbutton.setEnabled(False)
        self.hbuttonbox.addWidget(self.stopbutton)

        self.nextbutton = QtWidgets.QPushButton()
        # self.nextbutton.setToolTip(config.thisTranslation["next"])
        if config.menuLayout == "material":
            file = "material/av/skip_next/materialiconsoutlined/48dp/2x/outline_skip_next_black_48dp.png"
        else:
            file = os.path.join("buttons", "next.png")
        iconFile = self.parent.getQIcon(file)
        if config.menuLayout == "material":
            self.nextbutton.setStyleSheet(iconFile)
        else:
            self.nextbutton.setIcon(iconFile)
        self.nextbutton.clicked.connect(self.playNextInPlaylist)
        self.nextbutton.setEnabled(False)
        self.hbuttonbox.addWidget(self.nextbutton)

        self.hbuttonbox.addStretch(1)
        self.volumeslider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(self.mediaplayer.audio_get_volume())
        self.volumeslider.setToolTip(config.thisTranslation["volume"])
        self.hbuttonbox.addWidget(self.volumeslider)
        self.volumeslider.setValue(70)
        self.volumeslider.valueChanged.connect(self.set_volume)

        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addWidget(self.positionslider)
        self.vboxlayout.addLayout(self.hbuttonbox)

        self.setLayout(self.vboxlayout)

    def play_pause(self):
        if self.mediaplayer.is_playing():
            self.stopbutton.setEnabled(False)
            self.mediaplayer.pause()
            if config.menuLayout == "material":
                file = "material/av/play_circle_outline/materialiconsoutlined/48dp/2x/outline_play_circle_outline_black_48dp.png"
            else:
                file = os.path.join("buttons", "play.png")
            iconFile = self.parent.getQIcon(file)
            if config.menuLayout == "material":
                self.playbutton.setStyleSheet(iconFile)
            else:
                self.playbutton.setIcon(iconFile)
            self.is_paused = True
            self.timer.stop()
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return

            self.stopbutton.setEnabled(True)
            self.mediaplayer.play()
            if config.menuLayout == "material":
                file = "material/av/pause_circle/materialiconsoutlined/48dp/2x/outline_pause_circle_black_48dp.png"
            else:
                file = os.path.join("buttons", "pause.png")
            iconFile = self.parent.getQIcon(file)
            if config.menuLayout == "material":
                self.playbutton.setStyleSheet(iconFile)
            else:
                self.playbutton.setIcon(iconFile)
            self.timer.start()
            self.is_paused = False

    def stop(self):
        self.mediaplayer.stop()
        if config.menuLayout == "material":
            file = "material/av/play_circle_outline/materialiconsoutlined/48dp/2x/outline_play_circle_outline_black_48dp.png"
        else:
            file = os.path.join("buttons", "play.png")
        iconFile = self.parent.getQIcon(file)
        if config.menuLayout == "material":
            self.playbutton.setStyleSheet(iconFile)
        else:
            self.playbutton.setIcon(iconFile)
        self.stopbutton.setEnabled(False)

    def open_file(self):
        filename, filter = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Media File", ".")
        if filename:
            self.loadAndPlayFile(filename)

    def clearPlaylist(self):
        self.playlist = []

    def loadAndPlayFile(self, filename):
        self.playlist = []
        self.addToPlaylist(filename)
        self.playNextInPlaylist()

    def addToPlaylist(self, filename):
        if not os.path.exists(filename):
            return
        self.playlist.insert(0, filename)
        self.updateNextButton()

    def playNextInPlaylist(self):
        if len(self.playlist) > 0:
            filename = self.playlist.pop()
            if filename.endswith(".mp3"):
                self.resize(self.widthAudio, self.heightAudio)
            else:
                self.resize(self.widthVideo, self.heightVideo)
            if not self.centeredFirstTime:
                self.center()
                self.centeredFirstTime = True

            self.media = self.instance.media_new(filename)

            self.mediaplayer.set_media(self.media)
            self.media.parse()
            self.mediaplayer.play()
            # Disable the following line to fix issue: https://github.com/eliranwong/UniqueBible/issues/976
            #self.mediaplayer.set_position(0)
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

            self.updateNextButton()
            self.stopbutton.setEnabled(True)
        else:
            self.stopbutton.setEnabled(False)

    def resetTimer(self):
        if self.timer:
            self.timer.stop()
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)
        self.timer.start()

    def updateNextButton(self):
        if len(self.playlist) > 0:
            self.nextbutton.setEnabled(True)
        else:
            self.nextbutton.setEnabled(False)

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
                self.playNextInPlaylist()
                self.timer.start()
        if media_pos == 1000:
            self.playNextInPlaylist()


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
        self.parent.vlcPlayer = None


## Standalone development code

class DummyParent():
    vlcPlayer = None

def main():
    from uniquebible.util.LanguageUtil import LanguageUtil

    filename1 = "/Users/otseng/dev/UniqueBible/music/Draw Me Close To You - The AsidorS - Hillsong Cover.mp3"
    filename2 = "/Users/otseng/dev/UniqueBible/music/Through It All Hillsong Cover The AsidorS.mp3"
    filename3 = "/Users/otseng/dev/UniqueBible/music/04 Made Me Glad (Live).mp3"
    filename4 = "/Users/otseng/dev/UniqueBible/video/Luke 15_11 - The Prodigal Son.mp4"
    # filename = "doesnotexist.mp4"
    # filename = ""
    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    app = QtWidgets.QApplication(sys.argv)
    player = VlcPlayer(DummyParent(), filename1)
    player.addToPlaylist(filename2)
    player.addToPlaylist(filename3)
    player.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
