'''
Detect "Statement of operations" table in NCSR report.
 
Created on 27.09.2016

@author: michael
'''

import os
import string

import dill
import sys
import argparse
import re
import lxml.html
from lxml.builder import E
import multiprocessing
import time

from scipy.sparse import hstack
from scipy.sparse.csr import csr_matrix
#from sklearn.tree.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from sklearn import tree
#from sklearn.ensemble import ExtraTreesClassifier
#from sklearn.tree import ExtraTreeClassifier
from xgboost import XGBClassifier
#from sklearn.naive_bayes import BernoulliNB
#from bs4 import BeautifulSoup
#from sklearn.naive_bayes import MultinomialNB



from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from definitions import DATA_DIR, NSCR_REPORTS_FULL_FILE, NCSR_CLF_ID_NAME,\
    TABLE_DETECTION_CONFIDENCE_NAME
from definitions import ANNOTATED_FILENAMES
from parse_ncsr_backend.stemming_vectorizer import getVectorizer
from parse_ncsr_backend.ncsr_table_parsing import get_lxml_from_string,\
    parse_ncsr_tables_raw, create_table, parse_ncsr_tables_raw_tag
from ncsrtable.table import TABLE_ORIENTATION_HORIZONTAL,\
    TABLE_ORIENTATION_VERTICAL

 


KEYWORD_TO_CONTENT_RATIO=3
MINIMUM_COL_NUM = 2
MINIMUM_ROW_NUM = 10
NumCharacters = set(string.digits + ',' + '.' + ')' + '(')
serialize_filename = os.path.join(DATA_DIR,'table_detector_serialized.p')
defaultFilenames = ANNOTATED_FILENAMES

SOO_TITLE_PATTERN='statement[s]?\s*of\s*operations(?!.*cont.*ed)(?!.*cont[.])(?!.*[^\x00-\x7F]).*'
#SOO_TITLE_PATTERN_CONT='statement[s]\s*of\s*operations\s.*cont.*ed'

FH_TITLE_PATTERN= 'financial\s*highlights(?!.*cont.*ed)(?!.*cont[.])(?!.*[^\x00-\x7F]).*'
FH_TITLE_PATTERN_CONT= 'financial\s*highlights\s.*cont.*ed'

SAL_TITLE_PATTERN='statement[s]?\s*of\s*assets\s*and\s*liabilities(?!.*cont.*ed)(?!.*cont[.])(?!.*[^\x00-\x7F]).*'
SAL_TITLE_PATTERN_CONT='statement[s]?\s*of\s*assets\s*and\s*liabilities\s.*cont.*ed'

SCNA_TITLE_PATTERN='statement[s]?\s*of\s*changes\s*in\s*net\s*assets(?!.*cont.*ed)(?!.*cont[.])(?!.*[^\x00-\x7F]).*'
SCNA_TITLE_PATTERN_CONT='statement[s]?\s*of\s*changes\s*in\s*net\s*assets\s.*cont.*ed'

SOO_SAA_TITLE_PATTERN='statement[s]?\s*of\s*sperations\s*and\s*assets\s*and\s*liabilities(?!.*cont.*ed)'#(?!.*cont[.])(?!.*[^\x00-\x7F]).*'
DEBUG=False



