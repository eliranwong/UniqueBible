"""
This plugin does two things:
1) add mouse over action to existing links to lexical entry: 
    e.g. <ref onclick="lex('H1234')">
2) tag Strong's number / in plain text
    e.g. H1234
"""

import config, re

def tagLexicalEntry(text):
    searchReplace = (
        ("""(<ref onclick=["']lex\(["'])([^\(\)]+?)(["']\)["'])>""", r"""\1\2\3 onmouseover="ld('\2')">"""),
        (" ([EHG][0-9]+?) ", r""" <sup><ref onclick="lex('\1')" onmouseover="ld('\1')">\1</ref></sup> """),
        ("([EHG][0-9]+?) ", r"""<ref onclick="lex('\1')" onmouseover="ld('\1')">\1</ref> """),
    )
    for search, replace in searchReplace:
        text = re.sub(search, replace, text)
    return text

if config.theme == "dark":
    config.bibleWindowContentTransformers.append(tagLexicalEntry)
    config.studyWindowContentTransformers.append(tagLexicalEntry)
