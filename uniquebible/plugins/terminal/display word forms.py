from uniquebible import config

print(config.mainWindow.divider)
print("Enter a word:")
userInput = config.mainWindow.simplePrompt()
if not userInput or userInput.lower() == config.terminal_cancel_action:
    config.mainWindow.cancelAction()
else:
    print("Lemma: ", config.lemmatizer.lemmatize(userInput))
    formDict = config.get_word_forms("love")

    if formDict["n"]:
        nouns = formDict["n"]
        print("Nouns: ", "|".join(nouns))
    if formDict["a"]:
        adjectives = formDict["a"]
        print("Adjectives: ", "|".join(adjectives))
    if formDict["v"]:
        verbs = formDict["v"]
        print("Verbs: ", "|".join(verbs))
    if formDict["r"]:
        adverbs = formDict["r"]
        print("Adverbs: ", "|".join(adverbs))
