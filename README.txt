Repository for the ncsr-parsing project 

# Repository Structure #

src/parse_ncsr/             scripts for classification

src/parse_ncsr_backend      code used by the classification scripts
src/tests                   various test scripts
src/tools                   scripts for development, annotation, etc.


data/:            serialized files, synonym lists, etc.

testdata/:        NCSR reports

literature/pdfs   literature relevant to the project






# How do I get set up? #
## General ##
For installation of 'pystruct' (structured learning in python) see:
     https://pystruct.github.io/installation.html

Required packages for Python are listed in "src/requirements.txt". Using 'pip' (https://pypi.python.org/pypi/pip), requirements are installed via: 

     "pip install -r /path/to/requirements.txt"

NLTK requires to download additional data. This can be done in a python shell, executing:

      import nltk
      nltk.download()

Choosing the option "book (Everything used in the NLTK book)" is sufficient.

Additionally, the variable 'PYTHONPATH' must contain the path to the 'src' directory of the repository, so that Python knows where to look for modules. Scripts may then be called using 'python script.py'. 

## Scripts ##
1) Classify and print result to 'stdout':
SoO and FH table data can be extracted using the scripts

    parse_ncsr/soo_classify.py     and
    parse_ncsr/fh_classify.py

This will output a JSON result file containing the keys and respective numbers. Output can also be redirected to a file (--out OutputFilename).

Table detection can be performed using the script

    parse_ncsr/table_detector.py

2) Classify + annotate HTML files:
NCSR reports with marked SoO tables (class="soo_table" in table header) can be annotated using the script 

     tools/preannotate_data.py

This will insert "soo_label=X" marks into the HTML code (along with select boxes set to the respective value).