import os, signal, sys, re, base64, webbrowser, platform, subprocess, requests, logging, zipfile, glob
from uniquebible import config
import markdown, time
#from distutils import util
from functools import partial
from pathlib import Path

from uniquebible.util.ConfigUtil import ConfigUtil
from uniquebible.util.SystemUtil import SystemUtil
from uniquebible.gui.Worker import YouTubeDownloader, VLCVideo
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QUrl, Qt, QEvent, QThread, QDir, QTimer
    from PySide6.QtGui import QIcon, QGuiApplication, QFont, QKeySequence, QColor, QPixmap, QCursor, QAction, QShortcut
    from PySide6.QtWidgets import QInputDialog, QLineEdit, QMainWindow, QMessageBox, QWidget, QFileDialog, QLabel, QFrame, QFontDialog, QApplication, QPushButton, QColorDialog, QComboBox, QToolButton, QMenu, QCompleter, QHBoxLayout
    from PySide6.QtWebEngineCore import QWebEnginePage
    from PySide6.QtGui import QClipboard
    from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
    from PySide6.QtMultimediaWidgets import QVideoWidget
else:
    from qtpy.QtCore import QUrl, Qt, QEvent, QThread, QDir, QTimer
    from qtpy.QtGui import QIcon, QGuiApplication, QFont, QKeySequence, QColor, QPixmap, QCursor
    from qtpy.QtWidgets import QAction, QInputDialog, QLineEdit, QMainWindow, QMessageBox, QWidget, QFileDialog, QLabel, QFrame, QFontDialog, QApplication, QPushButton, QShortcut, QColorDialog, QComboBox, QToolButton, QMenu, QCompleter, QHBoxLayout
    from qtpy.QtWebEngineWidgets import QWebEnginePage
    from qtpy.QtGui import QClipboard
    from qtpy.QtMultimedia import QMediaPlayer, QMediaContent
    from qtpy.QtMultimediaWidgets import QVideoWidget
from uniquebible import update
from uniquebible.gui.PlaylistUI import PlaylistUI
from uniquebible.gui.WorkSpace import Workspace
from uniquebible.db.DevotionalSqlite import DevotionalSqlite
from uniquebible.gui.BibleCollectionDialog import BibleCollectionDialog
from uniquebible.gui.LibraryCatalogDialog import LibraryCatalogDialog
from uniquebible.gui.LiveFilterDialog import LiveFilterDialog
from uniquebible.util import exlbl
from uniquebible.util.WebtopUtil import WebtopUtil
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.HtmlColorCodes import HtmlColorCodes
from uniquebible.util.CatalogUtil import CatalogUtil
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.VlcUtil import VlcUtil
from uniquebible.util.themes import Themes
from uniquebible.util.GitHubRepoInfo import GitHubRepoInfo
from uniquebible.util.TextCommandParser import TextCommandParser
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.db.BiblesSqlite import BiblesSqlite, Bible
from uniquebible.db.AGBTSData import AGBTSData
from uniquebible.util.TextFileReader import TextFileReader
from uniquebible.util.Translator import Translator
from uniquebible.util.ThirdParty import Converter, ThirdPartyDictionary
from uniquebible.util.Languages import Languages
from uniquebible.db.ToolsSqlite import BookData, IndexesSqlite, Book, Commentary, Lexicon
from uniquebible.db.Highlight import Highlight
from uniquebible.gui.ConfigFlagsWindow import ConfigFlagsWindow
from uniquebible.gui.EnableIndividualPlugins import EnableIndividualPlugins
from uniquebible.gui.EditGuiLanguageFileDialog import EditGuiLanguageFileDialog
from uniquebible.gui.InfoDialog import InfoDialog
from uniquebible.util.PluginEventHandler import PluginEventHandler
# These "unused" window imports are actually used.  Do not delete these lines.
from uniquebible.gui.DisplayShortcutsWindow import DisplayShortcutsWindow
from uniquebible.gui.GistWindow import GistWindow
from uniquebible.gui.Downloader import Downloader, DownloadProcess
from uniquebible.gui.ModifyDatabaseDialog import ModifyDatabaseDialog
from uniquebible.gui.WatsonCredentialWindow import WatsonCredentialWindow
from uniquebible.gui.LanguageItemWindow import LanguageItemWindow
from uniquebible.gui.ImportSettings import ImportSettings
#from uniquebible.gui.NoteEditor import NoteEditor
from uniquebible.gui.NoteEditorDocker import NoteEditor
from uniquebible.gui.MasterControl import MasterControl
from uniquebible.gui.MiniControl import MiniControl
from uniquebible.gui.MorphDialog import MorphDialog
from uniquebible.gui.MiniBrowser import MiniBrowser
from uniquebible.gui.CentralWidget import CentralWidget
from uniquebible.gui.AppUpdateDialog import AppUpdateDialog
from uniquebible.gui.MaterialColorDialog import MaterialColorDialog
from uniquebible.db.ToolsSqlite import LexiconData
from uniquebible.util.TtsLanguages import TtsLanguages
from uniquebible.util.DatafileLocation import DatafileLocation
from uniquebible.util.LanguageUtil import LanguageUtil
from uniquebible.util.MacroParser import MacroParser
from uniquebible.util.NoteService import NoteService
from uniquebible.util.ShortcutUtil import ShortcutUtil
from uniquebible.util.TextUtil import TextUtil
from uniquebible.util.PydubUtil import PydubUtil
import uniquebible.shortcut as sc
from uniquebible.util.UpdateUtil import UpdateUtil
from uniquebible.util.DateUtil import DateUtil
from uniquebible.util.CrossPlatform import CrossPlatform
from uniquebible.util.GoogleCloudTTSVoices import GoogleCloudTTS
from uniquebible.util.HebrewTransliteration import HebrewTransliteration
from uniquebible.install.module import *
from uniquebible.gui.WebEngineViewPopover import WebEngineViewPopover
# These "unused" window imports are actually used.  Do not delete these lines.
from uniquebible.gui.AlephMainWindow import AlephMainWindow
from uniquebible.gui.ClassicMainWindow import ClassicMainWindow
from uniquebible.gui.FocusMainWindow import FocusMainWindow
from uniquebible.gui.MaterialMainWindow import MaterialMainWindow


