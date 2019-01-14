#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Author: Zhengheng Li <zhenghenge@gmail.com>

import os, sys, re, io
import numpy as np

def read_citation_count(filename):
    first_line = None
    with io.open(filename, 'r') as fin: first_line = fin.readline().strip()
    ref_fl = re.compile(r'valid: (\d+); total: (\d+)')
    m = ref_fl.match(first_line)
    if m:
        return int(m.group(2))
    else:
        return 0


if __name__ == '__main__':

    bibcode_list = []
    citation_count_list = []
    for fn in sys.argv[1:]:
        bibcode_list.append(fn[:-4])
        citation_count_list.append(read_citation_count(fn))
    bibcode_index = np.argsort(citation_count_list)
    for idx, x in enumerate(reversed(bibcode_index), start = 1):
        print idx, bibcode_list[x], citation_count_list[x]
        idx_str = "%03d_" % idx
        os.rename(bibcode_list[x] + ".txt", idx_str + bibcode_list[x] + ".txt")
        os.rename(bibcode_list[x] + "_pdfs", idx_str + bibcode_list[x] + "_pdfs")

