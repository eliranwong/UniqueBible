import re

from uniquebible import config
from uniquebible.db.BiblesSqlite import BiblesSqlite, Bible, MorphologySqlite
from uniquebible.db.ToolsSqlite import Commentary
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.BibleVerseParser import BibleVerseParser
from uniquebible.util.BibleBooks import BibleBooks

class HtmlGeneratorUtil:

    @staticmethod
    def getAudioPlayer(playlist):
        # Get book name translation
        books = BibleBooks().booksMap.get(config.standardAbbreviation, BibleBooks.abbrev["eng"])

        # Audio Player souce codes: https://github.com/likev/html5-audio-player
        html = """
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>Audio player HTML5</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <link rel="stylesheet" href="css/AudioPlayer.css?v=1.320">
    <style>

    #player{
        position: relative;
        max-width: 100%;
        /*max-width: 700px;*/
        height: 500px;
        border: solid 1px gray;
    }
    </style>
  </head>

  <body>
"""

        # Media player
        html += """
    <!-- Audio player container-->
    <div id='player' style='margin: auto;'></div>

    <!-- Audio player js begin-->
    <script src="js/AudioPlayer.js?v=1.320"></script>

    <script>
        // test image for web notifications
        var iconImage = null;

        AP.init({
            container:'#player',//a string containing one CSS selector
            volume   : 0.7,
            autoPlay : true,
            notification: false,
            playList: [ 
"""

        # Add playlist content
        for title, filePath in playlist:
            elements = title.split("_")
            if len(elements) in (5, 6):
                morphology = MorphologySqlite()
            if len(elements) == 4:
                text, b, c, v = elements
                if b in books:
                    v = v[:-4]
                    if text == "OHGB":
                        verseText = MorphologySqlite().getOriginalVerse(b, c, v)
                    else:
                        verseText = Bible(text).readTextVerse(b, c, v)[-1]
                        verseText = re.sub("({0}|<[^hg].*?>)".format(config.audioBibleIcon), "", verseText)
                        verseText = re.sub("'", "&apos;", verseText)
                        verseText = re.sub('"', "&quot;", verseText)
                    title = "({1} {2}:{3}, {0}) {4}".format(text, books[b][0], c, v, verseText)
            elif len(elements) == 5:
                text, b, c, v, wordID = elements
                wordID = wordID[:-4]
                if b in books:
                    word = morphology.getWord(b, wordID)
                    if word:
                        tag = "heb" if int(b) < 40 else "grk"
                        word = "<{0}>{1}</{0}>".format(tag, word)
                    else:
                        word = wordID
                    title = "{1} {2}:{3} - {4} ({0})".format(text, books[b][0], c, v, word)
            elif len(elements) == 6:
                lex, text, b, c, v, wordID = elements
                wordID = wordID[:-4]
                if b in books:
                    lexeme = morphology.getLexeme(int(b), int(wordID))
                    if lexeme:
                        tag = "heb" if int(b) < 40 else "grk"
                        lexeme = "<{0}>{1}</{0}>".format(tag, lexeme)
                    else:
                        lexeme = wordID
                    title = "{1} {2}:{3} - {4} [{5}] ({0})".format(text, books[b][0], c, v, lexeme, lex)
            html += "{"
            html += "'icon': iconImage, 'title': '_{0}', 'file': '{1}'".format(title, filePath)
            html += "},"
        html += """
          ]
        });
    </script>
    <!-- Audio player js end-->
"""

        # Add chapter navigation
        if playlist:
            firstFile = playlist[0][0]
            elements = firstFile.split("_")
            if elements[0] == "lex":
                lex, text, b, c, *_ = elements
            else:
                text, b, c, *_ = elements
            if not text in ("BHS5", "OGNT"):
                html += "<div style='margin: auto;'><p style='text-align: center;'>"
                html += HtmlGeneratorUtil.previousChapterAudio(text, int(b), int(c))
                html += HtmlGeneratorUtil.getChapterAudioButton(text, b, c, "{0} {1}".format(books[b][0], c))
                html += HtmlGeneratorUtil.nextChapterAudio(text, int(b), int(c))
                html += "</p></div>"

                bible = Bible(text)
                bookList = bible.getBookList()
                for bNo in bookList:
                    chapterList = bible.getChapterList(bNo)
                    commandPrefix = f"READCHAPTER:::{text}.{bNo}."
                    html += HtmlGeneratorUtil.getBibleChapterTable(books[str(bNo)][1], books[str(bNo)][0], chapterList, commandPrefix)

        html += """
  </body>
</html>        
"""
        return html

    @staticmethod
    def getChapterAudioButton(text, b, c, title):
        command = f"READCHAPTER:::{text}.{b}.{c}"
        html = """<button type='button' class='button1' title='{1}' onclick='document.title="{0}"'>{1}</button>""".format(command, title)
        return html

    @staticmethod
    def previousChapterAudio(text, b, c):
        if c > 1:
            newChapter = c - 1
        else:
            newChapter = BibleBooks.getLastChapter(b)
        command = f"READCHAPTER:::{text}.{b}.{newChapter}"
        html = """<button type='button' class='button1' title='{1}' onclick='document.title="{0}"'><span class="material-icons-outlined">navigate_before</span></button>""".format(command, config.thisTranslation["menu4_previous"])
        return html

    @staticmethod
    def nextChapterAudio(text, b, c):
        if c < BibleBooks.getLastChapter(b):
            newChapter = c + 1
        else:
            newChapter = 1
        command = f"READCHAPTER:::{text}.{b}.{newChapter}"
        html = """<button type='button' class='button1' title='{1}' onclick='document.title="{0}"'><span class="material-icons-outlined">navigate_next</span></button>""".format(command, config.thisTranslation["menu4_next"])
        return html


    @staticmethod
    def getBibleChapterTable(bookName, bookAbb, chapterList, commandPrefix="", commandSuffix=""):
        chapters = ""
        for c in chapterList:
            command = "{0}{1}{2}".format(commandPrefix, c, commandSuffix)
            chapters += """<button type='button' class='ubaButton' title='{0} {1}' onclick="document.title='{2}'">{1}</button>""".format(bookAbb, c, command)
            #chapters += """<ref title='{0} {1}' onclick="document.title='{2}'">{1}</ref> """.format(bookAbb, c, command)
        return """
<table>
  <tr>
    <th>{0}</th>
  </tr>
  <tr>
    <td><div style='margin: auto;'><p style='text-align: center;'>{1}</p></div></td>
  </tr>
</table>
""".format(bookName, chapters)

    @staticmethod
    def getBibleVerseTable(bookName, bookAbb, c, verseList, commandPrefix="", commandSuffix=""):
        verses = ""
        for v in verseList:
            command = "{0}{1}{2}".format(commandPrefix, v, commandSuffix)
            verses += """<button type='button' class='ubaButton' title='{0} {1}' onclick="document.title='_stayOnSameTab:::'; document.title='{2}'">{1}</button>""".format(bookAbb, v, command)
        return """
<table>
  <tr>
    <th>{0} {1}</th>
  </tr>
  <tr>
    <td><div style='margin: auto;'><p style='text-align: center;'>{2}</p></div></td>
  </tr>
</table>
""".format(bookName, c, verses)

    @staticmethod
    def getMenu(command, source="main"):
        biblesSqlite = BiblesSqlite()
        parser = BibleVerseParser(config.parserStandarisation)
        items = command.split(".", 3)
        text = items[0]
        versions = biblesSqlite.getBibleList()
        # provide a link to go back the last opened bible verse
        if source == "study":
            mainVerseReference = parser.bcvToVerseReference(config.studyB, config.studyC, config.studyV)
            menu = "<ref onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; {0} - {1}</ref>".format(config.studyText, mainVerseReference)
        else:
            mainVerseReference = parser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
            menu = "<ref onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; {0} - {1}</ref>".format(config.mainText, mainVerseReference)
        # select bible versions
        menu += "<hr><b>{1}</b> {0}".format(biblesSqlite.getTexts(), config.thisTranslation["html_bibles"])
        if text:
            # i.e. text specified; add book menu
            if config.openBibleInMainViewOnly or config.enableHttpServer:
                menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> <button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button>".format(text, mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_open"])
            else:
                if source == "study":
                    anotherView = "<button class='ubaButton' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openMain"])
                else:
                    anotherView = "<button class='ubaButton' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openStudy"])
                menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> <button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {4}".format(text, mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_openHere"], anotherView)
            menu += "<hr><b>{1}</b> {0}".format(biblesSqlite.getBooks(text), config.thisTranslation["html_book"])
            # create a list of inters b, c, v
            bcList = [int(i) for i in items[1:]]
            if bcList:
                check = len(bcList)
                bookNo = bcList[0]
                engFullBookName = BibleBooks().abbrev["eng"][str(bookNo)][-1]
                engFullBookNameWithoutNumber = engFullBookName
                matches = re.match("^[0-9]+? (.*?)$", engFullBookName)
                if matches:
                    engFullBookNameWithoutNumber = matches.group(1)
                # Book specific buttons
                if check >= 1:
                    # i.e. book specified; add chapter menu
                    bookReference = parser.bcvToVerseReference(bookNo, 1, 1)
                    bookAbb = bookReference[:-4]
                    # build open book button
                    if config.openBibleInMainViewOnly or config.enableHttpServer:
                        openOption = "<button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='ubaButton' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='ubaButton' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, bookReference, anotherView, config.thisTranslation["html_openHere"])
                    # build search book by book introduction button
                    introductionButton = "<button class='ubaButton' onclick='document.title=\"SEARCHBOOKCHAPTER:::Tidwell_The_Bible_Book_by_Book:::{0}\"'>{1}</button>".format(engFullBookName, config.thisTranslation["html_introduction"])
                    # build search timelines button
                    timelinesButton = "<button class='ubaButton' onclick='document.title=\"SEARCHBOOKCHAPTER:::Timelines:::{0}\"'>{1}</button>".format(engFullBookName, config.thisTranslation["html_timelines"])
                    # build search encyclopedia button
                    encyclopediaButton = "<button class='ubaButton' onclick='document.title=\"SEARCHTOOL:::{0}:::{1}\"'>{2}</button>".format(config.encyclopedia, engFullBookNameWithoutNumber, config.thisTranslation["context1_encyclopedia"])
                    # build search dictionary button
                    dictionaryButton = "<button class='ubaButton' onclick='document.title=\"SEARCHTOOL:::{0}:::{1}\"'>{2}</button>".format(config.dictionary, engFullBookNameWithoutNumber, config.thisTranslation["context1_dict"])
                    # display selected book
                    menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='bookName(\"{0}\")'>{0}</span> {1}<br>{3} {4} {5} {6}".format(bookAbb, openOption, config.thisTranslation["html_current"], introductionButton, timelinesButton, dictionaryButton, encyclopediaButton)
                    # display book commentaries
                    menu += "<br><br><b>{1}:</b> <span style='color: brown;' onmouseover='bookName(\"{0}\")'>{0}</span>".format(bookAbb, config.thisTranslation["commentaries"])
                    list = Commentary().getCommentaryListThatHasBookAndChapter(bookNo, 0)
                    for commentary in list:
                        button = " <button class='ubaButton' onmouseover='instantInfo(\"{2}\")' onclick='document.title=\"COMMENTARY:::{0}:::{1}\"'>{0}</button>".format(
                            commentary[0], engFullBookName, commentary[1])
                        menu += button
                    # Chapter specific buttons
                    # add chapter menu
                    menu += "<hr><b>{1}</b> {0}".format(biblesSqlite.getChapters(bookNo, text),
                                                        config.thisTranslation["html_chapter"])
                if check >= 2:
                    chapterNo = bcList[1]
                    # i.e. both book and chapter specified; add verse menu
                    chapterReference = parser.bcvToVerseReference(bookNo, chapterNo, 1)
                    # build open chapter button
                    if config.openBibleInMainViewOnly or config.enableHttpServer:
                        openOption = "<button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='ubaButton' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='ubaButton' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, chapterReference, anotherView, config.thisTranslation["html_openHere"])
                    # overview button
                    overviewButton = "<button class='ubaButton' onclick='document.title=\"OVERVIEW:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_overview"])
                    # chapter index button
                    chapterIndexButton = "<button class='ubaButton' onclick='document.title=\"CHAPTERINDEX:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_chapterIndex"])
                    # summary button
                    summaryButton = "<button class='ubaButton' onclick='document.title=\"SUMMARY:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_summary"])
                    # chapter commentary button
                    # chapterCommentaryButton = "<button class='ubaButton' onclick='document.title=\"COMMENTARY:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["menu4_commentary"])
                    # chapter note button
                    chapterNoteButton = " <button class='ubaButton' onclick='document.title=\"_openchapternote:::{0}.{1}\"'>{2}</button>".format(bookNo, chapterNo, config.thisTranslation["menu6_notes"])
                    # selected chapter
                    menu += "<br><br><b>{3}</b> <span style='color: brown;' onmouseover='document.title=\"_info:::Chapter {1}\"'>{1}</span> {2}{4}<br>{5} {6} {7}".format(bookNo, chapterNo, openOption, config.thisTranslation["html_current"], "" if config.enableHttpServer else chapterNoteButton, overviewButton, chapterIndexButton, summaryButton)

                    # display chapter commentaries
                    menu += "<br><br><b>{1}:</b> <span style='color: brown;' onmouseover='instantInfo(\"Chapter {0}\")'>{0}</span>".format(
                        chapterNo, config.thisTranslation["commentaries"])
                    list = Commentary().getCommentaryListThatHasBookAndChapter(bookNo, config.mainC)
                    for commentary in list:
                        button = " <button class='ubaButton' onmouseover='instantInfo(\"{2}\")' onclick='document.title=\"COMMENTARY:::{0}:::{1} {3}\"'>{0}</button>".format(
                            commentary[0], engFullBookName, commentary[1], config.mainC)
                        menu += button

                    # building verse list of slected chapter
                    menu += "<hr><b>{1}</b> {0}".format(biblesSqlite.getVersesMenu(bookNo, chapterNo, text), config.thisTranslation["html_verse"])
                # Verse specific buttons
                if check == 3:
                    verseNo = bcList[2]
                    if config.openBibleInMainViewOnly or config.enableHttpServer:
                        openOption = "<button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='ubaButton' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='ubaButton' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='ubaButton' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, mainVerseReference, anotherView, config.thisTranslation["html_openHere"])
                    verseNoteButton = " <button class='ubaButton' onclick='document.title=\"_openversenote:::{0}.{1}.{2}\"'>{3}</button>".format(bookNo, chapterNo, verseNo, config.thisTranslation["menu6_notes"])
                    menu += "<br><br><b>{5}</b> <span style='color: brown;' onmouseover='document.title=\"_instantVerse:::{0}:::{1}.{2}.{3}\"'>{3}</span> {4}{6}".format(text, bookNo, chapterNo, verseNo, openOption, config.thisTranslation["html_current"], "" if config.enableHttpServer else verseNoteButton)
                    #menu += "<hr><b>{0}</b> ".format(config.thisTranslation["html_features"])
                    menu += "<br>"
                    features = (
                        ("COMPARE", config.thisTranslation["menu4_compareAll"]),
                        ("CROSSREFERENCE", config.thisTranslation["menu4_crossRef"]),
                        ("TSKE", config.thisTranslation["menu4_tske"]),
                        ("TRANSLATION", config.thisTranslation["menu4_traslations"]),
                        ("DISCOURSE", config.thisTranslation["menu4_discourse"]),
                        ("WORDS", config.thisTranslation["menu4_words"]),
                        ("COMBO", config.thisTranslation["menu4_tdw"]),
                        ("COMMENTARY", config.thisTranslation["menu4_commentary"]),
                        ("INDEX", config.thisTranslation["menu4_indexes"]),
                    )
                    for keyword, description in features:
                        menu += "<button class='ubaButton' onclick='document.title=\"{0}:::{1}\"'>{2}</button> ".format(keyword, mainVerseReference, description)
                    #versions = biblesSqlite.getBibleList()
                    # Compare menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='compare{0}'></div> ".format(version)
                            menu += "<script>versionList.push('{0}');</script>".format(version)
                    menu += "<br><button type='button' onclick='checkCompare();' class='ubaButton'>{0}</button>".format(config.thisTranslation["html_showCompare"])
                    # Parallel menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='parallel{0}'></div> ".format(version)
                    menu += "<br><button type='button' onclick='checkParallel();' class='ubaButton'>{0}</button>".format(config.thisTranslation["html_showParallel"])
                    # Diff menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='diff{0}'></div> ".format(version)
                    menu += "<br><button type='button' onclick='checkDiff();' class='ubaButton'>{0}</button>".format(config.thisTranslation["html_showDifference"])
        else:
            # menu - Search a bible
            if source == "study":
                defaultSearchText = config.studyText
            else:
                defaultSearchText = config.mainText
            menu += "<hr><b>{1}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span>".format(defaultSearchText, config.thisTranslation["html_searchBible2"])
            menu += "<br><br><input type='text' id='bibleSearch' style='width:95%' autofocus><br><br>"
            searchOptions = ("COUNT", "SEARCHREFERENCE", "SEARCHOT", "SEARCHNT", "SEARCH", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
            for searchMode in searchOptions:
                menu += "<button  id='{0}' type='button' onclick='checkSearch(\"{0}\", \"{1}\");' class='ubaButton'>{0}</button> ".format(searchMode, defaultSearchText)
            # menu - Search multiple bibles
            menu += "<hr><b>{0}</b> <br>".format(config.thisTranslation["html_searchBibles2"])
            for version in versions:
                if version == defaultSearchText or version == config.favouriteBible:
                    menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='search{0}' checked></div> ".format(version)
                else:
                    menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='search{0}'></div> ".format(version)
                menu += "<script>versionList.push('{0}');</script>".format(version)
            menu += "<br><br><input type='text' id='multiBibleSearch' style='width:95%'><br><br>"
            for searchMode in searchOptions:
                menu += "<button id='multi{0}' type='button' onclick='checkMultiSearch(\"{0}\");' class='ubaButton'>{0}</button> ".format(searchMode)
            # Perform search when "ENTER" key is pressed
            menu += biblesSqlite.inputEntered("bibleSearch", "COUNT")
            menu += biblesSqlite.inputEntered("multiBibleSearch", "multiSEARCH")
        return menu


    @staticmethod
    def getComparisonMenu(command, source="main"):
        biblesSqlite = BiblesSqlite()
        parser = BibleVerseParser(config.parserStandarisation)
        #items = command.split(".", 3)
        #text = items[0]
        versions = biblesSqlite.getBibleList()
        # provide a link to go back the last opened bible verse
        mainVerseReference = parser.bcvToVerseReference(config.mainB, config.mainC, config.mainV)
        menu = "<ref onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>&lt;&lt;&lt; {0} - {1}</ref>".format(config.mainText, mainVerseReference)

        # menu - comparison
        defaultSearchText = config.mainText

        # menu - Search multiple bibles
        menu += "<hr>"
        for version in versions:
            if version == defaultSearchText or version == config.favouriteBible or version == config.favouriteBible2:
                menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='search{0}' checked></div> ".format(version)
            else:
                menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='search{0}'></div> ".format(version)
            menu += "<script>versionList.push('{0}');</script>".format(version)
        menu += "<hr>"
        
        searchOptions = ("PARALLEL", "SIDEBYSIDE", "COMPARE")
        for searchMode in searchOptions:
            menu += "<button id='multi{0}' type='button' onclick='checkComparison(\"{0}\");' class='ubaButton'>{0}</button> ".format(searchMode)

        return menu
