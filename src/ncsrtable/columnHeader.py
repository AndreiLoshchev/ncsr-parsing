'''
Created on 14.09.2016

@author: michael.fieseler@gmail.com
'''

from tableEntry import TableEntry

class ColumnHeader (TableEntry):
    
    def __init__(self,content, indentation, groundTruthClassification=None):
        super(TableEntry,self).__init__()
        self.content=content
        self.indentation=indentation
        self.groundTruthClassification=groundTruthClassification