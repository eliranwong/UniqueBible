import config, subprocess, os
from qtpy.QtWidgets import QFileDialog

if config.isPythonDocxInstalled:
    from docx import Document

    if config.pluginContext:
        options = QFileDialog.Options()
        fileName, filtr = QFileDialog.getOpenFileName(config.mainWindow,
                                                      config.thisTranslation["menu7_open"],
                                                      os.path.join(config.marvelData, "docx"),
                                                      "Word Documents (*.docx)",
                                                      "", options)
        if fileName:
            document = Document(fileName)
            document.add_paragraph(config.pluginContext)
            document.save(fileName)
            subprocess.Popen("{0} {1}".format(config.open, fileName), shell=True)
    else:
        config.contextSource.messageNoSelection()

else:
    config.mainWindow.displayMessage(config.thisTranslation["message_noSupport"])
