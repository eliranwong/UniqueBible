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
            text = "\n\n".join([pdfReader.getPage(pageNum).extractText() for pageNum in range(1, pdfReader.numPages)])
            pdfObject.close()
            return text
        except:
            return self.errorReadingFile(fileName)

    def readDocxFile(self, fileName):
        try:
            document = docx.Document(fileName)
            paragraphs = document.paragraphs
            return "\n".join([paragraph.text for paragraph in paragraphs])
        except:
            return self.errorReadingFile(fileName)
