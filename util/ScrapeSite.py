from urllib import request
import re

class ScrapeSite:

    FOLDER = "dss"
    DSS = "http://dssenglishbible.com/"

    @staticmethod
    def scrapeDSSSection(sectionUrl, sectionName):
        try:
            response = request.urlopen(sectionUrl)
            pagedata = response.read().decode("iso-8859-1")
            pagedata = pagedata.replace("\r", "").replace("\n", " ")

            pages = re.findall(r'<a href = "(.*?)">', pagedata)
            for page in pages:
                url = ScrapeSite.DSS + page
                ScrapeSite.scrapeDSSPage(url, sectionName)

        except Exception as ex:
            print(ex)

    @staticmethod
    def scrapeDSSPage(url, sectionName):
        try:
            response = request.urlopen(url)
            pagedata = response.read().decode("iso-8859-1")
            pagedata = pagedata.replace("\r", "").replace("\n", " ")

            re_title = re.compile('<title>Biblical Dead Sea Scrolls - (.*)</title>')
            titlesearch = re_title.search(pagedata)
            if titlesearch:
                title = titlesearch.group(1)
            else:
                title = "1Q1 Genesis"

            print(title)

            filename = "{0}/{1} - {2}.html".format(ScrapeSite.FOLDER, sectionName, title)
            outfile = open(filename, "w")

            outfile.write("<html>\n")
            outfile.write("<head>\n")
            outfile.write("<style>\n")
            outfile.write(".trivial { color: lightgreen }\n")
            outfile.write(".variation { color: salmon }\n")
            outfile.write(".unreadable { color: lightblue }\n")
            outfile.write("</style>\n")
            outfile.write("</head>\n")
            outfile.write("<body>\n")

            re_data = re.compile(r'<div class=WordSection1>(.*?)</div>')
            search = re_data.search(pagedata)
            data = search.group(1)

            data = data.replace("<p class=MsoNormal>", "<p>")

            data = re.sub("style='font-size:18.0pt;font-family:\"Arial\",\"sans-serif\";color:green'", 'class="trivial"', data)
            data = re.sub("style='color:green'", 'class="trivial"', data)

            data = re.sub("style='font-size:18.0pt; ?font-family:\"Arial\",\"sans-serif\"; ?color:red'", 'class="variation"', data)

            data = re.sub("style='font-size:18.0pt; ?font-family:\"Arial\",\"sans-serif\"; ?color:#1F497D'", 'class="unreadable"', data)
            data = re.sub("style='color: ?#1F497D'", 'class="unreadable"', data)

            data = re.sub("style='font-size: ?18.0pt; ?font-family: ?\"Arial\",\"sans-serif\";color:#1F497D'", 'class="normal"', data)
            data = re.sub("style='font-size: ?18.0pt; ?font-family: ?\"Arial\",\"sans-serif\"'", 'class="normal"', data)

            data = re.sub("style='color:red'", 'class="different"', data)

            data = data.replace("</p>", "</p>\n")

            outfile.write(data)
            outfile.write("</body>\n")
            outfile.write("</html>\n")
            outfile.close()

        except Exception as ex:
            print(ex)

    @staticmethod
    def test():
        pagedata = '<div class="WordSection1"><p class="MsoNormal"><b><i><span style="font-size:18.0pt;font-family:&quot;Arial&quot;,&quot;sans-serif&quot;">4Q1Genesis-Exodus<sup>a</sup></span></i></b></p></div>'
        re_data = re.compile(r'<div class="WordSection1">(.*)</div>')
        search = re_data.search(pagedata)
        data = search.group(1)
        print(data)


if __name__ == '__main__':

    # find -name "*.html" -exec sed -i 's/color: lightred/color: salmon/g' {} \;

    # url = "http://dssenglishbible.com/scroll4Q1.htm"
    # ScrapeSite.scrapeDSSPage(url, "Genesis")

    urls = [
        ("http://dssenglishbible.com/ScrollsGenesis.htm", "1 Genesis"),
        ("http://dssenglishbible.com/ScrollsExodus.htm", "2 Exodus"),
        ("http://dssenglishbible.com/ScrollsLeviticus.htm", "3 Leviticus")
        ("http://dssenglishbible.com/ScrollsNumbers.htm", "4 Numbers"),
        ("http://dssenglishbible.com/ScrollsDeuteronomy.htm", "5 Deuteronomy"),
        ("http://dssenglishbible.com/scrollsJoshua.htm", "6 Joshua"),
        ("http://dssenglishbible.com/scrollsJudges.htm", "7 Judges"),
        ("http://dssenglishbible.com/scrollsRuth.htm", "8 Ruth"),
        ("http://dssenglishbible.com/ScrollsSamuel.htm", "9 Samuel"),
        ("http://dssenglishbible.com/ScrollsKings.htm", "11 Kings"),
        ("http://dssenglishbible.com/ScrollsJob.htm", "18 Job"),
        ("http://dssenglishbible.com/ScrollsPsalms.htm", "19 Psalms"),
        ("http://dssenglishbible.com/ScrollsProverbs.htm", "20 Proverbs"),
        ("http://dssenglishbible.com/ScrollsEcclesiastes.htm", "21 Ecclesiastes"),
        ("http://dssenglishbible.com/Scrollssong.htm", "22 Song of Solomon"),
        ("http://dssenglishbible.com/ScrollsIsaiah.htm", "23 Isaiah"),
        ("http://dssenglishbible.com/Scrollsjeremiah.htm", "24 Jeremiah"),
        ("http://dssenglishbible.com/Scrollslamentations.htm", "25 Lamentations"),
        ("http://dssenglishbible.com/Scrollsezekiel.htm", "26 Ezekiel"),
        ("http://dssenglishbible.com/Scrollsdaniel.htm", "27 Daniel"),
        ("http://dssenglishbible.com/ScrollsMinorProphets.htm", "28 Minor"),
    ]
    for url in urls:
        ScrapeSite.scrapeDSSSection(url[0], url[1])

    urls = [
        ("http://dssenglishbible.com/Scroll4Q118.htm", "13 Chronicles"),
        ("http://dssenglishbible.com/Scroll4Q117.htm", "15 Ezra"),
    ]
    for url in urls:
        ScrapeSite.scrapeDSSPage(url[0], url[1])
