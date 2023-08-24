'''
Created on 13.01.2017

@author: michael

Test: output the first items from the row headers for control (for several documents)
'''


from parse_ncsr_backend.ncsr_table_parsing import parse_ncsr_tables_raw, create_table
from definitions import TESTDATA_DIR
import os


filenames=['4-annotated.html','3-annotated.html','5-annotated.html',
           'NCSR_113580_ANNUAL_119312514072484_Dodge-&-Cox-Stock-annotated.html',
           'NCSR_225400_ANNUAL_119312514457852_GS-Large-Cap-Growth-Insights-annotated.html',
           'NCSR_234580_ANNUAL_119312514457852_GS-Intl-Small-Cap-annotated.html']



print('----- FH -------')
for i in range(len(filenames)):
    data = parse_ncsr_tables_raw(os.path.join(TESTDATA_DIR,filenames[i]),'fh_table')
    t = create_table(data)
    itemHeaders = t[0].getRowHeaderColumns()
    itemHeaders = [x for x in itemHeaders if x!="" ]
    print(filenames[i])
    print(itemHeaders[0:5])
    print('')
#     if o[0]!=orientation_fh[i]:
#         raise Exception('Fail for ' + filenames[i])
#
print('----- SoO -------')     
for i in range(len(filenames)):
    data = parse_ncsr_tables_raw(os.path.join(TESTDATA_DIR,filenames[i]),'soo_table')
    t = create_table(data)
    itemHeaders = t[0].getRowHeaderColumns()
    itemHeaders = [x for x in itemHeaders if x!="" ]
    print(filenames[i])
    print(itemHeaders[0:5])
    print('')
#     o = t[0].getOrientation()
#     print(o)
#     if o[0]!=orientation_soo[i]:
#         raise Exception('Fail for ' + filenames[i])
#     
    