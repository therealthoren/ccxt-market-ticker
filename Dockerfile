#FROM ubuntu
FROM python:3.8-slim-buster

WORKDIR /usr/coindeck/pydataworker

RUN apt-get update && \
    apt-get upgrade -y

RUN apt-get install build-essential -y
RUN apt-get install wget curl -y

RUN apt-get install git -y

#RUN apt-get install python3.8 -y

#RUN apt-get install python3-pip -y
#RUN apt-get install python3-dev -y

#RUN pip3 install numpy
#RUN pip3 install TA-Lib

#RUN apt -y install curl dirmngr apt-transport-https lsb-release ca-certificates
#RUN curl -sL https://deb.nodesource.com/setup_12.x | bash
#RUN apt-get install nodejs -y
#RUN apt-get install npm -y already installed with above

#RUN apt-get install git -y

WORKDIR /usr/ccxtmarketticker/pydataworker/

RUN pip3 install google
RUN pip3 install grpcio
RUN pip3 install protobuf
RUN pip3 install chipmunkdb_python_client
RUN pip3 install pyarrow
RUN pip3 install ipython
RUN pip3 install ipykernel
RUN pip3 install pyarrow
RUN pip3 install --upgrade cython
RUN pip3 install loggly-python-handler


RUN pip3 install --upgrade protobuf

COPY python.conf python.conf
COPY coinlib/logger.py logger.py
COPY coinlib/coinlibFactory.py coinlibFactory.py

RUN export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
# needed to add all installed scripts
RUN ldconfig

COPY startup.sh startup.sh
#ENTRYPOINT ["jupyter-lab","--allow-root"," >> log.txt"]
ENTRYPOINT ["bash", "/usr/coindeck/pydataworker/startup.sh"]