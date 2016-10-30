FROM python:latest

MAINTAINER Niklas Voss version: 0.1

ADD ./requirements.txt /tmp/requirements.txt
RUN pip3 install -r /tmp/requirements.txt
RUN python -m textblob.download_corpora

ADD ./preprocess.py /opt/preprocess.py
ADD ./exampletext.txt /opt/exampletext.txt

CMD ["python", "/opt/preprocess.py"]