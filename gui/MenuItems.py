import os, config
# Do not delete items from the following two lines.  It appears that some are not used but they are actually used somewhere else. 
from qtpy.QtGui import QIcon, Qt
from qtpy.QtWidgets import QAction, QToolBar, QPushButton, QLineEdit, QStyleFactory, QComboBox

def addMenu(menuBar, translation):
    return menuBar.addMenu("&{0}".format(config.thisTranslation[translation]))

def addSubMenu(parentMenu, translation):
    return parentMenu.addMenu(config.thisTranslation[translation])

def addMenuItem(menu, feature, object, action, shortcut=None, translation=True):
    return menu.addAction(QAction(config.thisTranslation[feature] if translation else feature, object, triggered=action, shortcut=shortcut))

def addIconMenuItem(icon, menu, feature, object, action, shortcut=None, translation=True):
    icon = QIcon(os.path.join("htmlResources", icon))
    return menu.addAction(QAction(icon, config.thisTranslation[feature] if translation else feature, object, triggered=action, shortcut=shortcut))
