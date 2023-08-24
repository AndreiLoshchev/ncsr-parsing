'''
Created on 28.09.2016

@author: michael
'''
from __future__ import print_function
import json
import os
from definitions import DATA_DIR
from definitions import SOO_EXPENSE_SYNOYMS_FILENAME
from definitions import SOO_INCOME_SYNOYMS_FILENAME
from definitions import SOO_GAINLOSS_SYNONYMS_FILENAME
from parse_ncsr_backend.SOO_table_dict import SOO_table


''' Returns target_names and synonym lists for the respective sections '''
def get_train_data_synonym_list(sectionKeyword):
    
    filenames={'expense': os.path.join(DATA_DIR,SOO_EXPENSE_SYNOYMS_FILENAME),
               'income' : os.path.join(DATA_DIR,SOO_INCOME_SYNOYMS_FILENAME),
               'gainloss': os.path.join(DATA_DIR,SOO_GAINLOSS_SYNONYMS_FILENAME)}
    
    dict_keywords={'expense':'Expense','income':'Income',
                    'gainloss':'Realized and unrealized gain from investments'}  
    filename = filenames[sectionKeyword]
    with open(os.path.join(DATA_DIR,filename)) as f:
        data = json.load(f);
    
    # Build full keys (e.g. "Income//Dividends") from keys:
    full_keys=[];
    full_keys.append('undefined');
    key=["","",""];
    for tableIndex in range(len(SOO_table)):
        item = SOO_table[tableIndex];
        key[item[1]-1]=item[0];
        for gtIndex in range(item[1],len(key)):
            key[gtIndex]="";
        tmp=key[0];
        for gtIndex in range(1,len(key)):
            if key[gtIndex]!="":
                tmp+='//' + key[gtIndex]
            else:
                break;
        
        full_keys.append(tmp);
    
    
    SOO_CLASSES = [x for x in full_keys if x.find(dict_keywords[sectionKeyword])==0]    
    SOO_SYNONYMS=[];
    
    
    synonymKeys = [x[0] for x in data]
    
    for item in SOO_CLASSES:
        key = item.split('//')[-1];
        index = synonymKeys.index(key);
        SOO_SYNONYMS.append(data[index][1:])
        
    # derive structure (which items are headings [items which contain subitems])
    SOO_STRUCTURE_RAW = map(lambda x: len(x.split('//')),SOO_CLASSES)
    SOO_STRUCTURE=[0]*len(SOO_STRUCTURE_RAW)   
    for tableIndex in range(len(SOO_STRUCTURE_RAW)-1):
        if SOO_STRUCTURE_RAW[tableIndex]<SOO_STRUCTURE_RAW[tableIndex+1]:
            SOO_STRUCTURE[tableIndex]=1
        else:
            SOO_STRUCTURE[tableIndex]=0
    SOO_STRUCTURE[-1]=0
    train_data={}
    train_data['rows']=SOO_STRUCTURE
    train_data['words']=SOO_SYNONYMS

    return SOO_CLASSES, train_data


''' Print the classes used for annotation '''
def main():
    print("'undefined', ")
    for filename in ['income','expense','gainloss']:
        target_names, stuff = get_train_data_synonym_list(filename)
        for tableIndex in range(len(target_names)):
            if tableIndex==0:
                print("'---" + target_names[tableIndex] + "---', ")
            else:
                if (tableIndex+1)%3==0:
                    print("'" + target_names[tableIndex] + "', ")
                else:
                    print("'" + target_names[tableIndex] + "', ", end='')
             
if __name__ == "__main__": main()   

