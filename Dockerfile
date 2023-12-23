#FROM ubuntu
FROM python:3.10.0a6-buster

WORKDIR /usr/marketticker/pydataworker

RUN apt-get update && \
    apt-get upgrade -y

WORKDIR /usr/marketticker/pydataworker/

RUN pip3 install -r requirements.txt

COPY python.conf python.conf
COPY marketticker marketticker

RUN export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
# needed to add all installed scripts
RUN ldconfig

COPY startup.sh startup.sh
#ENTRYPOINT ["jupyter-lab","--allow-root"," >> log.txt"]
ENTRYPOINT ["bash", "/usr/coindeck/pydataworker/startup.sh"]