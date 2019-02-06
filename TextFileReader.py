import PyPDF2, docx

class TextFileReader:

    def errorReadingFile(self, fileName):
        print('Failed to open file "{0}".'.format(fileName))
        return ""

    def readTxtFile(self, fileName):
        try:
            f = open(fileName,'r')
            text = f.read()
            f.close()
            return text
        except:
            return self.errorReadingFile(fileName)

    def readPdfFile(self, fileName):
        try:
            pdfObject = open(fileName,'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfObject)
            text = "\n\n".join([pdfReader.getPage(pageNum).extractText() for pageNum in range(0, pdfReader.numPages)])
            pdfObject.close()
            return text
        except:
            return self.errorReadingFile(fileName)

    def readDocxFile(self, fileName):
        try:
            document = docx.Document(fileName)
            paragraphs = document.paragraphs
            text = []
            for paragraph in paragraphs:
                paragraphText = ""
                for run in paragraph.runs:
                    runText = run.text
                    if run.bold:
                        runText = "<b>{0}</b>".format(runText)
                    if run.italic:
                        runText = "<i>{0}</i>".format(runText)
                    if run.underline:
                        runText = "<u>{0}</u>".format(runText)
                    if run.font.superscript:
                        runText = "<sup>{0}</sup>".format(runText)
                    if run.font.subscript:
                        runText = "<sub>{0}</sub>".format(runText)
                    if run.font.strike or run.font.double_strike:
                        runText = "<s>{0}</s>".format(runText)
                    if run.font.rtl:
                        runText = "<rtl>{0}</rtl>".format(runText)
                    paragraphText += runText
                text.append(paragraphText)
            text = "<br>".join(text)
            return text
        except:
            return self.errorReadingFile(fileName)
