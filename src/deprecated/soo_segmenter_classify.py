'''
Created on 23.09.2016

@author: michael.fieseler@gmail.com
'''
 
from definitions import DATA_DIR
import re
import numpy as np
import os
import json
import string
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from parse_ncsr.soo_train_data_synonymList import get_train_data_synonym_list
from parse_ncsr.soo_classifier import SooClassifier
from parse_ncsr.stemming_vectorizer import LemmaTokenizer

filename=os.path.join(DATA_DIR,'StatementOfOperations_sectionKeywords.json')
section_names=['Income','Expense','Realized and unrealized gain']

class SooSegementClassify (object):
    
    def __init__(self, useStemming=False):
        self.train_data=[]
        self.targets=[]
        self.target_names=[]
        
        keywords=['income','expense','gainloss']
        for keyword in keywords:
            [target_names,train_data_raw]=get_train_data_synonym_list(keyword)
            train_data_raw = [" ".join(x) for x in train_data_raw['words']]
        
            self.train_data.append(string.join(train_data_raw," "))
            self.target_names.append(keyword)
        
        vect=CountVectorizer(tokenizer=LemmaTokenizer())
        classifier = MultinomialNB(alpha=1e-3)
        self.pipe = Pipeline([('vect',vect),('tfidf',TfidfTransformer()),('classifier',classifier)])
        self.pipe.fit(self.train_data,range(len(self.target_names)))
 

    def segment_soo_table(self,table):
        
        
        sc={}
        options={}
        options['USE_STEMMING']=True    
        [target_names,train_data]=get_train_data_synonym_list('expense')
        sc['expense']=SooClassifier(train_data,target_names,options)
        
        [target_names,train_data]=get_train_data_synonym_list('income')
        sc['income']=SooClassifier(train_data,target_names,options)
        
        [target_names,train_data]=get_train_data_synonym_list('gainloss')
        sc['gainloss']=SooClassifier(train_data,target_names,options)
        
        
        data = table.extractFeatures()

        proba = []
        keywords=['income','expense','gainloss']
        for tableIndex in range(3):
            #proba[:][tableIndex]=
            scores, minScores, maxScores, rawScores = sc[keywords[tableIndex]].getClassificationScores(data) 
            #print(scores)
            proba.append(scores)
            
        return proba
    def segment_soo_table_2(self,table):
        
        
        
        data = table.extractFeatures()
        
        predicted = self.pipe.predict(data['words'])
        scores = self.pipe.predict_proba(data['words'])
        #indicesOfPred = [self.pipe.classes_
        return predicted, scores
            
#     def train(self):
#         # Output: set of indices that segments the table into three parts
#         # Features: 
#         # Classification score gained from the three classififiers
#         # RowNumber
        
         
