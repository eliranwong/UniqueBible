import config, re

def fixHrefLinks(text):
    if config.enableHttpServer:
        return text
    else:
        return re.sub(r"""href=(['"])(http.*?)\1""", r"href='#' onclick={0}document.title='_command:::online:::\2'; document.title='online:::\2'{0}".format('"'), text)

config.bibleWindowContentTransformers.append(fixHrefLinks)
config.studyWindowContentTransformers.append(fixHrefLinks)
