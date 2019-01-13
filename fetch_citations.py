#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io, os, re, sys, shutil, requests
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
    result['title'] = soup.find("meta", attrs = {"name": "citation_title"}).get("content")
    result['author_list'] = soup.find("meta", attrs = {"name": "citation_authors"}).get("content").split("; ")
    data_string = soup.find("meta", attrs = {"name": "citation_date"}).get("content")
    result['citation_date'] = tuple(data_string.split("/")[::-1])
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
    print_paper_info(main_paper)
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
        # print_paper_info(citation, 8)
    status = "valid: %d; total: %d" % (len(valid_citations), len(citation_list))
    return status, main_paper, valid_citations

def write_for_one_paper(dest_dir, status, main_paper, valid_citations):
    print "writting citation data for paper " + main_paper['bibcode'], "...",
    sys.stdout.flush()
    fmt, items = "%s, %s, %s", ['bibcode', 'title', 'ads_link']
    lines = [status, ', '.join(items)]
    lines.append( fmt % tuple([main_paper[it] for it in items]) )
    for citation in valid_citations: lines.append( fmt % tuple([citation[it] for it in items]) )
    output_fn = os.path.join(dest_dir, main_paper['bibcode'] + ".txt")
    with io.open(output_fn, 'w') as fout: fout.writelines("\n".join(lines))
    print "written to %s" % output_fn

def download_pdfs(dest_dir, main_paper, valid_citations):
    print "downloading PDFs for paper " + main_paper['bibcode'], "..."
    prefix_dir = os.path.join(dest_dir, main_paper['bibcode'] + '_pdfs')
    prefix_citation_dir = os.path.join(prefix_dir, 'citations')
    if not os.path.isdir(prefix_dir): os.mkdir(prefix_dir)
    if not os.path.isdir(prefix_citation_dir): os.mkdir(prefix_citation_dir)
    print ' - downloading ' + main_paper['bibcode'], "...",
    sys.stdout.flush()
    if main_paper['pdf_link']:
        output_fn = os.path.join(prefix_dir, main_paper['bibcode'] + ".pdf")
        if download_one_pdf(main_paper['pdf_link'], output_fn):
            print "[DONE => %s]" % output_fn
        else:
            print "[FAILED]"
    else:
        print '[NO PDF LINK]'
    for citation in valid_citations:
        print ' - downloading ' + citation['bibcode'], "...",
        sys.stdout.flush()
        if citation['pdf_link']:
            output_fn = os.path.join(prefix_citation_dir, citation['bibcode'] + ".pdf")
            if download_one_pdf(citation['pdf_link'], output_fn):
                print "[DONE => %s]" % output_fn
            else:
                print "[FAILED]"
        else:
            print "[NO PDF LINK]"

def download_one_pdf(url, filename):
    try:
        req = requests.get(url, headers = {'user-agent': 'ADS'})
    except requests.ConnectionError, e:
        return False
    if req.status_code == 200 and req.headers.get('content-type') == 'application/pdf':
        with open(filename, 'wb') as fout: fout.write(req.content)
        return True
    else:
        return False

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

    for (index, (name, link)) in enumerate(main_list, start = 1):
        print "== %d/%d ==" % (index, len(main_list))
        status, main_paper, valid_citations = fetch_for_one_paper(name, link)
        write_for_one_paper(destdir, status, main_paper, valid_citations)
        download_pdfs(destdir, main_paper, valid_citations)


