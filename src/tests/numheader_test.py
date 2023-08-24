'''
Created on 13.01.2017

@author: michael

Test: extracts column headers from selected documents (if there are any).
Checks against GT if there should be column headers. Displays column headers for control.
'''



from parse_ncsr_backend.ncsr_table_parsing import parse_ncsr_tables_raw, create_table
from definitions import TESTDATA_DIR
import os


filenames=['4-annotated.html',
           '3-annotated.html',
           '5-annotated.html',
           'NCSR_113580_ANNUAL_119312514072484_Dodge-&-Cox-Stock-annotated.html',
           'NCSR_225400_ANNUAL_119312514457852_GS-Large-Cap-Growth-Insights-annotated.html',
           'NCSR_234580_ANNUAL_119312514457852_GS-Intl-Small-Cap-annotated.html']


has_col_headers_soo=[False,False,True,True,False,False]
has_col_headers_fh =[True,True,True,True,True,True]

fails_soo=[]
fails_fh=[]

print('----- FH -------')
for i in range(len(filenames)):
    data = parse_ncsr_tables_raw(os.path.join(TESTDATA_DIR,filenames[i]),'fh_table')
    t = create_table(data)
    itemHeaders = t[0].getColumnHeaders()
    itemHeaders = [x for x in itemHeaders if x!="" ]
    print(filenames[i])
    print(itemHeaders[0:5])
    if (itemHeaders!=[]) != has_col_headers_fh[i]:
        fails_fh.append(filenames[i])
        print('fail')
    print('')
#     if o[0]!=orientation_fh[i]:
#         raise Exception('Fail for ' + filenames[i])
#
print('----- SoO -------')     
for i in range(len(filenames)):
    data = parse_ncsr_tables_raw(os.path.join(TESTDATA_DIR,filenames[i]),'soo_table')
    t = create_table(data)
    itemHeaders = t[0].getColumnHeaders()
    itemHeaders = [x for x in itemHeaders if x!="" ]
    print(filenames[i])
    print(itemHeaders[0:5])
    if (itemHeaders!=[]) != has_col_headers_soo[i]:
        fails_soo.append(filenames[i])
        print('fail')
    print('')


print('----Summary:------')
print('Failed FH:')
for item in fails_fh:
    print(item)
print('---------')
print('Failed SoO:')
for item in fails_soo:
    print(item)