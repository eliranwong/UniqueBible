from uniquebible import config
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from prompt_toolkit.shortcuts import input_dialog, radiolist_dialog, checkboxlist_dialog, message_dialog
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter
from uniquebible.util.PromptValidator import NumberValidator
from uniquebible.db.BiblesSqlite import Bible
from uniquebible.db.ToolsSqlite import Book


class TerminalModeDialogs:

    def __init__(self, parent) -> None:
        self.parent = parent
        self.bibles = [(abb, self.parent.crossPlatform.textFullNameList[index]) for index, abb in enumerate(self.parent.crossPlatform.textList)]
        self.style = Style.from_dict(
            {
                "dialog": "bg:ansiblack",
                "dialog text-area": f"bg:ansiblack {config.terminalCommandEntryColor2}",
                "dialog text-area.prompt": config.terminalPromptIndicatorColor2,
                "dialog radio-checked": config.terminalResourceLinkColor,
                "dialog checkbox-checked": config.terminalResourceLinkColor,
                "dialog button.arrow": config.terminalResourceLinkColor,
                "dialog button.focused": f"bg:{config.terminalResourceLinkColor} ansiblack",
                "dialog frame.border": config.terminalResourceLinkColor,
                "dialog frame.label": f"bg:ansiblack {config.terminalResourceLinkColor}",
                "dialog.body": "bg:ansiblack ansiwhite",
                "dialog shadow": "bg:ansiblack",
            }
        ) if config.terminalResourceLinkColor.startswith("ansibright") else Style.from_dict(
            {
                "dialog": "bg:ansiwhite",
                "dialog text-area": f"bg:ansiblack {config.terminalCommandEntryColor2}",
                "dialog text-area.prompt": config.terminalPromptIndicatorColor2,
                "dialog radio-checked": config.terminalResourceLinkColor,
                "dialog checkbox-checked": config.terminalResourceLinkColor,
                "dialog button.arrow": config.terminalResourceLinkColor,
                "dialog button.focused": f"bg:{config.terminalResourceLinkColor} ansiblack",
                "dialog frame.border": config.terminalResourceLinkColor,
                "dialog frame.label": f"bg:ansiwhite {config.terminalResourceLinkColor}",
                "dialog.body": "bg:ansiwhite ansiblack",
                "dialog shadow": "bg:ansiwhite",
            }
        )

    # a wrapper to standard input_dialog; open radiolist_dialog showing available options when user input is not a valid option.
    def searchableInput(self, title="Text Entry", text="Enter / Search:", default="", completer=None, options=[], descriptions=[], validator=None, numberOnly=False, password=False, ok_text="OK", cancel_text="Cancel"):
        if completer is None and options:
            completer = FuzzyCompleter(WordCompleter(options, ignore_case=True))
        if validator is None and numberOnly:
            validator=NumberValidator()
        result = input_dialog(
            title=title,
            text=text,
            default=default,
            completer=completer,
            validator=validator,
            password=password,
            ok_text=ok_text,
            cancel_text=cancel_text,
            style=self.style,
        ).run().strip()
        if result.lower() == config.terminal_cancel_action:
            return result
        if options:
            if result and result in options:
                return result
            else:
                return self.getValidOptions(options=options, descriptions=descriptions, filter=result, default=default)
        else:
            if result:
                return result
            else:
                return ""

    def getValidOptions(self, options=[], descriptions=[], bold_descriptions=False, filter="", default="", title="Available Options", text="Select an item:"):
        if not options:
            return ""
        filter = filter.strip().lower()
        if descriptions:
            descriptionslower = [i.lower() for i in descriptions]
            values = [(option, HTML(f"<b>{descriptions[index]}</b>") if bold_descriptions else descriptions[index]) for index, option in enumerate(options) if (filter in option.lower() or filter in descriptionslower[index])]
        else:
            values = [(option, option) for option in options if filter in option.lower()]
        if not values:
            if descriptions:
                values = [(option, HTML(f"<b>{descriptions[index]}</b>") if bold_descriptions else descriptions[index]) for index, option in enumerate(options)]
            else:
                values = [(option, option) for option in options]
        result = radiolist_dialog(
            title=title,
            text=text,
            values=values,
            default=default if default and default in options else values[0][0],
            style=self.style,
        ).run()
        if result:
            self.parent.print(result)
            return result
        return ""

    def displayFeatureMenu(self, heading, features):
        values = [(command, command if config.terminalDisplayCommandOnMenu else self.parent.dotCommands[command][0]) for command in features]
        result = radiolist_dialog(
            title=heading,
            text="Select a feature:",
            values=values,
            default=features[0],
            style=self.style,
        ).run()
        if result:
            self.parent.printRunningCommand(result)
            return self.parent.getContent(result)
        else:
            return self.parent.cancelAction()
            #return ""

    def getbible(self, title="Bible Selection", default=config.mainText, text="Select a version:"):
        return radiolist_dialog(
            title=title,
            text=title,
            values=self.bibles,
            default=default,
            style=self.style,
        ).run()

    def getBibles(self, title="Bible Comparison", text="Select bible versions:", default_values=[]):
        if not default_values:
            default_values = config.compareParallelList
        return checkboxlist_dialog(
            title=title,
            text=text,
            values=self.bibles,
            default_values=default_values,
            style=self.style,
        ).run()

    def getMultipleSelection(self, title="Bible Books", text="Select book(s):", options=["ALL"], descriptions=["ALL"], default_values=["ALL"]):
        if not default_values:
            default_values = config.compareParallelList
        if descriptions:
            values = [(option, descriptions[index]) for index, option in enumerate(options)]
        else:
            values = [(option, option) for option in options]
        return checkboxlist_dialog(
            title=title,
            text=text,
            values=values,
            default_values=default_values,
            style=self.style,
        ).run()

    def changebible(self):
        result = self.getbible("Change Bible", config.mainText)
        if result:
            return self.parent.getContent(f"TEXT:::{result}")
        else:
            return self.parent.cancelAction()

    def changebibles(self):
        results = self.getBibles()
        if results:
            config.terminalBibleComparison = True
            config.compareParallelList = results
            return self.parent.getContent(".latestbible")
        else:
            return self.parent.cancelAction()

    def changefavouritebible1(self):
        result = radiolist_dialog(
            title="Change Favourite Bible Version 1",
            text="Select a version:",
            values=self.bibles,
            default=config.favouriteBible,
            style=self.style,
        ).run()
        if result:
            config.favouriteBible = result
            message_dialog(
                title="Changed!",
                text=f"config.favouriteBible = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changefavouritebible2(self):
        result = radiolist_dialog(
            title="Change Favourite Bible Version 2",
            text="Select a version:",
            values=self.bibles,
            default=config.favouriteBible2,
            style=self.style,
        ).run()
        if result:
            config.favouriteBible2 = result
            message_dialog(
                title="Changed!",
                text=f"config.favouriteBible2 = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changefavouritebible3(self):
        result = radiolist_dialog(
            title="Change Favourite Bible Version 3",
            text="Select a version:",
            values=self.bibles,
            default=config.favouriteBible3,
            style=self.style,
        ).run()
        if result:
            config.favouriteBible3 = result
            message_dialog(
                title="Changed!",
                text=f"config.favouriteBible3 = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changefavouriteoriginalbible(self):
        result = radiolist_dialog(
            title="Change Favourite Hebrew & Greek Bible",
            text="Select a version:",
            values=self.bibles,
            default=config.favouriteOriginalBible,
            style=self.style,
        ).run()
        if result:
            config.favouriteOriginalBible = result
            message_dialog(
                title="Changed!",
                text=f"config.favouriteOriginalBible = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changecommentary(self):
        result = radiolist_dialog(
            title="Change Commentary Module",
            text="Select a commentary:",
            values=[(abb, self.parent.crossPlatform.commentaryFullNameList[index]) for index, abb in enumerate(self.parent.crossPlatform.commentaryList)],
            default=config.commentaryText,
            style=self.style,
        ).run()
        if result:
            return self.parent.getContent(f"COMMENTARY:::{result}:::")
        else:
            return self.parent.cancelAction()

    def changelexicon(self):
        result = radiolist_dialog(
            title="Change Lexicon",
            text="Select a lexicon:",
            values=[(abb, self.parent.crossPlatform.lexiconList[index]) for index, abb in enumerate(self.parent.crossPlatform.lexiconList)],
            default=config.lexicon,
            style=self.style,
        ).run()
        if result:
            config.lexicon = result
            message_dialog(
                title="Changed!",
                text=f"config.lexicon = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changedictionary(self):
        result = radiolist_dialog(
            title="Change Dictionary",
            text="Select a dictionary:",
            values=[(abb, self.parent.crossPlatform.dictionaryList[index]) for index, abb in enumerate(self.parent.crossPlatform.dictionaryListAbb)],
            default=config.dictionary,
            style=self.style,
        ).run()
        if result:
            config.dictionary = result
            message_dialog(
                title="Changed!",
                text=f"config.dictionary = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changethirdpartydictionary(self):
        result = radiolist_dialog(
            title="Change Third-party Dictionary",
            text="Select a third-party dictionary:",
            values=[(abb, self.parent.crossPlatform.thirdPartyDictionaryList[index]) for index, abb in enumerate(self.parent.crossPlatform.thirdPartyDictionaryList)],
            default=config.thirdDictionary,
            style=self.style,
        ).run()
        if result:
            config.thirdDictionary = result
            message_dialog(
                title="Changed!",
                text=f"config.thirdDictionary = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changeencyclopedia(self):
        result = radiolist_dialog(
            title="Change Encyclopedia",
            text="Select an encyclopedia:",
            values=[(abb, self.parent.crossPlatform.encyclopediaList[index]) for index, abb in enumerate(self.parent.crossPlatform.encyclopediaListAbb)],
            default=config.encyclopedia,
            style=self.style,
        ).run()
        if result:
            config.encyclopedia = result
            message_dialog(
                title="Changed!",
                text=f"config.encyclopedia = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changeconcordance(self):
        strongBiblesFullNameList = [Bible(text).bibleInfo() for text in self.parent.crossPlatform.strongBibles]
        result = radiolist_dialog(
            title="Change Concordance",
            text="Select a concordance:",
            values=[(abb, strongBiblesFullNameList[index]) for index, abb in enumerate(self.parent.crossPlatform.strongBibles)],
            default=config.concordance,
            style=self.style,
        ).run()
        if result:
            config.concordance = result
            message_dialog(
                title="Changed!",
                text=f"config.concordance = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changereferencebook(self):
        result = radiolist_dialog(
            title="Change Reference Book",
            text="Select a book:",
            values=[(abb, self.parent.crossPlatform.referenceBookList[index]) for index, abb in enumerate(self.parent.crossPlatform.referenceBookList)],
            default=config.book,
            style=self.style,
        ).run()
        if result:
            config.book = result
            return self.changereferencebookchapter()
        else:
            return self.parent.cancelAction()

    def changereferencebookchapter(self):
        chapterList = Book(config.book).getTopicList()
        if chapterList:
            result = radiolist_dialog(
                title="Change Book Chapter",
                text="Select a chapter:",
                values=[(abb, chapterList[index]) for index, abb in enumerate(chapterList)],
                default=chapterList[0],
                style=self.style,
            ).run()
            if result:
                return self.parent.getContent(f"BOOK:::{config.book}:::{result}")
        else:
            return self.parent.cancelAction()

    def changenoteeditor(self):
        values = [
                ("", "built-in"),
                ("micro", "micro"),
                ("nano --softwrap --atblanks -", "nano"),
                ("vi -", "vi"),
                ("vim -", "vim"),
            ]
        result = radiolist_dialog(
            title="Change Editor",
            text="Select an editor:",
            values=values,
            default=config.terminalNoteEditor,
            style=self.style,
        ).run()
        config.terminalNoteEditor = result
        message_dialog(
            title="Changed!",
            text=f"config.terminalNoteEditor = '{result}'",
            style=self.style,
        ).run()

    def changebiblesearchmode(self):
        values = [
                (0, "COUNT"),
                (1, "SEARCH"),
                (2, "ANDSEARCH"),
                (3, "ORSEARCH"),
                (4, "ADVANCEDSEARCH"),
                (5, "REGEXSEARCH"),
            ]
        result = radiolist_dialog(
            title="Change Serach Bible Mode",
            text="Select a keyword:",
            values=values,
            default=config.bibleSearchMode,
            style=self.style,
        ).run()
        config.bibleSearchMode = result
        message_dialog(
            title="Changed!",
            text=f"config.bibleSearchMode = {result}",
            style=self.style,
        ).run()

    def getttslanguage(self, title="Change TTS Language", default=config.ttsDefaultLangauge):
        codes = self.parent.ttsLanguageCodes
        return radiolist_dialog(
            title=title,
            text="Select a language:",
            values=[(code, self.parent.ttsLanguages[code][-1]) for code in codes],
            default=default if default in codes else codes[0],
            style=self.style,
        ).run()

    def changettslanguage1(self):
        result = self.getttslanguage("Change TTS Language 1", config.ttsDefaultLangauge)
        if result:
            config.ttsDefaultLangauge = result
            message_dialog(
                title="Changed!",
                text=f"config.ttsDefaultLangauge = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changettslanguage2(self):
        result = self.getttslanguage("Change TTS Language 2", config.ttsDefaultLangauge2)
        if result:
            config.ttsDefaultLangauge2 = result
            message_dialog(
                title="Changed!",
                text=f"config.ttsDefaultLangauge2 = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changettslanguage3(self):
        result = self.getttslanguage("Change TTS Language 3", config.ttsDefaultLangauge3)
        if result:
            config.ttsDefaultLangauge3 = result
            message_dialog(
                title="Changed!",
                text=f"config.ttsDefaultLangauge3 = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()

    def changettslanguage4(self):
        result = self.getttslanguage("Change TTS Language 3", config.ttsDefaultLangauge4)
        if result:
            config.ttsDefaultLangauge4 = result
            message_dialog(
                title="Changed!",
                text=f"config.ttsDefaultLangauge4 = '{result}'",
                style=self.style,
            ).run()
        else:
            return self.parent.cancelAction()
