# -*- coding: utf-8 -*-
''' Provides methods for loading / parsing of tables in NCSR reports

Created on 22.09.2016

@author: michael.fieseler@gmail.com
'''
  
from __future__ import print_function
import string
import os
import re
import sys
import math
import lxml.html
import glob2, glob

import numpy as np 
import cssutils
#import cPickle as pickle
import dill
import copy
from ncsrtable.table import Table
from ncsrtable.tableEntry import TableEntry
from definitions import DATA_DIR, ANNOTATED_FILENAMES,ANNOTATED_FILENAMES1, NCSR_CLF_ID_NAME
import logging

from definitions import ALL
import random
random.shuffle(ALL)


NumCharacters = set(string.digits + u',' + u'.' + u')' + u'(' +  u'-' + u'+' + u'%' + u'$' + u'€') 

cssutils.log.setLevel(logging.CRITICAL)
 
DEBUG=False 
    
def get_lxml_from_string(s):
    
    s = re.sub('<select class="soo_.*?</select>',''     ,s ,flags=re.DOTALL)
    s = re.sub('<select class="fh_.*?</select>',''      ,s ,flags=re.DOTALL)
    s = re.sub('<select class="sal_.*?</select>',''     ,s ,flags=re.DOTALL)
    s = re.sub('<select class="scna_.*?</select>',''    ,s ,flags=re.DOTALL)
    s = re.sub('<select class="soo_plus_.*?</select>','',s ,flags=re.DOTALL)
    s = re.sub('<select class="ncsr_table_type.*?</select>','',s ,flags=re.DOTALL)
    s = re.sub(r'\\' + 'xa0', ' ', s)
    s = re.sub(u'&nbsp;', ' ',s)

    tree = lxml.html.fromstring(s)
    for item in tree.xpath('.//table'):
        if 'border' in item.keys():
            item.attrib.pop('border')
    return tree
    
def parse_ncsr_tables_raw(tree, tableType):
    '''Parse NCSR report from HTML file.
    
    tree - a lxml.html tree
    tableType - table type to extract ("soo_table" | "fh_table")'''
#########################CHANGES##############################
    if tree is None:
        print('ups')
    
    xpath_expr = '//table[@class="' + tableType + '"]'

    data=[]
    ncsr_tables = tree.xpath(xpath_expr)
    for i in range(len(ncsr_tables[:1])):

        if len(ncsr_tables) == 0:
            raise Exception("Could not find required mark 'class=" + tableType)
            sys.exit(1)
        
        d = parse_ncsr_tables_raw_tag(ncsr_tables[i], tableType)
        data.append(d)
    if DEBUG:    
        print('len tables: ' + str(len(data)))
    return data

def parse_ncsr_tables_raw_test(tree, tableType):
    '''Parse NCSR report from HTML file.'''
    
    if tree is None:
        print('ups')
    
    xpath_expr = '//table[@class="' + tableType + '"]'

    ncsr_tables = tree.xpath(xpath_expr)
    
    if len(ncsr_tables) == 0:
        raise Exception("Could not find required mark 'class=" + tableType)
        sys.exit(1)
    
    data1 = parse_ncsr_tables_raw_tag(ncsr_tables, tableType)


    return data1
##############################################################


