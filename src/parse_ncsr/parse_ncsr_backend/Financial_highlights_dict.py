'''
Created on 28.11.2016

@author: michael
'''

import os
import json

from definitions import DATA_DIR


FH_table=[
#           ('Net asset value (beginning)',1,'','d'),
#           ('Net asset value (end)',1,'','d'),
#           ('Income from:',1,'','h'),
#           ('Net investment income',2,'','d'),
#           ('Net realized and unrealized gain',2,'','d'),
#           ('Total',2,'','a'),
          ('undefined',1,'','u'),
          ('empty',1,'','e'),
          #('Ratios to average net assets',1,'','h'),
          ('Net Expenses Before Indirect',1,'','d'),
          ('Net Expenses After Indirect',1,'','d'),
          ('Net Investment Income',1,'','d'),
          ('Portfolio Turnover Rate',1,'','d')
          
    
    ]


with open(os.path.join(DATA_DIR, "fh_items.json"), 'wb') as f:
    # filter out type label for annotator.js:
    FH_table_mod=[x[0:2] for x in FH_table]
    json.dump(FH_table_mod, f,  sort_keys=False)
    #json.dump(SOO_table, f, indent=3, sort_keys=False)

keyToVal={}
key=["","",""]
for item in FH_table: 
        #item = SOO_table[i];
        key[item[1]-1]=item[0];
        for gtIndex in range(item[1],len(key)):
                key[gtIndex]="";
        tmp=key[0];
        for gtIndex in range(1,len(key)):
                if key[gtIndex]!="":
                        tmp+='//' + key[gtIndex];
                else:
                        break
        
        keyToVal[tmp]=item[3]

keyToVal['undefined']='u'  