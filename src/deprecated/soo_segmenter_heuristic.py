'''
Created on 21.09.2016
Segment the 'Statement of operations' table.
Currently only the 'expenses' section is segmented (via a simple heuristic)
@author: michael.fieseler@gmail.com
'''

import re
import numpy as np

def segment_soo_table(table):
     
    section_names=['income', 'expense','gainloss']
    section_indices=[] 
     
    # try to guess the expenses section:
    # a) find cells which contain 'expene'

    patternExpense = re.compile('expense', flags=re.IGNORECASE)
    patternIncome = re.compile('income', flags=re.IGNORECASE)
    patternGainsLosses = re.compile('realized and unrealized gain',flags=re.IGNORECASE)
    patternGainsLosses2 = re.compile('realized.*and.*unrealized appreciation.*',flags=re.IGNORECASE)
    position_expense=[]
    position_income=[]
    position_gainsLosses=[]
    position_gainsLosses2=[]
    position_empty_above=[]
    
    
    
#     if len(table.getItemHeaders())>1:
#         raise RuntimeError('Several columns with row headers not implemented')
    for tableIndex,item in enumerate(table.getItemHeaders()):
        
        out = patternExpense.search(item)
        if not out is None:
            position_expense.append(tableIndex)
           
        out = patternIncome.search(item)
        if not out is None:
            position_income.append(tableIndex)    
            
        out = patternGainsLosses.search(item)
        if not out is None:
            position_gainsLosses.append(tableIndex)
        out = patternGainsLosses2.search(item)
        if not out is None:
            position_gainsLosses2.append(tableIndex)
            #print('match')
    
    
        
    #print(position_gainsLosses)
    # b) determine consecutive lines (non-interrupted series
    # of non-empty rows)  
    # For numbers in 'consecutive_lines' it holds that
    # consecutive_lines[tableIndex]>0 if a block of rows with no blank lines
    # starts here, and consecutive_lines[tableIndex] gives the size of that block
    #
    # NOTE: this will miss offset lines at the end of the section
    consecutive_lines=np.zeros(len(table.getItemHeaders()))
    for tableIndex,item in enumerate(table.getItemHeaders()):
        if not item=='':
            consecutive_lines[tableIndex]=1;
    
    count=0
  
    counter=np.zeros(len(consecutive_lines))
    # iterate backwards, count number of consecutive lines
    # starting in each row (consecutive_lines[tableIndex]==n "including this line, n
    # consecutive rows follow"):
    for tableIndex in reversed(range(len(consecutive_lines))):
        if consecutive_lines[tableIndex]>0:
            count+=1
            counter[tableIndex]=count
        else:
            count=0
        
    consecutive_lines=counter;
    #print(consecutive_lines)
    # c) has empty line above
    for tableIndex, item in enumerate(table.getItemHeaders()):
        if (tableIndex-1)>=0 and item=='':
            position_empty_above.append(tableIndex)
      
    
    
    # expense
    best=consecutive_lines[position_expense].argmax()
    expense_start_index=int(position_expense[best])
    
    # income
    tmp = [x for x in position_income if x < expense_start_index]
    best=consecutive_lines[tmp].argmax()
    
    income_start_index=int(position_income[best])
    income_end_index= expense_start_index-1
    
    # gains / lossesprint
    if len(position_gainsLosses)==0:
        position_gainsLosses=position_gainsLosses2
    best=consecutive_lines[position_gainsLosses].argmax()
    gainsLosses_start_index=int(position_gainsLosses[best])
    gainsLosses_end_index=len(table.getItemHeaders())
    expense_end_index= gainsLosses_start_index-1
           
    section_indices.append([income_start_index,income_end_index])   
    section_indices.append([expense_start_index,expense_end_index])
    section_indices.append([gainsLosses_start_index,gainsLosses_end_index])
    
    return(section_names,section_indices)
     