from uniquebible import config

if config.pluginContext and  hasattr(config, "lemmatizer"):
    lemma = config.lemmatizer.lemmatize(config.pluginContext)
    if ("OnlineTts" in config.enabled):
        speech = lemma if lemma == config.pluginContext else "{0} {1}".format(config.pluginContext, lemma)
        config.mainWindow.runTextCommand("GTTS:::en:::{0}".format(speech))
    # Search multiple thrid-party dicitonaries
    for thridDict in ("webster", "wordnet"):
        config.mainWindow.runTextCommand("SEARCHTHIRDDICTIONARY:::{0}:::{1}".format(thridDict, lemma))
else:
    config.contextSource.messageNoSelection()
