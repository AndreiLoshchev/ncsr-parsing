'''
Created on 16.01.2017

@author: michael


 
'''
import os
import re

import numpy as np
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer

from parse_ncsr_backend.ncsr_table_parsing import parse_ncsr_tables_raw,\
    create_table, parse_ncsr_tables_raw_tag, load_table_data
#from parse_ncsr_backend.Financial_highlights_dict import numItemsPerHeader_currentDoc

from definitions import TESTDATA_DIR

pattern_num = re.compile('[0-9]*[.,][0-9]+|[0-9]+?')


stemmer=PorterStemmer()
tokenizer=RegexpTokenizer(r'\w+')


# FH current_table:
# horizontally split, meaning the split part is a continuation to the right side:
split_horizontally_fh_tables_filenames=['NCSR_225400_ANNUAL_119312514457852_GS-Large-Cap-Growth-Insights-annotated.html',
                           'NCSR_234580_ANNUAL_119312514457852_GS-Intl-Small-Cap-annotated.html','NCSR_769162_ANNUAL_119312514457852_GS-BRIC-annotated.html',
                              ]


# repetition of same table format, just for different funds:
split_fund_wise_fh_tables_filesnames=['6-annotated.html', '7-annotated.html','8-annotated.html','9-annotated.html','10-annotated.html',
                                      'NCSR_160140_ANNUAL_119312514425343_Wells-Fgo-Idx-Ast-Alloc-annotated.html',
                                      'NCSR_776177_ANNUAL_5193114001429_American-TxEx-Preservation-Port-annotated.html',
                                      'NCSR_776946_ANNUAL_5193114001428_American-College-2015-annotated.html','NCSR_776951_ANNUAL_5193114001428_American-College-2030-annotated.html']


# docs contained repeated, horizontally split FH current_table:
split_both_fh_tables_filenames =['5-annotated.html']




def determineNumberOfNumericLines(table):
    '''Find the number of numeric values given per item, e.g., for
    row header a      1.0    2.0
    row header b      2.0    1.0
    row header c    123    223
    
    the number of values per item is 2.
    '''
    numArray = table[0].getNumericValues()
    
    maxNums = 0
    for i in range(numArray.shape[1]):
        numItemsPerHeader_currentDoc = np.count_nonzero(~np.isnan(numArray[:,i]))
        if numItemsPerHeader_currentDoc>maxNums:
            maxNums=numItemsPerHeader_currentDoc
    
    return maxNums

def findOverlap(a,b):
    ''' Find the percentage of similar items in the item headers of two current_table'''
    
    # get the words only, do stemming:
    tmpa=[[stemmer.stem(x.lower()) for x in tokenizer.tokenize(item)] for item in a]
    tmpb=[[stemmer.stem(x.lower()) for x in tokenizer.tokenize(item)] for item in b]

    # remove empty items
    tmpa = [[x for x in item if x.strip() != ""] for item in tmpa]
    tmpa = [" ".join(x) for x in tmpa if x != []]
    
    tmpb = [[x for x in item if x.strip() != ""] for item in tmpb]
    tmpb = [" ".join(x) for x in tmpb if x != []]

    
    # count equal items
    # TODO: Use word frequencies
    count=0
    for item in tmpa:
        if item in tmpb:
            count+=1
            
    return(float(count)/len(tmpa))
    
    

def find_split_table(filename):
    # TODO: make interface of this function usefull
    
    LOOK_AHEAD = 20
    DEBUG=False
    tableType='fh_table'
    
    # determine the first FH table and the tables following it:
    # TODO: adapt to lxml
    soup = read_html(os.path.join(TESTDATA_DIR, filename))
    fhtables_tags = soup.find_all("table",class_=tableType)
    followingTables_tags = fhtables_tags[0].find_all_next("table")
    fhtables = create_table(parse_ncsr_tables_raw_tag(fhtables_tags[0], "fh_table"))
       
    # for the following tables:
    # check if 
    #     a) the numeric items per header are the same
    #     b) header items do not overlap
    detectedTableIndex=-1
    numItemsPerHeader_firstDoc=determineNumberOfNumericLines(fhtables)
    for i,table_tags in enumerate(followingTables_tags[0:LOOK_AHEAD]):
        current_data = parse_ncsr_tables_raw_tag(table_tags, "fh_table")
        current_table = create_table(current_data)
        
        try:
            if DEBUG:
                print(i)
            # may fail if table can't be parsed 
            numItemsPerHeader_currentDoc= determineNumberOfNumericLines(current_table)
            overlap=findOverlap(fhtables[0].getItemHeaders(), current_table[0].getItemHeaders())
            if DEBUG:
                print(overlap)
                if overlap==0.0:
                    print(fhtables[0].getItemHeaders())
                    print(current_table[0].getItemHeaders())
                    print(numItemsPerHeader_firstDoc)
                    print(numItemsPerHeader_currentDoc)
            if (numItemsPerHeader_firstDoc==numItemsPerHeader_currentDoc) and overlap==0.0:
                detectedTableIndex=i
        except Exception:
            pass

    
    resultTable=None
    if detectedTableIndex>-1:
        data = parse_ncsr_tables_raw_tag(followingTables_tags[detectedTableIndex], "fh_table")
        resultTable = create_table(data)
    return detectedTableIndex,resultTable 
   
# end of function definitions





if True:  
    # Test find_split_table() for all files. The first
    # three do contain a split table
    print('Find split table test:')
    # TODO: define and check GT for all tables
    #     gt=[5, 5, 5,
    #         -1, -1, -1, 9, -1, -1, -1]      
    allFiles = []
    allFiles.extend(split_horizontally_fh_tables_filenames)
    allFiles.extend(split_fund_wise_fh_tables_filesnames)
    allFiles.extend(split_both_fh_tables_filenames)
    
    for filename in allFiles:
        index, resultTable =find_split_table(filename)
        if index > -1:
            print(filename)
            print('Continued table at position #' + str(index))
            print('-----')
            #print(resultTable[0].getItemHeaders())
            
#find_split_table('9-annotated.html')        
    
# Test "overlap" function:
if False:
    print('\nTesting function overlap()')
    current_table = load_table_data("fh_table", reparse=False)
    for i in range(len(current_table)-1):
    
        overlap=findOverlap(current_table[i].getItemHeaders(),current_table[i+1].getItemHeaders())
        print(overlap)
        if overlap==0.0:
            print(current_table[i].getItemHeaders())
            print(current_table[i+1].getItemHeaders())
     
     
    print('Control:')
    print(findOverlap(current_table[1].getItemHeaders(),current_table[1].getItemHeaders()))
