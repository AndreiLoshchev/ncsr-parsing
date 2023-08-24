'''
Created on 07.02.2017

@author: mf
'''
from parse_ncsr_backend.ncsr_table_parsing import load_table_data
from parse_ncsr_backend.table_classifier_crf_crfsuite import TableClassifierCRF_CRFsuite
import scipy.stats

import numpy as np

from sklearn.metrics.scorer import make_scorer
 
from sklearn.model_selection import GridSearchCV
from sklearn_crfsuite import metrics


# setup input data
useDictForCRF=True
table_type="soo_table"
tables = load_table_data(table_type, reparse=False)
gt=[t.getGroundTruth() for t in tables]

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


# setup classifier:
clf_crf   = TableClassifierCRF_CRFsuite(useDict=useDictForCRF, tableClass=table_type)

# fit once to get Vectorizer etc. properly initialized:
clf_crf.fit(tables,gt)

# convert inputs so they can be used by CRF directly:
X_word,X_feat = clf_crf.processData(tables)
gt_numeric, gt_strings = clf_crf._keysToNumeric(gt)
X_train, y_train = clf_crf._convertToCRFsuiteItem(X_word, X_feat, gt_numeric)



# grid search setup:
params_space={
       'c1':np.linspace(0,.1,5),
       'c2':np.linspace(0,.01,5)
#     'c1': scipy.stats.expon(scale=0.5),
#     'c2': scipy.stats.expon(scale=0.05),
}
 
prec_scorer=make_scorer(metrics.flat_precision_score, average='micro')
 
crf = clf_crf.crf
  
print('fitting')
rs = GridSearchCV(crf,params_space,cv=5,verbose=3,n_jobs=4,scoring=prec_scorer)
 
 
rs.fit(X_train,y_train)
print('best params:', rs.best_params_)
print('best CV score:', rs.best_score_)
print('model size: {:0.2f}M'.format(rs.best_estimator_.size_ / 1000000))