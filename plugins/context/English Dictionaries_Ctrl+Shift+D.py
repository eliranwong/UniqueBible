import config, sys
from install.module import *
try:
    # https://pypi.org/project/lemmagen3/
    from lemmagen3 import Lemmatizer
    moduleInstalled = True
except:
    moduleInstalled = False

# Install essential module if it is absent
if not moduleInstalled:
    installmodule("lemmagen3")
if not "pypinyin" in sys.modules:
    try:
        from lemmagen3 import Lemmatizer
    except:
        config.mainWindow.displayMessage("This plugin is not enabled.\nRun 'pip3 install {0}' to install essential module first.".format("lemmagen3"))

if config.pluginContext:
    lemma = Lemmatizer('en').lemmatize(config.pluginContext)
    speech = lemma if lemma == config.pluginContext else "{0} {1}".format(config.pluginContext, lemma)
    config.mainWindow.runTextCommand("GTTS:::en:::{0}".format(speech))
    # Search multiple thrid-party dicitonaries
    for thridDict in ("webster", "wordnet"):
        config.mainWindow.runTextCommand("SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(thridDict, lemma))
else:
    config.contextSource.messageNoSelection()
