from uniquebible import config
import re

def transformSingleVerseLinkToRange(text):
    return re.sub(r'onmouseover="imv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">([1-4A-Za-z]+? )\2:\3-([0-9]+?)([^0-9])', r'onmouseover="imv(\1,\2,\3,\2,\5)">\4\2:\3-\5\6', text)

config.bibleWindowContentTransformers.append(transformSingleVerseLinkToRange)
config.studyWindowContentTransformers.append(transformSingleVerseLinkToRange)
