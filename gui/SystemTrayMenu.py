import config, platform, os
from util.FileUtil import FileUtil
from functools import partial
from util.Languages import Languages
from util.GoogleCloudTTSVoices import GoogleCloudTTS
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QMenu
    from PySide6.QtGui import QAction
else:
    from qtpy.QtWidgets import QMenu, QAction

# Set up a system tray

trayMenu = QMenu()
# Show Main Window
showMainWindow = QAction(config.thisTranslation["show"])
showMainWindow.triggered.connect(config.mainWindow.showFromTray)
trayMenu.addAction(showMainWindow)
# Add a separator
trayMenu.addSeparator()
# Control Panel
masterControl = QAction(config.thisTranslation["controlPanel"])
masterControl.triggered.connect(config.mainWindow.showFromTray)
masterControl.triggered.connect(partial(config.mainWindow.openControlPanelTab, 0))
trayMenu.addAction(masterControl)
miniControl = QAction(config.thisTranslation["menu1_miniControl"])
miniControl.triggered.connect(config.mainWindow.showFromTray)
miniControl.triggered.connect(config.mainWindow.manageMiniControl)
trayMenu.addAction(miniControl)
# Add a separatorJohn 3:16, 19
trayMenu.addSeparator()
# Search section
searchBibleForClipboardContent = QAction(config.thisTranslation["searchBibleForClipboardContent"])
searchBibleForClipboardContent.triggered.connect(config.mainWindow.showFromTray)
searchBibleForClipboardContent.triggered.connect(config.mainWindow.searchBibleForClipboardContent)
trayMenu.addAction(searchBibleForClipboardContent)
searchResourcesForClipboardContent = QAction(config.thisTranslation["searchMore"])
searchResourcesForClipboardContent.triggered.connect(config.mainWindow.showFromTray)
searchResourcesForClipboardContent.triggered.connect(config.mainWindow.searchResourcesForClipboardContent)
trayMenu.addAction(searchResourcesForClipboardContent)
# Add a separatorJohn 3:16, 19
trayMenu.addSeparator()
# Work with clipboard
openClipboardReferences = QAction(config.thisTranslation["openClipboardReferences"])
openClipboardReferences.triggered.connect(config.mainWindow.showFromTray)
openClipboardReferences.triggered.connect(config.mainWindow.openReferencesOnClipboard)
trayMenu.addAction(openClipboardReferences)
displayClipboardContent = QAction(config.thisTranslation["displayClipboardContent"])
displayClipboardContent.triggered.connect(config.mainWindow.showFromTray)
displayClipboardContent.triggered.connect(config.mainWindow.pasteFromClipboard)
trayMenu.addAction(displayClipboardContent)
if not config.noTtsFound:
    readClipboardContent = QAction(config.thisTranslation["readClipboardContent"])
    readClipboardContent.triggered.connect(config.mainWindow.readClipboardContent)
    trayMenu.addAction(readClipboardContent)
# Text-to-speech
# Google TEXT-TO-SPEECH feature
if config.isGoogleCloudTTSAvailable or ((not config.isOfflineTtsInstalled or config.forceOnlineTts) and config.isGTTSInstalled):
    languageCodes = GoogleCloudTTS.getLanguages() if config.isGoogleCloudTTSAvailable else Languages.gTTSLanguageCodes
    ttsMenu = QMenu()
    index = 0
    for language, languageCode in languageCodes.items():
        exec('ttsAction{0} = QAction(language)'.format(index))
        exec('ttsAction{0}.triggered.connect(partial(config.mainWindow.clipboardTts, languageCode))'.format(index))
        exec('ttsMenu.addAction(ttsAction{0})'.format(index))
        exec('index += 1')
    tts = QAction("{0} ...".format(config.thisTranslation["readClipboardContent"]))
    tts.setMenu(ttsMenu)
    trayMenu.addAction(tts)
    # Add a separator
    trayMenu.addSeparator()
# OFFLINE TEXT-TO-SPEECH feature
elif config.isOfflineTtsInstalled:
    languages = config.mainWindow.getTtsLanguages()
    ttsMenu = QMenu()
    languageCodes = list(languages.keys())
    items = [languages[code][1] for code in languageCodes]
    for index, item in enumerate(items):
        languageCode = languageCodes[index]
        exec('ttsAction{0} = QAction(item if config.ttsDefaultLangauge.startswith("[") else item.capitalize())'.format(index))
        exec('ttsAction{0}.triggered.connect(partial(config.mainWindow.clipboardTts, languageCode))'.format(index))
        exec('ttsMenu.addAction(ttsAction{0})'.format(index))
    tts = QAction("{0} ...".format(config.thisTranslation["readClipboardContent"]))
    tts.setMenu(ttsMenu)
    trayMenu.addAction(tts)
#runClipboardCommand = QAction(config.thisTranslation["runClipboardCommand"])
#runClipboardCommand.triggered.connect(config.mainWindow.showFromTray)
#runClipboardCommand.triggered.connect(config.mainWindow.parseContentOnClipboard)
#trayMenu.addAction(runClipboardCommand)
# Context plugins
if config.enablePlugins:
    subMenu = QMenu()
    for index, plugin in enumerate(FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "context"), "py")):
        feature, *_ = plugin.split("_", 1)
        exec("action{0} = QAction(feature)".format(index))
        exec("action{0}.triggered.connect(config.mainWindow.showFromTray)".format(index))
        exec("action{0}.triggered.connect(partial(config.mainWindow.runContextPluginOnClipboardContent, plugin))".format(index))
        exec("subMenu.addAction(action{0})".format(index))
    contextPlugins = QAction(config.thisTranslation["runContextPluginOnClipboardContent"])
    contextPlugins.setMenu(subMenu)
    trayMenu.addAction(contextPlugins)
# Add a separator
trayMenu.addSeparator()
# Media
youtubeDownloader = QAction(config.thisTranslation["youtube_utility"])
youtubeDownloader.triggered.connect(config.mainWindow.showFromTray)
youtubeDownloader.triggered.connect(config.mainWindow.openYouTube)
trayMenu.addAction(youtubeDownloader)
showMedia = QAction(config.thisTranslation["media"])
showMedia.triggered.connect(config.mainWindow.showFromTray)
showMedia.triggered.connect(partial(config.mainWindow.openControlPanelTab, 6))
trayMenu.addAction(showMedia)
stopPlayMedia = QAction(config.thisTranslation["stopPlayMedia"])
stopPlayMedia.triggered.connect(config.mainWindow.closeMediaPlayer)
trayMenu.addAction(stopPlayMedia)
# Add a separator
trayMenu.addSeparator()
# Restart UBA on macOS
if platform.system() == "Darwin":
    restartApp = QAction(config.thisTranslation["restart"])
    restartApp.triggered.connect(config.mainWindow.restartApp)
    trayMenu.addAction(restartApp)
