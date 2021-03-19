# This plugin search currently opened bible for all forms of selected English word.

import config, sys
from install.module import *
try:
    # https://pypi.org/project/word-forms/
    from word_forms.word_forms import get_word_forms
    moduleInstalled = True
except:
    moduleInstalled = False

# Install essential module if it is absent
if not moduleInstalled:
    installmodule("-U word_forms")
if not "word_forms" in sys.modules:
    try:
        from word_forms.word_forms import get_word_forms
    except:
        config.mainWindow.displayMessage("This plugin is not enabled.\nRun 'pip3 install -U {0}' to install essential module first.".format("word_forms"))

if config.pluginContext:
    allForms = get_word_forms(config.pluginContext)
    formList = []
    for form in allForms.values():
        if form:
            formList += list(form)
    config.mainWindow.runTextCommand("ORSEARCH:::{0}".format("|".join(set(formList))))
else:
    config.contextSource.messageNoSelection()
