from urllib import request
import re

class ScrapeSite:

    @staticmethod
    def scrapeDSSPage(url):
        try:
            response = request.urlopen(url)
            pagedata = response.read().decode("iso-8859-1")
            pagedata = pagedata.replace("\r", "").replace("\n", " ")

            re_title = re.compile('<title>Biblical Dead Sea Scrolls - (.*)</title>')
            title = re_title.search(pagedata).group(1)

            print(title)

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

            print(data)

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

    url = "http://dssenglishbible.com/scroll4Q1.htm"
    ScrapeSite.scrapeDSSPage(url)

