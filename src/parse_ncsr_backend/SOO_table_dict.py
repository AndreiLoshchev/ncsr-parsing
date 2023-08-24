'''
Created on 05.10.2016

@author: michael
'''


import json
import os
from definitions import DATA_DIR
# from collections import OrderedDict



# tuples are (name, level, value, type)
# where types are header (h), data (d), aggregate (a)
          
SOO_table=[
        ('undefined',1,'','u'),
        ('empty',1,'','e'),
        ('not sure',1,'','u'),
        ('Income',1,'','h'),
            ('Interest',2,'','d'),
            ('Interest:',2,'','h'),
                ('Companies owned (more|less) than X%',3,'','d'),
                ('Unspecified',3,'','d'),
            ('Dividends',2,'','d'),
            ('Dividends:',2,'','h'),
                ('Unspecified',3,'','d'),
            ('Lease',2,'','d'),
            ('Securities lending',2,'','d'),
            ('Other income',2,'','d'),
            ('Total investment income [Total]',2,'','a'),
        ('Expenses',1,'','h'),
            ('Total expenses [Total]',2,'','a'),
            ('Net expenses',2,'','d'),
            ('Net investment income / loss',2,'','d'),
            ('Accounting',2,'','d'),
            ('Administration',2,'','d'),
            ('Administration and management',2,'','d'),
            ('Advisory fees',2,'','d'),
                ('Advisory base',3,'','d'),
                ('Return including adjustment',3,'','d'),
                ('Group fee',3,'','d'),
            ('Amortization',2,'','d'),
            ('Auction fees',2,'','d'),
            ('Audit',2,'','d'),
            ('Audit and legal',2,'','d'),
            ('Audit and accounting',2,'','d'),
            ('Commitment fees',2,'','d'),
            ('Compliance officer fees',2,'','d'),
            ('Custodian',2,'','d'),
            ('Custodian and accounting',2,'','d'),
            ('Custody, accounting and administration',2,'','d'),
            ('Directors fee',2,'','d'),
            ('Directors/trustee comp',2,'','d'),
            ('Distribution fees',2,'','d'),
            ('Distribution and service plan fees',2,'','d'),
            ('Waivers',2,'','h'),
                ('Administrator waiver',3,'','d'),
                ('Advisor waiver',3,'','d'),
                ('Advisor recoup',3,'','d'),
                ('Custodian waiver', 3, '','d'),
                ('Combined waiver',3,'','d'),
                ('Other waiver',3,'','d'),
                ('Distribution waiver',3,'','d'),
            ('Indirect Expenses',2,'','h'),
                ('Indirect transfer agent',3,'','d'),
                ('Indirect custodian',3,'','d'),
                ('Indirect soft dollar',3,'','d'),
                ('Indirect other', 3, '','d'),
            ('Fund accounting',2,'','d'),
            ('General and administrative',2,'','d'),
            ('Incentive fees',2,'','d'),
            ('Insurance',2,'','d'),
            ('Interest expense',2,'','d'),
            ('Investment advisory fees',2,'','d'),
            ('Legal fees',2,'','d'),
            ('Legal and accounting',2,'','d'),
            ('Legal fees, professional fees, due diligence expenses',2,'','d'),
            ('Line of credit',2,'','d'),
            ('Liquidity fees',2,'','d'),
            ('Listing fees',2,'','d'),
            ('Management fees',2,'','d'),
            ('Marketing and distribution',2,'','d'),
            ('Management fee to affiliate',2,'','d'),
            ('Miscellaneous/other',2,'','d'),
            ('Offering expenses',2,'','d'),
            ('Organization costs',2,'','d'),
            ('Payroll',2,'','d'),
            ('Postage',2,'','d'),
            ('Preferred shares service fee',2,'','d'),
            ('Printing, postage, mailings',2,'','d'),
            ('Professional',2,'','d'),
            ('Ratings fees',2,'','d'),
            ('Registration',2,'','d'),
            ('Remarketing',2,'','d'),
            ('Remarketing preferred shares',2,'','d'),
            ('Reorganization',2,'','d'),
            ('Reports to shareholders',2,'','d'),
            ('Salaries and Compensation',2,'','d'),
            ('Shareholder communications',2,'','d'),
            ('Shareholder expenses',2,'','d'),
            ('Shareholder meetings',2,'','d'),
            ('Tax',2,'','d'),           
            ('Transfer and shareholder servicing agent',2,'','d'),
            ('Trustee compensation',2,'','d'),
        ('Realized and unrealized gain from investments',1,'','h'),
            ('Net realized gain (loss) [Total]',2, '','d'),
            ('Net realized gain (loss) from:',2,'','h'), 
                ('Interest',3,'','d'),
                ('Dividends',3,'','d'),
                ('Security transactions',3,'','d'),
                ('Future contracts',3,'','d'),
                ('Options on future contracts',3,'','d'),
                ('Forward contracts',3,'','d'),
                ('Swaps',3,'','d'),
                ('Broker commissions',3,'','d'),
                ('Foreign currency transactions',3,'','d'),
                ('Investments',3,'','d'),
                ('Unaffiliated securities',3,'','d'),
                ('Unspecified',3,'','d'),
                    #('Net realized gain (loss)',3,'','a'),
            ('Net change in unrealized appreciation (depreciation) [Total]',2,'','a'),
            ('Net change in unrealized appreciation (depreciation) on:',2,'','h'),
                ('Security transactions',3,'','d'),
                ('Options on future contracts',3,'','d'),
                ('Future contracts',3,'','d'),
                ('Forward contracts',3,'','d'),
                ('Foreign currency',3,'','d'),
                ('Investments',3,'','d'),
                ('Swaps',3,'','d'),
                ('Unaffiliated securities',3,'','d'),
                ('Unspecified',3,'','d'),
                #('Net change in unrealized appreciation (depreciation) [Total]',2,'','a'),                 
            ('Net gain (loss) from investments',2,'','a'),
            ('Net decrease in net assets',2,'','d')];
              
    
          
