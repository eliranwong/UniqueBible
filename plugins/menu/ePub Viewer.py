import config
import os
from qtpy.QtCore import QUrl


config.mainWindow.studyView.setTabText(config.mainWindow.studyView.currentIndex(), "EPUB")
config.mainWindow.studyView.setTabToolTip(config.mainWindow.studyView.currentIndex(), "EPUB")
file = os.path.join(os.getcwd(), './plugins/menu/ePubViewer/ePubViewer.html')
qurl = QUrl.fromLocalFile(file)
config.mainWindow.studyView.load(qurl)
