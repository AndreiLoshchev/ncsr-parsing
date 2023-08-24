'''
Created on 30.11.2016

@author: michael
'''

import numpy as np


from pystruct.learners import FrankWolfeSSVM
from pystruct.models import GraphCRF
from pystruct.models import ChainCRF
from pystruct.learners import SubgradientSSVM
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

from parse_ncsr.stemming_vectorizer import getVectorizer
from scipy.sparse import hstack 
from parse_ncsr.table_classifier import TableClassifier
from parse_ncsr.soo_train_data_synonymList import get_train_data_synonym_list


# For testing:
USE_ADDITIONAL_FEATURES=True

class TableClassifierCRF (TableClassifier):
    
    def __init__(self, useDict=False, tableClass='soo_table'):
        self.useDict=useDict
        self.tableClass=tableClass
    
        
    def fit(self, tables, GTs):
        '''Train CRF classifier on given data. 
        If useDict==True, data from the SOO dictionary is used in addition
        for the Vectorizer'''
        
        self.vect = getVectorizer()
        
        self.model=ChainCRF()
        #self.model=GraphCRF(directed=True, inference_method="max-product")
        
       
        
        self.ssvm = FrankWolfeSSVM(model=self.model, C=10, max_iter=100)
        
        numTables=len(tables)
        
        features = [t.extractFeatures() for t in tables]

        X_words = np.zeros([numTables],dtype=object)
        for i in range(len(tables)):
            X_words[i] = np.array(features[i]['words'])

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
            
        self.vect.fit(np.concatenate(X_words))
  
  
        
        # single out GT items
        tablesGroundTruth = np.zeros([numTables], dtype=object)
        gt = [x.getGroundTruth() for x in tables]
        for i in range(len(tables)):
            tablesGroundTruth[i]=['undefined' if x==None else x[0] for x in gt[i]]
        self.target_names=np.unique(np.concatenate(tablesGroundTruth))
        self.targets=range(len(self.target_names))
        
        self.gt_key_to_numeric={key:val for key,val in zip(self.target_names,self.targets)}
        
        tablesGroundTruth_numeric=np.zeros_like(tablesGroundTruth)
        for i,item in enumerate(tablesGroundTruth):
            tablesGroundTruth_numeric[i]=(np.array([self.gt_key_to_numeric[x] for x in tablesGroundTruth[i]]))
        
        X = self.processData(tables)   
        
        self.ssvm.fit(X, tablesGroundTruth_numeric)
        
#         This doesn't work due to a mismatch of states in the SSVM:
#         parms=[{ 'C': [0.001, 0.01, 0.1, 1, 10], 'max_iter':[10, 50, 100]}]
#         grid = GridSearchCV(estimator=FrankWolfeSSVM(model=ChainCRF()),param_grid=parms)
#         print(len(np.unique(np.concatenate(tablesGroundTruth_numeric))))
#         grid.fit(X,tablesGroundTruth_numeric)
#         print(grid)
#         print(grid.best_score_)
#         print(grid.best_estimator_)
         
        
    def processData(self, tables):
        '''Extract _features from tables, use Vectorizer on word _features'''
        
        features = [t.extractFeatures() for t in tables]
        numTables=len(features)
        
        X_features = np.zeros([numTables],dtype=object)
        X_words = np.zeros([numTables],dtype=object)
        
        for i in range(len(tables)):
            X_features[i]=tables[i]._features
        
        # create vectorizer dictionary    
        
        # fit classifier to train data
        for i in range(len(X_words)):
            #X_words[i]=self.vect.transform(X_words[i])
            X_words[i]=self.vect.transform(features[i]['words'])
        
        X = np.zeros([numTables], dtype=object)
        
        # For SoO we may use table _features, as orientation is 'vertical'
        # For FH tables, orientation comes in both ways, for now
        # only 'words' _features are used
        if self.tableClass=='soo_table' and USE_ADDITIONAL_FEATURES:
            for i in range(len(X_words)):
                X[i]=hstack((X_features[i],X_words[i])).toarray()
        elif self.tableClass=='fh_table' or not USE_ADDITIONAL_FEATURES:
            for i in range(len(X_words)):
                X[i]=X_words[i].toarray()
        else:
            raise Exception('STH went wrong')
        
        
        return X
        
    def predict(self, tables):
#         
        casted=False
        if not isinstance(tables,list):
            tables = [tables]
            casted=True
        
        X = self.processData(tables)
        predicted = self.ssvm.predict(X)
        subClasses, fillIn = self.predictSubclasses(tables)
        
        predictedTargetNames = [self.target_names[i] for i in predicted]
       
        out =  [zip(x,y) for x,y in zip(predictedTargetNames, subClasses)]       
        if casted:
            out=out[0]
        return out
    
    def getConfidence(self, tables):
        '''Currently returns list with empty entries, as
           confidence values are not implemented ATM'''
        prediction = self.predict(tables)
        
        confidence = ['']*len(prediction)
        
        return confidence
            
