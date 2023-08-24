'''
Created on 14.09.2016

@author: michael.fieseler@gmail.com
'''

#@PydevCodeAnalysisIgnore

from __future__ import print_function

import copy
import re

import numpy as np
from tabulate import tabulate
from cmath import isnan

# No of rows that are considered for column headers
MAX_ASSUMED_HEADER_ROWS=5

TABLE_ORIENTATION_VERTICAL = 'vertical'
TABLE_ORIENTATION_HORIZONTAL = 'horizontal'

# Thresholds giving the percentage of a column that
# must exhibit a feature (e.g., content consists of words) to be considered, e.g.,
# a row header column

THRESHOLD_NUMERIC_COLUMN = .1
THRESHOLD_COL_HEADER = .1
THRESHOLD_DANGLING = .05

# probe rows and columns for typical header items:
searchTerms=['value', 'average', 'period','ratio','ratios','income','loss','net asset value','expenses','dividends','asset',
             'income','realized','unrealized','expenses','investment','portfolio',
             'interest','fee','custodian', 'net']
    

class Table (object):
    
    def __init__(self):
    
        self._data=[]
        self._indices=[]
        
        self._orientation=None
        
        
        
        self.layout=None
        
        self._columnHeaderColumns=None
        self._rowHeaderColumns=None
        self._numericColumns=None
        self._features=None
        
        self.sourceFileName=''
        
        self._dataDict=None
        
 
    def mergeTable(self, tableToMerge, mergePoint):
        if mergePoint=='right':
            # for each row: determine max col index and
            # insert entries from "tableToAttach" accordingly:
            for row in self._getRowIndices():
                colIndices = [x[1] for x in self._indices if x[0]==row ]
                maxIndexCurrentRow=max(colIndices)
                
                for col,itemIndex in enumerate(tableToMerge._getItemIndicesForRow(row)):
                    self.setEntry(row, col+maxIndexCurrentRow+1 , tableToMerge._data[itemIndex])
            
        elif mergePoint=='bottom':
            for col in self._getColumnIndices():
                rowIndices = [x[0] for x in self._indices if x[1]==col]
                maxIndexCurrentCol=max(rowIndices)
                #print('Merge: ' + str(maxIndexCurrentCol))
                
                for row,itemIndex in enumerate(tableToMerge._getItemIndicesForColumn(col)):
                    self.setEntry(row+maxIndexCurrentCol+1, col , tableToMerge._data[itemIndex])
            
        else:
            raise Exception('Merge at "' + mergePoint + '" not implemented')
        
        
        # reset cached information:
        self.layout=None
        self._dataDict=None
        return self
        
    def printTable(self, orientation=TABLE_ORIENTATION_VERTICAL):
        
        values = self.getNumericValues()
        values = list([list(x) for x in values])
        values = [[x if not isnan(x) else '' for x in xs] for xs in values]
        headers =  self.getNumericHeaders()
        
        items = [self.getItemHeaders()]
        #print(items)
        for x in values:
            items.append(x)
        #print(items)
        items = map(list,map(None,*items))
        print(tabulate(items,headers=headers,tablefmt='grid',floatfmt='.5f'))
        
        

        
    def setEntry(self, row, col, tableNode):
        try:
            ind = self._indices.index((row,col))
            self._data[ind]=tableNode
        except ValueError:
            self._indices.append((row,col))
            self._data.append(tableNode)
            
        
    def getEntry(self,row,col):
        try:
            ind = self._indices.index((row,col))
            return(self._data[ind])
        except ValueError:
            #print('Value does not exist:')
            #print('Row: ' + str(row) + ' Col: ' + str(col))
            return None
    def _getIndexOfEntry(self, entry):
        return self._data.index(entry)
        
    def getStructure(self):
        
        STRUCTURE_EMPTY_VALUE=-1
        
        layout=np.zeros([1,1],dtype=np.int16)
        layout.fill(STRUCTURE_EMPTY_VALUE)
        test_ri = self._getRowIndices()
        test_ci = self._getColumnIndices()
        index=1
        current_i=0
        rowSpan_col=-1
        rowSpan_width=0
        rowSpan_count=0
        
        np.set_printoptions(linewidth=100,formatter={'int' : '{:4d}'.format  })
        for i in range(len(test_ri)):
            #print(i)
            current_j=0
            for j in range(len(test_ci)):
                
                entry = self.getEntry(i, j)
                
                if j==rowSpan_col and rowSpan_count>0:
                    current_i+=rowSpan_width
                
                if entry is not None:
                    #print('width: ' + str(entry.width))
                    index = self._getIndexOfEntry(entry)
                    if layout.shape[1]-1<current_j+entry.width:
                        #print('resize')
                        #print(layout.shape)
                        s=layout.shape
                        layout=np.pad(layout,((0,0),(0,(current_j+entry.width)-layout.shape[1])),mode='constant',constant_values=STRUCTURE_EMPTY_VALUE)
                        #print(layout.shape)
                    if layout.shape[0]-1<current_i+entry.height:
                        layout=np.pad(layout,((0,(current_i+entry.height)-layout.shape[0]),(0,0)),mode='constant',constant_values=STRUCTURE_EMPTY_VALUE)
                    layout[current_i:current_i+entry.height,current_j:current_j+entry.width]=index
                    if entry.height>1:
                        rowSpan_col=j
                        rowSpan_width=entry.width
                        rowSpan_count=entry.height
                        

                    rowSpan_count-=1
                    #index+=1
                    current_j+=entry.width
            current_i+=1
        self.layout=layout            
        return layout
    
    def _getAllPaths(self,orientation):
        
        if self.layout is None:
            self.getStructure()
        
        resultContent=[]
        resultNodes=[]
        
        if orientation==TABLE_ORIENTATION_VERTICAL:
            for c in range(len(self.layout[0])):
                lineContent=[]
                lineNodes=[]
                for r in range(len(self.layout)):
                    index=self.layout[r][c]
                    lineNodes.append(self._data[index])
                    lineContent.append(self._data[index].content)
                resultContent.append(lineContent)
                resultNodes.append(lineNodes)
            
            
        elif orientation==TABLE_ORIENTATION_HORIZONTAL:
            for r in range(len(self.layout)):
                lineContent=[]
                lineNodes=[]
                for c in range(len(self.layout[0])):
                    index=self.layout[r][c]
                    lineNodes.append(self._data[index])
                    lineContent.append(self._data[index].content)
                resultContent.append(lineContent)
                resultNodes.append(lineNodes)
            
        else:
            raise Exception('Orientation not defined properly')
        return resultContent, resultNodes
    
    
