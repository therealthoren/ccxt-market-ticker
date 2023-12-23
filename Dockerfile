#FROM ubuntu
FROM python:3.10.0a6-buster

WORKDIR /usr/marketticker/pydataworker

RUN apt-get update && \
    apt-get upgrade -y

WORKDIR /usr/marketticker/pydataworker/


COPY python.conf python.conf
COPY requirements.txt requirements.txt
COPY startup.sh startup.sh
COPY marketticker marketticker

RUN pip3 install -r requirements.txt

RUN export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
# needed to add all installed scripts
RUN ldconfig

COPY startup.sh startup.sh
#ENTRYPOINT ["jupyter-lab","--allow-root"," >> log.txt"]
ENTRYPOINT ["bash", "/usr/coindeck/pydataworker/startup.sh"]