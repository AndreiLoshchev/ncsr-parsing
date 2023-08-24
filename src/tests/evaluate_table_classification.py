'''
Created on 30.11.2016

@author: michael
'''


import numpy as np
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.model_selection import LeaveOneOut

from definitions import DATA_DIR

from parse_ncsr_backend.ncsr_table_parsing import load_table_data
from parse_ncsr_backend.table_classifier_crf_crfsuite import TableClassifierCRF_CRFsuite
from sklearn_crfsuite import metrics
from sklearn.metrics import classification_report
#from sklearn_crfsuite.metrics import flat_classification_report, flat_f1_score


# Tests to perfom:
DO_SPLIT=False
DO_TEST=False

DO_FIT_ALL=False
DO_SAVE_FIT_ALL_RESULT=True
FIT_ALL_RESULT_SAVENAME='testdata_fit_all.p'

DO_KFOLD=True
DO_SAVE_K_FOLD_RESULT=True
K_FOLD_K = 3    
K_FOLD_RESULT_SAVENAME='testdata_' + str(K_FOLD_K) + '-fold.p'
# leave one out:
DO_LOO = False

testSection=None

table_type='fh_table'#'soo_table'
# table_type='soo_table'
useDictForCRF=False
eval_crf=True
eval_simple=False
# setting for FH tables: 
'''if table_type=='fh_table':
    useDictForCRF=False
    eval_crf=True
    eval_simple=False
# setting for SOO tables (clf_simple not available for FH tables):    
elif table_type=='soo_table':
    useDictForCRF=False
    eval_crf=True
    eval_simple=False'''
    

tables = load_table_data(table_type, reparse=True)
gt=[t.getGroundTruth() for t in tables]
# not all tables are annotated:
annotatedIndices=[]
nonAnnotatedIndices=[]
for i in range(len(gt)):
    tmp = gt[i]
    if all([x[0]=='undefined' for x in tmp]):
        nonAnnotatedIndices.append(i)
    else:
        annotatedIndices.append(i)

print('Number of annotated tables:')
print(len(annotatedIndices))


tables = [tables[i] for i in annotatedIndices]
gt = [gt[i] for i in annotatedIndices]



#clf_simple   = TableClassifierCRF(useDict=useDictForCRF, tableClass=table_type) 
clf_crf   = TableClassifierCRF_CRFsuite(useDict=useDictForCRF, tableClass=table_type)

if DO_TEST:
    if eval_crf:
        print("crf")
        clf_crf.fit(tables,gt)
        print(clf_crf.score(tables,gt,testSection))
 

if DO_SPLIT:
    X_train, X_test, y_train, y_test = train_test_split(tables,gt,test_size=.3,random_state=42)
     
    print('\nSplit test set:')
    
    if eval_crf:
        print('crf')
        clf_crf.fit(X_train, y_train)
        pred = clf_crf.predict(X_test)
        print(clf_crf.score(X_test, y_test,testSection))
         
               
if DO_FIT_ALL:
    
    print('\nFitting with all available data:')

    if eval_crf:    
        print("crf")
        clf_crf.fit(tables,gt)
        print(clf_crf.score(tables,gt,testSection))
        if DO_SAVE_FIT_ALL_RESULT:
            data={}
            result = clf_crf.predict(tables,computeMarginals=True)
            pred = result['prediction']
            proba = result['confidence']
            data['cm_gt']=gt
            data['cm_pred']=pred
            data['cm_proba']=proba
            with open(os.path.join(DATA_DIR,FIT_ALL_RESULT_SAVENAME),'w') as f:
                pickle.dump(data,f)
  
 

# K_FOLD_K-fold cross validation:
if DO_KFOLD:
    binnedErrorDict={}
    
    cm_pred=[]
    cm_gt=[]
    cm_proba=[]
    
    print('\nk-fold validation, ' + '(k=' + str(K_FOLD_K) +')')    
    scores_crf   =[]
    scores_simple=[]
    indices = range(len(tables))
    scores_crf_train=[]
    
    kfold = KFold(n_splits=K_FOLD_K)
    for train,test in kfold.split(indices):
        if eval_crf:
            clf_crf.fit([tables[i] for i in train],[gt[i] for i in train])
            X_test = [tables[i] for i in test]
            y_test = [gt[i] for i in test]
            X_train=[tables[i] for i in train]
            y_train=[gt[i] for i in train]
            scores_crf_train.append(clf_crf.score(X_train,y_train))



            scores_crf.append(clf_crf.score(X_test,y_test))
            result = clf_crf.predict(X_test, computeMarginals=True)
            pred = result['prediction']
            proba = result['confidence']
            cm_gt.extend(y_test)
            cm_pred.extend(pred)
            cm_proba.extend(proba)
            
 
    if eval_crf:
        if DO_SAVE_K_FOLD_RESULT:
            data={}
            data['cm_gt']=cm_gt
            data['cm_pred']=cm_pred
            data['cm_proba']=cm_proba
            with open(os.path.join(DATA_DIR,K_FOLD_RESULT_SAVENAME),'w') as f:
                pickle.dump(data,f)
             
        print('crf test:')         
        print(np.mean(scores_crf))
        print('crf train:')
        print(np.mean(scores_crf_train))

        '''from sklearn.metrics import f1_score
        target_names = cm_gt #['undefined','Net Expenses Before Indirect','Net Expenses After Indirect','Net Investment Income','Portfolio Turnover Rate']
        from sklearn.preprocessing import MultiLabelBinarizer
        y_true=MultiLabelBinarizer().fit_transform(cm_gt)
        y_pred=MultiLabelBinarizer().fit_transform(cm_pred)
        print(classification_report(y_true, y_pred))'''
        #print(flat_f1_score(cm_gt, cm_pred))
        #report = flat_classification_report(cm_gt, cm_pred, labels=None)
        #print(report)
     
 
  
    if eval_simple:   
        print('simple:')
        print(np.mean(scores_simple))
        
# # leave-one-out test
if DO_LOO:
    print("\nLeave-one-out test:")
    scores_crf   =[]
    scores_simple=[]
    indices = range(len(tables))
    
    loo = LeaveOneOut()
    for train,test in loo.split(indices):
        if eval_crf:
            clf_crf.fit([tables[i] for i in train],[gt[i] for i in train])
            scores_crf.append(clf_crf.score([tables[i] for i in test],[gt[i] for i in test]))
            
         
    if eval_crf:
        print('crf:')         
        print(np.mean(scores_crf))
    if eval_simple:
        print('simple:')
        print(np.mean(scores_simple)) 
 