#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from docx import Document
from docx.shared import Inches

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

    document = Document()

    table = document.add_table(rows=0, cols=2)
    table.style = 'Table Grid'

    add_two_cols(table,
            u'论文1',
            u'填写论文信息，格式见备注1')

    add_one_col(table,
            u'论文引用情况及重要评价：填写论文信息，格式见备注1')

    add_one_col(table,
            u'引用数：   他引数（文献被除作者及合作者以外其他人的引用）：')

    add_two_cols(table,
            u'他引论文1',
            u'填写论文信息，格式见备注1')

    add_one_col(table,
            u'评价的中英文：引用部分的重要评价原文，如原文是英文请同时翻译成中文，如判断某一篇论文没有重要评价，就空着')

    add_two_cols(table,
            u'他引论文2',
            u'')

    add_one_col(table,
            u'')

    add_two_cols(table,
            u'他引论文n',
            u'')

    add_one_col(table,
            u'')

    # document.add_page_break()
    document.save(output_fn)

