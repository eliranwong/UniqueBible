from uniquebible import config

text = config.textEditor.oldChanges[0] if config.textEditor.oldChanges else ""
textSelection = config.textEditor.textSelection
beforeTextSelection = text[:config.textEditor.editorCursorPosition - len(textSelection)]
afterTextSelection = text[config.textEditor.editorCursorPosition:]

config.textEditorPluginOutput = beforeTextSelection + textSelection.lower() + afterTextSelection