class TableDetector(object):
    
    
    def __init__(self, train_file_names=None, doSerialize=True):
        self.target_soo='soo_table'
        self.target_soo_cont='soo_table_cont'
        self.target_fh ='fh_table'
        self.target_fh_cont='fh_table_cont'
        self.target_other ='other'
        self.target_sal='sal_table'
        self.target_sal_cont='sal_table_cont'
        self.target_scna='scna_table'
        self.target_scna_cont='scna_table_cont'
        self.target_soo_plus_saa='soo_plus_saa_table'
        self.target_names=[self.target_soo,self.target_fh,self.target_soo_cont,
        self.target_fh_cont,self.target_other,self.target_sal,self.target_sal_cont,
        self.target_scna,self.target_scna_cont,self.target_soo_plus_saa]
        self.train_data={}
 
        
        # The relevant parts for classification are serialized.
        # If present, these will be used.
        if not os.path.isfile(serialize_filename) or train_file_names is not None:
            
             
            #self.clf=DecisionTreeClassifier(min_samples_leaf=3,max_depth=10)
            #self.clf=ExtraTreesClassifier(n_estimators=100)#min_samples_leaf=3,max_depth=10)
            self.clf=XGBClassifier(n_estimators=800, min_child_weight=5,max_depth=4,gamma=1,colsample_bytree=1.0,subsample=0.6,n_jobs=multiprocessing.cpu_count())
            #self.clf=XGBClassifier(n_estimators=800,gamma=0.5)
            #self.clf=BernoulliNB()
            #self.clf=ExtraTreeClassifier()
            self.vect = Pipeline([('vect', getVectorizer()),('tfidf', TfidfTransformer()),])

            #self.vect=getVectorizer()
            self.trans=TfidfTransformer()
            self.readTrainData(train_file_names)
            #self.pca = TruncatedSVD()
            
            self._train()
            
            if doSerialize:
                self._serializeClassifier()

        else:
            with open(serialize_filename,'r') as f:
                self.clf, self.vect, self.train_data, self.train_targets = dill.load(f)
                #print(self.vect.vocabulary_)
        if False:
            tree.export_graphviz(self.clf,out_file=os.path.join(DATA_DIR,'tableDetector_tree.dot'), class_names=self.clf.classes_)
    
    
    
    def _serializeClassifier(self):
        with open(serialize_filename,'w') as f:
            dill.dump([self.clf,self.vect,self.train_data,self.train_targets],f)
    
    def find_keywords_before(self,table, keywordRegexs):
 
        LOOK_BACK_DISTANCE=20
        
        min_dists=[LOOK_BACK_DISTANCE]*len(keywordRegexs)
        patterns =[re.compile(x,flags=re.IGNORECASE) for x in keywordRegexs]
        
        item = table
        for dist in range(0,LOOK_BACK_DISTANCE): 

            item = item.getprevious();
            if item is None:
                break
            content = item.xpath('.//text()')

            if len(content)>0:
                content = " ".join([x.strip() for x in content])
                
            else:
                content=''
            
            for i in range(len(patterns)):
                match = re.search(patterns[i], content)
                
                # avoid mistaking keyword occurrence in free text
                # by testing for the ratio of content length and keyword(s) length
                if match and len(content)<KEYWORD_TO_CONTENT_RATIO*len(keywordRegexs[i]):
                    min_dists[i]=min(min_dists[i],dist)
                    
            # normalize distance:
            # ~ 1 -> keyword is found close before the table
            # ~ 0 -> keyword not found / far away
            #print(1- min_dist/float(LOOK_BACK_DISTANCE))
        
        return [1- x/float(LOOK_BACK_DISTANCE) for x in min_dists] 

    def find_keywords_in(self,words_joined, keywordRegex):
        
        pattern = re.compile(keywordRegex,flags=re.IGNORECASE)
        
        l = len(re.findall(pattern, words_joined))
        
        return 1 if l>=1 else 0 
    
    def number_of_numeric_entries(self, tableStringData):
         
        if len(tableStringData)==0:
            return 0
         
        pattern_num = re.compile('[0-9]*[.,][0-9]+|[0-9]+?', flags=re.IGNORECASE)
        l = sum([1 for x in tableStringData if re.search(pattern_num,x) ])
 
        return l/float(len(tableStringData))
    

    def percent_of_numeric(self, tableStringData):
         
        if len(tableStringData)==0:
            return 0
         
        numbers = sum(n.isdigit() for n in tableStringData)
        words_num = sum(w.isalpha() for w in tableStringData)
        try:
            r = numbers/words_num*100
        except ZeroDivisionError:
            r = 0
        return r 


    def years(self, tableStringData):
         
        if len(tableStringData)==0:
            return 0
         
        #words_sum = len(str(tableStringData).split())
        matches = re.findall('[1-3][0-9]{3}', str(tableStringData))
        
        return len(matches)
    
    
    def find_floats(self, tableStringData):
         
        if len(tableStringData)==0:
            return 0
         
        matches_float=re.findall('\d*\.\.?\d+',tableStringData)
        
        return len(matches_float)



    def extract_table_strings(self, table, includeNumbers=False):   
        
        rowData = table.xpath('.//tr')
        
        numCols = 0
        for row in rowData:
            l = len(row.xpath('.//td'))
            numCols = max(l,numCols)
        
        numRows = len(rowData);
        stringData = []
        
        if numCols<MINIMUM_COL_NUM or numRows<MINIMUM_ROW_NUM:
            return stringData
        
        for rowIndex in range(numRows):
            
            colData = rowData[rowIndex].xpath('.//td')
            for colIndex in range(len(colData)):
                value=colData[colIndex].xpath('.//text()')
                if len(value)>0:
                    value = string.join([x.strip() for x in value]).strip()
                else:
                    value=''

                if not includeNumbers and set(value) <=NumCharacters:
                    continue
                if len(value.strip())>0:
                    stringData.append(value)
                
        return stringData
    
    def train(self):
        '''Train classifier'''
        self.readTrainData()
        self._train()
        self._serializeClassifier()
    
    def _train(self):
        '''Train classifier (internal function)'''  

        self.vect.fit(self.train_data['words'])

        X = self._buildFeatureMatrix(self.train_data, train=True)
        #from imblearn.over_sampling import SMOTE
        #from imblearn.over_sampling import RandomOverSampler
        #ros = RandomOverSampler()
        self.clf.fit(X,self.train_targets)

       

           



    def readTrainData(self,train_file_names=None):
        
            self.train_data={}
            self.train_targets=[]
            
            if train_file_names is None:
                train_file_names=ANNOTATED_FILENAMES
                
                
            
            for filename in train_file_names:
                # get all tables
                with open(filename,'r') as f:
                    s = f.read()
                tree = get_lxml_from_string(s)
                tables = tree.xpath('//table') 
            ########Table string collection#########

            ########################################
                train_tables=[]
                gt = self._get_gt(tree)
                self.train_targets.extend(gt)       
                
                # get GT for each table
                for table in tables:
                    train_tables.append(table)
                   
                train_data = self._processTable(train_tables)
                

                 
                if self.train_data.keys()==[]:
                    self.train_data=train_data


                else:
                    self.train_data = self._joinDicts(self.train_data, train_data)
 
                
    def _get_gt(self, tree):
        targets=[]
        tables = tree.xpath('//table')
        for table in tables:
            table_classes=table.get('class')
            tmp=self.find_keywords_before(table, [FH_TITLE_PATTERN_CONT])

            if table_classes is not None:
                # the *_cont variants have to go first here:    
                if "soo_table_cont" in table_classes:
                    target=self.target_soo_cont
                elif ("fh_table_cont" in table_classes) or tmp[0]>0:
                    target=self.target_fh_cont
                elif ("fh_table" in table_classes) and tmp[0]>0:
                    target=self.target_fh_cont
                elif "sal_table_cont" in table_classes:
                    target=self.target_sal_cont
                elif "scna_table_cont" in table_classes:
                    target=self.target_scna_cont
                elif "soo_table" in table_classes:
                    target=self.target_soo
                elif "fh_table" in table_classes:
                    target=self.target_fh    
                elif "sal_table" in table_classes:
                    target=self.target_sal
                elif "scna_table" in table_classes:
                    target=self.target_scna
                elif "soo_plus_saa_table" in table_classes:
                    target=self.target_soo_plus_saa
                elif "other" in table_classes:
                    target=self.target_other
                else:
                    # typo in class attribute?
                    if DEBUG:
                        print('Check annotation:')
                        print(table_classes)
                    target=self.target_other
            else:
                target=self.target_other
    
            targets.append(target)
            
        return targets
    
    def _joinDicts(self,dict_a, dict_b):
        
        for key in dict_a.keys():
            dict_a[key].extend(dict_b[key])
            
        return dict_a
            
            
    def _processTable(self, tables):
        '''extract features from tables'''
        train_data={}
        train_data['words']=[]
        train_data['keyword_before_table_soo']=[]
        #train_data['keyword_before_table_soo_cont']=[]#cont soo
        train_data['keyword_before_table_fh']=[]
        train_data['keyword_before_table_fh_cont']=[]#cont
        train_data['keyword_before_table_sal']=[]
        train_data['keyword_before_table_sal_cont']=[]#cont sal
        train_data['keyword_before_table_scna']=[]
        train_data['keyword_before_table_scna_cont']=[]#cont scna
        train_data['keyword_before_table_soo_plus_saa']=[]

        train_data['keyword_in_table_soo']=[]
        #train_data['keyword_in_table_soo_cont']=[]#cont soo
        train_data['keyword_in_table_fh']=[]
        train_data['keyword_in_table_fh_cont']=[]#cont
        train_data['keyword_in_table_sal']=[]
        train_data['keyword_in_table_sal_cont']=[]#cont sal
        train_data['keyword_in_table_scna']=[]
        train_data['keyword_in_table_scna_cont']=[]#cont scna
        train_data['keyword_in_table_soo_plus_saa']=[]

        train_data['num_rows']=[]
        train_data['num_cols']=[]
        train_data['soo_keywords']=[]
        train_data['fh_keywords']=[]
        train_data['fh_cont_keywords']=[]#cont
        train_data['sal_keywords']=[]
        train_data['scna_keywords']=[]
        train_data['soo_plus_saa_keywords']=[]
        train_data['number_ratio']=[]
        train_data['years_fh']=[]
        train_data['years_fh_cont']=[]
        train_data['floats']=[]
        train_data['scna_cont_keywords']=[]
        train_data['sal_cont_keywords']=[]
        train_data['sal_cont_detect']=[]
        train_data['scna_cont_detect']=[]

       



        for table in tables:

            words_joined=string.join(self.extract_table_strings(table)," ")
            train_data['words'].append((words_joined))

            tmp=self.find_keywords_before(table, [SOO_TITLE_PATTERN,FH_TITLE_PATTERN,
            SAL_TITLE_PATTERN,SCNA_TITLE_PATTERN,SOO_SAA_TITLE_PATTERN,FH_TITLE_PATTERN_CONT,SAL_TITLE_PATTERN_CONT,SCNA_TITLE_PATTERN_CONT])

            train_data['keyword_before_table_soo'].append(tmp[0])
            train_data['keyword_before_table_fh'].append(tmp[1])
            train_data['keyword_before_table_sal'].append(tmp[2])
            train_data['keyword_before_table_scna'].append(tmp[3])
            train_data['keyword_before_table_soo_plus_saa'].append(tmp[4])
            train_data['keyword_before_table_fh_cont'].append(tmp[5])#cont
            #train_data['keyword_before_table_soo_cont'].append(tmp[6])#cont soo
            train_data['keyword_before_table_sal_cont'].append(tmp[6])#cont sal
            train_data['keyword_before_table_scna_cont'].append(tmp[7])#cont scna
            
            ########################################## KEYWORD MATCH #############################################
            kwd = re.match('.*incom.*expense.*realized and unrealized.*', words_joined,re.IGNORECASE)
	    #kwd1 = re.match('.*custodia.*',words_joined, re.IGNORECASE)	
            train_data['keyword_in_table_soo'].append(0 if kwd is None else 1)

            kwd = re.match('.*urnover.*', words_joined, re.IGNORECASE)
            train_data['keyword_in_table_fh'].append(0 if kwd is None else 1)
            
            kwd = re.match('.*liabilities.*', words_joined,re.IGNORECASE)
            train_data['keyword_in_table_sal'].append(0 if kwd is None else 1)
            
            kwd = re.match('.*perations.*distributions to s.*', words_joined,re.IGNORECASE)
            train_data['keyword_in_table_scna'].append(0 if kwd is None else 1)
            
            kwd = re.match('.*capital.*', words_joined,re.IGNORECASE)
            train_data['keyword_in_table_soo_plus_saa'].append(0 if kwd is None else 1)
            
            kwd = re.match('.*urnover.', words_joined,re.IGNORECASE)#cont
            train_data['keyword_in_table_fh_cont'].append(0 if kwd is None and tmp[5]<=0 else 1)

            #kwd = re.match('.*net realized and unrealized.*', words_joined,re.IGNORECASE)#cont soo
            #train_data['keyword_in_table_soo_cont'].append(0 if kwd is None and tmp[6]<=0 else 1)

            kwd = re.match('.*et asset value.*', words_joined,re.IGNORECASE)#cont sal
            train_data['keyword_in_table_sal_cont'].append(0 if kwd is None and tmp[6]<=0 else 1)

            kwd = re.match('.*class .*', words_joined,re.IGNORECASE)#cont scna
            train_data['keyword_in_table_scna_cont'].append(0 if kwd is None and tmp[7]<=0 else 1)


            #################################### TABLE KEYWORDS IN #######################################
            train_data['soo_keywords'].append(self.find_keywords_in(words_joined, SOO_TITLE_PATTERN))
            train_data['fh_keywords'].append(self.find_keywords_in(words_joined, FH_TITLE_PATTERN))
            train_data['fh_cont_keywords'].append(self.find_keywords_in(words_joined, FH_TITLE_PATTERN_CONT))
            train_data['sal_keywords'].append(self.find_keywords_in(words_joined, SAL_TITLE_PATTERN))
            train_data['scna_keywords'].append(self.find_keywords_in(words_joined, SCNA_TITLE_PATTERN))
            train_data['soo_plus_saa_keywords'].append(self.find_keywords_in(words_joined, SOO_SAA_TITLE_PATTERN))
            train_data['scna_cont_keywords'].append(self.find_keywords_in(words_joined, SCNA_TITLE_PATTERN_CONT))
            train_data['sal_cont_keywords'].append(self.find_keywords_in(words_joined, SAL_TITLE_PATTERN_CONT))
            ###########################################################################################
            
            
            name=table.text_content()
            d=re.sub('[^\x00-\x7F]+', '', name)
            d1=d.replace('\n', '')
            d2=d1.replace('\t', '')
            
            m=re.findall('^(?!.*distributions to s.*)(.*capital stock activity.*)$',d2,re.IGNORECASE)
            train_data['scna_cont_detect'].append(0 if m==[] else 1)
            
            m=re.findall('^(?!.*liabilities.*)(.*et asset value\s.*per.*)$',d2,re.IGNORECASE)
            train_data['sal_cont_detect'].append(0 if m==[] else 1)

           
            ######################################################################################
            train_data['floats'].append(0 if self.find_floats(str(self.extract_table_strings(table,True)))<=10 else 1)
            train_data['years_fh'].append(1 if self.years(self.extract_table_strings(table,True))>=2 and self.find_floats(str(self.extract_table_strings(table,True)))>=10 else 0)
            train_data['years_fh_cont'].append(1 if self.years(self.extract_table_strings(table,True))>=2 and self.find_floats(str(self.extract_table_strings(table,True)))>=10 and tmp[5]>0 else 0)
            # TODO: relate number of numbers to number of numeric columns
  
            train_data['number_ratio'].append(self.number_of_numeric_entries(self.extract_table_strings(table,True)))

            rows = table.xpath('.//tr')
            
            train_data['num_rows'].append(len(rows))
            if len(rows)>0:
                num_cols = len(rows[0].xpath('./td'))
            else:
                num_cols=0
            train_data['num_cols'].append(num_cols)
        

            
        #print(train_data['sal_cont_detect'])
        return train_data

    def _buildFeatureMatrix(self, table_data, train=False):
        ''' create X from data from vectorizer and other features'''
        
        string_data = [string.join(x) for x in table_data['words']]
        vectorized = self.vect.transform(string_data)

        tmp=[      
                   table_data['keyword_before_table_soo'],
                   #table_data['keyword_before_table_soo_cont'],
                   table_data['keyword_before_table_fh'],
                   table_data['keyword_before_table_sal'],
                   table_data['keyword_before_table_sal_cont'],
                   table_data['keyword_before_table_scna'],
                   table_data['keyword_before_table_scna_cont'],
                   table_data['keyword_before_table_soo_plus_saa'],
                   table_data['keyword_before_table_fh_cont'],
                   table_data['keyword_in_table_soo'],
                   #table_data['keyword_in_table_soo_cont'],
                   table_data['keyword_in_table_fh'],
                   table_data['keyword_in_table_fh_cont'],
                   table_data['keyword_in_table_sal'],
                   table_data['keyword_in_table_sal_cont'],
                   table_data['keyword_in_table_scna'],
                   table_data['keyword_in_table_scna_cont'],
                   table_data['keyword_in_table_soo_plus_saa'],
                   table_data['num_rows'],
                   table_data['num_cols'],
                   table_data['number_ratio'],
                   table_data['soo_keywords'],
                   table_data['fh_keywords'],
                   table_data['fh_cont_keywords'],
                   table_data['sal_keywords'],
                   table_data['scna_keywords'],
                   table_data['scna_cont_keywords'],
                   table_data['sal_cont_keywords'],
                   table_data['soo_plus_saa_keywords'],
                   table_data['years_fh'],
                   table_data['years_fh_cont'],
                   table_data['floats'],
                   table_data['sal_cont_detect'],
                   table_data['scna_cont_detect'],
            ]

        return hstack((vectorized,csr_matrix(tmp).transpose()))

    
    def predict(self, tree):

        HTMLtables = tree.xpath('//table')
        
        table_data=self._processTable(HTMLtables)

        X = self._buildFeatureMatrix(table_data)
 

        prediction=self.clf.predict(X)

        confidence=self.clf.predict_proba(X)
        
        return prediction, confidence   
         
    def score(self, tree, prediction):
   
        relevantTables=0
        truePositives=0
        falsePositives=0
        falseNegatives=0
        
        gt = self._get_gt(tree)

        for item in zip(gt,prediction):
           
            if item[0] != 'other':
                relevantTables+=1
                if item[0]==item[1]:
                    truePositives+=1
            else:
                if item[1]!='other':
                    falsePositives+=1
                
        
         
        precision = float(truePositives)/(.00000001+truePositives+falsePositives)
        recall = float(truePositives)/relevantTables
        
        data={}
        data['precision']=precision
        data['recall']=recall
        data['prediction']=prediction
        data['gt']=gt

        return data#################################################################################

    def predict_train(self, tree):

        HTMLtables = tree.xpath('//table')
        
        table_data=self._processTable(HTMLtables)

        X_train = self._buildFeatureMatrix(table_data)    

        prediction_train=self.clf.predict(X_train)
        
        return prediction_train 
         
    def score_train(self, tree, prediction_train):
   
        relevantTables=0
        truePositives=0
        falsePositives=0
        falseNegatives=0
        
        gt_train = self._get_gt(tree)

        for item in zip(gt_train,prediction_train):
           
            if item[0] != 'other':
                relevantTables+=1
                if item[0]==item[1]:
                    truePositives+=1
            else:
                if item[1]!='other':
                    falsePositives+=1
                
        
         
        precision_train = float(truePositives)/(.00000001+truePositives+falsePositives)
        recall_train = float(truePositives)/relevantTables
        
        data_train={}
        data_train['precision']=precision_train
        data_train['recall']=recall_train
        data_train['prediction']=prediction_train
        data_train['gt']=gt_train
        
        return data_train                         
              
