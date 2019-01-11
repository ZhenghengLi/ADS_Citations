#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, sys
import shutil
import requests
from bs4 import BeautifulSoup as BS

def get_main_paper_list(url):
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
    result['title'] = soup.find("title").get_text()
    result['author_list'] = soup.find("meta", attrs = {"name": "citation_authors"}).get("content").split("; ")
    result['doi'] = soup.find("meta", attrs = {"name": "citation_doi"}).get("content")
    result['bibcode'] = soup.find('input', attrs = {"type": "hidden", "name": "bibcode"}).get("value")
    dt_list = soup.find_all("dt")
    ref_citation = re.compile(r'.*Citations to the Article.*', re.I)
    ref_article = re.compile(r'.*Electronic Refereed Journal Article.*', re.I)
    result['citation_link'] = None
    result['article_link'] = None
    for dt in dt_list:
        atag = dt.find("a")
        if not atag: continue
        if ref_article.match(atag.get_text()):
            result['article_link'] = atag.get("href")
        if ref_citation.match(atag.get_text()):
            result['citation_link'] = atag.get("href")
    return result

def get_citation_list(url):
    citation_list = []
    paper_list = get_main_paper_list(url)
    for name, link in paper_list:
        paper = get_paper_info(link)
        citation_list.append(paper)

def check_citation_type(p1, p2):
    al1 = p1['author_list']
    al2 = p2['author_list']
    for x1 in al1:
        for x2 in al2:
            # TODO:
            if x1 == x2: return False
    return True

def write_data(dest_dir, status, main_paper, valid_citation_list):
    with open(os.path.join(dest_dir, main_paper['bibcode'] + ".txt"), 'w') as fout:
        head_line = "bibcode, title, article_link"
        lines = []
        lines.append(status)
        lines.append(head_line)
        first_line = "%s, %s, %s" % (main_paper['bibcode'], main_paper['title'], main_paper['article_link'])
        lines.append(first_line)
        for citation in valid_citation_list:
            citation_line = "%s, %s, %s" % (citation['bibcode'], citation['title'], citation['article_link'])
            lines.append(citation_line)
        fout.writelines([line + "\n" for line in lines])


def fetch_entry(paper_name_link):
    name, link = paper_name_link
    main_paper = get_paper_info(link)
    author_list = main_paper['author_list']
    citation_list = get_citation_list(main_paper['citation_link'])
    valid_citation_list = []
    for citation in citation_list:
        if check_citation_type(author_list, citation['author_list']):
            valid_citation_list.append(citation)
    status = "%d / %d" % (len(valid_citation_list), len(citation_list))
    return status, main_paper, valid_citation_list


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "USAGE: " + sys.argv[0] + " <url> <destdir>"
        exit(1)

    url, destdir = sys.argv[1:3]

    main_list = get_main_paper_list(url)
    for name_link in main_list:
        status, main_paper, valid_citation_list = fetch_entry(name_link)
        write_data(destdir, status, main_paper, valid_citation_list)

    # res = get_paper_info(url)
    # for x in res:
    #     print x, "=>", res[x]

