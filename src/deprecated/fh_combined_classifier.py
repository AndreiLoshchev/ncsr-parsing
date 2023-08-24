'''
Created on 23.11.2016

@author: michael.fieseler@gmail.com
'''

import numpy as np
from scipy.sparse import hstack 

from sklearn.cross_validation import train_test_split
from sklearn.metrics.classification import confusion_matrix

from parse_ncsr.ncsr_table_parsing import load_table_data
from parse_ncsr.Financial_highlights_dict import FH_table, keyToVal
from sklearn.feature_extraction.text import TfidfVectorizer
from parse_ncsr.stemming_vectorizer import LemmaTokenizer

from pystruct.learners import FrankWolfeSSVM
from pystruct.models import GraphCRF
from pystruct.models import ChainCRF
from pystruct.learners import SubgradientSSVM

tableType="fh_table"
tables = load_table_data("fh_table", reparse=False)

numTables=len(tables)

# 'undefined', 'data', 'header', 'aggregate' (a total)
typeKeys=['u','d','h','a']

X=np.zeros([numTables],dtype=object)
y_gt_row_type=np.zeros([numTables],dtype=object)
 
X_words= np.zeros([numTables],dtype=object)
y_gt   = np.zeros([numTables],dtype=object)
 
for tableIndex,table in enumerate(tables):
    print("table #" + str(tableIndex)) 
    gt = table.getGroundTruth()
    
    # grab _features and type-gt:
    y_tmp=np.zeros([len(gt)],dtype=int)
    for gtIndex, gt_item in enumerate(gt):
        
        if not gt_item:
            gtTypeKey=typeKeys.index('u')
            
        if gt_item:
            if len(gt_item[0])>0:
                gtTypeKey=typeKeys.index(keyToVal[gt_item[0]])
        y_tmp[gtIndex]=gtTypeKey
    # grab words and real gt:
    features = table.extractFeatures()
    X_words[tableIndex]=features['words']
    y_gt[tableIndex]=[None if x==None else x[0] for x in gt]
        
        
        
    
    y_gt_row_type[tableIndex]=y_tmp
    
    X[tableIndex]= table._features

ADD_WORDS=True
if ADD_WORDS:
    # init TfidfVect:
    vect=TfidfVectorizer(tokenizer=LemmaTokenizer())
    vect.fit(np.concatenate(X_words))
    
    # transform words:
    X_trans=np.zeros([numTables],dtype=object)
    for i,item in enumerate(X_words):
        X_trans[i]=vect.transform(X_words[i])
        
    # concatenate table and word _features (X[] and X_trans[])
    for i,item in enumerate(X_words):
        X[i]=hstack((X[i],X_trans[i])).toarray()
        
    # process GT (replace 'None' by undefined:
    y_gt=[map(lambda x:'undefined' if x is None else x,y) for y in y_gt]
    # generate indices:
    y_gt_terms=np.unique(np.concatenate(y_gt))
    y_gt_keys=range(len(y_gt_terms))
    y_dict={key:val for key,val in zip(y_gt_terms,y_gt_keys)}
    
    y_gt_indexed=np.zeros_like(y_gt)
    for i,item in enumerate(y_gt):
        y_gt_indexed[i]=(np.array([y_dict[x] for x in y_gt[i]]))
        

# for tableIndex in range(len(y_gt_row_type)):
#     print(np.bincount(y_gt_row_type[tableIndex]))   
X_train, X_test, y_train, y_test = train_test_split(X,y_gt_indexed,test_size=3,random_state=42)
  
       
model = ChainCRF(inference_method='ad3')
#model = GraphCRF(directed=True,inference_method='max-product')

#ssvm = FrankWolfeSSVM(model=model, C=.1, max_iter=10)
ssvm = SubgradientSSVM(model=model,max_iter=100)
   
   
   
   
ssvm.fit(X_train, y_train)
#ssvm.fit(X_test, y_test)
print(ssvm.score(X_train, y_train))
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


