import matplotlib
import matplotlib.pyplot as plt
import numpy as np
#from tests.evaluate_table_detection import TEST_REPORTS,precision_plot

#print(len(TEST_REPORTS))






# plt.plot(np.arange(1., 21., 1),
#          ['0.87302574176', '0.930840185924', '0.894147827916', '0.896491733626', '0.906054870252', '0.912648286925', '0.902651635476', '0.911803419685', '0.901659072355', '0.928713633009', '0.884387559114', '0.902089590987',
#           '0.911466975328', '0.938061562718', '0.911513194635', '0.891635891736', '0.919769871873', '0.885307384009', '0.888823699604', '0.873117093876'])
# plt.plot(np.arange(1., 21., 1),
#          ['0.87302574176', '0.930840185924', '0.894147827916', '0.896491733626', '0.906054870252', '0.912648286925', '0.902651635476', '0.911803419685', '0.901659072355', '0.928713633009', '0.884387559114', '0.902089590987',
#           '0.911466975328', '0.938061562718', '0.911513194635', '0.891635891736', '0.919769871873', '0.885307384009', '0.888823699604', '0.873117093876'],
#          'bo')
#
#
# plt.plot(np.arange(1., 21., 1),
#          ['0.766636620307', '0.851926932866', '0.77888490298', '0.827403634335', '0.839139852944', '0.863916035216', '0.83708483504', '0.823178659006', '0.83598068548', '0.812953051908', '0.815442047807', '0.836496504565', '0.837685597506',
#           '0.806919807808', '0.805090759371', '0.816807455446', '0.806489873475', '0.819649796787', '0.760342844649', '0.78134635644'])
# plt.plot(np.arange(1., 21., 1),
#          ['0.766636620307', '0.851926932866', '0.77888490298', '0.827403634335', '0.839139852944', '0.863916035216', '0.83708483504', '0.823178659006', '0.83598068548', '0.812953051908', '0.815442047807', '0.836496504565', '0.837685597506',
#           '0.806919807808', '0.805090759371', '0.816807455446', '0.806489873475', '0.819649796787', '0.760342844649', '0.78134635644'],
#          'ro')
#
# plt.axis([0, 19, 0.7, 1])
# plt.ylabel('P-avg (blue) R-avg (orange)')
# plt.xlabel('Up to Batch')
#
# plt.xticks(np.arange(1., 21., 1))
precision=[83,70,74,86]
recall=[67,52,65,79]
fscore=[66,54,66,80]
kappa=[65,56,67,80]
docs=[10,20,50,100]

plt.plot(docs,precision)
plt.plot(recall)
plt.plot(fscore)
plt.plot(kappa)


#plt.axis([0, 400, 1800, 11000])
#plt.ylabel('precision')
#plt.xlabel('docs')


plt.show()