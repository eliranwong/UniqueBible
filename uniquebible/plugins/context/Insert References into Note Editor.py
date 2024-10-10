from uniquebible import config
from uniquebible.util.BibleVerseParser import BibleVerseParser

if config.pluginContext:
    config.mainWindow.showNoteEditor()
    parser = BibleVerseParser(config.parserStandarisation)
    verseList = parser.extractAllReferences(config.pluginContext, False)
    if not verseList:
        config.mainWindow.displayMessage(config.thisTranslation["message_noReference"])
    else:
        content = "; ".join([parser.bcvToVerseReference(*verse) for verse in verseList])

        if hasattr(config.mainWindow, "noteEditor"):
            content = "<br><br>{0}<br><br>".format(content)
            if config.mainWindow.noteEditor.noteEditor.html:
                config.mainWindow.noteEditor.noteEditor.editor.insertHtml(content)
            else:
                config.mainWindow.noteEditor.noteEditor.editor.insertPlainText(content)
        else:
            config.contextItem = content
            config.mainWindow.createNewNoteFile()
else:
    config.contextSource.messageNoSelection()
