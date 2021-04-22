import re, html

class TextUtil:

    @staticmethod
    def formulateUBACommandHyperlink(text):
        # Create hyperlink to UBA command
        # work on text formatted like ***[CROSSREFERENCE:::John 3:16@An hyperlink link to open cross-references of John 3:16]
        return re.sub("\*\*\*\[([^'{0}]*?)@([^'{0}]*?)\]".format('"\*\[\]@'), r"<ref onclick={0}document.title='\1'{0}>\2</ref>".format('"'), text)

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

    @staticmethod
    def plainTextToUrl(text):
        # https://wiki.python.org/moin/EscapingHtml
        text = html.escape(text)
        searchReplace = (
            (" ", "%20"),
            ("\n", "%0D%0A"),
        )
        for search, replace in searchReplace:
            text = text.replace(search, replace)
        return text

    # Return digits from a string
    @staticmethod
    def getDigits(text):
        return ''.join(c for c in text if c.isdigit())

    # Remove Hebrew vowels or Greek accents
    @staticmethod
    def removeVowelAccent(text):
        searchReplace = (
            (r"[\֑\֒\֓\֔\֕\֖\֗\֘\֙\֚\֛\֜\֝\֞\֟\֠\֡\֣\֤\֥\֦\֧\֨\֩\֪\֫\֬\֭\֮\ֽ\ׄ\ׅ\‍\‪\‬\̣\ְ\ֱ\ֲ\ֳ\ִ\ֵ\ֶ\ַ\ָ\ֹ\ֺ\ֻ\ׂ\ׁ\ּ\ֿ\(\)\[\]\*\־\׀\׃\׆]", ""),
            ("[שׂשׁ]", "ש"),
            ("[ἀἄᾄἂἆἁἅᾅἃάᾴὰᾶᾷᾳ]", "α"),
            ("[ἈἌἎἉἍἋ]", "Α"),
            ("[ἐἔἑἕἓέὲ]", "ε"),
            ("[ἘἜἙἝἛ]", "Ε"),
            ("[ἠἤᾔἢἦᾖᾐἡἥἣἧᾗᾑήῄὴῆῇῃ]", "η"),
            ("[ἨἬἪἮἩἭἫ]", "Η"),
            ("[ἰἴἶἱἵἳἷίὶῖϊΐῒ]", "ι"),
            ("[ἸἼἹἽ]", "Ι"),
            ("[ὀὄὂὁὅὃόὸ]", "ο"),
            ("[ὈὌὉὍὋ]", "Ο"),
            ("[ῥ]", "ρ"),
            ("[Ῥ]", "Ρ"),
            ("[ὐὔὒὖὑὕὓὗύὺῦϋΰῢ]", "υ"),
            ("[ὙὝὟ]", "Υ"),
            ("[ὠὤὢὦᾠὡὥὧᾧώῴὼῶῷῳ]", "ω"),
            ("[ὨὬὪὮὩὭὯ]", "Ω"),
            (r"[\-\—\,\;\:\\\?\.\·\·\‘\’\‹\›\“\”\«\»\(\)\[\]\{\}\⧼\⧽\〈\〉\*\‿\᾽\⇔\¦]", ""),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        return text


if __name__ == '__main__':

    print(TextUtil.getDigits("abc123def"))
