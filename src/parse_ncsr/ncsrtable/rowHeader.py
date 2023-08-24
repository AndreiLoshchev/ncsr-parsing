'''
Created on 14.09.2016

@author: michael.fieseler@gmail.com
'''

from tableEntry import TableEntry

class RowHeader (TableEntry):
    
    def __init__(self, content, indentation, groundTruthClassification=None):
        super(TableEntry,self).__init__()
        self.indentation = indentation
        self.content = content
        self.groundTruthClassification=groundTruthClassification
        
        
