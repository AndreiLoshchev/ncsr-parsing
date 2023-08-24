'''
Created on 12.10.2016

@author: michael
'''                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             


import argparse
import os

import dill
 

from parse_ncsr_backend.table_classifier_crf_crfsuite import TableClassifierCRF_CRFsuite
from parse_ncsr_backend.ncsr_table_parsing import load_table_data,\
    create_table, parse_ncsr_tables_raw_tag, get_lxml_from_string

from definitions import DATA_DIR 
from parse_ncsr.table_detector import TableDetector
import sys
import lxml.html
from lxml.builder import E
 

from definitions import CRF_FH_SERIALIZED_FILENAME
from definitions import CRF_SOO_SERIALIZED_FILENAME

ADD_SCRIPT_TAGS=True
DETECT_TABLES=True

def main(args): 
    
    
    data = [['SOO', CRF_SOO_SERIALIZED_FILENAME, TableClassifierCRF_CRFsuite, "soo_table"],['FH', CRF_FH_SERIALIZED_FILENAME, TableClassifierCRF_CRFsuite, "fh_table"]]
    
    s = args.InputFilename.read()
    if s is None:
        raise Exception("Input file could not be parsed")
    
    tree = get_lxml_from_string(s)

    if DETECT_TABLES:
        table_detector = TableDetector()
        prediction, confidence = table_detector.predict(tree)
        print("Found " + str(sum([1 for x in prediction if x==table_detector.target_fh])) + ' FH tables')
        print("Found " + str(sum([1 for x in prediction if x==table_detector.target_soo])) + ' SOO tables')
        tables=tree.xpath('.//table')
        for i,pred in enumerate(prediction):
            classes = tables[i].classes
            classes.add(pred)
             
            if pred==table_detector.target_soo:
                classes.add(pred)
                     
 
        head = tree.find('.//head')
            
        scripttag_1 = E.script(src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js")
        scripttag_2 = E.script(src="annotator.js")
        
        head.append(scripttag_1)
        head.append(scripttag_2)
         
        
    # FH classification not fully included yet: 
    for item in data:
        
        shortName, clf_filename, clf_type, tableType = item
        
        if not os.path.isfile(os.path.join(DATA_DIR,clf_filename)):
            tables = load_table_data(tableType)
            gt = [t.getGroundTruth() for t in tables]
            # filter non-annotated tables:
            tmpTables=[]
            tmpGT=[]
            for i in range(len(tables)):
                if any([True if x[0]!='undefined' else False for x in gt[i] ]):
                    tmpTables.append(tables[i])
                    tmpGT.append(gt[i])
            
            tables=tmpTables
            gt = tmpGT
            
            
            sc = clf_type(tableClass=tableType)
            
            print('Training classifier for ' + shortName + ' tables (this may take some time)')
            print('Using ' + str(len(tables)) + " tables for training.")
            sc.fit(tables,gt)
            with open(os.path.join(DATA_DIR,clf_filename),'w') as f:
                dill.dump(sc,f)
        else:
            with open(os.path.join(DATA_DIR,clf_filename),'r') as f:
                sc = dill.load(f)
            
        xpath_expr = '//table[@class="' + tableType + '"]'
        tableRaw = tree.xpath(xpath_expr)
        
        #tableRaw = soup.find("table",class_=tableType)
        
        data = parse_ncsr_tables_raw_tag(tableRaw[0], tableType)
        table = create_table(data)
        
        # current annotation does not fit 'vertical' table 
        # orientation occurring in FH tables:
        if table[0].getOrientation()!='vertical':
            print('Skipping annotation of ' + shortName + ', as orientation is horizontal.')
        else:    
            output = sc.predict(table)
            prediction = output['prediction'][0] 
            
            tr = tableRaw[0].xpath('.//tr')
            for item in zip(tr,prediction):
                td = item[0].xpath('.//td')
                if tableType=="soo_table":
                    td[0].attrib['soo_label']    =item[1][0]
                    td[0].attrib['soo_label_sec']=item[1][1]
                else:
                    td[0].attrib['fh_label']    =item[1][0]

    # Add encoding tag
#     metatag = tableData['soup'].new_tag('meta')
#     metatag.attrs['charset']='utf-8'
#     tableData['soup'].head.append(metatag)
    if not args.OutputFilename:
        
        outputFilename=args.InputFilename.name
        if outputFilename.endswith('-toc-annotated'):
            outputFilename=outputFilename[:-14]+'-annotated.html'
        elif outputFilename.endswith('.html'):
            outputFilename=outputFilename[:-5]+'-annotated.html'
            print(outputFilename)
        print('Using default extension -annotated.html for output')
           
            
    else:
        outputFilename=args.OutputFilename
    if ADD_SCRIPT_TAGS:
            head = tree.find('.//head')
            
            scripttag_1 = E.script(src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js")
            scripttag_2 = E.script(src="annotator.js")
            
            head.append(scripttag_1)
            head.append(scripttag_2)
            
                
    if os.path.isfile(outputFilename):
        answer = raw_input('\nFile ' + outputFilename + ' exists. Overwrite [y/n]?')
        if answer!='y':
            print('Aborting')
            sys.exit(0)
    
    with open(outputFilename,'w') as f:
        #f.write(soup.prettify().encode('utf-8'))
        f.write(lxml.html.tostring(tree, pretty_print=True))
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Annotate NCSR document. Inserts annotation in form of "soo_label=X" into the HTML document using synonymlist-based classification.')
    parser.add_argument('InputFilename', 
                type=argparse.FileType('r'),
                help='Input file to parse. Must contain marked SoO table ("class=soo_table")')
    parser.add_argument('OutputFilename',
                        nargs='?',
                help='Output file.')
    args=parser.parse_args()
    
    main(args)
