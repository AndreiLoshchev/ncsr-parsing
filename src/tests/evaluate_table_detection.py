'''
Created on 15.02.2017

@author: michael
'''

#import pandas as pd
#import matplotlib
#matplotlib.use('Agg')
#import matplotlib.pyplot as plt
import numpy as np
from sklearn.model_selection import KFold
import glob2, glob
from definitions import *
from parse_ncsr.table_detector import TableDetector
from sklearn.metrics.classification import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import cohen_kappa_score
from sklearn.metrics import classification_report

import os
import time
import dill
from parse_ncsr_backend.ncsr_table_parsing import get_lxml_from_string
import random

#print(ALL)
TEST_REPORTS = glob2.glob('project/testdata/ncsr-data/*-annotated.html') 
def run_eval(docs=None):

    # Available evaluation types:

    DO_K_FOLD=True
    K_FOLD_K=3
    index_docs=random.sample(range(0, 180), 50)#change the number of docs
    #if docs != None:
        #TEST_REPORTS = docs
    #else:
    TEST_REPORTS = glob2.glob('project/testdata/ncsr-data/*-annotated.html')
    #TEST_REPORTS=['project/testdata/ncsr-data/ACM_2016-10-31_119312517002696-annotated.html', 'project/testdata/ncsr-data/PIM_2016-08-31_119312516758458-annotated.html', 'project/testdata/ncsr-data/PAD_2012-09-30_114420412066894-annotated.html', 'project/testdata/ncsr-data/TWC_2016-12-31_112415517000002-annotated.html', 'project/testdata/ncsr-data/RVS_2016-10-31_119312517002934-annotated.html', 'project/testdata/ncsr-data/SGB_2014-12-31_119312515082947-annotated.html', 'project/testdata/ncsr-data/SGB_2014-09-30_95012314012638-annotated.html', 'project/testdata/ncsr-data/MFS_2016-12-31_119312517058138-annotated.html', 'project/testdata/ncsr-data/AIM_2016-08-31_119312516767468-annotated.html', 'project/testdata/ncsr-data/PUT_2016-12-31_92881617000532-annotated.html']
    #TEST_REPORTS = [TEST_REPORTS[i] for i in index_docs]
    print (TEST_REPORTS)
    print('Using ' + str(len(TEST_REPORTS)) + ' documents')
    print('out of ' + str(len(TEST_REPORTS)))




    # k-fold validation:

    if DO_K_FOLD:
        t0_glob=time.time()
        kfold = KFold(n_splits=K_FOLD_K, shuffle=True)
        precision_all=[]
        recall_all=[]
        confidence_all=[]
        F1_manual_all=[]
        #f1_score_all=[]
        #acc_score_all=[]
        cohen_score_all=[]
        precision_train_all=[]
        recall_train_all=[]
        F1_manual_train_all=[]
        cohen_score_train_all=[]

        count=1

        gt_all=[]
        pred_all=[]
        gt_all_train=[]
        pred_all_train=[]

        for train, test in kfold.split(TEST_REPORTS):

            print('k-fold iteration ' + str(count) + ' of ' + str(K_FOLD_K))
            count+=1
            print(test)
            # Don't let the TableDetector serialize itself:
            print('training')
            t0 = time.time()
            detector = TableDetector([TEST_REPORTS[i] for i in train],doSerialize=False)
            t1 = time.time()
            print('time: ' + str(t1-t0))
            print('testing: ')
            t0 = time.time()
            for testindex in test:

                with open(TEST_REPORTS[testindex],'r') as f:
                    s = f.read()
                tree = get_lxml_from_string(s)
                prediction, confidence = detector.predict(tree)

                data = detector.score(tree, prediction)

                precision=data['precision']
                recall=data['recall']
                gt_all.extend(data['gt'])
                pred_all.extend(data['prediction'])
                try:
                    F1 = 2 * (precision * recall) / (precision + recall)
                except ZeroDivisionError:
                    F1 = 0
                #print(F1)
                #acc_score=accuracy_score(data['gt'],data['prediction'])
                precision_all.append(precision)
                recall_all.append(recall)
                F1_manual_all.append(F1)
                #acc_score_all.append(acc_score)
                #f1_score_all.append(f1)
                confidence_all.extend(confidence)
                cohen_score = cohen_kappa_score(data['gt'], data['prediction'])
                cohen_score_all.append(cohen_score)
                
        
            t1 = time.time()
            print('time: ' + str(t1-t0))################################
            """           
            for trainindex in train:

                with open(TEST_REPORTS[trainindex],'r') as f:
                    s = f.read()
                tree = get_lxml_from_string(s)
                prediction_train = detector.predict_train(tree)

                data_train = detector.score_train(tree, prediction_train)
                
                precision_train=data_train['precision']
                recall_train=data_train['recall']
                gt_all_train.extend(data_train['gt'])
                pred_all_train.extend(data_train['prediction'])
                try:
                    F1_train = 2 * (precision_train * recall_train) / (precision_train + recall_train)
                except ZeroDivisionError:
                    F1_train = 0
                #print(F1)
                #f1=f1_score(data['gt'],data['prediction'],average='micro')
                #acc_score=accuracy_score(data['gt'],data['prediction'])
                precision_train_all.append(precision_train)
                recall_train_all.append(recall)
                F1_manual_train_all.append(F1)
                #acc_score_all.append(acc_score)
                #f1_score_all.append(f1)
                confidence_all.extend(confidence)
                cohen_score_train = cohen_kappa_score(data_train['gt'], data_train['prediction'])
                cohen_score_train_all.append(cohen_score_train)
                
            """       
            #t1 = time.time()
            #print('time: ' + str(t1-t0))
        t1_glob=time.time()
        tt = str(t1_glob-t0_glob)
        print('Total time      : ' + (tt))
        pa = str(float(sum(precision_all))/len(precision_all))
        print('Precision avg   : ' + pa)
        ra = str(float(sum(recall_all))/len(recall_all))
        print('Recall avg      : ' + ra)
        f1scr=float(sum(F1_manual_all)/len(F1_manual_all))
        print ('F1 manual avg   : '+str(f1scr))
        #print('f1_score avg   : ',f1_scr)
        #ac_score=float(sum(acc_score_all)/len(acc_score_all))
        #print ('Accuracy avg   : '+str(ac_score))
        #print (confidence_all)
        cohen=float(sum(cohen_score_all)/len(cohen_score_all))
        print ('Cohen Kappa avg : '+str(cohen))


        #pa_train = str(float(sum(precision_train_all))/len(precision_train_all))
        #print('Precision train avg   : ' + pa_train)
        #ra_train = str(float(sum(recall_train_all))/len(recall_train_all))
        #print('Recall train avg      : ' + ra_train)
        #f1scr_train=float(sum(F1_manual_train_all)/len(F1_manual_train_all))
        #print ('F1 train manual avg   : '+str(f1scr_train))
        #print('f1_score avg   : ',f1_scr)
        #ac_score=float(sum(acc_score_all)/len(acc_score_all))
        #print ('Accuracy avg   : '+str(ac_score))
        #print (confidence_all)
        #cohen_train=float(sum(cohen_score_train_all)/len(cohen_score_train_all))
        #print ('Cohen Kappa train avg : '+str(cohen_train))
        '''d={'actual':gt_all, 'predicted':pred_all}
        import pandas as pd
        df=pd.DataFrame(d)
        print(df[df.actual=='fh_table_cont'],len(df.actual[df.actual=='fh_table_cont']))'''
        target_names = ['soo_table', 'fh_table', 'soo_table_cont', 'fh_table_cont',
         'sal_table', 'scna_table', 'soo_plus_saa_table', 'sal_table_cont', 'scna_table_cont', 'other']
        print(classification_report(gt_all, pred_all, target_names=target_names,labels=target_names))

        print('Confusion matrix:')
        labels=[detector.target_soo,detector.target_fh,
        detector.target_soo_cont,detector.target_fh_cont,
        detector.target_sal,detector.target_scna,detector.target_soo_plus_saa,
        detector.target_sal_cont,detector.target_scna_cont,detector.target_other]
        #labels=['soo','fh','soo_cont','fh_cont','sal','scna',
        #'soo_+_saa','sal_cont','scna_cont','other']
        cm = confusion_matrix(gt_all,pred_all,labels=labels)
        print(labels)
        print(cm)
        

        return (str(len(TEST_REPORTS)), tt, pa, ra) #pa_train, ra_train, cohen, cohen_train, f1scr, f1scr_train)


if __name__ == "__main__":
    run_eval()