'''
Created on 18.02.2017

@author: michael
'''
from numpy import isnan
from collections import OrderedDict
from definitions import NCSR_CLF_ID_NAME




def classifier_json_output(predicted, values, confidence,columnHeaders, strings, tableRowIDs=None):

 
    # Check columnHeaders for uniqueness.
    # If a header is not unique, add a prefix
    if len(set(columnHeaders))!=len(columnHeaders):
        seen=[]
        for i in range(len(columnHeaders)):
            seen.append(columnHeaders[i].replace(" ",""))
            columnHeaders[i] = "Fund #" + str(seen.count(columnHeaders[i].replace(" ",""))) + " " + columnHeaders[i]

    result = OrderedDict()
    numFunds=len(values[0])
    for fundIndex in range(numFunds):
        #print('FH table number - ',table_num)
        result_part=OrderedDict()       
        hasShareClasses=False
        for index in range(len(predicted)):
            # TODO: second level classification is not included here!
            shareClass=''
            # Leave out empty entries:
            if predicted[index][0]=='empty' or predicted[index][0]=='undefined':
                continue
            if all(isnan(values[index,:])):
                tmp = [predicted[index][0],'',strings[index]]
                
            else:
                tmp=[predicted[index][0],str(values[index][fundIndex]),strings[index]]
            
            # Append second-level classification (e.g. "Class X"):
            if predicted[index][1] != '':
                # remember:
                hasShareClasses=True
                shareClass=predicted[index][1]
                #tmp[0]+=', ' + predicted[index][1]
            else:
                # reset (TODO testing)
                hasShareClasses=False
                
            if True:
                if index < len(confidence):
                    tmp.append(confidence[index])
                else:
                    tmp.append("")
 
            key = tmp[0].split('//')

            if len(key)>3:
                raise Exception('Keys with more than 3 parts not implemented')            
            # TODO: possible to use reflections or sth similar?
            l = len(key)
            if l>=1 and key[0] not in result_part:
                result_part[key[0]]=OrderedDict()
            if l>=2 and key[1] not in result_part[key[0]]:
                result_part[key[0]][key[1]]=OrderedDict()
            if l>=3 and key[2] not in result_part[key[0]][key[1]]:
                result_part[key[0]][key[1]][key[2]]=OrderedDict()
            
            SHARECLASS_KEY='Shareclasses'
            if hasShareClasses:
                if l==2:
                    # add dict for shareclasses
                    if not result_part[key[0]][key[1]].has_key(SHARECLASS_KEY):
                        result_part[key[0]][key[1]][SHARECLASS_KEY]=OrderedDict()
                        
                    # add dict for the current shareclass:
                    if not result_part[key[0]][key[1]][SHARECLASS_KEY].has_key(shareClass):
                        result_part[key[0]][key[1]][SHARECLASS_KEY][shareClass]=OrderedDict()
                    
                    result_part[key[0]][key[1]][SHARECLASS_KEY][shareClass]['amount'] = tmp[1]
                    result_part[key[0]][key[1]][SHARECLASS_KEY][shareClass]['clfInput'] = tmp[2]   
                    result_part[key[0]][key[1]][SHARECLASS_KEY][shareClass]['confidence'] = confidence[index] if index < len(confidence) else ""
                    if tableRowIDs:
                        result_part[key[0]][key[1]][SHARECLASS_KEY][shareClass][NCSR_CLF_ID_NAME]=tableRowIDs[index]
                            
                if l==3:
                    # add dict for shareclasses:
                    if not result_part[key[0]][key[1]][key[2]].has_key(SHARECLASS_KEY):
                        result_part[key[0]][key[1]][key[2]][SHARECLASS_KEY]=OrderedDict()
                    # add dict for the current shareclass:
                    if not result_part[key[0]][key[1]][key[2]][SHARECLASS_KEY].has_key(shareClass):
                        result_part[key[0]][key[1]][key[2]][SHARECLASS_KEY][shareClass]=OrderedDict()
                    
                    result_part[key[0]][key[1]][key[2]][SHARECLASS_KEY][shareClass]['amount'] = tmp[1]   
                    result_part[key[0]][key[1]][key[2]][SHARECLASS_KEY][shareClass]['clfInput'] = tmp[2]
                    result_part[key[0]][key[1]][key[2]][SHARECLASS_KEY][shareClass]['confidence'] = confidence[index] if index < len(confidence) else ""    
                    if tableRowIDs:
                        result_part[key[0]][key[1]][key[2]][SHARECLASS_KEY][shareClass][NCSR_CLF_ID_NAME]=tableRowIDs[index]
            else:
                if l==1:
                    if not result_part[key[0]].has_key(SHARECLASS_KEY):
                        result_part[key[0]][SHARECLASS_KEY]=OrderedDict()
                    result_part[key[0]]['amount'] = tmp[1]
                    result_part[key[0]]['clfInput'] = tmp[2]
                    result_part[key[0]]['confidence'] = confidence[index] if index < len(confidence) else ""
                    if tableRowIDs:
                        result_part[key[0]][NCSR_CLF_ID_NAME]=tableRowIDs[index]
                        
                if l==2:
                    if not result_part[key[0]][key[1]].has_key(SHARECLASS_KEY):
                        result_part[key[0]][key[1]][SHARECLASS_KEY]=OrderedDict()
                    result_part[key[0]][key[1]]['amount'] = tmp[1]   
                    result_part[key[0]][key[1]]['clfInput'] = tmp[2]   
                    result_part[key[0]][key[1]]['confidence'] = confidence[index] if index < len(confidence) else ""
                    if tableRowIDs:
                        result_part[key[0]][key[1]][NCSR_CLF_ID_NAME]=tableRowIDs[index]    
                if l==3:
                    if not result_part[key[0]][key[1]][key[2]].has_key(SHARECLASS_KEY):
                        result_part[key[0]][key[1]][key[2]][SHARECLASS_KEY]=OrderedDict()
                    result_part[key[0]][key[1]][key[2]]['amount'] = tmp[1]   
                    result_part[key[0]][key[1]][key[2]]['clfInput'] = tmp[2]
                    result_part[key[0]][key[1]][key[2]]['confidence'] = confidence[index] if index < len(confidence) else ""
                    if tableRowIDs:
                        result_part[key[0]][key[1]][key[2]][NCSR_CLF_ID_NAME]=tableRowIDs[index]    
                    
            previous_key = key
            
        fund_name = "portfolio" if columnHeaders[fundIndex]=='' else columnHeaders[fundIndex]

        if fund_name in result.keys():
            raise Exception("Key already in dict")
            

        result[fund_name]=result_part   
    
    return result


