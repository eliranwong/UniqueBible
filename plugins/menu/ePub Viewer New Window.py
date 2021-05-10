import config, os, platform
from qtpy.QtCore import QUrl

file = "plugins/menu/Bibi-v1.2.0/bibi/index.html" if platform.system() == "Windows" else "plugins/menu/ePubViewer/ePubViewer.html"
file = os.path.join(os.getcwd(), file)
qurl = QUrl.fromLocalFile(file)
config.mainWindow.studyView.currentWidget().openPopoverUrl(qurl, name="EPUB")
