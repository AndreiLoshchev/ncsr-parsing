import pickle
import glob2
from tests.evaluate_table_detection import run_eval

list_of_lists = []

for i in range(20):
    strt = '/ncsr-data-3/group0001/batch'+str(i+1)+'00/*-annotated.html'
    if i == 0:
        list_of_lists.append(glob2.glob(strt))
    else:
        list_of_lists.append(glob2.glob(strt)+list_of_lists[-1])


print list_of_lists

log = {'numbers_of_documents': [],
        'total_times': [],
        'precision_avgs': [],
        'recall_avgs': []}

def add_values(dictt, nod, tt, pa, ra):
    dictt['numbers_of_documents'].append(nod)
    dictt['total_times'].append(tt)
    dictt['precision_avgs'].append(pa)
    dictt['recall_avgs'].append(ra)



for l in list_of_lists:
    vals = run_eval(l)
    add_values(log, vals[0], vals[1], vals[2], vals[3])

# Store data (serialize)
with open('reports.pickle', 'wb') as handle:
    pickle.dump(log, handle, protocol=pickle.HIGHEST_PROTOCOL)
