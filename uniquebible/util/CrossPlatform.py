from uniquebible import config
import os, glob, re, traceback
from uniquebible.db.BiblesSqlite import BiblesSqlite, Bible
from uniquebible.db.ToolsSqlite import BookData, IndexesSqlite, Commentary
from uniquebible.db.ToolsSqlite import LexiconData
from uniquebible.util.CatalogUtil import CatalogUtil
from uniquebible.util.ThirdParty import ThirdPartyDictionary
from uniquebible.util.HebrewTransliteration import HebrewTransliteration
from uniquebible.util.TextUtil import TextUtil
from uniquebible.install.module import *
from uniquebible.util.GoogleCloudTTSVoices import GoogleCloudTTS
from uniquebible.util.Languages import Languages
from uniquebible.util.TtsLanguages import TtsLanguages
from uniquebible.util.FileUtil import FileUtil


class CrossPlatform:

    def setupResourceLists(self):
        # bible versions
        self.textList = BiblesSqlite().getBibleList()
        if not config.enableHttpServer and self.textList and not config.mainText in self.textList:
            config.mainText = "KJV" if "KJV" in self.textList else self.textList[0]
        self.textFullNameList = [Bible(text).bibleInfo() for text in self.textList]
        bibleOHGBiPath = os.path.join(config.marvelData, "bibles", "OHGBi.bible")
        morphologyDatabase = os.path.join(config.marvelData, "morphology.sqlite")
        self.strongBibles = ["OHGBi"] if os.path.isfile(bibleOHGBiPath) and os.path.isfile(morphologyDatabase) else []
        self.strongBibles += [text for text in self.textList if Bible(text).bibleStrong()]
        #if self.versionCombo is not None and config.menuLayout in ("focus", "Starter"):
        #    for index, fullName in enumerate(self.textFullNameList):
        #        self.versionCombo.setItemData(index, fullName, Qt.ToolTipRole)
        # commentaries
        self.commentaryList = Commentary().getCommentaryList()
        if self.commentaryList and not config.commentaryText in self.commentaryList:
            config.commentaryText = "CBSC" if "CBSC" in self.commentaryList else self.commentaryList[0]
        #self.commentaryFullNameList = [Commentary(module).commentaryInfo() for module in self.commentaryList]
        self.commentaryFullNameList = []
        for module in self.commentaryList:
            info = Commentary(module).commentaryInfo()
            if info == "https://Marvel.Bible Commentary" and module in Commentary.marvelCommentaries:
                info = Commentary.marvelCommentaries[module]
            self.commentaryFullNameList.append(info)
        if config.enableAICommentary:
            self.commentaryList.insert(0, "AIC")
            self.commentaryFullNameList.insert(0, "AI Commentary")
        # reference book
        # menu10_dialog
        bookData = BookData()
        self.referenceBookList = [book for book, *_ in bookData.getBookList()]
        # open database
        indexes = IndexesSqlite()
        # topic
        # menu5_topics
        topicDictAbb2Name = {abb: name for abb, name in indexes.topicList}
        self.topicListAbb = list(topicDictAbb2Name.keys())
        topicDict = {name: abb for abb, name in indexes.topicList}
        self.topicList = list(topicDict.keys())
        # lexicon
        # context1_originalLexicon
        self.lexiconList = LexiconData().lexiconList
        # dictionary
        # context1_dict
        dictionaryDictAbb2Name = {abb: name for abb, name in indexes.dictionaryList}
        self.dictionaryListAbb = list(dictionaryDictAbb2Name.keys())
        dictionaryDict = {name: abb for abb, name in indexes.dictionaryList}
        self.dictionaryList = list(dictionaryDict.keys())
        # encyclopedia
        # context1_encyclopedia
        encyclopediaDictAbb2Name = {abb: name for abb, name in indexes.encyclopediaList}
        self.encyclopediaListAbb = list(encyclopediaDictAbb2Name.keys())
        encyclopediaDict = {name: abb for abb, name in indexes.encyclopediaList}
        self.encyclopediaList = list(encyclopediaDict.keys())
        # 3rd-party dictionary
        # menu5_3rdDict
        self.thirdPartyDictionaryList = ThirdPartyDictionary(self.isThridPartyDictionary(config.thirdDictionary)).moduleList
        # pdf list
        # self.pdfList = sorted([os.path.basename(file) for file in glob.glob(r"{0}/pdf/*.pdf".format(config.marvelData))])
        self.pdfList = CatalogUtil.getPDFs()
        # epub list
        self.epubList = sorted([os.path.basename(file) for file in glob.glob(r"{0}/epub/*.epub".format(config.marvelData))])
        # docx list
        self.docxList = sorted([os.path.basename(file) for file in glob.glob(r"{0}/docx/*.docx".format(config.marvelData))])
        # installed bible audio modules
        audioBibleDirectory = os.path.join("audio", "bibles")
        if os.path.isdir(audioBibleDirectory):
            self.bibleAudioModules = [name for name in os.listdir(audioBibleDirectory) if os.path.isdir(os.path.join(audioBibleDirectory, name))]
        else:
            self.bibleAudioModules = []
        # data list
        self.dataList = [item for item in FileUtil.fileNamesWithoutExtension(os.path.join(config.packageDir, "plugins", "menu", "Bible_Data"), "txt")]
        # search tool list
        self.searchToolList = self.dictionaryListAbb + self.encyclopediaListAbb + ["EXLBT", "EXLBP", "EXLBL", "mETCBC"]

        self.verseByVerseAudio = {
            "ASV (American accent; verse-by-verse)": ("BBE", "eliranwong/MP3_AmericanStandardVersion_american", "default"),
            "BBE (British accent; verse-by-verse)": ("BBE", "eliranwong/MP3_BibleInBasicEnglish_british", "default"),
            "BHS5 (Hebrew; word-by-word)": ("BHS5", "eliranwong/MP3_BHS5_word-by-word", "default"),
            "BSB (American accent; verse-by-verse)": ("BSB", "eliranwong/MP3_BereanStudyBible_american", "default"),
            "BSB (British accent; verse-by-verse)": ("BSB", "eliranwong/MP3_BereanStudyBible_british", "default"),
            "CUV (Cantonese; verse-by-verse)": ("CUV", "eliranwong/MP3_ChineseUnionVersion_cantonese", "default"),
            "CUVs (Mandarin; verse-by-verse)": ("CUVs", "eliranwong/MP3_ChineseUnionVersion_mandarin", "default"),
            "ERV (British accent; verse-by-verse)": ("ERV", "eliranwong/MP3_EnglishRevisedVersion_british", "default"),
            "ISV (American accent; verse-by-verse)": ("ISV", "eliranwong/MP3_InternationalStandardVersion_american", "default"),
            "ISV (British accent; verse-by-verse)": ("ISV", "eliranwong/MP3_InternationalStandardVersion_british", "default"),
            "KJV (American accent; verse-by-verse)": ("KJV", "eliranwong/MP3_KingJamesVersion_american", "default"),
            "KJV (British accent; verse-by-verse)": ("KJV", "eliranwong/MP3_KingJamesVersion_british", "default"),
            "LEB (American accent; verse-by-verse)": ("LEB", "eliranwong/MP3_LexhamEnglishBible_american", "default"),
            "LEB (British accent; verse-by-verse)": ("LEB", "eliranwong/MP3_LexhamEnglishBible_british", "default"),
            "NET (American accent; verse-by-verse)": ("NET", "eliranwong/MP3_NewEnglishTranslation_american", "default"),
            "NET (British accent; verse-by-verse)": ("NET", "eliranwong/MP3_NewEnglishTranslation_british", "default"),
            "OGNT (Greek; word-by-word)": ("OGNT", "eliranwong/MP3_OpenGNT_word-by-word", "default"),
            "OHGB (Hebrew & Greek; fast; verse-by-verse)": ("OHGB", "eliranwong/MP3_OpenHebrewGreekBible_fast", "default"),
            "OHGB (Hebrew & Greek; slow; verse-by-verse)": ("OHGB", "eliranwong/MP3_OpenHebrewGreekBible_slow", "default"),
            "SBLGNT (Greek; fast; verse-by-verse)": ("SBLGNT", "eliranwong/MP3_SBLGNT_fast", "default"),
            "SBLGNT (Greek; slow; verse-by-verse)": ("SBLGNT", "eliranwong/MP3_SBLGNT_slow", "default"),
            "WEB (British accent; verse-by-verse)": ("WEB", "eliranwong/MP3_WebEnglishBible_british", "default"), 
            "WLC (Hebrew; fast; verse-by-verse)": ("WLC", "eliranwong/MP3_WLC_fast", "default"),
            "WLC (Hebrew; slow; verse-by-verse)": ("WLC", "eliranwong/MP3_WLC_slow", "default"),
        }

        self.resources = {}
        self.resources["bibleListAbb"] = self.textList
        self.resources["strongBibleListAbb"] = self.strongBibles
        self.resources["bibleList"] = self.textFullNameList
        self.resources["commentaryListAbb"] = self.commentaryList
        self.resources["commentaryList"] = self.commentaryFullNameList
        self.resources["referenceBookList"] = self.referenceBookList
        self.resources["topicListAbb"] = self.topicListAbb
        self.resources["topicList"] = self.topicList
        self.resources["lexiconList"] = self.lexiconList
        self.resources["dictionaryListAbb"] = self.dictionaryListAbb
        self.resources["dictionaryList"] = self.dictionaryList
        self.resources["encyclopediaListAbb"] = self.encyclopediaListAbb
        self.resources["encyclopediaList"] = self.encyclopediaList
        self.resources["thirdPartyDictionaryList"] = self.thirdPartyDictionaryList
        self.resources["pdfList"] = self.pdfList
        self.resources["epubList"] = self.epubList
        self.resources["docxList"] = self.docxList
        self.resources["bibleAudioModules"] = self.bibleAudioModules
        self.resources["dataList"] = self.dataList
        self.resources["searchToolList"] = self.searchToolList
        #self.resources["verseByVerseAudio"] = self.verseByVerseAudio

    # Check if a third party dictionary exists:
    def isThridPartyDictionary(self, module):
        bibleBentoPlusLexicon = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(module, ".dic.bbp"))
        eSwordLexicon = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(module, ".lexi"))
        eSwordDictionary = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(module, ".dcti"))
        mySwordDictionary = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(module, ".dct.mybible"))
        myBibleDictionary = os.path.join("thirdParty", "dictionaries", "{0}{1}".format(module, ".dictionary.SQLite3"))

        if os.path.isfile(bibleBentoPlusLexicon):
            return (module, ".dic.bbp")
        elif os.path.isfile(eSwordLexicon):
            return (module, ".lexi")
        elif os.path.isfile(eSwordDictionary):
            return (module, ".dcti")
        elif os.path.isfile(mySwordDictionary):
            return (module, ".dct.mybible")
        elif os.path.isfile(myBibleDictionary):
            return (module, ".dictionary.SQLite3")
        else:
            return None

    # History record management

    def addHistoryRecord(self, view, textCommand, tab="0"):
        if not (config.enableHttpServer and config.webHomePage == "{0}.html".format(config.webPrivateHomePage)):
            if view == "http":
                view = "main"
            if not textCommand.startswith("_") and not re.search("^download:::|^qrcode:::", textCommand.lower()):
    
                if view in ("main", "study"):
                    compareParallel = (textCommand.lower().startswith("compare:::") or textCommand.lower().startswith("parallel:::") or textCommand.lower().startswith("sidebyside:::"))
                    if config.enforceCompareParallel and not config.tempRecord:
                        if not ":::" in textCommand:
                            view = "study"
                            textCommand = "STUDY:::{0}".format(textCommand)
                        elif textCommand.lower().startswith("bible:::"):
                            view = "study"
                            textCommand = re.sub("^.*?:::", "STUDY:::", textCommand)
                    if config.tempRecord:
                        self.runAddHistoryRecord("main", config.tempRecord, tab)
                        config.tempRecord = ""
                    elif not (view == "main" and config.enforceCompareParallel) or compareParallel:
                        self.runAddHistoryRecord(view, textCommand, tab)
                else:
                    self.runAddHistoryRecord(view, textCommand, tab)

    def runAddHistoryRecord(self, view, textCommand, tab):
        if view in ("main", "study"):
            command = textCommand
            if command.count(":::") == 0:
                if view == "main":
                    command = "BIBLE:::{0}:::{1}".format(config.mainText, command)
                elif view == "study":
                    command = "STUDY:::{0}:::{1}".format(config.mainText, command)
            elif command.count(":::") == 1:
                verse = command.find(":::") + 3
                if view == "main":
                    if command.lower().startswith("bible"):
                        command = "BIBLE:::{0}:::{1}".format(config.mainText, command[verse:])
                    elif command.lower().startswith("main"):
                        command = "MAIN:::{0}:::{1}".format(config.mainText, command[verse:])
                elif view == "study" and command.lower().startswith("study"):
                    command = "STUDY:::{0}:::{1}".format(config.mainText, command[verse:])
            config.tabHistory[view][tab] = command
        if view and textCommand and view in config.history:
            viewhistory = config.history[view]
            if not (viewhistory[-1] == textCommand):
                viewhistory.append(textCommand)
                # set maximum number of history records for each view here
                maximumHistoryRecord = config.maximumHistoryRecord
                if len(viewhistory) > maximumHistoryRecord:
                    viewhistory = viewhistory[-maximumHistoryRecord:]
                config.history[view] = viewhistory
                config.currentRecord[view] = len(viewhistory) - 1

    def getHistory(self, view):
        historyRecords = [(counter, record) for counter, record in enumerate(config.history[view])]
        if view == "external":
            html = "<br>".join([
                                   "<button class='ubaButton' onclick='openExternalRecord({0})'>{1}</button> [<ref onclick='editExternalRecord({0})'>edit</ref>]".format(
                                       counter, record) for counter, record in reversed(historyRecords)])
        else:
            html = "<br>".join(
                ["<button class='ubaButton' onclick='openHistoryRecord({0})'>{1}</button>".format(counter, record) for
                 counter, record in reversed(historyRecords)])
        return html

    # Plugins

    def runPlugin(self, fileName):
        script = os.path.join(config.packageDir, "plugins", "menu", "{0}.py".format(fileName))
        if os.path.isfile(script):
            self.execPythonFile(script)
        script = os.path.join(config.ubaUserDir, "plugins", "menu", "{0}.py".format(fileName))
        if os.path.isfile(script):
            self.execPythonFile(script)

    def execPythonFile(self, script):
        if config.developer:
            with open(script, 'r', encoding='utf8') as f:
                code = compile(f.read(), script, 'exec')
                exec(code, globals())
        else:
            try:
                with open(script, 'r', encoding='utf8') as f:
                    code = compile(f.read(), script, 'exec')
                    exec(code, globals())
            except:
                if config.developer:
                    print(traceback.format_exc())
                print("Failed to run '{0}'!".format(os.path.basename(script)))

    # Google text-to-speech

    def getTtsLanguages(self):
        if config.isGoogleCloudTTSAvailable:
            languages = {}
            for language, languageCode in GoogleCloudTTS.getLanguages().items():
                languages[languageCode] = ("", language)
        elif (not ("OfflineTts" in config.enabled) or config.forceOnlineTts) and ("Gtts" in config.enabled):
            languages = {}
            for language, languageCode in Languages.gTTSLanguageCodes.items():
                languages[languageCode] = ("", language)
        elif config.macVoices:
            languages = config.macVoices
        elif config.espeak:
            languages = TtsLanguages().isoLang2epeakLang
        else:
            languages = TtsLanguages().isoLang2qlocaleLang
        # Check default TTS language
        if not config.ttsDefaultLangauge in languages:
            for key in languages.keys():
                if key.startswith("en") or key.startswith("[en"):
                    config.ttsDefaultLangauge = key
                    break
        # return languages
        return languages

    def fineTuneGtts(self, text, language):
        text = re.sub("[\[\]\(\)'\"]", "", text)
        if not config.isGoogleCloudTTSAvailable:
            language = re.sub("\-.*?$", "", language)
        if language in ("iw", "he"):
            text = HebrewTransliteration().transliterateHebrew(text)
            language = "el-GR" if config.isGoogleCloudTTSAvailable else "el"
        elif language == "el" or language.startswith("el-"):
            text = TextUtil.removeVowelAccent(text)
        return (text, language)

    # Temporary filepath for tts export
    def getGttsFilename(self):
        folder = os.path.join(config.musicFolder, "tmp")
        if not os.path.isdir(folder):
            os.makedirs(folder, exist_ok=True)
        return os.path.abspath(os.path.join(folder, "gtts.mp3"))

    # Python package gTTS, not created by Google
    def saveGTTSAudio(self, inputText, languageCode, filename=""):
        try:
            from gtts import gTTS
            moduleInstalled = True
        except:
            moduleInstalled = False
        if not moduleInstalled:
            installmodule("--upgrade gTTS")

        from gtts import gTTS
        tts = gTTS(inputText, lang=languageCode)
        if not filename:
            filename = os.path.abspath(self.getGttsFilename())
        if os.path.isfile(filename):
            os.remove(filename)
        tts.save(filename)

    # Official Google Cloud Text-to-speech Service
    def saveCloudTTSAudio(self, inputText, languageCode, filename=""):
        try:
            from google.cloud import texttospeech
            moduleInstalled = True
        except:
            moduleInstalled = False
        if not moduleInstalled:
            installmodule("--upgrade google-cloud-texttospeech")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.getcwd(), "credentials_GoogleCloudTextToSpeech.json")
        # Modified from source: https://cloud.google.com/text-to-speech/docs/create-audio-text-client-libraries#client-libraries-install-python
        """Synthesizes speech from the input string of text or ssml.
        Make sure to be working in a virtual environment.

        Note: ssml must be well-formed according to:
            https://www.w3.org/TR/speech-synthesis/
        """
        from google.cloud import texttospeech
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=inputText)

        # Build the voice request, select the language code (e.g. "yue-HK") and the ssml
        # voice gender ("neutral")
        # Supported language: https://cloud.google.com/speech-to-text/docs/speech-to-text-supported-languages
        # Voice: https://cloud.google.com/text-to-speech/docs/voices
        # Gener: https://cloud.google.com/text-to-speech/docs/reference/rest/v1/SsmlVoiceGender
        voice = texttospeech.VoiceSelectionParams(
            language_code=languageCode, ssml_gender=texttospeech.SsmlVoiceGender.SSML_VOICE_GENDER_UNSPECIFIED
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            # For more config, read https://cloud.google.com/text-to-speech/docs/reference/rest/v1/text/synthesize#audioconfig
            speaking_rate=config.gcttsSpeed,
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        # Save into mp3
        if not filename:
            filename = os.path.abspath(self.getGttsFilename())
        if os.path.isfile(filename):
            os.remove(filename)
        with open(filename, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            #print('Audio content written to file "{0}"'.format(outputFile))
