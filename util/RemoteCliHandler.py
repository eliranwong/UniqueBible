# https://github.com/jquast/telnetlib3/blob/master/telnetlib3/server_shell.py
import asyncio
import re

CR, LF, NUL = '\r\n\x00'
CRLF = '\r\n'

class RemoteCliHandler:

    @asyncio.coroutine
    def shell(reader, writer):
        from TextCommandParser import TextCommandParser

        textCommandParser = TextCommandParser(MockWindow())

        writer.write("Connected to UniqueBible.app" + CRLF)

        linereader = RemoteCliHandler.readline(reader, writer)
        linereader.send(None)

        command = None
        while True:
            if command:
                writer.write(CRLF)
            writer.write('> ')
            command = None
            while command is None:
                inp = yield from reader.read(1)
                if not inp:
                    return
                command = linereader.send(inp)
            writer.write(CRLF)
            command = re.sub("\[[ABCD]", "", command)
            command = command.strip()
            if command.lower() in ('quit', 'exit', 'bye'):
                break
            elif command.lower() in ('help', '?'):
                RemoteCliHandler.help(writer)
            elif len(command) > 0:
                view, content, dict = textCommandParser.parser(command, "cli")
                content = re.sub("<br/?>", CRLF, content)
                content = re.sub('<[^<]+?>', '', content)
                content = content.strip()
                writer.write(content)
        writer.close()

    def help(writer):
        writer.write("Type 'quit' to exit" + CRLF)
        writer.write("All other commands will be processed by UBA" + CRLF)
        writer.write("Examples:" + CRLF)
        writer.write("BIBLE:::KJV:::John 3:16" + CRLF)
        writer.write("BIBLE:::KJV:::Jn 3:16; Rm 5:8; Deu 6:4" + CRLF)
        writer.write("PARALLEL:::NIV_KJV:::John 3:16" + CRLF)
        writer.write("SHOWSEARCH:::KJV:::omnipotent" + CRLF)
        writer.write("ADVANCEDSEARCH:::KJV_WEB:::Book = 1 AND Scripture LIKE '%love%'" + CRLF)
        writer.write("WORDS:::Gen 1:1")

    @asyncio.coroutine
    def readline(reader, writer):
        """
        A very crude readline coroutine interface.
        This function is a :func:`~asyncio.coroutine`.
        """
        command, inp, last_inp = '', '', ''
        inp = yield None
        while True:
            if inp in (LF, NUL) and last_inp == CR:
                last_inp = inp
                inp = yield None

            elif inp in (CR, LF):
                # first CR or LF yields command
                last_inp = inp
                inp = yield command
                command = ''

            elif inp in ('\b', '\x7f'):
                # backspace over input
                if command:
                    command = command[:-1]
                    writer.echo('\b \b')
                last_inp = inp
                inp = yield None

            else:
                # buffer and echo input
                command += inp
                writer.echo(inp)
                last_inp = inp
                inp = yield None

class MockWindow:

    def __init__(self):
        import update
        import config
        from Languages import Languages

        self.bibleInfo = update.bibleInfo
        config.thisTranslation = Languages.translation

    def updateMainRefButton(self):
        pass

    def enableParagraphButtonAction(self, v):
        pass

    def downloadHelper(self, v):
        pass

    def updateStudyRefButton(self):
        pass

    def updateCommentaryRefButton(self):
        pass

if __name__ == "__main__":
    import config
    from Languages import Languages
    
    config.thisTranslation = Languages.translation
    config.parserStandarisation = 'NO'
    config.standardAbbreviation = 'ENG'
    config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"

    command = "1[A[B[C[D2"
    command = re.sub("\[[ABCD]", "", command)
    print(command)