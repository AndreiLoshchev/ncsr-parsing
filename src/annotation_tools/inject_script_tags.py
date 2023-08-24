'''
Created on 24.03.2017

@author: michael
'''
import argparse

import lxml.html
from lxml.builder import E

              
def main(args):
    
   
           
           
    for filename in args.InputFilenames:
        
        print(filename)
        
        with open(filename,'r') as f:
            s = f.read()
        tree = lxml.html.fromstring(s)
        
           
                
        head = tree.find('.//head')
        
        scripttag_1 = E.script(src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js")
        scripttag_2 = E.script(src="annotator.js")
    

        # avoid repeated injection:        
        if lxml.html.tostring(scripttag_1) not in [lxml.html.tostring(x) for x in head.xpath('.//script')]:    
            head.append(scripttag_1)
            
        if lxml.html.tostring(scripttag_2) not in [lxml.html.tostring(x) for x in head.xpath('.//script')]:    
            head.append(scripttag_2)
    
    
        
        with open(filename,'w') as f:    
            f.write(lxml.html.tostring(tree))
            
if __name__ == "__main__":
            
    parser = argparse.ArgumentParser(
        description='Inject script tags into NCSR report')
    

    parser.add_argument('InputFilenames', 
                nargs='+',
                help='Input file(s) to inject tags into.')
    
    args = parser.parse_args()
        
    main(args)

