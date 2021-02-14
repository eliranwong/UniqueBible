from itertools import (takewhile, repeat)


class FileUtil:

    # https://stackoverflow.com/a/27518377/1397431
    @staticmethod
    def getLineCount(filename):
        try:
            f = open(filename, 'rb')
            bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
            return sum(buf.count(b'\n') for buf in bufgen)
        except Exception as e:
            # print(str(e))
            return -1
