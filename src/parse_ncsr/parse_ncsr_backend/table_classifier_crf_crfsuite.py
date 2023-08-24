'''
Created on 30.11.2016

@author: michael
'''

import numpy as np
import os
import sys
import dill
from time import time
 

from sklearn_crfsuite import CRF
from parse_ncsr_backend.stemming_vectorizer import getVectorizer1
from parse_ncsr_backend.table_classifier import TableClassifier
from parse_ncsr_backend.soo_train_data_synonymList import get_train_data_synonym_list

from definitions import DATA_DIR

# For testing:
USE_ADDITIONAL_FEATURES=True

# number of preceeding and following table 
# rows to consider in classification:
LOOK_BACK=1
LOOK_AHEAD=1

SAVE_TRAINDATA=False


class TableClassifierCRF_CRFsuite (TableClassifier):
    
    def __init__(self, useDict=False, tableClass='soo_table'):
        self.useDict=useDict
        self.tableClass=tableClass
        self.gt_key_to_numeric = None
        
    def fit(self, tables, GTs, parms=None, tableClass=None):
        '''Train CRF classifier on given data. 
        If useDict==True, data from the SOO dictionary is used in addition
        for the Vectorizer'''
        t0 = time()
        self.vect = getVectorizer1()
        
        
        # check to exclude non-annotated tables:
        print('Tables in: ' + str(len(tables)))
        indices = range(len(tables))
        for i in range(len(GTs)):
            if all([x[0]=='undefined' for x in GTs[i]]):
                indices.remove(i)
        tables=[tables[i] for i in indices]
        GTs   =[GTs[i]     for i in indices]
        numTables=len(tables)
        print('Tables annotated: ' + str(len(indices)))
        
        features = [t.extractFeatures() for t in tables]
        X_words = [] 
        for i in range(len(tables)):
            X_words.append(np.array(features[i]['words']))
        del features
        
        if self.useDict:
            allTrainData=[]
            [target_names,train_data]=get_train_data_synonym_list('expense')
            allTrainData.extend(train_data['words'])
            [target_names,train_data]=get_train_data_synonym_list('income')
            allTrainData.extend(train_data['words'])
            [target_names,train_data]=get_train_data_synonym_list('gainloss')
            allTrainData.extend(train_data['words'])
            allTrainData=np.array(allTrainData,dtype=object)

            X_words=np.concatenate((X_words,allTrainData))

            
        
        #stop_words = frozenset(["of ", " and ","by","as a","to"])

        self.vect.fit(np.concatenate(X_words))
        gt = [x.getGroundTruth() for x in tables]
        tablesGroundTruth_numeric, tablesGroundTruth = self._keysToNumeric(gt)
        del gt
        X_words,X_feat, strings = self.processData(tables)
        
        del tables
        

        '''if self.tableClass=='fh_table':
            X_feat=np.array(X_feat1*2)
        else:
            X_feat=X_feat1'''

        if parms==None:
           print('parms are none')
           self.crf = CRF(algorithm='lbfgs', c1=0.1,
                           c2=0.1,
                           max_iterations=100,
                           all_possible_transitions=True)
 
           #self.crf = CRF(algorithm='lbfgs', c1=0.025,
           #                c2=0.01,
           #                max_iterations=100,
           #                all_possible_transitions=True)
 
           #from sklearn.linear_model import SGDClassifier
           #self.crf = SGDClassifier(loss="hinge", penalty="l2", max_iter=5)
            #import scipy.stats
            #from sklearn.metrics import make_scorer
            #from sklearn.cross_validation import cross_val_score
            #from sklearn.model_selection import RandomizedSearchCV
            #from sklearn_crfsuite import metrics

            #crf = CRF(algorithm='ap',all_possible_transitions=True)
            #params_space = {'max_iterations': scipy.stats.expon(scale=0.5),}
            #f1_scorer = make_scorer(metrics.flat_f1_score,average='weighted', labels=None)
            #self.crf = RandomizedSearchCV(crf, params_space,cv=3,verbose=1,n_jobs=-1,n_iter=50,scoring=f1_scorer)
            #self.crf.fit(X,y)
            #print('best params:', self.crf.best_params_)
            #print('best CV score:', self.crf.best_score_)


        t1=time()
        print('Prefit ' + str(t1-t0))
        
        t0=time()
        self.crf.fit(self._genconvertToCRFsuiteItem(X_words,X_feat),self.ygen(tablesGroundTruth_numeric))
        t1=time()
        print('Fit ' + str(t1-t0))
      

    def _keysToNumeric(self, gt):
        tablesGroundTruth = np.zeros([len(gt)], dtype=object)
        for i in range(len(gt)):
            tablesGroundTruth[i]=['undefined' if x==None else x[0] for x in gt[i]]
        
        tablesGroundTruth_numeric=np.zeros_like(tablesGroundTruth)    
        
        #if self.gt_key_to_numeric is None:
        self.target_names=np.unique(np.concatenate(tablesGroundTruth))
        self.targets=range(len(self.target_names))
        self.gt_key_to_numeric={key:val for key,val in zip(self.target_names,self.targets)}
           
        for i,item in enumerate(tablesGroundTruth):
            tablesGroundTruth_numeric[i]=(np.array([self.gt_key_to_numeric[x] for x in tablesGroundTruth[i]]))
            
        return tablesGroundTruth_numeric, tablesGroundTruth   
    
    
    def ygen(self,y):
        y_str=[]
        sampleindex=0
        if y is not None:
            while sampleindex<len(y):
                yield y[sampleindex].astype(str)
                sampleindex+=1
                 
    def _genconvertToCRFsuiteItem(self,X_words,X_feat,y=None):
        
        y_str=[]
        if y is not None:
            for sampleIndex in range(len(y)):
                y_str.append(y[sampleIndex].astype(str))
                
        itemSequencesCollection = []

        sampleindex=0
        while sampleindex<len(X_words): 
            X_w = X_words[sampleindex]
            X_f = X_feat[sampleindex]
            
            sequence=[]
 
            for i in range(X_w.shape[0]):
                sample={}
                for j in range(X_w.shape[1]):
                    key='w'+str(j)
                    sample[key]=X_w[i,j]
                
                if self.tableClass=='soo_table':
                    for j in range(X_f.shape[1]):
                        key='f'+str(j)
                        sample[key]=X_f[i,j]
                '''if self.tableClass=='fh_table':
                    for j in range(X_feat[sampleIndex].shape[1]):
                        key='f'+str(j)
                        sample[key]=X_feat[sampleIndex][i,j]'''
                    
                # "look-back"
                for look_back in range(1,LOOK_BACK+1):
                    if i>(look_back-1):
                        for j in range(X_w.shape[1]):
                            key='-' + str(look_back) + 'w' + str(j)
                            sample[key]=X_w[i-look_back,j]
                            
                # "look-ahead"            
                for look_ahead in range(1,LOOK_AHEAD+1):
                    if i<X_w.shape[0]-look_ahead:
                        for j in range(X_w.shape[1]):
                            key='+' + str(look_ahead) + 'w' + str(j)
                            sample[key]=X_w[i+look_ahead,j]
                sequence.append(sample)

            yield sequence 
            sampleindex+=1



    def processData(self, tables):

        '''Extract _features from tables, use Vectorizer on word _features'''
        
        features = [t.extractFeatures() for t in tables]

        numTables=len(features)
        X_features=[] 
        X_words=[] 
        
        for i in range(len(tables)):
            X_features.append(tables[i]._features)
        
        
        # fit classifier to train data
        for i in range(numTables):
            X_words.append(self.vect.transform(features[i]['words']))
  
        strings=[x['words'] for x in features]
  
        return X_words,X_features, strings

        
    def predict(self, tables, computeMarginals=False):
        
        casted=False
        if not isinstance(tables,list):
            tables = [tables]
            casted=True
        
        X_words,X_feat, strings = self.processData(tables)

        X = [x for x in self._genconvertToCRFsuiteItem(X_words,X_feat)]
        
        predicted=self.crf.predict(X)
        confidence=[]
        if computeMarginals:
            marginals=self.crf.predict_marginals(X)
            for i, item in enumerate(predicted):
                confidence_tmp=[]
                for j, val in enumerate(item):
                    d = marginals[i][j]
                    confidence_tmp.append(d[val])
                confidence.append(confidence_tmp)
                          
        subClasses, fillIn = self.predictSubclasses(tables)
 
        predictedTargetNames =[[self.target_names[int(i)] for i in x] for x in predicted]  
       
        out =  [zip(x,y) for x,y in zip(predictedTargetNames, subClasses)]       
        if casted:
            out=out[0]
            if computeMarginals:
                confidence=confidence[0]
        result={}
        result['prediction']=out
        result['confidence']=confidence
        result['strings']=strings[0]
        
        return result
            
