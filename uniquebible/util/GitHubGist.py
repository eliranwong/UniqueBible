import logging
import re
import time
from uniquebible import config

try:
    from github import Github, InputFileContent
except:
    pass

# https://docs.github.com/en/rest/reference/gists
# https://pygithub.readthedocs.io/en/latest/introduction.html
# https://pygithub.readthedocs.io/en/latest/reference.html

# gist object
#   comments (int)
#   description (str)
#   files (dict)
#   id (str)
#   last_modified (str)
#   public (bool)
#   updated_at (datetime)
from uniquebible.util.DateUtil import DateUtil


class GitHubGist:

    def __init__(self, gistToken=""):
        self.logger = logging.getLogger('uba')
        self.enablePublicGist = True
        if not self.logger.hasHandlers():
            logHandler = logging.StreamHandler()
            logHandler.setLevel(logging.DEBUG)
            self.logger.addHandler(logHandler)
            self.logger.setLevel(logging.INFO)
        if gistToken == "":
            self.gistToken = config.gistToken
        else:
            self.gistToken = gistToken
        self.status = "Not configured"
        self.connected = False
        self.user = None
        self.gist = None
        self.description = None
        try:
            if len(self.gistToken) < 40:
                self.status = "Gist token is has valid"
                raise Exception(self.status)
            self.gh = Github(self.gistToken)
            self.user = self.gh.get_user()
            self.status = "Gist user: " + self.user.name
            self.logger.debug(self.status)
            self.connected = True
        except Exception as error:
            self.status = "Could not connect"
            self.logger.error(str(error))

    def openGistBookNote(self, book):
        self.description = GitHubGist.bToBookName(book)
        self.openGistByDescription(self.description)

    def openGistChapterNote(self, book, chapter):
        self.description = GitHubGist.bcToChapterName(book, chapter)
        self.openGistByDescription(self.description)

    def openGistVerseNote(self, book, chapter, verse):
        self.description = GitHubGist.bcvToVerseName(book, chapter, verse)
        self.openGistByDescription(self.description)

    def openGistByDescription(self, description):
        if self.connected and self.user is not None:
            self.gist = None
            gists = self.user.get_gists()
            for g in gists:
                if description == g.description:
                    self.gist = g
                    self.description = description
                    self.logger.debug("Existing Gist:{0}:{1}".format(description, self.gist.id))
                    break

    def openGistById(self, id):
        self.gist = None
        try:
            if self.gh:
                self.gist = self.gh.get_gist(id)
        except:
            return None
        if not self.description == self.gist.description:
            return None

    def getAllNoteGists(self):
        if self.connected and self.user is not None:
            self.gist = None
            self.description = None
            gists = self.user.get_gists()
            notes = []
            for g in gists:
                if g.description.startswith("UBA-Note-"):
                    notes.append(g)
            return notes

    def id(self):
        if self.gist:
            return self.gist.id
        else:
            return ""

    def updateContent(self, content, updated):
        if self.connected:
            if self.gist is not None:
                self.gist = self.user.create_gist(self.enablePublicGist, {self.description: InputFileContent(content),
                                                          "updated": InputFileContent(str(updated))},
                                                           self.description)
            else:
                self.gist.edit(files={self.description: InputFileContent(content),
                                      "updated": InputFileContent(str(updated))})

    def getFile(self):
        if self.connected and self.gist is not None:
            files = self.gist.files
            file = files[self.description]
            return file
        else:
            return None

    def getContent(self):
        file = self.getFile()
        if file is not None:
            return file.content
        else:
            return ""

    def getUpdated(self):
        if self.connected:
            if self.gist:
                files = self.gist.files
                file = files["updated"]
                if file and file.content is not None:
                    return int(file.content)
            return 0
        else:
            return 0

    def deleteAllNotes(self):
        if self.connected and self.user:
            self.gist = None
            self.description = None
            gists = self.user.get_gists()
            count = 0
            for g in gists:
                if g.description.startswith("UBA-Note-"):
                    count += 1
                    g.delete()
            return count

    def bToBookName(b):
        return "UBA-Note-Book-{0}".format(b)

    def bcToChapterName(b, c):
        return "UBA-Note-Chapter-{0}-{1}".format(b, c)

    def bcvToVerseName(b, c, v):
        return "UBA-Note-Verse-{0}-{1}-{2}".format(b, c, v)

    def bookNameToB(name):
        res = re.search(r'UBA-Note-Book-(\d*)', name).groups()
        return res[0]

    def chapterNameToBc(name):
        res = re.search(r'UBA-Note-Chapter-(\d*)-(\d*)', name).groups()
        return res

    def verseNameToBcv(name):
        res = re.search(r'UBA-Note-Verse-(\d*)-(\d*)-(\d*)', name).groups()
        return res

    def extractContent(gist):
        return gist.files[gist.description].content

    def extractUpdated(gist):
        files = gist.files
        file = files["updated"]
        if file and file.content is not None:
            return int(file.content)
        else:
            return 0


