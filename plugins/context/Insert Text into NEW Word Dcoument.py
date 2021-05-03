import config, subprocess

if config.isPythonDocxInstalled:
    from docx import Document

    if config.pluginContext:
        document = Document()
        document.add_paragraph(config.pluginContext)
        filename = "WordDocument_NEW.docx"
        document.save(filename)
        subprocess.Popen("{0} {1}".format(config.open, filename), shell=True)
    else:
        config.contextSource.messageNoSelection()

else:
    config.mainWindow.displayMessage(config.thisTranslation["message_noSupport"])