class Tooltip(QWidget):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.instantView = WebEngineViewPopover(self.parent, "main", "main", windowTitle=config.thisTranslation["menu2_hover"], enableCloseAction=False)
        layout = QHBoxLayout()
        layout.addWidget(self.instantView)
        self.setLayout(layout)
        self.setWindowTitle(config.thisTranslation["menu2_hover"])
        self.resize(config.floatableInstantViewWidth, config.floatableInstantViewHeight)

    def resizeEvent(self, event):
        size = event.size()
        config.floatableInstantViewWidth = size.width()
        config.floatableInstantViewHeight = size.height()


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.qt6 = True if config.qtLibrary == "pyside6" else False
        self.crossPlatform = CrossPlatform()
        self.logger = logging.getLogger('uba')

        config.inBootupMode = True
        bootStartTime = time.time()
        # delete old files
        for items in update.oldFiles:
            filePath = os.path.join(*items)
            if os.path.isfile(filePath):
                try:
                    os.remove(filePath)
                except:
                    print("'{0}' is not deleted.".format(filePath))
        # information on latest modules
        self.updatedFiles = update.updatedFiles
        self.bibleInfo = DatafileLocation.marvelBibles
        # set os open command
        self.setOsOpenCmd()
        # set translation of interface
        #self.setTranslation()
        # setup a parser for text commands
        self.textCommandParser = TextCommandParser(self)
        # set up resource lists
        self.setupResourceLists()
        # setup a global variable "baseURL"
        self.setupBaseUrl()
        # variables for history management
        self.now = time.time()
        self.lastMainTextCommand = ""
        self.lastStudyTextCommand = ""
        self.newTabException = False
        self.pdfOpened = False
        self.onlineCommand = ""
        # a variable to monitor if new changes made to editor's notes
        self.noteSaved = True
        # variables to work with Qt dialog
        self.openFilesPath = ""
        frameStyle = QFrame.Sunken | QFrame.Panel
        self.openFileNameLabel = QLabel()
        self.openFileNameLabel.setFrameStyle(frameStyle)
        self.directoryLabel = QLabel()
        self.directoryLabel.setFrameStyle(frameStyle)

        # setup UI
        self.setWindowTitle("UniqueBible.app")
        appIcon = QIcon(config.desktopUBAIcon)
        QGuiApplication.setWindowIcon(appIcon)
        # setup user menu & toolbars

        # set up media player
        config.audio_playing_file = os.path.join("temp", "000_audio_playing.txt")
        config.currentAudioFile = ""
        self.audioPlayList = []
        self.resetAudioPlaylist()
        if config.useThirdPartyVLCplayer:
            self.audioPlayer = None
        else:
            self.setupAudioPlayer()
        # VLC Player
        self.vlcPlayer = None

        # bible chat
        config.bibleChatEntry = ""

        # Setup menu layout
        self.refreshing = False
        self.versionCombo = None
        self.versionButton = None
        self.setupMenuLayout(config.menuLayout)

        # assign views
        # mainView & studyView are assigned with class "CentralWidget"
        self.mainView = None
        self.studyView = None
        self.toolTip = None
        #self.noteEditor = None
        self.centralWidget = CentralWidget(self)
        self.instantView = self.centralWidget.instantView
        # put up central widget
        self.setCentralWidget(self.centralWidget)
        # set variables for sync functions
        self.syncingBibles = False
        self.syncButtonChanging = False
        # assign pages
        if config.openBibleWindowContentOnNextTab:
            self.mainView.setCurrentIndex(config.numberOfTab - 1)
        self.setMainPage()
        if config.openStudyWindowContentOnNextTab and not config.syncAction:
            self.studyView.setCurrentIndex(config.numberOfTab - 1)
        self.setStudyPage()
        self.instantPage = self.instantView.page()
        if config.theme in ("dark", "night"):
            self.instantPage.setBackgroundColor(Qt.transparent)
        self.instantPage.titleChanged.connect(self.instantTextCommandChanged)
        # position views as the last-opened layout
        self.resizeCentral()

        # check if newer version is available
        #self.checkApplicationUpdate()
        # check if newer versions of formatted bibles are available
        self.checkModulesUpdate()
        # Control Panel
        self.controlPanel = None
        # Mini control
        self.miniControl = None
        # Used in pause() to pause macros
        config.pauseMode = False

        # Load resource descriptions
        self.loadResourceDescriptions()
        # Load local file catalog
        CatalogUtil.loadLocalCatalog()

        # workspace
        self.ws = Workspace(self)
        self.ws.exemptSaving = True
        self.ws.hide()
        self.ws.exemptSaving = False

        config.inBootupMode = False
        bootEndTime = time.time()
        timeDifference = bootEndTime - bootStartTime

        self.logger.info("Boot start time: {0}".format(timeDifference))

    # work with QThreadPool

    def workOnDownloadYouTubeFile(self, downloadCommand, youTubeLink, outputFolder):
        YouTubeDownloader(self).workOnDownloadYouTubeFile(downloadCommand, youTubeLink, outputFolder)

    # Codes on Media Player

    def toggleAudioPlayer(self):
        if self.thirdToolBar.isVisible():
            self.thirdToolBar.hide()
        else:
            self.thirdToolBar.show()

    def hideAudioPlayer(self):
        if hasattr(self, "thirdToolBar"):
            self.thirdToolBar.hide()

    def showAudioPlayer(self):
        if hasattr(self, "thirdToolBar"):
            self.thirdToolBar.show()

    def resizeAudioPlayer(self):
        config.maximiseMediaPlayerUI = not config.maximiseMediaPlayerUI
        self.setupMenuLayout(config.menuLayout)

    def setMediaSpeed(self, option):
        config.mediaSpeed = float(option)
        self.audioPlayer.setPlaybackRate(config.mediaSpeed)
        if config.menuLayout == "material":
            self.setSubMenuMediaSpeed()
            self.setSpeedButtonButton()

    def setSpeedButtonButton(self):
        icon = "material/av/speed/materialiconsoutlined/48dp/2x/outline_speed_black_48dp.png"
        qIcon = self.getQIcon(self.getCrossplatformPath(icon))
        self.speedButton.setStyleSheet(qIcon)
        self.speedButton.setPopupMode(QToolButton.InstantPopup)
        self.speedButton.setArrowType(Qt.NoArrow)
        self.speedButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.speedButton.setToolTip(config.thisTranslation["adjustSpeed"])
        menu = QMenu(self.speedButton)
        for value in (0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0):
            action = menu.addAction(str(value))
            action.triggered.connect(partial(self.setMediaSpeed, value))
            action.setCheckable(True)
            action.setChecked(True if config.mediaSpeed == value else False)
        self.speedButton.setMenu(menu)

    def toggleAudioPlayerMuteOption(self):
        config.audioMuted = not config.audioMuted
        if config.qtLibrary == "pyside6":
            config.audioOutput.setMuted(config.audioMuted)
        else:
            self.audioPlayer.setMuted(config.audioMuted)

    def setAudioVolume(self, value):
        config.audioVolume = value
        if config.qtLibrary == "pyside6":
            # PySide 6 volume range (float): 0.0-1.0
            config.audioOutput.setVolume(float(value/100))
        else:
            # PySide 2 volume range (int): 0-100
            self.audioPlayer.setVolume(value)

    def workOnPlaylistIndex(self):
        config.isVlcPlayingInQThread = False
        if self.audioPlayListIndex == -2: # stopped by users
            self.resetAudioPlaylist()
        else:
            if self.audioPlayListIndex == len(self.audioPlayList) - 1:
                self.resetAudioPlaylist()
                if config.loopMediaPlaylist:
                    self.playAudioPlayList()
            else:
                self.audioPlayListIndex += 1
                self.playAudioPlayList()

    def setupAudioPlayer(self):
        config.isVlcPlayingInQThread = False
        if config.qtLibrary == "pyside6":
            config.audioOutput = QAudioOutput()
            config.audioMuted = config.audioOutput.isMuted()

        def playbackStateChanged(state):
            if state == QMediaPlayer.StoppedState:
                self.workOnPlaylistIndex()

        self.audioPlayer = QMediaPlayer(self)
        if not config.qtLibrary == "pyside6":
            config.audioMuted = self.audioPlayer.isMuted()
        self.audioPlayer.setPlaybackRate(config.mediaSpeed)
        if config.qtLibrary == "pyside6":
            self.audioPlayer.playbackStateChanged.connect(playbackStateChanged)
        else:
            self.audioPlayer.stateChanged.connect(playbackStateChanged)
        #self.audioPlayer.mediaStatusChanged.connect(self.on_media_status_changed)
        self.audioPlayer.durationChanged.connect(self.on_duration_changed)  # Connect the durationChanged signal to our on_duration_changed slot
        self.audioPlayer.positionChanged.connect(self.on_position_changed)  # Connect the positionChanged signal to our on_position_changed slot

    def resetAudioPlaylist(self):
        self.audioPlayListIndex = 0
        self.isAudioPlayListPlaying = False

    def openAudioPlayListUI(self):
        self.audioPlayListUI = PlaylistUI(self)
        self.audioPlayListUI.show()
        self.selectAudioPlaylistUIItem()

    def isPlayListUIOpened(self):
        return (hasattr(self, "audioPlayListUI") and self.audioPlayListUI and self.audioPlayListUI.isVisible())

    def previousAudioFile(self):
        if self.audioPlayList and not self.audioPlayListIndex == 0:
            self.audioPlayListIndex = self.audioPlayListIndex - 2
            self.audioPlayer.stop()

    def nextAudioFile(self):
        if self.audioPlayList and not self.audioPlayListIndex == (len(self.audioPlayList) - 1):
            self.audioPlayer.stop()

    def getAudioPlayerState(self):
        return self.audioPlayer.playbackState() if self.qt6 else self.audioPlayer.state()

    def pauseAudioPlaying(self):
        if self.getAudioPlayerState() == QMediaPlayer.PlayingState:
            self.audioPlayer.pause()

    def playAudioPlaying(self):
        if self.getAudioPlayerState() == QMediaPlayer.PausedState:
            self.audioPlayer.play()
        elif self.getAudioPlayerState() == QMediaPlayer.StoppedState and config.currentAudioFile:
            self.playAudioPlayList()

    def stopAudioPlaying(self):
        if hasattr(config, "isVlcPlayingInQThread") and config.isVlcPlayingInQThread:
            self.audioPlayListIndex == -2
            VlcUtil.closeVlcPlayer()
            self.resetAudioPlaylist()
            config.isVlcPlayingInQThread = False
        if not self.getAudioPlayerState() == QMediaPlayer.StoppedState:
            self.audioPlayListIndex = -2
            self.audioPlayer.stop()

    def addToAudioPlayList(self, newPlayList, clear=False):
        isPlayListUIOpened = self.isPlayListUIOpened()
        if isPlayListUIOpened:
            self.audioPlayListUI.close()
        if clear:
            self.audioPlayList = []
        # allow adding a single file path in a string rather than a list
        if isinstance(newPlayList, str):
            self.audioPlayList.append(newPlayList)
        else:
            self.audioPlayList = self.audioPlayList + newPlayList
        if not self.isAudioPlayListPlaying:
            self.playAudioPlayList()
        if isPlayListUIOpened:
            self.openAudioPlayListUI()

    def playAudioPlayList(self):
        if self.audioPlayList:
            self.isAudioPlayListPlaying = True
            self.playAudioFile(self.audioPlayList[self.audioPlayListIndex])

    def showVideoView(self):
        if not hasattr(self, "videoView") or not self.videoView or not self.videoView.isVisible():
            self.openVideoView()
        elif self.videoView.isVisible():
            self.bringToForeground(self.videoView)

    def openVideoView(self):
        if config.useThirdPartyVLCplayerForVideoOnly:
            VlcUtil.openVlcPlayer()
        elif config.qtLibrary == "pyside6":
            self.videoView = QVideoWidget()
            self.videoView.setWindowTitle(config.thisTranslation["menu11_video"])
            self.videoView.show()
            self.audioPlayer.setVideoOutput(self.videoView)
        elif not hasattr(self, "videoView") or not self.videoView or not self.videoView.isVisible():
            if not hasattr(self, "videoView") or not self.videoView:
                def closeEvent(event):
                    event.ignore()
                    self.videoView.hide()
                self.videoView = QVideoWidget()
                self.videoView.setWindowTitle(config.thisTranslation["menu11_video"])
                self.videoView.closeEvent = closeEvent
                self.videoView.show()
                self.audioPlayer.setVideoOutput(self.videoView)
            self.videoView.show()

    def syncAudioWithText(self, filePath):
        basename = os.path.basename(filePath)
        if config.audioTextSync and not basename in ("gtts.mp3",) and not basename.startswith("gtts_"):
            # verse pattern, e.g. CSB_1_1_1.mp3
            versePattern = re.compile("^([^_]+?)_([0-9]+?)_([0-9]+?)_([0-9]+?).mp3")
            isVerse = versePattern.search(basename)
            if not isVerse:
                # word patterns, e.g. lex_OGNT_61_1_9_124169.mp3   OGNT_61_1_9_124169.mp3 BHS5_1_1_28_579.mp3  lex_BHS5_1_1_20_376.mp3
                wordPattern = re.compile("^.*?(BHS5|OGNT)_([0-9]+?)_[0-9]+?_[0-9]+?_([0-9]+?).mp3")
                isWord = wordPattern.search(filePath)
            def getDefaultInfo():
                return f"Playing media: {basename}"
            if isVerse:
                text, b, c, v = isVerse.groups()
                instantInfo = self.textCommandParser.getInstantMainVerseInfo(f"{b}.{c}.{v}", text) if text in self.textList else getDefaultInfo()
                if config.scrollBibleTextWithAudioPlayback:
                    self.mainPage.runJavaScript(self.getScrollVerseJS(b, c, v, underline=True))
            elif isWord:
                _, book, wordId = isWord.groups()
                instantInfo = self.textCommandParser.getInstantWordInfo(f"{book}:::{wordId}")
            else:
                instantInfo = getDefaultInfo()
            #self.instantView.setHtml(self.wrapHtml(instantInfo, "instant", False), baseUrl)
            # The line above does not work with QThreadPool on macOS, we use the following two lines instead
            instantInfo = instantInfo.replace('"', '\\"')
            self.instantPage.runJavaScript(f"""document.getElementsByTagName('body')[0].innerHTML = "{instantInfo}";""")

    def playAudioFile(self, filePath):
        if filePath and os.path.isfile(filePath):
            # check if it is a video file
            isVideo = re.search("(.mp4|.avi)$", filePath.lower()[-4:])
            # text synchronisation with audio playback
            self.syncAudioWithText(filePath)
            # full path is required for PySide2 QMediaPlayer to work
            config.currentAudioFile = os.path.abspath(QDir.toNativeSeparators(filePath))
            if isVideo and config.useThirdPartyVLCplayerForVideoOnly:
                # update playlist gui
                self.selectAudioPlaylistUIItem()
                try:
                    config.isVlcPlayingInQThread = True
                    VLCVideo(self).workOnPlayVideo(config.currentAudioFile, config.mediaSpeed)
                except:
                    self.audioPlayListIndex = -2
                    # possbily users close VLC player manually
                    pass
            # use built-in media player
            else:
                # in case it is a video file
                if isVideo:
                    self.openVideoView()
                    if not self.videoView.isVisible():
                        self.bringToForeground(self.videoView)
                # handle audio
                if not (config.mediaSpeed == 1.0):
                    isAudio = re.search("(.mp3|.wav)$", filePath.lower()[-4:])
                    if isAudio and config.useFfmpegToChangeAudioSpeed:
                        self.audioPlayer.setPlaybackRate(1.0)
                        newAudiofile = os.path.join(os.getcwd(), "temp", "ffmpeg.wav")
                        if os.path.isfile(newAudiofile):
                            os.remove(newAudiofile)
                        #os.system(f'''ffmpeg -i {config.currentAudioFile} -filter:a "atempo={config.mediaSpeed}" {newAudiofile}''')
                        # use subprocess instead of os.system, to hide terminal output
                        subprocess.Popen(f'''ffmpeg -i {config.currentAudioFile} -filter:a "atempo={config.mediaSpeed}" "{newAudiofile}"''', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
                        config.currentAudioFile = newAudiofile
                    elif isAudio and config.usePydubToChangeAudioSpeed:
                        self.audioPlayer.setPlaybackRate(1.0)
                        config.currentAudioFile = PydubUtil.exportAudioFile(config.currentAudioFile, config.mediaSpeed, config.speedUpFilterFrequency)
                    else:
                        self.audioPlayer.setPlaybackRate(config.mediaSpeed)
                # play audio file with builtin media player
                if config.qtLibrary == "pyside6":
                    # remarks: tested on Ubuntu
                    # for unknown reasons, the following three lines do not work when they are executed directly without puting into a string first
                    # work as expected when the string is executed with exec() method
                    codes = f"""
config.audioOutput = QAudioOutput()
config.audioOutput.setVolume(float(config.audioVolume/100))
config.audioOutput.setMuted(config.audioMuted)
config.mainWindow.audioPlayer.setAudioOutput(config.audioOutput)
config.mainWindow.audioPlayer.setSource(QUrl.fromLocalFile(""))
config.mainWindow.audioPlayer.setSource(QUrl.fromLocalFile(config.currentAudioFile))"""
                    exec(codes, globals())
                else:
                    dummy_media_content = QMediaContent(QUrl.fromLocalFile(""))
                    media_content = QMediaContent(QUrl.fromLocalFile(config.currentAudioFile))
                    # reset media is needed to repeatedly play files having the same filepaths but of different content
                    self.audioPlayer.setMedia(dummy_media_content)
                    self.audioPlayer.setMedia(media_content)
                self.audioPlayer.play()
                # update playlist gui
                self.selectAudioPlaylistUIItem()

    def selectAudioPlaylistUIItem(self):
        if hasattr(self, "audioPlayListUI") and self.audioPlayListUI and self.audioPlayListUI.isVisible() and (self.audioPlayListUI.model.rowCount() > self.audioPlayListIndex >= 0):
            self.audioPlayListUI.view.setCurrentIndex(self.audioPlayListUI.model.index(self.audioPlayListIndex, 0))

    # to work with slider
    def on_slider_moved(self, position):
        # Seek to the position of the slider when it is moved
        self.audioPlayer.setPosition(position)
        # note: need to reset audio output on Ubuntu to get audio working after chaning position
        if config.qtLibrary == "pyside6":
            codes = f"""
config.audioOutput = QAudioOutput()
config.audioOutput.setVolume(float(config.audioVolume/100))
config.audioOutput.setMuted(config.audioMuted)
config.mainWindow.audioPlayer.setAudioOutput(config.audioOutput)"""
            exec(codes, globals())

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.BufferedMedia:
            #self.audioPlayer.setPlaybackRate(config.mediaSpeed)
            #self.audioPlayer.play()
            pass

    def on_duration_changed(self, duration):
        # Set the range of the slider to the duration of the video when it is known
        self.seek_slider.setRange(0, duration)

    def on_position_changed(self, position):
        # Set the value of the slider to the current position of the video
        self.seek_slider.setValue(position)

    def __del__(self):
        del self.textCommandParser

    def setupResourceLists(self):
        self.crossPlatform.setupResourceLists()
        self.textList = self.crossPlatform.textList
        self.textFullNameList = self.crossPlatform.textFullNameList
        self.strongBibles = self.crossPlatform.strongBibles
        self.commentaryList = self.crossPlatform.commentaryList
        self.commentaryFullNameList = self.crossPlatform.commentaryFullNameList
        self.referenceBookList = self.crossPlatform.referenceBookList
        self.topicListAbb = self.crossPlatform.topicListAbb
        self.topicList = self.crossPlatform.topicList
        self.lexiconList = self.crossPlatform.lexiconList
        self.dictionaryListAbb = self.crossPlatform.dictionaryListAbb
        self.dictionaryList = self.crossPlatform.dictionaryList
        self.encyclopediaListAbb = self.crossPlatform.encyclopediaListAbb
        self.encyclopediaList = self.crossPlatform.encyclopediaList
        self.thirdPartyDictionaryList = self.crossPlatform.thirdPartyDictionaryList
        self.pdfList = self.crossPlatform.pdfList
        self.epubList = self.crossPlatform.epubList
        self.docxList = self.crossPlatform.docxList

    # Dynamically load menu layout
    def setupMenuLayout(self, layout):
        if not layout == config.menuLayout:
            config.menuLayout = layout
            self.setTheme(config.theme)
        else:
            config.shortcutList = []
            config.noStudyBibleToolbar = True if layout in ("focus", "material") else False
            if config.startup:
                config.startup = False
            else:
                try:
                    self.menuBar().clear()
                    self.removeToolBar(self.firstToolBar)
                    self.removeToolBar(self.secondToolBar)
                    if hasattr(self, "thirdToolBar"):
                        self.removeToolBar(self.thirdToolBar)
                    self.removeToolBar(self.leftToolBar)
                    self.removeToolBar(self.rightToolBar)
                    self.removeToolBar(self.studyBibleToolBar)
                except:
                    pass

            windowClass = None
            if layout in ("classic", "focus", "aleph", "material"):
                windowName = layout.capitalize() + "MainWindow"
                windowClass = getattr(sys.modules[__name__], windowName)
            elif config.enablePlugins:
                file = os.path.join(config.packageDir, "plugins", "layout", layout+".py")
                if os.path.exists(file):
                    mod = __import__('plugins.layout.{0}'.format(layout), fromlist=[layout])
                    windowClass = getattr(mod, layout)
            if windowClass is None:
                config.menuLayout = "material"
                windowClass = getattr(sys.modules[__name__], "MaterialMainWindow")
            if config.menuLayout == "material":
                config.defineStyle()
            getattr(windowClass, 'create_menu')(self)
            if config.toolBarIconFullSize and not config.menuLayout == "material":
                getattr(windowClass, 'setupToolBarFullIconSize')(self)
            else:
                getattr(windowClass, 'setupToolBarStandardIconSize')(self)
            self.setAdditionalToolBar()

    def setOsOpenCmd(self):
        if platform.system() == "Linux":
            config.open = config.openLinux
        elif platform.system() == "Darwin":
            config.open = config.openMacos
        elif platform.system() == "Windows":
            config.open = config.openWindows

    def loadResourceDescriptions(self):
        self.loadBibleDescriptions()
        self.loadLexiconSampleTopics()

    def loadBibleDescriptions(self):
        config.bibleDescription = {}
        for file in glob.glob(config.marvelData + "/bibles/*.bible"):
            name = Path(file).stem
            bible = Bible(name)
            config.bibleDescription[name] = bible.bibleInfo()

    def loadLexiconSampleTopics(self):
        config.lexiconDescription = {}
        for file in glob.glob(config.marvelData + "/lexicons/*.lexicon"):
            name = Path(file).stem
            lexicon = Lexicon(name)
            config.lexiconDescription[name] = lexicon.getSampleTopics()

    def setTranslation(self):
        config.thisTranslation = LanguageUtil.loadTranslation(config.displayLanguage)

    # base folder for webViewEngine
    def setupBaseUrl(self):
        # Variable "baseUrl" is shared by multiple classes
        # External objects, such as stylesheets or images referenced in the HTML document, are located RELATIVE TO baseUrl .
        # e.g. put all local files linked by html's content in folder "htmlResources"
        global baseUrl
        relativePath = os.path.join("htmlResources", "UniqueBibleApp.png")
        absolutePath = os.path.abspath(relativePath)
        baseUrl = QUrl.fromLocalFile(absolutePath)
        config.baseUrl = baseUrl

    def focusCommandLineField(self):
        if config.preferControlPanelForCommandLineEntry:
            self.manageControlPanel()
        elif self.textCommandLineEdit.isVisible():
            self.textCommandLineEdit.setFocus()
            self.textCommandLineEdit.selectAll()
        if config.clearCommandEntry:
            self.textCommandLineEdit.setText("")

    def openMiniControlTab(self, index):
        config.miniControlInitialTab = index
        self.manageMiniControl(index)

    def openControlPanelTab(self, index=None, b=None, c=None, v=None, text=None):
        if index is None:
            index = 0
        if b is None:
            b = config.mainB
        if c is None:
            c = config.mainC
        if v is None:
            v = config.mainV
        if text is None:
            text = config.mainText

        if self.textCommandParser.isDatabaseInstalled("bible"):
            # self.controlPanel.tabs.setCurrentIndex(index)
            self.manageControlPanel(True, index, b, c, v, text)
        else:
            self.textCommandParser.databaseNotInstalled("bible")

    def reloadResources(self, show=False):
        CatalogUtil.reloadLocalCatalog()
        self.loadResourceDescriptions()
        CrossPlatform().setupResourceLists()
        self.controlPanel.setupResourceLists()
        self.setupMenuLayout(config.menuLayout)
        self.reloadControlPanel(show)

    def reloadControlPanel(self, show=True):
        if self.controlPanel:
            self.controlPanel.close()
            config.controlPanel = False
            self.manageControlPanel(show)

    def manageControlPanel(self, show=True, index=None, b=None, c=None, v=None, text=None):
        if index is None:
            index = 0
        if b is None:
            b = config.mainB
        if c is None:
            c = config.mainC
        if v is None:
            v = config.mainV
        if text is None:
            text = config.mainText

        if self.textCommandParser.isDatabaseInstalled("bible"):
            if config.controlPanel and not (self.controlPanel.isVisible() and self.controlPanel.isActiveWindow()):
                self.controlPanel.updateBCVText(b, c, v, text)
                self.controlPanel.tabs.setCurrentIndex(index)
                textCommandText = self.textCommandLineEdit.text()
                if textCommandText:
                    self.controlPanel.commandField.setText(textCommandText)
                #selectedText = self.mainView.currentWidget().selectedText().strip()
                # Removed morphology tab temporarily until a fix.
                #self.controlPanel.morphologyTab.searchField.setText(selectedText)
                self.controlPanel.raise_()
                # Method activateWindow() does not work with qt.qpa.wayland
                # platform.system() == "Linux" and not os.getenv('QT_QPA_PLATFORM') is None and os.getenv('QT_QPA_PLATFORM') == "wayland"
                # The error message is received when QT_QPA_PLATFORM=wayland:
                # qt.qpa.wayland: Wayland does not support QWindow::requestActivate()
                # Therefore, we use hide and show methods instead with wayland.
                if self.controlPanel.isVisible() and not self.controlPanel.isActiveWindow():
                    self.controlPanel.hide()
                self.controlPanel.show()
                self.controlPanel.tabChanged(index)
                if not SystemUtil.isWayland():
                    self.controlPanel.activateWindow()
            elif not config.controlPanel:
                self.controlPanel = MasterControl(self, index, b, c, v, text)
                if show:
                    self.controlPanel.show()
                    self.controlPanel.tabChanged(index)
                if config.clearCommandEntry:
                    self.controlPanel.commandField.setText("")
                else:
                    self.controlPanel.commandField.setText(self.textCommandLineEdit.text())
                config.controlPanel = True
            # elif self.controlPanel:
            #        self.controlPanel.close()
            #        config.controlPanel = False
        else:
            self.textCommandParser.databaseNotInstalled("bible")

    def manageMiniControl(self, selectedTab = 0):
        if config.miniControl:
            textCommandText = self.textCommandLineEdit.text()
            if textCommandText:
                self.miniControl.searchLineEdit.setText(textCommandText)
            self.miniControl.tabs.setCurrentIndex(config.miniControlInitialTab)
            self.bringToForeground(self.miniControl)
        else:
            self.miniControl = MiniControl(self, selectedTab)
            self.miniControl.setMinimumHeight(config.minicontrolWindowHeight)
            self.miniControl.setMinimumWidth(config.minicontrolWindowWidth)
            self.miniControl.show()
            textCommandText = self.textCommandLineEdit.text()
            selectedText = self.mainView.currentWidget().selectedText().strip()
            if selectedText:
                self.miniControl.searchLineEdit.setText(selectedText)
            elif config.clearCommandEntry:
                self.miniControl.searchLineEdit.setText("")
            elif textCommandText:
                self.miniControl.searchLineEdit.setText(textCommandText)
            config.miniControl = True

    def closeEvent(self, event):
        if config.enableSystemTray:
            event.ignore()
            self.hide()
            config.mainWindowHidden = True
        else:
            event.accept()
            QGuiApplication.instance().quit()

    def quitApp(self):
        self.showFromTray()
        #self.ws.saveWorkspace()
        if self.noteSaved or self.warningNotSaved():
            QGuiApplication.instance().quit()

    def resetUI(self):
        config.defineStyle()
        app = QGuiApplication.instance()
        if config.qtMaterial and config.qtMaterialTheme:
            from qt_material import apply_stylesheet
            apply_stylesheet(app, theme=config.qtMaterialTheme)
            config.theme = "dark" if config.qtMaterialTheme.startswith("dark_") else "default"
        else:
            app.setPalette(Themes.getPalette())
            if config.menuLayout == "material":
                app.setStyleSheet(config.materialStyle)
                self.setupMenuLayout("material")
            else:
                app.setStyleSheet("")
        ConfigUtil.loadColorConfig()
        self.reloadCurrentRecord(True)

    def restartApp(self):
        config.restartUBA = True
        QGuiApplication.instance().quit()

    def displayMessage(self, message="", title="UniqueBible"):
        if hasattr(config, "cli") and config.cli:
            print(message)
        else:
            reply = QMessageBox.information(self, title, message)

    def addContextMenuShortcut(self, action, shortcut):
        if not shortcut in config.shortcutList:
            sc = QShortcut(QKeySequence(shortcut), self)
            sc.activated.connect(action)
            config.shortcutList.append(shortcut)

    def addContextPluginShortcut(self, plugin, shortcut):
        if not shortcut in config.shortcutList:
            sc = QShortcut(QKeySequence(shortcut), self)
            sc.activated.connect(lambda: self.runContextPlugin(plugin))
            config.shortcutList.append(shortcut)

    def runContextPlugin(self, plugin):
        mainWindowSelectedText = self.mainView.currentWidget().selectedText().strip()
        if mainWindowSelectedText:
            self.mainView.currentWidget().runPlugin(plugin)
        else:
            self.studyView.currentWidget().runPlugin(plugin)

    # manage key capture
    def event(self, event):
        if event.type() == QEvent.KeyRelease:
            if config.pauseMode:
                config.pauseMode = False
            if event.key() == Qt.Key_Tab:
                self.focusCommandLineField()
            elif event.key() == Qt.Key_Escape:
                self.setNoToolBar()
                config.quitMacro = True
                return True
        if isinstance(event, QEvent):
            return QWidget.event(self, event)

    # manage main page

    def getTextFromToolTip(self, tabToolTip, studyView=False):
        # Default text
        text = config.studyText if studyView else config.mainText
        texts = re.search(":::([^:]+?):::", tabToolTip)
        if texts:
            textList = self.textCommandParser.getConfirmedTexts(texts[0], True)
            if textList:
                text = textList[0]
        elif tabToolTip.lower().startswith("text:::"):
            *_, textForCheck = self.textCommandParser.splitCommand(tabToolTip)
            textList = self.textCommandParser.getConfirmedTexts(textForCheck, True)
            if textList:
                text = textList[0]
        return text

    def getTabText(self, studyView=False, index=None):
        # Settle index
        if index is None:
            index = self.studyView.currentIndex() if studyView else self.mainView.currentIndex()
        # Define tabText & tabToolTip
        tabText = self.studyView.tabText(index).strip() if studyView else self.mainView.tabText(index).strip()
        tabToolTip = self.studyView.tabToolTip(index).strip() if studyView else self.mainView.tabToolTip(index).strip()
        # Get text
        if tabToolTip:
            if "-" in tabText:
                textForCheck = tabText.split("-", 1)[0]
                textList = self.textCommandParser.getConfirmedTexts(textForCheck, True)
                if textList:
                    text = textList[0]
                else:
                    text = self.getTextFromToolTip(tabToolTip, studyView)
            else:
                text = self.getTextFromToolTip(tabToolTip, studyView)
        else:
            text = config.studyText if studyView else config.mainText
        return text

    def getTabBcv(self, studyView=False, index=None):
        # Settle index
        if index is None:
            index = self.studyView.currentIndex() if studyView else self.mainView.currentIndex()
        # Define tabText & tabToolTip
        tabText = self.studyView.tabText(index).strip() if studyView else self.mainView.tabText(index).strip()
        tabToolTip = self.studyView.tabToolTip(index).strip() if studyView else self.mainView.tabToolTip(index).strip()
        # Default bcv tuple
        bcvTuple = (config.studyB, config.studyC, config.studyV) if studyView else (config.mainB, config.mainC, config.mainV)
        # Refine bcv tuple according to tabText & tabToolTip
        if tabToolTip:
            parser = BibleVerseParser(config.parserStandarisation)
            # check reference
            references = parser.extractAllReferences(tabText)
            if references:
                b, c, v, *_ = references[-1]
                bcvTuple = (b, c, v)
            else:
                references = parser.extractAllReferences(tabToolTip) 
                if references:
                    b, c, v, *_ = references[-1]
                    bcvTuple = (b, c, v)
        return bcvTuple


    def setMainPage(self):
        # main page changes as tab is changed.
        # print(self.mainView.currentIndex())
        self.mainPage = self.mainView.currentWidget().page()
        if config.updateMainReferenceOnChangingTabs:
            # check command stored in each tab's tooltip
            tabToolTip = self.mainView.tabToolTip(self.mainView.currentIndex()).strip()
            if tabToolTip:
                # Update main reference button and text
                #self.textCommandParser.setMainVerse(text, bcvTuple)
                config.mainText = self.getTabText()
                config.mainB, config.mainC, config.mainV, *_ = self.getTabBcv()
                config.setMainVerse = True
                self.updateMainRefButton()
        if config.theme in ("dark", "night"):
            self.mainPage.setBackgroundColor(Qt.transparent)
        #self.mainPage.pdfPrintingFinished.connect(self.pdfPrintingFinishedAction)
        self.mainView.currentWidget().updateContextMenu()
        if config.openBibleInMainViewOnly:
            config.studyText = config.mainText

    def setStudyPage(self, tabIndex=None):
        if tabIndex != None:
            self.studyView.setCurrentIndex(tabIndex)
        # study page changes as tab is changed.
        # print(self.studyView.currentIndex())
        self.studyPage = self.studyView.currentWidget().page()
        if config.theme in ("dark", "night"):
            self.studyPage.setBackgroundColor(Qt.transparent)
        #self.studyPage.pdfPrintingFinished.connect(self.pdfPrintingFinishedAction)
        self.studyView.currentWidget().updateContextMenu()

    # Export File
    def savePlainText(self, view="main"):
        if view == "study":
            self.studyView.currentWidget().savePlainText()
        else:
            self.mainView.currentWidget().savePlainText()

    def saveHtml(self, view="main"):
        if view == "study":
            self.studyView.currentWidget().saveHtml()
        else:
            self.mainView.currentWidget().saveHtml()

    def savePdf(self, view="main"):
        if view == "study":
            self.studyView.currentWidget().savePdf()
        else:
            self.mainView.currentWidget().savePdf()

    def saveDocx(self, view="main"):
        if view == "study":
            self.studyView.currentWidget().saveDocx()
        else:
            self.mainView.currentWidget().saveDocx()

    def saveMarkdown(self, view="main"):
        if view == "study":
            self.studyView.currentWidget().saveMarkdown()
        else:
            self.mainView.currentWidget().saveMarkdown()

    # Command Prompt
    def commandPrompt(self, prefix):
        if prefix.startswith("online:::"):
            self.focusCommandLineField()
            self.textCommandLineEdit.setText(prefix)
            return
        suffix, ok = QInputDialog.getText(self, "Unique Bible App",
                config.thisTranslation["enter_text_here"], QLineEdit.Normal,
                "")
        if ok and suffix:
            command = "{0}{1}".format(prefix, suffix)
            self.textCommandLineEdit.setText(command)
            self.runTextCommand(command)
        else:
            self.focusCommandLineField()
            self.textCommandLineEdit.setText(prefix)

    # Interface to add config.openaiApiKey
    def setMyOpenAiApiKey(self):
        text, ok = QInputDialog.getText(self, "Unique Bible App",
                "OpenAI API Key", QLineEdit.Normal,
                config.openaiApiKey)
        if ok:
            config.openaiApiKey = text

    # Interface to add config.myGoogleApiKey
    def setMyGoogleApiKey(self):
        text, ok = QInputDialog.getText(self, "Unique Bible App",
                config.thisTranslation["setGoogleApiKey"], QLineEdit.Normal,
                config.myGoogleApiKey)
        if ok:
            config.myGoogleApiKey = text

    # manage latest update
    def checkApplicationUpdate(self):
        try:
            checkFile = "{0}UniqueBibleAppVersion.txt".format(UpdateUtil.repository)
            # latest version number is indicated in file "UniqueBibleAppVersion.txt"
            request = requests.get(checkFile, timeout=5)
            if request.status_code == 200:
                # tell the rest that internet connection is available
                config.internet = True
                # compare with user's current version
                if UpdateUtil.checkIfShouldCheckForAppUpdate() and not UpdateUtil.currentIsLatest(config.version, request.text):
                    self.promptUpdate(request.text)
            else:
                config.internet = False
        except Exception as e:
            config.internet = False
            print("Failed to read '{0}'.".format(checkFile))

    def checkModulesUpdate(self):
        if not config.disableModulesUpdateCheck:
            for filename in self.updatedFiles:
                abb = filename[:-6]
                if os.path.isfile(os.path.join(*self.bibleInfo[abb][0])):
                    if self.isNewerAvailable(filename):
                        self.displayMessage(
                            "{1} {0}.  {2} '{3} > {4}'".format(filename, config.thisTranslation["message_newerFile"],
                                                               config.thisTranslation["message_installFrom"],
                                                               config.thisTranslation["menu8_resources"],
                                                               config.thisTranslation["menu8_bibles"]))

    def isNewerAvailable(self, filename):
        abb = filename[:-6]
        if os.path.isfile(os.path.join(*self.bibleInfo[abb][0])):
            if not filename in self.updatedFiles:
                return False
            else:
                if filename in config.installHistory:
                    if config.installHistory[filename] == self.bibleInfo[abb][1]:
                        return False
        return True

    def promptUpdate(self, latestVersion):
        config.lastAppUpdateCheckDate = str(DateUtil.localDateNow())
        reply = QMessageBox.question(self, "Update is available ...",
                                     "Update is available ...\n\nLatest version: {0}\nInstalled version: {1:.2f}\n\nDo you want to proceed the update?".format(
                                         latestVersion, config.version),
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            UpdateUtil.updateUniqueBibleApp()

    # manage download helper
    def downloadHelper(self, databaseInfo):
        if config.isDownloading:
            self.displayMessage(config.thisTranslation["previousDownloadIncomplete"])
        else:
            self.downloader = Downloader(self, databaseInfo)
            self.downloader.show()

    def downloadFile(self, databaseInfo, notification=True):
        # Prevent downloading multiple files at the same time.
        config.isDownloading = True
        # Retrieve file information
        fileItems, cloudID, *_ = databaseInfo
        cloudFile = "https://drive.google.com/uc?id={0}".format(cloudID)
        localFile = "{0}.zip".format(os.path.join(*fileItems))
        # Configure a QThread
        self.downloadthread = QThread()
        self.downloadProcess = DownloadProcess(cloudFile, localFile)
        self.downloadProcess.moveToThread(self.downloadthread)
        # Connect actions
        self.downloadthread.started.connect(self.downloadProcess.downloadFile)
        self.downloadProcess.finished.connect(self.downloadthread.quit)
        self.downloadProcess.finished.connect(lambda: self.moduleInstalled(fileItems, cloudID, notification))
        self.downloadProcess.finished.connect(self.downloadProcess.deleteLater)
        self.downloadthread.finished.connect(self.downloadthread.deleteLater)
        # Start a QThread
        self.downloadthread.start()

    def moduleInstalled(self, fileItems, cloudID, notification=True):
        if hasattr(self, "downloader") and self.downloader.isVisible():
            self.downloader.close()
        # Check if file is successfully installed
        localFile = os.path.join(*fileItems)
        if os.path.isfile(localFile):
            # Reload Master Control
            self.reloadControlPanel(False)
            # Update install history
            config.installHistory[fileItems[-1]] = cloudID
            # Notify users
            if notification:
                self.displayMessage(config.thisTranslation["message_installed"])
        elif notification:
            self.displayMessage(config.thisTranslation["message_failedToInstall"])
        config.isDownloading = False
        Commentary().reloadFileLookup()
        CatalogUtil.reloadLocalCatalog()
        self.setupMenuLayout(config.menuLayout)

    def downloadGoogleStaticMaps(self):
        # https://developers.google.com/maps/documentation/maps-static/intro
        # https://developers.google.com/maps/documentation/maps-static/dev-guide
        for entry, location, lat, lng in exlbl.locations:
            print("downloading a map on '{0}' ...".format(location))
            # url variable store url
            url = "https://maps.googleapis.com/maps/api/staticmap?"
            # zoom defines the zoom
            # level of the map
            zoom = 9
            # specify size, maximum 640x640
            size = "640x640"
            # specify scale, value ranges from 1 to 4
            scale = 2
            # get method of requests module
            # return response object
            fullUrl = "{0}center={1},{2}&zoom={3}&size={4}&key={5}&scale={6}&markers=color:red%7Clabel:{7}%7C{1},{2}".format(
                url, lat, lng, zoom, size, config.myGoogleApiKey, scale, location[0])
            r = requests.get(fullUrl)
            # wb mode is stand for write binary mode
            filepath = os.path.join("htmlResources", "images", "exlbl_largeHD", "{0}.png".format(entry))
            with open(filepath, "wb") as f:
                # r.content gives content,
                # in this case gives image
                f.write(r.content)
        print("done")

    def setStudyBibleToolBar(self):
        if not config.noStudyBibleToolbar and hasattr(self, "studyBibleToolBar"):
            if config.openBibleInMainViewOnly:
                self.studyBibleToolBar.hide()
            else:
                self.studyBibleToolBar.show()

    # install marvel data
    def installMarvelBibles(self):
        installAll = "Install ALL Bibles"
        bibles = DatafileLocation.marvelBibles
        items = [bible for bible in bibles.keys() if
                 not os.path.isfile(os.path.join(os.getcwd(), *bibles[bible][0])) or self.isNewerAvailable(
                     self.bibleInfo[bible][0][-1])]
        if items:
            items.append(installAll)
        else:
            items = ["[All Installed]"]
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        config.thisTranslation["menu8_bibles"], items, 0, False)
        if ok and item and not item in ("[All Installed]", installAll):
            self.downloadHelper(bibles[item])
        elif item == installAll:
            self.installAllMarvelFiles(bibles, installAll)
        self.reloadResources()

    def installMarvelCommentaries(self):
        installAll = "Install ALL Commentaries"
        commentaries = DatafileLocation.marvelCommentaries
        items = [commentary for commentary in commentaries.keys() if
                 not os.path.isfile(os.path.join(os.getcwd(), *commentaries[commentary][0]))]
        if items:
            items.append(installAll)
        else:
            items = ["[All Installed]"]
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        config.thisTranslation["menu8_commentaries"], items, 0, False)
        if ok and item and not item in ("[All Installed]", installAll):
            self.downloadHelper(commentaries[item])
            self.reloadResources()
        elif item == installAll:
            self.installAllMarvelFiles(commentaries, installAll)

    def installAllMarvelFiles(self, files, installAll):
        if config.isDownloading:
            self.displayMessage(config.thisTranslation["previousDownloadIncomplete"])
        else:
            toBeInstalled = [file for file in files.keys() if
                             not file == installAll and not os.path.isfile(
                                 os.path.join(os.getcwd(), *files[file][0]))]
            self.displayMessage("{0}  {1}".format(config.thisTranslation["message_downloadAllFiles"],
                                                  config.thisTranslation["message_willBeNoticed"]))
            print("Downloading {0} files".format(len(toBeInstalled)))
            for file in toBeInstalled:
                databaseInfo = files[file]
                downloader = Downloader(self, databaseInfo)
                print("Downloading " + file)
                downloader.downloadFile(False)
            self.reloadResources()
            print("Downloading complete")
            self.displayMessage(config.thisTranslation["message_installed"])

    def installMarvelDatasets(self):
        installAll = "Install ALL Datasets"
        datasets = DatafileLocation.marvelData
        items = [dataset for dataset in datasets.keys() if not os.path.isfile(os.path.join(os.getcwd(), *datasets[dataset][0]))]
        if items:
            items.append(installAll)
        else:
            items = ["[All Installed]"]
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        config.thisTranslation["menu8_datasets"], items, 0, False)
        if ok and item and not item in ("[All Installed]", installAll):
            self.downloadHelper(datasets[item])
        elif item == installAll:
            self.installAllMarvelFiles(datasets, installAll)
        self.reloadResources()

    def installGithubBibles(self):
        self.installFromGitHub(GitHubRepoInfo.bibles)

    def installGithubBiblesIndex(self):
        self.installFromGitHub(GitHubRepoInfo.biblesIndex)

    def installGithubCommentaries(self):
        self.installFromGitHub(GitHubRepoInfo.commentaries)

    def installGithubHymnLyrics(self):
        self.installFromGitHub(GitHubRepoInfo.hymnLyrics)

    def installGithubBooks(self):
        self.installFromGitHub(GitHubRepoInfo.books)

    def installGithubStatistics(self):
        self.installFromGitHub(GitHubRepoInfo.statistics)

    def installGithubMaps(self):
        self.installFromGitHub(GitHubRepoInfo.maps)

    def installGithubPdf(self):
        self.installFromGitHub(GitHubRepoInfo.pdf)

    def installGithubEpub(self):
        self.installFromGitHub(GitHubRepoInfo.epub)

    def installGithubBibleMp3(self, audioModule=""):
        from uniquebible.gui.DownloadBibleMp3Dialog import DownloadBibleMp3Dialog
        self.downloadBibleMp3Dialog = DownloadBibleMp3Dialog(self, audioModule)
        self.downloadBibleMp3Dialog.show()

    def installGithubPluginsContext(self):
        if self.installFromGitHub(GitHubRepoInfo.pluginsContext):
            self.displayMessage(config.thisTranslation["message_configurationTakeEffectAfterRestart"])

    def installGithubPluginsMenu(self):
        if self.installFromGitHub(GitHubRepoInfo.pluginsMenu):
            self.displayMessage(config.thisTranslation["message_configurationTakeEffectAfterRestart"])

    def installGithubPluginsStartup(self):
        if self.installFromGitHub(GitHubRepoInfo.pluginsStartup):
            self.displayMessage(config.thisTranslation["message_configurationTakeEffectAfterRestart"])

    def installGithubDevotionals(self):
        self.installFromGitHub(GitHubRepoInfo.devotionals)

    def installGithubBibleAbbreviations(self):
        self.installFromGitHub(GitHubRepoInfo.bibleAbbreviations)
        BibleBooks.initialized = False
        self.setupMenuLayout(config.menuLayout)

    def showUserReposDialog(self):
        from uniquebible.gui.UserReposDialog import UserReposDialog
        self.userReposDialog = UserReposDialog(self)
        self.userReposDialog.show()

    def installFromGitHub(self, gitHubRepoInfo):
        repo, directory, title, extension = gitHubRepoInfo
        if ("Pygithub" in config.enabled):
            try:
                from uniquebible.util.GithubUtil import GithubUtil

                installAll = "Install ALL"
                github = GithubUtil(repo)
                repoData = github.getRepoData()
                folder = os.path.join(config.marvelData, directory)
                items = [item for item in repoData.keys() if not FileUtil.regexFileExists("^{0}.*".format(GithubUtil.getShortname(item).replace(".", "\\.")), folder)]
                if items:
                    items.append(installAll)
                else:
                    items = ["[All Installed]"]
                selectedItem, ok = QInputDialog.getItem(self, "UniqueBible",
                                                config.thisTranslation[title], items, 0, False)
                if ok and selectedItem:
                    if selectedItem == installAll:
                        self.displayMessage("{0}  {1}".format(config.thisTranslation["message_downloadAllFiles"],
                                                              config.thisTranslation["message_willBeNoticed"]))
                        items.remove(installAll)
                        print("Downloading {0} files".format(len(items)))
                    else:
                        self.displayMessage(selectedItem + " " + config.thisTranslation["message_installing"])
                        items = [selectedItem]
                    for index, item in enumerate(items):
                        file = os.path.join(folder, item+".zip")
                        print("Downloading {0}".format(file))
                        github.downloadFile(file, repoData[item])
                        with zipfile.ZipFile(file, 'r') as zipped:
                            zipped.extractall(folder)
                        os.remove(file)
                    print("Downloading complete")
                    self.reloadResources()
                    if selectedItem == installAll:
                        self.displayMessage(config.thisTranslation["message_installed"])
                    else:
                        self.installFromGitHub(gitHubRepoInfo)
                return True

            except Exception as ex:
                self.displayMessage(config.thisTranslation["couldNotAccess"] + " " + repo)
                print(ex)
        return False

    # Select database to modify
    def selectDatabaseToModify(self):
        items = BiblesSqlite().getFormattedBibleList()
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        config.thisTranslation["modify_database"], items, 0, False)
        if ok and item:
            dialog = ModifyDatabaseDialog("bible", item)
            dialog.exec_()

    # Select language file to edit
    def selectLanguageFileToEdit(self):
        items = LanguageUtil.getCodesSupportedLanguages()
        index = items.index(config.workingTranslation)
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        config.thisTranslation["edit_language_file"], items, index, False)
        if ok and item:
            config.workingTranslation = item
            dialog = EditGuiLanguageFileDialog(self, item)
            dialog.exec_()

    def selectReferenceTranslation(self):
        items = LanguageUtil.getCodesSupportedLanguages()
        index = items.index(config.referenceTranslation)
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        "Select Tooltip Translation", items, index, False)
        if ok and item:
            config.referenceTranslation = item

    def editWorkingTranslation(self):
        dialog = EditGuiLanguageFileDialog(self, config.workingTranslation)
        dialog.exec_()
        

    # convert bible references to string
    def bcvToVerseReference(self, b, c, v):
        parser = BibleVerseParser(config.parserStandarisation)
        verseReference = parser.bcvToVerseReference(b, c, v)
        del parser
        return verseReference

    # Open text on left and right view
    def openTextOnMainView(self, text, textCommand):
        updateMainReferenceOnChangingTabs = config.updateMainReferenceOnChangingTabs
        config.updateMainReferenceOnChangingTabs = False
        if config.bibleWindowContentTransformers:
            for transformer in config.bibleWindowContentTransformers:
                text = transformer(text)
        if hasattr(config, "cli"):
            config.bibleWindowContent = text
        if self.newTabException:
            self.newTabException = False
        elif self.syncingBibles:
            self.syncingBibles = False
        elif config.openBibleWindowContentOnNextTab:
            self.nextBibleWindowTab()
        # check size of text content
        if config.forceGenerateHtml or sys.getsizeof(text) > 2097152:
            # save html in a separate file if text is larger than 2MB
            # reason: setHTML does not work with content larger than 2MB
            outputFile = os.path.join("htmlResources", "main.html")
            fileObject = open(outputFile, "w", encoding="utf-8")
            fileObject.write(text)
            fileObject.close()
            # open the text file with webview
            fullOutputPath = os.path.abspath(outputFile)
            self.mainView.load(QUrl.fromLocalFile(fullOutputPath))
        else:
            self.mainView.setHtml(text, baseUrl)
        reference = "-".join(self.verseReference("main"))
        lastKeyword = self.textCommandParser.lastKeyword
        if lastKeyword in ("compare", "parallel", "sidebyside"):
            *_, reference2 = reference.split("-")
            reference = "{0}-{1}".format(lastKeyword[0:4], reference2)
        self.mainView.setTabText(self.mainView.currentIndex(), reference)
        self.mainView.setTabToolTip(self.mainView.currentIndex(), textCommand)
        config.updateMainReferenceOnChangingTabs = updateMainReferenceOnChangingTabs

    def setClipboardMonitoring(self, option):
        if not config.enableClipboardMonitoring == option:
            config.enableClipboardMonitoring = not config.enableClipboardMonitoring
        if config.enableSystemTray:
            if config.enableClipboardMonitoring:
                config.monitorOption1.setChecked(True)
                config.monitorOption2.setChecked(False)
            else:
                config.monitorOption1.setChecked(False)
                config.monitorOption2.setChecked(True)
        if config.menuLayout == "material":
            self.setClipboardMonitoringSubmenu()

    def setAppWindowStyle(self, style):
        config.windowStyle = "" if style == "default" else style
        #self.displayMessage(config.thisTranslation["message_themeTakeEffectAfterRestart"])
        if config.menuLayout == "material":
            self.setAppWindowStyleSubmenu()
        self.handleRestart()

    def setApplicationIcon(self, icon):
        config.desktopUBAIcon = icon
        if config.menuLayout == "material":
            self.setApplicationIconSubmenu()
        self.handleRestart()

    def setQtMaterialTheme(self, theme):
        config.qtMaterialTheme = theme
        #self.displayMessage(config.thisTranslation["message_themeTakeEffectAfterRestart"])
        self.handleRestart()

    def enableQtMaterial(self, qtMaterial=True):
        if qtMaterial:
            try:
                from qt_material import apply_stylesheet
                self.selectQtMaterialTheme()
            except:
                config.qtMaterial = False
                self.displayMessage(config.thisTranslation["installQtMaterial"])
        else:
            self.selectBuiltinTheme()

    def selectQtMaterialTheme(self):
        items = ("light_amber.xml", "light_blue.xml", "light_cyan.xml", "light_cyan_500.xml", "light_lightgreen.xml",
                 "light_pink.xml", "light_purple.xml", "light_red.xml", "light_teal.xml", "light_yellow.xml",
                 "dark_amber.xml", "dark_blue.xml", "dark_cyan.xml", "dark_lightgreen.xml", "dark_pink.xml",
                 "dark_purple.xml", "dark_red.xml", "dark_teal.xml", "dark_yellow.xml")
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        config.thisTranslation["menu1_selectThemeQtMaterial"], items, items.index(
                config.qtMaterialTheme) if config.qtMaterialTheme and config.qtMaterialTheme in items else 0, False)
        if ok and item:
            config.qtMaterial = True
            config.qtMaterialTheme = item
            self.resetUI()
            #self.displayMessage(config.thisTranslation["message_themeTakeEffectAfterRestart"])

    def selectBuiltinTheme(self):
        items = ("default", "dark", "night")
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        config.thisTranslation["menu1_selectThemeBuiltin"], items,
                                        items.index(config.theme) if config.theme and config.theme in items else 0,
                                        False)
        if ok and item:
            config.qtMaterial = False
            config.theme = item
            self.resetUI()
            #self.displayMessage(config.thisTranslation["message_themeTakeEffectAfterRestart"])

    def setDefaultTheme(self):
        config.theme = "default"
        #self.displayMessage(config.thisTranslation["message_themeTakeEffectAfterRestart"])
        self.handleRestart()

    def setDarkTheme(self):
        config.theme = "dark"
        #self.displayMessage(config.thisTranslation["message_themeTakeEffectAfterRestart"])
        self.handleRestart()

    def setTheme(self, theme, setColours=True):
        theme = theme.split(" ")
        if len(theme) == 2:
            theme, mainColor = theme
        else:
            theme = theme[0]
            mainColor = ""
        theme = theme.lower()
        if theme == "light":
            theme = "default"
        config.theme = theme
        if mainColor and setColours:
            self.setColours(mainColor)
        elif config.menuLayout == "material":
            if setColours:
                self.setColours()
        else:
            self.setupMenuLayout(config.menuLayout)
        PluginEventHandler.handleEvent("post_theme_change")
        self.resetUI()

    def setColours(self, color=""):
        config.menuLayout = "material"
        if config.theme in ("dark", "night"):
            config.maskMaterialIconColor = '#FFFFE0'
            config.maskMaterialIconBackground = False
            config.widgetBackgroundColor = '#2f2f2f'
            config.widgetForegroundColor = '#FFFFE0'
            config.widgetBackgroundColorHover = '#545454'
            config.widgetForegroundColorHover = '#FFFFE0'
            config.widgetBackgroundColorPressed = '#232323'
            config.widgetForegroundColorPressed = '#FFFFE0'
            config.darkThemeTextColor = '#ffffff'
            config.darkThemeActiveVerseColor = '#aaff7f'
        else:
            config.maskMaterialIconColor = "#483D8B"
            config.maskMaterialIconBackground = False
            config.widgetBackgroundColor = "#e7e7e7"
            config.widgetForegroundColor = "#483D8B"
            config.widgetBackgroundColorHover = "#f8f8a0"
            config.widgetForegroundColorHover = "#483D8B"
            config.widgetBackgroundColorPressed = "#d9d9d9"
            config.widgetForegroundColorPressed = "#483D8B"
            config.lightThemeTextColor = "#000000"
            config.lightThemeActiveVerseColor = "#483D8B"
        if color:
            color = HtmlColorCodes.colors[color][0]
            config.maskMaterialIconBackground = False
            config.maskMaterialIconColor = color
            config.widgetForegroundColor = color
            config.widgetForegroundColorHover = color
            config.widgetForegroundColorPressed = color
            if config.theme in ("dark", "night"):
                config.darkThemeActiveVerseColor = color
            else:
                config.lightThemeActiveVerseColor = color
        config.defineStyle()
        self.setupMenuLayout("material")

    def setClassicMenuLayout(self):
        self.setupMenuLayout("classic")

    def setFocusMenuLayout(self):
        self.setupMenuLayout("focus")

    def setMaterialMenuLayout(self):
        self.setupMenuLayout("material")

    def setAlephMenuLayout(self):
        self.setupMenuLayout("aleph")

    def setShortcuts(self, shortcut):
        config.menuShortcuts = shortcut
        ShortcutUtil.reset()
        ShortcutUtil.setup(shortcut)
        ShortcutUtil.loadShortcutFile()
        self.setupMenuLayout(config.menuLayout)

    def showUpdateAppWindow(self):
        updateAppWindow = AppUpdateDialog(self)
        updateAppWindow.exec()

    def displayShortcuts(self):
        shortcutWindow = DisplayShortcutsWindow(config.menuShortcuts, ShortcutUtil.getAllShortcuts())
        if shortcutWindow.exec():
            ShortcutUtil.setup(config.menuShortcuts)
            ShortcutUtil.loadShortcutFile(config.menuShortcuts)
            ShortcutUtil.loadShortcutFile()
            self.setupMenuLayout(config.menuLayout)

    def showInfo(self):
        infoDialog = InfoDialog()
        infoDialog.exec()

    def showConfigPyDocumentation(self):
        intro = "File config.py contains essential configurations for running UniqueBible.app.\n(Remarks: Generally speaking, users don't need to edit this file.\nIn case you need to do so, make sure UBA is not running when you manually edit this file.)\n\nIndividual items in config.py are briefly described below:\n(You may find more information of boolean settings via 'Config Flags Window'.)"
        content = "{0}\n\n{1}".format(intro, "\n\n".join(["[ITEM] {0}{1}".format(key, re.sub("        # ", "", value)) for key, value in config.help.items()]))
        infoDialog = InfoDialog(content, "config.py")
        infoDialog.exec()

    def showCommandDocumentation(self):
        content = "UBA commands:\n{0}".format("\n".join([re.sub("            #", "#", value[-1]) for value in config.mainWindow.textCommandParser.interpreters.values()]))
        infoDialog = InfoDialog(content, config.thisTranslation["ubaCommands"])
        infoDialog.exec()

    def exportAllImages(self, htmlText):
        self.exportImageNumber = 0
        searchPattern = r'src=(["{0}])data:image/([^<>]+?);[ ]*?base64,[ ]*?([^ <>]+?)\1'.format("'")
        htmlText = re.sub(searchPattern, self.exportAnImage, htmlText)
        return htmlText

    def exportAnImage(self, match):
        exportFolder = os.path.join("htmlResources", "images", "export")
        if not os.path.isdir(exportFolder):
            os.makedirs(exportFolder)
        quotationMark, ext, asciiString = match.groups()
        # Note the difference between "groups" and "group"
        # wholeString = match.group(0)
        # quotationMark = match.group(1)
        # ext = match.group(2)
        # asciiString = match.group(3)
        self.exportImageNumber += 1
        binaryString = asciiString.encode("ascii")
        binaryData = base64.b64decode(binaryString)
        imageFilename = "tab{0}_image{1}.{2}".format(self.studyView.currentIndex(), self.exportImageNumber, ext)
        exportPath = os.path.join(exportFolder, imageFilename)
        with open(exportPath, "wb") as fileObject2:
            fileObject2.write(binaryData)
        return "src={0}images/export/{1}{0}".format(quotationMark, imageFilename)

    def addOpenImageAction(self, text):
        return re.sub(r"(<img[^<>]*?src=)(['{0}])(images/[^<>]*?)\2([^<>]*?>)".format('"'),
                      r"<ref onclick={0}openHtmlFile('\3'){0}>\1\2\3\2\4</ref>".format('"'), text)

    def refreshBibleWindowTab(self):
        self.previousBibleWindowTab()
        self.nextBibleWindowTab()

    def refreshStudyWindowTab(self):
        self.previousStudyWindowTab()
        self.nextStudyWindowTab()

    def previousBibleWindowTab(self):
        previousIndex = self.mainView.currentIndex() - 1
        if previousIndex < 0:
            previousIndex = config.numberOfTab - 1
        self.mainView.setCurrentIndex(previousIndex)

    def previousStudyWindowTab(self):
        previousIndex = self.studyView.currentIndex() - 1
        if previousIndex < 0:
            previousIndex = config.numberOfTab - 1
        self.studyView.setCurrentIndex(previousIndex)

    def nextBibleWindowTab(self):
        nextIndex = self.mainView.currentIndex() + 1
        if nextIndex >= config.numberOfTab:
            nextIndex = 0
        self.mainView.setCurrentIndex(nextIndex)

    def nextStudyWindowTab(self):
        nextIndex = self.studyView.currentIndex() + 1
        if nextIndex >= config.numberOfTab:
            nextIndex = 0
        self.studyView.setCurrentIndex(nextIndex)
        # Alternatively,
        # self.studyView.setCurrentWidget(self.studyView.widget(nextIndex))

    def openTextOnStudyView(self, text, tab_title='', anchor=None, toolTip=""):
        if config.studyWindowContentTransformers:
            for transformer in config.studyWindowContentTransformers:
                text = transformer(text)
        if hasattr(config, "cli"):
            config.studyWindowContent = text
        if self.newTabException:
            self.newTabException = False
        elif self.syncingBibles:
            self.syncingBibles = False
        elif config.openStudyWindowContentOnNextTab:
            self.nextStudyWindowTab()
        # export embedded images if enabled
        if config.exportEmbeddedImages:
            text = self.exportAllImages(text)
        # added links to open image files if enabled
        if config.clickToOpenImage:
            text = self.addOpenImageAction(text)
        if anchor is not None:
            js = "jump('{0}');".format(anchor)
            self.studyView.currentWidget().loadFinished.connect(lambda: self.finishStudyViewLoading(None, js=js))
        # check size of text content
        if config.forceGenerateHtml or sys.getsizeof(text) > 2097152:
            # save html in a separate file if text is larger than 2MB
            # reason: setHTML does not work with content larger than 2MB
            outputFile = os.path.join("htmlResources", "study.html")
            fileObject = open(outputFile, "w", encoding="utf-8")
            fileObject.write(text)
            fileObject.close()
            # open the text file with webview
            fullOutputPath = os.path.abspath(outputFile)
            self.studyView.load(QUrl.fromLocalFile(fullOutputPath))
        else:
            self.studyView.setHtml(text, baseUrl)

        if config.parallelMode == 0:
            self.parallel()
        if self.textCommandParser.lastKeyword == "main":
            self.textCommandParser.lastKeyword = "study"
        if tab_title == '':
            tab_title = self.textCommandParser.lastKeyword
        self.studyView.setTabText(self.studyView.currentIndex(), tab_title)
        toolTip = toolTip if toolTip else tab_title
        self.studyView.setTabToolTip(self.studyView.currentIndex(), toolTip)

    # warning for next action without saving modified notes
    def toggleNoteEditor(self):
        if hasattr(config, "toggleDockWidget"):
            self.noteEditor.toggleViewAction().activate(QAction.Trigger)
        else:
            self.createNewNoteFile()

    def showNoteEditor(self):
        if hasattr(self, "noteEditor"):
            if not self.noteEditor.isVisible():
                self.noteEditor.setVisible(True)

    def openNoteEditorFileViaMenu(self):
        if not hasattr(self, "noteEditor"):
            self.noteEditor = NoteEditor(self, "file")
        self.showNoteEditor()
        self.noteEditor.noteEditor.openFileDialog()

    def saveNoteEditorFileViaMenu(self):
        if not hasattr(self, "noteEditor"):
            self.noteEditor = NoteEditor(self, "file")
        self.showNoteEditor()
        self.noteEditor.noteEditor.saveNote()

    def saveAsNoteEditorFileViaMenu(self):
        if not hasattr(self, "noteEditor"):
            self.noteEditor = NoteEditor(self, "file")
        self.showNoteEditor()
        self.noteEditor.noteEditor.openSaveAsDialog()

    def warningNotSaved(self):
        self.showNoteEditor()
        msgBox = QMessageBox(QMessageBox.Warning,
                             config.thisTranslation["attention"],
                             "Notes are currently opened and modified.  Do you really want to continue, without saving the changes?",
                             QMessageBox.NoButton, self)
        msgBox.addButton("Cancel", QMessageBox.RejectRole)
        msgBox.addButton("&Continue", QMessageBox.AcceptRole)
        answer = msgBox.exec_()
        if answer:
        #if answer == 1 or answer == QMessageBox.AcceptRole:
            # Continue
            self.noteSaved = True
            return True
        else:
            # Cancel
            self.noteSaved = False
            return False

    def insertContextTextToNoteEditor(self):
        if config.contextItem:
            self.noteEditor.noteEditor.editor.insertPlainText(config.contextItem)
            config.contextItem = ""

    # Actions - chapter / verse / new file note
    def createNewNoteFile(self):
        if not hasattr(self, "noteEditor"):
            self.noteEditor = NoteEditor(self, "file")
        else:
            self.showNoteEditor()
            if self.noteSaved or self.warningNotSaved():
                self.noteEditor.noteEditor.resetVariables()
                self.noteEditor.noteEditor.newNoteFileAction()
        self.insertContextTextToNoteEditor()

    def displayContentInNoteEditor(self, html):
        if not hasattr(self, "noteEditor"):
            self.noteEditor = NoteEditor(self, "file")
            self.noteEditor.noteEditor.editor.setHtml(html)
        else:
            self.showNoteEditor()
            if self.noteSaved or self.warningNotSaved():
                self.noteEditor.noteEditor.resetVariables()
                self.noteEditor.noteEditor.newNoteFileAction()
                self.noteEditor.noteEditor.editor.setHtml(html)

    def openNoteEditor(self, noteType, b=None, c=None, v=None, year=None, month=None, day=None):
        if not hasattr(self, "noteEditor"):
            self.noteEditor = NoteEditor(self, noteType, b=b, c=c, v=v, year=year, month=month, day=day)
        else:
            self.showNoteEditor()
            if not config.lastOpenedNote == (noteType, b, c, v, year, month, day) and (self.noteSaved or self.warningNotSaved()):
                self.noteEditor.noteEditor.resetVariables()
                self.noteEditor.noteEditor.displayInitialContent(noteType, b, c, v, year, month, day)
        self.insertContextTextToNoteEditor()

    def editExternalFileHistoryRecord(self, record):
        filename = config.history["external"][record]
        fileExtension = filename.split(".")[-1].lower()
        directEdit = ("uba", "html", "htm")
        if fileExtension in directEdit:
            if not hasattr(self, "noteEditor"):
                self.noteEditor = NoteEditor(self, "file", filename)
            else:
                self.showNoteEditor()
                if self.noteSaved or self.warningNotSaved():
                    self.noteEditor.noteEditor.resetVariables()
                    self.noteEditor.noteEditor.noteFileName = filename
                    self.noteEditor.noteEditor.displayInitialContent("file")
        else:
            self.openExternalFile(filename)

    def bringToForeground(self, window):
        if window and not (window.isVisible() and window.isActiveWindow()):
            window.raise_()
            # Method activateWindow() does not work with qt.qpa.wayland
            # platform.system() == "Linux" and not os.getenv('QT_QPA_PLATFORM') is None and os.getenv('QT_QPA_PLATFORM') == "wayland"
            # The error message is received when QT_QPA_PLATFORM=wayland:
            # qt.qpa.wayland: Wayland does not support QWindow::requestActivate()
            # Therefore, we use hide and show methods instead with wayland.
            if window.isVisible() and not window.isActiveWindow():
                window.hide()
            window.show()
            if not SystemUtil.isWayland():
                window.activateWindow()

    def openMainBookNote(self):
        self.openBookNote(config.mainB)

    def openMainChapterNote(self):
        self.openChapterNote(config.mainB, config.mainC)

    def openMainVerseNote(self):
        self.openVerseNote(config.mainB, config.mainC, config.mainV)

    def openStudyBookNote(self):
        self.openBookNote(config.studyB)

    def openStudyChapterNote(self):
        self.openChapterNote(config.studyB, config.studyC)

    def openStudyVerseNote(self):
        self.openVerseNote(config.studyB, config.studyC, config.studyV)

    def fixNoteFontDisplay(self, content):
        if config.overwriteNoteFont:
            content = re.sub("font-family:[^<>]*?([;'{0}])".format('"'), r"font-family:{0}\1".format(config.font),
                             content)
        if config.overwriteNoteFontSize:
            content = re.sub("font-size:[^<>]*?;", "", content)
        return content

    def openBibleNotes(self, noteType, bcv=None):
        # bcv should look like 43.3.16
        if bcv is None:
            bcv = "{0}.{1}.{2}".format(config.mainB, config.mainC, config.mainV)
        keywords = {
            "book": "_openbooknote",
            "chapter": "_openchapternote",
            "verse": "_openversenote",
        }
        command = "{0}:::{1}".format(keywords[noteType], bcv)
        self.runTextCommand(command)

    def editBibleNotes(self, noteType, bcv=None):
        # bcv should look like 43.3.16
        if bcv is None:
            bcv = "{0}.{1}.{2}".format(config.mainB, config.mainC, config.mainV)
        keywords = {
            "book": "_editbooknote",
            "chapter": "_editchapternote",
            "verse": "_editversenote",
        }
        command = "{0}:::{1}".format(keywords[noteType], bcv)
        self.runTextCommand(command)

    def openBookNote(self, b):
        self.textCommandParser.lastKeyword = "note"
        reference = BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, 1, 1)
        config.studyB, config.studyC, config.studyV = b, 1, 1
        self.updateStudyRefButton()
        config.commentaryB, config.commentaryC, config.commentaryV = b, 1, 1
        self.updateCommentaryRefButton()
        note = NoteService.getBookNote(b)
        note = self.fixNoteFontDisplay(note)
        reference = reference[:-4]
        note = "<p style=\"font-family:'{3}'; font-size:{4}pt;\"><b>Note on {0}</b> &ensp;<button class='ubaButton' onclick='document.title=\"_editbooknote:::{2}\"'>edit</button></p>{1}".format(
            reference, note, b, config.font, config.fontSize)
        note = self.htmlWrapper(note, True, "study", False)
        history = "OPENBOOKNOTE:::{0}".format(reference)
        self.openTextOnStudyView(note, tab_title="note-{0}".format(reference), toolTip=history)
        self.addHistoryRecord("study", history)

    def openChapterNote(self, b, c):
        self.textCommandParser.lastKeyword = "note"
        reference = BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, 1)
        config.studyB, config.studyC, config.studyV = b, c, 1
        self.updateStudyRefButton()
        config.commentaryB, config.commentaryC, config.commentaryV = b, c, 1
        self.updateCommentaryRefButton()
        note = NoteService.getChapterNote(b, c)
        note = self.fixNoteFontDisplay(note)
        reference = reference[:-2]
        history = "OPENCHAPTERNOTE:::{0}".format(reference)
        note = "<p style=\"font-family:'{4}'; font-size:{5}pt;\"><b>Note on {0}</b> &ensp;<button class='ubaButton' onclick='document.title=\"_editchapternote:::{2}.{3}\"'>edit</button></p>{1}".format(
            reference, note, b, c, config.font, config.fontSize)
        note = self.htmlWrapper(note, True, "study", False)
        self.openTextOnStudyView(note, tab_title="note-{0}".format(reference), toolTip=history)
        self.addHistoryRecord("study", history)

    def openVerseNote(self, b, c, v):
        self.textCommandParser.lastKeyword = "note"
        reference = BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)
        config.studyB, config.studyC, config.studyV = b, c, v
        self.updateStudyRefButton()
        config.commentaryB, config.commentaryC, config.commentaryV = b, c, v
        self.updateCommentaryRefButton()
        note = NoteService.getVerseNote(b, c, v)
        note = self.fixNoteFontDisplay(note)
        note = "<p style=\"font-family:'{5}'; font-size:{6}pt;\"><b>Note on {0}</b> &ensp;<button class='ubaButton' onclick='document.title=\"_editversenote:::{2}.{3}.{4}\"'>edit</button></p>{1}".format(
            reference, note, b, c, v, config.font, config.fontSize)
        note = self.htmlWrapper(note, True, "study", False)
        history = "OPENVERSENOTE:::{0}".format(reference)
        self.openTextOnStudyView(note, tab_title="note-{0}".format(reference), toolTip=history)
        self.addHistoryRecord("study", history)

    def getHighlightCss(self):
        css = ""
        for i in range(len(config.highlightCollections)):
            code = "hl{0}".format(i + 1)
            css += ".{2} {0} background: {3}; {1} ".format("{", "}", code, config.highlightDarkThemeColours[i] if config.theme in ("dark", "night") else config.highlightLightThemeColours[i])
        return css

    # Actions - open text from external sources
    def htmlWrapper(self, text, parsing=False, view="study", linebreak=True, html=True):
        searchReplace1 = (
            ("\r\n|\r|\n", "<br>"),
            ("\t", "&emsp;&emsp;"),
        )
        searchReplace2 = (
            ("<br>(<table>|<ol>|<ul>)", r"\1"),
            ("(</table>|</ol>|</ul>)<br>", r"\1"),
            ("<a [^\n<>]*?href=['{0}]([^\n<>]*?)['{0}][^\n<>]*?>".format('"'),
             r"<a href='javascript:void(0)' onclick='website({0}\1{0})'>".format('"')),
            (r"onclick='website\({0}([^\n<>]*?).uba{0}\)'".format('"'), r"onclick='uba({0}\1.uba{0})'".format('"'))
        )
        if linebreak:
            for search, replace in searchReplace1:
                text = re.sub(search, replace, text)
        if html:
            for search, replace in searchReplace2:
                text = re.sub(search, replace, text)
        if parsing:
            # Export inline images to external files, so as to improve parsing performance. 
            text = self.exportAllImages(text)
            text = TextUtil.formulateUBACommandHyperlink(text)
            text = BibleVerseParser(config.parserStandarisation).parseText(text)
        if not "<!DOCTYPE html><html><head><meta charset='utf-8'><title>UniqueBible.app</title>" in text:
            text = self.wrapHtml(text, view)
        return text

    def getClipboardText(self):
        clipboardText = QApplication.clipboard().text()
        if not clipboardText:
            text, ok = QInputDialog.getText(self, "Unique Bible App",
                    config.thisTranslation["enter_text_here"], QLineEdit.Normal,
                    "")
            if ok and text:
                clipboardText = text
        config.clipboardText = clipboardText
        return clipboardText

    def setClipboardText(self, text):
        QApplication.clipboard().setText(text)
        QApplication.clipboard().setText(text, QClipboard.Selection)
        QApplication.clipboard().setText(text, QClipboard.Clipboard)

    def pasteFromClipboard(self):
        clipboardText = self.getClipboardText()
        #clipboardText = QGuiApplication.instance().clipboard().text()
        # note: can use QGuiApplication.instance().clipboard().setText to set text in clipboard
        if clipboardText:
            self.openTextOnStudyView(self.htmlWrapper(clipboardText, True), tab_title="clipboard")
        else:
            self.displayMessage(config.thisTranslation["noClipboardContent"])

    def openReferencesOnClipboard(self):
        clipboardText = self.getClipboardText()
        if clipboardText:
            parser = BibleVerseParser(config.parserStandarisation)
            verseList = parser.extractAllReferences(clipboardText, False)
            if not verseList:
                self.displayMessage(config.thisTranslation["message_noReference"])
            else:
                references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verseList])
                self.runTextCommand(references)
        else:
            self.displayMessage(config.thisTranslation["noClipboardContent"])

    def clipboardTts(self, language):
        clipboardText = self.getClipboardText()
        if clipboardText:
            if config.isGoogleCloudTTSAvailable or ((not ("OfflineTts" in config.enabled) or config.forceOnlineTts) and ("Gtts" in config.enabled)):
                self.mainView.currentWidget().googleTextToSpeechLanguage(language, selectedText=clipboardText)
            elif ("OfflineTts" in config.enabled):
                self.mainView.currentWidget().textToSpeechLanguage(language, selectedText=clipboardText)
        else:
            self.displayMessage(config.thisTranslation["noClipboardContent"])

    def readClipboardContent(self):
        clipboardText = self.getClipboardText()
        if clipboardText:
            if ("OnlineTts" in config.enabled) and not config.isGoogleCloudTTSAvailable and not config.forceOnlineTts:
                keyword = "SPEAK"
            else:
                keyword = "GTTS"
            command = "{0}:::{1}".format(keyword, clipboardText)
            self.runTextCommand(command)
        else:
            self.displayMessage(config.thisTranslation["noClipboardContent"])

    def searchBibleForClipboardContent(self):
        clipboardText = self.getClipboardText()
        if clipboardText:
            self.runTextCommand("COUNT:::{0}".format(clipboardText))
        else:
            self.displayMessage(config.thisTranslation["noClipboardContent"])

    def searchResourcesForClipboardContent(self):
        clipboardText = QApplication.clipboard().text()
        self.openControlPanelTab(3)
        self.controlPanel.toolTab.searchField.setText(clipboardText if clipboardText else "")

    def runContextPluginOnClipboardContent(self, plugin, clipboardText=""):
        if not clipboardText:
            clipboardText = self.getClipboardText()
        if clipboardText:
            self.mainView.currentWidget().runPlugin(plugin, clipboardText)
        else:
            self.displayMessage(config.thisTranslation["noClipboardContent"])

    def parseContentOnClipboard(self):
        clipboardText = self.getClipboardText()
        if clipboardText:
            self.textCommandLineEdit.setText(clipboardText)
            self.runTextCommand(clipboardText)
            #self.manageControlPanel()
        else:
            self.displayMessage(config.thisTranslation["noClipboardContent"])

    def openTextFileDialog(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                                                      config.thisTranslation["menu7_open"],
                                                      "notes",
                                                      "UniqueBible.app Note Files (*.uba);;HTML Files (*.html);;HTM Files (*.htm);;Markdown Files (*.md);;Word Documents (*.docx);;Plain Text Files (*.txt);;PDF Files (*.pdf);;All Files (*)",
                                                      "", options)
        if fileName:
            self.openTextFile(fileName)

    def openTextFile(self, fileName):
        self.textCommandParser.lastKeyword = "file"
        functions = {
            "pdf": self.openPdfFile,
            "docx": self.openDocxFile,
            "uba": self.openUbaFile,
            "html": self.openUbaFile,
            "htm": self.openUbaFile,
            "md": self.openMarkdownFile,
        }
        function = functions.get(fileName.split(".")[-1].lower(), self.openTxtFile)
        function(fileName)
        self.addExternalFileHistory(fileName)
        self.setExternalFileButton()

    def addExternalFileHistory(self, fileName):
        externalFileHistory = config.history['external']
        if externalFileHistory == [] or externalFileHistory[-1] != fileName:
            if fileName in externalFileHistory:
                externalFileHistory.remove(fileName)
            externalFileHistory.append(fileName)

    def setExternalFileButton(self):
        if not config.menuLayout == "material":
            self.externalFileButton.setText(self.getLastExternalFileName()[:20])
            self.externalFileButton.setToolTip(self.getLastExternalFileName())

    def getLastExternalFileName(self):
        externalFileHistory = config.history["external"]
        if externalFileHistory:
            return os.path.split(externalFileHistory[-1])[-1]
        else:
            return "[open file]"

    def runBookFeatureIntroduction(self):
        engFullBookName = BibleBooks().abbrev["eng"][str(config.mainB)][1]
        command = "SEARCHBOOKCHAPTER:::Tidwell_The_Bible_Book_by_Book:::{0}".format(engFullBookName)
        self.textCommandLineEdit.setText(command)
        self.runTextCommand(command)

    def runBookFeatureTimelines(self):
        engFullBookName = BibleBooks().abbrev["eng"][str(config.mainB)][1]
        command = "SEARCHBOOKCHAPTER:::Timelines:::{0}".format(engFullBookName)
        self.textCommandLineEdit.setText(command)
        self.runTextCommand(command)

    def runBookFeatureDictionary(self):
        engFullBookName = BibleBooks().abbrev["eng"][str(config.mainB)][1]
        matches = re.match("^[0-9]+? (.*?)$", engFullBookName)
        if matches:
            engFullBookName = matches.group(1)
        command = "SEARCHTOOL:::{0}:::{1}".format(config.dictionary, engFullBookName)
        self.textCommandLineEdit.setText(command)
        self.runTextCommand(command)

    def runBookFeatureEncyclopedia(self):
        engFullBookName = BibleBooks().abbrev["eng"][str(config.mainB)][1]
        matches = re.match("^[0-9]+? (.*?)$", engFullBookName)
        if matches:
            engFullBookName = matches.group(1)
        command = "SEARCHTOOL:::{0}:::{1}".format(config.encyclopedia, engFullBookName)
        self.textCommandLineEdit.setText(command)
        self.runTextCommand(command)

    def runChapterFeatureOverview(self):
        bookAbb = BibleBooks().abbrev["eng"][str(config.mainB)][0]
        command = "OVERVIEW:::{0} {1}".format(bookAbb, config.mainC)
        self.textCommandLineEdit.setText(command)
        self.runTextCommand(command)

    def runChapterFeatureChapterIndex(self):
        bookAbb = BibleBooks().abbrev["eng"][str(config.mainB)][0]
        command = "CHAPTERINDEX:::{0} {1}".format(bookAbb, config.mainC)
        self.textCommandLineEdit.setText(command)
        self.runTextCommand(command)

    def runChapterFeatureSummary(self):
        bookAbb = BibleBooks().abbrev["eng"][str(config.mainB)][0]
        command = "SUMMARY:::{0} {1}".format(bookAbb, config.mainC)
        self.textCommandLineEdit.setText(command)
        self.runTextCommand(command)

    def runChapterFeatureCommentary(self):
        bookAbb = BibleBooks().abbrev["eng"][str(config.mainB)][0]
        command = "COMMENTARY:::{0} {1}".format(bookAbb, config.mainC)
        self.textCommandLineEdit.setText(command)
        self.runTextCommand(command)

    def externalFileButtonClicked(self):
        externalFileHistory = config.history["external"]
        if externalFileHistory:
            self.openExternalFileHistoryRecord(-1)
        else:
            self.openTextFileDialog()

    def editExternalFileButtonClicked(self):
        externalFileHistory = config.history["external"]
        if externalFileHistory:
            self.editExternalFileHistoryRecord(-1)
        else:
            self.openTextFileDialog()



    def openExternalFile(self, filename, isPdf=False):
        if platform.system() == "Linux":
            if isPdf:
                subprocess.Popen([config.openLinuxPdf, filename])
            else:
                subprocess.Popen([config.open, filename])
        else:
            os.system("{0} {1}".format(config.open, filename))

    def openExternalFileHistoryRecord(self, record):
        self.openTextFile(config.history["external"][record])

    def openExternalFileHistory(self):
        self.studyView.setHtml(self.getHistory("external"), baseUrl)

    def openTxtFile(self, fileName):
        if fileName:
            text = TextFileReader().readTxtFile(fileName)
            text = self.htmlWrapper(text, True)
            self.openTextOnStudyView(text, tab_title=".txt", toolTip=os.path.basename(fileName))

    def openUbaFile(self, fileName):
        if fileName:
            text = TextFileReader().readTxtFile(fileName)
            text = self.fixNoteFontDisplay(text)
            text = self.htmlWrapper(text, True, "study", False)
            self.openTextOnStudyView(text, tab_title=".uba", toolTip=os.path.basename(fileName))

    def openMarkdownFile(self, fileName):
        if fileName:
            with open(fileName, "r", encoding="utf-8") as input_file:
                text = input_file.read()
            text = markdown.markdown(text)
            text = self.fixNoteFontDisplay(text)
            text = self.htmlWrapper(text, True, "study", False)
            self.openTextOnStudyView(text, tab_title=".md", toolTip=os.path.basename(fileName))

    def openDocxFile(self, fileName):
        #if ("Pythondocx" in config.enabled):
        if ("Mammoth" in config.enabled):
            if fileName:
                text = TextFileReader().readDocxFile(fileName)
                if config.parseWordDocument:
                    text = self.exportAllImages(text)
                    text = text.replace("</p>", "</p>\n")
                    text = TextUtil.formulateUBACommandHyperlink(text)
                    text = BibleVerseParser(config.parserStandarisation).parseText(text)
                text = self.wrapHtml(text, "study")
                #text = self.htmlWrapper(text, True)
                self.openTextOnStudyView(text, tab_title=".docx", toolTip=os.path.basename(fileName))
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])
        else:
            self.displayMessage(config.thisTranslation["message_noSupport"])

    def importDocxDialog(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                                                      config.thisTranslation["import"],
                                                      self.openFileNameLabel.text(),
                                                      "Word Documents (*.docx)",
                                                      "", options)
        if fileName:
            self.importDocx(fileName)


    def openDocxDialog(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                                                      config.thisTranslation["menu7_open"],
                                                      os.path.join(config.marvelData, "docx"),
                                                      "Word Documents (*.docx)",
                                                      "", options)
        if fileName:
            self.openDocxFile(fileName)
            self.addExternalFileHistory(fileName)
            self.setExternalFileButton()

    def importDocx(self, fileName):
        Converter().importDocx(fileName)
        self.completeImport()

    def importPdfDialog(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                                                      config.thisTranslation["import"],
                                                      self.openFileNameLabel.text(),
                                                      "PDF Files (*.pdf)",
                                                      "", options)
        if fileName:
            self.importPdf(fileName)


    def openPdfDialog(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                                                      config.thisTranslation["menu7_open"],
                                                      os.path.join(config.marvelData, "pdf"),
                                                      "PDF Files (*.pdf)",
                                                      "", options)
        if fileName:
            self.openPdfFile(fileName)

    def openPdfFileDialog(self):
        items = self.pdfList
        if items:
            item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["pdfDocument"], items,
                                            0, False)
            fileName = item
            if fileName and ok:
                command = "PDF:::{0}".format(fileName)
                self.textCommandLineEdit.setText(command)
                self.runTextCommand(command)

    def openPdfReader(self, file, page=1, fullPath=False, fullScreen=False, search=None):
        if file:
            pdfViewer = "{0}{1}".format("file:///" if platform.system() == "Windows" else "file://", os.path.join(os.getcwd(), "htmlResources", "lib/pdfjs-2.7.570-dist/web/viewer.html"))
            if platform.system() == "Windows":
                pdfViewer = pdfViewer.replace("\\", "/")
            fileName = file if fullPath else os.path.join(os.getcwd(), CatalogUtil.getFolder(file), file)
            if search is None:
                url = QUrl.fromUserInput("{0}?file={1}&theme={2}#page={3}".format(pdfViewer, fileName, config.theme, page))
            else:
                url = QUrl.fromUserInput("{0}?file={1}&theme={2}#search={3}".format(pdfViewer, fileName, config.theme, search))
            if config.openPdfViewerInNewWindow:
                self.studyView.currentWidget().openPopoverUrl(url, name=fileName, fullScreen=fullScreen)
            else:
                self.studyView.load(url)
                self.studyView.setTabText(self.studyView.currentIndex(), os.path.basename(fileName)[:20])
                self.studyView.setTabToolTip(self.studyView.currentIndex(), fileName)
            config.pdfTextPath = fileName
            self.addExternalFileHistory(fileName)
            self.setExternalFileButton()
        else:
            self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def importPdf(self, fileName):
        Converter().importPdf(fileName)
        self.completeImport()

    def openPdfFile(self, fileName):
        self.openPdfReader(fileName, fullPath=True)

    def openEpubReader(self, file, page=1, fullPath=False, fullScreen=False):
        if file:
            epubViewer = "{0}{1}".format("file:///" if platform.system() == "Windows" else "file://", os.path.join(os.getcwd(), "htmlResources", "lib/bibi-v1.2.0/bibi/index.html"))
            if platform.system() == "Windows":
                epubViewer = epubViewer.replace("\\", "/")
            marvelDataPath = os.path.join(os.getcwd(), "marvelData") if config.marvelData == "marvelData" else config.marvelData
            # fileName = file if fullPath else os.path.join(marvelDataPath, "epub", file)
            url = QUrl.fromUserInput("{0}?book={1}&theme={2}#page={3}".format(epubViewer, file, config.theme, page))
            if config.openPdfViewerInNewWindow:
                self.studyView.currentWidget().openPopoverUrl(url, name=file, fullScreen=fullScreen)
            else:
                self.studyView.load(url)
                self.studyView.setTabText(self.studyView.currentIndex(), os.path.basename(file)[:20])
                self.studyView.setTabToolTip(self.studyView.currentIndex(), file)
            config.epubTextPath = file
            self.addExternalFileHistory(file)
            self.setExternalFileButton()
        else:
            self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def invokeSavePdfPage(self):
        pdfPage = self.studyView.currentWidget().page()
        pdfPage.runJavaScript("if (typeof saveCurrentPage === 'function') { saveCurrentPage() } else { alert('No PDF is currently opened!') }")

