from uniquebible import config

text = config.textEditor.oldChanges[0] if config.textEditor.oldChanges else ""

if text:
    lines = text.split("\n")
    lines = sorted(lines)
    text = "\n".join(lines)

config.textEditorPluginOutput = text
