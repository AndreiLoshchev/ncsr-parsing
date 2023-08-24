'''
Created on 19.12.2016

@author: michael
'''

import os
import re
import string
import numpy as np

from definitions import TESTDATA_DIR, BS_PARSER, DATA_DIR
from bs4 import BeautifulSoup

from definitions import ANNOTATED_FILENAMES
import glob
from parse_ncsr_backend.ncsr_table_parsing import parse_ncsr_tables_raw_tag,\
    create_table, load_table_data, parse_ncsr_tables_raw

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import nltk
# filenames=glob.glob(os.path.join(TESTDATA_DIR,"*-annotated.html"))
# 
# with open(os.path.join(DATA_DIR,'ner_test.txt')) as f:
#     document=f.read()
# #soup = BeautifulSoup(s, BS_PARSER)
# sentences = nltk.sent_tokenize(document.decode('utf-8'))
# sentences = [nltk.word_tokenize(sent) for sent in sentences] 
# sentences = [nltk.pos_tag(sent) for sent in sentences] 
# 
# grammar = "NP: {<DT>?<JJ>*<NN>}"
# cp = nltk.RegexpParser(grammar)
# result = cp.parse(sentences[0])
# print(result)


filename = os.path.join(TESTDATA_DIR,'2-annotated.html')
data = parse_ncsr_tables_raw(filename,"soo_table")



