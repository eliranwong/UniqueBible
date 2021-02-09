import logging
import re
import time
import config
from BibleBooks import BibleBooks
from Languages import Languages
from NoteSqlite import NoteSqlite
from util.DateUtil import DateUtil
from util.GitHubGist import GitHubGist
from PySide2.QtCore import QObject, Signal


class NoteService:

    ns = None

    def getNoteSqlite():
        if not NoteService.ns:
            NoteService.ns = NoteSqlite()
        return NoteService.ns

    def getBookNote(b):
        validGist = False
        noteL = noteG = None
        if config.enableGist:
            gh = GitHubGist()
            gh.openGistBookNote(b)
            file = gh.getFile()
            if file:
                updatedG = gh.getUpdated()
                noteG = file.content
                validGist = True
        ns = NoteService.getNoteSqlite()
        noteL, updatedL = ns.displayBookNote(b)
        validLocal = True
        if noteL == config.thisTranslation["empty"]:
            validLocal = False
        if validGist and not validLocal:
            note = noteG
        elif not validGist and validLocal:
            if config.enableGist:
                gh.updateContent(noteL, updatedL)
            note = noteL
        elif validGist and validLocal:
            if updatedL is None:
                note = NoteService.mergeNotes(noteL, noteG)
            elif updatedG > updatedL:
                note = noteG
            else:
                note = noteL
        else:
            note = noteL
        if noteG and note == noteG:
            ns.saveBookNote(b, noteG, updatedG)
        return note

    def getChapterNote(b, c):
        validGist = False
        noteL = noteG = None
        if config.enableGist:
            gh = GitHubGist()
            gh.openGistChapterNote(b, c)
            file = gh.getFile()
            if file:
                updatedG = gh.getUpdated()
                noteG = file.content
                validGist = True
        ns = NoteService.getNoteSqlite()
        noteL, updatedL = ns.displayChapterNote(b, c)
        validLocal = True
        if noteL == config.thisTranslation["empty"]:
            validLocal = False
        if validGist and not validLocal:
            note = noteG
        elif not validGist and validLocal:
            if config.enableGist:
                gh.updateContent(noteL, updatedL)
            note = noteL
        elif validGist and validLocal:
            if updatedL is None:
                note = NoteService.mergeNotes(noteL, noteG)
            elif updatedG > updatedL:
                note = noteG
            else:
                note = noteL
        else:
            note = noteL
        if noteG and note == noteG:
            ns.saveChapterNote(b, c, noteG, updatedG)
        return note

    def getVerseNote(b, c, v):
        validGist = False
        noteL = noteG = None
        if config.enableGist:
            gh = GitHubGist()
            gh.openGistVerseNote(b, c, v)
            file = gh.getFile()
            if file:
                updatedG = gh.getUpdated()
                noteG = file.content
                validGist = True
        ns = NoteService.getNoteSqlite()
        noteL, updatedL = ns.displayVerseNote(b, c, v)
        validLocal = True
        if noteL == config.thisTranslation["empty"]:
            validLocal = False
        if validGist and not validLocal:
            note = noteG
        elif not validGist and validLocal:
            if config.enableGist:
                gh.updateContent(noteL, updatedL)
            note = noteL
        elif validGist and validLocal:
            if updatedL is None:
                note = NoteService.mergeNotes(noteL, noteG)
            elif updatedG > updatedL:
                note = noteG
            else:
                note = noteL
        else:
            note = noteL
        if noteG is not None and note == noteG:
            ns.saveVerseNote(b, c, v, noteG, updatedG)
        return note

    def saveBookNote(b, note):
        now = DateUtil.epoch()
        if config.enableGist:
            gh = GitHubGist()
            gh.openGistBookNote(b)
            gh.updateContent(note, now)
        ns = NoteService.getNoteSqlite()
        ns.saveBookNote(b, note, now)

    def saveChapterNote(b, c, note):
        now = DateUtil.epoch()
        if config.enableGist:
            gh = GitHubGist()
            gh.openGistChapterNote(b, c)
            gh.updateContent(note, now)
        ns = NoteService.getNoteSqlite()
        ns.saveChapterNote(b, c, note, now)

    def saveVerseNote(b, c, v, note):
        now = DateUtil.epoch()
        if config.enableGist:
            gh = GitHubGist()
            gh.openGistVerseNote(b, c, v)
            gh.updateContent(note, now)
        ns = NoteService.getNoteSqlite()
        ns.saveVerseNote(b, c, v, note, now)

    def getSearchedChapterList(command):
        ns = NoteService.getNoteSqlite()
        chapters = ns.getSearchedChapterList(command)
        return chapters

    def getSearchedVerseList(command):
        ns = NoteService.getNoteSqlite()
        verses = ns.getSearchedVerseList(command)
        return verses

    def getChapterVerseList(b, c):
        ns = NoteService.getNoteSqlite()
        noteVerseList = ns.getChapterVerseList(b, c)
        return noteVerseList

    def isChapterNote(b, c):
        ns = NoteService.getNoteSqlite()
        result = ns.isChapterNote(b, c)
        return result

    def mergeNotes(note1, note2, separater=""):
        note1 = note1.replace('\n', '').replace('\r', '')
        note2 = note2.replace('\n', '').replace('\r', '')

        if "</body>" in note2:
            note2Body = re.search("<body.*?>(.*)</body>", note2).group(1)
        else:
            note2Body = note2

        note2Body = separater + note2Body

        if "</body>" in note2:
            merged = note1.replace("</body>", note2Body + "</body>")
        else:
            merged = note1 + note2Body

        return merged


