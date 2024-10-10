import logging
from uniquebible import config
from uniquebible.util.NoteService import NoteService
from uniquebible.util.DateUtil import DateUtil
from uniquebible.util.GitHubGist import GitHubGist
if config.qtLibrary == "pyside6":
    from PySide6.QtCore import QObject, Signal
else:
    from qtpy.QtCore import QObject, Signal


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
