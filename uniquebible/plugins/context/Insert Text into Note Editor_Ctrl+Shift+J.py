from uniquebible import config

if config.pluginContext:
    config.mainWindow.showNoteEditor()
    content = config.pluginContext.replace("\n", "<br>")

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
