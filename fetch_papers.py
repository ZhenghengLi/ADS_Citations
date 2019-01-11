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
    result['title'] = soup.find("title").get_text()
    result['author_list'] = soup.find("meta", attrs = {"name": "citation_authors"}).get("content").split("; ")
    result['bibcode'] = soup.find('input', attrs = {"type": "hidden", "name": "bibcode"}).get("value")
    tag = soup.find("a", string = re.compile(r'.*Citations to the Article.*', re.I))
    result['citation_link'] = tag.get_text() if tag else None
    tag = soup.find("a", string = re.compile(r'.*Electronic Refereed Journal Article.*', re.I))
    result['article_link'] = tag.get_text() if tag else None
    return result

def get_citation_list(url):
    citation_list = []
    paper_list = get_paper_list(url)
    for name, link in paper_list:
        paper = get_paper_info(link)
        citation_list.append(paper)
    return citation_list

def check_citation_type(al1, al2):
    # check for self citation or others by comparing author lists
    for x1 in al1:
        for x2 in al2:
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
        if check_citation_type(main_paper['author_list'], citation['author_list']):
        # if True:
            valid_citation_list.append(citation)
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

    print fetch_for_one_paper(url)
    # print get_citation_list(url)



