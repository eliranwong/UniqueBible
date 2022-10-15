# "open html content in lynx"
import config
from util.WebtopUtil import WebtopUtil


if WebtopUtil.isPackageInstalled("lynx"):
    config.mainWindow.cliTool("lynx -stdin", config.mainWindow.html)
else:
    config.mainWindow.printToolNotFound("lynx")