def main(args):
    
    detector = TableDetector()
    
    if args.train:
        detector.train()
        return

    if not args.InputFilename:
        raise Exception('Input file name missing') 
    
    s = args.InputFilename.read()
    
    tree = lxml.html.fromstring(s)
    
    
    if tree is not None:
        prediction, confidence = detector.predict(tree)
        allTables = tree.xpath('//table')
        numTables = len(allTables)
        if numTables!=len(prediction):
            raise Exception("Mismatch of prediction and number of tables in document (most likely a bug)")
       
        print('')
        print(str(numTables) + " tables in total")
        print(str(len([1 for x in prediction if x==detector.target_soo ])) + " SoO tables detected")
        print(str(len([1 for x in prediction if x==detector.target_soo_cont ])) + " continued SoO tables detected")
        print(str(len([1 for x in prediction if x==detector.target_fh ])) + " FH tables detected")
        print(str(len([1 for x in prediction if x==detector.target_fh_cont ])) + " continued FH tables detected")
        print(str(len([1 for x in prediction if x==detector.target_sal ])) + " SAL tables detected")
        print(str(len([1 for x in prediction if x==detector.target_sal_cont ])) + " continued SAL tables detected")
        print(str(len([1 for x in prediction if x==detector.target_scna ])) + " SCNA tables detected")
        print(str(len([1 for x in prediction if x==detector.target_scna_cont ])) + " continued SCNA tables detected")
        print(str(len([1 for x in prediction if x==detector.target_soo_plus_saa ])) + " Soo_plus_Saa tables detected")
        print(str(len([1 for x in prediction if x==detector.target_other ])) + " other tables detected")
        print('')
        
        if args.InputFilename.name==args.OutputFilename:
            raise Exception('Input file is equal to output file - this would overwrite the source file')
        
        
        # Determine output file name:        
        outputfilename=''
        if args.OutputFilename:
            outputfilename=args.OutputFilename
        else:
            print('Choosing input file name with suffix "-toc-annotated" as output file name:')
            if args.InputFilename.name.endswith(".html"):
                outputfilename=args.InputFilename.name[:-5]+"-toc-annotated"
                print(outputfilename)
                print('')
            else:
                outputfilename=args.InputFilename.name + "-toc-annotated"   
        
        # Use 'classes_' as sorted in the clf to 
        # relate confidence to predictions: 
        clf_classes = list(detector.clf.classes_)
        
        # add tags to HTML data:
        previous_tag=None
        previous_orientation=None
        ncsr_id=0
        
        for item in zip(prediction,allTables,confidence):

            tag_to_set = item[0]
            classes = item[1].classes
            classes.add(tag_to_set)
            c_ind = clf_classes.index(item[0])
            
            item[1].attrib['data-' + TABLE_DETECTION_CONFIDENCE_NAME]=str(item[2][c_ind])      
            
            if tag_to_set not in [detector.target_other]: 
  
                tmp_data = parse_ncsr_tables_raw_tag(item[1],tag_to_set)
                tmp_table = create_table([tmp_data])
                if tag_to_set in [detector.target_fh,detector.target_soo,
                detector.target_sal,detector.target_scna,detector.target_soo_plus_saa]:
                    ncsr_id=0
                    headerEntries = tmp_table[0].getItemHeaderLinks()
                    previous_orientation = tmp_table[0].getOrientation()
                    
                elif tag_to_set in [detector.target_fh_cont, detector.target_soo_cont,
                detector.target_sal_cont,detector.target_scna_cont]:
                    # try to get itemHeaderLinks. May fail if the table 
                    # does not contain text items to conclude where headers reside:
                    try:
                        headerEntries = tmp_table[0].getItemHeaderLinks()
                    except:
                        # if it fails, use orientation from preceding table, insert 
                        # IDs into first <TD> tags depending on orientation
                        
                        headerEntries=None
                    if headerEntries is None:
                        try:
                            if (tag_to_set==detector.target_fh_cont and previous_tag==detector.target_fh) or (tag_to_set==detector.target_soo_cont and previous_tag==detector.target_soo) or (tag_to_set==detector.target_sal_cont and previous_tag==detector.target_sal) or (tag_to_set==detector.target_scna_cont and previous_tag==detector.target_scna):
                                trs = item[1].xpath('.//tr')
                                if previous_orientation==TABLE_ORIENTATION_HORIZONTAL:
                                    headerEntries=trs[0].xpath('.//td')
                                elif previous_orientation==TABLE_ORIENTATION_VERTICAL:
                                    headerEntries=[x.xpath('.//tr')[0] for x in trs]
                        except:
                            # failed to set entries:
                            pass
                    else:
                        pass
                    # if its not a cont'd table. proceed as normal:
                    
                    
                    
                # parse table to extract header items:
                
