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
    tag = soup.find("a", string = re.compile(r'.*Electronic Refereed Journal Article.*'))
    result['article_link'] = tag.get("href") if tag else None
    tag = soup.find('a', string = re.compile(r'.*Refereed Journal Article.*PDF.*'))
    result['pdf_link'] = tag.get("href") if tag else None
    ref_citation = re.compile(r'.*Citations to the Article \((\d+)\).*')
    tag = soup.find("a", string = ref_citation)
    result['citation_link'] = tag.get("href") if tag else None
    result['citation_count'] = int(ref_citation.match(tag.get_text()).group(1)) if tag else 0
    return result

def check_citation_type(main_paper, citation):
    # check for self citation or others by comparing author lists
    for x1 in main_paper['author_list']:
        for x2 in citation['author_list']:
            # TODO: here use a very strict check
            if x1 == x2: return False
    return True

def fetch_for_one_paper(name, link):
    print 'fetching citations for paper ' + name + ' ...'
    main_paper = get_paper_info(link)
    # print_paper_info(main_paper)
    if not main_paper['citation_link']:
        print "NO CITATIONS for this paper."
        return "NO CITATIONS", main_paper, []
    print " - fetching citation list ...",
    sys.stdout.flush()
    citation_list = get_paper_list(main_paper['citation_link'])
    print "total %d." % len(citation_list),
    sys.stdout.flush()
    if (len(citation_list) != main_paper['citation_count']):
        print "WARNING: expectation is %d" % main_paper['citation_count']
    else:
        print
    valid_citations = []
    for (index, (name, link)) in enumerate(citation_list, start = 1):
        print " - %d/%d" % (index, len(citation_list)), "fetching citation info of " + name + " ...",
        sys.stdout.flush()
        citation = get_paper_info(link)
        if check_citation_type(main_paper, citation):
            valid_citations.append(citation)
            print '[cited by others]'
        else:
            print '[cited by self]'
    status = "valid: %d; total: %d" % (len(valid_citations), len(citation_list))
    return status, main_paper, valid_citations

def write_for_one_paper(dest_dir, tatus, main_paper, valid_citations):
    print "writting citation data for paper " + main_paper['bibcode'], "...",
    sys.stdout.flush()
    lines = [status, "bibcode, title, ads_link"]
    leading_line = "%s, %s, %s" % (main_paper['bibcode'], main_paper['title'], main_paper['ads_link'])
    lines.append(leading_line)
    for citation in valid_citations:
        citation_line = "%s, %s, %s" % (citation['bibcode'], citation['title'], citation['ads_link'])
        lines.append(citation_line)
    output_fn = os.path.join(dest_dir, main_paper['bibcode'] + ".txt")
    with open(output_fn, 'w') as fout:
        fout.writelines("\n".join(lines))
    print "written to %s" % output_fn

def download_pdfs(dest_dir, main_paper, valid_citations):
    prefix = os.path.join(dest_dir, main_paper['bibcode'] + '_pdfs')
    os.mkdir(prefix)
    os.mkdir(os.path.join(prefix, 'citations'))
    if not main_paper['pdf_link']:
        print 'download pdf from the link to prefix, use the bibcode as name'
    for citation in valid_citations:
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
    print " " * log_indent + "-----------------------------------------------------------"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print "USAGE: " + sys.argv[0] + " <url> <destdir>"
        exit(1)

    url, destdir = sys.argv[1:3]
    if not os.path.isdir(destdir):
        print 'Directory "%s" does not exist.' % destdir
        exit(1)

    print 'fetching main list ...',
    sys.stdout.flush()
    main_list = get_paper_list(url)
    print "total: %d" % len(main_list)

    for name, link in main_list[0:2]:
        status, main_paper, valid_citations = fetch_for_one_paper(name, link)
        write_for_one_paper(destdir, status, main_paper, valid_citations)


