import config, subprocess, os
from qtpy.QtWidgets import QFileDialog


options = QFileDialog.Options()
fileName, filtr = QFileDialog.getOpenFileName(config.mainWindow,
                                              config.thisTranslation["menu7_open"],
                                              os.path.join(config.marvelData, "docx"),
                                              "Word Documents (*.docx)",
                                              "", options)
if fileName:
    subprocess.Popen("{0} {1}".format(config.open, fileName), shell=True)