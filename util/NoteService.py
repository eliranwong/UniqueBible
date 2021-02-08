import logging
import time
import config
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
            gh.open_gist_book_note(b)
            file = gh.get_file()
            if file:
                updatedG = gh.get_updated()
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
                gh.update_content(noteL, updatedL)
            note = noteL
        elif validGist and validLocal:
            if updatedL is None:
                if len(noteG) > len(noteL):
                    note = noteG
                else:
                    note = noteL
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
            gh.open_gist_chapter_note(b, c)
            file = gh.get_file()
            if file:
                updatedG = gh.get_updated()
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
                gh.update_content(noteL, updatedL)
            note = noteL
        elif validGist and validLocal:
            if updatedL is None:
                if len(noteG) > len(noteL):
                    note = noteG
                else:
                    note = noteL
            elif updatedG > updatedL:
                note = noteG
            else:
                note = noteL
        else:
            note = noteL
        if noteG and note == noteG:
            ns.saveChapterNote(b, c, noteG, updatedG)
        return note

    def saveBookNote(b, note):
        now = DateUtil.epoch()
        if config.enableGist:
            gh = GitHubGist()
            gh.open_gist_book_note(b)
            gh.update_content(note, now)
        ns = NoteService.getNoteSqlite()
        ns.saveBookNote(b, note, now)

    def saveChapterNote(b, c, note):
        now = DateUtil.epoch()
        if config.enableGist:
            gh = GitHubGist()
            gh.open_gist_chapter_note(b, c)
            gh.update_content(note, now)
        ns = NoteService.getNoteSqlite()
        ns.saveChapterNote(b, c, note, now)

    def getVerseNote(b, c, v):
        validGist = False
        noteL = noteG = None
        if config.enableGist:
            gh = GitHubGist()
            gh.open_gist_verse_note(b, c, v)
            file = gh.get_file()
            if file:
                updatedG = gh.get_updated()
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
                gh.update_content(noteL, updatedL)
            note = noteL
        elif validGist and validLocal:
            if updatedL is None:
                if len(noteG) > len(noteL):
                    note = noteG
                else:
                    note = noteL
            elif updatedG > updatedL:
                note = noteG
            else:
                note = noteL
        else:
            note = noteL
        if noteG is not None and note == noteG:
            ns.saveVerseNote(b, c, v, noteG, updatedG)
        return note

    def saveVerseNote(b, c, v, note):
        now = DateUtil.epoch()
        if config.enableGist:
            gh = GitHubGist()
            gh.open_gist_verse_note(b, c, v)
            gh.update_content(note, now)
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

class SyncNotesWithGist(QObject):
    finished = Signal(int)
    progress = Signal(str)

    def __init__(self):
        super(SyncNotesWithGist, self).__init__()

    def run(self):
        logger = logging.getLogger('uba')
        gh = GitHubGist()
        gNotes = gh.get_all_note_gists()
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
        for note in notes:
            count += 1
            book = note[0]
            chapter = note[1]
            verse = note[2]
            content = note[3]
            updatedL = note[4]
            if chapter == 0:
                description = GitHubGist.b_to_book_name(book)
            elif verse == 0:
                description = GitHubGist.bc_to_chapter_name(book, chapter)
            else:
                description = GitHubGist.bcv_to_verse_name(book, chapter, verse)
            self.progress.emit("Uploading " + description + " ...")
            updateGistFile = False
            updated = DateUtil.epoch()
            gist = None
            if description in gists.keys():
                gist = gists[description]
            if gist is None:
                updateGistFile = True
            else:
                updatedG = GitHubGist.extract_updated(gist)
                if updatedL is None:
                    content = GitHubGist.extract_content(gist)
                    sizeG = len(content)
                    sizeL = len(content)
                    if sizeL > sizeG:
                        if chapter == 0:
                            ns.setBookNoteUpdate(book, chapter, updated)
                        elif verse == 0:
                            ns.setChapterNoteUpdate(book, chapter, updated)
                        else:
                            ns.setVerseNoteUpdate(book, chapter, verse, updated)
                        updateGistFile = True
                elif updatedG == 0 or updatedL > updatedG:
                    updateGistFile = True
                    updated = updatedL
            if updateGistFile:
                logger.debug("Updating gist " + description)
                if chapter == 0:
                    gh.open_gist_book_note(book)
                elif verse == 0:
                    gh.open_gist_chapter_note(book, chapter)
                else:
                    gh.open_gist_verse_note(book, chapter, verse)
                gh.update_content(content, updated)
        gNotes = gh.get_all_note_gists()
        for gist in gNotes:
            count += 1
            self.progress.emit("Downloading " + gist.description + " ...")
            contentG = GitHubGist.extract_content(gist)
            updatedG = GitHubGist.extract_updated(gist)
            if "Book" in gist.description:
                book = GitHubGist.book_name_to_b(gist.description)
                chapter = 0
                verse = 0
                res = [note for note in books if note[0] == book]
            elif "Chapter" in gist.description:
                (book, chapter) = GitHubGist.chapter_name_to_bc(gist.description)
                verse = 0
                res = [note for note in chapters if note[0] == book and note[1] == chapter]
            elif "Verse" in gist.description:
                (book, chapter, verse) = GitHubGist.verse_name_to_bcv(gist.description)
                res = [note for note in verses if note[0] == book and note[1] == chapter and note[2] == verse]
            if len(res) == 0:
                logger.debug("Creating local " + gist.description)
                if chapter == 0:
                    ns.saveBookNote(book, contentG, updatedG)
                elif verse == 0:
                    ns.saveChapterNote(book, chapter, contentG, updatedG)
                else:
                    ns.saveVerseNote(book, chapter, verse, contentG, updatedG)
            else:
                noteL = res[0]
                contentL = noteL[3]
                updatedL = noteL[4]
                update = False
                if updatedL is None:
                    if len(contentG) > len(contentL):
                        update = True
                elif updatedG > updatedL:
                    update = True
                if update:
                    logger.debug("Updating local " + gist.description)
                    if chapter == 0:
                        ns.setBookNoteUpdate(book, contentG, updatedG)
                    elif verse == 0:
                        ns.setChapterNoteUpdate(book, chapter, contentG, updatedG)
                    else:
                        ns.setVerseNoteUpdate(book, chapter, verse, contentG, updatedG)

        self.finished.emit(count)

def test_note():
    b = 40
    c = 1

    note = NoteService.getChapterNote(b, c)
    print(note)

    gh = GitHubGist()
    gh.open_gist_chapter_note(b, c)
    print(gh.get_updated())

def test_get_all_notes():
    ns = NoteService.getNoteSqlite()
    notes = ns.getAllChapters() + ns.getAllVerses()
    return notes

if __name__ == "__main__":
    config.thisTranslation = Languages.translation
    start = time.time()

    test_get_all_notes()

    print("---")
    end = time.time()
    print("Total time: {0}".format(end - start))

