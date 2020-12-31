import os, sys, re, config, base64, webbrowser, platform, subprocess, zipfile, gdown, requests, update, myTranslation
from datetime import datetime
from ast import literal_eval
from PySide2.QtCore import QUrl, Qt, QEvent
from PySide2.QtGui import QIcon, QGuiApplication, QFont
from PySide2.QtWidgets import (QAction, QInputDialog, QLineEdit, QMainWindow, QMessageBox, QPushButton, QToolBar, QWidget, QFileDialog, QLabel, QFrame, QFontDialog)
from TextCommandParser import TextCommandParser
from BibleVerseParser import BibleVerseParser
from BiblesSqlite import BiblesSqlite
from TextFileReader import TextFileReader
from NoteSqlite import NoteSqlite
from ThirdParty import Converter, ThirdPartyDictionary
from Languages import Languages
from ToolsSqlite import BookData, IndexesSqlite
from translations import translations
from shutil import copyfile, rmtree
from distutils.dir_util import copy_tree
from gui.Downloader import Downloader
from gui.MoreConfigOptions import MoreConfigOptions
from gui.ImportSettings import ImportSettings
from gui.NoteEditor import NoteEditor
from gui.RemoteControl import RemoteControl
from gui.MorphDialog import MorphDialog
from gui.YouTubePopover import YouTubePopover
from gui.CentralWidget import CentralWidget
from gui.imports import *
from ToolsSqlite import LexiconData

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Repository
        # Read about downloading a raw github file: https://unix.stackexchange.com/questions/228412/how-to-wget-a-github-file
        self.repository = "https://raw.githubusercontent.com/eliranwong/UniqueBible/master/"
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
        self.bibleInfo = update.bibleInfo
        # set os open command
        self.setOsOpenCmd()
        # set translation of interface
        self.setTranslation()
        # setup a parser for text commands
        self.textCommandParser = TextCommandParser(self)
        # setup a global variable "baseURL"
        self.setupBaseUrl()
        # variables for history management
        self.now = datetime.now()
        self.lastMainTextCommand = ""
        self.lastStudyTextCommand = ""
        self.newTabException = False
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
        self.setWindowTitle("UniqueBible.app [version {0}]".format(config.version))
        appIconFile = os.path.join("htmlResources", "theText.png")
        appIcon = QIcon(appIconFile)
        QGuiApplication.setWindowIcon(appIcon)
        # setup user menu & toolbars
        self.create_menu()
        self.setupToolBar()
        self.setAdditionalToolBar()
        # assign views
        # mainView & studyView are assigned with class "CentralWidget"        
        self.mainView = None
        self.studyView = None        
        self.noteEditor = None
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
        if config.openStudyWindowContentOnNextTab and not config.syncStudyWindowBibleWithMainWindow and not config.syncCommentaryWithMainWindow:
            self.studyView.setCurrentIndex(config.numberOfTab - 1)
        self.setStudyPage()
        self.instantPage = self.instantView.page()
        if config.theme == "dark":
            self.instantPage.setBackgroundColor(Qt.transparent)
        self.instantPage.titleChanged.connect(self.instantTextCommandChanged)
        # position views as the last-opened layout
        self.resizeCentral()

        # check if newer version is available
        self.checkApplicationUpdate()
        # check if newer versions of formatted bibles are available
        self.checkModulesUpdate()

        # setup a remote controller
        self.remoteControl = RemoteControl(self)
        if config.remoteControl:
            self.manageRemoteControl(True)

    def __del__(self):
        del self.textCommandParser

    def setOsOpenCmd(self):
        if platform.system() == "Linux":
            config.open = config.openLinux
        elif platform.system() == "Darwin":
            config.open = config.openMacos
        elif platform.system() == "Windows":
            config.open = config.openWindows

    def setTranslation(self):
        updateNeeded = False
        languages = Languages()
        if config.userLanguageInterface and hasattr(myTranslation, "translation"):
            # Check for missing items. Use Google Translate to translate the missing items.  Or use default English translation to fill in missing items if internet connection is not available.
            for key, value in languages.translation.items():
                if not key in myTranslation.translation:
                    if config.googletransSupport and hasattr(myTranslation, "translationLanguage"):
                        try:
                            languageCode = languages.codes[myTranslation.translationLanguage]
                            myTranslation.translation[key] = Translator().translate(value, dest=languageCode).text
                        except:
                            myTranslation.translation[key] = value
                    else:
                        myTranslation.translation[key] = value
                    updateNeeded = True
            # set thisTranslation to customised translation
            config.thisTranslation = myTranslation.translation
            # update myTranslation.py
            if updateNeeded:
                try:
                    languages.writeMyTranslation(myTranslation.translation, myTranslation.translationLanguage)
                except:
                    print("Failed to update 'myTranslation.py'.")
                self.displayMessage("{0}  {1} 'config.py'".format(config.thisTranslation["message_newInterfaceItems"], config.thisTranslation["message_improveTrans"]))
        elif config.userLanguageInterface and hasattr(config, "translationLanguage"):
            languageCode = languages.codes[config.translationLanguage]
            if languageCode in translations:
                # set thisTranslation to provided translation
                config.thisTranslation = translations[languageCode]
            else:
                # set thisTranslation to default English translation
                config.thisTranslation = languages.translation
        else:
            # set thisTranslation to default English translation
            config.thisTranslation = languages.translation

    def translateInterface(self):
        if config.googletransSupport:
            if not config.userLanguage:
                self.displayMessage("{0}\n{1}".format(config.thisTranslation["message_run"], config.thisTranslation["message_setLanguage"]))
            else:
                if Languages().translateInterface(config.userLanguage):
                    config.userLanguageInterface = True
                    self.displayMessage("{0}  {1} 'config.py'".format(config.thisTranslation["message_restart"], config.thisTranslation["message_improveTrans"]))
                else:
                    config.userLanguageInterface = False
                    self.displayMessage("'{0}' translation have not been added yet.  You can send us an email to request a copy of your language.".format(config.userLanguage))
        else:
            self.displayMessage("{0} 'googletrans'\n{1}".format(config.thisTranslation["message_missing"], config.thisTranslation["message_installFirst"]))

    def isMyTranslationAvailable(self):
        if hasattr(myTranslation, "translation") and hasattr(myTranslation, "translationLanguage"):
            return True
        else:
            return False

    def isOfficialTranslationAvailable(self):
        if hasattr(config, "translationLanguage") and Languages().codes[config.translationLanguage] in translations:
            return True
        else:
            return False

    def toogleInterfaceTranslation(self):
        if not self.isMyTranslationAvailable() and not self.isOfficialTranslationAvailable():
            self.displayMessage("{0}\n{1}".format(config.thisTranslation["message_run"], config.thisTranslation["message_translateFirst"]))
        else:
            config.userLanguageInterface = not config.userLanguageInterface
            self.displayMessage(config.thisTranslation["message_restart"])

    # base folder for webViewEngine
    def setupBaseUrl(self):
        # Variable "baseUrl" is shared by multiple classes
        # External objects, such as stylesheets or images referenced in the HTML document, are located RELATIVE TO baseUrl .
        # e.g. put all local files linked by html's content in folder "htmlResources"
        global baseUrl
        relativePath = os.path.join("htmlResources", "theText.png")
        absolutePath = os.path.abspath(relativePath)
        baseUrl = QUrl.fromLocalFile(absolutePath)
        config.baseUrl = baseUrl

    def manageRemoteControl(self, open=False):
        if open or not config.remoteControl:
            self.remoteControl.show()
            config.remoteControl = True
        else:
            self.remoteControl.hide()
            config.remoteControl = False

    def closeEvent(self, event):
        if self.noteEditor:
            if self.noteEditor.close():
                event.accept()
                qApp.quit()
            else:
                event.ignore()
        else:
            event.accept()
            qApp.quit()

    # check migration
    def checkMigration(self):
        if config.version >= 0.56:
            biblesSqlite = BiblesSqlite()
            biblesWithBothVersions = biblesSqlite.migratePlainFormattedBibles()
            if biblesWithBothVersions:
                self.displayMessage("{0}  {1}".format(config.thisTranslation["message_migration"], config.thisTranslation["message_willBeNoticed"]))
                biblesSqlite.proceedMigration(biblesWithBothVersions)
                self.displayMessage(config.thisTranslation["message_done"])
            del biblesSqlite

    def displayMessage(self, message, title="UniqueBible"):
        reply = QMessageBox.information(self, title, message)

    # manage key capture
    def event(self, event):
        if event.type() == QEvent.KeyRelease:
            if event.key() == Qt.Key_Tab:
                self.textCommandLineEdit.setFocus()
                return True
            elif event.key() == Qt.Key_Escape:
                self.setNoToolBar()
                return True
            # CHINESE TOOL - openCC
            # Convert command line from simplified Chinese to traditional Chinese characters
            # Ctrl + H
