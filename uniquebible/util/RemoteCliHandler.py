# https://github.com/jquast/telnetlib3/blob/master/telnetlib3/server_shell.py
import asyncio, re, sys
from uniquebible.util.TextUtil import TextUtil
from uniquebible.util.LanguageUtil import LanguageUtil
from uniquebible.util.ConfigUtil import ConfigUtil
from uniquebible.util.NetworkUtil import NetworkUtil
from uniquebible.util.RemoteCliMainWindow import RemoteCliMainWindow

CR, LF, NUL = '\r\n\x00'
CRLF = '\r\n'

class RemoteCliHandler:

    @staticmethod
    def setup():
        if (len(sys.argv) > 1) and sys.argv[1] == "cli":
            try:
                import telnetlib3
            except:
                print("Please run 'pip install telnetlib3' to use remote CLI")
                ConfigUtil.save()
                exit(0)

            try:
                import telnetlib3
                import asyncio
                from uniquebible.util.RemoteCliHandler import RemoteCliHandler

                port = 8888
                if (len(sys.argv) > 2):
                    port = int(sys.argv[2])
                print("Running in remote CLI Mode on port {0}".format(port))
                print("Access by 'telnet {0} {1}'".format(NetworkUtil.get_ip(), port))
                print("Press Ctrl-C to stop the server")
                loop = asyncio.get_event_loop()
                coro = telnetlib3.create_server(port=port, shell=RemoteCliHandler.shell)
                server = loop.run_until_complete(coro)
                loop.run_until_complete(server.wait_closed())
                exit(0)
            except KeyboardInterrupt:
                exit(0)
            except Exception as e:
                print(str(e))
                exit(-1)

    @asyncio.coroutine
    def shell(reader, writer):
        from uniquebible.util.TextCommandParser import TextCommandParser

        textCommandParser = TextCommandParser(RemoteCliMainWindow())

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
            if command.lower() in ('.quit', '.exit', '.bye'):
                break
            elif command.lower() in ('.help', '?'):
                RemoteCliHandler.help(writer)
            elif len(command) > 0:
                view, content, dict = textCommandParser.parser(command, "cli")
                if not content:
                    content = "Command processed!"
                content = TextUtil.htmlToPlainText(content)
                content = re.sub(r"\n", CRLF, content)
                content = content.strip()
                writer.write(content)
        writer.close()

    def help(writer):
        from uniquebible.util.TextCommandParser import TextCommandParser
        textCommandParser = TextCommandParser(RemoteCliMainWindow())

        writer.write("Type '.quit' to exit" + CRLF)
        writer.write("All other commands will be processed by UBA" + CRLF)
        writer.write(CRLF + "UBA commands:" + CRLF)
        content = "\n".join([re.sub("            #", "#", value[-1]) for value in textCommandParser.interpreters.values()])
        content = re.sub(r"\n", CRLF, content)
        writer.write(content)

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


if __name__ == "__main__":
    from uniquebible import config

    config.thisTranslation = LanguageUtil.loadTranslation("en_US")
    config.parserStandarisation = 'NO'
    config.standardAbbreviation = 'ENG'
    config.marvelData = "/Users/otseng/dev/UniqueBible/marvelData/"

    command = "1[A[B[C[D2"
    command = re.sub("\[[ABCD]", "", command)
    print(command)