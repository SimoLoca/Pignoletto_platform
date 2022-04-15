FROM ubuntu:20.04

COPY ./pignoletto /pignoletto-project/pignoletto
COPY ./requirements.txt /pignoletto-project
COPY ./run.py /pignoletto-project
COPY ./run.ini /pignoletto-project
COPY ./pignoletto_app /pignoletto-project

WORKDIR /pignoletto-project

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y gnupg software-properties-common wget nano \
    && wget -qO - https://qgis.org/downloads/qgis-2021.gpg.key | gpg --no-default-keyring --keyring gnupg-ring:/etc/apt/trusted.gpg.d/qgis-archive.gpg --import \
    && chmod a+r /etc/apt/trusted.gpg.d/qgis-archive.gpg \
    && add-apt-repository "deb https://qgis.org/ubuntu-ltr $(lsb_release -c -s) main" \
    && apt-get update && apt-get upgrade -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y qgis python-qgis qgis-plugin-grass \
    && apt-get install -y python3-pip \
    && pip3 install uwsgi \
    && pip3 install -r requirements.txt
    
CMD ["uwsgi", "run.ini"]
