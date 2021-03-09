import config, re

def addHoverFeatureToBibleLinks(text):
    text = re.sub(r'<(a|ref) onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">', r'<\1 onclick="bcv(\2,\3,\4)" onmouseover="imv(\2,\3,\4)">', text)
    text = re.sub(r'<(a|ref) onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?),([0-9]+?),([0-9]+?)\)">', r'<\1 onclick="bcv(\2,\3,\4,\5,\6)" onmouseover="imv(\2,\3,\4,\5,\6)">', text)
    return text

config.bibleWindowContentTransformers.append(addHoverFeatureToBibleLinks)
config.studyWindowContentTransformers.append(addHoverFeatureToBibleLinks)
