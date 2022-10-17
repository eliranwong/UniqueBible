# "open html content in lynx"
import config
from util.WebtopUtil import WebtopUtil


if WebtopUtil.isPackageInstalled("lynx"):
    html = config.mainWindow.fineTuneTextForWebBrowserDisplay()
    config.mainWindow.cliTool("lynx -stdin", html)
else:
    config.mainWindow.printToolNotFound("lynx")
