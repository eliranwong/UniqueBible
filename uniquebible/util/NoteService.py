import re
import time
from uniquebible import config
from uniquebible.util.BibleBooks import BibleBooks
from uniquebible.util.Languages import Languages
from uniquebible.db.NoteSqlite import NoteSqlite
from uniquebible.util.DateUtil import DateUtil
from uniquebible.util.GitHubGist import GitHubGist


class NoteService:

    ns = None

    @staticmethod
    def getNoteSqlite():
        if not NoteService.ns:
            NoteService.ns = NoteSqlite()
        return NoteService.ns

    @staticmethod
    def close():
        NoteService.getNoteSqlite().connection.close()

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def saveBookNote(b, note):
        now = DateUtil.epoch()
        if config.enableGist:
            gh = GitHubGist()
            gh.openGistBookNote(b)
            gh.updateContent(note, now)
        ns = NoteService.getNoteSqlite()
        ns.saveBookNote(b, note, now)

    @staticmethod
    def saveChapterNote(b, c, note):
        now = DateUtil.epoch()
        if config.enableGist:
            gh = GitHubGist()
            gh.openGistChapterNote(b, c)
            gh.updateContent(note, now)
        ns = NoteService.getNoteSqlite()
        ns.saveChapterNote(b, c, note, now)

    @staticmethod
    def saveVerseNote(b, c, v, note):
        now = DateUtil.epoch()
        if config.enableGist:
            gh = GitHubGist()
            gh.openGistVerseNote(b, c, v)
            gh.updateContent(note, now)
        ns = NoteService.getNoteSqlite()
        ns.saveVerseNote(b, c, v, note, now)

    @staticmethod
    def getSearchedChapterList(command):
        ns = NoteService.getNoteSqlite()
        chapters = ns.getSearchedChapterList(command)
        return chapters

    @staticmethod
    def getSearchedVerseList(command):
        ns = NoteService.getNoteSqlite()
        verses = ns.getSearchedVerseList(command)
        return verses

    @staticmethod
    def getChapterVerseList(b, c):
        ns = NoteService.getNoteSqlite()
        noteVerseList = ns.getChapterVerseList(b, c)
        return noteVerseList

    @staticmethod
    def isChapterNote(b, c):
        ns = NoteService.getNoteSqlite()
        result = ns.isChapterNote(b, c)
        return result

    @staticmethod
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

