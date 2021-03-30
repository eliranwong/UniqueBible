import config

def fixDisplayColourDarkTheme(text):
    searchReplace = (
        ("color: brown", "color: rgb(209, 186, 109)"),
    )
    for search, replace in searchReplace:
        text = text.replace(search, replace)
    return text

if config.theme == "dark":
    config.bibleWindowContentTransformers.append(fixDisplayColourDarkTheme)
    config.studyWindowContentTransformers.append(fixDisplayColourDarkTheme)
