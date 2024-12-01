import requests

from uniquebible import config

class Translator:

    language_mapping = {"de": "de", "el": "el", "en": "en", "en_GB": "en", "en_US": "en", "es": "es", "fr": "fr",
                        "hi": "hi", "it": "it", "ja": "ja", "ko": "ko", "ml": "en", "ro": "ro", "ru": "ru",
                        "zh": "zh", "zh_HANS": "zh", "zt": "zt", "zh_HANT": "zt"}

    fromLanguageCodes = ['ar', 'bg', 'bn', 'bs', 'ca', 'cnr', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'eu',
                         'fi', 'fr', 'fr-CA', 'ga', 'gu', 'he', 'hi', 'hr', 'hu', 'id', 'it', 'ja', 'ko', 'lt', 'lv',
                         'ml', 'ms', 'mt', 'nb', 'ne', 'nl', 'pl', 'pt', 'ro', 'ru', 'si', 'sk', 'sl', 'sr', 'sv', 'ta',
                         'te', 'th', 'tr', 'uk', 'ur', 'vi', 'zh', 'zh-TW']

    fromLanguageNames = ['Arabic', 'Bulgarian', 'Bengali', 'Bosnian', 'Catalan', 'Montenegrin', 'Czech', 'Welsh',
                         'Danish', 'German', 'Greek', 'English', 'Spanish', 'Estonian', 'Basque', 'Finnish', 'French',
                         'French (Canada)', 'Irish', 'Gujarati', 'Hebrew', 'Hindi', 'Croatian', 'Hungarian',
                         'Indonesian', 'Italian', 'Japanese', 'Korean', 'Lithuanian', 'Latvian', 'Malayalam', 'Malay',
                         'Maltese', 'Norwegian Bokmal', 'Nepali', 'Dutch', 'Polish', 'Portuguese', 'Romanian',
                         'Russian', 'Sinhala', 'Slovakian', 'Slovenian', 'Serbian', 'Swedish', 'Tamil', 'Telugu',
                         'Thai', 'Turkish', 'Ukrainian', 'Urdu', 'Vietnamese', 'Simplified Chinese',
                         'Traditional Chinese']

    toLanguageCodes = ['ar', 'bg', 'bn', 'bs', 'ca', 'cnr', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'eu', 'fi', 'fr', 'fr-CA', 'ga', 'gu', 'he', 'hi', 'hr', 'hu', 'id', 'it', 'ja', 'ko', 'lt', 'lv', 'ml', 'ms', 'mt', 'nb', 'ne', 'nl', 'pl', 'pt', 'ro', 'ru', 'si', 'sk', 'sl', 'sr', 'sv', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'vi', 'zh', 'zh-TW']

    toLanguageNames = ['Arabic', 'Bulgarian', 'Bengali', 'Bosnian', 'Catalan', 'Montenegrin', 'Czech', 'Welsh', 'Danish', 'German', 'Greek', 'English', 'Spanish', 'Estonian', 'Basque', 'Finnish', 'French', 'French (Canada)', 'Irish', 'Gujarati', 'Hebrew', 'Hindi', 'Croatian', 'Hungarian', 'Indonesian', 'Italian', 'Japanese', 'Korean', 'Lithuanian', 'Latvian', 'Malayalam', 'Malay', 'Maltese', 'Norwegian Bokmal', 'Nepali', 'Dutch', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Sinhala', 'Slovakian', 'Slovenian', 'Serbian', 'Swedish', 'Tamil', 'Telugu', 'Thai', 'Turkish', 'Ukrainian', 'Urdu', 'Vietnamese', 'Simplified Chinese', 'Traditional Chinese']

    def translate(self, text, fromLanguage="auto", toLanguage="en"):
        toLanguage = self.language_mapping[toLanguage]
        url = config.translate_api_url + "/translate"
        api_key = config.translate_api_key
        payload = {"source": fromLanguage, "target": toLanguage, "q": text, "format": "text", "api_key": api_key}
        data = requests.post(url, json=payload).json()
        if 'translatedText' in data:
            translation = data['translatedText']
        elif 'error' in data:
            translation = data['error']
        else:
            translation = '???'
        return translation

if __name__ == "__main__":
    translator = Translator()
    print(translator.translate("hello", "auto", "zt"))
