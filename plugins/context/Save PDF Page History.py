import config, os
from qtpy.QtWidgets import QInputDialog

def pageDialog():
    filename = os.path.basename(config.pdfTextPath)
    integer, ok = QInputDialog.getInt(config.mainWindow,
                                      "UniqueBible", "{0}\nSpecify a page number:".format(filename), 1, 1,
                                      10000, 1)
    if ok:
        addHistoryRecord(integer)

def addHistoryRecord(page):
    command = "ANYPDF:::{0}:::{1}".format(config.pdfTextPath, page)
    config.mainWindow.addHistoryRecord("study", command)

if config.pluginContext:
    if config.pdfTextPath:
        try:
            page = int(config.pluginContext)
            addHistoryRecord(page)
        except:
            pageDialog()
    else:
        config.mainWindow.displayMessage("No previously opened pdf is found!")
else:
    pageDialog()
