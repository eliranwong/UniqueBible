from uniquebible import config
import re

def fixTextColour(text):
    return re.sub("""<font color=['"][0-9]['"]>(.*?)</font>""", r"\1", text)

#config.bibleWindowContentTransformers.append(fixTextColour)
config.studyWindowContentTransformers.append(fixTextColour)
