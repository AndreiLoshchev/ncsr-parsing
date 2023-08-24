'''
Created on 20.09.2016
 
@author: michael.fieseler@gmail.com
'''
 

import string
import re

import numpy as np

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB, GaussianNB
from sklearn.pipeline import Pipeline, make_pipeline, make_union, FeatureUnion
 
from sklearn.linear_model import SGDClassifier
from sklearn.base import TransformerMixin, BaseEstimator

from src.parse_ncsr_backend.stemming_vectorizer import getVectorizer
 

USE_INDICES=True

class SooClassifier (object):
     
    #def __init__(self, useStemming,train_data,target_names,rowTypes): #,target_names,train_data):
    def __init__(self, train_data,target_names,options): #,target_names,train_data):
      
        # 'train_data' is dict conating
        self.train_data=train_data
        self.train_data['words'] = [" ".join(x) for x in train_data['words']]
        
        self.target_names=target_names
        self.target_names.append('undefined')
        self.train_data['words'].append("")
        self.train_data['rows'].append(0)

        self.target_names.append('empty')
        self.train_data['words'].append("")
        self.train_data['rows'].append(0)
                
        self.targets=range(len(self.target_names))
        
        self.useStemming=options['USE_STEMMING']

        vect = getVectorizer(use_stemming=self.useStemming)
        #classifier = SGDClassifier(loss='log', penalty='l2',alpha=1e-3, n_iter=5, random_state=42)#,probability=True)
        classifier = MultinomialNB(alpha=1e-3)
        #classifier = BernoulliNB(alpha=1e-3)
        
        
        word_pipe=make_pipeline(
            ItemExtractor('words'),vect,TfidfTransformer(use_idf=False))
        row_pipe =make_pipeline(
            ItemExtractor('rows'),ArrayCaster())
        
        featureWeights={}
        featureWeights['word_pipe']=1
        featureWeights['row_pipe']=1-featureWeights['word_pipe']
        features = FeatureUnion([('word_pipe',word_pipe),('row_pipe',row_pipe)],transformer_weights=featureWeights)
#         self.clf=Pipeline([('vectorizer',vect),
#                           ('tfidf',TfidfTransformer()),
#                           ('clf',classifier)]) 
        self.clf=Pipeline([('features',features),
                           ('clf',classifier)])
        if USE_INDICES:
            self.clf.fit(self.train_data,self.targets)
        else:
            self.clf.fit(self.train_data,self.target_names)
        #print(self.clf.get_params(False))
        
    def predict(self,items):
        if len(items)==0:
            return []
        
        # predict items, fix empty entries:
        predicted=self.clf.predict(items)
        
        predicted_subClass=['']*len(predicted)
        if USE_INDICES:
            predicted = [self.target_names[tableIndex] for tableIndex in predicted]
        for tableIndex in range(len(items['words'])):
            if items['words'][tableIndex].strip()=="":
                predicted[tableIndex]="empty"

        # process lines that have only a "class X" entry, e.g.
        # Distribution fees:
        #     Class A    <-
        #     Class B    <-
        #     ...
        
#         pattern = re.compile('Class [0-9]+|Class [A-Z]|Investor Class|Advisor Class|Institutional Class', flags=re.IGNORECASE)
#         for tableIndex in range(len(items['words'])):
#             match = re.search(pattern, items['words'][tableIndex])
#             # If line contains only "Class X"
#             # -> assign predicted value from item above
#             if match and match.group(0)==items['words'][tableIndex]:
#                 predicted[tableIndex]=predicted[tableIndex-1]
#                 
           
        return predicted #(zip(predicted,items['class']))
        
    ''' Returns either the decision function scores or probability values, 
    depending on which the chosen classifier provides'''    
    def getClassificationScores(self,stringData):
        if len(stringData)==0:
            return [None,None,None]
        
        # sort so it fits the output of self.predict()
        # NOTE: values given in 
        # a) get list of classes (for the classifier in use):
        #indicesOfPredicted = self.clf.predict(stringData)
        if USE_INDICES:
            sc_classes=[string.lower(self.target_names[x]) for x in list(self.clf.classes_)]
        else:
            sc_classes=[string.lower(x) for x in list(self.clf.classes_)]
        prediction = self.predict(stringData)
        
        # omit second-level classifiction
        
        prediction = [string.lower(x) for x in prediction]  
        indicesOfPredicted=[sc_classes.index(string.lower(item)) for item in prediction]
        
        # b) map scores to prediction:
        scores=[]
        minScores=[]
        maxScores=[]
        if hasattr(self.clf, 'decision_function'):
            decisionFunction=self.clf.decision_function(stringData)
        elif hasattr(self.clf, 'predict_proba'):
            decisionFunction=self.clf.predict_proba(stringData)
        
        for tableIndex in range(len(stringData['words'])):
            scores.append(decisionFunction[tableIndex][indicesOfPredicted[tableIndex]])
            minScores.append(decisionFunction[tableIndex].min())
            maxScores.append(decisionFunction[tableIndex].max())
        
        rawScores=decisionFunction
        
        # TODO Omitting everything else for now:
        return scores #, minScores, maxScores, rawScores
   
class ArrayCaster(BaseEstimator, TransformerMixin):
    def fit(self, x, y=None):
        return self

    def transform(self, data):
        data=np.array(data)
        #print data.shape
        #print np.transpose(np.matrix(data)).shape
        return np.transpose(np.matrix(data))
class ItemExtractor(TransformerMixin):

    def __init__(self, column):
        self.column = column

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X[self.column]           
#SooClassifier(False,'income')
          
      
           