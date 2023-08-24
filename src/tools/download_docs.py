'''
Created on 04.03.2017

@author: michael
'''

import csv
import requests
import os

from definitions import DATA_DIR
import lxml.html
import time



CSV_FILE='NCSR_report_list_Top20_Managers.csv'
OUTPUT_DIR='/home/michael/test'


company='Oppenheimer'
indices=range(0,10)



data=[]
with open(os.path.join(DATA_DIR,CSV_FILE),'r') as f:
    reader = csv.reader(f) 
    for row in reader:
        if row[1].startswith(company): 
            data.append(row)


for index in indices:
    current = data[index]
    
    url=current[5]
    outputname='NCSR_' + current[0] +'_' + current[2] +'_'+ current[4] + '_' + current[1]+'.html'
    outputname=outputname.replace(' ','_').replace('/','_')
    
    print('Fetching ' + outputname)
    r = requests.get(url)
    tmp = lxml.html.fromstring(r.content)
   
    frames=tmp.xpath('//frame')
    doc_identifier = frames[1].attrib['src']
    r.close()
    
    full_url = 'http://simfundfiling.com/' + doc_identifier
    try:
        r = requests.get(full_url, timeout=2)
        if len(r.content)>0:
            print('writing')
            
            with open(os.path.join(OUTPUT_DIR,outputname),'w') as f:
                f.write(r.content)
        else:
            print(len(r.content))
            
    except Exception as e:
        print(e.value)
        continue
    finally:
        r.close()
        
    time.sleep(2)