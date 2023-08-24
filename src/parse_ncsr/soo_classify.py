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
from numpy import isnan
import dill

from parse_ncsr_backend.ncsr_table_parsing import parse_ncsr_tables_raw, create_table,\
    load_table_data, get_lxml_from_string
#from parse_ncsr_backend.table_classifier_simple import TableClassifierSimple

from definitions import CRF_SOO_SERIALIZED_FILENAME, NCSR_CLF_ID_NAME
from parse_ncsr_backend.table_classifier_crf_crfsuite import TableClassifierCRF_CRFsuite
from parse_ncsr_backend.classifier_json_ouput import classifier_json_output


INCLUDE_CONFIDENCE_VALUES=True

DEBUG=False

def main(args): 


    # if a saved CRF is available and we are not instructed to train (--train):
    if os.path.isfile(CRF_SOO_SERIALIZED_FILENAME) and not args.train:
        with open(CRF_SOO_SERIALIZED_FILENAME) as f:
            sc = dill.load(f)
    # if no saved CRF is available or we are instructed to train:
    else:  
        sc = TableClassifierCRF_CRFsuite(useDict=False)
        tables=load_table_data('soo_table',reparse=True)
        gt = [t.getGroundTruth() for t in tables]
        sc.fit(tables,gt)
        with open(CRF_SOO_SERIALIZED_FILENAME,'w') as f:
            dill.dump(sc, f)
    if args.train and not args.InputFilename:
        return
    
    s = args.InputFilename.read()
    tree = get_lxml_from_string(s)
    tableData= parse_ncsr_tables_raw(tree, "soo_table")
    tables = create_table(tableData)
    table=tables[0]

    if DEBUG:
        warnings.warn("Only first table will be classified (multiple tables not yet implemented)")
    
    result = sc.predict(table,True)
    predicted = result['prediction']
    confidence = result['confidence']
 
    # round confidence to n=numDigits digits and format as string:
    if not all([x == '' for x in confidence]):
        numDigits=2
        formatString = '{0:.' + str(numDigits) + 'f}'
        confidence = [formatString.format(round(x,numDigits)) for x in confidence]
        
    # Build result:  
    values=table.getNumericValues()
    values=np.transpose(values)
    columnHeaders=table.getNumericHeaders()
    # get IDs from table:
    itemNodes = table.getItemHeaderLinks()
    classification_IDs=None
    if 'data-' + NCSR_CLF_ID_NAME in itemNodes[0].attrib:
        classification_IDs=[x.attrib['data-' + NCSR_CLF_ID_NAME] for x in itemNodes]
    
    
    result=classifier_json_output(predicted, values, confidence, columnHeaders, result['strings'],classification_IDs)

    if args.out:                   
        json.dump(result,args.out,indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Process NCSR report where the SoO table is marked using the css class "soo_table"')
    parser.add_argument('InputFilename', 
                type=argparse.FileType('r'),
                nargs='?',
                help='Input file to parse. Must contain marked SoO table ("class=soo_table")')
    parser.add_argument('--out',
                help='Output file (default=stdout).',
                type=argparse.FileType('w'),
                default=sys.stdout)
    parser.add_argument('--train',
                        action='store_true')
    
    args = parser.parse_args()
    
    main(args)
