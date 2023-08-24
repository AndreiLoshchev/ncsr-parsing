'''
Created on 30.11.2016

@author: michael
'''
import numpy as np

from parse_ncsr.soo_train_data_synonymList import get_train_data_synonym_list
from parse_ncsr.soo_classifier import SooClassifier
from parse_ncsr.soo_train_data_annotated_tables import get_train_data_annotated_tables,\
    get_train_data_from_tables
from parse_ncsr.soo_segmenter_heuristic import segment_soo_table
import array
from parse_ncsr.table_classifier import TableClassifier


# takes X_train, y_train for training, predicts

# uses SooClassifier on segmented table



class TableClassifierSimple (TableClassifier):
    
    def __init__(self, clfType):
        self.clfType=clfType
    
    def fit(self, X_train, y_train):

        options={}
        options['USE_STEMMING']=True  
            
        self.sc={}
        
        if self.clfType=='dict':
            
            # train classifiers using synonym lists:
            [target_names,train_data]=get_train_data_synonym_list('expense')
            self.sc['expense']=SooClassifier(train_data,target_names,options)
            
            [target_names,train_data]=get_train_data_synonym_list('income')
            self.sc['income']=SooClassifier(train_data,target_names,options)
            
            [target_names,train_data]=get_train_data_synonym_list('gainloss')
            self.sc['gainloss']=SooClassifier(train_data,target_names,options)
            
        elif self.clfType=='learn':
            
            [target_names,train_data]=get_train_data_from_tables('expense',X_train)
            self.sc['expense']=SooClassifier(train_data,target_names,options)
            
            [target_names,train_data]=get_train_data_from_tables('income',X_train)
            self.sc['income']=SooClassifier(train_data,target_names,options)
        
            [target_names,train_data]=get_train_data_from_tables('gainloss',X_train)
            self.sc['gainloss']=SooClassifier(train_data,target_names,options)

            
        
        
    def predict(self, tables, computeMarginals=False):
        casted=False
        if not isinstance(tables,list):
            tables=[tables]
            casted=True
        result=[]
        for t in tables:
            [section_names, section_indices] = segment_soo_table(t)
            
            singleResult=[('undefined')]*len(t.getItemHeaders())
            for i in range(0,3):
                features = t.extractFeatures(section_indices[i][0],section_indices[i][1])
                predicted = self.sc[section_names[i]].predict(features)
                predicted = ['undefined' if x==None else x for x in predicted]
                singleResult[section_indices[i][0]:section_indices[i][1]]=predicted
            result.append(singleResult)    
        
        subClasses, fillIn = self.predictSubclasses(tables)

        if computeMarginals:
            confidence=[]
            
            for t in tables:
                tableConfidence=[]
                [section_names, section_indices] = segment_soo_table(t)
            
            # collect confidence from all three sub-classifiers:
                for i in range(0,3):
                    features = t.extractFeatures(section_indices[i][0],section_indices[i][1])
                    tmp = self.sc[section_names[i]].getClassificationScores(features)
                    tableConfidence.extend(tmp) 
                confidence.append(tableConfidence)
        out = [zip(x,y) for x,y in zip(result, subClasses)]       
        if casted:
            out=out[0]
            if computeMarginals:
                confidence=confidence[0]
        if computeMarginals:
            return out,confidence
        else:
            return out