#            elif openccSupport and event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_H:
#                newTextCommand = opencc.convert(self.textCommandLineEdit.text(), config="s2t.json")
#                self.textCommandLineEdit.setText(newTextCommand)
#                return True
        return QWidget.event(self, event)

    # manage main page
    def setMainPage(self):
        # main page changes as tab is changed.
        #print(self.mainView.currentIndex())
        self.mainPage = self.mainView.currentWidget().page()
        if config.theme == "dark":
            self.mainPage.setBackgroundColor(Qt.transparent)
        self.mainPage.titleChanged.connect(self.mainTextCommandChanged)
        self.mainPage.loadFinished.connect(self.finishMainViewLoading)
        self.mainPage.pdfPrintingFinished.connect(self.pdfPrintingFinishedAction)

    def setStudyPage(self, tabIndex=None):
        if tabIndex != None:
            self.studyView.setCurrentIndex(tabIndex)
        # study page changes as tab is changed.
        #print(self.studyView.currentIndex())
        self.studyPage = self.studyView.currentWidget().page()
        if config.theme == "dark":
            self.studyPage.setBackgroundColor(Qt.transparent)
        self.studyPage.titleChanged.connect(self.studyTextCommandChanged)
        self.studyPage.loadFinished.connect(self.finishStudyViewLoading)
        self.studyPage.pdfPrintingFinished.connect(self.pdfPrintingFinishedAction)

    # manage latest update
    def checkApplicationUpdate(self):
        # delete unwanted old files / folders
        if config.version < 11.6:
            oldExlblFolder = os.path.join("htmlResources", "images", "EXLBL")
            if os.path.isdir(oldExlblFolder):
                rmtree(oldExlblFolder)
        try:
            # latest version number is indicated in file "UniqueBibleAppVersion.txt"
            checkFile = "{0}UniqueBibleAppVersion.txt".format(self.repository)
            request = requests.get(checkFile, timeout=5)
            if request.status_code == 200:
                # tell the rest that internet connection is available
                config.internet = True
                # compare with user's current version
                if float(request.text) > config.version:
                    self.promptUpdate(request.text)
            else:
                config.internet = False
        except:
            config.internet = False
            print("Failed to read '{0}'.".format(checkFile))

    def checkModulesUpdate(self):
        if not config.disableModulesUpdateCheck:
            for filename in self.updatedFiles:
                abb = filename[:-6]
                if os.path.isfile(os.path.join(*self.bibleInfo[abb][0])):
                    if self.isNewerAvailable(filename):
                        self.displayMessage("{1} {0}.  {2} '{3} > {4}'".format(filename, config.thisTranslation["message_newerFile"], config.thisTranslation["message_installFrom"], config.thisTranslation["menu8_resources"], config.thisTranslation["menu8_bibles"]))

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
        reply = QMessageBox.question(self, "Update is available ...",
                    "Update is available ...\n\nLatest version: {0}\nInstalled version: {1}\n\nDo you want to proceed the update?".format(latestVersion, config.version),
                    QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.updateUniqueBibleApp()

    # The following update method is used from version 11.9 onwards
    # "patches.txt" from the repository is read for proceeding the update
    def updateUniqueBibleApp(self):
        requestObject = requests.get("{0}patches.txt".format(self.repository))
        for line in requestObject.text.split("\n"):
            if line:
                try:
                    version, contentType, filePath = literal_eval(line)
                    if version > config.version:
                        localPath = os.path.join(*filePath.split("/"))
                        if contentType == "folder":
                            if not os.path.isdir(localPath):
                                os.makedirs(localPath)
                        elif contentType == "file":
                            requestObject2 = requests.get("{0}{1}".format(self.repository, filePath))
                            with open(localPath, "wb") as fileObject:
                                fileObject.write(requestObject2.content)
                except:
                    # message on failed item
                    self.displayMessage("{0}\n{1}".format(config.thisTranslation["message_fail"], line))
        # set executable files on macOS or Linux
        if not platform.system() == "Windows":
            for filename in ("main.py", "BibleVerseParser.py", "RegexSearch.py", "shortcut_uba_Windows_wsl2.sh", "shortcut_uba_macOS_Linux.sh"):
                os.chmod(filename, 0o755)
        # finish message
        self.displayMessage("{0}  {1}".format(config.thisTranslation["message_done"], config.thisTranslation["message_restart"]))
        self.openExternalFile("latest_changes.txt")

    # old way to do the update, all content will be downloaded to overwrite all current files
    def updateUniqueBibleApp2(self):
        masterfile = "https://github.com/eliranwong/UniqueBible/archive/master.zip"
        request = requests.get(masterfile)
        if request.status_code == 200:
            filename = masterfile.split("/")[-1]
            with open(filename, "wb") as content:
                content.write(request.content)
            if filename.endswith(".zip"):
                zipObject = zipfile.ZipFile(filename, "r")
                zipObject.extractall(os.getcwd())
                zipObject.close()
                os.remove(filename)
                # We use "distutils.dir_util.copy_tree" below instead of "shutil.copytree", as "shutil.copytree" does not overwrite old files.
                try:
                    # delete unwant files / folders first
                    oldExlblFolder = os.path.join("htmlResources", "images", "EXLBL")
                    if os.path.isdir(oldExlblFolder):
                        rmtree(oldExlblFolder)
                    # copy all new content
                    copy_tree("UniqueBible-master", os.getcwd())
                except:
                    print("Failed to overwrite files.")
                # set executable files on macOS or Linux
                if not platform.system() == "Windows":
                    for filename in ("main.py", "BibleVerseParser.py", "RegexSearch.py", "shortcut_uba_Windows_wsl2.sh", "shortcut_uba_macOS_Linux.sh"):
                        os.chmod(filename, 0o755)
                # remove download files after upgrade
                if config.removeBackup:
                    try:
                        rmtree("UniqueBible-master")
                    except:
                        print("Failed to remove downloaded files.")
                # prompt a restart
                self.displayMessage("{0}  {1}".format(config.thisTranslation["message_done"], config.thisTranslation["message_restart"]))
                self.openExternalFile("latest_changes.txt")
            else:
                self.displayMessage(config.thisTranslation["message_fail"])
        else:
            self.displayMessage(config.thisTranslation["message_fail"])

    # manage download helper
    def downloadHelper(self, databaseInfo):
        self.downloader = Downloader(self, databaseInfo)
        self.downloader.show()

    def moduleInstalled(self, databaseInfo):
        self.downloader.close()
        self.displayMessage(config.thisTranslation["message_done"])

        # Update install History
        fileItems, cloudID, *_ = databaseInfo
        config.installHistory[fileItems[-1]] = cloudID
        
    def moduleInstalledFailed(self, databaseInfo):
        self.downloader.close()
        self.displayMessage(config.thisTranslation["message_fail"])

    # setup interface
    def create_menu(self):
        menu1 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu1_app"]))
        menu1.addAction(QAction(config.thisTranslation["menu1_fullScreen"], self, triggered=self.fullsizeWindow))
        menu1.addAction(QAction(config.thisTranslation["menu1_resize"], self, triggered=self.twoThirdWindow))
        menu1.addSeparator()
        menu1.addAction(QAction(config.thisTranslation["menu1_topHalf"], self, triggered=self.halfScreenHeight))
        menu1.addAction(QAction(config.thisTranslation["menu1_leftHalf"], self, triggered=self.halfScreenWidth))
        menu1.addSeparator()
        menu1.addAction(QAction(config.thisTranslation["menu1_setDefaultFont"], self, triggered=self.setDefaultFont))
        menu1.addAction(QAction(config.thisTranslation["menu1_setChineseFont"], self, triggered=self.setChineseFont))
        menu1.addAction(QAction(config.thisTranslation["menu1_setAbbreviations"], self, triggered=self.setBibleAbbreviations))
        menu1.addAction(QAction(config.thisTranslation["menu1_tabNo"], self, triggered=self.setTabNumberDialog))
        menu1.addAction(QAction(config.thisTranslation["menu1_setMyFavouriteBible"], self, triggered=self.openFavouriteBibleDialog))
        menu1.addAction(QAction(config.thisTranslation["menu1_setMyLanguage"], self, triggered=self.openMyLanguageDialog))
        lexiconMenu = menu1.addMenu(config.thisTranslation["menu1_selectDefaultLexicon"])
        lexiconMenu.addAction(QAction(config.thisTranslation["menu1_StrongsHebrew"], self, triggered=self.openSelectDefaultStrongsHebrewLexiconDialog))
        lexiconMenu.addAction(QAction(config.thisTranslation["menu1_StrongsGreek"], self, triggered=self.openSelectDefaultStrongsGreekLexiconDialog))
        themeMenu = menu1.addMenu(config.thisTranslation["menu1_selectTheme"])
        themeMenu.addAction(QAction(config.thisTranslation["menu1_default_theme"], self, triggered=self.setDefaultTheme))
        themeMenu.addAction(QAction(config.thisTranslation["menu1_dark_theme"], self, triggered=self.setDarkTheme))
        menu1.addAction(QAction(config.thisTranslation["menu1_moreConfig"], self, triggered=self.moreConfigOptionsDialog))
        menu1.addSeparator()
        if (not self.isMyTranslationAvailable() and not self.isOfficialTranslationAvailable()) or (self.isMyTranslationAvailable() and not myTranslation.translationLanguage == config.userLanguage) or (self.isOfficialTranslationAvailable() and not config.translationLanguage == config.userLanguage):
            menu1.addAction(QAction(config.thisTranslation["menu1_translateInterface"], self, triggered=self.translateInterface))
        menu1.addAction(QAction(config.thisTranslation["menu1_toogleInterface"], self, triggered=self.toogleInterfaceTranslation))
        menu1.addSeparator()
        menu1.addAction(QAction(config.thisTranslation["menu1_update"], self, triggered=self.updateUniqueBibleApp))
        menu1.addSeparator()
        menu1.addAction(QAction(config.thisTranslation["menu1_remoteControl"], self, shortcut="Ctrl+O", triggered=self.manageRemoteControl))
        menu1.addSeparator()
        appIcon = QIcon(os.path.join("htmlResources", "theText.png"))
        quit_action = QAction(appIcon, config.thisTranslation["menu1_exit"], self, shortcut="Ctrl+Q", triggered=qApp.quit)
        menu1.addAction(quit_action)

        menu2 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu2_view"]))
        menu2.addAction(QAction(config.thisTranslation["menu2_all"], self, shortcut="Ctrl+J", triggered=self.setNoToolBar))
        menu2.addAction(QAction(config.thisTranslation["menu2_topOnly"], self, shortcut="Ctrl+G", triggered=self.hideShowAdditionalToolBar))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_top"], self, triggered=self.hideShowMainToolBar))
        menu2.addAction(QAction(config.thisTranslation["menu2_second"], self, triggered=self.hideShowSecondaryToolBar))
        menu2.addAction(QAction(config.thisTranslation["menu2_left"], self, triggered=self.hideShowLeftToolBar))
        menu2.addAction(QAction(config.thisTranslation["menu2_right"], self, triggered=self.hideShowRightToolBar))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_icons"], self, triggered=self.switchIconSize))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_landscape"], self, shortcut="Ctrl+L", triggered=self.switchLandscapeMode))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_study"], self, shortcut="Ctrl+W", triggered=self.parallel))
        menu2.addAction(QAction(config.thisTranslation["menu2_bottom"], self, shortcut="Ctrl+T", triggered=self.instant))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_hover"], self, shortcut="Ctrl+=", triggered=self.enableInstantButtonClicked))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_larger"], self, shortcut="Ctrl++", triggered=self.largerFont))
        menu2.addAction(QAction(config.thisTranslation["menu2_smaller"], self, shortcut="Ctrl+-", triggered=self.smallerFont))
        menu2.addSeparator()
        menu2.addAction(QAction(config.thisTranslation["menu2_format"], self, shortcut="Ctrl+P", triggered=self.enableParagraphButtonClicked))
        menu2.addAction(QAction(config.thisTranslation["menu2_subHeadings"], self, triggered=self.enableSubheadingButtonClicked))

        menu3 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu3_history"]))
        menu3.addAction(QAction(config.thisTranslation["menu3_main"], self, shortcut="Ctrl+'", triggered=self.mainHistoryButtonClicked))
        menu3.addAction(QAction(config.thisTranslation["menu3_mainBack"], self, shortcut="Ctrl+[", triggered=self.back))
        menu3.addAction(QAction(config.thisTranslation["menu3_mainForward"], self, shortcut="Ctrl+]", triggered=self.forward))
        menu3.addSeparator()
        menu3.addAction(QAction(config.thisTranslation["menu3_study"], self, shortcut = 'Ctrl+"', triggered=self.studyHistoryButtonClicked))
        menu3.addAction(QAction(config.thisTranslation["menu3_studyBack"], self, shortcut="Ctrl+{", triggered=self.studyBack))
        menu3.addAction(QAction(config.thisTranslation["menu3_studyForward"], self, shortcut="Ctrl+}", triggered=self.studyForward))
        menu3.addSeparator()
        menu3.addAction(QAction(config.thisTranslation["menu1_reload"], self, triggered=self.reloadCurrentRecord))

        menu4 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu4_further"]))
        menu4.addAction(QAction(config.thisTranslation["menu4_book"], self, triggered=self.bookFeatures))
        menu4.addAction(QAction(config.thisTranslation["menu4_chapter"], self, triggered=self.chapterFeatures))
        menu4.addSeparator()
        menu4.addAction(QAction(config.thisTranslation["menu4_next"], self, shortcut = 'Ctrl+>', triggered=self.nextMainChapter))
        menu4.addAction(QAction(config.thisTranslation["menu4_previous"], self, shortcut = 'Ctrl+<', triggered=self.previousMainChapter))
        menu4.addSeparator()
        menu4.addAction(QAction(config.thisTranslation["menu4_indexes"], self, shortcut="Ctrl+.", triggered=self.runINDEX))
        menu4.addAction(QAction(config.thisTranslation["menu4_commentary"], self, shortcut="Ctrl+Y", triggered=self.runCOMMENTARY))
        menu4.addSeparator()
        menu4.addAction(QAction(config.thisTranslation["menu4_traslations"], self, triggered=self.runTRANSLATION))
        menu4.addAction(QAction(config.thisTranslation["menu4_discourse"], self, triggered=self.runDISCOURSE))
        menu4.addAction(QAction(config.thisTranslation["menu4_words"], self, triggered=self.runWORDS))
        menu4.addAction(QAction(config.thisTranslation["menu4_tdw"], self, shortcut="Ctrl+K", triggered=self.runCOMBO))
        menu4.addSeparator()
        menu4.addAction(QAction(config.thisTranslation["menu4_crossRef"], self, shortcut="Ctrl+R", triggered=self.runCROSSREFERENCE))
        menu4.addAction(QAction(config.thisTranslation["menu4_tske"], self, shortcut="Ctrl+E", triggered=self.runTSKE))
        menu4.addSeparator()
        menu4.addAction(QAction(config.thisTranslation["menu4_compareAll"], self, shortcut="Ctrl+D", triggered=self.runCOMPARE))
        menu4.addSeparator()
        menu4.addAction(QAction(config.thisTranslation["menu4_moreComparison"], self, triggered=self.mainRefButtonClicked))

        # check if books in favourite list exist
        #for book in config.favouriteBooks:
            #if not os.path.isfile(os.path.join(config.marvelData, "books", "{0}.book".format(book))):
                #config.favouriteBooks.remove(book)

        # remove an old book from favourite list if it is not installed
        book = "Maps_ASB"
        if not os.path.isfile(os.path.join(config.marvelData, "books", "{0}.book".format(book))) and book in config.favouriteBooks:
            config.favouriteBooks.remove(book)

        menu10 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu10_books"]))
        if config.favouriteBooks:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[0]), self, triggered=self.openFavouriteBook0))
        if len(config.favouriteBooks) > 1:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[1]), self, triggered=self.openFavouriteBook1))
        if len(config.favouriteBooks) > 2:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[2]), self, triggered=self.openFavouriteBook2))
        if len(config.favouriteBooks) > 3:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[3]), self, triggered=self.openFavouriteBook3))
        if len(config.favouriteBooks) > 4:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[4]), self, triggered=self.openFavouriteBook4))
        if len(config.favouriteBooks) > 5:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[5]), self, triggered=self.openFavouriteBook5))
        if len(config.favouriteBooks) > 6:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[6]), self, triggered=self.openFavouriteBook6))
        if len(config.favouriteBooks) > 7:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[7]), self, triggered=self.openFavouriteBook7))
        if len(config.favouriteBooks) > 8:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[8]), self, triggered=self.openFavouriteBook8))
        if len(config.favouriteBooks) > 9:
            menu10.addAction(QAction(self.getBookName(config.favouriteBooks[9]), self, triggered=self.openFavouriteBook9))
        menu10.addSeparator()
        menu10.addAction(QAction(config.thisTranslation["menu5_book"], self, triggered=self.openBookMenu))
        menu10.addAction(QAction(config.thisTranslation["menu10_dialog"], self, triggered=self.openBookDialog))
        menu10.addSeparator()
        menu10.addAction(QAction(config.thisTranslation["menu10_addFavourite"], self, triggered=self.addFavouriteBookDialog))
        menu10.addSeparator()
        menu10.addAction(QAction(config.thisTranslation["menu10_bookFromImages"], self, triggered=self.createBookModuleFromImages))
        menu10.addAction(QAction(config.thisTranslation["menu10_bookFromHtml"], self, triggered=self.createBookModuleFromHTML))
        menu10.addAction(QAction(config.thisTranslation["menu10_bookFromNotes"], self, triggered=self.createBookModuleFromNotes))
        menu10.addSeparator()
        menu10.addAction(QAction(config.thisTranslation["menu10_clearBookHighlights"], self, triggered=self.clearBookHighlights))

        menu5 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu5_search"]))
        menu5.addAction(QAction(config.thisTranslation["menu5_main"], self, shortcut="Ctrl+1", triggered=self.displaySearchBibleCommand))
        menu5.addAction(QAction(config.thisTranslation["menu5_study"], self, shortcut="Ctrl+2", triggered=self.displaySearchStudyBibleCommand))
        menu5.addAction(QAction(config.thisTranslation["menu5_bible"], self, triggered=self.displaySearchBibleMenu))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_dictionary"], self, shortcut="Ctrl+3", triggered=self.searchCommandBibleDictionary))
        menu5.addAction(QAction(config.thisTranslation["context1_dict"], self, triggered=self.searchDictionaryDialog))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_encyclopedia"], self, shortcut="Ctrl+4", triggered=self.searchCommandBibleEncyclopedia))
        menu5.addAction(QAction(config.thisTranslation["context1_encyclopedia"], self, triggered=self.searchEncyclopediaDialog))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_book"], self, shortcut="Ctrl+5", triggered=self.displaySearchBookCommand))
        menu5.addAction(QAction(config.thisTranslation["menu5_selectBook"], self, triggered=self.searchBookDialog))
        menu5.addAction(QAction(config.thisTranslation["menu5_favouriteBook"], self, triggered=self.displaySearchFavBookCommand))
        menu5.addAction(QAction(config.thisTranslation["menu5_allBook"], self, triggered=self.displaySearchAllBookCommand))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_lastTopics"], self, shortcut="Ctrl+6", triggered=self.searchCommandBibleTopic))
        menu5.addAction(QAction(config.thisTranslation["menu5_topics"], self, triggered=self.searchTopicDialog))
        menu5.addAction(QAction(config.thisTranslation["menu5_allTopics"], self, triggered=self.searchCommandAllBibleTopic))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_characters"], self, shortcut="Ctrl+7", triggered=self.searchCommandBibleCharacter))
        menu5.addAction(QAction(config.thisTranslation["menu5_names"], self, shortcut="Ctrl+8", triggered=self.searchCommandBibleName))
        menu5.addAction(QAction(config.thisTranslation["menu5_locations"], self, shortcut="Ctrl+9", triggered=self.searchCommandBibleLocation))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_lexicon"], self, shortcut="Ctrl+0", triggered=self.searchCommandLexicon))
        menu5.addSeparator()
        menu5.addAction(QAction(config.thisTranslation["menu5_last3rdDict"], self, triggered=self.searchCommandThirdPartyDictionary))
        menu5.addAction(QAction(config.thisTranslation["menu5_3rdDict"], self, triggered=self.search3rdDictionaryDialog))

        menu6 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu6_notes"]))
        menu6.addAction(QAction(config.thisTranslation["menu6_mainChapter"], self, triggered=self.openMainChapterNote))
        menu6.addAction(QAction(config.thisTranslation["menu6_studyChapter"], self, triggered=self.openStudyChapterNote))
        menu6.addAction(QAction(config.thisTranslation["menu6_searchChapters"], self, triggered=self.searchCommandChapterNote))
        menu6.addSeparator()
        menu6.addAction(QAction(config.thisTranslation["menu6_mainVerse"], self, triggered=self.openMainVerseNote))
        menu6.addAction(QAction(config.thisTranslation["menu6_studyVerse"], self, triggered=self.openStudyVerseNote))
        menu6.addAction(QAction(config.thisTranslation["menu6_searchVerses"], self, triggered=self.searchCommandVerseNote))
        menu6.addSeparator()
        menu6.addAction(QAction(config.thisTranslation["menu10_clearBookHighlights"], self, triggered=self.clearNoteHighlights))

        menu7 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu7_topics"]))
        menu7.addAction(QAction(config.thisTranslation["menu7_create"], self, shortcut="Ctrl+N", triggered=self.createNewNoteFile))
        menu7.addAction(QAction(config.thisTranslation["menu7_open"], self, triggered=self.openTextFileDialog))
        menu7.addSeparator()
        menu7.addAction(QAction(config.thisTranslation["menu7_read"], self, triggered=self.externalFileButtonClicked))
        menu7.addAction(QAction(config.thisTranslation["menu7_edit"], self, triggered=self.editExternalFileButtonClicked))
        menu7.addSeparator()
        menu7.addAction(QAction(config.thisTranslation["menu7_recent"], self, triggered=self.openExternalFileHistory))
        menu7.addSeparator()
        menu7.addAction(QAction(config.thisTranslation["menu7_paste"], self, shortcut="Ctrl+^", triggered=self.pasteFromClipboard))

        menu11 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu11_multimedia"]))
        menu11.addAction(QAction(config.thisTranslation["menu11_images"], self, triggered=self.openImagesFolder))
        menu11.addAction(QAction(config.thisTranslation["menu11_music"], self, triggered=self.openMusicFolder))
        menu11.addAction(QAction(config.thisTranslation["menu11_video"], self, triggered=self.openVideoFolder))
        menu11.addSeparator()
        menu11.addAction(QAction(config.thisTranslation["menu11_setupDownload"], self, triggered=self.setupYouTube))
        menu11.addAction(QAction(config.thisTranslation["menu11_youtube"], self, triggered=self.openYouTube))
        menu11.addSeparator()
        menu11.addAction(QAction("YouTube -> mp3", self, triggered=self.downloadMp3Dialog))
        menu11.addAction(QAction("YouTube -> mp4", self, triggered=self.downloadMp4Dialog))

        menu8 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu8_resources"]))
        menu8.addAction(QAction(config.thisTranslation["menu8_marvelData"], self, triggered=self.openMarvelDataFolder))
        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["menu8_bibles"], self, triggered=self.installMarvelBibles))
        menu8.addAction(QAction(config.thisTranslation["menu8_commentaries"], self, triggered=self.installMarvelCommentaries))
        menu8.addAction(QAction(config.thisTranslation["menu8_datasets"], self, triggered=self.installMarvelDatasets))
        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["menu8_plusLexicons"], self, triggered=self.importBBPlusLexiconInAFolder))
        menu8.addAction(QAction(config.thisTranslation["menu8_plusDictionaries"], self, triggered=self.importBBPlusDictionaryInAFolder))
        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["menu8_download3rdParty"], self, triggered=self.moreBooks))
        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["menu8_3rdParty"], self, triggered=self.importModules))
        menu8.addAction(QAction(config.thisTranslation["menu8_3rdPartyInFolder"], self, triggered=self.importModulesInFolder))
        menu8.addAction(QAction(config.thisTranslation["menu8_settings"], self, triggered=self.importSettingsDialog))
        menu8.addSeparator()
        menu8.addAction(QAction(config.thisTranslation["menu8_tagFile"], self, triggered=self.tagFile))
        menu8.addAction(QAction(config.thisTranslation["menu8_tagFiles"], self, triggered=self.tagFiles))
        menu8.addAction(QAction(config.thisTranslation["menu8_tagFolder"], self, triggered=self.tagFolder))

        if config.showInformation:
            menu9 = self.menuBar().addMenu("&{0}".format(config.thisTranslation["menu9_information"]))
            menu9.addAction(QAction(config.thisTranslation["menu1_wikiPages"], self, triggered=self.openUbaWiki))
            menu9.addSeparator()
            menu9.addAction(QAction("BibleTools.app", self, triggered=self.openBibleTools))
            menu9.addAction(QAction("UniqueBible.app", self, triggered=self.openUniqueBible))
            menu9.addAction(QAction("Marvel.bible", self, triggered=self.openMarvelBible))
            menu9.addAction(QAction("BibleBento.com", self, triggered=self.openBibleBento))
            menu9.addAction(QAction("OpenGNT.com", self, triggered=self.openOpenGNT))
            menu9.addSeparator()
            menu9.addAction(QAction("GitHub Repositories", self, triggered=self.openSource))
            menu9.addAction(QAction("Unique Bible", self, triggered=self.openUniqueBibleSource))
            menu9.addAction(QAction("Open Hebrew Bible", self, triggered=self.openHebrewBibleSource))
            menu9.addAction(QAction("Open Greek New Testament", self, triggered=self.openOpenGNTSource))
            #menu9.addSeparator()
            #menu9.addAction(QAction(config.thisTranslation["menu9_credits"], self, triggered=self.openCredits))
            menu9.addSeparator()
            menu9.addAction(QAction("MarvelBible.Slack.com", self, triggered=self.goToSlack))
            menu9.addAction(QAction(config.thisTranslation["menu9_contact"], self, triggered=self.contactEliranWong))
            menu9.addSeparator()
            menu9.addAction(QAction(config.thisTranslation["menu9_donate"], self, triggered=self.donateToUs))

        # testing
        if config.testing:
            menu999 = self.menuBar().addMenu("&Testing")
            menu999.addAction(QAction("Download Google Static Maps", self, triggered=self.downloadGoogleStaticMaps))

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
            fullUrl =  "{0}center={1},{2}&zoom={3}&size={4}&key={5}&scale={6}&markers=color:red%7Clabel:{7}%7C{1},{2}".format(url, lat, lng, zoom, size, config.myGoogleApiKey, scale, location[0])
            r = requests.get(fullUrl)
            # wb mode is stand for write binary mode
            filepath = os.path.join("htmlResources", "images", "exlbl_largeHD", "{0}.png".format(entry))
            with open(filepath, "wb") as f:
                # r.content gives content,
                # in this case gives image
                f.write(r.content)
        print("done")

    def setupToolBar(self):
        if config.toolBarIconFullSize:
            self.setupToolBarFullIconSize()
        else:
            self.setupToolBarStandardIconSize()

    def setupToolBarStandardIconSize(self):

        textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"

        self.firstToolBar = QToolBar()
        self.firstToolBar.setWindowTitle(config.thisTranslation["bar1_title"])
        self.firstToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.firstToolBar)

        self.mainTextMenuButton = QPushButton(self.verseReference("main")[0])
        self.mainTextMenuButton.setToolTip(config.thisTranslation["bar1_menu"])
        self.mainTextMenuButton.setStyleSheet(textButtonStyle)
        self.mainTextMenuButton.clicked.connect(self.mainTextMenu)
        self.firstToolBar.addWidget(self.mainTextMenuButton)

        self.mainRefButton = QPushButton(self.verseReference("main")[1])
        self.mainRefButton.setToolTip(config.thisTranslation["bar1_reference"])
        self.mainRefButton.setStyleSheet(textButtonStyle)
        self.mainRefButton.clicked.connect(self.mainRefButtonClicked)
        self.firstToolBar.addWidget(self.mainRefButton)

        openChapterNoteButton = QPushButton()
        #openChapterNoteButton.setFixedSize(40, 40)
        #openChapterNoteButton.setBaseSize(70, 70)
        openChapterNoteButton.setToolTip(config.thisTranslation["bar1_chapterNotes"])
        openChapterNoteButtonFile = os.path.join("htmlResources", "noteChapter.png")
        openChapterNoteButton.setIcon(QIcon(openChapterNoteButtonFile))
        openChapterNoteButton.clicked.connect(self.openMainChapterNote)
        self.firstToolBar.addWidget(openChapterNoteButton)
        #t = self.firstToolBar.addAction(QIcon(openChapterNoteButtonFile), "Main View Chapter Notes", self.openMainChapterNote)
        #openChapterNoteButtonFile = os.path.join("htmlResources", "search.png")
        #t.setIcon(QIcon(openChapterNoteButtonFile))

        openVerseNoteButton = QPushButton()
        openVerseNoteButton.setToolTip(config.thisTranslation["bar1_verseNotes"])
        openVerseNoteButtonFile = os.path.join("htmlResources", "noteVerse.png")
        openVerseNoteButton.setIcon(QIcon(openVerseNoteButtonFile))
        openVerseNoteButton.clicked.connect(self.openMainVerseNote)
        self.firstToolBar.addWidget(openVerseNoteButton)

        searchBibleButton = QPushButton()
        searchBibleButton.setToolTip(config.thisTranslation["bar1_searchBible"])
        searchBibleButtonFile = os.path.join("htmlResources", "search.png")
        searchBibleButton.setIcon(QIcon(searchBibleButtonFile))
        searchBibleButton.clicked.connect(self.displaySearchBibleCommand)
        self.firstToolBar.addWidget(searchBibleButton)

        searchBibleButton = QPushButton()
        searchBibleButton.setToolTip(config.thisTranslation["bar1_searchBibles"])
        searchBibleButtonFile = os.path.join("htmlResources", "search_plus.png")
        searchBibleButton.setIcon(QIcon(searchBibleButtonFile))
        searchBibleButton.clicked.connect(self.displaySearchBibleMenu)
        self.firstToolBar.addWidget(searchBibleButton)

        self.firstToolBar.addSeparator()

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.setToolTip(config.thisTranslation["bar1_command"])
        self.textCommandLineEdit.setMinimumWidth(100)
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        self.firstToolBar.addWidget(self.textCommandLineEdit)

        self.firstToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["bar1_toolbars"])
        actionButtonFile = os.path.join("htmlResources", "toolbar.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.hideShowAdditionalToolBar)
        self.firstToolBar.addWidget(actionButton)

        self.addToolBarBreak()

        self.studyBibleToolBar = QToolBar()
        self.studyBibleToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.studyBibleToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.studyBibleToolBar)

        self.studyTextMenuButton = QPushButton(self.verseReference("study")[0])
        self.studyTextMenuButton.setToolTip(config.thisTranslation["bar2_menu"])
        self.studyTextMenuButton.setStyleSheet(textButtonStyle)
        self.studyTextMenuButton.clicked.connect(self.studyTextMenu)
        self.studyBibleToolBar.addWidget(self.studyTextMenuButton)

        self.studyRefButton = QPushButton(self.verseReference("study")[1])
        self.studyRefButton.setToolTip(config.thisTranslation["bar2_reference"])
        self.studyRefButton.setStyleSheet(textButtonStyle)
        self.studyRefButton.clicked.connect(self.studyRefButtonClicked)
        self.studyBibleToolBar.addWidget(self.studyRefButton)

        openStudyChapterNoteButton = QPushButton()
        openStudyChapterNoteButton.setToolTip(config.thisTranslation["bar2_chapterNotes"])
        openStudyChapterNoteButtonFile = os.path.join("htmlResources", "noteChapter.png")
        openStudyChapterNoteButton.setIcon(QIcon(openStudyChapterNoteButtonFile))
        openStudyChapterNoteButton.clicked.connect(self.openStudyChapterNote)
        self.studyBibleToolBar.addWidget(openStudyChapterNoteButton)

        openStudyVerseNoteButton = QPushButton()
        openStudyVerseNoteButton.setToolTip(config.thisTranslation["bar2_verseNotes"])
        openStudyVerseNoteButtonFile = os.path.join("htmlResources", "noteVerse.png")
        openStudyVerseNoteButton.setIcon(QIcon(openStudyVerseNoteButtonFile))
        openStudyVerseNoteButton.clicked.connect(self.openStudyVerseNote)
        self.studyBibleToolBar.addWidget(openStudyVerseNoteButton)

        searchStudyBibleButton = QPushButton()
        searchStudyBibleButton.setToolTip(config.thisTranslation["bar2_searchBible"])
        searchStudyBibleButtonFile = os.path.join("htmlResources", "search.png")
        searchStudyBibleButton.setIcon(QIcon(searchStudyBibleButtonFile))
        searchStudyBibleButton.clicked.connect(self.displaySearchStudyBibleCommand)
        self.studyBibleToolBar.addWidget(searchStudyBibleButton)

        searchStudyBibleButton = QPushButton()
        searchStudyBibleButton.setToolTip(config.thisTranslation["bar2_searchBibles"])
        searchStudyBibleButtonFile = os.path.join("htmlResources", "search_plus.png")
        searchStudyBibleButton.setIcon(QIcon(searchStudyBibleButtonFile))
        searchStudyBibleButton.clicked.connect(self.displaySearchBibleMenu)
        self.studyBibleToolBar.addWidget(searchStudyBibleButton)

        self.enableSyncStudyWindowBibleButton = QPushButton()
        self.enableSyncStudyWindowBibleButton.setToolTip(self.getSyncStudyWindowBibleDisplayToolTip())
        enableSyncStudyWindowBibleButtonFile = os.path.join("htmlResources", self.getSyncStudyWindowBibleDisplay())
        self.enableSyncStudyWindowBibleButton.setIcon(QIcon(enableSyncStudyWindowBibleButtonFile))
        self.enableSyncStudyWindowBibleButton.clicked.connect(self.enableSyncStudyWindowBibleButtonClicked)
        self.studyBibleToolBar.addWidget(self.enableSyncStudyWindowBibleButton)

        self.secondToolBar = QToolBar()
        self.secondToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.secondToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.secondToolBar)

        self.enableStudyBibleButton = QPushButton()
        self.enableStudyBibleButton.setToolTip(self.getStudyBibleDisplayToolTip())
        enableStudyBibleButtonFile = os.path.join("htmlResources", self.getStudyBibleDisplay())
        self.enableStudyBibleButton.setIcon(QIcon(enableStudyBibleButtonFile))
        self.enableStudyBibleButton.clicked.connect(self.enableStudyBibleButtonClicked)
        self.secondToolBar.addWidget(self.enableStudyBibleButton)

        self.secondToolBar.addSeparator()

        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
        self.commentaryRefButton.setToolTip(config.thisTranslation["menu4_commentary"])
        self.commentaryRefButton.setStyleSheet(textButtonStyle)
        self.commentaryRefButton.clicked.connect(self.commentaryRefButtonClicked)
        self.secondToolBar.addWidget(self.commentaryRefButton)

        self.enableSyncCommentaryButton = QPushButton()
        self.enableSyncCommentaryButton.setToolTip(self.getSyncCommentaryDisplayToolTip())
        enableSyncCommentaryButtonFile = os.path.join("htmlResources", self.getSyncCommentaryDisplay())
        self.enableSyncCommentaryButton.setIcon(QIcon(enableSyncCommentaryButtonFile))
        self.enableSyncCommentaryButton.clicked.connect(self.enableSyncCommentaryButtonClicked)
        self.secondToolBar.addWidget(self.enableSyncCommentaryButton)

        self.secondToolBar.addSeparator()

        openFileButton = QPushButton()
        openFileButton.setToolTip(config.thisTranslation["menu10_dialog"])
        openFileButtonFile = os.path.join("htmlResources", "open.png")
        openFileButton.setIcon(QIcon(openFileButtonFile))
        openFileButton.clicked.connect(self.openBookDialog)
        self.secondToolBar.addWidget(openFileButton)

        self.bookButton = QPushButton(config.book)
        self.bookButton.setToolTip(config.thisTranslation["menu5_book"])
        self.bookButton.setStyleSheet(textButtonStyle)
        self.bookButton.clicked.connect(self.openBookMenu)
        self.secondToolBar.addWidget(self.bookButton)

        searchBookButton = QPushButton()
        searchBookButton.setToolTip(config.thisTranslation["bar2_searchBooks"])
        searchBookButtonFile = os.path.join("htmlResources", "search.png")
        searchBookButton.setIcon(QIcon(searchBookButtonFile))
        searchBookButton.clicked.connect(self.displaySearchBookCommand)
        self.secondToolBar.addWidget(searchBookButton)

        self.secondToolBar.addSeparator()

        newFileButton = QPushButton()
        newFileButton.setToolTip(config.thisTranslation["menu7_create"])
        newFileButtonFile = os.path.join("htmlResources", "newfile.png")
        newFileButton.setIcon(QIcon(newFileButtonFile))
        newFileButton.clicked.connect(self.createNewNoteFile)
        self.secondToolBar.addWidget(newFileButton)

        openFileButton = QPushButton()
        openFileButton.setToolTip(config.thisTranslation["menu7_open"])
        openFileButtonFile = os.path.join("htmlResources", "open.png")
        openFileButton.setIcon(QIcon(openFileButtonFile))
        openFileButton.clicked.connect(self.openTextFileDialog)
        self.secondToolBar.addWidget(openFileButton)

        self.externalFileButton = QPushButton(self.getLastExternalFileName())
        self.externalFileButton.setToolTip(config.thisTranslation["menu7_read"])
        self.externalFileButton.setStyleSheet(textButtonStyle)
        self.externalFileButton.clicked.connect(self.externalFileButtonClicked)
        self.secondToolBar.addWidget(self.externalFileButton)

        editExternalFileButton = QPushButton()
        editExternalFileButton.setToolTip(config.thisTranslation["menu7_edit"])
        editExternalFileButtonFile = os.path.join("htmlResources", "edit.png")
        editExternalFileButton.setIcon(QIcon(editExternalFileButtonFile))
        editExternalFileButton.clicked.connect(self.editExternalFileButtonClicked)
        self.secondToolBar.addWidget(editExternalFileButton)

        self.secondToolBar.addSeparator()

        fontMinusButton = QPushButton()
        fontMinusButton.setToolTip(config.thisTranslation["menu2_smaller"])
        fontMinusButtonFile = os.path.join("htmlResources", "fontMinus.png")
        fontMinusButton.setIcon(QIcon(fontMinusButtonFile))
        fontMinusButton.clicked.connect(self.smallerFont)
        self.secondToolBar.addWidget(fontMinusButton)

        self.defaultFontButton = QPushButton("{0} {1}".format(config.font, config.fontSize))
        self.defaultFontButton.setToolTip(config.thisTranslation["menu1_setDefaultFont"])
        self.defaultFontButton.setStyleSheet(textButtonStyle)
        self.defaultFontButton.clicked.connect(self.setDefaultFont)
        self.secondToolBar.addWidget(self.defaultFontButton)

        fontPlusButton = QPushButton()
        fontPlusButton.setToolTip(config.thisTranslation["menu2_larger"])
        fontPlusButtonFile = os.path.join("htmlResources", "fontPlus.png")
        fontPlusButton.setIcon(QIcon(fontPlusButtonFile))
        fontPlusButton.clicked.connect(self.largerFont)
        self.secondToolBar.addWidget(fontPlusButton)

        self.secondToolBar.addSeparator()

        youtubeButton = QPushButton()
        youtubeButton.setToolTip(config.thisTranslation["menu11_youtube"])
        youtubeButtonFile = os.path.join("htmlResources", "youtube.png")
        youtubeButton.setIcon(QIcon(youtubeButtonFile))
        youtubeButton.clicked.connect(self.openYouTube)
        self.secondToolBar.addWidget(youtubeButton)

        self.secondToolBar.addSeparator()

        reloadButton = QPushButton()
        reloadButton.setToolTip(config.thisTranslation["menu1_reload"])
        reloadButtonFile = os.path.join("htmlResources", "reload.png")
        reloadButton.setIcon(QIcon(reloadButtonFile))
        reloadButton.clicked.connect(self.reloadCurrentRecord)
        self.secondToolBar.addWidget(reloadButton)

        self.secondToolBar.addSeparator()

        self.leftToolBar = QToolBar()
        self.leftToolBar.setWindowTitle(config.thisTranslation["bar3_title"])
        self.leftToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.LeftToolBarArea, self.leftToolBar)

        backButton = QPushButton()
        backButton.setToolTip(config.thisTranslation["menu3_mainBack"])
        leftButtonFile = os.path.join("htmlResources", "left.png")
        backButton.setIcon(QIcon(leftButtonFile))
        backButton.clicked.connect(self.back)
        self.leftToolBar.addWidget(backButton)

        mainHistoryButton = QPushButton()
        mainHistoryButton.setToolTip(config.thisTranslation["menu3_main"])
        mainHistoryButtonFile = os.path.join("htmlResources", "history.png")
        mainHistoryButton.setIcon(QIcon(mainHistoryButtonFile))
        mainHistoryButton.clicked.connect(self.mainHistoryButtonClicked)
        self.leftToolBar.addWidget(mainHistoryButton)

        forwardButton = QPushButton()
        forwardButton.setToolTip(config.thisTranslation["menu3_mainForward"])
        rightButtonFile = os.path.join("htmlResources", "right.png")
        forwardButton.setIcon(QIcon(rightButtonFile))
        forwardButton.clicked.connect(self.forward)
        self.leftToolBar.addWidget(forwardButton)

        self.leftToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["bar3_pdf"])
        actionButtonFile = os.path.join("htmlResources", "pdf.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.printMainPage)
        self.leftToolBar.addWidget(actionButton)

        self.leftToolBar.addSeparator()

        self.enableParagraphButton = QPushButton()
        self.enableParagraphButton.setToolTip(config.thisTranslation["menu2_format"])
        enableParagraphButtonFile = os.path.join("htmlResources", self.getReadFormattedBibles())
        self.enableParagraphButton.setIcon(QIcon(enableParagraphButtonFile))
        self.enableParagraphButton.clicked.connect(self.enableParagraphButtonClicked)
        self.leftToolBar.addWidget(self.enableParagraphButton)

        self.enableSubheadingButton = QPushButton()
        self.enableSubheadingButton.setToolTip(config.thisTranslation["menu2_subHeadings"])
        enableSubheadingButtonFile = os.path.join("htmlResources", self.getAddSubheading())
        self.enableSubheadingButton.setIcon(QIcon(enableSubheadingButtonFile))
        self.enableSubheadingButton.clicked.connect(self.enableSubheadingButtonClicked)
        self.leftToolBar.addWidget(self.enableSubheadingButton)

        self.leftToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_previous"])
        actionButtonFile = os.path.join("htmlResources", "previousChapter.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.previousMainChapter)
        self.leftToolBar.addWidget(actionButton)

#        actionButton = QPushButton()
#        actionButton.setToolTip(config.thisTranslation["bar1_reference"])
#        actionButtonFile = os.path.join("htmlResources", "bible.png")
#        actionButton.setIcon(QIcon(actionButtonFile))
#        actionButton.clicked.connect(self.openMainChapter)
#        self.leftToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_next"])
        actionButtonFile = os.path.join("htmlResources", "nextChapter.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.nextMainChapter)
        self.leftToolBar.addWidget(actionButton)

        self.leftToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_compareAll"])
        actionButtonFile = os.path.join("htmlResources", "compare_with.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runCOMPARE)
        self.leftToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_moreComparison"])
        actionButtonFile = os.path.join("htmlResources", "parallel_with.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.mainRefButtonClicked)
        self.leftToolBar.addWidget(actionButton)

        self.leftToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip("Marvel Original Bible")
        actionButtonFile = os.path.join("htmlResources", "original.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runMOB)
        self.leftToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip("Marvel Interlinear Bible")
        actionButtonFile = os.path.join("htmlResources", "interlinear.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runMIB)
        self.leftToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip("Marvel Trilingual Bible")
        actionButtonFile = os.path.join("htmlResources", "trilingual.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runMTB)
        self.leftToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip("Marvel Parallel Bible")
        actionButtonFile = os.path.join("htmlResources", "line.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runMPB)
        self.leftToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip("Marvel Annotated Bible")
        actionButtonFile = os.path.join("htmlResources", "annotated.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runMAB)
        self.leftToolBar.addWidget(actionButton)

        self.leftToolBar.addSeparator()

        self.rightToolBar = QToolBar()
        self.rightToolBar.setWindowTitle(config.thisTranslation["bar4_title"])
        self.rightToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.RightToolBarArea, self.rightToolBar)

        studyBackButton = QPushButton()
        studyBackButton.setToolTip(config.thisTranslation["menu3_studyBack"])
        leftButtonFile = os.path.join("htmlResources", "left.png")
        studyBackButton.setIcon(QIcon(leftButtonFile))
        studyBackButton.clicked.connect(self.studyBack)
        self.rightToolBar.addWidget(studyBackButton)

        studyHistoryButton = QPushButton()
        studyHistoryButton.setToolTip(config.thisTranslation["menu3_study"])
        studyHistoryButtonFile = os.path.join("htmlResources", "history.png")
        studyHistoryButton.setIcon(QIcon(studyHistoryButtonFile))
        studyHistoryButton.clicked.connect(self.studyHistoryButtonClicked)
        self.rightToolBar.addWidget(studyHistoryButton)

        studyForwardButton = QPushButton()
        studyForwardButton.setToolTip(config.thisTranslation["menu3_studyForward"])
        rightButtonFile = os.path.join("htmlResources", "right.png")
        studyForwardButton.setIcon(QIcon(rightButtonFile))
        studyForwardButton.clicked.connect(self.studyForward)
        self.rightToolBar.addWidget(studyForwardButton)

        self.rightToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["bar3_pdf"])
        actionButtonFile = os.path.join("htmlResources", "pdf.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.printStudyPage)
        self.rightToolBar.addWidget(actionButton)

        self.rightToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_indexes"])
        actionButtonFile = os.path.join("htmlResources", "indexes.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runINDEX)
        self.rightToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_commentary"])
        actionButtonFile = os.path.join("htmlResources", "commentary.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runCOMMENTARY)
        self.rightToolBar.addWidget(actionButton)

        self.rightToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_crossRef"])
        actionButtonFile = os.path.join("htmlResources", "cross_reference.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runCROSSREFERENCE)
        self.rightToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_tske"])
        actionButtonFile = os.path.join("htmlResources", "treasure.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runTSKE)
        self.rightToolBar.addWidget(actionButton)

        self.rightToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_traslations"])
        actionButtonFile = os.path.join("htmlResources", "translations.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runTRANSLATION)
        self.rightToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_discourse"])
        actionButtonFile = os.path.join("htmlResources", "discourse.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runDISCOURSE)
        self.rightToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_words"])
        actionButtonFile = os.path.join("htmlResources", "words.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runWORDS)
        self.rightToolBar.addWidget(actionButton)

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu4_tdw"])
        actionButtonFile = os.path.join("htmlResources", "combo.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.runCOMBO)
        self.rightToolBar.addWidget(actionButton)

        self.rightToolBar.addSeparator()

        actionButton = QPushButton()
        actionButton.setToolTip(config.thisTranslation["menu2_landscape"])
        actionButtonFile = os.path.join("htmlResources", "portrait.png")
        actionButton.setIcon(QIcon(actionButtonFile))
        actionButton.clicked.connect(self.switchLandscapeMode)
        self.rightToolBar.addWidget(actionButton)

        parallelButton = QPushButton()
        parallelButton.setToolTip(config.thisTranslation["menu2_study"])
        parallelButtonFile = os.path.join("htmlResources", "parallel.png")
        parallelButton.setIcon(QIcon(parallelButtonFile))
        parallelButton.clicked.connect(self.parallel)
        self.rightToolBar.addWidget(parallelButton)

        self.rightToolBar.addSeparator()

        self.enableInstantButton = QPushButton()
        self.enableInstantButton.setToolTip(config.thisTranslation["menu2_hover"])
        enableInstantButtonFile = os.path.join("htmlResources", self.getInstantInformation())
        self.enableInstantButton.setIcon(QIcon(enableInstantButtonFile))
        self.enableInstantButton.clicked.connect(self.enableInstantButtonClicked)
        self.rightToolBar.addWidget(self.enableInstantButton)

        instantButton = QPushButton()
        instantButton.setToolTip(config.thisTranslation["menu2_bottom"])
        instantButtonFile = os.path.join("htmlResources", "lightning.png")
        instantButton.setIcon(QIcon(instantButtonFile))
        instantButton.clicked.connect(self.instant)
        self.rightToolBar.addWidget(instantButton)

        self.rightToolBar.addSeparator()

    def setupToolBarFullIconSize(self):

        textButtonStyle = "QPushButton {background-color: #151B54; color: white;} QPushButton:hover {background-color: #333972;} QPushButton:pressed { background-color: #515790;}"

        self.firstToolBar = QToolBar()
        self.firstToolBar.setWindowTitle(config.thisTranslation["bar1_title"])
        self.firstToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.firstToolBar)

        self.mainTextMenuButton = QPushButton(self.verseReference("main")[0])
        self.mainTextMenuButton.setToolTip(config.thisTranslation["bar1_menu"])
        self.mainTextMenuButton.setStyleSheet(textButtonStyle)
        self.mainTextMenuButton.clicked.connect(self.mainTextMenu)
        self.firstToolBar.addWidget(self.mainTextMenuButton)

        self.mainRefButton = QPushButton(self.verseReference("main")[1])
        self.mainRefButton.setToolTip(config.thisTranslation["bar1_reference"])
        self.mainRefButton.setStyleSheet(textButtonStyle)
        self.mainRefButton.clicked.connect(self.mainRefButtonClicked)
        self.firstToolBar.addWidget(self.mainRefButton)

        iconFile = os.path.join("htmlResources", "noteChapter.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_chapterNotes"], self.openMainChapterNote)

        iconFile = os.path.join("htmlResources", "noteVerse.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_verseNotes"], self.openMainVerseNote)

        iconFile = os.path.join("htmlResources", "search.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_searchBible"], self.displaySearchBibleCommand)

        iconFile = os.path.join("htmlResources", "search_plus.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_searchBibles"], self.displaySearchBibleMenu)

        self.firstToolBar.addSeparator()

        self.textCommandLineEdit = QLineEdit()
        self.textCommandLineEdit.setToolTip(config.thisTranslation["bar1_command"])
        self.textCommandLineEdit.setMinimumWidth(100)
        self.textCommandLineEdit.returnPressed.connect(self.textCommandEntered)
        self.firstToolBar.addWidget(self.textCommandLineEdit)

        self.firstToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "toolbar.png")
        self.firstToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar1_toolbars"], self.hideShowAdditionalToolBar)

        self.addToolBarBreak()

        self.studyBibleToolBar = QToolBar()
        self.studyBibleToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.studyBibleToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.studyBibleToolBar)

        self.studyTextMenuButton = QPushButton(self.verseReference("study")[0])
        self.studyTextMenuButton.setToolTip(config.thisTranslation["bar2_menu"])
        self.studyTextMenuButton.setStyleSheet(textButtonStyle)
        self.studyTextMenuButton.clicked.connect(self.studyTextMenu)
        self.studyBibleToolBar.addWidget(self.studyTextMenuButton)

        self.studyRefButton = QPushButton(self.verseReference("study")[1])
        self.studyRefButton.setToolTip(config.thisTranslation["bar2_reference"])
        self.studyRefButton.setStyleSheet(textButtonStyle)
        self.studyRefButton.clicked.connect(self.studyRefButtonClicked)
        self.studyBibleToolBar.addWidget(self.studyRefButton)

        iconFile = os.path.join("htmlResources", "noteChapter.png")
        self.studyBibleToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar2_chapterNotes"], self.openStudyChapterNote)

        iconFile = os.path.join("htmlResources", "noteVerse.png")
        self.studyBibleToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar2_verseNotes"], self.openStudyVerseNote)

        iconFile = os.path.join("htmlResources", "search.png")
        self.studyBibleToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar2_searchBible"], self.displaySearchStudyBibleCommand)

        iconFile = os.path.join("htmlResources", "search_plus.png")
        self.studyBibleToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar2_searchBibles"], self.displaySearchBibleMenu)

        iconFile = os.path.join("htmlResources", self.getSyncStudyWindowBibleDisplay())
        self.enableSyncStudyWindowBibleButton = self.studyBibleToolBar.addAction(QIcon(iconFile), self.getSyncStudyWindowBibleDisplayToolTip(), self.enableSyncStudyWindowBibleButtonClicked)

        self.secondToolBar = QToolBar()
        self.secondToolBar.setWindowTitle(config.thisTranslation["bar2_title"])
        self.secondToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(self.secondToolBar)

        iconFile = os.path.join("htmlResources", self.getStudyBibleDisplay())
        self.enableStudyBibleButton = self.secondToolBar.addAction(QIcon(iconFile), self.getStudyBibleDisplayToolTip(), self.enableStudyBibleButtonClicked)

        self.secondToolBar.addSeparator()

        self.commentaryRefButton = QPushButton(self.verseReference("commentary"))
        self.commentaryRefButton.setToolTip(config.thisTranslation["menu4_commentary"])
        self.commentaryRefButton.setStyleSheet(textButtonStyle)
        self.commentaryRefButton.clicked.connect(self.commentaryRefButtonClicked)
        self.secondToolBar.addWidget(self.commentaryRefButton)

        iconFile = os.path.join("htmlResources", self.getSyncCommentaryDisplay())
        self.enableSyncCommentaryButton = self.secondToolBar.addAction(QIcon(iconFile), self.getSyncCommentaryDisplayToolTip(), self.enableSyncCommentaryButtonClicked)

        self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "open.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu10_dialog"], self.openBookDialog)

        self.bookButton = QPushButton(config.book)
        self.bookButton.setToolTip(config.thisTranslation["menu5_book"])
        self.bookButton.setStyleSheet(textButtonStyle)
        self.bookButton.clicked.connect(self.openBookMenu)
        self.secondToolBar.addWidget(self.bookButton)

        iconFile = os.path.join("htmlResources", "search.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar2_searchBooks"], self.displaySearchBookCommand)

        self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "newfile.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu7_create"], self.createNewNoteFile)

        iconFile = os.path.join("htmlResources", "open.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu7_open"], self.openTextFileDialog)

        self.externalFileButton = QPushButton(self.getLastExternalFileName())
        self.externalFileButton.setToolTip(config.thisTranslation["menu7_read"])
        self.externalFileButton.setStyleSheet(textButtonStyle)
        self.externalFileButton.clicked.connect(self.externalFileButtonClicked)
        self.secondToolBar.addWidget(self.externalFileButton)

        iconFile = os.path.join("htmlResources", "edit.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu7_edit"], self.editExternalFileButtonClicked)

        self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "fontMinus.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_smaller"], self.smallerFont)

        self.defaultFontButton = QPushButton("{0} {1}".format(config.font, config.fontSize))
        self.defaultFontButton.setToolTip(config.thisTranslation["menu1_setDefaultFont"])
        self.defaultFontButton.setStyleSheet(textButtonStyle)
        self.defaultFontButton.clicked.connect(self.setDefaultFont)
        self.secondToolBar.addWidget(self.defaultFontButton)

        iconFile = os.path.join("htmlResources", "fontPlus.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_larger"], self.largerFont)

        self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "youtube.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu11_youtube"], self.openYouTube)

        self.secondToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "reload.png")
        self.secondToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu1_reload"], self.reloadCurrentRecord)

        self.secondToolBar.addSeparator()

        self.leftToolBar = QToolBar()
        self.leftToolBar.setWindowTitle(config.thisTranslation["bar3_title"])
        self.leftToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.LeftToolBarArea, self.leftToolBar)

        iconFile = os.path.join("htmlResources", "left.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_mainBack"], self.back)

        iconFile = os.path.join("htmlResources", "history.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_main"], self.mainHistoryButtonClicked)

        iconFile = os.path.join("htmlResources", "right.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_mainForward"], self.forward)

        self.leftToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "pdf.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar3_pdf"], self.printMainPage)

        self.leftToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", self.getReadFormattedBibles())
        self.enableParagraphButton = self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_format"], self.enableParagraphButtonClicked)

        iconFile = os.path.join("htmlResources", self.getAddSubheading())
        self.enableSubheadingButton = self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_subHeadings"], self.enableSubheadingButtonClicked)

        self.leftToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "previousChapter.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_previous"], self.previousMainChapter)

