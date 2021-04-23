"""
This plugin does two things:
1) add mouse over action to existing links displaying lexical data on bottom window: 
    e.g. <ref onclick="lex('H1234')">
2) tag Strong's number / in plain text
    e.g. H1234
"""

import config, re

def tagLexicalEntry(text):
    searchReplace = (
        (r" [ ]+?([^ ])", r" \1"),
        (r"""(<ref onclick=["']lex\(["'])([^\(\)]+?)(["']\)["'])>""", r"""\1\2\3 onmouseover="ld('\2')">"""),
        (r" ([EHG][0-9]+?) ", r""" <sup><ref onclick="lex('\1')" onmouseover="ld('\1')">\1</ref></sup> """),
        (r" ([EHG][0-9]+?) ", r""" <sup><ref onclick="lex('\1')" onmouseover="ld('\1')">\1</ref></sup> """),
    )
    for search, replace in searchReplace:
        text = re.sub(search, replace, text)
    return text

config.bibleWindowContentTransformers.append(tagLexicalEntry)
config.studyWindowContentTransformers.append(tagLexicalEntry)
