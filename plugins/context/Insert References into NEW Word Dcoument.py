import config, subprocess
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

            document = Document()
            document.add_paragraph(references)
            filename = "WordDocument_NEW.docx"
            document.save(filename)
            subprocess.Popen("{0} {1}".format(config.open, filename), shell=True)
    else:
        config.contextSource.messageNoSelection()

else:
    config.mainWindow.displayMessage(config.thisTranslation["message_noSupport"])
