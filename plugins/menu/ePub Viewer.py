import config, os, platform
from qtpy.QtCore import QUrl

config.mainWindow.studyView.setTabText(config.mainWindow.studyView.currentIndex(), "EPUB")
config.mainWindow.studyView.setTabToolTip(config.mainWindow.studyView.currentIndex(), "EPUB")
file = "htmlResources/lib/bibi-v1.2.0/bibi/index.html" if platform.system() == "Windows" else "plugins/menu/ePubViewer/ePubViewer.html"
file = os.path.join(os.getcwd(), file)
qurl = QUrl.fromLocalFile(file)
config.mainWindow.studyView.load(qurl)
