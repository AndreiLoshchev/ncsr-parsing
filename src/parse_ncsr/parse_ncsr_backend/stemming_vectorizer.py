'''
Created on 28.09.2016

@author: michael
'''
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, HashingVectorizer




def getVectorizer(token_pat='alphaonly', use_stemming=True, useIDF=False):

    # default token_pattern of CountVectorizer is u'(?u)\\b\\w\\w+\\b',
    # which will also tokenize numbers. The pattern used for 'alphaonly' will 
    # disregard numbers and underscores
    #stop_words = frozenset(["of ", " and ","by","as a","to"])
    if token_pat=='alphaonly':
        analyzer = CountVectorizer(token_pattern=u'(?u)\\b[^\W\d_][^\W\d_]+\\b|:').build_analyzer()
        #analyzer = TfidfVectorizer(token_pattern=u'(?u)\\b[^\W\d_][^\W\d_]+\\b|:').build_analyzer()
        #analyzer = HashingVectorizer(token_pattern=u'(?u)\\b[^\W\d_][^\W\d_]+\\b|:').build_analyzer()
    else:
        analyzer = CountVectorizer().build_analyzer()
        #analyzer=TfidfVectorizer().build_analyzer()
        #analyzer = HashingVectorizer().build_analyzer()
    stemmer = PorterStemmer()
    
    def stemmed_words(doc):
        if use_stemming:
            return (stemmer.stem(w) for w in analyzer(doc))
        else:
            return (w for w in analyzer(doc))
        
    vect = CountVectorizer(analyzer=stemmed_words)
    #vect = TfidfVectorizer(analyzer=stemmed_words)
    #vect = HashingVectorizer(analyzer=stemmed_words)
    return vect

def getVectorizer1(token_pat='alphaonly', use_stemming=True, useIDF=False):

    # default token_pattern of CountVectorizer is u'(?u)\\b\\w\\w+\\b',
    # which will also tokenize numbers. The pattern used for 'alphaonly' will 
    # disregard numbers and underscores
    from sklearn.feature_extraction import text 

    stop_words = text.ENGLISH_STOP_WORDS#.union(my_additional_stop_words)
    stop_words = frozenset(["of", "and","by","as a","to","affilliates",
    "ratio of","(as a percentage of average daily net assets):","gross",
    "to average net assets","reductions","(f)","total","(5)","(loss)","to","on","loss"])
    if token_pat=='alphaonly':
        analyzer = CountVectorizer(token_pattern=u'(?u)\\b[^\W\d_][^\W\d_]+\\b|:').build_analyzer()
        #analyzer = TfidfVectorizer(token_pattern=u'(?u)\\b[^\W\d_][^\W\d_]+\\b|:').build_analyzer()
        #analyzer = HashingVectorizer(token_pattern=u'(?u)\\b[^\W\d_][^\W\d_]+\\b|:').build_analyzer()
    else:
        analyzer = CountVectorizer().build_analyzer()
        #analyzer=TfidfVectorizer().build_analyzer()
        #analyzer = HashingVectorizer().build_analyzer()
    stemmer = PorterStemmer()
    
    def stemmed_words(doc):
        if use_stemming:
            return (stemmer.stem(w) for w in analyzer(doc))
        else:
            return (w for w in analyzer(doc))
        
    vect = CountVectorizer(analyzer=stemmed_words)
    #vect = TfidfVectorizer(analyzer=stemmed_words)
    #vect = HashingVectorizer(analyzer=stemmed_words)
    return vect
