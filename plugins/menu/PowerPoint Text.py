import config, sys, os
from install.module import *
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

    options = QFileDialog.Options()
    fileName, filtr = QFileDialog.getOpenFileName(config.mainWindow,
                                                  config.thisTranslation["menu7_open"],
                                                  config.mainWindow.openFileNameLabel.text(),
                                                  "PowerPoint Files (*.pptx)",
                                                  "", options)
    if fileName:
        text = textract.process(fileName).decode()
        text = config.mainWindow.htmlWrapper(text, True, html=False)
        config.mainWindow.openTextOnStudyView(text, tab_title=os.path.basename(fileName))
