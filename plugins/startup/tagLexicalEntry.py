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
        #(r"""(<ref onclick=["']lex\(["'])([EHG][^\(\)]+?)(["']\)["'])>""", r"""\1\2\3 class="G\2" onmouseover="ld('\2'); hl1('','','\2')" onmouseout="hl0('','','\2')">"""),
        #<tag onclick='lex("G2193_G3739")' class="GG2193_G3739" onmouseover="ld('G2193_G3739'); hl1('','','G2193_G3739')" onmouseout="hl0('','','G2193_G3739')">
        (r"""<(ref|tag)( onclick=["']lex\(["'])([EHG][^\(\)]+?)(["']\)["'])>""", r"""<\1\2\3\4 class="G\3" onmouseover="ld('\3'); hl1('','','\3')" onmouseout="hl0('','','\3')">"""),
        (r" ([EHG][0-9]+?) ", r""" <sup><ref onclick="lex('\1')" class="G\1" onmouseover="ld('\1'); hl1('','','\1')" onmouseout="hl0('','','\1')">\1</ref></sup> """),
        (r" ([EHG][0-9]+?)([ <])", r""" <sup><ref onclick="lex('\1')" class="G\1" onmouseover="ld('\1'); hl1('','','\1')" onmouseout="hl0('','','\1')">\1</ref></sup>\2"""),
    )
    for search, replace in searchReplace:
        text = re.sub(search, replace, text)
    p = re.compile(r"""(class=['"][^"']+?)_([GH][0-9])""")
    while p.search(text):
        text = p.sub(r"\1 G\2", text)
    # mutual highlighting - less tolerant; keep the first entry only in multiple entries
    p = re.compile(r"""(hl[0-1])(\('','','[^']+?)_[^']+?'""")
    while p.search(text):
        text = p.sub(r"\1\2'", text)
    # mutual highlighting - alternative: less tolerant 2; keep the last entry only in multiple entries
    #p = re.compile(r"""(hl[0-1])(\('','',')[^']+?_([^'_]+?')""")
    #while p.search(text):
    #    text = p.sub(r"\1\2\3", text)
    # mutual highlighting - alternative: more tolerant; include all multiple entries
    #p = re.compile(r"""(hl[0-1])(\('','','[^']+?)_(G[0-9])""")
    #while p.search(text):
    #    text = p.sub(r"\1\2'); \1('','','\3", text)
    return text

config.bibleWindowContentTransformers.append(tagLexicalEntry)
config.studyWindowContentTransformers.append(tagLexicalEntry)