def parse_ncsr_tables_raw_tag(ncsr_table, tableType):
    ''' Parse SOO / FH table '''
    
    featureDictTemplate={'text-align:center':0,'text-align:left':0,'text-align:right':0,
             'font-weight:normal':0,'font-weight:bold':0,'font-weight:bolder':0,'font-weight:lighter':0,
             'border-bottom:pos':0,
             'text-indent:neg':0, 'text-indent:pos':0,
             'isNumeric':0,'isText':0,'isEmpty':0,'isTotal':0,
             'isMerged':0,
             'endsWithColon':0,'endsWithFrom':0,'endsWithOn':0}  
     
    result={}
    
    result['stringData']    =[]
    result['groundTruth']   =[]
    result['groundTruth_horizontal']=[]
    result['htmlLinks']     =[]
    result['_features']      =[]
    result['featureHeaders']=[]
    result['cellHeights']   =[]
    result['cellWidths']    =[]
    result['featureDicts']  =[]
    

    cellWidths =  []
    cellHeights = []

    
    # Determine maximum column length
    rowData = ncsr_table.xpath('.//tr')
             
    numCols = 0
    for row in rowData:
        if len(row.xpath('.//td')) >= numCols:
            numCols = len(row.xpath('.//td'))
            
    
    numRows = len(rowData);
    features=np.zeros([numRows,len(featureDictTemplate)], dtype=float)  
    
    stringData = np.zeros([len(rowData), numCols], dtype=object)
    stringData[:] = u""
    tablesGroundTruth = np.zeros([len(rowData),numCols], dtype=object)
    tablesGroundTruth.fill(None)
    
    
    featureDicts= np.zeros([len(rowData), numCols], dtype=object)
    htmlLinks = np.zeros([len(rowData), numCols], dtype=object)
    featureDicts.fill(None)
    
    
  
    ncsr_IDs=[]
    
    for r in range(numRows):
        row_cellWidths  =[]
        row_cellHeights =[]
        
        featureDict = {key:0 for key in featureDictTemplate}

     
                
            
        colData = rowData[r].xpath('.//td')
        colIndex=-1
    
        for c in range(len(colData)):
           
            colIndex+=1
            td_tag = colData[c]
            
            gtValue='undefined'
            gtValueSec=''

            if "soo_label" in td_tag.keys():
                gtValue=td_tag.attrib['soo_label']
            if "soo_label_sec" in td_tag.keys():
                gtValueSec=td_tag.attrib['soo_label_sec']
            if "fh_label" in td_tag.keys():
                gtValue=td_tag.attrib['fh_label']
            if "fh_label_sec" in td_tag.keys():
                gtValueSec=td_tag.attrib['fh_label_sec']    
            if "sal_label" in td_tag.keys():
                gtValue=td_tag.attrib['sal_label']
            if "sal_label_sec" in td_tag.keys():
                gtValueSec=td_tag.attrib['sal_label_sec']     
            if "scna_label" in td_tag.keys():
                gtValue=td_tag.attrib['scna_label']
            if "scna_label_sec" in td_tag.keys():
                gtValueSec=td_tag.attrib['scna_label_sec']     
            if "soo_plus_saa_label" in td_tag.keys():
                gtValue=td_tag.attrib['soo_plus_saa_label']
            if "soo_plus_saa_label_sec" in td_tag.keys():
                gtValueSec=td_tag.attrib['soo_plus_saa_label_sec'] 
               
            tablesGroundTruth[r,c]=(gtValue,gtValueSec) 
            
            htmlLinks[r,c]=colData[c]
            #htmlLinks[r,c]=copy.copy(colData[c])
            
            if 'colspan' in td_tag.keys():
                row_cellWidths.append(int(td_tag.attrib['colspan']))
            else:
                row_cellWidths.append(1)
            if 'rowspan' in td_tag.keys():
                row_cellHeights.append(int(td_tag.attrib['rowspan']))
            else:
                row_cellHeights.append(1)
 
            value=colData[colIndex].xpath('.//text()')
            if len(value)>0:
                value = string.join([x.strip() for x in value]).strip()
            else:
                value=''


            tag_align = -1 # left (default)   
            if True:
                s=[]
                try:
                    s = cssutils.parseStyle(td_tag.attrib['style'])
                except KeyError:
                    pass
