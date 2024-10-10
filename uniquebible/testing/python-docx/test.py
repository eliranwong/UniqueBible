#! /Users/Eliran/Desktop/venv/venv/bin/python
# source: https://github.com/python-openxml/python-docx/issues/276

from __future__ import (
    absolute_import, division, print_function, unicode_literals
)

from docx import Document
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph


def iter_block_items(parent):
    """
    Generate a reference to each paragraph and table child within *parent*,
    in document order. Each returned value is an instance of either Table or
    Paragraph. *parent* would most commonly be a reference to a main
    Document object, but also works for a _Cell object, which itself can
    contain paragraphs and tables.
    """
    if isinstance(parent, _Document):
        parent_elm = parent.element.body
        # print(parent_elm.xml)
    elif isinstance(parent, _Cell):
        parent_elm = parent._tc
    else:
        raise ValueError("something's not right")

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)

def table_print(block):
    table=block
    for row in table.rows:
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                print(paragraph.text,'  ',end='')
                #y.write(paragraph.text)
                #y.write('  ')
        print("\n")
        #y.write("\n")

document = Document('test2.docx')

#for block in iter_block_items(document):
#    print('found one')
#    print(block.text if isinstance(block, Paragraph) else '<table>')
   
for block in iter_block_items(document):
    if isinstance(block, Paragraph):
        print(block.text)
    elif isinstance(block, Table):
        table_print(block)