#     def getOrientationGL(self):
#     
#         searchTerms=['ratio','net\sasset\svalue','investment\sincome','investment\sloss','realized\sand\unrealized','expenses', 'net\sinvestment\sloss','portfolio\sturnover\srate']
#         
#         for _orientation in ['horizonal',TABLE_ORIENTATION_VERTICAL]:
#             content,nodes=self._getAllPaths(_orientation)
#             for 
    def getOrientation(self):
        '''Tries to determine the predominant table _orientation by searching for common
        terms. Orientation is either vertical (relevant terms are in a vertical column,
        i.e.:
        
        Income     10,0000
        Expenses   20,000
        
        or horizontal, i.e.:
        
        Income    Expenses
        10,000    20,000
        
        '''
        
        if isinstance(self._orientation,basestring):
            return self._orientation
        
        
        maxMatches={}
        maxMatches[TABLE_ORIENTATION_HORIZONTAL]=0
        maxMatches[TABLE_ORIENTATION_VERTICAL]=0
        
        for orientation in [TABLE_ORIENTATION_HORIZONTAL,TABLE_ORIENTATION_VERTICAL]:
            
            data, nodes = self._getAllPaths(orientation)

            for column, nodeColumn in zip(data,nodes):
                colMatches=0
                
                searchTermsCopy = copy.copy(searchTerms)
                for cellItem, cellItemNode in zip(column,nodeColumn):
                    itemFound=False
                    # Workaround for items spanning across almost a row or column: ignore them
                    if orientation==TABLE_ORIENTATION_HORIZONTAL and cellItemNode.width>3:
                        continue
                    if orientation==TABLE_ORIENTATION_VERTICAL and cellItemNode.height>3:
                        continue
                    for term in searchTermsCopy:
                        if re.search(term,cellItem,flags=re.IGNORECASE):
                            itemFound=True
                            break
                    
                    # Additional testing for numbers - usually, there should be more 
                    # numbers stacked in the dominant direction
