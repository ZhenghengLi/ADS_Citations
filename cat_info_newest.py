# -*- coding: UTF-8 -*-
'''
written by Nang Yi
mail nangyi@ihep.ac.cn
'''
import requests
from bs4 import BeautifulSoup
import re,sys
import urllib2
#sys.setdefaultencoding('utf-8')
def opwb(url):
    req = requests.get(url,{'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'})
    soup = BeautifulSoup(req.text,'lxml')
    lt=soup.find_all(attrs={'name':'bibcode','type':'checkbox'})
    return lt


def sea(wb):
    lts=[]
    wurl= requests.get(wb,{'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'})
    soup = BeautifulSoup(wurl.text,'lxml')
    ##########
    resp = urllib2.urlopen(wb)
    soup = BeautifulSoup(resp, from_encoding=resp.info().getparam('Refereed Journal Article (PDF/Postscript)'))
    for link in soup.find_all('a', href=True, text = 'Full Refereed Journal Article (PDF/Postscript)'):
        print link['href']
        if link.has_attr('href'):
            print link['href']
    #########
    lts.append(''.join(soup.find_all(text="Authors:")[0].parent.parent.next_sibling.next_sibling.text.split()).encode('utf-8'))
    lts.append(soup.find_all(text="Title:")[0].parent.parent.next_sibling.next_sibling.text.encode('utf-8'))
    tpl = soup.find_all(text="Publication:")[0].parent.parent.next_sibling.next_sibling.text.split(',')
    len_tpl = len(tpl)
    if len_tpl==4:
        print tpl
        lts.append(tpl[0].encode())
        if len(tpl[1].split())==2:
            lts.append(tpl[1].split()[1].encode('utf-8'))
        else:
            lts.append(tpl[1].encode)
        len_tpl2 = len(tpl[2].split())
        if len_tpl2==2:
            lts.append(tpl[2].split()[1].encode('utf-8'))
        else:
            lts.append(tpl[2].encode('utf-8'))
        lts.append('-'.join(re.findall('(\d+)',tpl[3])).encode())
    else:
        lts.append(tpl[0].encode('utf-8'))    
    lts.append(soup.find_all(text="Publication Date:")[0].parent.parent.next_sibling.next_sibling.text.split('/')[1].encode('utf-8'))
    return lts,len_tpl

def head(wb,outfile):
    print outfile
    wurl= requests.get(wb,{'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0'})
    soup = BeautifulSoup(wurl.text,'lxml')
    cord = soup.find_all(text=re.compile("Citations to the Article "))[0].parent
    fpg,len_tpl = sea(wb)
    print fpg
    with open(r'%s'%outfile,'w')as f:
        if len_tpl==4:
            print>>f,'论文\t'+'. '.join(fpg[:3])+'.%s(%s)(%s),%s.\n'%(fpg[3],fpg[4],fpg[6],fpg[5])
        else:
            print>>f,'论文\t'+'. '.join(fpg[:3])+'.%s.\n'%(fpg[-1])
        print>>f,'论文引用情况及重要评价：'
        print>>f,'引用数：%s  他引数：'%(re.split('[()]',cord.text)[1].encode('utf-8'))
    return cord['href']


def write(wb,outfile):
    website = head(wb,outfile)
    lt = opwb(website)
    with open(r'%s'%outfile,'a')as f:
        for i in range(len(lt)):
            wb = lt[i].parent.a.get("href").encode('utf-8')
            oupt,len_tpl = sea(wb)
            print sea(wb)
            if len_tpl==4:
                print>>f,'他引论文%s\t'%(i+1) + '. '.join(oupt[:3])+'.%s(%s)(%s),%s.\n'%(oupt[3],oupt[4],oupt[6],oupt[5])
            else:
                print>>f,'他引论文%s\t'%(i+1) + '. '.join(oupt[:3])+'.%s.\n'%(oupt[-1])

#def downloadfile(link):
#    download_file("http://adsabs.harvard.edu/abs/1997ApJ...477L..95Z")
#
#def download_file(download_url):
#    response = urllib2.urlopen(download_url)
#    file = open("document1.pdf", 'wb')
#    file.write(response.read())
#    file.close()
#    print("Completed")

if __name__ == "__main__":
    if len(sys.argv)< 2:
        urls = raw_input("URLS:")
        oup = raw_input("outfile:")
    else:
        urls,oup = sys.argv[1],sys.argv[2]
    write(urls,oup)

