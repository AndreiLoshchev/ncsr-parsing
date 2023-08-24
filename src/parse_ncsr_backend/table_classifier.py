'''
Created on 30.11.2016

@author: michael
'''

import numpy as np
import re

class TableClassifier(object):
    '''
    Super class for table classifiers.
    
    '''


    def __init__(self, params):
        '''
        Constructor
        '''
        
        
    def score(self, X_test, y_test, section=None):

        result = self.predict(X_test)
        pred=result['prediction']
        trueComparisons=0
        matches=0
        #print(pred[1])
         
        trueMain=0
        trueSec=0 
        nonEmtpySec=0
         
        y_test=np.concatenate(y_test)
        pred = np.concatenate(pred) 
        for i in range(len(y_test)):
            if section!=None:
                if not y_test[i][0].startswith(section):
                    continue
            if y_test[i][0]!='undefined'and y_test[i][0]!=None and y_test[i][0]!='empty':
                trueComparisons+=1
                if [x.lower() for x in list(y_test[i])]==[x.lower() for x in list(pred[i])]: 
                    matches+=1
                
                if y_test[i][0]==pred[i][0]:
                    trueMain+=1
                if y_test[i][1]==pred[i][1]:
                    trueSec+=1
            if y_test[i][1]!='':
                nonEmtpySec+=1
        print('True main items : ' + str(trueMain/float(trueComparisons)))
        print('True secondary items: ' + str(trueSec/float(trueComparisons)))

        
        return matches/float(trueComparisons)
    
    
    def predictSubclasses(self, tables):
        pattern = re.compile('Class\s+[0-9]+|Class\s+[A-Z]|Investor\s+Class|Advisor\s+Class|'
                                'Institutional\s+Class|Affiliated\s+issuers|Unaffiliated\s+issuers|'
                                'Service\s+shares|Non-service shares|Admiral\s+shares|Investor\s+(plus\s+|select\s+)?shares|Signal\s+shares|Institutional\s+(plus\s+|select\s+)?shares|ETF\s+shares', flags=re.IGNORECASE)
        
        predicted_subclass=[]
        predicted_fillIn=[]
        
        for t in tables:
            items=t.extractFeatures()
            predicted_fillIn_tmp=[0]*len(items['words'])
            predicted_tmp=[]
            for rowIndex in range(len(items['words'])):
                match = re.search(pattern, items['words'][rowIndex])

                if match:
#               
                    if match.group(0).lower()!='etf shares':    
                        predicted_tmp.append(match.group(0).title())
                    else:
                        predicted_tmp.append('ETF Shares')

                    
                else:
                    predicted_tmp.append('')
            predicted_subclass.append(predicted_tmp) 
            predicted_fillIn.append(predicted_fillIn_tmp)       
            
        return predicted_subclass, predicted_fillIn          
