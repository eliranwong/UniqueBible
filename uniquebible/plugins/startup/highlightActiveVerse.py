from uniquebible import config
import re

terminalTextStart = """「tmvs fg="{1}" bg="{0}"」{2}「/tmvs」""".format(config.terminalSearchHighlightBackground, config.terminalSearchHighlightForeground, config.terminalVerseSelectionStart) if config.runMode == "terminal" else ""
terminalTextEnd = """ 「tmvs fg="{1}" bg="{0}"」{2}「/tmvs」""".format(config.terminalSearchHighlightBackground, config.terminalSearchHighlightForeground, config.terminalVerseSelectionEnd) if config.runMode == "terminal" else ""

def highlightActiveVerseMain(text):
    colour = config.darkThemeActiveVerseColor if config.theme in ("dark", "night") else config.lightThemeActiveVerseColor
    bg = config.darkThemeActiveVerseBackgroundColor if config.theme in ("dark", "night") else config.lightThemeActiveVerseBackgroundColor
    style = f"color: {colour};" + (f" background-color: {bg};" if bg else "")
    searchReplace = (
        # underline
        #('(<vid id="v{0}\.{1}\.{2}".*?</vid>)(.*?)</verse>'.format(config.mainB, config.mainC, config.mainV), r"\1<u>\2</u></verse>"),
        # color
        (r"(<span id='s{0}\.{1}\.{2}'.*?>)(.*?)</span>".format(config.mainB, config.mainC, config.mainV), r"\1<span style='{0}'>{1}\2{2}</span></span>".format(style, terminalTextStart, terminalTextEnd)),
        (r'(<vid id="v{0}\.{1}\.{2}".*?</vid>)(.*?)</verse>'.format(config.mainB, config.mainC, config.mainV), r"\1<span style='{0}'>{1}\2{2}</span></verse>".format(style, terminalTextStart, terminalTextEnd)),
        (r"""(document\.title="_menu:::)([^<>]+?)(\.{0}\.{1}\.{2}"'>\2</ref>\)</sup></td><td><bibletext class='\2'>)(.*?)</bibletext>""".format(config.mainB, config.mainC, config.mainV), r"\1\2\3<span style='{0}'>{1}\4{2}</span></bibletext>".format(style, terminalTextStart, terminalTextEnd)),
    )
    for search, replace in searchReplace:
        text = re.sub(search, replace, text)
    return text

def highlightActiveVerseStudy(text):
    colour = config.darkThemeActiveVerseColor if config.theme in ("dark", "night") else config.lightThemeActiveVerseColor
    bg = config.darkThemeActiveVerseBackgroundColor if config.theme in ("dark", "night") else config.lightThemeActiveVerseBackgroundColor
    style = f"color: {colour};" + (f" background-color: {bg};" if bg else "")
    searchReplace = (
        # underline
        #('(<vid id="v{0}\.{1}\.{2}".*?</vid>)(.*?)</verse>'.format(config.studyB, config.studyC, config.studyV), r"\1<u>\2</u></verse>"),
        # color
        (r"(<span id='s{0}\.{1}\.{2}'.*?>)(.*?)</span>".format(config.studyB, config.studyC, config.studyV), r"\1<span style='{0}'>{1}\2{2}</span></span>".format(style, terminalTextStart, terminalTextEnd)),
        (r'(<vid id="v{0}\.{1}\.{2}".*?</vid>)(.*?)</verse>'.format(config.studyB, config.studyC, config.studyV), r"\1<span style='{0}'>{1}\2{2}</span></verse>".format(style, terminalTextStart, terminalTextEnd)),
    )
    for search, replace in searchReplace:
        text = re.sub(search, replace, text)
    return text

config.bibleWindowContentTransformers.append(highlightActiveVerseMain)
config.studyWindowContentTransformers.append(highlightActiveVerseStudy)
