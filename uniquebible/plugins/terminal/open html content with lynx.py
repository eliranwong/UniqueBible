# "open html content in lynx"
from uniquebible import config
from uniquebible.util.WebtopUtil import WebtopUtil


if WebtopUtil.isPackageInstalled("lynx"):
    html = config.mainWindow.fineTuneTextForWebBrowserDisplay()
    config.mainWindow.cliTool("lynx -stdin", html)
else:
    config.mainWindow.printToolNotFound("lynx")