#
# Only used for testing
#

def test_write():
    gh = GitHubGist()
    if not gh.connected:
        print(gh.status)
    else:
        book = 40
        chapter = 1
        gh.openGistChapterNote(book, chapter)
        updated = DateUtil.epoch()
        gh.updateContent("Matthew chapter change from command line", updated)
        updated = gh.getUpdated()
        print(updated)
        file = gh.getFile()
        if file:
            print(file.content)
            print(gh.id())
        else:
            print(gh.description + " gist does not exist")
            print(gh.id())

        print("---")

        book = 40
        chapter = 1
        verse = 2
        gh.openGistVerseNote(book, chapter, verse)
        updated = DateUtil.epoch()
        gh.updateContent("Matthew verse 2 from command line", updated)
        file = gh.getFile()
        updated = gh.getUpdated()
        print(updated)
        if file:
            print(gh.id())
            print(file.content)
        else:
            print(gh.description + " gist does not exist")

def test_read():
    gh = GitHubGist()
    if not gh.connected:
        print(gh.status)
    else:
        book = 40
        chapter = 1
        gh.openGistChapterNote(book, chapter)
        updated = gh.getUpdated()
        print(updated)
        file = gh.getFile()
        if file:
            print(file.content)
            print(gh.id())
        else:
            print(gh.description + " gist does not exist")
            print(gh.id())

        print("---")

        book = 40
        chapter = 1
        verse = 2
        gh.openGistVerseNote(book, chapter, verse)
        file = gh.getFile()
        updated = gh.getUpdated()
        print(updated)
        if file:
            print(gh.id())
            print(file.content)
        else:
            print(gh.description + " gist does not exist")

def test_names():
    chapter = "UBA-Note-Chapter-1-2"
    res = GitHubGist.chapterNameToBc(chapter)
    print(res)
    verse = "UBA-Note-Verse-10-4-5"
    res = GitHubGist.verse_name_to_bc(verse)
    print(res)

def test_getNotes():
    gh = GitHubGist()
    notes = gh.getAllNoteGists()
    for gist in notes:
        print(gist.description)
        print(int(GitHubGist.extractUpdated(gist)))
        if "Chapter" in gist.description:
            (book, chapter) = GitHubGist.chapterNameToBc(gist.description)
            # print("Book {0} Chapter {1}".format(book, chapter))
        elif "Verse" in gist.description:
            (book, chapter, verse) = GitHubGist.verseNameToBcv(gist.description)
            # print("Book {0} Chapter {1} Verse {2}".format(book, chapter, verse))

def test_getCount():
    gh = GitHubGist()
    notes = gh.getAllNoteGists()
    print("Total Gist notes")
    print(len(notes))

def test_updated():
    gh = GitHubGist()
    book = 40
    chapter = 1
    gh.openGistChapterNote(book, chapter)
    updated = gh.getUpdated()
    print(updated)
    content = gh.getContent()
    print(content)

# def test_delete():
#     gh = GitHubGist()
#     print(gh.deleteAllNotes())


if __name__ == "__main__":
    start = time.time()

    # test_write()
    # test_getNotes()
    test_getCount()

    print("---")

    end = time.time()
    print("Epoch: {0}".format(DateUtil.epoch()))
    print("Total time: {0}".format(end - start))
