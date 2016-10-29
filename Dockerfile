FROM python:latest

MAINTAINER Niklas Voss version: 0.1

# requirements.txt doesn't work, because cython needs
# to exist before all other packages and order of installation,
# so install dependency one by one, other
RUN pip install cython
RUN pip install numpy
RUN pip install scipy
RUN pip install textblob-de
RUN pip install langid
RUN pip install faker
RUN pip install pymongo
RUN python -m textblob.download_corpora

ADD ./preprocess.py /opt/preprocess.py
ADD ./exampletext.txt /opt/exampletext.txt

CMD ["python", "/opt/preprocess.py"]