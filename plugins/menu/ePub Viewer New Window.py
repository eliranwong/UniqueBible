import config, os, platform
from qtpy.QtCore import QUrl

file = "htmlResources/lib/bibi-v1.2.0/bibi/index.html"
file = os.path.join(os.getcwd(), file)
qurl = QUrl.fromLocalFile(file)
config.mainWindow.studyView.currentWidget().openPopoverUrl(qurl, name="EPUB")
