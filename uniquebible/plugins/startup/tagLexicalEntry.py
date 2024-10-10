"""
This plugin does two things:
1) add mouse over action to existing links displaying lexical data on bottom window: 
    e.g. <ref onclick="lex('H1234')">
2) tag Strong's number / in plain text
    e.g. H1234
"""

from uniquebible import config
import re


def tagLexicalEntry(text):
    searchReplace = (
        (r" [ ]+?([^ ])", r" \1"),
        (r"""<(ref|tag)( onclick=["']lex\(["'])([EHG][^\(\)]+?)(["']\)["'])>""", r"""<\1\2\3\4 class="G\3" onmouseover="ld('\3'); hl1('','','\3')" onmouseout="hl0('','','\3')">"""),
        (r" ([EHG][0-9]+?) ", r""" <sup><ref onclick="lex('\1')" class="G\1" onmouseover="ld('\1'); hl1('','','\1')" onmouseout="hl0('','','\1')">\1</ref></sup> """),
        (r" ([EHG][0-9]+?)([ <])", r""" <sup><ref onclick="lex('\1')" class="G\1" onmouseover="ld('\1'); hl1('','','\1')" onmouseout="hl0('','','\1')">\1</ref></sup>\2"""),
    )
    for search, replace in searchReplace:
        text = re.sub(search, replace, text)
    # Correct class for multiple lexical entries
    p = re.compile(r"""(class=['"][^"']+?)_([GH][0-9])""")
    while p.search(text):
        text = p.sub(r"\1 G\2", text)
    # When multiple Strong's numbers are tagged for a single string
    if config.mutualHighlightMultipleStrongNumber == 1:
        # mutual highlighting - less tolerance; keep the first entry only in multiple entries
        p = re.compile(r"""(hl[0-1])(\('','','[^']+?)_[^']+?'""")
        while p.search(text):
            text = p.sub(r"\1\2'", text)
    elif config.mutualHighlightMultipleStrongNumber == 2:
        # mutual highlighting - less tolerance 2; keep the last entry only in multiple entries
        p = re.compile(r"""(hl[0-1])(\('','',')[^']+?_([^'_]+?')""")
        while p.search(text):
            text = p.sub(r"\1\2\3", text)
    else:
        # mutual highlighting - more tolerance; include all multiple entries
        p = re.compile(r"""(hl[0-1])(\('','','[^']+?)_(G[0-9])""")
        while p.search(text):
            text = p.sub(r"\1\2'); \1('','','\3", text)
    return text

config.bibleWindowContentTransformers.append(tagLexicalEntry)
config.studyWindowContentTransformers.append(tagLexicalEntry)