#        actionButton = QPushButton()
#        actionButton.setToolTip(config.thisTranslation["bar1_reference"])
#        actionButtonFile = os.path.join("htmlResources", "bible.png")
#        actionButton.setIcon(QIcon(actionButtonFile))
#        actionButton.clicked.connect(self.openMainChapter)
#        self.leftToolBar.addWidget(actionButton)

        iconFile = os.path.join("htmlResources", "nextChapter.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_next"], self.nextMainChapter)

        self.leftToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "compare_with.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_compareAll"], self.runCOMPARE)

        iconFile = os.path.join("htmlResources", "parallel_with.png")
        self.leftToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_moreComparison"], self.mainRefButtonClicked)

        self.leftToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "original.png")
        self.leftToolBar.addAction(QIcon(iconFile), "Marvel Original Bible", self.runMOB)

        iconFile = os.path.join("htmlResources", "interlinear.png")
        self.leftToolBar.addAction(QIcon(iconFile), "Marvel Interlinear Bible", self.runMIB)

        iconFile = os.path.join("htmlResources", "trilingual.png")
        self.leftToolBar.addAction(QIcon(iconFile), "Marvel Trilingual Bible", self.runMTB)

        iconFile = os.path.join("htmlResources", "line.png")
        self.leftToolBar.addAction(QIcon(iconFile), "Marvel Parallel Bible", self.runMPB)

        iconFile = os.path.join("htmlResources", "annotated.png")
        self.leftToolBar.addAction(QIcon(iconFile), "Marvel Annotated Bible", self.runMAB)

        self.leftToolBar.addSeparator()

        self.rightToolBar = QToolBar()
        self.rightToolBar.setWindowTitle(config.thisTranslation["bar4_title"])
        self.rightToolBar.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.RightToolBarArea, self.rightToolBar)

        iconFile = os.path.join("htmlResources", "left.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_studyBack"], self.studyBack)

        iconFile = os.path.join("htmlResources", "history.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_study"], self.studyHistoryButtonClicked)

        iconFile = os.path.join("htmlResources", "right.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu3_studyForward"], self.studyForward)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "pdf.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["bar3_pdf"], self.printStudyPage)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "indexes.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_indexes"], self.runINDEX)

        iconFile = os.path.join("htmlResources", "commentary.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_commentary"], self.runCOMMENTARY)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "cross_reference.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_crossRef"], self.runCROSSREFERENCE)

        iconFile = os.path.join("htmlResources", "treasure.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_tske"], self.runTSKE)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "translations.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_traslations"], self.runTRANSLATION)

        iconFile = os.path.join("htmlResources", "discourse.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_discourse"], self.runDISCOURSE)

        iconFile = os.path.join("htmlResources", "words.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_words"], self.runWORDS)

        iconFile = os.path.join("htmlResources", "combo.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu4_tdw"], self.runCOMBO)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", "portrait.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_landscape"], self.switchLandscapeMode)

        iconFile = os.path.join("htmlResources", "parallel.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_study"], self.parallel)

        self.rightToolBar.addSeparator()

        iconFile = os.path.join("htmlResources", self.getInstantInformation())
        self.enableInstantButton = self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_hover"], self.enableInstantButtonClicked)

        iconFile = os.path.join("htmlResources", "lightning.png")
        self.rightToolBar.addAction(QIcon(iconFile), config.thisTranslation["menu2_bottom"], self.instant)

        self.rightToolBar.addSeparator()

    def setStudyBibleToolBar(self):
        if config.openBibleInMainViewOnly:
            self.studyBibleToolBar.hide()
        else:
            self.studyBibleToolBar.show()

    # install marvel data
    def installMarvelBibles(self):
        items = [self.bibleInfo[bible][-1] for bible in self.bibleInfo.keys() if not os.path.isfile(os.path.join(*self.bibleInfo[bible][0])) or self.isNewerAvailable(self.bibleInfo[bible][0][-1])]
        if not items:
            items = ["[All Installed]"]
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                config.thisTranslation["menu8_bibles"], items, 0, False)
        if ok and item and not item == "[All Installed]":
            for key, value in self.bibleInfo.items():
                if item == value[-1]:
                    self.downloadHelper(self.bibleInfo[key])
                    break


    def installMarvelCommentaries(self):
        commentaries = {
            "Notes on the Old and New Testaments (Barnes) [26 vol.]": ((config.marvelData, "commentaries", "cBarnes.commentary"), "13uxButnFH2NRUV-YuyRZYCeh1GzWqO5J"),
            "Commentary on the Old and New Testaments (Benson) [5 vol.]": ((config.marvelData, "commentaries", "cBenson.commentary"), "1MSRUHGDilogk7_iZHVH5GWkPyf8edgjr"),
            "Biblical Illustrator (Exell) [58 vol.]": ((config.marvelData, "commentaries", "cBI.commentary"), "1DUATP_0M7SwBqsjf20YvUDblg3_sOt2F"),
            "Complete Summary of the Bible (Brooks) [2 vol.]": ((config.marvelData, "commentaries", "cBrooks.commentary"), "1pZNRYE6LqnmfjUem4Wb_U9mZ7doREYUm"),
            "John Calvin's Commentaries (Calvin) [22 vol.]": ((config.marvelData, "commentaries", "cCalvin.commentary"), "1FUZGK9n54aXvqMAi3-2OZDtRSz9iZh-j"),
            "Cambridge Bible for Schools and Colleges (Cambridge) [57 vol.]": ((config.marvelData, "commentaries", "cCBSC.commentary"), "1IxbscuAMZg6gQIjzMlVkLtJNDQ7IzTh6"),
            "Critical And Exegetical Commentary on the NT (Meyer) [20 vol.]": ((config.marvelData, "commentaries", "cCECNT.commentary"), "1MpBx7z6xyJYISpW_7Dq-Uwv0rP8_Mi-r"),
            "Cambridge Greek Testament for Schools and Colleges (Cambridge) [21 vol.]": ((config.marvelData, "commentaries", "cCGrk.commentary"), "1Jf51O0R911Il0V_SlacLQDNPaRjumsbD"),
            "Church Pulpit Commentary (Nisbet) [12 vol.]": ((config.marvelData, "commentaries", "cCHP.commentary"), "1dygf2mz6KN_ryDziNJEu47-OhH8jK_ff"),
            "Commentary on the Bible (Clarke) [6 vol.]": ((config.marvelData, "commentaries", "cClarke.commentary"), "1ZVpLAnlSmBaT10e5O7pljfziLUpyU4Dq"),
            "College Press Bible Study Textbook Series (College) [59 vol.]": ((config.marvelData, "commentaries", "cCPBST.commentary"), "14zueTf0ioI-AKRo_8GK8PDRKael_kB1U"),
            "Expositor's Bible Commentary (Nicoll) [49 vol.]": ((config.marvelData, "commentaries", "cEBC.commentary"), "1UA3tdZtIKQEx-xmXtM_SO1k8S8DKYm6r"),
            "Commentary for English Readers (Ellicott) [8 vol.]": ((config.marvelData, "commentaries", "cECER.commentary"), "1sCJc5xuxqDDlmgSn2SFWTRbXnHSKXeh_"),
            "Expositor's Greek New Testament (Nicoll) [5 vol.]": ((config.marvelData, "commentaries", "cEGNT.commentary"), "1ZvbWnuy2wwllt-s56FUfB2bS2_rZoiPx"),
            "Greek Testament Commentary (Alford) [4 vol.]": ((config.marvelData, "commentaries", "cGCT.commentary"), "1vK53UO2rggdcfcDjH6mWXAdYti4UbzUt"),
            "Exposition of the Entire Bible (Gill) [9 vol.]": ((config.marvelData, "commentaries", "cGill.commentary"), "1O5jnHLsmoobkCypy9zJC-Sw_Ob-3pQ2t"),
            "Exposition of the Old and New Testaments (Henry) [6 vol.]": ((config.marvelData, "commentaries", "cHenry.commentary"), "1m-8cM8uZPN-fLVcC-a9mhL3VXoYJ5Ku9"),
            "Horæ Homileticæ (Simeon) [21 vol.]": ((config.marvelData, "commentaries", "cHH.commentary"), "1RwKN1igd1RbN7phiJDiLPhqLXdgOR0Ms"),
            "International Critical Commentary, NT (1896-1929) [16 vol.]": ((config.marvelData, "commentaries", "cICCNT.commentary"), "1QxrzeeZYc0-GNwqwdDe91H4j1hGSOG6t"),
            "Jamieson, Fausset, and Brown Commentary (JFB) [6 vol.]": ((config.marvelData, "commentaries", "cJFB.commentary"), "1NT02QxoLeY3Cj0uA_5142P5s64RkRlpO"),
            "Commentary on the Old Testament (Keil & Delitzsch) [10 vol.]": ((config.marvelData, "commentaries", "cKD.commentary"), "1rFFDrdDMjImEwXkHkbh7-vX3g4kKUuGV"),
            "Commentary on the Holy Scriptures: Critical, Doctrinal, and Homiletical (Lange) [25 vol.]": ((config.marvelData, "commentaries", "cLange.commentary"), "1_PrTT71aQN5LJhbwabx-kjrA0vg-nvYY"),
            "Expositions of Holy Scripture (MacLaren) [32 vol.]": ((config.marvelData, "commentaries", "cMacL.commentary"), "1p32F9MmQ2wigtUMdCU-biSrRZWrFLWJR"),
            "Preacher's Complete Homiletical Commentary (Exell) [37 vol.]": ((config.marvelData, "commentaries", "cPHC.commentary"), "1xTkY_YFyasN7Ks9me3uED1HpQnuYI8BW"),
            "Pulpit Commentary (Spence) [23 vol.]": ((config.marvelData, "commentaries", "cPulpit.commentary"), "1briSh0oDhUX7QnW1g9oM3c4VWiThkWBG"),
            "Word Pictures in the New Testament (Robertson) [6 vol.]": ((config.marvelData, "commentaries", "cRob.commentary"), "17VfPe4wsnEzSbxL5Madcyi_ubu3iYVkx"),
            "Spurgeon's Expositions on the Bible (Spurgeon) [3 vol.]": ((config.marvelData, "commentaries", "cSpur.commentary"), "1OVsqgHVAc_9wJBCcz6PjsNK5v9GfeNwp"),
            "Word Studies in the New Testament (Vincent) [4 vol.]": ((config.marvelData, "commentaries", "cVincent.commentary"), "1ZZNnCo5cSfUzjdEaEvZ8TcbYa4OKUsox"),
            "John Wesley's Notes on the Whole Bible (Wesley) [3 vol.]": ((config.marvelData, "commentaries", "cWesley.commentary"), "1rerXER1ZDn4e1uuavgFDaPDYus1V-tS5"),
            "Commentary on the Old and New Testaments (Whedon) [14 vol.]": ((config.marvelData, "commentaries", "cWhedon.commentary"), "1FPJUJOKodFKG8wsNAvcLLc75QbM5WO-9"),
        }
        items = [commentary for commentary in commentaries.keys() if not os.path.isfile(os.path.join(*commentaries[commentary][0]))]
        if items:
            commentaries["Install ALL Commentaries Listed Above"] = ""
            items.append("Install ALL Commentaries Listed Above")
        else:
            items = ["[All Installed]"]
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                config.thisTranslation["menu8_commentaries"], items, 0, False)
        if ok and item and not item in ("[All Installed]", "Install ALL Commentaries Listed Above"):
            self.downloadHelper(commentaries[item])
        elif item == "Install ALL Commentaries Listed Above":
            self.installAllMarvelCommentaries(commentaries)

    def installAllMarvelCommentaries(self, commentaries):
        toBeInstalled = [commentary for commentary in commentaries.keys() if not commentary == "Install ALL Commentaries Listed Above" and not os.path.isfile(os.path.join(*commentaries[commentary][0]))]
        self.displayMessage("{0}  {1}".format(config.thisTranslation["message_downloadAllFiles"], config.thisTranslation["message_willBeNoticed"]))
        for commentary in toBeInstalled:
            databaseInfo = commentaries[commentary]
            downloader = Downloader(self, databaseInfo)
            downloader.downloadFile(False)
        self.displayMessage(config.thisTranslation["message_done"])

    def installMarvelDatasets(self):
        datasets = {
            "Core Datasets": ((config.marvelData, "images.sqlite"), "1E7uoGqndCcqdeh8kl5kS0Z9pOTe8iWFp"),
            "Search Engine": ((config.marvelData, "search.sqlite"), "1A4s8ewpxayrVXamiva2l1y1AinAcIKAh"),
            "Smart Indexes": ((config.marvelData, "indexes2.sqlite"), "1hY-QkBWQ8UpkeqM8lkB6q_FbaneU_Tg5"),
            "Chapter & Verse Notes": ((config.marvelData, "note.sqlite"), "1OcHrAXLS-OLDG5Q7br6mt2WYCedk8lnW"),
            "Bible Background Data": ((config.marvelData, "data", "exlb3.data"), "1gp2Unsab85Se-IB_tmvVZQ3JKGvXLyMP"),
            "Bible Topics Data": ((config.marvelData, "data", "exlb3.data"), "1gp2Unsab85Se-IB_tmvVZQ3JKGvXLyMP"),
            "Cross-reference Data": ((config.marvelData, "cross-reference.sqlite"), "1fTf0L7l1k_o1Edt4KUDOzg5LGHtBS3w_"),
            "Dictionaries": ((config.marvelData, "data", "dictionary.data"), "1NfbkhaR-dtmT1_Aue34KypR3mfPtqCZn"),
            "Encyclopedia": ((config.marvelData, "data", "encyclopedia.data"), "1OuM6WxKfInDBULkzZDZFryUkU1BFtym8"),
            "Lexicons": ((config.marvelData, "lexicons", "MCGED.lexicon"), "157Le0xw2ovuoF2v9Bf6qeck0o15RGfMM"),
            "Atlas, Timelines & Books": ((config.marvelData, "books", "Maps_ABS.book"), "13hf1NvhAjNXmRQn-Cpq4hY0E2XbEfmEd"),
            "Word Data": ((config.marvelData, "data", "wordNT.data"), "11pmVhecYEtklcB4fLjNP52eL9pkytFdS"),
            "Words Data": ((config.marvelData, "data", "wordsNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
            "Clause Data": ((config.marvelData, "data", "clauseNT.data"), "11pmVhecYEtklcB4fLjNP52eL9pkytFdS"),
            "Translation Data": ((config.marvelData, "data", "translationNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
            "Discourse Data": ((config.marvelData, "data", "discourseNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
            "TDW Combo Data": ((config.marvelData, "data", "wordsNT.data"), "11bANQQhH6acVujDXiPI4JuaenTFYTkZA"),
        }
        items = [dataset for dataset in datasets.keys() if not os.path.isfile(os.path.join(*datasets[dataset][0]))]
        if not items:
            items = ["[All Installed]"]
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                config.thisTranslation["menu8_datasets"], items, 0, False)
        if ok and item and not item == "[All Installed]":
            self.downloadHelper(datasets[item])

    # convert bible references to string
    def bcvToVerseReference(self, b, c, v):
        parser = BibleVerseParser(config.parserStandarisation)
        verseReference = parser.bcvToVerseReference(b, c, v)
        del parser
        return verseReference

    # Open text on left and right view
    def openTextOnMainView(self, text):
        if self.newTabException:
            self.newTabException = False
        elif self.syncingBibles:
            self.syncingBibles = False
        elif config.openBibleWindowContentOnNextTab:
            nextIndex = self.mainView.currentIndex() + 1
            if nextIndex >= config.numberOfTab:
                nextIndex = 0
            self.mainView.setCurrentIndex(nextIndex)
        # check size of text content
        if not config.forceGenerateHtml and sys.getsizeof(text) < 2097152:
            self.mainView.setHtml(text, baseUrl)
        else:
            # save html in a separate file if text is larger than 2MB
            # reason: setHTML does not work with content larger than 2MB
            outputFile = os.path.join("htmlResources", "main.html")
            fileObject = open(outputFile, "w", encoding="utf-8")
            fileObject.write(text)
            fileObject.close()
            # open the text file with webview
            fullOutputPath = os.path.abspath(outputFile)
            self.mainView.load(QUrl.fromLocalFile(fullOutputPath))
        reference = "-".join(self.verseReference("main"))
        if self.textCommandParser.lastKeyword in ("compare", "parallel"):
            *_, reference2 = reference.split("-")
            reference = "{0}-{1}".format(self.textCommandParser.lastKeyword, reference2)
        self.mainView.setTabText(self.mainView.currentIndex(), reference)
        self.mainView.setTabToolTip(self.mainView.currentIndex(), reference)
            
    def setDefaultTheme(self):
        config.theme = "default"
        self.displayMessage(config.thisTranslation["message_themeTakeEffectAfterRestart"])

    def setDarkTheme(self):
        config.theme = "dark"
        self.displayMessage(config.thisTranslation["message_themeTakeEffectAfterRestart"])

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
        #wholeString = match.group(0)
        #quotationMark = match.group(1)
        #ext = match.group(2)
        #asciiString = match.group(3)
        self.exportImageNumber += 1
        binaryString = asciiString.encode("ascii")
        binaryData = base64.b64decode(binaryString)
        imageFilename = "tab{0}_image{1}.{2}".format(self.studyView.currentIndex(), self.exportImageNumber, ext)
        exportPath = os.path.join(exportFolder, imageFilename)
        with open(exportPath, "wb") as fileObject2:
            fileObject2.write(binaryData)
        return "src={0}images/export/{1}{0}".format(quotationMark, imageFilename)

    def addOpenImageAction(self, text):
        return re.sub(r"(<img[^<>]*?src=)(['{0}])(images/[^<>]*?)\2([^<>]*?>)".format('"'), r"<ref onclick={0}openHtmlFile('\3'){0}>\1\2\3\2\4</ref>".format('"'), text)

    def openTextOnStudyView(self, text):
        if self.newTabException:
            self.newTabException = False
        elif self.syncingBibles:
            self.syncingBibles = False
        elif config.openStudyWindowContentOnNextTab:
            nextIndex = self.studyView.currentIndex() + 1
            if nextIndex >= config.numberOfTab:
                nextIndex = 0
            self.studyView.setCurrentIndex(nextIndex)
            #Alternatively,
            #self.studyView.setCurrentWidget(self.studyView.widget(nextIndex))
        # export embedded images if enabled
        if config.exportEmbeddedImages:
            text = self.exportAllImages(text)
        # added links to open image files if enabled
        if config.clickToOpenImage:
            text = self.addOpenImageAction(text)
        # check size of text content
        if sys.getsizeof(text) < 2097152:
            self.studyView.setHtml(text, baseUrl)
        else:
            # save html in a separate file if text is larger than 2MB
            # reason: setHTML does not work with content larger than 2MB
            outputFile = os.path.join("htmlResources", "study.html")
            fileObject = open(outputFile, "w", encoding="utf-8")
            fileObject.write(text)
            fileObject.close()
            # open the text file with webview
            fullOutputPath = os.path.abspath(outputFile)
            self.studyView.load(QUrl.fromLocalFile(fullOutputPath))
        if config.parallelMode == 0:
            self.parallel()
        if self.textCommandParser.lastKeyword == "main":
            self.textCommandParser.lastKeyword = "study"
        self.studyView.setTabText(self.studyView.currentIndex(), self.textCommandParser.lastKeyword)
        self.studyView.setTabToolTip(self.studyView.currentIndex(), self.textCommandParser.lastKeyword)

    # warning for next action without saving modified notes
    def warningNotSaved(self):
        msgBox = QMessageBox(QMessageBox.Warning,
                "QMessageBox.warning()", "Notes are currently opened and modified.  Do you really want to continue, without saving the changes?",
                QMessageBox.NoButton, self)
        msgBox.addButton("Cancel", QMessageBox.AcceptRole)
        msgBox.addButton("&Continue", QMessageBox.RejectRole)
        if msgBox.exec_() == QMessageBox.AcceptRole:
            # Cancel
            return False
        else:
            # Continue
            return True

    # Actions - chapter / verse / new file note
    def createNewNoteFile(self):
        if self.noteSaved:
            self.noteEditor = NoteEditor(self, "file")
            self.noteEditor.show()
        elif self.warningNotSaved():
            self.noteEditor = NoteEditor(self, "file")
            self.noteEditor.show()
        else:
            self.noteEditor.raise_()

    def openNoteEditor(self, noteType, b=None, c=None, v=None):
        if not (config.noteOpened and config.lastOpenedNote == (noteType, b, c, v)):
            self.noteEditor = NoteEditor(self, noteType, b=b, c=c, v=v)
            self.noteEditor.show()

    def openMainChapterNote(self):
        self.openChapterNote(config.mainB, config.mainC)

    def openMainVerseNote(self):
        self.openVerseNote(config.mainB, config.mainC, config.mainV)

    def openStudyChapterNote(self):
        self.openChapterNote(config.studyB, config.studyC)

    def openStudyVerseNote(self):
        self.openVerseNote(config.studyB, config.studyC, config.studyV)

    def fixNoteFontDisplay(self, content):
        if config.overwriteNoteFont:
            content = re.sub("font-family:[^<>]*?([;'{0}])".format('"'), r"font-family:{0}\1".format(config.font), content)
        if config.overwriteNoteFontSize:
            content = re.sub("font-size:[^<>]*?;", "", content)
        return content

    def openChapterNote(self, b, c):
        self.textCommandParser.lastKeyword = "note"
        reference = BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, 1)
        config.studyB, config.studyC, config.studyV = b, c, 1
        self.updateStudyRefButton()
        config.commentaryB, config.commentaryC, config.commentaryV = b, c, 1
        self.updateCommentaryRefButton()
        note = self.fixNoteFontDisplay(NoteSqlite().displayChapterNote((b, c)))
        note = "<p style=\"font-family:'{4}'; font-size:{5}pt;\"><b>Note on {0}</b> &ensp;<button class='feature' onclick='document.title=\"_editchapternote:::{2}.{3}\"'>edit</button></p>{1}".format(reference[:-2], note, b, c, config.font, config.fontSize)
        note = self.htmlWrapper(note, True, "study", False)
        self.openTextOnStudyView(note)

    def openVerseNote(self, b, c, v):
        self.textCommandParser.lastKeyword = "note"
        reference = BibleVerseParser(config.parserStandarisation).bcvToVerseReference(b, c, v)
        config.studyB, config.studyC, config.studyV = b, c, v
        self.updateStudyRefButton()
        config.commentaryB, config.commentaryC, config.commentaryV = b, c, v
        self.updateCommentaryRefButton()
        note = self.fixNoteFontDisplay(NoteSqlite().displayVerseNote((b, c, v)))
        note = "<p style=\"font-family:'{5}'; font-size:{6}pt;\"><b>Note on {0}</b> &ensp;<button class='feature' onclick='document.title=\"_editversenote:::{2}.{3}.{4}\"'>edit</button></p>{1}".format(reference, note, b, c, v, config.font, config.fontSize)
        note = self.htmlWrapper(note, True, "study", False)
        self.openTextOnStudyView(note)

    # Actions - open text from external sources
    def htmlWrapper(self, text, parsing=False, view="study", linebreak=True):
        searchReplace1 = (
            ("\r\n|\r|\n", "<br>"),
            ("\t", "&emsp;&emsp;"),
        )
        searchReplace2 = (
            ("<br>(<table>|<ol>|<ul>)", r"\1"),
            ("(</table>|</ol>|</ul>)<br>", r"\1"),
            ("<a [^\n<>]*?href=['{0}]([^\n<>]*?)['{0}][^\n<>]*?>".format('"'), r"<a href='javascript:void(0)' onclick='website({0}\1{0})'>".format('"')),
            ("onclick='website\({0}([^\n<>]*?).uba{0}\)'".format('"'), r"onclick='uba({0}\1.uba{0})'".format('"'))
        )
        if linebreak:
            for search, replace in searchReplace1:
                text = re.sub(search, replace, text)
        for search, replace in searchReplace2:
            text = re.sub(search, replace, text)
        if parsing:
            text = BibleVerseParser(config.parserStandarisation).parseText(text)
        if view == "main":
            activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.mainText, config.mainB, config.mainC, config.mainV)
        elif view == "study":
            activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.studyText, config.studyB, config.studyC, config.studyV)
        text = "<!DOCTYPE html><html><head><title>UniqueBible.app</title><style>body {2} font-size: {4}px; font-family:'{5}'; {3} zh {2} font-family:'{6}'; {3}</style><link rel='stylesheet' type='text/css' href='css/{7}.css'><script src='js/{7}.js'></script><script src='w3.js'></script>{0}<script>var versionList = []; var compareList = []; var parallelList = []; var diffList = []; var searchList = [];</script></head><body><span id='v0.0.0'></span>{1}</body></html>".format(activeBCVsettings, text, "{", "}", config.fontSize, config.font, config.fontChinese, config.theme)
        
        return text

    def pasteFromClipboard(self):
        clipboardText = qApp.clipboard().text()
        # note: can use qApp.clipboard().setText to set text in clipboard
        self.openTextOnStudyView(self.htmlWrapper(clipboardText, True))

    def openTextFileDialog(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                config.thisTranslation["menu7_open"],
                self.openFileNameLabel.text(),
                "UniqueBible.app Note Files (*.uba);;HTML Files (*.html);;HTM Files (*.htm);;Word Documents (*.docx);;Plain Text Files (*.txt);;PDF Files (*.pdf);;All Files (*)", "", options)
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
        self.externalFileButton.setText(self.getLastExternalFileName())

    def getLastExternalFileName(self):
        externalFileHistory = config.history["external"]
        if externalFileHistory:
            return os.path.split(externalFileHistory[-1])[-1]
        else:
            return "[open file]"

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

    def editExternalFileHistoryRecord(self, record):
        filename = config.history["external"][record]
        fileExtension = filename.split(".")[-1].lower()
        directEdit = ("uba", "html", "htm")
        if fileExtension in directEdit:
            if self.noteSaved:
                self.noteEditor = NoteEditor(self, "file", filename)
                self.noteEditor.show()
            elif self.warningNotSaved():
                self.noteEditor = NoteEditor(self, "file", filename)
                self.noteEditor.show()
            else:
                self.noteEditor.raise_()
        else:
            self.openExternalFile(filename)

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
            self.openTextOnStudyView(text)

    def openUbaFile(self, fileName):
        if fileName:
            text = TextFileReader().readTxtFile(fileName)
            text = self.fixNoteFontDisplay(text)
            text = self.htmlWrapper(text, True, "study", False)
            self.openTextOnStudyView(text)

    def openPdfFile(self, fileName):
        if fileName:
            text = TextFileReader().readPdfFile(fileName)
            text = self.htmlWrapper(text, True)
            self.openTextOnStudyView(text)

    def openDocxFile(self, fileName):
        if fileName:
            text = TextFileReader().readDocxFile(fileName)
            text = self.htmlWrapper(text, True)
            self.openTextOnStudyView(text)

    # Actions - export to pdf
    def printMainPage(self):
        filename = "UniqueBible.app.pdf"
        self.mainPage.printToPdf(filename)

    def printStudyPage(self):
        filename = "UniqueBible.app.pdf"
        self.studyPage.printToPdf(filename)

    # import BibleBentoPlus modules
    def importBBPlusLexiconInAFolder(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                config.thisTranslation["menu8_plusLexicons"],
                self.directoryLabel.text(), options)
        if directory:
            if Converter().importBBPlusLexiconInAFolder(directory):
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
                "MySword Bibles (*.bbl.mybible);;MySword Commentaries (*.cmt.mybible);;MySword Books (*.bok.mybible);;MySword Dictionaries (*.dct.mybible);;e-Sword Bibles [Apple] (*.bbli);;e-Sword Commentaries [Apple] (*.cmti);;e-Sword Dictionaries [Apple] (*.dcti);;e-Sword Lexicons [Apple] (*.lexi);;e-Sword Books [Apple] (*.refi);;MyBible Bibles (*.SQLite3);;MyBible Commentaries (*.commentaries.SQLite3);;MyBible Dictionaries (*.dictionary.SQLite3)", "", options)
        if fileName:
            if fileName.endswith(".dct.mybible") or fileName.endswith(".dcti") or fileName.endswith(".lexi") or fileName.endswith(".dictionary.SQLite3"):
                self.importThirdPartyDictionary(fileName)
            elif fileName.endswith(".bbl.mybible"):
                self.importMySwordBible(fileName)
            elif fileName.endswith(".cmt.mybible"):
                self.importMySwordCommentary(fileName)
            elif fileName.endswith(".bok.mybible"):
                self.importMySwordBook(fileName)
            elif fileName.endswith(".bbli"):
                self.importESwordBible(fileName)
            elif fileName.endswith(".cmti"):
                self.importESwordCommentary(fileName)
            elif fileName.endswith(".refi"):
                self.importESwordBook(fileName)
            elif fileName.endswith(".commentaries.SQLite3"):
                self.importMyBibleCommentary(fileName)
            elif fileName.endswith(".SQLite3"):
                self.importMyBibleBible(fileName)

    def importModulesInFolder(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                config.thisTranslation["menu8_3rdPartyInFolder"],
                self.directoryLabel.text(), options)
        if directory:
            if Converter().importAllFilesInAFolder(directory):
                self.displayMessage(config.thisTranslation["message_done"])
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def createBookModuleFromImages(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self,
                config.thisTranslation["menu10_bookFromImages"],
                self.directoryLabel.text(), options)
        if directory:
            if Converter().createBookModuleFromImages(directory):
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
                self.displayMessage(config.thisTranslation["message_done"])
            else:
                self.displayMessage(config.thisTranslation["message_noSupportedFile"])

    def importThirdPartyDictionary(self, fileName):
        *_, name = os.path.split(fileName)
        destination = os.path.join("thirdParty", "dictionaries", name)
        try:
            copyfile(fileName, destination)
            self.completeImport()
        except:
            print("Failed to copy '{0}'.".format(fileName))

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

    def importMyBibleCommentary(self, fileName):
        Converter().importMyBibleCommentary(fileName)
        self.completeImport()

    def importMyBibleBible(self, fileName):
        Converter().importMyBibleBible(fileName)
        self.completeImport()

    def completeImport(self):
        self.displayMessage(config.thisTranslation["message_done"])

    # Actions - tag files with BibleVerseParser
    def onTaggingCompleted(self):
        self.displayMessage("{0}  {1} 'tagged_'".format(config.thisTranslation["message_done"], config.thisTranslation["message_tagged"]))

    def tagFile(self):
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(self,
                config.thisTranslation["menu8_tagFile"],
                self.openFileNameLabel.text(),
                "All Files (*);;Text Files (*.txt);;CSV Files (*.csv);;TSV Files (*.tsv)", "", options)
        if fileName:
            BibleVerseParser(config.parserStandarisation).startParsing(fileName)
            self.onTaggingCompleted()

    def tagFiles(self):
        options = QFileDialog.Options()
        files, filtr = QFileDialog.getOpenFileNames(self,
                config.thisTranslation["menu8_tagFiles"], self.openFilesPath,
                "All Files (*);;Text Files (*.txt);;CSV Files (*.csv);;TSV Files (*.tsv)", "", options)
        if files:
            parser = BibleVerseParser(config.parserStandarisation)
            for filename in files:
                parser.startParsing(filename)
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
            BibleVerseParser(config.parserStandarisation).startParsing(directory)
            self.onTaggingCompleted()

    # Action - open a dialog box to download a mp3 file from youtube
    def downloadMp3Dialog(self):
        text, ok = QInputDialog.getText(self, "YouTube -> mp3", config.thisTranslation["youtube_address"], QLineEdit.Normal, "")
        if ok and text and QUrl.fromUserInput(text).isValid():
            self.runTextCommand("mp3:::{0}".format(text))

    # Action - open a dialog box to download a youtube video in mp4 format
    def downloadMp4Dialog(self):
        text, ok = QInputDialog.getText(self, "YouTube -> mp4", config.thisTranslation["youtube_address"], QLineEdit.Normal, "")
        if ok and text and QUrl.fromUserInput(text).isValid():
            self.runTextCommand("mp4:::{0}".format(text))

    def setupYouTube(self):
        webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/download_youtube_audio_video")

    def openYouTube(self):
        self.youTubeView = YouTubePopover(self)
        self.youTubeView.show()

    # Action - open "images" directory
    def openImagesFolder(self):
        imageFolder = os.path.join("htmlResources", "images")
        self.runTextCommand("cmd:::{0} {1}".format(config.open, imageFolder))

    # Action - open "music" directory
    def openMusicFolder(self):
        self.runTextCommand("cmd:::{0} music".format(config.open))

    # Action - open "video" directory
    def openVideoFolder(self):
        self.runTextCommand("cmd:::{0} video".format(config.open))

    # Action - open "marvelData" directory
    def openMarvelDataFolder(self):
        self.runTextCommand("cmd:::{0} {1}".format(config.open, config.marvelData))

    # Actions - hide / show tool bars
    def hideShowMainToolBar(self):
        if self.firstToolBar.isVisible():
            self.firstToolBar.hide()
        else:
            self.firstToolBar.show()

    def hideShowSecondaryToolBar(self):
        if self.secondToolBar.isVisible():
            self.studyBibleToolBar.hide()
            self.secondToolBar.hide()
        else:
            self.setStudyBibleToolBar()
            self.secondToolBar.show()

    def hideShowLeftToolBar(self):
        if self.leftToolBar.isVisible():
            self.leftToolBar.hide()
        else:
            self.leftToolBar.show()

    def hideShowRightToolBar(self):
        if self.rightToolBar.isVisible():
            self.rightToolBar.hide()
        else:
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
            self.studyBibleToolBar.hide()
            self.secondToolBar.hide()
            self.leftToolBar.hide()
            self.rightToolBar.hide()
        else:
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
        self.setStudyBibleToolBar()
        self.secondToolBar.show()
        self.leftToolBar.show()
        self.rightToolBar.show()

    def hideAllToolBar(self):
        config.topToolBarOnly = False
        self.firstToolBar.hide()
        self.studyBibleToolBar.hide()
        self.secondToolBar.hide()
        self.leftToolBar.hide()
        self.rightToolBar.hide()

    # Actions - book features
    def openBookMenu(self):
        self.runTextCommand("BOOK:::{0}".format(config.book), True, "main")

    def displaySearchBookCommand(self):
        config.bookSearchString = ""
        self.textCommandLineEdit.setText("SEARCHBOOK:::{0}:::".format(config.book))
        self.textCommandLineEdit.setFocus()

    def displaySearchAllBookCommand(self):
        config.bookSearchString = ""
        self.textCommandLineEdit.setText("SEARCHBOOK:::ALL:::")
        self.textCommandLineEdit.setFocus()

    def clearBookHighlights(self):
        config.bookSearchString = ""
        self.reloadCurrentRecord()

    def clearNoteHighlights(self):
        config.noteSearchString = ""
        self.reloadCurrentRecord()

    def displaySearchFavBookCommand(self):
        config.bookSearchString = ""
        self.textCommandLineEdit.setText("SEARCHBOOK:::FAV:::")
        self.textCommandLineEdit.setFocus()

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
        bookData = BookData()
        items = [book for book, *_ in bookData.getBookList()]
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["menu10_dialog"], items, items.index(config.book), False)
        if ok and item:
            self.runTextCommand("BOOK:::{0}".format(item), True, "main")

    def setTabNumberDialog(self):
        integer, ok = QInputDialog.getInt(self,
                "UniqueBible", config.thisTranslation["menu1_tabNo"], config.numberOfTab, 1, 20, 1)
        if ok:
            config.numberOfTab = integer
            self.displayMessage(config.thisTranslation["message_restart"])

    def moreConfigOptionsDialog(self):
        self.moreConfigOptions = MoreConfigOptions(self)
        self.moreConfigOptions.show()

    def addFavouriteBookDialog(self):
        bookData = BookData()
        items = [book for book, *_ in bookData.getBookList()]
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["menu10_addFavourite"], items, items.index(config.book), False)
        if ok and item:
            config.favouriteBooks.insert(0, item)
            if len(config.favouriteBooks) > 10:
                config.favouriteBooks = [book for counter, book in enumerate(config.favouriteBooks) if counter < 10]
            self.displayMessage("{0}  {1}".format(config.thisTranslation["message_done"], config.thisTranslation["message_restart"]))

    def toggleDisplayBookContent(self):
        if config.bookOnNewWindow:
            config.bookOnNewWindow = False
            self.displayMessage(config.thisTranslation["menu10_bookOnStudy"])
        else:
            config.bookOnNewWindow = True
            self.displayMessage(config.thisTranslation["menu10_bookOnNew"])

    def searchBookDialog(self):
        bookData = BookData()
        items = [book for book, *_ in bookData.getBookList()]
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["menu10_dialog"], items, items.index(config.book), False)
        if ok and item:
            self.textCommandLineEdit.setText("SEARCHBOOK:::{0}:::".format(item))
            self.textCommandLineEdit.setFocus()

    def search3rdDictionaryDialog(self):
        items = ThirdPartyDictionary(self.textCommandParser.isThridPartyDictionary(config.thirdDictionary)).moduleList
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["menu5_3rdDict"], items, items.index(config.thirdDictionary), False)
        if ok and item:
            self.textCommandLineEdit.setText("SEARCHTHIRDDICTIONARY:::{0}:::".format(item))
            self.textCommandLineEdit.setFocus()

    def searchDictionaryDialog(self):
        indexes = IndexesSqlite()
        dictionaryDict = {abb: name for abb, name in indexes.dictionaryList}
        lastDictionary = dictionaryDict[config.dictionary]
        dictionaryDict = {name: abb for abb, name in indexes.dictionaryList}
        items = [key for key in dictionaryDict.keys()]
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["context1_dict"], items, items.index(lastDictionary), False)
        if ok and item:
            self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(dictionaryDict[item]))
            self.textCommandLineEdit.setFocus()

    def searchEncyclopediaDialog(self):
        indexes = IndexesSqlite()
        dictionaryDict = {abb: name for abb, name in indexes.encyclopediaList}
        lastDictionary = dictionaryDict[config.encyclopedia]
        dictionaryDict = {name: abb for abb, name in indexes.encyclopediaList}
        items = [key for key in dictionaryDict.keys()]
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["context1_encyclopedia"], items, items.index(lastDictionary), False)
        if ok and item:
            self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(dictionaryDict[item]))
            self.textCommandLineEdit.setFocus()

    def searchTopicDialog(self):
        indexes = IndexesSqlite()
        dictionaryDict = {abb: name for abb, name in indexes.topicList}
        lastDictionary = dictionaryDict[config.topic]
        dictionaryDict = {name: abb for abb, name in indexes.topicList}
        items = [key for key in dictionaryDict.keys()]
        item, ok = QInputDialog.getItem(self, "UniqueBible", config.thisTranslation["menu5_topics"], items, items.index(lastDictionary), False)
        if ok and item:
            self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(dictionaryDict[item]))
            self.textCommandLineEdit.setFocus()

    # Action - bible search commands
    def displaySearchBibleCommand(self):
        self.textCommandLineEdit.setText("SEARCH:::{0}:::".format(config.mainText))
        self.textCommandLineEdit.setFocus()

    def displaySearchStudyBibleCommand(self):
        self.textCommandLineEdit.setText("SEARCH:::{0}:::".format(config.studyText))
        self.textCommandLineEdit.setFocus()

    def displaySearchBibleMenu(self):
        self.runTextCommand("_menu:::", False, "main")

    # Action - other search commands
    def searchCommandChapterNote(self):
        self.textCommandLineEdit.setText("SEARCHCHAPTERNOTE:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandVerseNote(self):
        self.textCommandLineEdit.setText("SEARCHVERSENOTE:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleDictionary(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(config.dictionary))
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleEncyclopedia(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(config.encyclopedia))
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleCharacter(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::EXLBP:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleName(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::HBN:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleLocation(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::EXLBL:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandBibleTopic(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::{0}:::".format(config.topic))
        self.textCommandLineEdit.setFocus()

    def searchCommandAllBibleTopic(self):
        self.textCommandLineEdit.setText("SEARCHTOOL:::EXLBT:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandLexicon(self):
        self.textCommandLineEdit.setText("LEXICON:::")
        self.textCommandLineEdit.setFocus()

    def searchCommandThirdPartyDictionary(self):
        self.textCommandLineEdit.setText("SEARCHTHIRDDICTIONARY:::")
        self.textCommandLineEdit.setFocus()

    # Actions - open urls
    def openUbaWiki(self):
        webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki")

    def openBibleTools(self):
        webbrowser.open("https://bibletools.app")

    def openUniqueBible(self):
        webbrowser.open("https://uniquebible.app")

    def openMarvelBible(self):
        webbrowser.open("https://marvel.bible")

    def openBibleBento(self):
        webbrowser.open("https://biblebento.com")

    def openOpenGNT(self):
        webbrowser.open("https://opengnt.com")

    def openSource(self):
        webbrowser.open("https://github.com/eliranwong/")

    def openUniqueBibleSource(self):
        webbrowser.open("https://github.com/eliranwong/UniqueBible")

    def openHebrewBibleSource(self):
        webbrowser.open("https://github.com/eliranwong/OpenHebrewBible")

    def openOpenGNTSource(self):
        webbrowser.open("https://github.com/eliranwong/OpenGNT")

    def openCredits(self):
        webbrowser.open("https://marvel.bible/resource.php")

    def contactEliranWong(self):
        webbrowser.open("https://marvel.bible/contact/contactform.php")

    def goToSlack(self):
        webbrowser.open("https://marvelbible.slack.com")

    def donateToUs(self):
        webbrowser.open("https://www.paypal.me/MarvelBible")

    def moreBooks(self):
        webbrowser.open("https://github.com/eliranwong/UniqueBible/wiki/download_3rd_party_modules")

    # Actions - resize the main window
    def fullsizeWindow(self):
        self.resizeWindow(1, 1)

    def twoThirdWindow(self):
        self.resizeWindow(2/3, 2/3)

    def halfScreenHeight(self):
        self.resizeWindow(1, 1/2)

    def halfScreenWidth(self):
        self.resizeWindow(1/2, 1)

    def resizeWindow(self, widthFactor, heightFactor):
        availableGeometry = qApp.desktop().availableGeometry()
        self.resize(availableGeometry.width() * widthFactor, availableGeometry.height() * heightFactor)

    # Actions - enable or disable sync commentary
    def getSyncStudyWindowBibleDisplay(self):
        if config.syncStudyWindowBibleWithMainWindow:
            return "sync.png"
        else:
            return "noSync.png"

    def getSyncStudyWindowBibleDisplayToolTip(self):
        if config.syncStudyWindowBibleWithMainWindow:
            return config.thisTranslation["bar2_studyWindowBibleSyncEnabled"]
        else:
            return config.thisTranslation["bar2_studyWindowBibleSyncDisabled"]

    def enableSyncStudyWindowBibleButtonClicked(self):
        config.syncStudyWindowBibleWithMainWindow = not config.syncStudyWindowBibleWithMainWindow
        enableSyncStudyWindowBibleButtonFile = os.path.join("htmlResources", self.getSyncStudyWindowBibleDisplay())
        self.enableSyncStudyWindowBibleButton.setIcon(QIcon(enableSyncStudyWindowBibleButtonFile))
        self.enableSyncStudyWindowBibleButton.setToolTip(self.getSyncStudyWindowBibleDisplayToolTip())
        if config.syncCommentaryWithMainWindow and not self.syncButtonChanging:
            self.syncButtonChanging = True
            self.enableSyncCommentaryButtonClicked()
        if config.syncStudyWindowBibleWithMainWindow:
            self.reloadCurrentRecord()
        self.syncButtonChanging = False

    def getSyncCommentaryDisplay(self):
        if config.syncCommentaryWithMainWindow:
            return "sync.png"
        else:
            return "noSync.png"

    def getSyncCommentaryDisplayToolTip(self):
        if config.syncCommentaryWithMainWindow:
            return config.thisTranslation["bar2_commentarySyncEnabled"]
        else:
            return config.thisTranslation["bar2_commentarySyncDisabled"]

    def enableSyncCommentaryButtonClicked(self):
        config.syncCommentaryWithMainWindow = not config.syncCommentaryWithMainWindow
        enableSyncCommentaryButtonFile = os.path.join("htmlResources", self.getSyncCommentaryDisplay())
        self.enableSyncCommentaryButton.setIcon(QIcon(enableSyncCommentaryButtonFile))
        self.enableSyncCommentaryButton.setToolTip(self.getSyncCommentaryDisplayToolTip())
        if config.syncStudyWindowBibleWithMainWindow and not self.syncButtonChanging:
            self.syncButtonChanging = True
            self.enableSyncStudyWindowBibleButtonClicked()
        if config.syncCommentaryWithMainWindow:
            self.reloadCurrentRecord()
        self.syncButtonChanging = False

    def enableNoteIndicatorButtonClicked(self):
        config.showNoteIndicatorOnBibleChapter = not config.showNoteIndicatorOnBibleChapter
        self.reloadCurrentRecord()

    # Actions - enable or disable study bible / bible displayed on study view
    def getStudyBibleDisplay(self):
        if config.openBibleInMainViewOnly:
            return "addStudyViewBible.png"
        else:
            return "deleteStudyViewBible.png"

    def getStudyBibleDisplayToolTip(self):
        if config.openBibleInMainViewOnly:
            return config.thisTranslation["bar2_enableBible"]
        else:
            return config.thisTranslation["bar2_disableBible"]

    def enableStudyBibleButtonClicked(self):
        if config.openBibleInMainViewOnly:
            config.openBibleInMainViewOnly = False
            self.studyBibleToolBar.show()
        else:
            config.openBibleInMainViewOnly = True
            self.studyBibleToolBar.hide()
        enableStudyBibleButtonFile = os.path.join("htmlResources", self.getStudyBibleDisplay())
        self.enableStudyBibleButton.setIcon(QIcon(enableStudyBibleButtonFile))
        self.enableStudyBibleButton.setToolTip(self.getStudyBibleDisplayToolTip())

    # Actions - enable or disable lightning feature
    def getInstantInformation(self):
        if config.instantInformationEnabled:
            return "show.png"
        else:
            return "hide.png"

    def enableInstantButtonClicked(self):
        if config.instantInformationEnabled:
            config.instantInformationEnabled = False
        else:
            config.instantInformationEnabled = True
        enableInstantButtonFile = os.path.join("htmlResources", self.getInstantInformation())
        self.enableInstantButton.setIcon(QIcon(enableInstantButtonFile))

    # Actions - enable or disable paragraphs feature
    def displayBiblesInParagraphs(self):
        config.readFormattedBibles = not config.readFormattedBibles
        self.newTabException = True
        self.reloadCurrentRecord()

    def getReadFormattedBibles(self):
        if config.readFormattedBibles:
            return "paragraph.png"
        else:
            return "numbered_list.png"

    def enableParagraphButtonClicked(self):
        self.enableParagraphButtonAction(True)

    def enableParagraphButtonAction(self, display):
        if display:
            self.displayBiblesInParagraphs()
        enableParagraphButtonFile = os.path.join("htmlResources", self.getReadFormattedBibles())
        self.enableParagraphButton.setIcon(QIcon(enableParagraphButtonFile))

    # Actions - enable or disable sub-heading for plain bibles
    def getAddSubheading(self):
        if config.addTitleToPlainChapter:
            return "subheadingEnable.png"
        else:
            return "subheadingDisable.png"

    def enableSubheadingButtonClicked(self):
        config.addTitleToPlainChapter = not config.addTitleToPlainChapter
        self.newTabException = True        
        self.reloadCurrentRecord()
        enableSubheadingButtonFile = os.path.join("htmlResources", self.getAddSubheading())
        self.enableSubheadingButton.setIcon(QIcon(enableSubheadingButtonFile))

    # Actions - change font size
    def smallerFont(self):
        if not config.fontSize == 5:
            config.fontSize = config.fontSize - 1
            self.defaultFontButton.setText("{0} {1}".format(config.font, config.fontSize))
            self.reloadCurrentRecord()

    def largerFont(self):
        config.fontSize = config.fontSize + 1
        self.defaultFontButton.setText("{0} {1}".format(config.font, config.fontSize))
        self.reloadCurrentRecord()

    def reloadCurrentRecord(self):
        if config.readFormattedBibles:
            mappedBibles = (
                ("MIB", "OHGBi"),
                ("MOB", "OHGB"),
                #("LXX1", "LXX1i"),
                #("LXX2i", "LXX2"),
            )
            for view in ("main", "study"):
                textCommand = config.history[view][config.currentRecord[view]]
                for formattedBible, plainBible in mappedBibles:
                    textCommand = textCommand.replace(plainBible, formattedBible)
                    self.runTextCommand(textCommand, False, view)
        else:
            mappedBibles = (
                ("MIB", "OHGBi"),
                ("MOB", "OHGB"),
                ("MPB", "OHGB"),
                ("MTB", "OHGB"),
                ("MAB", "OHGB"),
                #("LXX1", "LXX1i"),
                #("LXX2i", "LXX2"),
            )
            for view in ("main", "study"):
                textCommand = config.history[view][config.currentRecord[view]]
                for formattedBible, plainBible in mappedBibles:
                    textCommand = textCommand.replace(formattedBible, plainBible)
                    self.runTextCommand(textCommand, False, view)

    # Actions - previous / next chapter
    def previousMainChapter(self):
        newChapter = config.mainC - 1
        biblesSqlite = BiblesSqlite()
        mainChapterList = biblesSqlite.getChapterList()
        del biblesSqlite
        if newChapter in mainChapterList:
            self.newTabException = True
            newTextCommand = self.bcvToVerseReference(config.mainB, newChapter, 1)
            self.textCommandChanged(newTextCommand, "main")

    def nextMainChapter(self):
        newChapter = config.mainC + 1
        biblesSqlite = BiblesSqlite()
        mainChapterList = biblesSqlite.getChapterList()
        del biblesSqlite
        if newChapter in mainChapterList:
            self.newTabException = True
            newTextCommand = self.bcvToVerseReference(config.mainB, newChapter, 1)
            self.textCommandChanged(newTextCommand, "main")

    def openMainChapter(self):
        newTextCommand = self.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        self.textCommandChanged(newTextCommand, "main")

    # Actions - recently opened bibles & commentary
    def mainTextMenu(self):
        newTextCommand = "_menu:::"
        self.runTextCommand(newTextCommand, False, "main")

    def studyTextMenu(self):
        newTextCommand = "_menu:::"
        self.runTextCommand(newTextCommand, False, "study")

    def bookFeatures(self):
        newTextCommand = "_menu:::{0}.{1}".format(config.mainText, config.mainB)
        self.runTextCommand(newTextCommand, False, "main")

    def chapterFeatures(self):
        newTextCommand = "_menu:::{0}.{1}.{2}".format(config.mainText, config.mainB, config.mainC)
        self.runTextCommand(newTextCommand, False, "main")

    def mainRefButtonClicked(self):
        newTextCommand = "_menu:::{0}.{1}.{2}.{3}".format(config.mainText, config.mainB, config.mainC, config.mainV)
        self.runTextCommand(newTextCommand, False, "main")

    def studyRefButtonClicked(self):
        newTextCommand = "_menu:::{0}.{1}.{2}.{3}".format(config.studyText, config.studyB, config.studyC, config.studyV)
        self.runTextCommand(newTextCommand, False, "study")

    def commentaryRefButtonClicked(self):
        newTextCommand = "_commentary:::{0}.{1}.{2}.{3}".format(config.commentaryText, config.commentaryB, config.commentaryC, config.commentaryV)
        self.runTextCommand(newTextCommand, False, "study")

    def updateMainRefButton(self):
        text, verseReference = self.verseReference("main")
        self.mainTextMenuButton.setText(text)
        self.mainRefButton.setText(verseReference)
        if config.syncStudyWindowBibleWithMainWindow and not config.openBibleInMainViewOnly and not self.syncingBibles:
            self.syncingBibles = True
            newTextCommand = "STUDY:::{0}".format(verseReference)
            self.runTextCommand(newTextCommand, True, "study")
        elif config.syncCommentaryWithMainWindow:
            self.syncingBibles = True
            newTextCommand = "COMMENTARY:::{0}".format(verseReference)
            self.runTextCommand(newTextCommand, True, "study")

    def updateStudyRefButton(self):
        text, verseReference = self.verseReference("study")
        self.studyTextMenuButton.setText(text)
        self.studyRefButton.setText(verseReference)
        if config.syncStudyWindowBibleWithMainWindow and not config.openBibleInMainViewOnly and not self.syncingBibles:
            self.syncingBibles = True
            newTextCommand = "MAIN:::{0}".format(verseReference)
            self.runTextCommand(newTextCommand, True, "main")

    def updateCommentaryRefButton(self):
        self.commentaryRefButton.setText(self.verseReference("commentary"))

    def verseReference(self, view):
        if view == "main":
            return (config.mainText, self.bcvToVerseReference(config.mainB, config.mainC, config.mainV))
        elif view == "study":
            return (config.studyText, self.bcvToVerseReference(config.studyB, config.studyC, config.studyV))
        elif view == "commentary":
            return "{0} - {1}".format(config.commentaryText, self.bcvToVerseReference(config.commentaryB, config.commentaryC, config.commentaryV))

    # Actions - access history records
    def mainHistoryButtonClicked(self):
        self.mainView.setHtml(self.getHistory("main"), baseUrl)

    def studyHistoryButtonClicked(self):
        self.studyView.setHtml(self.getHistory("study"), baseUrl)

    def getHistory(self, view):
        historyRecords = [(counter, record) for counter, record in enumerate(config.history[view])]
        if view == "external":
            html = "<br>".join(["<button class='feature' onclick='openExternalRecord({0})'>{1}</button> [<ref onclick='editExternalRecord({0})'>edit</ref>]".format(counter, record) for counter, record in reversed(historyRecords)])
        else:
            html = "<br>".join(["<button class='feature' onclick='openHistoryRecord({0})'>{1}</button>".format(counter, record) for counter, record in reversed(historyRecords)])
        html = self.htmlWrapper(html)
        return html

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
    def finishMainViewLoading(self):
        # scroll to the main verse
        self.mainPage.runJavaScript("var activeVerse = document.getElementById('v"+str(config.mainB)+"."+str(config.mainC)+"."+str(config.mainV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = 'red'; } else { document.getElementById('v0.0.0').scrollIntoView(); }")

    def finishStudyViewLoading(self):
        # scroll to the study verse
        self.studyPage.runJavaScript("var activeVerse = document.getElementById('v"+str(config.studyB)+"."+str(config.studyC)+"."+str(config.studyV)+"'); if (typeof(activeVerse) != 'undefined' && activeVerse != null) { activeVerse.scrollIntoView(); activeVerse.style.color = 'red'; } else { document.getElementById('v0.0.0').scrollIntoView(); }")

    # finish pdf printing
    def pdfPrintingFinishedAction(self, filePath, success):
        if success:
            self.openExternalFile(filePath, isPdf=True)
        else:
            print("Failed to print pdf")

    # running specific commands
    def runFeature(self, keyword):
        mainVerseReference = self.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        newTextCommand = "{0}:::{1}".format(keyword, mainVerseReference)
        self.textCommandChanged(newTextCommand, "main")

    def runMOB(self):
        self.runFeature("BIBLE:::MOB")

    def runMIB(self):
        self.runFeature("BIBLE:::MIB")

    def runMAB(self):
        self.runFeature("BIBLE:::MAB")

    def runMPB(self):
        self.runFeature("BIBLE:::MPB")

    def runMTB(self):
        self.runFeature("BIBLE:::MTB")

    def runCOMPARE(self):
        self.runFeature("COMPARE")

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

    # change of unique bible commands
    def mainTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "main")

    def studyTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "study")

    def instantTextCommandChanged(self, newTextCommand):
        self.textCommandChanged(newTextCommand, "instant")

    # change of text command detected via change of document.title
    def textCommandChanged(self, newTextCommand, source="main"):
        exceptionTuple = ("UniqueBible.app", "about:blank", "study.html")
        if not (newTextCommand.startswith("data:text/html;") or newTextCommand.startswith("file:///") or newTextCommand[-4:] == ".txt" or newTextCommand in exceptionTuple):
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

    def runTextCommand(self, textCommand, addRecord=True, source="main"):
        # reset document.title
        changeTitle = "document.title = 'UniqueBible.app';"
        self.mainPage.runJavaScript(changeTitle)
        self.studyPage.runJavaScript(changeTitle)
        self.instantPage.runJavaScript(changeTitle)
        # prevent repetitive command within unreasonable short time
        now = datetime.now()
        timeDifference = int((now - self.now).total_seconds())
        if textCommand == "_stayOnSameTab:::":
            self.newTabException = True
        elif (timeDifference > 1 or (source == "main" and textCommand != self.lastMainTextCommand) or \
            (source == "study" and textCommand != self.lastStudyTextCommand)) and textCommand != "main.html":
            # handle exception for new tab features
            if re.search('^(_commentary:::|_menu:::)', textCommand.lower()):
                self.newTabException = True
            # parse command
            view, content = self.textCommandParser.parser(textCommand, source)
            # process content
            if content == "INVALID_COMMAND_ENTERED":
                self.displayMessage(config.thisTranslation["message_invalid"] + ":" + textCommand)
            elif view == "command":
                self.textCommandLineEdit.setText(content)
                self.textCommandLineEdit.setFocus()
            else:
                activeBCVsettings = ""
                if view == "main":
                    activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.mainText, config.mainB, config.mainC, config.mainV)
                elif view == "study":
                    activeBCVsettings = "<script>var activeText = '{0}'; var activeB = {1}; var activeC = {2}; var activeV = {3};</script>".format(config.studyText, config.studyB, config.studyC, config.studyV)
                html = "<!DOCTYPE html><html><head><title>UniqueBible.app</title><style>body {2} font-size: {4}px; font-family:'{5}'; {3} zh {2} font-family:'{6}'; {3}</style><link rel='stylesheet' type='text/css' href='css/{7}.css'><script src='js/{7}.js'></script><script src='w3.js'></script>{0}<script>var versionList = []; var compareList = []; var parallelList = []; var diffList = []; var searchList = [];</script></head><body><span id='v0.0.0'></span>{1}</body></html>".format(activeBCVsettings, content, "{", "}", config.fontSize, config.font, config.fontChinese, config.theme)
                views = {
                    "main": self.mainView,
                    "study": self.studyView,
                    "instant": self.instantView,
                }
                # add hovering action to bible reference links
                searchReplace = (
                    ('{0}document.title="BIBLE:::([^<>"]*?)"{0}|"document.title={0}BIBLE:::([^<>{0}]*?){0}"'.format("'"), r'{0}document.title="BIBLE:::\1\2"{0} onmouseover={0}document.title="_imvr:::\1\2"{0}'.format("'")),
                    (r'onclick=([{0}"])bcv\(([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?)\)\1'.format("'"), r'onclick="bcv(\2,\3,\4,\5,\6)" onmouseover="imv(\2,\3,\4,\5,\6)"'),
                    (r'onclick=([{0}"])bcv\(([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?)\)\1'.format("'"), r'onclick="bcv(\2,\3,\4)" onmouseover="imv(\2,\3,\4)"'),
                    (r'onclick=([{0}"])cr\(([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?)\)\1'.format("'"), self.convertCrLink),
                )
                for search, replace in searchReplace:
                    html = re.sub(search, replace, html)
                # load into widget view
                if view == "study":
                    self.openTextOnStudyView(html)
                elif view == "main":
                    self.openTextOnMainView(html)
                elif view.startswith("popover"):
                    view = view.split(".")[1]
                    views[view].currentWidget().openPopover(html=html)
                # There is a case where view is an empty string "".
                # The following condition applies where view is not empty only.
                elif view:
                    views[view].setHtml(html, baseUrl)
                if addRecord == True and view in ("main", "study"):
                    self.addHistoryRecord(view, textCommand)
            # set checking blocks to prevent running the same command within unreasonable time frame
            self.now = now
            if source == "main":
                self.lastMainTextCommand = textCommand
            elif source == "study":
                self.lastStudyTextCommand = textCommand

    def convertCrLink(self, match):
        *_, b, c, v = match.groups()
        bookNo = Converter().convertMyBibleBookNo(int(b))
        return 'onclick="bcv({0},{1},{2})" onmouseover="imv({0},{1},{2})"'.format(bookNo, c, v)

    # add a history record
    def addHistoryRecord(self, view, textCommand):
        if not textCommand.startswith("_"):
            viewhistory = config.history[view]
            if not (viewhistory[-1] == textCommand):
                viewhistory.append(textCommand)
                # set maximum number of history records for each view here
                historyRecordAllowed = config.historyRecordAllowed
                if len(viewhistory) > historyRecordAllowed:
                    viewhistory = viewhistory[-historyRecordAllowed:]
                config.history[view] = viewhistory
                config.currentRecord[view] = len(viewhistory) - 1

    # switch between landscape / portrait mode
    def switchIconSize(self):
        if config.toolBarIconFullSize:
            config.toolBarIconFullSize = False
        else:
            config.toolBarIconFullSize = True
        self.displayMessage("{0}  {1}".format(config.thisTranslation["message_done"], config.thisTranslation["message_restart"]))

    # switch between landscape / portrait mode
    def switchLandscapeMode(self):
        if config.landscapeMode:
            config.landscapeMode = False
        else:
            config.landscapeMode = True
        self.centralWidget.switchLandscapeMode()
        self.resizeCentral()

    def resizeCentral(self):
        self.centralWidget.resizeMe()

    # Actions - hide / show / resize study & lightning views
    def instant(self):
        if config.instantMode == 2:
            config.instantMode = 0
        else:
            config.instantMode += 1
        self.resizeCentral()

    def parallel(self):
        if config.parallelMode == 3:
            config.parallelMode = 0
        else:
            config.parallelMode += 1
        self.resizeCentral()

    # Open Morphology Search Dialog by double clicking of Hebrew / Greek words on marvel bibles
    def openMorphDialog(self, items):
        self.morphDialog = MorphDialog(self, items)
        #self.morphDialog.setModal(True)
        self.morphDialog.show()

    # Set my language (config.userLanguage)
    def openMyLanguageDialog(self):
        languages = Languages()
        if config.userLanguage:
            userLanguage = config.userLanguage
        else:
            userLanguage = "English"
        items = [language for language in languages.codes.keys()]
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                config.thisTranslation["menu1_setMyLanguage"], items, items.index(userLanguage), False)
        if ok and item:
            config.userLanguage = item
            if not config.googletransSupport:
                self.displayMessage("{0}  'googletrans'\n{1}".format(config.thisTranslation["message_missing"], config.thisTranslation["message_installFirst"]))

    # Set default Strongs Greek lexicon (config.defaultLexiconStrongG)
    def openSelectDefaultStrongsGreekLexiconDialog(self):
        items = LexiconData().lexiconList
        item, ok = QInputDialog.getItem(self, config.thisTranslation["menu1_selectDefaultLexicon"],
            config.thisTranslation["menu1_setDefaultStrongsGreekLexicon"], items, items.index(config.defaultLexiconStrongG), False)
        if ok and item:
            config.defaultLexiconStrongG = item

    # Set default Strongs Hebrew lexicon (config.defaultLexiconStrongH)
    def openSelectDefaultStrongsHebrewLexiconDialog(self):
        items = LexiconData().lexiconList
        item, ok = QInputDialog.getItem(self, config.thisTranslation["menu1_selectDefaultLexicon"],
            config.thisTranslation["menu1_setDefaultStrongsHebrewLexicon"], items, items.index(config.defaultLexiconStrongH), False)
        if ok and item:
            config.defaultLexiconStrongH = item

    # Set Favourite Bible Version
    def openFavouriteBibleDialog(self):
        items = BiblesSqlite().getBibleList()
        item, ok = QInputDialog.getItem(self, config.thisTranslation["menu1_setMyFavouriteBible"],
                config.thisTranslation["message_addFavouriteVersion"], items, items.index(config.favouriteBible), False)
        if ok and item:
            config.favouriteBible = item
            config.addFavouriteToMultiRef = True
        else:
            config.addFavouriteToMultiRef = False
        self.reloadCurrentRecord()

    # Set bible book abbreviations
    def setBibleAbbreviations(self):
        items = ("ENG", "TC", "SC")
        item, ok = QInputDialog.getItem(self, "UniqueBible",
                config.thisTranslation["menu1_setAbbreviations"], items, items.index(config.standardAbbreviation), False)
        if ok and item:
            config.standardAbbreviation = item
            self.reloadCurrentRecord()

    # set default font
    def setDefaultFont(self):
        ok, font = QFontDialog.getFont(QFont(config.font, config.fontSize), self)
        if ok:
            #print(font.key())
            config.font, fontSize, *_ = font.key().split(",")
            config.fontSize = int(fontSize)
            self.defaultFontButton.setText("{0} {1}".format(config.font, config.fontSize))
            self.reloadCurrentRecord()

    # set Chinese font
    def setChineseFont(self):
        ok, font = QFontDialog.getFont(QFont(config.fontChinese, config.fontSize), self)
        if ok:
            #print(font.key())
            config.fontChinese, *_ = font.key().split(",")
            self.reloadCurrentRecord()