#                 tmp_data = parse_ncsr_tables_raw_tag(item[1],tag_to_set)
#                 tmp_table = create_table(tmp_data)
#              
               # previous_tag captures everything else than "other"
                previous_tag=tag_to_set
                
                #headerEntries = tmp_table[0].getItemHeaderLinks()
                if headerEntries:
                    for entry in headerEntries:
                        entry.attrib['data-' + NCSR_CLF_ID_NAME]=str(ncsr_id)
                        ncsr_id+=1
            
        if args.annotationscript: 
            
            head = tree.find('.//head')
            
            scripttag_1 = E.script(src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js")
            scripttag_2 = E.script(src="annotator.js")
            
            head.append(scripttag_1)
            head.append(scripttag_2)
            
        with open(outputfilename,'w') as f:    
            f.write(lxml.html.tostring(tree))
            
if __name__ == "__main__":
          
    parser = argparse.ArgumentParser(
        description='Detect and mark statement-of-operations table(s) (SOO) and financial highlight table(s) (FH) in NCSR report')
    

    parser.add_argument('InputFilename', 
                type=argparse.FileType('r'),
                nargs='?',
                help='Input file to parse.')
    parser.add_argument('OutputFilename', 
                #type=argparse.FileType('w'),
                nargs='?',
                help='File to output the result to (annotated table data)')
    
    parser.add_argument('-t','--train', help='train table detection from annotated documents.',
                        action='store_true')
    parser.add_argument('-a','--annotationscript', help="Add annotation script (annotator.js) to the document",
                        action='store_true')
    args = parser.parse_args()
    if (args.InputFilename or args.OutputFilename) and args.train:
        print("Specify either '--train' or input and output file")
        sys.exit(2)
        
    main(args)