with open(os.path.join(DATA_DIR, "soo_items.json"), 'wb') as f:
    # filter out type label for annotator.js:
    SOO_table_mod=[x[0:2] for x in SOO_table]
    json.dump(SOO_table_mod, f,  sort_keys=False)
    #json.dump(SOO_table, f, indent=3, sort_keys=False)


keyToVal={}
key=["","",""]
for item in SOO_table: 
        #item = SOO_table[i];
        key[item[1]-1]=item[0];
        for gtIndex in range(item[1],len(key)):
                key[gtIndex]="";
        tmp=key[0];
        for gtIndex in range(1,len(key)):
                if key[gtIndex]!="":
                        tmp+='//' + key[gtIndex];
                else:
                        break
        
        keyToVal[tmp]=item[3]

keyToVal['undefined']='u'  
    
    
    

# SOO_table = OrderedDict();    
# SOO_table['Income']=OrderedDict([
#                 ('Interest',''),
#                 ('Interest:',OrderedDict([
#                     ('unspecified sub-item','')])),
#                 ('Dividends',''),
#                 ('Dividends:',OrderedDict([
#                     ('unspecified sub-item','')])),
#                 ('Lease',''),
#                 ('Other income',''),
#                 ('Total investment income','')
#                     ]);
# SOO_table['Expenses']=OrderedDict([
#             ('Accounting',''),
#             ('Administration',''),
#             ('Amortization',''),
#             ('Auction fees',''),
#             ('Audit',''),
#             ('Audit and accounting',''),
#             ('Commitment fees',''),
#             ('Compliance officer fees',''),
#             ('Custodian',''),
#             ('Directors/trustee comp',''),
#             ('Distribution fees',''),
#             ('Fees waived',''),
#             ('Fund accounting',''),
#             ('General and administrative',''),
#             ('Incentive fees',''),
#             ('Insurance',''),
#             ('Interest expense',''),
#             ('Investment advisory fees',''),
#             ('Legal fees',''),
#             ('Legal and accounting',''),
#             ('Legal fees, professional fees, due diligence expenses',''),
#             ('Line of credit',''),
#             ('Liquidity fees',''),
#             ('Listing fees',''),
#             ('Management fees',''),
#             ('Management and advisory fees',''),
#             ('Management fee to affiliate',''),
#             ('Miscellaneous/other',''),
#             ('Net expenses',''),
#             ('Net investment income / loss',''),
#             ('Offering expenses',''),
#             ('Payroll',''),
#             ('Preferred shares service fee',''),
#             ('Printing, postage, mailings',''),
#             ('Professional',''),
#             ('Ratings fees',''),
#             ('Registration',''),
#             ('Remarketing',''),
#             ('Remarketing preferred shares',''),
#             ('Reorganization',''),
#             ('Reporting',''),
#             ('Reports to shareholders',''),
#             ('Shareholder communications',''),
#             ('Shareholder expenses',''),
#             ('Tax',''),
#             ('Total expenses',''),
#             ('Transfer agent','')
#             ]);
#              
# SOO_table['Realized and unrealized gain from investments']=OrderedDict([
#                 ('Net realized gain (loss)', ''),
#                 ('Net realized gain (loss) from:',OrderedDict([ 
#                 
#                     ('Interest',''),
#                     ('Dividends',''),
#                     ('Security transactions',''),
#                     ('Future contracts',''),
#                     ('Options on future contracts',''),
#                     ('Forward contracts',''),
#                     ('Foreign currency transactions',''),
#                     ('Net realized gain (loss)','')])),
#                     
#                 
#                 ('Net change in unrealized appreciation (depreciation)',''),
#                 ('Net change in unrealized appreciation (depreciation) on:',OrderedDict([
#                  
#                     ('Security transactions',''),
#                     ('Options on future contracts',''),
#                     ('Future contracts',''),
#                     ('Forward contracts',''),
#                     ('Foreign currency',''),
#                     ('Investments',''),
#                     ('Net change in unrealized appreciation (depreciation)','')])),
#                  
#                 ('Net gain (loss) from investments',''),
#                 ('Net decrease in net assets','')]);
#               
#     
#     

