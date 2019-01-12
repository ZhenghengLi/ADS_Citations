#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, sys, shutil, requests
from bs4 import BeautifulSoup as BS

def get_paper_list(url):
    soup = BS(requests.get(url).content, 'lxml')
    tags = soup.find_all("input", attrs = {"name": "bibcode","type": "checkbox"})
    paper_list = []
    for tag in tags:
        atag = tag.parent.find("a")
        paper_list.append( (atag.get_text(), atag.get("href")) )
    return paper_list

def get_paper_info(url):
    soup = BS(requests.get(url).content, "lxml")
    result = {}
    result['ads_link'] = url
    result['title'] = soup.find("title").get_text()
    result['author_list'] = soup.find("meta", attrs = {"name": "citation_authors"}).get("content").split("; ")
    result['bibcode'] = soup.find('input', attrs = {"type": "hidden", "name": "bibcode"}).get("value")
    tag = soup.find("a", string = re.compile(r'.*Citations to the Article.*', re.I))
    result['citation_link'] = tag.get("href") if tag else None
    tag = soup.find("a", string = re.compile(r'.*Electronic Refereed Journal Article.*', re.I))
    result['article_link'] = tag.get("href") if tag else None
    tag = soup.find('a', string = re.compile(r'.*Refereed Journal Article.*PDF.*', re.I))
    result['pdf_link'] = tag.get("href") if tag else None
    return result

def get_citation_list(url, log_indent = -1):
    citation_list = []
    paper_list = get_paper_list(url)
    for name, link in paper_list:
        if log_indent >= 0: print " " * log_indent + "fetch citation info of " + name + " ..."
        paper = get_paper_info(link)
        citation_list.append(paper)
    return citation_list

def check_citation_type(main_paper, citation):
    # check for self citation or others by comparing author lists
    for x1 in main_paper['author_list']:
        for x2 in citation['author_list']:
            # TODO: here use a very strict check
            if x1 == x2: return False
    return True

def fetch_for_one_paper(link):
    main_paper = get_paper_info(link)
    if not main_paper['citation_link']:
        return "0 / 0", main_paper, []
    citation_list = get_citation_list(main_paper['citation_link'])
    valid_citation_list = []
    for citation in citation_list:
        if check_citation_type(main_paper, citation): valid_citation_list.append(citation)
    status = "%d / %d" % (len(valid_citation_list), len(citation_list))
    return status, main_paper, valid_citation_list

def write_for_one_paper(dest_dir, tatus, main_paper, valid_citation_list):
    lines = [status, "bibcode, title, article_link"]
    leading_line = "%s, %s, %s" % (main_paper['bibcode'], main_paper['title'], main_paper['article_link'])
    lines.append(leading_line)
    for citation in valid_citation_list:
        citation_line = "%s, %s, %s" % (citation['bibcode'], citation['title'], citation['article_link'])
        lines.append(citation_line)
    with open(os.path.join(dest_dir, main_paper['bibcode'] + ".txt"), 'w') as fout:
        fout.writelines("\n".join(lines))

def download_pdfs(dest_dir, main_paper, valid_citation_list):
    prefix = os.path.join(dest_dir, main_paper['bibcode'] + '_pdfs')
    os.mkdir(prefix)
    os.mkdir(os.path.join(prefix, 'citations'))
    if not main_paper['pdf_link']:
        print 'download pdf from the link to prefix, use the bibcode as name'
    for citation in valid_citation_list:
        if not citation['pdf_link']:
            print 'download pdf from the link to prefix/citations, use the bibcode as name'

def print_paper_info(paper, log_indent = 0):
    bibcode = paper['bibcode']
    print " " * log_indent + "== " + bibcode + " ========================================"
    for key in paper:
        if key == 'author_list' and len(paper['author_list']) > 3:
            print " " * log_indent + key, "=>", paper['author_list'][0:3] + ['et al.']
        else:
            print " " * log_indent + key, "=>", paper[key]
    print ''

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "USAGE: " + sys.argv[0] + " <url> <destdir>"
        exit(1)

    url, destdir = sys.argv[1:3]

    #main_list = get_paper_list(url)

    #for name_link in main_list[0]:
    #    status, main_paper, valid_citation_list = fetch_entry(name_link)
    #    write_data(destdir, status, main_paper, valid_citation_list)

    # res = get_paper_info(url)
    # for x in res:
    #     print x, "=>", res[x]

    # res = fetch_for_one_paper(url)
    # print get_citation_list(url)

    res = get_citation_list(url, 4)
    print " "
    for x in res:
        print_paper_info(x, 4)



