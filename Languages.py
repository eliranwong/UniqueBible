class Languages:

    code = {
        "Chinese (Simplified) 简体中文": "zh_HANS",
        "Chinese (Traditional) 繁體中文": "zh_HANT",
        "English (UK)": "en_GB",
        "English (US)": "en_US",
        "French Français": "fr",
        "German Deutsch": "de",
        "Greek Νέα Ελληνικά": "el",
        "Hindi हिन्दी": "hi",
        "Korean 한국어": "ko",
        "Italian Italiano": "it",
        "Japanese 日本語": "ja",
        "Malayalam മലയാളം": "ml",
        "Russian Русский язык": "ru",
        "Spanish Español": "es",
    }

    @staticmethod
    def decode(code):
        for key in Languages.code.keys():
            if code == Languages.code[key]:
                return key
        return "Unknown"

if __name__ == '__main__':
    print(Languages.decode("ko"))
