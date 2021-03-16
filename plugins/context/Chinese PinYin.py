import config, sys
from install.module import *
try:
    from pypinyin import pinyin
    moduleInstalled = True
except:
    moduleInstalled = False


# A function to convert text into pinyin
def pinyinSelectedText(text):
    from pypinyin import pinyin
    pinyinList = pinyin(text)
    pinyinList = [" ".join(list) for list in pinyinList]
    return " ".join(pinyinList)


# Install essential module if it is absent
if not moduleInstalled:
    installmodule("pypinyin")
if not "pypinyin" in sys.modules:
    try:
        from pypinyin import pinyin
    except:
        config.mainWindow.displayMessage("This plugin is not enabled.\nRun 'pip3 install {0}' to install essential module first.".format("pypinyin"))

# Convert selected text to Chinese pinyin
if "pypinyin" in sys.modules:
    if config.pluginContext:
        config.contextSource.openPopover(html=pinyinSelectedText(config.pluginContext))
    else:
        config.contextSource.messageNoSelection()
