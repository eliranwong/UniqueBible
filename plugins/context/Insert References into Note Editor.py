import config
from BibleVerseParser import BibleVerseParser

if config.pluginContext:
    parser = BibleVerseParser(config.parserStandarisation)
    verseList = parser.extractAllReferences(config.pluginContext, False)
    if not verseList:
        config.mainWindow.displayMessage(config.thisTranslation["message_noReference"])
    else:
        content = "; ".join([parser.bcvToVerseReference(*verse) for verse in verseList])

        if config.noteOpened:
            content = "<br><br>{0}<br><br>".format(content)
            if config.mainWindow.noteEditor.html:
                config.mainWindow.noteEditor.editor.insertHtml(content)
            else:
                config.mainWindow.noteEditor.editor.insertPlainText(content)
            config.mainWindow.bringToForeground(config.mainWindow.noteEditor)
        else:
            config.contextItem = content
            config.mainWindow.createNewNoteFile()
else:
    config.contextSource.messageNoSelection()
