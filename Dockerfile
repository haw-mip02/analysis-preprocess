FROM python:latest

MAINTAINER Niklas Voss version: 0.1

ADD ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
RUN pip3 install hdbscan # needs to be installed separately
RUN python -m textblob.download_corpora

ADD ./preprocess.py /opt/preprocess.py

CMD ["python", "/opt/preprocess.py"]