#                 if 'text-align' in s.keys():
#                     print(s['text-align'])
                if s:
                    for tableIndex, item in enumerate(s.keys()):
                        val = s[item]
                        numericVal = re.search('([-]?[0-9.]+)([A-Za-z]+)',val)
                        key=''
                        if numericVal:
                            if float(numericVal.group(1))>0:
                                key=item+":pos"
                            elif float(numericVal.group(1))<0:
                                key=item+":neg"
                            
                        else:
                            key=item+":"+val
                        
                        try:
                            featureDict[key]+=1
                            #print(featureDict[key])
                        except KeyError:
                                pass    
                        
        
            colspan=1
            
            tag_align=0
            if 'colspan' in td_tag.keys():
                colspan=int(td_tag.attrib['colspan'])
            if colspan>1 and tag_align>0:
                colIndex+=(colspan-1)   
               
            stringData[r, c] = value
            
            # additional _features:
            if value.strip()!='':
                if set(value.strip())<NumCharacters:
                    featureDict['isNumeric']+=1   
                else:
                    featureDict['isText']+=1
                #  'endWithColon':0,'endsWithFrom':0,'endsWithOn':0
                if re.search(':',value):
                    featureDict['endsWithColon']+=1 # not quite precise
                if re.search('from',value,re.IGNORECASE):
                    featureDict['endsWithFrom']+=1
                if re.search('on',value,re.IGNORECASE):
                    featureDict['endsWithOn']+=1
            else:
                featureDict['isEmpty']+=1    
            if re.search('total',value.strip(),re.IGNORECASE):
                featureDict['isTotal']+=1
            if 'colspan' in td_tag.keys():
                featureDict['isMerged']+=1  
            
            if tag_align<0:
                colIndex+=(colspan-1)
         
            
            featureDicts[r,c]=featureDict
        # end of col loop
        # logarithmic binning], see Adelfio 2013
        # cval := numbers of cells that exhibit a feature
        # rval := numbers of cells in a row
        for tableIndex,key in enumerate(sorted(featureDict)):
            cval = float(featureDict[key])
            rval = float(numCols)
            
            if cval==0:
                a=0
            elif cval<rval/2:
                a=math.floor(math.log(cval,2)+1)
            elif cval<rval:
                a=math.floor(math.log(rval-cval)+1)
            elif cval==rval:
                a=0
            features[r,tableIndex]=a
        
        cellWidths.append(row_cellWidths)
        cellHeights.append(row_cellHeights)
            
    # end of row loop
        
    featureHeaders=sorted(featureDict)
    result['stringData']=stringData
    result['groundTruth']=tablesGroundTruth
    
    result['htmlLinks']=htmlLinks
    result['_features']=features
    result['featureHeaders']=featureHeaders
    
    result['cellWidths']=cellWidths
    result['cellHeights']=cellHeights
    
    result['featureDicts']=featureDicts
    
           
    return result


def create_table(listOfResultDicts):
    
    tables=[]
    
    for resultDict in listOfResultDicts:
        
        stringData =        resultDict['stringData']
        tablesGroundTruth = resultDict['groundTruth']
        features =          resultDict['_features']
        featureHeaders =    resultDict['featureHeaders']
        cellWidths =        resultDict['cellWidths']
        cellHeights=        resultDict['cellHeights']
        featureDicts=       resultDict['featureDicts']
        htmlLinks=          resultDict['htmlLinks']
        #numRows, numCols = stringData.shape  
        table = Table()
        table._features = features
        
        if 'sourceFileName' in resultDict.keys():
            table.sourceFileName = resultDict['sourceFileName']
        
        # create respective table entries:
        for row in range(len(cellWidths)):
        #for row in len()
            for col in range(len(cellWidths[row])):
                value = stringData[row][col]
                entry = TableEntry(cellWidths[row][col], cellHeights[row][col])
                entry.setContent(value)
                entry.featureDict=featureDicts[row][col]
                entry.groundTruthClassification=tablesGroundTruth[row,col]
            
                entry.htmlLink=htmlLinks[row,col]
                    
                table.setEntry(row,col,entry)
            
         
        table.featureHeaders=featureHeaders
        table.htmlDOM = resultDict['htmlLinks']
        
        tables.append(table)
        # end of loop over input lists
        
    return tables
    
    
