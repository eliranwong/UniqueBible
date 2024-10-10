from uniquebible import config
import sys, os
from uniquebible.install.module import *
if config.qtLibrary == "pyside6":
    from PySide6.QtWidgets import QFileDialog
else:
    from qtpy.QtWidgets import QFileDialog
try:
    import textract
    moduleInstalled = True
except:
    moduleInstalled = False

# Install essential module if it is absent
if not moduleInstalled:
    installmodule("textract")
if not "textract" in sys.modules:
    try:
        import textract
    except:
        config.mainWindow.displayMessage("This plugin is not enabled.\nRun 'pip3 install {0}' to install essential module first.".format("textract"))

# Convert selected text to Chinese pinyin
if "textract" in sys.modules:
    extensions = ("txt", "csv", "doc", "docx", "eml", "epub", "gif", "jpg", "jpeg", "json", "html", "htm", "mp3", "msg", "odt", "ogg", "pdf", "png", "pptx", "ps", "rtf", "tiff", "tif", "wav", "xlsx", "xls")
    filters = ["{0} Files (*.{1})".format(extension.upper(), extension) for extension in extensions]

    options = QFileDialog.Options()
    fileName, filtr = QFileDialog.getOpenFileName(config.mainWindow,
                                                  config.thisTranslation["menu7_open"],
                                                  config.mainWindow.openFileNameLabel.text(),
                                                  ";;".join(filters),
                                                  "", options)
    if fileName:
        text = textract.process(fileName).decode()
        text = config.mainWindow.htmlWrapper(text, True, html=False)
        config.mainWindow.openTextOnStudyView(text, tab_title=os.path.basename(fileName))
