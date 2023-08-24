'''
Created on 15.09.2016
Parses the .csv file (exported from Excel) into
a list of lists with synonyms
@author: michael.fieseler@gmail.com
'''


import csv
import json
import string
import os
from definitions import DATA_DIR

filename=os.path.join(DATA_DIR, "Annual Report Line Items Variants.csv")
savename=os.path.join(DATA_DIR, "StatementOfOperations_Synonyms.json")

out=[]
synonymList=[]
with open(filename) as csvfile:
    reader=csv.reader(csvfile,delimiter=',')
    for item in reader:
        #item=string.lower(item)
        # sort into synonymList:
        sublist = [x for x in synonymList if x[0]==string.lower(item[0])]
        if len(sublist) > 0:
            sublist[0].append(string.lower(item[1]))
        else:
            synonymList.append([string.lower(x) for x in item])
        
        out.append(item[::-1])
        

# synonymDict={}
# for item in out:
#     if not string.lower(item[0]) in synonymDict:
#         synonymDict[string.lower(item[0])]=string.lower(item[1])
#     else:
#         print('duplicate')

with open(savename,'w') as f:
    json.dump(synonymList,f);