'''Load annotated table data, SoO section'''
def load_table_data(tableClass, reparse=True):

    tables=[]
    tableSaveDataFilename=os.path.join(DATA_DIR, tableClass + ".p")
    if os.path.isfile(tableSaveDataFilename) and not reparse:
        tables=dill.load(open(tableSaveDataFilename,'rb'))
    else:
        print('Extracting from ' + str(len(ALL)) + ' documents:')
        for counter,filename in enumerate(ALL):
            if 'Vanguard_Long_Bond_Index-annotated' in filename:
                print('Skipping problematic table: ' + filename)
                continue
            print(str(counter) + ' of ' + str(len(ALL)))
            try:
                with open(filename,'r') as f:
                    s = f.read()
                    
                html = get_lxml_from_string(s)
 
                allTables=html.xpath('.//table')
                
                tableTypes = []
                for table in allTables:
                    cl = table.classes
                    if "soo_table_cont" in cl:
                        tableTypes.append("soo_table_cont")
                    elif "fh_table_cont" in cl:
                        tableTypes.append("fh_table_cont")
                    elif "soo_table" in cl:
                        tableTypes.append("soo_table")
                    elif "fh_table" in cl:
                        tableTypes.append("fh_table")
                    elif "sal_table_cont" in cl:
                        tableTypes.append("sal_table_cont")
                    elif "scna_table_cont" in cl:
                        tableTypes.append("scna_table_cont")
                    elif "sal_table" in cl:
                        tableTypes.append("sal_table")
                    elif "scna_table" in cl:
                        tableTypes.append("scna_table")
                    elif "soo_plus_saa_table" in cl:
                        tableTypes.append("soo_plus_saa_table")
                    else:
                        tableTypes.append('other')
                               
                indicesCurrentType = [i for i,val in enumerate(tableTypes) if val==tableClass]
                indicesContdCurrentType = [i for i,val in enumerate(tableTypes) if val==tableClass+"_cont"]
                 
                tableData = parse_ncsr_tables_raw(html, tableClass)
                
                tables_tmp = create_table(tableData)
                 
                # if there is a continuation for the current table: (determined via set intersection)
                #    Merge the two parts
                tableDataContd = parse_ncsr_tables_raw(html, tableClass + "_cont")
                tables_tmp_contd = create_table(tableDataContd)
                
                # We got:
                # - indices of the current table type 
                # - indices of the cont_ variants of the current type
                # - a list 'cont_idx' that gives the index of the _cont'd table that has to be merged
                #
                # iterating over indices for current type:
                index_to_merge=0
                for i,idx_current in enumerate(indicesCurrentType):
                    if i<len(indicesCurrentType)-1:
                        cont_idx = list(set(range(idx_current+1,indicesCurrentType[i+1])) & set(indicesContdCurrentType))
                    else:
                        cont_idx=[]
                    # cont_idx contains the index of the cont'd table to be merged with the table in idx_current
                    if cont_idx:
                        tables_tmp[i].mergeTable(tables_tmp_contd[index_to_merge],'right')
                        index_to_merge+=1
                
                
                if len(tables_tmp[0].getGroundTruth())==len(tables_tmp[0].getItemHeaders()):     
                    tables.extend(tables_tmp)


                ####################################FOR THE ONE FIRST TABLE###############################################
                '''indicesCurrentType = [i for i,val in enumerate(tableTypes) if val==tableClass]
                indicesContdCurrentType = [i for i,val in enumerate(tableTypes) if val==tableClass+"_cont"]

             
                tableData = parse_ncsr_tables_raw_test(allTables[indicesCurrentType[0]], tableClass)
                tables_tmp = create_table(tableData)

                # if there is a cont'd table and it comes before the next table of the same type:

                if indicesContdCurrentType!=[] and (len(indicesCurrentType)==1 or indicesContdCurrentType[0]<indicesCurrentType[1]):
                    tableDataContd = parse_ncsr_tables_raw_test(allTables[indicesContdCurrentType[0]], tableClass + "_cont")

                    tables_tmp_contd = create_table(tableDataContd)
                    tables_tmp[0].mergeTable(tables_tmp_contd[0],'right')'''
                ############################################################################################################

                    
            except Exception as err:
                print("Table parsing: {0}".format(err))
                continue 
                  
            
        dill.dump(tables, open(tableSaveDataFilename,'wb')) 
    
    return tables



def main():
    filename="10-annotated.htm"
    tableData = parse_ncsr_tables_raw(filename, "soo_table")
    tables = create_table(tableData)
    
    tables[0].printTable()
    
    print(tables[0].getGroundTruth())

