from uniquebible import config
import re
from uniquebible.util.ThirdParty import Converter

def convertCrLink(match):
    *_, b, c, v = match.groups()
    bookNo = Converter().convertMyBibleBookNo(int(b))
    return 'onclick="bcv({0},{1},{2})" onmouseover="imv({0},{1},{2})"'.format(bookNo, c, v)

def addHoverFeatureToBibleLinks(text):
    searchReplace = (
        (
        '{0}document.title="BIBLE:::([^<>"]*?)"{0}|"document.title={0}BIBLE:::([^<>{0}]*?){0}"'.format("'"),
        r'{0}document.title="BIBLE:::\1\2"{0} onmouseover={0}document.title="_imvr:::\1\2"{0}'.format("'")),
        (
        r'onclick=([{0}"])bcv\(([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?)\)\1'.format(
            "'"), r'onclick="bcv(\2,\3,\4,\5,\6)" onmouseover="imv(\2,\3,\4,\5,\6)"'),
        (r'onclick=([{0}"])bcv\(([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?)\)\1'.format("'"),
         r'onclick="bcv(\2,\3,\4)" onmouseover="imv(\2,\3,\4)"'),
        (
        r'onclick=([{0}"])cr\(([0-9]+?),[ ]*?([0-9]+?),[ ]*?([0-9]+?)\)\1'.format("'"), convertCrLink),
    )
    for search, replace in searchReplace:
        text = re.sub(search, replace, text)
    
    text = re.sub(r'<(a|ref) onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?)\)">', r'<\1 onclick="bcv(\2,\3,\4)" onmouseover="imv(\2,\3,\4)">', text)
    text = re.sub(r'<(a|ref) onclick="bcv\(([0-9]+?),([0-9]+?),([0-9]+?),([0-9]+?),([0-9]+?)\)">', r'<\1 onclick="bcv(\2,\3,\4,\5,\6)" onmouseover="imv(\2,\3,\4,\5,\6)">', text)
    
    # Fixed duplicated onmouseover
    duplicatedPattern = re.compile(r'onmouseover="imv\([^\(\)]+?\)" onmouseover="imv')
    while duplicatedPattern.search(text):
        text = re.sub(duplicatedPattern, 'onmouseover="imv', text)
    
    return text

config.bibleWindowContentTransformers.append(addHoverFeatureToBibleLinks)
config.studyWindowContentTransformers.append(addHoverFeatureToBibleLinks)
