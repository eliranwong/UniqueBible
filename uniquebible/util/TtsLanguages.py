# coding=utf-8

# langdetect: https://pypi.org/project/langdetect/
# Languages supported by supported:
# af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
# hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
# pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw
# ISO codes: https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

from uniquebible import config

class TtsLanguages:

    isoLang2epeakLang = {
        "af": ("af", "afrikaans", "other/af"),
        "an": ("an", "aragonese", "europe/an"),
        "bg": ("bg", "bulgarian", "europe/bg"),
        "bs": ("bs", "bosnian", "europe/bs"),
        "ca": ("ca", "catalan", "europe/ca"),
        "cs": ("cs", "czech", "europe/cs"),
        "cy": ("cy", "welsh", "europe/cy"),
        "da": ("da", "danish", "europe/da"),
        "de": ("de", "german", "de"),
        # espeak el voice cannot read accented Greek words
        "el": ("el", "greek", "europe/el"),
        # To read accented Greek words, use grc instead of el
        "grc": ("grc", "greek-ancient", "other/grc"),
        #"en": ("en", "default", "default"),
        "en": ("en", "english", "default"),
        #"en-gb": ("en-gb", "english", "en"),
        "en-gb": ("en-gb", "english-gb", "en"),
        "en-sc": ("en-sc", "en-scottish", "other/en-sc"),
        "en-uk-north": ("en-uk-north", "english-north", "other/en-n"),
        "en-uk-rp": ("en-uk-rp", "english_rp", "other/en-rp"),
        "en-uk-wmids": ("en-uk-wmids", "english_wmids", "other/en-wm"),
        "en-us": ("en-us", "english-us", "en-us"),
        "en-wi": ("en-wi", "en-westindies", "other/en-wi"),
        "eo": ("eo", "esperanto", "other/eo"),
        "es": ("es", "spanish", "europe/es"),
        "es-la": ("es-la", "spanish-latin-am", "es-la"),
        "et": ("et", "estonian", "europe/et"),
        "fa": ("fa", "persian", "asia/fa"),
        "fa-pin": ("fa-pin", "persian-pinglish", "asia/fa-pin"),
        "fi": ("fi", "finnish", "europe/fi"),
        "fr-be": ("fr-be", "french-Belgium", "europe/fr-be"),
        "fr": ("fr-fr", "french", "fr"),
        "ga": ("ga", "irish-gaeilge", "europe/ga"),
        "hi": ("hi", "hindi", "asia/hi"),
        "hr": ("hr", "croatian", "europe/hr"),
        "hu": ("hu", "hungarian", "europe/hu"),
        "hy": ("hy", "armenian", "asia/hy"),
        "hy-west": ("hy-west", "armenian-west", "asia/hy-west"),
        "id": ("id", "indonesian", "asia/id"),
        "is": ("is", "icelandic", "europe/is"),
        "it": ("it", "italian", "europe/it"),
        "jbo": ("jbo", "lojban", "other/jbo"),
        "ka": ("ka", "georgian", "asia/ka"),
        "kn": ("kn", "kannada", "asia/kn"),
        "ku": ("ku", "kurdish", "asia/ku"),
        "la": ("la", "latin", "other/la"),
        "lfn": ("lfn", "lingua_franca_nova", "other/lfn"),
        "lt": ("lt", "lithuanian", "europe/lt"),
        "lv": ("lv", "latvian", "europe/lv"),
        "mk": ("mk", "macedonian", "europe/mk"),
        "ml": ("ml", "malayalam", "asia/ml"),
        "ms": ("ms", "malay", "asia/ms"),
        "ne": ("ne", "nepali", "asia/ne"),
        "nl": ("nl", "dutch", "europe/nl"),
        "no": ("no", "norwegian", "europe/no"),
        "pa": ("pa", "punjabi", "asia/pa"),
        "pl": ("pl", "polish", "europe/pl"),
        "pt-br": ("pt-br", "brazil", "pt"),
        "pt": ("pt-pt", "portugal", "europe/pt-pt"),
        "ro": ("ro", "romanian", "europe/ro"),
        "ru": ("ru", "russian", "europe/ru"),
        "sk": ("sk", "slovak", "europe/sk"),
        "sq": ("sq", "albanian", "europe/sq"),
        "sr": ("sr", "serbian", "europe/sr"),
        "sv": ("sv", "swedish", "europe/sv"),
        "sw": ("sw", "swahili-test", "other/sw"),
        "ta": ("ta", "tamil", "asia/ta"),
        "tr": ("tr", "turkish", "asia/tr"),
        "vi": ("vi", "vietnam", "asia/vi"),
        "vi-hue": ("vi-hue", "vietnam_hue", "asia/vi-hue"),
        "vi-sgn": ("vi-sgn", "vietnam_sgn", "asia/vi-sgn"),
        "zh-cn": ("zh", "mandarin", "asia/zh"),
        "zh-tw": ("zh-yue", "cantonese", "asia/zh-yue"),
        "yue": ("zh-yue", "cantonese", "asia/zh-yue"),
        "he": ("he", "hebrew", "he"),
    }

    if config.noQt:
        isoLang2qlocaleLang = {}
    else:
        if config.qtLibrary == "pyside6":
            from PySide6.QtCore import QLocale
        else:
            from qtpy.QtCore import QLocale

        # QLocale: https://doc-snapshots.qt.io/qtforpython-5.14/PySide2/QtCore/QLocale.html
        isoLang2qlocaleLang = {
            "en": (QLocale(QLocale.English, QLocale.UnitedStates), "English-UnitedStates"),
            "it": (QLocale(QLocale.Italian, QLocale.Italy), "Italian-Italy"),
            "sv": (QLocale(QLocale.Swedish, QLocale.Sweden), "Swedish-Sweden"),
            #"": (QLocale(QLocale.French, QLocale.Canada), "French-Canada"),
            "de": (QLocale(QLocale.German, QLocale.Germany), "German-Germany"),
            "he": (QLocale(QLocale.Hebrew, QLocale.Israel), "Hebrew-Israel"),
            "id": (QLocale(QLocale.Indonesian, QLocale.Indonesia), "Indonesian-Indonesia"),
            "en-gb": (QLocale(QLocale.English, QLocale.UnitedKingdom), "English-UnitedKingdom"),
            #"": (QLocale(QLocale.Spanish, QLocale.Argentina), "Spanish-Argentina"),
            #"": (QLocale(QLocale.Dutch, QLocale.Belgium), "Dutch-Belgium"),
            "ro": (QLocale(QLocale.Romanian, QLocale.Romania), "Romanian-Romania"),
            "pt": (QLocale(QLocale.Portuguese, QLocale.Portugal), "Portuguese-Portugal"),
            "es": (QLocale(QLocale.Spanish, QLocale.Spain), "Spanish-Spain"),
            #"": (QLocale(QLocale.Spanish, QLocale.Mexico), "Spanish-Mexico"),
            "th": (QLocale(QLocale.Thai, QLocale.Thailand), "Thai-Thailand"),
            #"": (QLocale(QLocale.English, QLocale.Australia), "English-Australia"),
            "ja": (QLocale(QLocale.Japanese, QLocale.Japan), "Japanese-Japan"),
            "sk": (QLocale(QLocale.Slovak, QLocale.Slovakia), "Slovak-Slovakia"),
            "hi": (QLocale(QLocale.Hindi, QLocale.India), "Hindi-India"),
            "pt": (QLocale(QLocale.Portuguese, QLocale.Brazil), "Portuguese-Brazil"),
            "ar": (QLocale(QLocale.Arabic, QLocale.SaudiArabia), "Arabic-SaudiArabia"),
            "hu": (QLocale(QLocale.Hungarian, QLocale.Hungary), "Hungarian-Hungary"),
            # Use zh-cn for Taiwan Chinese, Taiwanese speaks Mandarin instead of Cantonese
            #"zh-tw": (QLocale(QLocale.Chinese, QLocale.Taiwan), "Chinese-Taiwan"),
            # we use grc here instead of el
            "grc": (QLocale(QLocale.Greek, QLocale.Greece), "Greek-Greece"),
            "ru": (QLocale(QLocale.Russian, QLocale.Russia), "Russian-Russia"),
            #"": (QLocale(QLocale.English, QLocale.Ireland), "English-Ireland"),
            "no": (QLocale(QLocale.NorwegianBokmal, QLocale.Norway), "NorwegianBokmal-Norway"),
            #"": (QLocale(QLocale.English, QLocale.India), "English-India"),
            "da": (QLocale(QLocale.Danish, QLocale.Denmark), "Danish-Denmark"),
            "fi": (QLocale(QLocale.Finnish, QLocale.Finland), "Finnish-Finland"),
            "zh-tw": (QLocale(QLocale.Chinese, QLocale.HongKong), "Chinese-HongKong"),
            #"": (QLocale(QLocale.English, QLocale.SouthAfrica), "English-SouthAfrica"),
            "fr": (QLocale(QLocale.French, QLocale.France), "French-France"),
            "zh-cn": (QLocale(QLocale.Chinese, QLocale.China), "Chinese-China"),
            "nl": (QLocale(QLocale.Dutch, QLocale.Netherlands), "Dutch-Netherlands"),
            "tr": (QLocale(QLocale.Turkish, QLocale.Turkey), "Turkish-Turkey"),
            "ko": (QLocale(QLocale.Korean, QLocale.SouthKorea), "Korean-SouthKorea"),
            "pl": (QLocale(QLocale.Polish, QLocale.Poland), "Polish-Poland"),
            "cs": (QLocale(QLocale.Czech, QLocale.CzechRepublic), "Czech-CzechRepublic"),
        }