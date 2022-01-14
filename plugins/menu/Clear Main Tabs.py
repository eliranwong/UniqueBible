import config

for tab in range(0, config.numberOfTab):
    config.mainWindow.mainView.setCurrentIndex(tab)
    config.mainWindow.mainView.setHtml("", "")
    config.mainWindow.mainView.setTabText(tab, "Bible")
    config.tabHistory["main"][str(tab)] = ''