class SyncNotesWithGist(QObject):
    finished = Signal(int)
    progress = Signal(str)

    def __init__(self):
        super(SyncNotesWithGist, self).__init__()
        self.logger = logging.getLogger('uba')

    def run(self):
        gh = GitHubGist()
        gNotes = gh.getAllNoteGists()
        gists = {}
        if gNotes:
            for gist in gNotes:
                gists[gist.description] = gist
        ns = NoteService.getNoteSqlite()
        count = 0
        books = ns.getAllBooks()
        chapters = ns.getAllChapters()
        verses = ns.getAllVerses()
        notes = books + chapters + verses
        self.logger.debug("Uploading {0} notes".format(len(notes)))
        # Upload from local to Gist
        for note in notes:
            count += 1
            book = note[0]
            chapter = note[1]
            verse = note[2]
            contentL = note[3]
            updatedL = note[4]
            if chapter == 0:
                description = GitHubGist.bToBookName(book)
            elif verse == 0:
                description = GitHubGist.bcToChapterName(book, chapter)
            else:
                description = GitHubGist.bcvToVerseName(book, chapter, verse)
            msg = "Processing upload " + description + " ..."
            self.progress.emit(msg)
            self.logger.debug(msg)
            updateGistFile = False
            updated = DateUtil.epoch()
            gist = None
            if description in gists.keys():
                gist = gists[description]
            if gist is None:
                updateGistFile = True
            else:
                updatedG = GitHubGist.extractUpdated(gist)
                # if the local updated time is blank,  merge the local database file with the gist file
                if updatedL is None:
                    contentG = GitHubGist.extractContent(gist)
                    contentL = NoteService.mergeNotes(contentL, contentG, "---<br/>")
                    if chapter == 0:
                        ns.saveBookNote(book, contentL, updated)
                    elif verse == 0:
                        ns.saveChapterNote(book, chapter, contentL, updated)
                    else:
                        ns.saveVerseNote(book, chapter, verse, contentL, updated)
                    updateGistFile = True
                # if the updated time of local database note > gist time, then update gist
                elif updatedL > updatedG:
                    updateGistFile = True
                    updated = updatedL
                # if the local time <= gist time, then don't update gist
                elif updatedL <= updatedG:
                    updateGistFile = False
            if updateGistFile:
                msg = "Updating gist " + description
                self.logger.debug(msg)
                if chapter == 0:
                    gh.openGistBookNote(book)
                elif verse == 0:
                    gh.openGistChapterNote(book, chapter)
                else:
                    gh.openGistVerseNote(book, chapter, verse)
                gh.updateContent(contentL, updated)
        # Download from Gist
        gNotes = gh.getAllNoteGists()
        for gist in gNotes:
            count += 1
            msg = "Processing download " + gist.description + " ..."
            self.progress.emit(msg)
            self.logger.debug(msg)
            contentG = GitHubGist.extractContent(gist)
            updatedG = GitHubGist.extractUpdated(gist)
            if "Book" in gist.description:
                book = GitHubGist.bookNameToB(gist.description)
                chapter = 0
                verse = 0
                res = [note for note in books if note[0] == book]
            elif "Chapter" in gist.description:
                (book, chapter) = GitHubGist.chapterNameToBc(gist.description)
                verse = 0
                res = [note for note in chapters if note[0] == book and note[1] == chapter]
            elif "Verse" in gist.description:
                (book, chapter, verse) = GitHubGist.verseNameToBcv(gist.description)
                res = [note for note in verses if note[0] == book and note[1] == chapter and note[2] == verse]
            # if local note does not exist, then create local note
            if len(res) == 0:
                msg = "Creating local " + gist.description
                self.logger.debug(msg)
                if chapter == 0:
                    ns.saveBookNote(book, contentG, updatedG)
                elif verse == 0:
                    ns.saveChapterNote(book, chapter, contentG, updatedG)
                else:
                    ns.saveVerseNote(book, chapter, verse, contentG, updatedG)
            # if local note already exist
            else:
                noteL = res[0]
                updatedL = noteL[4]
                # if gist update time > local update time, then update local
                if updatedG > updatedL:
                    self.logger.debug("Updating local " + gist.description)
                    if chapter == 0:
                        ns.setBookNoteUpdate(book, contentG, updatedG)
                    elif verse == 0:
                        ns.setChapterNoteUpdate(book, chapter, contentG, updatedG)
                    else:
                        ns.setVerseNoteUpdate(book, chapter, verse, contentG, updatedG)

        self.finished.emit(count)
        self.logger.debug("Sync done")


