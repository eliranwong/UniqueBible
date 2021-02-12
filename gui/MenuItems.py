import os, config, myTranslation
from PySide2.QtGui import QIcon, Qt
from PySide2.QtWidgets import (QAction, QToolBar, QPushButton, QLineEdit, QStyleFactory)
import gui.MenuItems
from gui.MainWindow import MainWindow
from gui.MasterControl import MasterControl

def addMenu(menuBar, translation):
    return menuBar.addMenu("&{0}".format(config.thisTranslation[translation]))

def addSubMenu(parentMenu, translation):
    return parentMenu.addMenu(config.thisTranslation[translation])

def addMenuItem(menu, feature, object, action, shortcut=None, translation=True):
    return menu.addAction(QAction(config.thisTranslation[feature] if translation else feature, object, triggered=action, shortcut=shortcut))

def addIconMenuItem(icon, menu, feature, object, action, shortcut=None, translation=True):
    icon = QIcon(os.path.join("htmlResources", icon))
    return menu.addAction(QAction(icon, config.thisTranslation[feature] if translation else feature, object, triggered=action, shortcut=shortcut))
