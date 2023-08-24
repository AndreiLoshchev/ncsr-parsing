'''
Created on 08.11.2016

@author: michael.fieseler@gmail.com
'''

# Based on example from scikit-learn documentation:
# http://scikit-learn.org/stable/auto_examples/model_selection/plot_confusion_matrix.html#sphx-glr-auto-examples-model-selection-plot-confusion-matrix-py


import itertools
import numpy as np
import matplotlib.pyplot as plt
 
from sklearn.metrics import confusion_matrix

def plot_confusion_matrix(cm_gt,cm_pred,allTargets,normalize=False):
    for tableIndex in range(len(cm_gt)):
        if cm_gt[tableIndex] is None:
            cm_gt[tableIndex]='undefined'
    cm_pred=[x[0] for x in cm_pred ]
    cm_gt=[x[0] for x in cm_gt ]  
    
    # Replace '//' in labels by 'newline' for presentation
    cm_gt=[x.replace("//","\n") for x in cm_gt]
    cm_pred=[x.replace("//","\n") for x in cm_pred]
    allTargets=[x.replace("//","\n") for x in allTargets]
           
    cm=confusion_matrix(cm_gt,cm_pred,labels=allTargets)
    
    
    plt.rcParams.update({'font.size': 6})
    plt.figure()

    # Restrict view to items which were classified wrongly:
    rowsToShow=[False]*len(cm)
    for tableIndex in range(len(cm)):
        for gtIndex in range(len(cm[0])):
            if tableIndex!=gtIndex and cm[tableIndex,gtIndex]!=0:
                rowsToShow[tableIndex]=True
                rowsToShow[gtIndex]=True
                  
    cm = cm.compress(rowsToShow,0)
    cm = cm.compress(rowsToShow,1)
 
    out=[]
    for tableIndex in range(len(rowsToShow)):
        if rowsToShow[tableIndex]:
            out.append(allTargets[tableIndex])
     
    allTargets=out
                
    plt.imshow(cm, interpolation='nearest',cmap="Blues") 
    
    plt.colorbar()
    tick_marks = np.arange(len(allTargets))
    plt.xticks(tick_marks, allTargets, rotation=90)
    plt.yticks(tick_marks, allTargets)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
        print("Normalized confusion matrix")
    else:
        print('Confusion matrix, without normalization')

    print(cm)

    thresh = cm.max() / 2.
    for tableIndex, gtIndex in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(gtIndex, tableIndex, cm[tableIndex, gtIndex],
                 horizontalalignment="center",
                 color="white" if cm[tableIndex, gtIndex] > thresh else "black")
    #!
    #plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    plt.show()  
    
