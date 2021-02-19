import config
from util.ConfigUtil import ConfigUtil
try:
    from ibm_watson import LanguageTranslatorV3
    from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
    config.enableIBMWatson = True
except:
    ConfigUtil.messageFeatureNotEnabled("Translation Service", "ibm-watson")
    config.enableIBMWatson = False

class Translator:

    def __init__(self):
        if config.enableIBMWatson:
            self.authenticate()
            if self.language_translator is not None and not hasattr(config, "fromLanguageCodes"):
                self.getLanguageLists()
        else:
            self.language_translator = None

    def authenticate(self):
        try:
            authenticator = IAMAuthenticator(config.myIBMWatsonApikey)
            language_translator = LanguageTranslatorV3(
                version='2018-05-01',
                authenticator=authenticator
            )
            language_translator.set_service_url(config.myIBMWatsonUrl)
            #print(language_translator)
            self.language_translator = language_translator
        except:
            self.language_translator = None

    def getLanguageLists(self):
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

    def identify(self, text):
        result = self.language_translator.identify(text).get_result()
        #print(json.dumps(language, indent=2))
        #print(result["languages"][0]["language"])
        return result["languages"][0]["language"]

    def translate(self, text, fromLanguage=None, toLanguage="en"):
        if fromLanguage is None:
            fromLanguage = self.identify(text)
        translation = self.language_translator.translate(
            text=text,
            model_id="{0}-{1}".format(fromLanguage, toLanguage)).get_result()
        #print(json.dumps(translation, indent=2, ensure_ascii=False))
        #print(translation["translations"][0]["translation"])
        return translation["translations"][0]["translation"]


if __name__ == "__main__":
    translator = Translator()
    #translator.identify("这是中文")
    #translator.getLanguageLists()
    #print(config.fromLanguageCodes, config.fromLanguageNames, config.toLanguageCodes, config.toLanguageNames)
    #translator.translate("test", "en", "zh")
