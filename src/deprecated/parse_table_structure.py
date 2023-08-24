'''
Created on 23.11.2016

@author: michael.fieseler@gmail.com
'''

import numpy as np
from pystruct.models import ChainCRF
from pystruct.learners import FrankWolfeSSVM
from sklearn.cross_validation import train_test_split
from sklearn.metrics.classification import confusion_matrix

from parse_ncsr.ncsr_table_parsing import load_table_data
from parse_ncsr.SOO_table_dict import SOO_table, keyToVal

tables = load_table_data("soo_table", reparse=False)

numTables=len(tables)

# 'undefined', 'data', 'header', 'aggregate' (a total)
typeKeys=['u','d','h','a']

X=np.zeros([numTables],dtype=object)
y_gt_row_type=np.zeros([numTables],dtype=object)
y=np.zeros([numTables],dtype=object)
 
for tableIndex,table in enumerate(tables):
    print("table #" + str(tableIndex)) 
    gt = table.getGroundTruth()
    y_tmp=np.zeros([len(gt)],dtype=int)
    for gtIndex, gt_item in enumerate(gt):
        
        if not gt_item:
            gtTypeKey=typeKeys.index('u')
            
        # y_gt_row_type[tableIndex] contains the index of the respective type in 'typeKeys':
        if gt_item:
            if len(gt_item[0])>0:
                gtTypeKey=typeKeys.index(keyToVal[gt_item[0]])
                #y_tmp[gtIndex]=typeKeys.index(keyToVal[gt_item[0]])
                #print((keyToVal[gt_item[0]]))
        y_tmp[gtIndex]=gtTypeKey
#         if gt_item:
#             print(typeKeys[gtTypeKey] + ")" + gt_item[0] )
#         else:
#             print(typeKeys[gtTypeKey] + ")" + 'no gt item ')
    y_gt_row_type[tableIndex]=y_tmp
    
    X[tableIndex]= table._features
#     
for tableIndex in range(len(y_gt_row_type)):
    print(np.bincount(y_gt_row_type[tableIndex]))   
X_train, X_test, y_train, y_test = train_test_split(X,y_gt_row_type,test_size=.3,random_state=42)
  
       
model = ChainCRF()
ssvm = FrankWolfeSSVM(model=model, C=.1, max_iter=10)
   
   
   
   
ssvm.fit(X_train, y_train)
print(ssvm.score(X_test, y_test))
pred=ssvm.predict(X_test)
 
cm = confusion_matrix(np.concatenate(y_test),np.concatenate(pred))
print(cm)
#  
# pred = ssvm.predict(X_test)
#  
# for tableIndex in range(len(y_test)):
#     print('----' + str(tableIndex) + '-------')
#     for gtIndex in range(len(y_test[tableIndex])):
#         print(typeKeys[pred[tableIndex][gtIndex]]+ "/" + typeKeys[y_test[tableIndex][gtIndex]])
#  


