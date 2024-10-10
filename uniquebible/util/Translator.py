from uniquebible import config

class Translator:

    fromLanguageCodes = ['ar', 'bg', 'bn', 'bs', 'ca', 'cnr', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'eu', 'fi', 'fr', 'fr-CA', 'ga', 'gu', 'he', 'hi', 'hr', 'hu', 'id', 'it', 'ja', 'ko', 'lt', 'lv', 'ml', 'ms', 'mt', 'nb', 'ne', 'nl', 'pl', 'pt', 'ro', 'ru', 'si', 'sk', 'sl', 'sr', 'sv', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'vi', 'zh', 'zh-TW']

    fromLanguageNames = ['Arabic', 'Bulgarian', 'Bengali', 'Bosnian', 'Catalan', 'Montenegrin', 'Czech', 'Welsh', 'Danish', 'German', 'Greek', 'English', 'Spanish', 'Estonian', 'Basque', 'Finnish', 'French', 'French (Canada)', 'Irish', 'Gujarati', 'Hebrew', 'Hindi', 'Croatian', 'Hungarian', 'Indonesian', 'Italian', 'Japanese', 'Korean', 'Lithuanian', 'Latvian', 'Malayalam', 'Malay', 'Maltese', 'Norwegian Bokmal', 'Nepali', 'Dutch', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Sinhala', 'Slovakian', 'Slovenian', 'Serbian', 'Swedish', 'Tamil', 'Telugu', 'Thai', 'Turkish', 'Ukrainian', 'Urdu', 'Vietnamese', 'Simplified Chinese', 'Traditional Chinese']

    toLanguageCodes = ['ar', 'bg', 'bn', 'bs', 'ca', 'cnr', 'cs', 'cy', 'da', 'de', 'el', 'en', 'es', 'et', 'eu', 'fi', 'fr', 'fr-CA', 'ga', 'gu', 'he', 'hi', 'hr', 'hu', 'id', 'it', 'ja', 'ko', 'lt', 'lv', 'ml', 'ms', 'mt', 'nb', 'ne', 'nl', 'pl', 'pt', 'ro', 'ru', 'si', 'sk', 'sl', 'sr', 'sv', 'ta', 'te', 'th', 'tr', 'uk', 'ur', 'vi', 'zh', 'zh-TW']

    toLanguageNames = ['Arabic', 'Bulgarian', 'Bengali', 'Bosnian', 'Catalan', 'Montenegrin', 'Czech', 'Welsh', 'Danish', 'German', 'Greek', 'English', 'Spanish', 'Estonian', 'Basque', 'Finnish', 'French', 'French (Canada)', 'Irish', 'Gujarati', 'Hebrew', 'Hindi', 'Croatian', 'Hungarian', 'Indonesian', 'Italian', 'Japanese', 'Korean', 'Lithuanian', 'Latvian', 'Malayalam', 'Malay', 'Maltese', 'Norwegian Bokmal', 'Nepali', 'Dutch', 'Polish', 'Portuguese', 'Romanian', 'Russian', 'Sinhala', 'Slovakian', 'Slovenian', 'Serbian', 'Swedish', 'Tamil', 'Telugu', 'Thai', 'Turkish', 'Ukrainian', 'Urdu', 'Vietnamese', 'Simplified Chinese', 'Traditional Chinese']

    def __init__(self):
        self.authenticate()

    def authenticate(self):
        try:
            if ("Ibmwatson" in config.enabled) and config.myIBMWatsonApikey:
                from ibm_watson import LanguageTranslatorV3
                from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

                authenticator = IAMAuthenticator(config.myIBMWatsonApikey)
                language_translator = LanguageTranslatorV3(
                    version=config.myIBMWatsonVersion,
                    authenticator=authenticator
                )
                language_translator.set_service_url(config.myIBMWatsonUrl)
                # print(language_translator)
                self.language_translator = language_translator
            else:
                self.language_translator = None
        except Exception as ex:
            print(ex)
            self.language_translator = None

    def getLanguageLists(self):
        try:
            languages = self.language_translator.list_languages().get_result()
            #print(json.dumps(languages, indent=2))
            config.fromLanguageCodes = []
            config.fromLanguageNames = []
            config.toLanguageCodes = []
            config.toLanguageNames = []
            for i in languages["languages"]:
                if i["supported_as_source"]:
                    config.fromLanguageCodes.append(i["language"])
                    config.fromLanguageNames.append(i["language_name"])
                if i["supported_as_target"]:
                    config.toLanguageCodes.append(i["language"])
                    config.toLanguageNames.append(i["language_name"])
            #print(config.fromLanguageCodes, config.fromLanguageNames, config.toLanguageCodes, config.toLanguageNames)
        except:
            self.language_translator = None

    def identify(self, text):
        result = self.language_translator.identify(text).get_result()
        #print(json.dumps(language, indent=2))
        #print(result["languages"][0]["language"])
        return result["languages"][0]["language"]

    def translate(self, text, fromLanguage=None, toLanguage="en"):
        if fromLanguage is None:
            fromLanguage = self.identify(text)
        if self.language_translator:
            translation = self.language_translator.translate(
                text=text,
                model_id="{0}-{1}".format(fromLanguage, toLanguage)).get_result()
            #print(json.dumps(translation, indent=2, ensure_ascii=False))
            #print(translation["translations"][0]["translation"])
            return translation["translations"][0]["translation"]
        else:
            return "<Translator not enabled>"


if __name__ == "__main__":
    config.updateModules("Ibmwatson", True)
    translator = Translator()
    #translator.identify("这是中文")
    #translator.getLanguageLists()
    #print(config.fromLanguageCodes, config.fromLanguageNames, config.toLanguageCodes, config.toLanguageNames)
    print(translator.translate("test", "en", "zh"))
