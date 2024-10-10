# This file contains class and functions related to reading external files

# To support reading paragraphs and tables with python-docx
# source: https://github.com/python-openxml/python-docx/issues/276
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from uniquebible import config
if ("Mammoth" in config.enabled):
    import mammoth
#if ("PyPDF2" in config.enabled):
#    import PyPDF2
#if ("Pythondocx" in config.enabled):
#    from docx import Document
#    from docx.document import Document as _Document
#    from docx.oxml.text.paragraph import CT_P
#    from docx.oxml.table import CT_Tbl
#    from docx.table import _Cell, Table
#    from docx.text.paragraph import Paragraph

class TextFileReader:

    def errorReadingFile(self, fileName):
        print('Failed to open file "{0}"!'.format(fileName))
        return ""

    def readTxtFile(self, fileName):
        try:
            f = open(fileName, "r", encoding="utf-8")
            text = f.read()
            f.close()
            return text
        except:
            return self.errorReadingFile(fileName)

#    def readPdfFile(self, fileName):
#        try:
#            pdfObject = open(fileName, "rb")
#            pdfReader = PyPDF2.PdfFileReader(pdfObject)
#            text = "\n\n".join([pdfReader.getPage(pageNum).extractText() for pageNum in range(0, pdfReader.numPages)])
#            pdfObject.close()
#            return text
#        except:
#            return self.errorReadingFile(fileName)

    def readDocxFile(self, fileName):
        with open(fileName, "rb") as docx_file:
            result = mammoth.convert_to_html(docx_file)
            html = result.value # The generated HTML
            #messages = result.messages # Any messages, such as warnings during conversion
        return html

#    def readDocxFileOLD(self, fileName):
#        document = Document(fileName)
#        documentText = ""
#        for block in self.iter_block_items(document):
#            if isinstance(block, Paragraph):
#                documentText += self.format_paragraph(block)
#            elif isinstance(block, Table):
#                documentText += self.format_table(block)
#        documentText = self.customFormat(documentText)
#        return documentText
#
#    def iter_block_items(self, parent):
#        """
#        Generate a reference to each paragraph and table child within *parent*,
#        in document order. Each returned value is an instance of either Table or
#        Paragraph. *parent* would most commonly be a reference to a main
#        Document object, but also works for a _Cell object, which itself can
#        contain paragraphs and tables.
#        """
#        if isinstance(parent, _Document):
#            parent_elm = parent.element.body
#            # print(parent_elm.xml)
#        elif isinstance(parent, _Cell):
#            parent_elm = parent._tc
#        else:
#            raise ValueError("something's not right")
#
#        for child in parent_elm.iterchildren():
#            if isinstance(child, CT_P):
#                yield Paragraph(child, parent)
#            elif isinstance(child, CT_Tbl):
#                yield Table(child, parent)
#
#    def format_paragraph(self, paragraph):
#
#        paragraphText = ""
#        for run in paragraph.runs:
#            #print(run.text, run.style.name)
#            runText = run.text
#            if run.bold:
#                runText = "<b>{0}</b>".format(runText)
#            if run.italic:
#                runText = "<i>{0}</i>".format(runText)
#            if run.underline:
#                runText = "<u>{0}</u>".format(runText)
#            if run.font.superscript:
#                runText = "<sup>{0}</sup>".format(runText)
#            if run.font.subscript:
#                runText = "<sub>{0}</sub>".format(runText)
#            if run.font.strike or run.font.double_strike:
#                runText = "<s>{0}</s>".format(runText)
#            if run.font.rtl:
#                runText = "<rtl>{0}</rtl>".format(runText)
#            paragraphText += runText
#        if paragraph.style.name == "List Paragraph":
#            paragraphText = "<ul><li>{0}</li></ul>".format(paragraphText)
#        else:
#            paragraphText = "<p>{0}</p>".format(paragraphText)
#
#        # paragraph.alignment
#        # None, CENTER ([0-9]), RIGHT ([0-9]), LEFT ([0-9]), JUSTIFY ([0-9]), DISTRIBUTE ([0-9])
#        alignment, *_ = str(paragraph.alignment).split(" ")
#        alignments = {
#            "None": "",
#            "CENTER": "center",
#            "RIGHT": "right",
#            "LEFT": "left",
#            "JUSTIFY": "",
#            "DISTRIBUTE": "justify",
#        }
#        alignment = alignments.get(alignment, "")
#        if alignment:
#            paragraphText = "<div style='text-align:{0};'>{1}</div>".format(alignment, paragraphText)
#
#        return paragraphText
#
#    def format_table(self, table):
#        tableText = "<table>"
#        for row in table.rows:
#            tableText += "<tr>"
#            for cell in row.cells:
#                for paragraph in cell.paragraphs:
#                    tableText += "<td>{0}</td>".format(self.format_paragraph(paragraph))
#            tableText += "</tr>"
#        tableText += "</table>"
#        return tableText
#
#    def customFormat(self, text):
#        text = text.replace("</ul><ul>", "")
#        return text
