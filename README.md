# ADS_Citations

## Usages

### Step 1: Fetch citations for a paper list  
$ mkdir results  
$ ./fetch_citations.py "http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?library&libname=achievement-3-methods&libid=44cf02882f" results  

### Step 2: Sort by citations count  
$ cd results  
$ ../sort_by_citation_count.py *.txt  

### Step 3: Convert to ms-word file  
$ # keep in the 'results' folder  
$ for x in *.txt; do echo $x; ../ADS_Citations/save_to_docx.py $x ${x/.txt/.docx}; done  
