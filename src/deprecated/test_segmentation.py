'''
Created on 27.09.2016

@author: michael
'''

 
from tabulate import tabulate
 
from parse_ncsr.ncsr_table_parsing import load_table_data
from parse_ncsr.soo_segmenter_heuristic import segment_soo_table


# Load parsed tables if available, parse if they're not:
tables=load_table_data("soo_table", reparse=False)



index = 4

[section_names,section_indices]=segment_soo_table(tables[index])

tables[index].printTable()

for i in range(len(section_indices)):
    item = section_indices[i]
    print('----- Item: ' + section_names[i]+'-------------')
    print(tabulate(tables[index].data[item[0]:item[1],:]))