# Only used for testing

def test_note():
    b = 40
    c = 1

    note = NoteService.getChapterNote(b, c)
    print(note)

    gh = GitHubGist()
    gh.openGistChapterNote(b, c)
    print(gh.getUpdated())

def test_getAllNotes():
    ns = NoteService.getNoteSqlite()
    notes = ns.getAllChapters() + ns.getAllVerses()
    return notes

def test_mergeNotes():
    note1 = """
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
<html><head><meta name="qrichtext" content="1" /><style type="text/css">
p, li { white-space: pre-wrap; }
</style></head><body style="font-family:''; font-size:19pt; font-weight:400; font-style:normal;">
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14pt;">Note1 - line1</span></p>
<p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;">Note1 - line2</p>
<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14pt;">Note1 - Line 3</span></p></body></html>
"""
    note2 = """
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
    <html><head><meta name="qrichtext" content="1" /><style type="text/css">
    p, li { white-space: pre-wrap; }
    </style></head><body style="font-family:''; font-size:19pt; font-weight:400; font-style:normal;">
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14pt;">Note2 - line1</span></p>
    <p style="-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:14pt;">Note2 - line2</p>
    <p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;"><span style=" font-size:14pt;">Note2 - Line 3</span></p></body></html>
    """

    merged = NoteService.mergeNotes(note1, note2, "-----<br/>")

    print(merged)

def test_createFakeNotes():
    maxNotes = 10
    count = 0
    for b in range(40, 67):
        count += 1
        note = "Test book note {0}".format(b)
        NoteService.saveBookNote(b, note)
        print(note)
        for c in range(1, BibleBooks.chapters[b]):
            note = "Test chapter note {0}:{1}".format(b, c)
            NoteService.saveChapterNote(b, c, note)
            print(note)
            for v in range(1, 10):
                note = "Test verse note {0}:{1}:{2}".format(b, c, v)
                NoteService.saveVerseNote(b, c, v, note)
                print(note)
                if count > maxNotes:
                    return



if __name__ == "__main__":
    config.thisTranslation = Languages.translation
    start = time.time()

    # test_getAllNotes()
    # test_mergeNotes()
    test_createFakeNotes()

    print("---")
    end = time.time()
    print("Total time: {0}".format(end - start))

