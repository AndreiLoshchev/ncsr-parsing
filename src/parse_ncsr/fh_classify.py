'''
Created on 18.10.2016

@author: michael
'''

import sys
import argparse
import json
import warnings
import os

import numpy as np
import dill
import dateutil.parser as timeStringParser

from parse_ncsr_backend.ncsr_table_parsing import parse_ncsr_tables_raw, create_table,\
    load_table_data, get_lxml_from_string, parse_ncsr_tables_raw_tag

from definitions import CRF_FH_SERIALIZED_FILENAME, NCSR_CLF_ID_NAME

from parse_ncsr_backend.table_classifier_crf_crfsuite import TableClassifierCRF_CRFsuite
from parse_ncsr_backend.classifier_json_ouput import classifier_json_output



DEBUG=False

def main(args): 
    
    output = classify(args.InputFilename, args.train_crf)
    if args.out:                   
        json.dump(output,args.out,indent=4)
    


def classify(inputFile, train=False):
        # if a saved CRF is available and we are not instructed to train (--train_crf):
    if os.path.isfile(CRF_FH_SERIALIZED_FILENAME) and not train:
        with open(CRF_FH_SERIALIZED_FILENAME) as f:
            sc = dill.load(f)
    # if no saved CRF is available or we are instructed to train:
    else:
        if DEBUG:
            print('Training classifier')  
        sc = TableClassifierCRF_CRFsuite(useDict=False, tableClass='fh_table')
        tables=load_table_data('fh_table',reparse=True)
        gt = [t.getGroundTruth() for t in tables]
        
        # separate out annotated tables:
        annotatedTables=[]
        gtForAnnotatedTables=[]
        for i in range(len(tables)):
            if any([True if x[0]!='undefined' else False for x in gt[i] ]):
                annotatedTables.append(tables[i])
                gtForAnnotatedTables.append(gt[i])
        
        sc.fit(annotatedTables,gtForAnnotatedTables)
        with open(CRF_FH_SERIALIZED_FILENAME,'w') as f:
            dill.dump(sc, f)
    
    if train:
        return
    
    s = inputFile.read()
    tree = get_lxml_from_string(s)
    
    all_FH_tables=tree.xpath('.//table[starts-with(@class,"fh_table")]')
    #print(all_FH_tables)
    #results=[]
    #for i in range(len(all_FH_tables)):
    if len(all_FH_tables)>=2 and "fh_table" in all_FH_tables[0].classes and "fh_table_cont" in all_FH_tables[1].classes:
        #print('Merging fh_table and fh_table_cont')
        data        = parse_ncsr_tables_raw_tag(all_FH_tables[0], "fh_table")
        data_cont   = parse_ncsr_tables_raw_tag(all_FH_tables[1], "fh_table_cont")
        tables      = create_table(data)
        tables_cont = create_table(data_cont)
        table=tables[0].mergeTable(tables_cont[0],'right')

        
        '''if tables[0].getOrientation()=='horizontal' and tables_cont[0].getOrientation()=='horizontal':
            table = tables[0].mergeTable(tables_cont[0],'right')
        else:
            raise Exception('Merging of these tables not implemented ATM')'''
    else:
        tableData= parse_ncsr_tables_raw(all_FH_tables[0], "fh_table")
        tables = create_table(tableData)#changing this parameter we can classify each existing table in document (not only the first one)
        table=tables[0]
        
        
        
    if DEBUG:
        warnings.warn("Only first table will be classified (multiple tables not yet implemented)")
    
    result = sc.predict(table, computeMarginals=True)
    predicted = result['prediction']
    marginals = result['confidence'] 
    # round confidence to n=numDigits digits and format as string:
    if not all([x == '' for x in marginals]):
        numDigits=2
        formatString = '{0:.' + str(numDigits) + 'f}'
        confidence = [formatString.format(round(x,numDigits)) for x in marginals]
        
    # Build result:  
    values=table.getNumericValues()
    values=np.transpose(values)
    columnHeaders=table.getNumericHeaders()
    
    
    # get classification IDs if they are there:
    itemNodes = table.getItemHeaderLinks()
    classification_IDs=None
    if 'data-' + NCSR_CLF_ID_NAME in itemNodes[0].attrib:
        classification_IDs=[]
        for x in itemNodes:
            attrib=''
            attrib=x.attrib['data-' + NCSR_CLF_ID_NAME]
            
            
#             try:
#                 attrib=x.attrib['data-' + NCSR_CLF_ID_NAME]
#             except:
#                 attrib=''
#             classification_IDs.append(attrib)
#     
    # TODO: if 'show only last year':
#     dates =[]
#     for item in columnHeaders:
#         item = re.sub('ended','',re.sub('Year','',item))
#         print(item)
#         dates.append(timeStringParser.parse(item))
#     print(dates)
    result = classifier_json_output(predicted, values, confidence, columnHeaders, result['strings'], classification_IDs)
    #results.append(result)

    
    
    return result

    
if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description='Process NCSR report where the "financial highlights" (FH) table is marked using the css class "fh_table"')
    argparser.add_argument('InputFilename', 
                type=argparse.FileType('r'),
                nargs='?',
                help='Input file to parse. Must contain marked FH table ("class=fh_table")')
    argparser.add_argument('--out',
                help='Output file (default=stdout).',
                type=argparse.FileType('w'),
                nargs='?',
                default=sys.stdout)
    argparser.add_argument('--train_crf',
                        action='store_true')
    
    args = argparser.parse_args()
    
    main(args)
