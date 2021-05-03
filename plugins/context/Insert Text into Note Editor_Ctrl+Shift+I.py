import config

if config.pluginContext:
    content = config.pluginContext.replace("\n", "<br>")
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
