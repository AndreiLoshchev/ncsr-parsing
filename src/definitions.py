'''
Created on 20.09.2016

@author: michael.fieseler@gmail.com
'''

import os
import glob2, glob

ROOT_DIR=os.path.dirname(os.path.abspath(__file__))
DATA_DIR=os.path.join(os.path.split(ROOT_DIR)[0],'data')
TESTDATA_DIR=os.path.join(os.path.split(ROOT_DIR)[0],'testdata','ncsr-data')

BATCH100 = os.path.join(os.path.split(ROOT_DIR)[0],'testdata','batch100')
BATCH100_TEST = os.path.join(os.path.split(ROOT_DIR)[0],'testdata','batch100_test')
BATCH200 = os.path.join(os.path.split(ROOT_DIR)[0],'testdata','batch200')
BATCH300 = os.path.join(os.path.split(ROOT_DIR)[0],'testdata','batch300')

SOO_EXPENSE_SYNOYMS_FILENAME='SoO_expense_synonyms.json'
SOO_INCOME_SYNOYMS_FILENAME ='SoO_income_synonyms.json'
SOO_GAINLOSS_SYNONYMS_FILENAME='SoO_gainloss_synonyms.json'
SOO_SECTION_KEYWORDS_FILENAME='SoO_section_keywords.json'

NCSR_CLF_ID_NAME='ncsr-classification-id'
TABLE_DETECTION_CONFIDENCE_NAME='table-detection-confidence'

ANNOTATED_FILENAMES1=glob2.glob(os.path.join("project/testdata/man/*-annotated.html"))#glob2.glob('project/testdata/ncsr-data/*-annotated.html')
#print(ANNOTATED_FILENAMES)
ANNOTATED_FILENAMES=glob2.glob(os.path.join("project/testdata/ncsr-data/*-annotated.html"))
ANNOTATED_BATCH100=glob.glob(os.path.join(BATCH100,"*-annotated.html"))
ANNOTATED_BATCH200=glob.glob(os.path.join(BATCH200,"*-annotated.html"))
ANNOTATED_BATCH300=glob.glob(os.path.join(BATCH300,"*-annotated.html"))

ALL =glob2.glob('/Users/salimmjahad/ncsr-data-3/group0001//**/*-annotated.html')

AVOID_FILES=['NCSR_274690_ANNUAL_95012315000008_Schwab-Dividend-Equity-annotated.html',
             'NCSR_776948_ANNUAL_5193114001428_American-College-2021-annotated.html',
             'NCSR_113570_ANNUAL_119312513079756_Dodge-&-Cox-Income-Fund-annotated.html',
             'NCSR_259790_ANNUAL_119312514072484_Dodge-&-Cox-Intl-Stock-annotated.html',
             'NCSR_776952_ANNUAL_5193114001428_American-College-Enrollment-annotated.html',
             'NCSR_160140_ANNUAL_119312514425343_Wells-Fgo-Idx-Ast-Alloc-annotated.html',
             'NCSR_223650_ANNUAL_119312514391940_GS-FnclSq-Treasury-Instr-MM-annotated.html',
             'NCSR_777013_ANNUAL_95012315000008_Schwab-Target-2045-annotated.html',
             'NCSR_113560_ANNUAL_119312513079756_Dodge-&-Cox-Balanced-annotated.html']


# Filename to serialize 
CRF_SOO_SERIALIZED_FILENAME=os.path.join(DATA_DIR,'crf_data_soo.p')
CRF_FH_SERIALIZED_FILENAME=os.path.join(DATA_DIR,'crf_data_fh.p')
NSCR_REPORTS_FULL_FILE='ncsr_reports_data_full.p'





