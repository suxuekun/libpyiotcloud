FROM jenkinsci/blueocean

USER root

RUN apk add openrc
RUN apk update
RUN apk add docker
RUN apk add py-pip
RUN apk add python-dev libffi-dev openssl-dev gcc libc-dev make
RUN pip install docker-compose
RUN rc-update add docker boot

EXPOSE 8080
EXPOSE 50000