# test = [['Income',1,''],['Interest',2,'']]
# with open(os.path.join(DATA_DIR, "soo_items2.json"), 'wb') as f:
#     json.dump(test, f,  sort_keys=False)
# with open(os.path.join(DATA_DIR, "SoO_income_synonyms.json")) as f:
#     SOO_synonyms=json.load(f)
# tmp=[x[0] for x in SOO_synonyms]
# for k in SOO_table['Income']:
#     print(tmp.index(k.strip(':')))
#     if isinstance(SOO_table['Income'][k],dict):
#             for l in SOO_table['Income'][k]:
#                 if l!='unspecified sub-item':
#                     print(tmp.index(l.strip(':')))
#                 
# with open(os.path.join(DATA_DIR, "SoO_expense_synonyms.json")) as f:
#     SOO_synonyms=json.load(f)
# tmp=[x[0] for x in SOO_synonyms]
# for k in SOO_table['Expenses']:
#     print(tmp.index(k.strip(':')))
#     if isinstance(SOO_table['Expenses'][k],dict):
#             for l in SOO_table['Expenses'][k]:
#                 if l!='unspecified sub-item':
#                     print(tmp.index(l.strip(':')))    
     
# with open(os.path.join(DATA_DIR, "SoO_gainloss_synonyms.json")) as f:
#     SOO_synonyms=json.load(f)
# tmp=[x[0] for x in SOO_synonyms]
# for k in SOO_table['Realized and unrealized gain from investments']:
#     print(tmp.index(k.strip(':')))
#     if isinstance(SOO_table['Realized and unrealized gain from investments'][k],dict):
#             for l in SOO_table['Realized and unrealized gain from investments'][k]:
#                 print(tmp.index(l.strip(':')))
