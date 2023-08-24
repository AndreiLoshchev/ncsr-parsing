FROM python:2.7.13
MAINTAINER Andrei Loshchev

RUN printf "deb http://archive.debian.org/debian/ jessie main\ndeb-src http://archive.debian.org/debian/ jessie main\ndeb http://security.debian.org jessie/updates main\ndeb-src http://security.debian.org jessie/updates main" > /etc/apt/sources.list

RUN apt-get update
RUN apt-get install -y apt-utils

# Convenience alias
RUN echo 'alias ll="ls -l"' >> ~/.bashrc


######################################################################
# Python, Numpy, SkLearn environment

RUN apt-get install -y build-essential python-dev python-setuptools python-numpy python-scipy libatlas-dev python-cvxopt python-pip

RUN pip install numpy
RUN pip install --user --upgrade scikit-learn pystruct lxml

COPY ./src/requirements.txt /
ENV PYTHONPATH /project/src

RUN pip install -r /requirements.txt
RUN python -m nltk.downloader -d /usr/local/share/nltk_data book

######################################################################
# Pickle

#RUN pip install pickle
RUN pip install glob2
# docker run -ti -v  C:\Users\aw121\ncsr-parsing:/project tableclassification /bin/bash
# python project/src/tests/evaluate_table_detection.py
# python project/src/parse_ncsr/table_detector.py project/testdata/ncsr-data/BEN_2017-02-28_75701017000097-annotated.html
# python project/src/tests/evaluate_table_classification.py
# python project/src/parse_ncsr/soo_classify.py project/testdata/ncsr-data/ING_2016-03-31_157104916015765-annotated.html
# docker run -ti -v C:\Users\aw121\ncsr-enviro\ncsr-server-env:/go server_ncsr /bin/bash