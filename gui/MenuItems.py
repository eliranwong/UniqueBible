import os, config
from util.FileUtil import FileUtil

# Do not delete items from the following two lines.  It appears that some are not used but they are actually used somewhere else. 
from qtpy.QtGui import QIcon, Qt
from qtpy.QtWidgets import QAction, QToolBar, QPushButton, QLineEdit, QStyleFactory, QComboBox

def addMenu(menuBar, translation):
    return menuBar.addMenu("&{0}".format(config.thisTranslation[translation]))

def addSubMenu(parentMenu, translation):
    return parentMenu.addMenu(config.thisTranslation[translation])

def addMenuItem(menu, feature, object, action, shortcut=None, translation=True):
    if shortcut:
        if shortcut in config.shortcutList:
            shortcut = None
        else:
            config.shortcutList.append(shortcut)
    return menu.addAction(QAction(config.thisTranslation[feature] if translation else feature, object, triggered=action, shortcut=shortcut))

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
        ("menu1_aleph_menu_layout", lambda: parent.setMenuLayout("aleph")),
        ("menu1_focus_menu_layout", lambda: parent.setMenuLayout("focus")),
        ("menu1_classic_menu_layout", lambda: parent.setMenuLayout("classic")),
    )
    for feature, action in items:
        addMenuItem(menu, feature, parent, action)
    layouts = FileUtil.fileNamesWithoutExtension(os.path.join("plugins", "layout"), "py")
    if layouts:
        menu.addSeparator()
        for pluginLayout in layouts:
            addMenuItem(menu, pluginLayout, parent, lambda: parent.setMenuLayout(pluginLayout), translation=False)
