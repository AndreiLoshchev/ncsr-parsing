'''
Created on 15.03.2017

@author: michael


Transfer classification labels from <TR> to the first <TR> element (in a row)

'''

from definitions import ANNOTATED_FILENAMES
from parse_ncsr_backend.ncsr_table_parsing import get_lxml_from_string
import lxml.html


count_soo=0
count_soo_sec=0
count_fh=0
print(len(ANNOTATED_FILENAMES))
for filename in ANNOTATED_FILENAMES:
    print(filename)
    # load
    with open(filename,'r') as f:
        s = f.read()
    tree = get_lxml_from_string(s)

    # examine all <TR> elements:
    TRs = tree.xpath('.//tr')
    
    SOO_LABEL="soo_label"
    SOO_LABEL_SEC="soo_label_sec"
    FH_LABEL="fh_label"
    # if soo_label ...
    for tr in TRs:
        TDs=tr.xpath('.//td')
        if len(TDs)==0:
            continue
        if SOO_LABEL in tr.attrib:
            TDs[0].attrib[SOO_LABEL]=tr.attrib.pop(SOO_LABEL)
            count_soo+=1
        if SOO_LABEL_SEC in tr.attrib:
            TDs[0].attrib[SOO_LABEL_SEC]=tr.attrib.pop(SOO_LABEL_SEC)
            count_soo_sec+=1
            
        if FH_LABEL in tr.attrib:
            TDs[0].attrib[FH_LABEL]=tr.attrib.pop(FH_LABEL)
            count_fh+=1
            
    with open(filename,'w') as f:
        f.write(lxml.html.tostring(tree))       
    
    
    
print(count_soo)
print(count_soo_sec)
print(count_fh)
