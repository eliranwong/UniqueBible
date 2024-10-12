from uniquebible import config
import re

def fixHrefLinks(text):
    if config.enableHttpServer:
        searchRelace = (
            (r"""onclick="website(\('.*?')\)""", r"""onclick="window.open\1, '_blank')"""),
            (r"""onclick='website(\(".*?")\)""", r"""onclick='window.open\1, "_blank")"""),
        )
        for search, replace in searchRelace:
            text = re.sub(search, replace, text)
        return text
    else:
        return re.sub(r"""href=(['"])(http.*?)\1""", r"href='#' onclick={0}document.title='_command:::online:::\2'; document.title='online:::\2'{0}".format('"'), text)

config.bibleWindowContentTransformers.append(fixHrefLinks)
config.studyWindowContentTransformers.append(fixHrefLinks)
