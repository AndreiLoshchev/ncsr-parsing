'''
Created on 14.09.2016

@author: michael.fieseler@gmail.com
'''



class TableEntry (object):
    def __init__(self, width, height):
        self.content=u''
        self.groundTruthClassification=('undefined','')
        self.width=width
        self.height=height
        self.featureDict=None
        self.htmlLink=None
        
                
    def getContent(self):
        return self.content
    
    def setContent(self,content):
        self.content=content    
        
    def isEmpty(self):
        return self.content==None #or self.content==""  
    
    
    def __str__(self):
        if self.content is None:
            return ""
        else:
            return self.content