import re

class TextUtil:

    @staticmethod
    def fixTextHighlighting(text):
        # fix searching LXX / SBLGNT words
        text = re.sub(r"<z>([LS][0-9]+?)</z>'\)"'"'">(.*?)</grk>", r"\1'\)"'"'r"><z>\2</z></grk>", text)
        # remove misplacement of tags <z> & </z>
        p = re.compile("(<[^<>]*?)<z>(.*?)</z>", flags=re.M)
        s = p.search(text)
        while s:
            text = re.sub(p, r"\1\2", text)
            s = p.search(text)
        return text

    # Return digits from a string
    @staticmethod
    def getDigits(text):
        return ''.join(c for c in text if c.isdigit())


if __name__ == '__main__':

    print(TextUtil.getDigits("abc123def"))
