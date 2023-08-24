'''
Created on 26.01.2017

@author: mf
'''



import itertools

import numpy as np
from src.parse_ncsr_backend.ncsr_table_parsing import load_table_data

from sklearn.naive_bayes import MultinomialNB, BernoulliNB, GaussianNB
from src.parse_ncsr_backend.stemming_vectorizer import getVectorizer
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances, \
    manhattan_distances, pairwise_kernels, polynomial_kernel, rbf_kernel, \
    sigmoid_kernel, laplacian_kernel, additive_chi2_kernel, chi2_kernel, \
    pairwise_distances, euclidean_distances
import sklearn.svm
from numpy import hstack, vstack
from sklearn import svm
from sklearn.svm.classes import SVC, LinearSVC, SVR
from math import floor
from leven import levenshtein

tables = load_table_data("soo_table", False)

words = [t.getItemHeaders() for t in tables]
gt = [t.getGroundTruth() for t in tables]

variationDict = {}

for i in range(len(words)):
    currentWords = words[i]
    currentGT = gt[i]
    for j in range(len(currentWords)):
        currentKey = currentGT[j][0]
        if currentKey != u"" and currentKey != "undefined" and currentKey != "empty":
            
            if currentKey in variationDict.keys():
                if currentWords[j] not in variationDict[currentKey]:
                    variationDict[currentKey].append(currentWords[j])
            else:
                variationDict[currentKey] = [currentWords[j]]
                    


# Setup simple classifier /w stemming

def mylev(X, Y=None):
    if Y is None:
        Y = X
        # assume X is a vector and Y as well
        # output is is Y.shape x X.shape matrix
        # if min(X.shape)!=1 or min(Y.shape)!=1:
         
            # raise Exception()
    output = np.zeros((len(Y), len(X)), dtype=np.long)
    for i in range(len(Y)):
        for j in range(len(X)):
            output[i, j] = levenshtein(X[j], Y[i])
    return output
    
        
def mydist(X, Y=None):
    # pairwise_kernels: 0.71
    # euclid dist: 0.64
    # cosine sim 0.66
    # cosine dist 0.59
    if Y is None:
        return X 
    else:
        return Y

    if Y is None:
        tmp = cosine_similarity(X, Y)
        # tmp,
        # return X.toarray()
        return np.hstack((X.toarray(), tmp))
        # return np.hstack((X.toarray()))
    else:

        tmp = cosine_similarity(X, Y)

        return np.transpose(vstack((np.transpose(Y.toarray()), tmp)))
        # return (vstack((np.transpose(Y.toarray()))))
    
    
    
    if Y is None:
        return hstack((cosine_similarity(X, Y), pairwise_kernels(X, Y)))
    else:
        return np.transpose(vstack((cosine_similarity(X, Y), pairwise_kernels(X, Y))))
    

def mydist2(X, X_words, Y=None, y_words=None):
    # pairwise_kernels: 0.71
    # euclid dist: 0.64
    # cosine sim 0.66
    # cosine dist 0.59
   
   
    l = mylev(X_words,y_words)
    
    if Y is None:
        return hstack((cosine_similarity(X, Y), l))
    else:
        tmp = cosine_similarity(X, Y)
        print(l[0].shape)
        print(tmp.shape)
        return np.transpose(vstack((tmp, np.transpose(l))))
    


 # a) Restrict to items for which there are several examples. See if this works fine
 # b) When does it fail? In which classes do the errors fall?   

# classifier.fit(words_t,gt_flat)

# 
# word vector for each class / for each sample of a class
# distance of an item to each class / each sample of a class is feature

gt_flat = [x[0] for x in list(itertools.chain.from_iterable(gt))]
X = []
y = []



X_train = []
y_train = []
X_test = []
y_test = []

threshold = 4
for key in variationDict.keys():
    items = variationDict[key]
    l = len(items)
    gts = [key] * l 
    if l >= threshold:
        # assign half to test, half to train
        # For now: First two to training:
        sep = int(floor(l / 2.0))
        # sep = l-2
        X_train.extend(items[0:sep])
        y_train.extend(gts[0:sep])
        X_test.extend(items[sep:])
        y_test.extend(gts[sep:])
        
    else:
        pass
        # X_train.extend(items)
        # y_train.extend(gts)
        # assign to train only
# 
# X_train = X
# y_train = y




vect = getVectorizer()
vect.fit(X_train)
classifier = MultinomialNB(alpha=1e-3)

# classifier = SVC(degree=3, gamma='auto',kernel='linear',tol=0.001)

# classifier = SVR()




words_t = vect.transform(X_train)


# words_t_dist = mydist(vect.transform(X_train))
#words_t_dist = mylev(X_train)
words_t_dist = mydist2(words_t, X_train, None, None)
classifier.fit(words_t_dist, y_train)



fails = 0
correct = 0
failedItems = []

failDict = {}

for i in range(len(X_test)):

    item_t = vect.transform([X_test[i]])
    key = y_test[i]
    # item_t_dist = mydist(words_t,item_t)
    #item_t_dist = mylev(X_train, [X_test[i]])
    item_t_dist = mydist2(words_t, X_train,item_t,[X_test[i]])
    # pred_index = item_t_dist.argmin()
    # pred = gt_flat[pred_index]
    pred = classifier.predict((item_t_dist))
    # pred = classifier.predict(item_t)
    
    if pred == key:
        correct += 1
    else:
        fails += 1
        failedItems.append((X_test[i], pred, y_test[i]))
        if not failDict.has_key(key):
            failDict[key] = [X_test[i]]
        else:
            failDict[key].append(X_test[i])

print("fail: " + str(fails))
print("correct: " + str(correct))
print("ratio: " + str(float(correct) / (correct + fails)))

     
