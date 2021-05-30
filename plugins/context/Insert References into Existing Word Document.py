import config, subprocess, os
from qtpy.QtWidgets import QFileDialog
from util.BibleVerseParser import BibleVerseParser

if config.isPythonDocxInstalled:
    from docx import Document

    if config.pluginContext:

        parser = BibleVerseParser(config.parserStandarisation)
        verseList = parser.extractAllReferences(config.pluginContext, False)
        if not verseList:
            config.mainWindow.displayMessage(config.thisTranslation["message_noReference"])
        else:
            references = "; ".join([parser.bcvToVerseReference(*verse) for verse in verseList])
    
            options = QFileDialog.Options()
            fileName, filtr = QFileDialog.getOpenFileName(config.mainWindow,
                                                          config.thisTranslation["menu7_open"],
                                                          os.path.join(config.marvelData, "docx"),
                                                          "Word Documents (*.docx)",
                                                          "", options)
            if fileName:
                document = Document(fileName)
                document.add_paragraph(references)
                document.save(fileName)
                subprocess.Popen("{0} {1}".format(config.open, fileName), shell=True)
    else:
        config.contextSource.messageNoSelection()

else:
    config.mainWindow.displayMessage(config.thisTranslation["message_noSupport"])
