'''
Created on 13.01.2017

@author: michael

Test: check orientation detection for selected documents against GT.
Throws an exception if an error occurs.
'''



from parse_ncsr_backend.ncsr_table_parsing import parse_ncsr_tables_raw, create_table
from definitions import TESTDATA_DIR
import os


filenames=['4-annotated.html','3-annotated.html','5-annotated.html',
           'NCSR_113580_ANNUAL_119312514072484_Dodge-&-Cox-Stock-annotated.html',
           'NCSR_225400_ANNUAL_119312514457852_GS-Large-Cap-Growth-Insights-annotated.html',
           'NCSR_234580_ANNUAL_119312514457852_GS-Intl-Small-Cap-annotated.html',
           'NCSR_145400_ANNUAL_119312515077297_Oppenheimer_Equity-annotated.html']
 
orientation_soo=['v','v','v','v','v','v','v']
orientation_fh =['v','v','h','v','h','h','v']


filenames=[]

if False:
    for i in range(len(filenames)):
        data = parse_ncsr_tables_raw(os.path.join(TESTDATA_DIR,filenames[i]),'fh_table')
        t = create_table(data)
        o = t[0].getOrientation()
        print(filenames[i])
        print(o)
        if o[0]!=orientation_fh[i]:
            raise Exception('Fail for ' + filenames[i])
if True:    
    for i in range(len(filenames)):
        data = parse_ncsr_tables_raw(os.path.join(TESTDATA_DIR,filenames[i]),'soo_table')
        t = create_table(data)
        o = t[0].getOrientation()
        print(filenames[i])
        print(o)
        if o[0]!=orientation_soo[i]:
            raise Exception('Fail for ' + filenames[i])
    
    