import config

for tab in range(0, config.numberOfTab):
    config.mainWindow.studyView.setCurrentIndex(tab)
    config.mainWindow.studyView.setHtml("", "")
    config.mainWindow.studyView.setTabText(tab, "Study")
    config.tabHistory["study"][str(tab)] = ''
