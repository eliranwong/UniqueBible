import config, re

def highlightActiveVerseMain(text):
    colour = config.activeVerseNoColourDark if config.theme == "dark" else config.activeVerseNoColourLight
    searchReplace = (
        # underline
        #('(<vid id="v{0}\.{1}\.{2}".*?</vid>)(.*?)</verse>'.format(config.mainB, config.mainC, config.mainV), r"\1<u>\2</u></verse>"),
        # color
        ("(<span id='s{0}\.{1}\.{2}'.*?>)(.*?)</span>".format(config.mainB, config.mainC, config.mainV), r"\1<span style='color: {0};'>\2</span></span>".format(colour)),
        ('(<vid id="v{0}\.{1}\.{2}".*?</vid>)(.*?)</verse>'.format(config.mainB, config.mainC, config.mainV), r"\1<span style='color: {0};'>\2</span></verse>".format(colour)),
    )
    for search, replace in searchReplace:
        text = re.sub(search, replace, text)
    return text

def highlightActiveVerseStudy(text):
    colour = config.activeVerseNoColourDark if config.theme == "dark" else config.activeVerseNoColourLight
    searchReplace = (
        # underline
        #('(<vid id="v{0}\.{1}\.{2}".*?</vid>)(.*?)</verse>'.format(config.studyB, config.studyC, config.studyV), r"\1<u>\2</u></verse>"),
        # color
        ("(<span id='s{0}\.{1}\.{2}'.*?>)(.*?)</span>".format(config.studyB, config.studyC, config.studyV), r"\1<span style='color: {0};'>\2</span></span>".format(colour)),
        ('(<vid id="v{0}\.{1}\.{2}".*?</vid>)(.*?)</verse>'.format(config.studyB, config.studyC, config.studyV), r"\1<span style='color: {0};'>\2</span></verse>".format(colour)),
    )
    for search, replace in searchReplace:
        text = re.sub(search, replace, text)
    return text

config.bibleWindowContentTransformers.append(highlightActiveVerseMain)
config.studyWindowContentTransformers.append(highlightActiveVerseStudy)
