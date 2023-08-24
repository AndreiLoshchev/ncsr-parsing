'''
Created on 28.09.2016

@author: michael
'''


import string
import re

from parse_ncsr.soo_train_data_synonymList import get_train_data_synonym_list
from parse_ncsr.ncsr_table_parsing import load_table_data


def get_train_data_annotated_tables(sectionKeyword,tablesToUseIndices):
    '''Training data for classifier (SoO table) generated from annotated tables'''
    tables=load_table_data("soo_table")
    tables = [tables[i] for i in tablesToUseIndices]
    target_names, train_data = get_train_data_from_tables(sectionKeyword, tables)
    return  target_names, train_data

def get_train_data_from_tables(sectionKeyword, tables):    

    target_names,unused=get_train_data_synonym_list(sectionKeyword)

    train_data_words=[[] for currentGroundTruthItem in target_names]
    train_data_rows=[0]*len(target_names)
    #tables = [tables[tableIndex] for tableIndex in tablesToUseIndices]
    
    count=[0 for x in target_names]
    tableCount=1
    
    for table in tables:
        
        tableCount+=1
        
        
        features = table.extractFeatures()
        items = features['words']
        
        tablesGroundTruth = table.getGroundTruth()
       
        for tableIndex in range(len(tablesGroundTruth)):
            
            currentGroundTruthItem=tablesGroundTruth[tableIndex]
            if currentGroundTruthItem is None:
                continue
            
            try:
                #index = target_names.index(string.lower(currentGroundTruthItem))
                index = target_names.index(currentGroundTruthItem[0])
                # strip items[tableIndex] of notes in parenthesis
                tmp = re.search('(.*)\(.*\)(.*)',items[tableIndex],flags=re.IGNORECASE)
                if not tmp is None:
                    items[tableIndex]=tmp.group(1) + " " + tmp.group(2)
                if not items[tableIndex] in train_data_words[index]:
                    train_data_words[index].append(items[tableIndex])
                    count[index]+=1
                    train_data_rows[index]=features['rows'][tableIndex]
            
            except ValueError:
                pass
                
    
    
    # detect empty entries and remove
    nonEmptyElements=[tableIndex for tableIndex,v in enumerate(train_data_words) if v!=[]]
    
    
    target_names=[target_names[tableIndex] for tableIndex in nonEmptyElements]
    train_data_words=[train_data_words[tableIndex] for tableIndex in nonEmptyElements]
    #train_data_words=[string.join(x) for x in train_data_words] 
    train_data={}
    train_data['words']=train_data_words
    train_data['rows']=[train_data_rows[tableIndex] for tableIndex in nonEmptyElements]
    
            
    return  target_names, train_data      
        

