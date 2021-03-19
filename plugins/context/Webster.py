# This plugin does three things:
# 1) Lemmatise selected English word
# 2) Read lemmatised word with text-to-speech engine
# 3) Lookup lemmatised word in third-party dictionary "webster"
# User can change or add more dictionaries in the tuple on line 29

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
if not "lemmagen3" in sys.modules:
    try:
        from lemmagen3 import Lemmatizer
    except:
        config.mainWindow.displayMessage("This plugin is not enabled.\nRun 'pip3 install {0}' to install essential module first.".format("lemmagen3"))

if config.pluginContext:
    lemma = Lemmatizer('en').lemmatize(config.pluginContext)
    config.mainWindow.runTextCommand("SPEAK:::en-gb:::{0}".format(lemma))
    # Search multiple thrid-party dicitonaries
    for thridDict in ("webster",):
        config.mainWindow.runTextCommand("SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(thridDict, lemma))
else:
    config.contextSource.messageNoSelection()