#                     if re.search('\(?[0-9]+\)?',cellItem):
#                         itemFound=True
                           
                    if itemFound:        
                        colMatches+=1

                if float(colMatches)>maxMatches[orientation]:
                    maxMatches[orientation]=float(colMatches)
        #print(maxMatches)
        if all(x < 3 for x in maxMatches.values()):           
            self._orientation='unknown'
        else:
            if maxMatches[TABLE_ORIENTATION_VERTICAL]>maxMatches[TABLE_ORIENTATION_HORIZONTAL]:
                self._orientation=TABLE_ORIENTATION_VERTICAL
            else:
                self._orientation=TABLE_ORIENTATION_HORIZONTAL
        return self._orientation    
                        
    def _getRowIndices(self):
        return sorted(list(set([x[0] for x in self._indices])))
    
    def _getColumnIndices(self):
        return sorted(list(set([x[1] for x in self._indices])))
    
    def _getItemIndicesForRow(self, row):
        tmp = [x for x in self._indices if x[0]==row]
        return [self._indices.index(x) for x in tmp]
        
    def _getItemIndicesForColumn(self, col):
        tmp = [x for x in self._indices if x[1]==col]
        return [self._indices.index(x) for x in tmp]
    
    def printTableLayout(self):
  
        signs=['x','o']
        # extract unique row _indices:
        rows=self._getRowIndices()
        for r in rows:
            rowString=''
            # column _indices for current row:
            cols = [x[1] for x in self._indices if x[0]==r]
            for c  in range(len(cols)):
                # find element for index (r,c):
                ind = self._indices.index((r,c))
                rowString+=(signs[c%2])*self._data[ind].width
            print(rowString)      
              

            
              
    def _internalGetItemHeaders(self):
        
        # TODO: Merge this function into self._extractDataDict()

        stringData, nodes = self._getAllPaths(self.getOrientation())

        outputStringData=[]
        outputNodes=[]
        ratios=[]
        allMatches=[0]*len(stringData)
        for i,content in enumerate(stringData):
            matches=0
            searchTermsCopy = copy.copy(searchTerms)
            for j,cell in enumerate(content):
                for searchTerm in searchTermsCopy:
                    if re.search(searchTerm,cell):
                        matches+=1
                        searchTermsCopy.remove(searchTerm)
                        break    
                    
            allMatches[i]=matches

             
            ratios.append(float(matches)/len(content))  
              
        maxIndex = allMatches.index(max(allMatches))
        
        tmp = stringData[maxIndex]
        tmp = [x.replace('\n',' ').replace('\r',' ') for x in tmp] 
        outputStringData.append(tmp)
        outputNodes.append(nodes[maxIndex])
        
        if len(outputStringData)==0:
            raise Exception('Could not determine row headers')
                
        return stringData, outputStringData, outputNodes, maxIndex    
    
    def _internalGetItemHeaderIndex(self):
        
        stringData, outputStringData, outputNodes, maxIndex = self._internalGetItemHeaders()
        
        return maxIndex
    
    def getItemHeaderLinks(self):
        ''' get the underlying lxml parts for the
        item header cells '''
        
        stringData, outputStringData, outputNodes, maxIndex = self._internalGetItemHeaders()
        
        return [x.htmlLink for x in outputNodes[0]]
      
    def getItemHeaders(self):
        '''
            returns the item headers for a table, e.g.
            
                            "Year ending 12/31/2016"
            item header a        123
            item header b        234
            item header c        342
            ...                  ...

            Depending on table _orientation, item headers may lie in a column (vertical _orientation) or in 
            a row (horizontal table _orientation).
        '''
        stringData, outputStringData, outputNodes, maxIndex = self._internalGetItemHeaders()
        
        return outputStringData[0]
                
    def _internalExtractDataDict(self):
        """Extract _data dict containing numerical values, location of header lines / numerical columns, etc."""
        
        if self._dataDict:
            return self._dataDict
        
        content,nodes=self._getAllPaths(self.getOrientation())
        
        content = np.array(content)

        
        # TODO: check patterns
        pattern_num = re.compile('\(?[0-9]*[\.,][0-9]+|[0-9]+?', flags=re.IGNORECASE)
        pattern_dang_left = re.compile(r'\s?\(\s?$')
        pattern_dang_right = re.compile(r'\s?\)%?\$?\s?$')
        pattern_dang = re.compile('\(%?|\)%?')
        pattern_isHeader=re.compile('20[0-9]{2}|[A-Za-z\s]{3,}|[0-9]+/[0-9]+/[0-9]+')
        #pattern_dang = re.compile('[\(\)%]+')
        
        # The direction of consecutive _data entries is determined by the direction of
        # item specifiers ('Expenses', 'Income', ....)
        # These entries are along the second dimension of the 'content' array
        
        numericLines=[]
        
        for i  in range(len(content)):
            item=content[i]
            matches = 0
            for cell in item:
                if re.match(pattern_num, cell):
                    matches+=1
            #
            if float(matches)/len(item)>THRESHOLD_NUMERIC_COLUMN:
                numericLines.append(i)
        
        headerLineIndices=[]
        
        rowHeaderColIndex = self._internalGetItemHeaderIndex()
        rowHeaders = self.getItemHeaders()
        
        # Heuristics for detection of "column header" items:
        # - at least one entry should match "pattern_num" (a year or text or a date)
        # - take care not to include items from rowHeaders
        # - avoid repetition of items (-> items with colspan>1)
        # - only check the first MAX_ASSUMED_HEADER_ROWS rows
        detectedMatches=[]
        for j in range(MAX_ASSUMED_HEADER_ROWS):
            matches=0
            #print(content[:,j])
            for i in range(len(content)):
                if i==rowHeaderColIndex:
                    continue
                match= re.search(pattern_isHeader, content[i,j])
                if match and match.group(0) not in detectedMatches and match.group(0) not in rowHeaders[j]:
                    detectedMatches.append(match.group(0))
                    matches+=1
            
            if matches>=1:
                headerLineIndices.append(j)
        
        output=[]

        # Merging differs depending on _orientation - if _orientation is 'horizontal',
        # possible merge candidates will be before or after in the first dimension.
        # If _orientation is 'vertical', merge candidates are before or after in the 
        # second dimension
        if self.getOrientation()==TABLE_ORIENTATION_VERTICAL:
            mergeAbove=[]
            mergeBelow=[]

            for index in numericLines:
                # check columns -1 and +1
                left=[]
                right=[]
                if index>0:
                    left = content[index-1,:]
                if index < len(content)-1:
                    right = content[index+1,:]
                matchesLeft=0
                matchesRight=0
                for j in range(len(left)):
                    if re.match(pattern_dang_left,left[j]):
                        matchesLeft+=1
                for j in range(len(right)):
                    if re.match(pattern_dang_right, right[j]):
                        matchesRight+=1
                        
                if len(left)>0:
                    if float(matchesLeft)/len(left)>THRESHOLD_DANGLING:
                        mergeAbove.append(index)
                if len(right)>0:
                    if float(matchesRight)/len(right)>THRESHOLD_DANGLING:
                        mergeBelow.append(index)
                    
            # Merge
            for index in numericLines:
                colsToMerge=[index]
                if index in mergeAbove:
                    colsToMerge.append(index-1)
                if index in mergeBelow:
                    colsToMerge.append(index+1)
                colsToMerge.sort()
                
                line=['']*len(content[index][:])
    
                #print(colsToMerge)
                # test
                #colsToMerge=[index]
                
                for j in colsToMerge:
                    #if j in headerLineIndices:
                    
                    for i in range(len(line)):
                        if i in headerLineIndices:
                            line[i]=content[index,i]
                            continue
                            
                        line[i]+=content[j,i]
                    
                output.append(line)
            
            
        elif self.getOrientation()==TABLE_ORIENTATION_HORIZONTAL:    
            
                # additional tests for numeric columns
                
                numericColumns=[]
                danglingColumns=[]
                for j in range(content.shape[1]): 
                    matches_dang=0
                    matches_num=0
                    for i in range(content.shape[0]):
                        if ')' in content[i][j] and not  re.match(pattern_num,content[i][j]):
                        
                            matches_dang+=1
                        if re.match(pattern_num,content[i][j]):
                            matches_num+=1
                    if float(matches_dang)/content.shape[0]>THRESHOLD_DANGLING:
                        danglingColumns.append(j)
                    if float(matches_num)/content.shape[0]>THRESHOLD_NUMERIC_COLUMN:
                        numericColumns.append(j)

                
                #print(danglingColumns)
                
                
                for i in numericLines:
                    #line = content[:,index]
                    line = content[i,:]
                    #print(line)
                    for j in range(content.shape[1]):
                        # Don't merge if line[j] is a header:
                        if j in headerLineIndices:
                            continue
                        if j+1 in danglingColumns and j in numericColumns:
                            line[j]+=line[j+1]
                            line[j+1]=u''
                            
                    output.append(line)
        
        else:
            raise Exception('Table _orientation could not be determined.')
        
        # Finally: Parse the actual numbers of combined cells
        # Additionally: Extract footnotes, units, etc
        numOutput = np.zeros_like(output,dtype=float)
        unitSpecifiers = np.zeros_like(output,dtype=object)
        unitSpecifiers.fill('')
        footNotes = np.zeros_like(output,dtype=object)
        footNotes.fill('')
        # regex number (possibly enclosed in parentheses), 
        # unit specifier, and footnotes
        # groups:
        # 1: left bracket
        # 2: number
        # 3: right bracket
        # 4: unit specifier
        # 5: footnote TODO: check
        gr_sign=1
        gr_left_bracket=2
        gr_number=3
        gr_right_bracket=4
        gr_unit_specifier=5
        gr_footnote=6
        pattern_entry = re.compile('([+-]?)(\(?)([0-9]*[\.][0-9]+|[0-9]+[,][,0-9]+|[0-9]+)(\)?)\s?([\%$]?)\s?([0-9A-Za-z\(\)\s]*)')
        
        
        for i in range(len(output)):
            item = output[i]
            for j in range(len(output[0])):
                match = re.search(pattern_entry,item[j])
                if match:
                    numOutput[i,j]=float(match.group(gr_sign) + match.group(gr_number).replace(',',''))
                    if '(' in match.group(gr_left_bracket) and ')' in match.group(gr_right_bracket):
                        numOutput[i,j]*=-1
                    if match.group(gr_unit_specifier):
                        unitSpecifiers[i,j]=match.group(gr_unit_specifier)
                    if match.group(gr_footnote):
                        footNotes[i,j]=match.group(gr_footnote)
                else:
                    numOutput[i,j]=np.nan
                
        #print(footNotes)
        data = {}
        data['numerical']=numOutput
        data['units']=unitSpecifiers
        data['footnotes']=footNotes
        data['headerIndices']=headerLineIndices
        data['numericalIndices']=numericLines
        data['content']=content
        data['nodes']=nodes
        
        self._dataDict = data
        
        return data
    
    def getNumericValues(self):
    
        data = self._internalExtractDataDict()
        
        return data['numerical']
      
    def getNumericHeaders(self):
        '''
            returns the headers for either a column or a row (depending on table _orientation) of several items. E.g.,
            
                    "Year ending 12/31/2016" <- numeric header
            item a    1234
            item b    2345
            item c    12
        '''
        data = self._internalExtractDataDict()
        
        numericIndices=data['numericalIndices']
        headerLineIndices=data['headerIndices']
        content=data['content']
        tmp = content[numericIndices,:]
        tmp = tmp[:,headerLineIndices]
        
        # test: extra header items:
        extraIndices=[]
        for i in numericIndices:
            if (i-1) not in numericIndices:
                extraIndices.append(i-1)
        
        tmpExtra=content[extraIndices,:]
        tmpExtra=tmpExtra[:,headerLineIndices]        
        #print(tmpExtra)
        
        # flatten array and filter out non-ascii characters 
        tmp = [' '.join(x) for x in tmp]
        tmp = [re.sub(r'[^\x00-\x7F]',' ', x) for x in tmp]
        
        # number of headers should match the number of 
        # numeric columns
        if len(numericIndices)!=len(tmp):
            tmp=[]

        return tmp
     
    def getFootnotes(self):
        
        data = self._internalExtractDataDict()
        
        return data['footnotes']
    
    def getUnits(self):
        
        data = self._internalExtractDataDict()
        
        return data['units']
    
         
    def extractFeatures(self,indexFrom=0,indexTo=None):
        items={}
        
        
        string_data, itemHeaders, itemNodes, rowHeaderIndex = self._internalGetItemHeaders()
 


        # 1) words
        items['words'] = [x for x in itemHeaders[0][indexFrom:indexTo]]
        items['str_size'] = [len(x) for x in itemHeaders[0][indexFrom:indexTo]]
        #print(items['words'])
        #print(items['str_size'])
         
      
        items['word.lower']=[item.lower() for item in items['words']]
        items['word.isupper']=[item.isupper() for item in items['words']]
        items['word.istitle']=[item.istitle() for item in items['words']]



    
      
        



        dataDict = self._internalExtractDataDict()
        numValues = dataDict['numerical']
        numNodes = []
        # 2) rows that might me header items:
        emptyRows=[1 if x=='' and y !="" else 0  for x,y in zip(numValues[0],itemHeaders[0])]
        items['rows']= emptyRows[indexFrom:indexTo]
        
        # 3) Class tags, dividing items by share class
        classTags=[]
        pattern = re.compile('Class [0-9]+|Class [A-Z]|Investor Class|Advisor Class|Institutional Class', flags=re.IGNORECASE)
        #print('regex')
        for item in items['words']:
            #print(item)
            out = re.search(pattern,item)
            if out:
                classTags.append(out.group(0))
            else:
                classTags.append("")
        items['class']=classTags 
        
        return items
        

                
    
    def getGroundTruth(self):
        
        if self.getOrientation()==TABLE_ORIENTATION_VERTICAL:
            return [self.getEntry(i, 0).groundTruthClassification if self.getEntry(i, 0) else ('undefined','') for i in self._getRowIndices() ]
        else:
            # for the 'horizontal case' the row the annotation is in is not fixed. It'll be 
            # in a row with a maximum number of cells. Here, we simply search for it:
            gt_row_index=-1
            for ri in range(0,max(self._getRowIndices())):
                for ci in range(1,max(self._getColumnIndices())):
                    entry = self.getEntry(ri, ci)
                    if entry and entry.groundTruthClassification:
                        if entry.groundTruthClassification[0]!='undefined':
                            gt_row_index=ri;
                            break;
            if gt_row_index==-1:
                # not annotated, any row will do:
                gt_row_index=1
            
            return [self.getEntry(gt_row_index, i).groundTruthClassification if self.getEntry(gt_row_index, i) else ('undefined','') for i in self._getColumnIndices()]
