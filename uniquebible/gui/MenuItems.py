import os
from uniquebible import config

from uniquebible.db.UserRepoSqlite import UserRepoSqlite
from uniquebible.util.FileUtil import FileUtil
from uniquebible.util.GitHubRepoInfo import GitHubRepoInfo
from uniquebible.util.HtmlColorCodes import HtmlColorCodes

# Do not delete items from the following two lines.  It appears that some are not used but they are actually used somewhere else. 
if config.qtLibrary == "pyside6":
    from PySide6.QtGui import QIcon, QColor, QPixmap, QAction, QCursor
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QToolBar, QPushButton, QLineEdit, QStyleFactory, QComboBox, QToolButton, QMenu, QLabel, QStyle, QSlider
    from PySide6.QtWebEngineCore import QWebEnginePage
else:
    from qtpy.QtGui import QIcon, QColor, QPixmap, QCursor
    from qtpy.QtCore import Qt
    from qtpy.QtWidgets import QAction, QToolBar, QPushButton, QLineEdit, QStyleFactory, QComboBox, QToolButton, QMenu, QLabel, QStyle, QSlider
    from qtpy.QtWebEngineWidgets import QWebEnginePage
from functools import partial


def addMenu(menuBar, title, translation=True):
    return menuBar.addMenu("{0}{1}".format(config.menuUnderline, config.thisTranslation[title] if translation else title))

def addSubMenu(parentMenu, translation):
    return parentMenu.addMenu(config.thisTranslation.get(translation, translation))

def addCheckableMenuItem(menu, feature, object, action, currentValue, thisValue, shortcut=None, translation=True, icon=""):
    if shortcut:
        if shortcut in config.shortcutList:
            shortcut = None
        else:
            config.shortcutList.append(shortcut)
    if shortcut is None:
        shortcut = ""
    qAction = QAction(config.thisTranslation[feature] if translation else feature, object, triggered=action, shortcut=shortcut)
    if icon:
        qAction.setIcon(QIcon(icon))
    qAction.setCheckable(True)
    if (isinstance(currentValue, str) and isinstance(thisValue, str) and currentValue.lower() == thisValue.lower()) or currentValue == thisValue:
        qAction.setChecked(True)
    return menu.addAction(qAction)

def addMenuItem(menu, feature, object, action, shortcut=None, translation=True):
    if shortcut:
        if shortcut in config.shortcutList:
            shortcut = None
        else:
            config.shortcutList.append(shortcut)
    if shortcut is None:
        shortcut = ""
    return menu.addAction(QAction(config.thisTranslation[feature] if translation else feature, object, triggered=action, shortcut=shortcut))

def addAllThemeColorMenuItem(theme, menu, object, action):
    for color in HtmlColorCodes.colors:
        themeName = "{0} {1}".format(theme, color)
        addColorIconMenuItem(color, menu, themeName, object, partial(action, themeName), None, False)

def addColorIconMenuItem(color, menu, feature, object, action, shortcut=None, translation=True):
    color = HtmlColorCodes.colors[color][0]
    color = QColor(color)
    menuFontSize = int(config.iconButtonSize / 3 * 2)
    pixmap = QPixmap(menuFontSize, menuFontSize)
    pixmap.fill(color)
    if shortcut:
        if shortcut in config.shortcutList:
            shortcut = None
        else:
            config.shortcutList.append(shortcut)
    icon = QIcon(pixmap)
    if shortcut is None:
        shortcut = ""
    return menu.addAction(QAction(icon, config.thisTranslation[feature] if translation else feature, object, triggered=action, shortcut=shortcut))

def addIconMenuItem(icon, menu, feature, object, action, shortcut=None, translation=True):
    if shortcut:
        if shortcut in config.shortcutList:
            shortcut = None
        else:
            config.shortcutList.append(shortcut)
    icon = QIcon(os.path.join("htmlResources", icon))
    return menu.addAction(QAction(icon, config.thisTranslation[feature] if translation else feature, object, triggered=action, shortcut=shortcut))

def addMenuLayoutItems(parent, menu):
    items = (
        ("menu1_material_menu_layout", lambda: parent.setupMenuLayout("material"), "material"),
    )
    for feature, action, thisValue in items:
        addCheckableMenuItem(menu, feature, parent, action, config.menuLayout, thisValue)
    menu.addSeparator()
    items = (
        ("menu1_aleph_menu_layout", lambda: parent.setupMenuLayout("aleph"), "aleph"),
        ("menu1_focus_menu_layout", lambda: parent.setupMenuLayout("focus"), "focus"),
        ("menu1_classic_menu_layout", lambda: parent.setupMenuLayout("classic"), "classic"),
    )
    for feature, action, thisValue in items:
        addCheckableMenuItem(menu, feature, parent, action, config.menuLayout, thisValue)
    layouts = FileUtil.fileNamesWithoutExtension(os.path.join(config.packageDir, "plugins", "layout"), "py")
    if layouts:
        menu.addSeparator()
        for pluginLayout in layouts:
            addCheckableMenuItem(menu, pluginLayout, parent, lambda: parent.setupMenuLayout(pluginLayout), config.menuLayout, pluginLayout, translation=False)

def addGithubDownloadMenuItems(self, subMenu):
    if ("Pygithub" in config.enabled):
        subMenu.addSeparator()
        items = (
            ("githubBibles", self.installGithubBibles),
            ("githubCommentaries", self.installGithubCommentaries),
            ("githubBooks", self.installGithubBooks),
            ("githubHymnLyrics", self.installGithubHymnLyrics),
            ("githubMaps", self.installGithubMaps),
            ("githubPdf", self.installGithubPdf),
            ("githubEpub", self.installGithubEpub),
            ("gitHubDevotionals", self.installGithubDevotionals),
            ("gitHubBibleMp3Files", self.installGithubBibleMp3),
            ("gitHubPluginsContext", self.installGithubPluginsContext),
            ("gitHubPluginsStartup", self.installGithubPluginsStartup),
            ("gitHubPluginsMenu", self.installGithubPluginsMenu),
            ("githubBiblesIndex", self.installGithubBiblesIndex),
            ("gitHubBibleAbbreviations", self.installGithubBibleAbbreviations),
            ("githubStatistics", self.installGithubStatistics),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)
        subMenu.addSeparator()
        addMenuItem(subMenu, config.thisTranslation["Configure User Custom Repos"],
                    self, self.showUserReposDialog, None, False)
        userRepoSqlite = UserRepoSqlite()
        repos = userRepoSqlite.getAll()
        if len(repos) > 0:
            subMenu.addSeparator()
            for id, active, name, type, repo, directory in repos:
                data = GitHubRepoInfo.buildInfo(repo, type, directory)
                addMenuItem(subMenu, f"{type}:{name}", self, lambda data=data: self.installFromGitHub(data), None, False)


def addBuildMacroMenuItems(self, subMenu):
    if ("Pygithub" in config.enabled):
        subMenu.addSeparator()
        items = (
            ("menu_command", self.macroSaveCommand),
            ("menu_highlight", self.macroSaveHighlights),
            ("settings", self.macroSaveSettings),
            ("downloadMissingFiles", self.macroGenerateDownloadMissingFiles),
            ("downloadExistingFiles", self.macroGenerateDownloadExistingFiles),
        )
        for feature, action in items:
            addMenuItem(subMenu, feature, self, action)