#    def openPdfFileOLD(self, fileName):
#        if ("PyPDF2" in config.enabled):
#            if fileName:
#                text = TextFileReader().readPdfFile(fileName)
#                text = self.htmlWrapper(text, True)
#                self.openTextOnStudyView(text, tab_title=os.path.basename(fileName))
#            else:
#                self.displayMessage(config.thisTranslation["message_noSupportedFile"])
#        else:
#            self.displayMessage(config.thisTranslation["message_noSupport"])

    # Actions - export to pdf
    def printMainPage(self):
        filename = "UniqueBible.app.pdf"
        self.mainPage.printToPdf(filename)

    def printStudyPage(self):
        filename = "UniqueBible.app.pdf"
        self.studyPage.printToPdf(filename)

    # Actions - export to Word Document (*.docx)
    def exportHtmlToDocx(self, html, filename=""):
        try:
            from htmldocx import HtmlToDocx
            new_parser = HtmlToDocx()
            docx = new_parser.parse_html_string(html.replace("</div><div", "</div><br><div"))
        except:
            from docx import Document
            import html_text
            text = html_text.extract_text(html)
            docx = Document()
            docx.add_paragraph(text)
        if not filename:
            filename = "UniqueBibleApp.docx"
            openFile = True
        else:
            openFile = False
        docx.save(filename)
        if openFile:
            subprocess.Popen("{0} {1}".format(config.open, filename), shell=True)

    def exportMainPageToDocx(self):
        if ("Htmldocx" in config.enabled):
            self.mainPage.toHtml(self.exportHtmlToDocx)
        else:
            self.displayMessage(config.thisTranslation["message_noSupport"])

    def exportStudyPageToDocx(self):
        if ("Htmldocx" in config.enabled):
            self.studyPage.toHtml(self.exportHtmlToDocx)
        else:
            self.displayMessage(config.thisTranslation["message_noSupport"])

    # import BibleBentoPlus modules
    def importBBPlusLexiconInAFolder(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["menu8_plusLexicons"],
                                                     self.directoryLabel.text(), options)
        if directory:
            if Converter().importBBPlusLexiconInAFolder(directory):
                self.reloadControlPanel(False)
                self.displayMessage(config.thisTranslation["message_done"])
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def importBBPlusDictionaryInAFolder(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["menu8_plusDictionaries"],
                                                     self.directoryLabel.text(), options)
        if directory:
            if Converter().importBBPlusDictionaryInAFolder(directory):
                self.reloadControlPanel(False)
                self.displayMessage(config.thisTranslation["message_done"])
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    # import 3rd party modules
    def importSettingsDialog(self):
        self.importSettings = ImportSettings(self)
        self.importSettings.show()

    def importModules(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
              config.thisTranslation["menu8_3rdParty"],
              self.openFileNameLabel.text(),
              (
                  "MySword Bibles (*.bbl.mybible);;MySword Commentaries (*.cmt.mybible);;MySword Books (*.bok.mybible);;"
                  "MySword Dictionaries (*.dct.mybible);;e-Sword Bibles [Apple] (*.bbli);;"
                  "e-Sword Bibles [Apple] (*.bblx);;e-Sword Commentaries [Apple] (*.cmti);;"
                  "e-Sword Dictionaries [Apple] (*.dcti);;e-Sword Lexicons [Apple] (*.lexi);;e-Sword Books [Apple] (*.refi);;"
                  "e-Sword Devotionals (*.devx);;"
                  "MyBible Bibles (*.SQLite3);;MyBible Commentaries (*.commentaries.SQLite3);;MyBible Dictionaries (*.dictionary.SQLite3);;"
                  "XML [Beblia/OSIS/Zefania] (*.xml);;"
                  "theWord Complete Bibles (*.ont);;"
                  "theWord OT Bibles (*.ot);;"
                  "theWord NT Bibles (*.nt);;"
                  "theWord xref module (*.xrefs.twm);;"
                  # "theWord Commentaries (*.twm);;"
                  "Word Documents (*.docx);;"
                  "PDF Documents (*.pdf)"), "", options)
        if fileName:
            if fileName.endswith(".dct.mybible") or fileName.endswith(".dcti") or fileName.endswith(
                    ".lexi") or fileName.endswith(".dictionary.SQLite3"):
                self.importThirdPartyDictionary(fileName)
            elif fileName.endswith(".pdf"):
                self.importPdf(fileName)
            elif fileName.endswith(".docx"):
                self.importDocx(fileName)
            elif fileName.endswith(".bbl.mybible"):
                self.importMySwordBible(fileName)
            elif fileName.endswith(".cmt.mybible"):
                self.importMySwordCommentary(fileName)
            elif fileName.endswith(".bok.mybible"):
                self.importMySwordBook(fileName)
            elif fileName.endswith(".bbli"):
                self.importESwordBible(fileName)
            elif fileName.endswith(".bblx"):
                self.importESwordBible(fileName)
            elif fileName.endswith(".cmti"):
                self.importESwordCommentary(fileName)
            elif fileName.endswith(".refi"):
                self.importESwordBook(fileName)
            elif fileName.endswith(".devx"):
                self.importESwordDevotional(fileName)
            elif fileName.endswith(".commentaries.SQLite3"):
                self.importMyBibleCommentary(fileName)
            elif fileName.endswith(".SQLite3"):
                self.importMyBibleBible(fileName)
            elif fileName.endswith(".xml"):
                self.importXMLBible(fileName)
            elif fileName.endswith(".nt") or fileName.endswith(".ot") or fileName.endswith(".ont"):
                self.importTheWordBible(fileName)
            elif fileName.endswith(".xrefs.twm"):
                self.importTheWordXref(fileName)
            elif fileName.endswith(".cmt.twm"):
                self.importTheWordCommentary(fileName)
        self.reloadResources()

    def customMarvelData(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["resourceDirectory"],
                                                     self.directoryLabel.text(), options)
        if directory:
            config.marvelData = directory
            self.reloadControlPanel(False)


    def importModulesInFolder(self, directory=None):
        if directory is None:
            options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
            directory = QFileDialog.getExistingDirectory(self,
                                                         config.thisTranslation["menu8_3rdPartyInFolder"],
                                                         self.directoryLabel.text(), options)
        if directory:
            if Converter().importAllFilesInAFolder(directory):
                self.completeImport()
                self.reloadResources()
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def createBookModuleFromImages(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["menu10_bookFromImages"],
                                                     self.directoryLabel.text(), options)
        if directory:
            if Converter().createBookModuleFromImages(directory):
                self.reloadResources()
                self.displayMessage(config.thisTranslation["message_done"])
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def createBookModuleFromHTML(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["menu10_bookFromHtml"],
                                                     self.directoryLabel.text(), options)
        if directory:
            if Converter().createBookModuleFromHTML(directory):
                self.reloadResources()
                self.displayMessage(config.thisTranslation["message_done"])
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def createBookModuleFromNotes(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["menu10_bookFromNotes"],
                                                     self.directoryLabel.text(), options)
        if directory:
            if Converter().createBookModuleFromNotes(directory):
                self.reloadResources()
                self.displayMessage(config.thisTranslation["message_done"])
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def createDevotionalFromNotes(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["devotionalFromNotes"],
                                                     self.directoryLabel.text(), options)
        if directory:
            if Converter().createDevotionalFromNotes(directory):
                self.reloadResources()
                self.displayMessage(config.thisTranslation["message_done"])
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def createCommentaryFromNotes(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["commentaryFromNotes"],
                                                     self.directoryLabel.text(), options)
        if directory:
            if Converter().createCommentaryFromNotes(directory):
                self.reloadResources()
                self.displayMessage(config.thisTranslation["message_done"])
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def createLexiconFromNotes(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["lexiconFromNotes"],
                                                     self.directoryLabel.text(), options)
        if directory:
            if Converter().createLexiconFromNotes(directory):
                self.reloadResources()
                self.displayMessage(config.thisTranslation["message_done"])
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def createBookModuleFromPDF(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["menu10_bookFromPDF"],
                                                     self.directoryLabel.text(), options)
        if directory:
            if Converter().createBookModuleFromPDF(directory):
                self.reloadResources()
                self.displayMessage(config.thisTranslation["message_done"])
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def importThirdPartyDictionary(self, fileName):
        Converter().importThirdPartyDictionary(fileName)
        self.completeImport()

    def importMySwordBible(self, fileName):
        Converter().importMySwordBible(fileName)
        self.completeImport()

    def importMySwordCommentary(self, fileName):
        Converter().importMySwordCommentary(fileName)
        self.completeImport()

    def importMySwordBook(self, fileName):
        Converter().importMySwordBook(fileName)
        self.completeImport()

    def importESwordBible(self, fileName):
        Converter().importESwordBible(fileName)
        self.completeImport()

    def importESwordCommentary(self, fileName):
        Converter().importESwordCommentary(fileName)
        self.completeImport()

    def importESwordBook(self, fileName):
        Converter().importESwordBook(fileName)
        self.completeImport()

    def importESwordDevotional(self, fileName):
        Converter().importESwordDevotional(fileName)
        self.completeImport()

    def importMyBibleCommentary(self, fileName):
        Converter().importMyBibleCommentary(fileName)
        self.completeImport()

    def importMyBibleBible(self, fileName):
        Converter().importMyBibleBible(fileName)
        self.completeImport()

    def importXMLBible(self, fileName):
        Converter().importXMLBible(fileName)
        self.completeImport()

    def importTheWordBible(self, filename):
        Converter().importTheWordBible(filename)
        self.completeImport()

    def importTheWordCommentary(self, fileName):
        Converter().importTheWordCommentary(fileName)
        self.completeImport()

    def importTheWordXref(self, fileName):
        Converter().importTheWordXref(fileName)
        self.completeImport()

    def completeImport(self):
        self.reloadControlPanel(False)
        self.displayMessage(config.thisTranslation["message_done"])

    # Actions - tag files with BibleVerseParser
    def onTaggingCompleted(self):
        self.displayMessage("{0}  {1} 'tagged_'".format(config.thisTranslation["message_done"],
                                                        config.thisTranslation["message_tagged"]))

    def tagFile(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                                                      config.thisTranslation["menu8_tagFile"],
                                                      self.openFileNameLabel.text(),
                                                      "All Files (*);;Text Files (*.txt);;CSV Files (*.csv);;TSV Files (*.tsv)",
                                                      "", options)
        if fileName:
            BibleVerseParser(config.parserStandarisation).extractAllReferencesStartParsing(fileName)
            self.onTaggingCompleted()

    def tagFiles(self):
        options = QFileDialog.Options()
        files, filtr = QFileDialog.getOpenFileNames(self,
                                                    config.thisTranslation["menu8_tagFiles"], self.openFilesPath,
                                                    "All Files (*);;Text Files (*.txt);;CSV Files (*.csv);;TSV Files (*.tsv)",
                                                    "", options)
        if files:
            parser = BibleVerseParser(config.parserStandarisation)
            for filename in files:
                parser.extractAllReferencesStartParsing(filename)
            del parser
            self.onTaggingCompleted()

    def tagFolder(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                                                     config.thisTranslation["menu8_tagFolder"],
                                                     self.directoryLabel.text(), options)
        if directory:
            path, filename = os.path.split(directory)
            outputFile = os.path.join(path, "output_{0}".format(filename))
            BibleVerseParser(config.parserStandarisation).extractAllReferencesStartParsing(directory)
            self.onTaggingCompleted()

    # Action - open a dialog box to download a mp3 file from youtube
    def downloadMp3Dialog(self):
        text, ok = QInputDialog.getText(self, "YouTube -> mp3", config.thisTranslation["youtube_address"],
                                        QLineEdit.Normal, "")
        if ok and text and QUrl.fromUserInput(text).isValid():
            self.runTextCommand("mp3:::{0}".format(text))

    # Action - open a dialog box to download a youtube video in mp4 format
    def downloadMp4Dialog(self):
        text, ok = QInputDialog.getText(self, "YouTube -> mp4", config.thisTranslation["youtube_address"],
                                        QLineEdit.Normal, "")
        if ok and text and QUrl.fromUserInput(text).isValid():
            self.runTextCommand("mp4:::{0}".format(text))

    def openMiniBrowser(self, initialUrl=None):
        selectedText = config.mainWindow.selectedText()
        if selectedText:
            content = TextUtil.plainTextToUrl(selectedText)
            initialUrl = f"https://youtube.com/results?search_query={content}"
        else:
            initialUrl = "https://youtube.com"
        self.youTubeView = MiniBrowser(self, initialUrl)
        self.youTubeView.show()

    # Action - open "images" directory
    def openDir(self, dir):
        if (config.runMode == "docker"):
            WebtopUtil.openDir(dir)
        else:
            self.runTextCommand("cmd:::{0} {1}".format(config.openLinuxDirectory if platform.system() == "Linux" else config.open, dir))

    def openImagesFolder(self):
        imageFolder = os.path.join("htmlResources", "images")
        self.openDir(imageFolder)

    # Action - open "music" directory
    def openMusicFolder(self):
        self.openDir(config.musicFolder)

    # Action - open "audio" directory
    def openAudioFolder(self):
        self.openDir(config.audioFolder)

    # Action - open "video" directory
    def openVideoFolder(self):
        self.openDir(config.videoFolder)

    # Action - open "marvelData" directory
    def openMarvelDataFolder(self):
        self.openDir(config.marvelData)

    # Actions - hide / show tool bars
    def hideShowMainToolBar(self):
        if self.firstToolBar.isVisible():
            self.firstToolBar.hide()
        else:
            self.firstToolBar.show()

    def showMainToolBar(self):
        self.firstToolBar.show()

    def hideMainToolBar(self):
        self.firstToolBar.hide()

    def hideShowSecondaryToolBar(self):
        if self.secondToolBar.isVisible():
            if not config.noStudyBibleToolbar:
                self.studyBibleToolBar.hide()
            self.secondToolBar.hide()
        else:
            if not config.noStudyBibleToolbar:
                self.setStudyBibleToolBar()
            self.secondToolBar.show()

    def showSecondaryToolBar(self):
        self.secondToolBar.show()

    def hideSecondaryToolBar(self):
        self.secondToolBar.hide()

    def hideShowLeftToolBar(self):
        if self.leftToolBar.isVisible():
            self.leftToolBar.hide()
        else:
            self.leftToolBar.show()

    def hideLeftToolBar(self):
        self.leftToolBar.hide()

    def showLeftToolBar(self):
        self.leftToolBar.show()

    def hideShowRightToolBar(self):
        if self.rightToolBar.isVisible():
            self.rightToolBar.hide()
        else:
            self.rightToolBar.show()

    def hideRightToolBar(self):
        self.rightToolBar.hide()

    def showRightToolBar(self):
        self.rightToolBar.show()

    def hideShowSideToolBars(self):
        if self.leftToolBar.isVisible():
            self.leftToolBar.hide()
            self.rightToolBar.hide()
        else:
            self.leftToolBar.show()
            self.rightToolBar.show()

    def hideShowAdditionalToolBar(self):
        if config.topToolBarOnly:
            config.topToolBarOnly = False
        else:
            config.topToolBarOnly = True
        self.setAdditionalToolBar()

    def setAdditionalToolBar(self):
        self.firstToolBar.show()
        config.noToolBar = False
        if config.topToolBarOnly:
            if not config.noStudyBibleToolbar:
                self.studyBibleToolBar.hide()
            self.secondToolBar.hide()
            self.leftToolBar.hide()
            self.rightToolBar.hide()
        else:
            if not config.noStudyBibleToolbar:
                self.setStudyBibleToolBar()
            self.secondToolBar.show()
            self.leftToolBar.show()
            self.rightToolBar.show()

    def setNoToolBar(self):
        if config.noToolBar:
            config.noToolBar = False
            self.showAllToolBar()
        else:
            config.noToolBar = True
            self.hideAllToolBar()

    def showAllToolBar(self):
        config.topToolBarOnly = False
        self.firstToolBar.show()
        if not config.noStudyBibleToolbar:
            self.setStudyBibleToolBar()
        self.secondToolBar.show()
        self.leftToolBar.show()
        self.rightToolBar.show()

    def hideAllToolBar(self):
        config.topToolBarOnly = False
        self.firstToolBar.hide()
        if not config.noStudyBibleToolbar:
            self.studyBibleToolBar.hide()
        self.secondToolBar.hide()
        self.leftToolBar.hide()
        self.rightToolBar.hide()

    # Actions - book features
    def installBooks(self):
        if self.textCommandParser.isDatabaseInstalled("book"):
            self.displayMessage(config.thisTranslation["message_installed"])
        else:
            self.textCommandParser.databaseNotInstalled("book")

    def openBookMenu(self):
        if self.textCommandParser.isDatabaseInstalled("book"):
            if config.refButtonClickAction == "master":
                self.openControlPanelTab(1)
            elif config.refButtonClickAction == "mini":
                self.openControlPanelTab(1)
            elif config.refButtonClickAction == "direct":
                self.openBook()
            else:
                self.openControlPanelTab(1)
        else:
            self.textCommandParser.databaseNotInstalled("book")

    def openBook(self):
        if hasattr(config, "bookChapNum"):
            self.runTextCommand("BOOK:::{0}:::{1}".format(config.book, config.bookChapNum), True, "main")
        else:
            self.runTextCommand("BOOK:::{0}".format(config.book), True, "main")

    def openBookPreviousChapter(self):
        if hasattr(config, "bookChapNum"):
            config.bookChapNum -= 1
            if config.bookChapNum < 1:
                config.bookChapNum = 1
            self.newTabException = True
            self.runTextCommand("BOOK:::{0}:::{1}".format(config.book, config.bookChapNum), True, "main")

    def openBookNextChapter(self):
        if hasattr(config, "bookChapNum"):
            book = Book(config.book)
            if config.bookChapNum < book.getChapterCount():
                config.bookChapNum += 1
            self.newTabException = True
            self.runTextCommand("BOOK:::{0}:::{1}".format(config.book, config.bookChapNum), True, "main")

    def displaySearchBookCommand(self):
        config.bookSearchString = ""
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHBOOK:::{0}:::".format(config.book))

    def searchBookCommand(self):
        text, ok = QInputDialog.getText(self, "QInputDialog.getText()",
                "{0} - {1}".format(config.thisTranslation["menu5_search"], config.book), QLineEdit.Normal,
                "")
        if ok and text:
            self.runTextCommand("SEARCHBOOK:::{0}:::{1}".format(config.book, text))

    def displaySearchAllBookCommand(self):
        config.bookSearchString = ""
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHBOOK:::ALL:::")

    def clearBookHighlights(self):
        config.bookSearchString = ""
        self.reloadCurrentRecord(True)

    def clearNoteHighlights(self):
        config.noteSearchString = ""
        self.reloadCurrentRecord(True)

    def displaySearchFavBookCommand(self):
        config.bookSearchString = ""
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHBOOK:::FAV:::")

    def getBookName(self, book):
        return book.replace("_", " ")

    def openFavouriteBook0(self):
        self.runTextCommand("BOOK:::{0}".format(config.favouriteBooks[0]), True, "main")

    def openFavouriteBook1(self):
        self.runTextCommand("BOOK:::{0}".format(config.favouriteBooks[1]), True, "main")

    def openFavouriteBook2(self):
        self.runTextCommand("BOOK:::{0}".format(config.favouriteBooks[2]), True, "main")

    def openFavouriteBook3(self):
        self.runTextCommand("BOOK:::{0}".format(config.favouriteBooks[3]), True, "main")

    def openFavouriteBook4(self):
        self.runTextCommand("BOOK:::{0}".format(config.favouriteBooks[4]), True, "main")

    def openFavouriteBook5(self):
        self.runTextCommand("BOOK:::{0}".format(config.favouriteBooks[5]), True, "main")

    def openFavouriteBook6(self):
        self.runTextCommand("BOOK:::{0}".format(config.favouriteBooks[6]), True, "main")

    def openFavouriteBook7(self):
        self.runTextCommand("BOOK:::{0}".format(config.favouriteBooks[7]), True, "main")

    def openFavouriteBook8(self):
        self.runTextCommand("BOOK:::{0}".format(config.favouriteBooks[8]), True, "main")

    def openFavouriteBook9(self):
        self.runTextCommand("BOOK:::{0}".format(config.favouriteBooks[9]), True, "main")

    def openBookDialog(self):
        if self.textCommandParser.isDatabaseInstalled("book"):
            self.openControlPanelTab(1)
        else:
            self.textCommandParser.databaseNotInstalled("book")

    #        bookData = BookData()
    #        items = [book for book, *_ in bookData.getBookList()]
    #        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["menu10_dialog"], items, items.index(config.book), False)
    #        if ok and item:
    #            self.runTextCommand("BOOK:::{0}".format(item), True, "main")

    def setMaximumOHGBiVersesDisplayDialog(self):
        integer, ok = QInputDialog.getInt(self,
                                          "UniqueBible", config.thisTranslation["selectMaximumOHGBiVerses"], config.maximumOHGBiVersesDisplayedInSearchResult, 1,
                                          10000, 50)
        if ok:
            config.maximumOHGBiVersesDisplayedInSearchResult = integer

    def changeActiveVerseColour(self):
        color = QColorDialog.getColor(QColor(config.darkThemeActiveVerseColor if config.theme in ("dark", "night") else config.lightThemeActiveVerseColor), self)
        if color.isValid():
            colorName = color.name()
            if config.theme in ("dark", "night"):
                config.darkThemeActiveVerseColor = colorName
            else:
                config.lightThemeActiveVerseColor = colorName
            self.reloadCurrentRecord(True)

    def changeButtonColour(self):
        dialog = MaterialColorDialog(self)
        dialog.exec_()

    def setTabNumberDialog(self):
        integer, ok = QInputDialog.getInt(self,
                                          "UniqueBible", config.thisTranslation["menu1_tabNo"], config.numberOfTab, 1,
                                          20, 1)
        if ok:
            config.numberOfTab = integer
            self.handleRestart()

    def setIconButtonSize(self, size=None):
        if size is None:
            integer, ok = QInputDialog.getInt(self,
                                            "UniqueBible", config.thisTranslation["customiseIconSize"], config.iconButtonSize, 12,
                                            48, 3)
            if ok:
                config.iconButtonSize = integer
                self.resetUI()
        else:
            config.iconButtonSize = size
            self.resetUI()

    def setNoOfLinesPerChunkForParsingDialog(self):
        integer, ok = QInputDialog.getInt(self,
                                          "UniqueBible", config.thisTranslation["noOfLinesPerChunkForParsing"], config.noOfLinesPerChunkForParsing, 1,
                                          2000, 10)
        if ok:
            config.noOfLinesPerChunkForParsing = integer

    def setMaximumHistoryRecordDialog(self):
        integer, ok = QInputDialog.getInt(self,
                                          "UniqueBible", config.thisTranslation["setMaximumHistoryRecord"], config.maximumHistoryRecord, 5,
                                          100, 1)
        if ok:
            config.maximumHistoryRecord = integer

    def moreConfigOptionsDialog(self):
        self.configFlagsDialog = ConfigFlagsWindow(self)
        self.configFlagsDialog.show()

    def showBibleCollectionDialog(self):
        self.bibleCollectionDialog = BibleCollectionDialog(self)
        self.bibleCollectionDialog.show()

    def showLiveFilterDialog(self):
        self.liveFilterDialog = LiveFilterDialog(self)
        self.liveFilterDialog.reloadFilters()
        #screen = QGuiApplication.instance().desktop().availableGeometry()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = screen.width() * float(1/8)
        y = screen.height() * float(1/5)
        self.liveFilterDialog.move(int(x), int(y))
        self.liveFilterDialog.show()

    def showLibraryCatalogDialog(self):
        self.libraryCatalogDialog = LibraryCatalogDialog(self)
        #screen = QGuiApplication.instance().desktop().availableGeometry()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = screen.width() * float(1/8)
        y = screen.height() * float(1/5)
        self.libraryCatalogDialog.move(int(x), int(y))
        self.libraryCatalogDialog.show()

    def enableIndividualPluginsWindow(self):
        self.individualPluginsWindow = EnableIndividualPlugins(self)
        self.individualPluginsWindow.show()

    def addFavouriteBookDialog(self):
        bookData = BookData()
        items = [book for book, *_ in bookData.getBookList()]
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["menu10_addFavourite"], items,
                                        0, False)
        if ok and item:
            if item not in config.favouriteBooks:
                config.favouriteBooks.insert(0, item)
                if len(config.favouriteBooks) > 10:
                    config.favouriteBooks = [book for counter, book in enumerate(config.favouriteBooks) if counter < 10]
                self.displayMessage(
                    "{0}".format(config.thisTranslation["message_done"]))

    def toggleDisplayBookContent(self):
        if config.openBookInNewWindow:
            config.openBookInNewWindow = False
            self.displayMessage(config.thisTranslation["menu10_bookOnStudy"])
        else:
            config.openBookInNewWindow = True
            self.displayMessage(config.thisTranslation["menu10_bookOnNew"])

    def searchBookDialog(self):
        bookData = BookData()
        items = [book for book, *_ in bookData.getBookList()]
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["menu10_dialog"], items,
                                        items.index(config.book), False)
        if ok and item:
            self.focusCommandLineField()
            self.textCommandLineEdit.setText("SEARCHBOOK:::{0}:::".format(item))

    def isThridPartyDictionary(self, module):
        return self.crossPlatform.isThridPartyDictionary(module)

    def search3rdDictionaryDialog(self):
        items = ThirdPartyDictionary(self.crossPlatform.isThridPartyDictionary(config.thirdDictionary)).moduleList
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["menu5_3rdDict"], items,
                                        items.index(config.thirdDictionary), False)
        if ok and item:
            self.focusCommandLineField()
            self.textCommandLineEdit.setText("SEARCHTHIRDDICTIONARY:::{0}:::".format(item))

    def searchDictionaryDialog(self):
        indexes = IndexesSqlite()
        dictionaryDict = {abb: name for abb, name in indexes.dictionaryList}
        lastDictionary = dictionaryDict[config.dictionary]
        dictionaryDict = {name: abb for abb, name in indexes.dictionaryList}
        items = list(dictionaryDict.keys())
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["context1_dict"], items,
                                        items.index(lastDictionary), False)
        if ok and item:
            self.focusCommandLineField()
            self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(dictionaryDict[item]))

    def searchEncyclopediaDialog(self):
        indexes = IndexesSqlite()
        dictionaryDict = {abb: name for abb, name in indexes.encyclopediaList}
        lastDictionary = dictionaryDict[config.encyclopedia]
        dictionaryDict = {name: abb for abb, name in indexes.encyclopediaList}
        items = list(dictionaryDict.keys())
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["context1_encyclopedia"], items,
                                        items.index(lastDictionary), False)
        if ok and item:
            self.focusCommandLineField()
            self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(dictionaryDict[item]))

    def searchTopicDialog(self):
        indexes = IndexesSqlite()
        dictionaryDict = {abb: name for abb, name in indexes.topicList}
        lastDictionary = dictionaryDict[config.topic]
        dictionaryDict = {name: abb for abb, name in indexes.topicList}
        items = list(dictionaryDict.keys())
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["menu5_topics"], items,
                                        items.index(lastDictionary), False)
        if ok and item:
            self.focusCommandLineField()
            self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(dictionaryDict[item]))

    # Action - bible search commands
    def displaySearchBibleCommand(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("COUNT:::{0}:::".format(config.mainText))

    def displaySearchStudyBibleCommand(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("COUNT:::{0}:::".format(config.studyText))

    def displaySearchBibleMenu(self):
        self.openControlPanelTab(3)

    def displaySearchHighlightCommand(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHHIGHLIGHT:::")

    # Action - other search commands
    def searchCommandChapterNote(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHCHAPTERNOTE:::")

    def searchCommandVerseNote(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHVERSENOTE:::")

    def searchCommandBookNote(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHBOOKNOTE:::")

    def searchCommandBibleDictionary(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(config.dictionary))

    def searchCommandBibleEncyclopedia(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(config.encyclopedia))

    def searchCommandBibleCharacter(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHTOOL:::EXLBP:::")

    def searchCommandBibleName(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHTOOL:::HBN:::")

    def searchCommandBibleLocation(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHTOOL:::EXLBL:::")

    def searchCommandBibleTopic(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(config.topic))

    def searchCommandAllBibleTopic(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHTOOL:::EXLBT:::")

    def searchCommandLexicon(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("LEXICON:::")

    def searchCommandThirdPartyDictionary(self):
        self.focusCommandLineField()
        self.textCommandLineEdit.setText("SEARCHTHIRDDICTIONARY:::")

    # Actions - open urls
    def openWebsite(self, url):
        command = "ONLINE:::{0}".format(url)
        self.textCommandLineEdit.setText(command)
        self.runTextCommand(command)

    def setupYouTube(self):
        self.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/Download-Youtube-audio-video")

    def setupGist(self):
        self.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/Gist-synching")

    def setupWatsonTranslator(self):
        self.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/IBM-Watson-Language-Translator")

    def openUbaWiki(self):
        self.openWebsite("https://github.com/eliranwong/UniqueBible/wiki")

    def openUbaDiscussions(self):
        self.openWebsite("https://github.com/eliranwong/UniqueBible/discussions")

    def openBibleTools(self):
        self.openWebsite("https://bibletools.app")

    def openUniqueBible(self):
        self.openWebsite("https://uniquebible.app")

    def openMarvelBible(self):
        self.openWebsite("https://marvel.bible")

    def openBibleBento(self):
        self.openWebsite("https://biblebento.com")

    def openOpenGNT(self):
        self.openWebsite("https://opengnt.com")

    def openSource(self):
        self.openWebsite("https://github.com/eliranwong/")

    def openUniqueBibleSource(self):
        self.openWebsite("https://github.com/eliranwong/UniqueBible")

    def openHebrewBibleSource(self):
        self.openWebsite("https://github.com/eliranwong/OpenHebrewBible")

    def openOpenGNTSource(self):
        self.openWebsite("https://github.com/eliranwong/OpenGNT")

    def openCredits(self):
        self.openWebsite("https://marvel.bible/resource.php")

    def contactEliranWong(self):
        self.openWebsite("https://marvel.bible/contact/contactform.php")

    def reportAnIssue(self):
        self.openWebsite("https://github.com/eliranwong/UniqueBible/issues")

    def goToSlack(self):
        self.openWebsite("https://marvelbible.slack.com")

    def donateToUs(self):
        self.openWebsite("https://www.paypal.me/MarvelBible")

    def moreBooks(self):
        self.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/Download-3rd-party-modules")

    def openBrowser(self, url):
        self.openWebsite(url)

    # Actions - resize the main window
    def fullsizeWindow(self):
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

    def maximizedWindow(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
            #self.resizeWindow(1, 1)
            #self.moveWindow(0, 0)

    def twoThirdWindow(self):
        self.resizeWindow(2 / 3, 2 / 3)
        self.moveWindow(1 / 6, 1 / 6)

    def topHalfScreenHeight(self):
        self.resizeWindow(1, 1 / 2)
        self.moveWindow(0, 0)

    def bottomHalfScreenHeight(self):
        self.resizeWindow(1, 1 / 2)
        self.moveWindow(0, 1 / 2)

    def leftHalfScreenWidth(self):
        self.resizeWindow(1 / 2, 1)
        self.moveWindow(0, 0)

    def rightHalfScreenWidth(self):
        self.resizeWindow(1 / 2, 1)
        self.moveWindow(1 / 2, 0)

    def resizeWindow(self, widthFactor, heightFactor):
        if platform.system() == "Linux":
            self.showNormal()
        #availableGeometry = QGuiApplication.instance().desktop().availableGeometry()
        availableGeometry = QGuiApplication.primaryScreen().availableGeometry()
        self.resize(int(availableGeometry.width() * widthFactor), int(availableGeometry.height() * heightFactor))

    def moveWindow(self, horizontal, vertical):
        # Note: move feature does not work on Chrome OS
        #screen = QGuiApplication.instance().desktop().availableGeometry()
        screen = QGuiApplication.primaryScreen().availableGeometry()
        x = screen.width() * float(horizontal)
        y = screen.height() * float(vertical)
        self.move(int(x), int(y))

    # Actions - enable or disable enforcement of comparison / parallel
    def getEnableCompareParallelDisplay(self):
        if config.enforceCompareParallel:
            return self.getCrossplatformPath("material/action/done_all/materialiconsoutlined/48dp/2x/outline_done_all_black_48dp.png") if config.menuLayout == "material" else "sync.png"
        else:
            return self.getCrossplatformPath("material/action/remove_done/materialiconsoutlined/48dp/2x/outline_remove_done_black_48dp.png") if config.menuLayout == "material" else "noSync.png"

    def getEnableCompareParallelDisplayToolTip(self):
        return "{0}: {1}".format(config.thisTranslation["parallelMode"], config.thisTranslation["on"] if config.enforceCompareParallel else config.thisTranslation["off"])

    def enforceCompareParallelButtonClicked(self):
        config.enforceCompareParallel = not config.enforceCompareParallel
        icon = self.getQIcon(self.getEnableCompareParallelDisplay())
        if config.menuLayout == "material":
            self.enforceCompareParallelButton.setStyleSheet(icon)
        else:
            self.enforceCompareParallelButton.setIcon(icon)
        self.enforceCompareParallelButton.setToolTip(self.getEnableCompareParallelDisplayToolTip())
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    # Actions - enable or disable sync main and secondary bibles
    def getSyncStudyWindowBibleDisplay(self):
        if config.syncStudyWindowBibleWithMainWindow:
            return self.getCrossplatformPath("material/notification/sync/materialiconsoutlined/48dp/2x/outline_sync_black_48dp.png") if config.menuLayout == "material" else "sync.png"
        else:
            return self.getCrossplatformPath("material/notification/sync_disabled/materialiconsoutlined/48dp/2x/outline_sync_disabled_black_48dp.png") if config.menuLayout == "material" else "noSync.png"

    def getSyncStudyWindowBibleDisplayToolTip(self):
        return "{0}: {1}".format(config.thisTranslation["studyBibleSyncsWithMainBible"], config.thisTranslation["on"] if config.syncStudyWindowBibleWithMainWindow else config.thisTranslation["off"])

    def enableSyncStudyWindowBibleButtonClicked(self):
        config.syncStudyWindowBibleWithMainWindow = not config.syncStudyWindowBibleWithMainWindow
        enableSyncStudyWindowBibleButtonFile = os.path.join("htmlResources", self.getSyncStudyWindowBibleDisplay())
        qIcon = self.getMaskedQIcon(enableSyncStudyWindowBibleButtonFile, config.maskMaterialIconColor, config.maskMaterialIconBackground, toolButton=True) if config.menuLayout == "material" else QIcon(enableSyncStudyWindowBibleButtonFile)
        self.enableSyncStudyWindowBibleButton.setIcon(qIcon)
        self.enableSyncStudyWindowBibleButton.setToolTip(self.getSyncStudyWindowBibleDisplayToolTip())
        if config.syncCommentaryWithMainWindow and not self.syncButtonChanging:
            self.syncButtonChanging = True
            self.enableSyncCommentaryButtonClicked()
        if config.syncStudyWindowBibleWithMainWindow:
            self.reloadCurrentRecord()
        self.syncButtonChanging = False
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    def getSyncCommentaryDisplay(self):
        if config.syncCommentaryWithMainWindow:
            return self.getCrossplatformPath("material/notification/sync/materialiconsoutlined/48dp/2x/outline_sync_black_48dp.png") if config.menuLayout == "material" else "sync.png"
        else:
            return self.getCrossplatformPath("material/notification/sync_disabled/materialiconsoutlined/48dp/2x/outline_sync_disabled_black_48dp.png") if config.menuLayout == "material" else "noSync.png"

    def getSyncCommentaryDisplayToolTip(self):
        return "{0}: {1}".format(config.thisTranslation["commentarySyncsWithMainBible"], config.thisTranslation["on"] if config.syncCommentaryWithMainWindow else config.thisTranslation["off"])

    def enableSyncCommentaryButtonClicked(self):
        config.syncCommentaryWithMainWindow = not config.syncCommentaryWithMainWindow
        icon = self.getQIcon(self.getSyncCommentaryDisplay())
        if config.menuLayout == "material":
            self.enableSyncCommentaryButton.setStyleSheet(icon)
        else:
            self.enableSyncCommentaryButton.setIcon(icon)
        self.enableSyncCommentaryButton.setToolTip(self.getSyncCommentaryDisplayToolTip())
        if config.syncStudyWindowBibleWithMainWindow and not self.syncButtonChanging:
            self.syncButtonChanging = True
            self.enableSyncStudyWindowBibleButtonClicked()
        if config.syncCommentaryWithMainWindow:
            self.reloadCurrentRecord()
        self.syncButtonChanging = False
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    def getOrientationDisplay(self):
        if config.landscapeMode:
            return self.getCrossplatformPath("material/communication/stay_current_landscape/materialiconsoutlined/48dp/2x/outline_stay_current_landscape_black_48dp.png")
        else:
            return self.getCrossplatformPath("material/communication/stay_current_portrait/materialiconsoutlined/48dp/2x/outline_stay_current_portrait_black_48dp.png")

    def getOrientationDisplayToolTip(self):
        return config.thisTranslation["landscape"] if config.landscapeMode else config.thisTranslation["portrait"]

    def orientationButtonClicked(self):
        self.switchLandscapeMode()
        icon = self.getQIcon(self.getOrientationDisplay())
        self.switchOrientationButton.setStyleSheet(icon)
        self.switchOrientationButton.setToolTip(self.getOrientationDisplayToolTip())
        self.setupMenuLayout("material")

    # Actions - enable or disable study bible / bible displayed on study view
    def getStudyBibleDisplay(self):
        if config.openBibleInMainViewOnly:
            #return self.getCrossplatformPath("material/content/add_circle_outline/materialiconsoutlined/48dp/2x/outline_add_circle_outline_black_48dp.png") if config.menuLayout == "material" else "addStudyViewBible.png"
            return self.getCrossplatformPath("material/toggle/toggle_on/materialiconsoutlined/48dp/2x/outline_toggle_on_black_48dp.png") if config.menuLayout == "material" else "addStudyViewBible.png"
        else:
            #return self.getCrossplatformPath("material/content/remove_circle_outline/materialiconsoutlined/48dp/2x/outline_remove_circle_outline_black_48dp.png") if config.menuLayout == "material" else "deleteStudyViewBible.png"
            return self.getCrossplatformPath("material/toggle/toggle_off/materialiconsoutlined/48dp/2x/outline_toggle_off_black_48dp.png") if config.menuLayout == "material" else "deleteStudyViewBible.png"

    def getStudyBibleDisplayToolTip(self):
        return "{0}: {1}".format(config.thisTranslation["enableStudyWindowBible"], config.thisTranslation["on"] if not config.openBibleInMainViewOnly else config.thisTranslation["off"])

    def enableStudyBibleButtonClicked(self):
        if config.openBibleInMainViewOnly:
            config.openBibleInMainViewOnly = False
            config.studyText = config.studyTextTemp
            if config.noStudyBibleToolbar:
                if config.menuLayout == "material":
                    self.studyBibleSelection.setEnabled(True)
                    self.studyB.setEnabled(True)
                    self.studyC.setEnabled(True)
                    self.studyRefLabel.setEnabled(True)
                    self.studyV.setEnabled(True)
                else:
                    self.studyRefButton.setVisible(True)
                #self.enableSyncStudyWindowBibleButton.setVisible(True)
                self.swapBibleButton.setVisible(True)
            else:
                self.studyBibleToolBar.show()
        else:
            config.openBibleInMainViewOnly = True
            config.studyTextTemp = config.studyText
            config.studyText = config.mainText
            if config.noStudyBibleToolbar:
                if config.menuLayout == "material":
                    self.studyBibleSelection.setDisabled(True)
                    self.studyB.setDisabled(True)
                    self.studyC.setDisabled(True)
                    self.studyRefLabel.setDisabled(True)
                    self.studyV.setDisabled(True)
                else:
                    self.studyRefButton.setVisible(False)
                #self.enableSyncStudyWindowBibleButton.setVisible(False)
                self.swapBibleButton.setVisible(False)
            else:
                self.studyBibleToolBar.hide()
        icon = self.getQIcon(self.getStudyBibleDisplay())
        if config.menuLayout == "material":
            self.enableStudyBibleButton.setStyleSheet(icon)
        else:
            self.enableStudyBibleButton.setIcon(icon)
        self.enableStudyBibleButton.setToolTip(self.getStudyBibleDisplayToolTip())
        # Reload Study Window content to update active text setting only when Study Window content is not a bible chapter view
        view = "study"
        textCommand = config.history[view][config.currentRecord[view]]
        if not re.search('^(study:::|studytext:::|bible:::)', textCommand.lower()):
            self.runTextCommand(textCommand, False, view, True)

    def updateBookButton(self):
        if not config.menuLayout == "material":
            self.bookButton.setText(config.book[:20])
            self.bookButton.setToolTip(config.book)

    # Actions - enable or disable lightning feature
    def getInstantInformation(self):
        if config.instantInformationEnabled:
            return self.getCrossplatformPath("material/image/flash_auto/materialiconsoutlined/48dp/2x/outline_flash_auto_black_48dp.png") if config.menuLayout == "material" else "show.png"
        else:
            return self.getCrossplatformPath("material/image/flash_off/materialiconsoutlined/48dp/2x/outline_flash_off_black_48dp.png") if config.menuLayout == "material" else "hide.png"

    def getInstantLookupDisplayToolTip(self):
        return "{0}: {1}".format(config.thisTranslation["menu2_hover"], config.thisTranslation["on"] if config.instantInformationEnabled else config.thisTranslation["off"])

    def enableInstantButtonClicked(self):
        config.instantInformationEnabled = not config.instantInformationEnabled
        if hasattr(self, 'enableInstantButton'):
            icon = self.getQIcon(self.getInstantInformation())
            if config.menuLayout == "material":
                self.enableInstantButton.setStyleSheet(icon)
            else:
                self.enableInstantButton.setIcon(icon)
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    # Actions - enable or disable paragraphs feature
    def displayBiblesInParagraphs(self):
        config.readFormattedBibles = not config.readFormattedBibles
        self.newTabException = True
        self.reloadCurrentRecord(True)

    def enableBiblesInParagraphs(self):
        config.readFormattedBibles = True
        self.newTabException = True
        self.reloadCurrentRecord(True)

    def disableBiblesInParagraphs(self):
        config.readFormattedBibles = False
        self.newTabException = True
        self.reloadCurrentRecord(True)

    def getCrossplatformPath(self, filePath):
        return os.path.join(*filePath.split("/"))

    def getReadFormattedBiblesToolTip(self):
        return "{0}: {1}".format(config.thisTranslation["formattedText"], config.thisTranslation["on"] if config.readFormattedBibles else config.thisTranslation["off"])

    def getReadFormattedBibles(self):
        if config.readFormattedBibles:
            return self.getCrossplatformPath("material/maps/local_parking/materialiconsoutlined/48dp/2x/outline_local_parking_black_48dp.png") if config.menuLayout == "material" else "numbered_list.png"
        else:
            return self.getCrossplatformPath("material/editor/format_list_numbered/materialiconsoutlined/48dp/2x/outline_format_list_numbered_black_48dp.png") if config.menuLayout == "material" else "paragraph.png"

    def enableParagraphButtonClicked(self):
        self.enableParagraphButtonAction(True)

    def enableParagraphButtonAction(self, display):
        if display:
            self.displayBiblesInParagraphs()
        icon = self.getQIcon(self.getReadFormattedBibles())
        if config.menuLayout == "material":
            self.enableParagraphButton.setStyleSheet(icon)
        else:
            self.enableParagraphButton.setIcon(icon)
        self.enableParagraphButton.setToolTip(self.getReadFormattedBiblesToolTip())
        if config.menuLayout == "material":
            self.setupMenuLayout("material")
            #if config.readFormattedBibles:
            #    self.enableSubheadingButton.setVisible(False)
            #else:
            #    self.enableSubheadingButton.setVisible(True)

    def toggleShowUserNoteIndicator(self):
        config.showUserNoteIndicator = not config.showUserNoteIndicator
        self.newTabException = True
        self.reloadCurrentRecord(True)
        if config.menuLayout == "material":
            self.setupMenuLayout("material")


    def toggleShowBibleNoteIndicator(self):
        config.showBibleNoteIndicator = not config.showBibleNoteIndicator
        self.newTabException = True
        self.reloadCurrentRecord(True)
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    def toggleChapterMenuTogetherWithBibleChapter(self):
        config.displayChapterMenuTogetherWithBibleChapter = not config.displayChapterMenuTogetherWithBibleChapter
        self.newTabException = True
        self.reloadCurrentRecord(True)
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    def toggleDisplayVerseAudioBibleIcon(self):
        config.displayVerseAudioBibleIcon = not config.displayVerseAudioBibleIcon
        self.newTabException = True
        self.reloadCurrentRecord(True)
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    def toggleShowVerseReference(self):
        config.showVerseReference = not config.showVerseReference
        self.newTabException = True
        self.reloadCurrentRecord(True)
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    def toggleShowHebrewGreekWordAudioLinks(self):
        config.showHebrewGreekWordAudioLinks = not config.showHebrewGreekWordAudioLinks
        self.newTabException = True
        self.reloadCurrentRecord(True)
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    def toggleShowHebrewGreekWordAudioLinksInMIB(self):
        config.showHebrewGreekWordAudioLinksInMIB = not config.showHebrewGreekWordAudioLinksInMIB
        self.newTabException = True
        self.reloadCurrentRecord(True)

    def toggleFavouriteVersionIntoMultiRef(self):
        config.addFavouriteToMultiRef = not config.addFavouriteToMultiRef
        self.newTabException = True
        self.reloadCurrentRecord(True)
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    def toggleHideLexicalEntryInBible(self):
        config.hideLexicalEntryInBible = not config.hideLexicalEntryInBible
        self.newTabException = True
        self.reloadCurrentRecord(True)
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    def toggleReadTillChapterEnd(self):
        config.readTillChapterEnd = not config.readTillChapterEnd
        self.newTabException = True
        self.reloadCurrentRecord(True)
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    # Actions - enable or disable sub-heading for plain bibles
    def getAddSubheading(self):
        if config.addTitleToPlainChapter:
            return self.getCrossplatformPath("material/av/subtitles/materialiconsoutlined/48dp/2x/outline_subtitles_black_48dp.png") if config.menuLayout == "material" else "subheadingEnable.png"
        else:
            return self.getCrossplatformPath("material/action/subtitles_off/materialiconsoutlined/48dp/2x/outline_subtitles_off_black_48dp.png") if config.menuLayout == "material" else "subheadingDisable.png"

    def enableSubheadingButtonClicked(self):
        config.addTitleToPlainChapter = not config.addTitleToPlainChapter
        self.newTabException = True
        self.reloadCurrentRecord(True)
        icon = self.getQIcon(self.getAddSubheading())
        if config.menuLayout == "material":
            self.enableSubheadingButton.setStyleSheet(icon)
        else:
            self.enableSubheadingButton.setIcon(icon)

    def enableSubheadingButtonClicked2(self):
        config.addTitleToPlainChapter = not config.addTitleToPlainChapter
        icon = os.path.join("htmlResources", self.getAddSubheading())
        qIcon = self.getMaskedQIcon(icon, config.maskMaterialIconColor, config.maskMaterialIconBackground, toolButton=True)
        self.enableSubheadingButton.setIcon(qIcon)
        self.enableSubheadingButton.setToolTip(self.enableSubheadingToolTip())
        self.newTabException = True
        self.reloadCurrentRecord(True)
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    def enableSubheadingToolTip(self):
        return "{0}: {1}".format(config.thisTranslation["menu_subheadings"], config.thisTranslation["on"] if config.addTitleToPlainChapter else config.thisTranslation["off"])

    # Actions - change font size
    def smallerFont(self):
        if not config.fontSize == 5:
            config.fontSize = config.fontSize - 1
            if hasattr(self, 'defaultFontButton'):
                self.defaultFontButton.setText("{0} {1}".format(config.font, config.fontSize))
            self.reloadCurrentRecord(forceExecute=True)

    def largerFont(self):
        config.fontSize = config.fontSize + 1
        if hasattr(self, 'defaultFontButton'):
            self.defaultFontButton.setText("{0} {1}".format(config.font, config.fontSize))
        self.reloadCurrentRecord(forceExecute=True)

    def setFontSize(self, size):
        config.fontSize = size
        if hasattr(self, 'defaultFontButton'):
            self.defaultFontButton.setText("{0} {1}".format(config.font, config.fontSize))
        self.reloadCurrentRecord(forceExecute=True)

    def toggleHighlightMarker(self):
        config.showHighlightMarkers = not config.showHighlightMarkers
        self.reloadCurrentRecord(forceExecute=True)

    def reloadCurrentRecord(self, forceExecute=False):
        if config.readFormattedBibles:
            mappedBibles = (
                ("MIB", "OHGBi"),
                ("MOB", "OHGB"),
                # ("LXX1", "LXX1i"),
                # ("LXX2i", "LXX2"),
            )
            for view in ("main", "study"):
                textCommand = config.history[view][config.currentRecord[view]]
                for formattedBible, plainBible in mappedBibles:
                    textCommand = textCommand.replace(plainBible, formattedBible)
                self.newTabException = True
                self.runTextCommand(textCommand, False, view, forceExecute)
        else:
            mappedBibles = (
                ("MIB", "OHGBi"),
                ("MOB", "OHGB"),
                ("MPB", "OHGB"),
                ("MTB", "OHGB"),
                ("MAB", "OHGB"),
                # ("LXX1", "LXX1i"),
                # ("LXX2i", "LXX2"),
            )
            for view in ("main", "study"):
                textCommand = config.history[view][config.currentRecord[view]]
                for formattedBible, plainBible in mappedBibles:
                    textCommand = textCommand.replace(formattedBible, plainBible)
                self.newTabException = True
                self.runTextCommand(textCommand, False, view, forceExecute)

    # Actions - previous / next chapter
    def showAllChaptersMenu(self):
        self.newTabException = True
        self.textCommandChanged("_chapters:::{0}".format(config.mainText), "main")

    def showAllChaptersMenuStudy(self):
        self.newTabException = True
        self.textCommandChanged("_chapters:::{0}".format(config.studyText), "study")

    def previousMainChapter(self):
        newChapter = config.mainC - 1
        if newChapter == 0:
            prevBook = Bible(config.mainText).getPreviousBook(config.mainB)
            newChapter = BibleBooks.getLastChapter(prevBook)
            config.mainB = prevBook
        biblesSqlite = BiblesSqlite()
        mainChapterList = biblesSqlite.getChapterList(config.mainB)
        del biblesSqlite
        if newChapter in mainChapterList or config.menuLayout == "aleph":
            self.newTabException = True
            newTextCommand = self.bcvToVerseReference(config.mainB, newChapter, 1)
            self.textCommandChanged(newTextCommand, "main")

    def nextMainChapter(self):
        if config.mainC < BibleBooks.getLastChapter(config.mainB):
            newChapter = config.mainC + 1
            biblesSqlite = BiblesSqlite()
            mainChapterList = biblesSqlite.getChapterList(config.mainB)
            del biblesSqlite
            if newChapter in mainChapterList or config.menuLayout == "aleph":
                self.newTabException = True
                newTextCommand = self.bcvToVerseReference(config.mainB, newChapter, 1)
                self.textCommandChanged(newTextCommand, "main")
        else:
            self.nextMainBook()

    def gotoFirstChapter(self):
        config.mainC = 1
        self.newTabException = True
        newTextCommand = self.bcvToVerseReference(config.mainB, config.mainC, 1)
        self.textCommandChanged(newTextCommand, "main")

    def gotoLastChapter(self):
        config.mainC = BibleBooks.getLastChapter(config.mainB)
        self.newTabException = True
        newTextCommand = self.bcvToVerseReference(config.mainB, config.mainC, 1)
        self.textCommandChanged(newTextCommand, "main")

    def previousMainBook(self):
        prevBook = Bible(config.mainText).getPreviousBook(config.mainB)
        if prevBook:
            newTextCommand = self.bcvToVerseReference(prevBook, 1, 1)
            if len(newTextCommand) > 0:
                config.mainB = prevBook
                config.mainC = 1
                config.mainV = 1
                self.textCommandChanged(newTextCommand, "main")

    def nextMainBook(self):
        nextBook = Bible(config.mainText).getNextBook(config.mainB)
        if nextBook:
            newTextCommand = self.bcvToVerseReference(nextBook, 1, 1)
            if len(newTextCommand) > 0:
                config.mainB = nextBook
                config.mainC = 1
                config.mainV = 1
                self.textCommandChanged(newTextCommand, "main")

    def openMainChapter(self):
        newTextCommand = self.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        self.textCommandChanged(newTextCommand, "main")

    def openMainChapterMaterial(self, text=""):
        if config.enforceCompareParallel:
            self.enforceCompareParallelButtonClicked()
        newTextCommand = "BIBLE:::{0}:::{1}".format(text if text else config.mainText, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV))
        self.textCommandChanged(newTextCommand, "main")

    def openStudyChapterMaterial(self, text=""):
        newTextCommand = "STUDY:::{0}:::{1}".format(text if text else config.studyText, self.bcvToVerseReference(config.studyB, config.studyC, config.studyV))
        self.textCommandChanged(newTextCommand, "main")

    def openStudyChapter(self):
        newTextCommand = self.bcvToVerseReference(config.studyB, config.studyC, config.studyV)
        self.textCommandChanged(newTextCommand, "study")

    def openCommentary(self):
        command = "COMMENTARY:::{0}".format(self.verseReference("main")[1])
        self.textCommandChanged(command, "study")
        command = "_commentaryinfo:::{0}".format(config.commentaryText)
        self.runTextCommand(command)

    # Actions - recently opened bibles & commentary
    def mainTextMenu(self):
        if config.refButtonClickAction == "mini":
            self.openMiniControlTab(0)
        else:
            self.openControlPanelTab(0)

    def studyTextMenu(self):
        self.openControlPanelTab(0)

    def bookFeatures(self):
        self.openControlPanelTab(0)

    def chapterFeatures(self):
        self.openControlPanelTab(0)

    def mainRefButtonClicked(self):
        if config.refButtonClickAction == "master":
            self.openControlPanelTab(0)
        elif config.refButtonClickAction == "mini":
            self.openMiniControlTab(0)
        elif config.refButtonClickAction == "direct":
            self.openMainChapter()
        else:
            self.openControlPanelTab(0)

    def mainRefButtonClickedMaterial(self):
        #if config.refButtonClickAction == "direct":
        #    self.openMainChapter()
        #else:
        #    self.showAllChaptersMenu()
        self.showAllChaptersMenu()

    def getOnlineLink(self):
        return TextUtil.getWeblink(self.textCommandLineEdit.text())

    def goOnline(self):
        webbrowser.open(self.getOnlineLink())

    def shareOnline(self):
        self.runTextCommand("_qr:::{0}".format(self.getOnlineLink()))

    def studyRefButtonClickedMaterial(self):
        if (config.syncAction == "STUDY"):
            self.runTextCommand("STUDY:::{0}:::{1}".format(config.studyText, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV)))
        else:
            self.showAllChaptersMenuStudy()
    
    def studyRefButtonClicked(self):
        if config.refButtonClickAction == "master":
            self.openControlPanelTab(0, config.studyB, config.studyC, config.studyV, config.studyText)
        elif config.refButtonClickAction == "mini":
            self.openControlPanelTab(0, config.studyB, config.studyC, config.studyV, config.studyText)
        elif config.refButtonClickAction == "direct":
            self.openStudyChapter()
        else:
            self.openControlPanelTab(0, config.studyB, config.studyC, config.studyV, config.studyText)

    def swapBibles(self):
        if config.openBibleInMainViewOnly:
            self.enableStudyBibleButtonClicked()
        mText, mb, mc, mv = config.mainText, config.mainB, config.mainC, config.mainV
        sText, sb, sc, sv = config.studyText, config.studyB, config.studyC, config.studyV
        config.mainText, config.mainB, config.mainC, config.mainV = sText, sb, sc, sv
        config.studyText, config.studyB, config.studyC, config.studyV = mText, mb, mc, mv
        self.runTextCommand("BIBLE:::{0}:::{1}".format(config.mainText, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV)))
        if not (config.syncAction == "STUDY"):
            self.runTextCommand("STUDY:::{0}:::{1}".format(config.studyText, self.bcvToVerseReference(config.studyB, config.studyC, config.studyV)))        

    def commentaryRefButtonClicked(self):
        if self.textCommandParser.isDatabaseInstalled("commentary"):
            if config.refButtonClickAction == "master":
                self.openControlPanelTab(1)
            elif config.refButtonClickAction == "mini":
                self.openMiniControlTab(2)
            elif config.refButtonClickAction == "direct":
                self.openCommentary()
            else:
                self.openControlPanelTab(1)
        else:
            self.textCommandParser.databaseNotInstalled("commentary")

    def changeBibleVersion(self, index):
        if not self.refreshing:
            if config.enforceCompareParallel:
                self.enforceCompareParallelButtonClicked()
            command = "TEXT:::{0}".format(self.bibleVersions[index])
            self.runTextCommand(command)

    def updateVersionCombo(self):
        if hasattr(self, "bibleSelection") and self.bibleSelection is not None and config.menuLayout in ("material",):
            self.setBibleSelection()
        if self.versionCombo is not None and config.menuLayout in ("focus", "Starter", "aleph", "material"):
            self.refreshing = True
            textIndex = 0
            if config.mainText in self.bibleVersions:
                textIndex = self.bibleVersions.index(config.mainText)
            self.versionCombo.setCurrentIndex(textIndex)
            self.refreshing = False
        if self.versionButton is not None and config.menuLayout not in ("Starter",):
            self.versionButton.setText(config.mainText)

    def changeCommentaryVersion(self, index):
        if not self.refreshing:
            commentary = self.commentaryList[index]
            if config.syncAction == "COMMENTARY":
                command = "COMMENTARY:::{0}:::{1}".format(commentary, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV))
            else:
                command = "_commentarychapters:::{0}".format(commentary)
            self.runTextCommand(command)

    def updateMainRefButton(self):
        *_, verseReference = self.verseReference("main")
        if config.mainC > 0:
            if config.menuLayout == "material":
                self.setBibleSelection()
                self.setMainRefMenu()
            elif config.menuLayout == "aleph":
                self.mainRefButton.setText(":::".join(self.verseReference("main")))
            else:
                self.mainRefButton.setText(verseReference)
            self.updateVersionCombo()
            if (config.syncAction == "STUDY") and not config.openBibleInMainViewOnly and not self.syncingBibles:
                self.syncingBibles = True
                newTextCommand = "STUDY:::{0}".format(verseReference)
                self.runTextCommand(newTextCommand, True, "study")
            elif config.syncAction:
                self.syncingBibles = True
                newTextCommand = f"{config.syncAction}:::{verseReference}"
                self.runTextCommand(newTextCommand, True, "study")

    def updateStudyRefButton(self):
        *_, verseReference = self.verseReference("study")
        if config.menuLayout == "material":
            self.setStudyBibleSelection()
            self.setStudyRefMenu()
        else:
            self.studyRefButton.setText(":::".join(self.verseReference("study")))
        if (config.syncAction == "STUDY") and not config.openBibleInMainViewOnly and not self.syncingBibles:
            self.syncingBibles = True
            newTextCommand = "MAIN:::{0}".format(verseReference)
            self.runTextCommand(newTextCommand, True, "main")

    def updateCommentaryRefButton(self):
        if hasattr(self, "commentaryCombo"):
            self.updateCommentaryCombo()
        if self.commentaryRefButton:
            self.commentaryRefButton.setText(config.commentaryText)

    def updateCommentaryCombo(self):
        if self.commentaryCombo is not None and config.menuLayout == "material":
            self.refreshing = True
            textIndex = 0
            if config.commentaryText in self.commentaryList:
                textIndex = self.commentaryList.index(config.commentaryText)
            self.commentaryCombo.setCurrentIndex(textIndex)
            self.refreshing = False

    def verseReference(self, view):
        if view == "main":
            return (config.mainText, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV))
        elif view == "study":
            return (config.studyText, self.bcvToVerseReference(config.studyB, config.studyC, config.studyV))
        elif view == "commentary":
            return "{0}:::{1}".format(config.commentaryText,
                                      self.bcvToVerseReference(config.commentaryB, config.commentaryC,
                                                               config.commentaryV))

    # Actions - access history records
    def mainHistoryButtonClicked(self):
        self.openControlPanelTab(4)
        # self.mainView.setHtml(self.getHistory("main"), baseUrl)

    def studyHistoryButtonClicked(self):
        self.openControlPanelTab(4)
        # self.studyView.setHtml(self.getHistory("study"), baseUrl)

    def getHistory(self, view):
        html = self.crossPlatform.getHistory(view)
        return self.htmlWrapper(html)

    # navigation between history records
    def openHistoryRecord(self, view, recordNumber):
        config.currentRecord[view] = recordNumber
        textCommand = config.history[view][recordNumber]
        self.runTextCommand(textCommand, False, view)
        if view == "main":
            self.textCommandLineEdit.setText(textCommand)

    def back(self):
        mainCurrentRecord = config.currentRecord["main"]
        if not mainCurrentRecord == 0:
            mainCurrentRecord = mainCurrentRecord - 1
            self.openHistoryRecord("main", mainCurrentRecord)

    def forward(self):
        mainCurrentRecord = config.currentRecord["main"]
        if not mainCurrentRecord == (len(config.history["main"]) - 1):
            mainCurrentRecord = mainCurrentRecord + 1
            self.openHistoryRecord("main", mainCurrentRecord)

    def studyBack(self):
        if config.parallelMode == 0:
            self.parallel()
        studyCurrentRecord = config.currentRecord["study"]
        if not studyCurrentRecord == 0:
            studyCurrentRecord = studyCurrentRecord - 1
            self.openHistoryRecord("study", studyCurrentRecord)

    def studyForward(self):
        if config.parallelMode == 0:
            self.parallel()
        studyCurrentRecord = config.currentRecord["study"]
        if not studyCurrentRecord == (len(config.history["study"]) - 1):
            studyCurrentRecord = studyCurrentRecord + 1
            self.openHistoryRecord("study", studyCurrentRecord)

    # finish view loading
    def checkMainPageTermination(terminationStatus, exitCode):
        print(terminationStatus, exitCode)

    def checkStudyPageTermination(terminationStatus, exitCode):
        print(terminationStatus, exitCode)

    def getScrollActiveVerseJS(self, studyView=False, index=None):
        if index is not None:
            b, c, v, *_ = self.getTabBcv(studyView=studyView, index=index)
        else:
            if studyView:
                b, c, v = config.studyB, config.studyC, config.studyV
            else:
                b, c, v = config.mainB, config.mainC, config.mainV
        return self.getScrollVerseJS(b, c, v)
    
    def getScrollVerseJS(self, b, c, v, underline=False):
        activeVerseNoColour = config.darkThemeActiveVerseColor if config.theme in ("dark", "night") else config.lightThemeActiveVerseColor
        js = """
            var activeVerse = document.getElementById('v{0}.{1}.{2}');
            if (typeof(activeVerse) != 'undefined' && activeVerse != null) {3}
                activeVerse.scrollIntoView(); activeVerse.style.color = '{5}';
                {6}
            {4} else if (document.getElementById('v0.0.0') != null) {3}
                document.getElementById('v0.0.0').scrollIntoView();
            {4}
        """.format(
            b,
            c,
            v,
            "{",
            "}",
            activeVerseNoColour,
            "activeVerse.style.textDecoration = 'underline';" if underline else "",
        )
        #print("studyView", studyView)
        #print(js)
        return js

    def startLoading(self):
        self.laodingStartTime = time.time()

    def finishMainViewLoading(self, ok, index=None):
        # scroll to the main verse
        if index is not None:
            self.mainView.widget(index).page().runJavaScript(self.getScrollActiveVerseJS(studyView=False, index=index))
            #self.fixContentDisplay(self.mainView)
            self.displayLoadingTime()
        else:
            self.mainPage.runJavaScript(self.getScrollActiveVerseJS(studyView=False, index=index))
            #self.fixContentDisplay(self.mainView)
            self.displayLoadingTime()

    def finishStudyViewLoading(self, ok, index=None, js=""):
        # scroll to the study verse
        if index is not None:
            self.studyView.widget(index).page().runJavaScript(js if js else self.getScrollActiveVerseJS(studyView=True, index=index))
            #self.fixContentDisplay(self.studyView)
            self.displayLoadingTime()
        else:
            self.studyPage.runJavaScript(js if js else self.getScrollActiveVerseJS(studyView=True, index=index))
            #self.fixContentDisplay(self.studyView)
            self.displayLoadingTime()

    """
    def fixContentDisplay(self, view):
        if config.qtLibrary == "pyside6":
            # It is observed that Qt6 library has a display issue.
            # QtWebEngineView widgets inside tabs do not display content properly after html is loaded.
            # Workaround is to switch tab selection
            index = view.currentIndex()
            if index == (config.numberOfTab - 1):
                view.setCurrentIndex(index - 1)
            else:
                view.setCurrentIndex(index + 1)
            view.setCurrentIndex(index)"""
    def displayLoadingTime(self):
        timeDifference = time.time() - self.laodingStartTime
        self.statusBar().showMessage(f"Loaded in {timeDifference}s.", config.displayLoadingTime)
        self.statusBar().show()
        QTimer.singleShot(config.displayLoadingTime, self.statusBar().hide)

    # finish pdf printing
    def pdfPrintingFinishedAction(self, filePath, success):
        if success:
            if self.pdfOpened:
                self.pdfOpened = False
            else:
                self.openExternalFile(filePath, isPdf=True)
                self.pdfOpened = True
        else:
            print("Failed to print pdf")

    # running specific commands
    def runMainText(self, text):
        newTextCommand = "TEXT:::{0}".format(text)
        self.textCommandChanged(newTextCommand, "main")

    def runStudyText(self, text):
        newTextCommand = "STUDYTEXT:::{0}".format(text)
        self.textCommandChanged(newTextCommand, "main")

    def chapterAction(self, keyword, verseReference=None):
        if verseReference is None:
            verseReference = self.bcvToVerseReference(config.mainB, config.mainC, config.mainV).split(":")[0]
        else:
            verseReference = verseReference.split(":")[0]
        newTextCommand = "{0}:::{1}".format(keyword, verseReference)
        self.textCommandChanged(newTextCommand, "main")

    def bookAction(self, keyword, b=None):
        if b is None:
            b = config.mainB
        engFullBookName = BibleBooks().abbrev["eng"][str(b)][1]
        self.textCommandChanged(f"{keyword}:::{engFullBookName}", "main")

    def searchBookName(self, dictionary, b=None):
        if b is None:
            b = config.mainB
        engFullBookName = BibleBooks().abbrev["eng"][str(b)][1]
        matches = re.match("^[0-9]+? (.*?)$", engFullBookName)
        if matches:
            engFullBookName = matches.group(1)
        newTextCommand = "SEARCHTOOL:::{0}:::{1}".format(config.dictionary if dictionary else config.encyclopedia, engFullBookName)
        self.textCommandChanged(newTextCommand, "main")

    def searchBookChapter(self, resource, b=None):
        if b is None:
            b = config.mainB
        engFullBookName = BibleBooks().abbrev["eng"][str(b)][1]
        newTextCommand = "SEARCHBOOKCHAPTER:::{0}:::{1}".format(resource, engFullBookName)
        self.textCommandChanged(newTextCommand, "main")

    def runFeature(self, keyword, verseReference=None):
        if verseReference is None:
            verseReference = self.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        newTextCommand = "{0}:::{1}".format(keyword, verseReference)
        self.textCommandChanged(newTextCommand, "main")

    def runCompareAction(self, keyword, verseReference=None):
        if not config.enforceCompareParallel:
            self.enforceCompareParallelButtonClicked()
        if config.menuLayout == "material":
            selectedVersions = "_".join(config.compareParallelList)
        else:
            selectedVersions = "{0}_{1}_{2}".format(config.favouriteBible, config.favouriteBible2, config.favouriteBible3)
        self.runFeature("{0}:::{1}".format(keyword, selectedVersions), verseReference)

    def runMOB(self):
        self.runFeature("BIBLE:::MOB")

    def runMIB(self):
        self.runFeature("BIBLE:::MIB")

    def runMIBStudy(self):
        if config.openBibleInMainViewOnly:
            self.enableStudyBibleButtonClicked()
        mainVerseReference = self.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        self.runTextCommand("STUDY:::{0}:::{1}".format(config.favouriteOriginalBible, mainVerseReference), addRecord=True, source="study", forceExecute=True)

    def runMAB(self):
        self.runFeature("BIBLE:::MAB")

    def runMPB(self):
        self.runFeature("BIBLE:::MPB")

    def runMTB(self):
        self.runFeature("BIBLE:::MTB")

    def runTransliteralBible(self):
        self.runFeature("BIBLE:::TRLIT")

    def runKJV2Bible(self):
        self.runFeature("BIBLE:::KJVx")

    def runCOMPARE(self):
        self.runFeature("COMPARE")

    def runCONTRASTS(self):
        self.runFeature("DIFFERENCE")

    def runCROSSREFERENCE(self):
        self.runFeature("CROSSREFERENCE")

    def runTSKE(self):
        self.runFeature("TSKE")

    def runTRANSLATION(self):
        self.runFeature("TRANSLATION")

    def runDISCOURSE(self):
        self.runFeature("DISCOURSE")

    def runWORDS(self):
        self.runFeature("WORDS")

    def runCOMBO(self):
        self.runFeature("COMBO")

    def runCOMMENTARY(self):
        self.runFeature("COMMENTARY")

    def runINDEX(self):
        self.runFeature("INDEX")

    # Actions - mute / unmute audio player
    def getMuteAudioDisplay(self):
        if config.audioMuted:
            return self.getCrossplatformPath("material/av/volume_off/materialiconsoutlined/48dp/2x/outline_volume_off_black_48dp.png")
        else:
            return self.getCrossplatformPath("material/av/volume_up/materialiconsoutlined/48dp/2x/outline_volume_up_black_48dp.png")

    def getMuteAudioToolTip(self):
        if config.audioMuted:
            return "{0}: {1}".format(config.thisTranslation["mute"], config.thisTranslation["on"])
        else:
            return "{0}: {1}".format(config.thisTranslation["mute"], config.thisTranslation["off"])

    def muteAudioButtonClicked(self):
        self.toggleAudioPlayerMuteOption()
        #icon = self.getQIcon(self.getMuteAudioDisplay())
        #self.muteAudioButton.setStyleSheet(icon)
        #self.muteAudioButton.setToolTip(self.getMuteAudioToolTip())
        iconFile = os.path.join("htmlResources", self.getMuteAudioDisplay())
        qIcon = self.getMaskedQIcon(iconFile, config.maskMaterialIconColor, config.maskMaterialIconBackground, toolButton=True)
        self.muteAudioButton.setIcon(qIcon)
        self.muteAudioButton.setToolTip(self.getMuteAudioToolTip())

    # Actions - enable or disable playlist looping
    def getLoopMediaButtonDisplay(self):
        if config.loopMediaPlaylist:
            return self.getCrossplatformPath("material/places/all_inclusive/materialiconsoutlined/48dp/2x/outline_all_inclusive_black_48dp.png")
        else:
            return self.getCrossplatformPath("material/action/hide_source/materialiconsoutlined/48dp/2x/outline_hide_source_black_48dp.png")

    def getLoopMediaButtonToolTip(self):
        if config.loopMediaPlaylist:
            return "{0}: {1}".format(config.thisTranslation["loopPlaylist"], config.thisTranslation["on"])
        else:
            return "{0}: {1}".format(config.thisTranslation["loopPlaylist"], config.thisTranslation["off"])

    def loopMediaButtonClicked(self):
        config.loopMediaPlaylist = not config.loopMediaPlaylist
        icon = self.getQIcon(self.getLoopMediaButtonDisplay())
        self.loopMediaButton.setStyleSheet(icon)
        self.loopMediaButton.setToolTip(self.getLoopMediaButtonToolTip())

    # Actions - enable or disable bible text scrolling synchronisation with audio 
    def getAudioTextScrollSyncDisplay(self):
        if config.scrollBibleTextWithAudioPlayback:
            return self.getCrossplatformPath("material/communication/import_export/materialiconsoutlined/48dp/2x/outline_import_export_black_48dp.png")
        else:
            return self.getCrossplatformPath("material/device/mobiledata_off/materialiconsoutlined/48dp/2x/outline_mobiledata_off_black_48dp.png")

    def getAudioTextScrollSyncToolTip(self):
        return "{0}: {1}".format(config.thisTranslation["scrollBibleTextWithAudioPlayback"], config.thisTranslation["on" if config.scrollBibleTextWithAudioPlayback else "off"])

    def audioTextScrollSyncButtonClicked(self):
        config.scrollBibleTextWithAudioPlayback = not config.scrollBibleTextWithAudioPlayback
        if config.scrollBibleTextWithAudioPlayback and not config.audioTextSync:
            self.audioTextSyncButtonClicked()
        icon = self.getQIcon(self.getAudioTextScrollSyncDisplay())
        self.audioTextScrollSyncButton.setStyleSheet(icon)
        self.audioTextScrollSyncButton.setToolTip(self.getAudioTextScrollSyncToolTip())

    # Actions - enable or disable text synchronisation with audio 
    def getAudioTextSyncDisplay(self):
        if config.audioTextSync:
            return self.getCrossplatformPath("material/editor/title/materialiconsoutlined/48dp/2x/outline_title_black_48dp.png")
        else:
            return self.getCrossplatformPath("material/editor/format_clear/materialiconsoutlined/48dp/2x/outline_format_clear_black_48dp.png")

    def getAudioTextSyncToolTip(self):
        if config.audioTextSync:
            return "{0}: {1}".format(config.thisTranslation["audioTextSync"], config.thisTranslation["on"])
        else:
            return "{0}: {1}".format(config.thisTranslation["audioTextSync"], config.thisTranslation["off"])

    def audioTextSyncButtonClicked(self):
        config.audioTextSync = not config.audioTextSync
        if not config.audioTextSync and config.scrollBibleTextWithAudioPlayback:
            self.audioTextScrollSyncButtonClicked()
        icon = self.getQIcon(self.getAudioTextSyncDisplay())
        self.audioTextSyncButton.setStyleSheet(icon)
        self.audioTextSyncButton.setToolTip(self.getAudioTextSyncToolTip())

    # Actions - enable or disable instant highlight
    def getInstantHighlightDisplay(self):
        if config.enableInstantHighlight:
            return self.getCrossplatformPath("material/image/auto_fix_normal/materialiconsoutlined/48dp/2x/outline_auto_fix_normal_black_48dp.png")
        else:
            return self.getCrossplatformPath("material/image/auto_fix_off/materialiconsoutlined/48dp/2x/outline_auto_fix_off_black_48dp.png")

    def getInstantHighlightToolTip(self):
        if config.enableInstantHighlight:
            return "{0}: {1}".format(config.thisTranslation["instantHighlight"], config.thisTranslation["on"])
        else:
            return "{0}: {1}".format(config.thisTranslation["instantHighlight"], config.thisTranslation["off"])

    def enableInstantHighlightButtonClicked(self):
        if config.enableInstantHighlight:
            self.removeInstantHighlight()
        else:
            config.enableInstantHighlight = True
            self.runInstantHighlight()
        icon = self.getQIcon(self.getInstantHighlightDisplay())
        if config.menuLayout == "material":
            self.enableInstantHighlightButton.setStyleSheet(icon)
        else:
            self.enableInstantHighlightButton.setIcon(icon)
        self.enableInstantHighlightButton.setToolTip(self.getInstantHighlightToolTip())
        if config.menuLayout == "material":
            self.setupMenuLayout("material")

    # Run instant highlight
    def runInstantHighlight(self):
        text = self.textCommandLineEdit.text().strip()
        if text.endswith(":::"):
            keyword = text[:-3].lower()
            if keyword and keyword in self.textCommandParser.interpreters:
                tooltip = self.textCommandParser.interpreters[keyword][-1]
                tooltip = re.sub("^            ", "", tooltip, flags=re.M)
                self.textCommandLineEdit.setToolTip(tooltip)
            else:
                self.textCommandLineEdit.setToolTip(config.thisTranslation["bar1_command"])
        else:
            self.textCommandLineEdit.setToolTip(config.thisTranslation["bar1_command"])
        if config.enableInstantHighlight:
            self.mainView.currentWidget().findText(text, QWebEnginePage.FindFlags())
            self.studyView.currentWidget().findText(text, QWebEnginePage.FindFlags())

    def removeInstantHighlight(self):
        config.enableInstantHighlight = False
        self.mainView.currentWidget().findText("", QWebEnginePage.FindFlags())
        self.studyView.currentWidget().findText("", QWebEnginePage.FindFlags())

    # Clear all tabs
    def refreshAllMainWindowTabs(self):
        thisIndex = self.mainView.currentIndex()
        nextIndex = thisIndex + 1
        for tab in range(0, config.numberOfTab):
            if nextIndex >= config.numberOfTab:
                nextIndex = 0
            self.mainView.setCurrentIndex(nextIndex)
            nextIndex += 1

    def refreshAllStudyWindowTabs(self):
        thisIndex = self.studyView.currentIndex()
        nextIndex = thisIndex + 1
        for tab in range(0, config.numberOfTab):
            if nextIndex >= config.numberOfTab:
                nextIndex = 0
            self.studyView.setCurrentIndex(nextIndex)
            nextIndex += 1

    def clearAllWindowTabs(self):
        self.clearAllMainWindowTabs()
        self.clearAllStudyWindowTabs()

    def clearAllMainWindowTabs(self):
        for tab in range(0, config.numberOfTab):
            self.mainView.setCurrentIndex(tab)
            self.mainView.setHtml("", "")
            self.mainView.setTabText(tab, "Bible")
            config.tabHistory["main"][str(tab)] = ''
        self.mainView.setCurrentIndex(0)

    def clearAllStudyWindowTabs(self):
        for tab in range(0, config.numberOfTab):
            self.studyView.setCurrentIndex(tab)
            self.studyView.setHtml("", "")
            self.studyView.setTabText(tab, "Study")
            config.tabHistory["study"][str(tab)] = ''
        self.studyView.setCurrentIndex(0)

    # change of unique bible commands

    def mainTextCommandChanged(self, newTextCommand):
        try:
            if isinstance(newTextCommand, str) and newTextCommand not in ("main.html", "UniqueBible.app", "Unique Bible App"):
                self.textCommandChanged(newTextCommand, "main")
        except Exception as ex:
            self.logger.error("mainTextCommandChanged:{0}".format(ex))

    def studyTextCommandChanged(self, newTextCommand):
        try:
            if isinstance(newTextCommand, str) and newTextCommand not in ("main.html", "UniqueBible.app", "Unique Bible App", "index.html", "This E-Book is Published with Bibi | EPUB Reader on your website.") \
                    and not newTextCommand.endswith("UniqueBibleApp.png") \
                    and not newTextCommand.startswith("viewer.html") \
                    and not newTextCommand.endswith(".pdf") \
                    and not newTextCommand.startswith("ePubViewer.html") \
                    and not newTextCommand.endswith("Published with Bibi") \
                    or (newTextCommand.lower().startswith("cmd:::") and newTextCommand.endswith(".pdf")) \
                    or (newTextCommand.lower().startswith("pdf:::") and newTextCommand.endswith(".pdf")) \
                    or (newTextCommand.lower().startswith("anypdf:::") and newTextCommand.endswith(".pdf")):
                self.textCommandChanged(newTextCommand, "study")
        except Exception as ex:
            self.logger.error("studyTextCommandChanged:{0}".format(ex))

    def instantTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "instant")

    # change of text command detected via change of document.title
    def textCommandChanged(self, newTextCommand, source="main"):
        if isinstance(newTextCommand, str):
            exceptionTuple = ("UniqueBible.app", "about:blank", "study.html", "Google Maps - gmplot", "bible_map.html")
            if not (newTextCommand.startswith("data:text/html;") or newTextCommand.startswith("file:///") or newTextCommand[
                                                                                                             -4:] == ".txt" or newTextCommand in exceptionTuple):
                if source == "main" and not newTextCommand.startswith("_"):
                    self.textCommandLineEdit.setText(newTextCommand)
                if newTextCommand.startswith("_"):
                    self.runTextCommand(newTextCommand, False, source)
                else:
                    self.runTextCommand(newTextCommand, True, source)

    # change of text command detected via user input
    def textCommandEntered(self, source="main"):
        newTextCommand = self.textCommandLineEdit.text()
        self.runTextCommand(newTextCommand, True, source)

    def runTextCommand(self, textCommand, addRecord=True, source="main", forceExecute=False):
        textCommandKeyword, *_ = re.split('[ ]*?:::[ ]*?', textCommand, 1)
        if not re.match("^online:::", textCommand, flags=re.IGNORECASE) or (":::" in textCommand and textCommandKeyword.lower() in self.textCommandParser.interpreters):
            self.passRunTextCommand(textCommand, addRecord, source, forceExecute)
        elif textCommand != self.onlineCommand:
            *_, address = textCommand.split(":::")
            if config.enableHttpServer and address.startswith("http"):
                subprocess.Popen("{0} {1}".format(config.open, address), shell=True)
            elif config.useWebbrowser:
                webbrowser.open(address)
            else:
                if config.openStudyWindowContentOnNextTab:
                    self.nextStudyWindowTab()
                self.onlineCommand = textCommand
                self.studyView.load(QUrl(address))
                self.addHistoryRecord("study", textCommand)

    def refineCommand(self, command):
        command = command.strip()
        try:
            # match a bible version
            if command in self.crossPlatform.textList:
                command = f"TEXT:::{command}"
            # match a bible reference, started with book number, e.g. 43.3.16
            elif re.search(r"^[0-9]+?\.[0-9]+?\.[0-9]+?$", command):
                b, c, v = [int(i) for i in command.split(".")]
                command = self.textCommandParser.bcvToVerseReference(b, c, v)
            else:
                # match a bible reference
                bc = command.split(":", 1)
                bci = [int(i) for i in bc if i]
                if len(bc) == 2 and len(bci) == 1:
                    # Users specify a verse number, e.g. :16
                    if command.startswith(":"):
                        command = self.textCommandParser.bcvToVerseReference(config.mainB, config.mainC, bci[0])
                    # Users specify a chapter number, e.g. 3:
                    elif command.endswith(":"):
                        command = self.textCommandParser.bcvToVerseReference(config.mainB, bci[0], 1)
                # Users specify both a chapter number and a verse number, e.g. 3:16
                elif len(bc) == 2 and len(bci) == 2:
                    command = self.textCommandParser.bcvToVerseReference(config.mainB, bci[0], bci[1])
        except:
            pass
        return command

    def passRunTextCommand(self, textCommand, addRecord=True, source="main", forceExecute=False):
        textCommand = self.refineCommand(textCommand)
        if config.logCommands:
            self.logger.debug(textCommand[:80])
        # reset document.title
        changeTitle = "document.title = 'UniqueBible.app';"
        self.mainPage.runJavaScript(changeTitle)
        self.studyPage.runJavaScript(changeTitle)
        self.instantPage.runJavaScript(changeTitle)
        # prevent repetitive command within unreasonable short time
        now = time.time()
        timeDifference = int(now - self.now)
        if textCommand == "_stayOnSameTab:::":
            self.newTabException = True
        elif (not forceExecute and (timeDifference <= 1 and ((source == "main" and textCommand == self.lastMainTextCommand) or (source == "study" and textCommand == self.lastStudyTextCommand)))) or textCommand == "main.html":
            self.logger.debug("Repeated command blocked {0}:{1}".format(textCommand, source))
        else:
            # handle exception for new tab features
            if re.search('^(_commentary:::|_menu:::|_vnsc:::|_chapters:::|_verses:::|_commentaries|_commentarychapters:::|_commentaryverses:::)', textCommand.lower()):
                self.newTabException = True
            # parse command
            view, content, infoDict = self.textCommandParser.parser(textCommand, source)
            # plugin event hook
            config.eventView = view
            config.eventContent = content
            config.eventDict = infoDict
            PluginEventHandler.handleEvent("command", textCommand)
            content = config.eventContent
            # process content
            if content == "INVALID_COMMAND_ENTERED":
                self.displayMessage("{0} '{1}'".format(config.thisTranslation["message_invalid"], textCommand))
                self.logger.info("{0} '{1}'".format(config.thisTranslation["message_invalid"], textCommand))
            elif content == "NO_AUDIO":
                self.displayMessage("{0} - {1}".format(config.thisTranslation["menu11_audio"], config.thisTranslation["message_installFirst"]))
            elif content == "NO_HEBREW_AUDIO":
                audioModule = "BHS5 (Hebrew; word-by-word)"
                self.displayMessage("{1} - {0}\n{2}".format(audioModule, config.thisTranslation["menu11_audio"], config.thisTranslation["message_installFirst"]))
                self.installGithubBibleMp3(audioModule)
            elif content == "NO_GREEK_AUDIO":
                audioModule = "OGNT (Greek; word-by-word)"
                self.displayMessage("{1} - {0}\n{2}".format(audioModule, config.thisTranslation["menu11_audio"], config.thisTranslation["message_installFirst"]))
                self.installGithubBibleMp3(audioModule)
            elif view == "command":
                self.commandPrompt(content)
            else:
                #if view == "main":
                #    content = config.enableInstantHighlight(content)
                pdfFilename = infoDict['pdf_filename'] if "pdf_filename" in infoDict.keys() else None
                outputFile = None
                if pdfFilename is not None:
                    outputFile = os.path.join("htmlResources", "{0}.pdf".format(pdfFilename))
                    fileObject = open(outputFile, "wb")
                    fileObject.write(content)
                    fileObject.close()
                else:
                    # wrap with shared UBA html elements for most cases
                    if ('tab_title' in infoDict.keys() and infoDict['tab_title'] in ("Map",)):
                        html = content
                    else:
                        html = self.wrapHtml(content, view, textCommand.startswith("BOOK:::"))
                views = {
                    "main": self.mainView,
                    "study": self.studyView,
                    "instant": self.instantView,
                }
                # add hovering action to bible reference links
#                searchReplace = (
#                    (
#                    '{0}document.title="BIBLE:::([^<>"]*?)"{0}|"document.title={0}BIBLE:::([^<>{0}]*?){0}"'.format("'"),
#                    r'{0}document.title="BIBLE:::\1\2"{0} onmouseover={0}document.title="_imvr:::\1\2"{0}'.format("'")),
#                    (
#                    r'onclick=([{0}"])bcv\(([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?)\)\1'.format(
#                        "'"), r'onclick="bcv(\2,\3,\4,\5,\6)" onmouseover="imv(\2,\3,\4,\5,\6)"'),
#                    (r'onclick=([{0}"])bcv\(([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?)\)\1'.format("'"),
#                     r'onclick="bcv(\2,\3,\4)" onmouseover="imv(\2,\3,\4)"'),
#                    (
#                    r'onclick=([{0}"])cr\(([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?)\)\1'.format("'"), self.convertCrLink),
#                )
#                for search, replace in searchReplace:
#                    html = re.sub(search, replace, html)
                # load into widget view
                if view == "study":
                    if pdfFilename is not None:
                        self.openPdfReader(outputFile)
                    else:
                        tab_title = infoDict['tab_title'] if 'tab_title' in infoDict.keys() else ""
                        anchor = infoDict['jump_to'] if "jump_to" in infoDict.keys() else None
                        self.openTextOnStudyView(html, tab_title, anchor, textCommand)
                elif view == "main":
                    self.openTextOnMainView(html, textCommand)
                elif view.startswith("popover"):
                    if pdfFilename is not None:
                        self.openPdfReader(outputFile)
                    else:
                        viewElements = view.split(".")
                        view = viewElements[1]
                        if view == "fullscreen":
                            screenNo = -1
                            try:
                                screenNo=int(viewElements[2])
                            except:
                                pass
                            views["main"].currentWidget().openPopover(html=html, fullScreen=True, screenNo=screenNo)
                        else:
                            views[view].currentWidget().openPopover(html=html)
                # There is a case where view is an empty string "".
                # The following condition applies where view is not empty only.
                elif view:
                    views[view].setHtml(html, baseUrl)

                if hasattr(config, "iModeSplitterSizes") and view == "instant" and (config.instantMode == 0 or (config.iModeSplitterSizes[-1] == 0 and not config.instantMode > 0)):
                    self.showFlotableInstantView(html)

                if addRecord:
                    tab = "0"
                    if view == "main":
                        tab = str(self.mainView.currentIndex())
                    elif view == "study":
                        tab = str(self.studyView.currentIndex())
                    self.addHistoryRecord(view, textCommand, tab)
#                if addRecord == True and view in ("main", "study"):
#                    compareParallel = (textCommand.lower().startswith("compare:::") or textCommand.lower().startswith("parallel:::"))
#                    if config.enforceCompareParallel and not config.tempRecord:
#                        if not ":::" in textCommand:
#                            view = "study"
#                            textCommand = "STUDY:::{0}".format(textCommand)
#                        elif textCommand.lower().startswith("bible:::"):
#                            view = "study"
#                            textCommand = re.sub("^.*?:::", "STUDY:::", textCommand)
#                    if config.tempRecord:
#                        self.addHistoryRecord("main", config.tempRecord)
#                        config.tempRecord = ""
#                    elif not (view == "main" and config.enforceCompareParallel) or compareParallel:
#                        self.addHistoryRecord(view, textCommand)

            # set checking blocks to prevent running the same command within unreasonable time frame
            self.now = now
            if source == "main":
                self.lastMainTextCommand = textCommand
            elif source == "study":
                self.lastStudyTextCommand = textCommand

    def showFlotableInstantView(self, html):
        cursor_position = QCursor.pos().toTuple()
        if self.toolTip is None:
            self.toolTip = Tooltip(self)
        else:
            self.bringToForeground(self.toolTip)
        self.toolTip.instantView.setHtml(html, baseUrl)
        self.toolTip.show()

        availableGeometry = QGuiApplication.primaryScreen().availableGeometry()
        screenWidth = availableGeometry.width()
        screenHeight = availableGeometry.height()
        x = cursor_position[0] + 15
        if (x + config.floatableInstantViewWidth) > screenWidth:
            x = screenWidth - config.floatableInstantViewWidth
        y = cursor_position[1]
        if (y + config.floatableInstantViewHeight) > screenHeight:
            y = screenHeight - config.floatableInstantViewHeight
        #self.toolTip.move(*cursor_position)
        self.toolTip.setGeometry(x, y, config.floatableInstantViewWidth, config.floatableInstantViewHeight)

    def closePopover(self, view="main"):
        views = {
            "main": self.mainView,
            "study": self.studyView,
            "instant": self.instantView,
        }
        views[view].currentWidget().closePopover()

#    def instantHighlight(self, text):
#        if config.instantHighlightString:
#            text = re.sub("({0})".format(config.instantHighlightString), r"<z>\1</z>", text, flags=re.IGNORECASE)
#            return TextUtil.fixTextHighlighting(text)
#        else:
#            return text

    def convertCrLink(self, match):
        *_, b, c, v = match.groups()
        bookNo = Converter().convertMyBibleBookNo(int(b))
        return 'onclick="bcv({0},{1},{2})" onmouseover="imv({0},{1},{2})"'.format(bookNo, c, v)

    def displayPlainTextOnBottomWindow(self, content):
        html = self.wrapHtml(content)
        self.instantView.setHtml(html, config.baseUrl)
        if config.forceGenerateHtml:
            outputFile = os.path.join("htmlResources", "instant.html")
            fileObject = open(outputFile, "w", encoding="utf-8")
            fileObject.write(html)
            fileObject.close()

    def wrapHtml(self, content, view="", book=False):
        fontFamily = config.font
        fontSize = "{0}px".format(config.fontSize)
        if book:
            if config.overwriteBookFontFamily:
                fontFamily = config.overwriteBookFontFamily
            if config.overwriteBookFontSize:
                if type(config.overwriteBookFontSize) == str:
                    fontSize = config.overwriteBookFontSize
                elif type(config.overwriteBookFontSize) == int:
                    fontSize = "{0}px".format(config.overwriteBookFontSize)
        if hasattr(config, "mainCssBibleFontStyle") and view in ("main", "instant"):
            bibleCss = config.mainCssBibleFontStyle
        elif hasattr(config, "studyCssBibleFontStyle") and view == "study":
            bibleCss = config.studyCssBibleFontStyle
        else:
            bibleCss = ""
        studyActiveText = config.mainText if config.openBibleInMainViewOnly else config.studyText
        bcv = (studyActiveText, config.studyB, config.studyC, config.studyV) if view == "study" else (config.mainText, config.mainB, config.mainC, config.mainV)
        activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(*bcv)
        html = ("""
                <!DOCTYPE html><html><head><meta charset='utf-8'><title>UniqueBible.app</title>
                <style>body {2} font-size: {4}; font-family:'{5}';{3} 
                zh {2} font-family:'{6}'; {3} 
                {8} {9}
                </style>
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/{7}.css?v=1.065'>
                {10}
                <link id='theme_stylesheet' rel='stylesheet' type='text/css' href='css/custom.css?v=1.065'>
                <script src='js/common.js?v=1.065'></script>
                <script src='js/{7}.js?v=1.065'></script>
                <script src='w3.js?v=1.065'></script>
                <script src='js/custom.js?v=1.065'></script>
                {0}
                {11}
                <script>var versionList = []; var compareList = []; var parallelList = []; 
                var diffList = []; var searchList = [];</script></head>
                <body><span id='v0.0.0'></span>{1}</body></html>
                """
                ).format(activeBCVsettings,
                         content,
                         "{",
                         "}",
                         fontSize,
                         fontFamily,
                         config.fontChinese,
                         config.theme,
                         self.getHighlightCss(),
                         bibleCss,
                         #config.widgetBackgroundColor,
                         #config.widgetForegroundColor,
                         self.getMaterialCss(),
                         self.getMaterialMutualHighlightScript(),
                         )
        return html

    def getMaterialMutualHighlightScript(self):
        return """
<script>
function hl1(id, cl, sn) {0}
    if (cl != '') {0}
        w3.addStyle('.c'+cl,'background-color','{2}');
        w3.addStyle('.c'+cl,'color','{3}');
    {1}
    if (sn != '') {0}
        w3.addStyle('.G'+sn,'background-color','{2}');
        w3.addStyle('.G'+sn,'color','{3}');
    {1}
    if (id != '') {0}
        var focalElement = document.getElementById('w'+id);
        if (focalElement != null) {0}
            document.getElementById('w'+id).style.background='{5}';
            document.getElementById('w'+id).style.color='{4}';
        {1}
    {1}
    if ((id != '') && (id.startsWith("l") != true)) {0}
        document.title = "_instantWord:::"+activeB+":::"+id;
    {1}
{1}

function hl0(id, cl, sn) {0}
    if (cl != '') {0}
        w3.addStyle('.c'+cl,'background-color','');
        w3.addStyle('.c'+cl,'color','');
    {1}
    if (sn != '') {0}
        w3.addStyle('.G'+sn,'background-color','');
        w3.addStyle('.G'+sn,'color','');
    {1}
    if (id != '') {0}
        var focalElement = document.getElementById('w'+id);
        if (focalElement != null) {0}
            document.getElementById('w'+id).style.background='';
            document.getElementById('w'+id).style.color='';
        {1}
    {1}
{1}

</script>
        """.format(
            "{",
            "}",
            config.widgetBackgroundColorHover,
            config.widgetForegroundColorHover,
            config.widgetBackgroundColorPressed, 
            config.widgetForegroundColorPressed, 
        )

    def getMaterialCss(self):
        textColor = config.darkThemeTextColor if config.theme in ("dark", "night") else config.lightThemeTextColor
        activeColor = config.darkThemeActiveVerseColor if config.theme in ("dark", "night") else config.lightThemeActiveVerseColor
        return "" if not config.menuLayout == "material" else """
<style>
body {0} color: {7}; {1}
.ubaButton {0} background-color: {6}; color: {2}; border: none; padding: 2px 10px; text-align: center; text-decoration: none; display: inline-block; font-size: 17px; margin: 2px 2px; cursor: pointer; {1}
.ubaButton:hover {0} background-color: {4}; color: {5}; {1}
vid, a, a:link, a:visited, ref, entry {0} color: {2}; {1}
aa, bb, hp, vb, red, red ref, red entry {0} color: {3}; {1}
z {0} background-color: {9}; color: {8}; {1}
vid:hover, a:hover, a:active, ref:hover, entry:hover, ch:hover, text:hover, addon:hover {0} background-color: {4}; color: {5}; {1}
::selection {0} background: {5}; color: {4}; {1}
::-moz-selection {0} background: {5}; color: {4}; {1}
</style>
        """.format(
            "{", 
            "}", 
            config.widgetForegroundColor, 
            activeColor, 
            config.widgetBackgroundColorHover, 
            config.widgetForegroundColorHover, 
            config.widgetBackgroundColor,
            textColor,
            config.widgetBackgroundColorPressed, 
            config.widgetForegroundColorPressed, 
            )

    # add a history record
    def addHistoryRecord(self, view, textCommand, tab="0"):
        self.crossPlatform.addHistoryRecord(view, textCommand, tab)

    # switch between landscape / portrait mode
    def setFullIconSize(self, full):
        config.toolBarIconFullSize = full
        self.setupMenuLayout(config.menuLayout)

    def switchIconSize(self):
        config.toolBarIconFullSize = not config.toolBarIconFullSize
        self.setupMenuLayout(config.menuLayout)

    # switch between landscape / portrait mode
    def switchLandscapeMode(self):
        if config.landscapeMode:
            config.landscapeMode = False
        else:
            config.landscapeMode = True
        self.centralWidget.switchLandscapeMode()
        self.resizeCentral()

    def setLandscapeMode(self, mode):
        config.landscapeMode = TextUtil.strtobool(mode)
        self.centralWidget.switchLandscapeMode()
        self.resizeCentral()

    def resizeCentral(self):
        self.centralWidget.resizeMe()

    # Actions - hide / show / resize study & lightning views
    def cycleInstant(self):
        config.instantMode += 1
        if config.instantMode == len(CentralWidget.instantRatio):
            config.instantMode = 0
        self.resizeCentral()

    def setInstantSize(self, size):
        config.instantMode = int(size)
        self.resizeCentral()

    def pause(self, seconds=0):
        seconds = int(seconds)
        config.pauseMode = True
        start = DateUtil.epoch()
        while config.pauseMode:
            QApplication.processEvents()
            elapsedSecs = DateUtil.epoch() - start
            if (seconds > 0 and elapsedSecs > seconds) or config.quitMacro:
                config.pauseMode = False

    def parallel(self):
        if config.parallelMode >= 4:
            config.parallelMode = 0
        else:
            config.parallelMode += 1
        self.resizeCentral()

    def setParallelSize(self, mode):
        config.parallelMode = int(mode)
        self.resizeCentral()

    # Calendar
    def showCalendar(self):
        self.calendar = Calendar(self)
        self.calendar.show()

    # Open Morphology Search Dialog by double clicking of Hebrew / Greek words on marvel bibles
    def openMorphDialog(self, items):
        self.morphDialog = MorphDialog(self, items)
        # self.morphDialog.setModal(True)
        self.morphDialog.show()

    def openInterfaceLanguageDialog(self):
        programInterfaceLanguage = Languages.decode(config.displayLanguage)
        items = LanguageUtil.getNamesSupportedLanguages()
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        config.thisTranslation["menu1_setMyLanguage"], items, items.index(programInterfaceLanguage),
                                        False)
        if ok and item:
            config.displayLanguage = Languages.code[item]
            self.setTranslation()
            self.setupMenuLayout(config.menuLayout)
            self.reloadControlPanel(False)

    def changeInterfaceLanguage(self, language):
        config.displayLanguage = Languages.code[language]
        self.setTranslation()
        self.setupMenuLayout(config.menuLayout)
        self.reloadControlPanel(False)

    # Set my language (config.userLanguage)
    # This one is different from the language of program interface
    # userLanguage is used when user translate a selected word with right-click menu or use TRANSLATE::: command
    # For example, a user can use English menu but he can translate a word into Chinese.
    def openTranslationLanguageDialog(self):
        # Use IBM Watson service to translate text
        translator = Translator()
        if translator.language_translator is not None:
            if not config.userLanguage or not config.userLanguage in Translator.toLanguageNames:
                userLanguage = "English"
            else:
                userLanguage = config.userLanguage
            item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["menu1_setMyLanguage"], Translator.toLanguageNames, Translator.toLanguageNames.index(userLanguage), False)
            if ok and item:
                config.userLanguage = item
        else:
            self.displayMessage(config.thisTranslation["ibmWatsonNotEnalbed"])
            self.openWebsite("https://github.com/eliranwong/UniqueBible/wiki/IBM-Watson-Language-Translator")

    # Set verse number single-click action (config.verseNoSingleClickAction)
    def selectSingleClickActionDialog(self):
        values = ("_noAction", "_cp0", "_cp1", "_cp2", "_cp3", "_cp4", "STUDY", "COMPARE", "CROSSREFERENCE", "TSKE", "TRANSLATION", "DISCOURSE", "WORDS", "COMBO", "INDEX", "COMMENTARY", "STUDY", "_menu")
        features = ["noAction", "cp0", "cp1", "cp2", "cp3", "cp4", "openInStudyWindow", "menu4_compareAll", "menu4_crossRef", "menu4_tske", "menu4_traslations", "menu4_discourse", "menu4_words", "menu4_tdw", "menu4_indexes", "menu4_commentary", "menu_syncStudyWindowBible", "classicMenu"]
        items = [config.thisTranslation[feature] for feature in features]
        itemsDict = dict(zip(items, values))
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["assignSingleClick"], items, values.index(config.verseNoSingleClickAction), False)
        if ok and item:
            config.verseNoSingleClickAction = itemsDict[item]
    
    def singleClickActionSelected(self, item):
        config.verseNoSingleClickAction = item
        if config.menuLayout == "material":
            self.singleClickActionSelectedSubmenu()

    # Set verse number double-click action (config.verseNoDoubleClickAction)
    def selectDoubleClickActionDialog(self):
        values = ("_noAction", "_cp0", "_cp1", "_cp2", "_cp3", "_cp4", "STUDY", "COMPARE", "CROSSREFERENCE", "TSKE", "TRANSLATION", "DISCOURSE", "WORDS", "COMBO", "INDEX", "COMMENTARY", "_menu")
        features = ["noAction", "cp0", "cp1", "cp2", "cp3", "cp4", "openInStudyWindow", "menu4_compareAll", "menu4_crossRef", "menu4_tske", "menu4_traslations", "menu4_discourse", "menu4_words", "menu4_tdw", "menu4_indexes", "menu4_commentary", "classicMenu"]
        items = [config.thisTranslation[feature] for feature in features]
        itemsDict = dict(zip(items, values))
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["assignDoubleClick"], items, values.index(config.verseNoDoubleClickAction), False)
        if ok and item:
            config.verseNoDoubleClickAction = itemsDict[item]

    def doubleClickActionSelected(self, item):
        config.verseNoDoubleClickAction = item
        if config.menuLayout == "material":
            self.doubleClickActionSelectedSubmenu()

    # Set reference button single-click action (config.refButtonClickAction)
    def selectRefButtonSingleClickActionDialog(self):
        if config.menuLayout == "material":
            values = ("master", "mini")
            features = ["controlPanel", "menu1_miniControl"]
        else:
            values = ("master", "mini", "direct")
            features = ["controlPanel", "menu1_miniControl", "direct"]
        items = [config.thisTranslation[feature] for feature in features]
        itemsDict = dict(zip(items, values))
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["controlPreference"], items, values.index(config.refButtonClickAction), False)
        if ok and item:
            config.refButtonClickAction = itemsDict[item]
            self.setupMenuLayout(config.menuLayout)

    def selectRefButtonSingleClickAction(self, option):
        config.refButtonClickAction = option
        self.setupMenuLayout(config.menuLayout)

    # Set default Strongs Greek lexicon (config.defaultLexiconStrongG)
    def openSelectDefaultStrongsGreekLexiconDialog(self):
        items = LexiconData().lexiconList
        item, ok = QInputDialog.getItem(self, config.thisTranslation["menu1_selectDefaultLexicon"],
                                        config.thisTranslation["menu1_setDefaultStrongsGreekLexicon"], items,
                                        items.index(config.defaultLexiconStrongG), False)
        if ok and item:
            config.defaultLexiconStrongG = item

    def defaultStrongsGreekLexiconSelected(self, item):
        config.defaultLexiconStrongG = item
        if config.menuLayout == "material":
            self.defaultStrongsGreekLexiconSelectedSubmenu()

    # Set default Strongs Hebrew lexicon (config.defaultLexiconStrongH)
    def openSelectDefaultStrongsHebrewLexiconDialog(self):
        items = LexiconData().lexiconList
        item, ok = QInputDialog.getItem(self, config.thisTranslation["menu1_selectDefaultLexicon"],
                                        config.thisTranslation["menu1_setDefaultStrongsHebrewLexicon"], items,
                                        items.index(config.defaultLexiconStrongH), False)
        if ok and item:
            config.defaultLexiconStrongH = item

    def defaultStrongsHebrewLexiconSelected(self, item):
        config.defaultLexiconStrongH = item
        if config.menuLayout == "material":
            self.defaultStrongsHebrewLexiconSelectedSubmenu()

    # Set Favourite Bible Version
    def openFavouriteMarvelBibleDialog(self):
        items = ["MOB", "MIB", "MTB", "MPB", "MAB"]
        item, ok = QInputDialog.getItem(self, config.thisTranslation["selectFavouriteHebrewGreekBible"],
                                        config.thisTranslation["selectFavouriteHebrewGreekBible"], items,
                                        items.index(config.favouriteOriginalBible), False)
        if ok and item:
            config.favouriteOriginalBible = item
        self.reloadResources()
        self.reloadCurrentRecord(True)

    def openFavouriteMarvelBibleDialog2(self):
        items = ["MOB", "MIB", "MTB", "MPB", "MAB"]
        item, ok = QInputDialog.getItem(self, config.thisTranslation["selectFavouriteHebrewGreekBible2"],
                                        config.thisTranslation["selectFavouriteHebrewGreekBible2"], items,
                                        items.index(config.favouriteOriginalBible2), False)
        if ok and item:
            config.favouriteOriginalBible2 = item
        self.reloadResources()
        self.reloadCurrentRecord(True)

    def openFavouriteMarvelBibleSelected1(self, item):
        config.favouriteOriginalBible = item
        self.reloadResources()
        self.reloadCurrentRecord(True)

    def openFavouriteMarvelBibleSelected2(self, item):
        config.favouriteOriginalBible = item
        self.reloadResources()
        self.reloadCurrentRecord(True)

    def openFavouriteBibleDialog(self):
        items = BiblesSqlite().getBibleList()
        item, ok = QInputDialog.getItem(self, config.thisTranslation["menu1_setMyFavouriteBible"],
                                        config.thisTranslation["menu1_setMyFavouriteBible"], items,
                                        items.index(config.favouriteBible), False)
        if ok and item:
            config.favouriteBible = item
        self.reloadResources()
        self.reloadCurrentRecord(True)

    def openFavouriteBibleSelected1(self, item):
        config.favouriteBible = item
        self.reloadResources()
        self.reloadCurrentRecord(True)

    def openFavouriteBibleSelected2(self, item):
        config.favouriteBible2 = item
        self.reloadResources()
        self.reloadCurrentRecord(True)

    def openFavouriteBibleSelected3(self, item):
        config.favouriteBible3 = item
        self.reloadResources()
        self.reloadCurrentRecord(True)

    def openFavouriteBibleDialog2(self):
        items = BiblesSqlite().getBibleList()
        item, ok = QInputDialog.getItem(self, config.thisTranslation["menu1_setMyFavouriteBible2"],
                                        config.thisTranslation["menu1_setMyFavouriteBible2"], items,
                                        items.index(config.favouriteBible2), False)
        if ok and item:
            config.favouriteBible2 = item
        self.reloadResources()
        self.reloadCurrentRecord(True)

    def openFavouriteBibleDialog3(self):
        items = BiblesSqlite().getBibleList()
        item, ok = QInputDialog.getItem(self, config.thisTranslation["menu1_setMyFavouriteBible3"],
                                        config.thisTranslation["menu1_setMyFavouriteBible3"], items,
                                        items.index(config.favouriteBible3), False)
        if ok and item:
            config.favouriteBible3 = item
        self.reloadResources()
        self.reloadCurrentRecord(True)

    # Set text-to-speech default language
    def getTtsLanguages(self):
        return self.crossPlatform.getTtsLanguages()

    def setDefaultTtsLanguage(self, language):
        config.ttsDefaultLangauge = language
        self.mainView.currentWidget().updateDefaultTtsVoice()
        self.studyView.currentWidget().updateDefaultTtsVoice()
        if config.menuLayout == "material":
            self.setupMenuLayout("material")
            self.instantTtsButton.setToolTip("{0} - {1}".format(config.thisTranslation["context1_speak"], config.ttsDefaultLangauge))

    def setDefaultTtsLanguage2(self, language):
        config.ttsDefaultLangauge2 = language
        if config.menuLayout == "material":
            self.setupMenuLayout("material")
            if hasattr(config, "instantTtsButton2"):
                self.instantTtsButton2.setToolTip("{0} - {1}".format(config.thisTranslation["context1_speak"], config.ttsDefaultLangauge))
            else:
                self.handleRestart()

    def setDefaultTtsLanguage3(self, language):
        config.ttsDefaultLangauge3 = language
        if config.menuLayout == "material":
            self.setupMenuLayout("material")
            if hasattr(config, "instantTtsButton3"):
                self.instantTtsButton3.setToolTip("{0} - {1}".format(config.thisTranslation["context1_speak"], config.ttsDefaultLangauge))
            else:
                self.handleRestart()

    # handling restart
    def handleRestart(self):
        if hasattr(config, "cli") and self.warningRestart():
            self.restartApp()
        else:
            self.displayMessage(config.thisTranslation["message_restart"])

    def warningRestart(self):
        msgBox = QMessageBox(QMessageBox.Warning,
                             config.thisTranslation["attention"],
                             "Restart Unique Bible App to make the changes effective?",
                             QMessageBox.NoButton, self)
        msgBox.addButton("Later", QMessageBox.RejectRole)
        msgBox.addButton("&Now", QMessageBox.AcceptRole)
        answer = msgBox.exec_()
        if answer:
        #if answer == 1 or answer == QMessageBox.AcceptRole:
            # Cancel
            return True
        else:
            # Continue
            return False

    def setDefaultTtsLanguageDialog(self):
        languages = self.getTtsLanguages()
        languageCodes = list(languages.keys())
        items = [languages[code][1] for code in languageCodes]
        # Check if selected tts engine has the language user specify.
        if not (config.ttsDefaultLangauge in languageCodes):
            config.ttsDefaultLangauge = "en-GB" if config.isGoogleCloudTTSAvailable else "en"
        # Initial index
        initialIndex = languageCodes.index(config.ttsDefaultLangauge)
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        config.thisTranslation["setDefaultTtsLanguage"], items,
                                        initialIndex, False)
        if ok and item:
            config.ttsDefaultLangauge = languageCodes[items.index(item)]

    # Set bible book abbreviations
    def setBibleAbbreviations(self):
        items = BibleBooks().booksMap.keys()
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        config.thisTranslation["menu1_setAbbreviations"], items,
                                        items.index(config.standardAbbreviation), False)
        if ok and item:
            config.standardAbbreviation = item
            self.reloadCurrentRecord(True)

    def setBibleAbbreviationsSelected(self, option):
        config.standardAbbreviation = option
        self.reloadCurrentRecord(True)
        if config.menuLayout == "material":
            self.setBibleAbbreviationsSelectedSubmenu()

    def setVlcSpeed(self, option):
        config.vlcSpeed = float(option)
        if config.menuLayout == "material":
            self.setSubMenuVlcSpeed()

    def setWorkspaceSavingOrder(self, option):
        savingOrder = {
            "Creation Order": 0,
            "Stacking Order": 1,
            "Activation History Order": 2,
        }
        config.workspaceSavingOrder = savingOrder[option]
        if config.menuLayout == "material":
            self.setWorkspaceSavingOrderSubmenu()

    def setMarkdownExportHeadingStyle(self, option):
        config.markdownifyHeadingStyle = option
        if config.menuLayout == "material":
            self.setMarkdownExportHeadingStyleSubmenu()

    # set default font
    def setDefaultFont(self):
        ok, font = QFontDialog.getFont(QFont(config.font, config.fontSize), self)
        if ok:
            config.font, fontSize, *_ = font.key().split(",")
            config.fontSize = int(fontSize)
            self.defaultFontButton.setText("{0} {1}".format(config.font, config.fontSize))
            self.reloadCurrentRecord(True)

    # set Chinese font
    def setChineseFont(self):
        ok, font = QFontDialog.getFont(QFont(config.fontChinese, config.fontSize), self)
        if ok:
            config.fontChinese, *_ = font.key().split(",")
            self.reloadCurrentRecord(True)

    def mainPageScrollPageDown(self):
        js = "window.scrollTo(0, window.scrollY + window.innerHeight * .95);"
        self.mainPage.runJavaScript(js)

    def mainPageScrollPageUp(self):
        js = "window.scrollTo(0, window.scrollY - window.innerHeight * .95);"
        self.mainPage.runJavaScript(js)

    def studyPageScrollPageDown(self):
        js = "window.scrollTo(0, window.scrollY + window.innerHeight * .95);"
        self.studyPage.runJavaScript(js)

    def studyPageScrollPageUp(self):
        js = "window.scrollTo(0, window.scrollY - window.innerHeight * .95);"
        self.studyPage.runJavaScript(js)

    def mainPageScrollToTop(self):
        js = "document.body.scrollTop = document.documentElement.scrollTop = 0;"
        self.mainPage.runJavaScript(js)

    def studyPageScrollToTop(self):
        js = "document.body.scrollTop = document.documentElement.scrollTop = 0;"
        self.studyPage.runJavaScript(js)

    def setStartupMacro(self):
        if not os.path.isdir(MacroParser.macros_dir):
            os.mkdir(MacroParser.macros_dir)
        files = [""]
        for file in os.listdir(MacroParser.macros_dir):
            if os.path.isfile(os.path.join(MacroParser.macros_dir, file)) and ".ubam" in file:
                files.append(file.replace(".ubam", ""))
        index = 0
        if config.startupMacro in files:
            index = files.index(config.startupMacro)
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                                        config.thisTranslation["message_select_macro"], files, index, False)
        if ok:
            config.startupMacro = item

    def macroSaveHighlights(self):
        verses = Highlight().getHighlightedVerses()
        if len(verses) == 0:
            self.displayMessage("No verses are highlighted")
        else:
            filename, ok = self.openSaveMacroDialog(config.thisTranslation["message_macro_save_highlights"])
            if ok:
                file = os.path.join(MacroParser.macros_dir, filename)
                outfile = open(file, "w")
                parser = BibleVerseParser(config.standardAbbreviation)
                for (b, c, v, code) in verses:
                    reference = parser.bcvToVerseReference(b, c, v)
                    outfile.write("_HIGHLIGHT:::{0}:::{1}\n".format(code, reference))
                outfile.write(". displayMessage Highlighted verses loaded\n")
                outfile.close()
                self.displayMessage("Highlighted verses saved to {0}".format(filename))

    def macroSaveCommand(self):
        filename, ok = self.openSaveMacroDialog(config.thisTranslation["message_macro_save_command"])
        if ok:
            file = os.path.join(MacroParser.macros_dir, filename)
            outfile = open(file, "w")
            outfile.write(self.textCommandLineEdit.text() + "\n")
            outfile.close()
            self.reloadResources()
            self.displayMessage("Command saved to {0}".format(filename))

    def macroSaveSettings(self):
        filename, ok = self.openSaveMacroDialog(config.thisTranslation["message_macro_save_settings"])
        if ok:
            file = os.path.join(MacroParser.macros_dir, filename)
            outfile = open(file, "w")
            outfile.write("config.defaultLexiconStrongH = '{0}'{1}".format(config.defaultLexiconStrongH, "\n"))
            outfile.write("config.defaultLexiconStrongG = '{0}'{1}".format(config.defaultLexiconStrongG, "\n"))
            outfile.write("config.displayLanguage = '{0}'{1}".format(config.displayLanguage, "\n"))
            outfile.write("config.enablePlugins = {0}{1}".format(config.enablePlugins, "\n"))
            outfile.write("config.favouriteBible = '{0}'{1}".format(config.favouriteBible, "\n"))
            outfile.write("config.forceGenerateHtml = {0}{1}".format(config.forceGenerateHtml, "\n"))
            outfile.write("config.lexicon = '{0}'{1}".format(config.lexicon, "\n"))
            outfile.write("config.menuLayout = '{0}'{1}".format(config.menuLayout, "\n"))
            outfile.write("config.menuShortcuts = '{0}'{1}".format(config.menuShortcuts, "\n"))
            outfile.write("config.numberOfTab = {0}{1}".format(config.numberOfTab, "\n"))
            outfile.write("config.qtMaterial = {0}{1}".format(config.qtMaterial, "\n"))
            outfile.write("config.theme = '{0}'{1}".format(config.theme, "\n"))
            outfile.write("config.useLiteVerseParsing = {0}{1}".format(config.useLiteVerseParsing, "\n"))
            outfile.write("config.useWebbrowser = {0}{1}".format(config.useWebbrowser, "\n"))
            outfile.write("config.verseNoSingleClickAction = '{0}'{1}".format(config.verseNoSingleClickAction, "\n"))
            outfile.write("config.verseNoDoubleClickAction = '{0}'{1}".format(config.verseNoDoubleClickAction, "\n"))
            outfile.write("config.windowStyle = '{0}'{1}".format(config.windowStyle, "\n"))
            outfile.write(". displayMessage Restart for settings to take effect\n")
            outfile.close()
            self.reloadResources()
            self.displayMessage("Command saved to {0}".format(filename))

    def macroGenerateDownloadMissingFiles(self):
        filename, ok = self.openSaveMacroDialog(config.thisTranslation["message_macro_save_command"])
        if ok:
            bibleList = [os.path.basename(file) for file in glob.glob(r"{0}/bibles/*.bible".format(config.marvelData))]
            commentaryList = [os.path.basename(file) for file in glob.glob(r"{0}/commentaries/*.commentary".format(config.marvelData))]
            bookList = [os.path.basename(file) for file in glob.glob(r"{0}/books/*.book".format(config.marvelData))]
            pdfList = [os.path.basename(file) for file in glob.glob(r"{0}/pdf/*.pdf".format(config.marvelData))]
            epubList = [os.path.basename(file) for file in glob.glob(r"{0}/epub/*.epub".format(config.marvelData))]

            file = os.path.join(MacroParser.macros_dir, filename)
            outfile = open(file, "w")
            for key in DatafileLocation.marvelBibles.keys():
                if (key+".bible") not in bibleList:
                    outfile.write("DOWNLOAD:::MarvelBible:::{0}\n".format(key))
            for key in DatafileLocation.marvelCommentaries.keys():
                value = DatafileLocation.marvelCommentaries[key]
                if (value[0][2]) not in commentaryList:
                    outfile.write("DOWNLOAD:::MarvelCommentary:::{0}\n".format(key))
            if ("Pygithub" in config.enabled):
                from uniquebible.util.GithubUtil import GithubUtil

                for file in GithubUtil(GitHubRepoInfo.bible[0]).getRepoData():
                    if file not in bibleList:
                        outfile.write("DOWNLOAD:::GitHubBible:::{0}\n".format(file.replace(".bible", "")))
                for file in GithubUtil(GitHubRepoInfo.commentaries[0]).getRepoData():
                    if file not in commentaryList:
                        outfile.write("DOWNLOAD:::GitHubCommentary:::{0}\n".format(file.replace(".commentary", "")))
                for file in GithubUtil(GitHubRepoInfo.books[0]).getRepoData():
                    if file not in bookList:
                        outfile.write("DOWNLOAD:::GitHubBook:::{0}\n".format(file.replace(".book", "")))
                for file in GithubUtil(GitHubRepoInfo.maps[0]).getRepoData():
                    if file not in bookList:
                        outfile.write("DOWNLOAD:::GitHubMap:::{0}\n".format(file.replace(".book", "")))
                for file in GithubUtil(GitHubRepoInfo.pdf[0]).getRepoData():
                    if file not in pdfList:
                        outfile.write("DOWNLOAD:::GitHubPdf:::{0}\n".format(file.replace(".pdf", "")))
                for file in GithubUtil(GitHubRepoInfo.epub[0]).getRepoData():
                    if file not in epubList:
                        outfile.write("DOWNLOAD:::GitHubEpub:::{0}\n".format(file.replace(".epub", "")))
            outfile.close()
            self.reloadResources()
            self.displayMessage("Command saved to {0}".format(filename))

    def macroGenerateDownloadExistingFiles(self):
        filename, ok = self.openSaveMacroDialog(config.thisTranslation["message_macro_save_command"])
        if ok:
            bibleList = [os.path.basename(file) for file in glob.glob(r"{0}/bibles/*.bible".format(config.marvelData))]
            commentaryList = [os.path.basename(file) for file in glob.glob(r"{0}/commentaries/*.commentary".format(config.marvelData))]
            bookList = [os.path.basename(file) for file in glob.glob(r"{0}/books/*.book".format(config.marvelData))]
            pdfList = [os.path.basename(file) for file in glob.glob(r"{0}/pdf/*.pdf".format(config.marvelData))]
            epubList = [os.path.basename(file) for file in glob.glob(r"{0}/epub/*.epub".format(config.marvelData))]

            bibles = [value[0][2] for value in DatafileLocation.marvelBibles.values()]
            commentaries = [value[0][2] for value in DatafileLocation.marvelCommentaries.values()]

            file = os.path.join(MacroParser.macros_dir, filename)
            outfile = open(file, "w")
            for file in bibleList:
                if file in bibles:
                    file = file.replace(".bible", "")
                    outfile.write("DOWNLOAD:::MarvelBible:::{0}\n".format(file))
            for file in commentaryList:
                if file in commentaries:
                    file = file.replace(".commentary", "")
                    outfile.write("DOWNLOAD:::MarvelCommentary:::{0}\n".format(file))

            if ("Pygithub" in config.enabled):
                from uniquebible.util.GithubUtil import GithubUtil
                for file in GithubUtil(GitHubRepoInfo.bible[0]).getRepoData():
                    if file in bibleList:
                        outfile.write("DOWNLOAD:::GitHubBible:::{0}\n".format(file.replace(".bible", "")))
                for file in GithubUtil(GitHubRepoInfo.commentaries[0]).getRepoData():
                    if file in commentaryList:
                        outfile.write("DOWNLOAD:::GitHubCommentary:::{0}\n".format(file.replace(".commentary", "")))
                for file in GithubUtil(GitHubRepoInfo.books[0]).getRepoData():
                    if file in bookList:
                        outfile.write("DOWNLOAD:::GitHubBook:::{0}\n".format(file.replace(".book", "")))
                for file in GithubUtil(GitHubRepoInfo.maps[0]).getRepoData():
                    if file in bookList:
                        outfile.write("DOWNLOAD:::GitHubMap:::{0}\n".format(file.replace(".book", "")))
                for file in GithubUtil(GitHubRepoInfo.pdf[0]).getRepoData():
                    if file in pdfList:
                        outfile.write("DOWNLOAD:::GitHubPdf:::{0}\n".format(file.replace(".pdf", "")))
                for file in GithubUtil(GitHubRepoInfo.epub[0]).getRepoData():
                    if file in epubList:
                        outfile.write("DOWNLOAD:::GitHubEpub:::{0}\n".format(file.replace(".epub", "")))
            outfile.close()
            self.reloadResources()
            self.displayMessage("Command saved to {0}".format(filename))

    def openSaveMacroDialog(self, message):
        filename, ok = QInputDialog.getText(self, "UniqueBible.app", message, QLineEdit.Normal, "")
        if ok and not filename == "":
            if not ".ubam" in filename:
                filename += ".ubam"
            file = os.path.join(MacroParser.macros_dir, filename)
            if os.path.isfile(file):
                reply = QMessageBox.question(self, "File exists",
                                             "File currently exists.  Do you want to overwrite it?",
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    return filename, True
                else:
                    return "", False
            else:
                return filename, True
        else:
            return "", False

    def loadRunMacrosMenu(self, run_macro_menu):
        if config.enableMacros:
            count = 1
            macros_dir = MacroParser.macros_dir
            if not os.path.isdir(macros_dir):
                os.mkdir(macros_dir)
            for file in os.listdir(macros_dir):
                if os.path.isfile(os.path.join(macros_dir, file)) and ".ubam" in file:
                    action = QAction(file.replace(".ubam", ""), self, triggered=partial(self.runMacro, file))
                    if count < 10:
                        if sc.loadRunMacro is not None and "Ctrl" in sc.loadRunMacro:
                            action.setShortcuts([sc.loadRunMacro + ", " + str(count)])
                        run_macro_menu.addAction(action)
                        count += 1

    def runMacro(self, file="", extra=""):
        if config.enableMacros and len(file) > 0:
            if not ".ubam" in file:
                file += ".ubam"
            MacroParser(self).parse(file)

    def addMenuPluginButton(self, plugin, feature, icon, toolbar, translation=True):
        if self.isMenuPlugin(plugin) and not plugin in config.excludeMenuPlugins:
            self.addMaterialIconButton(feature, icon, partial(self.runPlugin, plugin), toolbar, translation=translation)

    def isMenuPlugin(self, plugin):
        return os.path.isfile(os.path.join(config.packageDir, "plugins", "menu", "{0}.py".format(plugin))) or os.path.isfile(os.path.join(config.ubaUserDir, "plugins", "menu", "{0}.py".format(plugin)))

    def runPlugin(self, fileName, _=None):
        self.crossPlatform.runPlugin(fileName)

    def execPythonFile(self, script):
        self.crossPlatform.execPythonFile(script)

    def showGistWindow(self):
        gw = GistWindow()
        if gw.exec():
            config.gistToken = gw.gistTokenInput.text()
        self.reloadCurrentRecord()

    def showWatsonCredentialWindow(self):
        window = WatsonCredentialWindow()
        if window.exec():
            config.myIBMWatsonApikey, config.myIBMWatsonUrl, config.myIBMWatsonVersion = window.inputApiKey.text(), window.inputURL.text(), window.inputVersion.text()

    def showAddLanguageItemWindow(self):
        window = LanguageItemWindow(config.thisTranslation["addLanguageFiles"])
        if window.exec() and window.key.text():
            LanguageUtil.addLanguageStringToAllFiles(window.key.text(), window.entry.text())

    def showUpdateLanguageItemWindow(self):
        window = LanguageItemWindow(config.thisTranslation["updateLanguageFiles"])
        if window.exec() and window.key.text():
            LanguageUtil.updateLanguageStringToAllFiles(window.key.text(), window.entry.text())

    def pycharm(self):
        stdout, *_  = subprocess.Popen("uname -m", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        machine = stdout.decode("utf-8")
        if machine == "aarch64\n":
            self.webtopAurApp("pycharm", "pycharm-community-jre-aarch64", "/config/UniqueBible/")
        else:
            self.webtopApp("pycharm", "pycharm-community-edition", "/config/UniqueBible/")

    def webtopApp(self, app, pkg="", arg=""):
        isInstalled = WebtopUtil.isPackageInstalled(app)
        if not isInstalled:
            self.displayMessage("Installing '{0}' ...".format(pkg if pkg else app))
            WebtopUtil.installPackage(pkg if pkg else app)
        WebtopUtil.run("{0} {1}".format(app, arg) if arg else app)

    def webtopAurApp(self, app, pkg="", arg=""):
        isInstalled = WebtopUtil.isPackageInstalled(app)
        if not isInstalled:
            self.displayMessage("Installing '{0}' ...".format(pkg if pkg else app))
            WebtopUtil.installAurPackage(pkg if pkg else app)
        WebtopUtil.run("{0} {1}".format(app, arg) if arg else app)

    def addStandardTextButton(self, toolTip, action, toolbar, button=None, translation=True):
        textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"
        if button is None:
            button = QPushButton()
        button.setToolTip(config.thisTranslation[toolTip] if translation else toolTip)
        if not config.menuLayout == "material":
            button.setStyleSheet(textButtonStyle)
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(action)
        toolbar.addWidget(button)

    def addStandardIconButton(self, toolTip, icon, action, toolbar, button=None, translation=True):
        if button is None:
            button = QPushButton()
        if config.qtMaterial and config.qtMaterialTheme:
            #button.setFixedSize(config.iconButtonWidth, config.iconButtonWidth)
            button.setFixedWidth(config.iconButtonWidth)
            #button.setFixedHeight(config.iconButtonWidth)
        elif platform.system() == "Darwin" and not config.windowStyle == "Fusion":
            button.setFixedWidth(40)
        button.setToolTip(config.thisTranslation[toolTip] if translation else toolTip)
        buttonIconFile = os.path.join("htmlResources", icon)
        button.setIcon(QIcon(buttonIconFile))
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.clicked.connect(action)
        toolbar.addWidget(button)

    def getIconPushButton(self, iconFilePath):
        button = QPushButton()
        qIcon = self.getQIcon(iconFilePath)
        if config.menuLayout == "material":
            button.setStyleSheet(qIcon)
        else:
            button.setIcon(qIcon)
        #if config.menuLayout == "material":
        #    button.setStyleSheet(config.buttonStyle)
        return button

    def getQIcon(self, iconFilePath):
        iconFilePath = os.path.join("htmlResources", *iconFilePath.split("/"))
        if not config.menuLayout == "material" or config.maskMaterialIconBackground:
            qIcon = QIcon(iconFilePath)
        else:
            qIcon = self.getMaskedQIcon(iconFilePath, config.maskMaterialIconColor, config.maskMaterialIconBackground)
        return qIcon

    def getMaskedQIcon(self, iconFile, color=config.maskMaterialIconColor, maskMaterialIconBackground=config.maskMaterialIconBackground, toolButton=False):
        for foregroundColor in (config.widgetForegroundColor, config.widgetForegroundColorHover, config.widgetForegroundColorPressed):
            self.savePixmapIcon(iconFile, foregroundColor)
        if color:
            if toolButton:
                pixmap = QPixmap(iconFile)
                if maskMaterialIconBackground:
                    # To change transparent to gray
                    # The following line has the same result as mask = pixmap.createMaskFromColor(QColor(0,0,0,0), Qt.MaskOutColor)
                    mask = pixmap.createMaskFromColor(Qt.transparent, Qt.MaskOutColor)
                    pixmap.fill(QColor(color))
                else:
                    # To change the foreground black color
                    mask = pixmap.createMaskFromColor(QColor('black'), Qt.MaskOutColor)
                    pixmap.fill(QColor(color))
                pixmap.setMask(mask)
                return QIcon(pixmap)
            else:
                return self.getPushButtonIconStyle(iconFile)
        else:
            return QIcon(iconFile)

    def getPushButtonIconStyle(self, icon):
        folder, icon = os.path.split(icon)
        defaultIconFile = "{0}_{1}.png".format(icon[:-4], config.widgetForegroundColor)
        hoveredIconFile = "{0}_{1}.png".format(icon[:-4], config.widgetForegroundColorHover)
        pressedIconFile = "{0}_{1}.png".format(icon[:-4], config.widgetForegroundColorPressed)
        QDir.addSearchPath(defaultIconFile, os.path.join(os.getcwd(), folder))
        # border-image scales image whereas background-image does not.
        return """
                QPushButton {0} image: url({2}:{2}); {1} QPushButton:hover {0} image: url({2}:{3}); {1} QPushButton:pressed {0} image: url({2}:{4}); {1}
                QToolButton {0} border-image: url({2}:{2}); {1} QToolButton:hover {0} border-image: url({2}:{3}) center no-repeat; {1} QToolButton:pressed {0} border-image: url({2}:{4}) center no-repeat; {1}
            """.format("{", "}", defaultIconFile, hoveredIconFile, pressedIconFile)

    def savePixmapIcon(self, iconFile, foregroundColor):
        pixmap = QPixmap(iconFile)
        mask = pixmap.createMaskFromColor(QColor('black'), Qt.MaskOutColor)
        pixmap.fill(QColor(foregroundColor))
        pixmap.setMask(mask)
        pixmapIconFile = "{0}_{1}.png".format(iconFile[:-4], foregroundColor)
        if not os.path.isfile(pixmapIconFile):
            pixmap.save(pixmapIconFile)

    def addMaterialIconAction(self, toolTip, icon, action, toolbar, translation=True):
        icon = os.path.join("htmlResources", os.path.join(*icon.split("/")))
        return toolbar.addAction(self.getMaskedQIcon(icon, config.maskMaterialIconColor, config.maskMaterialIconBackground), config.thisTranslation[toolTip] if translation else toolTip, action)

    def addMaterialIconButton(self, toolTip, icon, action, toolbar, button=None, translation=True, toolButton=False):
        if button is None:
            button = QToolButton() if toolButton else QPushButton()
        button.setFixedSize(int(config.iconButtonSize * 4/3), int(config.iconButtonSize * 4/3))
        button.setCursor(QCursor(Qt.PointingHandCursor))
        button.setToolTip(config.thisTranslation[toolTip] if translation else toolTip)
        qIcon = self.getQIcon(icon)
        if config.menuLayout == "material":
            button.setStyleSheet(qIcon)
        else:
            button.setIcon(qIcon)
        if action is not None:
            button.clicked.connect(action)
        toolbar.addWidget(button)
        return button

    def getSyncDisplay(self):
        if config.syncAction:
            return self.getCrossplatformPath("material/notification/sync/materialiconsoutlined/48dp/2x/outline_sync_black_48dp.png") if config.menuLayout == "material" else "sync.png"
        else:
            return self.getCrossplatformPath("material/notification/sync_disabled/materialiconsoutlined/48dp/2x/outline_sync_disabled_black_48dp.png") if config.menuLayout == "material" else "noSync.png"

    def setSyncButton(self):
        qIcon = self.getQIcon(self.getSyncDisplay())
        self.syncButton.setStyleSheet(qIcon)
        self.syncButton.setPopupMode(QToolButton.InstantPopup)
        self.syncButton.setArrowType(Qt.NoArrow)
        self.syncButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.syncButton.setToolTip("{0}: {1}".format(config.thisTranslation["sync"], config.thisTranslation["on"] if config.syncAction else config.thisTranslation["off"]))
        menu = QMenu(self.syncButton)
        def addSyncAction(feature, keyword):
            action = menu.addAction(config.thisTranslation[feature])
            action.triggered.connect(partial(self.syncAction, keyword))
            action.setCheckable(True)
            action.setChecked(True if config.syncAction == keyword else False)
        addSyncAction("none", "")
        menu.addSeparator()
        addSyncAction("studyWindowBible", "STUDY")
        menu.addSeparator()
        features = (
            ("menu_bible_chapter_notes", "OPENCHAPTERNOTE"),
            ("menu_bible_verse_notes", "OPENVERSENOTE"),
        )
        for feature, keyword in features:
            addSyncAction(feature, keyword)
        menu.addSeparator()
        if config.compareOnStudyWindow:
            features = (
                ("parallelVersions", "PARALLEL"),
                ("sideBySideComparison", "SIDEBYSIDE"),
                ("rowByRowComparison", "COMPARE"),
            )
            for feature, keyword in features:
                addSyncAction(feature, keyword)
            menu.addSeparator()
        features = (
            ("html_overview", "OVERVIEW"),
            ("html_chapterIndex", "CHAPTERINDEX"),
            ("html_summary", "SUMMARY"),
        )
        for feature, keyword in features:
            addSyncAction(feature, keyword)
        menu.addSeparator()
        features = (
            ("menu4_commentary", "COMMENTARY"),
            ("menu4_compareAll", "COMPARE"),
            ("contrasts", "DIFFERENCE"),
            ("menu4_crossRef", "CROSSREFERENCE"),
            ("menu4_tske", "TSKE"),
            ("menu4_traslations", "TRANSLATION"),
            ("menu4_discourse", "DISCOURSE"),
            ("menu4_words", "WORDS"),
            ("menu4_tdw", "COMBO"),
            ("menu4_indexes", "INDEX"),
        )
        for feature, keyword in features:
            addSyncAction(feature, keyword)
        self.syncButton.setMenu(menu)

    def syncAction(self, keyword):
        config.syncAction = keyword
        if keyword:
            *_, verseReference = self.verseReference("main")
            self.runTextCommand(f"{config.syncAction}:::{verseReference}", True, "study")
        self.setSyncButton()

    def setMainRefMenu(self):
        bible = Bible(config.mainText)
        # Book menu
        abbreviations = BibleVerseParser(config.parserStandarisation).standardAbbreviation
        standardFullBookName = BibleVerseParser(config.parserStandarisation).standardFullBookName
        self.mainB.setText(abbreviations[str(config.mainB)])
        self.mainB.setToolTip(config.thisTranslation["menu_book"])
        self.mainB.setPopupMode(QToolButton.InstantPopup)
        self.mainB.setArrowType(Qt.NoArrow)
        menu = QMenu(self.mainB)
        subMenu = menu.addMenu(config.thisTranslation["menu_bookNote"])
        action = subMenu.addAction(config.thisTranslation["open"])
        action.triggered.connect(partial(self.openBibleNotes, "book"))
        action = subMenu.addAction(config.thisTranslation["edit"])
        action.triggered.connect(partial(self.editBibleNotes, "book"))
        subMenu = menu.addMenu(config.thisTranslation["menu4_book"])
        features = (
            ("html_introduction", lambda: self.searchBookChapter("Tidwell_The_Bible_Book_by_Book")),
            ("outline", lambda: self.bookAction("OUTLINE")),
            ("html_timelines", lambda: self.searchBookChapter("Timelines")),
            ("context1_dict", lambda: self.searchBookName(True)),
            ("context1_encyclopedia", lambda: self.searchBookName(False)),
        )
        for description, triggered in features:
            action = subMenu.addAction(config.thisTranslation[description])
            action.triggered.connect(triggered)
        action = menu.addAction(config.thisTranslation["bibleChat"])
        action.triggered.connect(partial(self.bibleChat, "book"))
        menu.addSeparator()
        for b in bible.getBookList():
            if str(b) in abbreviations:
                abb = abbreviations[str(b)]
                fullName = standardFullBookName[str(b)]
                action = menu.addAction(f"[{b}] {fullName} ({abb})")
                action.triggered.connect(partial(self.mainRefMenuSelected, (bible, "b", b)))
                action.setCheckable(True)
                action.setChecked(True if b == config.mainB else False)
        self.mainB.setMenu(menu)
        # Chapter menu
        self.mainC.setText(str(config.mainC))
        self.mainC.setToolTip(config.thisTranslation["menu_chapter"])
        self.mainC.setPopupMode(QToolButton.InstantPopup)
        self.mainC.setArrowType(Qt.NoArrow)
        menu = QMenu(self.mainC)
        subMenu = menu.addMenu(config.thisTranslation["menu_chapterNote"])
        action = subMenu.addAction(config.thisTranslation["open"])
        action.triggered.connect(partial(self.openBibleNotes, "chapter"))
        action = subMenu.addAction(config.thisTranslation["edit"])
        action.triggered.connect(partial(self.editBibleNotes, "chapter"))
        subMenu = menu.addMenu(config.thisTranslation["menu4_chapter"])
        features = (
            ("html_overview", lambda: self.chapterAction("OVERVIEW")),
            ("html_chapterIndex", lambda: self.chapterAction("CHAPTERINDEX")),
            ("html_summary", lambda: self.chapterAction("SUMMARY")),
            ("menu4_commentary", lambda: self.chapterAction("COMMENTARY")),
            ("parallelVersions", lambda: self.runCompareAction("PARALLEL")),
            ("sideBySideComparison", lambda: self.runCompareAction("SIDEBYSIDE")),
            ("rowByRowComparison", lambda: self.runCompareAction("COMPARE")),
        )
        for description, triggered in features:
            action = subMenu.addAction(config.thisTranslation[description])
            action.triggered.connect(triggered)
        action = menu.addAction(config.thisTranslation["bibleChat"])
        action.triggered.connect(partial(self.bibleChat, "chapter"))
        menu.addSeparator()
        for c in bible.getChapterList(config.mainB):
            action = menu.addAction(str(c))
            action.triggered.connect(partial(self.mainRefMenuSelected, (bible, "c", c)))
            action.setCheckable(True)
            action.setChecked(True if c == config.mainC else False)
        self.mainC.setMenu(menu)
        # Verse menu
        self.mainV.setText(str(config.mainV))
        self.mainV.setToolTip(config.thisTranslation["menu_verse"])
        self.mainV.setPopupMode(QToolButton.InstantPopup)
        self.mainV.setArrowType(Qt.NoArrow)
        menu = QMenu(self.mainV)
        subMenu = menu.addMenu(config.thisTranslation["menu_verseNote"])
        action = subMenu.addAction(config.thisTranslation["open"])
        action.triggered.connect(partial(self.openBibleNotes, "verse"))
        action = subMenu.addAction(config.thisTranslation["edit"])
        action.triggered.connect(partial(self.editBibleNotes, "verse"))
        subMenu = menu.addMenu(config.thisTranslation["menu4_verse"])
        features = (
            ("menu4_compareAll", lambda: self.runFeature("COMPARE")),
            ("contrasts", lambda: self.runFeature("DIFFERENCE")),
            ("menu4_crossRef", lambda: self.runFeature("CROSSREFERENCE")),
            ("menu4_tske", lambda: self.runFeature("TSKE")),
            ("menu4_traslations", lambda: self.runFeature("TRANSLATION")),
            ("menu4_discourse", lambda: self.runFeature("DISCOURSE")),
            ("menu4_words", lambda: self.runFeature("WORDS")),
            ("menu4_tdw", lambda: self.runFeature("COMBO")),
            ("menu4_indexes", lambda: self.runFeature("INDEX")),
            ("menu4_commentary", lambda: self.runFeature("COMMENTARY")),
        )
        for description, triggered in features:
            action = subMenu.addAction(config.thisTranslation[description])
            action.triggered.connect(triggered)
        action = subMenu.addAction(config.thisTranslation["interlinearData"])
        action.triggered.connect(partial(self.runPlugin, "Interlinear Data"))
        action = menu.addAction(config.thisTranslation["bibleChat"])
        action.triggered.connect(partial(self.bibleChat, "verse"))
        menu.addSeparator()
        for v in bible.getVerseList(config.mainB, config.mainC):
            action = menu.addAction(str(v))
            action.triggered.connect(partial(self.mainRefMenuSelected, (bible, "v", v)))
            action.setCheckable(True)
            action.setChecked(True if v == config.mainV else False)
        self.mainV.setMenu(menu)

    def bibleChat(self, mode):
        #config.chatGPTApiIncludeDuckDuckGoSearchResults = False
        config.chatGPTApiContextInAllInputs = False
        fullBookName = BibleBooks().abbrev["eng"][str(config.mainB)][1]
        if mode == "verse":
            config.chatGPTApiPredefinedContext = "Interpret OT Verse" if config.mainC < 40 else "Interpret NT Verse"
            verseText = Bible(config.mainText).readTextVerse(config.mainB, config.mainC, config.mainV, True)[-1]
            verseText = re.sub("<[^<>]*?>", "", verseText)
            config.bibleChatEntry = f"[{fullBookName} {config.mainC}:{config.mainV}] {verseText}"
        elif mode == "chapter":
            subheadings = AGBTSData().getchapterSubheadings(config.mainB, config.mainC)
            extraInfo = ""
            if subheadings:
                verse1 = Bible(config.mainText).readTextVerse(config.mainB, config.mainC, 1, True)[-1]
                extraInfo = f'''The first verse of the chapter is "{verse1}".\n'''
                extraInfo += """I am also providing you with subheadings of the chapter below, to assist your writing:\n"""
                for item in subheadings:
                    *_, v, subheading = item
                    extraInfo += f"From verse {v} - {subheading}\n"
            config.chatGPTApiPredefinedContext = "Summarize a Chapter"
            config.bibleChatEntry = f"The chapter is {fullBookName} {config.mainC}.\n{extraInfo}"
        elif mode == "book":
            config.chatGPTApiPredefinedContext = "Introduce a Book"
            config.bibleChatEntry = fullBookName
        self.runPlugin("Bible Chat")

    def runBibleChatPlugins(self):
        # The following config values can be modified with plugins, to extend functionalities
        config.predefinedContexts = {
            "[none]": "",
            "[custom]": "",
        }
        config.inputSuggestions = []
        config.chatGPTTransformers = []
        config.chatGPTApiFunctionSignatures = []
        config.chatGPTApiAvailableFunctions = {}

        pluginFolder = os.path.join(config.packageDir, "plugins", "chatGPT")
        # always run 'integrate google searches'
        internetSeraches = "integrate google searches"
        script = os.path.join(pluginFolder, "{0}.py".format(internetSeraches))
        self.execPythonFile(script)
        for plugin in FileUtil.fileNamesWithoutExtension(pluginFolder, "py"):
            if not plugin == internetSeraches and not plugin in config.chatGPTPluginExcludeList:
                script = os.path.join(pluginFolder, "{0}.py".format(plugin))
                self.execPythonFile(script)
        if internetSeraches in config.chatGPTPluginExcludeList:
            del config.chatGPTApiFunctionSignatures[0]


    def bibleChatAction(self, context="", copiedText=False):
        if context:
            #config.chatGPTApiIncludeDuckDuckGoSearchResults = False
            config.chatGPTApiContextInAllInputs = False
            config.chatGPTApiPredefinedContext = context
            config.bibleChatEntry = self.getClipboardText() if copiedText else self.selectedText().replace("audiotrack ", "").strip()
        self.runPlugin("Bible Chat")

    def setBibleChatButton(self):
        self.runBibleChatPlugins()
        qIcon = self.getQIcon(self.getCrossplatformPath("material/hardware/smart_toy/materialiconsoutlined/48dp/2x/outline_smart_toy_black_48dp.png"))
        self.bibleChatButton.setStyleSheet(qIcon)
        self.bibleChatButton.setPopupMode(QToolButton.InstantPopup)
        self.bibleChatButton.setArrowType(Qt.NoArrow)
        self.bibleChatButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.bibleChatButton.setToolTip(config.thisTranslation["bibleChat"])
        menu = QMenu(self.bibleChatButton)
        action = menu.addAction(config.thisTranslation["bibleChat"])
        action.triggered.connect(self.bibleChatAction)
        menu.addSeparator()
        for context in config.predefinedContexts:
            action = menu.addAction(context)
            action.triggered.connect(partial(self.bibleChatAction, context))
            action.setToolTip(config.predefinedContexts[context])
        self.bibleChatButton.setMenu(menu)

    def mainRefMenuSelected(self, bcvValue):
        bible, bcv, value = bcvValue
        if bcv == "b":
            config.mainB = value
            chapterList = bible.getChapterList(config.mainB)
            config.mainC = chapterList[0] if chapterList else 1
            verseList = bible.getVerseList(config.mainB, config.mainC)
            config.mainV = verseList[0] if verseList else 1
        elif bcv == "c":
            config.mainC = value
            verseList = bible.getVerseList(config.mainB, config.mainC)
            config.mainV = verseList[0] if verseList else 1
        elif bcv == "v":
            config.mainV = value
        self.openMainChapterMaterial()

    def setStudyRefMenu(self):
        bible = Bible(config.studyText)
        noteBcv = "{0}.{1}.{2}".format(config.studyB, config.studyC, config.studyV)
        bcv = self.bcvToVerseReference(config.studyB, config.studyC, config.studyV)
        bc = bcv.split(":")[0]
        # Book menu
        abbreviations = BibleVerseParser(config.parserStandarisation).standardAbbreviation
        self.studyB.setText(abbreviations[str(config.studyB)])
        self.studyB.setToolTip(config.thisTranslation["menu_book"])
        self.studyB.setPopupMode(QToolButton.InstantPopup)
        self.studyB.setArrowType(Qt.NoArrow)
        menu = QMenu(self.studyB)
        subMenu = menu.addMenu(config.thisTranslation["menu_bookNote"])
        action = subMenu.addAction(config.thisTranslation["open"])
        action.triggered.connect(partial(self.openBibleNotes, "book", noteBcv))
        action = subMenu.addAction(config.thisTranslation["edit"])
        action.triggered.connect(partial(self.editBibleNotes, "book", noteBcv))
        subMenu = menu.addMenu(config.thisTranslation["menu4_book"])
        features = (
            ("html_introduction", lambda: self.searchBookChapter("Tidwell_The_Bible_Book_by_Book", config.studyB)),
            ("html_timelines", lambda: self.searchBookChapter("Timelines", config.studyB)),
            ("context1_dict", lambda: self.searchBookName(True, config.studyB)),
            ("context1_encyclopedia", lambda: self.searchBookName(False, config.studyB)),
        )
        for description, triggered in features:
            action = subMenu.addAction(config.thisTranslation[description])
            action.triggered.connect(triggered)
        menu.addSeparator()
        for b in bible.getBookList():
            if str(b) in abbreviations:
                action = menu.addAction(abbreviations[str(b)])
                action.triggered.connect(partial(self.studyRefMenuSelected, (bible, "b", b)))
                action.setCheckable(True)
                action.setChecked(True if b == config.studyB else False)
        self.studyB.setMenu(menu)
        # Chapter menu
        self.studyC.setText(str(config.studyC))
        self.studyC.setToolTip(config.thisTranslation["menu_chapter"])
        self.studyC.setPopupMode(QToolButton.InstantPopup)
        self.studyC.setArrowType(Qt.NoArrow)
        menu = QMenu(self.studyC)
        subMenu = menu.addMenu(config.thisTranslation["menu_chapterNote"])
        action = subMenu.addAction(config.thisTranslation["open"])
        action.triggered.connect(partial(self.openBibleNotes, "chapter", noteBcv))
        action = subMenu.addAction(config.thisTranslation["edit"])
        action.triggered.connect(partial(self.editBibleNotes, "chapter", noteBcv))
        subMenu = menu.addMenu(config.thisTranslation["menu4_chapter"])
        features = (
            ("html_overview", lambda: self.chapterAction("OVERVIEW", bc)),
            ("html_chapterIndex", lambda: self.chapterAction("CHAPTERINDEX", bc)),
            ("html_summary", lambda: self.chapterAction("SUMMARY", bc)),
            ("menu4_commentary", lambda: self.chapterAction("COMMENTARY", bc)),
            ("parallelVersions", lambda: self.runCompareAction("PARALLEL", bcv)),
            ("sideBySideComparison", lambda: self.runCompareAction("SIDEBYSIDE", bcv)),
            ("rowByRowComparison", lambda: self.runCompareAction("COMPARE", bcv)),
        )
        for description, triggered in features:
            action = subMenu.addAction(config.thisTranslation[description])
            action.triggered.connect(triggered)
        menu.addSeparator()
        for c in bible.getChapterList(config.studyB):
            action = menu.addAction(str(c))
            action.triggered.connect(partial(self.studyRefMenuSelected, (bible, "c", c)))
            action.setCheckable(True)
            action.setChecked(True if c == config.studyC else False)
        self.studyC.setMenu(menu)
        # Verse menu
        self.studyV.setText(str(config.studyV))
        self.studyV.setToolTip(config.thisTranslation["menu_verse"])
        self.studyV.setPopupMode(QToolButton.InstantPopup)
        self.studyV.setArrowType(Qt.NoArrow)
        menu = QMenu(self.studyV)
        subMenu = menu.addMenu(config.thisTranslation["menu_verseNote"])
        action = subMenu.addAction(config.thisTranslation["open"])
        action.triggered.connect(partial(self.openBibleNotes, "verse", noteBcv))
        action = subMenu.addAction(config.thisTranslation["edit"])
        action.triggered.connect(partial(self.editBibleNotes, "verse", noteBcv))
        subMenu = menu.addMenu(config.thisTranslation["menu4_verse"])
        features = (
            ("menu4_compareAll", lambda: self.runFeature("COMPARE", bcv)),
            ("contrasts", lambda: self.runFeature("DIFFERENCE", bcv)),
            ("menu4_crossRef", lambda: self.runFeature("CROSSREFERENCE", bcv)),
            ("menu4_tske", lambda: self.runFeature("TSKE", bcv)),
            ("menu4_traslations", lambda: self.runFeature("TRANSLATION", bcv)),
            ("menu4_discourse", lambda: self.runFeature("DISCOURSE", bcv)),
            ("menu4_words", lambda: self.runFeature("WORDS", bcv)),
            ("menu4_tdw", lambda: self.runFeature("COMBO", bcv)),
            ("menu4_indexes", lambda: self.runFeature("INDEX", bcv)),
            ("menu4_commentary", lambda: self.runFeature("COMMENTARY", bcv)),
        )
        for description, triggered in features:
            action = subMenu.addAction(config.thisTranslation[description])
            action.triggered.connect(triggered)
        #action = subMenu.addAction(config.thisTranslation["interlinearData"])
        #action.triggered.connect(partial(self.runPlugin, "Interlinear Data"))
        menu.addSeparator()
        for v in bible.getVerseList(config.studyB, config.studyC):
            action = menu.addAction(str(v))
            action.triggered.connect(partial(self.studyRefMenuSelected, (bible, "v", v)))
            action.setCheckable(True)
            action.setChecked(True if v == config.studyV else False)
        self.studyV.setMenu(menu)

    def studyRefMenuSelected(self, bcvValue):
        bible, bcv, value = bcvValue
        if bcv == "b":
            config.studyB = value
            chapterList = bible.getChapterList(config.studyB)
            config.studyC = chapterList[0] if chapterList else 1
            verseList = bible.getVerseList(config.studyB, config.studyC)
            config.studyV = verseList[0] if verseList else 1
        elif bcv == "c":
            config.studyC = value
            verseList = bible.getVerseList(config.studyB, config.studyC)
            config.studyV = verseList[0] if verseList else 1
        elif bcv == "v":
            config.studyV = value
        self.openStudyChapterMaterial()

    def setStudyBibleSelection(self):
        label = config.studyText
        toolTip = config.thisTranslation["studyWindowBible"]
        selectedList = [config.studyText]
        triggered = self.openStudyChapterMaterial
        checkable = True
        bibleCollections = True
        bibleCollectionTriggered = self.openStudyChapterMaterial
        bibleCollectionExpansion = True
        self.setBibleSelectionMenuButton(self.studyBibleSelection, label, toolTip, triggered, checkable, selectedList, bibleCollections, bibleCollectionTriggered, bibleCollectionExpansion)

    def setBibleSelection(self):
        label = config.mainText
        toolTip = config.thisTranslation["selectSingleBible"]
        selectedList = [config.mainText]
        triggered = self.openMainChapterMaterial
        checkable = True
        bibleCollections = True
        bibleCollectionTriggered = self.openMainChapterMaterial
        bibleCollectionExpansion = True
        self.setBibleSelectionMenuButton(self.bibleSelection, label, toolTip, triggered, checkable, selectedList, bibleCollections, bibleCollectionTriggered, bibleCollectionExpansion)

    def bibleSelectionForComparisonSelected(self, text):
        if text in config.compareParallelList:
            config.compareParallelList.remove(text)
        else:
            config.compareParallelList.append(text)
        config.compareParallelList.sort()
        self.setBibleSelectionForComparison()

    def bibleCollectionSelectionForComparisonSelected(self, collection=[]):
        if not collection:
            config.compareParallelList = [config.favouriteBible, config.favouriteBible2, config.favouriteBible3]
        elif collection in config.bibleCollections:
            config.compareParallelList = config.bibleCollections[collection]
        config.compareParallelList.sort()
        self.setBibleSelectionForComparison()

    def setBibleSelectionForComparison(self):
        if not config.compareParallelList:
            config.compareParallelList = [config.favouriteBible, config.favouriteBible2, config.favouriteBible3]
        label = "{0}, ...".format(config.compareParallelList[0])
        toolTip = config.thisTranslation["selectMultipleBibles"]
        selectedList = config.compareParallelList
        triggered = self.bibleSelectionForComparisonSelected
        checkable = True
        bibleCollections = True
        bibleCollectionTriggered = self.bibleCollectionSelectionForComparisonSelected
        self.setBibleSelectionMenuButton(self.bibleSelectionForComparison, label, toolTip, triggered, checkable, selectedList, bibleCollections, bibleCollectionTriggered)

    def setBibleSelectionMenuButton(self, menuButton, label, toolTip, triggered, checkable=False, selectedList=[], bibleCollections=False, bibleCollectionTriggered=None, bibleCollectionExpansion=False):
        if menuButton:
            menuButton.setText(label)
            menuButton.setToolTip(toolTip)
            menuButton.setPopupMode(QToolButton.InstantPopup)
            menuButton.setAutoRaise(True)
            menuButton.setArrowType(Qt.NoArrow)
            menu = QMenu(menuButton)
            if bibleCollections:
                if bibleCollectionExpansion:
                    subMenu = menu.addMenu(config.thisTranslation["menu_favouriteBible"])
                    for text in [config.favouriteBible, config.favouriteBible2, config.favouriteBible3]:
                        action = subMenu.addAction(text)
                        action.setCheckable(True if checkable else False)
                        if checkable and selectedList:
                            action.setChecked(True if text in selectedList else False)
                        if bibleCollectionTriggered:
                            action.triggered.connect(partial(bibleCollectionTriggered, text))
                    for collection in config.bibleCollections:
                        subMenu = menu.addMenu(collection)
                        for text in config.bibleCollections[collection]:
                            action = subMenu.addAction(text)
                            action.setCheckable(True if checkable else False)
                            if checkable and selectedList:
                                action.setChecked(True if text in selectedList else False)
                            if bibleCollectionTriggered:
                                action.triggered.connect(partial(bibleCollectionTriggered, text))
                else:
                    action = menu.addAction(config.thisTranslation["menu_favouriteBible"])
                    if bibleCollectionTriggered:
                        action.triggered.connect(bibleCollectionTriggered)
                    for collection in config.bibleCollections:
                        action = menu.addAction(collection)
                        if bibleCollectionTriggered:
                            action.triggered.connect(partial(bibleCollectionTriggered, collection))
                menu.addSeparator()
            for text in self.textList:
                action = menu.addAction(text)
                action.triggered.connect(partial(triggered, text))
                action.setCheckable(True if checkable else False)
                if checkable and selectedList:
                    selectedList = list(set(sorted(selectedList)))
                    action.setChecked(True if text in selectedList else False)
            menuButton.setMenu(menu)

    def addBibleVersionButton(self):
        if self.textCommandParser.isDatabaseInstalled("bible"):
            if config.refButtonClickAction == "direct":
                self.versionButton = None
                self.versionCombo = QComboBox()
                self.bibleVersions = BiblesSqlite().getBibleList()
                self.versionCombo.addItems(self.bibleVersions)
                initialIndex = 0
                if config.mainText in self.bibleVersions:
                    initialIndex = self.bibleVersions.index(config.mainText)
                self.versionCombo.setCurrentIndex(initialIndex)
                self.versionCombo.currentIndexChanged.connect(self.changeBibleVersion)
                textButtonStyle = "QComboBox {background-color: #151B54; color: white;} QComboBox:hover {background-color: #333972;} QComboBox:pressed { background-color: #515790;}"
                self.versionCombo.setStyleSheet(textButtonStyle)
                self.firstToolBar.addWidget(self.versionCombo)
            else:
                self.versionCombo = None
                self.versionButton = QPushButton(config.mainText)
                textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"
                self.versionButton.setStyleSheet(textButtonStyle)
                self.addStandardTextButton("bibleVersion", self.versionButtonClicked, self.firstToolBar,
                                           self.versionButton)

    def versionButtonClicked(self):
        if config.refButtonClickAction == "master":
            self.openControlPanelTab(0)
        elif config.refButtonClickAction == "mini":
            self.openMiniControlTab(1)

    def openInterlinearData(self):
        selectedText = self.mainView.currentWidget().selectedText().strip()
        if not selectedText:
            selectedText = self.studyView.currentWidget().selectedText().strip()
            if not selectedText:
                self.runPlugin("Interlinear Data")
            else:
                self.studyView.currentWidget().runPlugin("Interlinear Data", selectedText)
        else:
            self.studyView.currentWidget().runPlugin("Interlinear Data", selectedText)

    def generateChartsAndTable(self):
        selectedText = self.mainView.currentWidget().selectedText().strip()
        if not selectedText:
            selectedText = self.studyView.currentWidget().selectedText().strip()
            if not selectedText:
                self.studyView.currentWidget().page().toPlainText(self.runChartsAndTable)
            else:
                self.runChartsAndTable(selectedText)
        else:
            self.runChartsAndTable(selectedText)

    def runChartsAndTable(self, selectedText):
        self.studyView.currentWidget().runPlugin("Charts and Table", selectedText)

    def getSelectionMonitoringButtonToolTip(self):
        return "{0}: {1}".format(config.thisTranslation["selectionMonitoring"], config.thisTranslation["on"] if config.enableSelectionMonitoring else config.thisTranslation["off"])

    def selectionMonitoringButtonClicked(self):
        config.enableSelectionMonitoring = not config.enableSelectionMonitoring
        self.selectionMonitoringButton.setChecked(True if config.enableSelectionMonitoring else False)
        self.selectionMonitoringButton.setToolTip(self.getSelectionMonitoringButtonToolTip())

    def instantTTS(self):
        if config.isGoogleCloudTTSAvailable or ((not ("OfflineTts" in config.enabled) or config.forceOnlineTts) and ("Gtts" in config.enabled)):
            # online tts
            self.mainView.currentWidget().googleTextToSpeechLanguage("", True)
        else:
            # offline tts
            self.mainView.currentWidget().textToSpeech(True)

    def instantTTS2(self):
        if config.isGoogleCloudTTSAvailable or ((not ("OfflineTts" in config.enabled) or config.forceOnlineTts) and ("Gtts" in config.enabled)):
            # online tts
            self.mainView.currentWidget().googleTextToSpeechLanguage(config.ttsDefaultLangauge2, True)
        else:
            # offline tts
            self.mainView.currentWidget().textToSpeechLanguage(config.ttsDefaultLangauge2, True)

    def instantTTS3(self):
        if config.isGoogleCloudTTSAvailable or ((not ("OfflineTts" in config.enabled) or config.forceOnlineTts) and ("Gtts" in config.enabled)):
            # online tts
            self.mainView.currentWidget().googleTextToSpeechLanguage(config.ttsDefaultLangauge3, True)
        else:
            # offline tts
            self.mainView.currentWidget().textToSpeechLanguage(config.ttsDefaultLangauge3, True)            

    def openVlcPlayer(self):
        VlcUtil.openVlcPlayer()

    def closeMediaPlayer(self):
        #if hasattr(config, "workerThread") and config.workerThread is not None:
        #    config.workerThread.quit()
        # stop terminal mode .readsync loop
        isPydubPlaying = os.path.join("temp", "isPydubPlaying")
        for file_to_be_deleted in (config.audio_playing_file, isPydubPlaying):
            if os.path.isfile(file_to_be_deleted):
                os.remove(file_to_be_deleted)
        if self.audioPlayer is not None:
            self.stopAudioPlaying()
        VlcUtil.closeVlcPlayer()
        if not platform.system() == "Windows" and WebtopUtil.isPackageInstalled("pkill"):
            if WebtopUtil.isPackageInstalled("espeak"):
                os.system("pkill espeak")
        # stop individual offline TTS audio
        if self.textCommandParser.cliTtsProcess is not None:
            #print(self.cliTtsProcess)
            # The following two lines do not work:
            #self.cliTtsProcess.kill()
            #self.cliTtsProcess.terminate()
            # Therefore, we use:
            try:
                os.killpg(os.getpgid(self.textCommandParser.cliTtsProcess.pid), signal.SIGTERM)
            except:
                pass
            self.textCommandParser.cliTtsProcess = None
        elif self.textCommandParser.qtTtsEngine is not None:
            self.textCommandParser.qtTtsEngine.stop()

    def playAudioBibleChapterVerseByVerse(self, text, b, c, startVerse=0):
        playlist = []
        folder = os.path.join(config.audioFolder, "bibles", text, "default", "{0}_{1}".format(b, c))
        if os.path.isdir(folder):
            verses = Bible(text).getVerseList(b, c)
            for verse in verses:
                if verse >= startVerse:
                    audioFile = os.path.join(folder, "{0}_{1}_{2}_{3}.mp3".format(text, b, c, verse))
                    if os.path.isfile(audioFile):
                        playlist.append(audioFile)
        self.playAudioBibleFilePlayList(playlist)

    def playAudioBibleFilePlayList(self, playlist, gui=True):
        self.closeMediaPlayer()
        if self.audioPlayer is not None:
            self.addToAudioPlayList(playlist, True)
        elif config.isVlcAvailable:
            VlcUtil.playMediaFile(playlist, config.vlcSpeed, gui)
        else:
            self.displayMessage(config.thisTranslation["noMediaPlayer"])

    def playBibleMP3Playlist(self, playlist):
        self.closeMediaPlayer()
        if playlist:
            def getFilelist():
                fileList = []
                for listItem in playlist:
                    (text, book, chapter, verse, folder) = listItem
                    file = FileUtil.getBibleMP3File(text, book, folder, chapter, verse)
                    if file:
                        fileList.append(file)
                return fileList
            if self.audioPlayer is not None:
                self.addToAudioPlayList(getFilelist(), True)
            elif config.isVlcAvailable:
                VlcUtil.playMediaFile(getFilelist(), config.vlcSpeed, True)
        else:
            self.displayMessage(config.thisTranslation["noMediaPlayer"])

    def playBibleMP3File(self, text, book, chapter, folder=config.defaultMP3BibleFolder):
        playlist = []
        playlist.append((text, book, chapter, folder))
        self.playBibleMP3Playlist(playlist)

    def openDevotional(self, devotional, date=""):
        if date == "":
            month = DateUtil.currentMonth()
            day = DateUtil.currentDay()
        else:
            (m, d) = date.split("-")
            month = int(m)
            day = int(d)
        d = DevotionalSqlite(devotional)
        text = d.getEntry(month, day)
        text = re.sub('<a href=.*?>','', text)
        text = text.replace('</a>', '')
        text = self.htmlWrapper(text, True, "study", False, True)
        current = DateUtil.dateStringToObject("{0}-{1}-{2}".format(DateUtil.currentYear(), month, day))
        previous = DateUtil.addDays(current, -1)
        next = DateUtil.addDays(current, 1)
        prevMonth = previous.month
        prevDay = previous.day
        nextMonth = next.month
        nextDay = next.day
        header = """<center><h3>{0} {1}</h3>
                <p>[{2}Previous</ref>] - [{3}Next</ref>]</p></center>
                """.format(DateUtil.monthFullName(month), day,
                "<ref onclick='document.title=\"DEVOTIONAL:::{0}:::{1}-{2}\"'>".format(devotional, prevMonth, prevDay),
                "<ref onclick='document.title=\"DEVOTIONAL:::{0}:::{1}-{2}\"'>".format(devotional, nextMonth, nextDay))
        text = header + text

        self.openTextOnStudyView(text, tab_title="devotional", toolTip=devotional)


    # Google Text-to-speech
    # Temporary filepath for tts export
    def getGttsFilename(self):
        return self.crossPlatform.getGttsFilename()

    # Fine tune text and language
    def fineTuneGtts(self, text, language):
        return self.crossPlatform.fineTuneGtts(text, language)

    # Python package gTTS, not created by Google
    def saveGTTSAudio(self, inputText, languageCode, filename=""):
        self.crossPlatform.saveGTTSAudio(inputText, languageCode, filename)

    # Official Google Cloud Text-to-speech Service
    def saveCloudTTSAudio(self, inputText, languageCode, filename=""):
        self.crossPlatform.saveCloudTTSAudio(inputText, languageCode, filename)

    def testing(self):
        #pass
        print("testing")

    # Work with system tray
    def showFromTray(self):
        self.show()
        if self.isMinimized():
            self.showMaximized()
        if not SystemUtil.isWayland():
            self.activateWindow()
        self.raise_()
        if platform.system() == "Linux":
            self.bringToForeground(self)
        config.mainWindowHidden = False

    # Work with workspace
    def swapWorkspaceWithMainWindow(self):
        if self.isActiveWindow():
            self.displayWorkspace()
        else:
            self.showFromTray()

    def displayWorkspace(self):
        self.ws.exemptSaving = True
        self.ws.show()
        if self.ws.isMinimized():
            self.ws.showMaximized()
        if not SystemUtil.isWayland():
            self.ws.activateWindow()
        self.ws.raise_()
        if platform.system() == "Linux":
            self.bringToForeground(self.ws)
        self.ws.exemptSaving = False

    def addToWorkspaceReadOnlyAction(self, html, windowTitle=""):
        self.ws.addHtmlContent(html, False, windowTitle)

    def addToWorkspaceEditableAction(self, html, windowTitle=""):
        self.ws.addHtmlContent(html, True, windowTitle)

    def addTextSelectionToWorkspace(self, selectedText="", editable=False):
        if selectedText:
            html = self.htmlWrapper(selectedText, True)
            windowTitle = selectedText.replace("\n", " ")
            if editable:
                self.addToWorkspaceEditableAction(html, windowTitle)
            else:
                self.addToWorkspaceReadOnlyAction(html, windowTitle)
        else:
            self.messageNoSelection()

    def addBibleReferencesInTextSelectionToWorkspace(self, selectedText="", editable=False):
        if selectedText:
            parser = BibleVerseParser(config.parserStandarisation)
            verseList = parser.extractAllReferences(selectedText, False)
            if not verseList:
                self.displayMessage(config.thisTranslation["message_noReference"])
            else:
                references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verseList])
                html = self.htmlWrapper(references, True)
                if editable:
                    self.addToWorkspaceEditableAction(html, references)
                else:
                    self.addToWorkspaceReadOnlyAction(html, references)
        else:
            self.messageNoSelection()

    def messageNoSelection(self):
        self.displayMessage("{0}\n{1}".format(config.thisTranslation["message_run"], config.thisTranslation["selectTextFirst"]))

    def getTextCommandSuggestion(self):
        # Text command autocompletion/autosuggest
        textCommandParser = TextCommandParser(self)
        textCommands = [key + ":::" for key in textCommandParser.interpreters.keys()]
        bb = BibleBooks()
        bibleBooks = bb.getStandardBookAbbreviations()
        allKJVreferences = bb.getAllKJVreferences()[0]
        textCommandAutosuggestion = QCompleter(textCommands + bibleBooks + allKJVreferences)
        textCommandAutosuggestion.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        return textCommandAutosuggestion

    # Get text selection
    def getSelectedText(self):
        selectedText = self.mainView.currentWidget().selectedText().strip()
        if not selectedText:
            selectedText = self.studyView.currentWidget().selectedText().strip()
        if not selectedText:
            config.selectedText = None
        else:
            config.selectedText = selectedText

    def selectedText(self, studyViewFirst=False):
        if studyViewFirst:
            selectedText = self.studyView.currentWidget().selectedText().strip()
            if not selectedText:
                selectedText = self.mainView.currentWidget().selectedText().strip()
            return selectedText
        else:
            selectedText = self.mainView.currentWidget().selectedText().strip()
            if not selectedText:
                selectedText = self.studyView.currentWidget().selectedText().strip()
            return selectedText
