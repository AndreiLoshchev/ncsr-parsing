'''
Created on 14.09.2016

@author: michael.fieseler@gmail.com
'''
from tableEntry import TableEntry


class NumericEntry (TableEntry):


    def __init__(self, content):
            super(TableEntry,self).__init__()
            self.content = content
