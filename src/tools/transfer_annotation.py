'''
Created on 07.03.2017

@author: mf

Transfer annotation to the original 
document (amend encoding errors in some of the annotated docs).

'''
import lxml.html
from lxml.builder import E


from definitions import ANNOTATED_FILENAMES
import os
from parse_ncsr_backend.ncsr_table_parsing import get_lxml_from_string

orig_files_missing=[]


def checkLayout(tables_a, tables_b):
        allGood = True
        
        if(len(tables_a)!=len(tables_a)):
            allGood=False
            return False
        else:
            for t in zip(tables_a,tables_b):
                if len(t[0].xpath('.//tr'))!=len(t[1].xpath('.//tr')):
                    allGood=False
        return allGood
                
for annotated in ANNOTATED_FILENAMES:
    
    #print(item.endswith('annotated.html'))
    
    
    
    orig_filename=annotated[:-15]+'.html'
    if not os.path.isfile(orig_filename):
        
        orig_files_missing.append(annotated)
        
    else:
        with open(orig_filename,'r') as f:
            s = f.read()
        clean = get_lxml_from_string(s)
        
        with open(annotated,'r') as f:
            s = f.read()
        anno = get_lxml_from_string(s)
        
        # table count:
        allGood = True
        tables_clean = clean.xpath('//table')
        tables_anno = anno.xpath('//table')
        
        allGood = checkLayout(tables_clean, tables_anno)
        
        
        if allGood:
            # both files are present and tables are identical:
            
            
            
            # ? encoding?
            
            soo_label = "soo_label"
            fh_label = "fh_label"
            soo_label_sec = "soo_label_sec"
            
            soo_table = "soo_table"
            soo_table_cont = "soo_table_cont"
            fh_table="fh_table"
            fh_table_cont = "fh_table_cont"
            table_other = 'other'
            
            # 1) for all <table> tags: transfer all "class" item
            for t_item in zip(tables_anno,tables_clean):
                classes = t_item[0].get('class')
                if classes:
                    
                    if soo_table_cont in classes:
                        t_item[1].classes.add(soo_table_cont)

                    elif fh_table_cont in classes:
                        t_item[1].classes.add(fh_table_cont)
                    
                    elif fh_table in classes:
                        t_item[1].classes.add(fh_table)
                    
                    elif soo_table in classes:
                        t_item[1].classes.add(soo_table)
                    # 2) for all <tr> tags in a table:
                    #     if soo_label and soo_label_sec are present -> transfer
                    #     if fh_label is present -> transfer
                    if not table_other in classes:
                        for tds in zip(t_item[0].xpath('.//tr'),t_item[1].xpath('.//tr')):
                            if soo_label in tds[0].keys():
                                tds[1].attrib[soo_label]=tds[0].attrib[soo_label]
                            if soo_label_sec in tds[0].keys():
                                tds[1].attrib[soo_label_sec]=tds[0].attrib[soo_label_sec]
                            if fh_label in tds[0].keys():
                                tds[1].attrib[fh_label]=tds[0].attrib[fh_label]
                
            head = clean.find('.//head')
            
            scripttag_1 = E.script(src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js")
            scripttag_2 = E.script(src="annotator.js")
            
            head.append(scripttag_1)
            head.append(scripttag_2)
            savename = annotated 
            with open(savename,'w') as f:
                f.write(lxml.html.tostring(clean))
                
                     
                
            
for item in orig_files_missing:
    print(item)
        
