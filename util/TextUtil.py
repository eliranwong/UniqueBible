import re, html, base64, os, config

try:
    import html_text
    isHtmlTextInstalled = True
except:
    isHtmlTextInstalled = False

try:
    from bs4 import BeautifulSoup
    import html5lib
    isBeautifulsoup4Installed = True
except:
    isBeautifulsoup4Installed = False

class TextUtil:

    @staticmethod
    def formatConfigLabel(text):
        text = re.sub("([a-z])([A-Z])", r"\1 \2", text)
        words = text.split(" ")
        words[0] = words[0].capitalize()
        return " ".join(words)

    @staticmethod
    def getQueryPrefix():
        return "PRAGMA case_sensitive_like = {0}; ".format("true" if config.enableCaseSensitiveSearch else "false")

    @staticmethod
    def regexp(expr, item):
        reg = re.compile(expr, flags=0 if config.enableCaseSensitiveSearch else re.IGNORECASE)
        #return reg.match(item) is not None
        return reg.search(item) is not None

    @staticmethod
    def highlightSearchString(text, searchString):
        if searchString == "z":
            return text
        if config.enableCaseSensitiveSearch:
            return re.sub("({0})".format(searchString), r"<z>\1</z>", text, flags=0)
        else:
            return re.sub("({0})".format(searchString), r"<z>\1</z>", text, flags=re.IGNORECASE)

    @staticmethod
    def htmlToPlainText(content):
        if isHtmlTextInstalled:
            content = html_text.extract_text(content)
        elif isBeautifulsoup4Installed:
            content = re.sub("(</th>|</td>)", r"\1&emsp;", content)
            content = re.sub("(<br>|<br/>|</tr>)", r"\1\n", content)
            content = re.sub("(</h[0-9]>|</p>|</div>|<hr>)", r"\1\n\n", content)
            content = BeautifulSoup(content, "html5lib").get_text()
        else:
            content = re.sub("<br/?>|<br>", "\n", content)
            content = re.sub('<[^<]+?>', '', content)
        return content

    @staticmethod
    def imageToText(filepath):
        fileBasename = os.path.basename(filepath)
        *_, fileExtension = os.path.splitext(fileBasename)
        if fileExtension.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
            # read a binary file
            with open(filepath, "rb") as fileObject:
                binaryData = fileObject.read()
                encodedData = base64.b64encode(binaryData)
                binaryString = encodedData.decode("ascii")
                htmlTag = '<img src="data:image/{2};base64,{0}" alt="{1}">'.format(binaryString, fileBasename, fileExtension[1:])
            return htmlTag
        else:
            return "[File type not supported!]"

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
            (r"[\֑\֒\֓\֔\֕\֖\֗\֘\֙\֚\֛\֜\֝\֞\֟\֠\֡\֣\֤\֥\֦\֧\֨\֩\֪\֫\֬\֭\֮\ֽ\ׄ\ׅ\‍\‪\‬\̣\ְ\ֱ\ֲ\ֳ\ִ\ֵ\ֶ\ַ\ָ\ֹ\ֺ\ֻ\ׂ\ׁ\ּ\ֿ\־\׀\׆]", ""),
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
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        return text

    # Remove special characters
    @staticmethod
    def removeSpecialCharacters(text):
        searchReplace = (
            (r"[\-\—\,\;\:\\\?\.\·\·\‘\’\‹\›\“\”\«\»\(\)\[\]\{\}\⧼\⧽\〈\〉\*\‿\᾽\⇔\¦]", ""),
        )
        for search, replace in searchReplace:
            text = re.sub(search, replace, text)
        return text


if __name__ == '__main__':

    print(TextUtil.getDigits("abc123def"))
