#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, io
from docx import Document
from docx.shared import Inches

def extract_info(line):
    separator = u' <-=|=-> '
    fields = line.split(separator)
    info = {}
    info['bibcode'] = fields[0]
    info['publication_date'] = fields[1]
    info['author_list_str'] = fields[2]
    info['title'] = fields[3]
    info['publication_journal'] = fields[4]
    info['ads_link'] = fields[5]
    return info

def read_paper(filename):
    lines = None
    with io.open(filename, 'r') as fin: lines = fin.readlines()
    lines = [line.strip() for line in lines]
    paper = {}
    ref_fl = re.compile(r'valid: (\d+); total: (\d+)')
    m = ref_fl.match(lines[0])
    if m:
        paper['valid'], paper['total'] = int(m.group(1)), int(m.group(2))
    else:
        paper['valid'], paper['total'] = 0, 0
    paper['main'] = extract_info(lines[2])
    paper['citations'] = []
    for line in lines[3:]:
        paper['citations'].append(extract_info(line))
    return paper

def add_two_cols(table, col1_str, col2_str):
    col1, col2 = table.add_row().cells
    col1.text, col2.text = col1_str, col2_str

def add_one_col(table, col_str):
    col1, col2 = table.add_row().cells
    mcol = col1.merge(col2)
    mcol.text = col_str

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print 'Usage: ' + sys.argv[0] + ' <input.txt> <output.docx>'
        exit(1)

    input_fn, output_fn = sys.argv[1:3]
    paper_id = int(input_fn[0:3])
    paper = read_paper(input_fn)

    document = Document()

    table = document.add_table(rows=0, cols=2)
    table.style = 'Table Grid'

    add_two_cols(table,
            u'论文 %d' % paper_id,
            '. '.join([paper['main']['author_list_str'],
                paper['main']['title'], paper['main']['publication_journal']]))

    add_one_col(table,
            u"\n".join([u"论文引用情况及重要评价：", paper['main']['bibcode'],
                paper['main']['publication_date'], paper['main']['ads_link']]))

    add_one_col(table,
            u'引用数： %d    他引数： %d' % (paper['total'], paper['valid']) )

    for index, citation in enumerate(paper['citations'], start = 1):
        add_two_cols(table,
                u'他引论文 %d' % index,
                '. '.join([citation['author_list_str'], citation['title'], citation['publication_journal']]))
        add_one_col(table,
                u"\n".join([u"评价的中英文：", citation['bibcode'],
                    citation['publication_date'], citation['ads_link']]))

    # document.add_page_break()
    document.save(output_fn)

