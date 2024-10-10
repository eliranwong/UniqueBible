from uniquebible import config

def fixDisplayColourDarkTheme(text):
    searchReplace = (
        ("color: brown", "color: {0}".format(config.darkThemeActiveVerseColor)),
    )
    for search, replace in searchReplace:
        text = text.replace(search, replace)
    return text

def fixDisplayColourLightTheme(text):
    searchReplace = (
        ("color: brown", "color: {0}".format(config.lightThemeActiveVerseColor)),
    )
    for search, replace in searchReplace:
        text = text.replace(search, replace)
    return text

if config.theme == "default":
    config.bibleWindowContentTransformers.append(fixDisplayColourLightTheme)
    config.studyWindowContentTransformers.append(fixDisplayColourLightTheme)
else:
    config.bibleWindowContentTransformers.append(fixDisplayColourDarkTheme)
    config.studyWindowContentTransformers.append(fixDisplayColourDarkTheme)
