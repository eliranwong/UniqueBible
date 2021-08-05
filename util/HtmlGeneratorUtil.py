import re

import config
from db.BiblesSqlite import BiblesSqlite
from db.ToolsSqlite import Commentary
from util.BibleBooks import BibleBooks
from util.BibleVerseParser import BibleVerseParser


class HtmlGeneratorUtil:


    def getMenu(self, command, source="main"):
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
                menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> <button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button>".format(text, mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_open"])
            else:
                if source == "study":
                    anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openMain"])
                else:
                    anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openStudy"])
                menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> <button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {4}".format(text, mainVerseReference, config.thisTranslation["html_current"], config.thisTranslation["html_openHere"], anotherView)
            menu += "<hr><b>{1}</b> {0}".format(biblesSqlite.getBooks(text), config.thisTranslation["html_book"])
            # create a list of inters b, c, v
            bcList = [int(i) for i in items[1:]]
            if bcList:
                check = len(bcList)
                bookNo = bcList[0]
                engFullBookName = BibleBooks().eng[str(bookNo)][-1]
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
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, bookReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, bookReference, anotherView, config.thisTranslation["html_openHere"])
                    # build search book by book introduction button
                    introductionButton = "<button class='feature' onclick='document.title=\"SEARCHBOOKCHAPTER:::Tidwell_The_Bible_Book_by_Book:::{0}\"'>{1}</button>".format(engFullBookName, config.thisTranslation["html_introduction"])
                    # build search timelines button
                    timelinesButton = "<button class='feature' onclick='document.title=\"SEARCHBOOKCHAPTER:::Timelines:::{0}\"'>{1}</button>".format(engFullBookName, config.thisTranslation["html_timelines"])
                    # build search encyclopedia button
                    encyclopediaButton = "<button class='feature' onclick='document.title=\"SEARCHTOOL:::{0}:::{1}\"'>{2}</button>".format(config.encyclopedia, engFullBookNameWithoutNumber, config.thisTranslation["context1_encyclopedia"])
                    # build search dictionary button
                    dictionaryButton = "<button class='feature' onclick='document.title=\"SEARCHTOOL:::{0}:::{1}\"'>{2}</button>".format(config.dictionary, engFullBookNameWithoutNumber, config.thisTranslation["context1_dict"])
                    # display selected book
                    menu += "<br><br><b>{2}</b> <span style='color: brown;' onmouseover='bookName(\"{0}\")'>{0}</span> {1}<br>{3} {4} {5} {6}".format(bookAbb, openOption, config.thisTranslation["html_current"], introductionButton, timelinesButton, dictionaryButton, encyclopediaButton)
                    # display book commentaries
                    menu += "<br><br><b>{1}:</b> <span style='color: brown;' onmouseover='bookName(\"{0}\")'>{0}</span>".format(bookAbb, config.thisTranslation["commentaries"])
                    list = Commentary().getCommentaryListThatHasBookAndChapter(bookNo, 0)
                    for commentary in list:
                        button = " <button class='feature' onmouseover='instantInfo(\"{2}\")' onclick='document.title=\"COMMENTARY:::{0}:::{1}\"'>{0}</button>".format(
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
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, chapterReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, chapterReference, anotherView, config.thisTranslation["html_openHere"])
                    # overview button
                    overviewButton = "<button class='feature' onclick='document.title=\"OVERVIEW:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_overview"])
                    # chapter index button
                    chapterIndexButton = "<button class='feature' onclick='document.title=\"CHAPTERINDEX:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_chapterIndex"])
                    # summary button
                    summaryButton = "<button class='feature' onclick='document.title=\"SUMMARY:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["html_summary"])
                    # chapter commentary button
                    # chapterCommentaryButton = "<button class='feature' onclick='document.title=\"COMMENTARY:::{0} {1}\"'>{2}</button>".format(bookAbb, chapterNo, config.thisTranslation["menu4_commentary"])
                    # chapter note button
                    chapterNoteButton = " <button class='feature' onclick='document.title=\"_openchapternote:::{0}.{1}\"'>{2}</button>".format(bookNo, chapterNo, config.thisTranslation["menu6_notes"])
                    # selected chapter
                    menu += "<br><br><b>{3}</b> <span style='color: brown;' onmouseover='document.title=\"_info:::Chapter {1}\"'>{1}</span> {2}{4}<br>{5} {6} {7}".format(bookNo, chapterNo, openOption, config.thisTranslation["html_current"], "" if config.enableHttpServer else chapterNoteButton, overviewButton, chapterIndexButton, summaryButton)

                    # display chapter commentaries
                    menu += "<br><br><b>{1}:</b> <span style='color: brown;' onmouseover='instantInfo(\"Chapter {0}\")'>{0}</span>".format(
                        chapterNo, config.thisTranslation["commentaries"])
                    list = Commentary().getCommentaryListThatHasBookAndChapter(bookNo, config.mainC)
                    for commentary in list:
                        button = " <button class='feature' onmouseover='instantInfo(\"{2}\")' onclick='document.title=\"COMMENTARY:::{0}:::{1} {3}\"'>{0}</button>".format(
                            commentary[0], engFullBookName, commentary[1], config.mainC)
                        menu += button

                    # building verse list of slected chapter
                    menu += "<hr><b>{1}</b> {0}".format(biblesSqlite.getVersesMenu(bookNo, chapterNo, text), config.thisTranslation["html_verse"])
                # Verse specific buttons
                if check == 3:
                    verseNo = bcList[2]
                    if config.openBibleInMainViewOnly or config.enableHttpServer:
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_open"])
                    else:
                        if source == "study":
                            anotherView = "<button class='feature' onclick='document.title=\"MAIN:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openMain"])
                        else:
                            anotherView = "<button class='feature' onclick='document.title=\"STUDY:::{0}:::{1}\"'>{2}</button>".format(text, mainVerseReference, config.thisTranslation["html_openStudy"])
                        openOption = "<button class='feature' onclick='document.title=\"_stayOnSameTab:::\"; document.title=\"BIBLE:::{0}:::{1}\"'>{3}</button> {2}".format(text, mainVerseReference, anotherView, config.thisTranslation["html_openHere"])
                    verseNoteButton = " <button class='feature' onclick='document.title=\"_openversenote:::{0}.{1}.{2}\"'>{3}</button>".format(bookNo, chapterNo, verseNo, config.thisTranslation["menu6_notes"])
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
                        menu += "<button class='feature' onclick='document.title=\"{0}:::{1}\"'>{2}</button> ".format(keyword, mainVerseReference, description)
                    #versions = biblesSqlite.getBibleList()
                    # Compare menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='compare{0}'></div> ".format(version)
                            menu += "<script>versionList.push('{0}');</script>".format(version)
                    menu += "<br><button type='button' onclick='checkCompare();' class='feature'>{0}</button>".format(config.thisTranslation["html_showCompare"])
                    # Parallel menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='parallel{0}'></div> ".format(version)
                    menu += "<br><button type='button' onclick='checkParallel();' class='feature'>{0}</button>".format(config.thisTranslation["html_showParallel"])
                    # Diff menu
                    menu += "<hr><b><span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span> {1}</b><br>".format(text, config.thisTranslation["html_and"])
                    for version in versions:
                        if not version == text:
                            menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='diff{0}'></div> ".format(version)
                    menu += "<br><button type='button' onclick='checkDiff();' class='feature'>{0}</button>".format(config.thisTranslation["html_showDifference"])
        else:
            # menu - Search a bible
            if source == "study":
                defaultSearchText = config.studyText
            else:
                defaultSearchText = config.mainText
            menu += "<hr><b>{1}</b> <span style='color: brown;' onmouseover='textName(\"{0}\")'>{0}</span>".format(defaultSearchText, config.thisTranslation["html_searchBible2"])
            menu += "<br><br><input type='text' id='bibleSearch' style='width:95%' autofocus><br><br>"
            searchOptions = ("SEARCH", "SEARCHREFERENCE", "SEARCHOT", "SEARCHNT", "SEARCHALL", "ANDSEARCH", "ORSEARCH", "ADVANCEDSEARCH", "REGEXSEARCH")
            for searchMode in searchOptions:
                menu += "<button  id='{0}' type='button' onclick='checkSearch(\"{0}\", \"{1}\");' class='feature'>{0}</button> ".format(searchMode, defaultSearchText)
            # menu - Search multiple bibles
            menu += "<hr><b>{0}</b> ".format(config.thisTranslation["html_searchBibles2"])
            for version in versions:
                if version == defaultSearchText or version == config.favouriteBible:
                    menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='search{0}' checked></div> ".format(version)
                else:
                    menu += "<div style='display: inline-block' onmouseover='textName(\"{0}\")'>{0} <input type='checkbox' id='search{0}'></div> ".format(version)
                menu += "<script>versionList.push('{0}');</script>".format(version)
            menu += "<br><br><input type='text' id='multiBibleSearch' style='width:95%'><br><br>"
            for searchMode in searchOptions:
                menu += "<button id='multi{0}' type='button' onclick='checkMultiSearch(\"{0}\");' class='feature'>{0}</button> ".format(searchMode)
            # Perform search when "ENTER" key is pressed
            menu += biblesSqlite.inputEntered("bibleSearch", "SEARCH")
            menu += biblesSqlite.inputEntered("multiBibleSearch", "multiSEARCH")
        return menu
